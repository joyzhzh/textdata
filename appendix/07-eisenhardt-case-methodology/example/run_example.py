#!/usr/bin/env python3
"""Worked example: sealed-plan housekeeping on a synthetic workspace, without network or model calls.

Steps: copy example/input/workspace to a fresh directory; inventory it; write a move plan bound to the
live filesystem identity of the two sealed packages; seal the plan; dry-run; show four refusals
(apply without approval, apply with a wrong hash, a tampered plan under the same seal, and a drifted
workspace); apply with the exact sealed hash; verify. With --record, the retained records under
example/output/ are rewritten with the absolute workspace path replaced by <workspace>.
Python 3.9+, standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "tool" / "scripts"
INPUT = HERE / "input" / "workspace"
OUTPUT = HERE / "output"
sys.path.insert(0, str(SCRIPTS))
from apply_move_plan import scan_tree, sha256_file  # noqa: E402

PACKAGES = ["alpha-sealed", "beta-sealed"]


def run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *args], capture_output=True, text=True, check=False)


def outcome(proc: subprocess.CompletedProcess[str]) -> dict:
    stream = proc.stdout if proc.returncode == 0 else proc.stderr
    try:
        payload = json.loads(stream)
    except json.JSONDecodeError:
        payload = {"raw": stream.strip()}
    return {"returncode": proc.returncode, "payload": payload}


def write_plan(root: Path, plan_name: str = "move-plan.json") -> tuple[Path, Path, str]:
    plan = {
        "schema_version": "1.0",
        "plan_id": "example-housekeeping-plan",
        "created_at_utc": "2026-11-01T00:00:00Z",
        "workspace_root": str(root),
        "intent": "Move two sealed packages whole under provenance/ and expose them through relative aliases; copy, edit and delete nothing.",
        "policy": {
            "dry_run_default": True,
            "same_volume_renames_only": True,
            "copy_files": False,
            "delete_files": False,
            "overwrite_existing_paths": False,
            "rewrite_sealed_content": False,
            "follow_symlinks": False,
            "require_exact_plan_sha_for_apply": True,
        },
        "mkdirs": ["provenance", "current"],
        "moves": [],
        "critical_hashes_before_and_after": [],
        "symlinks": [],
        "post_artifacts": ["post-move-report.json"],
        "required_validations": ["verify_workspace.py"],
    }
    for name in PACKAGES:
        plan["moves"].append({"source": name, "target": f"provenance/{name}", "expected": scan_tree(root / name)})
        plan["critical_hashes_before_and_after"].append(
            {"source_path": f"{name}/payload.txt", "target_path": f"provenance/{name}/payload.txt", "sha256": sha256_file(root / name / "payload.txt")}
        )
        plan["symlinks"].append({"path": f"current/{name.removesuffix('-sealed')}", "target": f"../provenance/{name}"})
    plan_path = root / plan_name
    plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    plan_sha = hashlib.sha256(plan_path.read_bytes()).hexdigest()
    seal_path = root / (plan_name.removesuffix(".json") + ".sha256")
    seal_path.write_text(f"{plan_sha}  {plan_path.name}\n", encoding="utf-8")
    return plan_path, seal_path, plan_sha


def listing(root: Path) -> list[str]:
    lines = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            lines.append(f"{rel} -> {path.readlink().as_posix()}")
        elif path.is_dir():
            lines.append(f"{rel}/")
        else:
            lines.append(rel)
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", type=Path, help="fresh directory to run in (default: a new temporary directory, left in place)")
    parser.add_argument("--record", action="store_true", help="rewrite the retained records under example/output/")
    args = parser.parse_args()
    workdir = args.workdir or Path(tempfile.mkdtemp(prefix="eisenhardt-example-"))
    workdir.mkdir(parents=True, exist_ok=True)
    root = workdir / "workspace"
    drift_root = workdir / "drift-workspace"
    if root.exists() or drift_root.exists():
        raise SystemExit("workdir already holds a run; choose a fresh directory")
    shutil.copytree(INPUT, root)
    shutil.copytree(INPUT, drift_root)

    records: dict[str, object] = {}
    inv = run("inventory_workspace.py", str(root), "--hash", "alpha-sealed/payload.txt", "--output", str(root / "pre-inventory.json"))
    records["01-inventory"] = outcome(inv)

    plan_path, seal_path, plan_sha = write_plan(root)
    records["02-move-plan"] = json.loads(plan_path.read_text(encoding="utf-8"))
    records["02-move-plan.sha256"] = seal_path.read_text(encoding="utf-8")

    records["03-dry-run"] = outcome(run("apply_move_plan.py", "--plan", str(plan_path), "--seal", str(seal_path)))

    refusals: dict[str, object] = {}
    refusals["apply-without-approval"] = outcome(run("apply_move_plan.py", "--plan", str(plan_path), "--seal", str(seal_path), "--apply"))
    refusals["apply-with-wrong-hash"] = outcome(run("apply_move_plan.py", "--plan", str(plan_path), "--seal", str(seal_path), "--apply", "--approve-plan-sha", "0" * 64))
    tampered = root / "tampered-plan.json"
    tampered_plan = json.loads(plan_path.read_text(encoding="utf-8"))
    tampered_plan["moves"][0]["target"] = "provenance/alpha-renamed"
    tampered_plan["intent"] = tampered_plan["intent"] + " (edited after sealing)"
    tampered.write_text(json.dumps(tampered_plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tampered_seal = root / "tampered-plan.sha256"
    tampered_seal.write_text(f"{plan_sha}  tampered-plan.json\n", encoding="utf-8")
    refusals["tampered-plan-same-seal"] = outcome(run("apply_move_plan.py", "--plan", str(tampered), "--seal", str(tampered_seal)))
    drift_plan, drift_seal, _ = write_plan(drift_root)
    (drift_root / "beta-sealed" / "late-addition.txt").write_text("a file added after the plan was sealed\n", encoding="utf-8")
    refusals["workspace-drift-after-sealing"] = outcome(run("apply_move_plan.py", "--plan", str(drift_plan), "--seal", str(drift_seal)))
    records["04-refusals"] = refusals

    records["05-apply"] = outcome(run("apply_move_plan.py", "--plan", str(plan_path), "--seal", str(seal_path), "--apply", "--approve-plan-sha", plan_sha))
    records["06-verify"] = outcome(run("verify_workspace.py", "--plan", str(plan_path), "--seal", str(seal_path), "--output", str(root / "post-move-report.json")))
    records["07-reapply-refused"] = outcome(run("apply_move_plan.py", "--plan", str(plan_path), "--seal", str(seal_path)))
    records["08-workspace-after"] = listing(root)

    def status(key: str) -> object:
        item = records[key]
        return item["payload"].get("status") if isinstance(item, dict) and "payload" in item else None

    summary = {
        "inventory": status("01-inventory"),
        "dry_run": status("03-dry-run"),
        "refusals": {k: v["payload"].get("status") for k, v in refusals.items()},
        "apply": status("05-apply"),
        "verify": status("06-verify"),
        "reapply": status("07-reapply-refused"),
        "sealed_plan_sha256": plan_sha,
        "renames": sum(1 for op in records["05-apply"]["payload"].get("applied_operations", []) if op.get("operation") == "rename"),
        "symlinks": sum(1 for op in records["05-apply"]["payload"].get("applied_operations", []) if op.get("operation") == "symlink"),
        "copies": 0,
        "deletions": 0,
    }
    expected = {
        "inventory": "PASS_READ_ONLY_INVENTORY",
        "dry_run": "PASS_PREFLIGHT",
        "refusals": {k: "REFUSED" for k in refusals},
        "apply": "PASS_APPLIED",
        "verify": "PASS_POST_MOVE_STRUCTURE_HASHES_ALIASES",
        "reapply": "REFUSED",
        "renames": 2,
        "symlinks": 2,
    }
    summary["all_as_expected"] = all(summary[k] == v for k, v in expected.items())
    records["SUMMARY"] = summary

    if args.record:
        OUTPUT.mkdir(exist_ok=True)
        for name, payload in records.items():
            text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n" if not isinstance(payload, str) else payload
            for real, label in ((drift_root.resolve(), "<drift-workspace>"), (root.resolve(), "<workspace>"), (drift_root, "<drift-workspace>"), (root, "<workspace>")):
                text = text.replace(str(real), label)  # resolved paths first, so no system prefix such as /private survives
            suffix = "" if name.endswith(".sha256") else ".json"
            (OUTPUT / f"{name}{suffix}").write_text(text, encoding="utf-8")
    print(json.dumps({"workdir": str(workdir), "summary": summary}, indent=2))
    return 0 if summary["all_as_expected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
