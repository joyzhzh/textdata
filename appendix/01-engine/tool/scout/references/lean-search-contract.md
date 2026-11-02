# Lean search and saturation contract v0.5

Use this contract for `rapid-scout`, `high-recall-map`, and
`systematic-review-ready`. Keep task-specific additions in the task folder,
not in the reusable skill.

## Contents

- Minimum prospective record
- Lightweight ledgers
- Retrieval frames
- Coverage cells and clocks
- Working-plateau reduction
- Claim ceilings
- Escalation rules

## Minimum prospective record

Before the first query, record:

- research question and unit of analysis;
- cutoff, language boundary, and public/licensed source boundary;
- inclusion, exclusion, merge, and evidence-class rules;
- compact concept or mechanism cells plus synonyms and confusion negatives;
- planned retrieval frames and any required sources;
- run type (a literal `run_type:` line so validators can read it), permitted
  claim language, resource ceiling, and allocation;
- marginal-yield threshold `K`, required independent low-yield passes, and
  citation/graph depth; and
- prohibited actions, especially candidate acquisition or execution.

The freeze may be one short Markdown section. Log later vocabulary, route, or
scope additions with time, reason, and affected cells; do not repeatedly
refreeze the campaign.

## Lightweight ledgers

Use JSON Lines so discovery can append records immediately.

### Search log

Each query or graph traversal records:

```text
query_id
frame
cell_ids
source_or_platform
exact_query_or_traversal
started_at
ended_at
filters_and_limits
result_boundary
results_screened = integer | not_available
new_lead_ids[]
updated_work_ids[]
duplicate_count
exclusion_count
unresolved_count
state = complete | partial | blocked
limitation
```

Use `complete` only for an exhausted cursor, last page, finite collection, or
frozen finite window. A visible result count alone is not completion. Never
invent totals that the interface does not expose.

### Screening ledger

Give each plausible named lead one compact row:

```text
lead_id
canonical_label
primary_locator
first_seen_query_id
cell_ids[]
year_or_version
decision = deep-code | context | merge | exclude | unresolved
reason
work_id
duplicate_or_supersession_target
checked_at
```

This is the negative-space memory. A fully developed identity graph is not
required for ordinary exclusions.

### Evidence ledger

Maintain stable `work_id` values across manifestations. A retained row records
the work, aliases, cell assignments, manifestations, screening lineage, and
one or more claim objects:

```text
claim_id
claim
manifestation_id
manifestation_type
exact_locator
observed_at
evidence_class
source_independence
scope
confidence
contradiction_or_parent_claim_ids[]
```

Do not let one manifestation lend publication status, license, metrics, or
empirical support to another without an explicit relation.

## Retrieval frames

Choose frames that differ in source channel or retrieval logic. Typical
options are:

1. terminology, synonym, and exact-title discovery;
2. scholarly metadata indexes and relevant venue/proceedings searches;
3. surveys, handbooks, editorial guidance, or curated-census reconciliation;
4. backward references and forward citations from central seeds;
5. author, maintainer, institution, repository, dependency, or sibling graphs;
6. normative authorities, official documentation, and version/status checks;
7. negative, adverse, null, criticism, and terminology-confusion searches;
8. thinnest-cell, recency, grey-literature, or justified native-language
   backstops.

Tag each search-log `frame` value with a stable frame-id prefix (`F0` for a
zero-credit legacy import, `F1`–`F8` for the options above) so coverage
accounting stays mechanical across sessions and reviewers.

`rapid-scout` uses the few frames needed for representative coverage.
`high-recall-map` normally uses at least three materially different frames and
must include citation or identity-graph traversal when applicable.
`systematic-review-ready` freezes an enumerable source universe and replayable
source-specific strategies.

## Coverage cells and clocks

Cells express the smallest distinctions whose omission could change the
synthesis. Keep them mechanism- or concept-centered rather than attempting an
unbounded census of every application.

Permitted cell states:

```text
unsearched
searched-rich
searched-thin
searched-empty
blocked
not-applicable
```

Track separately:

- **identity/class clock:** time or pass since the last plausible new identity
  or concept/mechanism class; and
- **evidence clock:** time or pass since the last material upgrade,
  contradiction, or current-manifestation correction.

Any plausible new identity or class resets the relevant identity/class clock,
even if later excluded. Keyword variants in one engine are not independent
passes.

## Working-plateau reduction

For a `high-recall-map`:

```text
run planned frames
screen and merge
search thin cells and open graph frontiers

if a new class or plausible identity appears:
    reset the relevant clock
else if the pass is materially independent:
    count its net-new retained yield

stop at working plateau only if:
    every required cell has a disposition
    every planned frame ran or is limited explicitly
    no high-priority unresolved lead or high-yield frontier remains
    two independent post-merge passes add zero new classes
    both passes add no more than K retained identities
```

If the resource ceiling arrives first, stop safely and label the result
`high-coverage, effort-bounded, not saturated`. Never continue merely to force
zero yield.

## Claim ceilings

| Evidence state | Strongest default wording |
|---|---|
| Representative examples or capped search | `rapid representative scout; no recall claim` |
| Multiple frames, screened ledger, incomplete stop evidence | `systematic/multi-route effort-bounded map` |
| High-recall stop reduction passes | `high-coverage map searched to a working plateau` |
| Resource ceiling with positive tail | `high-coverage snapshot; not saturated` |
| Enumerable source universe, prospective recall tests, duplicate review, and independent search review pass | `systematic-review-ready inside the declared envelope` |

No open-web procedure proves an unknown complete universe. PRISMA-style
reporting, manifests, and valid schemas improve transparency; they do not
upgrade recall by themselves.

## Escalate only when the claim requires it

Add the following only for `systematic-review-ready` or an explicit
high-stakes request:

- preserved raw database exports and complete result windows;
- prospective known-item sentinels or a blinded holdout family;
- duplicate title/abstract screening and claim extraction with adjudication;
- formal source-flow reconciliation and quality appraisal;
- independent search-strategy review or different-vendor recall challenge;
- multilingual lanes beyond the justified task boundary;
- source snapshots, builds, runtime tests, or recurring living-review
  infrastructure under separate authority.

Capture-recapture is at most a warning diagnostic when channel-independence
and equal-catchability assumptions are defensible. It is never a completeness
certificate.
