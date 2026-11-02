#!/usr/bin/env python3
"""Turn raw files (exactly as served) into clean reading text.

A raw file is the government's plain text inside a small HTML wrapper:
<html><head><title>...</title></head><body><pre> ... </pre></body></html>.
The websites' delivery network (Cloudflare) also replaced every e-mail address
with a coded "[email protected]" link and added a script tag at the end.

Clean text = everything inside the <pre> block, with the hidden e-mail
addresses decoded back, remaining tags removed, HTML entities unescaped, line
endings LF, outer whitespace stripped, one final newline.

    python3 scripts/clean_text.py text-2012-06.tar.xz --out clean/     # a whole pack
    python3 scripts/clean_text.py 2012-06-01__2012-11118.txt           # one raw file, to the screen
"""
import argparse
import html
import lzma
import os
import re
import sys
import tarfile

PRE_OPEN = re.compile(r'<pre(?:\s[^>]*)?>', re.I)
PRE_CLOSE = re.compile(r'</pre\s*>', re.I)
HIDDEN_EMAIL = re.compile(r'<(a|span)\b[^>]*\bdata-cfemail="([0-9a-fA-F]+)"[^>]*>.*?</\1\s*>', re.I | re.S)
TAG = re.compile(r'<[^>]+>', re.S)


def decode_hidden_email(coded):
    raw = bytes.fromhex(coded)
    return bytes(value ^ raw[0] for value in raw[1:]).decode('utf-8', 'replace')


def clean(raw_bytes, restore_emails=True):
    text = raw_bytes.decode('utf-8', errors='replace')
    start = PRE_OPEN.search(text)
    ends = list(PRE_CLOSE.finditer(text))
    if not start or not ends or ends[-1].start() < start.end():
        raise ValueError('no complete <pre> block')
    body = text[start.end():ends[-1].start()]
    if restore_emails:
        body = HIDDEN_EMAIL.sub(lambda match: html.escape(decode_hidden_email(match.group(2))), body)
    body = TAG.sub('', body)
    body = html.unescape(body)
    body = body.replace('\r\n', '\n').replace('\r', '\n')
    return body.strip() + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('inputs', nargs='+', help='packs (text-YYYY-MM.tar.xz) and/or single raw files')
    parser.add_argument('--out', help='output folder (required for packs)')
    args = parser.parse_args()

    for path in args.inputs:
        if path.endswith('.tar.xz'):
            if not args.out:
                sys.exit('give --out for packs')
            count = 0
            with lzma.open(path, 'rb') as xz, tarfile.open(fileobj=xz, mode='r|') as tar:
                for member in tar:
                    if not member.isfile() or not re.match(r'^\d{4}-\d{2}/[A-Za-z0-9._-]+\.txt$', member.name):
                        continue
                    target = os.path.join(args.out, member.name)
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    with open(target, 'w', encoding='utf-8', newline='\n') as handle:
                        handle.write(clean(tar.extractfile(member).read()))
                    count += 1
            print('%s: %d clean files in %s' % (os.path.basename(path), count, args.out))
        else:
            with open(path, 'rb') as handle:
                cleaned = clean(handle.read())
            if args.out:
                os.makedirs(args.out, exist_ok=True)
                with open(os.path.join(args.out, os.path.basename(path)), 'w', encoding='utf-8', newline='\n') as handle:
                    handle.write(cleaned)
            else:
                sys.stdout.write(cleaned)


if __name__ == '__main__':
    main()
