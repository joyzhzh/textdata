#!/usr/bin/env python3
"""Verify final JSON/CSV parity, counts, synthesis hashes, worked outputs and the file manifest.
Python 3.9+, standard library, offline. Run from the component folder:
    python3 checks/verify_counts.py
"""
import csv, gzip, hashlib, io, json, os, re, subprocess, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
STATED = {'records': 10732, 'with_abstract_on_file': 107, 'abstract_text_shipped': 0, 'with_reading_note': 8236,
          'by_catalogue': {'annotation_checkpoint': 318, 'annotation_successor': 319, 'annotation_journals': 8222, 'catalogue_d': 1873},
          'fields': 14, 'syntheses': 3, 'syntheses_shipped': 2}
fails = []
def check(cond, msg):
    if not cond: fails.append(msg)
def usable(v): return isinstance(v, str) and v.strip() != ''
with gzip.open(P('data', 'records.json.gz'), 'rt', encoding='utf-8') as f: d = json.load(f)
recs = d['records']
with gzip.open(P('data', 'records.csv.gz'), 'rt', encoding='utf-8', newline='') as f: rows = list(csv.DictReader(f))
summary = json.load(open(P('data', 'summary.json'), encoding='utf-8'))
counts = {'records': len(recs), 'with_abstract_on_file': sum(r['abstract_on_file'] for r in recs),
          'abstract_text_shipped': sum(usable(r['abstract']) for r in recs),
          'with_reading_note': sum(usable(r['reading_note']) for r in recs),
          'by_catalogue': dict(collections.Counter(r['source_catalogue'] for r in recs))}
# Abstract text is withheld: null in every JSON entry, empty in every CSV row.
check(all(r['abstract'] is None for r in recs), 'a JSON entry carries an abstract value')
check(all(c['abstract'] == '' for c in rows), 'a CSV row carries abstract text')
check(all(len(r) == STATED['fields'] for r in recs), 'a JSON entry does not have 14 fields')
check(len(rows) == len(recs) and [r['id'] for r in rows] == [r['id'] for r in recs], 'CSV and JSON exports differ in entries or order')
for k in summary['fields']:
    def csv_value(v): return '' if v is None else str(v).lower() if isinstance(v, bool) else str(v)
    check(all(csv_value(r[k]) == c[k] for r, c in zip(recs, rows)), f'CSV {k} differs from JSON {k}')
check(d['schema'] == summary['schema'] == 'textdata-literature/2', 'schema mismatch')
check(all(list(r) == summary['fields'] for r in recs), 'record field order differs from schema')
check(all(isinstance(r['abstract_on_file'], bool) for r in recs), 'abstract availability is not boolean')
for k in ('records', 'with_abstract_on_file', 'abstract_text_shipped', 'with_reading_note', 'by_catalogue'):
    check(counts[k] == STATED[k], f'shipped {k}: recount {counts[k]} != stated {STATED[k]}')
    check(counts[k] == summary['shipped'][k], f'shipped {k}: recount {counts[k]} != data/summary.json {summary["shipped"][k]}')
for k, f in (('with_url', 'url'), ('with_doi', 'doi')):
    check(sum(usable(r[f]) for r in recs) == summary['shipped'][k], f'shipped {k}: recount differs from data/summary.json')
ids = {r['id'] for r in recs}
check(len(ids) == len(recs), 'duplicate IDs in export')
check(all(r['id'].startswith(r['source_catalogue'] + ':') for r in recs), 'record ID and catalogue label differ')
syn = json.load(open(P('docs', 'SYNTHESES.json'), encoding='utf-8'))
check(len(syn['documents']) == STATED['syntheses'] and sum(s['shipped'] for s in syn['documents']) == STATED['syntheses_shipped'], 'synthesis counts differ from 3 (2 shipped)')
for s in syn['documents']:
    if s['shipped']:
        h = hashlib.sha256(open(P('docs', s['file']), 'rb').read()).hexdigest()
        check(h == s['sha256'], f'{s["file"]}: SHA-256 {h[:12]} != recorded {s["sha256"][:12]}')
    else:
        check(set(s) <= {'slug', 'file', 'shipped', 'title', 'withheld_reason'} and s.get('title') == 'A third synthesis, withheld', 'held synthesis metadata is not generic')
        check(not os.path.exists(P('docs', s['slug'] + '.md')), f'{s["slug"]} is marked withheld but a file is present')
# The worked example: rerun tool/query.py and compare with the stored outputs.
q = json.load(open(P('example', 'input', 'QUERY.json'), encoding='utf-8'))
def run(*args):
    out = subprocess.run([sys.executable, P('tool', 'query.py'), *args], capture_output=True, text=True, check=True).stdout
    return json.loads(out)
check(run('--counts') == json.load(open(P('example', 'output', 'counts.json'), encoding='utf-8')) == counts, 'example/output/counts.json differs from a fresh recount')
rec = json.load(open(P('example', 'output', 'record-W026.json'), encoding='utf-8'))
check(run('--id', q['id']) == rec, 'example/output/record-W026.json differs from a fresh run of tool/query.py')
check(run('--search', 'inter-rater reliability') == json.load(open(P('example', 'output', 'search-inter-rater-reliability.json'), encoding='utf-8')), 'example search output differs from a fresh run')
e = rec['entry']
check(e['abstract'] is None and e['abstract_on_file'] and usable(e['reading_note']), 'example should have an abstract available and a reading note')
# MANIFEST.json lists every other file with its size and SHA-256.
man = json.load(open(P('MANIFEST.json'), encoding='utf-8'))
listed = {f['path']: f for f in man['files']}
present = set()
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [x for x in dn if x != '__pycache__']
    for f in fn:
        rel = os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, '/')
        if rel != 'MANIFEST.json' and not f.startswith('.'): present.add(rel)
check(present == set(listed), f'MANIFEST.json and the folder differ: unlisted {sorted(present - set(listed))[:5]}, missing {sorted(set(listed) - present)[:5]}')
for rel in present & set(listed):
    b = open(P(rel), 'rb').read()
    check(len(b) == listed[rel]['bytes'] and hashlib.sha256(b).hexdigest() == listed[rel]['sha256'], f'{rel}: size or SHA-256 differs from MANIFEST.json')
if fails:
    print('\n'.join('FAIL ' + m for m in fails)); sys.exit(1)
print('all counts match'); print(json.dumps(counts, indent=1))
