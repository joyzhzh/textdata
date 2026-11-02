---
name: "lean-scout"
description: "Run calibrated SOTA, literature, repository, and adjacent-artifact scouts. Use for a representative landscape, high-recall evidence map, systematic-review-ready search, exact identity/license lookup, or explicitly authorized immutable-artifact preservation. Starts discovery early, screens breadth before deep coding, tracks identities, provenance, and marginal yield, and prevents validation machinery from displacing the research."
---

# Scout skill v0.5.2 — Lean Draft Beta

Produce a useful evidence map whose claims remain honest under review. This
revision is a supervised operational draft, not `eval-green`, integrated, or
ratified. The v0.4 schemas and validators remain available for explicitly
selected advanced or preservation work; they are no longer the default path
for an ordinary SOTA scout.

## Protect research time

Begin real discovery as soon as safety, authority, scope, and a minimal search
contract are clear.

- Cap pre-discovery setup at one pass, one repair attempt, and normally 10% of
  the declared campaign budget or 20 minutes, whichever comes first.
- Reserve at least half of the campaign for discovery, screening, and
  evidence inspection; use 60% as the default allocation.
- Do not build a custom schema, validator, ontology package, audit package, or
  preservation system when a small ledger is sufficient.
- Do not let an optional deliverable, software lane, package-integrity defect,
  or unavailable reviewer block unrelated core outputs.
- Stop only for a safety, authority, destructive-action, source-integrity, or
  scope defect that could invalidate the research. Record and isolate lesser
  defects, lower the affected claim, and continue.
- If no real query has run by the setup ceiling, stop the setup loop and
  report the blocker. Never begin an audit of an audit before discovery.

## Select the smallest valid run type

Freeze one type before searching:

| Run type | Use | Permitted coverage language |
|---|---|---|
| `bounded-lookup` | One identity/license question or a finite named shortlist | `no-claim` |
| `bounded-preservation` | One named immutable artifact under an explicit grant | `no-claim` |
| `rapid-scout` | Representative examples or a quick landscape | `representative; not recall-oriented` |
| `high-recall-map` | Default for SOTA, state-of-the-art, comprehensive-oriented, or mechanism-landscape requests | `high-coverage, effort-bounded map as of <date>` |
| `systematic-review-ready` | Explicit systematic/exhaustive/high-stakes review with sufficient access, time, and reviewers | Only the strongest label whose recall gates actually pass |

The word “SOTA” does not force `systematic-review-ready`. Choose
`high-recall-map` unless the user explicitly requests systematic-review-grade
conduct or a closed/completeness claim. Treat a living update as a versioned
rerun of the selected type, not as mandatory monitoring infrastructure.

## Load only what the run needs

- For `rapid-scout`, `high-recall-map`, or `systematic-review-ready`, read
  `references/lean-search-contract.md`.
- For `bounded-preservation`, read `references/artifact-contract.md` and use
  the preservation schema, template, and inventory validator.
- Read `references/legacy-migration.md` only when importing old evidence.
- Read `references/source-adapters.md` or `references/evidence-scoring.md`
  only when their routes or rubric fit the task.
- Load `matrix-schema.md`, `readiness-and-freeze.md`,
  `evidence-state-contract.md`, the v0.4 campaign schemas/templates, and
  `validate_campaign.py` only when the user explicitly
  selects the legacy full-matrix package or the run genuinely needs
  `systematic-review-ready` assurance. They are not discovery prerequisites
  for rapid or high-recall work.

## Freeze the minimum contract, then search

Record only:

1. question, unit of analysis, cutoff, language boundary, run type, claim
   ceiling, and resource ceiling;
2. inclusion/exclusion rules plus a compact concept lattice, mechanism
   families, synonyms, and known confusion negatives;
3. planned source and retrieval frames;
4. evidence classes and any inspection/execution/acquisition prohibition; and
5. the stop rule, low-yield threshold `K`, and citation/graph depth.

Start an append-only deviation log (a `SCOPE.md` section by default) and the
lightweight search and screening ledgers defined in
`lean-search-contract.md`. Add newly discovered vocabulary without silently
changing frozen meanings. Do not wait for deep-code fields, final schemas, or
a complete candidate ontology before running the first query.

Within the same setup ceiling, one session that did not author the scope
reviews the frozen items once — question translation, cells, frames,
synonyms, confusion negatives, and claim ceiling — and its dispositions land
in the deviation log. This review is part of the single setup pass, never a
reason to add one.

## Search breadth before coding depth

1. Run the planned orthogonal frames: scholarly indexes, venues or authority
   catalogs, surveys/bibliographies, primary repositories/documentation,
   backward/forward citations, author/maintainer graphs, current-version
   checks, and negative/confusion searches as relevant.
2. Log the exact query, source, time, limits, boundary, screened count or
   `not_available`, yields, failures, and newly opened leads.
3. Give every plausible named lead a lightweight disposition. Preserve
   duplicates, superseded works, exclusions, blocked items, and unresolved
   leads instead of rediscovering them later.
4. Resolve stable work identities separately from manifestations such as
   preprints, journal articles, repositories, releases, datasets, or
   standards versions.
5. Screen broadly first. Deep-code only retained or synthesis-relevant
   records; never make a large fixed field schema the price of discovering
   the field.
