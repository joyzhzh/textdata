#!/usr/bin/env python3
"""Small file-based annotation adapter. Python standard library; no API calls.

prepare freezes a study, sources, units, codebook and prompt in a new directory.
export validates a supplied response and preserves its provenance in another new
directory. Missing units remain missing; no labels or human judgments are made
by this program. Existing outputs are never overwritten.
"""
import argparse
import csv
import hashlib
import json
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(path):
    return sha(Path(path).read_bytes())


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path, rows):
    Path(path).write_text("".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n" for row in rows), encoding="utf-8")


def seal(row):
    # Pattern adapted from an earlier results ledger: canonical JSON excludes its seal.
    body = {k: v for k, v in row.items() if k != "row_sha256"}
    return sha(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode())


def relative_file(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f"source path is not a file inside the study: {name}")
    return path


def prepare(study_root, out):
    root = Path(study_root)
    study = read_json(root / "study.json")
    codebook = read_json(root / "codebook.json")
    units = read_jsonl(root / "units.jsonl")
    if not units or len({u["unit_id"] for u in units}) != len(units):
        raise ValueError("units must be nonempty and have unique IDs")
    docs = {d["document_id"]: d for d in study["documents"]}
    if len(docs) != len(study["documents"]):
        raise ValueError("duplicate document IDs")
    copies = {"study.json", "codebook.json", "units.jsonl", "prompt.txt"}
    for d in docs.values():
        for key in ("raw_path", "text_path"):
            p = relative_file(root, d[key])
            if digest(p) != d[key.replace("_path", "_sha256")]:
                raise ValueError(f"source hash mismatch: {d[key]}")
            copies.add(d[key])
    for u in units:
        d = docs[u["document_id"]]
        text = relative_file(root, d["text_path"]).read_text(encoding="utf-8")
        if type(u["start"]) is not int or type(u["end"]) is not int or not 0 <= u["start"] < u["end"] <= len(text):
            raise ValueError(f"bad unit offsets: {u['unit_id']}")
        if text[u["start"]:u["end"]] != u["text"]:
            raise ValueError(f"unit does not match source: {u['unit_id']}")
        if not u.get("locator") or not u.get("split") or not u.get("family_id"):
            raise ValueError("unit needs locator, split and document-family ID")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    for name in sorted(copies):
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, target)
    requests = []
    prompt = (root / "prompt.txt").read_text(encoding="utf-8")
    for u in units:
        d = docs[u["document_id"]]
        request = {
            "request_id": f"{study['study_id']}:{u['unit_id']}",
            "unit_id": u["unit_id"], "study_id": study["study_id"],
            "instructions": prompt, "codebook": codebook,
            "document": {k: d[k] for k in ("document_id", "source_url", "publication_date", "text_sha256")},
            "context_text": (root / d["text_path"]).read_text(encoding="utf-8"),
            "coding_unit": u,
            "response_contract": {
                "unit_id": "matching ID", "status": "annotated|abstain|failed",
                "disposition": "relations_present|no_assignment|unresolved",
                "evidence_quote": "exact contiguous quote from coding_unit.text",
                "reason": "brief evidentiary explanation, not hidden reasoning",
                "relations": [{"actor_quote": "exact unit quote", "actor_occurrence": "optional zero-based index if quote repeats", "action_quote": "exact unit quote", "action_occurrence": "optional zero-based index if quote repeats", "modality": list(codebook["modalities"]), "qualifier_quotes": ["exact unit quote"], "other_roles": [{"role": "consulted|recipient|coordinator|other", "quote": "exact unit quote"}]}],
            },
        }
        request["request_sha256"] = seal(request)
        requests.append(request)
    write_jsonl(out / "requests.jsonl", requests)
    manifest = {"schema_version": "textdata-annotation-1", "study_id": study["study_id"], "created_at": datetime.now(timezone.utc).isoformat(), "files": {name: digest(out / name) for name in sorted(copies | {"requests.jsonl"})}, "adapter_sha256": digest(__file__)}
    write_json(out / "manifest.json", manifest)
    return {"units": len(units), "documents": len(docs), "manifest_sha256": digest(out / "manifest.json")}


def checked_package(package):
    root = Path(package)
    manifest = read_json(root / "manifest.json")
    for name, expected in manifest["files"].items():
        if digest(relative_file(root, name)) != expected:
            raise ValueError(f"frozen input changed: {name}")
    return root, manifest


