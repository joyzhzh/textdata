#!/usr/bin/env python3
"""Validate the Phase A structure of a grounded-theory analysis cycle (schema 0.2-phase-a).

Row shapes are defined once, in ``schemas/*.schema.json``, and applied here
with ``jsonschema``. This script adds only the cross-file rules a per-row
schema cannot express: identity uniqueness, referential integrity, ordinal
uniqueness, manifestation containment, and supersession lifecycle.

Exit codes: 0 = PASS, 1 = FAIL, 2 = usage or missing dependency.
A PASS establishes structure only, never source truth, coding fidelity,
category quality, groundedness, sufficiency, saturation, admission, or release.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError:  # pragma: no cover - exercised only on hosts without the dependency
    jsonschema = None


SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"

# (packet file, schema name, identity field)
PACKET_FILES = (
    ("MANIFEST.json", "manifest", None),
    ("EPISODES.jsonl", "episode", "episode_id"),
    ("INCIDENTS.jsonl", "incident", "incident_id"),
    ("CODES.jsonl", "code", "code_id"),
    ("COMPARISONS.jsonl", "comparison", "comparison_id"),
    ("CATEGORY_MEMOS.jsonl", "category-memo", "memo_id"),
    ("MEMOS.jsonl", "memo", "memo_id"),
    ("SAMPLING_REQUESTS.jsonl", "sampling-request", "request_id"),
)

Row = dict[str, Any]


class PacketError(ValueError):
    """A deterministic packet-contract failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PacketError(message)


def load_schema(name: str) -> Any:
    require(jsonschema is not None, "jsonschema is required; choose an interpreter with the existing validator dependency")
    path = SCHEMA_DIR / f"{name}.schema.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def schema_errors(validator: Any, row: Row) -> list[str]:
    errors = sorted(validator.iter_errors(row), key=lambda e: list(e.path))
    messages = []
    for error in errors:
        location = "/".join(str(p) for p in error.path) or "<row>"
        messages.append(f"{location}: {error.message}")
    return messages


def read_json(path: Path) -> Row:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PacketError(f"{path.name}: cannot read valid JSON: {exc}") from exc
    require(isinstance(value, dict), f"{path.name}: root must be an object")
    return value


def read_jsonl(path: Path) -> list[Row]:
    rows: list[Row] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise PacketError(f"{path.name}: cannot read: {exc}") from exc
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise PacketError(f"{path.name}:{number}: invalid JSON: {exc}") from exc
        require(isinstance(row, dict), f"{path.name}:{number}: row must be an object")
        row["__line__"] = number
        rows.append(row)
    return rows


def where(filename: str, row: Row) -> str:
    return f"{filename}:{row.get('__line__', '?')}"


def apply_schema(filename: str, validator: Any, rows: list[Row]) -> None:
    for row in rows:
        clean = {k: v for k, v in row.items() if k != "__line__"}
        errors = schema_errors(validator, clean)
        if errors:
            raise PacketError(f"{where(filename, row)}: {errors[0]}")


def unique_ids(filename: str, rows: list[Row], field: str) -> dict[str, Row]:
    by_id: dict[str, Row] = {}
    for row in rows:
        identifier = row[field]
        require(identifier not in by_id, f"{where(filename, row)}: duplicate {field} {identifier}")
        by_id[identifier] = row
    return by_id


def current_rows(rows: list[Row], field: str) -> list[Row]:
    """Successors determine current state without editing historical status fields."""
    replaced = {r.get("supersedes") for r in rows}
    return [r for r in rows if r[field] not in replaced and r.get("status") not in {"RETIRED", "SUPERSEDED"}]


def check_lifecycle(filename: str, rows: list[Row], field: str) -> None:
    seen: set[str] = set()
    replaced: set[str] = set()
    for row in rows:
        target = row.get("supersedes")
        if target is not None:
            require(target in seen, f"{where(filename, row)}: supersedes must name an earlier row in this packet")
            require(target not in replaced, f"{where(filename, row)}: predecessor already has a successor")
            require(bool(row.get("supersession_reason", "").strip()), f"{where(filename, row)}: supersession_reason required")
            replaced.add(target)
        seen.add(row[field])
    for row in rows:
        if row.get("status") == "SUPERSEDED":
            require(row[field] in replaced, f"{where(filename, row)}: SUPERSEDED row has no successor in the packet")


