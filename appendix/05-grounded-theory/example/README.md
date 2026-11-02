# Worked example: how an interpretation changes

[Read the trace](output/TRACE.md) from an initial proposition, through contrary accounts and category revisions, to the distinction between an acceptable result and authorization to act. Every step names its supporting records. The final sampling request remains a proposal.

From the component folder:

```bash
python3 example/trace_comparison.py
python3 checks/verify_counts.py
```

Python 3.9 or later; standard library only; no network or model. The first command reproduces the trace and the second checks its bytes, counts and retained inputs.

`input/study/` supplies the seven analytical row files, source bindings, selection records, analytical account and review. The row files are unchanged from their seal; two manifests are redacted derivatives. The original duplicate handoff is kept privately. Current packet bytes are listed in `RELEASE_SHA256SUMS`.

Transcripts are not supplied. Readers can follow the analytical chain here, but checking its source interpretations requires the same transcripts. This is an inspectable record of the study; the [synthetic example](../tool/examples/synthetic/) is the self-contained runnable demonstration.
