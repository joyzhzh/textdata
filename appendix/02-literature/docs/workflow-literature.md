# Annotation-workflow design: sensitivity, repeatability and evaluation

This assessment draws on eight selected primary texts. It is a scoped reading, not a systematic review or replication. Source versions, preliminary work and reporting inconsistencies are qualified below.

## Why it belongs in the workflow

The subsequent [methods comparison](annotation-methods.md) examines how the papers actually construct prompts, label text and test or combine models. It also records additional execution/reporting ambiguities found during that deeper reading. The workflow recommendation here should be read with those implementation limits.

The collected literature distinguishes sensitivity, repeatability, reference evaluation and downstream inference:

| Evidence from the retained source | Methodological implication | Limit on the inference |
|---|---|---|
| **Text as Data (2013), PDF pp. 3–5, 13:** automated text methods require application-specific validation and substantive human judgment; model selection and validation must be separated. | Document how a classifier is chosen and evaluate its intended meaning. Do not choose a list simply because it is largest or produces the strongest later fit. | A useful diagnostic is not validation of the intended construct. |
| **PNAS (2023), PDF pp. 3–6:** assess repeated annotation agreement separately from accuracy against a trained-human reference. Their accuracy analysis uses cases where both trained annotators agree. | Report repeatability and reference-relative error as separate outcomes, with explicit denominators. | Their temperature experiment, per-text chats and annotation tasks do not establish an optimal reasoning effort or three-reader vote for another catalogue. |
| **Variance-Aware LLM Annotation for Strategy Research, preliminary v3, main pp. 24–33 / PDF pp. 26–35; appendix p. 6 / PDF p. 48:** recommends recording variance, fixed audit inputs and change-triggered checks; allows relative stability monitoring when human labels are unavailable. | Retain the frozen catalogue, prompt, individual judgments, aggregation and comparison; repeat the diagnostic after material changes. | Proposed sampling defaults and small fixed-stimulus demonstrations do not supply power for a new replication design. |
| **Hidden Measurement Error in LLM Pipelines, v6, pp. 4, 20, 44:** separates repeated-call variation from sensitivity to selected pipeline settings; distinguishes an exact finite roster from a population of items or models. | Treat the selected items and configurations as the evaluation scope. Fresh ensemble repetitions measure something a single ensemble per condition cannot isolate. | Three replications is pilot guidance, accompanied by at least two prompt variants in that paper—not proof that a single-prompt study is sufficient. |
| **Dealing with Disagreements (2022), printed pp. 102–104 / PDF pp. 11–13:** aggregation can hide meaningful annotation disagreement. | Preserve all three votes, reasons and minority positions beside the binary handoff. | Evidence about subjective human annotations does not prove an AI minority is correct. |
| **Model Diversity Over Model Size, retained v2-associated manuscript, pp. 17–19, 65–68, 90–92:** ensemble gains depend on error diversity and the voting rule; a paired effort comparison does not favor higher effort on that task. | Test model composition and effort empirically. Keep the error-cost tradeoff explicit. | Fresh chats and different names do not establish independent errors or cross-provider diversity. |
| **Correct Codes for the Wrong Reasons?, v1, pp. 8–9:** inspectable coding can still follow the wrong theoretical distinction. | Inspect whether supplied evidence supports the intended risk-related scenario, including plausible omissions and neighboring constructs. | This is a conceptual proposal with an end-to-end demonstration still forthcoming. It does not establish that another application requires the proposed architecture. |
| **Using Large Language Model Annotations for the Social Sciences, November 2024 manuscript, printed pp. 19–24, 34–35 / PDF pp. 20–25, 35–36:** downstream inference needs a specified reference procedure and appropriate error treatment; reference disagreement also matters. | Examine whether alternative annotations change a derived measure and substantive conclusions. | Their design-based correction requires known positive reference-sampling probabilities and a matching estimator. It is not a drop-in correction for a shared selection vector. |

The distinction is consequential: a sensitivity experiment can show that a measurement choice changes results. It cannot, without additional evidence, tell us which result represents the intended construct.

## Why majority voting remains provisional

The ensemble manuscript’s main Table 4 and discussion (pp. 17–19) illustrate the tradeoff: for the Lower-6 ensemble, unanimity raises precision from 50.1% to 73.8% while reducing sensitivity from 86.7% to 68.6%. The paper explicitly cautions against unanimity where missing a true category is especially costly. Its Appendix Table 25 (p. 89) inconsistently prints 86.7% as unanimous sensitivity; the figures here follow the main table and accompanying narrative, without repairing the source.

This supports testing an aggregation rule against the intended costs, not importing unanimity to address excessive exclusion. The manuscript's GPT-5 minimal-versus-high effort check (pp. 90–92) also favors minimal effort on its survey task; that is evidence against assuming more effort always helps, not evidence that a particular setting is best in another application. Different tasks, models and execution procedures limit transfer.

Neither a larger selected set nor greater agreement establishes quality. Disagreements can form a review queue; they cannot be the only items reviewed, because systematic mistakes may be unanimous.

## Source access and version notes

Locators above use the retained PDFs, not an assumed current online revision. Page numbering differences are explicit. Source PDFs are not included.

- [Text as Data](https://doi.org/10.1093/pan/mps028), 2013. The retained advance PDF has 31 internally numbered pages; use the PDF locators above.
- [ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks](https://doi.org/10.1073/pnas.2305016120), 2023. Retained 13-page author manuscript contains a PNAS publication notice; the catalogue's arXiv-v2 association is not used to override that visible version evidence.
- [Dealing with Disagreements](https://aclanthology.org/2022.tacl-1.6/), 2022, TACL 10:92–110.
- [Variance-Aware LLM Annotation for Strategy Research](https://arxiv.org/abs/2601.02370v3). Retained preliminary draft title date 21 January 2026; arXiv stamp 19 January 2026. These dates are preserved separately.
- [Model Diversity Over Model Size](https://doi.org/10.31235/osf.io/er6mz_v2). The catalogue associates this DOI with the retained 104-page manuscript; no title-page publication date is asserted. It reports that its study was not preregistered.
- [Correct Codes for the Wrong Reasons?](https://arxiv.org/abs/2606.28574v1). Front matter 30 June 2026; arXiv stamp 26 June 2026. Conceptual preprint, with forthcoming empirical demonstration explicitly distinguished.
- [Hidden Measurement Error in LLM Pipelines Distorts Annotation, Evaluation, and Benchmarking](https://arxiv.org/abs/2604.11581v6), retained v6, 13 May 2026, under review. Selected methods and practical sections were checked; its full proofs and implementation were not independently validated.
- [Using Large Language Model Annotations for the Social Sciences](https://naokiegami.com/paper/dsl_ss.pdf), retained author manuscript 17 November 2024, first version 13 May 2024. This extends the authors' 2023 work; the two are not treated as the same version. The live author URL need not serve the retained bytes.
