#!/usr/bin/env python3
"""Validate this repo's JSONL card format, NOT source support or admission.

Dependency-free evaluator for the deliberately small JSON Schema vocabulary
used in schemas/measure-card.schema.json. Unknown keywords fail closed; this
is not a general-purpose Draft 2020-12 implementation.
"""
import argparse
import json
import re
from pathlib import Path

SCHEMA = Path(__file__).resolve().parents[1] / "schemas/measure-card.schema.json"
SUPPORTED = {"$schema", "$id", "$defs", "$ref", "title", "description", "type",
             "properties", "required", "additionalProperties", "enum", "const",
             "minLength", "minItems", "items", "pattern", "anyOf"}
ANNOTATIONS = {"$schema", "$id", "title", "description"}


def check_schema(node, root):
    extra = set(node) - SUPPORTED
    if extra:
        raise ValueError(f"unsupported schema keywords: {sorted(extra)}")
    for key in ("$defs", "properties"):
        for child in node.get(key, {}).values():
            check_schema(child, root)
    for child in node.get("anyOf", []):
        check_schema(child, root)
    if "items" in node:
        check_schema(node["items"], root)
    if "$ref" in node:
        resolve(node["$ref"], root)


def resolve(ref, root):
    if not ref.startswith("#/$defs/"):
        raise ValueError(f"unsupported reference: {ref}")
    return root["$defs"][ref[len("#/$defs/"):]]


def validate(value, schema, root, path="$"):
    if "$ref" in schema:
        validate(value, resolve(schema["$ref"], root), root, path)
    kind = schema.get("type")
    matches = {
        "object": isinstance(value, dict), "array": isinstance(value, list),
        "string": isinstance(value, str), "null": value is None,
        "boolean": isinstance(value, bool),
    }
    if kind and not matches.get(kind, False):
        raise ValueError(f"{path}: expected {kind}")
    if "const" in schema and value != schema["const"]:
        raise ValueError(f"{path}: expected {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{path}: value outside allowed enum")
    if "anyOf" in schema:
        for option in schema["anyOf"]:
            try:
                validate(value, option, root, path)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f"{path}: no permitted status/value/locator combination")
    if isinstance(value, dict):
        missing = set(schema.get("required", [])) - set(value)
        if missing:
            raise ValueError(f"{path}: missing {sorted(missing)}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False and set(value) - set(props):
            raise ValueError(f"{path}: unexpected fields {sorted(set(value) - set(props))}")
        for key, child in props.items():
            if key in value:
                validate(value[key], child, root, f"{path}.{key}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise ValueError(f"{path}: string too short")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            raise ValueError(f"{path}: invalid string pattern")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise ValueError(f"{path}: array too short")
        if "items" in schema:
            for index, item in enumerate(value):
                validate(item, schema["items"], root, f"{path}[{index}]")


def load_and_validate(paths, submission=False):
    schema = json.loads(SCHEMA.read_text())
    check_schema(schema, schema)
    seen = set()
    count = 0
    for path in paths:
        for lineno, line in enumerate(Path(path).read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                validate(record, schema, schema)
                if record["id"] in seen:
                    raise ValueError(f"duplicate record id: {record['id']}")
                if submission and record["teaching_example"]:
                    raise ValueError("teaching example cannot be submitted")
                seen.add(record["id"])
                count += 1
            except (ValueError, KeyError) as exc:
                raise ValueError(f"{path}:{lineno}: {exc}") from exc
    if not count:
        raise ValueError("no measure cards found")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--submission", action="store_true",
                        help="also reject teaching examples; does not admit evidence")
    args = parser.parse_args()
    try:
        count = load_and_validate(args.paths, args.submission)
    except ValueError as exc:
        parser.exit(1, f"INVALID: {exc}\n")
    print(f"STRUCTURE OK: {count} card(s); source support and rights require independent review.")


if __name__ == "__main__":
    main()
