#!/usr/bin/env python3
"""Build the monthly packs text-YYYY-MM.tar.xz from the manifest.

Each document's raw file is read straight from its place in the local
collection (local/source_paths.tsv), checked against the manifest line (size and
SHA-256) and streamed into the pack. No unpacked copy is made.

A pack is built the same way every time: members sorted by name, fixed owner
and permissions, each member's time set to its publication date, one xz stream
at a fixed level. Same input, same pack bytes (with the same xz library).

Inside a pack:  YYYY-MM/YYYY-MM-DD__<document number>.txt   (bytes as served)

Writes the packs into --out and the pack list packs.tsv into the repository.

    python3 scripts/build_packs.py --out path/to/packs

Release edition: the output path in the line above is a placeholder for a local one (docs/RELEASE_CHANGES.md).
"""
import argparse
import calendar
import hashlib
import io
import lzma
import os
import sys
import tarfile
import time
from multiprocessing import get_context

XZ_PRESET = 9            # fixed; changing it changes every pack's bytes
PACKS_COLUMNS = ['pack', 'release', 'documents', 'raw_bytes', 'pack_bytes', 'sha256']


def read_manifest_month(path):
    """-> list of (date, document_number, bytes, sha256) for documents with text."""
    members = []
    with open(path, encoding='utf-8') as handle:
        header = handle.readline().rstrip('\n').split('\t')
        for line in handle:
            row = dict(zip(header, line.rstrip('\n').split('\t')))
            if row['text_status'] == 'text':
                members.append((row['date'], row['document_number'], int(row['bytes']), row['sha256']))
    return members


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def build_month(job):
    month, members, sources, out_dir = job
    pack_name = 'text-%s.tar.xz' % month
    final = os.path.join(out_dir, pack_name)
    raw_bytes = sum(m[2] for m in members)
    if not os.path.exists(final):
        partial = final + '.partial'
        with lzma.open(partial, 'wb', format=lzma.FORMAT_XZ, preset=XZ_PRESET) as xz:
            with tarfile.open(fileobj=xz, mode='w', format=tarfile.USTAR_FORMAT) as tar:
                for date, docnum, size, sha in sorted(members, key=lambda m: '%s__%s.txt' % (m[0], m[1])):
                    with open(sources[(date, docnum)], 'rb') as handle:
                        data = handle.read()
                    if len(data) != size or hashlib.sha256(data).hexdigest() != sha:
                        os.remove(partial)
                        return month, 'source file no longer matches the manifest: %s|%s' % (date, docnum), None
                    info = tarfile.TarInfo('%s/%s__%s.txt' % (month, date, docnum))
                    info.size = size
                    info.mtime = calendar.timegm(time.strptime(date, '%Y-%m-%d'))
                    info.mode = 0o644
                    info.uid = info.gid = 0
                    info.uname = info.gname = ''
                    info.type = tarfile.REGTYPE
                    tar.addfile(info, io.BytesIO(data))
        os.replace(partial, final)
    return month, None, (pack_name, 'text-' + month[:4], len(members), raw_bytes, os.path.getsize(final), file_sha256(final))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', required=True, help='folder for the packs (existing packs are kept, not rebuilt)')
    parser.add_argument('--repo', help='repository root (default: the folder above scripts/)')
    parser.add_argument('--months', nargs='+', help='only these months (test mode; packs.tsv then goes into --out)')
    parser.add_argument('--workers', type=int, default=6, help='each worker needs about 0.7 GB of memory')
    args = parser.parse_args()

    started = time.time()
    repo = os.path.abspath(args.repo) if args.repo else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    sources = {}
    with open(os.path.join(repo, 'local', 'source_paths.tsv'), encoding='utf-8') as handle:
        for line in handle:
            date, docnum, path = line.rstrip('\n').split('\t')
            sources[(date, docnum)] = path

    manifest_dir = os.path.join(repo, 'manifest')
    months = sorted(name[:-4] for name in os.listdir(manifest_dir) if name.endswith('.tsv'))
    if args.months:
        months = [m for m in months if m in set(args.months)]
    jobs = []
    for month in months:
        members = read_manifest_month(os.path.join(manifest_dir, month + '.tsv'))
        if not members:
            continue
        missing = [m for m in members if (m[0], m[1]) not in sources]
        if missing:
            sys.exit('STOP: %s has %d documents without a local source path' % (month, len(missing)))
        jobs.append((month, members, {(m[0], m[1]): sources[(m[0], m[1])] for m in members}, out_dir))

    results, errors = [], []
    with get_context('fork').Pool(args.workers) as pool:
        for month, error, result in pool.imap_unordered(build_month, jobs):
            if error:
                errors.append('%s: %s' % (month, error))
            else:
                results.append(result)
                if len(results) % 20 == 0 or len(results) == len(jobs):
                    print('  %d of %d packs ready (%.0fs)' % (len(results), len(jobs), time.time() - started), flush=True)
    if errors:
        sys.exit('STOP:\n  ' + '\n  '.join(errors))

    packs_tsv = os.path.join(out_dir if args.months else repo, 'packs.tsv')
    with open(packs_tsv, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write('\t'.join(PACKS_COLUMNS) + '\n')
        for result in sorted(results):
            handle.write('\t'.join(str(value) for value in result) + '\n')
    print('OK  %d packs | %d documents | raw %.2f GB -> packed %.2f GB | list: %s (%.0fs)' % (
        len(results), sum(r[2] for r in results), sum(r[3] for r in results) / 1e9,
        sum(r[4] for r in results) / 1e9, packs_tsv, time.time() - started))


if __name__ == '__main__':
    main()
