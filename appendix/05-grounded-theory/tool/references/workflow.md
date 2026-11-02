# Running a bounded local cycle

Use `scripts/analysis_cycle.py` from this skill directory. It invokes no model,
network service, contact or source acquisition. Codex performs the interpretation
and writes proposed rows; the helper preserves bytes and checks declared links.
Use a Python 3.9+ interpreter with `jsonschema` (the existing validator dependency).
The installed skill is a link to its durable Git checkout; source HEAD and a
runtime-tree SHA-256 are recorded, so uncommitted implementation bytes are not
misrepresented as the HEAD commit alone.

## Authorized input configuration

Choose a new study directory outside every Git checkout. It must contain no
nested checkout. `.vault-root` is a machine-local pointer to the study parent,
not permission to inspect every study. Commands use an explicit study root.
For real data, use only the user's bounded authorized inputs and existing
applicable authority. `AUTHORIZED_REAL` records a decision; it does not make it.

Create `input-config.json` in that study, using this shape. This example is
synthetic; substitute the actual recorded authority and paths only for an
explicitly authorized study. Omitted source `sha256` values are computed during
prepare; supplied values must match. Source paths must resolve inside the study.

```json
{
  "study_id": "SYNTHETIC-STUDY",
  "data_kind": "SYNTHETIC",
  "authority_ref": "SYNTHETIC-EXAMPLE-ONLY",
  "license": "SYNTHETIC_GENERATED",
  "rights": "Wholly invented input",
  "privacy": "No real people or private information",
  "retention": "VAULT_ONLY",
  "model_processing": {"authority_ref": "SYNTHETIC-EXAMPLE-ONLY", "models": []},
  "sources": [{
    "manifestation_id": "MNF-SYNTHETIC-001", "path": "trace.txt",
    "kind": "NORMALIZED_TEXT", "language": "en",
    "rights": "Wholly invented input", "source_url": "synthetic:trace"
  }]
}
```

For a real licensed dataset also record its name, source URL, license identifier,
license-file hash and retrieved snapshot hash, as applicable to the actual
ruling. If `license` is `UNKNOWN`, `unknown_license_authority_ref` must name an
explicit allowance. C001 uses `GT-RULING-2026-09-02-05R`; do not reuse it for other
data. Revised C001 rulings allow normalized text/event exports for recorded cloud
model processing, keep raw media and outputs in the vault, and retain minimization.
Jurisdiction, institutional, provider/platform and release matters outside those
rulings remain open. This implementation does not ingest or pilot that dataset.

List exact processing models in `model_processing.models`; an empty list means
no model processed study data. A normalized source may include `derived_from`:
an array of `{ "path", "sha256", "transformation" }` objects pointing to retained
raw/preceding bytes inside the study. The helper verifies the predecessor hashes;
it cannot establish that the transformation is faithful. `RAW` source entries
can record custody, but source/quote locators used by this helper must bind
`NORMALIZED_TEXT`. No automatic audiovisual extraction is implemented.

## Prepare and append

Run the following with resolved absolute paths and the actual seats/question:

```bash
python3 -B <skill-dir>/scripts/analysis_cycle.py prepare \
  --study-root /absolute/study --config /absolute/study/input-config.json \
  --cycle C001 --question 'The frozen study question' \
  --producer producing-seat --reviewer designated-independent-reviewer
```

This creates the existing eight-file packet plus a frozen `INPUT_MANIFEST.json`.
An existing cycle is refused. The source-bound workflow extends schema
`0.2-phase-a` with `workflow_profile: source-bound-v1`; legacy packets still get
structure-only checks with `validate_analysis_packet.py`.

Write a proposed JSONL batch outside the cycle, then append it:

```bash
python3 -B <skill-dir>/scripts/analysis_cycle.py append \
  --cycle /absolute/study/C001 --file incidents --rows /absolute/study/new-incidents.jsonl
```

`--file` accepts `episodes`, `incidents`, `codes`, `comparisons`, `categories`,
`memos`, or `sampling`. Append dependencies first in that order. The whole proposed
packet is checked in memory before any row bytes are appended. Failed proposals
leave existing rows intact. Use fresh IDs and explicit supersession to revise a
row; duplicated identities, forks and missing predecessors are rejected.

## Fields to make analytical decisions inspectable

