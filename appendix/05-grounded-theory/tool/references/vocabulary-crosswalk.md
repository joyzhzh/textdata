# Vocabulary crosswalk — grounded-theory ↔ companion evidence vault

The tool repository and the evidence vault model different objects: the vault
describes what a source shows; the tool analyzes it. Their vocabularies are
therefore unified only where the concept is the same and cross-walked where it
is not. Nothing in this page maps automatically; a mapped value is an
analytical judgment recorded in the cycle.

**Vault revision observed:** the companion evidence-vault repository (revision withheld for review)
(package schema `0.3-phase-a`: unified `boundary_basis`, `request_id` and
`request_sha256` on the package, `lane_handoffs` binding the protocol's
three-file worker handoff, and `conflicts_with` on records).

## Unified terms

| Concept | Value set | Where |
|---|---|---|
| Episode boundary basis | `SOURCE_EXPLICIT`, `RECONSTRUCTED`, `UNCERTAIN` | tool `episode.schema.json`; vault `episode.schema.json` |
| Workflow regime | `SEQUENTIAL_DECOMPOSED`, `HYBRID_TRANSITION`, `DIRECT_JOINT`, `UNKNOWN_OR_INSUFFICIENT` | vault `TEMPORAL_REGIMES.md` owns the definitions; the tool's sampling request cites them verbatim |
| Manifestation identity | `MNF-…` | minted by the study vault; both repositories cite it |
| Evidence classes | `OBSERVED_ACTION`, `CREATOR_REPORTED_ACTION`, `CREATOR_STATED_INTERPRETATION`, `THIRD_PARTY_INTERPRETATION`, `TECHNOLOGY_COMPANY_CLAIM` | identical in both; the tool adds `ANALYST_INFERENCE` and `THEORETICAL_CONSTRUCT`, which never appear in a vault package |

## Episode outcome crosswalk

The vault records a descriptive outcome; the tool records the creator's
disposition toward the intention. Where a cell says no default, the analyst
decides from incidents and records the basis in a descriptive memo citing the
episode.

| Vault `outcome_status` (descriptive) | Tool `outcome_status` (analytical) | Condition |
|---|---|---|
| `SUCCESS` | `ACCEPTED` | only when acceptance is observed or creator-stated; a descriptive success is not acceptance |
| `PARTIAL_SUCCESS` | no default | `ACCEPTED`, `TRANSFORMED`, or `UNKNOWN` from incidents |
| `COMPROMISE` | `TRANSFORMED` | when the intention changed to fit the realization; otherwise no default |
| `SUBSTITUTION` | `SUBSTITUTED` | |
| `DECOMPOSITION` | `DECOMPOSED` | |
| `POSTPONEMENT` | `POSTPONED` | |
| `ABANDONMENT` | `ABANDONED` | |
| `UNKNOWN` | `UNKNOWN` | never upgraded without new incidents |

## Identity prefixes

| Repository | Prefixes |
|---|---|
| vault | `SRC-`, `MNF-`, `EPI-`, `EVT-`, `QTE-`, `PKG-`; records `ACE-M##-L##-R001`–`R010` |
| tool | `E###`, `I###`, `CDE###`, `CMP###`, `CAT###`, `MEM###`, `MEMO###`, `REQ###`, cycles `C###` |

A tool episode may carry `derived_from` naming the vault `PKG-` package and
the `EPI-` episodes it was reconstructed from; a tool incident may carry
`derived_from_event_id` naming the vault `EVT-` event. These links preserve
the chain; they do not import the vault's descriptive outcome or ratings.

## The sampling request

One schema, owned here and cited by the vault:

- path `schemas/sampling-request.schema.json`
- SHA-256 `da81ae28ee4444c9b4ca4ba9e845dea49433319b53b5861b39bc22a1f4d98c09`

Status flow: the tool writes `PROPOSED`; the vault researcher's fire decision
sets `AUTHORIZED` with an `authority_ref`; the vault's package sets `RETURNED`
with `returned_package_id`; the reviewing seat sets `CLOSED`. Every step past
`PROPOSED` names its authority. An `ACE-M04` lane in the vault must bind to
exactly one request by `request_id`.

## What does not cross

Discovery snippets, Scout scores, star counts, ratings, category membership,
codes, memos, saturation language, admission verdicts, and publication
authority never cross in either direction.
