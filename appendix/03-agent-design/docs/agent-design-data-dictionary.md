# Agent Design and Orchestration Database — data dictionary

Schema version **2.0**. JSON, HTML and the database exports describe the same 34 entries. Text uses UTF-8. Null means unavailable or not applicable.

## Tables and relationships

| JSON collection / SQLite table | Key and purpose |
| --- | --- |
| `families` | Seven categories, each with `id`, `name` and a design `question` |
| `records` / `profiles` | Entry IDs AD-001 through AD-034; each entry belongs to one category through `family` |
| `records[].references` / `source_references` | 91 reference rows linked by entry ID; publication/documentation URL, version, locator and observation date |
| `records[].repository_urls` / `repositories` | 22 repository-link rows, each linked to its entry and inspection-scope statement |
| Top-level fields / `metadata` | Title, edition date, schema version, description, scope and attribution |

An entry is a design component or body of work. It can connect a paper and an implementation, or describe several versions. Reference and repository rows are not counts of independent findings or unique packages.

## Entry fields

| Field | Meaning |
| --- | --- |
| `id`, `name`, `kind`, `credit` | Stable identifier, name, type and author/maintainer credit |
| `family` | Primary category ID, linked to `families.id` |
| `mechanism` | What the component does and how it operates |
| `evidence` | What the documented evidence supports |
| `limitations` | Conditions and unresolved issues affecting use of the evidence |
| `textdata_use` | Possible application in TextData |
| `textdata_evaluation` | Question that would need to be evaluated; not a reported TextData result |
| `evidence_basis`, `reading_scope` | Whether the entry draws on selected primary text or a documented source summary, and the corresponding reading limit |
| `primary_url`, `primary_locator`, `source_version` | Main reference, relevant passage and version |
| `repository_urls`, `repository_status` | Repository links and the scope of inspection; no current compatibility or license-clearance claim |
| `references` | Additional publication/documentation records with `url`, `version`, `locator`, `observed_at` |
| `implementation_status` | No implementation was executed or benchmarked for this database |

Nineteen entries use the label **Selected primary text** and fifteen use **Documented source summary**. These labels describe the basis of the record. Neither certifies a full-text review of every linked reference, and the labels are not a quality ranking.

`record_json` in SQLite retains the complete entry. CSV arrays and objects are JSON-encoded in their cells. `data/catalogue.json` is sufficient to rebuild all product exports. Detailed editorial lineage is kept separately from the product database.

## Example queries

```sql
-- Find entries on delegation and handoff.
SELECT id, name, textdata_evaluation
FROM profiles WHERE family = 'coordination';

-- Retrieve the references for one entry.
SELECT p.name, r.url, r.version, r.locator
FROM profiles p JOIN source_references r ON r.profile_id = p.id
WHERE p.id = 'AD-014';

-- Find entries with repository links.
SELECT p.id, p.name, r.url
FROM profiles p JOIN repositories r ON r.profile_id = p.id;
```

The database retains version-specific descriptions and uncertainty. Original publications and maintainers remain the authority for their own work.
