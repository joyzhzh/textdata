"""Synthetic self-tests. Fixtures/results are retained; nothing is deleted."""

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

EVIDENCE = Path(__file__).resolve().parents[1]
HELPER = EVIDENCE / 'skills/gioia-methodology/scripts/check_quote.py'


def sha(data):
    return hashlib.sha256(data).hexdigest()


class QuoteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (EVIDENCE / '.test-artifacts').mkdir(exist_ok=True)
        cls.run_root = Path(tempfile.mkdtemp(prefix='quote-tests-', dir=EVIDENCE / '.test-artifacts'))
        print('Retained fixtures: ' + str(cls.run_root), flush=True)

    def setUp(self):
        self.case = self.run_root / self._testMethodName
        self.case.mkdir()
        self.calls = 0

    def row(self, text='I waited. Then I sent the draft.\n', mid='M1'):
        data = text.encode('utf-8') if isinstance(text, str) else text
        filename = mid + '.txt'
        with (self.case / filename).open('xb') as f:
            f.write(data)
        return {'id': mid, 'work_id': 'W?', 'kind': 'synthetic_text',
                'version': 'unknown', 'text_path': filename, 'sha256': sha(data),
                'hash_basis': 'whole_file_bytes', 'access': 'available',
                'admission': {'state': 'undecided', 'who': None},
                'source_status': {'state': 'unknown'},
                'permissions': {'local_processing': 'permitted',
                                'local_processing_basis': 'Self-authored synthetic test',
                                'quote_reuse': 'unknown', 'participant_data_use': 'not_applicable_synthetic',
                                'restrictions': ['Synthetic only; no empirical evidence']}}

    def run_request(self, quote, rows, expected_exit, raw=None):
        self.calls += 1
        path = self.case / ('request-%d.json' % self.calls)
        request = {'schema_version': 1, 'quote': quote, 'manifestations': rows}
        with path.open('x', encoding='utf-8') as f:
            f.write(raw if raw is not None else json.dumps(request, ensure_ascii=False))
        before = {p.name: p.read_bytes() for p in self.case.iterdir() if p.is_file() and not p.is_symlink()}
        proc = subprocess.run([sys.executable, '-B', str(HELPER), str(path)],
                              capture_output=True, text=True, timeout=10)
        after = {p.name: p.read_bytes() for p in self.case.iterdir() if p.is_file() and not p.is_symlink()}
        self.assertEqual(before, after, 'Helper changed inputs or wrote files')
        report = json.loads(proc.stdout)
        with (self.case / ('observed-%d.json' % self.calls)).open('x') as f:
            json.dump({'exit': proc.returncode, 'stderr': proc.stderr, 'report': report}, f, indent=2)
        self.assertEqual(proc.returncode, expected_exit, proc.stdout + proc.stderr)
        return report

    def test_exact_unicode_offsets(self):
        r = self.row('起点\nCafé — wait.\n')
        out = self.run_request('Café', [r], 0)
        self.assertEqual(out['fidelity'], 'EXACT_SINGLE')
        self.assertEqual(out['results'][0]['matches'], [
            {'byte_start': 7, 'byte_end': 12, 'character_start': 3,
             'character_end': 7, 'line_start': 2, 'line_end': 2}])
        self.assertEqual(out['interpretive_assessment'], 'NOT_ASSESSED')
        self.assertEqual(out['contextual_adequacy'], 'NOT_ASSESSED')
        self.assertEqual(out['reuse_clearance'], 'NOT_DETERMINED')

    def test_altered_word_is_rejected(self):
        out = self.run_request('I hesitated.', [self.row()], 1)
        self.assertEqual(out['fidelity'], 'NO_EXACT_MATCH')

    def test_splice_is_rejected(self):
        out = self.run_request('I waited. I sent the draft.', [self.row()], 1)
        self.assertEqual(out['fidelity'], 'NO_EXACT_MATCH')

    def test_ellipsis_is_not_expanded(self):
        out = self.run_request('I waited. … the draft.', [self.row()], 1)
        self.assertEqual(out['fidelity'], 'NO_EXACT_MATCH')

    def test_duplicate_passages_all_reported(self):
        out = self.run_request('Ready.', [self.row('Ready.\nNot yet.\nReady.\n')], 1)
        self.assertEqual(out['fidelity'], 'AMBIGUOUS_MATCHES')
        self.assertEqual([x['byte_start'] for x in out['results'][0]['matches']], [0, 16])

    def test_overlapping_matches(self):
        out = self.run_request('aa', [self.row('aaa')], 1)
        self.assertEqual([x['byte_start'] for x in out['results'][0]['matches']], [0, 1])

    def test_two_versions_not_merged(self):
        a = self.row('Ready. Version one.', 'M1')
        b = self.row('Ready. Version two.', 'M2')
        a['version'] = '1'; b['version'] = '2'
        out = self.run_request('Ready.', [a, b], 1)
        self.assertEqual(out['fidelity'], 'AMBIGUOUS_MANIFESTATIONS')
        self.assertEqual([x['manifestation'] for x in out['results']], [a, b])

    def test_identical_files_remain_two_manifestations(self):
        a = self.row('Ready.', 'M1'); b = self.row('Ready.', 'M2')
        out = self.run_request('Ready.', [a, b], 1)
        self.assertEqual(out['fidelity'], 'AMBIGUOUS_MANIFESTATIONS')

    def test_unknown_access_is_not_zero(self):
        row = self.row(); row['access'] = 'unknown'; row['text_path'] = 'never-created.txt'
        out = self.run_request('I waited.', [row], 1)
        self.assertEqual(out['results'][0]['status'], 'NOT_CHECKED_ACCESS')
        self.assertIsNone(out['results'][0]['match_count'])
        self.assertIsNone(out['results'][0]['observed_sha256'])
        self.assertEqual(out['fidelity'], 'NOT_ESTABLISHED')

    def test_unknown_and_prohibited_local_permission_gate_read(self):
        row = self.row()
        for state in ['unknown', 'prohibited']:
            row['permissions']['local_processing'] = state
            row['text_path'] = 'never-created.txt'
            out = self.run_request('I waited.', [row], 1)
            self.assertEqual(out['results'][0]['status'], 'NOT_CHECKED_LOCAL_USE')
            self.assertIsNone(out['results'][0]['match_count'])

    def test_permission_basis_required(self):
        row = self.row(); row['permissions']['local_processing_basis'] = ''
        out = self.run_request('I waited.', [row], 1)
        self.assertEqual(out['results'][0]['status'], 'NOT_CHECKED_LOCAL_USE')

    def test_unknown_or_prohibited_reuse_never_cleared(self):
        row = self.row()
        for state in ['unknown', 'prohibited']:
            row['permissions']['quote_reuse'] = state
            out = self.run_request('I waited.', [row], 0)
            self.assertEqual(out['reuse_clearance'], 'NOT_DETERMINED')
            self.assertEqual(out['results'][0]['manifestation'], row)

    def test_status_and_admission_independent_of_match(self):
        row = self.row(); row['source_status'] = {'state': 'retracted', 'source': 'synthetic notice'}
        row['admission'] = {'state': 'excluded', 'who': 'fictional researcher', 'reason': 'fixture'}
        out = self.run_request('I waited.', [row], 0)
        self.assertEqual(out['results'][0]['manifestation'], row)

    def test_single_match_with_unchecked_version_is_incomplete(self):
        a = self.row('Ready.', 'M1'); b = self.row('Ready.', 'M2'); b['access'] = 'blocked'
        out = self.run_request('Ready.', [a, b], 1)
        self.assertEqual(out['fidelity'], 'EXACT_SINGLE_INCOMPLETE_SCOPE')
        self.assertFalse(out['scope_complete'])
        self.assertEqual(out['unchecked_manifestation_count'], 1)

    def test_no_match_plus_blocked_is_not_absence(self):
        a = self.row('Wait.', 'M1'); b = self.row('Ready.', 'M2'); b['access'] = 'blocked'
        out = self.run_request('Ready.', [a, b], 1)
        self.assertEqual(out['fidelity'], 'NOT_ESTABLISHED')

    def test_changed_bytes_stop_before_matching(self):
        row = self.row('Ready. inserted.'); row['sha256'] = sha(b'Ready.')
        out = self.run_request('Ready.', [row], 1)
        self.assertEqual(out['results'][0]['status'], 'HASH_MISMATCH')
        self.assertIsNone(out['results'][0]['match_count'])

    def test_reordered_pages_fail_old_binding(self):
        row = self.row('PAGE 2\nReady.\fPAGE 1\nWait.')
        row['sha256'] = sha(b'PAGE 1\nWait.\fPAGE 2\nReady.')
        out = self.run_request('Ready.', [row], 1)
        self.assertEqual(out['results'][0]['status'], 'HASH_MISMATCH')

    def test_unicode_normalization_is_not_silent(self):
        row = self.row('Cafe\u0301')
        out = self.run_request('Caf\u00e9', [row], 1)
        self.assertEqual(out['fidelity'], 'NO_EXACT_MATCH')

    def test_crlf_not_collapsed(self):
        row = self.row(b'One\r\nTwo\r\n')
        out = self.run_request('One\nTwo', [row], 1)
        self.assertEqual(out['fidelity'], 'NO_EXACT_MATCH')
        exact = self.run_request('Two', [row], 0)
        self.assertEqual(exact['results'][0]['matches'][0]['byte_start'], 5)

    def test_invalid_utf8_is_not_decoded_lossily(self):
        out = self.run_request('Ready.', [self.row(b'Ready.\xff')], 1)
        self.assertEqual(out['results'][0]['status'], 'NOT_UTF8_TEXT')

    def test_directory_path_is_not_a_text_file(self):
        row = self.row(); row['text_path'] = '.'
        out = self.run_request('I waited.', [row], 1)
        self.assertEqual(out['results'][0]['status'], 'UNREADABLE_OR_UNSAFE_PATH')

    def test_missing_file_does_not_become_zero(self):
        row = self.row(); row['text_path'] = 'absent.txt'
        out = self.run_request('I waited.', [row], 1)
        self.assertEqual(out['results'][0]['status'], 'UNREADABLE_OR_UNSAFE_PATH')
        self.assertIsNone(out['results'][0]['match_count'])

    def test_parent_and_absolute_paths_are_refused(self):
        row = self.row()
        for path in ['../anything.txt', str(self.case / 'M1.txt')]:
            row['text_path'] = path
            out = self.run_request('I waited.', [row], 1)
            self.assertEqual(out['results'][0]['status'], 'UNREADABLE_OR_UNSAFE_PATH')

    def test_symlink_file_and_directory_are_refused(self):
        row = self.row()
        (self.case / 'alias.txt').symlink_to('M1.txt')
        (self.case / 'alias-dir').symlink_to(self.case, target_is_directory=True)
        for path in ['alias.txt', 'alias-dir/M1.txt']:
            row['text_path'] = path
            out = self.run_request('I waited.', [row], 1)
            self.assertEqual(out['results'][0]['status'], 'UNREADABLE_OR_UNSAFE_PATH')

    def test_empty_quote_is_invalid(self):
        out = self.run_request('', [self.row()], 2)
        self.assertEqual(out['status'], 'INVALID_REQUEST')

    def test_duplicate_identity_is_invalid(self):
        row = self.row()
        out = self.run_request('I waited.', [row, copy.deepcopy(row)], 2)
        self.assertEqual(out['status'], 'INVALID_REQUEST')

    def test_duplicate_json_keys_are_invalid(self):
        out = self.run_request('unused', [], 2, raw='{"schema_version":1,"schema_version":2}')
        self.assertEqual(out['status'], 'INVALID_REQUEST')

    def test_wrong_hash_basis_is_invalid(self):
        row = self.row(); row['hash_basis'] = 'compact_json_object'
        out = self.run_request('I waited.', [row], 2)
        self.assertEqual(out['status'], 'INVALID_REQUEST')

    def test_malformed_hash_is_invalid(self):
        row = self.row(); row['sha256'] = None
        out = self.run_request('I waited.', [row], 2)
        self.assertEqual(out['status'], 'INVALID_REQUEST')


if __name__ == '__main__':
    unittest.main(verbosity=2)
