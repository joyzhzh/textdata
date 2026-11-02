#!/usr/bin/env python3
"""Build the offline methods catalogue from docs/g9-design.

Standard library only; no network or model calls. Source locators and fingerprints
bind the generated formats to the supplied input files. No text is scored.
"""
import csv
from contextlib import closing
import hashlib
import io
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
G9 = ROOT / 'docs/g9-design'
OUT = ROOT / 'data/catalogue'
HTML = ROOT / 'docs/catalogue/index.html'
TEMPLATE = ROOT / 'tool/templates/catalogue-template.html'
DESIGN_FILES = ['README.md', 'CAMPAIGN_DESIGN.md', 'EXTRACTION_AND_VALIDATION.md', 'MISSIONS.md',
                'SEARCH_PROTOCOL.md', 'METHOD_FAMILIES.json', 'MISSIONS.json', 'LANES.jsonl',
                'APPLICATION_COVERAGE.csv', 'METHOD_APPLICABILITY.csv', 'REGISTRY_CONTRACTS.json']


def manifest():
    rows = []
    for name in DESIGN_FILES:
        data = (G9 / name).read_bytes()
        rows.append({'path': 'docs/g9-design/' + name, 'source_path': 'docs/g9-design/' + name,
                     'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
    return rows


def read_json(name):
    return json.loads((G9 / name).read_text())


def read_csv(name):
    with (G9 / name).open(newline='') as f:
        return list(csv.DictReader(f))


def ref(sources, name, locator):
    path = 'docs/g9-design/' + name
    return {'path': path, 'locator': locator,
            'sha256': next(r['sha256'] for r in sources if r['path'] == path)}


def build():
    sources = manifest()
    lanes = [json.loads(line) for line in (G9 / 'LANES.jsonl').read_text().splitlines() if line]
    methods, apps = read_json('METHOD_FAMILIES.json'), read_csv('APPLICATION_COVERAGE.csv')
    matrix, missions = read_csv('METHOD_APPLICABILITY.csv'), read_json('MISSIONS.json')
    registries = read_json('REGISTRY_CONTRACTS.json')
    lane_map = {r['lane_id']: r for r in lanes}
    records = []
    for r in methods:
        owner = lane_map[r['owner_lane']]
        records.append({'id': r['method_id'], 'kind': 'Method', 'title': r['title'],
            'owner_lane': r['owner_lane'], 'mission_id': owner['mission_id'],
            'question': owner['question'], 'subareas': owner['required_subareas'],
            'adverse_case': owner['required_adverse_case'], 'planned_output': owner['deliverable'],
            'status': 'Designed; applicability unassessed',
            'note': 'Question, subareas, adverse case and planned output describe the owner lane; some lanes serve more than one method family.',
            'source': ref(sources, 'METHOD_FAMILIES.json', 'method_id=' + r['method_id']),
            'detail_source': ref(sources, 'LANES.jsonl', 'lane_id=' + r['owner_lane'])})
    for r in apps:
        owner = lane_map[r['owner_lane']]
        records.append({'id': r['application_cell'], 'kind': 'Application', 'title': r['title'],
            'owner_lane': r['owner_lane'], 'mission_id': r['mission_id'],
            'question': owner['question'], 'subareas': r['required_subareas'].split(';'),
            'adverse_case': owner['required_adverse_case'], 'planned_output': owner['deliverable'],
            'status': 'Unsearched; 14 method entries unassessed', 'note': r['remaining_frontier'],
            'source': ref(sources, 'APPLICATION_COVERAGE.csv', 'application_cell=' + r['application_cell']),
            'detail_source': ref(sources, 'LANES.jsonl', 'lane_id=' + r['owner_lane'])})
    for i, r in enumerate(lanes, 1):
        records.append({'id': r['lane_id'], 'kind': 'Research question', 'title': r['title'],
            'owner_lane': r['lane_id'], 'mission_id': r['mission_id'],
            'question': r['question'], 'subareas': r['required_subareas'],
            'adverse_case': r['required_adverse_case'], 'planned_output': r['deliverable'],
            'status': 'Proposed research question; unsearched',
            'note': 'A question for future measurement research; no result is claimed.',
            'source': ref(sources, 'LANES.jsonl', f'line {i}; lane_id=' + r['lane_id'])})
    counts = {'method_families': len(methods), 'application_settings': len(apps),
              'research_lanes': len(lanes), 'missions': len(missions),
              'applicability_entries': len(matrix), 'registry_specifications': len(registries['registries']),
              'browsable_records': len(records), 'observed_novelty_results_in_this_release': 0}
    assert counts == {'method_families': 14, 'application_settings': 35, 'research_lanes': 61,
                      'missions': 12, 'applicability_entries': 490, 'registry_specifications': 6,
                      'browsable_records': 110, 'observed_novelty_results_in_this_release': 0}
    assert len({(r['application_cell'], r['method_id']) for r in matrix}) == 490
    assert all(r['applicability'] == 'unassessed' and r['evidence_state'] == 'unsearched' for r in matrix)
    assert all(r['status'] == 'designed_not_launched' and r['coverage_state'] == 'unsearched' for r in lanes)
    assert all(r['coverage_state'] == 'unsearched' for r in apps)
    assert {r['owner_lane'] for r in methods + apps} <= set(lane_map)
    assert {r['mission_id'] for r in lanes} == {r['mission_id'] for r in missions}
    catalogue = {'schema_version': 'textdata-novelty-design-catalogue-1',
        'title': 'Novelty measurement design catalogue', 'design_date': '2026-10-10',
        'release_status': 'Derived research-design catalogue; no empirical novelty scores',
        'counts': counts, 'records': records, 'methods': methods, 'applications': apps,
        'missions': missions, 'lanes': lanes, 'applicability': matrix,
        'registry_contracts': registries,
        'sources': sources,
        'editorial_scope': 'Record content is transcribed from the named source fields. Workflow and illustration prose in the HTML is a proposed TextData adaptation. No candidate literature claims or teaching-card results enter the catalogue.'}
    data = json.dumps(catalogue, ensure_ascii=False, indent=2) + '\n'
    # Build and validate a fresh database before touching any release output.
    # Existing releases are compared in full, read-only; never merge with stale rows.
    db = sqlite3.connect(':memory:')
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript('''
      CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS missions(mission_id TEXT PRIMARY KEY,title TEXT,status TEXT,payload_json TEXT);
      CREATE TABLE IF NOT EXISTS lanes(lane_id TEXT PRIMARY KEY,mission_id TEXT REFERENCES missions(mission_id),title TEXT,status TEXT,coverage_state TEXT,payload_json TEXT);
      CREATE TABLE IF NOT EXISTS methods(method_id TEXT PRIMARY KEY,title TEXT,owner_lane TEXT REFERENCES lanes(lane_id));
      CREATE TABLE IF NOT EXISTS applications(application_cell TEXT PRIMARY KEY,title TEXT,owner_lane TEXT REFERENCES lanes(lane_id),coverage_state TEXT,payload_json TEXT);
      CREATE TABLE IF NOT EXISTS applicability(application_cell TEXT REFERENCES applications(application_cell),method_id TEXT REFERENCES methods(method_id),applicability TEXT,evidence_state TEXT,rationale TEXT,source_refs TEXT,PRIMARY KEY(application_cell,method_id));
      CREATE TABLE IF NOT EXISTS registries(registry_id TEXT PRIMARY KEY,owner_lane TEXT REFERENCES lanes(lane_id),status TEXT,payload_json TEXT);
      CREATE TABLE IF NOT EXISTS catalogue_records(id TEXT PRIMARY KEY,kind TEXT,title TEXT,mission_id TEXT REFERENCES missions(mission_id),status TEXT,source_path TEXT,source_locator TEXT,payload_json TEXT);
      CREATE TABLE IF NOT EXISTS sources(path TEXT PRIMARY KEY,source_path TEXT,sha256 TEXT,byte_count INTEGER);
    ''')
    for k, v in {'schema_version': catalogue['schema_version'],
                 'release_status': catalogue['release_status'], 'design_date': catalogue['design_date']}.items():
        db.execute('INSERT INTO metadata VALUES (?,?)', (k, v))
    for r in missions:
        db.execute('INSERT INTO missions VALUES (?,?,?,?)', (r['mission_id'], r['title'], r['status'], json.dumps(r, ensure_ascii=False)))
    for r in lanes:
        db.execute('INSERT INTO lanes VALUES (?,?,?,?,?,?)', (r['lane_id'], r['mission_id'], r['title'], r['status'], r['coverage_state'], json.dumps(r, ensure_ascii=False)))
    for r in methods:
        db.execute('INSERT INTO methods VALUES (?,?,?)', (r['method_id'], r['title'], r['owner_lane']))
    for r in apps:
        db.execute('INSERT INTO applications VALUES (?,?,?,?,?)', (r['application_cell'], r['title'], r['owner_lane'], r['coverage_state'], json.dumps(r, ensure_ascii=False)))
    for r in matrix:
        db.execute('INSERT INTO applicability VALUES (?,?,?,?,?,?)', tuple(r[k] for k in ['application_cell', 'method_id', 'applicability', 'evidence_state', 'rationale', 'source_refs']))
    for r in registries['registries']:
        db.execute('INSERT INTO registries VALUES (?,?,?,?)', (r['registry_id'], r['owner_lane'], registries['status'], json.dumps(r, ensure_ascii=False)))
    for r in records:
        db.execute('INSERT INTO catalogue_records VALUES (?,?,?,?,?,?,?,?)', (r['id'], r['kind'], r['title'], r['mission_id'], r['status'], r['source']['path'], r['source']['locator'], json.dumps(r, ensure_ascii=False)))
    for r in sources:
        db.execute('INSERT INTO sources VALUES (?,?,?,?)', (r['path'], r['source_path'], r['sha256'], r['bytes']))
    db.commit()
    assert [json.loads(r[0]) for r in db.execute('SELECT payload_json FROM catalogue_records ORDER BY rowid')] == records
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert not db.execute('PRAGMA foreign_key_check').fetchall()
    sql_counts = {table: db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] for table in ['missions', 'lanes', 'methods', 'applications', 'applicability', 'registries', 'catalogue_records', 'sources']}
    assert sql_counts['catalogue_records'] == len(records) and sql_counts['applicability'] == len(matrix)
    template = TEMPLATE.read_text()
    assert '__CATALOGUE_JSON__' in template
    rendered_html = template.replace('__CATALOGUE_JSON__', data.replace('<', '\\u003c'))
    records_text = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records)
    csv_buffer = io.StringIO(newline='')
    writer = csv.DictWriter(csv_buffer, fieldnames=list(matrix[0]))
    writer.writeheader()
    writer.writerows(matrix)
    receipt = json.dumps({'counts': counts, 'sqlite_counts': sql_counts, 'integrity_check': 'ok', 'foreign_key_check': 'ok', 'source_statuses_preserved': True, 'novelty_scoring_run': False}, indent=2) + '\n'
    database = OUT / 'novelty-design.sqlite'
    if database.exists():
        with closing(sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True)) as existing:
            try:
                assert existing.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
                assert not existing.execute('PRAGMA foreign_key_check').fetchall()
                schema_query = 'SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name'
                assert existing.execute(schema_query).fetchall() == db.execute(schema_query).fetchall()
                tables = [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
                for table in tables:
                    query = f'SELECT * FROM {table} ORDER BY rowid'
                    assert existing.execute(query).fetchall() == db.execute(query).fetchall(), table
            except (AssertionError, sqlite3.DatabaseError) as exc:
                raise ValueError('Existing database differs; no outputs written. Preserve this release and build in a new named copy with no generated outputs.') from exc
    # Detect inputs changing during preparation, including prose-only source edits.
    assert manifest() == sources, 'Design inputs changed during build; no outputs written.'

    # All parsing, template and database checks precede publication. This is not
    # an atomic multi-file transaction against disk failure or concurrent writers.
    OUT.mkdir(parents=True, exist_ok=True)
    HTML.parent.mkdir(parents=True, exist_ok=True)
    if not database.exists():
        with sqlite3.connect(database) as target:
            db.backup(target)
        target.close()
    db.close()
    (OUT / 'catalogue.json').write_text(data)
    (OUT / 'records.jsonl').write_text(records_text)
    with (OUT / 'applicability.csv').open('w', newline='') as handle:
        handle.write(csv_buffer.getvalue())
    HTML.write_text(rendered_html)
    (OUT / 'BUILD_RECEIPT.json').write_text(receipt)
    print(json.dumps(counts))


if __name__ == '__main__':
    build()
