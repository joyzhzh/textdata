# Reference and corpus assistance

## Inspect the inventory at its stated scope

Use user-supplied records or an explicitly authorized existing reference map. An index is a navigation aid, not a count of independent works or a blanket permission to open every linked object. Respect excluded and frozen paths without reading or hashing them. Inspect permitted metadata first; keep inaccessible or undecided items visible. Do not follow credential-bearing or restricted routes to fill gaps.

For each item relevant to the question, distinguish:

| Object or state | What to retain |
|---|---|
| Work hypothesis | Stable local work ID, recorded citation/identifier, identity confidence and unresolved alternatives. A title or DOI alone does not prove byte or version identity. |
| Manifestation | Separate ID, kind (publisher PDF, manuscript, provider text, abstract, metadata, image, etc.), version/capture event, retained path or locator, inspected coverage, hash and declared hash basis when available. |
| Derivation | Parent manifestation, parent hash/basis, extraction method/version/options and derivative hash; whether replay actually occurred. A hash of extracted text does not verify its parent PDF. |
| Assertion provenance | Who asserted a citation, status or relationship, from what source, and when; separate from who created the work or added the entry. |
| Corpus decision | Candidate/admitted/undecided/excluded, collection-specific role, decision author/date/reason, permitted local use and residual uncertainty. Ingestion or parsing cannot choose admission. |
| Access and source status | Available/partial/blocked/unattempted/unknown separately from reported correction, concern, retraction, withdrawal or unknown; retain the status source/date without overwriting eligibility. |
| Permissions | Per-manifestation access/retention/local processing, quote or other reuse, participant consent/data-use limits, evidence for each and unknowns. Article licences do not settle participant permissions. |

Use `unknown` (or `null` with a reason) for unreported values. Use `not_applicable` only with a reason. An observed zero needs a unit, scope and actual check. A rival reference deserves its own item; it need not be folded into the entry it disputes.

## Resolve identity without losing alternatives

Show candidate links with precise types: `possible_same_work`, `version_of`, `derived_from`, `quotes`, `revises`, `cites`, `contradicts`. Do not turn these into `same_as`. Two rows, manifestations or excerpts from one source family are not independent corroboration.

If a human resolves identity, record author, time, reason, affected IDs and the evidence. Retain the predecessor record and all unrelated fields. A successor points to a predecessor hash with its basis (whole-file bytes, exact line bytes, or a precisely specified object serialization); never substitute one basis for another. If a provided hash basis is ambiguous, preserve that ambiguity and defer the identity assertion. A local quotation check requires a separate whole-file binding for its text input; [quote-check.md](quote-check.md) explains first-use hashing and the reference-entry mapping.

## Propose maintenance

Use the maintenance section of the [templates](../assets/working-templates.md). The result is a dry proposal, not a filesystem action. List item-level source/target identities, intended effect, expected byte/hash bindings, restrictions, decision needed and a recovery approach. Creating a navigation index beside existing files is often sufficient; do not copy restricted captures into it.

If the user later commissions execution, it is separate work outside this package's helper: bind the precise approved plan by whole-file hash, recheck preconditions, avoid occupied targets and record each observed outcome. A multi-item action is not one transaction. On partial failure retain the exact completed/pending/failed/unknown items and prepare a successor recovery plan; do not retry an uncertain action blindly. Neither a plan nor an execution receipt changes admission, release or deletion authority. Never propose agent deletion, replacement of originals, or a cleanup disguised as deduplication.

## Return

Give a small reference table or map with independent state columns and the useful next checks. Include unresolved version matches and inaccessible/unused objects. Preserve restrictions in every derived view. Do not pool grouped citations into a unique-work total until identity decisions support it; a library can be helpful without claiming exhaustive coverage.
