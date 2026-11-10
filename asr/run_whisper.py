#!/usr/bin/env python3
"""faster-whisper runner for the bake-off.

  uv run python asr/run_whisper.py --model large-v3-turbo            # plain
  uv run python asr/run_whisper.py --model large-v3-turbo --context  # per-talk prompt as hotwords

Settings shared by all configs: language=en, Silero VAD on, condition_on_previous_text=False
(the old CLI default of True is the main cause of repetition loops), word timestamps on.
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (GpuMemoryMonitor, Run, load_clip, load_manifest, local_model, log,  # noqa: E402
                    preload_cuda_libs, talk_context)

SHORT = {"large-v3-turbo": "whisper-turbo", "large-v3": "whisper-large-v3", "distil-large-v3.5": "whisper-distil"}
REPOS = {"large-v3-turbo": "mobiuslabsgmbh/faster-whisper-large-v3-turbo", "large-v3": "Systran/faster-whisper-large-v3"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="large-v3-turbo")
    ap.add_argument("--context", action="store_true", help="pass the talk's context prompt as hotwords")
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--compute-type", default=None, help="default: float16 on cuda, int8 on cpu")
    ap.add_argument("--batch-size", type=int, default=None,
                    help="0 = sequential decoding; default 8 (turbo) or 2 (large-v3: its 32-layer decoder OOMs at 4 with ~5.5 GB free)")
    ap.add_argument("--beam-size", type=int, default=5)
    ap.add_argument("--kinds", nargs="*", default=["speech", "nonspeech"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--system", help="override output system name")
    args = ap.parse_args()

    if args.batch_size is None:
        args.batch_size = 2 if args.model == "large-v3" else 8
    if args.device == "cuda":
        preload_cuda_libs()
    from faster_whisper import BatchedInferencePipeline, WhisperModel

    compute = args.compute_type or ("float16" if args.device == "cuda" else "int8")
    system = args.system or SHORT.get(args.model, args.model) + ("+ctx" if args.context else "")
    params = {"language": "en", "vad_filter": True, "condition_on_previous_text": False,
              "word_timestamps": True, "beam_size": args.beam_size, "batch_size": args.batch_size,
              "compute_type": compute, "context": "hotwords=talk prompt" if args.context else None}
    run = Run(system, f"faster-whisper {args.model}", params, args.device)

    clips = [c for c in load_manifest(kinds=args.kinds, limit=args.limit) if not run.done(c)]
    log(f"[{system}] {len(clips)} clips to do")
    if not clips:
        return
    with GpuMemoryMonitor() as mon:
        t = time.time()
        src = local_model(REPOS[args.model]) if args.model in REPOS else args.model
        if src == REPOS.get(args.model):
            src = args.model  # not fetched locally: let faster-whisper resolve the name
        model = WhisperModel(src, device=args.device, compute_type=compute,
                             cpu_threads=0 if args.device == "cuda" else 12)
        pipe = BatchedInferencePipeline(model) if args.batch_size > 0 else model
        run.meta["load_sec"] = round(time.time() - t, 1)
        for n, clip in enumerate(clips, 1):
            audio = load_clip(clip)
            ctx = talk_context(clip["talk_id"]) if args.context else None
            hot = ctx["prompt"] if ctx else None
            kw = dict(language="en", vad_filter=True, condition_on_previous_text=False,
                      word_timestamps=True, beam_size=args.beam_size, hotwords=hot)
            if args.batch_size > 0:
                kw["batch_size"] = args.batch_size
            t = time.time()
            segs, _ = pipe.transcribe(audio, **kw)
            segs = list(segs)
            dt = time.time() - t
            segments = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segs]
            words = [{"start": round(w.start, 2), "end": round(w.end, 2), "word": w.word.strip()}
                     for s in segs for w in (s.words or [])]
            text = " ".join(s["text"] for s in segments)
            run.save(clip, text, segments, words, len(audio) / 16000, dt, context=hot)
            log(f"  {n}/{len(clips)} {clip['clip_id']} {len(audio)/16000:.0f}s in {dt:.1f}s")
    run.finish(mon.peak_mb if args.device == "cuda" else None)


if __name__ == "__main__":
    main()
