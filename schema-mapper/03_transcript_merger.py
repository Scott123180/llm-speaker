"""Merge transcripts into talk JSON files based on data lineage priority."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple

from utils import iter_json_files, load_json, save_json

# Where the JSON files live (produced by earlier steps).
OUTPUT_DIR = Path(__file__).with_name("output") / "talks"

# Base project directory so transcript folders can be configured relative to repo.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Stages in data lineage order (earlier -> later). Later stages take precedence.
LINEAGE_STAGES = [
    "audio_original",
    "transcript_raw",
    "transcript_structured",
]

# Map stages to folders and filename templates. Update as lineage expands.
STAGE_SOURCES = {
    "transcript_raw": {
        "directory": "/home/biosdaddy/Documents/talks/all",
        "filename_templates": ["{id}.txt"],
    },
    "transcript_structured": {
        "directory": "/home/biosdaddy/Documents/talks/output/output",
        "filename_templates": ["{id}_cleaned.txt"],
    },
}

# Fallback lineage marker when no transcript is found.
LINEAGE_UNPROCESSED = ["unprocessed"]


def iter_stage_priority() -> Iterable[str]:
    """Yield stages from highest to lowest priority."""
    return reversed(LINEAGE_STAGES)


def build_lineage(selected_stage: str) -> list[str]:
    """Return lineage up to and including the selected stage."""
    if selected_stage not in LINEAGE_STAGES:
        return [selected_stage]
    idx = LINEAGE_STAGES.index(selected_stage) + 1
    return LINEAGE_STAGES[:idx]


def find_transcript_path(talk_id: str) -> Tuple[Path | None, str | None]:
    """Find the highest-priority transcript file for the given talk ID."""
    for stage in iter_stage_priority():
        source = STAGE_SOURCES.get(stage)
        if not source:
            continue
        directory: Path = source["directory"]
        for template in source["filename_templates"]:
            candidate = directory / template.format(id=talk_id)
            if candidate.is_file():
                return candidate, stage
    return None, None


def process_file(path: Path) -> Tuple[bool, str]:
    """Merge the best available transcript into the talk JSON."""
    data = load_json(path)
    talk_id = str(data.get("id", "")).strip()
    if not talk_id:
        return False, "missing id"

    transcript_path, stage = find_transcript_path(talk_id)
    if not transcript_path or not stage:
        data["dataLineage"] = LINEAGE_UNPROCESSED
        save_json(path, data)
        return False, "no transcript found"

    transcript_text = transcript_path.read_text(encoding="utf-8").rstrip()
    data["transcript"] = transcript_text
    data["dataLineage"] = build_lineage(stage)
    save_json(path, data)
    return True, f"merged from {stage}"


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
