"""Populate audio URLs in JSON files based on their id."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

from utils import iter_json_files, load_json, save_json


# Directory containing the JSON files produced by 01_csv_talk_mapper.py.
OUTPUT_DIR = Path(__file__).with_name("output") / "talks"

# Base URL template; `ref` will be populated from the `id` field in each JSON file.
AUDIO_URL_TEMPLATE = "https://media-archive.zmmapple.com/pages/download.php?direct=1&ref={ref}&ext=mp3"


def build_audio_url(ref: str) -> str:
    """Drop the id into the configured template."""
    return AUDIO_URL_TEMPLATE.format(ref=ref)


def process_file(path: Path) -> Tuple[bool, str]:
    """Update a single JSON file; returns (updated?, reason)."""
    data = load_json(path)
    talk_id = data.get("id")

    if not talk_id:
        return False, "missing id"

    data["audioUrl"] = build_audio_url(str(talk_id).strip())
    save_json(path, data)
    return True, "updated"


def main() -> None:
    if not OUTPUT_DIR.exists():
        raise FileNotFoundError(f"Output directory not found: {OUTPUT_DIR}")

    updated = 0
    skipped = 0

    for json_path in iter_json_files(OUTPUT_DIR):
        ok, reason = process_file(json_path)
        if ok:
            updated += 1
        else:
            skipped += 1
            print(f"[skip] {json_path.name}: {reason}")

    print(f"Done. Updated {updated} file(s). Skipped {skipped} file(s).")


if __name__ == "__main__":
    main()
