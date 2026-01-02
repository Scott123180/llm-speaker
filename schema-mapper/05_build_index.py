"""Build a lightweight index.json array for all talks."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from utils import LINEAGE_STAGES, iter_json_files, load_json, save_json

# Directory containing per-talk JSON files.
TALKS_DIR = Path(__file__).with_name("output") / "talks"
# Where the index will be written (one level up from talks).
INDEX_PATH = Path(__file__).with_name("output") / "talks-index.json"


def _lineage_stage_number(data_lineage: object) -> int:
    """Return a 1-based stage number, or 0 when unknown."""
    # `dataLineage` should be a non-empty list; otherwise treat as unknown.
    if not isinstance(data_lineage, list) or not data_lineage:
        return 0
    last_stage = data_lineage[-1]
    try:
        # Map last lineage stage to 1-based index in LINEAGE_STAGES.
        return LINEAGE_STAGES.index(last_stage) + 1
    except ValueError:
        # Unknown stage names collapse to 0.
        return 0


def build_index_entry(data: Dict) -> Dict:
    """Shape a single talk into the index-friendly structure."""
    return {
        "id": str(data.get("id", "")),
        "title": data.get("title", ""),
        "teacher": data.get("speaker", ""),
        "date": data.get("date", ""),
        "tags": data.get("tags", []) or [],
        "summary": data.get("summary", ""),
        "duration": data.get("duration", ""),
        "ts": _lineage_stage_number(data.get("dataLineage")), # transcript stage
    }


def main() -> None:
    if not TALKS_DIR.exists():
        raise FileNotFoundError(f"Talks directory not found: {TALKS_DIR}")

    entries: List[Dict] = []
    for path in iter_json_files(TALKS_DIR):
        data = load_json(path)
        entries.append(build_index_entry(data))

    # Sort by id for deterministic order.
    entries.sort(key=lambda item: item.get("id", ""))

    save_json(INDEX_PATH, entries)
    print(f"Wrote {len(entries)} entries to {INDEX_PATH}")


if __name__ == "__main__":
    main()
