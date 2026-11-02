#!/usr/bin/env python3
"""Verify the counts this component's README states, the data files' agreement, the worked example, and the absence
of identifying patterns. Python 3.9+, standard library; no network, no model.

Usage (from the component folder):  python3 checks/verify_counts.py
Exit status 0 when every check passes. Set ANON_TERMS_FILE to a local, uncommitted term list (one term per line,
case-insensitive) to also scan every file for those terms; the list itself is never read into the report.
"""
import csv, hashlib, json, os, re, sqlite3, subprocess, sys
from pathlib import Path
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
results = []

def check(name, ok, detail=None):
    results.append({'check': name, 'passed': bool(ok), 'detail': detail})

# ---------- agent-design database ----------
cat = json.load(open(P('data/agent-design/data/catalogue.json'), encoding='utf-8'))
recs = cat['records']; fams = cat['families']
check('agent-design: 34 entries', len(recs) == 34, len(recs))
check('agent-design: 7 categories', len(fams) == 7, len(fams))
check('agent-design: 91 reference rows', sum(len(r['references']) for r in recs) == 91, sum(len(r['references']) for r in recs))
check('agent-design: 22 repository-link rows', sum(len(r['repository_urls']) for r in recs) == 22, sum(len(r['repository_urls']) for r in recs))
percat = {f['id']: sum(1 for r in recs if r['family'] == f['id']) for f in fams}
check('agent-design: category counts 5/4/5/3/5/7/5', [percat[k] for k in ['action', 'orchestration', 'state', 'interfaces', 'coordination', 'evaluation', 'evidence']] == [5, 4, 5, 3, 5, 7, 5], percat)
basis = {b: sum(1 for r in recs if r['evidence_basis'] == b) for b in ['Selected primary text', 'Documented source summary']}
check('agent-design: 19 selected-primary-text, 15 documented-summary', list(basis.values()) == [19, 15], basis)
check('agent-design: every entry says not executed or benchmarked', all(r['implementation_status'] == 'Not executed or benchmarked for this database.' for r in recs))
check('agent-design: ids AD-001..AD-034 unique', sorted(r['id'] for r in recs) == [f'AD-{i:03d}' for i in range(1, 35)])
csv.field_size_limit(10**9)
for name, n in [('records', 34), ('categories', 7), ('references', 91), ('repositories', 22)]:
    rows = list(csv.DictReader(open(P('data/agent-design/exports', f'{name}.csv'), newline='', encoding='utf-8')))
    check(f'agent-design: exports/{name}.csv has {n} rows', len(rows) == n, len(rows))
# Validate values as well as row counts across every public representation.
def csv_records(name):
    with open(P('data/agent-design/exports', name + '.csv'), newline='', encoding='utf8') as stream:
        return list(csv.DictReader(stream))

record_csv = csv_records('records')
for row in record_csv:
    for column in ('repository_urls', 'references'):
        row[column] = json.loads(row[column])
check('agent-design: CSV profiles and categories agree with catalogue', record_csv == recs and csv_records('categories') == fams)
refs = [dict(profile_id=r['id'], **{k: v or '' for k, v in ref.items()}) for r in recs for ref in r['references']]
repos = [dict(profile_id=r['id'], url=url, inspection_scope=r['repository_status']) for r in recs for url in r['repository_urls']]
check('agent-design: CSV reference and repository values agree with catalogue',
      csv_records('references') == refs and csv_records('repositories') == repos)
