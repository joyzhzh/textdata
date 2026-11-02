# Adaptable working records

Copy only the section useful to the task. These are prompts for recording evidence and decisions, not a mandatory database schema or proof of quality. `unknown` means not established; `not_applicable` needs a reason. Preserve predecessor records when revising completed work.

## Reference entry

```yaml
record_id:
recorded_citation:
work: {id: null, identity_confidence: unknown, unresolved_matches: []}
manifestation:
  id:
  kind:
  version: unknown
  capture_event: unknown
  retained_locator:
  hash: {algorithm: sha256, value: null, basis: unknown}
  extraction: {parent_id: null, parent_hash: null, method: unknown, replay_status: not_checked}
  inspected_coverage: unknown
assertion_provenance: {who: unknown, source: unknown, date: unknown}
collection_role: unknown
admission: {state: undecided, who: null, when: null, reason: null}
access: {state: unknown, route: null, checked_at: null, coverage: unknown}
source_status: {state: unknown, source: null, checked_at: null}
permissions:
  retention: unknown
  local_processing: unknown
  local_processing_basis: null
  quote_reuse: unknown
  participant_data_use: unknown
  evidence_and_scope: null
  restrictions: []
typed_links: []
predecessor: {id: null, hash: null, hash_basis: null}
unresolved_checks: []
```

## Analytic decision

```yaml
decision_id:
question_and_unit:
inputs:
  - excerpt_id:
    manifestation_and_version:
    locator_and_hash_basis:
    permitted_use:
    participant_expression: null
    context_and_translation_limits:
concept:
  original_suggestion:
  label:
  level: proposed_researcher_concept
  origin: model
  state: proposed
  rationale:
  aggregation_status: unresolved
adoption: {who: null, when: null, explicit_instruction: null, reason: null}
alternatives: []
negative_cases: {status: not_assessed, excerpt_refs: [], implications: null}
exclusions_with_reasons: []
relationships:
  - endpoints: []
    relation_type: unspecified  # e.g. temporal, causal, enabling, conditional, co_membership
    claim_status: hypothesis
    unit_time_case:
    warrant_refs: []
    rival_explanations: []
    disconfirming_refs: []
    state: warrant_missing
literature_consultation: []
revision:
  predecessor_id: null
  predecessor_hash_and_basis: null
  changed_by: null
  reason: null
quote_checks: []  # Per candidate/segment: report_ref, manifestation_id, matches, gap/context review
contextual_adequacy: not_assessed
interpretive_assessment: unresolved
unresolved_questions: []
```

## Coverage statement

```yaml
question_and_construct:
unit:
procedure:
inspected_material_and_versions: []
unavailable_routes: []
unsearched_routes: []
positive_tail: unknown
adverse_tail: unknown
counts: {inspected: null, eligible_total: null, denominator_basis: unknown}
stop_reason:
allowed_claim:
remaining_unknowns: []
```

## Maintenance proposal

```yaml
plan_id:
state: proposed_not_executed
purpose:
items:
  - item_id:
    action: propose_index_entry
    source_identity_and_hash_basis:
    proposed_target:
    expected_before:
    expected_after:
    restrictions: []
    decision_required:
    observed_execution: not_executed
    recovery_if_partial:
approval: {person: null, exact_plan_sha256: null, scope: null, date: null}
preservation: originals_retained
admission_effect: none
release_effect: none
```

No delete operation is supported. Only the researcher personally deletes. If a separately authorized action fails, append a receipt per item with before/after evidence and known/unknown outcome; preserve the plan and partial history.
