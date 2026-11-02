# Notices for the LLM-annotation workflow component

## Third-party material included

**Executive Order 13960**, "Promoting the Use of Trustworthy Artificial Intelligence in the Federal Government" (3 December 2020), Federal Register 85(236): 78939–78943, document 2020-27065. A work of the United States Government, in the public domain. Credit: Office of the Federal Register, National Archives and Records Administration, and the U.S. Government Publishing Office, which publishes the official edition at GovInfo. Included as retrieved on 29 October 2026 (`example/input/source/2020-27065.html`, duplicated in the frozen package `example/prepared/source/`), with a normalized reading text derived from it (`2020-27065.txt`, same folders). The frozen requests carry the normalized text as context, and the records quote passages of it. The analysis here is historical textual analysis of the published text; it makes no statement about present legal effect. Identity, retrieval and fingerprints: `data/SOURCES.md`.

## Third-party sources cited, not included

The design of the codebook, the checks and the export follows distinctions drawn in:

- Carlson, N. A., and V. Burbano. 2026. The use of LLMs to annotate data in management research: Foundational guidelines and warnings. *Strategic Management Journal* 47(3): 699–725. https://doi.org/10.1002/smj.70023
- Egami, N., M. Hinck, B. M. Stewart, and H. Wei. 2024. Using large language model annotations for the social sciences: A general framework of using predicted variables in downstream analyses. Author manuscript, 17 November 2024.
- Gilardi, F., M. Alizadeh, and M. Kubli. 2023. ChatGPT outperforms crowd-workers for text-annotation tasks. *Proceedings of the National Academy of Sciences* 120(30). https://doi.org/10.1073/pnas.2305016120

None of these studies' text, procedures, data or models are reproduced here.

## Material from other parts of this project

- The record-sealing pattern in `tool/workflow.py` (canonical JSON hash of a record that excludes its own seal, append-only outputs, unknown values stored as null with a reason) is adapted from a prior results ledger. No code was imported verbatim and no data from it is used.
- The method syntheses on annotation, model comparison and workflow design that informed the codebook are the project's own literature work, carried by component 2 (Textual-data literature reviews and database). They are referenced, not copied here.

## Licences

- Code (`tool/`, `checks/verify.py`): Apache License 2.0, as the repository root `LICENSE` states.
- Documents and data authored by the project (`README.md`, `AI-PROMPT.md`, `NOTICE.md`, `MANIFEST.json`, `docs/`, `data/SOURCES.md`, and in `example/` and `checks/recorded-2026-10-29/` the codebook, study definition, prompt, coding units, frozen requests, candidate records, receipts, manifests, exported outputs, recorded check results and the two synthetic error files): Creative Commons Attribution 4.0 International (CC BY 4.0), as the repository root `LICENSE-docs` states.
- Some of these files were written with an AI assistant in the project's own sessions (the producer receipts say which records); under the assistant provider's terms of use the output belongs to the user, and the project licenses it on the terms above.
- Copyright holder during review: the TextData authors, 2026.
- Public-domain material (the executive order as retrieved, its normalized text, and the passages of it quoted in the requests and records) is not relicensed.

## Example provenance

The manifests, producer receipt and execution record under `example/` are labelled release-derived. They preserve the saved requests, responses and annotation records; they do not claim a new model run. Original binding records under `checks/recorded-2026-10-29/` support the included integrity check. Their historical fingerprints differ from the release-derived package. The wider interactive context is unavailable.