def support(quote, unit, occurrence=None):
    if not isinstance(quote, str) or not quote or quote not in unit["text"]:
        raise ValueError(f"unsupported quote in {unit['unit_id']}: {quote!r}")
    positions, position = [], 0
    while True:
        found = unit["text"].find(quote, position)
        if found < 0:
            break
        positions.append(found)
        position = found + 1
    if occurrence is None and len(positions) != 1:
        raise ValueError(f"ambiguous quote in {unit['unit_id']}; return a longer unique quote")
    if occurrence is not None and (type(occurrence) is not int or not 0 <= occurrence < len(positions)):
        raise ValueError(f"invalid quote occurrence: {unit['unit_id']}")
    start = unit["start"] + positions[0 if occurrence is None else occurrence]
    return {"quote": quote, "start": start, "end": start + len(quote), "offset_unit": "Unicode code points in normalized source"}


def validate(package, responses, receipt):
    root, manifest = checked_package(package)
    units = read_jsonl(root / "units.jsonl")
    unit_map = {u["unit_id"]: u for u in units}
    codebook = read_json(root / "codebook.json")
    if receipt.get("annotation_provenance") != "model_generated_candidate":
        raise ValueError("this adapter exports candidates only; never manufactures reference judgments")
    if receipt.get("manifest_sha256") != digest(root / "manifest.json"):
        raise ValueError("response receipt targets a different frozen package")
    for field in ("run_id", "execution_mode", "producer", "recorded_at", "model", "settings", "context_limitations"):
        if not receipt.get(field):
            raise ValueError(f"receipt missing {field}")
    if receipt.get("response_sha256") != digest(responses):
        raise ValueError("response bytes do not match producer receipt")
    source_rows = read_jsonl(responses)
    seen, records = set(), []
    for row in source_rows:
        uid = row.get("unit_id")
        if uid not in unit_map or uid in seen:
            raise ValueError(f"unknown or duplicate unit ID: {uid}")
        seen.add(uid)
        unit = unit_map[uid]
        status = row.get("status")
        disposition = row.get("disposition")
        relations = row.get("relations")
        if status not in ("annotated", "abstain", "failed") or not isinstance(relations, list) or not isinstance(row.get("reason"), str) or not row["reason"].strip():
            raise ValueError(f"invalid response status/content: {uid}")
        if status != "annotated":
            if disposition != "unresolved" or relations:
                raise ValueError(f"abstained/failed unit cannot contain decided relations: {uid}")
        elif disposition == "no_assignment":
            if relations:
                raise ValueError(f"no_assignment contains relations: {uid}")
        elif disposition != "relations_present" or not relations:
            raise ValueError(f"annotated unit needs relations or explicit no_assignment: {uid}")
        enriched = []
        duplicate_keys = set()
        for i, rel in enumerate(relations):
            if rel.get("modality") not in codebook["modalities"]:
                raise ValueError(f"unknown modality: {uid}")
            if not isinstance(rel.get("qualifier_quotes"), list) or not isinstance(rel.get("other_roles"), list):
                raise ValueError(f"missing qualifiers/roles arrays: {uid}")
            actor = support(rel.get("actor_quote"), unit, rel.get("actor_occurrence"))
            action = support(rel.get("action_quote"), unit, rel.get("action_occurrence"))
            key = (actor["start"], actor["end"], action["start"], action["end"], rel["modality"])
            if key in duplicate_keys:
                raise ValueError(f"duplicate relation within unit: {uid}")
            duplicate_keys.add(key)
            roles = []
            for role in rel["other_roles"]:
                if role.get("role") not in ("consulted", "recipient", "coordinator", "other"):
                    raise ValueError(f"invalid actor role: {uid}")
                roles.append({"role": role["role"], **support(role.get("quote"), unit)})
            enriched.append({"relation_id": f"{uid}:r{i+1}", "actor": actor, "action": action, "modality": rel["modality"], "qualifiers": [support(q, unit) for q in rel["qualifier_quotes"]], "other_roles": roles})
        evidence = support(row.get("evidence_quote"), unit) if status == "annotated" else None
        item = {"run_id": receipt["run_id"], "unit_id": uid, "document_id": unit["document_id"], "family_id": unit["family_id"], "split": unit["split"], "locator": unit["locator"], "status": status, "disposition": disposition, "reason": row["reason"], "evidence": evidence, "relations": enriched, "annotation_provenance": "model_generated_candidate", "semantic_review": "not_performed", "supersedes": []}
        item["row_sha256"] = seal(item)
        records.append(item)
    for unit in units:
        if unit["unit_id"] not in seen:
            item = {"run_id": receipt["run_id"], "unit_id": unit["unit_id"], "document_id": unit["document_id"], "family_id": unit["family_id"], "split": unit["split"], "locator": unit["locator"], "status": "missing", "disposition": "unresolved", "reason": "No response supplied for this requested unit", "evidence": None, "relations": [], "annotation_provenance": "model_generated_candidate", "semantic_review": "not_performed", "supersedes": []}
            item["row_sha256"] = seal(item)
            records.append(item)
    records.sort(key=lambda r: list(unit_map).index(r["unit_id"]))
    return records, manifest


