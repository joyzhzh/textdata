from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPOSITORY_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from apply_move_plan import scan_tree, sha256_file  # noqa: E402


class MigrationWorkflowTest(unittest.TestCase):
    def run_script(self, script: str, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / script), *arguments],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_sealed_dry_run_apply_and_verify(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="eisenhardt-maintainer-test-"))
        sources = ["alpha-sealed", "beta-sealed"]
        payload_hashes: dict[str, str] = {}

        for index, name in enumerate(sources, start=1):
            source = root / name
            source.mkdir()
            payload = source / "payload.txt"
            payload.write_text(f"sealed payload {index}\n", encoding="utf-8")
            payload_hashes[name] = sha256_file(payload)
            (source / "SHA256SUMS").write_text(
                f"{payload_hashes[name]}  payload.txt\n",
                encoding="utf-8",
            )

        plan = {
            "schema_version": "1.0",
            "plan_id": "integration-test-plan",
            "created_at_utc": "2026-01-01T00:00:00Z",
            "workspace_root": str(root),
            "intent": "Move two sealed fixtures without copying or editing them.",
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
            "post_artifacts": [],
            "required_validations": [],
        }

        for name in sources:
            plan["moves"].append(
                {
                    "source": name,
                    "target": f"provenance/{name}",
                    "expected": scan_tree(root / name),
                }
            )
            plan["critical_hashes_before_and_after"].append(
                {
                    "source_path": f"{name}/payload.txt",
                    "target_path": f"provenance/{name}/payload.txt",
                    "sha256": payload_hashes[name],
                }
            )
            plan["symlinks"].append(
                {
                    "path": f"current/{name.removesuffix('-sealed')}",
                    "target": f"../provenance/{name}",
                }
            )

        plan_path = root / "move-plan.json"
        plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        plan_sha = hashlib.sha256(plan_path.read_bytes()).hexdigest()
        seal_path = root / "move-plan.sha256"
        seal_path.write_text(f"{plan_sha}  {plan_path.name}\n", encoding="utf-8")

        inventory = self.run_script(
            "inventory_workspace.py",
            str(root),
            "--hash",
            "alpha-sealed/payload.txt",
            "--output",
            str(root / "pre-inventory.json"),
        )
        self.assertEqual(inventory.returncode, 0, inventory.stderr)
        self.assertIn("PASS_READ_ONLY_INVENTORY", inventory.stdout)

        dry_run = self.run_script(
            "apply_move_plan.py",
            "--plan",
            str(plan_path),
            "--seal",
            str(seal_path),
        )
        self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
        self.assertIn("PASS_PREFLIGHT", dry_run.stdout)

        missing_approval = self.run_script(
            "apply_move_plan.py",
            "--plan",
            str(plan_path),
            "--seal",
            str(seal_path),
            "--apply",
        )
        self.assertEqual(missing_approval.returncode, 1)
        self.assertIn("exact sealed --approve-plan-sha", missing_approval.stderr)

        wrong_approval = self.run_script(
            "apply_move_plan.py",
            "--plan",
            str(plan_path),
            "--seal",
            str(seal_path),
            "--apply",
            "--approve-plan-sha",
            "0" * 64,
        )
        self.assertEqual(wrong_approval.returncode, 1)

        wrong_name_seal = root / "wrong-name.sha256"
        wrong_name_seal.write_text(f"{plan_sha}  wrong-plan.json\n", encoding="utf-8")
        wrong_name = self.run_script(
            "apply_move_plan.py",
            "--plan",
            str(plan_path),
            "--seal",
            str(wrong_name_seal),
        )
        self.assertEqual(wrong_name.returncode, 1)
        self.assertIn("plan seal filename mismatch", wrong_name.stderr)

        applied = self.run_script(
            "apply_move_plan.py",
            "--plan",
            str(plan_path),
            "--seal",
            str(seal_path),
            "--apply",
            "--approve-plan-sha",
            plan_sha,
        )
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertIn("PASS_APPLIED", applied.stdout)

        report_path = root / "post-move-report.json"
        verified = self.run_script(
            "verify_workspace.py",
            "--plan",
            str(plan_path),
            "--seal",
            str(seal_path),
            "--output",
            str(report_path),
        )
        self.assertEqual(verified.returncode, 0, verified.stderr)
        self.assertIn("PASS_POST_MOVE_STRUCTURE_HASHES_ALIASES", verified.stdout)

        for name in sources:
            self.assertFalse((root / name).exists())
            self.assertTrue((root / "provenance" / name / "payload.txt").is_file())
            alias = root / "current" / name.removesuffix("-sealed")
            self.assertTrue(alias.is_symlink())
            self.assertEqual(
                sha256_file(alias / "payload.txt"),
                payload_hashes[name],
            )

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "PASS_POST_MOVE_STRUCTURE_HASHES_ALIASES")


if __name__ == "__main__":
    unittest.main()
