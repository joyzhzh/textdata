#!/usr/bin/env python3
"""Regenerate MANIFEST.json for this component folder.

Lists every shipped file with its size and SHA-256 (MANIFEST.json itself excepted), states the
counts with their units, and records what this release includes and holds. Before writing, it
recomputes the counts from the sealed records with checks/verify_counts.py and stops if any
stated count differs.

Standard library only; no network, no model.

Usage: python3 checks/build_manifest.py
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # leave no cache files in the component folder

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.json"
SKIP_NAMES = {".DS_Store"}  # by name, anywhere; the root MANIFEST.json is skipped by path
STUDY = "example/input/study/snapshots/C003/"

# The counts this folder states, in the units the README and the final appendix use.
SELECTIONS = "example/input/study/C002_SELECTION.json, example/input/study/C003_SELECTION.json, " + STUDY + "INPUT_MANIFEST.json"
COUNTS = [
    ("interviews after cycle 1 (pilot)", 6, "bound interviews not named by either selection record", SELECTIONS),
    ("interviews after cycle 2", 14, "the pilot's plus those the C002 selection record names", SELECTIONS),
    ("interviews after cycle 3", 22, "the above plus those the C003 selection record names", SELECTIONS),
    ("bound interview transcripts", 22, "transcript files bound by SHA-256 (cumulative over three cycles: 6, 14, 22); not included", "INPUT_MANIFEST.json"),
    ("incident records", 234, "incident rows; speakers' accounts, none directly observed", "INCIDENTS.jsonl"),
    ("incidents with exact quotation hashes", 78, "incident rows carrying the SHA-256 of the quoted lines (stated interpretations)", "INCIDENTS.jsonl"),
    ("incidents coded as directly observed action", 0, "incident rows with epistemic_class OBSERVED_ACTION", "INCIDENTS.jsonl"),
    ("comparison records", 43, "comparison rows", "COMPARISONS.jsonl"),
    ("category versions", 15, "category-memo rows, all versions retained", "CATEGORY_MEMOS.jsonl"),
    ("current categories", 6, "categories whose latest version is not superseded", "CATEGORY_MEMOS.jsonl"),
    ("memo versions", 14, "memo rows across four memo types", "MEMOS.jsonl"),
    ("sampling requests", 3, "request rows", "SAMPLING_REQUESTS.jsonl"),
    ("sampling requests left PROPOSED", 3, "request rows with status PROPOSED; none executed by the tool", "SAMPLING_REQUESTS.jsonl"),
    ("episode versions", 89, "episode rows (account envelopes), all versions", "EPISODES.jsonl"),
    ("current account envelopes", 86, "episodes not superseded; not independent observations", "EPISODES.jsonl"),
    ("current envelopes with UNKNOWN ending", 62, "current episodes whose outcome_status is UNKNOWN", "EPISODES.jsonl"),
    ("code versions", 235, "initial-code rows, all versions", "CODES.jsonl"),
    ("current codes", 234, "code rows not superseded", "CODES.jsonl"),
]

HEADER = {
    "component": 5,
    "slug": "grounded-theory",
    "title": "Grounded Theory",
    "appendix_item": 5,
    "documentation": "README.md",
    "release": "Proposal prototype: see README.md for use and limits.",
    "status": {"built": True, "demonstrated": "empirical (22 interviews, three cycles) and synthetic", "validated": False},
    "contents": [
        {"path": "tool/", "what": "the toolkit's agent skill: instructions, six references, eight schemas, three helpers, three templates, a synthetic fixture and input text, two test files (53 tests)", "edition": "release edition; modifications noted in CHANGES.md"},
        {"path": "example/input/study/", "what": "the sealed third-cycle records of the 22-interview study, the two selection records, the analytical account, the review and the producers' dispositions", "edition": "release inspection edition: seven original analytical files unchanged; duplicate handoff omitted; INPUT_MANIFEST.json and MANIFEST.json are declared derivatives; original and release fingerprints are separate"},
        {"path": "example/trace_comparison.py, example/output/TRACE.md", "what": "the worked example: one analytical chain traced through the records", "edition": "written for this release"},
        {"path": "checks/", "what": "the verification a reviewer runs, and the script that regenerates this manifest", "edition": "written for this release"},
        {"path": "README.md, NOTICE.md, CHANGES.md, data/README.md, example/README.md", "what": "the technical account, credits and licences, the change note, and what is and is not here", "edition": "written for this release"},
    ],
    "entry_points": [
        "tool/SKILL.md",
        "tool/AGENT_STARTER.md",
        "tool/scripts/analysis_cycle.py",
        "tool/scripts/validate_analysis_packet.py",
        "tool/examples/synthetic/workflow.py",
        "example/trace_comparison.py",
        "checks/verify_counts.py",
    ],
    "example": {
        "input": [STUDY + n for n in (
            "COMPARISONS.jsonl", "CATEGORY_MEMOS.jsonl", "INCIDENTS.jsonl", "EPISODES.jsonl", "CODES.jsonl",
            "MEMOS.jsonl", "SAMPLING_REQUESTS.jsonl", "MANIFEST.json", "INPUT_MANIFEST.json", "SHA256SUMS", "RELEASE_DERIVATION.json", "RELEASE_SHA256SUMS")] + [
            "example/input/study/C002_SELECTION.json",
            "example/input/study/C003_SELECTION.json",
            "example/input/study/C003_ANALYSIS.md",
            "example/input/study/SAMPLE_AND_CHANGES.md",
            "example/input/study/audit/INDEPENDENT_REVIEW.md",
            "example/input/study/audit/DISPOSITIONS.md",
        ],
        "output": ["example/output/TRACE.md"],
        "command": "python3 example/trace_comparison.py",
        "needs_network": False,
        "needs_model": False,
        "python": "3.9+ standard library",
    },
    "checks": [
        {"command": "python3 checks/verify_counts.py", "needs": "Python 3.9+ standard library; offline; no model",
         "expects": "all checks passed"},
        {"command": "python3 -B -m unittest discover -s tests (run in tool/)", "needs": "jsonschema; macOS, Linux or WSL; ordinary copied tool files are supported without Git history",
         "expects": "OK, 53 tests"},
    ],
    "data": [
        {"source": "22 interview transcripts of a published podcast (credited in NOTICE.md)", "rights": "copyright of their owners; licence unknown; referenced only by file name, line locators and SHA-256", "included": False},
        {"source": "the study's analytical records", "rights": "the project's own records; CC BY 4.0 (repository LICENSE-docs)", "included": True},
        {"source": "the synthetic fixture and synthetic input text", "rights": "wholly invented; Apache License 2.0 with the code (repository LICENSE)", "included": True},
    ],
    "held": [
        {"what": "interview transcripts", "why": "no redistribution right claimed"},
        {"what": "private development records and duplicate handoff", "why": "not required to use the prototype"},
    ],
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def shipped_files():
    out = []
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT).as_posix()
        if p.is_symlink():
            sys.exit(f"refusing: symlink {rel}")
        if not p.is_file() or p == MANIFEST or p.name in SKIP_NAMES or "__pycache__" in p.parts or p.suffix == ".pyc":
            continue
        out.append(p)
    return out


def main():
    spec = importlib.util.spec_from_file_location("verify_counts", ROOT / "checks" / "verify_counts.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    computed = mod.recompute()
    bad = [f"{what}: stated {value}, records give {computed.get(what)}"
           for what, value, _, _ in COUNTS if computed.get(what) != value]
    if bad:
        sys.exit("refusing to write MANIFEST.json:\n  " + "\n  ".join(bad))
    files = [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p)}
             for p in shipped_files()]
    manifest = dict(HEADER)
    manifest["counts"] = [{"what": w, "value": v, "unit": u, "where": f if "/" in f else STUDY + f} for w, v, u, f in COUNTS]
    manifest["file_count"] = len(files)
    manifest["size_bytes"] = sum(f["bytes"] for f in files)
    manifest["files"] = files
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote MANIFEST.json: {len(files)} files, {manifest['size_bytes']} bytes, {len(COUNTS)} counts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
