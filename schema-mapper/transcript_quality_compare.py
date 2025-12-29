"""Compare transcript quality JSONL logs across model versions."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import statistics
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class Entry:
    talk_id: str
    status: Optional[str]
    likeness: Optional[float]
    selected_file: Optional[str]
    model_version: str
    source_path: Path


def iter_log_entries(path: Path) -> Iterable[Tuple[int, dict]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                yield line_number, json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number} in {path}") from exc


def parse_version_pairs(pairs: List[str]) -> Dict[Path, str]:
    version_map: Dict[Path, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid --version value '{pair}'. Use VERSION=PATH.")
        version, raw_path = pair.split("=", 1)
        version = version.strip()
        if not version:
            raise ValueError(f"Invalid --version value '{pair}'. Version cannot be empty.")
        path = Path(raw_path).expanduser()
        version_map[path.resolve()] = version
    return version_map


def coerce_likeness(value: object) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_entries(
    paths: List[Path],
    version_map: Dict[Path, str],
) -> Tuple[Dict[str, Dict[str, Entry]], List[str]]:
    entries_by_version: Dict[str, Dict[str, Entry]] = {}
    warnings: List[str] = []

    for path in paths:
        assigned_version = version_map.get(path.resolve())
        for line_number, payload in iter_log_entries(path):
            talk_id = payload.get("talk_id")
            if not talk_id:
                warnings.append(f"{path}:{line_number}: missing talk_id, skipping")
                continue
            model_version = assigned_version or payload.get("model_version") or "unknown"
            if assigned_version and payload.get("model_version") and payload.get("model_version") != assigned_version:
                warnings.append(
                    f"{path}:{line_number}: model_version '{payload.get('model_version')}'"
                    f" overridden by --version '{assigned_version}'"
                )
            entry = Entry(
                talk_id=str(talk_id),
                status=payload.get("status"),
                likeness=coerce_likeness(payload.get("likeness")),
                selected_file=payload.get("selected_file"),
                model_version=model_version,
                source_path=path,
            )
            version_entries = entries_by_version.setdefault(model_version, {})
            if entry.talk_id in version_entries:
                warnings.append(
                    f"{path}:{line_number}: duplicate talk_id '{entry.talk_id}' for version"
                    f" '{model_version}', overwriting prior entry"
                )
            version_entries[entry.talk_id] = entry

    return entries_by_version, warnings


def summarize_entries(entries: Dict[str, Entry]) -> dict:
    all_entries = list(entries.values())
    likeness_scores = [entry.likeness for entry in all_entries if entry.likeness is not None]
    statuses = [entry.status == "succeeded" for entry in all_entries]
    success_count = sum(1 for status in statuses if status)
    total = len(all_entries)
    summary = {
        "total": total,
        "successes": success_count,
        "success_rate": (success_count / total) if total else None,
        "likeness_count": len(likeness_scores),
        "average_likeness": statistics.fmean(likeness_scores) if likeness_scores else None,
        "median_likeness": statistics.median(likeness_scores) if likeness_scores else None,
    }
    return summary


def format_float(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value:.4f}"


def compare_versions(
    base_version: str,
    base_entries: Dict[str, Entry],
    other_version: str,
    other_entries: Dict[str, Entry],
    limit: int,
) -> str:
    common_ids = sorted(set(base_entries) & set(other_entries))
    deltas: List[Tuple[float, Entry, Entry]] = []
    missing_likeness = 0
    success_to_fail = 0
    fail_to_success = 0

    for talk_id in common_ids:
        base_entry = base_entries[talk_id]
        other_entry = other_entries[talk_id]
        if base_entry.likeness is None or other_entry.likeness is None:
            missing_likeness += 1
            continue
        delta = other_entry.likeness - base_entry.likeness
        deltas.append((delta, base_entry, other_entry))
        if base_entry.status == "succeeded" and other_entry.status != "succeeded":
            success_to_fail += 1
        if base_entry.status != "succeeded" and other_entry.status == "succeeded":
            fail_to_success += 1

    improvements = [item for item in deltas if item[0] > 0]
    regressions = [item for item in deltas if item[0] < 0]
    unchanged = len(deltas) - len(improvements) - len(regressions)

    avg_delta = statistics.fmean([item[0] for item in deltas]) if deltas else None
    median_delta = statistics.median([item[0] for item in deltas]) if deltas else None

    lines = [
        f"Comparison: {base_version} -> {other_version}",
        f"  Matched talks: {len(common_ids)}",
        f"  Compared talks (with likeness): {len(deltas)}",
        f"  Improved: {len(improvements)}  Regressed: {len(regressions)}  Unchanged: {unchanged}",
        f"  Success->Fail: {success_to_fail}  Fail->Success: {fail_to_success}",
        f"  Avg delta: {format_float(avg_delta)}  Median delta: {format_float(median_delta)}",
    ]

    if missing_likeness:
        lines.append(f"  Skipped (missing likeness): {missing_likeness}")

    def format_change(delta_item: Tuple[float, Entry, Entry]) -> str:
        delta, base_entry, other_entry = delta_item
        status_change = f"{base_entry.status} -> {other_entry.status}"
        return (
            f"    {base_entry.talk_id}: {base_entry.likeness:.4f} ->"
            f" {other_entry.likeness:.4f} (delta {delta:+.4f}) status {status_change}"
        )

    if regressions:
        lines.append(f"  Top regressions (limit {limit}):")
        for item in sorted(regressions, key=lambda x: x[0])[:limit]:
            lines.append(format_change(item))

    if improvements:
        lines.append(f"  Top improvements (limit {limit}):")
        for item in sorted(improvements, key=lambda x: x[0], reverse=True)[:limit]:
            lines.append(format_change(item))

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare transcript quality JSONL logs across model versions.",
    )
    parser.add_argument(
        "log_paths",
        nargs="*",
        type=Path,
        help="Path(s) to JSONL log files.",
    )
    parser.add_argument(
        "--version",
        action="append",
        default=[],
        metavar="VERSION=PATH",
        help="Override model_version for a given log path (repeatable).",
    )
    parser.add_argument(
        "--baseline",
        default=None,
        help="Baseline version to compare against (defaults to first seen).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Limit for top regressions/improvements per comparison.",
    )
    args = parser.parse_args()

    version_map = parse_version_pairs(args.version)
    log_paths = list(args.log_paths)
    for path in version_map:
        if path not in log_paths:
            log_paths.append(path)

    if not log_paths:
        raise SystemExit("Provide at least one log path.")

    entries_by_version, warnings = load_entries(log_paths, version_map)
    if not entries_by_version:
        raise SystemExit("No entries found in provided logs.")

    print("Version summaries:")
    for version in sorted(entries_by_version.keys()):
        summary = summarize_entries(entries_by_version[version])
        print(f"- {version}")
        print(f"  Entries: {summary['total']}")
        print(f"  Successes: {summary['successes']}")
        print(f"  Success rate: {format_float(summary['success_rate'])}")
        print(f"  Average likeness: {format_float(summary['average_likeness'])}")
        print(f"  Median likeness: {format_float(summary['median_likeness'])}")

    versions = sorted(entries_by_version.keys())
    if len(versions) > 1:
        baseline = args.baseline or versions[0]
        if baseline not in entries_by_version:
            raise SystemExit(f"Baseline version '{baseline}' not found in logs.")
        for other in versions:
            if other == baseline:
                continue
            print()
            print(
                compare_versions(
                    baseline,
                    entries_by_version[baseline],
                    other,
                    entries_by_version[other],
                    args.limit,
                )
            )

    if warnings:
        print()
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
