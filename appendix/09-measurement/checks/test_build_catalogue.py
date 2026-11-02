#!/usr/bin/env python3
"""Exercise rebuild consistency in fresh copies; retain fixtures for inspection."""
import contextlib
import hashlib
import importlib.util
import io
import json
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
WORK = Path(tempfile.mkdtemp(prefix='measurement-builder-'))


class RebuildTests(unittest.TestCase):
    def setUp(self):
        self.root = WORK / self._testMethodName
        shutil.copytree(ROOT / 'docs/g9-design', self.root / 'docs/g9-design')
        shutil.copytree(ROOT / 'tool/templates', self.root / 'tool/templates')
        spec = importlib.util.spec_from_file_location('catalogue_builder', ROOT / 'tool/scripts/build_catalogue.py')
        self.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.builder)
        self.builder.ROOT = self.root
        self.builder.G9 = self.root / 'docs/g9-design'
        self.builder.OUT = self.root / 'data/catalogue'
        self.builder.HTML = self.root / 'docs/catalogue/index.html'
        self.builder.TEMPLATE = self.root / 'tool/templates/catalogue-template.html'

    def seed_release(self):
        shutil.copytree(ROOT / 'data/catalogue', self.builder.OUT)
        self.builder.HTML.parent.mkdir(parents=True)
        shutil.copy2(ROOT / 'docs/catalogue/index.html', self.builder.HTML)

    def outputs(self):
        paths = list(self.builder.OUT.rglob('*')) + [self.builder.HTML]
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in paths if p.is_file()}

    def build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.builder.build()

    def change_mission(self):
        path = self.builder.G9 / 'MISSIONS.json'
        rows = json.loads(path.read_text())
        rows[0]['question'] = 'Regression fixture: a changed mission question.'
        path.write_text(json.dumps(rows, ensure_ascii=False) + '\n')

    def change_lane(self):
        path = self.builder.G9 / 'LANES.jsonl'
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        rows[0]['title'] = 'Regression fixture: a changed lane title.'
        path.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))

    def assert_refused_unchanged(self):
        before = self.outputs()
        with self.assertRaisesRegex(ValueError, 'Existing database differs; no outputs written'):
            self.build()
        self.assertEqual(before, self.outputs())

    def test_unchanged_release_is_byte_identical(self):
        self.seed_release()
        before = self.outputs()
        self.build()
        self.assertEqual(before, self.outputs())

    def test_changed_mission_is_refused_before_outputs(self):
        self.seed_release()
        self.change_mission()
        self.assert_refused_unchanged()

    def test_changed_lane_is_refused_before_outputs(self):
        self.seed_release()
        self.change_lane()
        self.assert_refused_unchanged()

    def test_changed_prose_fingerprint_is_refused_before_outputs(self):
        self.seed_release()
        path = self.builder.G9 / 'README.md'
        path.write_text(path.read_text() + '\nRegression fixture: changed design prose.\n')
        self.assert_refused_unchanged()

    def test_stale_non_browse_table_is_refused_before_outputs(self):
        self.seed_release()
        with sqlite3.connect(self.builder.OUT / 'novelty-design.sqlite') as db:
            db.execute("UPDATE metadata SET value='stale-fixture' WHERE key='design_date'")
        db.close()
        self.assert_refused_unchanged()

    def test_invalid_template_preserves_outputs(self):
        self.seed_release()
        self.builder.TEMPLATE.write_text('Regression fixture: missing data placeholder.\n')
        before = self.outputs()
        with self.assertRaises(AssertionError):
            self.build()
        self.assertEqual(before, self.outputs())

    def test_new_release_contains_changed_inputs_in_every_format(self):
        self.change_mission()
        self.change_lane()
        self.build()
        data = json.loads((self.builder.OUT / 'catalogue.json').read_text())
        self.assertEqual(data['missions'], json.loads((self.builder.G9 / 'MISSIONS.json').read_text()))
        self.assertEqual(data['lanes'], [json.loads(x) for x in (self.builder.G9 / 'LANES.jsonl').read_text().splitlines()])
        self.assertEqual(data['records'], [json.loads(x) for x in (self.builder.OUT / 'records.jsonl').read_text().splitlines()])
        embedded = self.builder.HTML.read_text().split('<script id="catalogue-data" type="application/json">', 1)[1].split('</script>', 1)[0]
        self.assertEqual(json.loads(embedded), data)
        with sqlite3.connect((self.builder.OUT / 'novelty-design.sqlite').resolve().as_uri() + '?mode=ro', uri=True) as db:
            for table, key in [('missions', 'missions'), ('lanes', 'lanes'), ('applications', 'applications'), ('catalogue_records', 'records')]:
                self.assertEqual([json.loads(row[0]) for row in db.execute(f'SELECT payload_json FROM {table} ORDER BY rowid')], data[key])
            self.assertEqual([json.loads(row[0]) for row in db.execute('SELECT payload_json FROM registries ORDER BY rowid')], data['registry_contracts']['registries'])
            self.assertEqual(db.execute('SELECT * FROM methods ORDER BY rowid').fetchall(), [(x['method_id'], x['title'], x['owner_lane']) for x in data['methods']])
            fields = ['application_cell', 'method_id', 'applicability', 'evidence_state', 'rationale', 'source_refs']
            self.assertEqual(db.execute('SELECT * FROM applicability ORDER BY rowid').fetchall(), [tuple(x[k] for k in fields) for x in data['applicability']])
            self.assertEqual(dict(db.execute('SELECT * FROM metadata')), {k: data[k] for k in ['schema_version', 'release_status', 'design_date']})
            self.assertEqual(db.execute('SELECT * FROM sources ORDER BY rowid').fetchall(), [(x['path'], x['source_path'], x['sha256'], x['bytes']) for x in data['sources']])
            for source in data['sources']:
                raw = (self.root / source['path']).read_bytes()
                self.assertEqual(source['sha256'], hashlib.sha256(raw).hexdigest())
                self.assertEqual(source['bytes'], len(raw))
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
        db.close()
        before = self.outputs()
        self.build()
        self.assertEqual(before, self.outputs())


if __name__ == '__main__':
    print('Retained builder regression fixtures:', WORK, flush=True)
    unittest.main(verbosity=2)
