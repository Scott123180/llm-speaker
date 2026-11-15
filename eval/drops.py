#!/usr/bin/env python3
"""Dropped stretches: reference words a system leaves out in runs of 4+ words, against the
silver references (data/silver). Isolated misses are ordinary errors; long runs mean the
voice detector or the decoder skipped real speech.

  uv run python eval/drops.py                       # every system
  uv run python eval/drops.py whisper-turbo+ctx ... # only these
"""
import json
import sys
from pathlib import Path

from rapidfuzz.distance import Levenshtein

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "eval"))
from silver import OUT_DIR as SILVER, OUTPUTS, hyp_tokens  # noqa: E402

RUN = 4


def drops(ref, hyp):
    """-> (ref words, words in dropped runs, number of runs)"""
    lost = runs = 0
    for op in Levenshtein.opcodes(ref, hyp):
        n = (op.src_end - op.src_start) - (op.dest_end - op.dest_start if op.tag == "replace" else 0)
        if op.tag in ("delete", "replace") and n >= RUN:
            lost += n
            runs += 1
    return len(ref), lost, runs


def main():
    refs = {p.stem: [t["n"] for t in json.loads(p.read_text())["tokens"] if t["n"] and not t.get("filler")]
            for p in SILVER.glob("*.json") if not p.stem.startswith("worklist")}
    systems = sys.argv[1:] or sorted(p.name for p in OUTPUTS.iterdir() if p.is_dir())
    print(f"{'system':34s} {'dropped':>8s} {'runs':>5s} {'clips':>6s} {'words/min':>9s}")
    for s in systems:
        N = L = R = C = 0
        sec = words = 0.0
        for cid, ref in refs.items():
            f = OUTPUTS / s / f"{cid}.json"
            if not f.exists():
                continue
            o = json.loads(f.read_text())
            dur = o.get("duration") or o.get("audio_sec") or 0
            hyp = [t["n"] for t in hyp_tokens(o, dur)]
            n, lost, runs = drops(ref, hyp)
            N, L, R, C = N + n, L + lost, R + runs, C + (runs > 0)
            sec, words = sec + dur, words + len(hyp)
        if N:
            wpm = f"{60 * words / sec:.0f}" if sec else "-"
            print(f"{s:34s} {100 * L / N:7.2f}% {R:5d} {C:6d} {wpm:>9s}")


if __name__ == "__main__":
    main()
