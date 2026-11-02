#!/usr/bin/env python3
"""Compare the email-redacted release copies from the two official-site retrievals against the retained inventory.
Historical original-file results are separately checked by verify_historical.py; they cannot be re-hashed from these copies.

For every identity: are the raw bytes from the two sites the same; are the reading copies the same; which site's bytes
the retained collection holds; whether the retained line matches the run that used that site. Every raw file is
re-hashed and its reading copy made again here with the retained cleaner; both must agree with the run's records.

    python3 example/compare_sites.py           (no network; prints the result, writes nothing)
    python3 example/compare_sites.py --record  (also writes example/output/SITES.json and SITES.tsv)
    python3 example/compare_sites.py --json    (prints the result as JSON, for checks/verify_counts.py)
"""
import collections
import csv
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = {'federalregister.gov': os.path.join(HERE, 'output', 'run'), 'govinfo.gov': os.path.join(HERE, 'output', 'run-govinfo')}
RETAINED = os.path.join(HERE, 'input', '2020-12.tsv')
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tool'))
from clean_text import clean  # the retained cleaner, as the normalize stage uses it


def read_tsv(path):
    with open(path, encoding='utf-8', newline='') as handle:
        return {(r['date'], r['document_number']): r for r in csv.DictReader(handle, delimiter='\t')}


def reading_copy_hashes(run, inventory):
    """Re-hash every raw file and the reading copy made from it; stop if either disagrees with the run's records."""
    index = read_tsv(os.path.join(run, 'clean', 'INDEX.tsv'))
    hashes = {}
    for key, row in inventory.items():
        if row['text_status'] != 'text':
            continue
        name = '%s__%s.txt' % key
        with open(os.path.join(run, 'raw', name), 'rb') as handle:
            data = handle.read()
        hashes[key] = {'clean_sha256': hashlib.sha256(clean(data).encode('utf-8')).hexdigest()}
        if hashlib.sha256(data).hexdigest() != row['sha256'] or hashes[key]['clean_sha256'] != index[key]['clean_sha256']:
            sys.exit('%s: %s differs from its record' % (os.path.basename(run), name))
    return hashes


def main():
    inv = {site: read_tsv(os.path.join(run, 'inventory.tsv')) for site, run in RUNS.items()}
    copies = {site: reading_copy_hashes(run, inv[site]) for site, run in RUNS.items()}
    retained = read_tsv(RETAINED)
    keys = sorted(inv['federalregister.gov'])
    if set(keys) != set(inv['govinfo.gov']):
        sys.exit('the two runs list different identities')
    tally = collections.Counter()
    lines = []
    for key in keys:
        a, b = inv['federalregister.gov'][key], inv['govinfo.gov'][key]
        r = retained.get(key)
        raw_same = a['sha256'] == b['sha256']
        clean_same = copies['federalregister.gov'][key]['clean_sha256'] == copies['govinfo.gov'][key]['clean_sha256']
        site_used = a['source_site'] + '/' + b['source_site']
        retained_match = 'none'
        if r:
            if r['sha256'] == a['sha256'] and r['sha256'] == b['sha256']:
                retained_match = 'both'
            elif r['sha256'] == a['sha256']:
                retained_match = 'federalregister.gov'
            elif r['sha256'] == b['sha256']:
                retained_match = 'govinfo.gov'
        emails = int(a['hidden_emails']) > 0 or int(b['hidden_emails']) > 0
        outcome = ('raw same' if raw_same else 'raw differ') + ', ' + ('clean same' if clean_same else 'clean differ')
        tally[(outcome, 'coded e-mail' if emails else 'no coded e-mail', 'retained site ' + (r['source_site'] if r else 'none'),
               'retained matches ' + retained_match)] += 1
        lines.append({'date': key[0], 'document_number': key[1], 'raw_same': raw_same, 'clean_same': clean_same,
                      'sites_actually_used': site_used, 'coded_emails': emails,
                      'retained_site': r['source_site'] if r else '', 'retained_matches': retained_match})
    result = {
        'evidence_basis': 'email-redacted release copies; original retrieval results are recorded separately in example/historical/',
        'identities': len(keys),
        'raw_bytes_same_from_both_sites': sum(1 for l in lines if l['raw_same']),
        'raw_bytes_differ_between_sites': sum(1 for l in lines if not l['raw_same']),
        'reading_copies_same_from_both_sites': sum(1 for l in lines if l['clean_same']),
        'reading_copies_differ_between_sites': sum(1 for l in lines if not l['clean_same']),
        'differing_raw_all_have_coded_emails': all(l['coded_emails'] for l in lines if not l['raw_same']),
        'retained_line_matches_the_site_it_names': sum(1 for l in lines if l['retained_matches'] in ('both', l['retained_site'])),
        'retained_line_matches_neither_site': sum(1 for l in lines if l['retained_matches'] == 'none'),
        'breakdown': [{'outcome': k[0], 'emails': k[1], 'retained': k[2], 'match': k[3], 'documents': v} for k, v in sorted(tally.items())],
    }
    if '--record' in sys.argv[1:]:
        with open(os.path.join(HERE, 'output', 'SITES.json'), 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(json.dumps(result, indent=2) + '\n')
        with open(os.path.join(HERE, 'output', 'SITES.tsv'), 'w', encoding='utf-8', newline='\n') as handle:
            columns = list(lines[0])
            handle.write('\t'.join(columns) + '\n')
            for l in lines:
                handle.write('\t'.join(str(l[c]) for c in columns) + '\n')
    if '--json' in sys.argv[1:]:
        print(json.dumps(result))
        return
    for k, v in result.items():
        if k != 'breakdown':
            print('%-48s %s' % (k, v))
    for b in result['breakdown']:
        print('  %3d  %s | %s | %s | %s' % (b['documents'], b['outcome'], b['emails'], b['retained'], b['match']))


if __name__ == '__main__':
    main()
