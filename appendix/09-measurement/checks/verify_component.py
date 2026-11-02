#!/usr/bin/env python3
"""Verify the counts stated in README.md and MANIFEST.json, re-run the worked example,
confirm the withheld search terms are absent and every file matches MANIFEST.json.

Standard library only; no network, no model calls. Run from anywhere:
    python3 checks/verify_component.py
Exit status 0 means every check passed; the first failing check raises.
"""
import copy
import csv
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep the component tree free of machine-specific cache files
ROOT = Path(__file__).resolve().parents[1]
G9 = ROOT / 'docs/g9-design'
DATA = ROOT / 'data/catalogue'
sys.path.insert(0, str(ROOT / 'tool/scripts'))
from validate_measure_cards import SCHEMA, check_schema, load_and_validate, validate  # noqa: E402

EXPECTED = {
    'method families (records in METHOD_FAMILIES.json)': 14,
    'application settings (rows in APPLICATION_COVERAGE.csv)': 35,
    'research questions (lane records in LANES.jsonl)': 61,
    'missions (records in MISSIONS.json)': 12,
    'application-method entries (rows in METHOD_APPLICABILITY.csv)': 490,
    'registry specifications (entries in REGISTRY_CONTRACTS.json)': 6,
    'browse records (lines in data/catalogue/records.jsonl)': 110,
    'populated measure cards (lines in example/input/ASKIN_MEASURE_CARD.jsonl)': 1,
    'fields in the measure card': 44,
    'measure-card fields reported with a locator': 17,
    'measure-card fields explicitly unknown': 24,
    'measure-card fields marked proposed': 3,
    'executed measurements or validated estimates': 0,
}
WITHHELD_SCOPE = ['docs/g9-design/LANES.jsonl', 'docs/g9-design/MISSIONS.md', 'docs/catalogue/index.html',
                  'data/catalogue/catalogue.json', 'data/catalogue/records.jsonl', 'data/catalogue/novelty-design.sqlite']


def jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def csv_rows(path):
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))


def expect_rejection(callback, label):
    try:
        callback()
    except ValueError:
        return
    raise AssertionError(f'invalid case was accepted: {label}')


