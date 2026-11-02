#!/usr/bin/env python3
"""Build the manifest: one line per Federal Register document.

Version 1 covers every document published 2000-01-01 .. 2026-09-15. Each
document is resolved to its single raw text file in the local collection, using
the collection's own ownership lists. Every file is opened and checked to be a
real document before its size and SHA-256 are recorded.

Writes  manifest/YYYY-MM.tsv   one file per month, one line per document
        COVERAGE.json          date range and counts
        local/source_paths.tsv where each file sits on this machine (not in git)

The source tree is only read, never written. If anything does not add up,
nothing is written except local/build_manifest_problems.tsv and the exit code
is 1.

    python3 scripts/build_manifest.py --source-root path/to/source-tree
    python3 scripts/build_manifest.py --source-root ... --months 2012-06 --out path/to/test-output

Release edition: the source tree's folder names below are neutral placeholders for the original working
tree's, and two labels are reworded (docs/RELEASE_CHANGES.md). The program needs that tree and cannot run
without it; it is kept as the record of how every inventory line was admitted.
"""
import argparse
import collections
import hashlib
import json
import os
import re
import sys
import time
from multiprocessing import get_context

# ---- what version 1 must contain (from the collection's frozen lists) -------
EXPECTED = {
    'documents': 806941,
    'with_text': 806237,
    'pdf_only': 704,
    'frozen_list': 803741,
    'delta': 3200,
    'july_govinfo_incl_stragglers': 132550,
    'stragglers': 20,
    'august_bulk': 282675,
    'fetch_set': 373245,
    'year_2026_jan_jul': 15271,
    'months': 321,
}
COVERAGE_START = '2000-01-01'
COVERAGE_END = '2026-09-15'

# ---- where things are, relative to --source-root ----------------------------
T = 'collection-workspace'
FROZEN_LIST = T + '/frozen-list-2026-07/identities.txt'
SLICES = T + '/month-slices'
PDF_ONLY_LIST = T + '/pdf-only-704/MANIFEST.json'
HOLDING_A = 'holding-a/{year}/html'                           # <date>_<docnum>_<hash16>.html
HOLDING_B = 'holding-b/{truck}/{year}/{date}__{docnum}.txt'
HOLDING_C = T + '/text/{month}/{year}/{date}__{docnum}.txt'
C_REGISTRIES = T + '/text/registries'
DELTA = 'holding-d/daily-archive'                             # records/<date>/<docnum>.txt
HOLDING_E = 'holding-e/resolution'

SITE_GOVINFO = 'govinfo.gov'
SITE_FR = 'federalregister.gov'

COLUMNS = ['date', 'document_number', 'text_status', 'source_site', 'collection_pass',
           'fetched_at', 'bytes', 'sha256', 'image_placeholders', 'hidden_emails']

IMAGE_PLACEHOLDER = b'[GRAPHIC] [TIFF OMITTED]'
HIDDEN_EMAIL = b'data-cfemail="'
FR_DOC_MARKER = b'[FR Doc No:'
DOCNUM_OK = re.compile(r'^[A-Za-z0-9._-]+$')
# Front/back-matter items that the official list includes but that have no FR Doc number: their
# "X" numbers are date-coded stand-ins, so the file has no "[FR Doc No:" line and does not contain
# its own number. 2007-02-02 X07-10202 is Reader Aids; the two 2009-12-30 items are Contents pages.
# Exempted by name from those two checks only (the researcher's decision, 22 Sep 2026); they must still
# open with the usual "[Federal Register Volume" header and pass every other check.
NO_FR_DOC_LINE = {'2007-02-02|X07-10202', '2009-12-30|X09-11230', '2009-12-30|X09-31230'}
VOLUME_HEADER = b'[Federal Register Volume'
WAIVED_FOR_NO_FR_DOC_LINE = {'no_FR_Doc_No_marker', 'own_document_number_missing'}
A_NAME = re.compile(r'^(\d{4}-\d{2}-\d{2})_(.+)_([0-9a-f]{16})\.html$')
E_NAME = re.compile(r'^(\d{4}-\d{2}-\d{2})_(.+)\.htm$')


