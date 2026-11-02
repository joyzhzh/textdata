# Data and source bindings

The [analytical packet](../example/input/study/snapshots/C003/) contains episodes, incidents, codes, comparisons, category versions, memos and proposed sampling requests from 22 interviews. Incident descriptions are analysts’ paraphrases; quotations are represented by their fingerprints. Source accounts are credited in [NOTICE.md](../NOTICE.md).

The transcripts are not included, and no redistribution right is claimed. A reader holding the same files can compare `shasum -a 256 "<transcript file>"` with each source’s `sha256` in `INPUT_MANIFEST.json`. Each incident’s `source_ref` gives its one-based, inclusive line span; `quote_ref` gives the quoted-line fingerprint where applicable.

The seven analytical row files match the original seal. The two manifests are redacted derivatives, identified in `RELEASE_DERIVATION.json`; `RELEASE_SHA256SUMS` covers the current packet. The original handoff, which reprinted the rows, is retained privately.

The historical `NON_RELEASE` and saturation `NOT_ASSESSED` labels mean the analysis was not admitted as established findings and saturation was not assessed. Short transcript overlaps and fragments remain third-party material, excluded from the project licence; see [NOTICE.md](../NOTICE.md).

The [synthetic example](../tool/examples/synthetic/) is wholly invented and self-contained. It exercises the software and is not empirical evidence.
