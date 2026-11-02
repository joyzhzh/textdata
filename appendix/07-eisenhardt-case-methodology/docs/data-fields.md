# Reference collection: files and fields

The metadata-only collection contains 22,856 candidate-reference records, observed through 26 August 2026. Records may include duplicates or versions; they are not a count of distinct papers.

## Files

- `references.csv`: one row per record.
- `references.jsonl`: typed JSON records in the same order.
- `dois.txt`: 20,732 unique normalized DOIs.
- `MANIFEST.json`: counts, hashes and the export specification.

## Screening qualifications

| Evidence tier | Records | Meaning |
|---|---:|---|
| `canonical-metadata-qualified` | 15,198 | Metadata qualified; method adherence is not established. |
| `provisional-high-recall` | 7,658 | Provisional reference requiring further inspection. |

Screening labels comprise 12,300 `confirmed-case-study` and 10,556 `probable-case-study` records. These labels do not establish correct use of the Eisenhardt method. Inspect the linked work. Coverage is bounded and incomplete.

## Fields

| Field | Description |
|---|---|
| `source_release` | Collection version, `R12` |
| `public_id` | Identifier within this release |
| `evidence_tier` | Metadata-qualified or provisional |
| `screening_label` | Confirmed or probable case-study label |
| `title` | Work title |
| `publication_year`, `publication_date` | Available publication timing |
| `authors` | JSON array of author names; may be empty; JSON text within a CSV cell |
| `venue` | Journal, proceedings, repository or other venue |
| `doi`, `doi_url` | Normalized DOI and resolver URL |
| `urn` | URN where available |
| `openalex_id` | OpenAlex work identifier |
| `landing_url` | DOI, OpenAlex or stable public URL; blank if unavailable |
| `landing_url_source` | DOI, OpenAlex, stable URL or unavailable |

The files contain no abstracts, article text or PDFs. A reading link is a locator, not a reuse licence. The exporter is bound to a private source ledger, so this appendix checks the shipped files rather than regenerating them. See [NOTICE.md](../NOTICE.md) for source credit, terms and the remaining API-provenance qualification.
