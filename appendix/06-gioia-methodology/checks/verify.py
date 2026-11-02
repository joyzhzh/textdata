#!/usr/bin/env python3
"""Verify the Gioia toolkit folder: replay the example, run the checker's tests, check the
manifest counts, and scan for identifying patterns. Python 3.9+, standard library,
no network, no model.

    python3 checks/verify.py

Prints one line per check and ends with "all counts match" (exit 0) or "FAILED" (exit 1).
"""

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / 'example'
TOOL = ROOT / 'tool'
RUNNER = EXAMPLE / 'run_example.py'

EXPECTED = {  # request stem -> (fidelity, exit code, match count)
    'request-1-bundled-exact': ('EXACT_SINGLE', 0, 1),
    'request-2-altered-word': ('NO_EXACT_MATCH', 1, 0),
    'request-3-two-speakers': ('AMBIGUOUS_MATCHES', 1, 2),
    'request-4-episode-exact': ('EXACT_SINGLE', 0, 1),
}
COUNTS = {  # package quantities recorded in MANIFEST.json
    'quotation requests in example/input': 4,
    'reports in example/output': 4,
    'test definitions in tool/tests': 39,
    'files in tool/': 13,
    'methodological references in bibliography.md': 7,
    'guides besides the bibliography': 4,
    'working record templates': 4,
    'checker request templates': 1,
    'synthetic texts': 2,
    'synthetic analytic memos': 1,
}
# The final proposal requires this public component destination.
PUBLIC_COMPONENT_URL = 'https://github.com/joyzhzh/textdata/tree/main/appendix/06-gioia-methodology'

PATTERNS = [  # the submission site's built-in identity patterns, spelled in pieces so that
    # this file does not itself contain the literal strings it looks for
    (re.compile('/Us' + 'ers/'), 'home-folder path'),
    (re.compile('mail' + 'to:', re.I), 'mailto link'),
    (re.compile(r'[\w.+-]+' + '@' + r'[\w-]+(\.[\w-]+)+'), 'e-mail address'),
    (re.compile('git' + r'hub\.com/', re.I), 'GitHub link'),
    (re.compile('linked' + r'in\.com', re.I), 'LinkedIn link'),
    (re.compile('net' + r'lify\.app', re.I), 'Netlify subdomain'),
]

failures = []


def check(name, ok, detail=''):
    print(('ok    ' if ok else 'FAIL  ') + name + (('  ' + detail) if detail else ''))
    if not ok:
        failures.append(name)


def replay_example():
    scratch = TOOL / '.test-artifacts'
    scratch.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix='report-replay-', dir=scratch))
    proc = subprocess.run([sys.executable, '-I', '-B', str(RUNNER), '--out', tmp],
                          capture_output=True, text=True, timeout=120)
    check('example runner exits 0', proc.returncode == 0, proc.stderr.strip())
    for stem, (fidelity, code, count) in EXPECTED.items():
        fresh = tmp / (stem + '.report.json')
        kept = EXAMPLE / 'output' / (stem + '.report.json')
        check('replay reproduces ' + kept.name + ' byte for byte',
              fresh.exists() and kept.exists() and fresh.read_bytes() == kept.read_bytes())
        if kept.exists():
            report = json.loads(kept.read_text(encoding='utf-8'))
            check(stem + ' fidelity ' + fidelity, report.get('fidelity') == fidelity,
                  'got ' + str(report.get('fidelity')))
            check(stem + ' match count %d' % count,
                  report.get('observed_match_count') == count)
    summary = EXAMPLE / 'output' / 'SUMMARY.json'
    if summary.exists():
        rows = {r['request'].replace('.json', ''): r
                for r in json.loads(summary.read_text(encoding='utf-8'))}
        for stem, (_, code, _) in EXPECTED.items():
            check(stem + ' exit code %d' % code, rows.get(stem, {}).get('exit_code') == code)
    check('replay reproduces SUMMARY.json byte for byte',
          summary.is_file() and (tmp / 'SUMMARY.json').is_file() and
          (tmp / 'SUMMARY.json').read_bytes() == summary.read_bytes())


