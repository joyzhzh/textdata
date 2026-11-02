#!/usr/bin/env python3
"""Inventory a workspace without following symlinks or changing filesystem state."""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apply_move_plan import rooted, scan_tree, sha256_file


def top_level_entry(path: Path) -> dict[str, Any]:
    info = path.lstat()
    base: dict[str, Any] = {
        "path": path.name,
        "device_id": info.st_dev,
        "inode": info.st_ino,
    }
    if stat.S_ISLNK(info.st_mode):
        base.update({"kind": "symlink", "target": os.readlink(path)})
    elif stat.S_ISDIR(info.st_mode):
        base.update({"kind": "directory", "snapshot": scan_tree(path)})
    elif stat.S_ISREG(info.st_mode):
        base.update(
            {
                "kind": "regular-file",
                "logical_bytes": info.st_size,
                "nlink": info.st_nlink,
            }
        )
    else:
        base.update({"kind": "unsupported"})
    return base


def within(root: Path, path: Path) -> bool:
    return os.path.commonpath([str(root.resolve()), str(path.resolve(strict=False))]) == str(root.resolve())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--hash", action="append", default=[], dest="hash_paths", help="relative regular file to hash")
    parser.add_argument("--output", type=Path, help="create a new JSON output file; refuses overwrite")
    args = parser.parse_args()
    try:
        requested_root = args.root.absolute()
        if not requested_root.is_dir() or requested_root.is_symlink():
            raise ValueError("root must be a real directory")
        root = requested_root.resolve(strict=True)
        report: dict[str, Any] = {
            "schema_version": "1.0",
            "observed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "workspace_root": str(root),
            "totals": scan_tree(root),
            "top_level": [top_level_entry(path) for path in sorted(root.iterdir(), key=lambda item: item.name)],
            "requested_hashes": {},
            "status": "PASS_READ_ONLY_INVENTORY",
        }
        for value in args.hash_paths:
            path = rooted(root, value)
            if not path.is_file() or path.is_symlink():
                raise ValueError(f"hash target must be a real regular file: {value}")
            report["requested_hashes"][value] = sha256_file(path)
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.output:
            output = args.output.resolve(strict=False)
            if not within(root, output):
                raise ValueError("output must be inside the audited workspace")
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("x", encoding="utf-8") as handle:
                handle.write(rendered)
        print(rendered, end="")
        return 0
    except Exception as exc:
        print(json.dumps({"status": "REFUSED", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
