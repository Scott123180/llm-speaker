#!/usr/bin/env python3
"""Build the gold-set: stratified speech excerpts + non-speech clips.

  uv run python eval/goldset.py select     # choose talks/windows -> eval/goldset/manifest.json
  uv run python eval/goldset.py download   # fetch talk audio -> data/audio/
  uv run python eval/goldset.py cut        # snap to silences, cut wavs, write drafts + legacy outputs

Speech excerpts are stratified by era, speaker, content type (koan / Q&A / other) and
audio difficulty (Whisper's own avg_logprob on the old transcript). Non-speech clips
(bells, silence, room noise) come from talk openings and long gaps in the old
transcripts, confirmed with Silero VAD; they measure hallucination.

Drafts in eval/goldset/drafts/ come from the *old* transcript (the baseline), so
correcting them doesn't anchor the gold set to any new candidate system.
Corrected references go in eval/goldset/refs/{clip_id}.txt (see eval/CONVENTIONS.md).
"""
import argparse
import json
import random
import re
import statistics
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "asr"))
sys.path.insert(0, str(REPO / "transcriber"))
from common import DATA, MANIFEST, SR, load_audio, log  # noqa: E402

GOLD = REPO / "eval" / "goldset"
OLD_JSON = Path("~/Documents/talks/all_json").expanduser()
METADATA = Path("~/Downloads/metadata_export__20261109-20_16.csv").expanduser()
AUDIO_URL = "https://d2f7aw4s8anu7j.cloudfront.net/audio/{id}.mp3"
LEGACY = "legacy-whisper-cli"

MAIN_SPEAKERS = {
    "John Daido Loori": "Daido", "Geoffrey Shugen Arnold": "Shugen", "Konrad Ryushin Marchaj": "Ryushin",
    "Jody Hojin Kimmel": "Hojin", "Bonnie Myotai Treace": "Myotai", "Ron Hogen Green": "Hogen",
    "Bear Gokan Bonebakker": "teachers-other", "Vanessa Zuisei Goddard": "teachers-other",
    "Danica Shoan Ankele": "teachers-other",
}
QA_RE = re.compile(r"mondo|dharma (encounter|combat)|q ?& ?a|question|interview|hossen", re.I)
HALLU_RE = re.compile(r"transcription by|thank you( for watching)?\.?$|subtitles|amara\.org|castingwords", re.I)


def talk_features(meta, old):
    segs = old["segments"]
    dur = segs[-1]["end"] if segs else 0
    speech = [s for s in segs if s["no_speech_prob"] < 0.5]
    lp = statistics.mean(s["avg_logprob"] for s in speech) if speech else -9
    date = (meta.get("Date") or "").strip()
    year = int(date[:4]) if date[:4].isdigit() else None
    title = (meta.get("Title") or "") + " " + (meta.get("Caption or Other Speaker") or "")[:200]
    return {
        "duration": dur, "logprob": lp, "year": year,
        "era": f"{year // 10 * 10}s" if year else "unknown",
        "speaker": (meta.get("Speaker") or "").strip() or "Other",
        "speaker_group": MAIN_SPEAKERS.get((meta.get("Speaker") or "").strip(), "seniors-guests-other"),
        "content": "qa" if QA_RE.search(title) else ("koan" if (meta.get("Koan Collection") or "").strip() else "other"),
        "title": (meta.get("Title") or "").strip(),
    }


