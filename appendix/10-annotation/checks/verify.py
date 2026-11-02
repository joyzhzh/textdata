#!/usr/bin/env python3
"""Verify the annotation component: the 16 software checks, the byte-identical
replay of the worked example, the counts stated in README.md, and that the
release edition of 2 November 2026 left the retained request file, the
candidate responses and the exported records byte-identical, with its derived
manifest, receipt and run record labelled as such (see NOTICE.md).

Python 3.9 or newer, standard library only. No network, no model call.
Writes fixtures and RESULTS.json to --out (default: a fresh temporary folder);
never writes inside the component folder. Exit 0 when every check passes.

The 16 cases reproduce the fault cases of the 29 October 2026 check script
(whose recorded results are in checks/recorded-2026-10-29/CHECK_RESULTS.json).
They test software behaviour, never annotation correctness: two cases,
semantic_limit_wrong_actor_still_passes and semantic_limit_omission_still_passes,
pass by design although the annotation they carry is wrong.
"""
import argparse
import copy
import csv
import hashlib
import importlib.util
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tool" / "workflow.py"
EXAMPLE = ROOT / "example"
PACKAGE = EXAMPLE / "prepared"
RESPONSE = EXAMPLE / "candidate" / "candidate_response.jsonl"
RECEIPT = EXAMPLE / "candidate" / "producer_receipt.json"
OUTPUT = EXAMPLE / "output"
RECORDED = ROOT / "checks" / "recorded-2026-10-29"

# The counts README.md states, with their units.
EXPECTED = {
    "requested_units": (5, "coding units (passages)"),
    "annotated_units": (5, "unit records with status annotated"),
    "no_assignment_units": (1, "unit records with disposition no_assignment"),
    "candidate_relations": (4, "relation records"),
    "mandatory_relations": (4, "relation records with modality mandatory"),
    "other_modality_relations": (0, "relation records in the other four modalities"),
    "qualifier_spans": (14, "quoted qualification spans"),
    "other_role_spans": (5, "quoted other-party spans"),
    "located_spans": (32, "quoted spans with character positions (evidence, actor, action, qualifier, other role)"),
    "feature_rows": (5, "rows in features.csv"),
    "frozen_requests": (5, "requests in prepared/requests.jsonl"),
    "frozen_files": (7, "files listed in prepared/manifest.json"),
    "software_checks": (16, "check cases"),
    "replay_identical_files": (6, "output files identical on replay"),
}


