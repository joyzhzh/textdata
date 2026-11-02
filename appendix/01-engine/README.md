# Deep-research engine

[Working demonstration](https://textdata.info/engine/) · [AI prompt](AI-PROMPT.md) · [All components](../README.md)

The deep-research engine connects a researcher’s question to source-supported findings and decisions about research tools. The working prototype includes a reusable scout skill, an offline validator, and an evidence map whose claims can be followed back to the exact source passage.

## Try the prototype

[Explore the evidence map](https://textdata.info/engine/), or follow [the worked example](example/README.md): Langley’s article on theorizing from process data → two claims bounded to the publisher abstract → their use in the synthesis.

The example contains **77 works, 101 inspected versions and 141 located claims** about theory-building methods and software. Its [findings](example/campaign/FINDINGS.md) and [synthesis](example/campaign/SYNTHESIS.md) support a modular design: select the mode of theorizing first, preserve the sources of each claim, and treat theory quality as several criteria rather than one score.

To check the supplied example, use Python 3.9 or later from this folder. No network, model or package installation is required:

```sh
python3 checks/verify_campaign.py
python3 tool/scout/scripts/validate_lean_bundle.py example/campaign
python3 checks/verify_manifest.py
```

Expected: `19/19 checks passed`, validator artifact and claim-ceiling gates `PASS`, and `0 failures` from the manifest check. These checks establish file and record consistency, not source accuracy or search completeness. [Tool instructions](tool/README.md) explain the included scout skill.

## Completed contribution

A methods inquiry informed the Grounded Theory toolkit’s source and comparison checks: analysts identify the lines supporting an incident, record what a comparison changed, and explain responses to negative cases. Further sampling remains a proposal for the researcher. The [methods basis](docs/RESEARCH_TO_CAPABILITY.md) links to the toolkit and retains the qualifications behind these choices.

## Limits and proposed development

The evidence map is English-primary and public-access, observed through 28 July 2026. It is effort-bounded and not saturated; many claims rest on abstracts or software documentation. Candidate software was not run, and all claims have not been checked by a human against their sources.

The included validator runs offline; the scout skill is a procedure for a researcher or agent with source access. A shareable, integrated engine and its evaluation remain proposed. The successor helper is not included and has only synthetic-input evidence (42 unit tests); unattended operation and wide external adoption have not been demonstrated.

## Files

- `tool/`: scout instructions, search contract and validator.
- `example/`: final evidence map, findings, synthesis and a short reading guide. Search and screening inputs are retained because the validator requires them.
- `docs/RESEARCH_TO_CAPABILITY.md`: how the methods evidence informs the Grounded Theory toolkit.
- `checks/` and `MANIFEST.json`: offline checks and file hashes.

Project code is Apache-2.0; project-authored documents and records are CC BY 4.0. Third-party material retains its own terms. See [NOTICE.md](NOTICE.md).
