# Choosing a source for a demonstration

The comparison uses the dated profiles and their linked documentation. It assesses what each source makes observable, how records can be linked, and whether access and reuse are practical. The proposed tasks below have not been run.

## When a released field changes the choice

The [CFPB profile (D17)](../data/profiles/D17.md) records the removal of complaint narratives in the provider’s September 2026 release. Structured complaint fields remain, so the database remains useful for structured analysis and as a source-change example. It cannot supply the proposed current complaint–response text task.

[Google Local (D02)](../data/profiles/D02.md) is the next candidate because it documents review text and business responses with dates. Its reuse terms remain unresolved; selecting it is conditional, not an acquisition result.

## Three useful starting points

| Source | Demonstration it could support | Main boundary |
|---|---|---|
| [SEC EDGAR (D09)](../data/profiles/D09.md) | Link disclosures to issuers and disclosed events using stable filing and issuer identifiers. | Disclosure dates are not necessarily decision dates; third-party exhibits have separate rights. |
| [AMI (D12)](../data/profiles/D12.md) | Reconstruct meeting episodes from time-aligned discussion and annotations. | Scenario roles are not organizational authority; licensing varies across annotation layers. |
| [Open Food Facts (D07)](../data/profiles/D07.md) | Compare product labels, ingredients and structured attributes. | Snapshot differences do not establish launch dates or historical firstness; database, contents and images have distinct licenses. |

Other strong text candidates are [Federal Register (D10)](../data/profiles/D10.md) for regulatory framing and stated obligations, [Food.com (D03)](../data/profiles/D03.md) for recipe recombination, [Amazon Reviews (D01)](../data/profiles/D01.md) for linked evaluations and product attributes, and [PatentsView (D08)](../data/profiles/D08.md) for innovation comparisons. Their profiles retain the relevant reuse, sampling and access conditions. Regulatory text is not implementation, and patent records do not cover all innovation.

## Replication, process traces and context

| Source | Comparative judgment | Main boundary |
|---|---|---|
| [Doshi–Hauser (D20)](../data/profiles/D20.md) | Preferred portable creativity-replication candidate: CC0, a compact processed package and two documented reproduction routes. | Execution is untested. |
| [Noy–Zhang (D14)](../data/profiles/D14.md) | Concrete access evidence makes it a promising replication candidate; D20 has clearer reuse terms. | Snapshots and grades do not reveal hidden motives; terms and runtime fidelity remain unresolved. |
| [CoAuthor (D19)](../data/profiles/D19.md) | Strong writing-process source: observable suggestion, acceptance, dismissal and editing events. | Dataset reuse is unresolved; private criteria, attention and stopping reasons remain unobserved. |
| [GLEIF (D23)](../data/profiles/D23.md) | CC0 legal-entity identifiers, accounting-parent relationships and explicit missingness categories complement SEC records. | Not all organizational control or history is represented; a SEC join has not been established. |
| [O*NET (D22)](../data/profiles/D22.md) | Versioned task descriptions and ratings support instrument and measurement design under CC BY 4.0. | They do not directly measure adoption, automation or authority. |
| [BPI Challenge (D21)](../data/profiles/D21.md) | Operational event logs could support handoff, rework and duration analysis. | Legacy reuse terms remain unresolved. |
| [SocioPatterns (D24)](../data/profiles/D24.md) | Small CC0 temporal-network contrast helps test what a process measure means. | Physical contact is not the same as collaboration. |
| [WildChat annotations (D25)](../data/profiles/D25.md) | Observational complement to controlled writing studies. | Model-generated labels, filtering and missing analysis code need validation. |

D20, D23 and D22 are the clearest preparation priorities for portable demonstrations. D19 with D20 is a useful creative-process pairing if CoAuthor’s data terms are resolved. These priorities depend on the intended task; they do not replace the substantive strengths of SEC, AMI or Open Food Facts.

[WikiConv (D13)](../data/profiles/D13.md) is useful when editing and conversational state changes matter. [QASPER (D16)](../data/profiles/D16.md) supplies a compact evidence-grounding fixture alongside a substantive task; [UCI (D18)](../data/profiles/D18.md) supplies a structured control. The [hybrid-work replication package (D15)](../data/profiles/D15.md) has explicit licensing, but its file inventory and joins remain unverified.

## Release details that matter

The [PatentsView profile](../data/profiles/D08.md) distinguishes current ODP access from legacy delivery. The [RecipePairs profile](../data/profiles/D04.md) distinguishes the much larger hosted dataset from the smaller SHARE benchmark: they are not interchangeable. These are reasons to select and freeze a specific release before running a proposed task.

All judgments above belong to this review. Provider evidence and exact locators remain in [the source records](../data/evidence.jsonl), with dated qualifications in the individual profiles.
