#!/usr/bin/env python3
"""Microsoft VibeVoice-ASR (9B, transformers >= 5.3), with optional hotword context.

  uv run --project asr/envs/hf python asr/run_vibevoice.py               # whole clip, one pass
  uv run --project asr/envs/hf python asr/run_vibevoice.py --terms       # + per-talk hard terms as context
  uv run --project asr/envs/hf python asr/run_vibevoice.py --vad         # only VAD speech spans

Takes up to 60 min per call and returns speaker-labelled, timestamped segments.
~18 GB in bf16: fits a 24 GB GPU; on smaller GPUs --offload spreads it over GPU + RAM
(slow, for smoke tests). Context is passed as the processor's `prompt` (card: "Providing
context"); per Huber & Waibel 2026 it helps with correct lists and collapses with many
distractors, so keep lists short.
"""
import argparse
import json
import re
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (GpuMemoryMonitor, Run, clip_audio_path, hard_terms, load_manifest, local_model,  # noqa: E402
                    log, talk_context, write_pieces)


def salvage(raw):
    """Segments from VibeVoice output whose JSON doesn't parse: every complete {...} object that
    does, then the text of a final cut-off "Content" string."""
    out = []
    for m in re.finditer(r"\{[^{}]*\}", raw):
        try:
            obj = json.loads(m.group(0))
        except ValueError:
            continue
        if isinstance(obj, dict) and obj.get("Content"):
            out.append(obj)
    tail = raw[raw.rfind("}") + 1:] if "}" in raw else raw
    m = re.search(r'"Start"\s*:\s*([\d.]+).*?"Content"\s*:\s*"(.*)$', tail, re.S)
    if m and m.group(2).strip():
        out.append({"Start": float(m.group(1)), "End": float(m.group(1)), "Content": m.group(2).strip()})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="microsoft/VibeVoice-ASR-HF")
    ap.add_argument("--terms", action="store_true")
    ap.add_argument("--max-terms", type=int, default=20)
    ap.add_argument("--vad", action="store_true", help="decode VAD speech spans (merged up to --chunk-sec)")
    ap.add_argument("--chunk-sec", type=float, default=300)
    ap.add_argument("--offload", action="store_true", help="device_map=auto (GPU + CPU RAM)")
    ap.add_argument("--tokenizer-chunk-sec", type=float, help="acoustic tokenizer chunk (lower if OOM)")
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--kinds", nargs="*", default=["speech", "nonspeech"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--system")
    ap.add_argument("--batch-size", type=int, default=1,
                    help="whole clips per generate call, grouped by length; halves on CUDA out-of-memory")
    ap.add_argument("--tokens-per-sec", type=float, default=15.0,
                    help="output token budget per second of audio (speech plus JSON is about 6-8)")
    args = ap.parse_args()
    if args.vad and args.batch_size > 1:
        ap.error("--batch-size applies to whole clips; use it without --vad")

    import os
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    import torch
    from transformers import AutoProcessor, VibeVoiceAsrForConditionalGeneration

    system = args.system or "vibevoice-asr" + ("+vad" if args.vad else "") + ("+terms" if args.terms else "")
    dtype = torch.bfloat16 if args.device == "cuda" else torch.float32
    params = {"backend": "transformers", "dtype": str(dtype).split(".")[-1], "offload": args.offload,
              "input": f"VAD spans <= {args.chunk_sec:g}s" if args.vad else "whole clip",
              "context": f"prompt = hard terms (max {args.max_terms})" if args.terms else None}
    run = Run(system, args.model, params, args.device)
    clips = [c for c in load_manifest(kinds=args.kinds, limit=args.limit) if not run.done(c)]
    log(f"[{system}] {len(clips)} clips to do")
    if not clips:
        return

    gen_kw = {}
    if args.tokenizer_chunk_sec:
        gen_kw["tokenizer_chunk_size"] = int(args.tokenizer_chunk_sec * 24000) // 3200 * 3200
    with GpuMemoryMonitor() as mon:
        t = time.time()
        src = local_model(args.model)
        processor = AutoProcessor.from_pretrained(src)
        if args.offload:
            model = VibeVoiceAsrForConditionalGeneration.from_pretrained(src, torch_dtype=dtype, device_map="auto")
        else:
            model = VibeVoiceAsrForConditionalGeneration.from_pretrained(src, torch_dtype=dtype).to(args.device)
        model.eval()
        run.meta["load_sec"] = round(time.time() - t, 1)
        tmp = tempfile.mkdtemp(prefix="vibevoice-")

        def parse(gen_row, off):
            """Segments from one generated row (shape 1 x tokens)."""
            try:
                parsed = processor.decode(gen_row, return_format="parsed")[0]
            except ValueError:  # malformed JSON (runaway or truncated generation): keep what's readable
                parsed = salvage(processor.batch_decode(gen_row, skip_special_tokens=True)[0])
                run.meta["salvaged"] = run.meta.get("salvaged", 0) + 1
            segs = []
            if isinstance(parsed, list):
                for s in parsed:
                    txt = str(s.get("Content", "")).strip()
                    if txt:
                        segs.append({"start": round(float(s.get("Start", 0)) + off, 2),
                                     "end": round(float(s.get("End", 0)) + off, 2), "text": txt,
                                     "speaker": s.get("Speaker")})
            else:  # unparseable: keep the raw text
                txt = processor.decode(gen_row, return_format="transcription_only")[0].strip()
                if txt:
                    segs.append({"start": off, "end": off, "text": txt})
            return segs

        def generate(audio, prompt, sec):
            """Generated tokens for one audio path or a list of them (left-padded batch)."""
            inputs = processor.apply_transcription_request(audio=audio, prompt=prompt).to(model.device, model.dtype)
            with torch.inference_mode():
                # cap the output by audio length: a runaway loop otherwise runs to 32k tokens
                out = model.generate(**inputs, **gen_kw, max_new_tokens=int(200 + args.tokens_per_sec * sec))
            return out[:, inputs["input_ids"].shape[1]:]

        def terms_for(clip):
            return hard_terms(talk_context(clip["talk_id"]), max_terms=args.max_terms) if args.terms else []

        if args.vad:
            for n, clip in enumerate(clips, 1):
                terms = terms_for(clip)
                t = time.time()
                segments = []
                for path, off in write_pieces(clip, args.chunk_sec, tmp):
                    segments += parse(generate(path, ", ".join(terms) or None, args.chunk_sec), off)
                    if args.device == "cuda":
                        torch.cuda.empty_cache()
                dt, dur = time.time() - t, clip["end"] - clip["start"]
                run.save(clip, " ".join(s["text"] for s in segments), segments, None, dur, dt, context=terms or None)
                log(f"  {n}/{len(clips)} {clip['clip_id']} {dur:.0f}s in {dt:.1f}s")
        else:
            # similar lengths batch together (silent clips are ~30 s, speech clips ~6 min)
            order = sorted(clips, key=lambda c: c["end"] - c["start"])
            bs, i = max(1, args.batch_size), 0
            run.meta["params"]["batch_size"] = bs
            while i < len(order):
                batch = order[i:i + bs]
                terms = [terms_for(c) for c in batch]
                prompts = [", ".join(t) or None for t in terms]
                sec = max(c["end"] - c["start"] for c in batch)
                t = time.time()
                try:
                    if len(batch) == 1:
                        gen = generate(str(clip_audio_path(batch[0])), prompts[0], sec)
                    else:
                        gen = generate([str(clip_audio_path(c)) for c in batch], prompts, sec)
                except torch.cuda.OutOfMemoryError:
                    if bs == 1:
                        raise
                    bs //= 2
                    run.meta["params"]["batch_size"] = bs
                    log(f"  out of GPU memory: batch size now {bs}")
                    torch.cuda.empty_cache()
                    continue
                except Exception as e:  # batching itself failed: carry on one clip at a time
                    if bs == 1:
                        raise
                    bs = 1
                    run.meta["params"]["batch_size"] = bs
                    run.meta["batch_error"] = repr(e)[:300]
                    log(f"  batched generation failed ({e!r}); batch size now 1")
                    continue
                dt = time.time() - t
                for j, (clip, tms) in enumerate(zip(batch, terms)):
                    segments = parse(gen[j:j + 1], 0.0)
                    dur = clip["end"] - clip["start"]
                    # the batch's time is shared evenly, so summed wall_sec stays the elapsed time
                    run.save(clip, " ".join(s["text"] for s in segments), segments, None, dur, dt / len(batch),
                             context=tms or None)
                i += len(batch)
                log(f"  {i}/{len(order)} batch of {len(batch)} ({sec:.0f}s max) in {dt:.1f}s")
                if args.device == "cuda":
                    torch.cuda.empty_cache()
    run.finish(mon.peak_mb if args.device == "cuda" else None)


if __name__ == "__main__":
    main()
