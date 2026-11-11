"""Shared helpers for ASR runners (stdlib + numpy only, so every env can import it).

Every runner reads the same manifest, decodes audio the same way, and writes
the same JSON per clip:

  data/outputs/{system}/{clip_id}.json
    {clip_id, system, text, segments: [{start, end, text}], words: [{start, end, word}] | null,
     audio_sec, wall_sec, context: str | list | null}
  data/outputs/{system}/_run.json   (model, params, device, load time, peak memory, totals)
"""
from __future__ import annotations

import ctypes
import glob
import json
import os
import resource
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
MANIFEST = REPO / "eval" / "goldset" / "manifest.json"
CONTEXT_DIR = REPO / "transcriber" / "context"
SR = 16000


def preload_cuda_libs():
    """CTranslate2 dlopens libcublas/libcudnn by soname; when they come from pip
    wheels (nvidia-*-cu12) they aren't on the loader path. Preload them globally."""
    order = ["cublasLt", "cublas", "cudnn_graph", "cudnn_ops", "cudnn_cnn", "cudnn_adv",
             "cudnn_engines_precompiled", "cudnn_engines_runtime_compiled", "cudnn_heuristic", "cudnn"]
    roots = [Path(p) / "nvidia" for p in sys.path if p.endswith("site-packages")]
    for name in order:
        for root in roots:
            hits = sorted(glob.glob(str(root / "*" / "lib" / f"lib{name}.so.*")))
            if hits:
                try:
                    ctypes.CDLL(hits[0], mode=ctypes.RTLD_GLOBAL)
                except OSError:
                    pass
                break


def local_model(repo):
    """Prefer a copy fetched by asr/fetch_model.py (data/models/{repo}) over the HF cache."""
    d = DATA / "models" / repo
    return str(d) if (d / ".complete").exists() else repo


def load_audio(path, start=None, end=None):
    """Decode with the ffmpeg CLI to 16 kHz mono float32 (identical for every runner)."""
    cmd = ["ffmpeg", "-nostdin", "-v", "error"]
    if start is not None:
        cmd += ["-ss", f"{start:.3f}"]
    if end is not None:
        cmd += ["-to", f"{end:.3f}"] if start is None else ["-t", f"{end - start:.3f}"]
    cmd += ["-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def load_manifest(path=MANIFEST, kinds=None, limit=None):
    clips = json.loads(Path(path).read_text())["clips"]
    if kinds:
        clips = [c for c in clips if c["kind"] in kinds]
    return clips[:limit] if limit else clips


def clip_audio_path(clip):
    return DATA / "goldset" / "clips" / f"{clip['clip_id']}.wav"


def load_clip(clip):
    p = clip_audio_path(clip)
    if not p.exists():
        sys.exit(f"missing {p}; run: uv run python eval/goldset.py cut")
    return load_audio(p)


def vad_chunks(clip, max_sec, pad=0.2):
    """Speech regions from eval/goldset.py vad, merged into spans of at most max_sec.
    Returns [(start_s, end_s)]; empty for clips with no detected speech."""
    p = DATA / "goldset" / "vad" / f"{clip['clip_id']}.json"
    if not p.exists():
        sys.exit(f"missing {p}; run: uv run python eval/goldset.py vad")
    spans = []
    for s, e in json.loads(p.read_text()):
        if spans and e - spans[-1][0] <= max_sec:
            spans[-1][1] = e
        else:
            spans.append([s, e])
    return [(max(0.0, s - pad), e + pad) for s, e in spans]


def write_pieces(clip, max_sec, out_dir):
    """Write the clip's VAD speech spans (merged up to max_sec) as 16 kHz PCM wavs.
    Returns [(path, offset_s)]; for runners whose API takes file paths."""
    import wave
    audio = load_clip(clip)
    out = []
    for i, (s, e) in enumerate(vad_chunks(clip, max_sec)):
        seg = audio[int(s * SR):int(e * SR)]
        if len(seg) < SR // 10:
            continue
        p = Path(out_dir) / f"{clip['clip_id']}_{i:03d}.wav"
        with wave.open(str(p), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((np.clip(seg, -1, 1) * 32767).astype("<i2").tobytes())
        out.append((str(p), s))
    return out


def hard_terms(ctx, max_terms=20, min_difficulty=0.15):
    """Terms Whisper tends to get wrong that have evidence in this talk (same filter as the prompt)."""
    if not ctx:
        return []
    terms = [t for t in ctx["terms"] if t["difficulty"] >= min_difficulty and t.get("evidence", True)]
    return [t["form"] for t in terms[:max_terms]]


def talk_context(talk_id):
    p = CONTEXT_DIR / f"{talk_id}.json"
    return json.loads(p.read_text()) if p.exists() else None


class GpuMemoryMonitor:
    """Polls nvidia-smi for device memory used; reports peak above the baseline."""

    def __init__(self, interval=0.5):
        self.interval, self.peak, self.baseline = interval, 0, self._used()
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._run, daemon=True)

    @staticmethod
    def _used():
        try:
            out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                                 capture_output=True, text=True, timeout=5).stdout
            return int(out.split()[0])
        except Exception:
            return 0

    def _run(self):
        while not self._stop.is_set():
            self.peak = max(self.peak, self._used())
            self._stop.wait(self.interval)

    def __enter__(self):
        self._t.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._t.join()

    @property
    def peak_mb(self):
        return max(0, self.peak - self.baseline)


def peak_rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


class Run:
    """Collects per-clip results and the run summary for one system."""

    def __init__(self, system, model, params, device):
        self.system = system
        self.dir = DATA / "outputs" / system
        self.dir.mkdir(parents=True, exist_ok=True)
        self.meta = {"system": system, "model": model, "params": params, "device": device,
                     "started": time.strftime("%Y-%m-%d %H:%M:%S"), "clips": 0,
                     "audio_sec": 0.0, "wall_sec": 0.0, "load_sec": None}

    def done(self, clip):
        return (self.dir / f"{clip['clip_id']}.json").exists()

    def save(self, clip, text, segments, words, audio_sec, wall_sec, context=None):
        rec = {"clip_id": clip["clip_id"], "system": self.system, "text": text.strip(),
               "segments": segments, "words": words, "audio_sec": round(audio_sec, 2),
               "wall_sec": round(wall_sec, 3), "context": context}
        (self.dir / f"{clip['clip_id']}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1))
        self.meta["clips"] += 1
        self.meta["audio_sec"] += audio_sec
        self.meta["wall_sec"] += wall_sec

    def finish(self, gpu_peak_mb=None):
        m = self.meta
        m["rtfx"] = round(m["audio_sec"] / m["wall_sec"], 1) if m["wall_sec"] else None
        m["gpu_peak_mb"] = gpu_peak_mb
        m["ram_peak_mb"] = round(peak_rss_mb())
        m["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
        prev = self.dir / "_run.json"
        if prev.exists() and m["clips"] == 0:
            return  # nothing new; keep the earlier run summary
        prev.write_text(json.dumps(m, indent=2))
        print(f"[{self.system}] {m['clips']} clips, {m['audio_sec']/60:.1f} min audio, "
              f"RTFx {m['rtfx']}, GPU peak {gpu_peak_mb} MB, RAM peak {m['ram_peak_mb']} MB", file=sys.stderr)


def log(msg):
    print(msg, file=sys.stderr, flush=True)
