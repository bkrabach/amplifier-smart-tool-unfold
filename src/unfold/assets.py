"""Deterministic creative assets, immutable pack versions and portable ZIP exchange."""

import hashlib
import json
import mimetypes
import re
import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath

from .models import UnfoldError
from .store import digest, portable_archive, uid

MAX_PACK = 256 * 1024 * 1024
MAX_FILES = 256


def label(value):
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= 120:
        raise UnfoldError("INVALID_INPUT", "Use a name of 1–120 characters.")
    return value.strip()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


class Assets:
    def assets(self):
        return [self.asset(a["id"]) for a in self.store.list("asset")]

    def asset(self, asset_id):
        a = self.store.get(asset_id, "asset")
        path = (
            Path(a["external_path"])
            if a["ownership"] == "external reference"
            else self.store.root / a["relative_path"]
        )
        a["path"] = str(path)
        a["integrity"] = (
            "intact" if path.is_file() and digest(path) == a["sha256"] else "changed_or_missing"
        )
        return a

    def import_asset(
        self, path, name=None, role="image", mode="copy", rights="unknown", attribution=""
    ):
        path = Path(path).expanduser().resolve()
        if role not in (
            "image",
            "video",
            "audio",
            "font",
            "example",
            "motion",
            "recipe",
        ) or mode not in ("copy", "reference"):
            raise UnfoldError("INVALID_INPUT", "Unsupported asset role or intake mode.")
        if not path.is_file() or path.stat().st_size > MAX_PACK:
            raise UnfoldError("INVALID_INPUT", "Choose a file up to 256 MiB.")
        if rights not in ("unknown", "redistributable", "restricted"):
            raise UnfoldError(
                "INVALID_INPUT", "Rights must be unknown, redistributable or restricted."
            )
        identity = uid()
        suffix = path.suffix.lower()
        if not re.fullmatch(r"\.[a-z0-9]{1,10}", suffix):
            suffix = ".bin"
        record = {
            "id": identity,
            "kind": "asset",
            "name": label(name or path.stem),
            "role": role,
            "sha256": digest(path),
            "bytes": path.stat().st_size,
            "suffix": suffix,
            "mime": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
            "rights": rights,
            "attribution": attribution,
            "ownership": "external reference" if mode == "reference" else "Unfold-managed",
        }
        if mode == "reference":
            record["external_path"] = str(path)
        else:
            destination = self.store.root / "assets" / (identity + suffix)
            destination.parent.mkdir(exist_ok=True)
            shutil.copyfile(path, destination)
            if digest(destination) != record["sha256"]:
                destination.unlink()
                raise UnfoldError(
                    "SOURCE_CHANGED", "Input changed during copy. Original preserved."
                )
            record["relative_path"] = str(destination.relative_to(self.store.root))
        with self.store.connect() as db:
            self.store.put("asset", record, db)
            self.store.event(
                "asset_imported",
                identity,
                {"mode": mode, "original": str(path), "original_preserved": True},
                db,
            )
        return self.asset(identity)

    def update_asset(self, asset_id, rights=None, attribution=None):
        record = self.store.get(asset_id, "asset")
        if rights is not None:
            if rights not in ("unknown", "redistributable", "restricted"):
                raise UnfoldError(
                    "INVALID_INPUT", "Choose unknown, redistributable or restricted rights."
                )
            record["rights"] = rights
        if attribution is not None:
            if not isinstance(attribution, str) or len(attribution) > 2000:
                raise UnfoldError(
                    "INVALID_INPUT", "Attribution must be text up to 2000 characters."
                )
            record["attribution"] = attribution
        self.store.put("asset", record)
        self.store.event("asset_metadata_updated", asset_id, {"rights": record["rights"]})
        return self.asset(asset_id)

    def packs(self):
        return self.store.list("pack")

    def save_pack(self, name, guidance, asset_ids=None, pack_id=None, prerequisites=None):
        name = label(name)
        if not isinstance(guidance, dict) or len(json.dumps(guidance)) > 20000:
            raise UnfoldError("INVALID_INPUT", "Guidance must be a JSON object up to 20 KB.")
        assets = [self.asset(i) for i in dict.fromkeys(asset_ids or [])]
        if any(a["integrity"] != "intact" for a in assets):
            raise UnfoldError(
                "MATERIAL_CHANGED", "Repair changed or missing assets before creating a version."
            )
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            for asset in assets:
                self.store.get(asset["id"], "asset", db)
                if self.asset(asset["id"])["integrity"] != "intact":
                    raise UnfoldError("MATERIAL_CHANGED", "Asset changed while creating pack.")
            pack = (
                self.store.get(pack_id, "pack", db)
                if pack_id
                else {"id": uid(), "kind": "pack", "versions": []}
            )
            version = {
                "id": uid(),
                "kind": "pack_version",
                "pack_id": pack["id"],
                "number": len(pack["versions"]) + 1,
                "guidance": guidance,
                "assets": [a["id"] for a in assets],
                "asset_hashes": {a["id"]: a["sha256"] for a in assets},
                "prerequisites": prerequisites or [],
            }
            pack.update(name=name, current_version=version["id"])
            pack["versions"].append(version["id"])
            self.store.put("pack_version", version, db)
            self.store.put("pack", pack, db)
            self.store.event("pack_version_created", pack["id"], {"version_id": version["id"]}, db)
        return {**pack, "version": version}

    def duplicate_pack(self, pack_id, name):
        pack = self.store.get(pack_id, "pack")
        version = self.store.get(pack["current_version"], "pack_version")
        result = self.save_pack(
            name, version["guidance"], version["assets"], prerequisites=version["prerequisites"]
        )
        self.store.event(
            "pack_duplicated", result["id"], {"origin": pack_id, "version": version["id"]}
        )
        return result

    def dependencies(self, identity):
        record = self.store.get(identity)
        targets = [identity] + record.get("versions", [])
        found = []
        for kind in ("pack_version", "project", "revision", "delivery"):
            for r in self.store.list(kind):
                if r["id"] not in targets and any(
                    i in r.get("assets", [])
                    or i == r.get("identity_version")
                    or i in r.get("dependencies", [])
                    or i == r.get("brief", {}).get("reference_id")
                    for i in targets
                ):
                    found.append({"id": r["id"], "kind": kind})
        return found

    def remove(self, identity):
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            record = self.store.get(identity, db=db)
            if record["kind"] not in ("asset", "pack", "artifact"):
                raise UnfoldError(
                    "UNSUPPORTED", "Removal supports assets, packs and generated outputs."
                )
            targets = [identity] + record.get("versions", [])
            dependents = []
            for row in db.execute(
                "SELECT data FROM records WHERE kind IN ('pack_version','project','revision','delivery')"
            ):
                item = json.loads(row[0])
                if item["id"] not in targets and any(
                    i in item.get("assets", [])
                    or i in item.get("dependencies", [])
                    or i == item.get("identity_version")
                    or i == item.get("brief", {}).get("reference_id")
                    for i in targets
                ):
                    dependents.append({"id": item["id"], "kind": item["kind"]})
            if dependents:
                raise UnfoldError(
                    "IN_USE", "Retained work depends on this item: " + json.dumps(dependents)
                )
            removed, missing = [], []
            if record.get("relative_path"):
                path = self.store.root / record["relative_path"]
                if path.exists():
                    path.unlink()
                    removed.append(str(path))
                else:
                    missing.append(str(path))
            if record["kind"] == "artifact":
                revision = self.store.get(record["revision_id"], "revision", db)
                revision["artifacts"] = [i for i in revision["artifacts"] if i != identity]
                self.store.put("revision", revision, db)
            for target in targets:
                db.execute("DELETE FROM records WHERE id=?", (target,))
            result = {
                "id": identity,
                "removed": removed,
                "missing": missing,
                "external_originals_preserved": True,
            }
            self.store.event("removed", identity, result, db)
        return result

    def export_pack(self, version_id, destination):
        version = self.store.get(version_id, "pack_version")
        pack = self.store.get(version["pack_id"], "pack")
        manifest = {
            "format": "unfold.identity",
            "version": 1,
            "pack_id": pack["id"],
            "version_id": version_id,
            "number": version["number"],
            "name": pack["name"],
            "guidance": version["guidance"],
            "prerequisites": version["prerequisites"],
            "assets": [],
            "omissions": [],
        }
        included = []
        for asset_id in version["assets"]:
            a = self.asset(asset_id)
            if a["integrity"] != "intact" or a["sha256"] != version["asset_hashes"][asset_id]:
                raise UnfoldError("MATERIAL_CHANGED", "Pack asset differs from its pinned version.")
            if a["rights"] != "redistributable":
                manifest["omissions"].append(
                    {
                        "name": a["name"],
                        "role": a["role"],
                        "reason": a["rights"] + " redistribution rights",
                        "sha256": a["sha256"],
                    }
                )
                continue
            entry = {
                k: a[k]
                for k in (
                    "id",
                    "name",
                    "role",
                    "sha256",
                    "bytes",
                    "suffix",
                    "mime",
                    "rights",
                    "attribution",
                )
            }
            entry["file"] = "assets/" + a["id"] + a["suffix"]
            manifest["assets"].append(entry)
            included.append((a["path"], entry["file"]))
        if sum(a["bytes"] for a in manifest["assets"]) > MAX_PACK:
            raise UnfoldError("PACK_LIMIT", "Pack exceeds 256 MiB.")
        destination = Path(destination).expanduser().resolve()
        try:
            with portable_archive(destination) as archive:
                archive.writestr("manifest.json", json.dumps(manifest, indent=2))
                for path, relative in included:
                    archive.write(path, relative)
        except FileExistsError:
            raise UnfoldError("OUTPUT_EXISTS", "Choose a new ZIP destination.") from None
        self.store.event(
            "pack_exported",
            version_id,
            {"path": str(destination), "omissions": manifest["omissions"]},
        )
        return {"path": str(destination), "manifest": manifest, "sha256": digest(destination)}

    def inspect_pack(self, path):
        """Validate everything before exposing contents. Never extract or execute ZIP code."""
        try:
            if Path(path).stat().st_size > MAX_PACK + 1024 * 1024:
                raise ValueError("Archive exceeds 257 MiB on disk.")
            with zipfile.ZipFile(path) as archive:
                entries = archive.infolist()
                names = [e.filename for e in entries]
                if (
                    len(entries) > MAX_FILES
                    or sum(e.file_size for e in entries) > MAX_PACK
                    or len(names) != len(set(names))
                ):
                    raise ValueError("Archive exceeds limits or has duplicate entries.")
                for e in entries:
                    p = PurePosixPath(e.filename)
                    if (
                        p.is_absolute()
                        or ".." in p.parts
                        or "\\" in e.filename
                        or stat.S_ISLNK(e.external_attr >> 16)
                        or e.flag_bits & 1
                    ):
                        raise ValueError("Unsafe archive entry.")
                if "manifest.json" not in names:
                    raise ValueError("Missing manifest.json. Select an Unfold identity ZIP.")
                if archive.getinfo("manifest.json").file_size > 1000000:
                    raise ValueError("Manifest too large.")
                m = json.loads(archive.read("manifest.json"))
                if m["format"] != "unfold.identity" or m["version"] != 1:
                    raise ValueError("Unsupported pack format/version.")
                label(m["name"])
                if not isinstance(m["guidance"], dict) or not isinstance(m["prerequisites"], list):
                    raise ValueError("Invalid guidance or prerequisites.")
                if (
                    not isinstance(m.get("omissions"), list)
                    or not isinstance(m.get("assets"), list)
                    or not isinstance(m.get("number"), int)
                    or m["number"] < 1
                ):
                    raise ValueError("Invalid pack version, omissions or asset list.")
                for key in ("pack_id", "version_id"):
                    if not re.fullmatch("[a-f0-9]{32}", m[key]):
                        raise ValueError("Invalid pack identity.")
                files = []
                for a in m["assets"]:
                    label(a["name"])
                    if (
                        a["role"]
                        not in ("image", "audio", "video", "font", "example", "motion", "recipe")
                        or not isinstance(a["attribution"], str)
                        or len(a["attribution"]) > 2000
                        or not isinstance(a["mime"], str)
                    ):
                        raise ValueError("Invalid asset metadata.")
                    if not re.fullmatch("[a-f0-9]{32}", a["id"]) or not re.fullmatch(
                        r"\.[a-z0-9]{1,10}", a["suffix"]
                    ):
                        raise ValueError("Invalid asset identity.")
                    if (
                        a["file"] != "assets/" + a["id"] + a["suffix"]
                        or a["rights"] != "redistributable"
                    ):
                        raise ValueError("Invalid asset manifest.")
                    raw = archive.read(a["file"])
                    if len(raw) != a["bytes"] or hashlib.sha256(raw).hexdigest() != a["sha256"]:
                        raise ValueError("Asset integrity mismatch.")
                    files.append(a["file"])
                if len(files) != len(set(files)) or set(names) != {"manifest.json", *files}:
                    raise ValueError("Archive contents do not match manifest.")
                return {"manifest": m, "sha256": digest(path), "bytes": Path(path).stat().st_size}
        except (ValueError, KeyError, TypeError, zipfile.BadZipFile, RuntimeError) as exc:
            raise UnfoldError("INVALID_PACK", str(exc)) from None

    def import_pack(self, path, expected_sha256=None, conflict="refuse"):
        if conflict not in ("refuse", "copy"):
            raise UnfoldError("INVALID_INPUT", "Conflict policy must be refuse or copy.")
        checked = self.inspect_pack(path)
        if expected_sha256 and checked["sha256"] != expected_sha256:
            raise UnfoldError("SOURCE_CHANGED", "ZIP changed after inspection.")
        m = checked["manifest"]
        # Local IDs never trust foreign IDs. A receipt detects repeat/conflicting claims.
        claim_id = "import-" + m["version_id"]
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                prior = self.store.get(claim_id, "pack_import", db)
            except UnfoldError:
                prior = None
            if prior:
                if prior["manifest_hash"] == fingerprint(m):
                    return prior
                if conflict == "copy":
                    claim_id = "import-" + uid()
                else:
                    raise UnfoldError(
                        "PACK_CONFLICT",
                        "That version identity already names different content. Export a new version.",
                    )
            created = []
            try:
                with zipfile.ZipFile(path) as archive:
                    for a in m["assets"]:
                        identity = uid()
                        relative = "assets/" + identity + a["suffix"]
                        dest = self.store.root / relative
                        dest.parent.mkdir(exist_ok=True)
                        dest.write_bytes(archive.read(a["file"]))
                        created.append(dest)
                        if digest(dest) != a["sha256"]:
                            raise UnfoldError("SOURCE_CHANGED", "ZIP changed while importing.")
                        record = {
                            k: a[k]
                            for k in (
                                "name",
                                "role",
                                "sha256",
                                "bytes",
                                "suffix",
                                "mime",
                                "rights",
                                "attribution",
                            )
                        }
                        record.update(
                            id=identity,
                            kind="asset",
                            ownership="Unfold-managed",
                            relative_path=relative,
                            origin_id=a["id"],
                        )
                        self.store.put("asset", record, db)
                pack_id, version_id = uid(), uid()
                assets = [p.stem for p in created]
                version = {
                    "id": version_id,
                    "kind": "pack_version",
                    "pack_id": pack_id,
                    "number": 1,
                    "guidance": m["guidance"],
                    "assets": assets,
                    "asset_hashes": {i: a["sha256"] for i, a in zip(assets, m["assets"])},
                    "prerequisites": m["prerequisites"] + m.get("omissions", []),
                    "origin_version": m["version_id"],
                    "origin_number": m["number"],
                }
                pack = {
                    "id": pack_id,
                    "kind": "pack",
                    "name": m["name"],
                    "versions": [version_id],
                    "current_version": version_id,
                    "origin_id": m["pack_id"],
                }
                receipt = {
                    "id": claim_id,
                    "kind": "pack_import",
                    "pack_id": pack_id,
                    "version_id": version_id,
                    "manifest_hash": fingerprint(m),
                    "sha256": checked["sha256"],
                }
                for kind, r in (
                    ("pack", pack),
                    ("pack_version", version),
                    ("pack_import", receipt),
                ):
                    self.store.put(kind, r, db)
                self.store.event("pack_imported", pack_id, receipt, db)
            except Exception:
                for p in created:
                    p.unlink(missing_ok=True)
                raise
        return receipt
