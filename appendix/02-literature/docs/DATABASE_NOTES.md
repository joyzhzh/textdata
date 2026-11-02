# Database schema and use

`data/records.json.gz` contains a `textdata-literature/2` object with `schema`, `release` and `records`. The CSV contains the same entries, fields and order. Null values become empty CSV cells; booleans are `true` or `false`.

## Fields

| Fields | Meaning |
|---|---|
| `id`, `source_catalogue`, `source_record_id` | Stable entry identity and catalogue membership. A paper may have more than one entry. |
| `title`, `authors`, `year`, `journal`, `doi`, `url` | Bibliographic metadata. An ambiguous year is null; qualifications retain relevant version/year limits. |
| `abstract` | Always null: abstract prose is not distributed. |
| `abstract_on_file` | Whether an abstract is available in this edition’s underlying source collection; this does not establish full-paper reading. |
| `abstract_source` | Public source URL(s), or the article’s DOI/URL as a reading destination. It is not a licence grant or necessarily the exact acquisition endpoint. |
| `reading_note` | Project-authored scholarly notes: findings, interpretation, source/version and page references, and reading-depth limits. Null if no substantive note is available. Separate assessments may concern different versions. |
| `qualifications` | Limits on bibliography, reading depth, access, interpretation or redistribution. |

Notes are a presentation edition: operational history and internal locators are omitted, and identifying study context and overlapping abstract passages are omitted or paraphrased. Bibliographic facts, source findings and relevant limitations are preserved. The export is not the original working record.

## Repository edition

| Catalogue | Entries |
|---|---:|
| `annotation_checkpoint` | 318 |
| `annotation_successor` | 319 |
| `annotation_journals` | 8,222 |
| `catalogue_d` | 1,873 |
| **Total** | **10,732** |

There are 8,236 substantive reading notes, 107 entries with an abstract available, 10,114 entries with a URL and 9,857 with a DOI. No entries are merged across catalogues. A note may reflect metadata, an abstract or selected passages; consult its reading-depth statement.

The webpage’s separately labelled edition has 10,731 entries, 8,236 notes and 4,790 abstracts on file, of which 4,710 contribute to word search. Both editions preserve source-scoped IDs. The page also provides aggregate theme counts over 4,732 source abstracts, a wider basis than its searchable entries; these word-pattern counts are not semantic classifications or a representative sample.

Run `python3 checks/verify_counts.py` from the component folder to verify the final repository files. `tool/query.py` searches metadata, not notes; the webpage additionally searches distinct abstract words without displaying abstract prose. `tool/build_sqlite.py` creates the same 14-field table plus schema/release metadata.

Metadata search retains every included entry. Abstract-word search and theme counts omit sources without established sharing permission.
