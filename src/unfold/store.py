"""Transactional records, stable identities and an ordered public change log."""

import hashlib
import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

from .models import UnfoldError


def uid():
    return uuid.uuid4().hex


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, data):
    path = Path(path)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n")
    temporary.replace(path)


class Store:
    def __init__(self, root):
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "operations").mkdir(exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS records (
                    id TEXT PRIMARY KEY, kind TEXT NOT NULL, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS events (
                    cursor INTEGER PRIMARY KEY AUTOINCREMENT, time REAL NOT NULL,
                    kind TEXT NOT NULL, subject TEXT NOT NULL, data TEXT NOT NULL);
            """)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.root / "library.sqlite3", timeout=15)
        try:
            with db:
                yield db
        finally:
            db.close()

    def get(self, identity, kind=None, db=None):
        if db is None:
            with self.connect() as connection:
                return self.get(identity, kind, connection)
        row = db.execute("SELECT kind,data FROM records WHERE id=?", (identity,)).fetchone()
        if not row or (kind and row[0] != kind):
            raise UnfoldError("NOT_FOUND", "No such " + (kind or "record") + ": " + identity)
        return json.loads(row[1])

    def put(self, kind, data, db=None):
        if db is None:
            with self.connect() as connection:
                return self.put(kind, data, connection)
        db.execute(
            "INSERT INTO records VALUES (?,?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data",
            (data["id"], kind, json.dumps(data)),
        )

    def event(self, kind, subject, data, db=None):
        if db is None:
            with self.connect() as connection:
                return self.event(kind, subject, data, connection)
        db.execute(
            "INSERT INTO events(time,kind,subject,data) VALUES(?,?,?,?)",
            (time.time(), kind, subject, json.dumps(data)),
        )

    def list(self, kind):
        with self.connect() as db:
            return [
                json.loads(r[0])
                for r in db.execute("SELECT data FROM records WHERE kind=? ORDER BY rowid", (kind,))
            ]

    def events(self, after=0):
        if after < 0:
            raise UnfoldError("INVALID_INPUT", "Cursor must be nonnegative.")
        with self.connect() as db:
            return [
                {
                    "cursor": r[0],
                    "time": r[1],
                    "kind": r[2],
                    "subject": r[3],
                    "data": json.loads(r[4]),
                }
                for r in db.execute("SELECT * FROM events WHERE cursor>? ORDER BY cursor", (after,))
            ]

    def workspace(self, operation_id):
        if len(operation_id) != 32 or any(c not in "0123456789abcdef" for c in operation_id):
            raise UnfoldError("INVALID_INPUT", "Invalid operation identity.")
        path = self.root / "operations" / operation_id
        path.mkdir(exist_ok=True)
        return path


@contextmanager
def portable_archive(destination):
    """Publish a complete ZIP without overwrite; failures never leave a partial export."""
    import os
    import tempfile
    import zipfile

    destination = Path(destination)
    descriptor, name = tempfile.mkstemp(prefix=".unfold-", suffix=".zip", dir=destination.parent)
    os.close(descriptor)
    temporary = Path(name)
    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as archive:
            yield archive
        try:
            os.link(temporary, destination)
        except FileExistsError:
            raise UnfoldError("OUTPUT_EXISTS", "Choose a new ZIP destination.") from None
    finally:
        temporary.unlink(missing_ok=True)
