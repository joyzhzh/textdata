#!/usr/bin/env python3
"""Validate a lean SOTA-scout bundle (skill v0.5.2).

Mechanical artifact gate plus claim-language ceiling for the default bundle:
SCOPE.md, SEARCH_LOG.jsonl, SCREENING.jsonl, EVIDENCE_LEDGER.jsonl,
FINDINGS.md, optional SHA-256 manifest (SHA256SUMS / *.sha256).

Enforces parseability, required keys, ID uniqueness, referential integrity,
enum states, and forbidden claim wording keyed to the declared run type.
It does NOT measure recall or coverage adequacy — the coverage gate remains
a reported judgment (SKILL.md, "Validate two gates, once").

Usage: python3 validate_lean_bundle.py [--partial] <bundle-dir>

--partial: mid-campaign mode — files not yet written are reported INFO and
skipped instead of failing; every check whose inputs exist still runs.
Cross-file checks run only when both sides exist.

On a passing FULL run the validator prints `bundle_sha256`: sha256 over the
sorted `<relpath> <filesha256>` lines of the bundle's top-level regular
files, excluding `SHA256SUMS`, `GATE_LOG.md`, `HANDOFF__*.md`, and
hidden/AppleDouble files. That value is the bundle hash of record for
RETURN lines and acceptance rows.

Exit:  0 = no FAIL (warnings allowed) · 1 = at least one FAIL · 2 = usage/IO.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

RUN_TYPES = {
    "bounded-lookup", "bounded-preservation", "rapid-scout",
    "high-recall-map", "systematic-review-ready",
}

SEARCH_KEYS = [
    "query_id", "frame", "cell_ids", "source_or_platform",
    "exact_query_or_traversal", "started_at", "ended_at",
    "filters_and_limits", "result_boundary", "results_screened",
    "new_lead_ids", "updated_work_ids", "duplicate_count",
    "exclusion_count", "unresolved_count", "state", "limitation",
]
SEARCH_CORE = ["query_id", "frame", "source_or_platform",
               "exact_query_or_traversal", "state"]
SEARCH_STATES = {"complete", "partial", "blocked"}

SCREEN_KEYS = [
    "lead_id", "canonical_label", "primary_locator", "first_seen_query_id",
    "cell_ids", "year_or_version", "decision", "reason", "work_id",
    "duplicate_or_supersession_target", "checked_at",
]
SCREEN_CORE = ["lead_id", "canonical_label", "decision"]
DECISIONS = {"deep-code", "context", "merge", "exclude", "unresolved"}

CLAIM_CORE = ["claim_id", "claim", "exact_locator", "observed_at",
              "evidence_class", "confidence"]

# Claim-language ceiling. A match negated within the preceding window
# ("not saturated", "no exhaustive claim", "never proof of") is permitted.
FORBIDDEN_ALL = [
    r"\bexhaustive\b", r"\bcomplete\s+sota\b", r"\ball\s+resources\b",
    r"\bcomplete\s+global\s+landscape\b", r"\buniversal\s+winner\b",
]
FORBIDDEN_BELOW_SYSTEMATIC = [
    r"\bcomprehensive\b", r"\bnear-comprehensive\b", r"\bsaturated\b",
    r"\bsystematic\s+review\b", r"\bfinite-source-complete\b",
]
NEGATORS = re.compile(
    r"\b(not|no|never|non|without|cannot|nor|forbid\w*|avoid\w*)\b"
    r"|rather than|instead of|does not|do not|makes? no|is not",
    re.IGNORECASE,
)
NEG_WINDOW = 40

BUNDLE_HASH_EXCLUDE = re.compile(r"^(SHA256SUMS|GATE_LOG\.md|HANDOFF__.*\.md)$")

results = []


def add(level, check, detail=""):
    results.append((level, check, detail))


def read_jsonl(path):
    rows, bad = [], 0
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                rows.append((n, json.loads(line)))
            except json.JSONDecodeError as exc:
                bad += 1
                add("FAIL", f"{path.name}:parse", f"line {n}: {exc}")
    if not bad:
        add("PASS", f"{path.name}:parse", f"{len(rows)} rows")
    return rows


def check_keys(name, rows, keys, core, enum_field=None, enum=None):
    for n, row in rows:
        missing = [k for k in keys if k not in row]
        if missing:
            add("FAIL", f"{name}:keys", f"line {n} missing {missing}")
        empty_core = [k for k in core
                      if row.get(k) in (None, "", []) ]
        if empty_core:
            add("FAIL", f"{name}:core", f"line {n} null/empty {empty_core}")
        if enum_field and row.get(enum_field) not in enum:
            add("FAIL", f"{name}:enum",
                f"line {n} {enum_field}={row.get(enum_field)!r}")


def unique(name, rows, field):
    seen = {}
    for n, row in rows:
        val = row.get(field)
        if val in (None, ""):
            continue
        if val in seen:
            add("FAIL", f"{name}:unique",
                f"{field}={val!r} on lines {seen[val]} and {n}")
        seen[val] = n
    return set(seen)


def scan_findings(text, run_type):
    lowered = text.lower()

    def flag(patterns, label):
        for pat in patterns:
            for m in re.finditer(pat, lowered):
                window = lowered[max(0, m.start() - NEG_WINDOW):m.start()]
                if NEGATORS.search(window):
                    continue
                add("FAIL", "claim-ceiling",
                    f"{label} wording {m.group(0)!r} without negation "
                    f"(char {m.start()})")

    flag(FORBIDDEN_ALL, "forbidden")
    if run_type != "systematic-review-ready":
        flag(FORBIDDEN_BELOW_SYSTEMATIC, f"above-{run_type}")

    required = {
        "rapid-scout": [(r"representative", "representative"),
                        (r"no\s+recall|not\s+recall", "no-recall label")],
        "high-recall-map": [(r"effort-bounded|working\s+plateau",
                             "effort-bounded / working-plateau label"),
                            (r"\bas\s+of\b", "'as of <date>' label")],
        "bounded-lookup": [(r"no[- ]claim", "no-claim statement")],
        "bounded-preservation": [(r"no[- ]claim", "no-claim statement")],
    }
    for pat, label in required.get(run_type, []):
        if re.search(pat, lowered):
            add("PASS", "claim-label", label)
        else:
            add("FAIL", "claim-label", f"missing {label} for {run_type}")
    if run_type == "systematic-review-ready":
        add("INFO", "claim-label",
            "systematic tier: label gates run outside this linter")


def verify_manifest(bundle, manifest):
    for n, line in enumerate(manifest.read_text(encoding="utf-8")
                             .splitlines(), 1):
        m = re.match(r"^([0-9a-f]{64})\s+\*?(.+)$", line.strip())
        if not m:
            continue
        digest, rel = m.groups()
        target = bundle / rel
        if not target.is_file():
            add("FAIL", "manifest", f"line {n}: missing file {rel}")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            add("FAIL", "manifest", f"{rel}: hash mismatch")
        else:
            add("PASS", "manifest", rel)


def bundle_sha256(bundle):
    lines = []
    for p in sorted(bundle.iterdir()):
        if not p.is_file():
            continue
        if p.name.startswith(".") or p.name.startswith("._"):
            continue
        if BUNDLE_HASH_EXCLUDE.match(p.name):
            continue
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append(f"{p.name} {digest}")
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def main():
    argv = sys.argv[1:]
    partial = "--partial" in argv
    args = [a for a in argv if a != "--partial"]
    if len(args) != 1:
        print(__doc__)
        return 2
    bundle = Path(args[0])
    if not bundle.is_dir():
        print(f"not a directory: {bundle}")
        return 2

    required = ["SCOPE.md", "SEARCH_LOG.jsonl", "SCREENING.jsonl",
                "EVIDENCE_LEDGER.jsonl", "FINDINGS.md"]
    missing = [f for f in required if not (bundle / f).is_file()]
    if partial:
        for f in missing:
            add("INFO", "files", f"absent mid-campaign: {f}")
    else:
        for f in missing:
            add("FAIL", "files", f"missing {f}")
        if missing:
            report()
            return 1

    run_type = None
    if (bundle / "SCOPE.md").is_file():
        scope = (bundle / "SCOPE.md").read_text(encoding="utf-8")
        if not scope.strip():
            add("FAIL", "SCOPE.md", "empty")
        m = re.search(r"^\s*run[_ ]?type\s*[:=]\s*`?([a-z-]+)`?",
                      scope, re.IGNORECASE | re.MULTILINE)
        run_type = m.group(1).lower() if m else None
        if run_type not in RUN_TYPES:
            add("FAIL", "SCOPE.md:run_type",
                f"missing or invalid literal run_type line (got {run_type!r})")
            run_type = None
        else:
            add("PASS", "SCOPE.md:run_type", run_type)

    have_search = (bundle / "SEARCH_LOG.jsonl").is_file()
    query_ids = set()
    if have_search:
        search = read_jsonl(bundle / "SEARCH_LOG.jsonl")
        check_keys("SEARCH_LOG", search, SEARCH_KEYS, SEARCH_CORE,
                   "state", SEARCH_STATES)
        for n, row in search:
            rs = row.get("results_screened")
            if not (isinstance(rs, int) or rs == "not_available"):
                add("FAIL", "SEARCH_LOG:results_screened",
                    f"line {n}: {rs!r} (int or 'not_available')")
        query_ids = unique("SEARCH_LOG", search, "query_id")

    have_screen = (bundle / "SCREENING.jsonl").is_file()
    deep_work_ids = set()
    screen = []
    if have_screen:
        screen = read_jsonl(bundle / "SCREENING.jsonl")
        check_keys("SCREENING", screen, SCREEN_KEYS, SCREEN_CORE,
                   "decision", DECISIONS)
        unique("SCREENING", screen, "lead_id")
        for n, row in screen:
            fsq = row.get("first_seen_query_id")
            if have_search and fsq and fsq not in query_ids:
                add("FAIL", "SCREENING:lineage",
                    f"line {n}: first_seen_query_id {fsq!r} not in search log")
            if row.get("decision") == "deep-code":
                if row.get("work_id") in (None, ""):
                    add("FAIL", "SCREENING:deep-code",
                        f"line {n}: deep-code without work_id")
                else:
                    deep_work_ids.add(row["work_id"])
            if row.get("decision") == "merge" and not row.get(
                    "duplicate_or_supersession_target"):
                add("FAIL", "SCREENING:merge",
                    f"line {n}: merge without target")

    have_ledger = (bundle / "EVIDENCE_LEDGER.jsonl").is_file()
    if have_ledger:
        ledger = read_jsonl(bundle / "EVIDENCE_LEDGER.jsonl")
        work_ids = unique("EVIDENCE_LEDGER", ledger, "work_id")
        claim_ids = set()
        for n, row in ledger:
            if row.get("work_id") in (None, ""):
                add("FAIL", "EVIDENCE_LEDGER:work_id", f"line {n}: missing")
            claims = row.get("claims", [])
            if not isinstance(claims, list) or not claims:
                add("WARN", "EVIDENCE_LEDGER:claims",
                    f"line {n}: no claim objects")
                continue
            for c in claims:
                empty = [k for k in CLAIM_CORE if c.get(k) in (None, "")]
                if empty:
                    add("FAIL", "EVIDENCE_LEDGER:claim-core",
                        f"line {n}: null/empty {empty}")
                cid = c.get("claim_id")
                if cid:
                    if cid in claim_ids:
                        add("FAIL", "EVIDENCE_LEDGER:claim-unique",
                            f"duplicate claim_id {cid!r}")
                    claim_ids.add(cid)
        if have_screen:
            orphaned = deep_work_ids - work_ids
            if orphaned:
                add("FAIL", "lineage:deep-code→ledger",
                    f"deep-coded work_ids missing from ledger: "
                    f"{sorted(orphaned)}")
            extra = work_ids - {r.get("work_id") for _, r in screen}
            if extra:
                add("WARN", "lineage:ledger-only",
                    f"ledger work_ids never screened (legacy import?): "
                    f"{sorted(extra)[:5]}")

    if (bundle / "FINDINGS.md").is_file():
        scan_findings((bundle / "FINDINGS.md").read_text(encoding="utf-8"),
                      run_type or "high-recall-map")

    manifests = [p for p in bundle.iterdir()
                 if p.name == "SHA256SUMS" or p.suffix == ".sha256"]
    if manifests:
        verify_manifest(bundle, manifests[0])
    else:
        add("INFO", "manifest", "none present (required only by repo policy)")

    code = report()
    if not partial and code == 0:
        digest = bundle_sha256(bundle)
        print(f"bundle_sha256 = {digest}")
        print(f"bundle_sha12  = {digest[:12]}  (hash of record for RETURN "
              f"and ACCEPT rows)")
    elif partial:
        print("PARTIAL MODE: mid-campaign check only — no bundle hash, no "
              "final-gate claim")
    return code


def report():
    fails = 0
    for level, check, detail in results:
        print(f"{level:4} — {check}" + (f" — {detail}" if detail else ""))
        fails += level == "FAIL"
    claim_fail = any(l == "FAIL" and c.startswith("claim")
                     for l, c, _ in results)
    art_fail = any(l == "FAIL" and not c.startswith("claim")
                   for l, c, _ in results)
    print(f"ARTIFACT GATE: {'FAIL' if art_fail else 'PASS'}")
    print(f"CLAIM CEILING: {'FAIL' if claim_fail else 'PASS'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
