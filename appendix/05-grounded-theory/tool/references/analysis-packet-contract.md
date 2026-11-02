# Analysis packet contract — schema 0.2-phase-a

Each analytical cycle is a new directory. Historical cycles are immutable.

```text
C001/
  MANIFEST.json
  EPISODES.jsonl
  INCIDENTS.jsonl
  CODES.jsonl
  COMPARISONS.jsonl
  CATEGORY_MEMOS.jsonl
  MEMOS.jsonl
  SAMPLING_REQUESTS.jsonl
```

Row shapes are defined once, in `schemas/*.schema.json`, one schema per file,
and the validator applies them with `jsonschema`. This page states what each
file is for and the cross-file rules the validator adds.

## Identities

Formats are fixed: `E###` episodes, `I###` incidents, `CDE###` codes,
`CMP###` comparisons, `CAT###` categories, `MEM###` category memos,
`MEMO###` analytical memos, `REQ###` sampling requests, and `MNF-…`
manifestations minted by the study vault. Timestamps are ISO-8601 UTC with a
`Z` suffix. Hashes are lowercase SHA-256.

## Manifest

`schema_version` is `0.2-phase-a`. The manifest binds the frozen input
manifest hash, the exact protocol revision, the exact `tool_revision` of this
repository, the `producer_seat`, a `reviewer_seat` that must differ, and
`model_processing` naming the processing-authority decision and the exact
models used (an empty list means no model processed study data).
`analysis_status` is `WORKING` or `SUBMITTED_FOR_REVIEW`; `release_status` is
always `NON_RELEASE`; `saturation_status` is `NOT_ASSESSED`, `NOT_REACHED`,
or `PROVISIONAL_SUFFICIENCY_CANDIDATE`, never a saturation claim.

## Episodes

Each row has `boundary_basis` (`SOURCE_EXPLICIT`, `RECONSTRUCTED`,
`UNCERTAIN`), `outcome_status` (`ACCEPTED`, `TRANSFORMED`, `SUBSTITUTED`,
`DECOMPOSED`, `POSTPONED`, `ABANDONED`, `UNKNOWN`), and nonempty
`source_refs` of manifestation identities. An episode reconstructed from a
vault package may carry `derived_from` naming the `PKG-` package and `EPI-`
episodes; see [vocabulary-crosswalk.md](vocabulary-crosswalk.md) for how the
vault's descriptive outcome relates to the analytical one.

## Incidents

Each row has `episode_id`, a positive `ordinal` unique within its episode,
exactly one `epistemic_class`, and `description`.

- Source-based classes require `source_ref` with a manifestation among the
  episode's `source_refs` and an exact locator.
- `CREATOR_STATED_INTERPRETATION` also requires `quote_ref`: the same
  manifestation, a locator, and the SHA-256 of the exact retained wording.
  Free text is not a quotation binding.
- `ANALYST_INFERENCE` requires `inference_basis_ids`; `THEORETICAL_CONSTRUCT`
  requires `construct_basis_ids`. Both cite existing incidents or codes and
  never the incident itself.
- An incident reconstructed from a vault event may carry
  `derived_from_event_id` (`EVT-…`).

## Codes

Each row has `label`, `level` (`FIRST_ORDER` or `IN_VIVO`), `status`
(`CURRENT`, `SUPERSEDED`, `RETIRED`), and nonempty `incident_ids`.

## Comparisons

Constant comparison is recorded, not asserted. Each row names at least two
compared identities (incidents, episodes, codes, or categories), a `relation`
(`SIMILARITY`, `DIFFERENCE`, `CONDITION`, `CONSEQUENCE`), the `observation`,
a `possible_condition` and `rival_explanation` (explicit `null` when none was
identified), and the `discriminating_evidence` that would settle it.

## Category memos

Each row has `category_id`, `status`, `definition`, `not_this`,
`supporting_code_ids`, `comparison_ids`, `negative_case_ids`,
`rival_explanations`, and optionally `counter_search`.

- `SENSITIZING_ONLY` needs no support. Interesting language is not support.
- `EMERGING` and `FOCUSED` require at least one supporting code and at least
  one recorded comparison.
- `FOCUSED` additionally requires at least one rival explanation and a
  `counter_search` stating what was sought that should violate the category.
  A negative case need not exist yet; the search for one must be recorded.

## Memos

Descriptive, comparison, methodological, and theoretical memos are separate
record types (`memo_type`) in one file. A memo has `refs` to existing
identities and a `body`; comparison and theoretical memos must cite at least
one identity. A memo is an argument, never evidence.

## Sampling requests

A request is the one contract shared with the evidence vault and is defined
in `schemas/sampling-request.schema.json`: `provisional_focus` and the
`focus_ids` (existing categories or comparisons) it rests on,
`discriminating_question`, `targets` from `SUPPORT`, `CONTRADICTION`,
`BOUNDARY`, `RIVAL`, `NEGATIVE_CASE`, `eligible_source_classes`, `languages`,
`date_range`, `creators`, `workflow_regimes` (the vault's regime vocabulary),
`restrictions`, `counter_search`, `resource_ceiling`, `stop_rule`,
`claim_ceiling`, `required_return_fields`, and `status`. The tool writes only
`PROPOSED`; `AUTHORIZED`, `RETURNED`, and `CLOSED` require an `authority_ref`
naming the decision that changed the status, and `RETURNED` names the
`returned_package_id`.

## Cross-file rules

- Identities are unique within their file.
- Every cited identity exists in the packet.
- Supersession is explicit: a successor carries `supersedes` and
  `supersession_reason`, names an earlier row, and cannot fork an existing chain.
  Its predecessor stays byte-identical; successors determine current state. A
  `RETIRED` row carries `retirement_reason`. Legacy rows already marked
  `SUPERSEDED` still require a successor in the packet.
- The producing seat cannot be the reviewing seat.

## Validator ceiling

`validate_analysis_packet.py` checks structure and referential integrity. Its
PASS does not establish source truth, coding fidelity, category quality,
groundedness, sufficiency, saturation, evidence admission, or release.

## Source-bound local workflow

The optional `source-bound-v1` profile adds a frozen INPUT_MANIFEST.json, actual
source/quote hash checks, explicit boundary and comparison consequences,
negative-case response fields, inherited defaults, and previous-cycle byte
preservation. See [workflow.md](workflow.md) for the complete field additions and
commands. `HANDOFF.md` plus SHA256SUMS records submission without editing the
manifest’s historical WORKING state. Neither structure nor byte-binding PASS
establishes analytical validity.