def nonspeech_candidates(tid, f, segs, max_n=4):
    """Openings (bells / chant / hallucinated intro), long gaps, and spans where the
    old transcript looks hallucinated. Confirmed later with VAD in `cut`."""
    cands = []
    first_speech = next((x for x in segs if x["no_speech_prob"] < 0.5 and not HALLU_RE.search(x["text"].strip())
                         and x["temperature"] < 0.5), None)
    if first_speech and first_speech["start"] >= 25:
        cands.append((5.0, min(first_speech["start"] - 1, 35.0), "opening"))
    for x in segs:
        if HALLU_RE.search(x["text"].strip()) or (x["no_speech_prob"] > 0.7 and x["temperature"] >= 0.6):
            cands.append((x["start"], min(x["end"], x["start"] + 30), "old-hallucination"))
    for a, b in zip(segs, segs[1:]):
        if b["start"] - a["end"] >= 20:
            mid = (a["end"] + b["start"]) / 2
            cands.append((mid - 12.5, mid + 12.5, "gap"))
    return [{"clip_id": f"{tid}_n{int(s0):05d}", "kind": "nonspeech", "talk_id": tid,
             "start": round(s0, 2), "end": round(e0, 2), "window": why,
             "speaker_group": f["speaker_group"], "era": f["era"], "year": f["year"],
             "difficulty": f["difficulty"], "verified": False}
            for s0, e0, why in cands[:max_n] if e0 - s0 >= 8]


def select(args):
    from build_context import Glossary, load_dictionary, load_metadata

    rng = random.Random(args.seed)
    metadata = load_metadata(METADATA)
    gloss = Glossary(REPO / "glossary" / "glossary.csv", load_dictionary())
    talks = {}
    for p in sorted(OLD_JSON.glob("*.json")):
        tid = p.stem
        if tid not in metadata:
            continue
        old = json.loads(p.read_text())
        f = talk_features(metadata[tid], old)
        if f["duration"] >= 15 * 60 and f["year"]:
            talks[tid] = (f, old)
    log(f"{len(talks)} candidate talks (>=15 min, dated, with old transcript)")

    # difficulty terciles from Whisper's confidence on the old transcript
    lps = sorted(f["logprob"] for f, _ in talks.values())
    cut1, cut2 = lps[len(lps) // 3], lps[2 * len(lps) // 3]
    for f, _ in talks.values():
        f["difficulty"] = "hard" if f["logprob"] <= cut1 else ("medium" if f["logprob"] <= cut2 else "easy")

    quotas = {"difficulty": {"hard": 14, "medium": 10, "easy": 8},
              "content": {"qa": 7, "koan": 12, "other": 10},
              "era": {e: 5 for e in ("1980s", "1990s", "2000s", "2010s", "2020s")},
              "speaker_group": {g: 4 for g in set(MAIN_SPEAKERS.values()) | {"seniors-guests-other"}}}
    quotas["speaker_group"]["Daido"] = 8
    quotas["speaker_group"]["Shugen"] = 7
    counts = {k: Counter() for k in quotas}
    pool = list(talks)
    rng.shuffle(pool)
    chosen = []
    while len(chosen) < args.n and pool:
        def deficit(tid):
            f = talks[tid][0]
            return sum(max(0, quotas[k].get(f[k], 0) - counts[k][f[k]]) for k in quotas)
        best = max(pool, key=deficit)  # shuffled order breaks ties randomly
        pool.remove(best)
        chosen.append(best)
        for k in quotas:
            counts[k][talks[best][0][k]] += 1

    clips = []
    for n, tid in enumerate(chosen):
        f, old = talks[tid]
        segs = old["segments"]
        L = args.excerpt_sec
        if f["content"] == "qa":  # Q&A usually happens in the second half
            start = rng.uniform(0.55, 0.85) * (f["duration"] - L)
            how = "qa-second-half"
        else:
            starts = [s for s in range(180, int(f["duration"] - L - 60), 30)]
            if n % 2 == 0:  # half term-rich windows, half random
                def richness(s0):
                    text = " ".join(x["text"] for x in segs if s0 <= x["start"] < s0 + L)
                    return sum(1 for i, k, _ in gloss.find(text) if gloss.entries[i]["category"] not in ("title",))
                start, how = max(starts, key=richness), "term-rich"
            else:
                start, how = rng.choice(starts), "random"
        clips.append({"clip_id": f"{tid}_s{int(start):05d}", "kind": "speech", "talk_id": tid,
                      "start": round(start, 2), "end": round(start + L, 2), "window": how,
                      **{k: f[k] for k in ("title", "speaker", "speaker_group", "era", "year", "content", "difficulty")},
                      "old_logprob": round(f["logprob"], 3)})

        clips += nonspeech_candidates(tid, f, segs)

    # extra talks used only for non-speech clips, favouring ones where the old
    # transcript shows a hallucination
    rest = [t for t in talks if t not in chosen]
    rng.shuffle(rest)
    rest.sort(key=lambda t: -sum(1 for c in nonspeech_candidates(t, *talks[t][:1], talks[t][1]["segments"])
                                 if c["window"] == "old-hallucination"))
    added = 0
    for tid in rest:
        if added >= args.extra_nonspeech_talks:
            break
        cands = nonspeech_candidates(tid, talks[tid][0], talks[tid][1]["segments"])
        if cands:
            clips += cands
            added += 1

    GOLD.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps({"seed": args.seed, "excerpt_sec": args.excerpt_sec, "clips": clips}, indent=1))
    sp = [c for c in clips if c["kind"] == "speech"]
    log(f"selected {len(sp)} speech excerpts ({len(sp) * args.excerpt_sec / 3600:.1f} h) and "
        f"{len(clips) - len(sp)} non-speech candidates")
    for k in ("era", "speaker_group", "content", "difficulty"):
        log(f"  {k}: {dict(Counter(c[k] for c in sp))}")


