#!/usr/bin/env python3
"""Preflight and apply an exact, sealed, no-copy workspace move plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_relative(value: str) -> PurePosixPath:
    rel = PurePosixPath(value)
    if rel.is_absolute() or not rel.parts or any(part in {"", ".", ".."} for part in rel.parts):
        raise ValueError(f"unsafe relative path: {value!r}")
    return rel


def rooted(root: Path, value: str) -> Path:
    rel = safe_relative(value)
    path = root.joinpath(*rel.parts)
    # A lexical in-root path may still escape through an existing directory alias.
    parent = root
    for part in rel.parts[:-1]:
        parent = parent / part
        if parent.is_symlink():
            raise ValueError(f"symlink ancestor refused: {value!r}")
    return path


def scan_tree(root: Path) -> dict[str, Any]:
    root_stat = root.lstat()
    if not stat.S_ISDIR(root_stat.st_mode):
        raise ValueError(f"not a directory: {root}")

    directories = 0
    regular_files = 0
    symlinks = 0
    logical_bytes = 0
    files_with_nlink_gt_1 = 0
    file_inodes: set[tuple[int, int]] = set()
    nlink_distribution: Counter[int] = Counter()
    stack = [root]

    while stack:
        current = stack.pop()
        directories += 1
        with os.scandir(current) as entries:
            for entry in entries:
                item = Path(entry.path)
                item_stat = item.lstat()
                mode = item_stat.st_mode
                if stat.S_ISLNK(mode):
                    symlinks += 1
                elif stat.S_ISDIR(mode):
                    stack.append(item)
                elif stat.S_ISREG(mode):
                    regular_files += 1
                    logical_bytes += item_stat.st_size
                    file_inodes.add((item_stat.st_dev, item_stat.st_ino))
                    nlink_distribution[item_stat.st_nlink] += 1
                    if item_stat.st_nlink > 1:
                        files_with_nlink_gt_1 += 1
                else:
                    raise ValueError(f"unsupported filesystem object: {item}")

    return {
        "device_id": root_stat.st_dev,
        "root_inode": root_stat.st_ino,
        "directories_including_root": directories,
        "regular_files": regular_files,
        "symlinks": symlinks,
        "logical_bytes": logical_bytes,
        "files_with_nlink_gt_1": files_with_nlink_gt_1,
        "unique_regular_file_inodes": len(file_inodes),
        "nlink_distribution": {str(key): value for key, value in sorted(nlink_distribution.items())},
    }


def load_sealed_plan(plan_path: Path, seal_path: Path) -> tuple[dict[str, Any], str]:
    plan_sha = sha256_file(plan_path)
    seal_fields = seal_path.read_text(encoding="utf-8").strip().split()
    if len(seal_fields) != 2 or seal_fields[0] != plan_sha:
        raise ValueError(f"plan seal mismatch: calculated {plan_sha}")
    sealed_basename = Path(seal_fields[1].lstrip("*")).name
    if sealed_basename != plan_path.name:
        raise ValueError(
            f"plan seal filename mismatch: expected {plan_path.name!r}, got {sealed_basename!r}"
        )
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if plan.get("schema_version") != "1.0":
        raise ValueError("unsupported plan schema")
    return plan, plan_sha


def compare_expected(label: str, actual: dict[str, Any], expected: dict[str, Any]) -> None:
    required = {"device_id", "root_inode", "directories_including_root", "regular_files",
                "symlinks", "logical_bytes", "files_with_nlink_gt_1", "unique_regular_file_inodes"}
    if not required <= expected.keys():
        raise ValueError(f"incomplete expected snapshot for {label}")
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            raise ValueError(
                f"precondition drift for {label}: {key} expected {expected_value!r}, got {actual_value!r}"
            )


def future_path_exists(root: Path, path: Path, moves: list[dict[str, Any]]) -> bool:
    for move in moves:
        target = rooted(root, move["target"])
        if os.path.commonpath([str(target), str(path)]) != str(target):
            continue
        relative = path.relative_to(target)
        precursor = rooted(root, move["source"]).joinpath(relative)
        if os.path.lexists(precursor):
            if precursor.resolve(strict=False) != root.resolve() / precursor.relative_to(root):
                raise ValueError("future alias target traverses a symlink")
            return True
    if any(rooted(root, m["source"]) == path or rooted(root, m["source"]) in path.parents for m in moves):
        return False
    if os.path.lexists(path):
        if path.resolve(strict=False) != root.resolve() / path.relative_to(root):
            raise ValueError("alias target traverses a symlink")
        return True
    return False


def preflight(plan: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    if Path(plan["workspace_root"]) != root:
        raise ValueError("workspace root does not match sealed plan")
    if not root.is_dir() or root.is_symlink():
        raise ValueError("workspace root must be a real directory")

    results: list[dict[str, Any]] = []
    root_device = root.stat().st_dev

    def overlaps(a: Path, b: Path) -> bool:
        return a == b or a in b.parents or b in a.parents

    sources = [rooted(root, m["source"]) for m in plan["moves"]]
    targets = [rooted(root, m["target"]) for m in plan["moves"]]
    mkdirs = [rooted(root, p) for p in plan["mkdirs"]]
    aliases = [rooted(root, p["path"]) for p in plan["symlinks"]]
    for paths in (sources, targets, aliases):
        if any(overlaps(a, b) for i, a in enumerate(paths) for b in paths[i + 1:]):
            raise ValueError("duplicate or overlapping planned paths")
    if len(set(mkdirs)) != len(mkdirs):
        raise ValueError("duplicate planned directory")
    if any(overlaps(s, t) for s in sources for t in targets):
        raise ValueError("move source and destination trees overlap")
    # Directory/alias creation must never edit a moved sealed package.
    if any(p == tree or tree in p.parents for p in mkdirs + aliases for tree in sources + targets):
        raise ValueError("planned creation inside a moved tree")
    if any(overlaps(a, p) for a in aliases for p in mkdirs + sources + targets):
        # A planned directory may be an alias's parent; that is the normal case.
        if any(overlaps(a, p) and not (p in mkdirs and p in a.parents)
               for a in aliases for p in mkdirs + sources + targets):
            raise ValueError("planned alias collides with another operation")
    for path in mkdirs + targets + aliases:
        parent = path.parent
        while not parent.exists() and parent != root:
            parent = parent.parent
        if not parent.is_dir() or parent.stat().st_dev != root_device:
            raise ValueError(f"target parent is not on the workspace filesystem: {path}")
    available_mkdirs: set[str] = set()
    for value in plan["mkdirs"]:
        rel = str(safe_relative(value))
        path = rooted(root, rel)
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            raise ValueError(f"planned directory collides with a non-directory: {path}")
        parent_rel = str(PurePosixPath(rel).parent)
        if not path.exists() and not path.parent.is_dir() and parent_rel not in available_mkdirs:
            raise ValueError(f"mkdir parent is neither present nor earlier in the plan: {path.parent}")
        if path.exists() and path.stat().st_dev != root_device:
            raise ValueError(f"cross-device planned directory refused: {path}")
        available_mkdirs.add(rel)

    for move in plan["moves"]:
        source = rooted(root, move["source"])
        target = rooted(root, move["target"])
        if not source.is_dir() or source.is_symlink():
            raise ValueError(f"source is missing or not a real directory: {source}")
        if target.exists() or target.is_symlink():
            raise ValueError(f"target already exists: {target}")
        parent_rel = str(PurePosixPath(move["target"]).parent)
        if not target.parent.is_dir() and parent_rel not in available_mkdirs:
            raise ValueError(f"move target parent is neither present nor planned: {target.parent}")
        actual = scan_tree(source)
        compare_expected(move["source"], actual, move["expected"])
        if actual["device_id"] != root_device:
            raise ValueError(f"cross-device source refused: {source}")
        results.append({"source": move["source"], "target": move["target"], "snapshot": actual})

    for item in plan["critical_hashes_before_and_after"]:
        path = rooted(root, item["source_path"])
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"critical hash target is not a real regular file: {item['source_path']}")
        actual_hash = sha256_file(path)
        if actual_hash != item["sha256"]:
            raise ValueError(f"critical hash drift for {item['source_path']}: {actual_hash}")

    planned_mkdirs = {str(safe_relative(item)) for item in plan["mkdirs"]}
    for link in plan["symlinks"]:
        link_path = rooted(root, link["path"])
        if link_path.exists() or link_path.is_symlink():
            raise ValueError(f"symlink path already exists: {link_path}")
        parent_rel = str(PurePosixPath(link["path"]).parent)
        if parent_rel not in planned_mkdirs and not link_path.parent.is_dir():
            raise ValueError(f"symlink parent is neither present nor planned: {link_path.parent}")
        target_text = link["target"]
        if os.path.isabs(target_text):
            raise ValueError(f"absolute symlink target refused: {target_text}")
        resolved_text = os.path.abspath(os.path.normpath(os.path.join(str(link_path.parent), target_text)))
        if os.path.commonpath([str(root), resolved_text]) != str(root):
            raise ValueError(f"out-of-root symlink target refused: {target_text}")
        if not future_path_exists(root, Path(resolved_text), plan["moves"]):
            raise ValueError(f"symlink target will not exist after planned moves: {target_text}")
    return results


def apply_plan(plan: dict[str, Any], root: Path) -> list[dict[str, str]]:
    applied: list[dict[str, str]] = []
    for rel in plan["mkdirs"]:
        path = rooted(root, rel)
        path.mkdir(parents=False, exist_ok=True)
        applied.append({"operation": "mkdir", "path": rel})
    for move in plan["moves"]:
        source = rooted(root, move["source"])
        target = rooted(root, move["target"])
        source.rename(target)
        applied.append({"operation": "rename", "source": move["source"], "target": move["target"]})
    for link in plan["symlinks"]:
        path = rooted(root, link["path"])
        target_text = link["target"]
        resolved = Path(os.path.abspath(os.path.normpath(os.path.join(str(path.parent), target_text))))
        if not resolved.exists():
            raise ValueError(f"planned symlink target is missing after moves: {resolved}")
        os.symlink(target_text, path)
        applied.append({"operation": "symlink", "path": link["path"], "target": target_text})
    return applied


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--seal", required=True, type=Path)
    parser.add_argument("--apply", action="store_true", help="apply after complete preflight; default is dry-run")
    parser.add_argument("--approve-plan-sha", help="exact sealed plan SHA required with --apply")
    args = parser.parse_args()
    try:
        plan, plan_sha = load_sealed_plan(args.plan, args.seal)
        root = Path(plan["workspace_root"])
        checked = preflight(plan, root)
        output: dict[str, Any] = {
            "status": "PASS_PREFLIGHT",
            "mode": "dry-run",
            "plan_id": plan["plan_id"],
            "plan_sha256": plan_sha,
            "moves_checked": checked,
            "planned_symlinks": plan["symlinks"],
        }
        if args.apply:
            if args.approve_plan_sha != plan_sha:
                raise ValueError("--apply requires the exact sealed --approve-plan-sha value")
            output["applied_operations"] = apply_plan(plan, root)
            output["mode"] = "apply"
            output["status"] = "PASS_APPLIED"
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "REFUSED", "error": str(exc)}, indent=2, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