def validate_packet(root: Path, additions: dict[str, list[Row]] | None = None) -> None:
    require(root.is_dir(), f"packet root is not a directory: {root}")
    for filename, _, _ in PACKET_FILES:
        require((root / filename).is_file(), f"missing required file: {filename}")

    validators = {name: load_schema(name) for _, name, _ in PACKET_FILES}

    manifest = read_json(root / "MANIFEST.json")
    errors = schema_errors(validators["manifest"], manifest)
    if errors:
        if errors[0].startswith("saturation_status"):
            raise PacketError(f"MANIFEST.json: saturation_status cannot declare saturation ({errors[0]})")
        raise PacketError(f"MANIFEST.json: {errors[0]}")
    require(
        manifest["producer_seat"] != manifest["reviewer_seat"],
        "MANIFEST.json: reviewer_seat must differ from producer_seat; the producing seat cannot review its own cycle",
    )

    def rows(filename: str) -> list[Row]:
        existing = read_jsonl(root / filename)
        return existing + (additions or {}).get(filename, [])

    episodes = rows("EPISODES.jsonl")
    incidents = rows("INCIDENTS.jsonl")
    codes = rows("CODES.jsonl")
    comparisons = rows("COMPARISONS.jsonl")
    category_memos = rows("CATEGORY_MEMOS.jsonl")
    memos = rows("MEMOS.jsonl")
    sampling = rows("SAMPLING_REQUESTS.jsonl")

    apply_schema("EPISODES.jsonl", validators["episode"], episodes)
    apply_schema("INCIDENTS.jsonl", validators["incident"], incidents)
    apply_schema("CODES.jsonl", validators["code"], codes)
    apply_schema("COMPARISONS.jsonl", validators["comparison"], comparisons)
    apply_schema("CATEGORY_MEMOS.jsonl", validators["category-memo"], category_memos)
    apply_schema("MEMOS.jsonl", validators["memo"], memos)
    apply_schema("SAMPLING_REQUESTS.jsonl", validators["sampling-request"], sampling)

    episodes_by_id = unique_ids("EPISODES.jsonl", episodes, "episode_id")
    incidents_by_id = unique_ids("INCIDENTS.jsonl", incidents, "incident_id")
    codes_by_id = unique_ids("CODES.jsonl", codes, "code_id")
    comparisons_by_id = unique_ids("COMPARISONS.jsonl", comparisons, "comparison_id")
    category_memos_by_id = unique_ids("CATEGORY_MEMOS.jsonl", category_memos, "memo_id")
    memos_by_id = unique_ids("MEMOS.jsonl", memos, "memo_id")
    requests_by_id = unique_ids("SAMPLING_REQUESTS.jsonl", sampling, "request_id")
    category_ids = {row["category_id"] for row in category_memos}

    basis_ids = set(incidents_by_id) | set(codes_by_id)
    check_lifecycle("EPISODES.jsonl", episodes, "episode_id")
    check_lifecycle("INCIDENTS.jsonl", incidents, "incident_id")
    active_incidents = {r["incident_id"] for r in current_rows(incidents, "incident_id")}
    ordinals: dict[str, set[int]] = {}
    for row in incidents:
        loc = where("INCIDENTS.jsonl", row)
        episode = episodes_by_id.get(row["episode_id"])
        require(episode is not None, f"{loc}: unknown episode_id {row['episode_id']}")
        seen = ordinals.setdefault(row["episode_id"], set())
        require(row["incident_id"] not in active_incidents or row["ordinal"] not in seen, f"{loc}: duplicate ordinal {row['ordinal']} within episode {row['episode_id']}")
        if row["incident_id"] in active_incidents:
            seen.add(row["ordinal"])
        source_ref = row.get("source_ref")
        if source_ref is not None:
            require(
                source_ref["manifestation_id"] in episode["source_refs"],
                f"{loc}: source_ref manifestation {source_ref['manifestation_id']} is not among episode {row['episode_id']} source_refs",
            )
        quote_ref = row.get("quote_ref")
        if quote_ref is not None:
            require(source_ref is not None, f"{loc}: quote_ref requires source_ref")
            require(
                quote_ref["manifestation_id"] == source_ref["manifestation_id"],
                f"{loc}: quote_ref manifestation {quote_ref['manifestation_id']} differs from source_ref manifestation",
            )
        for field in ("inference_basis_ids", "construct_basis_ids"):
            for basis in row.get(field, []):
                require(basis != row["incident_id"], f"{loc}: {field} cannot cite the incident itself")
                require(basis in basis_ids, f"{loc}: {field} cites unknown incident or code {basis}")

    for row in codes:
        loc = where("CODES.jsonl", row)
        for incident_id in row["incident_ids"]:
            require(incident_id in incidents_by_id, f"{loc}: unknown incident_id {incident_id}")
    check_lifecycle("CODES.jsonl", codes, "code_id")

    comparable_ids = set(incidents_by_id) | set(episodes_by_id) | set(codes_by_id) | category_ids
    for row in comparisons:
        loc = where("COMPARISONS.jsonl", row)
        for compared in row["compared_ids"]:
            require(compared in comparable_ids, f"{loc}: compared_ids cites unknown incident, episode, code, or category {compared}")
    check_lifecycle("COMPARISONS.jsonl", comparisons, "comparison_id")

    case_ids = set(incidents_by_id) | set(episodes_by_id)
    for row in category_memos:
        loc = where("CATEGORY_MEMOS.jsonl", row)
        for code_id in row["supporting_code_ids"]:
            require(code_id in codes_by_id, f"{loc}: unknown supporting code {code_id}")
        for comparison_id in row["comparison_ids"]:
            require(comparison_id in comparisons_by_id, f"{loc}: comparison_ids cites unknown comparison {comparison_id}")
        for case_id in row["negative_case_ids"]:
            require(case_id in case_ids, f"{loc}: negative_case_ids cites unknown incident or episode {case_id}")
    check_lifecycle("CATEGORY_MEMOS.jsonl", category_memos, "memo_id")

    for row in sampling:
        loc = where("SAMPLING_REQUESTS.jsonl", row)
        for focus in row.get("focus_ids", []):
            require(focus in category_ids or focus in comparisons_by_id, f"{loc}: focus_ids cites unknown category or comparison {focus}")

    referable_ids = comparable_ids | set(comparisons_by_id) | set(category_memos_by_id) | set(requests_by_id)
    for row in memos:
        loc = where("MEMOS.jsonl", row)
        for ref in row["refs"]:
            require(ref in referable_ids, f"{loc}: refs cites unknown identity {ref}")
    check_lifecycle("MEMOS.jsonl", memos, "memo_id")
    if manifest.get("workflow_profile") == "source-bound-v1":
        from source_bound import validate_bound_cycle
        try:
            validate_bound_cycle(root, manifest, {
                "EPISODES.jsonl": episodes, "INCIDENTS.jsonl": incidents,
                "CODES.jsonl": codes, "COMPARISONS.jsonl": comparisons,
                "CATEGORY_MEMOS.jsonl": category_memos, "MEMOS.jsonl": memos,
                "SAMPLING_REQUESTS.jsonl": sampling,
            })
        except (ValueError, OSError) as exc:
            raise PacketError(str(exc)) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("packet", type=Path, help="cycle packet directory")
    args = parser.parse_args()
    if jsonschema is None:
        print("FAIL_ANALYSIS_PACKET: the jsonschema package is required (python3 -m pip install jsonschema)", file=sys.stderr)
        return 2
    try:
        validate_packet(args.packet.resolve())
    except PacketError as exc:
        print(f"FAIL_ANALYSIS_PACKET: {exc}", file=sys.stderr)
        return 1
    print("PASS_ANALYSIS_PACKET_STRUCTURE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
