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

Production options (off by default, so earlier command lines give the same output):
  --vad            send only voice-detected speech: the clip's VAD spans (data/goldset/vad) merged into
                   pieces of at most --chunk-sec, split at pauses longer than --max-gap. The model invents
                   text in long silences and noise; a clip with no detected speech gets no request.
  --word-times     ask the server for word timestamps (the encoder's CTC timestamp head) and speaker
                   labels; saved as `words` and as cue-level `segments`, shifted by each piece's offset.
                   Speaker labels are per request, so they are not comparable across pieces.
  --strip-fillers  drop "uh", "um", "er" from `text` and `words`; the model's text is kept as `raw_text`.
Stdlib + numpy only (runs in the main env).
"""
import argparse
import base64
import glob
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import wave
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (DATA, GpuMemoryMonitor, Run, clip_audio_path, hard_terms, load_manifest,  # noqa: E402
                    log, talk_context, write_pieces)

GGUF_REPO = "AtomicChat/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-GGUF"
PLAIN = "Transcribe with punctuation and capitalization."
TEMPLATES = {
    "docs": PLAIN + " Context terms: {terms}.",
    "nvidia": PLAIN + " This audio may contain the following words or phrases (some may not be present "
                      "in the clip): {terms}.",
}
# hesitation sounds only; "ah", "oh", "mm" can carry meaning in a talk and stay
FILLERS = {"uh", "um", "umm", "uhm", "uhh", "er", "erm"}


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


def _core(tok):
    return re.sub(r"^\W+|\W+$", "", tok).lower()


def is_filler(tok):
    return _core(tok) in FILLERS


def strip_fillers(text):
    """Drop hesitation words, keeping the sentence readable: "Um, now Obaku…" -> "Now Obaku…",
    "in, uh, Soto school" -> "in Soto school", "tutor. Uh, who's" -> "tutor. Who's"."""
    out, cap_next = [], False
    for tok in text.split():
        if not is_filler(tok):
            if cap_next and tok[:1].islower():
                tok = tok[:1].upper() + tok[1:]
            cap_next = False
            out.append(tok)
            continue
        end = re.search(r"[.?!]+$", tok)
        if end and out:  # "word, uh." -> "word."
            out[-1] = re.sub(r"[,;:]+$", "", out[-1])
            if not re.search(r"[.?!]$", out[-1]):
                out[-1] += end.group()
        elif tok.endswith(",") and out and out[-1].endswith(","):  # "in, uh, Soto" -> "in Soto"
            out[-1] = out[-1][:-1]
        sentence_start = not out or re.search(r"[.?!]$", out[-1])
        if tok[:1].isupper() and sentence_start:
            cap_next = True
    return " ".join(out)


def pieces_for(clip, args, tmp):
    """[(wav path, offset s)] to send for one clip."""
    if args.vad:
        return write_pieces(clip, args.chunk_sec, tmp, max_gap=args.max_gap)
    return [(str(clip_audio_path(clip)), 0.0)]


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
    ap.add_argument("--repeat", type=int, default=1,
                    help="speed tests only: send every clip N times, to keep more requests in flight than there are clips")
    ap.add_argument("--concurrency", type=int, default=1,
                    help="requests in flight at once (the server batches up to salm max_sequences)")
    ap.add_argument("--vad", action="store_true", help="send voice-detected pieces only (see the module docstring)")
    ap.add_argument("--chunk-sec", type=float, default=120, help="--vad: longest piece (s)")
    ap.add_argument("--max-gap", type=float, default=5, help="--vad: a longer pause starts a new piece (s)")
    ap.add_argument("--word-times", action="store_true", help="word timestamps and speaker labels from the server")
    ap.add_argument("--strip-fillers", action="store_true", help='drop "uh", "um", "er" (raw text kept as raw_text)')
    ap.add_argument("--timeout", type=float, default=3600, help="per-request timeout (s)")
    ap.add_argument("--kinds", nargs="*", default=["speech", "nonspeech"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--system")
    args = ap.parse_args()

    binary, model = find_bin(args.bin), find_model(args.quant)
    backend = "cuda" if "cuda" in binary else "cpu"
    system = args.system or (f"nemotron-3.5-{args.quant.lower()}" + ("+terms" if args.terms else "")
                             + (f"+vad{args.chunk_sec:g}" if args.vad else ""))
    params = {"runtime": "NeMo-Speech.cpp " + backend, "decoder": model.name, "salm": args.salm,
              "instruction": TEMPLATES[args.template] if args.terms else PLAIN,
              "context": f"context terms (hard terms, max {args.max_terms})" if args.terms else None,
              "input": (f"VAD pieces <= {args.chunk_sec:g}s, split at pauses > {args.max_gap:g}s" if args.vad
                        else "whole clip"),
              "word_times": args.word_times, "strip_fillers": args.strip_fillers}
    run = Run(system, f"nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B ({args.quant} GGUF)", params, backend)
    clips = [c for c in load_manifest(kinds=args.kinds, limit=args.limit) if not run.done(c)] * max(1, args.repeat)
    log(f"[{system}] {len(clips)} clips to do" + (f" ({args.repeat} times each)" if args.repeat > 1 else ""))
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
    tmp = tempfile.mkdtemp(prefix="nemotron-")
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

            def transcribe(job):
                i, k, path, off, terms = job
                instruction = TEMPLATES[args.template].format(terms=", ".join(terms)) if terms else PLAIN
                audio_b64 = base64.b64encode(Path(path).read_bytes()).decode()
                payload = {"model": "salm", "temperature": 0, "messages": [{"role": "user", "content": [
                    {"type": "text", "text": instruction},
                    {"type": "input_audio", "input_audio": {"data": audio_b64, "format": "wav"}}]}]}
                if args.word_times:
                    payload["timestamp_granularities"] = ["word"]
                t = time.time()
                res = post(base + "/v1/chat/completions", payload, args.timeout)
                text = (res["choices"][0]["message"].get("content") or "").strip()
                tr = res.get("transcription") or {}
                words = [{"word": w["word"], "start": round(w["start"] + off, 3), "end": round(w["end"] + off, 3),
                          **({"speaker": w["speaker"]} if w.get("speaker") is not None else {})}
                         for w in tr.get("words") or []]
                cues = [{"start": round(c["start"] + off, 2), "end": round(c["end"] + off, 2), "text": c["text"]}
                        for c in tr.get("subtitle_cues") or []]
                status = (tr.get("word_timestamp_alignment") or {}).get("status") if args.word_times else None
                with wave.open(path) as wf:
                    sec = wf.getnframes() / wf.getframerate()
                return i, k, off, sec, text, words, cues, status, time.time() - t

            # every piece of every clip is one request; a clip is saved once all its pieces are back
            jobs, todo, parts, clip_terms = [], {}, {}, {}
            for i, clip in enumerate(clips):
                terms = clip_terms[i] = hard_terms(talk_context(clip["talk_id"]), max_terms=args.max_terms) \
                    if args.terms else []
                ps = pieces_for(clip, args, tmp)
                todo[i], parts[i] = len(ps), [None] * len(ps)
                jobs += [(i, k, path, off, terms) for k, (path, off) in enumerate(ps)]
            run.meta["requests"] = len(jobs)
            done = 0

            def finish(i):
                nonlocal done
                clip, got = clips[i], parts[i]
                dur = clip["end"] - clip["start"]
                # got[k] = (offset, piece seconds, text, words, cues, alignment status, request seconds)
                raw = " ".join(g[2] for g in got if g[2])
                words = [w for g in got for w in g[3]]
                segments = [c for g in got for c in g[4]] or [
                    {"start": round(g[0], 2), "end": round(g[0] + g[1], 2), "text": g[2]} for g in got if g[2]]
                extra = {"raw_text": raw} if args.strip_fillers else {}
                text = strip_fillers(raw) if args.strip_fillers else raw
                if args.strip_fillers:
                    words = [w for w in words if not is_filler(w["word"])]
                    segments = [dict(s, text=strip_fillers(s["text"])) for s in segments]
                    segments = [s for s in segments if s["text"]]
                if args.word_times:
                    extra["alignment"] = [g[5] for g in got]
                run.save(clip, text, segments, words if args.word_times else None, dur, sum(g[6] for g in got),
                         context=clip_terms[i] or None, extra=extra)
                done += 1
                log(f"  {done}/{len(clips)} {clip['clip_id']} {dur:.0f}s, {len(got)} piece(s)")

            # results are saved on this thread; with several requests in flight, each clip's
            # wall_sec is its own latency and the run's wall_sec is the elapsed time
            t0 = time.time()
            for i in [i for i, n in todo.items() if n == 0]:  # no speech detected: no request
                finish(i)
            with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
                futs = [pool.submit(transcribe, j) for j in jobs]
                for fut in as_completed(futs):
                    i, k, off, sec, text, words, cues, status, dt = fut.result()
                    parts[i][k] = (off, sec, text, words, cues, status, dt)
                    todo[i] -= 1
                    if todo[i] == 0:
                        finish(i)
            if args.concurrency > 1 or args.vad:
                run.meta["wall_sec"] = time.time() - t0
                run.meta["concurrency"] = args.concurrency
            if args.word_times:
                st = [g[5] for p in parts.values() for g in p if g]
                run.meta["alignment"] = {s: st.count(s) for s in set(st)}
        run.finish(mon.peak_mb if backend == "cuda" else None)
    finally:
        try:
            os.killpg(srv.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass  # the server already exited (its log says why)
        try:
            srv.wait(timeout=30)
        except subprocess.TimeoutExpired:
            os.killpg(srv.pid, signal.SIGKILL)


if __name__ == "__main__":
    main()
