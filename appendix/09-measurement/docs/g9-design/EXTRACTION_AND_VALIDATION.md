# Measurement extraction and validation

Each retained operationalization must be reconstructable from the inspected source and interpretable for its actual task. Preserve the distinction between what authors claim, what their evidence supports and what the researcher infers. An explicit unknown is preferable to filling in a plausible method detail.

## Required measure record

The nine-section measure card records the following information. Keep source locators, support, limitations and rights explicit.

| Section | Required content |
|---|---|
| Identity and provenance | Canonical work, manifestation/version, publication status, DOI or stable ID, correction/retraction state, retrieval date, inspection depth, rights and exact locators |
| Construct and application | Intended novelty target; application/subarea; person/process/product/set level; production setting; evaluator population; actual artifact versus representation versus perception report |
| Inputs and observation | Input and preprocessing, original language, modality, omitted information, model/version, known or unknown training cutoff, context limits, prompts, examples, decoding and extraction steps |
| Formula and reference universe | Formula or faithful source-located pseudocode; distance and normalization; reference eligibility and dates; genre/field/market restriction; neighbor count; weighting; null model; aggregation; direction; missing/empty-pool handling |
| Sample and human criterion | Objects and denominators, rater numbers and expertise, instructions, scale/anchors, blinding, familiarity, disagreement, clustering, exclusions, sampling and train/calibration/test splits |
| Validation actually performed | Each reliability/validity/transport result with estimate, uncertainty if reported, exact task/population/split, comparator and limitations; absence of validation stays explicit |
| Rival explanations | Length, fluency, rare words, incoherence, quality, usefulness, prestige, popularity, familiarity, topic, corpus density, future knowledge, selection and reference coverage |
| Assets and operational requirements | Paper/code/data/model links and separately inspected licenses, documentation depth, reproducibility details, reported cost/latency, missing access and deployment prerequisites |
| Adverse evidence and interpretation | Strongest contradiction or failed test; author limits; researcher inference; dependency cluster; corrections and supersession; supported use, unvalidated transfer or unresolved status |

For an LLM judge, additionally record the target rubric, actual comparison context, retrieved material, citation behavior, answer format, score anchors, repetition and aggregation. For a retriever, distinguish retrieval recall/coverage from the assessor's behavior given correct references. For an extraction pipeline, distinguish lost or hallucinated features from errors in the final comparison.

## Evidence states

Method recommendations use these descriptive categories, with reasons and citations rather than a synthetic quality score:

- Supported for the stated task and population.
- Supported with material constraints or mixed evidence.
- Candidate approach with insufficient validation for the proposed use.
- Evidence against the proposed interpretation or use.
- Unresolved or inaccessible evidence.
- Not applicable to the defined target, with rationale.

These are use-specific decisions. The same method can occupy different categories across applications. A benchmark paper is not independent of its own evaluator training set, and multiple papers using one label set do not provide multiple independent validations.

## Mandatory validation questions

1. **Content and construct:** Does the measurement observe the feature on which novelty is claimed? Are descriptions adequate for the artifact?
2. **Human criterion:** Whose judgment is the target? Are experts, consumers or affected communities appropriate and sufficiently exposed to the comparator set?
3. **Reliability:** What happens across raters, prompts, repetitions and model versions? Report agreement and uncertainty separately from validity.
4. **Convergence and discrimination:** Does the score relate to appropriate criteria while remaining distinguishable from length, rarity, usefulness, coherence and quality?
5. **Reference sensitivity:** How do eligibility, missing predecessors, self matches, window size, category density and comparator sampling affect the result?
6. **Retrieval and evidence grounding:** Are retrieved sources relevant and sufficiently complete for the bounded claim? Does each asserted antecedent actually support the comparison?
7. **Temporal integrity:** Are the object, references, labels and model knowledge consistent with the intended assessment date? Unknown model knowledge is not a clean temporal boundary.
8. **Representation robustness:** Are meaningful differences retained and irrelevant wording changes suppressed? Does translation or summarization change the target?
9. **Domain and population transport:** Was the method tested outside the domain, creator, prompt family, language or cohort on which it was chosen?
10. **Calibration and abstention:** What does a confidence or score interval mean? When should the system return insufficient evidence or request human review?
11. **Selection and dependence:** Were only top ideas, accepted papers or selected outputs validated? Are multiple submissions, model generations and ratings clustered correctly?
12. **Downstream use:** Is the score suitable for screening, comparison or statistical inference? What are the costs of false novelty and missed novelty?
13. **Reproducibility and operation:** Can the version, prompt, corpus, preprocessing and aggregation be recovered? Which reported costs or latencies are actually comparable?

## Perturbation and comparator design

The following are proposed test families to assess in the literature and specify for later empirical work. They are not executed experiments. Expected responses must be tied to the particular construct and metric.

