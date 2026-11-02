#!/usr/bin/env python3
"""Create a wholly invented two-cycle demonstration outside the tool checkout."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from analysis_cycle import prepare, append, handoff, encoded, create_file

TEXT = '''A maker begins a short moving title with specification A.
After an unreadable result, the maker repeats specification A and accepts the next result.
A maker begins another moving title with specification B.
After an unreadable result, the maker switches to a static panel and records a transformed outcome.
A maker begins a moving title with specification C.
The maker explicitly abandons that attempt after an unreadable result.
A maker begins a moving title with specification D.
The recording stops while the maker is still adjusting the title; no result is visible.
The maker says: I used a static panel because movement hid the label.
'''


def ref(first, last=None):
    return {'manifestation_id':'MNF-SYNTHETIC-TRACE', 'locator':f'lines:{first}-{last or first}'}


def build_example(root, seal_final=True):
    root = Path(root).resolve()
    root.mkdir(parents=True)  # no reuse or overwrite
    create_file(root/'trace.txt', TEXT.encode())
    config = {'study_id':'SYNTHETIC-CONTRASTS','data_kind':'SYNTHETIC','authority_ref':'SYNTHETIC-DEMO-ONLY',
              'license':'SYNTHETIC_GENERATED','rights':'wholly invented, no real people or sources',
              'privacy':'no personal data','retention':'VAULT_ONLY',
              'model_processing':{'authority_ref':'SYNTHETIC-DEMO-ONLY','models':[]},
              'sources':[{'manifestation_id':'MNF-SYNTHETIC-TRACE','path':'trace.txt','kind':'NORMALIZED_TEXT',
                          'language':'en','rights':'wholly invented fixture','source_url':'synthetic:trace'}]}
    create_file(root/'input-config.json', encoded(config))
    cycle = prepare(root,root/'input-config.json','C001','How do responses to an unreadable result differ?',
                    'synthetic-producer','synthetic-reviewer')
    episodes=[]
    for i,(start,end,outcome) in enumerate([(1,2,'ACCEPTED'),(3,4,'TRANSFORMED'),(5,6,'ABANDONED'),(7,8,'UNKNOWN')],1):
        episodes.append({'episode_id':f'E{i:03}','boundary_basis':'UNCERTAIN' if outcome=='UNKNOWN' else 'SOURCE_EXPLICIT',
                         'outcome_status':outcome,'source_refs':['MNF-SYNTHETIC-TRACE'],'intended_outcome':'a readable moving title',
                         'boundary':{'start_ref':ref(start),'end_ref':ref(end),
                                     'ending':'TRACE_ENDS' if outcome=='UNKNOWN' else 'OUTCOME_OBSERVED',
                                     'event_order':'SOURCE_ORDER','missingness':['ending not retained'] if outcome=='UNKNOWN' else []}})
    append(cycle,'EPISODES.jsonl',episodes)
    incidents=[{'incident_id':f'I{i:03}','episode_id':f'E{i:03}','ordinal':1,'epistemic_class':'OBSERVED_ACTION',
                'description':TEXT.splitlines()[ln-1],'source_ref':ref(ln)} for i,ln in enumerate([2,4,6,8],1)]
    incidents.append({'incident_id':'I005','episode_id':'E002','ordinal':2,'epistemic_class':'CREATOR_STATED_INTERPRETATION',
                      'description':'The maker attributes the switch to label readability.','source_ref':ref(9),
                      'quote_ref':dict(ref(9),quote_sha256=hashlib.sha256(TEXT.splitlines()[8].encode()).hexdigest()),
                      'attribution_basis':'CREATOR_STATEMENT'})
    append(cycle,'INCIDENTS.jsonl',incidents)
    append(cycle,'CODES.jsonl',[{'code_id':f'CDE{i:03}','label':label,'level':'FIRST_ORDER','status':'CURRENT','incident_ids':[f'I{i:03}']}
                              for i,label in enumerate(['repeating a specification','changing the intended result','abandoning the attempt','continuing without an observed ending'],1)])
    append(cycle,'COMPARISONS.jsonl',[{'comparison_id':'CMP001','compared_ids':['I001','I004'],'relation':'DIFFERENCE',
             'purpose':'Compare repetition with an incompletely observed attempt.','observation':'E001 has a known accepted result; E004 ends without an outcome.',
             'possible_condition':None,'rival_explanation':'recording coverage differs',
             'discriminating_evidence':'a complete E004 ending','analytical_consequence':'Keep E004 UNKNOWN; do not infer eventual acceptance.', 'status':'CURRENT'}])
    category={'memo_id':'MEM001','category_id':'CAT001','status':'EMERGING',
              'definition':'A tentative repetition account: continuing the same approach after an unreadable result.',
              'not_this':'No claim about unobserved endings or real makers.','supporting_code_ids':['CDE001'],
              'comparison_ids':['CMP001'],'negative_case_ids':[],'rival_explanations':['recording selection'],
              'properties':['response after difficulty'],'dimensions':['same approach'],
              'conditions':['unreadable result'],'consequences':['another attempt']}
    append(cycle,'CATEGORY_MEMOS.jsonl',[category])
    append(cycle,'MEMOS.jsonl',[{'memo_id':f'MEMO{i:03}','memo_type':kind,'body':body,'refs':['CAT001','CMP001'],'status':'WORKING'}
              for i,(kind,body) in enumerate([('DESCRIPTIVE','Four contrasting invented endings are retained.'),
               ('COMPARISON','A missing ending differs from an observed successful outcome.'),
               ('METHODOLOGICAL','Repetition is a tentative account and must face the transformed case.'),
               ('THEORETICAL','The tentative repetition account is an analytical proposal, not evidence.')],1)])
    create_file(root/'analysis-C001.md', b'This is an invented demonstration. A tentative repetition category requires comparison against switching and abandonment. E004 is unresolved because the trace ends. No empirical claim or saturation conclusion.\n')
    handoff(cycle,root/'analysis-C001.md','Initial synthetic comparison complete; counterevidence remains to be analyzed.','NOT_REACHED')
    successor=prepare(root,cycle/'INPUT_MANIFEST.json','C002','How do responses to an unreadable result differ?',
                      'synthetic-producer','synthetic-reviewer',cycle)
    append(successor,'COMPARISONS.jsonl',[{'comparison_id':'CMP002','compared_ids':['I001','I002','I003'],'relation':'DIFFERENCE',
             'purpose':'Challenge the same-approach account with changed and abandoned outcomes.',
             'observation':'The invented traces include repetition, changed outcome, and explicit abandonment.',
             'possible_condition':'whether movement remains necessary for the intended result','rival_explanation':'different task constraints rather than learning',
             'discriminating_evidence':'matched tasks with an attributable reason for retaining or changing the goal',
             'analytical_consequence':'Bound CAT001 to cases retaining the goal and approach; do not generalize repetition to all responses.', 'status':'CURRENT'}])
    changed=dict(category, memo_id='MEM002',supersedes='MEM001',supersession_reason='The transformed and abandoned cases challenge an unrestricted repetition account.',
                 definition='Repetition is one response when the goal and approach are retained, alongside transformation and abandonment.',
                 not_this='Does not describe E002 or E003 as repetition, or infer an E004 outcome.',
                 dimensions=['retain approach','change intended result','abandon attempt'],
                 conditions=['unreadable result','goal and approach retained for repetition'],
                 comparison_ids=['CMP001','CMP002'],negative_case_ids=['E002','E003'],
                 negative_case_response={'action':'BOUND','reason':'Countercases change the scope of the repetition account.',
                                         'discriminating_evidence':'matched constraints and explicit reasons for each response'})
    append(successor,'CATEGORY_MEMOS.jsonl',[changed])
    append(successor,'MEMOS.jsonl',[{'memo_id':'MEMO005','memo_type':'THEORETICAL','status':'WORKING','refs':['MEM002','CMP002'],
            'body':'The countercases narrow the earlier repetition account. The examples establish software behavior only.',
            'supersedes':'MEMO004','supersession_reason':'Record the change in category boundary after counterevidence.'}])
    append(successor,'SAMPLING_REQUESTS.jsonl',[{'request_id':'REQ001','provisional_focus':'Conditions for retaining an approach versus changing the intended result.',
            'focus_ids':['CAT001','CMP002'],'discriminating_question':'Do matched constraints distinguish repetition from transformation?',
            'targets':['RIVAL','NEGATIVE_CASE'],'eligible_source_classes':['authorized complete normalized traces'],
            'languages':['en'],'date_range':{'from':None,'to':None},'creators':[],'workflow_regimes':[],
            'restrictions':['draft only; no acquisition or contact'],'counter_search':'a transformed result under otherwise matched constraints',
            'resource_ceiling':'one proposed matched contrast','stop_rule':'record whether the contrast is available and discriminating',
            'claim_ceiling':'bounded analyst proposal','required_return_fields':['source hash','locator','ending basis'],'status':'PROPOSED',
            'expected_observations':{'supports':'repetition only where retaining motion is required','challenges':'transformation despite the same motion requirement',
                                     'decision_if_missing':'retain the unresolved rival; do not claim adequacy'}}])
    create_file(root/'analysis-C002.md',b'This synthetic cycle narrows CAT001 using transformed and abandoned countercases. It preserves E004 as UNKNOWN. The request would distinguish constraints from a general repetition account and remains PROPOSED. These are invented traces; no empirical validity, study finding, saturation or agent efficacy is established.\n')
    if seal_final:
        handoff(successor,root/'analysis-C002.md','The planned synthetic scenarios are complete; a real-data pilot remains unperformed.','NOT_REACHED')
    return successor


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();print(build_example(args.output))
