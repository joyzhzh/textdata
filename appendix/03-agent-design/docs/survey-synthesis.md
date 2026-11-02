# Systems survey: implications for research-system design

The survey connects technical resources to the work of organizational inquiry. Its central distinction is between a component producing an output and evidence that the output supports a defensible inference.

## Design implications

- **Resources and retrieval:** inspect source coverage, versions and dependence before treating retrieved material as evidence.
- **Collection and measurement:** parsing, translation and annotation can change the meaning of source material. Preserve uncertainties through subsequent analysis.
- **Agent coordination:** separate execution state from the study record. A successful restart does not guarantee that an external action occurs only once; the [LangGraph worked example](../example/output/AD-014.md) makes this distinction concrete.
- **Evaluation:** keep author demonstrations, user reports and independent studies distinct. Benchmark performance remains tied to the reported task and conditions.
- **Research workflows:** connect consequential decisions to their evidence and make revisions inspectable. Proposed uses in TextData still require evaluation.

## Research functions

The full survey contains 22,667 typed entries and 22,749 function memberships. The public index includes 22,640 entries; 27 are excluded. Function totals overlap and are not counts of independent systems.

| Function | Full-survey entries |
| --- | ---: |
| Adjacent operational resources | 205 |
| Agent execution and coordination | 3,546 |
| Collection and source preparation | 464 |
| Disciplinary research systems | 3,378 |
| Discovery and knowledge resources | 1,709 |
| Evaluation and verification | 775 |
| Governance and source custody | 749 |
| Language and translation | 142 |
| Measurement resources and validity | 6,550 |
| Methods and analytical tools | 1,508 |
| Organizational and bibliographic context | 762 |
| Reproducibility and execution | 394 |
| Research communication and interfaces | 1,874 |
| Simulation and formal theory | 693 |

Browse the [public index](../data/systems-survey/survey-index.csv) or use the [query helper](../tool/query_survey.py) to inspect individual entries. The focused [agent-design database](../data/agent-design/index.html) provides 34 closer assessments of mechanisms, evidence, limitations and possible uses.

## Limits

Coverage is bounded by the available documentary sources. Entries are not unique systems, repeated sources are not corroboration, and unresolved fields are not findings of absent capabilities. The survey records an evaluation gap for 10,169 entries. Summary text is withheld for 19,401 public entries; the remaining note or evidence state must not be treated as a new primary-source check. No surveyed software or TextData configuration was benchmarked here.

[Method](survey-method.md) · [Data dictionary](survey-data-dictionary.md) · [Sources and licences](../NOTICE.md)
