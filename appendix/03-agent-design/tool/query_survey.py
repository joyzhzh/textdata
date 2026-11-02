#!/usr/bin/env python3
"""Browse the released systems survey. Output is one JSON object per matching row."""
import argparse
import csv
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "systems-survey" / "survey-index.csv"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", help="exact entry ID")
    parser.add_argument("--function", help="exact research function, ignoring case")
    parser.add_argument("--search", help="case-insensitive substring of the name or released summary")
    parser.add_argument("--limit", type=int, help="show only the first N matching rows")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")

    shown = 0
    with DATA.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if args.id and row["id"] != args.id:
                continue
            if args.search and args.search.casefold() not in (row["name"] + "\n" + row["summary"]).casefold():
                continue
            for field in ("functions", "disciplines", "field_gaps", "source_links"):
                row[field] = json.loads(row[field])
            if args.function and args.function.casefold() not in {f.casefold() for f in row["functions"]}:
                continue
            print(json.dumps(row, ensure_ascii=False))
            shown += 1
            if args.limit == shown:
                break
    return int(shown == 0)

if __name__ == "__main__":
    raise SystemExit(main())
