#!/usr/bin/env python3
"""Verify the counts the README states, the data hashes, the toolkit's own tests, the worked example, the method map and MANIFEST.json.

Runs without network or model calls. Python 3.9+, standard library. Exit status 0 when every check passes.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data" / "r12"
TOOL = ROOT / "tool"

EXPECTED_COUNTS = {
    "rows": 22856,
    "unique_public_ids": 22856,
    "evidence_tier_counts": {"canonical-metadata-qualified": 15198, "provisional-high-recall": 7658},
    "screening_label_counts": {"confirmed-case-study": 12300, "probable-case-study": 10556},
    "doi_rows": 20732,
    "unique_dois": 20732,
    "landing_url_source_counts": {"doi": 20732, "openalex": 1671, "stable-url": 57, "unavailable": 396},
    "fields": 15,
    "empty_author_lists": 635,
}
EXPECTED_MAP = {"phases": 8, "missing": 8, "sources": 66, "claims": 101}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_counts() -> dict:
    tiers: Counter[str] = Counter(); labels: Counter[str] = Counter(); landing: Counter[str] = Counter()
    ids: set[str] = set(); dois: list[str] = []; rows = 0; no_authors = 0; fields = 0
    with (DATA / "references.csv").open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = len(reader.fieldnames or [])
        for row in reader:
            rows += 1; ids.add(row["public_id"]); tiers[row["evidence_tier"]] += 1
            labels[row["screening_label"]] += 1; landing[row["landing_url_source"]] += 1
            if row["doi"]:
                dois.append(row["doi"])
            if row["authors"] == "[]":
                no_authors += 1
    observed = {
        "rows": rows, "unique_public_ids": len(ids), "evidence_tier_counts": dict(tiers), "screening_label_counts": dict(labels),
        "doi_rows": len(dois), "unique_dois": len(set(dois)), "landing_url_source_counts": dict(landing), "fields": fields,
        "empty_author_lists": no_authors,
    }
    doi_list = [line.strip() for line in (DATA / "dois.txt").read_text(encoding="utf-8").splitlines() if line.strip()]
    observed["dois_txt_lines"] = len(doi_list)
    ok = all(observed[k] == v for k, v in EXPECTED_COUNTS.items()) and len(doi_list) == EXPECTED_COUNTS["unique_dois"] and set(doi_list) == set(dois)
    note = f"{no_authors} records carry an empty authors list, as exported in the R12 release."
    return {"name": "data counts match README and MANIFEST", "pass": ok, "observed": observed, "note": note}


def check_hashes() -> dict:
    manifest = json.loads((DATA / "MANIFEST.json").read_text(encoding="utf-8"))
    results = {}
    ok = True
    for name, record in manifest["files"].items():
        path = DATA / name
        actual = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
        results[name] = actual
        ok = ok and actual == record
    gen = TOOL / manifest["generator"]["path"]
    results["generator"] = sha256_file(gen)
    ok = ok and results["generator"] == manifest["generator"]["sha256"]
    return {"name": "data file hashes match data/r12/MANIFEST.json", "pass": ok, "observed": results}


def check_tests() -> dict:
    env = {"PYTHONPATH": str(TOOL), "PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin:/usr/local/bin"}
    proc = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", str(TOOL / "tests"), "-t", str(TOOL / "tests"), "-v"], capture_output=True, text=True, env=env, check=False)
    tail = proc.stderr.strip().splitlines()[-3:]
    return {"name": "toolkit test suite (19 tests)", "pass": proc.returncode == 0 and "Ran 19 tests" in proc.stderr, "observed": tail}


def check_example() -> dict:
    workdir = Path(tempfile.mkdtemp(prefix="eisenhardt-checks-"))
    proc = subprocess.run([sys.executable, "-I", "-B", str(ROOT / "example" / "run_example.py"), "--workdir", str(workdir)], capture_output=True, text=True, check=False)
    try:
        fresh = json.loads(proc.stdout)["summary"]
    except (json.JSONDecodeError, KeyError):
        return {"name": "worked example reproduces the retained SUMMARY", "pass": False, "observed": proc.stderr.strip().splitlines()[-5:]}
    retained = json.loads((ROOT / "example" / "output" / "SUMMARY.json").read_text(encoding="utf-8"))
    volatile = {"sealed_plan_sha256"}  # the plan binds live inodes, so its hash differs per machine
    same = {k: fresh.get(k) == v for k, v in retained.items() if k not in volatile}
    print(f"worked example run left in {workdir}", file=sys.stderr)  # kept out of the JSON so a recorded result carries no machine path
    return {"name": "worked example reproduces the retained SUMMARY", "pass": proc.returncode == 0 and all(same.values()), "observed": {"fields_compared": same}}


def check_map() -> dict:
    map_data = json.loads((ROOT / "docs" / "method-map" / "map.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "docs" / "method-map" / "sources.json").read_text(encoding="utf-8"))
    observed = {"phases": len(map_data["phases"]), "missing": len(map_data["missing"]), "sources": len(sources), "claims": sum(len(s["claims"]) for s in sources)}
    render = subprocess.run([sys.executable, "-I", "-B", str(HERE / "render_method_map.py"), "--check"], capture_output=True, text=True, check=False)
    ok = observed == EXPECTED_MAP and render.returncode == 0
    return {"name": "method map counts and METHOD_MAP.md rendering", "pass": ok, "observed": {**observed, "render": render.stdout.strip()}}


def check_manifest() -> dict:
    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    volatile = {"checks/last-run.json"}  # a new run of this script may be recorded there
    listed = {entry["path"]: entry for entry in manifest["files"]}
    on_disk = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*")
               if p.is_file() and "__pycache__" not in p.parts and not p.name.startswith(".")} - {"MANIFEST.json"}
    mismatched = [path for path, entry in listed.items() if path in on_disk and path not in volatile
                  and ((ROOT / path).stat().st_size != entry["bytes"] or sha256_file(ROOT / path) != entry["sha256"])]
    observed = {"listed": len(listed), "unlisted": sorted(on_disk - set(listed)), "missing": sorted(set(listed) - on_disk), "mismatched": mismatched}
    ok = not (observed["unlisted"] or observed["missing"] or mismatched)
    return {"name": "every file matches its size and SHA-256 in MANIFEST.json", "pass": ok, "observed": observed}


def main() -> int:
    results = [check_counts(), check_hashes(), check_tests(), check_example(), check_map(), check_manifest()]
    print(json.dumps({"all_pass": all(r["pass"] for r in results), "checks": results}, indent=2))
    return 0 if all(r["pass"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
