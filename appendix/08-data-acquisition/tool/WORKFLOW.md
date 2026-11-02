# Agent instructions: acquiring a large public text source as a fixed, checkable collection

These instructions are for a research agent working under a researcher's direction, and for the researcher reading what the agent did. The program is `acquire.py`; the source-specific rules live in one adapter module under `adapters/`. Every stage writes files a reviewer can open; nothing is kept only in memory or in a conversation.

## The rule that governs every stage

A document is in the collection only when (1) the source's own index listed it, (2) a file for it was opened and found to be a real document of that identity, and (3) its size and SHA-256 are on its inventory line. A document the index lists but whose text could not be obtained stays in the inventory as a gap. Nothing is written when a check fails; the failure is written instead.

## Stage 1: define the source

Decide, and record in `run/source.json` by running `acquire.py define`:
- the adapter (the provider and its index and text addresses);
- the window and the filters: the default is no filter, every document the index lists, because a keyword or agency filter decided before reading is a sampling decision the study must defend;
- the identity rule the provider uses (for the Federal Register: publication date + document number);
- the text sites to try and the order; the delay between requests (default one second) and the retry policy.
Tell the researcher the expected size (the index gives counts) before retrieving anything large.

## Stage 2: retrieve

`acquire.py retrieve` lists every identity in the window from the index into `run/frame.tsv` (frozen; listed once), then downloads each text into `run/raw/<date>__<number>.txt` with a sidecar `.json` recording site, address, HTTP status, time, size, SHA-256 and every attempt. The stage is resumable: files already held and matching their sidecar are skipped. A response is kept only if it passes the adapter's checks (HTML wrapper, the document's own number, the source's marker); a blocked or error page is logged as rejected and the next site is tried. Read `run/retrieve_log.tsv` afterwards and report the counts of captured, rejected and without-text to the researcher. Do not raise the request rate to finish faster; if the site blocks, stop and say so.

## Stage 3: inventory

`acquire.py inventory` opens every raw file again, independently of the sidecars, applies the adapter's checks, and writes `run/inventory.tsv` with one line per identity in the frame: text lines carry site, pass, time, size, SHA-256 and the counted defects (image placeholders, coded e-mail addresses); gap lines carry the status `pdf_only` and nothing else, with the reason in `run/problems.tsv`. Report the totals and every problem. A gap is a finding, not a failure of the run: it stays in the denominator.

## Stage 4: normalize

`acquire.py normalize` writes a reading copy of each text into `run/clean/` with `clean_text.py` (text out of the wrapper, coded e-mail addresses restored, tags removed, entities unescaped, line endings normalized) and an index of their sizes and hashes. The raw file is never changed. Say in the report what normalization cannot do: it does not restore images and does not interpret anything.

## Stage 5: package

`acquire.py package` writes the collection tree (`run/collection/manifest/YYYY-MM.tsv`, `COVERAGE.json`, `packs.tsv`) and one deterministic pack per month in `run/packs/`, using the retained collection's pack builder: sorted members, fixed owner and times, one xz stream; the same files give the same pack bytes with the same xz library.

## Stage 6: verify, then compare

`acquire.py verify` re-hashes every raw file against the inventory and runs `verify.py` over the packs (size and SHA-256 of each pack against the pack list; every member re-hashed against its inventory line; members missing, unexpected or doubled reported). `acquire.py compare --retained <manifest>` matches the run's inventory against a retained manifest for the same window: identities only in one or the other, status differences, identical bytes, bytes that differ. Report the outcome table and, for every `bytes_differ`, open both records before offering an explanation; a difference can be a provider correction, a delivery-network change or a defect of the run, and only the files say which.

## Adapting to a new source

Write one module in `adapters/` with: `NAME`; `SITES`; `list_identities(http, start, end, days)` yielding `{date, document_number, ...}` from the provider's own index, partitioned so that no query hits the provider's result cap; `text_urls(identity, site_order)`; `check_text(data, identity)` returning the problems that make a response not a document of that identity; `defect_counts(data)`. Keep the inventory columns; they are what the verifier and the comparison read. Record in the source definition what the provider says about rate limits and reuse, and respect both.

## What to report to the researcher after a run

The window and filters; the frame count; captured, rejected and gap counts with reasons; the defect counts; the verify result; the comparison outcomes if a retained manifest exists; the paths of every file named above. Counts are document records (identities), not files on disk and not substantive units such as rules or organizations.
