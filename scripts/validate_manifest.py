#!/usr/bin/env python3
"""Validate manifest.json against the repository contents.

The manifest is the contract every consumer reads, so it has to stay in sync
with what is actually committed. This checks both directions.

    python scripts/validate_manifest.py            # consistency only
    python scripts/validate_manifest.py --strict   # also require files on disk

--strict fails while the corpus import is still pending; it is the form CI
should run once the fixtures land.
"""

import argparse
import json
import sys
from pathlib import Path

DATA_DIRS = ("corpus", "broken", "analysis")
CATEGORIES = {"valid", "encrypted", "certificate", "broken", "analysis"}
# Categories that are never executed as CI inputs.
UNTESTED = {"broken", "analysis"}
SKIPS = {"process", "save", "edit", "incremental_save"}
FIELDS = {
    "category", "user_password", "owner_password", "certificate",
    "skip", "expect", "tested", "source", "license",
}
# Paths in the config block that must point at a manifest entry.
CONFIG_PATHS = ("merge_file", "signing_certificate")


def discover(root: Path) -> set:
    """Every committed fixture, as a repo-relative POSIX path."""
    found = set()
    for name in DATA_DIRS:
        for path in (root / name).rglob("*"):
            if path.is_file() and path.name != ".gitkeep":
                found.add(path.relative_to(root).as_posix())
    return found


def validate(manifest: dict, on_disk: set, strict: bool) -> list:
    errors = []
    warnings = []

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

        category = entry.get("category")
        if category not in CATEGORIES:
            errors.append(f"{where} category {category!r} not in {sorted(CATEGORIES)}")

        bad_skips = set(entry.get("skip", [])) - SKIPS
        if bad_skips:
            errors.append(f"{where} unknown skip value(s) {sorted(bad_skips)}")

        # broken/ and analysis/ hold fixtures that must never reach CI as inputs,
        # and each directory must agree with the category of what it holds.
        if category in UNTESTED and entry.get("tested") is not False:
            errors.append(f'{where} category {category!r} requires "tested": false')
        for name in UNTESTED:
            if path.startswith(f"{name}/") and category != name:
                errors.append(f"{where} lives under {name}/ but category is {category!r}")

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
                        help="treat missing fixture files as errors")
    args = parser.parse_args()

    manifest = json.loads((args.root / "manifest.json").read_text(encoding="utf-8"))
    errors = validate(manifest, discover(args.root), args.strict)

    if errors:
        for line in errors:
            print(f"error: {line}", file=sys.stderr)
        print(f"\n{len(errors)} error(s)", file=sys.stderr)
        return 1

    print(f"ok: {len(manifest['files'])} manifest entries validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
