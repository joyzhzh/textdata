# Textual-data literature reviews and database

[Database guide](docs/DATABASE_NOTES.md) · [Use with an AI assistant](AI-PROMPT.md) · [All components](../README.md)

A searchable research foundation for choosing and evaluating textual methods. The finished collection separates bibliographic facts from reading notes and their limitations. It contains **10,732 entries from overlapping catalogues**, **8,236 substantive reading notes**, and **two of three methodological syntheses**.

## Try it

Read [the saved example](example/output/record-W026.json) for Andrew Speer’s article on the reliability of AI scores: the note distinguishes correlational agreement from factor-model reliability, while its reading-depth qualification prevents treating the note as proof of full-paper reading. Use the commands below to query the local metadata and notes.

The supplied 10,732-entry edition is distinct from the separately labelled 10,731-entry website edition, which has more abstracts available for word search and is not included here. Neither edition distributes abstract prose. Counts are entries, not distinct papers.

For an offline example, use Python 3.9 or later; no additional packages, network or model service are needed:

```sh
python3 tool/query.py --id annotation_checkpoint:W026
python3 tool/query.py --search "inter-rater reliability"
python3 checks/verify_counts.py
python3 tool/build_sqlite.py --out literature.sqlite
```

The last command creates a queryable SQLite database. The check verifies the exports, counts, syntheses, worked outputs and file hashes.

## Included material

| File | Use |
|---|---|
| `data/records.json.gz`, `data/records.csv.gz` | The same 10,732 entries in JSON and CSV |
| `data/summary.json`, `docs/DATABASE_NOTES.md` | Final counts and the 14-field schema |
| `docs/annotation-methods.md` | How seven papers and three supplements use prompts, models, repetitions and comparisons |
| `docs/workflow-literature.md` | Eight-source assessment of sensitivity, repeatability, reference evaluation and downstream inference |
| `docs/SYNTHESES.json` | Two included syntheses and a generic marker for the third |
| `tool/`, `example/`, `checks/` | Metadata search, SQLite conversion, worked outputs and an offline integrity check |
| `NOTICE.md`, `MANIFEST.json` | Credits, licence boundaries and file hashes |

The syntheses explain why comparing models, repeating a model and combining model judgments answer different questions. Each retains source/version references and the limits of the inspected evidence.

## Limits and next steps

Catalogues overlap; entries and notes do not count unique papers or completed full-paper readings. Abstract coverage is uneven. Source claims and the project’s interpretations are distinguished, but the papers’ results have not been independently reproduced and the notes have not all been checked against the original papers. These are scoped syntheses, not systematic reviews.

Further syntheses, abstract coverage and reading notes are proposed development. Code is Apache-2.0; project-authored material is CC BY 4.0. Third-party sources retain their own terms; see [NOTICE.md](NOTICE.md).
