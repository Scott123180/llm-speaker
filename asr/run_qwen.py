#!/usr/bin/env python3
"""Qwen3-ASR runner (transformers backend), with optional per-talk context.

  uv run --project asr/envs/qwen python asr/run_qwen.py               # plain
  uv run --project asr/envs/qwen python asr/run_qwen.py --context     # talk prompt as system context

Qwen3-ASR takes up to 20 min per call and was trained to use the system prompt as
background context (word lists or prose). No word timestamps here (its aligner
needs <=3-min chunks); text only, which is enough for WER and term metrics.
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (GpuMemoryMonitor, Run, hard_terms, load_clip, load_manifest, local_model,  # noqa: E402
                    log, talk_context, vad_chunks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-ASR-1.7B")
    ap.add_argument("--context", action="store_true", help="talk prompt (prose) as system context")
    ap.add_argument("--terms", action="store_true", help="comma-separated hard terms as system context")
    ap.add_argument("--vad", action="store_true", help="transcribe only VAD speech regions (eval/goldset.py vad)")
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--max-new-tokens", type=int, default=1024, help="per chunk")
    ap.add_argument("--chunk-sec", type=float, default=120,
                    help="split at low-energy points into chunks this long (fits an 8 GB GPU)")
    ap.add_argument("--kinds", nargs="*", default=["speech", "nonspeech"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--system")
    args = ap.parse_args()

    import os
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    import torch
    from qwen_asr import Qwen3ASRModel
    from qwen_asr.inference.utils import split_audio_into_chunks

    short = args.model.split("/")[-1].lower().replace("qwen3-asr-", "qwen3-asr-")
    system = args.system or short + ("+vad" if args.vad else "") + ("+ctx" if args.context else "") + (
        "+terms" if args.terms else "")
    dtype = torch.bfloat16 if args.device == "cuda" else torch.float32
    params = {"backend": "transformers", "dtype": str(dtype).split(".")[-1], "language": "English",
              "max_new_tokens": args.max_new_tokens, "chunk_sec": args.chunk_sec,
              "vad": args.vad,
              "context": ("system prompt = talk prompt" if args.context else
                          "system prompt = hard-term list" if args.terms else None)}
    run = Run(system, args.model, params, args.device)
    clips = [c for c in load_manifest(kinds=args.kinds, limit=args.limit) if not run.done(c)]
    log(f"[{system}] {len(clips)} clips to do")
    if not clips:
        return

    with GpuMemoryMonitor() as mon:
        t = time.time()
        model = Qwen3ASRModel.from_pretrained(local_model(args.model), dtype=dtype, device_map=args.device,
                                              max_inference_batch_size=1, max_new_tokens=args.max_new_tokens)
        run.meta["load_sec"] = round(time.time() - t, 1)
        for n, clip in enumerate(clips, 1):
            audio = load_clip(clip)
            ctx = talk_context(clip["talk_id"]) if (args.context or args.terms) else None
            prompt = ""
            if ctx and args.context:
                prompt = ctx["prompt"]
            elif ctx and args.terms:
                prompt = ", ".join(hard_terms(ctx))
            t = time.time()
            texts, segments = [], []
            if args.vad:
                pieces = [(audio[int(s * 16000):int(e * 16000)], s) for s, e in vad_chunks(clip, args.chunk_sec)]
            else:
                pieces = split_audio_into_chunks(audio, 16000, max_chunk_sec=args.chunk_sec)
            pieces = list(pieces)
            while pieces:
                chunk, offset = pieces.pop(0)
                try:
                    with torch.inference_mode():
                        res = model.transcribe(audio=(chunk, 16000), context=prompt, language="English")[0]
                except torch.OutOfMemoryError:
                    # Free VRAM varies with whatever else is on the GPU; halve the chunk and retry.
                    torch.cuda.empty_cache()
                    if len(chunk) < 10 * 16000:
                        raise
                    half = len(chunk) // 2
                    log(f"    OOM on {len(chunk)/16000:.0f}s chunk at {offset:.0f}s; splitting")
                    run.meta["oom_splits"] = run.meta.get("oom_splits", 0) + 1
                    pieces[:0] = [(chunk[:half], offset), (chunk[half:], offset + half / 16000)]
                    continue
                txt = (res.text or "").strip()
                if txt:
                    texts.append(txt)
                    segments.append({"start": round(offset, 2), "end": round(offset + len(chunk) / 16000, 2),
                                     "text": txt})
                torch.cuda.empty_cache() if args.device == "cuda" else None
            dt = time.time() - t
            run.save(clip, " ".join(texts), segments, None, len(audio) / 16000, dt, context=prompt or None)
            log(f"  {n}/{len(clips)} {clip['clip_id']} {len(audio)/16000:.0f}s in {dt:.1f}s")
    run.finish(mon.peak_mb if args.device == "cuda" else None)


if __name__ == "__main__":
    main()