def run_tests():
    proc = subprocess.run([sys.executable, '-I', '-B', '-m', 'unittest', 'discover',
                           '-s', str(TOOL / 'tests'), '-t', str(TOOL / 'tests')],
                          capture_output=True, text=True, timeout=300)
    ran = re.search(r'Ran (\d+) tests', proc.stderr)
    n = int(ran.group(1)) if ran else 0
    check('checker test suite: 39 tests ran and passed',
          proc.returncode == 0 and n == 39, 'ran %d, exit %d' % (n, proc.returncode))


def count_things():
    observed = {
        'guides besides the bibliography': len([
            p for p in (TOOL / 'skills/gioia-methodology/references').glob('*.md')
            if p.name != 'bibliography.md']),
        'working record templates': len(re.findall(
            r'^## ', (TOOL / 'skills/gioia-methodology/assets/working-templates.md')
            .read_text(encoding='utf-8'), re.M)),
        'checker request templates': int((TOOL / 'skills/gioia-methodology/assets/quote-request.json').is_file()),
        'synthetic texts': len(list((EXAMPLE / 'input').glob('*.txt'))),
        'synthetic analytic memos': len(list((EXAMPLE / 'input').glob('memo-*.yaml'))),
        'quotation requests in example/input': len(list((EXAMPLE / 'input').glob('request-*.json'))),
        'reports in example/output': len(list((EXAMPLE / 'output').glob('*.report.json'))),
        'test definitions in tool/tests': sum(
            len(re.findall(r'^\s+def test_', p.read_text(encoding='utf-8'), re.M))
            for p in (TOOL / 'tests').glob('test_*.py')),
        'files in tool/': sum(1 for p in TOOL.rglob('*') if p.is_file()
                              and '.test-artifacts' not in p.parts and '__pycache__' not in p.parts),
        'methodological references in bibliography.md': len(re.findall(
            r'^\d+\. ', (TOOL / 'skills/gioia-methodology/references/bibliography.md')
            .read_text(encoding='utf-8'), re.M)),
    }
    for name, expected in COUNTS.items():
        check('%s = %d' % (name, expected), observed[name] == expected, 'observed %d' % observed[name])


def scan_identity():
    hits = []
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or '.test-artifacts' in path.parts or '__pycache__' in path.parts:
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            line = line.replace(PUBLIC_COMPONENT_URL, '')
            for pattern, label in PATTERNS:
                if pattern.search(line):
                    hits.append('%s:%d %s' % (path.relative_to(ROOT), i, label))
    check('identity patterns: no hits', not hits, '; '.join(hits[:10]))


def verify_inventory():
    """Compare exact release paths, byte sizes and hashes with the shipped manifest."""
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text(encoding='utf-8'))
    check('manifest component counts', manifest['counts'] == COUNTS)
    files = []
    for path in sorted(ROOT.rglob('*')):
        relative = path.relative_to(ROOT)
        if relative.parts[:2] == ('tool', '.test-artifacts') or '__pycache__' in relative.parts:
            continue
        if path.is_symlink():
            check('regular release path ' + str(relative), False)
        elif path.is_file() and relative.as_posix() != 'MANIFEST.json':
            data = path.read_bytes()
            files.append({'path': relative.as_posix(), 'bytes': len(data),
                          'sha256': hashlib.sha256(data).hexdigest()})
    check('manifest paths, sizes and SHA-256 match every payload file', files == manifest['files'])
    check('inventory totals', manifest['payload_files'] == len(files) and
          manifest['payload_bytes'] == sum(row['bytes'] for row in files))


def main():
    replay_example()
    run_tests()
    count_things()
    scan_identity()
    verify_inventory()
    memo = EXAMPLE / 'input/memo-synthetic.yaml'
    check('original synthetic memo SHA-256',
          hashlib.sha256(memo.read_bytes()).hexdigest() ==
          '8b428c25c43ca7aa7bff95fc4e18cb6f55b0b8d7073f8d3520a4dbd8151d3a63')
    if failures:
        print('FAILED: ' + ', '.join(failures))
        return 1
    print('all counts match')
    return 0


if __name__ == '__main__':
    sys.exit(main())
