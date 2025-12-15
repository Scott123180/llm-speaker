"""Rewrite JSON files into a compact, web-friendly form."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

from utils import iter_json_files, load_json, save_json_compact

# Directory containing the JSON files produced by earlier steps.
OUTPUT_DIR = Path(__file__).with_name("output") / "talks"


def process_file(path: Path) -> Tuple[bool, str]:
    """Load and rewrite the JSON without extra whitespace."""
    data = load_json(path)
    save_json_compact(path, data)
    return True, "minified"


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

    print(f"Done. Minified {updated} file(s).")


if __name__ == "__main__":
    main()
