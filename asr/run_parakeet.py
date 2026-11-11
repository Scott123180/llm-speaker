#!/usr/bin/env python3
"""NVIDIA Parakeet-TDT (NeMo) runner, with optional GPU phrase boosting.

  uv run --project asr/envs/nemo python asr/run_parakeet.py                 # plain
  uv run --project asr/envs/nemo python asr/run_parakeet.py --boost 0.5     # boost the talk's ranked terms

Uses local attention so the same setup handles 90-minute talks in production.
Boosting swaps the decoder's phrase list for every talk (GPU-PB / "TurboBias").
"""
import argparse
import copy
import logging
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (GpuMemoryMonitor, Run, clip_audio_path, hard_terms, load_manifest,  # noqa: E402
                    local_model, log, talk_context, write_pieces)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="nvidia/parakeet-tdt-0.6b-v3")
    ap.add_argument("--boost", type=float, default=0.0, help="boosting_tree_alpha (0 = off)")
    ap.add_argument("--max-terms", type=int, default=40)
    ap.add_argument("--hard-only", action="store_true",
                    help="boost only terms Whisper often gets wrong (skips common words like 'koan')")
    ap.add_argument("--cut-sec", type=float, default=0,
                    help="decode VAD speech spans merged up to this length (parakeet-ft-v1 recipe: 90); 0 = whole clip")
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--kinds", nargs="*", default=["speech", "nonspeech"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--system")
    args = ap.parse_args()

    logging.getLogger("nemo_logger").setLevel(logging.ERROR)
    import gc
    import os
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    import torch
    import nemo.collections.asr as nemo_asr
    from omegaconf import open_dict

    short = "parakeet-v3" if "v3" in args.model else args.model.split("/")[-1]
    system = args.system or (short + (f"+vad{args.cut_sec:g}" if args.cut_sec else "")
                             + (f"+boost{args.boost:g}" if args.boost else "") + ("f" if args.hard_only else ""))
    which = "hard terms (difficulty>=0.15, with evidence)" if args.hard_only else f"top {args.max_terms} talk terms"
    params = {"decoding": "greedy_batch (TDT label-looping)", "attention": "rel_pos_local_attn [256,256]",
              "cut": f"VAD spans <= {args.cut_sec:g}s" if args.cut_sec else "whole clip",
              "context": f"phrase boosting alpha={args.boost}, {which}" if args.boost else None}
    run = Run(system, args.model, params, args.device)
    clips = [c for c in load_manifest(kinds=args.kinds, limit=args.limit) if not run.done(c)]
    log(f"[{system}] {len(clips)} clips to do")
    if not clips:
        return

    with GpuMemoryMonitor() as mon:
        t = time.time()
        local = Path(local_model(args.model))
        nemo_files = sorted(local.glob("*.nemo")) if local.is_dir() else []
        # load the state dict on the CPU, then move: loading straight to the GPU briefly holds
        # two copies of the weights (~4.8 GB), which no longer fits beside the desktop's VRAM use
        if nemo_files:
            model = nemo_asr.models.ASRModel.restore_from(str(nemo_files[0]), map_location="cpu")
        else:
            model = nemo_asr.models.ASRModel.from_pretrained(args.model, map_location="cpu")
        model = model.to(args.device)
        model.change_attention_model("rel_pos_local_attn", [256, 256])
        model.change_subsampling_conv_chunking_factor(1)
        model.eval()
        base_cfg = copy.deepcopy(model.cfg.decoding)
        with open_dict(base_cfg):
            base_cfg.strategy = "greedy_batch"
            # CUDA-graph compilation failed on this GPU/driver and the graphs pile up
            # when the decoder is rebuilt per talk; plain loops are plenty fast.
            base_cfg.greedy.use_cuda_graph_decoder = False
        model.change_decoding_strategy(base_cfg, verbose=False)
        run.meta["load_sec"] = round(time.time() - t, 1)

        current = None
        tmp = tempfile.mkdtemp(prefix="parakeet-")
        for n, clip in enumerate(clips, 1):
            terms = None
            if args.boost:
                ctx = talk_context(clip["talk_id"])
                if args.hard_only:
                    terms = hard_terms(ctx, max_terms=args.max_terms)
                else:
                    terms = [x["form"] for x in (ctx or {}).get("terms", [])[: args.max_terms]]
                if terms != current:
                    cfg = copy.deepcopy(base_cfg)
                    with open_dict(cfg):
                        cfg.greedy.boosting_tree = {"key_phrases_list": terms or ["Zen"], "context_score": 1.0,
                                                    "depth_scaling": 2.0}
                        cfg.greedy.boosting_tree_alpha = args.boost if terms else 0.0
                    model.change_decoding_strategy(cfg, verbose=False)
                    current = terms
                    gc.collect()
                    torch.cuda.empty_cache() if args.device == "cuda" else None
            path = clip_audio_path(clip)
            dur = clip["end"] - clip["start"]
            t = time.time()
            if args.cut_sec:
                pieces = write_pieces(clip, args.cut_sec, tmp)
            else:
                pieces = [(str(path), 0.0)]
            texts, segments, words = [], [], []
            for p, off in pieces:
                with torch.inference_mode():
                    hyp = model.transcribe([p], timestamps=True, batch_size=1, verbose=False)[0]
                ts = hyp.timestamp or {}
                if hyp.text.strip():
                    texts.append(hyp.text.strip())
                segments += [{"start": round(s["start"] + off, 2), "end": round(s["end"] + off, 2),
                              "text": s["segment"].strip()} for s in ts.get("segment", [])]
                words += [{"start": round(w["start"] + off, 2), "end": round(w["end"] + off, 2), "word": w["word"]}
                          for w in ts.get("word", [])]
            dt = time.time() - t
            run.save(clip, " ".join(texts), segments, words, dur, dt, context=terms)
            log(f"  {n}/{len(clips)} {clip['clip_id']} {dur:.0f}s in {dt:.1f}s")
    run.finish(mon.peak_mb if args.device == "cuda" else None)


if __name__ == "__main__":
    main()
