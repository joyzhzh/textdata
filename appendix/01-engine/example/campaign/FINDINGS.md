# Theory-building evidence map — findings

finding_state: final  
scope_id: THEORY-SCOUT-V051-SCOPE-001  
run_type: high-recall-map  
claim_label: high-coverage, effort-bounded map as of 2026-07; not saturated  
cutoff: 2026-07-28  

## Executive finding

Public theory-building support is abundant as doctrine and fragmented as machinery. The doctrine track supplies mature but plural criteria for theory quality, multiple modes of theorizing, and detailed editorial guidance for conceptual papers. The machinery track supplies useful components—formal representations, theory maps, causal and configurational tools, prompt packs, templates, and human-review rubrics—but the inspected public evidence does not establish an independently validated, end-to-end engine for diagnosing, generating, drafting, and reviewing organization or management theory.

The strongest design implication is therefore compositional: treat doctrine as a set of mode- and venue-conditioned constraints, assemble machinery as replaceable modules, preserve provenance at the claim and representation level, and keep human adjudication at contribution, novelty, and venue-fit gates. No cross-track winner was selected.

## Coverage by frozen cell

Counts below are stable work assignments in `EVIDENCE_LEDGER.jsonl`; one work may support more than one cell.

| Cell | Works | Disposition |
|---|---:|---|
| Q-D — theory-quality doctrine | 33 | Strong coverage of criteria, trade-offs, contribution, usefulness, falsifiability, scope, construct clarity, and critiques of novelty or interestingness. |
| Q-M — theory-quality machinery | 13 | Populated but uneven: rubrics, theory representations, package functions, prompt packs, and one creator-led scale; little independent reliability evidence. |
| T-D — theorizing doctrine | 37 | Strong plural-method coverage: disciplined imagination, problematization, abduction, mechanisms, process, configuration, paradox, multiple paradigms, and contextualization. |
| T-M — theorizing machinery | 14 | Useful components for formalization, theory mapping, causal mapping, QCA, literature-driven generation, and prompt-guided workflows; no shared benchmark across components. |
| C-D — conceptual-paper doctrine | 44 | Densest cell: problem framing, contribution architecture, construct and proposition logic, positioning, figures, revision, and venue guidance. |
| C-M — conceptual-paper machinery | 10 | Templates, checklists, argument maps, and prompt packs exist, but most are human-facing or creator-authored and lack outcome validation. |
| O-D — organization/management doctrine | 37 | Strong field-specific doctrine and venue guidance, including explicit support for several non-propositional modes. |
| O-M — organization/management machinery | 12 | AOM/OMT rubrics, AMR-oriented prompt packs, mapping tools, and QCA-class software provide building blocks; domain-native software and corpora remain sparse. |

## Doctrine findings

### 1. Theory quality is multidimensional and purpose-conditioned

The retained doctrine does not reduce quality to novelty, citations, or a single score. One established organization-theory framework places measurement, scope, construct validity, logical adequacy, explanatory potential, empirical adequacy, and predictive adequacy under falsifiability and utility (`clm-doc-013-01`, `clm-doc-013-02`). A recent synthesis instead identifies importance, interestingness, actionability, generality, simplicity, and accuracy and explicitly treats trade-offs among them as a research-program design issue (`clm-ven-020-01`, `clm-ven-020-02`). Corley and Gioia distinguish originality from utility and further discuss scope and prescience (`clm-grf-008-01`).

These are complementary lenses, not interchangeable scales. They imply that an engine should retain criterion provenance, theory mode, intended contribution, and venue or audience before issuing a diagnosis. A flat aggregate score would erase documented trade-offs and normative differences.

### 2. Theorizing is a family of modes, not a proposition-only pipeline

Organizational theorizing includes propositional, configurational, process, perspectival, metatheoretical, provocative, and critical forms with different aims, reasoning, and evaluative terms (`clm-doc-003-01`, `clm-doc-003-02`). The mode-specific methods retained here include disciplined imagination (`clm-idx-022-01`, `clm-idx-022-02`), problematization (`clm-sur-025-01`, `clm-sur-025-02`), configurational scoping/linking/naming (`clm-grf-003-01`), process-data strategies (`clm-grf-005-01`, `clm-grf-005-02`), argument mapping (`clm-grf-006-01`, `clm-grf-006-02`), mechanisms, paradox, multiparadigm work, construct development, contextualization, and abduction.

