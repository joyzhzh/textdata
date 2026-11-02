# Run the acquisition workflow

Use Python 3.9 or later and the standard library. The Federal Register adapter supplies six stages; [agent instructions](../tool/WORKFLOW.md) explain how to use them for a research question.

| Stage | Command | Output |
|---|---|---|
| Define | acquire.py define | Source, publication window and identity rule |
| Retrieve | acquire.py retrieve | Document frame, checked text files and source receipts |
| Inventory | acquire.py inventory | One row per identifier, including missing text |
| Normalize | acquire.py normalize | Reading copies with document headers and fingerprints |
| Package | acquire.py package | Monthly text pack and inventory |
| Verify / compare | acquire.py verify; acquire.py compare | File-integrity results and differences from a reference inventory |

From the appendix folder, replay the supplied example without network access:

    python3 example/run_example.py
    python3 example/compare_sites.py

For a fresh retrieval, define a window and use a new output folder:

    python3 tool/acquire.py all --run my-run --start 2025-01-06 --end 2025-01-07 --retained data/inventories/inventory-2025.tar.xz

This command needs network access. It uses the provider’s index, checks document identities, retries eligible failures and keeps gaps in the inventory. Requests are paced at one per second. A fresh retrieval contains source text as currently served; it is not the email-redacted example edition.

Normalization removes HTML and decodes entities but cannot restore images. Packs use sorted members and fixed metadata; byte identity requires the same xz library. Verification checks bytes and inventory consistency, not meaning or complete source content.

The original two-day comparison found 169 matches and 22 unresolved raw-file differences. The released example removes emails and therefore has a different comparison: 61 matches and 130 differences against historical fingerprints. Keep these two results distinct. The original acquisition cannot be fully replayed; additional-source adapters and integration remain proposed.
