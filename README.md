# TextData

**TextData expands what organizational researchers can do with text data.**

*Adaptive AI Infrastructure for Organizational Research*

[Website](https://textdata.info/) · [Interactive design](https://textdata.info/how-it-works/) · [Website repository](https://github.com/joyzhzh/textdata-site)

TextData provides reusable research infrastructure for AI-enabled research loops under human direction. Its [deep-research engine](https://textdata.info/engine/) supports developing the tools and workflows of textual inquiry as the inquiry itself unfolds. Researchers direct AI agents to investigate methods, sources, and technical advances, and to build and revise capabilities for acquiring, interpreting, and measuring textual evidence.

**The central proposition is that emerging research questions and interpretations can shape the capabilities available to pursue a study.** An inquiry can lead to a different source, a revised analytical procedure, or a new measurement design. TextData connects that development work to the investigation of organizational phenomena, while retaining the resulting tools, workflows, and resources for further research.

This repository presents the design and its proof of concept through an engine, reusable research resources, and documented applications to text data. The examples below show what has been built, what it has been used to do, and what readers can examine or reproduce.

## The design

[![TextData infrastructure design](assets/textdata-design.png)](https://textdata.info/how-it-works/)

*Explore the figure interactively on the website.*

On the **left**, a coordinator agent turns the researcher’s goals into assignments. Task agents reason and use tools; workflows organize their work. Findings return to the researcher for examination.

On the **right**, development agents build and maintain the deep-research engine. Research agents work within it to investigate methods and capabilities, building and using tools in that inquiry. Evidence and conclusions accumulate in a shared knowledge vault for retrieval and reconsideration.

**Resources connect research with capability development.** They preserve evidence, methodological guidance, conclusions, and toolkit components. They inform both the conduct of a study and the continuing development of its research infrastructure. The human researcher retains authority over methodological choices, interpretations, and scholarly claims.

## Proof of concept

The deep-research engine has supported the development of **nine resources, organized into three groups**. Together, they connect research on text-data methods with reusable capabilities and documented applications. The technical appendix provides the methodological accounts and evidence qualifications; component documentation provides operating instructions and supporting records.

### Research foundation

These resources inform which textual evidence to seek, how to study it, and which technical capabilities to develop.

1. **[Textual-data literature reviews and database](https://textdata.info/foundation/literature-reviews/)**

   Three methodological syntheses connect to a searchable literature database with a browsing interface and SQLite, CSV, and JSON editions. Researchers and agents can examine the studies and reading notes behind methodological choices and reuse them in a new inquiry.

   **Explore:** syntheses, bibliographic records, qualified reading notes, and database exports.

2. **[AI research systems and agent design](https://textdata.info/foundation/ai-research-systems/)**

   A survey of AI research systems and a focused agent-design database help identify technical approaches suited to a research task. They connect infrastructure development to documented systems and mechanisms that researchers can examine and compare.

   **Explore:** system profiles, agent-design records, source evidence, and documented assessments.

3. **[Rich textual-data sources review](https://textdata.info/foundation/textual-data-sources/)**

   A source catalogue and comparative review help match a research question to suitable text data. Source profiles describe what each collection preserves, its coverage, and its access conditions, providing a basis for selection and acquisition.

   **Explore:** source profiles, cross-source comparisons, and acquisition considerations.

### Qualitative toolkit

These components support developing and revising interpretations and theory from textual evidence.

4. **[Grounded Theory](https://textdata.info/toolkit/grounded-theory/)**

   A methods synthesis informed reusable agent instructions and software helpers for coding, constant comparison, memoing, category development, and theoretical sampling proposals.

   **Demonstration:** the toolkit was applied to published interviews from Lenny’s Podcast in a study of human agency in AI-mediated work. The study expanded from six to twenty-two interviews as comparisons exposed conceptual uncertainties. Added evidence required distinctions among satisfaction with an AI-produced output, authorization of an action, and the ability to intervene effectively. Source-linked incidents, comparisons, memos, and category versions preserve how the provisional account changed.

   **Explore:** methodological guidance, agent instructions and helpers, a synthetic example, and the interview study’s selection and revision records.

5. **[Gioia Methodology](https://textdata.info/toolkit/gioia-methodology/)**

   Analytical guidance, working templates, and an executable quotation checker support concept development and examination of data structures. Synthetic exercises demonstrate their use while preserving the distinction between participant expressions and analytical interpretation.

   **Explore:** analytical guidance, templates, quotation checks, and worked exercises.

6. **[Eisenhardt Case Methodology](https://textdata.info/toolkit/eisenhardt-case-methodology/)**

   A methodological reference collection and working maintenance and export tools support preparing, organizing, and checking case-research materials. They provide a foundation for case-based theory development.

   **Explore:** the methodological reference map, research-material organization, and maintenance and export tools.

### Quantitative toolkit

These components support preparing textual collections and developing source-linked analytical records and measurement designs.

7. **[Large-scale data acquisition](https://textdata.info/toolkit/large-scale-data-acquisition/)**

   The Federal Register collection contains **806,941 document records** dated from January 2000 through September 2026. Its inventory preserves source identities, text availability, and known gaps; accompanying tools prepare text and check the collection. The original download scripts are not included, so the historical acquisition cannot be replayed in full.

   **Explore:** collection inventories, source and coverage records, text-preparation tools, and verification tools.

8. **[Combining ML, NLP and LLMs](https://textdata.info/toolkit/combining-ml-nlp-llms/)**

   A methods catalogue and structured measurement designs connect machine learning, natural language processing, and large language models. They specify how textual annotations, language representations, and statistical comparisons can contribute to an organizational measure, and what evaluation is needed.

   **Explore:** the methods catalogue, measurement specifications, and evaluation requirements.

9. **[LLM-annotation workflow](https://textdata.info/toolkit/llm-annotation-workflow/)**

   A coding workflow connects preserved policy text, a codebook, candidate annotations, and executable checks to structured outputs.

   **Demonstration:** five passages from [Executive Order 13960](https://www.govinfo.gov/content/pkg/FR-2020-12-08/html/2020-27065.htm) produce four candidate actor–action relations and one explicit no-assignment record. Quotes, passage locations, conditions, and other mentioned roles remain attached. Saved annotations reproduce the same exported table. Deliberately incorrect examples show that valid quotations can still support an incorrect assignment of responsibility; independent reference coding remains part of the evaluation agenda.

   **Explore:** preserved text, codebook, selected passages, candidate annotations, exported table, and documented error cases. The replay command below reproduces the saved outputs.

## Reproduce a result

Start with the LLM-annotation workflow’s `WORKED_EXAMPLE.txt` and `worked-output/features.csv`. From that component’s folder, replay the saved annotations with Python 3.9 or newer:

```sh
python3 workflow.py export \
  --package prepared \
  --response candidate_response.jsonl \
  --receipt producer_receipt.json \
  --out replay-01
```

Use a new output-directory name for each replay. The command checks the retained inputs and annotations, then reproduces the source-linked outputs using Python’s standard library. This is replay of saved annotations; independent assessment of their meaning is a separate task.

These demonstrations establish working parts of the design: research-informed capability development, successive qualitative analysis, and reproducible processing from text to candidate analytical records. Evaluating the integrated infrastructure across further studies is part of continued development.

See [Extending TextData](EXTENDING.md) for planned extensions and ways to build on the infrastructure.