The evidence also supplies adverse checks against methodological monoculture. Proposition grammar can constrain explanations and motivate triangulation across theoretical grammars (`clm-adv-004-01`, `clm-adv-004-02`). An organization-theory editorial explicitly admits metatheoretical, critical, process, perspectival, and essay forms alongside construct-and-proposition work (`clm-adv-006-01`, `clm-adv-006-02`). Any future engine should branch by theory mode before choosing generation templates or quality tests.

### 3. Conceptual-paper craft is staged, iterative, and contribution-centered

The doctrine converges on recurring operations without establishing a single mandatory sequence:

- decide what belongs in the explanation while managing parsimony against explanatory breadth (`clm-doc-012-01`, `clm-doc-012-02`);
- use exercises iteratively to clarify and concretize the focal scientific argument (`clm-doc-008-01`, `clm-doc-008-02`);
- position the manuscript through common ground, complication, concern, course of action, and contribution (`clm-grf-001-01`, `clm-grf-001-02`);
- make proposition sets clear, consistent, concise, distinctive, coherent, and contribution-bearing when a proposition mode is chosen (`clm-sur-022-01`, `clm-sur-022-02`);
- expose originality and utility rather than equating contribution with a literature gap (`clm-grf-008-01`); and
- preserve a creative theoretical leap even when analysis strategies are disciplined (`clm-grf-005-02`).

This supports an iterative workspace with explicit intermediate artifacts—phenomenon statement, problem framing, construct ledger, mechanism or process account, rival explanation, boundary conditions, contribution claim, argument map, and venue-specific manuscript architecture—rather than one-shot prose generation.

### 4. Adverse doctrine sets non-negotiable guardrails

Several retained works directly challenge common shortcuts:

- gap spotting may be institutionally normalized and can crowd out assumption-challenging questions (`clm-sur-025-01`, `clm-sur-025-02`; `clm-adv-001-01`, `clm-adv-001-02`);
- interestingness alone is not a sufficient scientific virtue and can encourage problematic research practices (`clm-adv-002-01`);
- multiple legitimate theory-contribution traditions use different truth and representation assumptions (`clm-adv-003-01`, `clm-adv-003-02`);
- mandatory theory contribution can undervalue description and pretheoretical fact generation (`clm-adv-007-01`, `clm-adv-007-02`); and
- diagrams, hypotheses, data, variables, and references can support theorizing but do not by themselves constitute theory (`clm-idx-008-01`).

An engine should therefore test whether a claimed contribution changes explanation or understanding, rather than rewarding novelty rhetoric, proposition count, visual complexity, or venue mimicry.

## Machinery findings

### 1. Representation and provenance are the most mature reusable layer

`theorytools` provides documented functions and vignettes for formalizing, versioning, checking pre-empirical coherence, and deriving hypotheses, including movement from prose to IF–THEN statements and a directed graph (`clm-mch2-012-01`, `clm-mch2-012-02`). The FAIR-theory workflow adds implementation, documentation, version control, archiving, and metadata while remaining agnostic between natural-language and formal representations (`clm-aut-001-01`, `clm-aut-001-02`). Theory mapping supplies a visual representation of construct relations plus reusable templates (`clm-aut-002-01`, `clm-aut-002-02`).

These components are well suited to an engine's artifact and provenance substrate. They do not decide which phenomenon matters, which explanation is best, or whether a contribution is consequential.

### 2. Generation machinery is promising but evidence-bounded

Asta documents literature-conditioned and parametric theory synthesis, linked evidence, reusable schemas and stores, and judge-based assessment of accuracy, specificity, novelty, and testability (`clm-mch2-005-01`, `clm-mch2-005-02`). Two public prompt packs expose broad theory-and-hypotheses and AMR-oriented workflows (`clm-mch2-007-01`, `clm-mch2-008-01`). Their public artifacts support claims about documented scope, not independent quality or field transfer.

