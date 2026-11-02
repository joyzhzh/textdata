#!/usr/bin/env python3
"""Large-scale data acquisition: six stages from a source definition to a verified, packaged collection.

    define     write run/source.json: adapter, window, identity rule, site order, politeness
    retrieve   list every document in the window from the source's own index (run/frame.tsv), then download
               each text to run/raw/ with a sidecar record; resumable; the only stage that uses the network
    inventory  open every raw file, apply the source's checks, record size, SHA-256, site, defects;
               run/inventory.tsv (one line per document in the frame, gaps included) and run/problems.tsv
    normalize  reading copies in run/clean/ (the cleaner keeps the raw file untouched)
    package    one deterministic pack per month in run/packs/ and the collection tree in run/collection/
               (manifest/YYYY-MM.tsv, COVERAGE.json, packs.tsv): the same layout as the retained collection
    verify     re-hash every raw file against the inventory, then run verify.py over the packs
    compare    match the run's inventory against a retained manifest (identities, status, bytes, SHA-256)

    python3 tool/acquire.py all --run example/output/run --adapter federal_register --start 2020-12-07 --end 2020-12-08
    python3 tool/acquire.py retrieve --run RUN           (resume an interrupted download)
    python3 tool/acquire.py compare --run RUN --retained path/to/manifest-or-folder-or-tar.xz

Python 3.9+, standard library only. Network is used by `retrieve` alone.
"""
import argparse
import collections
import csv
import datetime
import hashlib
import http.client
import importlib
import json
import os
import re
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'historical'))
sys.dont_write_bytecode = True

COLUMNS = ['date', 'document_number', 'text_status', 'source_site', 'collection_pass',
           'fetched_at', 'bytes', 'sha256', 'image_placeholders', 'hidden_emails']
PACKS_COLUMNS = ['pack', 'release', 'documents', 'raw_bytes', 'pack_bytes', 'sha256']
USER_AGENT = 'textdata-data-acquisition/0.1 (research toolkit; standard-library urllib)'


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def sha256_of(data):
    return hashlib.sha256(data).hexdigest()


def days(start, end):
    day = datetime.date.fromisoformat(start)
    last = datetime.date.fromisoformat(end)
    while day <= last:
        yield day.isoformat()
        day += datetime.timedelta(days=1)


def read_tsv(path):
    with open(path, encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle, delimiter='\t'))


