"""Regressions for preflight containment and plan conflicts; fixtures are retained."""
from __future__ import annotations
import copy
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from apply_move_plan import preflight, scan_tree

class PreflightBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.fixture = Path(tempfile.mkdtemp(prefix='maintenance-boundary-')).resolve()
        self.root = self.fixture / 'workspace'; self.root.mkdir()
        self.outside = self.fixture / 'outside'; self.outside.mkdir()
        for name in ['a', 'b']:
            p = self.root / name; p.mkdir(); (p / 'payload').write_text('fixture')
        self.plan = {'workspace_root': str(self.root), 'mkdirs': ['dest', 'current'],
            'moves': [{'source': 'a', 'target': 'dest/a', 'expected': scan_tree(self.root/'a')}],
            'critical_hashes_before_and_after': [], 'symlinks': []}

    def refuses(self, pattern):
        before = sorted(str(p.relative_to(self.root)) for p in self.root.rglob('*'))
        with self.assertRaisesRegex(ValueError, pattern): preflight(self.plan, self.root)
        self.assertEqual(before, sorted(str(p.relative_to(self.root)) for p in self.root.rglob('*')))
        self.assertEqual(list(self.outside.iterdir()), [])

    def test_destination_through_directory_symlink(self):
        (self.root/'escape').symlink_to(self.outside, target_is_directory=True)
        self.plan['moves'][0]['target'] = 'escape/moved'
        self.refuses('symlink ancestor')

    def test_duplicate_move_target(self):
        self.plan['moves'].append({'source':'b','target':'dest/a','expected':scan_tree(self.root/'b')})
        self.refuses('overlapping planned')

    def test_nested_move_sources(self):
        (self.root/'a/nested').mkdir()
        self.plan['moves'][0]['expected'] = scan_tree(self.root/'a')
        self.plan['moves'].append({'source':'a/nested','target':'dest/nested','expected':scan_tree(self.root/'a/nested')})
        self.refuses('overlapping planned')

    def test_directory_creation_in_sealed_source(self):
        self.plan['mkdirs'].append('a/new')
        self.refuses('creation inside a moved tree')

    def test_missing_snapshot_fields(self):
        self.plan['moves'][0]['expected'] = {}
        self.refuses('incomplete expected snapshot')

    def test_alias_into_moved_away_source(self):
        self.plan['symlinks'] = [{'path':'current/a','target':'../a'}]
        self.refuses('target will not exist')

    def test_alias_through_external_symlink(self):
        (self.root/'escape').symlink_to(self.outside, target_is_directory=True)
        self.plan['symlinks'] = [{'path':'current/a','target':'../escape'}]
        self.refuses('target traverses a symlink')

    def test_alias_path_conflict(self):
        self.plan['symlinks'] = [{'path':'current','target':'dest/a'}]
        self.refuses('alias collides')

    def test_critical_hash_cannot_follow_symlink(self):
        (self.root/'hash-alias').symlink_to(self.root/'a/payload')
        self.plan['critical_hashes_before_and_after'] = [{'source_path':'hash-alias','target_path':'dest/a/payload','sha256':'0'*64}]
        self.refuses('not a real regular file')

if __name__ == '__main__': unittest.main()
