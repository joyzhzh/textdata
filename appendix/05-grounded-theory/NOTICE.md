# Notice: sources, licences and credits

This component contains software, agent instructions, documents and analytical records authored by the TextData project. The interview transcripts the records analyse, and any extended excerpt from them, are withheld; the records' incident descriptions paraphrase the interviews. Three short runs of 8, 9 and 9 words in those paraphrases coincide with the transcripts' wording, three fragments of one to four words are quoted in quotation marks with their speaker identified, and a few single words of the speakers appear without quotation marks.

## Licences

- **Code and the agent skill** — everything under `tool/` (instructions, references, schemas, helpers, templates, the synthetic fixture and input text, tests), `example/trace_comparison.py` and `checks/`: Apache License 2.0, as given in the repository's root `LICENSE`. Copyright: the TextData authors.
- **Documents and data authored by the project** — the component documents, analytical records under `example/input/study/` and generated `example/output/TRACE.md`: Creative Commons Attribution 4.0 International (CC BY 4.0), as given in the repository's root `LICENSE-docs`.
- Third-party material keeps its own terms. None is included beyond what is described below: the names of the podcast, its host and the interviewees, bibliographic references to published works, the three short coinciding runs, the three short quoted fragments and those few single words. The rights in the transcripts remain with their owners and are not covered by the project's CC BY terms.

## Source accounts (referenced, not included)

The interview study analyses 22 interview transcripts of Lenny's Podcast. Credit for the source accounts belongs to Lenny's Podcast, its host Lenny Rachitsky, and the interviewees. The transcripts are held in a private research archive; their licence is recorded as unknown, and no redistribution right is claimed or implied. What ships is the project's own analytical record: paraphrased incident descriptions that name the speakers, one-based line spans into each transcript, and SHA-256 hashes of each transcript and of each quoted passage in place of the quotation. A comparison of every file in this folder with the 22 transcripts found no shared run of 12 or more words; the only runs of 8 or more are the three noted above, inside paraphrased incident descriptions (`example/input/study/snapshots/C003/INCIDENTS.jsonl`). A reader holding the same transcripts can verify every binding; the project does not supply them.

The provider now publishes [dataset terms](https://github.com/LennysNewsletter/lennys-newsletterpodcastdata/blob/main/LICENSE.md) (checked 2 November 2026). They permit specified personal projects, prohibit raw-file redistribution and distinguish the public starter set from the paid full archive. Those terms do not establish which licence covered the exact retained research copies, nor do they license the transcripts under CC BY 4.0. The original input records retain their historical `UNKNOWN` licence status. The short overlaps and attributed fragments described above remain excluded from the project licence; their length alone is not a redistribution permission.

## Method sources (cited, not included)

The toolkit's methods basis (`tool/references/methods-basis.md`) summarises methodological guidance; source papers are not bundled. The operative sources for the three analytical operations that carry the worked example are:

- Boeije H (2002) A purposeful approach to the constant comparative method in the analysis of qualitative interviews. *Quality & Quantity* 36(4):391–409. https://doi.org/10.1023/A:1020909529486
- Birks M, Chapman Y, Francis K (2008) Memoing in qualitative research: Probing data and processes. *Journal of Research in Nursing* 13(1):68–75. https://doi.org/10.1177/1744987107081254
- Foley G, Timonen V (2015) Using grounded theory method to capture and analyze health care experiences. *Health Services Research* 50(4):1195–1210. https://doi.org/10.1111/1475-6773.12275

Further methodological sources:

- Corbin JM, Strauss A (1990) Grounded theory research: Procedures, canons, and evaluative criteria. *Qualitative Sociology* 13:3–21. https://doi.org/10.1007/BF00988593
- Fram SM (2013) The constant comparative analysis method outside of grounded theory. *The Qualitative Report* 18, Article 1:1–25.
- Gehman J, Glaser VL, Eisenhardt KM, Gioia D, Langley A, Corley KG (2018) Finding theory–method fit: A comparison of three qualitative approaches to theory building. *Journal of Management Inquiry* 27(3):284–300. https://doi.org/10.1177/1056492617706029
- Gioia DA, Corley KG, Hamilton AL (2013) Seeking qualitative rigor in inductive research: Notes on the Gioia methodology. *Organizational Research Methods* 16(1):15–31. https://doi.org/10.1177/1094428112452151
- Glaser BG (2008) The constant comparative method of qualitative analysis. *Grounded Theory Review* 7(3). Reprint of *Social Problems* 12 (1965):436–445.
- Glaser BG (2012) Constructivist grounded theory? *Grounded Theory Review* 11(1):28–38. Reprint of a 2002 article.
- Leonardi P (2011) When flexible routines meet flexible technologies: Affordance, constraint, and the imbrication of human and material agencies. *MIS Quarterly* 35(1):147–167.
- Liu A, Esbenshade L, Xiao M, Tian V, Zhang Z, He K, Sun M (2026) Agreement is not quality: Blind expert verification of human and LLM qualitative coding when human consensus is not ground truth. arXiv:2607.28890.
- Malterud K, Siersma VD, Guassora ADK (2016) Sample size in qualitative interview studies: Guided by information power. *Qualitative Health Research* 26(13):1753–1760. https://doi.org/10.1177/1049732315617444
- Martínez Montes C, et al. (2025) Large language models in thematic analysis: Prompt engineering, evaluation, and guidelines for qualitative software engineering research. arXiv:2510.18456.
- Nelson J (2017) Using conceptual depth criteria: Addressing the challenge of reaching saturation in qualitative research. *Qualitative Research* 17(5):554–570. https://doi.org/10.1177/1468794116679873
- Orlikowski WJ (2008) Using technology and constituting structures: A practice lens for studying technology in organizations. In *Resources, Co-Evolution and Artifacts*, 255–305. https://doi.org/10.1007/978-1-84628-901-9_10
- Parry MM, Dario LM, Moule RK (2019) Is seeing believing? On the content validity of video recordings for use in criminological research. *Deviant Behavior*. https://doi.org/10.1080/01639625.2019.1699259
- UNESCO (2023) *Guidance for generative AI in education and research*. Miao F, Holmes W.

The method label used throughout is "inductive process study using grounded-theory techniques"; the toolkit does not claim conformity to any single grounded-theory school.

## Analysis credit

The study's records were produced by AI agents applying this toolkit under the researcher's direction, and reviewed by a separate, non-producing agent using the same model; no human methodological review has taken place.

## Software dependencies (not included)

The worked example and the checks use the Python 3 standard library only. The helpers under `tool/scripts/`, the synthetic two-cycle demonstration and the tests also need the `jsonschema` package (MIT License), listed in `tool/requirements.txt`.
