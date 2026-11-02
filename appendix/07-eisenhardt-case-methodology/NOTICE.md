# Notices: third-party sources and credits

## Method

The toolkit prepares research in the tradition of Eisenhardt KM (1989), Building theories from case study research, Academy of Management Review 14(4):532–550, https://doi.org/10.5465/amr.1989.4308385, and Eisenhardt KM (2021), What is the Eisenhardt Method, really?, Strategic Organization 19(1):147–160, https://doi.org/10.1177/1476127020982866. These works are cited, not included. This is an independent research-tooling project and is not affiliated with the method's author. The 66 source rows listed in `docs/METHOD_MAP.md` (61 publication rows, 60 of them with a DOI, and five public software repository rows) are cited, not included; the source notes are project-authored paraphrases and short quoted phrases. The map is a selected, paraphrased reader edition.

## Reference collection (`data/r12/`)

The four files are the toolkit's R12 release, byte for byte; `data/r12/MANIFEST.json` is the release's own manifest, and `checks/run_checks.py` compares the three data files with the sizes and SHA-256 hashes it records. The files contain bibliographic facts, public identifiers and links, plus project-created tier and screening annotations. The project's original annotations and compilation are released under CC BY 4.0 to the extent the project holds rights in them. No ownership is asserted over titles, author names, publication metadata, DOIs, OpenAlex identifiers, linked papers or other third-party material, which remain subject to applicable law and source-specific terms:

- Crossref treats bibliographic metadata as facts and states that its metadata may be reused without restriction, except abstracts (https://www.crossref.org/documentation/retrieve-metadata/).
- OpenAlex makes its data free and open under CC0 (https://openalex.org/about; https://help.openalex.org/access/overview/) and asks users to cite it (https://help.openalex.org/how-to/citing-openalex/): Priem J, Piwowar H, Orr R (2022) OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. arXiv:2205.01833.
- Some metadata was informed by the Semantic Scholar API (credit: Semantic Scholar, https://www.semanticscholar.org/?utm_source=api). Its API licence (https://api.semanticscholar.org/license/) governs data obtained through the API; the release does not record which values came from it.

- DataCite DOI metadata is offered under CC0 (https://support.datacite.org/docs/harvesting-datacite-doi-metadata).
- OpenAIRE Graph is offered under CC BY, with some parts CC0 (https://graph.openaire.eu/docs/license/). Credit: OpenAIRE Graph. The conservative attribution basis for included OpenAIRE-derived metadata is CC BY; the project does not relicense it.
- OpenCitations datasets are CC0 (https://opencitations.net/). An OpenCitations record label does not establish the source or rights of each joined value.

**Provenance qualification:** the included collection contains ordinary bibliographic facts and links plus project annotations, not abstracts, article text or provider payloads. Some source records involved the Semantic Scholar API, whose terms restrict sharing without authorization. The export does not retain field-level provider provenance, and the retained comparison does not establish that an unmatched value came exclusively from a restricted API. This is an unresolved provenance/terms question for API-derived metadata, not evidence that each unmatched title or URL creates a separate redistribution conflict. No blanket licence is asserted over third-party material.

No PDFs, abstracts, article text, provider payloads, credentials or search logs are redistributed. A `landing_url` is a locator, not a statement that the linked work is open access or licensed for redistribution. Author names are the published authors of the listed works, as the metadata providers report them.

## Code and documents

The code in `tool/scripts/`, `tool/tests/`, `example/run_example.py`, `checks/run_checks.py` and `checks/render_method_map.py` is released under the Apache License 2.0 (`LICENSE` at the repository root). The documents and records (`README.md`, `AI-PROMPT.md`, `NOTICE.md`, `MANIFEST.json`, `docs/`, `tool/SKILL.md`, `tool/references/`, the example's synthetic input and recorded outputs, `data/r12/MANIFEST.json`) and the project's annotations and compilation in `data/` are released under CC BY 4.0 (`LICENSE-docs` at the repository root). How to cite the repository is in `CITATION.cff` at its root.
