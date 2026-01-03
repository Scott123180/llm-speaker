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

from utils import LINEAGE_STAGES, iter_json_files, load_json, save_json

# Where the JSON files live (produced by earlier steps).
OUTPUT_DIR = Path(__file__).with_name("output") / "talks"

MODEL_VERSION = "v3"
QUALITY_LOG_PATH = OUTPUT_DIR.parent / f"transcript_quality_local_{MODEL_VERSION}_{int(time.time() * 1000)}.log"

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
    # "transcript_cleaned": {
    #     "directory": "/home/biosdaddy/Documents/talks/local_output_v3",
    #     "filename_templates": ["{id}_cleaned.txt"],
    # },
    "transcript_structured": {
        "directory": "/home/biosdaddy/Documents/talks/local_output_v3",
        "filename_templates": ["{id}_cleaned.txt"],
    },
}

# Fallback lineage marker when no transcript is found.
LINEAGE_UNPROCESSED = ["audio_original"]
QUALITY_THRESHOLD = 0.9


def iter_stage_priority() -> Iterable[str]:
    """Yield stages from highest to lowest priority."""
    return reversed(LINEAGE_STAGES)


def build_lineage(
    selected_stage: str, structured_likeness: float | None = None
) -> list[object]:
    """Return lineage up to and including the selected stage."""
    if selected_stage not in LINEAGE_STAGES:
        return [selected_stage]
    idx = LINEAGE_STAGES.index(selected_stage) + 1
    lineage: list[object] = []
    for stage in LINEAGE_STAGES[:idx]:
        if stage == "transcript_structured" and structured_likeness is not None:
            lineage.append(
                {
                    "stage": stage,
                    "likeness": round(structured_likeness, 4),
                }
            )
        else:
            lineage.append(stage)
    return lineage


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


def _log_quality(
    talk_id: str,
    candidate_path: Path,
    candidate_stage: str,
    selected_path: Path,
    selected_stage: str,
    score: float,
    passed: bool,
) -> None:
    """Record lineage quality checks for LLM-produced transcripts."""
    status = "succeeded" if passed else "failed"
    QUALITY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    log_entry = {
        "talk_id": talk_id,
        "candidate_stage": candidate_stage,
        "candidate_file": candidate_path.name,
        "status": status,
        "likeness": round(score, 4),
        "selected_stage": selected_stage,
        "selected_file": selected_path.name,
        "model_version": MODEL_VERSION,
    }
    with QUALITY_LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")


def _evaluate_candidate(
    talk_id: str,
    raw_path: Path | None,
    candidate_path: Path | None,
    candidate_stage: str,
) -> Tuple[Path | None, str | None, float | None]:
    """Return candidate when it passes quality checks, otherwise None."""
    if not candidate_path:
        return None, None, None
    if not raw_path:
        return candidate_path, candidate_stage, None

    score = likeness_ratio_from_files(raw_path, candidate_path)
    passed = score >= QUALITY_THRESHOLD
    selected_path = candidate_path if passed else raw_path
    selected_stage = candidate_stage if passed else "transcript_raw"
    _log_quality(
        talk_id=talk_id,
        candidate_path=candidate_path,
        candidate_stage=candidate_stage,
        selected_path=selected_path,
        selected_stage=selected_stage,
        score=score,
        passed=passed,
    )
    if passed:
        return candidate_path, candidate_stage, score
    return None, None, score


def find_transcript_path(
    talk_id: str,
) -> Tuple[Path | None, str | None, float | None]:
    """Find the highest-priority transcript file for the given talk ID."""
    raw_path = find_stage_path(talk_id, "transcript_raw")
    for candidate_stage in ("transcript_structured", "transcript_cleaned"):
        candidate_path = find_stage_path(talk_id, candidate_stage)
        selected_path, selected_stage, score = _evaluate_candidate(
            talk_id, raw_path, candidate_path, candidate_stage
        )
        if selected_path and selected_stage:
            return selected_path, selected_stage, score

    if raw_path:
        return raw_path, "transcript_raw", None

    for stage in iter_stage_priority():
        if stage in ("transcript_raw", "transcript_cleaned", "transcript_structured"):
            continue
        candidate = find_stage_path(talk_id, stage)
        if candidate:
            return candidate, stage, None
    return None, None, None


def process_file(path: Path) -> Tuple[bool, str]:
    """Merge the best available transcript into the talk JSON."""
    data = load_json(path)
    talk_id = str(data.get("id", "")).strip()
    if not talk_id:
        return False, "missing id"

    transcript_path, stage, structured_likeness = find_transcript_path(talk_id)
    if not transcript_path or not stage:
        data["dataLineage"] = LINEAGE_UNPROCESSED
        save_json(path, data)
        return False, "no transcript found"

    transcript_text = transcript_path.read_text(encoding="utf-8").rstrip()
    data["transcript"] = transcript_text
    data["dataLineage"] = build_lineage(
        stage,
        structured_likeness=structured_likeness
        if stage == "transcript_structured"
        else None,
    )
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