def download(args):
    clips = json.loads(MANIFEST.read_text())["clips"]
    ids = sorted({c["talk_id"] for c in clips})
    out = DATA / "audio"
    out.mkdir(parents=True, exist_ok=True)

    def fetch(tid):
        p = out / f"{tid}.mp3"
        if p.exists() and p.stat().st_size > 0:
            return tid, "cached"
        r = requests.get(AUDIO_URL.format(id=tid), timeout=120)
        if r.status_code != 200:
            return tid, f"HTTP {r.status_code}"
        p.write_bytes(r.content)
        return tid, f"{len(r.content) / 1e6:.0f} MB"

    with ThreadPoolExecutor(4) as ex:
        for tid, status in ex.map(fetch, ids):
            log(f"  {tid}: {status}")


def vad_chunks(audio, offset):
    from faster_whisper.vad import VadOptions, get_speech_timestamps
    ts = get_speech_timestamps(audio, VadOptions(min_silence_duration_ms=300, speech_pad_ms=100))
    return [(offset + t["start"] / SR, offset + t["end"] / SR) for t in ts]


def snap(mp3, t, radius=15.0):
    """Move a cut point to the middle of the nearest pause within +-radius s."""
    a0 = max(0.0, t - radius)
    chunks = vad_chunks(load_audio(mp3, a0, t + radius), a0)
    gaps = [((x[1] + y[0]) / 2, y[0] - x[1]) for x, y in zip(chunks, chunks[1:]) if y[0] - x[1] >= 0.3]
    if not chunks:
        return t
    gaps.append((max(a0, chunks[0][0] - 0.2), 1.0))
    return min(gaps, key=lambda g: abs(g[0] - t) - min(g[1], 1.0))[0]


