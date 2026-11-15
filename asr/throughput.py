"""Measure GPU throughput of an ASR runner: N copies in parallel, each on 1/N of the clips.

    uv run python asr/throughput.py --label whisper-prod --procs 1 2 4 -- \\
        uv run python asr/run_whisper.py --model large-v3-turbo --context --batch-size 0 --kinds speech

For each N the runner is started N times with ASR_SHARD=k/N (asr/common.py splits the clip list) and
ASR_OUT pointing at data/logs/speed/<label>/<variant>-p<N>/shard<k>/, so transcripts stay out of data/outputs
(they are kept for checking that parallel runs transcribe the same). A runner that parallelises
internally (a batch size, concurrent requests) is measured with --procs 1 and a --variant name.

Results are merged into data/logs/speed/<label>.json, keyed by variant and N:
  wall_sec         launch to last exit, including model loading
  decode_sec       slowest process's transcription time (excludes loading)
  rtfx_decode      total audio / decode_sec (steady-state throughput, the number to plan with)
  rtfx_wall        total audio / wall_sec
  gpu_peak_mb      device memory in use at peak (all processes)
  gpu_util_avg     mean GPU utilisation while running (%)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SPEED = REPO / "data" / "logs" / "speed"


def smi(field):
    try:
        out = subprocess.run(["nvidia-smi", f"--query-gpu={field}", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=5).stdout.split()
        return out[0] if out else None
    except Exception:
        return None


class Sampler:
    def __init__(self):
        self.util, self.mem, self._stop = [], [], threading.Event()
        self._t = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        while not self._stop.is_set():
            u, m = smi("utilization.gpu"), smi("memory.used")
            if u and u.isdigit():
                self.util.append(int(u))
            if m and m.isdigit():
                self.mem.append(int(m))
            self._stop.wait(1.0)

    def __enter__(self):
        self._t.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._t.join()


def recount(label):
    """Fix results written before each process had its own output folder (2026-11-15 A10 run): the
    processes shared one _run.json, so totals came from one shard only. Clip files are all there, so
    audio is recounted from them; decode_sec (the last writer, i.e. the slowest shard) is kept."""
    path = SPEED / f"{label}.json"
    res = json.loads(path.read_text())
    for r in res["results"]:
        slug = "".join(ch if ch.isalnum() else "-" for ch in r["variant"]).strip("-")
        d = SPEED / label / f"{slug}-p{r['procs']}"
        if r["procs"] == 1 or list(d.glob("shard*/")) and not list(d.glob("*/_run.json")):
            continue
        files = [f for f in d.glob("*/*.json") if not f.name.startswith("_")]
        audio = sum(json.loads(f.read_text())["audio_sec"] for f in files)
        r.update(clips=len(files), audio_sec=round(audio, 1), rtfx_decode=round(audio / r["decode_sec"], 1),
                 rtfx_wall=round(audio / r["wall_sec"], 1), recounted=True)
        print(f"  {r['variant']} p{r['procs']}: {len(files)} clips, {r['rtfx_decode']}x", file=sys.stderr)
    path.write_text(json.dumps(res, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--label", required=True, help="results file name, e.g. whisper-prod")
    ap.add_argument("--recount", action="store_true", help="fix totals of an older multi-process result")
    ap.add_argument("--variant", default="procs", help="name of this configuration, e.g. 'batch 4'")
    ap.add_argument("--procs", type=int, nargs="+", default=[1])
    ap.add_argument("cmd", nargs=argparse.REMAINDER, help="runner command after --")
    args = ap.parse_args()
    if args.recount:
        return recount(args.label)
    cmd = args.cmd[1:] if args.cmd[:1] == ["--"] else args.cmd
    if not cmd:
        sys.exit("give the runner command after --")

    SPEED.mkdir(parents=True, exist_ok=True)
    res_path = SPEED / f"{args.label}.json"
    res = json.loads(res_path.read_text()) if res_path.exists() else {"label": args.label, "results": []}
    res.update(gpu=smi("name"), gpu_mem_mb=smi("memory.total"), command=" ".join(cmd))

    for n in args.procs:
        slug = "".join(ch if ch.isalnum() else "-" for ch in args.variant).strip("-")
        out = SPEED / args.label / f"{slug}-p{n}"
        if out.exists():
            subprocess.run(["rm", "-rf", str(out)], check=True)
        out.mkdir(parents=True)
        print(f"[{args.label}] {args.variant}, {n} process(es)", file=sys.stderr, flush=True)
        t = time.time()
        with Sampler() as smp:
            procs = []
            for k in range(n):
                env = dict(os.environ, ASR_SHARD=f"{k}/{n}", ASR_OUT=str(out / f"shard{k}"))
                logf = open(out / f"shard{k}.log", "w")
                procs.append((subprocess.Popen(cmd, env=env, stdout=logf, stderr=subprocess.STDOUT), logf))
            codes = []
            for p, logf in procs:
                codes.append(p.wait())
                logf.close()
        wall = time.time() - t
        runs = [json.loads(p.read_text()) for p in out.glob("shard*/*/_run.json")]  # one per process
        audio = sum(r["audio_sec"] for r in runs)
        decode = max((r["wall_sec"] for r in runs), default=0)
        row = {"variant": args.variant, "procs": n, "failed": sum(c != 0 for c in codes),
               "clips": sum(r["clips"] for r in runs), "audio_sec": round(audio, 1),
               "wall_sec": round(wall, 1), "decode_sec": round(decode, 1),
               "rtfx_decode": round(audio / decode, 1) if decode else None,
               "rtfx_wall": round(audio / wall, 1) if wall else None,
               "gpu_peak_mb": max(smp.mem, default=None),
               "gpu_util_avg": round(sum(smp.util) / len(smp.util)) if smp.util else None,
               "at": time.strftime("%Y-%m-%d %H:%M:%S")}
        res["results"] = [r for r in res["results"] if (r["variant"], r["procs"]) != (args.variant, n)] + [row]
        res_path.write_text(json.dumps(res, indent=2))
        print(f"  {row}", file=sys.stderr, flush=True)
        if row["failed"]:
            print(f"  {row['failed']} process(es) failed; see {out}/shard*.log", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
