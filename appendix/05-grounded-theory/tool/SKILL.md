---
name: grounded-theory
description: Reconstruct episodes and analyze authorized qualitative traces through source-near coding, constant comparison, versioned memos and categories, negative cases, and discriminating sampling drafts. Use for an inductive process study using grounded-theory techniques and its analysis handoff; does not acquire data or certify saturation.
---

# Grounded Theory

Help the analyst build an inspectable account from authorized qualitative data.
Use the label **inductive process study using grounded-theory techniques**.
Treat the model's codes and explanations as proposals to inspect against sources.

## Choose the work

| Mode | Result | Read when needed |
|---|---|---|
| `orient` | Explain choices and draft the study question/boundary; no ingestion | [Method basis](references/methods-basis.md), [study charter](templates/STUDY_CHARTER.md) |
| `prepare` | Freeze exact authorized input bindings and a new external cycle | [Local workflow](references/workflow.md) |
| `pilot-code` | Reconstruct episodes, incidents and source-near initial codes within the authorized bound | [Analysis contract](references/grounded-theory-contract.md), [local workflow](references/workflow.md) |
| `compare` | Record substantive comparisons, negative-case consequences and successor category/memo versions | [Analysis contract](references/grounded-theory-contract.md), [packet contract](references/analysis-packet-contract.md) |
| `sample` | Draft the contrast that would distinguish a live explanation from its rival | [Packet contract](references/analysis-packet-contract.md), [vault interface](references/vault-interface.md) |
| `integrate` | Propose transitions, mechanisms, rivals, falsifiers and remaining gaps | [Method basis](references/methods-basis.md), [theory memo](templates/THEORY_MEMO.md) |
| `audit` | From a nonproducing seat, inspect source fidelity and reasoning as well as links | [Analysis contract](references/grounded-theory-contract.md) |
| `paper-handoff` | Package current reviewed analysis with its unresolved limits | [Local workflow](references/workflow.md), [vault interface](references/vault-interface.md) |
| `draft-paper` | In an authorized author seat, draft from immutable independently reviewed inputs | [Paper charter](templates/PAPER_DRAFT_CHARTER.md) |

Load the references for the requested mode, not every reference by default.
The [local workflow](references/workflow.md) has runnable commands and a synthetic
example. Python 3.9+ with `jsonschema` is required for the deterministic helpers.

## Start a cycle

Use the user's named study and exact authorized inputs. Record the question,
method profile, rights/privacy/retention and model-processing authority before
reading real data. Reuse existing applicable authorization; ask only for a
missing fact that actually gates the requested action. Revised C001 rulings 4/5
have a specific `license: UNKNOWN` allowance; it is not a global rights waiver.
No real-data pilot is authorized merely by invoking this skill.

Keep the study root outside every Git checkout, with no checkout inside it.
The ignored `.vault-root` points to the local study parent; commands take an
explicit `--study-root`. Source bytes, real prompts and outputs stay there.
`prepare` binds inputs; it does not download or normalize them. Work from
permitted normalized text with exact source/transform links. For raw media,
first produce a separately authorized, traceable normalized export.

## Analyze and preserve decisions

- Keep event order/time separate from presentation time. Record explicit or
  uncertain starts/ends and missing intervals. A trace ending without outcome
  evidence is `UNKNOWN`, never inferred acceptance or abandonment.
- Assign each incident one of the seven [epistemic classes](references/grounded-theory-contract.md).
  Behavior alone cannot establish belief. Creator-stated interpretation needs
  an attributable statement and exact quotation binding; inference stays separate.
- Use action-oriented initial coding; **prefer gerunds where they capture
  process**. Keep source language, working translation, alternatives and rationale
  inspectable. Do not seed initial codes with the project's candidate theory.
- Comparisons name operands, purpose, observation, rival, discriminating evidence
  and analytical consequence. A similarity score or filled template is insufficient.
- Keep **descriptive, comparison, methodological and theoretical** memos distinct.
  Category versions expose properties/dimensions, conditions/consequences,
  support, boundaries and countercases. A negative case needs a reasoned response:
  revise, split, bound, retire, justify retention, or preserve unresolved status.
- Append a new identity with `supersedes` and a reason. Never edit a historical row
  to mark it obsolete; successors determine the current view. Continue a sealed
  cycle into a new directory. No deletion helper is provided.
- Sampling drafts specify opposing expected observations and what an unavailable
  contrast would leave unresolved. They stay `PROPOSED`; acquire nothing and
  contact nobody without separate authority.

The inherited four memo types and gerund preference are operative defaults.
The proposed six-purpose taxonomy and optional-gerund amendment remain inactive,
pending an explicit researcher decision. Memo/version formats and archive sampling
are single-source proposals; they are not validated instruments.

## Review and handoff

Validate byte bindings and declared structure, then inspect analytical fidelity.
Checks can catch broken links, missing attribution bindings, rewritten history
and absent response fields; they cannot judge whether an interpretation is true
or a reason persuasive. The producing seat cannot clear its own analysis.
A named reviewer is a planned role, not proof that review occurred.

State the actual stop reason and missing contrasts. Repeated codes, a fixed
corpus and a budget ceiling do not establish saturation. The strongest tool
state is `PROVISIONAL_SUFFICIENCY_CANDIDATE`, pending independent and human review;
“sufficiency” is inherited vocabulary, not an admitted Dey procedure.

Keep outputs `NON_RELEASE`. A local handoff sends nothing and grants no admission,
publication or release authority. A paper draft must bind substantive claims to
current reviewed inputs; mark author framing and unresolved claims explicitly.
LLM coding studies do not validate this agent's full analytical cycle. The
[method basis](references/methods-basis.md) preserves source scopes and mandatory
recheck qualifications, including the author-staffed evaluation in Q-C5.
