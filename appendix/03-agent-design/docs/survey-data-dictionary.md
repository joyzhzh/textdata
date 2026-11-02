# Survey index dictionary

`data/systems-survey/survey-index.csv` contains one UTF-8 row per public entry. JSON arrays are encoded inside CSV cells. Use `tool/query_survey.py` to read decoded rows.

| Field | Meaning |
| --- | --- |
| `id`, `name` | Stable entry identifier and display name. |
| `unit_type` | Research item or evidence-unit class; not necessarily a unique system. |
| `relevance_tier` | Research-infrastructure, measurement, organizational or adjacent context. |
| `assessment_status` | Documentary evidence state; not a fresh independent validation. |
| `identity_status` | Basis and remaining uncertainty in grouping source identities. |
| `functions`, `disciplines` | Research functions and settings used for browsing; JSON arrays. |
| `summary` | Available project note or evidence-gap notice; blank when text is withheld. |
| `field_gaps` | Unresolved questions among the eight assessment fields; JSON array. |
| `source_links` | Public source locators where available; JSON array. |

The eight assessment fields are `purpose`, `setting`, `mechanism`, `inputs_outputs`, `interfaces`, `evaluation`, `limitations` and `version`. A gap means the assessment did not settle the question. A populated source field does not establish a verified capability.

`coverage.json` gives the survey population, evidence states, unit classes, research functions and gap totals. `function-membership.json` maps all 22,667 survey IDs to functions, including IDs omitted from the public index; memberships total 22,749 because functions overlap. `survey-index-held-back.json` records the 27 excluded IDs and reasons. These totals describe the full survey; browser search returns the 22,640 public entries.

The index contains 19,401 blank summaries. Other summaries comprise 15 checked notes, 3,167 description gaps and 57 unresolved assessments. The complete source texts are not included. [Method and limits](survey-method.md) · [Sources and licences](../NOTICE.md)
