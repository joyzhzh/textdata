#!/usr/bin/env python3
"""Build the public, metadata-only R12 reference release.

The exporter is deliberately narrow. It reads the compact promoted reader
ledger, verifies its sealed identity, allowlists public fields, and selects
DOI, OpenAlex, or non-sensitive HTTPS URLs. It never edits the source workspace
and it refuses to write into a non-empty output directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit


RELEASE = "R12"
OBSERVED_THROUGH = "2026-08-26"
SOURCE_ARTIFACT = "EISENHARDT_CASE_STUDIES_READING_LEDGER.jsonl"
SOURCE_SHA256 = "5cee45c5e7bd5c3961a20d5b1707173c14838c3b27a379b70d4f02208ae0a1cf"
EXPECTED_ROWS = 22_856
EXPECTED_DOI_ROWS = 20_732
EXPECTED_TIER_COUNTS = {
    "canonical-metadata-qualified": 15_198,
    "provisional-high-recall": 7_658,
}
EXPECTED_CLASSIFICATION_COUNTS = {
    "confirmed-case-study": 12_300,
    "probable-case-study": 10_556,
}

PUBLIC_FIELDS = (
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

_SENSITIVE_QUERY_KEY = re.compile(
    r"(?:^|[_-])(?:token|api[_-]?key|access[_-]?key|signature|sig|auth|"
    r"session|password|secret|credential|jwt|ticket|expires?|x-amz|saml|code)"
    r"(?:$|[_-])",
    re.IGNORECASE,
)
_AUTH_PATH = re.compile(
    r"(?:^|[/_.-])(?:login|signin|password|saml|shibboleth|oauth|authorize)"
    r"(?:[/_.-]|$)",
    re.IGNORECASE,
)
_BLOCKED_HOST_PARTS = ("login.", "signin.", "auth.", "sso.")
_BLOCKED_HOSTS = {
    "orcid.org",
    "www.orcid.org",
    "paperzz.com",
    "www.paperzz.com",
}
_EMAIL_ADDRESS = re.compile(
    r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}",
    re.IGNORECASE,
)
_WEB_ADDRESS = re.compile(
    r"(?:[a-z][a-z0-9+.-]*://|www\.)",
    re.IGNORECASE,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_doi(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    doi = value.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.lower().startswith(prefix):
            doi = doi[len(prefix) :]
            break
    doi = doi.strip().lower()
    return doi or None


def doi_url(doi: str | None) -> str | None:
    if not doi:
        return None
    return "https://doi.org/" + quote(doi, safe="/():._-;")


def safe_http_url(value: object) -> str | None:
    """Return a non-sensitive public HTTPS URL or None."""

    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    lowered = raw.lower()
    if "/users/" in lowered or lowered.startswith(("file:", "data:")):
        return None
    try:
        parts = urlsplit(raw)
    except ValueError:
        return None
    if parts.scheme.lower() != "https" or not parts.hostname:
        return None
    hostname = parts.hostname.lower()
    if parts.username or parts.password:
        return None
    if any(part in hostname for part in _BLOCKED_HOST_PARTS):
        return None
    if hostname in _BLOCKED_HOSTS:
        return None
    if _AUTH_PATH.search(parts.path):
        return None
    if parts.query:
        for item in parts.query.split("&"):
            key = item.split("=", 1)[0]
            if _SENSITIVE_QUERY_KEY.search(key):
                return None
    return urlunsplit((parts.scheme.lower(), parts.netloc, parts.path, parts.query, ""))


def choose_landing_url(
    row: dict[str, object], doi: str | None
) -> tuple[str | None, str]:
    if doi:
        return doi_url(doi) or "", "doi"

    openalex_id = row.get("openalex_id")
    if isinstance(openalex_id, str) and re.fullmatch(r"W\d+", openalex_id.strip()):
        return f"https://openalex.org/{openalex_id.strip()}", "openalex"

    stable_landing = safe_http_url(row.get("stable_landing_url"))
    if stable_landing:
        return stable_landing, "stable-url"
    return None, "unavailable"


def public_id(row_number: int) -> str:
    return f"ECS-{RELEASE}-{row_number:06d}"


def normalized_sort_text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(normalized.split())


def public_author_names(value: object) -> list[str]:
    authors = [] if value is None else value
    if not isinstance(authors, list) or not all(isinstance(a, str) for a in authors):
        raise ValueError("authors must be a string array")
    return [
        name
        for author in authors
        if (name := author.strip())
        and not _EMAIL_ADDRESS.search(name)
        and not _WEB_ADDRESS.search(name)
    ]


def public_projection_values(row: dict[str, object]) -> dict[str, object]:
    title = row.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("row has no title")

    doi = normalize_doi(row.get("doi"))
    landing_url, landing_url_source = choose_landing_url(row, doi)
    return {
        "evidence_tier": row.get("evidence_tier"),
        "screening_label": row.get("classification"),
        "title": title.strip(),
        "publication_year": row.get("publication_year"),
        "publication_date": row.get("publication_date"),
        "authors": public_author_names(row.get("authors")),
        "venue": row.get("venue"),
        "doi": doi,
        "doi_url": doi_url(doi),
        "urn": row.get("urn"),
        "openalex_id": row.get("openalex_id"),
        "landing_url": landing_url,
        "landing_url_source": landing_url_source,
    }


def public_sort_key(row: dict[str, object]) -> tuple[object, ...]:
    values = public_projection_values(row)
    public_tiebreak = json.dumps(
        {"source_release": RELEASE, **values},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (
        normalized_sort_text(values["title"]),
        values["publication_year"]
        if isinstance(values["publication_year"], int)
        else 9999,
        values["doi"] or "",
        normalized_sort_text(values["venue"]),
        tuple(normalized_sort_text(author) for author in values["authors"]),
        public_tiebreak,
    )


def project_row(row: dict[str, object], row_number: int) -> dict[str, object]:
    result = {
        "source_release": RELEASE,
        "public_id": public_id(row_number),
        **public_projection_values(row),
    }
    if tuple(result) != PUBLIC_FIELDS:
        raise AssertionError("public field order drifted")
    return result


def csv_value(field: str, value: object) -> object:
    if value is None:
        return ""
    if field == "authors":
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def validate_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    if len(rows) != EXPECTED_ROWS:
        raise ValueError(f"expected {EXPECTED_ROWS} rows, observed {len(rows)}")
    ids = [str(row["public_id"]) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("public_id values are not unique")

    tier_counts = Counter(str(row["evidence_tier"]) for row in rows)
    screening_label_counts = Counter(str(row["screening_label"]) for row in rows)
    doi_rows = sum(bool(row["doi"]) for row in rows)
    if dict(tier_counts) != EXPECTED_TIER_COUNTS:
        raise ValueError(f"evidence-tier drift: {dict(tier_counts)!r}")
    if dict(screening_label_counts) != EXPECTED_CLASSIFICATION_COUNTS:
        raise ValueError(f"screening-label drift: {dict(screening_label_counts)!r}")
    if doi_rows != EXPECTED_DOI_ROWS:
        raise ValueError(f"DOI-row drift: expected {EXPECTED_DOI_ROWS}, observed {doi_rows}")
    for row in rows:
        url = row["landing_url"]
        source = row["landing_url_source"]
        if source == "unavailable":
            if url is not None:
                raise ValueError("unavailable landing source has a URL")
        elif not safe_http_url(url):
            raise ValueError("unsafe landing URL survived projection")

    dois = [str(row["doi"]) for row in rows if row["doi"]]
    return {
        "rows": len(rows),
        "unique_public_ids": len(set(ids)),
        "doi_rows": doi_rows,
        "unique_dois": len(set(dois)),
        "evidence_tier_counts": dict(tier_counts),
        "screening_label_counts": dict(screening_label_counts),
        "landing_url_source_counts": dict(
            Counter(str(row["landing_url_source"]) for row in rows)
        ),
    }


def load_and_project(source: Path) -> tuple[list[dict[str, object]], dict[str, object]]:
    observed_hash = sha256_file(source)
    if observed_hash != SOURCE_SHA256:
        raise ValueError(
            f"source hash mismatch: expected {SOURCE_SHA256}, observed {observed_hash}"
        )
    raw_rows: list[dict[str, object]] = []
    with source.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError("row must be a JSON object")
                raw_rows.append(row)
            except Exception as exc:
                raise ValueError(f"source line {line_number}: {exc}") from exc
    raw_rows.sort(key=public_sort_key)
    rows = [
        project_row(row, row_number)
        for row_number, row in enumerate(raw_rows, 1)
    ]
    return rows, validate_rows(rows)


def write_release(source: Path, output_dir: Path) -> None:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"refusing non-empty output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    rows, counts = load_and_project(source)

    jsonl_path = output_dir / "references.jsonl"
    csv_path = output_dir / "references.csv"
    dois_path = output_dir / "dois.txt"

    with jsonl_path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            stream.write("\n")

    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=PUBLIC_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(field, row[field]) for field in PUBLIC_FIELDS})

    unique_dois = sorted({str(row["doi"]) for row in rows if row["doi"]})
    with dois_path.open("w", encoding="utf-8", newline="\n") as stream:
        for value in unique_dois:
            stream.write(value + "\n")

    files = {}
    for path in (jsonl_path, csv_path, dois_path):
        files[path.name] = {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }

    generator = Path(__file__).resolve()
    manifest = {
        "schema_version": "1.0",
        "release": RELEASE,
        "observed_through": OBSERVED_THROUGH,
        "artifact_role": "Public metadata-only candidate-reference projection",
        "claim_boundary": (
            "High-coverage, effort-bounded evidence map; not a systematic census, "
            "exhaustive or comprehensive recall, proof of method adherence, or "
            "literal saturation."
        ),
        "source": {
            "artifact": SOURCE_ARTIFACT,
            "sha256": SOURCE_SHA256,
            "rows": EXPECTED_ROWS,
        },
        "projection": {
            "fields": list(PUBLIC_FIELDS),
            "excluded": [
                "abstracts and article text",
                "PDFs and provider payloads",
                "email addresses and web routes embedded in author strings",
                "search queries, logs, and screening implementation",
                "runtime authorizations and local paths",
                "internal campaign IDs and detailed review-status fields",
                "signed, authenticated, session-bearing, and transient URLs",
            ],
            "landing_url_policy": (
                "Prefer DOI, then OpenAlex, then a non-sensitive HTTPS stable "
                "public URL. Publish null when none is available; never publish "
                "raw reader fallbacks."
            ),
            "public_id_policy": (
                "Release-local sequential ECS-R12 identifier assigned after a "
                "deterministic bibliographic sort whose final tie-break is derived "
                "only from public fields; internal campaign IDs, mappings, and "
                "source order are not published."
            ),
        },
        "counts": counts,
        "generator": {
            "path": "scripts/export_public_references.py",
            "sha256": sha256_file(generator),
        },
        "files": files,
    }
    manifest_path = output_dir / "MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        write_release(args.source.resolve(), args.output_dir.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
