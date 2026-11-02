#!/usr/bin/env python3
"""Check historical comparison records from original fingerprints, without the withheld original text.

The original 169/22 comparison and original reading-copy equality are historical evidence.
The email-redacted copies in output/ are checked separately by compare_sites.py and run_example.py.
Python 3.9+, standard library, offline; writes nothing.
"""
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

def rows(path):
    with path.open(encoding='utf-8', newline='') as h:
        data = list(csv.DictReader(h, delimiter='\t'))
    keyed = {(r['date'], r['document_number']): r for r in data}
    if len(keyed) != len(data):
        raise ValueError('duplicate identity in ' + path.name)
    return keyed

def main():
    retained = rows(HERE / 'input/2020-12.tsv')
    provenance = json.loads((HERE / 'RELEASE_PROVENANCE.json').read_text())['records']
    provenance = {(r['run'], r['file']): r for r in provenance}
    inventories, clean = {}, {}
    results = {}
    for run in ('run', 'run-govinfo'):
        hist = HERE / 'historical' / run
        inv = rows(hist / 'inventory.tsv')
        source = json.loads((hist / 'source.json').read_text())
        window = {k: v for k, v in retained.items() if source['window_start'] <= k[0] <= source['window_end']}
        assert set(inv) == set(window), 'historical identities differ'
        comparison = rows(hist / 'comparison.tsv')
        assert set(comparison) == set(inv), 'historical comparison identity set differs'
        outcomes = {}
        for key, row in inv.items():
            old = window[key]
            same = (row['bytes'], row['sha256']) == (old['bytes'], old['sha256'])
            outcome = 'identical_bytes' if same else 'bytes_differ'
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
            recorded = comparison[key]
            assert recorded['outcome'] == outcome
            assert recorded['run_sha256'] == row['sha256']
            assert recorded['retained_sha256'] == old['sha256']
            name = '%s__%s.txt' % key
            p = provenance[(run, name)]
            assert p['original_sha256'] == row['sha256'] and p['original_bytes'] == int(row['bytes'])
            released = (HERE / 'output' / run / 'raw' / name).read_bytes()
            assert p['release_sha256'] == hashlib.sha256(released).hexdigest()
            assert p['release_bytes'] == len(released)
        recorded = json.loads((hist / 'comparison.json').read_text())
        assert recorded['outcomes'] == outcomes
        results[run] = {'identities': len(inv), 'outcomes_from_original_fingerprint_records': outcomes}
        inventories[run] = inv
        clean[run] = rows(hist / 'clean/INDEX.tsv')
        assert set(clean[run]) == set(inv)
    assert set(inventories['run']) == set(inventories['run-govinfo'])
    same_reading = sum(clean['run'][key]['clean_sha256'] == clean['run-govinfo'][key]['clean_sha256'] for key in inventories['run'])
    sites = json.loads((HERE / 'historical/SITES.json').read_text())
    keys = set(inventories['run'])
    raw_same = sum(inventories['run'][k]['sha256'] == inventories['run-govinfo'][k]['sha256'] for k in keys)
    neither = sum(retained[k]['sha256'] not in (inventories['run'][k]['sha256'], inventories['run-govinfo'][k]['sha256']) for k in keys)
    matched_named_site = sum(retained[k]['sha256'] == inventories['run' if retained[k]['source_site'] == 'federalregister.gov' else 'run-govinfo'][k]['sha256'] for k in keys)
    assert sites['raw_bytes_same_from_both_sites'] == raw_same == 61
    assert sites['raw_bytes_differ_between_sites'] == len(keys) - raw_same == 130
    assert sites['retained_line_matches_neither_site'] == neither == 22
    assert sites['retained_line_matches_the_site_it_names'] == matched_named_site == 169
    assert sites['reading_copies_differ_between_sites'] == len(keys) - same_reading == 0
    assert all(int(inventories['run'][k]['hidden_emails']) > 0 or int(inventories['run-govinfo'][k]['hidden_emails']) > 0 for k in keys if inventories['run'][k]['sha256'] != inventories['run-govinfo'][k]['sha256'])
    assert sites['differing_raw_all_have_coded_emails'] is True
    assert same_reading == sites['reading_copies_same_from_both_sites'] == 191
    assert results['run']['outcomes_from_original_fingerprint_records'] == {'identical_bytes': 169, 'bytes_differ': 22}
    results['original_reading_copy_fingerprints_equal'] = same_reading
    results['basis'] = 'Historical fingerprint records; withheld original text was not re-hashed. Released text provenance was re-hashed.'
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
