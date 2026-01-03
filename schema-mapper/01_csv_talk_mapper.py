"""Convert rows from a CSV export into one JSON file per resource ID."""

from __future__ import annotations

import csv
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple


RESOURCE_ID_FIELD = "Resource ID(s)"
TITLE_FIELD = "Title"
CSV_PATH = Path(__file__).with_name("metadata_export__20251214-20_59.csv")
# Where generated talk JSON files will live.
OUTPUT_DIR = Path(__file__).with_name("output") / "talks"
# Set to an int to cap how many rows are processed; leave as None to process all.
ROW_LIMIT: int | None = None
# Validation handling: "enforce" skips invalid rows,
# "log_only" logs the issues but still writes the output.
VALIDATION_MODE = "enforce"
FIELD_MAP: Dict[str, str] = {
    "Resource ID(s)": "id",
    "Resource type": "resourceType",
    "Status": "status",
    "Contributed by": "contributedBy",
    "Date": "date",
    "Audio Library Catalog ID": "catalogId",
    "Koan Case #": "koanCase",
    "Talk Location": "location",
    "Title": "title",
    "Caption or Other Speaker": "caption",
    "Extracted Text": "transcript",
    "Speaker": "speaker",
    "Koan Collection": "koanCollection",
    "Track": "track",
    "Genre": "genre",
    "Duration": "duration",
    "Training Quarter": "trainingQuarter",
}
# Any CSV headers listed here will be dropped from the output even if present in FIELD_MAP.
IGNORED_CSV_FIELDS = {
    "Resource type",
    "Status",
    "Contributed by",
    "Genre",
}


@dataclass(frozen=True)
class RequiredField:
    field: str
    label: str


REQUIRED_FIELDS = [
    RequiredField(field=RESOURCE_ID_FIELD, label="resource id"),
    RequiredField(field=TITLE_FIELD, label="title"),
]


def sanitize_for_filename(value: str) -> str:
    """Keep filenames filesystem-safe."""
    value = value.strip().replace(os.sep, "_")
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "missing-id"


def clean_row(row: Dict[str, str]) -> Dict[str, str]:
    """Trim whitespace around headers and values."""
    cleaned: Dict[str, str] = {}
    for key, value in row.items():
        key = key.strip() if isinstance(key, str) else key
        cleaned[key] = value.strip() if isinstance(value, str) else value
    return cleaned


def iter_rows(reader: Iterable[Dict[str, str]], limit: int | None) -> Iterable[Tuple[int, Dict[str, str]]]:
    """Yield rows with an index, respecting an optional limit."""
    for idx, raw_row in enumerate(reader, start=1):
        if limit is not None and idx > limit:
            break
        yield idx, clean_row(raw_row)


def find_missing_required_fields(row: Dict[str, str]) -> Tuple[RequiredField, ...]:
    """Return any required fields that are missing or blank."""
    missing = []
    for required in REQUIRED_FIELDS:
        value = row.get(required.field, "")
        if not str(value).strip():
            missing.append(required)
    return tuple(missing)


def validate_row(row: Dict[str, str], idx: int) -> Tuple[bool, Tuple[RequiredField, ...], str]:
    """Validate required fields and return whether the row should be processed."""
    missing_fields = find_missing_required_fields(row)
    resource_id = str(row.get(RESOURCE_ID_FIELD, "")).strip()

    if missing_fields:
        missing_labels = ", ".join(field.label for field in missing_fields)
        print(f"[invalid] Row {idx}: missing required field(s): {missing_labels}")
        if VALIDATION_MODE != "log_only":
            return False, missing_fields, resource_id

    if not resource_id and VALIDATION_MODE == "log_only":
        resource_id = f"missing-id-row-{idx}"

    return True, missing_fields, resource_id


def validate_headers(fieldnames: Iterable[str]) -> None:
    """Ensure required CSV headers exist."""
    missing_headers = [
        required.field for required in REQUIRED_FIELDS if required.field not in fieldnames
    ]
    if missing_headers:
        missing_list = ", ".join(missing_headers)
        raise ValueError(f"Required column(s) not found in CSV headers: {missing_list}")


def transform_row(row: Dict[str, str]) -> Dict[str, object]:
    """Rename CSV headers to JSON-friendly keys and add extra fields."""
    transformed: Dict[str, object] = {}
    for csv_key, json_key in FIELD_MAP.items():
        if csv_key in IGNORED_CSV_FIELDS:
            continue
        value = row.get(csv_key, "")
        transformed[json_key] = value

    # Additional fields expected by downstream consumers.
    transformed["audioUrl"] = ""
    transformed["summary"] = ""
    transformed["dataLineage"] = []
    transformed["tags"] = []

    return transformed


def main() -> None:
    csv_path = CSV_PATH
    output_dir: Path = OUTPUT_DIR

    # Validate inputs before doing any work.
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Ensure the output directory exists so files can be written.
    output_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    missing_required = 0
    removed_missing_title = 0

    # Read the CSV once and stream rows into individual JSON files.
    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)

        if not reader.fieldnames:
            raise ValueError("CSV file contains no headers.")
        validate_headers(reader.fieldnames)

        for idx, row in iter_rows(reader, ROW_LIMIT):
            should_process, missing_fields, resource_id = validate_row(row, idx)
            if missing_fields:
                missing_required += 1
                if VALIDATION_MODE != "log_only" and any(
                    field.field == TITLE_FIELD for field in missing_fields
                ):
                    removed_missing_title += 1
            if not should_process:
                skipped += 1
                continue

            # Use the resource ID as the filename after making it filesystem-safe.
            safe_name = sanitize_for_filename(resource_id)
            output_path = output_dir / f"{safe_name}.json"

            transformed = transform_row(row)

            with output_path.open("w", encoding="utf-8") as json_file:
                # Persist the row as pretty-printed JSON for readability, sorted alphabetically by key.
                json.dump(transformed, json_file, ensure_ascii=False, indent=2, sort_keys=True)
                json_file.write("\n")

            written += 1

    print(
        "Done. Wrote {written} file(s) to {output_dir}. "
        "Skipped {skipped} row(s). "
        "Invalid rows {missing_required}. "
        "Removed {removed_missing_title} file(s) due to missing title.".format(
            written=written,
            output_dir=output_dir,
            skipped=skipped,
            missing_required=missing_required,
            removed_missing_title=removed_missing_title,
        )
    )


if __name__ == "__main__":
    main()
