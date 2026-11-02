# Agent Design and Orchestration Database

The **Agent Design and Orchestration Database** provides a local HTML interface. The database contains **34 entries across seven categories**, covering papers, repositories, specifications and reusable components. Each entry identifies a design mechanism, describes its capabilities and supporting evidence, records its limitations and relevant versions, and explains its possible use in TextData. Links connect entries to their publications, documentation and repositories.

[Open the database](../data/agent-design/index.html#catalogue) · [Download SQLite](../data/agent-design/exports/textdata-agent-design.sqlite) · [Download JSON](../data/agent-design/data/catalogue.json) · [Download CSV](../data/agent-design/exports/records.csv)

## Database organization

The seven categories organize entries by the design questions they address. Each entry has a stable identifier, AD-001 through AD-034, and one primary category. An entry may connect a paper with an implementation or distinguish several versions of the same component.

| Category | Entries | Design question |
| --- | ---: | --- |
| Action and planning | 5 | How should an agent choose, execute and revise its next step? |
| Orchestration and reuse | 4 | Which responsibilities belong in program structure, and which in a model decision? |
| State and context | 5 | What must persist, and what does the model need to see now? |
| Tools and skills | 3 | How should capabilities and methodological instructions be exposed? |
| Delegation and handoff | 5 | When does dividing work help, and what must pass between workers? |
| Evaluation and adaptation | 7 | How will we assess a change without confusing extra computation with better design? |
| Evidence and authority | 5 | How can we recover the basis of a claim and keep source content within its proper role? |

## Information in each entry

| Information | What the reader can inspect |
| --- | --- |
| Identity and type | Name, stable identifier, category, publication or component type, and author or maintainer credit |
| Mechanism | What the component does and how it operates |
| Evidence | What the documented evidence supports and whether the entry draws on selected primary text or a documented summary |
| Limitations | Conditions, unresolved questions and boundaries on the evidence |
| Relevance to TextData | A possible use and the question that would need to be evaluated |
| References and versions | Primary publication or documentation, relevant version and passage, additional references and repository links |

The entry separates reported evidence from proposed use. A possible TextData application is a design interpretation, not an observed result. Reference versions are recorded so readers can distinguish a paper, an implementation and changing documentation. Several references to a work do not imply several independent findings.

## HTML interface

**Browse database** provides text search and filters for category, entry type and evidence basis. The result count updates as filters are combined. Selecting an entry opens its full description, evidence, limitations, TextData relevance and references. Each entry has a direct link that can be saved or shared with someone who has access to the files.

**About the database** presents this appendix and the entry register below. **Download** provides the complete database and individual data tables. The browse view also exports the current selection as JSON. Search and filtering run locally in the browser.

For example, selecting *State and context* displays five entries on retaining and accessing information. Searching for *LangGraph* opens the entry distinguishing thread checkpoints from data shared across threads. Its detail view keeps the mechanism, evidence, limitations and proposed evaluation together.

## Entry register

Select an entry to open its database record.

| ID | Entry | Category |
| --- | --- | --- |
| AD-001 | [CoALA](../data/agent-design/index.html#AD-001) | Action and planning |
| AD-002 | [Building effective agents](../data/agent-design/index.html#AD-002) | Orchestration and reuse |
| AD-003 | [ReAct](../data/agent-design/index.html#AD-003) | Action and planning |
| AD-004 | [AutoGen](../data/agent-design/index.html#AD-004) | Delegation and handoff |
| AD-005 | [DSPy](../data/agent-design/index.html#AD-005) | Orchestration and reuse |
| AD-006 | [Model Context Protocol resources and tools](../data/agent-design/index.html#AD-006) | Tools and skills |
| AD-007 | [Co-Scientist](../data/agent-design/index.html#AD-007) | Delegation and handoff |
| AD-008 | [Anthropic multi-agent Research](../data/agent-design/index.html#AD-008) | Delegation and handoff |
| AD-009 | [Effective context engineering](../data/agent-design/index.html#AD-009) | State and context |
| AD-010 | [LLooM](../data/agent-design/index.html#AD-010) | Evidence and authority |
| AD-011 | [MAST](../data/agent-design/index.html#AD-011) | Delegation and handoff |
| AD-012 | [W3C PROV-DM](../data/agent-design/index.html#AD-012) | Evidence and authority |
| AD-013 | [Managed Agents architecture](../data/agent-design/index.html#AD-013) | State and context |
| AD-014 | [LangGraph persistence](../data/agent-design/index.html#AD-014) | State and context |
| AD-015 | [Reflexion](../data/agent-design/index.html#AD-015) | Action and planning |
| AD-016 | [Tree of Thoughts](../data/agent-design/index.html#AD-016) | Action and planning |
| AD-017 | [LLMCompiler](../data/agent-design/index.html#AD-017) | Action and planning |
| AD-018 | [Open Agent Specification](../data/agent-design/index.html#AD-018) | Orchestration and reuse |
| AD-019 | [Temporal agent integration](../data/agent-design/index.html#AD-019) | Orchestration and reuse |
| AD-020 | [MemGPT](../data/agent-design/index.html#AD-020) | State and context |
| AD-021 | [Mem0](../data/agent-design/index.html#AD-021) | State and context |
| AD-022 | [Agent Skills](../data/agent-design/index.html#AD-022) | Tools and skills |
| AD-023 | [SWE-agent](../data/agent-design/index.html#AD-023) | Tools and skills |
| AD-024 | [Who Validates the Validators / EvalGen](../data/agent-design/index.html#AD-024) | Evaluation and adaptation |
| AD-025 | [Inspect AI](../data/agent-design/index.html#AD-025) | Evaluation and adaptation |
| AD-026 | [OpenTelemetry GenAI conventions](../data/agent-design/index.html#AD-026) | Evidence and authority |
| AD-027 | [AgentDojo](../data/agent-design/index.html#AD-027) | Evidence and authority |
| AD-028 | [PrivacyLens](../data/agent-design/index.html#AD-028) | Evidence and authority |
| AD-029 | [Berkeley Function Calling Leaderboard](../data/agent-design/index.html#AD-029) | Evaluation and adaptation |
| AD-030 | [tau-bench](../data/agent-design/index.html#AD-030) | Evaluation and adaptation |
| AD-031 | [GEPA](../data/agent-design/index.html#AD-031) | Evaluation and adaptation |
| AD-032 | [MIPRO and MIPROv2](../data/agent-design/index.html#AD-032) | Evaluation and adaptation |
| AD-033 | [AI Agents That Matter](../data/agent-design/index.html#AD-033) | Evaluation and adaptation |
| AD-034 | [Handoff Debt](../data/agent-design/index.html#AD-034) | Delegation and handoff |

## Files and use

The HTML interface and database files are supplied together. JSON contains the complete structured database; CSV and JSONL provide entry tables; SQLite supports queries across entries, categories, references and repositories. A SQL file reconstructs the SQLite database. The [data dictionary](agent-design-data-dictionary.md) describes the fields and relationships, and the [opening instructions](../README.md) explain local use.

This edition is dated **29 October 2026**. The database supports inspection and comparison of design options. Inclusion is not an endorsement, and no listed implementation has been executed or benchmarked for the database. References, evidence statements and limitations should be read together when considering an entry for TextData.
