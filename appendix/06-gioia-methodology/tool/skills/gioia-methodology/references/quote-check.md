# Exact local quotation check

Use `scripts/check_quote.py` when the requested operation permits inspecting a retained UTF-8 text file. Python 3.9+ and a POSIX system with no-follow directory opens are required; there are no third-party runtime dependencies. The helper reads explicitly named files and emits JSON to stdout. It does not extract a PDF, access a network, write a report, normalize text, repair a quote or update a record.

## Prepare the request

Use the [JSON template](../assets/quote-request.json). Set the actual candidate quote. For an available, permitted text file, supply its relative path and recorded whole-file SHA-256. If no binding exists yet and the read is authorized, compute one with `shasum -a 256 /path/to/retained.txt` (or `sha256sum`), recording who/when/basis; retain any other-basis hash separately. Do not replace an expected binding with a value from a mismatch report. Keep the request in an authorized working directory; text paths must be relative children of that directory, without parent traversal or symlink components. Do not copy restricted material just to satisfy this layout. If needed, place a new request beside the permitted retained text, within the authorized write scope.

Only set `access` to `available` and `permissions.local_processing` to `permitted` when those statements are supported for this operation, including applicable participant-use restrictions. A nonempty `local_processing_basis` records that decision. The helper trusts this declaration; it cannot resolve a contradictory or false permission claim. Unknown/blocked access and unknown/prohibited local processing are not checked, with `match_count: null`, never zero. Quote reuse may remain unknown even where a local fidelity check is permitted; no result clears reuse.

When converting a [reference entry](../assets/working-templates.md), map `manifestation.id` to `id`, `manifestation.retained_locator` to `text_path` only if it is a permitted relative text path, `manifestation.hash.value/basis` to `sha256/hash_basis`, and `access.state` to the request's string `access`. Carry `permissions.local_processing_basis` through explicitly; general `evidence_and_scope` does not substitute for the operation-specific permission decision. Preserve other provenance and restrictions as metadata.

Every row needs a distinct ID and a permissions object. Unavailable/unknown access or unknown/prohibited local processing may use null path/hash; keep these rows in the request as unchecked. Only rows eligible for checking require a path, lowercase 64-character SHA-256 and `hash_basis: whole_file_bytes`. The helper preserves supplied metadata without adjudicating it; unknown identity/version remains unknown. It rejects duplicate IDs/JSON keys, non-finite JSON numbers and whitespace-only quotes. Two IDs sharing a path remain two declared records, not proof of independent versions.

Hashes of a JSON object, normalized text or a PDF cannot substitute for the input text file's hash. An unsupported basis on a row eligible for checking invalidates the whole request. If no authorized whole-file binding can be supplied, keep the excluded ID/basis and `not_checked: unsupported_hash_basis` in the coverage note, and label any reduced helper request as that subset. Never fabricate a hash, alter an access state or omit an inventory item from the surrounding assessment to obtain a complete result.

Run from any directory using the actual package and request paths:

```sh
python3 /path/to/gioia-methodology/scripts/check_quote.py /path/to/work/quote-request.json
```

Review stdout before recording its result. Save to a new, authorized output file if needed; do not redirect over an input or predecessor. Requests contain the candidate quote and the report preserves supplied metadata; handle both within the same applicable data-use boundary.

## Interpret the output

| Result | Meaning |
|---|---|
| `EXACT_SINGLE` | One literal contiguous match across the fully checked declared set; `matching_manifestation_ids` names the record. Confirm its version is the one being cited. Still not interpretation or reuse clearance. |
| `AMBIGUOUS_MATCHES` | More than one occurrence in one manifestation; every match is returned, including overlaps. Inspect context; the helper chooses none. |
| `AMBIGUOUS_MANIFESTATIONS` | Matches in multiple supplied manifestations, even if they claim the same work or have identical bytes. No version is chosen or merged. |
| `NO_EXACT_MATCH` | Fully checked declared text has no exact span. Reject the candidate as an exact quotation of those bytes; do not infer absence elsewhere. |
| `NOT_ESTABLISHED` / `*_INCOMPLETE_SCOPE` | One or more inputs were not checked. A match in a checked file does not establish uniqueness across unchecked files. |
| Per-item `HASH_MISMATCH` | Current bytes differ from the supplied binding. Matching is skipped; record drift rather than silently rebinding. |
| Per-item `NOT_CHECKED_ACCESS`, `NOT_CHECKED_LOCAL_USE` | The declared operation is not established as available/permitted; the text is not opened. |
| Per-item `UNREADABLE_OR_UNSAFE_PATH`, `NOT_UTF8_TEXT` | Path/read/type restriction or decoding failure; not evidence of absence. |
| `INVALID_REQUEST` | Malformed request; no valid quote-check report. |
| `HELPER_ERROR` | Unexpected helper failure; no valid quote-check result. |

Exit **0** means only `EXACT_SINGLE` within the complete declared set; **1** means another valid result, including ambiguity; **2** means invalid input/usage; **3** means a helper or report-delivery failure. Treat missing, partial or unparseable stdout as no result regardless of exit code. A valid report includes `request_sha256` over the request's whole bytes. Record its path, matching manifestation/version and selected spans in the memo. `scope_complete` covers only the declared set, not the entire inventory. Do not use exit 0 as an admission, rights or scientific acceptance gate.

Offsets use raw UTF-8 bytes and Unicode code points separately, both zero-based with exclusive ends. Lines are one-based, delimited by LF, and are not printed or PDF page numbers. CRLF bytes are preserved. If text was extracted, record the parent and extraction relation separately: the helper verifies the derivative's supplied hash only. It cannot detect a spliced or inaccurate derivative whose own hash has been accepted.

There is no Unicode normalization, whitespace collapse, punctuation repair, case folding or ellipsis expansion. Visually similar but differently encoded text fails an exact test. A substring may begin/end inside a word or multi-code-point symbol; inspect its boundaries in context even after exit 0. Inserted text or reordered pages change the hash before matching. All matches are returned without a silent cap; highly repetitive files can produce large reports.

For deliberate omissions, run one request per exact segment. Select spans from the same manifestation/version and verify that each later segment starts at or after the previous segment ends, in the order proposed. Record each report and the omitted byte ranges in `quote_checks`, then review the gaps for meaning and attribution. Two individually exact segments do not establish their order or support the composite. Never report an ellipsised composite as one contiguous `EXACT_SINGLE` quote.

After locating text, review context, attribution, selection and support for the actual claim. Keep `contextual_adequacy`, `interpretive_assessment` and `reuse_clearance` separate from literal fidelity; the helper always leaves them unassessed or undetermined.
