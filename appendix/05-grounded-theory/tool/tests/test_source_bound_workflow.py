"""Behavioral checks on wholly synthetic, recoverable temporary study trees."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from analysis_cycle import append, prepare, handoff
from source_bound import external_root, verify_seal
from validate_analysis_packet import validate_packet, current_rows, read_jsonl
spec=importlib.util.spec_from_file_location('workflow_example', ROOT/'examples/synthetic/workflow.py')
demo=importlib.util.module_from_spec(spec);spec.loader.exec_module(demo)


class SourceBoundWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Never permanently delete test outputs; the local no-delete policy applies.
        cls.scratch=Path(tempfile.mkdtemp(prefix='gt-workflow-tests-'))

    def study(self):
        parent=Path(tempfile.mkdtemp(prefix='case-',dir=self.scratch))
        return demo.build_example(parent/'study',seal_final=False)

    def test_contrasting_endings_and_changed_category_are_usable(self):
        c=self.study();validate_packet(c)
        self.assertEqual({r['outcome_status'] for r in read_jsonl(c/'EPISODES.jsonl')},{'ACCEPTED','TRANSFORMED','ABANDONED','UNKNOWN'})
        old=read_jsonl(c.parent/'C001/CATEGORY_MEMOS.jsonl')[0]
        now=current_rows(read_jsonl(c/'CATEGORY_MEMOS.jsonl'),'memo_id')
        self.assertEqual(len(now),1);self.assertNotEqual(now[0]['definition'],old['definition'])
        self.assertEqual(now[0]['negative_case_response']['action'],'BOUND')
        self.assertEqual(now[0]['negative_case_ids'],['E002','E003'])
        self.assertEqual(old['status'],'EMERGING')  # original row was not edited to SUPERSEDED
        verify_seal(c.parent/'C001')

    def test_missing_ending_cannot_be_abandonment(self):
        c=self.study();r=copy.deepcopy(read_jsonl(c/'EPISODES.jsonl')[-1]);r.pop('__line__')
        r.update(episode_id='E005',outcome_status='ABANDONED',supersedes='E004',supersession_reason='invalid attempted inference')
        before=(c/'EPISODES.jsonl').read_bytes()
        with self.assertRaisesRegex(ValueError,'UNKNOWN'):append(c,'EPISODES.jsonl',[r])
        self.assertEqual((c/'EPISODES.jsonl').read_bytes(),before)

    def test_behavior_only_cannot_be_creator_belief(self):
        c=self.study();r={'incident_id':'I006','episode_id':'E001','ordinal':2,'description':'The maker believes repetition guarantees success.',
             'epistemic_class':'CREATOR_STATED_INTERPRETATION','source_ref':demo.ref(2),'attribution_basis':'BEHAVIOR_ONLY',
             'quote_ref':dict(demo.ref(2),quote_sha256=hashlib.sha256(demo.TEXT.splitlines()[1].encode()).hexdigest())}
        before=(c/'INCIDENTS.jsonl').read_bytes()
        with self.assertRaisesRegex(ValueError,'behavior alone'):append(c,'INCIDENTS.jsonl',[r])
        self.assertEqual((c/'INCIDENTS.jsonl').read_bytes(),before)

    def test_invented_quote_cannot_pass_byte_binding(self):
        c=self.study();r={'incident_id':'I006','episode_id':'E001','ordinal':2,'description':'Unsupported attributed belief.',
             'epistemic_class':'CREATOR_STATED_INTERPRETATION','source_ref':demo.ref(2),'attribution_basis':'CREATOR_STATEMENT',
             'quote_ref':dict(demo.ref(2),quote_sha256='0'*64)}
        with self.assertRaisesRegex(ValueError,'quote hash'):append(c,'INCIDENTS.jsonl',[r])

    def test_changed_source_bytes_are_rejected(self):
        c=self.study();(c.parent/'trace.txt').write_text(demo.TEXT+'Injected synthetic line.\n')
        with self.assertRaisesRegex(ValueError,'source hash mismatch'):validate_packet(c)

    def test_broken_source_link_and_out_of_range_locator_are_rejected(self):
        c=self.study();r={'incident_id':'I006','episode_id':'E001','ordinal':2,'description':'Invented action.',
                         'epistemic_class':'OBSERVED_ACTION','source_ref':demo.ref(999)}
        with self.assertRaisesRegex(ValueError,'locator outside'):append(c,'INCIDENTS.jsonl',[r])
        r['source_ref']['manifestation_id']='MNF-MISSING'
        with self.assertRaisesRegex(ValueError,'not among episode'):append(c,'INCIDENTS.jsonl',[r])

    def test_silent_history_replacement_is_rejected(self):
        c=self.study();p=c/'CODES.jsonl';rows=read_jsonl(p);rows[0]['label']='silently changed label'
        p.write_text(''.join(json.dumps({k:v for k,v in r.items() if k!='__line__'})+'\n' for r in rows))
        with self.assertRaisesRegex(ValueError,'silent history replacement'):validate_packet(c)

    def test_duplicate_identity_cannot_overwrite_an_existing_row(self):
        c=self.study();r={k:v for k,v in read_jsonl(c/'CODES.jsonl')[0].items() if k!='__line__'};r['label']='different'
        before=(c/'CODES.jsonl').read_bytes()
        with self.assertRaisesRegex(ValueError,'duplicate'):append(c,'CODES.jsonl',[r])
        self.assertEqual((c/'CODES.jsonl').read_bytes(),before)

    def test_countercase_with_no_changed_state_is_rejected(self):
        c=self.study();r={k:v for k,v in read_jsonl(c/'CATEGORY_MEMOS.jsonl')[-1].items() if k!='__line__'}
        r.update(memo_id='MEM003',supersedes='MEM002',supersession_reason='claims revision without changing interpretation')
        before=(c/'CATEGORY_MEMOS.jsonl').read_bytes()
        with self.assertRaisesRegex(ValueError,'change analytical state'):append(c,'CATEGORY_MEMOS.jsonl',[r])
        self.assertEqual((c/'CATEGORY_MEMOS.jsonl').read_bytes(),before)

    def test_comparison_without_consequence_is_rejected(self):
        c=self.study();r={k:v for k,v in read_jsonl(c/'COMPARISONS.jsonl')[-1].items() if k!='__line__'}
        r['comparison_id']='CMP003';r.pop('analytical_consequence')
        with self.assertRaisesRegex(ValueError,'analytical_consequence'):append(c,'COMPARISONS.jsonl',[r])

    def test_request_cannot_self_authorize_or_offer_identical_predictions(self):
        c=self.study();r={k:v for k,v in read_jsonl(c/'SAMPLING_REQUESTS.jsonl')[0].items() if k!='__line__'}
        r.update(request_id='REQ002',status='AUTHORIZED',authority_ref='invented-authority')
        with self.assertRaisesRegex(ValueError,'only PROPOSED'):append(c,'SAMPLING_REQUESTS.jsonl',[r])
        r['status']='PROPOSED';r['expected_observations']['challenges']=r['expected_observations']['supports']
        with self.assertRaisesRegex(ValueError,'discriminate'):append(c,'SAMPLING_REQUESTS.jsonl',[r])

    def test_seal_prevents_helper_edits_and_detects_later_tampering(self):
        c=self.study();handoff(c,c.parent/'analysis-C002.md','bounded synthetic completion','NOT_REACHED')
        with self.assertRaisesRegex(ValueError,'sealed cycle'):append(c,'MEMOS.jsonl',[{'memo_id':'MEMO006'}])
        validate_packet(c)
        with (c/'MEMOS.jsonl').open('a') as f:f.write('\n')
        with self.assertRaisesRegex(ValueError,'sealed history changed'):validate_packet(c)

    def test_no_saturation_state_and_no_overwriting_cycle(self):
        c=self.study()
        with self.assertRaisesRegex(ValueError,'saturation declarations'):handoff(c,c.parent/'analysis-C002.md','stop','SATURATED')
        before=(c/'MANIFEST.json').read_bytes()
        with self.assertRaises(FileExistsError):prepare(c.parent,c/'INPUT_MANIFEST.json','C002','question','producer','reviewer')
        self.assertEqual((c/'MANIFEST.json').read_bytes(),before)

    def test_vault_cannot_contain_a_nested_git_checkout(self):
        p=Path(tempfile.mkdtemp(dir=self.scratch));(p/'nested/.git').mkdir(parents=True)
        with self.assertRaisesRegex(ValueError,'contains a Git'):external_root(p)
        with self.assertRaisesRegex(ValueError,'tool'):external_root(ROOT)

    def test_category_version_cannot_silently_fork_its_current_state(self):
        c=self.study();r={k:v for k,v in read_jsonl(c/'CATEGORY_MEMOS.jsonl')[-1].items() if k!='__line__'}
        r.update(memo_id='MEM003');r.pop('supersedes');r.pop('supersession_reason')
        with self.assertRaisesRegex(ValueError,'multiple current versions'):append(c,'CATEGORY_MEMOS.jsonl',[r])

    def test_retirement_reason_is_visible_in_the_handoff(self):
        c=self.study();r={k:v for k,v in read_jsonl(c/'CATEGORY_MEMOS.jsonl')[-1].items() if k!='__line__'}
        r.update(memo_id='MEM003',supersedes='MEM002',status='RETIRED',
                 supersession_reason='retiring this synthetic candidate',retirement_reason='the candidate does not distinguish responses')
        r['negative_case_response']['action']='RETIRE'
        append(c,'CATEGORY_MEMOS.jsonl',[r])
        path=handoff(c,c.parent/'analysis-C002.md','candidate retired','NOT_REACHED')
        blocks=__import__('re').findall(r'```json\n(.*?)\n```',path.read_text(),__import__('re').S)
        records=[json.loads(b) for b in blocks]
        retired=next(r for r in records if r.get('memo_id')=='MEM003')
        self.assertEqual(retired['retirement_reason'],'the candidate does not distinguish responses')
        self.assertEqual(current_rows(read_jsonl(c/'CATEGORY_MEMOS.jsonl'),'memo_id'),[])

    def test_pending_amendments_cannot_be_activated_as_defaults(self):
        c=self.study();p=c/'MANIFEST.json';m=json.loads(p.read_text());m['method_defaults']['pending_amendments']['optional_gerunds']=True;p.write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError,'unratified'):validate_packet(c)


if __name__=='__main__':unittest.main()
