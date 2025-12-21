"""Build a lightweight index.json array for all talks."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from utils import iter_json_files, load_json, save_json

# Directory containing per-talk JSON files.
TALKS_DIR = Path(__file__).with_name("output") / "talks"
# Where the index will be written (one level up from talks).
INDEX_PATH = Path(__file__).with_name("output") / "talks-index.json"


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