6. Attach substantive statements to claim-level evidence objects with exact
   locators, manifestation, observation date, evidence class, independence,
   scope, and confidence. Adjudicate contradictions rather than averaging or
   silently merging them.

Reading scholarly full text is evidence inspection, not candidate-code
acquisition. Do not download, install, import, build, execute, or preserve
candidate software/data unless separately authorized.

## Use parallelism as a recall instrument

- Use one primary search and at most two focused discovery lanes by default.
  Every pre-synthesis lane must search or screen; do not spend a slot building
  ancillary infrastructure.
- Give lanes different source channels or retrieval logics. Freeze their
  initial captures before list-sharing when overlap is being measured; do not
  require elaborate sibling-blind filesystems for an ordinary high-recall
  map.
- Merge after the primary first pass, then aim residual searches at thin
  cells, unresolved leads, and lane-unique vocabulary.
- Same-vendor lanes are diversified searches, not independent validation.
- Start independent QA only after a substantive corpus exists. Run one
  bounded correction pass for ordinary high-recall work; escalate further
  only for a material research defect or an explicitly selected systematic
  tier.

## Stop honestly

For `rapid-scout`, stop at the frozen resource ceiling or when the requested
representative set is sufficient.

For `high-recall-map`, stop at a working plateau only when:

1. every required concept/source cell has a searched, thin, empty, blocked,
   or not-applicable disposition;
2. every planned retrieval frame ran or has a recorded limitation;
3. no high-priority unresolved lead or open high-yield citation/identity
   frontier remains;
4. two materially independent post-merge passes add no new mechanism or
   concept class and no more than the predeclared `K` net-new retained
   identities; and
5. a newly discovered class or plausible identity resets the relevant stop
   clock.

This is a one-sided working-plateau test, never proof of exhaustiveness. If the
resource ceiling arrives while material yield remains positive, complete the
run as `high-coverage, effort-bounded, not saturated`. That is a valid outcome.

Add frozen source-universe exports, prospective sentinel/holdout tests,
duplicate screening/extraction, formal flow reconciliation, independent
search review, and different-vendor recall review only for
`systematic-review-ready` claims. A pending different-vendor review does not
block an honestly labelled effort-bounded map.

## Validate two gates, once

Report separately:

- **Artifact gate:** required files readable, JSONL parseable, IDs unique,
  counts reconciled, evidence locators present, final files read back, and a
  final manifest valid when required.
- **Coverage gate:** planned cells/routes accounted for, yields and unresolved
  leads visible, stop rule recomputed, and narrative label no stronger than
  the evidence.

Run `scripts/validate_lean_bundle.py <bundle-dir>` for the artifact gate and
the claim-language ceiling; it fails closed on unparseable ledgers, duplicate
IDs, broken screening-to-ledger lineage, and wording stronger than the
declared run type permits. Mid-campaign, run it with `--partial`: files not
yet written are skipped as INFO and every check whose inputs exist still
runs. On a passing full run it prints `bundle_sha256` — the bundle hash of
record, quoted in RETURN lines and acceptance rows so producer and acceptor
name the same bytes. The coverage gate stays a reported judgment — no
script proves recall. When coverage or negative findings will support a paper
claim, a freeze decision, or a go/no-go, a session that did not produce the
corpus re-runs the coverage gate before that use; same-vendor is acceptable
below `systematic-review-ready`.

Hashes prove bytes, not recall. Run final validation after substantive search,
then permit one ordinary repair pass. A defect confined to an optional
artifact lowers only that artifact or claim; it does not restart the campaign.

## Keep the default bundle compact

An ordinary scout needs only:

1. `SCOPE.md`, including a literal `run_type:` line and the append-only
   deviation log;
2. `SEARCH_LOG.jsonl`;
3. `SCREENING.jsonl`;
4. `EVIDENCE_LEDGER.jsonl`;
5. `FINDINGS.md`, including limitations and the stop decision; and
6. one final checksum manifest when repository policy requires it.

Add a separate coverage matrix, dual-review ledgers, raw exports, frozen
receipts, or preservation inventory only when the selected tier needs them.
Artifact count is never a recall metric.

## Run bounded modes without campaign machinery

For `bounded-lookup`, freeze the finite question and routes, resolve stable
identity and manifestation/version, record each attempt and limitation, and
deliver the evidence locator plus `coverage_claim=no-claim`. Do not acquire
bytes.

For `bounded-preservation`, freeze one immutable manifestation, destination,
expected identity/hash when available, artifact-specific grant, allowed
static actions, and prohibited actions. Follow `artifact-contract.md` and the
inventory validator. Treat bytes as `acquired-unverified` until typed static
checks, SHA-256, byte count, and destination read-back pass. Never infer corpus
coverage from a successful preservation.

## Preserve hard boundaries

- A score, citation count, checksum, or repeated claim cannot establish
  identity, independence, license, authority, execution, or coverage.
- No exact manifestation-scoped compatible license evidence means no
  preservation eligibility.
- No exact grant covering the immutable artifact, allowed actions, and
  writable root means no acquisition.
- Unknown is never zero; blocked or capped search is never complete.
- Do not claim `comprehensive`, `exhaustive`, `complete SOTA`, or `saturated`
  unless the corresponding prospective gates passed.
- Do not call this skill ratified without fresh evaluation, positive
  different-vendor validation where required, registration, and researcher
  ratification.
