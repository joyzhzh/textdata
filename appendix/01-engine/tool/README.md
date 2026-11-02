# Scout skill and offline validator

The scout skill packages instructions, a search contract and a validator for bounded literature and software inquiries. A researcher or agent follows the procedure with access to sources; the validator itself runs offline.

| File | Purpose |
|---|---|
| `scout/SKILL.md` | Define the question, select a run type, search and screen, record located claims, and state honest limits. |
| `scout/references/lean-search-contract.md` | Required scope and record fields, search boundaries and stopping rules. |
| `scout/scripts/validate_lean_bundle.py` | Check parseability, identifiers, references, required fields and claim language. |

## Run

From `appendix/01-engine/`, using Python 3.9 or later:

```sh
python3 tool/scout/scripts/validate_lean_bundle.py example/campaign
```

Expected: twelve `PASS` lines, `ARTIFACT GATE: PASS`, `CLAIM CEILING: PASS`, and a `bundle_sha256` fingerprint. Exit 0 means no failure, 1 means a failed check, and 2 means a usage error. No packages, network or model are needed. `--partial` checks the available files of an unfinished bundle.

## Scope

This package supplies the lean `high-recall-map` path and its worked example. The included validator is version 0.5.2; the example was produced using 0.5.1 and checked with 0.5.2. Other modes named in the instructions require materials not included here and have not been demonstrated by this example. The skill remains a supervised draft, without formal performance evaluation.

The validator checks structure and permitted claims, not recall, coverage or source interpretation. It does not check every work-update or claim-to-version reference. Use it on trusted bundles: this version does not reject checksum entries outside the bundle folder; invalid UTF-8 produces a Python error. It only reads files.

The instructions use a neutral package name and “researcher” for the human director. Code is Apache-2.0; project-authored instructions and records are CC BY 4.0. See [NOTICE.md](../NOTICE.md).
