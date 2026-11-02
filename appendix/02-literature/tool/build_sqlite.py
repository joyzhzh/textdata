#!/usr/bin/env python3
"""Rebuild a portable SQLite database from the shipped export.

    python3 tool/build_sqlite.py [--out literature.sqlite]

Creates one table, records, with the 14 fields of data/records.json.gz (one row per entry) and
indexes on source_catalogue, year and doi, then prints the row count. The SQLite file is created locally. Python 3.9+, standard library. Example query afterwards:
    sqlite3 literature.sqlite "SELECT source_catalogue, COUNT(*) FROM records GROUP BY 1;"
"""
import argparse, gzip, json, os, sqlite3
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), 'data', 'records.json.gz')
FIELDS = ['id','title','authors','year','journal','doi','url','source_catalogue','source_record_id',
          'abstract','abstract_on_file','abstract_source','reading_note','qualifications']
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default='literature.sqlite'); ap.add_argument('--data', default=DATA)
    a = ap.parse_args()
    if os.path.exists(a.out): raise SystemExit(f'{a.out} exists; choose another --out (nothing is overwritten)')
    with gzip.open(a.data, 'rt', encoding='utf-8') as f: d = json.load(f)
    con = sqlite3.connect(a.out)
    types = {'id': 'TEXT PRIMARY KEY', 'year': 'INTEGER', 'abstract_on_file': 'INTEGER'}
    con.execute('CREATE TABLE records (' + ', '.join(k + ' ' + types.get(k, 'TEXT') for k in FIELDS) + ')')
    con.executemany('INSERT INTO records VALUES (' + ','.join('?' * len(FIELDS)) + ')', ([r[k] for k in FIELDS] for r in d['records']))
    for c in ('source_catalogue', 'year', 'doi'): con.execute(f'CREATE INDEX records_{c} ON records({c})')
    con.execute("CREATE TABLE build_metadata (key TEXT PRIMARY KEY, value TEXT)")
    con.executemany('INSERT INTO build_metadata VALUES (?,?)', [('schema', d['schema']), ('release', d['release'])])
    con.commit(); n = con.execute('SELECT COUNT(*) FROM records').fetchone()[0]; con.close()
    print(f'{a.out}: {n} rows')
if __name__ == '__main__': main()
