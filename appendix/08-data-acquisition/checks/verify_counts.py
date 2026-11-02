#!/usr/bin/env python3
"""Verify the counts README.md and MANIFEST.json state, from the files in this folder.

  1. the retained collection: data/MANIFEST_INDEX.tsv (one line per monthly inventory) summed and compared with
     data/COVERAGE.json; data/packs.tsv reconciled (packs, releases, bytes); then the 321 monthly inventories in
     data/inventories/ opened, each checked against its index line (size and SHA-256), and every line recounted
  2. the email-redacted release run in example/output/run/: frame, inventory, raw files re-hashed against their inventory lines,
     verify records and separate historical comparison fingerprint records, against checks/expected.json
  3. the second retrieval (example/output/run-govinfo/) and example/compare_sites.py, run again here: every raw file
     of both runs re-hashed and its reading copy made again; the result must equal the kept example/output/SITES.json
  4. the replay: example/run_example.py is run and must reproduce the kept records
  5. both released text sets and every example-pack member are cleaned and scanned for reconstructed emails
  6. example/input/2020-12.tsv is the retained inventory for December 2020 (its SHA-256 is in MANIFEST_INDEX.tsv)

    python3 checks/verify_counts.py           (Python 3.9+, standard library, no network; about twenty seconds; writes nothing)
    python3 checks/verify_counts.py --record  (the same, and also writes checks/RESULT.json)

Exit code 0 means every count matched.
"""
import csv
import hashlib
import importlib.util
import re
import json
import os
import subprocess
import sys
import tarfile
import time

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
RUN = os.path.join(ROOT, 'example', 'output', 'run')
HIST = os.path.join(ROOT, 'example', 'historical')


def read_tsv(path):
    with open(path, encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle, delimiter='\t'))


