#!/usr/bin/env python3
"""Show one agent-design record end to end, then the systems-survey entries that share a locator with it.

Usage (from the component folder):
    python3 example/show_record.py AD-014 > example/output/AD-014.md

Reads data/agent-design/data/catalogue.json and example/input/survey-entries-sharing-a-locator.jsonl.
Python 3.9+, standard library; no network, no model. Output is deterministic.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CATALOGUE = os.path.join(ROOT, 'data', 'agent-design', 'data', 'catalogue.json')
SURVEY = os.path.join(HERE, 'input', 'survey-entries-sharing-a-locator.jsonl')
FIELD_ORDER = ['purpose', 'setting', 'mechanism', 'inputs_outputs', 'interfaces', 'evaluation', 'limitations', 'version']
FIELD_NAMES = {'purpose': 'Purpose and contribution', 'setting': 'Task and disciplinary setting', 'mechanism': 'Mechanism and procedure',
               'inputs_outputs': 'Inputs, outputs and representations', 'interfaces': 'Interfaces and dependencies',
               'evaluation': 'Reported evaluation and conditions', 'limitations': 'Limitations and contrary evidence',
               'version': 'Version, observation date and access'}

def norm(u):
    return u.rstrip('/').lower()

def main(record_id):
    cat = json.load(open(CATALOGUE, encoding='utf-8'))
    families = {f['id']: f for f in cat['families']}
    rec = next((r for r in cat['records'] if r['id'] == record_id), None)
    if rec is None:
        sys.exit(f'no record {record_id} in {CATALOGUE}')
    fam = families[rec['family']]
    out = []
    w = out.append
    w(f"# {rec['id']} · {rec['name']}")
    w('')
    w(f"Agent Design and Orchestration Database, edition {cat['as_of']}. Category: {fam['name']} ({fam['question']}). Kind: {rec['kind']}.")
    w('')
    w('## The record, field by field')
    w('')
    for label, key in [('Mechanism', 'mechanism'), ('Evidence', 'evidence'), ('Limitations', 'limitations'),
                       ('Possible use in TextData (a design interpretation, not an observed result)', 'textdata_use'),
                       ('Question an evaluation would have to answer', 'textdata_evaluation'),
                       ('Evidence basis', 'evidence_basis'), ('Reading scope', 'reading_scope'),
                       ('Implementation status', 'implementation_status'), ('Credit', 'credit')]:
        w(f"- **{label}.** {rec[key]}")
    w('')
    w('## Sources recorded for it')
    w('')
    w(f"Primary: {rec['primary_url']} · version: {rec['source_version']} · passage: {rec['primary_locator']}")
    w('')
    if rec['repository_urls']:
        w('Repositories (' + rec['repository_status'] + '):')
        for u in rec['repository_urls']:
            w(f'- {u}')
        w('')
    w(f"References ({len(rec['references'])} rows; a row is a reference, not an independent finding):")
    w('')
    w('| URL | Version | Passage | Observed |')
    w('| --- | --- | --- | --- |')
    for m in rec['references']:
        w(f"| {m['url']} | {m.get('version') or ''} | {m.get('locator') or ''} | {m.get('observed_at') or 'not recorded'} |")
    w('')
    # survey side
    urls = {norm(rec['primary_url'])} | {norm(u) for u in rec['repository_urls']} | {norm(m['url']) for m in rec['references']}
    entries = []
    with open(SURVEY, encoding='utf-8') as f:
        for line in f:
            e = json.loads(line)
            shared = sorted({u for u in e.get('links', []) if norm(u) in urls})
            if shared:
                entries.append((e, shared))
    entries.sort(key=lambda x: x[0]['id'])
    w('## The same component in the systems survey')
    w('')
    w(f"{len(entries)} survey entries share at least one locator with this record. The example gives selected project paraphrases. A shared locator is a connection to check, not an asserted identity.")
    w('')
    for e, shared in entries:
        w(f"### {e['id']} · {e['name']}")
        w('')
        w(f"Unit: {e['unit_type']}. Assessment state: {e['assessment_status']}. Identity: {e['identity_status']}.")
        w('')
        w('Shared locator(s): ' + '; '.join(shared))
        w('')
        gaps = e.get('field_gaps', [])
        for key in FIELD_ORDER:
            paras = e['fields'].get(key, [])
            if key in gaps:
                w(f"- **{FIELD_NAMES[key]}.** Gap: the extracted evidence does not settle this.")
                continue
            if not paras:
                continue
            w(f"- **{FIELD_NAMES[key]}.**")
            seen = set()
            for p in paras:
                if p['text'] in seen:
                    continue
                seen.add(p['text'])
                w(f"  - {p['text']}")
        rel = e.get('relevance', [])
        if rel:
            w(f"- **Connection to TextData ({rel[0]['basis']}).** {rel[0]['assessment']}")
        w('')
    w('## What the two readings give together')
    w('')
    w('AD-014 proposes interrupting a task and checking both its restart position and whether it repeats an external action. '
      'In issue 7417 the reporter describes repeated calls during checkpoint recovery. The report remains unconfirmed. '
      'The project did not execute this test, install a listed component or measure performance.')
    sys.stdout.write('\n'.join(out) + '\n')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'AD-014')
