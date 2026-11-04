# Grounded Theory

[Worked example](example/output/TRACE.md) · [All components](../README.md)

A working agent toolkit for inductive process studies using grounded-theory techniques. It connects source passages, codes, comparisons and successive category definitions so a researcher can inspect why an interpretation changed. The researcher directs the inquiry and judges the explanations.

The prototype includes an agent skill, templates, three Python helpers, 53 tests, a runnable synthetic example and analytical records from **22 interviews over three cycles (6, 14, 22)**.

## What the demonstration shows

The interview analysis first proposed that opportunities to revise delegated work preserve agency. A contrary account of repeated repairs ending in a product shutdown separated having a correction channel from making an effective correction. A later account described an investor email sent without expected approval, although the speaker accepted its content. That distinction—**approval of an outcome versus authorization to act**—survived review in a revised episode that also retains unknown recipient effects and future control.

[Follow the worked example](example/output/TRACE.md): each comparison names its supporting records, the category it changes and the reason. The [analytical account](example/input/study/C003_ANALYSIS.md) develops the provisional explanation; the [review findings](example/input/study/audit/INDEPENDENT_REVIEW.md) show its qualifications.

[Explore with your AI assistant](AI-PROMPT.md): a prompt for reading the example and working with the prototype.

## Run the prototype

From this folder, with Python 3.9 or later:

```bash
python3 checks/verify_counts.py
python3 example/trace_comparison.py
```

These offline, standard-library commands check counts and file integrity, and reproduce `example/output/TRACE.md`. No model or network is needed. A successful check ends with `all checks passed`.

To run the synthetic two-cycle example or tests, install the dependency in [tool/requirements.txt](tool/requirements.txt). The helpers require macOS, Linux or WSL. The tool files work from an ordinary copied folder without Git history; runtime identity is recorded as `snapshot-sha256:<runtime tree hash>`:

```bash
cd tool
python3 -m pip install -r requirements.txt
python3 -B scripts/validate_analysis_packet.py examples/synthetic/C001
python3 -B examples/synthetic/workflow.py --output /absolute/new/folder/outside/any/git/checkout
python3 -B -m unittest discover -s tests
```

The example uses an invented nine-line text and calls no model. To work with an AI agent, load [tool/SKILL.md](tool/SKILL.md) and use [tool/AGENT_STARTER.md](tool/AGENT_STARTER.md).

## Materials

| Path | Contents |
|---|---|
| [tool/](tool/) | Agent instructions, methods guidance, schemas, helpers, templates, synthetic input and tests |
| [example/](example/) | Interview-study records, selection rationale, analytical account, review and reproducible comparison trace |
| [data/README.md](data/README.md) | Source bindings and transcript access limits |
| [checks/](checks/) and [MANIFEST.json](MANIFEST.json) | Offline count and integrity checks |
| [NOTICE.md](NOTICE.md) | Sources, credits and licences |

## Results and units

| Count | Value | Unit |
|---|---:|---|
| Interviews analysed | 22 | Bound transcript files; three cycles: 6, 14, 22 |
| Incidents | 234 | Accounts from sources; none directly observed |
| Incidents with a quotation hash | 78 | Quoted-line fingerprints, without the quotations |
| Comparisons | 43 | Comparison rows |
| Categories | 6 current | 15 versions retained |
| Memos | 14 | Versions across four memo types |
| Sampling requests | 3 | All proposed; none executed by the tool |
| Account envelopes | 86 current | 89 episode versions; not independent events |
| Unknown endings | 62 | Current envelopes with unknown outcome |
| Initial codes | 234 current | 235 versions retained |
| Tests | 53 | Released tests, including three copied-folder identity checks; the original 61 included 11 checks of private project files |

## Limits and next work

These are provisional interpretations of interview accounts, with founders overrepresented and many later outcomes unknown. Review was performed by a separate AI agent using the producers’ model, without blinding and on selected passages. There has been no independent human methodological assessment or comparison with the literature, and no claim to saturation or a validated theory.

The transcripts are not redistributed: no redistribution grant has been established for the retained copies. The analytical rows preserve their original status labels, `NON_RELEASE` and saturation `NOT_ASSESSED`. They show how the prototype operated, rather than established findings. The runnable synthetic example is self-contained; continuing the original interview study would require its transcripts and runtime. Withholding this study’s transcripts does not demonstrate general safeguards against prompt injection, bias or leakage.

Proposed development: extend empirical applications, examine alternative interpretations and assess the resulting theoretical claims.

Code and the agent skill are offered under Apache-2.0; project-authored documents and records under CC BY 4.0. Third-party rights remain with their owners. [Release modifications](CHANGES.md) distinguish retained records from the two redacted manifests.
