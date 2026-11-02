"""Focused synthetic regressions; all generated files remain under this revision."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_quote_helper as support
EVIDENCE, HELPER, sha = support.EVIDENCE, support.HELPER, support.sha


def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


helper = module_at('successor', HELPER)


class RevisionTests(unittest.TestCase):
    setUpClass = classmethod(support.QuoteTests.setUpClass.__func__)
    setUp = support.QuoteTests.setUp
    row = support.QuoteTests.row
    run_request = support.QuoteTests.run_request

    def test_unchecked_records_without_bindings(self):
        ready = self.row('Ready.')
        for access, use, basis, status in [
            ('blocked', 'permitted', 'synthetic', 'NOT_CHECKED_ACCESS'),
            ('unknown', 'unknown', None, 'NOT_CHECKED_ACCESS'),
            (None, 'unknown', None, 'NOT_CHECKED_ACCESS'),
            ('available', 'prohibited', None, 'NOT_CHECKED_LOCAL_USE'),
            ('available', 'unknown', None, 'NOT_CHECKED_LOCAL_USE'),
            ('available', 'permitted', ' ', 'NOT_CHECKED_LOCAL_USE'),
        ]:
            with self.subTest(access=access, use=use, basis=basis):
                missing = {'id': 'M2', 'text_path': None, 'sha256': None,
                           'hash_basis': 'unknown', 'access': access,
                           'permissions': {'local_processing': use, 'local_processing_basis': basis}}
                report = self.run_request('Ready.', [ready, missing], 1)
                self.assertEqual(report['fidelity'], 'EXACT_SINGLE_INCOMPLETE_SCOPE')
                self.assertEqual(report['unchecked_manifestation_count'], 1)
                self.assertEqual(report['matching_manifestation_ids'], ['M1'])
                item = report['results'][1]
                self.assertEqual(item['status'], status)
                self.assertIsNone(item['match_count'])
                self.assertIsNone(item['observed_sha256'])
                self.assertEqual(item['manifestation'], missing)
                with patch.object(helper, 'read_relative_regular') as read:
                    helper.check({'schema_version': 1, 'quote': 'Ready.', 'manifestations': [missing]}, self.case)
                    read.assert_not_called()

    def test_request_template_can_declare_unknown(self):
        request = json.loads((EVIDENCE / 'skills/gioia-methodology/assets/quote-request.json').read_text())
        report = self.run_request('Ready.', request['manifestations'], 1)
        self.assertEqual(report['fidelity'], 'NOT_ESTABLISHED')
        self.assertIsNone(report['results'][0]['match_count'])

    def test_whitespace_candidates_rejected(self):
        row = self.row(' \t\r\n')
        for quote in [' ', '\t', '\r\n']:
            self.assertEqual(self.run_request(quote, [row], 2)['status'], 'INVALID_REQUEST')

    def test_nonfinite_metadata_rejected_before_read(self):
        request = {'schema_version': 1, 'quote': 'Ready.', 'manifestations': [self.row('Ready.')]}
        request['manifestations'][0]['metric'] = 'NUMBER'
        for token in ['NaN', 'Infinity', '-Infinity', '1e999', '-1e999']:
            raw = json.dumps(request).replace('"NUMBER"', token)
            self.assertEqual(self.run_request('', [], 2, raw=raw)['status'], 'INVALID_REQUEST')
        request['manifestations'][0]['metric'] = float('inf')
        with patch.object(helper, 'read_relative_regular') as read:
            with self.assertRaises(ValueError):
                helper.check(request, self.case)
            read.assert_not_called()

    def test_matching_version_and_request_binding(self):
        old = self.row('We approve every draft.', 'old')
        old['version'] = 'superseded_v1'
        current = self.row('We reject some drafts.', 'current')
        current['version'] = 'v2'
        report = self.run_request('approve every draft', [old, current], 0)
        self.assertEqual(report['matching_manifestation_ids'], ['old'])
        self.assertEqual(report['results'][1]['status'], 'NO_EXACT_MATCH')
        self.assertEqual(report['request_sha256'], sha((self.case / 'request-1.json').read_bytes()))

    def test_same_storage_records_and_metadata_preserved(self):
        first = self.row('Ready.')
        first['source_text'] = 'Self-authored synthetic metadata, echoed intentionally.'
        second = copy.deepcopy(first)
        second['id'] = 'same_storage'
        report = self.run_request('Ready.', [first, second], 1)
        self.assertEqual(report['matching_manifestation_ids'], ['M1', 'same_storage'])
        self.assertEqual([r['manifestation'] for r in report['results']], [first, second])

    def test_subword_remains_a_literal_match(self):
        report = self.run_request('waited', [self.row('awaited')], 0)
        self.assertEqual(report['results'][0]['matches'][0]['byte_start'], 1)
        self.assertEqual(report['contextual_adequacy'], 'NOT_ASSESSED')

    def test_segment_order_is_not_composite_fidelity(self):
        row = self.row('First event. Later event.')
        later = self.run_request('Later event.', [row], 0)['results'][0]['matches'][0]
        first = self.run_request('First event.', [row], 0)['results'][0]['matches'][0]
        self.assertLess(first['byte_start'], later['byte_end'])
        self.assertEqual(self.run_request('Later event. First event.', [row], 1)['fidelity'], 'NO_EXACT_MATCH')

    def test_offsets_include_unicode_overlaps_and_line_endings(self):
        cases = [
            ('开始\nααα\n', 'αα', [
                {'byte_start': 7, 'byte_end': 11, 'character_start': 3, 'character_end': 5, 'line_start': 2, 'line_end': 2},
                {'byte_start': 9, 'byte_end': 13, 'character_start': 4, 'character_end': 6, 'line_start': 2, 'line_end': 2}]),
            ('One\r\nTwo\nThree\n', 'Two\n', [
                {'byte_start': 5, 'byte_end': 9, 'character_start': 5, 'character_end': 9, 'line_start': 2, 'line_end': 2}]),
            ('a\na\na\n', 'a\na', [
                {'byte_start': 0, 'byte_end': 3, 'character_start': 0, 'character_end': 3, 'line_start': 1, 'line_end': 2},
                {'byte_start': 2, 'byte_end': 5, 'character_start': 2, 'character_end': 5, 'line_start': 2, 'line_end': 3}]),
        ]
        for text, quote, expected in cases:
            self.assertEqual(helper.spans(text.encode(), quote.encode()), expected)
        text = b'marker filler line\n' * 12000
        actual = helper.spans(text, b'marker')
        self.assertEqual(len(actual), 12000)
        for i, span in enumerate(actual):
            self.assertEqual(span, {'byte_start': i * 19, 'byte_end': i * 19 + 6,
                                    'character_start': i * 19, 'character_end': i * 19 + 6,
                                    'line_start': i + 1, 'line_end': i + 1})

    def test_output_and_internal_errors(self):
        request = {'schema_version': 1, 'quote': 'Ready.', 'manifestations': [self.row('Ready.')]}
        good = self.case / 'good.json'
        bad = self.case / 'bad.json'
        good.write_text(json.dumps(request))
        bad.write_text('{')
        for mode, path in [('internal', good), ('stdout_none', good), ('stdout_none', bad),
                           ('broken_pipe', good), ('broken_pipe', bad), ('broken_pipe_internal', good)]:
            with self.subTest(mode=mode, request=path.name):
                setup = 'sys.stdout=None;' if mode == 'stdout_none' else ''
                if mode in ['internal', 'broken_pipe_internal']:
                    setup += 'del os.O_DIRECTORY;'
                code = ('import os,sys,runpy;' + setup + 'sys.argv=[' + repr(str(HELPER)) + ',' +
                        repr(str(path)) + '];runpy.run_path(' + repr(str(HELPER)) + ',run_name="__main__")')
                command = [sys.executable, '-B', '-c', code]
                if mode.startswith('broken_pipe'):
                    reader, writer = os.pipe()
                    os.close(reader)
                    try:
                        proc = subprocess.run(command, stdout=writer, stderr=subprocess.PIPE, timeout=10)
                    finally:
                        os.close(writer)
                    stdout = ''
                else:
                    proc = subprocess.run(command, capture_output=True, timeout=10)
                    stdout = proc.stdout.decode()
                receipt = {'mode': mode, 'request': path.name, 'command': command, 'exit': proc.returncode,
                           'stdout': stdout, 'stderr': proc.stderr.decode()}
                with (self.case / (mode + '-' + path.stem + '.json')).open('x') as f:
                    json.dump(receipt, f, indent=2)
                self.assertEqual(proc.returncode, 3, receipt)
                self.assertNotIn('Exception ignored', receipt['stderr'])
                self.assertNotIn('Traceback', receipt['stderr'])
                if mode == 'internal':
                    self.assertEqual(json.loads(stdout)['status'], 'HELPER_ERROR')
                else:
                    self.assertFalse(stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
