#!/usr/bin/env python3
"""Worked example: re-acquire two publication days of the Federal Register (7 and 8 December 2020) through
the public API, run every stage, and compare the result with the retained collection's inventory.

The email-redacted release outputs are kept in example/output/run/ (frame, raw files with sidecars, inventory, problems,
the reading-copy index, collection tree, pack, verify and comparison records).

    python3 example/run_example.py           replay: re-run every stage after retrieval on the kept raw files,
                                             in a temporary folder, and confirm the release records are reproduced
                                             (no network, no model, about ten seconds; writes nothing here)
    python3 example/run_example.py --record  the same, and also write example/output/REPLAY.json
    python3 example/run_example.py --live    retrieve the slice again from the public API into example/output/run/
                                             (network; about four minutes at one request per second)

Python 3.9+, standard library. Exit code 0 means the replay reproduced the kept inventory, pack list and
comparison, or that the live run completed every stage. Original 169/22 results are
checked separately by verify_historical.py from historical fingerprint records.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUN = os.path.join(HERE, 'output', 'run')
RETAINED = os.path.join(HERE, 'input', '2020-12.tsv')
ACQUIRE = os.path.join(ROOT, 'tool', 'acquire.py')
START, END = '2020-12-07', '2020-12-08'


def sha256_of(path):
    with open(path, 'rb') as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def acquire(stage, run, extra=()):
    command = [sys.executable, '-I', ACQUIRE, stage, '--run', run] + list(extra)
    done = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    print(done.stdout, end='')
    return done.returncode


def live():
    if os.path.exists(RUN):
        os.replace(RUN, RUN + '.previous-' + time.strftime('%Y%m%d-%H%M%S', time.gmtime()))
    code = acquire('all', RUN, ['--adapter', 'federal_register', '--start', START, '--end', END,
                                '--pass-name', 'sample_' + time.strftime('%Y-%m-%d', time.gmtime()), '--retained', RETAINED])
    sys.exit(code)


def replay():
    started = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        run = os.path.join(tmp, 'run')
        os.makedirs(run)
        shutil.copy(os.path.join(RUN, 'source.json'), run)
        shutil.copy(os.path.join(RUN, 'frame.tsv'), run)
        shutil.copytree(os.path.join(RUN, 'raw'), os.path.join(run, 'raw'))
        code = acquire('offline', run, ['--retained', RETAINED])
        if code:
            sys.exit('replay: a stage failed')
        same = {}
        for name in ('inventory.tsv', 'problems.tsv', os.path.join('clean', 'INDEX.tsv'), os.path.join('collection', 'packs.tsv')):
            same[name] = sha256_of(os.path.join(run, name)) == sha256_of(os.path.join(RUN, name))
        with open(os.path.join(run, 'comparison.json'), encoding='utf-8') as handle:
            fresh = json.load(handle)
        with open(os.path.join(RUN, 'comparison.json'), encoding='utf-8') as handle:
            kept = json.load(handle)
        same['comparison outcomes'] = fresh['outcomes'] == kept['outcomes']
        with open(os.path.join(run, 'verify.json'), encoding='utf-8') as handle:
            verify = json.load(handle)
        same['verify.py over the rebuilt pack'] = verify['verify_py_exit_code'] == 0 and not verify['raw_problems']
    result = {'replayed_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'python': sys.version.split()[0],
              'seconds': round(time.time() - started), 'reproduced': same, 'all_reproduced': all(same.values()),
              'comparison_outcomes': kept['outcomes'], 'evidence_basis': 'email-redacted release copies; historical original-file results are separate'}
    if '--record' in sys.argv[1:]:
        with open(os.path.join(HERE, 'output', 'REPLAY.json'), 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(json.dumps(result, indent=2) + '\n')
    for name, ok in same.items():
        print('%-40s %s' % (name, 'reproduced' if ok else 'DIFFERS'))
    print('replay: %s (%ds)' % ('OK' if all(same.values()) else 'FAILED', result['seconds']))
    sys.exit(0 if all(same.values()) else 1)


if __name__ == '__main__':
    live() if '--live' in sys.argv[1:] else replay()
