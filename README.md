# TextData

**TextData expands what organizational researchers can do with text data.**

*Adaptive AI Infrastructure for Organizational Research*

[Component guide](appendix/README.md) · [Design figure](assets/textdata-design.png) · [Extending TextData](EXTENDING.md)

TextData is an adaptive AI research infrastructure designed to help organizational researchers acquire, prepare and analyze textual data. It draws on frontier large language models (LLMs) to help researchers examine extensive evidence, construct organizational measures and refine theoretical explanations. Researchers direct the inquiry and retain authority over methods and conclusions.

This repository provides finished resources, runnable examples and usage guides for ten components.

## Start here

- **Explore a component:** choose a component folder in the [component guide below](#the-ten-components).
- **Try an example:** follow the component’s README for instructions, expected outputs and what remains proposed.
- **Use your AI assistant:** supply the component folder to your assistant and copy its `AI-PROMPT.md` to explore the resources and worked example.

## How TextData works

[View the design figure](assets/textdata-design.png)

The design brings together four interdependent elements:

- **AI agents** use LLMs to choose and carry out steps toward researcher-defined goals.
- **Tools** perform specified operations, such as retrieving records, preparing texts, locating passages and constructing measures.
- **Workflows** coordinate agent actions and tool operations, specifying their sequence, conditions for proceeding and how results pass between agents.
- **Resources** preserve source texts, findings, methodological guidance and reusable components. These include *agent skills*: packages of instructions, reference materials and supporting tools for particular research tasks.

**Researcher-directed inquiry.** The researcher defines the question and scope. A coordinator agent turns that goal into assignments for task agents, which consult resources and use tools within workflows. The coordinator brings results together for the researcher to assess the evidence, judge which claims it supports and direct further work. Evidence, findings and methodological decisions become resources for subsequent inquiry.

**An adaptive core.** The deep-research engine coordinates continuing inquiry into capabilities, methods and tools, helping TextData adapt as research needs, LLMs and open-source components change. Research agents examine literature, primary sources and technical repositories, retaining findings and sources in a shared knowledge vault. Under researcher direction, this evidence informs which components to adopt, adapt or build and test. Human researchers and development agents build and maintain the engine that supports this work.

**Reliability and continuing evaluation.** Source links, quotation checks and separate review help examine claims. Alternative interpretations and contrary evidence help challenge premature agreement. Software checks support, but do not establish, the validity of an interpretation. Repeated trials of model-dependent tasks and comparisons after model or workflow updates remain planned.

## The ten components

[View the components and development status figure](assets/textdata-components.png). Its arrows indicate the engine’s intended support for continuing development; asterisks mark proposed additions or integration.

Component numbers match the proposal and technical appendix. Each component name links to its README; the local starting points below lead to supplied examples and resources. The [appendix index](appendix/README.md) provides a compact directory.

The resources and demonstrations establish working parts of the design. Integration and research validity require further evaluation.

### Deep-research engine

| Component | Available resources and examples | Start locally |
|---|---|---|
| [1. Deep-research engine](appendix/01-engine/README.md) | A scout skill, offline validator and worked evidence map. A shareable, integrated engine remains proposed. | [Worked example](appendix/01-engine/example/README.md) |

### Research foundations

| Component | Available resources and examples | Start locally |
|---|---|---|
| [2. Textual-data literature reviews and database](appendix/02-literature/README.md) | A searchable 10,732-entry database and two of three methodological syntheses. Entries come from overlapping catalogues. | [Reading example](appendix/02-literature/example/output/record-W026.json) |
| [3. AI research systems and agent design](appendix/03-agent-design/README.md) | Two databases with browsing and query tools document research systems and agent designs. | [Design browser](appendix/03-agent-design/data/agent-design/index.html) |
| [4. Rich textual-data sources review](appendix/04-data-sources/README.md) | A catalogue, dated source profiles, comparative review and profile-rendering tool help assess coverage and what a source can reveal. | [Source profiles](appendix/04-data-sources/data/profiles/README.md) |

### Qualitative toolkits

| Component | Available resources and examples | Start locally |
|---|---|---|
| [5. Grounded Theory](appendix/05-grounded-theory/README.md) | An agent skill, workflows, templates and software helpers, with a worked analysis of 22 interviews. | [Analysis trace](appendix/05-grounded-theory/example/output/TRACE.md) |
| [6. Gioia Methodology](appendix/06-gioia-methodology/README.md) | An agent skill, templates and a quotation checker. A synthetic example shows how an exact quotation can still be misinterpreted. | [Usage guide](appendix/06-gioia-methodology/docs/USAGE.md) |
| [7. Eisenhardt Case Methodology](appendix/07-eisenhardt-case-methodology/README.md) | A method map, reference collection and maintenance skill support preparation for case research. Case analysis remains proposed. | [Method map](appendix/07-eisenhardt-case-methodology/docs/METHOD_MAP.md) |

### Acquisition and measurement

| Component | Available resources and examples | Start locally |
|---|---|---|
| [8. Large-scale data acquisition](appendix/08-data-acquisition/README.md) | An inventory of 806,941 historical document records and a 191-document acquisition and verification example. | [Example files](appendix/08-data-acquisition/example/) |
| [9. Combining ML, NLP and LLMs](appendix/09-measurement/README.md) | A methods catalogue, measurement specifications and a validator. The proposed product-description measure has no scores. | [Offline catalogue](appendix/09-measurement/docs/catalogue/index.html) |
| [10. LLM-annotation workflow](appendix/10-annotation/README.md) | Request preparation, quotation checks and feature export, illustrated with saved responses for five passages. Source checks do not establish annotation accuracy. | [Worked example](appendix/10-annotation/docs/WORKED_EXAMPLE.txt) |

ML: machine learning; NLP: natural language processing; LLM: large language model.

## Reuse and further development

Researchers can adopt individual components, inspect their sources and limitations, and adapt the procedures to their own questions. Saved inputs and worked examples support reuse and specified software checks. See [Extending TextData](EXTENDING.md) for planned development and ways to build on the infrastructure.

## Licenses

Project code is licensed under [Apache 2.0](LICENSE); project-authored documentation and data are licensed under [CC BY 4.0](LICENSE-docs). Third-party material retains its own terms, recorded in the component notices.
