#!/usr/bin/env python3
"""Read-only, exact UTF-8 quote locator. Python 3.9+, standard library only."""

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError('Non-finite JSON number: ' + value)


def local_use_allowed(permissions):
    return (permissions.get('local_processing') == 'permitted' and
            isinstance(permissions.get('local_processing_basis'), str) and
            bool(permissions['local_processing_basis'].strip()))


def validate(request):
    require(isinstance(request, dict), 'Request must be an object')
    # Also reject overflowed JSON numbers (e.g. 1e999) in optional metadata.
    json.dumps(request, allow_nan=False)
    require(type(request.get('schema_version')) is int and request['schema_version'] == 1,
            'schema_version must be 1')
    quote = request.get('quote')
    require(isinstance(quote, str) and bool(quote), 'quote must be a nonempty string')
    require(bool(quote.strip()), 'quote must contain non-whitespace text')
    quote.encode('utf-8', errors='strict')
    rows = request.get('manifestations')
    require(isinstance(rows, list) and bool(rows), 'manifestations must be a nonempty list')
    seen = set()
    for row in rows:
        require(isinstance(row, dict), 'Each manifestation must be an object')
        mid = row.get('id')
        require(isinstance(mid, str) and bool(mid), 'Each manifestation needs an id')
        require(mid not in seen, 'Duplicate manifestation id: ' + mid)
        seen.add(mid)
        require(isinstance(row.get('permissions'), dict), 'permissions must be an object')
        access = row.get('access', 'unknown')
        require(access is None or isinstance(access, str), 'access must be a string or null')
        if access == 'available' and local_use_allowed(row['permissions']):
            require(isinstance(row.get('text_path'), str) and bool(row['text_path']),
                    'Each checked manifestation needs a text_path')
            require(isinstance(row.get('sha256'), str) and
                    re.fullmatch(r'[0-9a-f]{64}', row['sha256']) is not None,
                    'Each checked manifestation needs a lowercase SHA-256')
            require(row.get('hash_basis') == 'whole_file_bytes',
                    'Only whole_file_bytes hash basis is supported')
        else:
            # These records will not be opened. Never require acquiring bytes or
            # a new binding merely to report that a check cannot be performed.
            for key in ('text_path', 'sha256'):
                require(row.get(key) is None or isinstance(row[key], str),
                        key + ' must be a string or null')


def read_relative_regular(base, name):
    """Open components relative to base without following symlinks; never write."""
    rel = Path(name)
    require(not rel.is_absolute() and bool(rel.parts) and
            '..' not in rel.parts and '\x00' not in name,
            'text_path must stay within the request directory')
    # Directory descriptors also avoid a check-then-open symlink replacement.
    directory = os.open(str(base), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in rel.parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(rel.parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                     dir_fd=directory)
        with os.fdopen(fd, 'rb') as stream:
            require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode),
                    'text_path must be a regular file')
            return stream.read()
    finally:
        os.close(directory)


def spans(data, needle):
    """All overlapping matches; accumulate offsets without rescanning prefixes."""
    result = []
    cursor = characters = 0
    line = 1
    quote_characters = len(needle.decode('utf-8'))
    inner_lines = needle.count(b'\n') - int(needle.endswith(b'\n'))
    start = data.find(needle)
    while start != -1:
        gap = data[cursor:start]
        characters += len(gap.decode('utf-8'))
        line += gap.count(b'\n')
        cursor = start
        end = start + len(needle)
        result.append({
            'byte_start': start, 'byte_end': end,
            'character_start': characters,
            'character_end': characters + quote_characters,
            'line_start': line,
            'line_end': line + inner_lines,
        })
        start = data.find(needle, start + 1)
    return result