Accordingly, these assets are reference implementations or pilot candidates. They should not be adopted as quality authorities without frozen test cases, provenance checks, mode-sensitive evaluation, independent review, and explicit failure analysis.

### 3. Mapping and configurational tools cover important but narrower operations

The retained machinery includes comparative cognitive causal mapping and CMAP3 (`clm-mch-001-01`, `clm-mch-001-02`), participatory group concept mapping (`clm-mch-002-01`, `clm-mch-002-02`), QCA and SetMethods (`clm-mch-003-01`, `clm-mch-003-02`; `clm-aut-007-01`, `clm-aut-007-02`), argument mapping (`clm-grf-007-01`), and an LLM system-dynamics bot with a bounded internal evaluation (`clm-aut-005-01`, `clm-aut-005-02`).

These tools can externalize relations, configurations, cases, and feedback structures. They should enter only when the selected theory mode warrants them. A causal-loop diagram, QCA solution, or argument map is an intermediate representation, not an automatic theoretical contribution.

### 4. Human rubrics and templates are plentiful but venue-specific

AOM and OMT reviewer guidance operationalizes theoretical grounding, construct consistency, conceptual logic, proposition support, novelty, positioning, scope, and contribution (`clm-mch2-014-01`, `clm-mch2-015-01`). AOM's reviewer hub, the AMP reviewer template, SLJM structure, the Johannessen/Olsen book, and the Theory Evaluation Scale add further checklists and criteria (`clm-mch2-016-01`, `clm-bks-002-01`, `clm-bks-002-02`, `clm-mch2-004-01`, `clm-mch2-002-01`, `clm-mch2-006-01`, `clm-mch2-006-02`).

They are valuable as named, human-facing lenses. They should remain separated by venue, genre, and disciplinary origin. The evidence does not license blending them into an anonymous universal score.

## Main gaps

1. **No validated end-to-end public engine.** The inspected resources do not jointly demonstrate reliable movement from a phenomenon or puzzle through grounded constructs, plural candidate explanations, contribution adjudication, conceptual drafting, venue fit, and empirical implications.
2. **No mode-balanced benchmark.** Asta exposes useful stores and evaluation schemas, but the campaign did not locate an independently validated organization/management corpus spanning strong and weak examples across propositional, process, configurational, critical, metatheoretical, and other modes.
3. **Weak evidence for automated judging.** Public repositories and rubrics document prompts and criteria; they rarely report blinded, independent agreement with qualified theorists, transfer across domains, calibration, or consequential-error analysis.
4. **Fragmented representations.** Prose, IF–THEN statements, DAGs, theory maps, argument maps, causal-loop diagrams, and QCA configurations are rarely connected by a shared construct, claim, mechanism, boundary, and provenance schema.
5. **Thin non-propositional machinery.** Doctrine explicitly recognizes plural forms, while public machinery remains concentrated in hypotheses, causal relations, graphs, checklists, and manuscript sections.
6. **Venue specificity is often obscured.** Official reviewer criteria are useful but conditional. Third-party prompt packs sometimes imitate venue forms without venue endorsement or outcome evidence.
7. **Two high-value machinery repositories remained unresolved.** Their discoverability was sufficient for screening but not for evidence coding under the public-access and exact-locator rules.

## Limits of inference

- This was an English-primary, public-access, time-capped map. Most open-web, scholarly-index, repository, and citation-graph windows remained partial.
- Search-result snippets and secondary Layer-A material were used only for discovery. Substantive statements in this report trace to claim objects with inspected manifestations.
- Repository documentation establishes documented capabilities, not successful installation, correctness, maintenance quality, usefulness, or independent validation. Candidate assets were not downloaded, installed, executed, imported, or preserved.
- Editorials and reviewer rubrics establish field or venue expectations, not causal effects on theory quality or publication outcomes.
- Citation and author graphs are dependence-prone. Same-work, same-author, creator-hosted, and venue-family relations are recorded in the ledger and should not be mistaken for independent corroboration.
- Positive yield remained at the campaign ceiling. Additional backward/forward traversals, non-English routes, paywalled full text, and empirical validation searches may change the map.
