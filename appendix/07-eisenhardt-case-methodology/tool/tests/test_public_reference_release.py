import csv
import hashlib
import json
import re
import unicodedata
import unittest
from collections import Counter
from itertools import zip_longest
from pathlib import Path

from scripts.export_public_references import (
    PUBLIC_FIELDS,
    doi_url,
    public_author_names,
    safe_http_url,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT.parent / "data" / "r12"  # review snapshot: data sits beside tool/
EXPECTED_PUBLIC_FIELDS = (
    "source_release",
    "public_id",
    "evidence_tier",
    "screening_label",
    "title",
    "publication_year",
    "publication_date",
    "authors",
    "venue",
    "doi",
    "doi_url",
    "urn",
    "openalex_id",
    "landing_url",
    "landing_url_source",
)
EMAIL_ADDRESS = re.compile(
    r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}",
    re.IGNORECASE,
)
WEB_ADDRESS = re.compile(
    r"(?:[a-z][a-z0-9+.-]*://|www\.)",
    re.IGNORECASE,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def csv_to_typed(row: dict[str, str]) -> dict[str, object]:
    typed: dict[str, object] = dict(row)
    typed["authors"] = json.loads(row["authors"])
    typed["publication_year"] = int(row["publication_year"]) if row["publication_year"] else None
    for field in (
        "publication_date",
        "venue",
        "doi",
        "doi_url",
        "urn",
        "openalex_id",
        "landing_url",
    ):
        if typed[field] == "":
            typed[field] = None
    return typed


def normalized_sort_text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(normalized.split())


def public_row_sort_key(row: dict[str, object]) -> tuple[object, ...]:
    public_tiebreak = json.dumps(
        {
            field: row[field]
            for field in EXPECTED_PUBLIC_FIELDS
            if field != "public_id"
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (
        normalized_sort_text(row["title"]),
        row["publication_year"]
        if isinstance(row["publication_year"], int)
        else 9999,
        row["doi"] or "",
        normalized_sort_text(row["venue"]),
        tuple(normalized_sort_text(author) for author in row["authors"]),
        public_tiebreak,
    )


class PublicReferenceReleaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((DATA / "MANIFEST.json").read_text(encoding="utf-8"))

    def test_manifest_hashes(self) -> None:
        self.assertEqual(PUBLIC_FIELDS, EXPECTED_PUBLIC_FIELDS)
        self.assertEqual(self.manifest["schema_version"], "1.0")
        self.assertEqual(self.manifest["release"], "R12")
        self.assertEqual(
            tuple(self.manifest["projection"]["fields"]),
            EXPECTED_PUBLIC_FIELDS,
        )
        for name, record in self.manifest["files"].items():
            path = DATA / name
            self.assertEqual(path.stat().st_size, record["bytes"])
            self.assertEqual(sha256_file(path), record["sha256"])
        generator = ROOT / self.manifest["generator"]["path"]
        self.assertEqual(sha256_file(generator), self.manifest["generator"]["sha256"])

    def test_csv_and_jsonl_are_exact_twins(self) -> None:
        jsonl_path = DATA / "references.jsonl"
        csv_path = DATA / "references.csv"
        row_count = 0
        public_ids: set[str] = set()
        tier_counts: Counter[str] = Counter()
        screening_label_counts: Counter[str] = Counter()
        doi_values: list[str] = []
        previous_sort_key: tuple[object, ...] | None = None

        with jsonl_path.open(encoding="utf-8") as json_stream, csv_path.open(
            encoding="utf-8", newline=""
        ) as csv_stream:
            reader = csv.DictReader(csv_stream)
            self.assertEqual(tuple(reader.fieldnames or ()), EXPECTED_PUBLIC_FIELDS)
            missing = object()
            for json_line, csv_row in zip_longest(json_stream, reader, fillvalue=missing):
                self.assertIsNot(json_line, missing)
                self.assertIsNot(csv_row, missing)
                json_row = json.loads(json_line)
                self.assertEqual(tuple(json_row), EXPECTED_PUBLIC_FIELDS)
                self.assertEqual(json_row, csv_to_typed(csv_row))
                row_count += 1
                public_id = json_row["public_id"]
                self.assertEqual(public_id, f"ECS-R12-{row_count:06d}")
                self.assertNotIn(public_id, public_ids)
                public_ids.add(public_id)
                self.assertTrue(json_row["title"])
                observed_sort_key = public_row_sort_key(json_row)
                if previous_sort_key is not None:
                    self.assertLessEqual(previous_sort_key, observed_sort_key)
                previous_sort_key = observed_sort_key
                if json_row["landing_url_source"] == "unavailable":
                    self.assertIsNone(json_row["landing_url"])
                else:
                    self.assertIsNotNone(safe_http_url(json_row["landing_url"]))
                serialized = json.dumps(json_row, ensure_ascii=False).lower()
                self.assertNotIn("/users/", serialized)
                self.assertNotIn("file://", serialized)
                self.assertNotIn("casa_token", serialized)
                self.assertNotIn("x-amz", serialized)
                self.assertNotIn("password-login", serialized)
                tier_counts[json_row["evidence_tier"]] += 1
                screening_label_counts[json_row["screening_label"]] += 1
                if json_row["doi"]:
                    doi_values.append(json_row["doi"])
                    self.assertEqual(json_row["doi_url"], doi_url(json_row["doi"]))

        counts = self.manifest["counts"]
        self.assertEqual(row_count, counts["rows"])
        self.assertEqual(len(public_ids), counts["unique_public_ids"])
        self.assertEqual(dict(tier_counts), counts["evidence_tier_counts"])
        self.assertEqual(
            dict(screening_label_counts), counts["screening_label_counts"]
        )
        self.assertEqual(len(doi_values), counts["doi_rows"])
        self.assertEqual(len(set(doi_values)), counts["unique_dois"])

    def test_author_values_exclude_contact_routes(self) -> None:
        self.assertEqual(
            public_author_names(
                [
                    "Person Name",
                    "Department, person" + "@" + "example.edu",
                    "https://example.edu/profile",
                    "Mat Naim Abdullah@Asmoni",
                ]
            ),
            ["Person Name", "Mat Naim Abdullah@Asmoni"],
        )
        self.assertEqual(
            public_author_names(["person" + "@" + "example.edu", "www.example.edu"]),
            [],
        )
        with (DATA / "references.jsonl").open(encoding="utf-8") as stream:
            for row in map(json.loads, stream):
                for author in row["authors"]:
                    self.assertTrue(author, row["public_id"])
                    self.assertEqual(author, author.strip(), row["public_id"])
                    self.assertIsNone(EMAIL_ADDRESS.search(author), row["public_id"])
                    self.assertIsNone(WEB_ADDRESS.search(author), row["public_id"])

    def test_doi_list_matches_reference_release(self) -> None:
        with (DATA / "references.jsonl").open(encoding="utf-8") as stream:
            expected = sorted(
                {
                    row["doi"]
                    for row in map(json.loads, stream)
                    if row.get("doi")
                }
            )
        observed = (DATA / "dois.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
