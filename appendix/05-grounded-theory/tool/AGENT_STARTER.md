# Start a bounded grounded-theory analysis

Replace **Study question**, **Input path**, and **Output study path** below,
then paste the prompt into a Codex task with this skill installed. Use absolute
paths, or identify the input relative to the installed skill for the included
synthetic example. The agent resolves the paths and handles packet mechanics.

```text
Use the installed grounded-theory skill to carry out a bounded analysis through a local handoff.

Study question: {{study_question}}
Input path: {{input_path}}
Output study path: {{output_study_path}}

Use only these inputs. Reuse applicable recorded rights, privacy, retention and model-processing authority. For real inputs, ask only for genuinely missing facts that gate this work; do not ask me to approve already-authorized steps again. Historical project rulings do not authorize a new dataset. Keep synthetic results clearly labeled SYNTHETIC / INVENTED / NON_RELEASE and real results NON_RELEASE. Preserve source bytes and existing work. Use an unused study directory outside every Git checkout, with a distinct suffix if needed; retain exact source copies there for binding.

Record the question, scope and authority before analysis. Reconstruct episodes and explicit attempt relationships, preserving uncertain links and unknown endings. Link incidents to exact passages, propose source-near codes, make substantive comparisons, keep descriptive/comparison/methodological/theoretical memos distinct, and let counterexamples change or constrain a provisional category. Preserve earlier versions. Draft one discriminating sampling proposal without executing it.

Use the supported helpers for source bindings, validation and handoff. Resolve routine file and schema mechanics yourself. Deliver a short readable DEMO.md with links to the input, meaningful findings, category consequences, checks and limits. Stop at that handoff or an exact evidence/authority limitation. Do not acquire other inputs, contact anyone, launch extra agents, claim saturation or independent review, draft a paper, or start another cycle automatically.
```

For a fully invented practice input, use [cloud_post.txt](examples/synthetic/cloud_post.txt)
as the **Input path** in the prompt above.
The text describes fictional attempts and decisions; it is not research evidence.
No previous analytical answer is provided with it.

Prerequisites: Python 3.9+, Git and the dependencies in [requirements.txt](requirements.txt).
The installed agent performs interpretation; the helpers check source bindings,
declared structure and history. Those checks do not evaluate the truth of an
interpretation. Obtain separate human/independent review before using a
provisional analysis as reviewed research.
