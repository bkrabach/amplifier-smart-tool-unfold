"""Library-owned feedback authority, durable drafts and asynchronous refinement."""

import hashlib
import json
import os
import subprocess
import sys
import threading
import time

from .models import Grant, UnfoldError
from .store import uid


class Review:
    def authorize_review(self, project_id, grant, refinements=1):
        self.store.get(project_id, "project")
        grant = Grant.model_validate(grant)
        if not 1 <= refinements <= 10:
            raise UnfoldError("INVALID_INPUT", "Authorize 1–10 bounded refinements.")
        record = {
            "id": project_id + "-authority",
            "kind": "authority",
            "project_id": project_id,
            "grant": grant.model_dump(),
            "remaining": refinements,
        }
        self.store.put("authority", record)
        self.store.event("review_authorized", project_id, {"remaining": refinements})
        return record

    def save_draft(self, revision_id, text, at=0, end=None, sequence=0):
        revision = self.store.get(revision_id, "revision")
        duration = revision.get("brief", {}).get("duration", 60)
        if not isinstance(text, str) or len(text) > 5000 or not 0 <= at <= duration:
            raise UnfoldError("INVALID_INPUT", "Invalid draft or time.")
        if end is not None and not at <= end <= duration:
            raise UnfoldError("INVALID_INPUT", "Interval must fit the revision.")
        record = {
            "id": revision_id + "-draft",
            "kind": "draft",
            "revision_id": revision_id,
            "text": text,
            "at": at,
            "end": end,
            "sequence": sequence,
        }
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                old = self.store.get(record["id"], "draft", db)
                if old["sequence"] >= sequence:
                    return old
                if old.get("submitted_job") and all(
                    old.get(k) == record.get(k) for k in ("text", "at", "end")
                ):
                    record["submitted_job"] = old["submitted_job"]
            except UnfoldError:
                pass
            self.store.put("draft", record, db)
        return record

    def submit_refinement(
        self, revision_id, text, request_id, at=0, end=None, identity_version=None
    ):
        """Accept once, consume one existing project grant, then launch owned work."""
        self.store.workspace(request_id)  # validates caller retry identity
        rev = self.store.get(revision_id, "revision")
        if not isinstance(text, str) or not text.strip() or len(text) > 5000:
            raise UnfoldError("INVALID_INPUT", "Write feedback before applying it.")
        duration = rev.get("brief", {}).get("duration", 60)
        if not 0 <= at <= duration or (end is not None and not at <= end <= duration):
            raise UnfoldError("INVALID_INPUT", "Feedback time must fit the viewed revision.")
        payload = {
            "revision_id": revision_id,
            "text": text,
            "at": at,
            "end": end,
            "identity_version": identity_version,
        }
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                old = self.store.get(request_id, "review_job", db)
            except UnfoldError:
                old = None
            if old:
                if old["fingerprint"] != fingerprint:
                    raise UnfoldError("REQUEST_CONFLICT", "Retry identity has different feedback.")
                return old
            project = self.store.get(rev["project_id"], "project", db)
            if project["current_revision"] != revision_id:
                raise UnfoldError(
                    "STALE_BASE",
                    "A newer revision exists. Open it and adapt your feedback; your draft stays on this version.",
                )
            try:
                authority = self.store.get(project["id"] + "-authority", "authority", db)
            except UnfoldError:
                raise UnfoldError(
                    "AUTHORITY_REQUIRED", "Caller must authorize dashboard refinement first."
                ) from None
            if authority["remaining"] < 1:
                raise UnfoldError(
                    "AUTHORITY_EXHAUSTED", "Ask the caller for another refinement allowance."
                )
            busy = db.execute("SELECT data FROM records WHERE kind='review_job'").fetchall()
            if any(
                (j := json.loads(row[0]))["project_id"] == project["id"]
                and j["status"] in ("queued", "running", "cancelling")
                for row in busy
            ):
                raise UnfoldError("BUSY", "This project already has refinement work in progress.")
            note = {
                "id": uid(),
                "kind": "feedback",
                "project_id": project["id"],
                **payload,
                "status": "pending",
                "job_id": request_id,
            }
            job = {
                "id": request_id,
                "kind": "review_job",
                **payload,
                "fingerprint": fingerprint,
                "project_id": project["id"],
                "feedback_id": note["id"],
                "operation_id": uid(),
                "status": "queued",
                "grant": authority["grant"],
                "created": time.time(),
            }
            authority["remaining"] -= 1
            self.store.put("authority", authority, db)
            self.store.put("feedback", note, db)
            self.store.put("review_job", job, db)
            try:
                draft = self.store.get(revision_id + "-draft", "draft", db)
                if all(draft.get(k) == payload.get(k) for k in ("text", "at", "end")):
                    draft["submitted_job"] = request_id
                    self.store.put("draft", draft, db)
            except UnfoldError:
                pass
            self.store.event(
                "refinement_accepted", request_id, {"feedback_id": note["id"], **payload}, db
            )
        try:
            logpath = self.store.workspace(request_id) / "review.log"
            with logpath.open("w") as log:
                child = subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "unfold.review_worker",
                        str(self.store.root),
                        str(self.backend.root),
                        request_id,
                    ],
                    stdout=log,
                    stderr=log,
                    start_new_session=True,
                )
            threading.Thread(target=child.wait, daemon=True).start()
            with self.store.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                job = self.store.get(request_id, "review_job", db)
                job["pid"] = child.pid
                self.store.put("review_job", job, db)
        except OSError:
            job.update(
                status="failed",
                error="Could not start refinement. Allowance was consumed; explicit authorization is needed to retry.",
            )
            self.store.put("review_job", job)
        return job

    def run_review_job(self, job_id):
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            job = self.store.get(job_id, "review_job", db)
            if job["status"] != "queued":
                return job
            job.update(status="running", pid=os.getpid())
            self.store.put("review_job", job, db)
        try:
            result = self.revise(
                job["revision_id"],
                job["text"],
                Grant.model_validate(job["grant"]),
                request_id=job["operation_id"],
                target={"at": job["at"], "end": job["end"]},
                identity_version=job.get("identity_version"),
            )
            if result["status"] == "completed":
                self.address_feedback(job["feedback_id"], result["revision_id"])
            with self.store.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                current = self.store.get(job_id, "review_job", db)
                current.update(status=result["status"], result=result)
                self.store.put("review_job", current, db)
                self.store.event("refinement_" + result["status"], job_id, result, db)
                return current
        except Exception as exc:
            job.update(
                status="cancelled"
                if isinstance(exc, UnfoldError) and exc.code == "CANCELLED"
                else "failed",
                error=str(exc),
            )
            self.store.put("review_job", job)
            self.store.event("refinement_failed", job_id, {"error": str(exc)})
            return job

    def cancel_refinement(self, job_id):
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            job = self.store.get(job_id, "review_job", db)
            if job["status"] == "queued":
                job["status"] = "cancelled"
            elif job["status"] == "running":
                job["status"] = "cancelling"
            self.store.put("review_job", job, db)
            self.store.event("refinement_cancel_requested", job_id, {}, db)
        try:
            self.cancel(job["operation_id"])
        except UnfoldError:
            pass
        return job

    def review_state(self):
        jobs = self.store.list("review_job")
        for job in jobs:
            if job["status"] not in ("queued", "running", "cancelling"):
                continue
            alive = False
            if job.get("pid"):
                try:
                    os.kill(job["pid"], 0)
                    alive = True
                except ProcessLookupError:
                    pass
            elif time.time() - job["created"] < 10:
                alive = True
            if alive:
                continue
            try:
                operation = self.store.get(job["operation_id"], "operation")
            except UnfoldError:
                operation = None
            if operation and operation["status"] == "completed":
                self.address_feedback(job["feedback_id"], operation["revision_id"])
                job.update(status="completed", result=operation)
            else:
                if operation:
                    self.cancel(operation["id"])
                    self._stop_recorded_worker(operation)
                job.update(
                    status="interrupted",
                    error="Worker stopped. No automatic retry or additional spending.",
                )
            with self.store.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                current = self.store.get(job["id"], "review_job", db)
                if current["status"] in ("queued", "running", "cancelling"):
                    self.store.put("review_job", job, db)
                    self.store.event(
                        "refinement_recovered", job["id"], {"status": job["status"]}, db
                    )
        return {
            "projects": self.projects(),
            "revisions": [self.inspect(r) for p in self.projects() for r in p["revisions"]],
            "events": self.observe(),
            "jobs": self.store.list("review_job"),
            "drafts": self.store.list("draft"),
            "authorities": self.store.list("authority"),
            "assets": self.assets(),
            "packs": self.packs(),
            "versions": self.store.list("pack_version"),
            "deliveries": self.store.list("delivery"),
            "outputs": [self.artifact(a["id"]) for a in self.store.list("artifact")],
        }

    def _stop_recorded_worker(self, operation):
        """Recover an orphan only if its command still identifies this exact owned request."""
        pid = operation.get("worker_pid")
        if not pid:
            return
        expected = str(self.store.workspace(operation["id"]) / "request.json")
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="], capture_output=True, text=True
        )
        if "unfold.worker" in result.stdout and expected in result.stdout:
            import signal

            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        operation.update(
            status="failed",
            error={
                "code": "INTERRUPTED",
                "message": "Supervisor stopped; owned worker cleanup requested.",
            },
        )
        self.store.put("operation", operation)
