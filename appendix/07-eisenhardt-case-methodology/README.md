# Eisenhardt Case Methodology

[Explore the webpage](https://textdata.info/toolkit/eisenhardt-case-methodology/) · [Use with an AI assistant](AI-PROMPT.md) · [All components](../README.md)

A method map, a reference collection and a working maintenance skill support preparation for case-based theory building. The software preserved research materials during a documented reorganization. Case analysis remains proposed.

## Explore the work

- **Method map:** [METHOD_MAP.md](docs/METHOD_MAP.md) explains eight phases, from defining a puzzle to communicating a theory, with source notes and material qualifications. For example, theoretically useful similarities support replication across cases; differences can challenge an emerging explanation.
- **Reference collection:** [data/r12/](data/r12/) contains 22,856 candidate-reference records in CSV and JSONL, plus 20,732 unique DOIs. Records are not distinct papers; duplicates or versions may remain. [Field definitions](docs/data-fields.md) explain screening labels and metadata qualifications.
- **Maintenance prototype:** [tool/SKILL.md](tool/SKILL.md) and four scripts inventory, plan, apply and verify workspace changes, and export the reference collection. The analytical steps of case selection, within-case analysis, cross-case analysis and theory development are not implemented.

## Run the illustrative example

Python 3.9 or newer; standard library only. No network or model is needed. From this folder:

```bash
python3 example/run_example.py
```

The example copies two synthetic packages into a temporary workspace, seals a move plan with a checksum, applies the approved plan and verifies the result. Expected output: `all_as_expected: true`, two renames, two relative links, zero copies and zero deletions. It refuses missing or incorrect approval, a changed plan, added-file drift and re-application.

Inspect the retained [summary](example/output/SUMMARY.json) and [refusals](example/output/04-refusals.json), or follow the [AI prompt](AI-PROMPT.md) to explore them. This is an executable preparation example, not a demonstration of theory building.

```bash
python3 checks/run_checks.py
```

Expected: `all_pass: true`. The offline checks cover the collection's counts and hashes, the 19 software tests, example replay, method-map rendering and the folder manifest.

## Material limits

The map is a bounded interpretation, not a systematic review. Collection labels are screening judgments, not proof that a paper follows the method. The exporter requires a private source ledger; the shipped collection can be checked but cannot be regenerated here.

Moves are sequential, not transactional. A partial failure requires inspection before recovery. Aggregate snapshots and selected hashes can miss same-size changes; the workspace must not change during application. Tests and one real maintenance use do not validate research quality or general agent control.

## Sources and licences

The method builds on [Eisenhardt (1989)](https://doi.org/10.5465/amr.1989.4308385) and [Eisenhardt (2021)](https://doi.org/10.1177/1476127020982866). Cited works are not included.

Project code is Apache-2.0; project-authored documentation, annotations and compilation are CC BY 4.0. Third-party metadata retains its source terms. Field-level provider provenance is incomplete; this is not proof that each unmatched title or link is restricted. See [NOTICE.md](NOTICE.md) for source credit and the remaining API-terms qualification.
