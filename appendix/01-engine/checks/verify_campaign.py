#!/usr/bin/env python3
"""Verify the release edition of the retained theory-building campaign in example/campaign/
against the fixed record counts. Python 3.9+, standard library only, no network, no model.

Checks: SHA256SUMS (6 files); the edition's hash of record (bundle_sha256 over the six top-level
campaign artifacts, as the validator in tool/scout/ defines it; the hash describes this public edition); every timestamp in UTC;
the counts of search windows,
screened leads, works, manifestations and located claims; the recorded search states and
screening decisions; the stop rule (new leads in the last eight search windows); the eight
frozen capability cells; deep-code -> ledger coverage; the claim identifiers cited in
FINDINGS.md and SYNTHESIS.md all resolving to ledger claims; and the one worked trace
(lead-grf-005 -> work-doi:10.5465/amr.1999.2553248 -> clm-grf-005-01/02 -> SYNTHESIS.md).
Exit 0 when every expectation holds, 1 otherwise.
"""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent / "example" / "campaign"
SIX = ["SCOPE.md", "SEARCH_LOG.jsonl", "SCREENING.jsonl", "EVIDENCE_LEDGER.jsonl", "FINDINGS.md", "SYNTHESIS.md"]

EXPECTED = {
    "hash_of_record": "58e2ea5ca8e0d99f9f38dfe9001e769f1598b51fd8917e165f7d68a1d0abfd0c",
    "search_windows": 40,
    "search_states": {"complete": 4, "partial": 35, "blocked": 1},
    "screened_leads": 232,
    "screening_decisions": {"deep-code": 76, "context": 47, "merge": 24, "exclude": 24, "unresolved": 61},
    "works": 77,
    "manifestations": 101,
    "claims": 141,
    "claims_with_exact_locator": 141,
    "cells": {"Q-D": 33, "Q-M": 13, "T-D": 37, "T-M": 14, "C-D": 44, "C-M": 10, "O-D": 37, "O-M": 12},
    "last_eight_new_leads_min": 1,
    "last_eight_new_leads_max": 10,
    "claim_ids_cited_in_findings": 66,
    "claim_ids_cited_in_synthesis": 54,
}

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name):
    return [json.loads(line) for line in (CAMPAIGN / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    # 1. SHA256SUMS
    manifest = {}
    for line in (CAMPAIGN / "SHA256SUMS").read_text().splitlines():
        if line.strip():
            digest, name = line.split(None, 1)
            manifest[name.strip()] = digest
    ok = set(manifest) == set(SIX) and all(sha256(CAMPAIGN / n) == manifest[n] for n in SIX)
    check("SHA256SUMS: six campaign files match", ok, f"{sum(sha256(CAMPAIGN / n) == manifest.get(n) for n in SIX)}/6")

    # 2. Hash of record: sha256 over the newline-joined sorted "<name> <filesha256>" lines of the six
    #    top-level artifacts, the convention of the validator (tool/scout/scripts/validate_lean_bundle.py)
    lines = sorted(f"{n} {sha256(CAMPAIGN / n)}" for n in SIX)
    digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    check("edition hash of record reproduced", digest == EXPECTED["hash_of_record"], digest[:12])

    # 2b. Every ISO timestamp in the edition carries the UTC designator
    stamp = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?([^\d:.]|$)")
    found = [m.group(1) for n in SIX
             for m in stamp.finditer((CAMPAIGN / n).read_text(encoding="utf-8"))]
    check("every timestamp in UTC", bool(found) and all(s == "Z" for s in found), f"{len(found)} timestamps")

    # 3. Counts
    search = rows("SEARCH_LOG.jsonl")
    screening = rows("SCREENING.jsonl")
    ledger = rows("EVIDENCE_LEDGER.jsonl")
    check("search windows", len(search) == EXPECTED["search_windows"], f"{len(search)} rows")
    states = Counter(s["state"] for s in search)
    check("search states", dict(states) == EXPECTED["search_states"], str(dict(states)))
    check("screened leads", len(screening) == EXPECTED["screened_leads"], f"{len(screening)} rows")
    decisions = Counter(c["decision"] for c in screening)
    check("screening decisions", dict(decisions) == EXPECTED["screening_decisions"], str(dict(decisions)))
    check("works", len(ledger) == EXPECTED["works"], f"{len(ledger)} work rows")
    manifestations = sum(len(w["manifestations"]) for w in ledger)
    check("manifestations", manifestations == EXPECTED["manifestations"], str(manifestations))
    claims = [c for w in ledger for c in w["claims"]]
    check("claims", len(claims) == EXPECTED["claims"], str(len(claims)))
    located = sum(1 for c in claims if c.get("exact_locator"))
    check("claims with exact_locator", located == EXPECTED["claims_with_exact_locator"], f"{located}/{len(claims)}")

    # 4. Cells: works assigned per frozen capability cell
    cells = Counter(cell for w in ledger for cell in w["cell_ids"])
    check("eight frozen cells populated", dict(cells) == EXPECTED["cells"], str(dict(cells)))

    # 5. Stop rule: last eight windows still yielded new leads -> not saturated
    tail = [len(s["new_lead_ids"]) for s in search[-8:]]
    ok = len(tail) == 8 and min(tail) >= EXPECTED["last_eight_new_leads_min"] and max(tail) <= EXPECTED["last_eight_new_leads_max"] and all(t > 0 for t in tail)
    check("stop rule: positive tail, saturation not claimed", ok, f"new leads in last 8 windows {tail}")

    # 6. Closure: every deep-coded work has a ledger row; identifiers unique
    deep = {c["work_id"] for c in screening if c["decision"] == "deep-code"}
    ledger_ids = [w["work_id"] for w in ledger]
    check("deep-code -> ledger closure", deep <= set(ledger_ids), f"{len(deep & set(ledger_ids))}/{len(deep)}")
    claim_ids = [c["claim_id"] for c in claims]
    check("unique work and claim identifiers", len(set(ledger_ids)) == len(ledger_ids) and len(set(claim_ids)) == len(claim_ids))
    query_ids = {s["query_id"] for s in search}
    check("screening -> search lineage", all(c["first_seen_query_id"] in query_ids for c in screening))

    # 7. Claim identifiers cited in the two reports resolve to the ledger
    pattern = re.compile(r"clm-[a-z0-9]+-\d{3}-\d{2}")
    for name, key in (("FINDINGS.md", "claim_ids_cited_in_findings"), ("SYNTHESIS.md", "claim_ids_cited_in_synthesis")):
        cited = set(pattern.findall((CAMPAIGN / name).read_text(encoding="utf-8")))
        unresolved = cited - set(claim_ids)
        check(f"{name}: cited claim ids resolve", len(cited) == EXPECTED[key] and not unresolved, f"{len(cited)} distinct, {len(unresolved)} unresolved")

    # 8. The worked trace
    q = next((s for s in search if s["query_id"] == "Q-GRF-002"), None)
    lead = next((c for c in screening if c["lead_id"] == "lead-grf-005"), None)
    work = next((w for w in ledger if w["work_id"] == "work-doi:10.5465/amr.1999.2553248"), None)
    synthesis = (CAMPAIGN / "SYNTHESIS.md").read_text(encoding="utf-8")
    ok = (q is not None and "lead-grf-005" in q["new_lead_ids"] and q["state"] == "partial"
          and lead is not None and lead["first_seen_query_id"] == "Q-GRF-002" and lead["decision"] == "deep-code"
          and work is not None and lead["work_id"] == work["work_id"]
          and {c["claim_id"] for c in work["claims"]} == {"clm-grf-005-01", "clm-grf-005-02"}
          and all(c["exact_locator"] for c in work["claims"])
          and "clm-grf-005-01" in synthesis and "clm-grf-005-02" in synthesis)
    check("worked trace: Q-GRF-002 -> lead-grf-005 -> Langley (1999) -> two claims -> SYNTHESIS.md", ok)

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
