#!/usr/bin/env python3
"""Trace one analytical chain through the sealed C003 packet of the interview study.

Reads the study's own records (no transcripts, no network, no model) and writes
example/output/TRACE.md: pilot proposal -> sampling request -> selected interview ->
source-bound incidents -> initial codes -> comparison -> category revision -> reviewer
finding and episode correction -> successor theoretical memo -> next sampling request.

Python 3.9+, standard library only. Deterministic: the same input yields the same bytes.

Usage:
    python3 example/trace_comparison.py                 # writes example/output/TRACE.md
    python3 example/trace_comparison.py --stdout        # prints instead of writing
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKET = HERE / "input" / "study" / "snapshots" / "C003"
STUDY = HERE / "input" / "study"
OUT = HERE / "output" / "TRACE.md"

# The chain traced. Every identifier below is a row identity inside the packet.
CHAIN = {
    "pilot_memo": "MEMO005",
    "pilot_category_version": "MEM002",
    "first_request": "REQ001",
    "wave2_selection_file": "Aishwarya Naresh Reganti + Kiriti Badam.txt",
    "wave2_incidents": ["I501", "I502", "I503", "I504"],
    "wave2_comparison": "CMP015",
    "wave2_category_version": "MEM006",
    "wave2_memo": "MEMO010",
    "second_request": "REQ002",
    "wave3_selection_file": "Dan Shipper 2.0.txt",
    "wave3_incidents": ["I710", "I711", "I712"],
    "wave3_comparison": "CMP027",
    "wave3_category_version": "MEM010",
    "episode_before": "E703",
    "episode_after": "E714",
    "wave3_memo": "MEMO014",
    "third_request": "REQ003",
}


def rows(name):
    with open(PACKET / name, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def by(key, items):
    return {r[key]: r for r in items}


def locator(ref):
    if not ref:
        return "(none)"
    return f"{ref.get('manifestation_id')} {ref.get('locator')}"


def md_table(headers, body):
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for row in body:
        lines.append("| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in row) + " |")
    return "\n".join(lines)


def build():
    incidents = by("incident_id", rows("INCIDENTS.jsonl"))
    episodes = rows("EPISODES.jsonl")
    codes = rows("CODES.jsonl")
    comparisons = by("comparison_id", rows("COMPARISONS.jsonl"))
    categories = by("memo_id", rows("CATEGORY_MEMOS.jsonl"))
    memos = by("memo_id", rows("MEMOS.jsonl"))
    requests = by("request_id", rows("SAMPLING_REQUESTS.jsonl"))
    manifest = json.load(open(PACKET / "MANIFEST.json", encoding="utf-8"))
    inputs = json.load(open(PACKET / "INPUT_MANIFEST.json", encoding="utf-8"))
    sources = {s["manifestation_id"]: s for s in inputs["sources"]}
    sel2 = json.load(open(STUDY / "C002_SELECTION.json", encoding="utf-8"))
    sel3 = json.load(open(STUDY / "C003_SELECTION.json", encoding="utf-8"))
    sel2 = {s["file"]: s for s in sel2}
    sel3 = {s["file"]: s for s in sel3}

    def episode(eid):
        for e in episodes:
            if e["episode_id"] == eid:
                return e
        raise KeyError(eid)

    def code_for(iid):
        return [c for c in codes if iid in c.get("incident_ids", [])]

    out = []
    w = out.append
    w("# One comparison, traced through the sealed records")
    w("")
    w("Generated from the study's own records by `example/trace_comparison.py`. The transcripts are not "
      "reproduced: each incident carries the source file identity, the one-based line span, and, for "
      "quoted interpretations, the SHA-256 of the quoted lines. A reader holding the transcript can "
      "verify every binding; a reader without it can still follow what the analysis did with it.")
    w("")
    w(f"Packet: cycle {manifest['cycle_id']} of study {manifest['study_id']}; tool revision as "
      f"retained as historical provenance in the release-derived `MANIFEST.json`; method profile: {manifest['method_profile']}; release status "
      f"{manifest['release_status']}; saturation status {manifest['saturation_status']}.")
    w("")

    # 1. Pilot proposal
    w("## 1. The pilot's proposal (cycle C001, six interviews)")
    w("")
    m = memos[CHAIN["pilot_memo"]]
    w(f"**{m['memo_id']}** ({m['memo_type']} memo, supersedes {m.get('supersedes')}):")
    w("")
    w("> " + m["body"])
    w("")
    c = categories[CHAIN["pilot_category_version"]]
    w(f"**Category {c['category_id']}, version {c['memo_id']}** (supersedes {c.get('supersedes')}): {c['definition']}")
    w("")
    w(f"Dimensions then: {'; '.join(c.get('dimensions', []))}.")
    w("")

    # 2. First request
    r = requests[CHAIN["first_request"]]
    w(f"## 2. The pilot asked for the evidence that could break it ({r['request_id']}, status {r['status']})")
    w("")
    w(f"Discriminating question: {r['discriminating_question']}")
    w("")
    w(f"Counter-search: {r['counter_search']}")
    w("")
    w(f"Expected if supported: {r['expected_observations']['supports']}")
    w("")
    w(f"Expected if challenged: {r['expected_observations']['challenges']}")
    w("")

    # 3. Wave 2 selection and incidents
    s = sel2[CHAIN["wave2_selection_file"]]
    w("## 3. Second cycle (C002): a contrary case selected before coding")
    w("")
    w(f"Selection record for `{s['file']}` ({s['manifestation_id']}, SHA-256 `{s['sha256']}`), "
      f"stage {s['selection_stage']}, following {s['prior_request']}:")
    w("")
    w(f"- Gap: {s['gap']}")
    w(f"- Discriminating question: {s['discriminating_question']}")
    w(f"- Opposing expected observations: {s['opposing_expected_observations']}")
    w("")
    w("Incidents bound to the transcript (descriptions are the analysts' paraphrases; line spans are one-based and inclusive):")
    w("")
    body = []
    for iid in CHAIN["wave2_incidents"]:
        i = incidents[iid]
        q = i.get("quote_ref", {}).get("quote_sha256", "")
        body.append([iid, i["epistemic_class"], locator(i["source_ref"]), i["description"],
                     i.get("evidence_limit", ""), q])
    w(md_table(["Incident", "Epistemic class", "Source and lines", "Description", "Evidence limit", "Quote SHA-256"], body))
    w("")
    w("Initial codes (action-oriented, with the alternative reading each analyst recorded):")
    w("")
    body = []
    for iid in CHAIN["wave2_incidents"]:
        for cd in code_for(iid):
            body.append([cd["code_id"], iid, cd["label"], cd.get("alternative_reading", "")])
    w(md_table(["Code", "Incident", "Label", "Alternative reading"], body))
    w("")

    # 4. Wave 2 comparison and category revision
    cmp_ = comparisons[CHAIN["wave2_comparison"]]
    w(f"## 4. The comparison that changed the category ({cmp_['comparison_id']})")
    w("")
    for k in ("compared_ids", "relation", "purpose", "observation", "possible_condition",
              "rival_explanation", "discriminating_evidence", "analytical_consequence"):
        v = cmp_.get(k)
        w(f"- **{k}**: {', '.join(v) if isinstance(v, list) else v}")
    w("")
    c = categories[CHAIN["wave2_category_version"]]
    w(f"**Category {c['category_id']}, version {c['memo_id']}** supersedes {c['supersedes']}.")
    w("")
    w(f"- Reason recorded: {c.get('supersession_reason')}")
    w(f"- New definition: {c['definition']}")
    w(f"- Dimensions now: {'; '.join(c.get('dimensions', []))}")
    w(f"- Negative cases cited: {', '.join(c.get('negative_case_ids', []))}")
    ncr = c.get("negative_case_response", {})
    w(f"- Negative-case response: {ncr.get('action')} — {ncr.get('reason')} Discriminating evidence: {ncr.get('discriminating_evidence')}")
    w(f"- Comparisons cited: {', '.join(c.get('comparison_ids', []))}")
    w("")
    m = memos[CHAIN["wave2_memo"]]
    w(f"**{m['memo_id']}** ({m['memo_type']} memo) revises the pilot proposal:")
    w("")
    w("> " + m["body"])
    w("")

    # 5. Second request
    r = requests[CHAIN["second_request"]]
    w(f"## 5. The revised account asked its next question ({r['request_id']}, status {r['status']})")
    w("")
    w(f"Focus: {r['provisional_focus']}")
    w("")
    w(f"Discriminating question: {r['discriminating_question']}")
    w("")
    w(f"Focus records: {', '.join(r['focus_ids'])}. Counter-search: {r['counter_search']}")
    w("")

    # 6. Wave 3 selection and incidents
    s = sel3[CHAIN["wave3_selection_file"]]
    w("## 6. Third cycle (C003): the case that split 'acceptable' from 'authorized'")
    w("")
    w(f"Selection record for `{s['file']}` ({s['manifestation_id']}, SHA-256 `{s['sha256']}`), "
      f"stage {s['selection_stage']}, following {s['prior_request']}:")
    w("")
    w(f"- Gap: {s['gap']}")
    w(f"- Opposing expected observations: {s['opposing_expected_observations']}")
    w("")
    w("The interview was selected for a different reason (specialist reframing after repeated patches). "
      "The incident below was found while coding it in full; it was not the reason for selection.")
    w("")
    body = []
    for iid in CHAIN["wave3_incidents"]:
        i = incidents[iid]
        q = i.get("quote_ref", {}).get("quote_sha256", "")
        body.append([iid, i["epistemic_class"], locator(i["source_ref"]), i["description"],
                     i.get("evidence_limit", ""), q])
    w(md_table(["Incident", "Epistemic class", "Source and lines", "Description", "Evidence limit", "Quote SHA-256"], body))
    w("")
    body = []
    for iid in CHAIN["wave3_incidents"]:
        for cd in code_for(iid):
            body.append([cd["code_id"], iid, cd["label"], cd.get("alternative_reading", "")])
    w(md_table(["Code", "Incident", "Label", "Alternative reading"], body))
    w("")

    cmp_ = comparisons[CHAIN["wave3_comparison"]]
    w(f"### Comparison {cmp_['comparison_id']}")
    w("")
    for k in ("compared_ids", "relation", "purpose", "observation", "possible_condition",
              "rival_explanation", "discriminating_evidence", "analytical_consequence"):
        v = cmp_.get(k)
        w(f"- **{k}**: {', '.join(v) if isinstance(v, list) else v}")
    w("")
    c = categories[CHAIN["wave3_category_version"]]
    w(f"### Category {c['category_id']}, version {c['memo_id']} (supersedes {c['supersedes']})")
    w("")
    w(f"- Reason recorded: {c.get('supersession_reason')}")
    w(f"- New definition: {c['definition']}")
    w(f"- Dimensions now: {'; '.join(c.get('dimensions', []))}")
    w(f"- Not this: {c.get('not_this')}")
    w(f"- Negative cases cited: {', '.join(c.get('negative_case_ids', []))}")
    ncr = c.get("negative_case_response", {})
    w(f"- Negative-case response: {ncr.get('action')} — {ncr.get('reason')} Discriminating evidence: {ncr.get('discriminating_evidence')}")
    w("")

    # 7. Review and episode correction
    e0 = episode(CHAIN["episode_before"])
    e1 = episode(CHAIN["episode_after"])
    w("## 7. A reviewer who did not produce the rows caught an overbroad label")
    w("")
    w(f"Episode **{e0['episode_id']}** recorded outcome `{e0['outcome_status']}` with intended outcome: {e0['intended_outcome']}")
    w("")
    w(f"Episode **{e1['episode_id']}** supersedes {e1.get('supersedes')}: {e1.get('supersession_reason')}")
    w("")
    w(f"- Intended outcome now: {e1['intended_outcome']}")
    co = e1.get("component_outcomes", {})
    for k, v in co.items():
        w(f"- Component outcome, {k}: {v}")
    w("")
    w("The reviewer's finding (AUD-01) and the producers' disposition are in "
      "`example/input/study/audit/INDEPENDENT_REVIEW.md` and `DISPOSITIONS.md`. The review was by a "
      "separate, non-producing agent using the same model and environment, not blinded, and not a human review.")
    w("")

    # 8. Successor theoretical memo
    m = memos[CHAIN["wave3_memo"]]
    w(f"## 8. The account after two waves ({m['memo_id']}, supersedes {m.get('supersedes')})")
    w("")
    w("> " + m["body"])
    w("")

    # 9. Next request
    r = requests[CHAIN["third_request"]]
    w(f"## 9. What the study now asks for ({r['request_id']}, status {r['status']})")
    w("")
    w(f"Focus: {r['provisional_focus']}")
    w("")
    w(f"Discriminating question: {r['discriminating_question']}")
    w("")
    w(f"Expected if supported: {r['expected_observations']['supports']}")
    w("")
    w(f"Expected if challenged: {r['expected_observations']['challenges']}")
    w("")
    w(f"Restrictions: {'; '.join(r['restrictions'])}")
    w("")

    # 10. Plain language
    w("## 10. The analytical consequence in plain language")
    w("")
    w("The six-interview pilot proposed that people keep their agency over AI-mediated work through "
      "*revisable delegation*: hand work to the system, keep a place to review and correct it. The pilot's "
      "own sampling request asked for cases that would break this. The second cycle added an account of a "
      "support product that was patched repeatedly and then shut down; comparing it with the pilot's review "
      "practices (CMP015) showed that having a channel for correction says nothing about whether correction "
      "works, so the category was redefined to separate *the presence of review* from *the ability to make a "
      "consequential change* (MEM006), and the theoretical memo was revised (MEMO010). The third cycle added "
      "an account in which an agent sent an investor's email without the expected approval, and the sender, "
      "reading it afterwards, found it exactly right. Comparing that with accounts of review and of interfaces "
      "designed to feel controllable (CMP027) split the category again: an *acceptable result*, an *authorized "
      "procedure* and *effective redirection* are three different things that an interview can show "
      "separately (MEM010). A non-producing reviewer then objected that the episode's single label ACCEPTED "
      "hid the failed approval; the producers issued a successor episode (E714) that keeps both facts, without "
      "editing the original row. The current memo (MEMO014) therefore proposes *agency through consequential "
      "revision*, and the open request (REQ003) names the evidence the archive did not supply: an ordinary "
      "worker's disagreement followed through a known consequence.")
    w("")
    w("What this is not: not a validated theory, not saturation, not observed behavior (every incident is a "
      "speaker's own account), and not an independent human review. What it is: a chain in which each step "
      "is a row with an identity, a predecessor, a reason, and a locator a reader can check.")
    w("")

    # Sources used (identities and hashes only)
    w("## Source files bound in this chain")
    w("")
    body = []
    for mid in sorted({incidents[i]["source_ref"]["manifestation_id"] for i in CHAIN["wave2_incidents"] + CHAIN["wave3_incidents"]}):
        src = sources[mid]
        body.append([mid, Path(src["path"]).name, src["sha256"], src["rights"]])
    w(md_table(["Manifestation", "File", "SHA-256 of the transcript", "Rights as recorded"], body))
    w("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stdout", action="store_true", help="print instead of writing example/output/TRACE.md")
    args = ap.parse_args()
    text = build()
    if args.stdout:
        sys.stdout.write(text)
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(HERE.parent)} ({len(text.encode('utf-8'))} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
