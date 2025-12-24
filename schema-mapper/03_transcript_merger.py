"""Merge transcripts into talk JSON files based on data lineage priority."""

from __future__ import annotations

from pathlib import Path
import json
import sys
import time
from typing import Iterable, Tuple

# A bit of effort to add a file in from another directory in a 
# project that's not using packages
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from llm.accuracy.likeness import likeness_ratio_from_files
# End ugly, hard effort. This is not the way to do things

from utils import iter_json_files, load_json, save_json

# Where the JSON files live (produced by earlier steps).
OUTPUT_DIR = Path(__file__).with_name("output") / "talks"

QUALITY_LOG_PATH = OUTPUT_DIR.parent / f"transcript_quality_local_v2_{int(time.time() * 1000)}.log"

# Stages in data lineage order (earlier -> later). Later stages take precedence.
LINEAGE_STAGES = [
    "audio_original",
    "transcript_raw",
    "transcript_structured",
]

# # local mapping
# STAGE_SOURCES = {
#     "transcript_raw": {
#         "directory": "/home/biosdaddy/Documents/talks/all",
#         "filename_templates": ["{id}.txt"],
#     },
#     "transcript_structured": {
#         "directory": "/home/biosdaddy/Documents/talks/local_output",
#         "filename_templates": ["{id}_cleaned.txt"],
#     },
# }
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
QUALITY_THRESHOLD = 0.9


def iter_stage_priority() -> Iterable[str]:
    """Yield stages from highest to lowest priority."""
    return reversed(LINEAGE_STAGES)


def build_lineage(selected_stage: str) -> list[str]:
    """Return lineage up to and including the selected stage."""
    if selected_stage not in LINEAGE_STAGES:
        return [selected_stage]
    idx = LINEAGE_STAGES.index(selected_stage) + 1
    return LINEAGE_STAGES[:idx]


def find_stage_path(talk_id: str, stage: str) -> Path | None:
    """Find a transcript file for the given talk ID at the requested stage."""
    source = STAGE_SOURCES.get(stage)
    if not source:
        return None
    directory = Path(source["directory"])
    for template in source["filename_templates"]:
        candidate = directory / template.format(id=talk_id)
        if candidate.is_file():
            return candidate
    return None


def find_transcript_path(talk_id: str) -> Tuple[Path | None, str | None]:
    """Find the highest-priority transcript file for the given talk ID."""
    structured_path = find_stage_path(talk_id, "transcript_structured")
    raw_path = find_stage_path(talk_id, "transcript_raw")

    if structured_path:
        if raw_path:
            score = likeness_ratio_from_files(raw_path, structured_path)
            passed = score >= QUALITY_THRESHOLD
            selected_path = structured_path if passed else raw_path
            selected_stage = "transcript_structured" if passed else "transcript_raw"
            status = "succeeded" if passed else "failed"
            QUALITY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            log_entry = {
                "talk_id": talk_id,
                "structured": structured_path.name,
                "status": status,
                "likeness": round(score, 4),
                "selected_stage": selected_stage,
                "selected_file": selected_path.name,
            }
            with QUALITY_LOG_PATH.open("a", encoding="utf-8") as log_file:
                log_file.write(json.dumps(log_entry) + "\n")
            if not passed:
                return raw_path, "transcript_raw"
        return structured_path, "transcript_structured"

    if raw_path:
        return raw_path, "transcript_raw"

    for stage in iter_stage_priority():
        if stage in ("transcript_raw", "transcript_structured"):
            continue
        candidate = find_stage_path(talk_id, stage)
        if candidate:
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
