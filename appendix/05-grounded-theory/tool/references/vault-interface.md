# Vault and paper interface

## Sampling request to evidence vault

The grounded-theory tool sends one `SAMPLING_REQUESTS.jsonl` row that
conforms to [schemas/sampling-request.schema.json](../schemas/sampling-request.schema.json):
request ID, provisional focus and the packet identities it rests on,
discriminating question, targets (`SUPPORT`, `CONTRADICTION`, `BOUNDARY`,
`RIVAL`, `NEGATIVE_CASE`), eligible source classes, languages, date range,
creators, workflow regimes, restrictions, counter-search, resource ceiling,
stop rule, claim ceiling, and required return fields. The vault cites the same
schema by hash; shared terms are in
[vocabulary-crosswalk.md](vocabulary-crosswalk.md).

This is a proposal, not acquisition authority. Only a status of `PROPOSED` may
be written by the tool; every later status names its `authority_ref`.

## Evidence return

The evidence vault returns an immutable package lock with:

- the `request_id` it answers;
- exact vault snapshot and package-manifest hash;
- the lane handoffs it projects, each bound by the hashes of the protocol's
  `records.jsonl`, `report.md`, and `searchlog.md`;
- source and manifestation IDs and hashes;
- episode/event IDs, locators, and epistemic classes;
- quotation, translation, rights, privacy, and access state;
- source-lineage and deduplication state;
- negative cases, limitations, and unknowns; and
- status: `SUBMITTED_FOR_REVIEW`, `UNADJUDICATED`, `NON_RELEASE` unless a
  later independent record says otherwise.

Discovery snippets and generic summaries do not cross as evidence. Sharing
bytes and provenance does not share conclusions, category membership,
admission verdicts, saturation judgments, or publication authority.

## Paper handoff

A claim-bearing handoff must bind only current, independently admitted records
whose use is compatible with rights, privacy, quotation, translation, and
access restrictions. It includes construct boundaries, rivals, negative cases,
claim-to-record bindings, falsifiers, unresolved questions, and exact claim
ceilings.

Drafting, acceptance, release, and publication are separate decisions. A
fresh release auditor must inspect the exact draft surface.

## Paper drafting

`draft-paper` requires a frozen charter and a separately authorized author
seat. It consumes only the immutable adjudicated `GT_LITE`, current admitted
record bindings, and approved author-framing instructions. Each substantive
sentence maps to a current claim ID; author framing is visibly distinct. The
draft status is `DRAFT_NON_RELEASE`.

The author may not retrieve new evidence, revive superseded records, infer a
creator belief from behavior, strengthen a claim beyond its ceiling, declare
saturation, or authorize submission/publication. A correction to evidence or
analysis invalidates downstream draft bindings until they are replayed.
