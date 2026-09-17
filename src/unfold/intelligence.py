"""Model-facing production capabilities and executable submission boundaries."""

import json
import threading
from pathlib import Path

from .backend import Backend
from .models import Grant, Scene, UnfoldError
from .store import Store, digest, uid


class Production:
    def __init__(self, request):
        self.request = request
        self.grant = Grant.model_validate(request["grant"])
        self.store = Store(request["library"])
        self.directory = self.store.workspace(request["operation_id"])
        self.backend = Backend(request["backend"])
        self.scene = None
        self.rendered = None
        self.observations = {}
        self.delivered = set()
        self.calls = self.model_calls = self.renders = self.frames = 0
        self.text_bytes = self.image_bytes = 0
        self.result = self.fatal = None
        self.lock = threading.Lock()

    def remaining(self):
        return {
            "model_calls": self.grant.max_model_calls - self.model_calls,
            "tool_calls": self.grant.max_tool_calls - self.calls,
            "renders": self.grant.max_renders - self.renders,
            "frames": self.grant.max_frames - self.frames,
        }

    def event(self, kind, data):
        self.store.event(kind, self.request["operation_id"], data)

    def call(self, action, payload):
        with self.lock:
            if self.result is not None:
                raise UnfoldError(
                    "ALREADY_SUBMITTED", "This operation has already submitted a result."
                )
            if self.store.get(self.request["operation_id"], "operation")["status"] != "running":
                raise UnfoldError("CANCELLED", "Operation is no longer active.")
            self.calls += 1
            if self.calls > self.grant.max_tool_calls:
                self.fatal = UnfoldError("RESOURCE_LIMIT", "Tool allowance exhausted.")
                raise self.fatal
            self.event("production", {"action": action, "call": self.calls})
            data = json.loads(payload)
            if action == "inspect":
                return {
                    "scene": self.scene.model_dump() if self.scene else None,
                    "base_scene": self.request.get("base_scene"),
                    "remaining": self.remaining(),
                }
            if action == "author":
                scene = Scene.model_validate(data)
                if scene.duration != self.request["brief"]["duration"]:
                    raise ValueError("Preserve the requested duration exactly.")
                self.backend.author(scene, self.directory / "source")
                self.scene, self.rendered = scene, None
                self.observations.clear()
                self.delivered.clear()
                return {
                    "authored": True,
                    "source_sha256": self.backend.source_hash(self.directory / "source"),
                }
            if action == "render":
                if not self.scene:
                    raise ValueError("Author a scene first.")
                if self.renders >= self.grant.max_renders:
                    raise ValueError(
                        "Render allowance exhausted; submit existing valid work or a limitation."
                    )
                self.renders += 1
                self.rendered = None
                self.observations.clear()
                self.delivered.clear()
                self.rendered = self.backend.render(
                    self.directory / "source", self.directory / "video.mp4"
                )
                self.event("rendered_preview", self.rendered)
                return self.rendered
            if action == "sample":
                if not self.rendered:
                    raise ValueError("Render the current scene first.")
                times = data["times"]
                if len(times) + self.frames > self.grant.max_frames:
                    raise ValueError("Frame allowance exhausted.")
                self.frames += len(times)
                evidence_id = uid()
                frames = self.backend.frames(
                    self.directory / "video.mp4", times, self.directory / ("samples-" + evidence_id)
                )
                evidence = {
                    "id": evidence_id,
                    "video_sha256": self.rendered["sha256"],
                    "source_sha256": self.rendered["source_sha256"],
                    "frames": frames,
                    "method": "decoded JPEG samples from encoded MP4",
                }
                self.observations[evidence_id] = evidence
                return {
                    "evidence_id": evidence_id,
                    "times": times,
                    "next": "Images will be delivered with the next model call; inspect before submitting.",
                }
            if action == "submit":
                if not self.rendered or not self.delivered:
                    raise ValueError(
                        "Render and sample current source, then inspect delivered images first."
                    )
                if (
                    self.backend.source_hash(self.directory / "source")
                    != self.rendered["source_sha256"]
                ):
                    raise ValueError("Source changed since rendering.")
                if digest(self.directory / "video.mp4") != self.rendered["sha256"]:
                    raise ValueError("Rendered bytes changed since inspection.")
                review = data.get("review", "")
                limitations = data.get("limitations", [])
                if not isinstance(review, str) or not 1 <= len(review) <= 5000:
                    raise ValueError("Provide a bounded review of the actual sampled images.")
                if (
                    not isinstance(limitations, list)
                    or len(limitations) > 20
                    or any(not isinstance(x, str) or len(x) > 1000 for x in limitations)
                ):
                    raise ValueError("Provide at most 20 short limitations.")
                evidence = [self.observations[i] for i in self.delivered]
                for observation in evidence:
                    for frame in observation["frames"]:
                        if digest(frame["path"]) != frame["sha256"]:
                            raise ValueError("Observation bytes changed.")
                        frame["path"] = str(Path(frame["path"]).relative_to(self.store.root))
                self.result = {
                    "source_sha256": self.rendered["source_sha256"],
                    "render": self.rendered,
                    "evidence": evidence,
                    "model_review": review,
                    "limitations": limitations
                    + [
                        "Sampled frames do not verify every intervening frame or motion smoothness.",
                        "Silent illustrative animation; not a captured execution or timing measurement.",
                        "Human review pending.",
                    ],
                    "backend": self.backend.doctor()["versions"],
                    "usage": {
                        "model_calls": self.model_calls,
                        "tool_calls": self.calls,
                        "renders": self.renders,
                        "frames": self.frames,
                        "text_bytes": self.text_bytes,
                        "image_bytes": self.image_bytes,
                    },
                }
                return {"submitted": True}
            if action == "limitation":
                self.fatal = UnfoldError(
                    "CREATIVE_LIMITATION", str(data.get("reason", "Unsupported request"))[:2000]
                )
                raise self.fatal
            raise ValueError("Unknown production action.")

    def tool(self):
        import asyncio

        from amplifier_core import ToolResult

        owner = self

        class Tool:
            name = "production"
            description = (
                "Author, render, inspect and submit a motion composition within the granted scope."
            )
            input_schema = {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["inspect", "author", "render", "sample", "submit", "limitation"],
                    },
                    "payload": {
                        "type": "string",
                        "description": "JSON object for the chosen action.",
                    },
                },
                "required": ["action", "payload"],
                "additionalProperties": False,
            }

            async def execute(self, input):
                try:
                    value = await asyncio.to_thread(owner.call, input["action"], input["payload"])
                    return ToolResult(success=True, output=value)
                except Exception as exc:
                    error = (
                        exc.as_dict()
                        if isinstance(exc, UnfoldError)
                        else {"message": str(exc)[:3000]}
                    )
                    return ToolResult(success=False, error=error)

        return Tool()
