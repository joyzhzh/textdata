# One comparison, traced through the sealed records

Generated from the study's own records by `example/trace_comparison.py`. The transcripts are not reproduced: each incident carries the source file identity, the one-based line span, and, for quoted interpretations, the SHA-256 of the quoted lines. A reader holding the transcript can verify every binding; a reader without it can still follow what the analysis did with it.

Packet: cycle C003 of study LENNY-HUMAN-AGENCY-AI-20261028; tool revision as retained as historical provenance in the release-derived `MANIFEST.json`; method profile: inductive process study using grounded-theory techniques; release status NON_RELEASE; saturation status NOT_ASSESSED.

## 1. The pilot's proposal (cycle C001, six interviews)

**MEMO005** (THEORETICAL memo, supersedes MEMO004):

> Candidate theoretical framing: human agency through revisable delegation. Define action reach as what a person can attempt or accomplish; distinguish it from practical revision capacity over goals, means, standards and commitments. AI can widen the first while leaving the second unchanged or compromised. Proposed process: an opportunity or difficulty prompts delegation; people encounter outputs and limits; they inspect, accept, renegotiate, reclaim or reframe work; the arrangement and feasible goals may change. This is an assembled process hypothesis, not an observed universal sequence. Criteria and goals may also emerge through AI interaction. Meaningful revision requires more than formal accountability, but its knowledge, infrastructure and organizational conditions are unresolved.

**Category CAT001, version MEM002** (supersedes MEM001): Negotiating checkpoints and criteria: people and AI contribute to plans, evaluations and follow-up tasks, while the practical ability to contest or revise the arrangement remains an empirical question.

Dimensions then: explicit versus inferred criteria; pre-action versus post-action checkpoints; one-way versus reciprocal task direction.

## 2. The pilot asked for the evidence that could break it (REQ001, status PROPOSED)

Discriminating question: For comparable tasks, does increased output preserve people’s ability to detect trouble, refuse recommendations and change the workflow, and how do novice versus expert and worker versus owner conditions differ?

Counter-search: Find continued successful delegation without specialist understanding; knowledgeable users unable to override; ordinary workers required to adopt tools; cases where abandoning AI improves task performance or discretion.

Expected if supported: Under comparable capability and tasks, users with workable review and revision routes can change or reclaim unsatisfactory work, while users without those routes show greater output but blocked correction or imposed commitments.

Expected if challenged: Output and effective discretion improve durably without meaningful review or revision routes, or identical routes have no relation to handling disagreement once task and role differences are addressed.

## 3. Second cycle (C002): a contrary case selected before coding

Selection record for `Aishwarya Naresh Reganti + Kiriti Badam.txt` (MNF-LENNY-010, SHA-256 `53e6543c005ebc381ee4ecf88176dc54cc6c231df16ab7fb44f86cb4f9798d9a`), stage C002_AFTER_CONTEXTUAL_SCREEN_BEFORE_FULL_CODING, following REQ001:

- Gap: Expert failure, shutdown and expanding user demands
- Discriminating question: Does iterative repair preserve useful delegation, or can repairs cease to make the workflow workable?
- Opposing expected observations: A reported shutdown despite expertise challenges indefinite revision as a sufficient mechanism; bounded recalibration after scope expansion shows an alternative response.