def check(request, base):
    validate(request)
    needle = request['quote'].encode('utf-8')
    results = []
    for row in request['manifestations']:
        permissions = row['permissions']
        # Retain the full supplied record, including unknowns and restrictions.
        result = {'manifestation': copy.deepcopy(row), 'match_count': None,
                  'matches': [], 'observed_sha256': None}
        results.append(result)
        if row.get('access', 'unknown') != 'available':
            result['status'] = 'NOT_CHECKED_ACCESS'
            continue
        if not local_use_allowed(permissions):
            result['status'] = 'NOT_CHECKED_LOCAL_USE'
            continue
        try:
            data = read_relative_regular(base, row['text_path'])
        except (OSError, ValueError):
            result['status'] = 'UNREADABLE_OR_UNSAFE_PATH'
            continue
        result['observed_sha256'] = digest(data)
        if result['observed_sha256'] != row['sha256']:
            result['status'] = 'HASH_MISMATCH'
            continue
        try:
            data.decode('utf-8', errors='strict')
        except UnicodeDecodeError:
            result['status'] = 'NOT_UTF8_TEXT'
            continue
        result['matches'] = spans(data, needle)
        result['match_count'] = len(result['matches'])
        result['status'] = ('NO_EXACT_MATCH' if not result['matches'] else
                            'EXACT_SINGLE' if len(result['matches']) == 1 else
                            'AMBIGUOUS_MATCHES')

    checked_states = {'NO_EXACT_MATCH', 'EXACT_SINGLE', 'AMBIGUOUS_MATCHES'}
    complete = all(r['status'] in checked_states for r in results)
    matching = [r for r in results if r['matches']]
    if len(matching) > 1:
        fidelity = 'AMBIGUOUS_MANIFESTATIONS'
    elif matching:
        fidelity = matching[0]['status']
    else:
        fidelity = 'NO_EXACT_MATCH' if complete else 'NOT_ESTABLISHED'
    if not complete:
        fidelity += '_INCOMPLETE_SCOPE' if matching else ''
    return {
        'schema_version': 1,
        'fidelity': fidelity,
        'matching_manifestation_ids': [r['manifestation']['id'] for r in matching],
        'scope_complete': complete,
        'observed_match_count': sum(len(r['matches']) for r in results),
        'unchecked_manifestation_count': sum(r['status'] not in checked_states for r in results),
        'quote_sha256': digest(needle), 'quote_bytes': len(needle),
        'matching_policy': 'exact_utf8_bytes_no_normalization',
        'locator_basis': 'zero_based_start_inclusive_end_exclusive; lines_one_based_LF; not_PDF_pages',
        'interpretive_assessment': 'NOT_ASSESSED',
        'contextual_adequacy': 'NOT_ASSESSED',
        'reuse_clearance': 'NOT_DETERMINED',
        'permission_basis': 'User declarations only; not independently verified',
        'source_authenticity': 'NOT_ASSESSED',
        'results': results,
    }


def emit_report(report):
    """Deliver one JSON report; a closed pipe is an output failure, not a result."""
    try:
        require(sys.stdout is not None, 'stdout is unavailable')
        print(json.dumps(report, indent=2, ensure_ascii=True, allow_nan=False))
        sys.stdout.flush()
        return True
    except (OSError, ValueError) as error:
        # Closing marks the stream closed even if its buffered flush fails.
        # Do not let interpreter shutdown retry that flush and change the exit.
        if sys.stdout is not None:
            try:
                sys.stdout.close()
            except (OSError, ValueError):
                pass
        sys.stdout = None
        try:
            print('check_quote: report could not be delivered: ' + str(error), file=sys.stderr)
            sys.stderr.flush()
        except (OSError, ValueError, AttributeError):
            pass
        return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request', type=Path, help='JSON request; text paths are relative to its directory')
    args = parser.parse_args(argv)
    try:
        request_path = args.request.resolve(strict=True)
        raw = request_path.read_bytes()
        request = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_keys,
                             parse_constant=invalid_constant)
        report = check(request, request_path.parent)
        report['request_sha256'] = digest(raw)
        exit_code = 0 if report['fidelity'] == 'EXACT_SINGLE' else 1
    except (OSError, ValueError, UnicodeError, RecursionError) as error:
        report = {'status': 'INVALID_REQUEST', 'error': str(error)}
        exit_code = 2
    except Exception as error:
        report = {'status': 'HELPER_ERROR', 'error': type(error).__name__ + ': ' + str(error)}
        exit_code = 3
    return exit_code if emit_report(report) else 3


if __name__ == '__main__':
    sys.exit(main())
