"""Code-owned HTML, HyperFrames invocation and decoded-media observations.

Models supply validated scene data, never executable HTML/JS, paths or shell commands.
"""

import html
import json
import os
import shutil
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path

from .models import Scene, UnfoldError
from .store import digest, write_json


def run(argv, timeout=180):
    # Renderer processes have no provider credentials, user configuration or telemetry.
    env = {key: os.environ[key] for key in ("PATH", "TMPDIR", "SYSTEMROOT") if key in os.environ}
    env.update(HYPERFRAMES_NO_TELEMETRY="1", DO_NOT_TRACK="1")
    try:
        result = subprocess.run(argv, capture_output=True, text=True, env=env, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise UnfoldError(
            "BACKEND_FAILED", type(exc).__name__, "Check doctor and backend setup."
        ) from None
    if result.returncode:
        raise UnfoldError("BACKEND_FAILED", result.stderr[-3000:] or result.stdout[-3000:])
    return result.stdout


class Backend:
    def __init__(self, root):
        self.root = Path(root).expanduser().resolve()
        self.cli = self.root / "node_modules/.bin/hyperframes"
        self.gsap = self.root / "node_modules/gsap/dist/gsap.min.js"

    def doctor(self):
        versions = {}
        for name, required in (("hyperframes", "0.8.33"), ("gsap", "3.14.2")):
            try:
                actual = json.loads(
                    (self.root / "node_modules" / name / "package.json").read_text()
                )["version"]
            except (OSError, ValueError, KeyError):
                actual = None
            versions[name] = {"required": required, "actual": actual, "ready": actual == required}
        commands = {name: shutil.which(name) for name in ("node", "ffmpeg", "ffprobe")}
        return {
            "ready": all(v["ready"] for v in versions.values()) and all(commands.values()),
            "versions": versions,
            "commands": commands,
            "root": str(self.root),
        }

    def require(self):
        if not self.doctor()["ready"]:
            raise UnfoldError(
                "MISSING_PREREQUISITE",
                "Pinned renderer prerequisites are unavailable.",
                "Install the packaged backend.json with npm in the configured backend directory; install ffmpeg.",
            )

    def author(self, scene: Scene, directory):
        self.require()
        directory = Path(directory)
        directory.mkdir(exist_ok=True)
        elements = []
        for e in scene.elements:
            padding = "18px" if e.kind == "card" else "0"
            background = e.fill if e.kind != "text" else "transparent"
            border = f"1px solid {e.border}" if e.kind == "card" else "none"
            text = html.escape(e.text).replace("\n", "<br>")
            label = f'<div class="label">{html.escape(e.label)}</div>' if e.label else ""
            elements.append(
                f'<div id="{e.id}" class="element {e.kind}" style="left:{e.x}px;top:{e.y}px;'
                f"width:{e.width}px;height:{e.height}px;color:{e.color};background:{background};"
                f"font-size:{e.font_size}px;opacity:{e.opacity};border:{border};"
                f'border-radius:{e.radius}px;padding:{padding}">{label}{text}</div>'
            )
        lines = []
        for tween in scene.tweens:
            props = tween.model_dump(exclude_none=True, exclude={"target", "at"})
            lines.append(f'tl.to("#{tween.target}",{json.dumps(props)},{tween.at});')
        document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; object-src 'none'; frame-src 'none'">
<title>{html.escape(scene.title)}</title><script src="gsap.min.js"></script><style>
*{{box-sizing:border-box}}html,body{{margin:0;width:100%;height:100%;overflow:hidden}}
body{{font-family:system-ui,sans-serif}}#root{{position:relative;width:100%;height:100%;background:{scene.background};overflow:hidden}}
.element{{position:absolute;line-height:1.22;transform-origin:center center;font-weight:550}}
.label{{font-size:14px;line-height:1.2;letter-spacing:1.5px;margin-bottom:10px;font-weight:600}}
.line,.dot{{pointer-events:none}}
</style></head><body><div id="root" data-composition-id="unfold" data-start="0" data-width="1280" data-height="720" data-duration="{scene.duration}">
{"".join(elements)}</div><script>
window.__timelines=window.__timelines||{{}};const tl=gsap.timeline({{paused:true}});
{"".join(lines)}
window.__timelines.unfold=tl;
</script></body></html>'''
        (directory / "index.html").write_text(document)
        shutil.copyfile(self.gsap, directory / "gsap.min.js")
        write_json(directory / "scene.json", scene.model_dump())
        return self.source_hash(directory)

    def source_hash(self, directory):
        import hashlib

        return hashlib.sha256(
            "".join(
                digest(Path(directory) / name)
                for name in ("index.html", "gsap.min.js", "scene.json")
            ).encode()
        ).hexdigest()

    def render(self, directory, output):
        self.require()
        # Regenerate executable bytes from validated scene data before any browser execution.
        scene = Scene.model_validate_json((Path(directory) / "scene.json").read_text())
        expected = self.source_hash(directory)
        with tempfile.TemporaryDirectory(
            prefix="unfold-validate-", dir=Path(directory).parent
        ) as temporary:
            self.author(scene, temporary)
            if self.source_hash(temporary) != expected:
                raise UnfoldError(
                    "SOURCE_CHANGED",
                    "Generated source was externally modified; no code was executed or replaced.",
                )
        run(
            [
                str(self.cli),
                "render",
                str(directory),
                "--output",
                str(output),
                "--fps",
                "30",
                "--workers",
                "2",
                "--quality",
                "standard",
            ],
            timeout=240,
        )
        meta = self.probe(output)
        if (
            meta["width"] != 1280
            or meta["height"] != 720
            or abs(meta["duration"] - scene.duration) > 0.05
            or Fraction(meta["fps"]) != 30
        ):
            raise UnfoldError(
                "INVALID_RENDER", "Rendered dimensions or duration do not match source."
            )
        return {
            "source_sha256": expected,
            "sha256": digest(output),
            **meta,
            "method": "ffprobe of encoded MP4",
            "audio": "silent",
            "alpha": False,
        }

    def probe(self, path):
        data = json.loads(
            run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_streams",
                    "-show_format",
                    "-of",
                    "json",
                    str(path),
                ]
            )
        )
        videos = [s for s in data["streams"] if s["codec_type"] == "video"]
        if len(videos) != 1 or videos[0]["codec_name"] != "h264":
            raise UnfoldError("INVALID_RENDER", "Expected one H.264 video stream.")
        if any(s["codec_type"] == "audio" for s in data["streams"]):
            raise UnfoldError("INVALID_RENDER", "This profile promises silent output.")
        return {
            "width": videos[0]["width"],
            "height": videos[0]["height"],
            "duration": float(data["format"]["duration"]),
            "fps": videos[0]["avg_frame_rate"],
            "bytes": Path(path).stat().st_size,
        }

    def frames(self, video, times, directory):
        meta = self.probe(video)
        if not times or len(times) > 12 or any(not 0 <= t < meta["duration"] for t in times):
            raise UnfoldError("INVALID_INPUT", "Sample 1–12 times within the encoded duration.")
        directory = Path(directory)
        directory.mkdir(exist_ok=True)
        result = []
        for i, time in enumerate(times):
            path = directory / f"frame-{i}.jpg"
            run(
                [
                    "ffmpeg",
                    "-v",
                    "error",
                    "-ss",
                    str(time),
                    "-i",
                    str(video),
                    "-frames:v",
                    "1",
                    "-q:v",
                    "2",
                    "-y",
                    str(path),
                ],
                timeout=30,
            )
            result.append({"time": time, "path": str(path), "sha256": digest(path)})
        return result
