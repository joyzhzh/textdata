# Theory-building engine synthesis

synthesis_state: final  
evidence_cutoff: 2026-07-28  
claim_label: high-coverage, effort-bounded map as of 2026-07; not saturated  
decision_scope: design guidance only; no candidate acquisition, installation, or production adoption  

## Design implications

The engine should not search for one external “theory builder” to adopt. The public landscape supports a modular architecture in which:

1. published doctrine defines plural, mode-conditioned standards;
2. reusable machinery represents, traces, and stress-tests intermediate artifacts;
3. generation produces several candidate explanations rather than a single polished answer;
4. venue rubrics remain named, conditional lenses;
5. adversarial review tests contribution and explanatory substance; and
6. a downstream modelling tool would receive explicit rival models and empirical signatures only after conceptual construction has earned that handoff.

The core missing capability is a provenance-preserving orchestration layer from phenomenon to defensible conceptual contribution. The inspected public resources do not establish a validated end-to-end system.

## What the landscape changes

### Quality should be a profile, not a scalar

The evidence supports several quality ontologies: falsifiability and utility with component tests (`clm-doc-013-01`, `clm-doc-013-02`); importance, interestingness, actionability, generality, simplicity, and accuracy with explicit trade-offs (`clm-ven-020-01`, `clm-ven-020-02`); originality and utility with scope and prescience (`clm-grf-008-01`); and a creator-led social-work scale with nine domain-specific criteria (`clm-mch2-006-01`, `clm-mch2-006-02`).

The engine should store a **quality profile**:

- criterion identifier and definition;
- source and exact claim locator;
- applicable theory mode, genre, domain, and venue;
- evaluator verdict plus rationale and counterevidence;
- confidence and independence;
- unresolved trade-offs; and
- human adjudication status.

It should not average distinct criteria into an unexplained score. A contribution can be simple but narrow, surprising but weakly grounded, useful but not revelatory, or accurate but uninteresting; those differences are decision-relevant.

### Theory mode must be chosen before machinery

The retained doctrine recognizes propositional, configurational, process, perspectival, metatheoretical, provocative, and critical forms (`clm-doc-003-01`, `clm-doc-003-02`). Configurational theorizing has scoping/linking/naming heuristics (`clm-grf-003-01`); process theorizing permits several analysis strategies but still requires a creative leap (`clm-grf-005-01`, `clm-grf-005-02`); proposition-centric grammar has known inferential limits (`clm-adv-004-01`, `clm-adv-004-02`).

Therefore:

- QCA or SetMethods belongs in configurational work, not as a generic theory evaluator (`clm-mch-003-01`, `clm-mch-003-02`; `clm-aut-007-01`, `clm-aut-007-02`).
- Causal-loop or cognitive maps belong where feedback, causal structure, or stakeholder concept systems are theoretically warranted (`clm-mch-001-01`, `clm-mch-002-01`, `clm-aut-005-01`).
- Propositions and hypothesis ladders belong only after a propositional mode is admitted.
- Critical, metatheoretical, process, and perspectival modes require distinct artifacts and review questions rather than being treated as incomplete hypothesis papers (`clm-adv-006-01`, `clm-adv-006-02`).

### Intermediate representations should interoperate without becoming the theory

The strongest reusable machinery concerns explicit representations and lifecycle controls. `theorytools` documents prose-to-IF–THEN-to-graph formalization, versioning, coherence checks, and hypothesis derivation (`clm-mch2-012-01`, `clm-mch2-012-02`). FAIR theory adds documentation, version control, archive, and metadata steps (`clm-aut-001-01`, `clm-aut-001-02`). Theory maps and argument maps expose construct and argumentative relations (`clm-aut-002-01`, `clm-grf-006-01`, `clm-grf-006-02`).

The engine should maintain a common semantic spine:

```text
phenomenon/puzzle
  → construct definitions and aliases
  → claims and warrant links
  → mechanisms, processes, configurations, or interpretive relations
  → assumptions and boundary conditions
  → rival explanations and disconfirming observations
  → contribution claim and audience
  → empirical signatures or conceptual consequences
```

Prose, graphs, maps, propositions, and diagrams should be views over that spine. The classic warning remains binding: references, variables, data, diagrams, and hypotheses can support theory but are not themselves theory (`clm-idx-008-01`).

