"""Adapter: the U.S. Federal Register through its public API and the two official text sites.

Population:  https://www.federalregister.gov/api/v1/documents.json, queried one publication date at
             a time (the API returns at most 2,000 results per query), no agency, type or keyword filter.
Text:        federalregister.gov  .../documents/full_text/text/YYYY/MM/DD/<number>.txt
             govinfo.gov          .../content/pkg/FR-<date>/html/<number>.htm
             Both serve the same Government Publishing Office text in the same HTML wrapper.
Identity:    publication date + document number (the same number on two dates is two documents).
Checks:      the rules the retained collection's manifest builder applied to every file.
"""
import json
import re
import urllib.parse

NAME = 'federal_register'
SITES = {'federalregister': 'federalregister.gov', 'govinfo': 'govinfo.gov'}
API = 'https://www.federalregister.gov/api/v1/documents.json'
PER_PAGE = 1000

IMAGE_PLACEHOLDER = b'[GRAPHIC] [TIFF OMITTED]'          # the form the retained inventory counts
IMAGE_PLACEHOLDER_2 = b'GRAPHIC(S) NOT AVAILABLE IN TIFF FORMAT'  # a second form, reported separately
HIDDEN_EMAIL = b'data-cfemail="'
FR_DOC_MARKER = b'[FR Doc No:'
VOLUME_HEADER = b'[Federal Register Volume'
# Front/back-matter items the official list includes that carry no FR Doc number (exempted by name).
NO_FR_DOC_LINE = {'2007-02-02|X07-10202', '2009-12-30|X09-11230', '2009-12-30|X09-31230'}
DOCNUM_OK = re.compile(r'^[A-Za-z0-9._-]+$')


def list_identities(http, start, end, days):
    """Yield {date, document_number, type, text_url} for every document published on each day in [start, end]."""
    for day in days(start, end):
        page_url = API + '?' + urllib.parse.urlencode({
            'conditions[publication_date][is]': day, 'per_page': PER_PAGE,
            'fields[]': ['document_number', 'publication_date', 'type', 'raw_text_url'],
        }, doseq=True)
        seen = 0
        while page_url:
            status, data = http(page_url)
            if status != 200:
                raise RuntimeError('index query failed for %s: HTTP %s' % (day, status))
            body = json.loads(data.decode('utf-8'))
            for r in body.get('results', []):
                if not DOCNUM_OK.match(r['document_number']) or r['publication_date'] != day:
                    raise RuntimeError('unexpected identity from the index: %r' % r)
                seen += 1
                yield {'date': r['publication_date'], 'document_number': r['document_number'],
                       'type': r.get('type') or '', 'text_url': r.get('raw_text_url') or ''}
            page_url = body.get('next_page_url')
            if page_url is None and body.get('count', seen) != seen:
                raise RuntimeError('index for %s says %s documents, received %d' % (day, body.get('count'), seen))


def text_urls(identity, site_order):
    """Candidate text addresses in the order to try."""
    date, number = identity['date'], identity['document_number']
    urls = {
        'federalregister': identity.get('text_url') or
            'https://www.federalregister.gov/documents/full_text/text/%s/%s/%s/%s.txt' % (date[:4], date[5:7], date[8:10], number),
        'govinfo': 'https://www.govinfo.gov/content/pkg/FR-%s/html/%s.htm' % (date, number),
    }
    return [(SITES[s], urls[s]) for s in site_order]


def check_text(data, identity):
    """-> list of problems; empty means the bytes are a real Federal Register document for this identity."""
    key = identity['date'] + '|' + identity['document_number']
    number = identity['document_number']
    problems = []
    head, tail = data[:2000].lower(), data[-4000:].lower()
    if b'<html' not in head or b'<pre' not in head:
        problems.append('no_html_pre_wrapper_at_start')
    if b'</pre' not in tail:
        problems.append('no_closing_pre_at_end')
    exempt = key in NO_FR_DOC_LINE
    if FR_DOC_MARKER not in data and not exempt:
        problems.append('no_FR_Doc_No_marker')
    if exempt and VOLUME_HEADER not in data[:2000]:
        problems.append('exempted_item_without_Federal_Register_Volume_header')
    normalized = lambda s: re.sub(r'[^A-Za-z0-9]', '', s).upper()
    if number.encode() not in data and normalized(number) not in normalized(data.decode('utf-8', 'replace')) and not exempt:
        problems.append('own_document_number_missing')
    return problems


def defect_counts(data):
    """Known defects of a served file, counted per file."""
    return {'image_placeholders': data.count(IMAGE_PLACEHOLDER), 'hidden_emails': data.count(HIDDEN_EMAIL),
            'image_placeholders_other_form': data.count(IMAGE_PLACEHOLDER_2)}