def fail(message):
    print('STOP: ' + message, file=sys.stderr)
    sys.exit(1)


def read_lines(path):
    with open(path, encoding='utf-8') as handle:
        return [line.rstrip('\n') for line in handle if line.strip()]


def utc_seconds(value):
    """'2026-08-15T23:23:55.166572Z' or '...+00:00' -> '2026-08-15T23:23:55Z'."""
    if not value:
        return ''
    match = re.match(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.\d+)?(?:Z|\+00:00)$', value)
    return match.group(1) + 'Z' if match else ''


def normalized(text):
    return re.sub(r'[^A-Za-z0-9]', '', text).upper()


# ---- one file: open it, check it, measure it (runs in worker processes) -----
def check_file(task):
    identity, path, expected_sha, expected_bytes = task
    docnum = identity.split('|', 1)[1]
    problems = []
    try:
        with open(path, 'rb') as handle:
            data = handle.read()
    except OSError as exc:
        return identity, None, ['cannot_read:' + type(exc).__name__]
    sha = hashlib.sha256(data).hexdigest()
    lowered_head = data[:2000].lower()
    lowered_tail = data[-4000:].lower()
    if b'<html' not in lowered_head or b'<pre' not in lowered_head:
        problems.append('no_html_pre_wrapper_at_start')
    if b'</pre' not in lowered_tail:
        problems.append('no_closing_pre_at_end')
    if FR_DOC_MARKER not in data:
        problems.append('no_FR_Doc_No_marker')
    if identity in NO_FR_DOC_LINE and VOLUME_HEADER not in data[:2000]:
        problems.append('exempted_item_without_Federal_Register_Volume_header')
    number_exact = docnum.encode() in data
    number_loose = number_exact or normalized(docnum) in normalized(data.decode('utf-8', 'replace'))
    if not number_loose:
        problems.append('own_document_number_missing')
    if expected_sha and sha != expected_sha:
        problems.append('sha256_differs_from_collection_record')
    if expected_bytes >= 0 and len(data) != expected_bytes:
        problems.append('size_differs_from_collection_record')
    try:
        data.decode('utf-8')
        utf8 = True
    except UnicodeDecodeError:
        utf8 = False
    facts = {
        'bytes': len(data),
        'sha256': sha,
        'image_placeholders': data.count(IMAGE_PLACEHOLDER),
        'hidden_emails': data.count(HIDDEN_EMAIL),
        'number_only_after_normalizing': (not number_exact) and number_loose,
        'pre_blocks': data.lower().count(b'<pre'),
        'utf8': utf8,
    }
    return identity, facts, problems


