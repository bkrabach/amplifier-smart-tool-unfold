"""Optional loopback review adapter. Only encoded media reaches the browser."""

import json
import secrets
import threading
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

from .models import UnfoldError


class Dashboard:
    def __init__(self, library, port=0):
        self.library = library
        self.token = secrets.token_urlsafe(32)
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass  # Do not log viewer credentials.

            def allowed(self):
                cookies = SimpleCookie()
                try:
                    cookies.load(self.headers.get("Cookie", ""))
                    return secrets.compare_digest(cookies["unfold"].value, owner.token)
                except (KeyError, ValueError):
                    return False

            def respond(self, status, body, content_type="application/json", extra=None):
                if not isinstance(body, bytes):
                    body = json.dumps(body).encode()
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Referrer-Policy", "no-referrer")
                self.send_header(
                    "Content-Security-Policy",
                    "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; object-src 'none'",
                )
                for key, value in (extra or {}).items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(body)

            def valid_host(self):
                return self.headers.get("Host") == f"127.0.0.1:{owner.server.server_port}"

            def do_GET(self):
                if not self.valid_host():
                    return self.respond(403, {"error": "Invalid host"})
                parsed = urlparse(self.path)
                token = parse_qs(parsed.query).get("token", [""])[0]
                if parsed.path == "/" and token and secrets.compare_digest(token, owner.token):
                    return self.respond(
                        303,
                        b"",
                        extra={
                            "Location": "/",
                            "Set-Cookie": f"unfold={owner.token}; HttpOnly; SameSite=Strict; Path=/",
                        },
                    )
                if not self.allowed():
                    return self.respond(
                        403, {"error": "Open the dashboard URL returned by Unfold."}
                    )
                try:
                    if parsed.path == "/":
                        return self.respond(
                            200,
                            files("unfold").joinpath("resources/dashboard.html").read_bytes(),
                            "text/html; charset=utf-8",
                        )
                    if parsed.path == "/state":
                        return self.respond(
                            200,
                            {
                                "projects": library.projects(),
                                "revisions": [
                                    library.inspect(revision_id)
                                    for project in library.projects()
                                    for revision_id in project["revisions"]
                                ],
                                "events": library.observe(),
                            },
                        )
                    if parsed.path.startswith("/media/"):
                        artifact = library.artifact(parsed.path.removeprefix("/media/"))
                        if artifact["integrity"] != "intact":
                            raise UnfoldError(
                                "MATERIAL_CHANGED", "Saved output changed or is missing."
                            )
                        data = Path(artifact["path"]).read_bytes()
                        headers = {"Accept-Ranges": "bytes"}
                        if "download" in parse_qs(parsed.query):
                            headers["Content-Disposition"] = (
                                "attachment; filename*=UTF-8''" + quote(artifact["download_name"])
                            )
                        status = 200
                        if self.headers.get("Range"):
                            import re

                            match = re.fullmatch(r"bytes=(\d+)-(\d*)", self.headers["Range"])
                            if not match:
                                return self.respond(416, b"")
                            start = int(match[1])
                            end = min(int(match[2]) if match[2] else len(data) - 1, len(data) - 1)
                            if start > end:
                                return self.respond(416, b"")
                            headers["Content-Range"] = f"bytes {start}-{end}/{len(data)}"
                            data, status = data[start : end + 1], 206
                        return self.respond(status, data, "video/mp4", headers)
                    return self.respond(404, {"error": "Not found"})
                except UnfoldError as exc:
                    return self.respond(400, {"error": exc.as_dict()})

            def do_POST(self):
                origin = f"http://127.0.0.1:{owner.server.server_port}"
                if (
                    not self.valid_host()
                    or not self.allowed()
                    or self.headers.get("Origin") != origin
                ):
                    return self.respond(403, {"error": "Invalid viewer origin"})
                try:
                    count = int(self.headers.get("Content-Length", "0"))
                    if not 0 < count <= 20000:
                        return self.respond(413, {"error": "Invalid request size"})
                    data = json.loads(self.rfile.read(count))
                    if self.path == "/feedback":
                        result = library.feedback(data["revision_id"], data["text"])
                    elif self.path == "/rename":
                        result = library.rename(data["id"], data["name"])
                    else:
                        return self.respond(404, {"error": "Not found"})
                    return self.respond(200, result)
                except (ValueError, KeyError, UnfoldError) as exc:
                    return self.respond(400, {"error": str(exc)})

        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}/?token={self.token}"

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