## Recommended engine architecture

### Stage 0 — phenomenon and evidence intake

Require:

- a bounded phenomenon or problem statement;
- target domain, audience, and intended contribution type;
- an evidence packet with stable source identities and claim-level locators;
- known empirical regularities, anomalies, tensions, and negative cases; and
- a declaration of unsupported speculation.

Do not begin from “find a gap.” Gap spotting is common in the reviewed organization-studies sample, while problematization deliberately interrogates assumptions (`clm-sur-025-01`, `clm-sur-025-02`). The engine should offer gap, problem, phenomenon, paradox, and stakeholder-consequence starts and record which one was chosen.

### Stage 1 — mode and genre admission

Generate a short candidate set of theory modes and genres. For each, record:

- why it fits the phenomenon;
- required representation and evidence;
- what it can and cannot explain;
- venue or audience compatibility;
- failure risks; and
- a reject/retain verdict.

This is where propositional, process, configurational, critical, metatheoretical, and other forms diverge (`clm-doc-003-01`, `clm-doc-003-02`). Genre-specific templates enter only after this gate.

### Stage 2 — construct and relation registry

Create versioned construct records with definitions, scope, aliases, level, time, observable implications, source grounding, and semantic relations. Require explicit distinctions between constructs and variables and between mechanism, association, process, configuration, and interpretation.

Use the representation ideas in `theorytools`, Theory Maps, argument mapping, and causal mapping as adapters rather than as the governing ontology (`clm-mch2-012-02`, `clm-aut-002-01`, `clm-grf-006-01`, `clm-mch-001-01`).

### Stage 3 — plural candidate explanation generation

Produce several structurally different explanations. Each candidate should specify:

- focal outcome or understanding target;
- constructs and relations;
- causal mechanism, process, configuration, or interpretive logic;
- assumptions and boundary conditions;
- rival explanation;
- potential disconfirming observation;
- distinctive contribution; and
- evidence links plus unsupported elements.

Asta is relevant as a reference for literature-linked generation and schema design (`clm-mch2-005-01`, `clm-mch2-005-02`), but its self-documented judge and corpus cannot serve as the engine's authority. Public prompt packs may contribute prompt patterns (`clm-mch2-007-01`, `clm-mch2-008-01`) only after local benchmark and provenance controls exist.

### Stage 4 — adversarial theory review

Run separate reviewers for:

- explanatory substance versus relabeling;
- construct clarity and semantic drift;
- mechanism or process completeness;
- scope and boundary conditions;
- rival explanations and underdetermination;
- contribution originality and utility;
- evidence grounding and citation stripping;
- venue or genre fit; and
- mode-specific failure tests.

Preserve dissent. Interestingness must not override scientific warrant (`clm-adv-002-01`), and mandatory theory rhetoric must not erase the value of description or pretheoretical facts (`clm-adv-007-01`, `clm-adv-007-02`).

### Stage 5 — contribution and manuscript architecture

Only surviving candidates proceed to conceptual-paper construction. The composer can use:

- AMR's common-ground/complication/concern/course-of-action/contribution structure (`clm-grf-001-01`, `clm-grf-001-02`);
- nonalgorithmic introduction positioning (`clm-grf-002-01`);
- the iterative seven-exercise workflow (`clm-doc-008-01`, `clm-doc-008-02`);
- proposition-set checks when that mode is selected (`clm-sur-022-01`, `clm-sur-022-02`); and
- named venue rubrics rather than a blended rubric (`clm-mch2-014-01`, `clm-mch2-015-01`, `clm-bks-002-01`, `clm-bks-002-02`).

The output should retain links from prose paragraphs and figures back to constructs, claims, warrants, assumptions, and reviewer verdicts.

### Stage 6 — modelling handoff

For theory modes that imply empirical discrimination, translate each surviving conceptual explanation into:

- rival model specifications;
- shared and differentiating constructs;
- predicted signatures and boundary conditions;
- decisive and merely supportive observations;
- likely measurement or identification threats; and
- recovery plans when evidence is inconclusive.

The [modelling tool] should reject handoffs that contain only prose labels or a single favored model. Conceptual uncertainty should remain visible rather than being laundered into formal precision.

### Stage 7 — human gate and freeze

Human adjudication is required for:

