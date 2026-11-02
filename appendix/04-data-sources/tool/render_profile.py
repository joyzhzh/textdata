"""Render dated source profiles as Markdown, using included records only.

From the component folder:
    python3 -I tool/render_profile.py D17 --out example/output
    python3 -I tool/render_profile.py --all --out data/profiles

Reads data/catalogue.json, data/arenas.json, data/provider_checks.json and
 data/evidence.jsonl. Writes one Markdown file per selected family and, with
--all, an index. Source facts and judgments come from the catalogue; headings
and layout come from this renderer. Python 3.9+, standard library only.
No network or model. Output is byte-stable.
"""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = 'data/evidence.jsonl'
# One rechecked page sits on a host none of the family's own records cites: the official
# Federal Register edition on GovInfo, which the check names as the D10 providers' publication.
CHECK_HOST_FAMILY = {'www.govinfo.gov': 'D10'}
KIND = {'arena': 'in an arena of rich text', 'structured': 'complementary structured data',
        'narrative-excluded': 'no longer a narrative source'}
REUSE = {'explicit': 'explicit licence or permission', 'restricted': 'restricted or custom terms',
         'unresolved': 'unknown or unresolved terms'}


def load(root):
    cat = json.loads((root / 'data' / 'catalogue.json').read_text(encoding='utf-8'))
    arenas = {a['id']: a for a in json.loads((root / 'data' / 'arenas.json').read_text(encoding='utf-8'))['arenas']}
    checks = json.loads((root / 'data' / 'provider_checks.json').read_text(encoding='utf-8'))
    ledger = {}
    for line in (root / EVIDENCE).read_text(encoding='utf-8').splitlines():
        if line.strip():
            rec = json.loads(line)
            ledger[rec['catalog_id']] = rec
    return cat, arenas, checks, ledger


def checks_by_family(cat, checks, ledger):
    hosts = {}
    for f in cat['families']:
        rec = ledger[f['id']]
        urls = [f['entry_point']] + [d['url'] for d in f['documentation']] + rec['aliases'] + \
               [m['locator'] for m in rec['manifestations']]
        for u in urls:
            hosts.setdefault(urlsplit(u).netloc, set()).add(f['id'])
    out = {}
    for s in checks['sources']:
        host = urlsplit(s['url']).netloc
        owners = {CHECK_HOST_FAMILY[host]} if host in CHECK_HOST_FAMILY else hosts.get(host, set())
        if len(owners) != 1:
            sys.exit(f'provider check {s["title"]!r} does not belong to exactly one family: {sorted(owners)}')
        out.setdefault(owners.pop(), []).append(s)
    return out


def profile(f, arenas, checks, ledger, checked_at):
    arena = arenas.get(f['arena'])
    lines = [f'# {f["id"]} {f["name"]}', '',
             f'Documentation-based profile dated {f["checked_at"]}. No source records acquired. '
             'Rendered from the included catalogue and source evidence.',
             '', '## In the catalogue', '',
             f'- Kind: {KIND[f["kind"]]}']
    if arena:
        lines.append(f'- Arena: {arena["id"]} {arena["name"]} (what it can support and its main boundary: '
                     f'{arena["fit_and_boundary"]})')
    lines += [f'- Reuse group: {REUSE[f["reuse_group"]]}',
              f'- Provider: {f["provider"]}',
              f'- Entry point: {f["entry_point"]}']
    if f['entry_point_note']:
        lines.append(f'- Entry point note: {f["entry_point_note"]}')
    lines += ['', '## Unit of analysis', '', f['units_and_scope'],
              '', '## Coverage and dates', '',
              f'Release: {f["release"]}', '', f'Time: {f["coverage_and_dates"]}', '', f'Size: {f["size"]}',
              '', '## Content: fields and the identifiers that link records', '', f['fields_and_links'],
              '', '## Access and reuse', '',
              f'Access: {f["access"]}', '', f'Route: {f["route"]}', '', f'Authentication: {f["authentication"]}',
              '', f'What the review inspected: {f["inspected"]}', '',
              f'Reuse status: {f["reuse_status"]}', '', f'Reuse terms: {f["reuse_terms"]}', '']
    if f['documentation']:
        lines += ['Provider documentation inspected:', '']
        lines += [f'- {d["label"]}: {d["url"]}' for d in f['documentation']]
        lines.append('')
    lines += ['## Source evidence', '']
    for c in ledger[f['id']]['claims']:
        lines.append(f'- {c["claim"]} ({c["evidence_class"]}; observed {c["observed_at"]}) {c["exact_locator"]}')
    lines += ['', '## Limits', '',
              'A profile is dated; it is not a promise that the source still looks like this. Recheck the provider\'s '
              'pages before acquisition.', '', 'Source-specific limits:', '']
    lines += [f'- {lim}' for lim in f['limitations']]
    lines += ['', '## The review\'s decision on this source', '',
              f'Decision ({f["checked_at"]}): {f["review_decision"]}', '',
              f'Proposed first task (not executed): {f["suggested_task"]}', '']
    for s in checks:
        lines += [f'Provider page rechecked ({checked_at}): {s["title"]}, {s["url"]}. Claim checked: {s["checked_claim"]}', '']
    return '\n'.join(lines)


def index(cat, arenas, by_family):
    lines = ['# The 25 source profiles', '',
             f'Profiles dated {cat["dates"]["profiles"]}, with ten provider-page checks dated '
             f'{cat["dates"]["provider_checks"]}. Rendered by `tool/render_profile.py --all`. '
             'Families are sources described, not datasets included.', '',
             '| Id | Family | Kind | Arena | Reuse group | Provider pages rechecked |',
             '|---|---|---|---|---|---|']
    for f in cat['families']:
        arena = f'{f["arena"]} {arenas[f["arena"]]["name"]}' if f['arena'] else ''
        lines.append(f'| [{f["id"]}]({f["id"]}.md) | {f["name"]} | {KIND[f["kind"]]} | {arena} | '
                     f'{REUSE[f["reuse_group"]]} | {len(by_family.get(f["id"], []))} |')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('ids', nargs='*', help='family ids, e.g. D17')
    ap.add_argument('--all', action='store_true', help='render all 25 and an index')
    ap.add_argument('--out', required=True, help='output folder')
    a = ap.parse_args(argv)
    cat, arenas, checks, ledger = load(ROOT)
    fams = {f['id']: f for f in cat['families']}
    ids = list(fams) if a.all else a.ids
    unknown = [i for i in ids if i not in fams]
    if not ids or unknown:
        ap.error(f'give --all or ids from D01 to D25 (unknown: {unknown})')
    by_family = checks_by_family(cat, checks, ledger)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for i in ids:
        text = profile(fams[i], arenas, by_family.get(i, []), ledger, checks['checked_at'])
        (out / f'{i}.md').write_text(text, encoding='utf-8')
    if a.all:
        (out / 'README.md').write_text(index(cat, arenas, by_family), encoding='utf-8')
    print(f'wrote {len(ids)} profile{"s" if len(ids) != 1 else ""}' + (' and README.md' if a.all else '') + f' to {out}')


if __name__ == '__main__':
    main()