def cut(args):
    man = json.loads(MANIFEST.read_text())
    clips_dir = DATA / "goldset" / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    (GOLD / "drafts").mkdir(exist_ok=True)
    (GOLD / "refs").mkdir(exist_ok=True)
    legacy = DATA / "outputs" / LEGACY
    legacy.mkdir(parents=True, exist_ok=True)
    kept, per_talk_ns = [], Counter()
    for c in man["clips"]:
        mp3 = DATA / "audio" / f"{c['talk_id']}.mp3"
        if not mp3.exists():
            log(f"skip {c['clip_id']}: no audio")
            continue
        old = json.loads((OLD_JSON / f"{c['talk_id']}.json").read_text())
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    str(mp3)], capture_output=True, text=True).stdout or 0)
        if c["end"] > dur:  # old transcripts sometimes run past the end of the file
            log(f"skip {c['clip_id']}: ends at {c['end']:.0f}s but audio is {dur:.0f}s")
            continue
        if c["kind"] == "speech":
            if not c.get("snapped"):
                c["start"], c["end"] = round(snap(mp3, c["start"]), 2), round(snap(mp3, c["end"]), 2)
                c["snapped"] = True
        else:
            if per_talk_ns[c["talk_id"]] >= args.nonspeech_per_talk:
                continue
            a = load_audio(mp3, c["start"], c["end"])
            speech = sum(e - s for s, e in vad_chunks(a, 0))
            c["vad_speech_ratio"] = round(speech / max(1e-6, c["end"] - c["start"]), 3)
            if c["vad_speech_ratio"] > args.max_speech_ratio:
                continue
            per_talk_ns[c["talk_id"]] += 1
        wav = clips_dir / f"{c['clip_id']}.wav"
        if not wav.exists():
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{c['start']:.3f}",
                            "-t", f"{c['end'] - c['start']:.3f}", "-i", str(mp3), "-ac", "1", "-ar", str(SR), str(wav)],
                           check=True)
        # old transcript slice: segments whose midpoint falls inside the clip
        inside = [s for s in old["segments"] if c["start"] <= (s["start"] + s["end"]) / 2 < c["end"]]
        text = " ".join(s["text"].strip() for s in inside)
        if c["kind"] == "speech":
            (GOLD / "drafts" / f"{c['clip_id']}.txt").write_text(text + "\n")
        (legacy / f"{c['clip_id']}.json").write_text(json.dumps({
            "clip_id": c["clip_id"], "system": LEGACY, "text": text,
            "segments": [{"start": round(s["start"] - c["start"], 2), "end": round(s["end"] - c["start"], 2),
                          "text": s["text"].strip()} for s in inside],
            "words": None, "audio_sec": round(c["end"] - c["start"], 2), "wall_sec": None, "context": None}, indent=1))
        kept.append(c)
    man["clips"] = kept
    MANIFEST.write_text(json.dumps(man, indent=1))
    (legacy / "_run.json").write_text(json.dumps({
        "system": LEGACY, "model": "openai-whisper CLI turbo (existing transcripts)",
        "params": {"vad_filter": False, "condition_on_previous_text": True, "prompt": None},
        "device": "unknown", "rtfx": None, "note": "sliced from full-talk transcripts by segment midpoint"}, indent=2))
    sp = sum(1 for c in kept if c["kind"] == "speech")
    log(f"cut {sp} speech excerpts and {len(kept) - sp} non-speech clips; drafts in {GOLD / 'drafts'}")


def vad(args):
    """Silero VAD speech regions per clip -> data/goldset/vad/{clip_id}.json, so runners
    without a built-in VAD (Qwen, Parakeet) can be gated exactly like faster-whisper."""
    from common import load_manifest
    from faster_whisper.vad import VadOptions, get_speech_timestamps
    out = DATA / "goldset" / "vad"
    out.mkdir(parents=True, exist_ok=True)
    for c in load_manifest():
        a = load_audio(DATA / "goldset" / "clips" / f"{c['clip_id']}.wav")
        ts = get_speech_timestamps(a, VadOptions())  # faster-whisper defaults
        (out / f"{c['clip_id']}.json").write_text(json.dumps(
            [[round(t["start"] / SR, 2), round(t["end"] / SR, 2)] for t in ts]))
    log(f"wrote VAD regions to {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("vad")
    s = sub.add_parser("select")
    s.add_argument("--n", type=int, default=40)
    s.add_argument("--excerpt-sec", type=int, default=360)
    s.add_argument("--seed", type=int, default=7)
    s.add_argument("--extra-nonspeech-talks", type=int, default=30)
    sub.add_parser("download")
    c = sub.add_parser("cut")
    c.add_argument("--nonspeech-per-talk", type=int, default=1)
    c.add_argument("--max-speech-ratio", type=float, default=0.1)
    args = ap.parse_args()
    {"select": select, "download": download, "cut": cut, "vad": vad}[args.cmd](args)


if __name__ == "__main__":
    main()