- the phenomenon's importance;
- mode and genre choice;
- normative or stakeholder commitments;
- contribution and novelty;
- acceptable speculation;
- venue targeting;
- unresolved reviewer disagreement; and
- any promotion from exploratory machinery to production use.

Freeze the accepted theory package with hashes, provenance, version relations, claim locators, dissent, and a statement of unresolved weaknesses.

## Adoption posture

### Reference or adapt now

- Use the FAIR and `theorytools` lifecycle concepts to design versioned theory artifacts, without assuming the package determines substantive quality (`clm-aut-001-01`, `clm-aut-001-02`, `clm-mch2-012-01`, `clm-mch2-012-02`).
- Adapt Theory Maps and argument maps as optional views over the engine's semantic spine (`clm-aut-002-01`, `clm-aut-002-02`, `clm-grf-006-01`).
- Encode AOM, OMT, and AMP criteria as separately named rubric profiles (`clm-mch2-014-01`, `clm-mch2-015-01`, `clm-bks-002-01`, `clm-bks-002-02`).
- Extend the [review skill] with sourced quality criteria and adverse tests, preserving conflicts rather than collapsing them.

### Pilot only after a dedicated evaluation brief

- Asta's literature-linked generation and evaluation schema (`clm-mch2-005-01`, `clm-mch2-005-02`);
- the UTD and AMR-oriented prompt packs (`clm-mch2-007-01`, `clm-mch2-008-01`);
- the System Dynamics Bot (`clm-aut-005-01`, `clm-aut-005-02`);
- CMAP3, groupwisdom, QCA, and SetMethods for admitted mapping or configurational modes (`clm-mch-001-02`, `clm-mch-002-01`, `clm-mch-003-01`, `clm-aut-007-01`).

Each pilot needs fixed tasks, expert-produced references, blinded review, failure categories, provenance checks, maintenance/security review, and an explicit stop rule. This campaign performed no installation or runtime test.

### Do not promote as authority

- repository popularity, stars, downloads, or search ranking;
- creator-authored claims of accuracy or novelty without independent evaluation;
- LLM-as-judge scores without calibration and consequential-error analysis;
- venue-mimicking templates presented as venue endorsement;
- generic proposition count, diagram density, citation volume, or polished prose as proxies for theory quality.

## Minimum credible vertical slice

A useful next build should remain small enough to evaluate:

1. Accept one bounded organization/management phenomenon with a verified evidence packet.
2. Admit three candidate theory modes, including at least one non-propositional mode.
3. Generate three rival explanations per admitted mode.
4. Represent constructs, relations, assumptions, boundaries, contribution, and evidence in one versioned schema.
5. Render at least two views, such as prose plus theory or argument map.
6. Run the [review skill] with sourced, mode-specific rubric profiles and preserve disagreements.
7. Produce one conceptual-paper skeleton for the surviving candidate and one [modelling tool] handoff where empirical signatures are warranted.
8. Have independent qualified reviewers score grounding, explanatory gain, mode fit, construct clarity, rival handling, and error severity against a human baseline.

Success should mean traceable reasoning, useful differentiation among candidates, and recoverable failure—not merely fluent output.

## Research and validation backlog

1. Build a rights-cleared, provenance-rich benchmark of theory excerpts and intermediate artifacts spanning several theory modes and quality levels.
2. Establish expert-review protocols with inter-rater agreement, adjudication, and explicit domain or venue conditioning.
3. Test whether theory maps, argument maps, and formal schemas improve diagnosis or merely make weak reasoning look orderly.
4. Compare human-only, machine-assisted, and machine-generated workflows on the same bounded phenomena.
5. Measure hallucinated grounding, construct drift, circular mechanisms, unfalsifiable boundary escape, rival suppression, and novelty inflation.
6. Develop machinery for process, critical, metatheoretical, perspectival, and other non-propositional modes.
7. Run a separately scoped multilingual backstop if future phenomena or target literatures warrant it.
8. Revisit unresolved repositories and paywalled sources only under a new authority and access decision.

## Decision

Do not install or canonize a public theory-building repository from this scout. Use the evidence ledger to design a modular theory-construction layer that is doctrine-backed, mode-aware, provenance-preserving, adversarial, and human-gated; then evaluate a bounded vertical slice before integration with [the producing project's writing skill], [its review skill], or [modelling tool].
