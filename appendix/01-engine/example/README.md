# Worked example: from a source to a synthesis

This evidence map examines published methods and reusable software for building organization and management theory. It contains 77 works, 101 inspected source versions and 141 claims with exact locators.

## Follow one source

1. In `campaign/EVIDENCE_LEDGER.jsonl`, find `work-doi:10.5465/amr.1999.2553248`: Langley’s 1999 article on theorizing from process data. The inspected version is the publisher abstract.
2. Read `clm-grf-005-01` and `clm-grf-005-02`. They concern the different kinds of theory yielded by analysis strategies, the value of combining strategies, and the continuing need for a creative leap. Each claim names its supporting passage and is limited to abstract-level evidence.
3. In `campaign/SYNTHESIS.md`, open “Theory mode must be chosen before machinery.” Both claims support that design recommendation.

The [web demonstration](https://textdata.info/engine/) makes the same links interactive. The evidence supports a design proposal; it does not validate an automated theory builder.

## Run the checks

From `appendix/01-engine/`, with Python 3.9 or later:

```sh
python3 checks/verify_campaign.py
python3 tool/scout/scripts/validate_lean_bundle.py example/campaign
```

The first command checks the fixed counts, file hashes, source links and worked trace. The second validates the supplied bundle’s structure and permitted claim language. Both run offline without a model. `SHA256SUMS` identifies this public edition; it is not a byte-for-byte copy of the private working record.

## Data and limits

`EVIDENCE_LEDGER.jsonl` holds the final work, version and claim records. `FINDINGS.md` reports the literature findings; `SYNTHESIS.md` develops their design implications. The validator also needs `SCOPE.md`, `SEARCH_LOG.jsonl` and `SCREENING.jsonl`; these retain the question, search boundaries and inclusion decisions needed to check the example.

The search is effort-bounded, English-primary, public-access and not saturated. Most evidence comes from abstracts or public documentation; no candidate software was installed or run. All 76 deep-coded works have evidence entries; the 77th work is a context source. Nine search-log work-update references have no evidence entry and are not additional claim-bearing works. All 141 claim-to-version references resolve. A passing validator does not establish complete coverage or correct interpretation of every source.
