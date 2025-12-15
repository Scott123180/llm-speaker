"""Minify the generated talks index for web serving."""

from __future__ import annotations

from pathlib import Path

from utils import load_json, save_json_compact

# Paths for the index.
OUTPUT_DIR = Path(__file__).with_name("output")
INDEX_PATH = OUTPUT_DIR / "talks-index.json"


def main() -> None:
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"Index file not found: {INDEX_PATH}")

    data = load_json(INDEX_PATH)
    save_json_compact(INDEX_PATH, data)
    print(f"Minified index at {INDEX_PATH}")


if __name__ == "__main__":
    main()