def sha256_of(path):
    with open(path, 'rb') as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main():
    started = time.time()
    with open(os.path.join(ROOT, 'checks', 'expected.json'), encoding='utf-8') as handle:
        expected = json.load(handle)
    found, problems = {}, []

    # 1. the retained collection, from its inventory index
    index = read_tsv(os.path.join(DATA, 'MANIFEST_INDEX.tsv'))
    found['retained: monthly inventories'] = len(index)
    found['retained: document records'] = sum(int(r['rows']) for r in index)
    found['retained: records with a text file'] = sum(int(r['text']) for r in index)
    found['retained: records PDF only'] = sum(int(r['pdf_only']) for r in index)
    with open(os.path.join(DATA, 'COVERAGE.json'), encoding='utf-8') as handle:
        coverage = json.load(handle)
    for key, what in (('documents', 'retained: document records'), ('with_text', 'retained: records with a text file'),
                      ('pdf_only', 'retained: records PDF only'), ('packs', 'retained: monthly inventories')):
        if coverage[key] != found[what]:
            problems.append('COVERAGE.json %s = %s, index sums to %s' % (key, coverage[key], found[what]))
    found['retained: raw text bytes (coverage record)'] = coverage['raw_bytes']
    packs = read_tsv(os.path.join(DATA, 'packs.tsv'))
    found['retained: packs listed'] = len(packs)
    found['retained: annual releases'] = len(set(p['release'] for p in packs))
    found['retained: packed bytes'] = sum(int(p['pack_bytes']) for p in packs)
    found['retained: documents in packs'] = sum(int(p['documents']) for p in packs)
    if found['retained: documents in packs'] != found['retained: records with a text file']:
        problems.append('packs.tsv documents do not sum to the text records')
    month = next((r for r in index if r['month'] == '2020-12'), None)
    if not month or month['tsv_sha256'] != sha256_of(os.path.join(ROOT, 'example', 'input', '2020-12.tsv')):
        problems.append('example/input/2020-12.tsv is not the indexed inventory for 2020-12')

    # 1b. the monthly inventories themselves: each against its index line, then every line recounted
    by_month = {r['month']: r for r in index}
    pack_docs = {p['pack'][5:12]: int(p['documents']) for p in packs}
    archives = sorted(n for n in os.listdir(os.path.join(DATA, 'inventories')) if n.endswith('.tar.xz'))
    tally = dict.fromkeys(('files', 'matching', 'records', 'text', 'pdf', 'equal', 'fr', 'govinfo', 'image', 'email', 'untimed'), 0)
    for name in archives:
        with tarfile.open(os.path.join(DATA, 'inventories', name)) as tar:
            for member in tar.getmembers():
                if not member.isfile():
                    continue
                month = os.path.basename(member.name)[:-4]
                data = tar.extractfile(member).read()
                line = by_month.get(month)
                tally['files'] += 1
                tally['matching'] += bool(line and len(data) == int(line['tsv_bytes'])
                                          and hashlib.sha256(data).hexdigest() == line['tsv_sha256'])
                month_text = 0
                for row in csv.DictReader(data.decode('utf-8').splitlines(), delimiter='\t'):
                    tally['records'] += 1
                    if row['text_status'] != 'text':
                        tally['pdf'] += 1
                        continue
                    month_text += 1
                    tally['fr' if row['source_site'] == 'federalregister.gov' else 'govinfo'] += 1
                    tally['image'] += int(row['image_placeholders']) > 0
                    tally['email'] += int(row['hidden_emails']) > 0
                    tally['untimed'] += not row['fetched_at']
                tally['text'] += month_text
                tally['equal'] += month_text == pack_docs.get(month)
    found['inventories: archives'] = len(archives)
    found['inventories: monthly files'] = tally['files']
    found['inventories: monthly files matching the index'] = tally['matching']
    found['inventories: document records recounted'] = tally['records']
    found['inventories: records with a text file'] = tally['text']
    found['inventories: records PDF only'] = tally['pdf']
    found['inventories: months whose text records equal their pack'] = tally['equal']
    found['inventories: text records from federalregister.gov'] = tally['fr']
    found['inventories: text records from govinfo.gov'] = tally['govinfo']
    found['inventories: documents with counted image placeholders'] = tally['image']
    found['inventories: documents with coded e-mail addresses'] = tally['email']
    found['inventories: text records without a fetch time'] = tally['untimed']

    # 2. the sample run
    frame = read_tsv(os.path.join(RUN, 'frame.tsv'))
    inventory = read_tsv(os.path.join(RUN, 'inventory.tsv'))
    found['sample: identities listed by the index'] = len(frame)
    found['sample: inventory lines'] = len(inventory)
    text = [r for r in inventory if r['text_status'] == 'text']
    found['sample: text files held'] = len(text)
    found['sample: gaps (no text file)'] = len(inventory) - len(text)
    found['sample: raw bytes'] = sum(int(r['bytes']) for r in text)
    mismatched = 0
    for row in text:
        path = os.path.join(RUN, 'raw', '%s__%s.txt' % (row['date'], row['document_number']))
        if not os.path.exists(path) or os.path.getsize(path) != int(row['bytes']) or sha256_of(path) != row['sha256']:
            mismatched += 1
    found['sample: raw files differing from their inventory line'] = mismatched
    found['sample: documents with counted image placeholders'] = sum(1 for r in text if int(r['image_placeholders']))
    found['sample: documents with coded e-mail addresses'] = sum(1 for r in text if int(r['hidden_emails']))
    with open(os.path.join(RUN, 'verify.json'), encoding='utf-8') as handle:
        verify = json.load(handle)
    found['sample: verify.py exit code over the pack'] = verify['verify_py_exit_code']
    found['sample: raw files re-hashed by the verify stage'] = verify['raw_files_rehashed']
    with open(os.path.join(HIST, 'run', 'comparison.json'), encoding='utf-8') as handle:
        comparison = json.load(handle)
    for outcome in ('identical_bytes', 'bytes_differ', 'only_in_this_run', 'only_in_retained', 'status_differs', 'both_without_text'):
        found['historical first site: comparison ' + outcome] = comparison['outcomes'].get(outcome, 0)
    found['historical first site: identities retained in the window'] = comparison['identities_in_retained_window']
    found['historical first site: identical bytes from the same site as retained'] = comparison['identical_bytes_from_same_site']
    found['historical first site: identical bytes from the other site'] = comparison['identical_bytes_from_other_site']

    # 3. the second retrieval and the two-site comparison
    run2 = read_tsv(os.path.join(ROOT, 'example', 'output', 'run-govinfo', 'inventory.tsv'))
    found['second site: inventory lines'] = len(run2)
    found['second site: text files held'] = sum(1 for r in run2 if r['text_status'] == 'text')
    found['second site: files from govinfo.gov'] = sum(1 for r in run2 if r.get('source_site') == 'govinfo.gov')
    with open(os.path.join(HIST, 'run-govinfo', 'comparison.json'), encoding='utf-8') as handle:
        comparison2 = json.load(handle)
    found['historical second site: comparison identical_bytes'] = comparison2['outcomes'].get('identical_bytes', 0)
    found['historical second site: comparison bytes_differ'] = comparison2['outcomes'].get('bytes_differ', 0)
    sites = subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'example', 'compare_sites.py'), '--json'],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    if sites.returncode:
        problems.append('compare_sites.py failed:\n' + sites.stdout[-1500:])
        site_result = {}
    else:
        site_result = json.loads(sites.stdout)
    with open(os.path.join(ROOT, 'example', 'output', 'SITES.json'), encoding='utf-8') as handle:
        if json.load(handle) != site_result:
            problems.append('example/output/SITES.json is not what compare_sites.py produces from the kept files')
    for key in ('raw_bytes_same_from_both_sites', 'raw_bytes_differ_between_sites', 'reading_copies_same_from_both_sites',
                'reading_copies_differ_between_sites', 'retained_line_matches_the_site_it_names', 'retained_line_matches_neither_site'):
        found['release sites: ' + key.replace('_', ' ')] = site_result.get(key)
    found['release sites: differing raw all have coded e-mails'] = site_result.get('differing_raw_all_have_coded_emails')

    # Check the text that readers actually obtain, including addresses split across HTML tags.
    spec = importlib.util.spec_from_file_location('release_clean_text', os.path.join(ROOT, 'tool', 'clean_text.py'))
    cleaner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cleaner)
    email = re.compile(r'[A-Za-z0-9_.+%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
    raw_hits = 0
    for run_name in ('run', 'run-govinfo'):
        raw_dir = os.path.join(ROOT, 'example', 'output', run_name, 'raw')
        for name in sorted(os.listdir(raw_dir)):
            if name.endswith('.txt'):
                with open(os.path.join(raw_dir, name), 'rb') as handle:
                    raw_hits += len(email.findall(cleaner.clean(handle.read())))
    pack_hits = 0
    with tarfile.open(os.path.join(RUN, 'packs', 'text-2020-12.tar.xz')) as archive:
        for member in archive.getmembers():
            if member.isfile():
                pack_hits += len(email.findall(cleaner.clean(archive.extractfile(member).read())))
    found['privacy: emails in cleaned release copies'] = raw_hits
    found['privacy: emails in cleaned example pack'] = pack_hits

    # Historical original-file outcomes are checked from retained fingerprint records.
    historical = subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'example', 'verify_historical.py')],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    found['historical: fingerprint-record verification exit code'] = historical.returncode
    if historical.returncode:
        problems.append('historical fingerprint verification failed:\n' + historical.stdout[-1500:])

    # 4. the replay
    replay = subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'example', 'run_example.py')],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    found['replay: exit code'] = replay.returncode
    if replay.returncode:
        problems.append('replay failed:\n' + replay.stdout[-1500:])

    rows = []
    print('%-62s %14s %14s' % ('count', 'expected', 'found'))
    for what, value in expected.items():
        ok = found.get(what) == value
        if not ok:
            problems.append('%s: expected %s, found %s' % (what, value, found.get(what)))
        rows.append({'what': what, 'expected': value, 'found': found.get(what), 'ok': ok})
        print('%-62s %14s %14s%s' % (what, value, found.get(what), '' if ok else '   <-- MISMATCH'))
    for what in sorted(set(found) - set(expected)):
        print('%-62s %14s %14s' % (what, '', found[what]))
    result = {'date': time.strftime('%Y-%m-%d', time.gmtime()), 'python': sys.version.split()[0], 'seconds': round(time.time() - started),
              'all_counts_match': not problems, 'counts': rows, 'units': expected_units(), 'evidence_basis': 'historical-prefixed counts use original fingerprint records; sample, second-site and release-sites counts use email-redacted release copies', 'problems': problems}
    if '--record' in sys.argv[1:]:
        with open(os.path.join(ROOT, 'checks', 'RESULT.json'), 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(json.dumps(result, indent=2) + '\n')
    if problems:
        print('\nFAILED: %d problems' % len(problems))
        for p in problems[:20]:
            print('  ' + p)
        sys.exit(1)
    print('\nOK: all counts match (%ds)' % (time.time() - started))


def expected_units():
    return {'retained: *': 'document records (publication date + document number) unless named bytes, files or releases',
            'sample: *': 'document records of the two-day slice; raw files are email-redacted release copies under example/output/run/raw/',
            'historical*: *': 'original retrieval fingerprint records; withheld original text is not re-hashed',
            'privacy: *': 'email-pattern occurrences in text produced by the supplied cleaner' }


if __name__ == '__main__':
    main()
