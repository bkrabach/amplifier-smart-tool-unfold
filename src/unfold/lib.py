"""Public domain operations. Adapters do not implement creative-library behavior."""

import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

from .backend import Backend
from .models import Brief, Grant, UnfoldError
from .store import Store, digest, uid, write_json


class Unfold:
    def __init__(self, library=None, backend=None):
        self.store = Store(library or Path.home() / ".local/share/unfold")
        self.backend = Backend(backend or Path.home() / ".local/share/unfold-backend")

    def doctor(self):
        return {
            "library": str(self.store.root),
            "backend": self.backend.doctor(),
            "providers": {
                name: bool(os.getenv(env))
                for name, env in (
                    ("gemini", "GEMINI_API_KEY"),
                    ("openai", "OPENAI_API_KEY"),
                    ("anthropic", "ANTHROPIC_API_KEY"),
                )
            },
        }

    def projects(self):
        return self.store.list("project")

    def inspect(self, identity):
        record = self.store.get(identity)
        if record.get("kind") == "artifact":
            return self.artifact(identity)
        if "artifacts" in record:
            record["resolved_artifacts"] = [self.artifact(i) for i in record["artifacts"]]
            directory = self.store.root / record["source"]
            try:
                intact = self.backend.source_hash(directory) == record["source_sha256"]
            except OSError:
                intact = False
            record["source_integrity"] = "intact" if intact else "changed_or_missing"
            record["source_path"] = str(directory)
        return record

    def artifact(self, identity):
        record = self.store.get(identity, "artifact")
        path = self.store.root / record["relative_path"]
        record["path"] = str(path)
        record["integrity"] = (
            "intact"
            if path.is_file() and digest(path) == record["sha256"]
            else "changed_or_missing"
        )
        record["download_name"] = re.sub(r"[^\w .-]", "_", record["name"]).strip(". ") + ".mp4"
        return record

    def observe(self, after=0):
        return self.store.events(after)

    def rename(self, identity, name):
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 120:
            raise UnfoldError("INVALID_INPUT", "Use a name of 1–120 characters.")
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            record = self.store.get(identity, db=db)
            if record.get("kind") not in {"project", "artifact"}:
                raise UnfoldError(
                    "UNSUPPORTED", "This slice renames projects and saved video outputs."
                )
            record["name"] = name.strip()
            self.store.put(record["kind"], record, db)
            self.store.event("renamed", identity, {"name": name.strip()}, db)
        return record

    def export(self, artifact_id, directory):
        artifact = self.artifact(artifact_id)
        revision = self.inspect(artifact["revision_id"])
        if artifact["integrity"] != "intact" or revision["source_integrity"] != "intact":
            raise UnfoldError(
                "MATERIAL_CHANGED", "Retained source or output changed; export was not performed."
            )
        directory = Path(directory).expanduser().resolve()
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / artifact["download_name"]
        try:
            with path.open("xb") as dest, Path(artifact["path"]).open("rb") as source:
                shutil.copyfileobj(source, dest)
        except FileExistsError:
            raise UnfoldError(
                "OUTPUT_EXISTS",
                "Export would overwrite an existing file.",
                "Choose a different directory or rename the output.",
            ) from None
        result = {
            "artifact_id": artifact_id,
            "path": str(path),
            "sha256": digest(path),
            "ownership": "caller-owned copy",
            "source_preserved": True,
        }
        self.store.event("exported", artifact_id, result)
        return result

    def feedback(self, revision_id, text):
        revision = self.store.get(revision_id, "revision")
        if not isinstance(text, str) or not 1 <= len(text.strip()) <= 5000:
            raise UnfoldError("INVALID_INPUT", "Feedback must have 1–5000 characters.")
        note = {
            "id": uid(),
            "kind": "feedback",
            "revision_id": revision_id,
            "project_id": revision["project_id"],
            "text": text.strip(),
            "status": "pending",
        }
        with self.store.connect() as db:
            self.store.put("feedback", note, db)
            self.store.event("feedback_submitted", revision_id, note, db)
        return note

    def cancel(self, operation_id):
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            operation = self.store.get(operation_id, "operation", db)
            if operation["status"] == "running":
                operation["status"] = "cancelling"
                self.store.put("operation", operation, db)
                self.store.event("cancellation_requested", operation_id, {}, db)
        return operation

    def address_feedback(self, feedback_id, revision_id):
        """Link submitted feedback to a revision that actually applied that exact request."""
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            note = self.store.get(feedback_id, "feedback", db)
            revision = self.store.get(revision_id, "revision", db)
            if (
                revision["base_revision"] != note["revision_id"]
                or revision["feedback"] != note["text"]
            ):
                raise UnfoldError(
                    "FEEDBACK_MISMATCH", "Revision does not carry this feedback and base."
                )
            if note.get("result_revision") == revision_id:
                return note
            if note["status"] != "pending":
                raise UnfoldError("FEEDBACK_CONFLICT", "Feedback already has a different result.")
            note.update(status="addressed", result_revision=revision_id)
            self.store.put("feedback", note, db)
            self.store.event("feedback_addressed", feedback_id, {"revision_id": revision_id}, db)
        return note

    def create(self, brief: Brief, grant: Grant, *, request_id=None):
        return self._produce(brief, grant, request_id=request_id)

    def revise(self, revision_id, feedback, grant: Grant, *, request_id=None):
        revision = self.inspect(revision_id)
        if revision.get("kind") != "revision" or revision["source_integrity"] != "intact":
            raise UnfoldError("MATERIAL_CHANGED", "A valid retained base revision is required.")
        if not isinstance(feedback, str) or not 1 <= len(feedback) <= 5000:
            raise UnfoldError("INVALID_INPUT", "Use feedback of 1–5000 characters.")
        return self._produce(
            Brief.model_validate(revision["brief"]),
            grant,
            base=revision,
            feedback=feedback,
            request_id=request_id,
        )

    def render(self, revision_id):
        """Re-render a committed composition without initializing intelligence."""
        revision = self.inspect(revision_id)
        if revision.get("kind") != "revision" or revision["source_integrity"] != "intact":
            raise UnfoldError("MATERIAL_CHANGED", "A valid retained source is required.")
        operation_id = uid()
        directory = self.store.workspace(operation_id)
        # Never rewrite committed source when preparing renderer input.
        shutil.copytree(revision["source_path"], directory / "source")
        metadata = self.backend.render(directory / "source", directory / "video.mp4")
        artifact = self._artifact(
            revision_id,
            directory / "video.mp4",
            metadata,
            self.store.get(revision["project_id"], "project")["name"],
        )
        with self.store.connect() as db:
            self.store.put("artifact", artifact, db)
            self.store.event("rendered", revision_id, {"artifact_id": artifact["id"]}, db)
        return self.artifact(artifact["id"])

    def _artifact(self, revision_id, path, metadata, name):
        return {
            "id": uid(),
            "kind": "artifact",
            "revision_id": revision_id,
            "name": name,
            "relative_path": str(path.relative_to(self.store.root)),
            **metadata,
            "ownership": "Unfold-managed",
            "format": "mp4",
            "time_basis": "composition seconds",
        }

    def _produce(self, brief, grant, base=None, feedback="", request_id=None):
        brief = Brief.model_validate(brief)
        grant = Grant.model_validate(grant)
        if not (grant.allow_context and grant.allow_frames and grant.vision):
            raise UnfoldError(
                "DISCLOSURE_REQUIRED",
                "This creative path requires context and sampled-frame disclosure to a vision model.",
                "Supply an explicit Grant permitting context and frames, with vision=True.",
            )
        self.backend.require()
        operation_id = request_id or uid()
        directory = self.store.workspace(operation_id)
        payload = {
            "brief": brief.model_dump(),
            "grant": grant.model_dump(),
            "base": base["id"] if base else None,
            "feedback": feedback,
        }
        request_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                previous = self.store.get(operation_id, "operation", db)
            except UnfoldError as exc:
                if exc.code != "NOT_FOUND":
                    raise
            else:
                if previous["request_sha256"] != request_hash:
                    raise UnfoldError(
                        "REQUEST_CONFLICT", "Request identity was already used for different input."
                    )
                return (
                    previous  # Includes uncertain/running/failed states; never silently re-spend.
                )
            if base:
                project = self.store.get(base["project_id"], "project", db)
                if project["current_revision"] != base["id"]:
                    raise UnfoldError(
                        "STALE_BASE",
                        "Feedback targets an earlier revision.",
                        "Use the current revision explicitly.",
                    )
            else:
                project = {
                    "id": uid(),
                    "kind": "project",
                    "name": brief.title,
                    "current_revision": None,
                    "revisions": [],
                }
                self.store.put("project", project, db)
            operation = {
                "id": operation_id,
                "kind": "operation",
                "project_id": project["id"],
                "status": "running",
                "request_sha256": request_hash,
                **payload,
            }
            self.store.put("operation", operation, db)
            self.store.event("started", operation_id, {"project_id": project["id"]}, db)
        if base:
            payload["base_scene"] = json.loads(
                (Path(base["source_path"]) / "scene.json").read_text()
            )
        write_json(
            directory / "request.json",
            {
                **payload,
                "library": str(self.store.root),
                "backend": str(self.backend.root),
                "operation_id": operation_id,
            },
        )
        process = None
        try:
            with (directory / "worker.log").open("w") as log:
                process = subprocess.Popen(
                    [sys.executable, "-m", "unfold.worker", str(directory / "request.json")],
                    stdout=log,
                    stderr=log,
                    start_new_session=True,
                )
                deadline = time.monotonic() + grant.max_seconds
                while process.poll() is None:
                    if self.store.get(operation_id, "operation")["status"] == "cancelling":
                        raise UnfoldError(
                            "CANCELLED",
                            "Operation was cancelled; prior revisions remain available.",
                        )
                    if time.monotonic() > deadline:
                        raise UnfoldError(
                            "RESOURCE_LIMIT", "Operation wall-clock allowance exhausted."
                        )
                    time.sleep(0.1)
            result_path = directory / "result.json"
            if not result_path.exists():
                raise UnfoldError(
                    "WORKER_FAILED",
                    "The isolated Amplifier worker stopped without a result.",
                    "Inspect the local worker log and prerequisites; retry requires a new request identity.",
                )
            result = json.loads(result_path.read_text())
            if "error" in result:
                raise UnfoldError(**result["error"])
            source = directory / "source"
            video = directory / "video.mp4"
            if (
                self.backend.source_hash(source) != result["source_sha256"]
                or digest(video) != result["render"]["sha256"]
            ):
                raise UnfoldError("STALE_RESULT", "Source or video changed after agent inspection.")
            self.backend.probe(video)
            revision_id = uid()
            artifact = self._artifact(revision_id, video, result["render"], project["name"])
            revision = {
                "id": revision_id,
                "kind": "revision",
                "project_id": project["id"],
                "base_revision": base["id"] if base else None,
                "brief": brief.model_dump(),
                "feedback": feedback,
                "source": str(source.relative_to(self.store.root)),
                "artifacts": [artifact["id"]],
                "operation_id": operation_id,
                **result,
            }
            with self.store.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                operation = self.store.get(operation_id, "operation", db)
                current = self.store.get(project["id"], "project", db)
                if operation["status"] != "running":
                    raise UnfoldError("CANCELLED", "Late result cannot commit after cancellation.")
                if current["current_revision"] != project["current_revision"]:
                    raise UnfoldError(
                        "STALE_BASE",
                        "Another operation committed first; result retained as uncommitted work.",
                    )
                current["current_revision"] = revision_id
                current["revisions"].append(revision_id)
                operation.update(status="completed", revision_id=revision_id)
                for kind, record in (
                    ("revision", revision),
                    ("artifact", artifact),
                    ("project", current),
                    ("operation", operation),
                ):
                    self.store.put(kind, record, db)
                self.store.event("completed", operation_id, {"revision_id": revision_id}, db)
            return operation
        except (Exception, KeyboardInterrupt) as exc:
            self._stop_worker(process)
            error = (
                exc
                if isinstance(exc, UnfoldError)
                else UnfoldError(
                    "INTERRUPTED" if isinstance(exc, KeyboardInterrupt) else "EXECUTION_FAILED",
                    "Work stopped without a committed result.",
                )
            )
            operation = self.store.get(operation_id, "operation")
            operation.update(
                status="cancelled" if error.code == "CANCELLED" else "failed", error=error.as_dict()
            )
            with self.store.connect() as db:
                self.store.put("operation", operation, db)
                self.store.event(operation["status"], operation_id, error.as_dict(), db)
            return operation
        finally:
            self._stop_worker(process)

    @staticmethod
    def _stop_worker(process):
        if process:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=10)

    def dashboard(self, port=0):
        from .dashboard import Dashboard

        return Dashboard(self, port)
