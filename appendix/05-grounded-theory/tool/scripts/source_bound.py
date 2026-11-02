"""Local byte bindings and immutable-cycle checks for the source-bound workflow.

These checks establish declared links and history, never interpretation truth.
No network, deletion, model invocation or authority creation.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1]
PROFILE = "source-bound-v1"
METHOD = "inductive process study using grounded-theory techniques"
DEFAULTS = {"memo_types": ["DESCRIPTIVE", "COMPARISON", "METHODOLOGICAL", "THEORETICAL"],
            "initial_coding": "action-oriented; prefer gerunds where they capture process",
            "pending_amendments": {"six_memo_purposes": False, "optional_gerunds": False}}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def external_root(path):
    root = Path(path)
    need(root.is_absolute(), "study_root must be absolute")
    root = root.resolve()
    need(root.is_dir(), "study_root must already exist")
    need(not root.is_relative_to(TOOL) and not TOOL.is_relative_to(root), "study_root must neither contain nor sit inside the tool")
    need(not any((p / ".git").exists() for p in (root, *root.parents)), "study_root is inside a Git checkout")
    need(not any(root.rglob(".git")), "study_root contains a Git checkout")
    return root


def source_path(source, root):
    p = Path(source["path"])
    if not p.is_absolute():
        p = root / p
    p = p.resolve()
    need(p.is_relative_to(root) and p.is_file(), "source path must resolve to a file inside study_root")
    return p


def check_input(spec, root, fill_hashes=False):
    need(isinstance(spec, dict), "input manifest must be an object")
    need(spec.get("data_kind") in {"SYNTHETIC", "AUTHORIZED_REAL"}, "declare SYNTHETIC or AUTHORIZED_REAL inputs")
    for field in ("study_id", "authority_ref", "rights", "privacy", "retention", "license"):
        need(isinstance(spec.get(field), str) and spec[field].strip(), f"input manifest needs {field}")
    need(spec["retention"] == "VAULT_ONLY", "this workflow retains study outputs in the vault")
    if spec["license"] == "UNKNOWN":
        need(spec.get("unknown_license_authority_ref"), "UNKNOWN license needs an explicit recorded allowance (C001 ruling 05R where applicable)")
    processing = spec.get("model_processing", {})
    need(processing.get("authority_ref") and isinstance(processing.get("models"), list), "model_processing needs authority_ref and exact models")
    sources = spec.get("sources")
    need(isinstance(sources, list) and sources, "input manifest needs sources")
    ids = set()
    for source in sources:
        mid = source.get("manifestation_id", "")
        need(re.fullmatch(r"MNF-[A-Z0-9-]+", mid) and mid not in ids, "source identities must be unique MNF IDs")
        ids.add(mid)
        need(source.get("kind") in {"NORMALIZED_TEXT", "RAW"}, "source kind must be NORMALIZED_TEXT or RAW")
        need(source.get("language") and source.get("rights") and source.get("source_url"), "each source needs language, rights and source_url")
        p = source_path(source, root)
        observed = digest(p)
        if fill_hashes and "sha256" not in source:
            source["sha256"] = observed
        need(source.get("sha256") == observed, f"source hash mismatch: {mid}")
        for derived in source.get("derived_from", []):
            need(derived.get("transformation"), "derived source needs transformation description")
            need(digest(source_path(derived, root)) == derived.get("sha256"), "derived source hash mismatch")
    return {s["manifestation_id"]: s for s in sources}


def span(ref, sources, root):
    need(isinstance(ref, dict), "source locator must be an object")
    mid = ref.get("manifestation_id")
    need(mid in sources, f"unknown input manifestation: {mid}")
    source = sources[mid]
    need(source["kind"] == "NORMALIZED_TEXT", "deterministic line checks require an authorized normalized text source")
    loc = ref.get("locator", "")
    match = re.fullmatch(r"lines:(\d+)-(\d+)", loc)
    need(match, "locator must be lines:<first>-<last>, one-based inclusive")
    first, last = map(int, match.groups())
    lines = source_path(source, root).read_text(encoding="utf-8").splitlines()
    need(1 <= first <= last <= len(lines), "locator outside retained text")
    return "\n".join(lines[first-1:last])


def verify_seal(cycle):
    seal = cycle / "SHA256SUMS"
    need(seal.is_file(), "previous cycle must have a handoff seal")
    listed = set()
    for line in seal.read_text().splitlines():
        h, name = line.split("  ", 1)
        need(Path(name).name == name and name not in listed, "invalid seal path")
        listed.add(name)
        need((cycle / name).is_file() and digest(cycle / name) == h, f"sealed history changed: {name}")
    actual = {p.name for p in cycle.iterdir() if p.is_file() and p.name != "SHA256SUMS"}
    need(listed == actual, "seal does not cover the cycle files")


def validate_bound_cycle(cycle, manifest, rows):
    root = external_root(manifest["study_root"])
    need(cycle.resolve().is_relative_to(root), "cycle must be inside study_root")
    need(manifest.get("method_profile") == METHOD and manifest.get("method_defaults") == DEFAULTS,
         "unratified memo/coding alternatives cannot replace inherited defaults")
    need(manifest.get("research_question", "").strip(), "research question required")
    inputs = cycle / "INPUT_MANIFEST.json"
    need(digest(inputs) == manifest["input_manifest_sha256"], "frozen input manifest changed")
    spec = json.loads(inputs.read_text())
    need(spec["study_id"] == manifest["study_id"], "input study_id mismatch")
    need(spec["model_processing"] == manifest["model_processing"], "processing authority/model mismatch")
    sources = check_input(spec, root)
    previous = manifest.get("previous_cycle")
    if previous:
        prior = Path(previous["path"]).resolve()
        need(prior.is_relative_to(root) and prior != cycle.resolve(), "previous cycle outside study or self-reference")
        verify_seal(prior)
        need(digest(prior / "SHA256SUMS") == previous["seal_sha256"], "previous cycle seal changed")
        for name in rows:
            old = (prior / name).read_bytes()
            need((cycle / name).read_bytes().startswith(old), f"silent history replacement in {name}")
    if (cycle / "SHA256SUMS").exists():
        verify_seal(cycle)
    for r in rows["EPISODES.jsonl"]:
        need(all(mid in sources for mid in r["source_refs"]), "episode source_refs missing from input manifest")
        need(r.get("intended_outcome", "").strip(), "episode needs intended_outcome")
        boundary = r.get("boundary", {})
        need(boundary.get("ending") in {"OUTCOME_OBSERVED", "TRACE_ENDS", "MISSING_INTERVAL"}, "episode needs an explicit ending basis")
        for field in ("start_ref", "end_ref"):
            ref = boundary.get(field)
            need(isinstance(ref, dict) and ref.get("manifestation_id") in r["source_refs"], "boundary reference outside episode sources")
            span(ref, sources, root)
        need(boundary.get("event_order") in {"SOURCE_ORDER", "RECONSTRUCTED", "UNCERTAIN"} and "missingness" in boundary,
             "boundary needs event_order and explicit missingness")
        if boundary["ending"] != "OUTCOME_OBSERVED":
            need(r["outcome_status"] == "UNKNOWN", "trace truncation/missing outcome requires UNKNOWN, not inferred abandonment or acceptance")
        else:
            need(r["outcome_status"] != "UNKNOWN", "OUTCOME_OBSERVED conflicts with UNKNOWN")
    for r in rows["INCIDENTS.jsonl"]:
        if r.get("source_ref"):
            span(r["source_ref"], sources, root)
        if r.get("quote_ref"):
            quote = span(r["quote_ref"], sources, root)
            need(r["quote_ref"]["locator"] == r["source_ref"]["locator"], "quote/source locator mismatch")
            need(hashlib.sha256(quote.encode()).hexdigest() == r["quote_ref"]["quote_sha256"], "creator statement quote hash does not match the retained span")
        if r["epistemic_class"] == "CREATOR_STATED_INTERPRETATION":
            need(r.get("attribution_basis") == "CREATOR_STATEMENT", "behavior alone cannot establish creator-stated interpretation")
    for r in rows["COMPARISONS.jsonl"]:
        need(r.get("purpose", "").strip() and r.get("analytical_consequence", "").strip(), "comparison needs purpose and analytical_consequence")
    cats = {r["memo_id"]: r for r in rows["CATEGORY_MEMOS.jsonl"]}
    replaced = {r.get("supersedes") for r in cats.values()}
    active_categories = set()
    for r in cats.values():
        if r["memo_id"] not in replaced and r["status"] not in {"RETIRED", "SUPERSEDED"}:
            need(r["category_id"] not in active_categories, "category has multiple current versions; append with explicit supersedes")
            active_categories.add(r["category_id"])
    for r in cats.values():
        for field in ("properties", "dimensions", "conditions", "consequences"):
            need(isinstance(r.get(field), list), f"category needs explicit {field} (may be empty)")
        if r["negative_case_ids"]:
            response = r.get("negative_case_response", {})
            need(response.get("action") in {"REVISE", "SPLIT", "BOUND", "RETIRE", "RETAIN_WITH_REASON", "UNRESOLVED"}, "negative case needs analytical response")
            need(response.get("reason", "").strip() and response.get("discriminating_evidence", "").strip(), "negative-case response needs reason and discriminating evidence")
            if response["action"] in {"REVISE", "SPLIT", "BOUND"}:
                need(r.get("supersedes") in cats, "changed category must name its previous version")
                old = cats[r["supersedes"]]
                fields = {"definition", "not_this", "properties", "dimensions", "conditions", "consequences"}
                need(any(r.get(k) != old.get(k) for k in fields), "counterevidence must change analytical state, not only add a negative-case ID")
            if response["action"] == "RETIRE":
                need(r["status"] == "RETIRED", "RETIRE response requires RETIRED category")
    for r in rows["SAMPLING_REQUESTS.jsonl"]:
        need(r["status"] == "PROPOSED", "analytical workflow creates only PROPOSED requests; record later authority in the evidence vault")
        expected = r.get("expected_observations", {})
        need(all(isinstance(expected.get(k), str) and expected[k].strip() for k in ("supports", "challenges", "decision_if_missing")), "sampling needs opposing expected observations and a missing-contrast consequence")
        need(expected["supports"].strip().casefold() != expected["challenges"].strip().casefold(), "sampling observations must discriminate alternatives")
