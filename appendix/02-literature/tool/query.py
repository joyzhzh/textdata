#!/usr/bin/env python3
"""Open one entry of the literature database, or search its metadata, without a server.

    python3 tool/query.py --id annotation_checkpoint:W026 [--out example/output/record-W026.json]
    python3 tool/query.py --search "inter-rater reliability" [--limit 25]
    python3 tool/query.py --counts

Reads the final 14-field export. Abstract prose is not distributed; abstract_on_file records
availability and abstract_source gives a public reading destination. Search matches title,
authors, journal, year, DOI and IDs, folding typographic hyphens. It does not search notes.
Python 3.9+, standard library.
"""
import argparse, gzip, json, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), 'data', 'records.json.gz')
def fold(s): return re.sub(r'[‐‑‒–—−]', '-', (s or '')).lower()
def load(path=DATA):
    with gzip.open(path, 'rt', encoding='utf-8') as f: return json.load(f)
def usable(v): return isinstance(v, str) and v.strip() != ''
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--id'); ap.add_argument('--search'); ap.add_argument('--counts', action='store_true')
    ap.add_argument('--limit', type=int, default=25); ap.add_argument('--out'); ap.add_argument('--data', default=DATA)
    a = ap.parse_args(); d = load(a.data); recs = d['records']
    if a.counts:
        out = {'records': len(recs), 'with_abstract_on_file': sum(r['abstract_on_file'] for r in recs),
               'abstract_text_shipped': sum(usable(r['abstract']) for r in recs),
               'with_reading_note': sum(usable(r['reading_note']) for r in recs),
               'by_catalogue': dict(collections.Counter(r['source_catalogue'] for r in recs))}
    elif a.id:
        m = [r for r in recs if r['id'] == a.id]
        if not m: sys.exit(f'no entry with id {a.id}')
        r = m[0]
        out = {'entry': r,
               'held_text': {'abstract_on_file': r['abstract_on_file'], 'abstract_text_shipped': usable(r['abstract']),
                             'reading_note': usable(r['reading_note'])},
               'read_the_abstract_at': r['url'] or (('https://doi.org/' + r['doi']) if usable(r['doi']) else None)}
    elif a.search:
        q = fold(a.search)
        m = [r for r in recs if q in fold(' '.join(str(r[k]) for k in ('title','authors','journal','year','doi','id','source_record_id') if r[k] is not None))]
        out = {'query': a.search, 'matching_entries': len(m),
               'entries': [{k: r[k] for k in ('id','title','authors','year','journal','doi')} | {'abstract_on_file': r['abstract_on_file'], 'has_reading_note': usable(r['reading_note'])} for r in m[:a.limit]]}
    else: ap.error('give --id, --search or --counts')
    text = json.dumps(out, indent=1, ensure_ascii=False)
    if a.out:
        with open(a.out, 'w', encoding='utf-8') as f: f.write(text + '\n')
        print(f'wrote {a.out}')
    else: print(text)
if __name__ == '__main__': main()
