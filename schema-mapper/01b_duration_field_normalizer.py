"""Normalize duration values in generated JSON talk files."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

from utils import iter_json_files, load_json, save_json


OUTPUT_DIR = Path(__file__).with_name("output") / "talks"
APPROX_TOKEN = "(approx)"


def normalize_duration(value: object) -> Tuple[object, bool]:
    """Strip the approx marker and whitespace from duration strings."""
    if not isinstance(value, str):
        return value, False
    cleaned = value.replace(APPROX_TOKEN, "").strip()
    return cleaned, cleaned != value


def process_file(path: Path) -> Tuple[bool, str]:
    """Update the duration field if needed; returns (updated?, reason)."""
    data = load_json(path)
    duration = data.get("duration")
    cleaned, changed = normalize_duration(duration)
    if not changed:
        return False, "no change"
    data["duration"] = cleaned
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
            if reason != "no change":
                print(f"[skip] {json_path.name}: {reason}")

    print(f"Done. Updated {updated} file(s). Skipped {skipped} file(s).")


if __name__ == "__main__":
    main()
