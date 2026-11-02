# Gioia Methodology

Trace a proposed concept back to the words that prompted it. This working toolkit combines an agent skill, analytic templates and an exact-quotation checker. Its synthetic example shows why correct quotations can still support an incorrect interpretation.

[Try the interactive example](https://textdata.info/toolkit/gioia-methodology/) · [Explore with your AI](AI-PROMPT.md) · [Usage guide](docs/USAGE.md) · [All components](../README.md)

## Worked example

In a six-line synthetic interview, Speaker A reports sending a draft after receiving no reply. Speaker B describes checking figures during the wait. Both say “I waited for a reply”: the checker correctly finds two occurrences, one for each speaker.

An AI-written memo proposes “Proceeding without sign-off” and a rival reading, “Using the wait”. It then treats B as a negative case, claiming the wait was “followed by not sending”. **Whether B sent the draft is unknown.** Exact quotation matching cannot detect this unsupported inference. The original memo remains unchanged, with its proposals awaiting a researcher’s decision.

Read the [passage](example/input/synthetic-episode.txt), compare the [memo](example/input/memo-synthetic.yaml), and inspect the [two-speaker report](example/output/request-3-two-speakers.report.json). The [saved summary](example/output/SUMMARY.json) covers all four requests: one exact match, an altered quotation, two matching speakers, and A’s sentence about the deadline.

## Use it

For concept development, give an assistant the [skill](tool/skills/gioia-methodology/SKILL.md), your research question and authorized excerpts. The [working templates](tool/skills/gioia-methodology/assets/working-templates.md) keep source expressions, proposed concepts, rivals and researcher decisions distinct. The [AI prompt](AI-PROMPT.md) starts with the supplied example.

To run the two-speaker quotation check, use Python 3.9 or later on macOS or Linux. From the repository root:

```sh
cd appendix/06-gioia-methodology
python3 -B tool/skills/gioia-methodology/scripts/check_quote.py example/input/request-3-two-speakers.json
```

Expect `AMBIGUOUS_MATCHES`, two matches and exit 1. The report locates each occurrence; it does not choose a speaker or assess meaning. Character and byte offsets start at zero and exclude the end; line numbers start at one.

To replay all four saved reports and run the 39 checker tests:

```sh
python3 -B checks/verify.py
```

Expect `all counts match` and exit 0. These commands use only local files and Python’s standard library, without a model or network connection. The verifier retains generated fixtures under ignored `tool/.test-artifacts/`. It replays quotation checks, not the generation of the memo.

## What works now and what remains proposed

The skill, templates, checker and synthetic demonstration are available here. The example contains no participant data, and no researcher has adopted its proposed concepts. The software checks literal wording; it does not establish authenticity, reuse rights, contextual support or interpretive validity.

Empirical evaluation with research materials and researcher judgments remains proposed. The example does not demonstrate improved qualitative analysis.

## Sources and licences

This independent implementation draws on [Gioia, Corley and Hamilton (2013)](https://doi.org/10.1177/1094428112452151); it is not endorsed by the method’s authors. See the [selected bibliography](tool/skills/gioia-methodology/references/bibliography.md) and [NOTICE](NOTICE.md) for credit and terms: Apache-2.0 for software and CC BY 4.0 for project-authored documentation and synthetic data. The [manifest](MANIFEST.json) lists the released files and fingerprints.
