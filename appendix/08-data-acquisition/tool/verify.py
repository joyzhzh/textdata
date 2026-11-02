#!/usr/bin/env python3
"""Check the manifest, the pack list and the packs against each other.

Without --packs-dir only the small files are checked (manifest, packs.tsv,
COVERAGE.json). With --packs-dir every pack found there is opened and every
file inside it is re-hashed against its manifest line. Add --all to insist
that every pack on the list is present.

    python3 scripts/verify.py
    python3 scripts/verify.py --packs-dir path/to/packs --all

Release edition: the usage example uses a relative output path; verification logic is unchanged.

Exit code 0 means everything matched.
"""
import argparse
import hashlib
import json
import lzma
import os
import re
import sys
import tarfile
import time
from multiprocessing import get_context

COLUMNS = ['date', 'document_number', 'text_status', 'source_site', 'collection_pass',
           'fetched_at', 'bytes', 'sha256', 'image_placeholders', 'hidden_emails']
PACKS_COLUMNS = ['pack', 'release', 'documents', 'raw_bytes', 'pack_bytes', 'sha256']
MEMBER = re.compile(r'^(\d{4}-\d{2})/(\d{4}-\d{2}-\d{2})__([A-Za-z0-9._-]+)\.txt$')


def read_manifest(manifest_dir, problems):
    """-> {month: {(date, docnum): (bytes, sha256) or None for PDF-only}}"""
    months = {}
    seen = set()
    for name in sorted(os.listdir(manifest_dir)):
        if not name.endswith('.tsv'):
            continue
        month = name[:-4]
        entries = {}
        previous = None
        with open(os.path.join(manifest_dir, name), encoding='utf-8') as handle:
            if handle.readline().rstrip('\n').split('\t') != COLUMNS:
                problems.append('%s: unexpected header' % name)
                continue
            for number, line in enumerate(handle, 2):
                values = line.rstrip('\n').split('\t')
                if len(values) != len(COLUMNS):
                    problems.append('%s line %d: wrong number of columns' % (name, number))
                    continue
                row = dict(zip(COLUMNS, values))
                key = (row['date'], row['document_number'])
                if not row['date'].startswith(month):
                    problems.append('%s line %d: date outside the month' % (name, number))
                if key in seen:
                    problems.append('%s line %d: duplicate document %s|%s' % (name, number, key[0], key[1]))
                seen.add(key)
                if previous is not None and key < previous:
                    problems.append('%s line %d: not sorted' % (name, number))
                previous = key
                if row['text_status'] == 'text':
                    if not re.match(r'^[0-9a-f]{64}$', row['sha256']) or not row['bytes'].isdigit():
                        problems.append('%s line %d: bad size or checksum' % (name, number))
                        continue
                    entries[key] = (int(row['bytes']), row['sha256'])
                elif row['text_status'] == 'pdf_only':
                    if any(row[c] for c in COLUMNS[3:]):
                        problems.append('%s line %d: PDF-only line carries file details' % (name, number))
                    entries[key] = None
                else:
                    problems.append('%s line %d: unknown text_status' % (name, number))
        months[month] = entries
    return months


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def check_pack(job):
    path, month, listed, expected = job          # expected: {(date, docnum): (bytes, sha256)}
    problems = []
    name = os.path.basename(path)
    if os.path.getsize(path) != listed['pack_bytes'] or file_sha256(path) != listed['sha256']:
        problems.append('%s: size or checksum differs from packs.tsv' % name)
    found = set()
    previous = ''
    try:
        with lzma.open(path, 'rb') as xz, tarfile.open(fileobj=xz, mode='r|') as tar:
            for member in tar:
                match = MEMBER.match(member.name)
                if not member.isfile() or not match or match.group(1) != month:
                    problems.append('%s: unexpected member %r' % (name, member.name))
                    continue
                key = (match.group(2), match.group(3))
                if member.name <= previous:
                    problems.append('%s: members not sorted at %s' % (name, member.name))
                previous = member.name
                if key in found:
                    problems.append('%s: member twice: %s' % (name, member.name))
                found.add(key)
                want = expected.get(key)
                if not want:
                    problems.append('%s: member not in the manifest: %s' % (name, member.name))
                    continue
                data = tar.extractfile(member).read()
                if len(data) != want[0] or hashlib.sha256(data).hexdigest() != want[1]:
                    problems.append('%s: bytes differ from the manifest: %s' % (name, member.name))
    except (lzma.LZMAError, tarfile.TarError, EOFError, OSError) as exc:
        problems.append('%s: cannot be read to the end (%s)' % (name, type(exc).__name__))
    missing = set(expected) - found
    if missing:
        problems.append('%s: %d manifest documents are not in the pack' % (name, len(missing)))
    return name, len(found), problems


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--repo', help='repository root (default: the folder above scripts/)')
    parser.add_argument('--packs-dir', help='folder holding text-YYYY-MM.tar.xz files to check')
    parser.add_argument('--packs-tsv', help='pack list (default: packs.tsv in the repository)')
    parser.add_argument('--all', action='store_true', help='every pack on the list must be present in --packs-dir')
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args()

    started = time.time()
    repo = os.path.abspath(args.repo) if args.repo else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    problems = []

    months = read_manifest(os.path.join(repo, 'manifest'), problems)
    documents = sum(len(entries) for entries in months.values())
    with_text = sum(1 for entries in months.values() for value in entries.values() if value)
    text_months = sorted(m for m, entries in months.items() if any(entries.values()))

    coverage = json.load(open(os.path.join(repo, 'COVERAGE.json')))
    for key, value in (('documents', documents), ('with_text', with_text),
                       ('pdf_only', documents - with_text), ('packs', len(text_months))):
        if coverage.get(key) != value:
            problems.append('COVERAGE.json says %s = %s, the manifest has %s' % (key, coverage.get(key), value))
    all_dates = sorted(key[0] for entries in months.values() for key in entries)
    if all_dates and (all_dates[0] < coverage['coverage_start'] or all_dates[-1] > coverage['coverage_end']):
        problems.append('manifest dates fall outside the coverage window in COVERAGE.json')

    packs = {}
    with open(args.packs_tsv or os.path.join(repo, 'packs.tsv'), encoding='utf-8') as handle:
        if handle.readline().rstrip('\n').split('\t') != PACKS_COLUMNS:
            problems.append('packs.tsv: unexpected header')
        for line in handle:
            row = dict(zip(PACKS_COLUMNS, line.rstrip('\n').split('\t')))
            for column in ('documents', 'raw_bytes', 'pack_bytes'):
                row[column] = int(row[column])
            packs[row['pack']] = row
    partial = bool(coverage.get('partial_test_build')) or bool(args.packs_tsv)
    for month in text_months:
        name = 'text-%s.tar.xz' % month
        entries = [value for value in months[month].values() if value]
        if name not in packs:
            if not partial:
                problems.append('packs.tsv has no line for %s' % name)
            continue
        if packs[name]['documents'] != len(entries) or packs[name]['raw_bytes'] != sum(v[0] for v in entries):
            problems.append('packs.tsv line for %s disagrees with the manifest' % name)
        if packs[name]['release'] != 'text-' + month[:4]:
            problems.append('packs.tsv line for %s names the wrong release' % name)
    for name in packs:
        if name[5:12] not in text_months:
            problems.append('packs.tsv lists %s, which the manifest does not need' % name)

    print('manifest: %d documents | %d with text | %d PDF-only | %d months | pack list: %d packs'
          % (documents, with_text, documents - with_text, len(text_months), len(packs)))

    checked_packs = checked_members = 0
    if args.packs_dir:
        jobs = []
        for name in sorted(os.listdir(args.packs_dir)):
            if not re.match(r'^text-\d{4}-\d{2}\.tar\.xz$', name):
                continue
            month = name[5:12]
            if name not in packs or month not in months:
                problems.append('%s: not on the pack list' % name)
                continue
            expected = {key: value for key, value in months[month].items() if value}
            jobs.append((os.path.join(args.packs_dir, name), month, packs[name], expected))
        if args.all:
            present = set(os.path.basename(job[0]) for job in jobs)
            for name in sorted(set(packs) - present):
                problems.append('%s: on the pack list but not in %s' % (name, args.packs_dir))
        with get_context('fork').Pool(args.workers) as pool:
            for name, members, pack_problems in pool.imap_unordered(check_pack, jobs):
                checked_packs += 1
                checked_members += members
                problems.extend(pack_problems)
                if checked_packs % 40 == 0:
                    print('  %d packs checked (%.0fs)' % (checked_packs, time.time() - started), flush=True)
        print('packs opened: %d | files re-hashed against the manifest: %d' % (checked_packs, checked_members))

    if problems:
        print('\nFAILED: %d problems' % len(problems))
        for problem in problems[:40]:
            print('  ' + problem)
        sys.exit(1)
    print('OK (%.0fs)' % (time.time() - started))


if __name__ == '__main__':
    main()
