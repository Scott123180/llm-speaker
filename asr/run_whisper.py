#!/usr/bin/env python3
"""faster-whisper runner for the bake-off.

  uv run python asr/run_whisper.py --model large-v3-turbo            # plain
  uv run python asr/run_whisper.py --model large-v3-turbo --context  # per-talk prompt as hotwords

Settings shared by all configs: language=en, Silero VAD on, condition_on_previous_text=False
(the old CLI default of True is the main cause of repetition loops), word timestamps on.

Phrase-drop experiments (see eval/drops.py):
  --vad-threshold 0.35 --vad-pad-ms 800   # let quieter speech through the voice detector
  --batch-size 0                          # sequential decoding instead of batched 30 s chunks
  --no-speech-threshold off               # never skip a window the decoder thinks is silence
  --context-dir DIR --system NAME         # alternative per-talk prompts (e.g. longer ones)
  --drop-prompt-echo                      # remove segments that only repeat the prompt (noise, silence)
  --hallucination-silence 2               # sequential only: skip silent gaps where Whisper hallucinates
"""
import json
import re
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (GpuMemoryMonitor, Run, load_clip, load_manifest, local_model, log,  # noqa: E402
                    preload_cuda_libs, talk_context)

SHORT = {"large-v3-turbo": "whisper-turbo", "large-v3": "whisper-large-v3", "distil-large-v3.5": "whisper-distil"}
REPOS = {"large-v3-turbo": "mobiuslabsgmbh/faster-whisper-large-v3-turbo", "large-v3": "Systran/faster-whisper-large-v3"}


def _toks(text):
    return re.findall(r"[a-z0-9']+", text.lower())


def is_echo(text, prompt, n=4):
    """A segment that repeats the prompt instead of transcribing audio: 3-5 words found verbatim
    in the prompt, or at least half of its 4-grams in the prompt (same rule as eval/report.py)."""
    st, pt = _toks(text), _toks(prompt)
    if len(st) < 3:
        return False
    if len(st) <= 5 and any(pt[i:i + len(st)] == st for i in range(len(pt) - len(st) + 1)):
        return True
    grams = {tuple(pt[i:i + n]) for i in range(len(pt) - n + 1)}
    hits = sum(1 for i in range(len(st) - n + 1) if tuple(st[i:i + n]) in grams)
    return len(st) >= n and hits >= 0.5 * (len(st) - n + 1)


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
    ap.add_argument("--vad-threshold", type=float, help="Silero speech probability threshold (default 0.5)")
    ap.add_argument("--vad-pad-ms", type=int, help="padding around detected speech (default 400)")
    ap.add_argument("--min-silence-ms", type=int, help="silence that splits speech (default 2000)")
    ap.add_argument("--no-vad", action="store_true", help="no voice detection (sequential decoding only)")
    ap.add_argument("--no-speech-threshold", default="0.6", help="'off' = never skip a window as silence")
    ap.add_argument("--context-dir", type=Path, help="read per-talk prompts from this dir instead")
    ap.add_argument("--drop-prompt-echo", action="store_true", help="remove segments that repeat the prompt")
    ap.add_argument("--hallucination-silence", type=float, help="sequential decoding: hallucination_silence_threshold")
    args = ap.parse_args()

    if args.batch_size is None:
        args.batch_size = 2 if args.model == "large-v3" else 8
    if args.no_vad and args.batch_size > 0:
        ap.error("--no-vad needs --batch-size 0 (batched decoding cuts audio at voice-detector boundaries)")
    vad = {k: v for k, v in (("threshold", args.vad_threshold), ("speech_pad_ms", args.vad_pad_ms),
                             ("min_silence_duration_ms", args.min_silence_ms)) if v is not None}
    nst = None if args.no_speech_threshold == "off" else float(args.no_speech_threshold)
    if args.device == "cuda":
        preload_cuda_libs()
    from faster_whisper import BatchedInferencePipeline, WhisperModel

    compute = args.compute_type or ("float16" if args.device == "cuda" else "int8")
    system = args.system or SHORT.get(args.model, args.model) + ("+ctx" if args.context else "")
    if args.hallucination_silence is not None and args.batch_size > 0:
        ap.error("--hallucination-silence needs --batch-size 0")
    params = {"language": "en", "vad_filter": not args.no_vad, "vad_parameters": vad or None,
              "drop_prompt_echo": args.drop_prompt_echo, "hallucination_silence_threshold": args.hallucination_silence,
              "no_speech_threshold": nst, "condition_on_previous_text": False,
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
            if args.context and args.context_dir:
                f = args.context_dir / f"{clip['talk_id']}.json"
                ctx = json.loads(f.read_text()) if f.exists() else None
            else:
                ctx = talk_context(clip["talk_id"]) if args.context else None
            hot = ctx["prompt"] if ctx else None
            kw = dict(language="en", vad_filter=not args.no_vad, vad_parameters=vad or None,
                      no_speech_threshold=nst, condition_on_previous_text=False,
                      word_timestamps=True, beam_size=args.beam_size, hotwords=hot)
            if args.batch_size > 0:
                kw["batch_size"] = args.batch_size
            if args.hallucination_silence is not None:
                kw["hallucination_silence_threshold"] = args.hallucination_silence
            t = time.time()
            segs, _ = pipe.transcribe(audio, **kw)
            segs = list(segs)
            dt = time.time() - t
            if args.drop_prompt_echo and hot:
                kept = [s for s in segs if not is_echo(s.text, hot)]
                run.meta["echo_dropped"] = run.meta.get("echo_dropped", 0) + len(segs) - len(kept)
                segs = kept
            segments = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segs]
            words = [{"start": round(w.start, 2), "end": round(w.end, 2), "word": w.word.strip()}
                     for s in segs for w in (s.words or [])]
            text = " ".join(s["text"] for s in segments)
            run.save(clip, text, segments, words, len(audio) / 16000, dt, context=hot)
            log(f"  {n}/{len(clips)} {clip['clip_id']} {len(audio)/16000:.0f}s in {dt:.1f}s")
    run.finish(mon.peak_mb if args.device == "cuda" else None)


if __name__ == "__main__":
    main()
