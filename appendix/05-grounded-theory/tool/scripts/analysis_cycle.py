#!/usr/bin/env python3
"""Prepare, append, continue and seal a local qualitative analysis cycle.

No acquisition, model execution, deletion, admission or publication.
"""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from source_bound import TOOL, PROFILE, METHOD, DEFAULTS, check_input, digest, external_root, need, verify_seal
from validate_analysis_packet import PACKET_FILES, validate_packet, current_rows, read_jsonl

FILES = {"episodes": "EPISODES.jsonl", "incidents": "INCIDENTS.jsonl", "codes": "CODES.jsonl",
         "comparisons": "COMPARISONS.jsonl", "categories": "CATEGORY_MEMOS.jsonl",
         "memos": "MEMOS.jsonl", "sampling": "SAMPLING_REQUESTS.jsonl"}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def create_file(path, data):
    with path.open("xb") as f:
        f.write(data)


def tool_identity():
    # A deployed tree can be uncommitted. Bind its runtime files in addition to HEAD.
    result = subprocess.run(["git", "-C", str(TOOL), "rev-parse", "HEAD"], text=True, capture_output=True)
    need(result.returncode == 0, "use the durable tool checkout (Git HEAD is required)")
    paths = [TOOL / "SKILL.md", TOOL / "PROTOCOL.lock.json"]
    for folder in ("scripts", "schemas", "references", "templates"):
        paths += [p for p in (TOOL / folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    payload = "".join(f"{p.relative_to(TOOL)}\0{digest(p)}\n" for p in sorted(paths))
    return result.stdout.strip(), hashlib.sha256(payload.encode()).hexdigest()


def prepare(study_root, config, cycle_id, question, producer, reviewer, previous=None):
    root = external_root(study_root)
    need(__import__('re').fullmatch(r"C[0-9]{3,}", cycle_id), "cycle must be C followed by at least three digits")
    need(producer.strip() and reviewer.strip() and producer != reviewer, "producer and independent reviewer must differ")
    need(question.strip(), "research question required")
    spec = json.loads(Path(config).read_text())
    check_input(spec, root, fill_hashes=True)
    revision, tree = tool_identity()
    manifest = {"schema_version": "0.2-phase-a", "workflow_profile": PROFILE,
                "study_root": str(root), "study_id": spec["study_id"], "cycle_id": cycle_id,
                "created_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "input_manifest_sha256": hashlib.sha256(encoded(spec)).hexdigest(),
                "protocol_revision": json.loads((TOOL / "PROTOCOL.lock.json").read_text())["revision"],
                "tool_revision": revision, "tool_tree_sha256": tree,
                "producer_seat": producer, "reviewer_seat": reviewer,
                "model_processing": spec["model_processing"], "research_question": question,
                "method_profile": METHOD, "method_defaults": copy.deepcopy(DEFAULTS),
                "analysis_status": "WORKING", "release_status": "NON_RELEASE", "saturation_status": "NOT_ASSESSED"}
    if previous:
        previous = Path(previous).resolve()
        need(previous.is_relative_to(root), "previous cycle outside study_root")
        verify_seal(previous)
        old_manifest = json.loads((previous / "MANIFEST.json").read_text())
        need(old_manifest.get("workflow_profile") == PROFILE and old_manifest["study_id"] == spec["study_id"], "previous study/profile mismatch")
        old_sources = json.loads((previous / "INPUT_MANIFEST.json").read_text())["sources"]
        sources = {s['manifestation_id']: s for s in spec['sources']}
        need(all(s['manifestation_id'] in sources and sources[s['manifestation_id']]['sha256'] == s['sha256'] for s in old_sources), "preserve previous source identities/hashes; changed bytes need a new manifestation ID")
        manifest["previous_cycle"] = {"path": str(previous), "seal_sha256": digest(previous / "SHA256SUMS")}
    cycle = root / cycle_id
    cycle.mkdir()  # refuses existing cycles; a failed new cycle is left recoverable
    create_file(cycle / "MANIFEST.json", encoded(manifest))
    create_file(cycle / "INPUT_MANIFEST.json", encoded(spec))
    for name in FILES.values():
        create_file(cycle / name, (previous / name).read_bytes() if previous else b"")
    validate_packet(cycle)
    return cycle


def append(cycle, filename, additions):
    cycle = Path(cycle).resolve()
    need(filename in FILES.values(), "not an appendable analysis file")
    need(additions and all(isinstance(r, dict) for r in additions), "append requires JSON object rows")
    need(all(not any(k.startswith('__') for k in r) for r in additions), "internal fields cannot be supplied")
    with (cycle / "MANIFEST.json").open("rb") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        manifest = json.loads(lock.read())
        need(manifest.get('workflow_profile') == PROFILE, "append requires a prepared source-bound cycle")
        need(not (cycle / "SHA256SUMS").exists() and not (cycle / "HANDOFF.md").exists(), "sealed cycle cannot change; continue into a new cycle")
        target = cycle / filename
        need(not target.is_symlink(), "append target cannot be a symlink")
        before = target.read_bytes()
        need(not before or before.endswith(b'\n'), "existing rows must end with a newline; do not silently rewrite")
        validate_packet(cycle, {filename: additions})  # full prospective state, before any append
        payload = b''.join((json.dumps(r, ensure_ascii=False) + '\n').encode() for r in additions)
        with target.open("ab") as f:
            f.write(payload)
        return len(additions)


def handoff(cycle, analysis, stop_reason, stop_status="NOT_ASSESSED"):
    cycle = Path(cycle).resolve()
    need(stop_status in {"NOT_ASSESSED", "NOT_REACHED", "PROVISIONAL_SUFFICIENCY_CANDIDATE"}, "saturation declarations are not supported")
    need(stop_reason.strip(), "state the actual stopping reason")
    narrative = Path(analysis).read_text()
    need(narrative.strip(), "analytical handoff requires an authored account of support, rivals, unknowns and next discriminators")
    with (cycle / "MANIFEST.json").open("rb") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        need(not (cycle / "SHA256SUMS").exists() and not (cycle / "HANDOFF.md").exists(), "handoff exists; preserve it and continue into a new cycle")
        manifest = json.loads(lock.read())
        need(manifest.get('workflow_profile') == PROFILE, "handoff requires a source-bound cycle")
        validate_packet(cycle)
        need(read_jsonl(cycle / 'EPISODES.jsonl') and read_jsonl(cycle / 'INCIDENTS.jsonl'), "handoff needs analyzed episodes and incidents")
        parts = [f"# {manifest['study_id']} / {manifest['cycle_id']} analytical handoff\n",
                 "SUBMITTED_FOR_REVIEW; NON_RELEASE. Byte/link checks do not establish analytical validity or admission.\n",
                 f"Producer: {manifest['producer_seat']}; designated reviewer: {manifest['reviewer_seat']}. This handoff does not claim that review occurred.\n",
                 f"Method: {METHOD}. Stop status: {stop_status}; reason: {stop_reason}. Candidate sufficiency remains pending independent and human review.\n",
                 "## Analyst account\n", narrative,
                 "\n## Current analytical state\n"]
        for name, _, identity in PACKET_FILES[1:]:
            rows = read_jsonl(cycle / name)
            current = current_rows(rows, identity)
            replaced = {r.get("supersedes") for r in rows}
            retired = [r for r in rows if r[identity] not in replaced and r.get("status") == "RETIRED"]
            parts.append(f"\n### {name} — {len(current)} current / {len(retired)} latest retired / {len(rows)} historical\n")
            for row in current + retired:
                clean = {k:v for k,v in row.items() if k != '__line__'}
                parts.append('```json\n' + json.dumps(clean, ensure_ascii=False, indent=2) + '\n```\n')
        parts.append('\n## Source bindings\n\nSee INPUT_MANIFEST.json and its hash in MANIFEST.json; exact cycle files are bound by SHA256SUMS. No source is transmitted by this helper.\n')
        create_file(cycle / "HANDOFF.md", '\n'.join(parts).encode())
        files = sorted(p for p in cycle.iterdir() if p.is_file())
        create_file(cycle / "SHA256SUMS", ''.join(f'{digest(p)}  {p.name}\n' for p in files).encode())
        return cycle / "HANDOFF.md"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("prepare", help="freeze authorized input bindings in a new cycle")
    p.add_argument("--study-root", required=True, type=Path);p.add_argument("--config", required=True, type=Path)
    p.add_argument("--cycle", required=True);p.add_argument("--question", required=True)
    p.add_argument("--producer", required=True);p.add_argument("--reviewer", required=True)
    p = subs.add_parser("continue", help="copy sealed history into a new cycle")
    p.add_argument("--previous", required=True, type=Path);p.add_argument("--cycle", required=True)
    p.add_argument("--producer", required=True);p.add_argument("--reviewer", required=True)
    p.add_argument("--config", type=Path, help="optional expanded input set, preserving old source hashes")
    p = subs.add_parser("append", help="validate then append JSONL rows; never replace history")
    p.add_argument("--cycle", required=True, type=Path);p.add_argument("--file", required=True, choices=FILES)
    p.add_argument("--rows", required=True, type=Path)
    p = subs.add_parser("validate", help="check source bindings, declared structure and sealed history")
    p.add_argument("--cycle", required=True, type=Path)
    p = subs.add_parser("handoff", help="create a local review handoff and immutable byte seal")
    p.add_argument("--cycle", required=True, type=Path);p.add_argument("--analysis", required=True, type=Path)
    p.add_argument("--stop-reason", required=True)
    p.add_argument("--stop-status", default="NOT_ASSESSED", choices=["NOT_ASSESSED", "NOT_REACHED", "PROVISIONAL_SUFFICIENCY_CANDIDATE"])
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            result = prepare(args.study_root, args.config, args.cycle, args.question, args.producer, args.reviewer)
        elif args.command == "continue":
            m = json.loads((args.previous / "MANIFEST.json").read_text())
            result = prepare(Path(m['study_root']), args.config or args.previous / 'INPUT_MANIFEST.json', args.cycle,
                             m['research_question'], args.producer, args.reviewer, args.previous)
        elif args.command == "append":
            additions = [json.loads(line) for line in args.rows.read_text().splitlines() if line.strip()]
            result = f"appended {append(args.cycle, FILES[args.file], additions)} row(s)"
        elif args.command == "validate":
            m = json.loads((args.cycle / 'MANIFEST.json').read_text())
            need(m.get('workflow_profile') == PROFILE, 'use the legacy validator for structure-only packets')
            validate_packet(args.cycle.resolve());result = "PASS_SOURCE_BINDINGS_AND_STRUCTURE; analytical validity not assessed"
        else:
            result = handoff(args.cycle, args.analysis, args.stop_reason, args.stop_status)
        print(result)
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"HOLD_ANALYSIS_CYCLE: {exc}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
