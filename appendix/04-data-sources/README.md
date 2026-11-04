# Rich textual-data sources review

Choose a source by the observations it can support. This working prototype brings together **25 dated source profiles**, a searchable catalogue, a comparative review and an offline profile renderer. It makes coverage, linking fields, access and reuse limits visible before data acquisition.

[Source profiles](data/profiles/README.md) · [Use the AI exploration prompt](AI-PROMPT.md)

## An illustrative selection decision

The Consumer Financial Protection Bureau database looked promising for complaint–response research. Its [D17 profile](example/output/D17.md) records that the provider’s September 2026 release removed complaint narratives. Structured complaint fields remain, but they cannot support the proposed narrative task.

[Google Local (D02)](data/profiles/D02.md) is the review’s next candidate: it documents review text and dated business responses. Its reuse terms remain unresolved. The example shows a source decision changing before acquisition; it does not demonstrate a completed empirical study.

## What works now

- [The catalogue](data/catalogue.json), also available as [CSV](data/catalogue.csv), describes 25 source families: 18 in [12 research arenas](data/arenas.json), six structured complements and one former narrative source.
- [All 25 readable profiles](data/profiles/README.md) give units, coverage, identifiers, access, reuse, limits and a proposed first task.
- [The comparison](docs/comparison.md) explains which sources suit different demonstrations and why.
- [Source evidence](data/evidence.jsonl) links 70 claims to provider pages, papers or archive records. [Ten provider-page checks](data/provider_checks.json) cover nine families.

Profiles are dated 11 October 2026; the provider checks are dated 29 October. These are documentation-based assessments, not 25 included datasets.

## Run the prototype

From this folder, with Python 3.9 or later:

```sh
python3 -I tool/render_profile.py D17 --out example/output
python3 -I tool/render_profile.py --all --out data/profiles
python3 -I checks/verify_counts.py
```

The renderer uses the included records, requires no network or model, and reproduces the shipped Markdown profiles. The check verifies the counts, source mappings, JSON/CSV agreement, rendered output and file manifest; success prints `all checks pass`.

## What remains proposed

Acquiring source datasets, running the suggested tasks and testing their fit in a study remain future work. The review is representative, not exhaustive. Source releases and terms can change; public access alone does not grant reuse rights. The [notice](NOTICE.md) credits providers and separates their terms from the licenses for this component’s text and code.

[Component files](.)