Incidents bound to the transcript (descriptions are the analysts' paraphrases; line spans are one-based and inclusive):

| Incident | Epistemic class | Source and lines | Description | Evidence limit | Quote SHA-256 |
|---|---|---|---|---|---|
| I501 | CREATOR_REPORTED_ACTION | MNF-LENNY-010 lines:266-266 | Aishwarya reports working with customers to build end-to-end agents, narrowing the account to a customer-support use case. | General multi-customer introduction becomes one support case; no configuration or logs inspected. |  |
| I502 | CREATOR_REPORTED_ACTION | MNF-LENNY-010 lines:266-269 | In the support-product account, Aishwarya reports repeated debugging and hot fixes before shutdown. | Frequency, staffing, duration and effectiveness of individual repairs are not provided. |  |
| I503 | CREATOR_REPORTED_ACTION | MNF-LENNY-010 lines:269-269 | Aishwarya reports that the team had to shut down the support product. | Known reported cessation only. Separate Air Canada news anecdote in the same line is not support for this incident. |  |
| I504 | CREATOR_STATED_INTERPRETATION | MNF-LENNY-010 lines:266-269 | Aishwarya attributes the shutdown to emerging problems the team could not keep track of after repeated hot fixes, explaining that uncertain user/system actions made multi-step debugging difficult. | Participant causal explanation, not independent identification of the shutdown cause. | 581b179fefa72afef6cde07d4ff1a9630b0e2979effce3368119b8581801096e |

Initial codes (action-oriented, with the alternative reading each analyst recorded):

| Code | Incident | Label | Alternative reading |
|---|---|---|---|
| CDE501 | I501 | building an end-to-end support agent | The account may retrospectively compress several deployments; the exact system boundary and autonomy level are unavailable. |
| CDE502 | I502 | repeatedly patching an automated support product | Repair burden could also reflect immature implementation, insufficient resources or unusual customer requirements. |
| CDE503 | I503 | shutting down the product after repeated repairs | Shutdown might be temporary or jointly driven by commercial concerns; permanence and decision process are not stated. |
| CDE504 | I504 | finding emerging problems too numerous to track | The framework-selling context may accentuate complexity as the explanation; resources, implementation quality and customer economics remain rivals. |

## 4. The comparison that changed the category (CMP015)

- **compared_ids**: I502, I503, I504, I108, I205
- **relation**: DIFFERENCE
- **purpose**: Test whether repeated review and correction sustain delegated work.
- **observation**: Aishwarya reports repeated hot fixes ending in support-product shutdown; pilot Shipper/Boris describe review practices without comparable terminal failure.
- **possible_condition**: Multistep dependencies and unpredictable use may outrun local fixes.
- **rival_explanation**: Implementation immaturity, staffing or selected task difficulty could explain the shutdown.
- **discriminating_evidence**: Comparable logged failures with review frequency, repair effort and durable outcomes.
- **analytical_consequence**: Review opportunities are insufficient evidence of recoverability; retain withdrawal as a distinct endpoint.

**Category CAT001, version MEM006** supersedes MEM002.

- Reason recorded: Failures despite repeated patching and disputes about criteria require separating checkpoints from workable correction.
- New definition: Making evaluation answerable to the task: forming, contesting and revising criteria and checkpoints with human and AI contributions; the presence of review is distinct from the ability to make a consequential correction.
- Dimensions now: output repair versus criterion revision; review present versus consequential change achieved
- Negative cases cited: I503, I518, I509
- Negative-case response: REVISE — A reviewed output or repeated correction can still fail; task criteria themselves may be inadequate or change. Discriminating evidence: Follow a disputed criterion through attempted correction and downstream use.
- Comparisons cited: CMP015, CMP021, CMP022, CMP026

**MEMO010** (THEORETICAL memo) revises the pilot proposal:

> Revise the pilot proposal: agency through revisable delegation requires investigating whether revisions can be made consequential, not simply whether a review channel exists. Candidate process: delegate and encounter an output; judge adequacy using revisable criteria; attempt local correction; where inadequate, seek a change in expertise, infrastructure or scope, restrict use, or withdraw. Success can itself broaden the task and reopen this sequence. Resource access and authority are candidate conditions measured independently of success. CAT003 remains thin and is not enlarged merely by more task-level criteria examples. Next compare specialist reframing, provider-level evaluation repair and actual organizational authority, seeking minimally supported success and resource-rich failure as rivals. This is a conditional proposition, not a causal finding.

## 5. The revised account asked its next question (REQ002, status PROPOSED)

Focus: When local revision stalls, who can obtain a consequential change, and whose criteria or commitments govern it?

Discriminating question: Do specialist reframing, provider changes and organizational authority distinguish recovery from continued patching, and can apparent success coexist with unwanted commitments?

Focus records: CAT001, CAT004, CAT005, CMP015, CMP017, CMP025. Counter-search: Seek successful novices without specialist correction, failures despite abundant support, legitimate rejection of capability gains, and organizational explanations that predate AI.

## 6. Third cycle (C003): the case that split 'acceptable' from 'authorized'

Selection record for `Dan Shipper 2.0.txt` (MNF-LENNY-015, SHA-256 `77996f733a68141758155c92378c48fa3b885636c13130461d1ec11ab85d23d2`), stage AFTER_C002_COMPARISON_BEFORE_C003_CODING, following REQ002:

- Gap: Specialist reframing after repeated production patches
- Opposing expected observations: Reported recovery after a different diagnosis supports a reframing condition; ordinary continued prompting that suffices challenges it.

The interview was selected for a different reason (specialist reframing after repeated patches). The incident below was found while coding it in full; it was not the reason for selection.

| Incident | Epistemic class | Source and lines | Description | Evidence limit | Quote SHA-256 |
|---|---|---|---|---|---|
| I710 | CREATOR_REPORTED_ACTION | MNF-LENNY-015 lines:440-440 | He says he asked Codex to handle an investor email, expected it to ask him before sending, and discovered it had sent the email without that check. | Reports an unexpected action, not analyst observation of an unauthorized send. |  |
| I711 | CREATOR_REPORTED_ACTION | MNF-LENNY-015 lines:440-440 | He reports opening his sent mail afterward and finding the email exactly what he would have sent. | Reported retrospective acceptance only; recipient effects unknown. |  |
| I712 | CREATOR_STATED_INTERPRETATION | MNF-LENNY-015 lines:443-443 | He says he wants to think about what an email should say, while its exact sentences usually matter less to him, although he still values human writing. | A personal value distinction, not a universal property of writing or evidence that intent was preserved in every email. | 979d8bf369ae22c706d06558c7f7cfc0675eaf81ec78e8097196c5d89972556b |

| Code | Incident | Label | Alternative reading |
|---|---|---|---|
| CDE710 | I710 | Finding an email sent without the expected approval | The exact delegated instruction is unavailable; whether the agent violated an explicit standing rule cannot be independently checked. |
| CDE711 | I711 | Accepting the content after an unexpected send | Post hoc satisfaction could reflect a routine low-ambiguity task and need not generalize to consequential correspondence. |
| CDE712 | I712 | Distinguishing message intent from sentence production | The distinction may vary by genre and stakes rather than define a permanent division of labor. |

### Comparison CMP027

- **compared_ids**: I710, I711, I102, I605, I607, I817, I818
- **relation**: DIFFERENCE
- **purpose**: Test the relationship among favorable output, checkpoint compliance and effective direction.
- **observation**: Shipper reports an email sent without expected approval that nevertheless matched his intended content; other accounts describe review or interfaces designed to feel controllable.
- **possible_condition**: Routine tasks may yield acceptable outputs without a check.
- **rival_explanation**: A fortunate outcome may conceal unreliable compliance; declared checks may differ from actual behavior.
- **discriminating_evidence**: Repeated matched sends including disagreement, intervention attempts, logs and recipient effects.
- **analytical_consequence**: Separate acceptable result, authorization and perceived control; do not predict every skipped check causes harm or treat satisfaction as proof of agency.

### Category CAT001, version MEM010 (supersedes MEM006)

- Reason recorded: Favorable unapproved output and provider reform distinguish criteria, authorization, felt control and actual intervention.
- New definition: Making evaluation answerable to the task: forming and revising criteria and checkpoints across users, specialists and providers, while distinguishing acceptable content from authorized procedure and effective redirection.
- Dimensions now: content satisfaction versus procedural compliance; felt versus demonstrated control; local versus provider-level criteria
- Not this: Not a claim that unreviewed output must be bad, that felt control proves effective control, that humans alone originate criteria, or that provider-stated goals are users’ actual interests.
- Negative cases cited: I711, I808, I818
- Negative-case response: REVISE — Acceptable email content coexists with a failed approval expectation; value constraints can impair performance; an interface can target a feeling of control without observed override. Discriminating evidence: Trace disagreements and attempted changes, measuring authorization and task consequences separately.

## 7. A reviewer who did not produce the rows caught an overbroad label

Episode **E703** recorded outcome `ACCEPTED` with intended outcome: Send an investor email with content acceptable to Shipper.

Episode **E714** supersedes E703: Independent source audit requested keeping the expected approval procedure visible alongside content satisfaction; do not treat narrow ACCEPTED label as overall success.

- Intended outcome now: Send investor-email content acceptable to Shipper while following his expected pre-send approval procedure.
- Component outcome, email_content: ACCEPTED retrospectively by sender
- Component outcome, expected_presend_approval: NOT_FOLLOWED
- Component outcome, recipient_effect: UNKNOWN
- Component outcome, future_intervention_capacity: UNKNOWN

The reviewer's finding (AUD-01) and the producers' disposition are in `example/input/study/audit/INDEPENDENT_REVIEW.md` and `DISPOSITIONS.md`. The review was by a separate, non-producing agent using the same model and environment, not blinded, and not a human review.

## 8. The account after two waves (MEMO014, supersedes MEMO010)

> The candidate explanation is agency through consequential revision: people may expand what they can attempt while remaining differently able to authorize means, revise criteria, obtain repair or limit resulting commitments. This is a research proposition, not a definition from which effects are deduced. A disagreement or discrepancy can lead to local correction, autonomous route change, specialist reframing, infrastructure intervention, narrowing, pause or withdrawal. Paths need not converge on success. Resources and authority must be measured before outcomes, not inferred from success. Capacity can generate additional obligations for other people. Organizational structure, task complexity, voluntary engagement and retrospective rationalization remain live rivals. Noncoder successes do not establish no expertise; favorable output does not prove control. Direct worker trajectories and durable comparative outcomes remain missing.

## 9. What the study now asks for (REQ003, status PROPOSED)

Focus: Whether people with different authority and resources can make consequential changes during comparable AI-mediated work.

Discriminating question: Under comparable tasks/capabilities, what happens when a person disagrees with an AI-mediated action, evaluation or workload demand, and attempts to change or refuse it?

Expected if supported: With comparable tasks and capabilities, pre-existing access and decision rights distinguish consequential redirection from repeated ineffective attempts; wider production can coexist with unwanted commitments imposed elsewhere.

Expected if challenged: Comparable redirection is unrelated to those conditions, or desired discretion persists without available redirection; task difficulty, organization change or chosen engagement explains the pattern better.

Restrictions: PROPOSED only; no contact or new acquisition; Do not replace direct worker histories with further leader accounts; Record prior expertise/resources/decision rights before classifying outcomes

## 10. The analytical consequence in plain language

The six-interview pilot proposed that people keep their agency over AI-mediated work through *revisable delegation*: hand work to the system, keep a place to review and correct it. The pilot's own sampling request asked for cases that would break this. The second cycle added an account of a support product that was patched repeatedly and then shut down; comparing it with the pilot's review practices (CMP015) showed that having a channel for correction says nothing about whether correction works, so the category was redefined to separate *the presence of review* from *the ability to make a consequential change* (MEM006), and the theoretical memo was revised (MEMO010). The third cycle added an account in which an agent sent an investor's email without the expected approval, and the sender, reading it afterwards, found it exactly right. Comparing that with accounts of review and of interfaces designed to feel controllable (CMP027) split the category again: an *acceptable result*, an *authorized procedure* and *effective redirection* are three different things that an interview can show separately (MEM010). A non-producing reviewer then objected that the episode's single label ACCEPTED hid the failed approval; the producers issued a successor episode (E714) that keeps both facts, without editing the original row. The current memo (MEMO014) therefore proposes *agency through consequential revision*, and the open request (REQ003) names the evidence the archive did not supply: an ordinary worker's disagreement followed through a known consequence.

What this is not: not a validated theory, not saturation, not observed behavior (every incident is a speaker's own account), and not an independent human review. What it is: a chain in which each step is a row with an identity, a predecessor, a reason, and a locator a reader can check.

## Source files bound in this chain

| Manifestation | File | SHA-256 of the transcript | Rights as recorded |
|---|---|---|---|
| MNF-LENNY-010 | Aishwarya Naresh Reganti + Kiriti Badam.txt | 53e6543c005ebc381ee4ecf88176dc54cc6c231df16ab7fb44f86cb4f9798d9a | Researcher-supplied research material; license unverified; no redistribution grant |
| MNF-LENNY-015 | Dan Shipper 2.0.txt | 77996f733a68141758155c92378c48fa3b885636c13130461d1ec11ab85d23d2 | Researcher-supplied research material; license unverified; no redistribution grant |