def main():
    found = {}
    methods = json.loads((G9 / 'METHOD_FAMILIES.json').read_text())
    apps = csv_rows(G9 / 'APPLICATION_COVERAGE.csv')
    lanes = jsonl(G9 / 'LANES.jsonl')
    missions = json.loads((G9 / 'MISSIONS.json').read_text())
    matrix = csv_rows(G9 / 'METHOD_APPLICABILITY.csv')
    registries = json.loads((G9 / 'REGISTRY_CONTRACTS.json').read_text())
    found['method families (records in METHOD_FAMILIES.json)'] = len(methods)
    found['application settings (rows in APPLICATION_COVERAGE.csv)'] = len(apps)
    assert len({r['application_cell'] for r in apps}) == len(apps), 'duplicate application cells'
    found['research questions (lane records in LANES.jsonl)'] = len(lanes)
    found['missions (records in MISSIONS.json)'] = len(missions)
    found['application-method entries (rows in METHOD_APPLICABILITY.csv)'] = len(matrix)
    assert len({(r['application_cell'], r['method_id']) for r in matrix}) == len(matrix), 'duplicate matrix entries'
    assert all(r['applicability'] == 'unassessed' for r in matrix), 'an applicability entry is assessed'
    assert all(r['evidence_state'] == 'unsearched' for r in matrix), 'an applicability entry is searched'
    assert all(r['status'] == 'designed_not_launched' and r['coverage_state'] == 'unsearched' for r in lanes)
    assert registries['status'] == 'future_production_schema_not_empirical_data'
    found['registry specifications (entries in REGISTRY_CONTRACTS.json)'] = len(registries['registries'])

    records = jsonl(DATA / 'records.jsonl')
    found['browse records (lines in data/catalogue/records.jsonl)'] = len(records)
    kinds = {}
    for r in records:
        kinds[r['kind']] = kinds.get(r['kind'], 0) + 1
    assert kinds == {'Method': 14, 'Application': 35, 'Research question': 61}, kinds
    catalogue = json.loads((DATA / 'catalogue.json').read_text())
    assert catalogue['records'] == records, 'catalogue.json and records.jsonl differ'
    assert catalogue['counts']['observed_novelty_results_in_this_release'] == 0
    assert csv_rows(DATA / 'applicability.csv') == matrix, 'data/catalogue/applicability.csv differs from the design table'
    html = (ROOT / 'docs/catalogue/index.html').read_text()
    embedded = html.split('<script id="catalogue-data" type="application/json">', 1)[1].split('</script>', 1)[0]
    assert json.loads(embedded) == catalogue, 'HTML embedded data differs from catalogue.json'
    db = sqlite3.connect(f'file:{DATA / "novelty-design.sqlite"}?mode=ro', uri=True)
    sql = {t: db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
           for t in ['missions', 'lanes', 'methods', 'applications', 'applicability', 'registries', 'catalogue_records', 'sources']}
    assert sql == {'missions': 12, 'lanes': 61, 'methods': 14, 'applications': 35, 'applicability': 490,
                   'registries': 6, 'catalogue_records': 110, 'sources': 11}, sql
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert db.execute("SELECT COUNT(*) FROM applicability WHERE applicability!='unassessed' OR evidence_state!='unsearched'").fetchone()[0] == 0
    # The catalogue's file fingerprints describe the design files as shipped.
    for path, digest, size in db.execute('SELECT path, sha256, byte_count FROM sources'):
        data = (ROOT / path).read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest and len(data) == size, f'stale fingerprint for {path} in the database'
    assert {(s['path'], s['sha256']) for s in catalogue['sources']} == set(db.execute('SELECT path, sha256 FROM sources').fetchall())
    db.close()

    # Worked example: the one populated measure card, both validator modes, and the recorded outputs.
    example = ROOT / 'example/input/ASKIN_MEASURE_CARD.jsonl'
    cards = jsonl(example)
    found['populated measure cards (lines in example/input/ASKIN_MEASURE_CARD.jsonl)'] = len(cards)
    card = cards[0]
    assert card['teaching_example'] is True and card['review_status'] == 'unreviewed'
    statuses = {}
    n_fields = 0
    for section in card['sections'].values():
        for field in section.values():
            n_fields += 1
            statuses[field['status']] = statuses.get(field['status'], 0) + 1
    found['fields in the measure card'] = n_fields
    found['measure-card fields reported with a locator'] = statuses.get('reported', 0)
    found['measure-card fields explicitly unknown'] = statuses.get('unknown', 0)
    found['measure-card fields marked proposed'] = statuses.get('proposed', 0)
    assert load_and_validate([example]) == 1
    expect_rejection(lambda: load_and_validate([example], submission=True), 'teaching card in submission mode')
    expect_rejection(lambda: load_and_validate([example, example]), 'duplicate record id')
    schema = json.loads(SCHEMA.read_text())
    check_schema(schema, schema)
    for defect in ('missing_comparator', 'unknown_with_value', 'reported_without_locator', 'held_rights', 'self_admission'):
        bad = copy.deepcopy(card)
        if defect == 'missing_comparator':
            bad['sections']['scoring'].pop('comparator_universe')
        elif defect == 'unknown_with_value':
            bad['sections']['study']['population_and_sample']['value'] = 'invented'
        elif defect == 'reported_without_locator':
            bad['sections']['scoring']['time_window']['locator'] = None
        elif defect == 'held_rights':
            bad['rights'] = 'held'
        else:
            bad['review_status'] = 'admitted'
        expect_rejection(lambda: validate(bad, schema, schema), defect)
    validator = ROOT / 'tool/scripts/validate_measure_cards.py'
    run = subprocess.run([sys.executable, '-I', str(validator), str(example)], capture_output=True, text=True, cwd=ROOT)
    assert run.returncode == 0 and run.stdout.startswith('STRUCTURE OK: 1 card(s)'), run
    recorded = (ROOT / 'example/output/structure_check.txt').read_text()
    assert run.stdout.strip() in recorded and 'exit status: 0' in recorded, 'structure_check.txt differs from a fresh run'
    run = subprocess.run([sys.executable, '-I', str(validator), '--submission', str(example)], capture_output=True, text=True, cwd=ROOT)
    assert run.returncode == 1 and 'teaching example cannot be submitted' in run.stderr, run
    recorded = (ROOT / 'example/output/submission_check.txt').read_text()
    assert 'teaching example cannot be submitted' in recorded and 'exit status: 1' in recorded, 'submission_check.txt differs from a fresh run'
    found['executed measurements or validated estimates'] = 0  # nothing in this folder scores or evaluates text

    # Withheld: the Chinese-language search terms (the public design omits these terms).
    cjk = re.compile('[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]')
    assert not any('chinese_terms' in r for r in lanes + catalogue['lanes']), 'a research question still carries its Chinese search terms'
    for rel in WITHHELD_SCOPE:
        text = (ROOT / rel).read_bytes().decode('utf-8', 'ignore')
        assert 'chinese_terms' not in text and not cjk.search(text), f'withheld search terms found in {rel}'
    # The search protocol keeps its multilingual probe table; only the Japanese row may use Han or kana characters.
    protocol = (G9 / 'SEARCH_PROTOCOL.md').read_text().splitlines()
    assert all(line.startswith('| Japanese |') for line in protocol if cjk.search(line)), 'withheld search terms found in SEARCH_PROTOCOL.md'

    # Every shipped file is listed in MANIFEST.json with its size and SHA-256, and nothing else is listed.
    listed = {f['path']: f for f in json.loads((ROOT / 'MANIFEST.json').read_text())['files']}
    shipped = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*')
                     if p.is_file() and p.name not in ('MANIFEST.json', '.DS_Store') and '__pycache__' not in p.parts)
    assert sorted(listed) == shipped, f'MANIFEST.json and the folder differ: {sorted(set(listed) ^ set(shipped))}'
    for rel in shipped:
        data = (ROOT / rel).read_bytes()
        assert listed[rel]['bytes'] == len(data) and listed[rel]['sha256'] == hashlib.sha256(data).hexdigest(), f'{rel} differs from MANIFEST.json'

    mismatches = {k: (EXPECTED[k], found.get(k)) for k in EXPECTED if EXPECTED[k] != found.get(k)}
    assert not mismatches, f'count mismatches (expected, found): {mismatches}'
    for k, v in found.items():
        print(f'OK  {v:>4}  {k}')
    print('OK  worked example: structure accepted, submission rejected, duplicate rejected, five constructed defects rejected')
    print(f'OK  withheld: no Chinese search terms in {len(WITHHELD_SCOPE) + 1} files (design tables, search protocol, catalogue)')
    print(f'OK  manifest: {len(shipped)} files match MANIFEST.json (size and SHA-256)')
    print('all counts match; no measurement was executed; no estimate was validated')


if __name__ == '__main__':
    main()
