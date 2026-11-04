# Large-scale data acquisition

[Example files](example/) · [Use with your AI](AI-PROMPT.md)

A working Federal Register adapter turns a publication window into an inventory, reading copies and verified text packs. It retains a document’s identifier when text is missing, so a sampling frame does not silently exclude unreadable documents. The included monthly inventories cover 806,941 document records from January 2000 through 15 September 2026: 806,237 with text and 704 without.

## Try the example

With Python 3.9 or later, from this folder, no network or model is needed:

    python3 example/run_example.py
    python3 example/compare_sites.py
    python3 checks/verify_counts.py

The example covers 7–8 December 2020. The original comparison recovered all 191 identifiers: 169 raw files matched the historical inventory and 22 differed for an unresolved reason. Reading copies agreed across both official sites for all 191 documents.

The supplied text is email-redacted. Its offline replay reproduces the released outputs and compares 61 unchanged / 130 changed files with historical fingerprints. That is a separate result from the original 169/22 comparison. Original fingerprint records support the historical finding; the original email-bearing text is not supplied. These research copies are not official legal editions.

## Explore the files

- [Workflow instructions](tool/WORKFLOW.md) and [procedure](docs/PROCEDURE.md): define, retrieve, inventory, normalize, package and verify.
- [Inventory index](data/MANIFEST_INDEX.tsv) and [collection guide](docs/COLLECTION.md): all 321 monthly inventories are included in data/inventories/.
- [Example](example/): the two-day input, released text copies and executable replay.
- [Availability](docs/TEXT_PACKS.md), [source/licence notice](NOTICE.md) and [release edition](docs/RELEASE_CHANGES.md).

## What remains proposed

Integration with research skills, adapters for additional sources and investigation of the 22 discrepancies remain proposed. The historical listing/download programs were not retained, so full historical acquisition cannot be replayed. Historical text packs are not distributed; the example supplies a small working slice. Images remain placeholders, their counts are lower bounds, and file checks do not establish content completeness or meaning.

Project code and agent instructions use Apache-2.0; project-authored data and documents use CC BY 4.0. Federal Register text retains its own republication basis and third-party qualifications; see NOTICE.md.