def write_tsv(path, columns, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write('\t'.join(columns) + '\n')
        for row in rows:
            handle.write('\t'.join(str(row.get(c, '')) for c in columns) + '\n')


def load_source(run):
    with open(os.path.join(run, 'source.json'), encoding='utf-8') as handle:
        source = json.load(handle)
    return source, importlib.import_module('adapters.' + source['adapter'])


def file_name(identity):
    return '%s__%s.txt' % (identity['date'], identity['document_number'])


# ---------------------------------------------------------------- HTTP (retrieve only)
class Http:
    def __init__(self, delay, tries, timeout, log):
        self.delay, self.tries, self.timeout, self.log = delay, tries, timeout, log
        self.last = 0.0
        self.requests = 0

    def __call__(self, url):
        """-> (status, bytes). Waits `delay` seconds between requests; retries on 429, 5xx, network errors and incomplete reads."""
        for attempt in range(1, self.tries + 1):
            wait = self.delay - (time.time() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()
            self.requests += 1
            try:
                request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': '*/*'})
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    return response.status, response.read()
            except urllib.error.HTTPError as exc:
                status, body = exc.code, exc.read() if exc.fp else b''
                if status not in (429, 500, 502, 503, 504) or attempt == self.tries:
                    return status, body
                self.log('retry', url, 'HTTP %d, attempt %d' % (status, attempt))
            except (urllib.error.URLError, http.client.HTTPException, TimeoutError, OSError) as exc:
                if attempt == self.tries:
                    return 0, str(exc).encode()
                self.log('retry', url, '%s, attempt %d' % (type(exc).__name__, attempt))
            time.sleep(min(60, self.delay * (2 ** attempt)))
        return 0, b''


# ---------------------------------------------------------------- stages
def stage_define(args):
    source = {
        'adapter': args.adapter, 'window_start': args.start, 'window_end': args.end,
        'identity': 'publication date + document number', 'filters': 'none: every document the index lists',
        'site_order': args.site_order.split(','), 'delay_seconds': args.delay, 'tries': args.tries,
        'timeout_seconds': args.timeout, 'collection_pass': args.pass_name or 'run_' + time.strftime('%Y%m%d', time.gmtime()),
        'defined_at': utc_now(), 'user_agent': USER_AGENT,
    }
    os.makedirs(args.run, exist_ok=True)
    with open(os.path.join(args.run, 'source.json'), 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps(source, indent=2) + '\n')
    print('define: %s, %s to %s, sites %s' % (source['adapter'], args.start, args.end, source['site_order']))


def stage_retrieve(args):
    source, adapter = load_source(args.run)
    raw_dir = os.path.join(args.run, 'raw')
    os.makedirs(raw_dir, exist_ok=True)
    log_path = os.path.join(args.run, 'retrieve_log.tsv')

    def log(outcome, url, detail=''):
        with open(log_path, 'a', encoding='utf-8') as handle:
            handle.write('%s\t%s\t%s\t%s\n' % (utc_now(), outcome, url, detail))

    http = Http(source['delay_seconds'], source['tries'], source['timeout_seconds'], log)
    frame_path = os.path.join(args.run, 'frame.tsv')
    if os.path.exists(frame_path) and not args.refresh_frame:
        frame = read_tsv(frame_path)
        print('retrieve: frame already listed, %d identities (use --refresh-frame to list again)' % len(frame))
    else:
        frame = list(adapter.list_identities(http, source['window_start'], source['window_end'], days))
        keys = [(r['date'], r['document_number']) for r in frame]
        if len(set(keys)) != len(keys):
            sys.exit('STOP: the index returned a duplicate identity')
        frame.sort(key=lambda r: (r['date'], r['document_number']))
        write_tsv(frame_path, ['date', 'document_number', 'type', 'text_url'], frame)
        log('frame', frame_path, '%d identities' % len(frame))
        print('retrieve: listed %d identities for %s to %s' % (len(frame), source['window_start'], source['window_end']))

    done = skipped = failed = 0
    for identity in frame:
        target = os.path.join(raw_dir, file_name(identity))
        sidecar = target + '.json'
        if os.path.exists(sidecar) and os.path.exists(target):
            with open(sidecar, encoding='utf-8') as handle:
                record = json.load(handle)
            if record.get('http_status') == 200:
                with open(target, 'rb') as handle:
                    if sha256_of(handle.read()) == record.get('sha256'):
                        skipped += 1
                        continue
        record = {'identity': identity['date'] + '|' + identity['document_number'], 'attempts': []}
        for site, url in adapter.text_urls(identity, source['site_order']):
            status, data = http(url)
            problems = adapter.check_text(data, identity) if status == 200 else []
            record['attempts'].append({'site': site, 'url': url, 'http_status': status, 'bytes': len(data),
                                       'checked_at': utc_now(), 'problems': problems})
            if status == 200 and not problems:
                with open(target, 'wb') as handle:
                    handle.write(data)
                record.update({'site': site, 'url': url, 'http_status': 200, 'bytes': len(data),
                               'sha256': sha256_of(data), 'fetched_at': utc_now()})
                done += 1
                log('captured', url, '%d bytes' % len(data))
                break
            log('rejected', url, 'HTTP %s %s' % (status, ';'.join(problems)))
        else:
            record['http_status'] = record['attempts'][-1]['http_status'] if record['attempts'] else 0
            failed += 1
            if os.path.exists(target):
                os.replace(target, target + '.rejected')
        with open(sidecar, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(json.dumps(record, indent=2) + '\n')
        if (done + failed) % 25 == 0:
            print('  %d captured, %d skipped, %d without text, %d requests' % (done, skipped, failed, http.requests), flush=True)
    print('retrieve: %d captured, %d already held, %d without text; %d HTTP requests' % (done, skipped, failed, http.requests))


def stage_inventory(args):
    source, adapter = load_source(args.run)
    frame = read_tsv(os.path.join(args.run, 'frame.tsv'))
    raw_dir = os.path.join(args.run, 'raw')
    rows, problems, extra = [], [], []
    for identity in frame:
        key = identity['date'] + '|' + identity['document_number']
        target = os.path.join(raw_dir, file_name(identity))
        sidecar = target + '.json'
        base = {'date': identity['date'], 'document_number': identity['document_number']}
        if not (os.path.exists(target) and os.path.exists(sidecar)):
            rows.append(dict(base, text_status='pdf_only'))
            reason = 'no text file retrieved'
            if os.path.exists(sidecar):
                with open(sidecar, encoding='utf-8') as handle:
                    attempts = json.load(handle).get('attempts', [])
                reason += ': ' + '; '.join('%s HTTP %s %s' % (a['site'], a['http_status'], ','.join(a['problems'])) for a in attempts)
            problems.append({'identity': key, 'problem': reason})
            continue
        with open(target, 'rb') as handle:
            data = handle.read()
        with open(sidecar, encoding='utf-8') as handle:
            record = json.load(handle)
        file_problems = adapter.check_text(data, identity)
        sha = sha256_of(data)
        if record.get('sha256') != sha or record.get('bytes') != len(data):
            file_problems.append('file_differs_from_its_retrieval_record')
        if file_problems:
            rows.append(dict(base, text_status='pdf_only'))
            for p in file_problems:
                problems.append({'identity': key, 'problem': p})
            continue
        defects = adapter.defect_counts(data)
        rows.append(dict(base, text_status='text', source_site=record['site'], collection_pass=source['collection_pass'],
                         fetched_at=record.get('fetched_at', ''), bytes=len(data), sha256=sha,
                         image_placeholders=defects['image_placeholders'], hidden_emails=defects['hidden_emails']))
        extra.append(dict(base, **{k: v for k, v in defects.items() if k not in ('image_placeholders', 'hidden_emails')}))
    rows.sort(key=lambda r: (r['date'], r['document_number']))
    write_tsv(os.path.join(args.run, 'inventory.tsv'), COLUMNS, rows)
    write_tsv(os.path.join(args.run, 'problems.tsv'), ['identity', 'problem'], problems)
    if extra:
        write_tsv(os.path.join(args.run, 'defects_extra.tsv'), list(extra[0]), extra)
    with_text = [r for r in rows if r['text_status'] == 'text']
    summary = {
        'documents': len(rows), 'with_text': len(with_text), 'pdf_only': len(rows) - len(with_text),
        'raw_bytes': sum(r['bytes'] for r in with_text),
        'documents_with_image_placeholders': sum(1 for r in with_text if r['image_placeholders']),
        'documents_with_hidden_emails': sum(1 for r in with_text if r['hidden_emails']),
        'by_source_site': dict(collections.Counter(r['source_site'] for r in with_text)),
        'problems': len(problems), 'inventoried_at': utc_now(),
    }
    with open(os.path.join(args.run, 'inventory_summary.json'), 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps(summary, indent=2) + '\n')
    print('inventory: %d documents | %d with text | %d without | %d problems' % (len(rows), len(with_text), len(rows) - len(with_text), len(problems)))


def stage_normalize(args):
    from clean_text import clean
    rows = read_tsv(os.path.join(args.run, 'inventory.tsv'))
    clean_dir = os.path.join(args.run, 'clean')
    os.makedirs(clean_dir, exist_ok=True)
    index = []
    for row in rows:
        if row['text_status'] != 'text':
            continue
        name = file_name(row)
        with open(os.path.join(args.run, 'raw', name), 'rb') as handle:
            text = clean(handle.read())
        with open(os.path.join(clean_dir, name), 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(text)
        index.append({'date': row['date'], 'document_number': row['document_number'], 'clean_bytes': len(text.encode('utf-8')),
                      'lines': text.count('\n'), 'clean_sha256': sha256_of(text.encode('utf-8'))})
    write_tsv(os.path.join(clean_dir, 'INDEX.tsv'), ['date', 'document_number', 'clean_bytes', 'lines', 'clean_sha256'], index)
    print('normalize: %d reading copies in %s' % (len(index), clean_dir))


def stage_package(args):
    import build_packs  # the retained collection's pack builder: deterministic packs, one per month
    source, _ = load_source(args.run)
    rows = read_tsv(os.path.join(args.run, 'inventory.tsv'))
    collection = os.path.join(args.run, 'collection')
    manifest_dir = os.path.join(collection, 'manifest')
    packs_dir = os.path.join(args.run, 'packs')
    os.makedirs(manifest_dir, exist_ok=True)
    os.makedirs(packs_dir, exist_ok=True)
    by_month = collections.defaultdict(list)
    for row in rows:
        by_month[row['date'][:7]].append(row)
    results = []
    for month, month_rows in sorted(by_month.items()):
        write_tsv(os.path.join(manifest_dir, month + '.tsv'), COLUMNS, month_rows)
        members = [(r['date'], r['document_number'], int(r['bytes']), r['sha256']) for r in month_rows if r['text_status'] == 'text']
        if not members:
            continue
        sources = {(m[0], m[1]): os.path.join(args.run, 'raw', '%s__%s.txt' % (m[0], m[1])) for m in members}
        pack_path = os.path.join(packs_dir, 'text-%s.tar.xz' % month)
        if os.path.exists(pack_path):
            os.replace(pack_path, pack_path + '.previous')
        _, error, result = build_packs.build_month((month, members, sources, packs_dir))
        if error:
            sys.exit('STOP: ' + error)
        results.append(result)
    write_tsv(os.path.join(collection, 'packs.tsv'), PACKS_COLUMNS, [dict(zip(PACKS_COLUMNS, r)) for r in sorted(results)])
    with_text = [r for r in rows if r['text_status'] == 'text']
    dates = sorted(r['date'] for r in rows)
    coverage = {
        'dataset': 'acquisition run: ' + source['adapter'], 'collection_pass': source['collection_pass'],
        'coverage_start': source['window_start'], 'coverage_end': source['window_end'],
        'first_publication_date': dates[0] if dates else '', 'last_publication_date': dates[-1] if dates else '',
        'documents': len(rows), 'with_text': len(with_text), 'pdf_only': len(rows) - len(with_text),
        'packs': len(results), 'raw_bytes': sum(int(r['bytes']) for r in with_text),
        'documents_with_image_placeholders': sum(1 for r in with_text if int(r['image_placeholders'])),
        'documents_with_hidden_emails': sum(1 for r in with_text if int(r['hidden_emails'])),
        'by_source_site': dict(collections.Counter(r['source_site'] for r in with_text)),
        'partial_test_build': sorted(by_month),
    }
    with open(os.path.join(collection, 'COVERAGE.json'), 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps(coverage, indent=2) + '\n')
    print('package: %d packs, %d documents, %s' % (len(results), sum(r[2] for r in results), packs_dir))


def stage_verify(args):
    rows = read_tsv(os.path.join(args.run, 'inventory.tsv'))
    problems = []
    checked = 0
    for row in rows:
        if row['text_status'] != 'text':
            continue
        with open(os.path.join(args.run, 'raw', file_name(row)), 'rb') as handle:
            data = handle.read()
        checked += 1
        if len(data) != int(row['bytes']) or sha256_of(data) != row['sha256']:
            problems.append('%s|%s: raw file differs from the inventory' % (row['date'], row['document_number']))
    command = [sys.executable, '-I', os.path.join(HERE, 'verify.py'), '--repo', os.path.join(args.run, 'collection'),
               '--packs-dir', os.path.join(args.run, 'packs'), '--all']
    run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    result = {'verified_at': utc_now(), 'raw_files_rehashed': checked, 'raw_problems': problems,
              'verify_py_exit_code': run.returncode, 'verify_py_output': run.stdout.strip().splitlines()}
    with open(os.path.join(args.run, 'verify.json'), 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps(result, indent=2) + '\n')
    print('verify: %d raw files re-hashed, %d problems; verify.py over the packs: %s'
          % (checked, len(problems), 'OK' if run.returncode == 0 else 'FAILED'))
    if problems or run.returncode:
        print(run.stdout)
        sys.exit(1)


def load_retained(path, months):
    """Rows of a retained manifest for the given months, from a folder of YYYY-MM.tsv, a tar.xz of them, or one tsv."""
    rows = []
    if os.path.isdir(path):
        for month in months:
            p = os.path.join(path, month + '.tsv')
            if os.path.exists(p):
                rows.extend(read_tsv(p))
    elif path.endswith('.tar.xz'):
        with tarfile.open(path, 'r:xz') as tar:
            for member in tar.getmembers():
                if member.isfile() and os.path.basename(member.name)[:-4] in months:
                    text = tar.extractfile(member).read().decode('utf-8')
                    rows.extend(csv.DictReader(text.splitlines(), delimiter='\t'))
    else:
        rows = read_tsv(path)
    return rows


def stage_compare(args):
    source, _ = load_source(args.run)
    rows = read_tsv(os.path.join(args.run, 'inventory.tsv'))
    months = sorted(set(r['date'][:7] for r in rows))
    retained_all = load_retained(args.retained, months)
    start, end = source['window_start'], source['window_end']
    retained = {(r['date'], r['document_number']): r for r in retained_all if start <= r['date'] <= end}
    run_rows = {(r['date'], r['document_number']): r for r in rows}
    lines, tally = [], collections.Counter()
    for key in sorted(set(retained) | set(run_rows)):
        a, b = run_rows.get(key), retained.get(key)
        if a and not b:
            outcome = 'only_in_this_run'
        elif b and not a:
            outcome = 'only_in_retained'
        elif a['text_status'] != b['text_status']:
            outcome = 'status_differs'
        elif a['text_status'] != 'text':
            outcome = 'both_without_text'
        elif a['sha256'] == b['sha256'] and a['bytes'] == b['bytes']:
            outcome = 'identical_bytes'
        else:
            outcome = 'bytes_differ'
        tally[outcome] += 1
        lines.append({'date': key[0], 'document_number': key[1], 'outcome': outcome,
                      'run_site': (a or {}).get('source_site', ''), 'retained_site': (b or {}).get('source_site', ''),
                      'retained_pass': (b or {}).get('collection_pass', ''),
                      'run_sha256': (a or {}).get('sha256', ''), 'retained_sha256': (b or {}).get('sha256', '')})
    write_tsv(os.path.join(args.run, 'comparison.tsv'), list(lines[0]) if lines else ['date'], lines)
    same_site = sum(1 for l in lines if l['outcome'] == 'identical_bytes' and l['run_site'] == l['retained_site'])
    result = {
        'compared_at': utc_now(), 'window': [start, end], 'retained_manifest': os.path.basename(args.retained),
        'identities_in_this_run': len(run_rows), 'identities_in_retained_window': len(retained),
        'outcomes': dict(sorted(tally.items())),
        'identical_bytes_from_same_site': same_site,
        'identical_bytes_from_other_site': tally['identical_bytes'] - same_site,
        'retained_passes_in_window': dict(collections.Counter(r['collection_pass'] for r in retained.values() if r['text_status'] == 'text')),
    }
    with open(os.path.join(args.run, 'comparison.json'), 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps(result, indent=2) + '\n')
    print('compare: %d identities in this run, %d retained in the window; %s' % (len(run_rows), len(retained), result['outcomes']))


STAGES = [('define', stage_define), ('retrieve', stage_retrieve), ('inventory', stage_inventory),
          ('normalize', stage_normalize), ('package', stage_package), ('verify', stage_verify), ('compare', stage_compare)]
OFFLINE = ['inventory', 'normalize', 'package', 'verify', 'compare']


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('stage', choices=[s for s, _ in STAGES] + ['all', 'offline'],
                        help='one stage, "all" (define through compare) or "offline" (every stage after retrieve)')
    parser.add_argument('--run', required=True, help='the run folder')
    parser.add_argument('--adapter', default='federal_register')
    parser.add_argument('--start', help='first publication date, YYYY-MM-DD (define)')
    parser.add_argument('--end', help='last publication date, YYYY-MM-DD (define)')
    parser.add_argument('--site-order', default='federalregister,govinfo', help='text sites to try, in order (define)')
    parser.add_argument('--delay', type=float, default=1.0, help='seconds between HTTP requests (define)')
    parser.add_argument('--tries', type=int, default=4)
    parser.add_argument('--timeout', type=float, default=60.0)
    parser.add_argument('--pass-name', help='label written into the collection_pass column (define)')
    parser.add_argument('--refresh-frame', action='store_true', help='list the index again even if frame.tsv exists (retrieve)')
    parser.add_argument('--retained', help='retained manifest: a folder of YYYY-MM.tsv, a tar.xz of them, or one tsv (compare)')
    args = parser.parse_args()

    if args.stage == 'all':
        wanted = [s for s, _ in STAGES]
    elif args.stage == 'offline':
        wanted = OFFLINE
    else:
        wanted = [args.stage]
    if 'define' in wanted and not (args.start and args.end):
        parser.error('define needs --start and --end')
    if 'compare' in wanted and not args.retained:
        if args.stage in ('all', 'offline'):
            wanted.remove('compare')
        else:
            parser.error('compare needs --retained')
    for name, function in STAGES:
        if name in wanted:
            function(args)


if __name__ == '__main__':
    main()
