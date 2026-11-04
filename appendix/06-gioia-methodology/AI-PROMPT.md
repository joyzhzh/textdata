# Explore the Gioia Methodology prototype

Help me explore this toolkit for tracing proposed concepts back to source expressions.

Use the supplied files in `appendix/06-gioia-methodology/` (or the attached component folder). All paths below are relative to that folder; [README.md](README.md) is the starting point. If a needed file is unavailable, identify it and ask me to provide it; do not infer its contents.

Within that folder, start with `README.md` and `tool/skills/gioia-methodology/SKILL.md`. Read `example/input/synthetic-episode.txt`, `example/input/memo-synthetic.yaml`, `example/output/request-3-two-speakers.report.json` and `example/output/SUMMARY.json`; use `docs/USAGE.md` for commands and `NOTICE.md` for credit and licences.

Explain the example in plain English: both speakers say “I waited for a reply”, but Speaker B’s later sending decision is unknown. Show how the memo turns that unknown into an unsupported negative case, even though the quotations match. Keep participants’ expressions separate from the assistant’s proposed concepts, rival reading and pending researcher decision.

Guide me through the supplied passage, memo and saved quotation-check reports. Compare the shared phrase with “I waited for a reply too” and the altered quotation in the saved requests, then explain the recorded results. If local execution is available, the two-speaker check is `python3 -B tool/skills/gioia-methodology/scripts/check_quote.py example/input/request-3-two-speakers.json`, run from the component folder; two matches and exit 1 are expected. State which files and results you actually inspected or ran.

Distinguish the completed skill, templates, checker and synthetic demonstration from proposed empirical evaluation. Exact matches do not establish meaning or interpretive validity. Apply the guidance to my authorized excerpts if supplied, leaving analytic decisions to me and unsupported conclusions open.

My research question or material to explore: [insert here]
