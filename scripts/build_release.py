#!/usr/bin/env python3
"""Build the release archives for this corpus.

Each data directory ships as its own asset. Consumers pin only what they use:
the core build needs corpus/ alone, so bundling all three would make every CI
run download roughly three times what it reads.

    python scripts/build_release.py                    # build into dist/
    python scripts/build_release.py --only corpus      # one asset
    python scripts/build_release.py --summary out.md   # markdown asset table

Archives are reproducible: identical inputs produce a byte-identical file and
therefore a stable SHA256. Consumers pin those hashes via URL_HASH, so a hash
that drifted on every rebuild would make re-running this workflow silently
invalidate every pin downstream.

This is why the archive is not a one-line shutil.make_archive: that stamps the
current time into both the tar members and the gzip header. tarfile.add already
walks recursively and sorts each directory listing, so the only plumbing left is
wrapping the gzip layer to pin its timestamp.
"""

import argparse
import gzip
import hashlib
import sys
import tarfile
from pathlib import Path
from typing import NamedTuple, Self

DATA_DIRS = ("corpus", "broken", "analysis")


class Asset(NamedTuple):
    """A built archive and the facts a consumer needs to pin it."""

    path: Path
    size: int
    digest: str

    @classmethod
    def of(cls, path: Path) -> Self:
        with open(path, "rb") as fh:
            digest = hashlib.file_digest(fh, "sha256").hexdigest()
        return cls(path, path.stat().st_size, digest)

    @property
    def mib(self) -> float:
        return self.size / 1024**2

    @property
    def checksum_line(self) -> str:
        """sha256sum's own format, so `sha256sum -c SHA256SUMS` verifies it."""
        return f"{self.digest}  {self.path.name}\n"

    @property
    def summary_row(self) -> str:
        return f"| `{self.path.name}` | {self.mib:.1f} MiB | `{self.digest}` |"

    def __str__(self) -> str:
        return f"{self.digest}  {self.path.name}  ({self.mib:.1f} MiB)"


def _normalise(info: tarfile.TarInfo) -> tarfile.TarInfo | None:
    """Drop placeholders and strip everything that varies between checkouts.

    Timestamps and ownership differ on every machine and every clone. Left in,
    they change the archive bytes — and the hash — without any content change.
    """
    if Path(info.name).name == ".gitkeep":
        return None
    info.mtime = 0
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mode = 0o755 if info.isdir() else 0o644  # data, not programs
    return info


def build(directory: Path, out: Path) -> Asset:
    """Write directory to out as a deterministic .tar.gz, streaming as it goes."""
    out.parent.mkdir(parents=True, exist_ok=True)
    with (
        open(out, "wb") as fh,
        gzip.GzipFile(filename="", fileobj=fh, mode="wb", compresslevel=9, mtime=0) as gz,
        tarfile.open(fileobj=gz, mode="w", format=tarfile.GNU_FORMAT) as tar,
    ):
        tar.add(directory, arcname=directory.name, filter=_normalise)
    return Asset.of(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                        help="repository root (default: current directory)")
    parser.add_argument("--out", type=Path,
                        help="output directory (default: <root>/dist)")
    parser.add_argument("--only", action="append", choices=DATA_DIRS,
                        help="build a subset; repeatable")
    parser.add_argument("--summary", type=Path,
                        help="append a markdown asset table to this file")
    args = parser.parse_args()

    root = args.root
    out = args.out or root / "dist"
    wanted = args.only or list(DATA_DIRS)

    if missing := [name for name in wanted if not (root / name).is_dir()]:
        sys.exit(f"error: not present under {root}: {', '.join(missing)}. "
                 "The fixtures have not been imported yet.")

    assets = [build(root / name, out / f"{name}.tar.gz") for name in wanted]
    for asset in assets:
        print(asset)

    sums = out / "SHA256SUMS"
    sums.write_text("".join(a.checksum_line for a in assets),
                    encoding="utf-8", newline="\n")
    print(f"\nwrote {sums}")

    if args.summary:
        with open(args.summary, "a", encoding="utf-8") as fh:
            fh.write("\n".join([
                "## Assets", "",
                "| Asset | Size | SHA256 |",
                "|---|---|---|",
                *(a.summary_row for a in assets), "",
                "Pin these via `URL_HASH SHA256=...` in consuming projects.",
            ]) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
