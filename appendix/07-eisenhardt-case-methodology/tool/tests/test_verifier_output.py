"""Verifier output must not mutate preserved targets; synthetic fixtures are retained."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from apply_move_plan import scan_tree


class VerificationOutputTest(unittest.TestCase):
    def fixture(self):
        root = Path(tempfile.mkdtemp(prefix="maintenance-report-")).resolve()
        target = root / "provenance/sealed"
        target.mkdir(parents=True)
        (target / "payload.txt").write_text("preserved evidence\n", encoding="utf-8")
        (root / "current").mkdir()
        (root / "current/sealed").symlink_to("../provenance/sealed", target_is_directory=True)
        plan = {
            "schema_version": "1.0", "plan_id": "verification-output-fixture",
            "workspace_root": str(root),
            "moves": [{"source": "original", "target": "provenance/sealed", "expected": scan_tree(target)}],
            "critical_hashes_before_and_after": [{
                "source_path": "original/payload.txt", "target_path": "provenance/sealed/payload.txt",
                "sha256": hashlib.sha256((target / "payload.txt").read_bytes()).hexdigest(),
            }],
            "symlinks": [{"path": "current/sealed", "target": "../provenance/sealed"}],
        }
        plan_path = root / "plan.json"
        plan_path.write_text(json.dumps(plan, sort_keys=True) + "\n", encoding="utf-8")
        seal_path = root / "plan.sha256"
        seal_path.write_text(hashlib.sha256(plan_path.read_bytes()).hexdigest() + "  plan.json\n", encoding="utf-8")
        return root, target

    def run_verifier(self, root, output=None):
        command = [sys.executable, "-B", str(SCRIPTS / "verify_workspace.py"),
                   "--plan", str(root / "plan.json"), "--seal", str(root / "plan.sha256")]
        if output is not None:
            command.extend(["--output", str(output)])
        return subprocess.run(command, capture_output=True, text=True, check=False)

    def snapshot(self, root):
        result = {}
        for path in root.rglob("*"):
            name = path.relative_to(root).as_posix()
            if path.is_symlink():
                result[name] = ("symlink", os.readlink(path))
            elif path.is_dir():
                result[name] = ("directory",)
            else:
                result[name] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
        return result

    def assert_refused_without_mutation(self, root, output, message):
        before = self.snapshot(root)
        rejected = self.run_verifier(root, output)
        self.assertEqual(rejected.returncode, 1, rejected.stdout)
        self.assertIn(message, rejected.stderr)
        self.assertEqual(before, self.snapshot(root))
        again = self.run_verifier(root)
        self.assertEqual(again.returncode, 0, again.stderr)

    def test_direct_and_nested_preserved_outputs_are_refused(self):
        for relative in ["verification.json", "new/nested/verification.json"]:
            with self.subTest(relative=relative):
                root, target = self.fixture()
                self.assert_refused_without_mutation(root, target / relative, "inside a preserved target")

    def test_aliases_into_preserved_targets_are_refused(self):
        for alias in ["planned", "directory", "dangling_file"]:
            with self.subTest(alias=alias):
                root, target = self.fixture()
                if alias == "planned":
                    output = root / "current/sealed/new/verification.json"
                elif alias == "directory":
                    (root / "other-alias").symlink_to(target, target_is_directory=True)
                    output = root / "other-alias/new/verification.json"
                else:
                    output = root / "report-alias.json"
                    output.symlink_to(target / "new/verification.json")
                self.assert_refused_without_mutation(root, output, "inside a preserved target")

    def test_preserved_directory_itself_is_refused(self):
        root, target = self.fixture()
        self.assert_refused_without_mutation(root, target, "inside a preserved target")

    def test_external_to_package_reports_preserve_repeat_verification(self):
        root, target = self.fixture()
        before = self.snapshot(target)
        for name in ["first.json", "second.json"]:
            output = root / "operations/reports" / name
            report = self.run_verifier(root, output)
            self.assertEqual(report.returncode, 0, report.stderr)
            self.assertEqual(json.loads(output.read_text())["status"], "PASS_POST_MOVE_STRUCTURE_HASHES_ALIASES")
            self.assertEqual(before, self.snapshot(target))
            again = self.run_verifier(root)
            self.assertEqual(again.returncode, 0, again.stderr)
        self.assert_refused_without_mutation(root, output, "File exists")

    def test_output_outside_workspace_is_refused(self):
        root, target = self.fixture()
        self.assert_refused_without_mutation(root, root.parent / (root.name + "-outside/report.json"),
                                            "inside the verified workspace")


if __name__ == "__main__":
    unittest.main()

