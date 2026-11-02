"""Verify the source catalogue, renderer and shipped files, offline.

Usage: python3 -I checks/verify_counts.py
Checks 25 profiles, 12 arenas, JSON/CSV agreement, 10 provider pages mapped to
9 families, 70 source claims, byte-identical profile rendering, Markdown links
and manifest hashes. Python 3.9+, standard library only.
"""
import csv
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)


def jsonl(rel):
    return [json.loads(x) for x in (ROOT / rel).read_text(encoding='utf-8').splitlines() if x.strip()]


# 1. catalogue
cat = json.loads((ROOT / 'data' / 'catalogue.json').read_text(encoding='utf-8'))
fam = cat['families']
ids = [f['id'] for f in fam]
check(ids == [f'D{i:02d}' for i in range(1, 26)], 'ids are not D01..D25 in order')
check({f['checked_at'] for f in fam} == {'2026-10-11'}, 'profiles not all dated 2026-10-11')
check(Counter(f['kind'] for f in fam) == {'arena': 18, 'structured': 6, 'narrative-excluded': 1}, 'kinds are not 18 / 6 / 1')
check([f['id'] for f in fam if f['kind'] == 'narrative-excluded'] == ['D17'] and cat['narrative_exclusion'] == 'D17',
      'the narrative exclusion is not D17')
for f in fam:
    check(f['provider'] and f['entry_point'].startswith('https://'), f'{f["id"]}: provider or entry point missing')
    check(f['reuse_group'] in ('explicit', 'restricted', 'unresolved'), f'{f["id"]}: reuse group')
    check(len(f['limitations']) >= 1, f'{f["id"]}: no limitation')
    check(bool(f['review_decision']) and bool(f['suggested_task']), f'{f["id"]}: decision or task missing')
check(cat['counts'] == {'families': 25, 'arenas': 12,
                        'families_in_arenas': 18, 'families_structured': 6, 'families_narrative_excluded': 1,
                        'provider_checks': 10}, 'counts block disagrees')

# 2. arenas
ar = json.loads((ROOT / 'data' / 'arenas.json').read_text(encoding='utf-8'))['arenas']
check(len(ar) == 12, f'arenas: {len(ar)} != 12')
fields = {'id', 'name', 'group', 'families', 'concrete_sources', 'fit_and_boundary'}
check(all(set(a) == fields for a in ar), 'an arena carries fields beyond the website\'s set')
arena_fams = [d for a in ar for d in a['families']]
check(len(arena_fams) == 18 and len(set(arena_fams)) == 18, 'arena family lists do not partition 18 families')
check(sorted(arena_fams) == sorted(f['id'] for f in fam if f['kind'] == 'arena'), 'arena families disagree with catalogue')

# 3. csv
with (ROOT / 'data' / 'catalogue.csv').open(encoding='utf-8', newline='') as fh:
    rows = list(csv.DictReader(fh))
check([(r['id'], r['name'], r['reuse_group']) for r in rows] == [(f['id'], f['name'], f['reuse_group']) for f in fam],
      'csv disagrees with json')

# 4. provider checks, assigned to families by the renderer's own rule
sys.dont_write_bytecode = True  # leave no cache files in the folder
sys.path.insert(0, str(ROOT / 'tool'))
import render_profile  # noqa: E402
pc = json.loads((ROOT / 'data' / 'provider_checks.json').read_text(encoding='utf-8'))
check(len(pc['sources']) == 10 and pc['checked_at'] == '2026-10-29', 'provider checks != 10 on 2026-10-29')
_, _, _, ledger = render_profile.load(ROOT)
by_family = render_profile.checks_by_family(cat, pc, ledger)
check(sum(len(v) for v in by_family.values()) == 10 and len(by_family) == 9, 'provider checks do not map to 9 families')

# 5. source evidence
ev = jsonl('data/evidence.jsonl')
check([r['catalog_id'] for r in ev] == ids, 'source records are not one per family in order')
check(len(ev) == 25 and sum(len(r['claims']) for r in ev) == 70, 'source evidence counts')
check(all(c['exact_locator'] and c['observed_at'] for r in ev for c in r['claims']), 'source locator or date missing')

# 6. renderer reproduces the shipped profiles and the worked example
with tempfile.TemporaryDirectory() as tmp:
    for args, rel in ((['--all'], 'data/profiles'), (['D17'], 'example/output')):
        out = Path(tmp) / rel
        res = subprocess.run([sys.executable, '-I', str(ROOT / 'tool' / 'render_profile.py'), *args, '--out', str(out)],
                             capture_output=True, text=True)
        check(res.returncode == 0, f'render_profile.py {args} failed: {res.stderr.strip()}')
        shipped = sorted(p.name for p in (ROOT / rel).iterdir())
        made = sorted(p.name for p in out.iterdir()) if out.is_dir() else []
        check(shipped == made, f'{rel}: rendered file list differs')
        for name in set(shipped) & set(made):
            check((ROOT / rel / name).read_bytes() == (out / name).read_bytes(), f'{rel}/{name} is not reproduced byte for byte')
check(len(list((ROOT / 'data' / 'profiles').glob('D*.md'))) == 25, 'data/profiles does not hold 25 profiles')

# 7. relative links in Markdown
for md in sorted(ROOT.rglob('*.md')):
    for target in re.findall(r'\]\(([^)\s]+)\)', md.read_text(encoding='utf-8')):
        if re.match(r'[a-z]+:', target) or target.startswith('#'):
            continue
        path = (md.parent / target.split('#')[0]).resolve()
        check(path.exists(), f'{md.relative_to(ROOT)}: link to {target} does not open a file')

# 8. manifest
man = json.loads((ROOT / 'MANIFEST.json').read_text(encoding='utf-8'))
listed = {e['path']: e for e in man['files']}
present = sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob('*')
                 if p.is_file() and p.name != 'MANIFEST.json' and '__pycache__' not in p.parts)
check(sorted(listed) == present, 'MANIFEST.json file list differs from the folder')
for rel in set(listed) & set(present):
    data = (ROOT / rel).read_bytes()
    check(listed[rel]['bytes'] == len(data) and listed[rel]['sha256'] == hashlib.sha256(data).hexdigest(),
          f'MANIFEST.json: {rel} size or hash differs')

if failures:
    print('FAIL: ' + failures[0])
    for f in failures[1:]:
        print('      ' + f)
    sys.exit(1)
print('all checks pass')
