# Release modifications

This edition retains the toolkit’s analytical workflow and the interview study’s analytical rows. Project-identifying schema addresses, archive paths and private-project wording were replaced with neutral values. Two synthetic revision values are schema-valid zero placeholders. Private project files and their 11 tests are omitted; the earlier release retained 50 runnable tests.

The 4 November 2026 correction replaces website schema addresses with neutral URNs and makes new cycles use a content-derived `snapshot-sha256:<hash>` tool revision. The same runtime hash remains in `tool_tree_sha256`; no Git history or Git executable is required for tool identity. Historical cycle revisions and the original study seal are unchanged. Three identity tests bring the current suite to 53 tests. Local documentation replaces the manifest’s website link.

The seven analytical JSONL files match their original seal. The input manifest replaces private archive addresses while preserving all 22 transcript hashes. The cycle manifest withholds two machine paths. `example/input/study/snapshots/C003/RELEASE_DERIVATION.json` identifies those two derivatives; `RELEASE_SHA256SUMS` verifies the current packet. The original `SHA256SUMS` is retained for provenance, including the handoff kept privately because it duplicates the row files.

The released toolkit does not reproduce the historical runtime-tree fingerprint. The schema fingerprint in `tool/references/vocabulary-crosswalk.md` identifies its original version, before neutralized metadata. Neither is a claim about current file bytes.

Public explanations are condensed for the proposal; development diaries and duplicate handoff material are retained privately. Source qualifications, analytical rows, fixed counts and required attributions are preserved.
