"""Placeholder transcript merger that marks lineage as 'unprocessed'."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

from utils import iter_json_files, load_json, save_json

# Where the JSON files live (produced by earlier steps).
OUTPUT_DIR = Path(__file__).with_name("output") / "talks"

# Static lineage marker for now; swap out later when transcripts are merged.
LINEAGE_VALUE = ["unprocessed"]


def process_file(path: Path) -> Tuple[bool, str]:
    """Set dataLineage to the static LINEAGE_VALUE."""
    data = load_json(path)
    data["dataLineage"] = LINEAGE_VALUE
    save_json(path, data)
    return True, "updated"


def main() -> None:
    if not OUTPUT_DIR.exists():
        raise FileNotFoundError(f"Output directory not found: {OUTPUT_DIR}")

    updated = 0

    for json_path in iter_json_files(OUTPUT_DIR):
        ok, reason = process_file(json_path)
        if ok:
            updated += 1
        else:
            print(f"[skip] {json_path.name}: {reason}")

    print(f"Done. Updated {updated} file(s).")


if __name__ == "__main__":
    main()