def export(package, responses, receipt_path, out):
    receipt = read_json(receipt_path)
    records, manifest = validate(package, responses, receipt)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(responses, out / "response.jsonl")
    shutil.copyfile(receipt_path, out / "producer_receipt.json")
    write_jsonl(out / "annotations.jsonl", records)
    fields = ["run_id", "unit_id", "document_id", "family_id", "split", "locator", "status", "disposition", "relation_id", "actor", "action", "modality", "qualifiers_json", "other_roles_json", "annotation_provenance", "semantic_review"]
    with (out / "features.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for item in records:
            base = {k: item[k] for k in fields if k in item}
            for rel in item["relations"] or [None]:
                row = dict(base)
                if rel:
                    row.update(relation_id=rel["relation_id"], actor=rel["actor"]["quote"], action=rel["action"]["quote"], modality=rel["modality"], qualifiers_json=json.dumps(rel["qualifiers"], ensure_ascii=False), other_roles_json=json.dumps(rel["other_roles"], ensure_ascii=False))
                writer.writerow(row)
    statuses = Counter(r["status"] for r in records)
    counts = Counter(rel["modality"] for r in records for rel in r["relations"])
    summary = {"study_id": manifest["study_id"], "run_id": receipt["run_id"], "scope": "Supplied coding units only; candidate annotations, not independently verified source facts", "requested_units": len(records), "unit_status_counts": dict(statuses), "no_assignment_units": sum(r["disposition"] == "no_assignment" for r in records), "candidate_relation_counts": {k: counts[k] for k in read_json(Path(package) / "codebook.json")["modalities"]}, "resolved_fraction": {"numerator": statuses["annotated"], "denominator": len(records)}, "reference_relative_accuracy": {"value": None, "reason": "No independent reference labels supplied"}, "construct_validity": "not_established", "population_estimate": {"value": None, "reason": "Illustrative selection; no probability sample or full-document coding"}}
    write_json(out / "summary.json", summary)
    # Empty judgments are deliberately not copied from model suggestions.
    review_rows = [{"unit_id": r["unit_id"], "document_id": r["document_id"], "locator": r["locator"], "reference_status": "not_coded", "reference_relations": None, "coder_id": None, "decision_reason": None} for r in records]
    write_jsonl(out / "reference_template.jsonl", review_rows)
    run = {"operation": "deterministic validation and candidate export", "executed_at": datetime.now(timezone.utc).isoformat(), "adapter_sha256": digest(__file__), "input_manifest_sha256": digest(Path(package) / "manifest.json"), "response_sha256": digest(responses), "producer_receipt_sha256": digest(receipt_path), "output_sha256": {p.name: digest(p) for p in sorted(out.iterdir()) if p.is_file()}, "checks": ["frozen input hashes", "source-contained units", "response byte identity", "unit identity and unique response", "typed status/modality", "exact unique source spans", "no duplicate relations", "explicit missingness", "candidate provenance"], "limits": ["No semantic entailment check", "No independent reference coding", "No omission/recall estimate", "No model API called by this adapter"]}
    write_json(out / "run.json", run)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--study", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("export")
    p.add_argument("--package", required=True)
    p.add_argument("--response", required=True)
    p.add_argument("--receipt", required=True)
    p.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        result = prepare(args.study, args.out) if args.command == "prepare" else export(args.package, args.response, args.receipt, args.out)
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as e:
        parser.exit(1, f"Refused: {e}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
