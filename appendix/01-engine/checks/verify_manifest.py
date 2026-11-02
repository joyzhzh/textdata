#!/usr/bin/env python3
"""Check that this folder holds exactly the files listed in MANIFEST.json, each with the
listed size and SHA-256. Python 3.9+, standard library only, no network, no model.
Exit 0 when every file matches and nothing is unlisted, 1 otherwise.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IGNORED = {"MANIFEST.json"}


def main():
    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    listed = {f["path"]: f for f in manifest["files"]}
    present = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*")
               if p.is_file() and "__pycache__" not in p.parts and p.name != ".DS_Store"}
    present -= IGNORED
    failures = 0
    for path, entry in sorted(listed.items()):
        target = ROOT / path
        if not target.is_file():
            print(f"FAIL  missing  {path}")
            failures += 1
            continue
        data = target.read_bytes()
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            print(f"FAIL  changed  {path}")
            failures += 1
    for path in sorted(present - set(listed)):
        print(f"FAIL  unlisted  {path}")
        failures += 1
    print(f"{len(listed)} files listed, {len(present)} present, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
