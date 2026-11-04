# AI research systems and agent design

[Agent-design browser](data/agent-design/index.html) · [All components](../README.md)

Two searchable databases connect research requirements to technical design options, keeping mechanisms, evidence and limitations alongside proposed uses in TextData.

- **34 agent-design assessments across seven categories**, with a local browser, comparison-ready records, and JSON, CSV and SQLite exports.
- **22,640 public survey entries across 14 research functions**, drawn from a survey of 22,667 typed entries. Entries are not unique systems; function memberships overlap.
- **A worked LangGraph record** connects a proposed restart test to an unconfirmed report of repeated tool calls.

[Explore with your AI](AI-PROMPT.md) — copy the tailored prompt into your assistant.

## Try the prototype

Open the [agent-design browser](data/agent-design/index.html) locally with JavaScript enabled. Search for **AD-014** to inspect LangGraph persistence: a checkpoint saves execution position, but external actions need their own protection against repetition. The record proposes interrupting a task and checking both where it resumes and whether a tool call repeats.

The [worked reading](example/output/AD-014.md) connects this assessment to seven survey entries through shared public source addresses. [Issue 7417](https://github.com/langchain-ai/langgraph/issues/7417) reports a second dispatch while earlier calls were still active. The report remains unconfirmed; the restart test has not been run.

From this folder, use Python 3.9 or newer. These commands need no account, extra package, model call or network connection:

```sh
python3 -I tool/query_survey.py --id I-1aea8ea4c6bffc5c6e
python3 -I tool/query_survey.py --function 'Evaluation and verification' --search LangGraph --limit 3
python3 -I example/show_record.py AD-014 | diff example/output/AD-014.md -
python3 -I checks/verify_counts.py
```

The comparison is silent on success; the verifier reports zero failures. It checks the supplied files and example, not LangGraph performance.

## Data and interpretation

| Material | Contents |
| --- | --- |
| [Agent-design database](data/agent-design/data/catalogue.json) | 34 assessments; 19 use selected primary text and 15 documented source summaries. [SQLite](data/agent-design/exports/textdata-agent-design.sqlite) · [CSV](data/agent-design/exports/records.csv) · [Dictionary](docs/agent-design-data-dictionary.md) |
| [Survey index](data/systems-survey/survey-index.csv) | 22,640 entries with research functions, evidence states, gaps and public source addresses where available. [Dictionary](docs/survey-data-dictionary.md) |
| [Survey synthesis](docs/survey-synthesis.md) | What the evidence suggests for research-system design, with [method and limits](docs/survey-method.md). |

The survey excludes 27 entries and omits 19,401 summary passages for privacy or reuse reasons. Empty summaries and unresolved fields do not establish that a capability is absent. Assessments are documentary, coverage is bounded, and repeated sources do not supply independent corroboration.

## What remains proposed

The databases and browsing/query tools work now. No listed system was installed or benchmarked for TextData, no TextData configuration has been evaluated, and no documented TextData decision has yet used a focused design record. Next work will use the records to develop and evaluate configurations, including whether evidence survives delegation and contrary passages prompt substantive revision.

[Sources and licences](NOTICE.md) · [File inventory and hashes](MANIFEST.json)
