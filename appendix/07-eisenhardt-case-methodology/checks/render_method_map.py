#!/usr/bin/env python3
"""Render docs/METHOD_MAP.md from docs/method-map/map.json and sources.json (deterministic; standard library)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent / "docs"


def render(map_data: dict, sources: list[dict]) -> str:
    out: list[str] = []
    w = out.append
    w("# The Eisenhardt method, mapped")
    w("")
    w("A methodological reference for preparing case-based theory building. Read the eight phases alongside the cited sources. This is a bounded synthesis, not a systematic review or a validated analytical engine.")
    w("")
    w("The source notes are in `method-map/sources.json`; the phase map is in `method-map/map.json`. Some entries describe the same work, so source rows are not a count of distinct publications.")
    w("")
    w("## The method, phase by phase")
    w("")
    w("| Phase | What the method asks | What it leaves to inspect | A common failure |")
    w("|---|---|---|---|")
    for i, p in enumerate(map_data["phases"], 1):
        w(f"| {i}. {p['name']} | {p['asks']} | {p['output']} | {p['failure']} |")
    w("")
    w("## Core features and folklore")
    w("")
    w("Core features supported by the current first-party clarification:")
    w("")
    for item in map_data["core"]:
        w(f"- {item}")
    w("")
    w("Not method requirements:")
    w("")
    for item in map_data["folklore"]:
        w(f"- {item}")
    w("")
    w("## Method demarcation")
    w("")
    w("| Approach | Primary analytic target | Distinctive warrant | Relationship to Eisenhardt |")
    w("|---|---|---|---|")
    for d in map_data["demarcation"]:
        w(f"| {d['approach']} | {d['target']} | {d['warrant']} | {d['relation']} |")
    w("")
    w(map_data["demarcationNote"])
    w("")
    w("## Development beyond preparation")
    w("")
    w("The following analytical tasks remain for the researcher. TextData has not implemented or evaluated these capabilities:")
    w("")
    for i, item in enumerate(map_data["missing"], 1):
        w(f"{i}. {item}")
    w("")
    w("## The sources behind the map")
    w("")
    w("Source notes state the evidence type, confidence and material limits of each interpretation. Consult the cited work before using a claim.")
    w("")
    for src in sources:
        year = f" ({src['year']})" if src.get("year") else ""
        doi = f" DOI {src['doi']}." if src.get("doi") else ""
        kind = "" if src["kind"] == "publication" else f" [{src['kind']}]"
        w(f"### {src['id']} {src['label']}{kind}")
        w("")
        w(f"Cells: {', '.join(src['cells'])}.{doi}")
        if src.get("caution"):
            w("")
            w(f"Caution: {src['caution']}")
        w("")
        for c in src["claims"]:
            w(f"- {c['text']} (Evidence: {c['evidence']}; confidence: {c['confidence']}.)")
        w("")
    return "\n".join(out).rstrip("\n") + "\n"


def main() -> int:
    map_data = json.loads((DOCS / "method-map" / "map.json").read_text(encoding="utf-8"))
    sources = json.loads((DOCS / "method-map" / "sources.json").read_text(encoding="utf-8"))
    text = render(map_data, sources)
    if "--check" in sys.argv:
        current = (DOCS / "METHOD_MAP.md").read_text(encoding="utf-8")
        print("METHOD_MAP.md matches its sources" if current == text else "METHOD_MAP.md DIFFERS from its sources")
        return 0 if current == text else 1
    (DOCS / "METHOD_MAP.md").write_text(text, encoding="utf-8")
    print(f"wrote {DOCS / 'METHOD_MAP.md'} ({len(text)} characters; {len(sources)} sources; {sum(len(s['claims']) for s in sources)} claims)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
