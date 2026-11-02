#!/usr/bin/env python3
"""Verify the counts stated in README.md and MANIFEST.json against the shipped records.

Standard library only; no network, no model. Exit code 0 means every check passed.

Checks:
  1. Recompute counts from example/input/study/snapshots/C003 and compare with MANIFEST.json "counts".
  2. Verify seven unchanged analytical files against the original C003 seal; verify the two declared
     release derivatives and every current packet file against RELEASE_SHA256SUMS.
  3. Regenerate the worked example in memory and compare it byte-for-byte with example/output/TRACE.md.
  4. Confirm the synthetic fixture and the tool entry points named in MANIFEST.json exist.
  5. Confirm every file in the folder is listed in MANIFEST.json with its size and SHA-256, and
     that no listed file is missing, no file is a symlink and none exceeds 100 MB.

Usage: python3 checks/verify_counts.py
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # leave no cache files in the component folder

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "example" / "input" / "study" / "snapshots" / "C003"
MANIFEST = ROOT / "MANIFEST.json"
TRACE = ROOT / "example" / "output" / "TRACE.md"
SEALED_INPUT_MANIFEST_SHA256 = "9128fd18d8fa44c5e69be7f407180816778bf6080137b64c18cb61a17a6a22ff"

failures = []


def check(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        failures.append(what)


def rows(name):
    with open(PACKET / name, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def current(items, idkey):
    superseded = {r.get("supersedes") for r in items if r.get("supersedes")}
    return [r for r in items if r[idkey] not in superseded]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def recompute():
    inputs = json.load(open(PACKET / "INPUT_MANIFEST.json", encoding="utf-8"))
    episodes = rows("EPISODES.jsonl")
    incidents = rows("INCIDENTS.jsonl")
    codes = rows("CODES.jsonl")
    comparisons = rows("COMPARISONS.jsonl")
    categories = rows("CATEGORY_MEMOS.jsonl")
    memos = rows("MEMOS.jsonl")
    requests = rows("SAMPLING_REQUESTS.jsonl")
    cur_cat = current(categories, "memo_id")
    cur_epi = current(episodes, "episode_id")
    cur_codes = current(codes, "code_id")
    endings = {}
    for e in cur_epi:
        endings[e["outcome_status"]] = endings.get(e["outcome_status"], 0) + 1
    classes = {}
    for i in incidents:
        classes[i["epistemic_class"]] = classes.get(i["epistemic_class"], 0) + 1
    # Cycle sizes: the two selection records name the interviews added in cycles 2 and 3;
    # the bound interviews they do not name are the pilot's.
    bound = {Path(s["path"]).name for s in inputs["sources"]}
    added = [{s["file"] for s in json.load(open(PACKET.parents[1] / name, encoding="utf-8"))} & bound
             for name in ("C002_SELECTION.json", "C003_SELECTION.json")]
    pilot = bound - added[0] - added[1]
    return {
        "interviews after cycle 1 (pilot)": len(pilot),
        "interviews after cycle 2": len(pilot) + len(added[0]),
        "interviews after cycle 3": len(pilot) + len(added[0]) + len(added[1] - added[0]),
        "bound interview transcripts": len(inputs["sources"]),
        "incident records": len(incidents),
        "incidents with exact quotation hashes": sum(1 for i in incidents if i.get("quote_ref")),
        "comparison records": len(comparisons),
        "category versions": len(categories),
        "current categories": len({c["category_id"] for c in cur_cat}),
        "memo versions": len(memos),
        "sampling requests": len(requests),
        "episode versions": len(episodes),
        "current account envelopes": len(cur_epi),
        "code versions": len(codes),
        "current codes": len(cur_codes),
        "current envelopes with UNKNOWN ending": endings.get("UNKNOWN", 0),
        "incidents coded as directly observed action": classes.get("OBSERVED_ACTION", 0),
        "sampling requests left PROPOSED": sum(1 for r in requests if r.get("status") == "PROPOSED"),
    }


def main():
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    stated = {c["what"]: c for c in manifest.get("counts", [])}
    computed = recompute()
    print("== 1. counts recomputed from the sealed packet and the selection records")
    for what, value in computed.items():
        if what in stated:
            check(stated[what]["value"] == value,
                  f"{what}: manifest says {stated[what]['value']} {stated[what]['unit']}, records give {value}")
        else:
            print(f"INFO {what}: {value} (not stated in MANIFEST.json)")
    for what in stated:
        if what not in computed:
            check(False, f"{what}: stated in MANIFEST.json but not recomputed here")

    print("== 2. original seal and explicitly derived release packet")
    derivation = json.loads((PACKET / "RELEASE_DERIVATION.json").read_text(encoding="utf-8"))
    derived = {d["path"]: d for d in derivation["derived_files"]}
    check(set(derived) == {"INPUT_MANIFEST.json", "MANIFEST.json"},
          "exactly two declared release derivatives")
    check(sha256(PACKET / "SHA256SUMS") == derivation["original_seal_sha256"],
          "original SHA256SUMS preserved byte-for-byte")
    omitted = set(derivation.get("omitted_original_files", []))
    check(omitted == {"HANDOFF.md"} and not (PACKET / "HANDOFF.md").exists(),
          "only the duplicate original handoff is omitted")
    original_names = set()
    for line in (PACKET / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, name = line.split(None, 1)
        name = name.strip()
        if Path(name).name != name or name in original_names:
            check(False, "invalid or duplicate original seal path")
            continue
        original_names.add(name)
        if name in omitted:
            continue
        actual = sha256(PACKET / name)
        if name in derived:
            d = derived[name]
            check(d["original_sha256"] == digest and d["release_sha256"] == actual,
                  f"{name}: original and release fingerprints explicitly distinguished")
            if name == "INPUT_MANIFEST.json":
                note = json.loads((PACKET / name).read_text(encoding="utf-8")).get("_redaction_note", "")
                check(digest == SEALED_INPUT_MANIFEST_SHA256 and digest in note,
                      "INPUT_MANIFEST.json: existing redaction note retains original fingerprint")
        else:
            check(actual == digest, f"{name}: {actual[:12]}… matches the original seal")
    check(original_names - set(derived) - omitted == set(derivation["unchanged_original_files"]),
          "unchanged-file inventory matches original seal")
    release_names, release_problems = set(), []
    for line in (PACKET / "RELEASE_SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, name = line.split(None, 1)
        name = name.strip()
        if Path(name).name != name or name in release_names:
            release_problems.append("invalid or duplicate path")
            continue
        release_names.add(name)
        if not (PACKET / name).is_file() or sha256(PACKET / name) != digest:
            release_problems.append(name)
    present_packet = {p.name for p in PACKET.iterdir() if p.is_file() and p.name != "RELEASE_SHA256SUMS"}
    check(not release_problems and release_names == present_packet,
          "RELEASE_SHA256SUMS covers every current packet file with matching bytes")

    print("== 3. worked example regenerates byte-for-byte")
    spec = importlib.util.spec_from_file_location("trace_comparison", ROOT / "example" / "trace_comparison.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    regenerated = mod.build()
    shipped = TRACE.read_text(encoding="utf-8") if TRACE.exists() else None
    check(shipped == regenerated, "example/output/TRACE.md equals a fresh run of example/trace_comparison.py")

    print("== 4. entry points and fixture")
    for p in manifest.get("entry_points", []):
        check((ROOT / p).exists(), f"entry point present: {p}")
    fixture = ROOT / "tool" / "examples" / "synthetic" / "C001"
    expected = {"CATEGORY_MEMOS.jsonl", "CODES.jsonl", "COMPARISONS.jsonl", "EPISODES.jsonl",
                "INCIDENTS.jsonl", "MANIFEST.json", "MEMOS.jsonl", "SAMPLING_REQUESTS.jsonl"}
    check(fixture.is_dir() and expected <= {p.name for p in fixture.iterdir()},
          "synthetic fixture tool/examples/synthetic/C001 has its eight packet files")
    for p in manifest.get("example", {}).get("input", []) + manifest.get("example", {}).get("output", []):
        check((ROOT / p).exists(), f"example path present: {p}")

    print("== 5. shipped files match MANIFEST.json")
    listed = {f["path"]: f for f in manifest.get("files", [])}
    present, problems = {}, []
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT).as_posix()
        if p.is_symlink():
            problems.append(f"{rel}: symlink")
            continue
        if not p.is_file() or p == MANIFEST or p.name == ".DS_Store" or "__pycache__" in p.parts or p.suffix == ".pyc":
            continue
        present[rel] = p
    for rel, p in present.items():
        f = listed.get(rel)
        if f is None:
            problems.append(f"{rel}: present but not listed")
        elif p.stat().st_size != f["bytes"] or sha256(p) != f["sha256"]:
            problems.append(f"{rel}: size or SHA-256 differs from the listing")
    problems += [f"{rel}: listed but missing" for rel in listed if rel not in present]
    for prob in problems:
        print("     " + prob)
    check(not problems, f"{len(present)} files present, {len(listed)} listed; sizes and SHA-256 agree; no symlinks")
    biggest = max((p.stat().st_size for p in present.values()), default=0)
    check(biggest < 100 * 1024 * 1024, f"largest file {biggest} bytes, under 100 MB")

    print()
    if failures:
        print(f"{len(failures)} check(s) failed")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
