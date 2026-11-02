# Using the Gioia toolkit

The toolkit is a set of instructions for an AI agent, four adaptable working records, a selected bibliography and one program. It helps a researcher move from supplied excerpts towards concepts and a data structure in the manner of Gioia, Corley and Hamilton (2013): the agent proposes, the researcher decides, and what participants said is kept apart from what the analyst makes of it. Version 0.1.1.

## What it does

| Task | Result |
|---|---|
| Develop an analytic memo | Linked expressions, proposed concepts, rivals, negative cases, and unresolved questions |
| Review a data structure or process model | Explicit aggregation choices and separate warrants for temporal or causal relationships |
| Organize supplied references | Separate work and version identities, access, source status, permissions, and maintenance proposals |
| Check quotation wording | Exact byte, character and line spans, matching version IDs, ambiguity, hash drift, and unchecked records |

Start with `tool/skills/gioia-methodology/SKILL.md`. It routes to one of four guides under `references/` (analysis, corpus, quote-check, limits) and to the working records in `assets/working-templates.md`. A short question does not require a completed form.

## Use with an agent

Give an assistant that can read files the path to `tool/skills/gioia-methodology/SKILL.md` and the excerpts or reference records it may use. Assistants that support a skills directory can take `tool/skills/gioia-methodology/` as a skill. A request looks like:

```text
Use the gioia-methodology skill on these authorized interview excerpts.
Propose a short analytic memo. Keep participant expressions separate
from your concepts, include a rival and negative case, and leave
adoption pending. Do not force a completed three-level hierarchy.
```

Other useful requests: review proposed category links, distinguishing membership, temporal order and causation; compare reference entries without merging same-title versions; check a proposed quotation against supplied text versions and say which version matches.

Reading the Markdown needs no Python. Running the quotation checker needs Python 3.9 or later on macOS or Linux (it relies on no-follow directory opens), local file access and nothing else. It makes no network requests.

## Run the quotation checker

```sh
python3 tool/skills/gioia-methodology/scripts/check_quote.py example/input/request-1-bundled-exact.json
```

Expected: a JSON report with `fidelity: EXACT_SINGLE`, matching ID `synthetic-v1`, exit code 0. The checker reads the named files and writes its report to standard output; it never changes the source text.

For your own material, copy `tool/skills/gioia-methodology/assets/quote-request.json` into a working directory beside the text, record who permits local processing and on what basis, compute the whole-file SHA-256 of the text, and use text paths relative to the request (no parent traversal, no symbolic links). The guide `references/quote-check.md` explains each field and each result. Blocked or prohibited records can stay in the request without paths or hashes; their match counts stay unknown, never zero.

| Exit | Meaning |
|---|---|
| 0 | One exact match within the fully checked declared set |
| 1 | Another valid result: ambiguity, no exact match, or incomplete scope |
| 2 | Invalid request or command usage |
| 3 | Helper failure or report-delivery failure |

Always read the JSON. An exact match can occur inside a word, in an older version, or in a passage that does not support the intended reading. Omitted segments need one request per segment and a separate check of their order.

## Tests

```sh
python3 -m unittest discover -s tool/tests -t tool/tests -v
```

The suite has 39 tests of the checker: exact and altered quotations, overlapping and multibyte spans, versions, blocked and prohibited records, unsafe paths, strict JSON, metadata preservation and output failures. They retain their synthetic fixtures under `tool/.test-artifacts/`, which is ignored. They establish bounded mechanical behaviour, not improved qualitative analysis or interpretive accuracy.

## Scope

An independent implementation informed by the Gioia methodology, not a product of its authors. Generated concepts remain proposals; adoption or agreement does not establish interpretive validity. The checker compares retained UTF-8 bytes. It does not extract PDFs, authenticate sources, choose an authoritative version, clear reuse rights or judge meaning. Corpus maintenance produces proposals and moves, merges, publishes and deletes nothing. The package contains no article corpus and no participant data. Further limits: `references/limits.md`; methodological sources: `references/bibliography.md`.