Core row shapes are in the existing schemas and [packet contract](analysis-packet-contract.md).
The source-bound profile additionally requires:

| Row | Additional fields and their use |
|---|---|
| Episode | `intended_outcome`; `boundary.start_ref`, `end_ref`, `ending`, `event_order`, `missingness`. An endpoint ref contains manifestation_id and locator. Ending is OUTCOME_OBSERVED, TRACE_ENDS or MISSING_INTERVAL; the latter two require UNKNOWN. Event order is SOURCE_ORDER, RECONSTRUCTED or UNCERTAIN. Record event/presentation times and their uncertainty when known; do not invent them. |
| Source/quote ref | `locator: "lines:1-3"` means one-based inclusive lines of the bound normalized UTF-8 source. Quotation hashes use those lines joined by LF, excluding the final line terminator. Inspect the span before classifying it. |
| Creator-stated interpretation | Existing source_ref and quote_ref plus `attribution_basis: "CREATOR_STATEMENT"`. A BEHAVIOR_ONLY basis is refused. Exact quote matching does not prove that the statement supports the interpretation; review must inspect it. |
| Code/translation | Keep source-near label and incident_ids. Add original_language, working_translation, alternative_reading and translation_rationale when translation affects interpretation; original wording is recovered from the incident source ref. Gerund preference stays operative. |
| Comparison | Existing fields plus nonempty `purpose` and `analytical_consequence`; state why this contrast changes or bounds the analysis. |
| Category version | Explicit arrays `properties`, `dimensions`, `conditions`, `consequences` (empty when unknown), alongside definition, not_this, support, comparisons and rivals. |
| Negative case | `negative_case_response` with action REVISE/SPLIT/BOUND/RETIRE/RETAIN_WITH_REASON/UNRESOLVED, reason and discriminating_evidence. REVISE/SPLIT/BOUND must name a predecessor and actually change definition, boundary, properties/dimensions or conditions/consequences. RETIRE requires RETIRED status and retirement_reason. These are design adaptations, not a universal methodology taxonomy. |
| Sampling | `expected_observations.supports`, `.challenges`, `.decision_if_missing`. Opposing predictions must differ; status stays PROPOSED. A schema cannot judge their substantive discriminating power. |

## Hand off and continue

Write an analysis account outside the cycle stating support, rivals, negative
cases, uncertainty, missing contrasts and the next discriminator. Create a local
review handoff and exact byte seal:

```bash
python3 -B <skill-dir>/scripts/analysis_cycle.py handoff \
  --cycle /absolute/study/C001 --analysis /absolute/study/analysis.md \
  --stop-reason 'Bounded cycle complete; named contrasts remain unresolved' \
  --stop-status NOT_REACHED
```

`HANDOFF.md` embeds the current analytical view and labels it SUBMITTED_FOR_REVIEW;
`SHA256SUMS` binds the files. The frozen manifest's WORKING value is historical;
the sealed handoff records the submission state without rewriting it. A reviewer
must still assess the source passages and reasoning. No message is sent.

```bash
python3 -B <skill-dir>/scripts/analysis_cycle.py continue \
  --previous /absolute/study/C001 --cycle C002 \
  --producer producing-seat --reviewer designated-independent-reviewer
python3 -B <skill-dir>/scripts/analysis_cycle.py validate --cycle /absolute/study/C002
```

Continue copies sealed history into a new cycle. New rows supersede old IDs
without editing their historical status. Optional `--config` can bind an expanded
authorized input set; all prior manifestation IDs/hashes must remain. New bytes
need new manifestation identities. Sealed-history tampering and altered copied
prefixes are rejected. Direct manual edits to an unsealed first cycle cannot all
be detected by a schema; use the append helper and preserve sealed milestones.

## Synthetic demonstration

```bash
python3 -B <skill-dir>/examples/synthetic/workflow.py --output /absolute/new-synthetic-study
```

The destination must not exist. The example creates four invented endings
(accepted, transformed, abandoned, unknown), source-linked incidents/codes, four
memo types, and a second cycle that narrows a category after counterevidence.
It includes a PROPOSED discriminating sampling request and two sealed handoffs.
No real dataset or model is used. Test directories are retained under the local
no-permanent-deletion policy; no destructive cleanup is performed.
