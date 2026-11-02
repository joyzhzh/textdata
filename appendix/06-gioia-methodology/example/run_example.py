#!/usr/bin/env python3
"""Run the Gioia toolkit's quotation checker on every request in example/input/.

Writes one report per request to the output directory (default: example/output/) plus
SUMMARY.json with each request's fidelity and exit code. Python 3.9+, standard library only,
no network, no model. The checker opens only the text files the requests name and writes
nothing itself; reports are deterministic, so a rerun reproduces example/output/ byte for byte.

    python3 example/run_example.py            # writes example/output/
    python3 example/run_example.py --out DIR  # writes elsewhere, for comparison
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKER = HERE.parent / 'tool' / 'skills' / 'gioia-methodology' / 'scripts' / 'check_quote.py'
INPUT = HERE / 'input'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, default=HERE / 'output')
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    summary = []
    for request in sorted(INPUT.glob('request-*.json')):
        proc = subprocess.run([sys.executable, '-I', '-B', str(CHECKER), str(request)],
                              capture_output=True, text=True, timeout=30)
        report = json.loads(proc.stdout)
        target = args.out / (request.stem + '.report.json')
        target.write_text(json.dumps(report, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
        summary.append({
            'request': request.name,
            'quote': json.loads(request.read_text(encoding='utf-8'))['quote'],
            'fidelity': report.get('fidelity', report.get('status')),
            'exit_code': proc.returncode,
            'match_count': report.get('observed_match_count'),
            'report': target.name,
        })
    (args.out / 'SUMMARY.json').write_text(json.dumps(summary, indent=2, ensure_ascii=True) + '\n',
                                           encoding='utf-8')
    for row in summary:
        print('%-32s %-20s exit %d  matches %s' % (row['request'], row['fidelity'],
                                                    row['exit_code'], row['match_count']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