def read_c_registry(path):
    """identity -> [(fetched_at, raw_sha256), ...] for captured rows of one year."""
    found = collections.defaultdict(list)
    with open(path, encoding='utf-8') as handle:
        for line in handle:
            if '"TEXT_CAPTURED"' not in line:
                continue
            row = json.loads(line)
            if row.get('status') == 'TEXT_CAPTURED':
                found[row['identity']].append((utc_seconds(row.get('completed_at_utc')), row.get('raw_sha256')))
    return dict(found)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--source-root', required=True, help='the local collection tree (read only)')
    parser.add_argument('--out', help='where to write (default: the repository root)')
    parser.add_argument('--months', nargs='+', help='test mode: only these months; totals are not enforced')
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args()

    started = time.time()
    root = os.path.abspath(args.source_root)
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.abspath(args.out) if args.out else repo
    test_months = set(args.months or [])
    if test_months and not args.out:
        fail('--months is a test mode; give --out so the real manifest is not overwritten')

    def wanted(identity):
        return not test_months or identity[:7] in test_months

    # ---- 1. the lists of what must exist -----------------------------------
    frozen = read_lines(os.path.join(root, FROZEN_LIST))
    if len(frozen) != EXPECTED['frozen_list'] or len(set(frozen)) != len(frozen):
        fail('frozen list: %d lines, %d unique; expected %d' % (len(frozen), len(set(frozen)), EXPECTED['frozen_list']))
    frozen_set = set(frozen)

    status = json.load(open(os.path.join(root, DELTA, 'STATUS.json')))
    if status.get('state') != 'COMPLETE' or status.get('coverage_end') != COVERAGE_END:
        fail('delta STATUS.json is not COMPLETE through %s' % COVERAGE_END)
    catalog_path = os.path.join(root, DELTA, 'catalogs', os.path.basename(status['catalog']))
    catalog = json.load(open(catalog_path))
    delta = [r['identity'] for r in catalog['records']]
    for record in catalog['records']:
        if record['identity'] != record['date'] + '|' + record['document_number']:
            fail('delta catalog identity does not match its date and number: ' + record['identity'])
    if len(delta) != EXPECTED['delta'] or len(set(delta)) != len(delta) or frozen_set & set(delta):
        fail('delta catalog: %d records, %d unique, %d overlap with frozen list'
             % (len(delta), len(set(delta)), len(frozen_set & set(delta))))

    everything = sorted(frozen_set | set(delta))
    for identity in everything:
        date, _, docnum = identity.partition('|')
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date) or not DOCNUM_OK.match(docnum):
            fail('identity with unexpected characters: %r' % identity)
        if not COVERAGE_START <= date <= COVERAGE_END:
            fail('identity outside the coverage window: ' + identity)

    pdf_only = set(r['identity'] for r in json.load(open(os.path.join(root, PDF_ONLY_LIST)))['records'])

    legacy, allowed, fetch = set(), {}, set()
    slice_ids = set()
    slices_dir = os.path.join(root, SLICES)
    months_seen = sorted(m for m in os.listdir(slices_dir) if re.match(r'^\d{4}-\d{2}$', m))
    for month in months_seen:
        folder = os.path.join(slices_dir, month)
        ids = read_lines(os.path.join(folder, 'identities.txt'))
        if any(not i.startswith(month) for i in ids) or len(set(ids)) != len(ids):
            fail('ownership list %s has foreign or duplicate lines' % month)
        slice_ids |= set(ids)
        legacy |= set(read_lines(os.path.join(folder, 'held_legacy.txt')))
        for line in read_lines(os.path.join(folder, 'held_allow_list.tsv')):
            identity, truck, sha, size = line.split('\t')
            if identity in allowed:
                fail('duplicate allow-list line: ' + identity)
            allowed[identity] = (truck, sha, int(size))
        fetch |= set(read_lines(os.path.join(folder, 'fetch_set.txt')))
        if os.path.getsize(os.path.join(folder, 'unexplained_gap.txt')):
            fail('ownership list %s has an unexplained gap' % month)
    pre_2026 = set(i for i in frozen_set if i < '2026-01-01')
    year_2026 = frozen_set - pre_2026
    counts_ok = (
        len(months_seen) == 312 and slice_ids == pre_2026
        and not (legacy & set(allowed)) and not (legacy & fetch) and not (set(allowed) & fetch)
        and (legacy | set(allowed) | fetch) == slice_ids
        and len(legacy) == EXPECTED['july_govinfo_incl_stragglers']
        and len(allowed) == EXPECTED['august_bulk']
        and len(fetch) == EXPECTED['fetch_set']
        and len(year_2026) == EXPECTED['year_2026_jan_jul']
        and len(pdf_only) == EXPECTED['pdf_only'] and pdf_only <= fetch
    )
    if not counts_ok:
        fail('ownership lists do not add up: months %d, legacy %d, allow-list %d, fetch set %d, 2026 %d, pdf-only %d'
             % (len(months_seen), len(legacy), len(allowed), len(fetch), len(year_2026), len(pdf_only)))

    # ---- 2. resolve every document to its one file -------------------------
    a_index = collections.defaultdict(list)
    for year in range(2000, 2026):
        folder = os.path.join(root, HOLDING_A.format(year=year))
        for name in os.listdir(folder):
            match = A_NAME.match(name)
            if match:
                a_index[match.group(1) + '|' + match.group(2)].append(os.path.join(folder, name))
    e_registry = json.load(open(os.path.join(root, HOLDING_E, 'RESOLUTION_REGISTRY.json')))
    e_time = utc_seconds(e_registry.get('fetched_at_utc'))
    e_records = {r['record_key']: r for r in e_registry['records']}
    e_index = {}
    for name in os.listdir(os.path.join(root, HOLDING_E, 'raw')):
        match = E_NAME.match(name)
        if match:
            e_index[match.group(1) + '|' + match.group(2)] = os.path.join(root, HOLDING_E, 'raw', name)

    rows = {}        # identity -> dict of manifest fields known before opening the file
    tasks = []       # (identity, path, expected sha or '', expected bytes or -1)
    unresolved = []
    for identity in everything:
        if not wanted(identity):
            continue
        date, _, docnum = identity.partition('|')
        year, month = date[:4], date[:7]
        if identity in pdf_only:
            rows[identity] = {'text_status': 'pdf_only'}
            continue
        expected_sha, expected_bytes, fetched_at = '', -1, ''
        if identity in legacy:
            candidates = a_index.get(identity, [])
            if len(candidates) == 1:
                path, site, how = candidates[0], SITE_GOVINFO, 'july_govinfo'
            elif not candidates and identity in e_index:
                path, site, how = e_index[identity], SITE_GOVINFO, 'stragglers_govinfo'
                record = e_records.get(identity) or {}
                expected_sha, expected_bytes, fetched_at = record.get('raw_sha256', ''), record.get('raw_bytes', -1), e_time
            else:
                unresolved.append((identity, 'july list: %d candidate files' % len(candidates)))
                continue
        elif identity in allowed:
            truck, expected_sha, expected_bytes = allowed[identity]
            path = os.path.join(root, HOLDING_B.format(truck=truck, year=year, date=date, docnum=docnum))
            site, how = SITE_FR, 'august_bulk'
        elif identity in fetch or identity in year_2026:
            path = os.path.join(root, HOLDING_C.format(month=month, year=year, date=date, docnum=docnum))
            site, how = SITE_FR, 'monthly_pass'
        else:
            path = os.path.join(root, DELTA, 'records', date, docnum + '.txt')
            site, how = SITE_FR, 'daily_delta'
            try:
                sidecar = json.load(open(path + '.json'))
            except OSError:
                unresolved.append((identity, 'delta record has no sidecar'))
                continue
            if sidecar.get('status') != 'CAPTURED' or sidecar.get('http_status') != 200 or sidecar.get('identity') != identity:
                unresolved.append((identity, 'delta sidecar is not a captured 200'))
                continue
            expected_sha, expected_bytes, fetched_at = sidecar.get('sha256', ''), sidecar.get('bytes', -1), utc_seconds(sidecar.get('checked_at'))
        if not os.path.isfile(path):
            unresolved.append((identity, 'file missing: ' + path))
            continue
        rows[identity] = {'text_status': 'text', 'source_site': site, 'collection_pass': how,
                          'fetched_at': fetched_at, 'path': path}
        tasks.append((identity, path, expected_sha, expected_bytes))
    for identity in pdf_only:
        if wanted(identity):
            date, _, docnum = identity.partition('|')
            ghost = os.path.join(root, HOLDING_C.format(month=date[:7], year=date[:4], date=date, docnum=docnum))
            if os.path.exists(ghost):
                unresolved.append((identity, 'listed as PDF-only but a text file exists: ' + ghost))
    print('resolved %d documents to files, %d PDF-only, %d unresolved (%.0fs)'
          % (len(tasks), sum(1 for r in rows.values() if r['text_status'] == 'pdf_only'), len(unresolved), time.time() - started), flush=True)

    # ---- 3. open every file -------------------------------------------------
    problems = list(unresolved)
    notes = collections.Counter()
    with get_context('fork').Pool(args.workers) as pool:
        years = sorted(set(i[:4] for i, r in rows.items() if r.get('collection_pass') == 'monthly_pass'))
        registry_files = [os.path.join(root, C_REGISTRIES, y + '.jsonl') for y in years]
        c_registry = {}
        for part in pool.imap_unordered(read_c_registry, [p for p in registry_files if os.path.isfile(p)]):
            c_registry.update(part)
        print('read the monthly-pass registries: %d captured rows (%.0fs)' % (len(c_registry), time.time() - started), flush=True)
        done = 0
        for identity, facts, file_problems in pool.imap_unordered(check_file, tasks, chunksize=200):
            done += 1
            if done % 100000 == 0:
                print('  opened %d files (%.0fs)' % (done, time.time() - started), flush=True)
            row = rows[identity]
            if identity in NO_FR_DOC_LINE and WAIVED_FOR_NO_FR_DOC_LINE & set(file_problems):
                file_problems = [p for p in file_problems if p not in WAIVED_FOR_NO_FR_DOC_LINE]
                notes['kept_without_FR_Doc_line_by_researcher_override'] += 1
            if facts:
                row.update(facts)
                if row['collection_pass'] == 'monthly_pass':
                    recorded = c_registry.get(identity)
                    if not recorded:
                        notes['monthly_pass_without_registry_row'] += 1
                    else:
                        matching = [t for t, sha in recorded if sha == facts['sha256']]
                        if matching:
                            row['fetched_at'] = matching[-1]
                        else:
                            file_problems.append('sha256_differs_from_collection_record')
                notes['number_found_only_after_normalizing'] += facts['number_only_after_normalizing']
                notes['files_with_more_than_one_pre_block'] += facts['pre_blocks'] > 1
                notes['files_not_valid_utf8'] += not facts['utf8']
            for problem in file_problems:
                problems.append((identity, problem))

    # ---- 4. totals ----------------------------------------------------------
    with_text = [i for i, r in rows.items() if r['text_status'] == 'text' and 'sha256' in r]
    without = [i for i, r in rows.items() if r['text_status'] == 'pdf_only']
    months = sorted(set(i[:7] for i in with_text))
    if not test_months:
        if len(rows) != EXPECTED['documents'] or len(with_text) != EXPECTED['with_text'] or len(without) != EXPECTED['pdf_only']:
            problems.append(('TOTALS', 'documents %d, with text %d, PDF-only %d; expected %d / %d / %d'
                             % (len(rows), len(with_text), len(without), EXPECTED['documents'], EXPECTED['with_text'], EXPECTED['pdf_only'])))
        if len(months) != EXPECTED['months']:
            problems.append(('TOTALS', 'months with text: %d; expected %d' % (len(months), EXPECTED['months'])))
        stragglers = sum(1 for r in rows.values() if r.get('collection_pass') == 'stragglers_govinfo')
        if stragglers != EXPECTED['stragglers']:
            problems.append(('TOTALS', 'stragglers: %d; expected %d' % (stragglers, EXPECTED['stragglers'])))

    os.makedirs(os.path.join(out, 'local'), exist_ok=True)
    problems_path = os.path.join(out, 'local', 'build_manifest_problems.tsv')
    if problems:
        with open(problems_path, 'w', encoding='utf-8') as handle:
            for identity, problem in sorted(problems):
                handle.write('%s\t%s\n' % (identity, problem))
        by_kind = collections.Counter(p for _, p in problems)
        print('\nSTOP: %d problems; nothing written except %s' % (len(problems), problems_path))
        for kind, count in by_kind.most_common(12):
            print('  %6d  %s' % (count, kind[:150]))
        sys.exit(1)
    if os.path.exists(problems_path):
        os.remove(problems_path)

    # ---- 5. write -----------------------------------------------------------
    manifest_dir = os.path.join(out, 'manifest')
    os.makedirs(manifest_dir, exist_ok=True)
    by_month = collections.defaultdict(list)
    for identity in sorted(rows, key=lambda i: tuple(i.split('|', 1))):
        by_month[identity[:7]].append(identity)
    for month, identities in by_month.items():
        with open(os.path.join(manifest_dir, month + '.tsv'), 'w', encoding='utf-8', newline='\n') as handle:
            handle.write('\t'.join(COLUMNS) + '\n')
            for identity in identities:
                date, _, docnum = identity.partition('|')
                row = rows[identity]
                if row['text_status'] == 'pdf_only':
                    values = [date, docnum, 'pdf_only', '', '', '', '', '', '', '']
                else:
                    values = [date, docnum, 'text', row['source_site'], row['collection_pass'], row['fetched_at'],
                              str(row['bytes']), row['sha256'], str(row['image_placeholders']), str(row['hidden_emails'])]
                handle.write('\t'.join(values) + '\n')
    with open(os.path.join(out, 'local', 'source_paths.tsv'), 'w', encoding='utf-8', newline='\n') as handle:
        for identity in sorted(with_text, key=lambda i: tuple(i.split('|', 1))):
            date, _, docnum = identity.partition('|')
            handle.write('%s\t%s\t%s\n' % (date, docnum, rows[identity]['path']))

    def tally(key):
        return dict(sorted(collections.Counter(rows[i][key] for i in with_text).items()))

    by_year = {}
    for identity, row in rows.items():
        entry = by_year.setdefault(identity[:4], {'documents': 0, 'with_text': 0, 'pdf_only': 0})
        entry['documents'] += 1
        entry['with_text' if row['text_status'] == 'text' else 'pdf_only'] += 1
    dates = sorted(i[:10] for i in rows)
    coverage = {
        'dataset': 'Federal Register full text',
        'version': 1,
        'coverage_start': COVERAGE_START,
        'coverage_end': COVERAGE_END,
        'first_publication_date': dates[0],
        'last_publication_date': dates[-1],
        'documents': len(rows),
        'with_text': len(with_text),
        'pdf_only': len(without),
        'packs': len(months),
        'raw_bytes': sum(rows[i]['bytes'] for i in with_text),
        'documents_with_image_placeholders': sum(1 for i in with_text if rows[i]['image_placeholders']),
        'documents_with_hidden_emails': sum(1 for i in with_text if rows[i]['hidden_emails']),
        'by_source_site': tally('source_site'),
        'by_collection_pass': tally('collection_pass'),
        'by_year': dict(sorted(by_year.items())),
    }
    if test_months:
        coverage['partial_test_build'] = sorted(test_months)
    with open(os.path.join(out, 'COVERAGE.json'), 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps(coverage, indent=2) + '\n')

    print('\nOK  documents %d | with text %d | PDF-only %d | months %d | raw text %.2f GB'
          % (len(rows), len(with_text), len(without), len(months), coverage['raw_bytes'] / 1e9))
    print('    by site: %s' % coverage['by_source_site'])
    print('    by pass: %s' % coverage['by_collection_pass'])
    print('    with image placeholders: %d | with hidden e-mail addresses: %d'
          % (coverage['documents_with_image_placeholders'], coverage['documents_with_hidden_emails']))
    print('    notes: %s' % dict(notes))
    print('    wrote %s, COVERAGE.json, local/source_paths.tsv in %s (%.0fs)' % ('manifest/', out, time.time() - started))


if __name__ == '__main__':
    main()
