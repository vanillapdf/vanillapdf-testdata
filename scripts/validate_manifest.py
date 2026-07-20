#!/usr/bin/env python3
"""Validate manifest.json against the repository contents.

The manifest is the contract every consumer reads, so it has to stay in sync
with what is actually committed. This checks both directions.

    python scripts/validate_manifest.py            # consistency only
    python scripts/validate_manifest.py --strict   # also require files on disk

--strict additionally verifies every fixture against its recorded sha256, so
it detects a file edited in place. It is the form CI runs.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

DATA_DIRS = ("corpus", "broken", "analysis")
# What the artifact is, and what state it is in — deliberately orthogonal.
# Encryption is not a type or a status: it is expressed by the password fields.
TYPES = {"pdf": (".pdf",), "certificate": (".pfx",)}
STATUSES = {"valid", "broken"}
# A consumer enumerates tests as type == "pdf" and status == "valid".

# Staging directories hold what the parser cannot handle; corpus/ holds what it
# can. A passing fixture in staging should have been promoted or dropped.
DIRECTORY_STATUS = {"broken": "broken", "analysis": "broken", "corpus": "valid"}

SKIPS = {"process", "save", "edit", "incremental_save"}
FIELDS = {
    "type", "status", "user_password", "owner_password", "certificate",
    "skip", "expect", "source", "license", "note", "sha256",
}
# Paths in the config block that must point at a manifest entry.
CONFIG_PATHS = ("merge_file", "signing_certificate")


def digest(path: Path) -> str:
    with open(path, "rb") as fh:
        return hashlib.file_digest(fh, "sha256").hexdigest()


def discover(root: Path) -> set:
    """Every committed fixture, as a repo-relative POSIX path."""
    found = set()
    for name in DATA_DIRS:
        for path in (root / name).rglob("*"):
            if path.is_file() and path.name != ".gitkeep":
                found.add(path.relative_to(root).as_posix())
    return found


def validate(manifest: dict, root: Path, strict: bool) -> list:
    errors = []
    warnings = []
    on_disk = discover(root)

    files = manifest.get("files")
    if not isinstance(files, dict):
        return ['"files" is missing or not an object']

    for path, entry in sorted(files.items()):
        where = f"{path}:"

        if not isinstance(entry, dict):
            errors.append(f"{where} entry is not an object")
            continue

        unknown = set(entry) - FIELDS
        if unknown:
            errors.append(f"{where} unknown field(s) {sorted(unknown)}")

        kind = entry.get("type")
        status = entry.get("status")
        if kind not in TYPES:
            errors.append(f"{where} type {kind!r} not in {sorted(TYPES)}")
        elif not path.lower().endswith(TYPES[kind]):
            errors.append(f"{where} type {kind!r} disagrees with the file extension")
        if status not in STATUSES:
            errors.append(f"{where} status {status!r} not in {sorted(STATUSES)}")

        bad_skips = set(entry.get("skip", [])) - SKIPS
        if bad_skips:
            errors.append(f"{where} unknown skip value(s) {sorted(bad_skips)}")

        expected = DIRECTORY_STATUS.get(path.split("/")[0])
        # A certificate is an input, not something the parser is asked to handle,
        # so the directory's status expectation does not apply to it.
        if expected and kind != "certificate" and status != expected:
            errors.append(f"{where} lives under {path.split('/')[0]}/ "
                          f"but status is {status!r}, expected {expected!r}")

        # Every path is rooted in this repository — nothing may point outside it.
        cert = entry.get("certificate")
        if cert is not None and cert not in files:
            errors.append(f"{where} certificate {cert!r} has no manifest entry")

        if not entry.get("source"):
            errors.append(f"{where} missing source")
        if not entry.get("license"):
            errors.append(f"{where} missing license")

        if path not in on_disk:
            (errors if strict else warnings).append(f"{where} no such file")
            continue

        # The recorded hash is what makes the manifest self-verifying: it catches
        # a fixture edited in place, corrupted, or mangled by an EOL conversion —
        # none of which an archive-level checksum would see.
        recorded = entry.get("sha256")
        if not recorded:
            errors.append(f"{where} missing sha256")
        elif strict and (actual := digest(root / path)) != recorded:
            errors.append(f"{where} sha256 {actual[:12]}, recorded {recorded[:12]}")

    for path in sorted(on_disk - set(files)):
        errors.append(f"{path}: on disk but absent from manifest")

    config = manifest.get("config", {})
    for key in CONFIG_PATHS:
        value = config.get(key)
        if value is None:
            errors.append(f"config.{key} is missing")
        elif value not in files:
            errors.append(f"config.{key} {value!r} has no manifest entry")

    for line in warnings:
        print(f"warning: {line}")
    if warnings:
        print(f"warning: {len(warnings)} file(s) not yet imported "
              f"(expected until the corpus import lands)\n")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                        help="repository root (default: current directory)")
    parser.add_argument("--strict", action="store_true",
                        help="require every file on disk and verify its sha256")
    args = parser.parse_args()

    manifest = json.loads((args.root / "manifest.json").read_text(encoding="utf-8"))
    errors = validate(manifest, args.root, args.strict)

    if errors:
        for line in errors:
            print(f"error: {line}", file=sys.stderr)
        print(f"\n{len(errors)} error(s)", file=sys.stderr)
        return 1

    print(f"ok: {len(manifest['files'])} manifest entries validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
