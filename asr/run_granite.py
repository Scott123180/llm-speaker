#!/usr/bin/env python3
"""IBM Granite Speech runner (transformers), with optional keyword-list biasing.

  uv run --project asr/envs/hf python asr/run_granite.py            # plain (punctuated)
  uv run --project asr/envs/hf python asr/run_granite.py --terms    # + per-talk hard-term keywords

Granite 5.0-2B is documented for segments up to ~2 minutes, so audio is always
decoded as VAD speech spans merged up to --chunk-sec (also gates silence). The
keyword prompt is the model card's own template: "transcribe the speech to text.
Keywords: a, b, c" (the model was trained with keyword lists containing absent terms).
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (GpuMemoryMonitor, Run, hard_terms, load_clip, load_manifest, local_model,  # noqa: E402
                    log, talk_context, vad_chunks, SR)

PLAIN = "<|audio|>transcribe the speech with proper punctuation and capitalization."
KEYWORDS = "<|audio|>transcribe the speech to text. Keywords: {}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="ibm-granite/granite-speech-5.0-2b")
    ap.add_argument("--terms", action="store_true", help="per-talk hard terms as the keyword list")
    ap.add_argument("--max-terms", type=int, default=20)
    ap.add_argument("--chunk-sec", type=float, default=110)
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--kinds", nargs="*", default=["speech", "nonspeech"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--system")
    args = ap.parse_args()

    import os
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

    tag = args.model.split("/")[-1].replace("granite-speech-", "granite-")
    system = args.system or tag + ("+terms" if args.terms else "")
    dtype = torch.bfloat16 if args.device == "cuda" else torch.float32
    params = {"backend": "transformers", "dtype": str(dtype).split(".")[-1], "chunk": f"VAD spans <= {args.chunk_sec:g}s",
              "prompt": KEYWORDS if args.terms else PLAIN,
              "context": f"keyword list (hard terms, max {args.max_terms})" if args.terms else None}
    run = Run(system, args.model, params, args.device)
    clips = [c for c in load_manifest(kinds=args.kinds, limit=args.limit) if not run.done(c)]
    log(f"[{system}] {len(clips)} clips to do")
    if not clips:
        return

    with GpuMemoryMonitor() as mon:
        t = time.time()
        src = local_model(args.model)
        processor = AutoProcessor.from_pretrained(src)
        tok = processor.tokenizer
        model = AutoModelForSpeechSeq2Seq.from_pretrained(src, torch_dtype=dtype, device_map=args.device).eval()
        run.meta["load_sec"] = round(time.time() - t, 1)
        for n, clip in enumerate(clips, 1):
            audio = load_clip(clip)
            terms = hard_terms(talk_context(clip["talk_id"]), max_terms=args.max_terms) if args.terms else []
            user = KEYWORDS.format(", ".join(terms)) if terms else PLAIN
            prompt = tok.apply_chat_template([{"role": "user", "content": user}], tokenize=False,
                                             add_generation_prompt=True)
            t = time.time()
            texts, segments = [], []
            for s, e in vad_chunks(clip, args.chunk_sec):
                chunk = audio[int(s * SR):int(e * SR)]
                if len(chunk) < SR // 10:
                    continue
                wav = torch.from_numpy(chunk).unsqueeze(0)
                inputs = processor(prompt, wav, device=args.device, return_tensors="pt").to(args.device)
                max_new = max(256, int(12 * len(chunk) / SR))  # card: ~12 tokens per second of audio for ASR
                with torch.inference_mode():
                    out = model.generate(**inputs, max_new_tokens=max_new, do_sample=False, num_beams=1)
                txt = tok.batch_decode(out[:, inputs["input_ids"].shape[-1]:], skip_special_tokens=True)[0].strip()
                if txt:
                    texts.append(txt)
                    segments.append({"start": round(s, 2), "end": round(e, 2), "text": txt})
            dt = time.time() - t
            run.save(clip, " ".join(texts), segments, None, len(audio) / SR, dt, context=terms or None)
            log(f"  {n}/{len(clips)} {clip['clip_id']} {len(audio)/SR:.0f}s in {dt:.1f}s")
    run.finish(mon.peak_mb if args.device == "cuda" else None)


if __name__ == "__main__":
    main()
