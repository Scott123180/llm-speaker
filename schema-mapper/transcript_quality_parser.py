"""Parse transcript quality JSONL logs and report summary stats.

Example run of the program:

input:
python3 transcript_quality_parser.py \
    output/transcript_quality_local_v2_1766579118957.log

output:
Entries: 56
Successes: 19
Success rate: 0.3393
Average likeness: 0.7843
Median likeness: 0.8117

---
alternate input - add the threshold param
python3 transcript_quality_parser.py \
  output/transcript_quality_local_v2_1766579118957.log \
  --threshold 0.95

Entries: 56
Successes: 11
Success rate: 0.1964
Average likeness: 0.7843
Median likeness: 0.8117

"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
from typing import Iterable, List


def iter_log_entries(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                yield json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}") from exc


def compute_statuses(likeness_scores: List[float], threshold: float) -> List[bool]:
    return [score >= threshold for score in likeness_scores]


def summarize_scores(scores: List[float]) -> dict:
    if not scores:
        return {
            "count": 0,
            "average": None,
            "median": None,
        }
    return {
        "count": len(scores),
        "average": statistics.fmean(scores),
        "median": statistics.median(scores),
    }


def compute_distribution(scores: List[float]) -> List[int]:
    bins = [0 for _ in range(11)]
    for score in scores:
        percent = int(score * 100)
        if percent < 0:
            percent = 0
        elif percent > 100:
            percent = 100
        if percent == 100:
            bins[10] += 1
        else:
            bins[percent // 10] += 1
    return bins


def render_distribution(bins: List[int]) -> None:
    if not bins:
        return
    max_count = max(bins)
    scale = 40
    print("\nQuality distribution (files per accuracy range):")
    for index, count in enumerate(bins):
        if index < 10:
            label = f"{index * 10:02d}-{index * 10 + 9:02d}%"
        else:
            label = "100%"
        bar_length = int(round((count / max_count) * scale)) if max_count else 0
        bar = "#" * bar_length
        print(f"{label} | {bar} ({count})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize transcript quality JSONL logs.",
    )
    parser.add_argument("log_path", type=Path, help="Path to JSONL log file")
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Recalculate success/failure using this likeness threshold.",
    )
    args = parser.parse_args()

    entries = list(iter_log_entries(args.log_path))
    likeness_scores = [float(entry["likeness"]) for entry in entries if "likeness" in entry]

    if args.threshold is not None:
        statuses = compute_statuses(likeness_scores, args.threshold)
    else:
        statuses = [entry.get("status") == "succeeded" for entry in entries]

    summary = summarize_scores(likeness_scores)
    success_count = sum(1 for status in statuses if status)
    total = summary["count"]
    success_rate = (success_count / total) if total else None

    print(f"Entries: {total}")
    print(f"Successes: {success_count}")
    if success_rate is None:
        print("Success rate: N/A")
    else:
        print(f"Success rate: {success_rate:.4f}")
    if summary["average"] is None:
        print("Average likeness: N/A")
        print("Median likeness: N/A")
    else:
        print(f"Average likeness: {summary['average']:.4f}")
        print(f"Median likeness: {summary['median']:.4f}")
    if likeness_scores:
        render_distribution(compute_distribution(likeness_scores))


if __name__ == "__main__":
    main()
