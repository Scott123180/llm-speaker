"""Shared helpers for JSON file IO across mapping scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterator

LINEAGE_STAGES = [
    "audio_original",
    "transcript_raw",
    "transcript_structured",
    "transcript_cleaned",
]


def iter_json_files(directory: Path) -> Iterator[Path]:
    """Yield JSON files in a deterministic order."""
    for path in sorted(directory.glob("*.json")):
        if path.is_file():
            yield path


def load_json(path: Path) -> Dict:
    """Read a JSON file into a dict."""
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Dict) -> None:
    """Write a JSON file with stable formatting."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def save_json_compact(path: Path, data: Dict) -> None:
    """Write a JSON file without unnecessary whitespace (good for web serving)."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
