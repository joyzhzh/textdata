# LLM-annotation workflow

A working prototype that turns passages into candidate actor–action records, checks their quotations and exports source-linked features.

[Worked example](docs/WORKED_EXAMPLE.txt) · [Use with your AI assistant](AI-PROMPT.md)

## Start with the example

Five selected passages from Executive Order 13960 yield **four candidate relations and one no-assignment record**. In section 4(b), the candidate actor is “the Director of OMB (Director)”, the action is posting a roadmap, and the consulted stakeholders are recorded separately.

Read [the walkthrough](docs/WORKED_EXAMPLE.txt), inspect [the feature table](example/output/features.csv), or follow the exact quotations and character positions in [the annotation records](example/output/annotations.jsonl).

Two synthetic errors—substituting stakeholders as the actor and omitting an assignment—both pass the source checks. The prototype checks that quoted words occur in a passage; independent reading is needed to assess their meaning.

## Run the prototype

Python 3.9 or newer, standard library only. From this folder:

    python3 tool/workflow.py export --package example/prepared --response example/candidate/candidate_response.jsonl --receipt example/candidate/producer_receipt.json --out replay-01

Choose a new output folder each time. This replays saved responses without a network or model call. Six output files match the supplied output byte for byte; run.json records the new execution. To run the included software checks:

    python3 checks/verify.py

Expected: exit 0 and "all_ok": true. The checks include both deliberately wrong interpretations; passing is not an accuracy result.

## Files to use

| Entry | Purpose |
|---|---|
| [docs/WORKFLOW.txt](docs/WORKFLOW.txt) | Prepare a package, check responses and export features |
| [example/input/](example/input/) | Source text, study definition, five passages, codebook and annotation instructions |
| [example/prepared/requests.jsonl](example/prepared/requests.jsonl) | Saved requests with the full document as context |
| [example/candidate/](example/candidate/) | Saved model candidates and their production limits |
| [example/output/](example/output/) | Source-linked records, feature table, summary and empty reference-coding form |
| [tool/](tool/) | Preparation and export tools |
| [checks/verify.py](checks/verify.py) | Offline quotation, integrity and replay checks |

## Completed and proposed

Preparation, quotation checks, source-linked export and saved-output replay work on this example. Model calls and an agent skill remain proposed, along with independent reference coding and tests of accuracy and repeatability before scaling.

The candidates were produced interactively by the assistant that built the prototype. The full conversation context and exact model/settings are unavailable. No independent reference labels or accuracy estimate exist. These hand-selected passages illustrate textual assignments, not observed behavior, current legal effect or a population estimate.

## Sources and licences

The official order is a public-domain United States Government work, credited to the Office of the Federal Register, NARA and U.S. Government Publishing Office/GovInfo. [Source details](data/SOURCES.md) and [notices](NOTICE.md) retain attribution and material qualifications. Project code: Apache-2.0. Project-authored documentation and data: CC BY 4.0. Third-party material retains its own status.
