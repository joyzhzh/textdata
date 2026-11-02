#!/usr/bin/env python3
"""Verify post-move identity, critical hashes, and aliases against a sealed plan."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apply_move_plan import compare_expected, load_sealed_plan, rooted, scan_tree, sha256_file


def verify(plan: dict[str, Any], plan_sha: str, root: Path) -> dict[str, Any]:
    moves: list[dict[str, Any]] = []
    for move in plan["moves"]:
        source = rooted(root, move["source"])
        target = rooted(root, move["target"])
        if os.path.lexists(source):
            raise ValueError(f"original source still exists: {move['source']}")
        if not target.is_dir() or target.is_symlink():
            raise ValueError(f"target missing or not a real directory: {move['target']}")
        actual = scan_tree(target)
        compare_expected(move["target"], actual, move["expected"])
        moves.append({"source_absent": move["source"], "target": move["target"], "snapshot": actual, "status": "PASS"})

    critical_hashes: list[dict[str, str]] = []
    for item in plan["critical_hashes_before_and_after"]:
        target = rooted(root, item["target_path"])
        actual = sha256_file(target)
        if actual != item["sha256"]:
            raise ValueError(f"critical hash mismatch: {item['target_path']}")
        critical_hashes.append({"path": item["target_path"], "sha256": actual, "status": "PASS"})

    canonical_root = root.resolve(strict=True)
    symlinks: list[dict[str, str]] = []
    for item in plan["symlinks"]:
        path = rooted(root, item["path"])
        if not path.is_symlink():
            raise ValueError(f"planned symlink missing: {item['path']}")
        actual_target = os.readlink(path)
        if actual_target != item["target"] or os.path.isabs(actual_target):
            raise ValueError(f"symlink drift or absolute target: {item['path']}")
        resolved = path.resolve(strict=True)
        if os.path.commonpath([str(canonical_root), str(resolved)]) != str(canonical_root):
            raise ValueError(f"symlink resolves outside workspace: {item['path']}")
        symlinks.append(
            {
                "path": item["path"],
                "target": actual_target,
                "resolved": str(resolved),
                "status": "PASS_RELATIVE_RESOLVED_IN_ROOT",
            }
        )

    return {
        "schema_version": "1.0",
        "observed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "workspace_root": str(root),
        "plan_id": plan["plan_id"],
        "plan_sha256": plan_sha,
        "moves": moves,
        "critical_hashes": critical_hashes,
        "symlinks": symlinks,
        "status": "PASS_POST_MOVE_STRUCTURE_HASHES_ALIASES",
    }


def within(root: Path, path: Path) -> bool:
    return os.path.commonpath([str(root.resolve()), str(path.resolve(strict=False))]) == str(root.resolve())


def report_destination(plan: dict[str, Any], root: Path, path: Path) -> Path:
    """Resolve aliases and reject writes into any preserved move target."""
    output = path.resolve(strict=False)
    if not within(root, output):
        raise ValueError("output must be inside the verified workspace")
    for move in plan["moves"]:
        target = rooted(root, move["target"])
        if within(target, output):
            raise ValueError(f"output must not be inside a preserved target: {move['target']}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--seal", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="create a new report inside the workspace, outside preserved targets; refuses overwrite")
    args = parser.parse_args()
    try:
        plan, plan_sha = load_sealed_plan(args.plan, args.seal)
        root = Path(plan["workspace_root"])
        if not root.is_dir() or root.is_symlink():
            raise ValueError("workspace root must be a real directory")
        output = report_destination(plan, root, args.output) if args.output else None
        report = verify(plan, plan_sha, root)
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if output is not None:
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("x", encoding="utf-8") as handle:
                handle.write(rendered)
        print(rendered, end="")
        return 0
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