def load_workflow():
    spec = importlib.util.spec_from_file_location("workflow", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def software_checks(w, out):
    """The 16 cases, in the order and with the expectations of the 29 October script."""
    rows = w.read_jsonl(RESPONSE)
    receipt = w.read_json(RECEIPT)
    results = []

    def run(name, candidate, expect_refusal=False, assertion=None, change_receipt=None):
        response = out / f"{name}.jsonl"
        w.write_jsonl(response, candidate)
        rec = copy.deepcopy(receipt)
        rec["response_sha256"] = w.digest(response)
        if change_receipt:
            change_receipt(rec)
        try:
            validated, _ = w.validate(PACKAGE, response, rec)
            if expect_refusal:
                results.append({"case": name, "passed": False, "error": "accepted invalid input"})
                return
            if assertion:
                assertion(validated)
            results.append({"case": name, "passed": True})
        except ValueError as e:
            results.append({"case": name, "passed": expect_refusal, "refusal": str(e)})
        except AssertionError:
            results.append({"case": name, "passed": False, "error": "assertion failed"})

    def eq(actual, expected):
        assert actual == expected, (actual, expected)

    run("original", rows, assertion=lambda r: eq((len(r), sum(len(x["relations"]) for x in r)), (5, 4)))
    bad = copy.deepcopy(rows); bad[1]["relations"][0]["action_quote"] = "invented action absent from source"
    run("unsupported_quote", bad, True)
    bad = copy.deepcopy(rows); bad[1]["relations"][0]["modality"] = "legally_enforced"
    run("unknown_label", bad, True)
    run("duplicate_unit", rows + [rows[0]], True)
    bad = copy.deepcopy(rows); bad[0]["unit_id"] = "unknown-unit"
    run("unknown_unit", bad, True)
    bad = copy.deepcopy(rows); bad[3]["relations"][0].pop("actor_occurrence")
    run("ambiguous_actor_location", bad, True)
    bad = copy.deepcopy(rows); bad[1]["relations"].append(bad[1]["relations"][0])
    run("duplicate_relation", bad, True)
    run("missing_response_preserved", rows[:-1], assertion=lambda r: eq((len(r), r[-1]["status"], r[-1]["disposition"]), (5, "missing", "unresolved")))
    bad = copy.deepcopy(rows); bad[4] = {"unit_id": "u5", "status": "abstain", "disposition": "unresolved", "reason": "Illustrative fault test, not a new model run", "relations": []}
    run("abstention_is_not_negative", bad, assertion=lambda r: eq((r[-1]["status"], r[-1]["disposition"]), ("abstain", "unresolved")))
    run("wrong_package_receipt", rows, True, change_receipt=lambda r: r.update(manifest_sha256="0" * 64))
    run("wrong_response_hash", rows, True, change_receipt=lambda r: r.update(response_sha256="0" * 64))
    run("no_false_human_reference", rows, True, change_receipt=lambda r: r.update(annotation_provenance="human_reference"))
    # Deliberately wrong but source-contained: the consulted stakeholders become the actor. Accepted mechanically.
    bad = copy.deepcopy(rows); bad[1]["relations"][0]["actor_quote"] = "key stakeholders identified by the Director"
    run("semantic_limit_wrong_actor_still_passes", bad, assertion=lambda r: eq(r[1]["relations"][0]["actor"]["quote"], "key stakeholders identified by the Director"))
    # Deliberately wrong: the assignment in u3 is suppressed as no_assignment. Accepted mechanically.
    bad = copy.deepcopy(rows); bad[2]["relations"] = []; bad[2]["disposition"] = "no_assignment"
    run("semantic_limit_omission_still_passes", bad, assertion=lambda r: eq(len(r[2]["relations"]), 0))
    validated, _ = w.validate(PACKAGE, RESPONSE, receipt)
    for record in validated:
        assert record["row_sha256"] == w.seal(record)
    damaged = copy.deepcopy(validated[1]); damaged["relations"][0]["modality"] = "recommended"
    results.append({"case": "changed_annotation_breaks_seal", "passed": damaged["row_sha256"] != w.seal(damaged)})
    frozen = w.read_json(PACKAGE / "manifest.json")
    results.append({"case": "all_frozen_files_match", "passed": all(w.digest(PACKAGE / k) == v for k, v in frozen["files"].items())})
    return results


def replay(w, out):
    target = out / "replay"
    w.export(PACKAGE, RESPONSE, RECEIPT, target)
    names = ["annotations.jsonl", "features.csv", "summary.json", "reference_template.jsonl", "response.jsonl", "producer_receipt.json"]
    identical = {n: (target / n).read_bytes() == (OUTPUT / n).read_bytes() for n in names}
    recorded_run = w.read_json(OUTPUT / "run.json")
    recorded_hashes_match = all(sha256(OUTPUT / n) == h for n, h in recorded_run["output_sha256"].items())
    return {"identical_outputs": identical, "recorded_output_hashes_match": recorded_hashes_match,
            "adapter_sha256_matches_recorded_run": sha256(TOOL) == recorded_run["adapter_sha256"],
            "note": "Deterministic replay of saved candidate output; run.json differs in its execution timestamp, and the shipped copy also carries its release-derived label."}


def release_edition(w):
    """Compare the release-derived manifest, receipt and run record with the 29 October originals kept in checks/recorded-2026-10-29/."""
    old_manifest, new_manifest = w.read_json(RECORDED / "manifest.json"), w.read_json(PACKAGE / "manifest.json")
    old_receipt, new_receipt = w.read_json(RECORDED / "producer_receipt.json"), w.read_json(RECEIPT)
    old_run, new_run = w.read_json(RECORDED / "run.json"), w.read_json(OUTPUT / "run.json")
    changed = sorted(k for k in old_manifest["files"] if new_manifest["files"].get(k) != old_manifest["files"][k])
    records = ["annotations.jsonl", "features.csv", "summary.json", "reference_template.jsonl", "response.jsonl"]
    rows = [
        {"check": "originals_kept_and_named", "ok": sha256(RECORDED / "manifest.json") == old_receipt["manifest_sha256"] == new_manifest.get("original_manifest_sha256") == new_receipt.get("original_manifest_sha256")
            and sha256(RECORDED / "producer_receipt.json") == new_receipt.get("original_receipt_sha256") and sha256(RECORDED / "run.json") == new_run.get("original_run_sha256")},
        {"check": "derived_records_labelled", "ok": all(str(r.get("record", "")).startswith("Release-derived") for r in (new_manifest, new_receipt, new_run))},
        {"check": "derived_receipt_bound_to_shipped_package", "ok": new_receipt["manifest_sha256"] == sha256(PACKAGE / "manifest.json")},
        {"check": "only_study_file_changed_in_package", "ok": sorted(old_manifest["files"]) == sorted(new_manifest["files"]) and changed == ["study.json"], "changed": changed},
        {"check": "request_file_identical_to_2026-10-29", "ok": new_manifest["files"]["requests.jsonl"] == old_manifest["files"]["requests.jsonl"] == sha256(PACKAGE / "requests.jsonl")},
        {"check": "responses_and_records_identical_to_2026-10-29", "ok": all(sha256(OUTPUT / n) == old_run["output_sha256"][n] for n in records) and sha256(RESPONSE) == old_receipt["response_sha256"]},
        {"check": "derived_receipt_repeats_original_fields", "ok": all(new_receipt.get(k) == v for k, v in old_receipt.items() if k != "manifest_sha256")},
    ]
    return rows


def counts(w, check_results, replay_result):
    records = w.read_jsonl(OUTPUT / "annotations.jsonl")
    text = (EXAMPLE / "input" / "source" / "2020-27065.txt").read_text(encoding="utf-8")
    spans, mismatched, qualifiers, roles, relations = 0, 0, 0, 0, 0
    modality = {}
    for r in records:
        items = [r["evidence"]] if r["evidence"] else []
        for rel in r["relations"]:
            relations += 1
            modality[rel["modality"]] = modality.get(rel["modality"], 0) + 1
            items += [rel["actor"], rel["action"]] + rel["qualifiers"] + rel["other_roles"]
            qualifiers += len(rel["qualifiers"])
            roles += len(rel["other_roles"])
        for s in items:
            spans += 1
            if text[s["start"]:s["end"]] != s["quote"]:
                mismatched += 1
    with (OUTPUT / "features.csv").open(encoding="utf-8", newline="") as f:
        feature_rows = sum(1 for _ in csv.DictReader(f))
    observed = {
        "requested_units": len(records),
        "annotated_units": sum(r["status"] == "annotated" for r in records),
        "no_assignment_units": sum(r["disposition"] == "no_assignment" for r in records),
        "candidate_relations": relations,
        "mandatory_relations": modality.get("mandatory", 0),
        "other_modality_relations": relations - modality.get("mandatory", 0),
        "qualifier_spans": qualifiers,
        "other_role_spans": roles,
        "located_spans": spans,
        "feature_rows": feature_rows,
        "frozen_requests": len(w.read_jsonl(PACKAGE / "requests.jsonl")),
        "frozen_files": len(w.read_json(PACKAGE / "manifest.json")["files"]),
        "software_checks": len(check_results),
        "replay_identical_files": sum(replay_result["identical_outputs"].values()),
    }
    summary = w.read_json(OUTPUT / "summary.json")
    table = []
    for key, (expected, unit) in EXPECTED.items():
        table.append({"what": key, "unit": unit, "expected": expected, "observed": observed[key], "ok": observed[key] == expected})
    table.append({"what": "span_quotes_match_source", "unit": "mismatched spans", "expected": 0, "observed": mismatched, "ok": mismatched == 0})
    table.append({"what": "summary_counts_agree", "unit": "summary.json", "expected": True,
                  "observed": summary["requested_units"] == observed["requested_units"] and summary["no_assignment_units"] == observed["no_assignment_units"] and summary["candidate_relation_counts"]["mandatory"] == observed["mandatory_relations"],
                  "ok": None})
    table[-1]["ok"] = table[-1]["observed"] is True
    table.append({"what": "reference_relative_accuracy_is_null", "unit": "summary.json", "expected": True, "observed": summary["reference_relative_accuracy"]["value"] is None, "ok": summary["reference_relative_accuracy"]["value"] is None})
    recorded = w.read_json(RECORDED / "CHECK_RESULTS.json")
    same_cases = [c["case"] for c in recorded["cases"]] == [c["case"] for c in check_results]
    table.append({"what": "check_cases_match_recorded_2026-10-29", "unit": "case names in order", "expected": True, "observed": same_cases, "ok": same_cases})
    return table


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", help="folder for fixtures, replay and RESULTS.json (default: new temporary folder)")
    args = parser.parse_args()
    out = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="annotation-verify-"))
    out.mkdir(parents=True, exist_ok=True)
    w = load_workflow()
    check_results = software_checks(w, out)
    replay_result = replay(w, out)
    table = counts(w, check_results, replay_result)
    edition = release_edition(w)
    passed_checks = sum(r["passed"] for r in check_results)
    all_ok = (passed_checks == len(check_results)
              and all(replay_result["identical_outputs"].values())
              and replay_result["recorded_output_hashes_match"]
              and replay_result["adapter_sha256_matches_recorded_run"]
              and all(row["ok"] for row in table)
              and all(row["ok"] for row in edition))
    result = {
        "scope": "Software integrity checks, deterministic replay, README count verification and release-edition comparison; no accuracy test",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "software_checks": {"passed": passed_checks, "total": len(check_results), "cases": check_results},
        "replay": replay_result,
        "counts": table,
        "release_edition": edition,
        "all_ok": all_ok,
        "out": str(out),
    }
    w.write_json(out / "RESULTS.json", result)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