| Test family | Illustrative variants | Question |
|---|---|---|
| Meaning preserved | Paraphrase, name substitution, translation, faithful summary | Does the claimed semantic measure resist irrelevant form changes? |
| Meaning changed | Same words with different relations, changed mechanism, new causal structure | Does it detect substantive departures? |
| Presentation changed | Longer pitch, polished style, prestige cues, confident claims | Does quality or status contaminate novelty? |
| Invalid content | Rare-word injection, contradictions, impossible or incoherent combinations | Is rarity being mistaken for a useful novelty construct? |
| Prior work changed | Add a real predecessor, omit the closest antecedent, introduce a misleading citation | How sensitive is the claim to evidence and retrieval failures? |
| Reference population changed | Same field versus all fields, different genre, local versus global, different pool sizes | Is the score's interpretation stable or predictably conditional? |
| Temporal boundary changed | Future references, later model knowledge, revised disclosures | Is the method ex ante, retrospective or temporally ambiguous? |
| Modality changed | Artifact versus synopsis/caption, text-only versus multimodal | What information is lost or introduced? |
| Production setting changed | Human, AI, collaborative, individual, crowd, repeated samples | Are source and dependence effects separated from novelty? |
| Strategic submissions | Instructions embedded in an idea, manipulated citations, score-seeking language | Can the evaluator resist task-irrelevant instructions and gaming? |

A nearest-prior-art measure and a mean-distance measure need not obey the same response to adding one predecessor. A perceived-newness measure may intentionally change with evaluator exposure. Judge against the method's declared target rather than a universal checklist of desired numerical behavior.

## Domain protocol template

Every application cell receives a protocol with:

1. The intended decision, object and novelty definition.
2. What the assessor can observe and what remains outside the representation.
3. Reference-universe eligibility, source coverage, time window and sampling rules.
4. Human criteria and distinct novelty, usefulness, feasibility and quality labels.
5. Candidate methods and parsimonious baselines, with reasons tied to evidence.
6. Prompt or extraction specification where source support permits it; unvalidated adaptations explicitly labelled.
7. Score direction, aggregation, uncertainty and interpretation; no unexplained composite.
8. Missing-data, failed-retrieval, insufficient-context and abstention behavior.
9. Relevant perturbations, population shifts and temporal checks.
10. Evidence references, known failure modes and the additional validation needed before use.

The film-synopsis walkthrough must distinguish plot/narrative departure, audience-perceived novelty and artistic execution. The venture walkthrough must distinguish market newness from pitch distinctiveness. The crowd walkthrough must separate within-pool uniqueness from external prior-solution novelty. The science walkthrough must distinguish contribution, correctness, significance and feasibility. Other applications receive equivalent specificity, with variants when subareas require different observations or comparators.

## Proposed empirical follow up

The empirical validation study is proposed, not run. Define target populations and sampling strata; select sample size from precision or power needs and realistic rater variation; specify expert and audience panels; separate calibration from testing; cluster by creator, institution, task and source dataset where warranted; keep paraphrase families, related patents, franchises and repeated model outputs from leaking across splits.

Compare justified classical, human and LLM alternatives. Include a direct judge, a retrieval-grounded method and a structured comparison where applicable, with ablations that isolate representation, retrieval and scoring. Evaluate rank and score agreement, screening false positives/negatives, calibration and abstention, perturbation sensitivity and transport. A pooled correlation alone cannot decide the best method.

Freeze decision criteria before inspecting empirical results. Record uncertainty and missingness. Do not choose a measure because it maximizes a later manuscript coefficient. Preserve the distinction between methodological recommendation, preregistration design and observed validation.

## Additional reference records

REGISTRY_CONTRACTS.json specifies owners and fields for glossary, measure genealogy, benchmarks/datasets, tools/platforms, prompts/rubrics and evaluator-model cutoff records. A registry row requires a stable identity, version or explicit unknown, primary locator, inspection depth and evidence state. Source descriptions of assets do not authorize acquiring or executing them.

For generated comparator distributions, record generator and judge identities, prompts, sampling policy and sample count, selection/filtering, date and seed if disclosed, and dependence on the evaluated producer. Model expectations are not a historical corpus. For MF14, identify the observed corpus and its relationship to actual training data, the overlap unit and denominator, leakage, membership uncertainty and why the result could or could not support a domain-novelty claim.

For official categories, record issuer, jurisdiction, document/edition, effective date and precise criterion. Keep patent anticipation and inventive step, originality, distinctiveness, statistical new-to levels and regulatory classifications distinct. An administrative designation is not a validated continuous novelty measure.

For creator-group audits, document the target criterion and its uncertainty, relevant group/context definitions, sample sizes, exposure, error/calibration estimates and intervals, threshold consequences, and limits of identification. An observed group difference alone cannot identify measurement bias or a difference in latent novelty. No new demographic data collection is included.

The additional walkthroughs distinguish patent research measurement from legal conclusions; divergent-thinking task-relative originality from broader historical novelty; and AI-generated scientific contribution from correctness, feasibility and producer self-assessment. Derivative-work protocols record multiple/uncertain antecedents; games protocols audit database coverage before a bounded first-occurrence claim.
