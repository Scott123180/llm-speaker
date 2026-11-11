#!/usr/bin/env python3
"""Nemotron-3.5-Transcribe via NVIDIA NeMo-Speech.cpp (GGUF), with optional context terms.

  uv run python asr/run_nemotron_cpp.py --bin data/src/NeMo-Speech.cpp/build/cuda-asr/bin/nemo-speech
  uv run python asr/run_nemotron_cpp.py --terms --salm max_sequences=4 --salm mtp_draft=0

Starts `nemo-speech serve` once (the model loads once), then sends each clip to the
OpenAI-style /v1/chat/completions endpoint with an instruction. Works the same with a
CPU or CUDA build of NeMo-Speech.cpp; pick the SALM memory settings for the GPU with
--salm (docs/salm/configuration.md: 24 GB GPU = max_sequences 4, mtp_draft 0, ...).

Instructions follow the NeMo-Speech.cpp docs ("Names and terms spelled right"):
  plain:  "Transcribe with punctuation and capitalization."
  terms:  "Transcribe with punctuation and capitalization. Context terms: A, B, C."
The model card's training template is available with --template nvidia.
Stdlib + numpy only (runs in the main env).
"""
import argparse
import base64
import glob
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (DATA, GpuMemoryMonitor, Run, clip_audio_path, hard_terms, load_manifest,  # noqa: E402
                    log, talk_context)

GGUF_REPO = "AtomicChat/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-GGUF"
PLAIN = "Transcribe with punctuation and capitalization."
TEMPLATES = {
    "docs": PLAIN + " Context terms: {terms}.",
    "nvidia": PLAIN + " This audio may contain the following words or phrases (some may not be present "
                      "in the clip): {terms}.",
}


def find_bin(explicit):
    if explicit:
        return explicit
    hits = sorted(glob.glob(str(DATA / "src" / "NeMo-Speech.cpp" / "build" / "*" / "bin" / "nemo-speech")))
    cuda = [h for h in hits if "cuda" in h]
    if not (cuda or hits):
        sys.exit("nemo-speech binary not found; build NeMo-Speech.cpp (cloud/remote/setup_nemo_speech_cpp.sh)")
    return (cuda or hits)[0]


def find_model(quant):
    d = DATA / "models" / GGUF_REPO
    hits = sorted(d.glob(f"*AD-{quant}.gguf")) or sorted(d.glob(f"*{quant}*.gguf"))
    if not hits:
        sys.exit(f"no {quant} decoder in {d}; run: python3 asr/fetch_model.py \"{GGUF_REPO}:*Encoder-F16.gguf,*AD-{quant}.gguf\"")
    return hits[0]


def post(url, payload, timeout):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", help="path to nemo-speech (default: newest build under data/src/NeMo-Speech.cpp)")
    ap.add_argument("--quant", default="IQ4_NL", help="decoder GGUF variant in data/models/" + GGUF_REPO)
    ap.add_argument("--terms", action="store_true", help="per-talk hard terms as context terms")
    ap.add_argument("--max-terms", type=int, default=20)
    ap.add_argument("--template", default="docs", choices=sorted(TEMPLATES))
    ap.add_argument("--salm", action="append", default=[], metavar="KEY=VALUE",
                    help="asr.salm.* setting, e.g. max_sequences=1 (repeatable)")
    ap.add_argument("--threads", type=int, help="asr.backend.threads (CPU builds)")
    ap.add_argument("--port", type=int, default=8089)
    ap.add_argument("--timeout", type=float, default=3600, help="per-request timeout (s)")
    ap.add_argument("--kinds", nargs="*", default=["speech", "nonspeech"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--system")
    args = ap.parse_args()

    binary, model = find_bin(args.bin), find_model(args.quant)
    backend = "cuda" if "cuda" in binary else "cpu"
    system = args.system or f"nemotron-3.5-{args.quant.lower()}" + ("+terms" if args.terms else "")
    params = {"runtime": "NeMo-Speech.cpp " + backend, "decoder": model.name, "salm": args.salm,
              "instruction": TEMPLATES[args.template] if args.terms else PLAIN,
              "context": f"context terms (hard terms, max {args.max_terms})" if args.terms else None}
    run = Run(system, f"nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B ({args.quant} GGUF)", params, backend)
    clips = [c for c in load_manifest(kinds=args.kinds, limit=args.limit) if not run.done(c)]
    log(f"[{system}] {len(clips)} clips to do")
    if not clips:
        return

    cmd = [binary, "serve", "--asr-model", str(model), "--host", "127.0.0.1", "--port", str(args.port)]
    for kv in args.salm:
        k, _, v = kv.partition("=")
        cmd += [f"--asr.salm.{k}", v]
    if args.threads:
        cmd += ["--asr.backend.threads", str(args.threads)]
    logf = open(DATA / "logs" / f"nemo-speech-{system}.log", "a")
    log("  starting: " + " ".join(cmd))
    srv = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT, start_new_session=True)
    base = f"http://127.0.0.1:{args.port}"
    try:
        with GpuMemoryMonitor() as mon:
            t = time.time()
            while True:
                if srv.poll() is not None:
                    sys.exit(f"nemo-speech exited ({srv.returncode}); see data/logs/nemo-speech-{system}.log")
                try:
                    with urllib.request.urlopen(base + "/ready", timeout=5) as r:
                        if r.status == 200:
                            break
                except (urllib.error.URLError, OSError):
                    pass
                time.sleep(3)
            run.meta["load_sec"] = round(time.time() - t, 1)
            log(f"  server ready in {run.meta['load_sec']}s")
            for n, clip in enumerate(clips, 1):
                terms = hard_terms(talk_context(clip["talk_id"]), max_terms=args.max_terms) if args.terms else []
                instruction = TEMPLATES[args.template].format(terms=", ".join(terms)) if terms else PLAIN
                audio_b64 = base64.b64encode(clip_audio_path(clip).read_bytes()).decode()
                payload = {"model": "salm", "temperature": 0, "messages": [{"role": "user", "content": [
                    {"type": "text", "text": instruction},
                    {"type": "input_audio", "input_audio": {"data": audio_b64, "format": "wav"}}]}]}
                t = time.time()
                res = post(base + "/v1/chat/completions", payload, args.timeout)
                dt = time.time() - t
                text = (res["choices"][0]["message"].get("content") or "").strip()
                dur = clip["end"] - clip["start"]
                run.save(clip, text, [{"start": 0.0, "end": round(dur, 2), "text": text}] if text else [], None,
                         dur, dt, context=terms or None)
                log(f"  {n}/{len(clips)} {clip['clip_id']} {dur:.0f}s in {dt:.1f}s")
        run.finish(mon.peak_mb if backend == "cuda" else None)
    finally:
        os.killpg(srv.pid, signal.SIGTERM)
        try:
            srv.wait(timeout=30)
        except subprocess.TimeoutExpired:
            os.killpg(srv.pid, signal.SIGKILL)


if __name__ == "__main__":
    main()
