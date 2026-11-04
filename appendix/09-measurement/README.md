# Combining ML, NLP and LLMs

[Offline catalogue](docs/catalogue/index.html) · [Explore with your AI](AI-PROMPT.md) · [All components](../README.md)

A working methods catalogue and measure-card validator help specify a measurement before scoring text. The catalogue connects 14 method families, 35 application settings and 61 research questions. Its 490 application–method pairs are unassessed: these are design options, not recommendations or literature-coverage claims.

## Try the prototype

Open [the offline catalogue](docs/catalogue/index.html) in a browser. Search **functional equivalence**, or open **Products and functional concepts (APP05)** to explore its methods and possible failure cases. The same data are available as [JSON](data/catalogue/catalogue.json), [JSONL](data/catalogue/records.jsonl), [CSV](data/catalogue/applicability.csv) and [SQLite](data/catalogue/novelty-design.sqlite).

The fictional example compares “Schedules appointments from a shared calendar” with “Books meetings using a team calendar” and a description that adds supervisor approval. It illustrates the difference between new wording and an added stated function. No model produced these examples and no novelty score has been computed.

## Run the teaching example

The [measure card](example/input/ASKIN_MEASURE_CARD.jsonl) documents musical typicality in Askin and Mauskapf (2017). It compares sonic features with earlier charting songs, weighted by genre similarity. Its 44 fields in nine sections include 17 reported values, 24 explicit unknowns and 3 proposed choices. It demonstrates the format, not a validated text measure.

From this folder, with Python 3.9 or later (standard library only; no model or network):

```sh
python3 tool/scripts/validate_measure_cards.py example/input/ASKIN_MEASURE_CARD.jsonl
python3 tool/scripts/validate_measure_cards.py --submission example/input/ASKIN_MEASURE_CARD.jsonl
```

The first command reports `STRUCTURE OK` and exits 0. The second refuses the teaching card and exits 1, as intended. [Recorded outputs](example/output/) show both results. Unknown fields stay empty; reported values require source locators. The validator checks structure, not whether a source supports a value. The card is unreviewed teaching material; [NOTICE.md](NOTICE.md) supplies the full citation.

## Files and reuse

- [Measure-card schema](tool/schemas/measure-card.schema.json) and [validator](tool/scripts/validate_measure_cards.py).
- [Design tables](docs/g9-design/README.md): 110 browse records in 12 research areas, plus six empty registry specifications.
- [Measurement and validation guidance](docs/g9-design/EXTRACTION_AND_VALIDATION.md).
- [Build script](tool/scripts/build_catalogue.py) and [HTML template](tool/templates/catalogue-template.html).
- [MANIFEST.json](MANIFEST.json): file sizes and SHA-256 fingerprints.

`python3 checks/verify_component.py` checks the supplied files and teaching example. `python3 tool/scripts/build_catalogue.py` rebuilds unchanged inputs. To change the design, preserve this release and copy `docs/g9-design/` and `tool/` into a new named folder without generated outputs. The builder refuses a changed existing database. Fresh SQLite bytes can differ across SQLite versions; separate output writes are not atomic against disk failure or concurrent writers.

## What remains proposed

The product-description specification is not populated and no texts have been scored or estimates validated. Developing the measurement workflow and agent skill, and evaluating functional differentiation using independent judgments, paraphrases and alternative comparison sets, remain proposed work. The catalogue and validator run now; they do not establish construct validity.

Code: Apache-2.0. Project-authored documents and data: CC BY 4.0. Third-party works retain their own terms; see [NOTICE.md](NOTICE.md) and the repository root licences and citation file. Product Hunt is credited as a preparation-data provider; its restricted collection is not distributed.