jl = [json.loads(x) for x in open(P('data/agent-design/exports/records.jsonl'), encoding='utf-8').read().splitlines()]
check('agent-design: records.jsonl equals catalogue records', jl == recs)
js = open(P('data/agent-design/assets/catalogue.js'), encoding='utf-8').read()
pfx = 'window.CATALOGUE = '
check('agent-design: browser data equals catalogue', js.startswith(pfx) and json.loads(js[len(pfx):-2].replace('<\\/', '</')) == cat)
db = sqlite3.connect('file:' + P('data/agent-design/exports/textdata-agent-design.sqlite') + '?mode=ro', uri=True)
check('agent-design: sqlite integrity ok', db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok')
check('agent-design: sqlite foreign keys ok', not db.execute('PRAGMA foreign_key_check').fetchall())
check('agent-design: sqlite record_json equals catalogue records', [json.loads(x[0]) for x in db.execute('SELECT record_json FROM profiles ORDER BY id')] == recs)
mem = sqlite3.connect(':memory:'); mem.executescript(open(P('data/agent-design/exports/textdata-agent-design.sql'), encoding='utf-8').read())
check('agent-design: SQL reconstructs all five tables with the same rows',
      all(mem.execute(f'SELECT * FROM {t}').fetchall() == db.execute(f'SELECT * FROM {t}').fetchall() for t in ['profiles', 'families', 'source_references', 'repositories', 'metadata']))

# ---------- systems survey ----------
cov = json.load(open(P('data/systems-survey/coverage.json'), encoding='utf-8'))
check('survey: coverage.json survey_entries = 22,667', cov.get('survey_entries') == 22667, cov.get('survey_entries'))
check('survey: coverage.json unit types sum to 22,667', sum(cov['unit_types'].values()) == 22667, cov['unit_types'])
check('survey: coverage.json assessment states sum to 22,667', sum(cov['assessment_states'].values()) == 22667, cov['assessment_states'])
mem_ = json.load(open(P('data/systems-survey/function-membership.json'), encoding='utf-8'))
check('survey: 14 research functions', len(mem_) == 14, len(mem_))
union = set(); total = 0
for f in mem_:
    union |= set(f['item_ids']); total += len(f['item_ids'])
    if cov['functions'].get(f['function']) != len(f['item_ids']):
        check(f"survey: function count agrees for {f['function']}", False, (cov['functions'].get(f['function']), len(f['item_ids'])))
check('survey: every entry appears in at least one function (union = 22,667)', len(union) == 22667, len(union))
check('survey: function memberships overlap (sum of memberships 22,749 > 22,667)', total == 22749, total)
idx_ids = []
with open(P('data/systems-survey/survey-index.csv'), newline='', encoding='utf-8') as f:
    rd = csv.DictReader(f)
    cols = rd.fieldnames
    for row in rd:
        idx_ids.append(row['id'])
held = json.load(open(P('data/systems-survey/survey-index-held-back.json'), encoding='utf-8'))
held_ids = set(i for v in held['reasons'].values() for i in v['ids'])
check('survey: index columns as documented', cols == ['id', 'name', 'unit_type', 'relevance_tier', 'assessment_status', 'identity_status', 'functions', 'disciplines', 'summary', 'field_gaps', 'source_links'], cols)
check('survey: shipped index rows + held-back ids = 22,667', len(idx_ids) + len(held_ids) == 22667, {'rows': len(idx_ids), 'held_back': len(held_ids)})
check('survey: index ids unique and disjoint from held-back ids', len(set(idx_ids)) == len(idx_ids) and not (set(idx_ids) & held_ids))
check('survey: every index id and held-back id is a member of some function', (set(idx_ids) | held_ids) <= union)
check('survey: held-back file states its own counts', held['rows_kept'] == len(idx_ids) and held['rows_dropped'] == len(held_ids))

# ---------- worked example ----------
ex = P('example/output/AD-014.md')
out = subprocess.run([sys.executable, '-I', P('example/show_record.py'), 'AD-014'], capture_output=True)
check('example: show_record.py AD-014 runs', out.returncode == 0, out.stderr.decode()[-300:])
check('example: output reproduces example/output/AD-014.md byte for byte', out.stdout == Path(ex).read_bytes())
with open(P('example/input/survey-entries-sharing-a-locator.jsonl'), encoding='utf-8') as f:
    n_entries = sum(1 for _ in f)
check('example: 7 survey entries share a locator with AD-014', n_entries == 7 and out.stdout.count(b'\n### I-') == 7, n_entries)
rec = json.load(open(P('example/input/AD-014.json'), encoding='utf-8'))
check('example: input AD-014.json equals the catalogue record', rec == next(r for r in recs if r['id'] == 'AD-014'))
check('example: AD-014 has 11 reference rows', len(rec['references']) == 11, len(rec['references']))

# ---------- release helper, worked source, and complete payload ----------
helper = P('tool/query_survey.py')
issue_id = 'I-1aea8ea4c6bffc5c6e'
issue_url = 'https://github.com/langchain-ai/langgraph/issues/7417'
lookup = subprocess.run([sys.executable, '-I', helper, '--id', issue_id], capture_output=True, text=True)
entry = json.loads(lookup.stdout) if lookup.returncode == 0 else {}
check('survey: helper retrieves the known report, status and source',
      entry.get('id') == issue_id
      and issue_url in entry.get('source_links', []) and 'unconfirmed' in entry.get('summary', ''))
browse = subprocess.run([sys.executable, '-I', helper, '--function', 'Evaluation and verification',
                         '--search', 'LangGraph', '--limit', '1'], capture_output=True, text=True)
browsed = [json.loads(line) for line in browse.stdout.splitlines()]
check('survey: function and search filters work together', browse.returncode == 0 and len(browsed) == 1
      and 'Evaluation and verification' in browsed[0]['functions'] and 'langgraph' in browsed[0]['name'].lower())
missing = subprocess.run([sys.executable, '-I', helper, '--id', sorted(held_ids)[0]], capture_output=True)
check('survey: withheld ID produces no row', missing.returncode == 1 and missing.stdout == b'')
with open(P('data/systems-survey/survey-index.csv'), newline='', encoding='utf8') as source:
    rows = {r['id']: r for r in csv.DictReader(source)}
functions = {f['function']: set(f['item_ids']) for f in mem_}
check('survey: CSV function assignments equal full membership for each released ID',
      all(set(json.loads(r['functions'])) == {name for name, ids in functions.items() if i in ids}
          for i, r in rows.items()))
check('survey: 22,640 released; 20 direct and seven linked held', len(rows) == 22640 and
      len(held['reasons']['identifying_detail_in_entry']['ids']) == 20 and
      len(held['reasons']['identifying_detail_in_linked_source_occurrence']['ids']) == 7)
check('survey: declared reason counts match distinct IDs', all(len(set(v['ids'])) == len(v['ids']) == v['count']
      for v in held['reasons'].values()) and sum(v['count'] for v in held['reasons'].values()) == len(held_ids))
check('survey: withheld summary fields', sum(not r['summary'] for r in rows.values()) == 19401)
with open(P('example/input/survey-entries-sharing-a-locator.jsonl'), encoding='utf8') as stream:
    examples = [json.loads(line) for line in stream]
public_urls = {u.rstrip('/').lower() for u in [rec['primary_url'], *rec['repository_urls'],
                                             *(r['url'] for r in rec['references'])]}
check('example: each released survey input has a shared design locator and matching index metadata',
      len({e['id'] for e in examples}) == 7 and all(set(e['links']) and
      all(u.rstrip('/').lower() in public_urls for u in e['links']) and e['name'] == rows[e['id']]['name'] for e in examples))
report = next(e for e in examples if e['id'] == issue_id)
statements = {i: p['text'] for paras in report['fields'].values() for p in paras for i in p['statement_ids']}
check('example: issue link, repeated call and uncertainty retained',
      issue_url in report['links'] and 'second copy' in statements['O-9edae85adb0581bb0f-F18']
      and 'unconfirmed' in statements['O-9edae85adb0581bb0f-F19'])
check('example: eight selected paraphrases retain their statement IDs', sum(len(p['statement_ids'])
      for e in examples for paras in e['fields'].values() for p in paras) == 8)
manifest = json.loads(Path(P('MANIFEST.json')).read_text(encoding='utf8'))
inventory = {f['path']: f for f in manifest['files']}
payload = {p.relative_to(ROOT).as_posix(): p for p in Path(ROOT).rglob('*')
           if p.is_file() and p != Path(P('MANIFEST.json'))}
check('manifest: inventory covers exactly the payload', len(inventory) == len(manifest['files'])
      and inventory.keys() == payload.keys())
check('manifest: every payload size and SHA-256 agrees', inventory.keys() == payload.keys()
      and all(p.stat().st_size == inventory[n]['bytes'] and
              hashlib.sha256(p.read_bytes()).hexdigest() == inventory[n]['sha256'] for n, p in payload.items()))
check('manifest: payload byte total', sum(p.stat().st_size for p in payload.values()) == manifest['payload_bytes'])

# ---------- identity patterns (built in) and optional local terms ----------
# the two literals are split so this file does not match its own patterns
pats = [('home-folder path', re.compile('/Us' + 'ers/')), ('mailto link', re.compile('mail' + 'to:', re.I)),
        ('e-mail address', re.compile(r'[\w.+-]+@[\w-]+(\.[\w-]+)+')), ('GitHub no-reply address', re.compile(r'users\.noreply\.github\.com', re.I)),
        ('LinkedIn link', re.compile(r'linkedin\.com', re.I)), ('Netlify subdomain', re.compile(r'netlify\.app', re.I))]
terms = []
tf = os.environ.get('ANON_TERMS_FILE')
if tf:
    terms = [t.strip().lower() for t in open(tf, encoding='utf-8') if t.strip() and not t.lstrip().startswith('#')]
hits = []; n_files = 0; size = 0
for dp, dn, fn in os.walk(ROOT):
    for name in fn:
        p = os.path.join(dp, name); n_files += 1; size += os.path.getsize(p)
        rel = os.path.relpath(p, ROOT)
        raw = Path(p).read_bytes()
        text = rel + '\n' + raw.decode('utf-8', 'replace')
        if name.endswith('.sqlite'):
            conn = sqlite3.connect(Path(p).resolve().as_uri() + '?mode=ro', uri=True)
            for table, in conn.execute("SELECT name FROM sqlite_schema WHERE type='table'"):
                safe_table = table.replace('"', '""')
                text += '\n' + '\n'.join(str(row) for row in conn.execute(f'SELECT * FROM "{safe_table}"'))
            conn.close()
        text = unquote(unquote(text))
        # These public archive URL paths contain an at-sign, not a user or contact address.
        if rel == 'data/systems-survey/survey-index.csv':
            text = re.sub(r'(https://anthology\.ach\.org/volumes/vol0003/[\w-]+/10\.63744)@'
                          r'(w9C0wDxmZTVt|GxQbSDPPyqvL)(\.pdf)', r'\1[at]\2\3', text)
            # URL-encoded package and version tags are public software locators.
            text = re.sub(r'(https://github\.com/[\w.-]+/[\w.-]+/(?:releases/tag|blob)/[^\s\"]*?)@(\d+\.\d+\.\d+)(?=[/\"])', r'\1[at]\2', text)
        for label, pat in pats:
            if pat.search(text):
                hits.append((rel, label))
        low = text.lower()
        for i, t in enumerate(terms):
            if t in low:
                hits.append((rel, f'listed term #{i + 1}'))
check('identity: no built-in pattern in any file (e-mail, home path, no-reply, LinkedIn, Netlify, mailto)', not [h for h in hits if not h[1].startswith('listed')], [h for h in hits if not h[1].startswith('listed')])
check(f"identity: no listed term in any file ({'local list supplied' if terms else 'no local list supplied; built-in patterns only'})", not [h for h in hits if h[1].startswith('listed')], [h for h in hits if h[1].startswith('listed')])
check('inventory: component total includes manifest', size == manifest['payload_bytes'] + os.path.getsize(P('MANIFEST.json')), {'files': n_files, 'bytes': size})

failed = [r for r in results if not r['passed']]
report = {'component': 'ai-systems', 'checks': results, 'passed': len(results) - len(failed), 'failed': len(failed),
          'files': n_files, 'bytes': size, 'scope': 'Structure, counts, data agreement, example reproduction and identity patterns; no software benchmark or scientific-validity claim.'}
print(json.dumps(report, indent=1))
sys.exit(1 if failed else 0)
