# Data in this component

This component ships one source document, in full, because it is a United States Government work in the public domain. It lives with the worked example rather than here, so that the example is self-contained.

## Executive Order 13960

- Title: Promoting the Use of Trustworthy Artificial Intelligence in the Federal Government. Signed 3 December 2020; published 8 December 2020 in the Federal Register, volume 85, number 236, pages 78939–78943; Federal Register document number 2020-27065.
- Issuer and provider: Office of the Federal Register, National Archives and Records Administration, and the U.S. Government Publishing Office (GovInfo).
- Rights: official United States Government text, public domain. Source attribution is retained in `example/input/study.json`.
- Retrieved: 29 October 2026, directly from https://www.govinfo.gov/content/pkg/FR-2020-12-08/html/2020-27065.htm. It was not taken from the Federal Register release packs of component 8.
- Files: `example/input/source/2020-27065.html` (as retrieved; SHA-256 `b5aebc25b9665fb743fe13094c7143cefe99f2be6f201e63b8069de585e98875`) and `example/input/source/2020-27065.txt` (normalized reading text; SHA-256 `88f5a24f104b140f904574274bfc9bc3e3824e594fd5ce43f86f46e235ef8533`). The normalization is declared in `study.json` (`transformation`) and performed by `tool/make_example.py`. Character positions in every annotation refer to the normalized text.

To fetch the document again, download the URL above and compare the SHA-256 of the bytes with the value recorded here; the provider may correct historical records, so a different hash means a different version, not an error in this package.

## Not included

No other corpus is part of this component. The Federal Register corpus (component 8) and the annotation-methods literature (component 2) are separate components of this repository.
