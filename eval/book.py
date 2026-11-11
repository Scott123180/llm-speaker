#!/usr/bin/env python3
"""Talks from *Mountain Record of Zen Talks* (John Daido Loori, 1988) as an independent
reference: an edited, human-made text for 12 recordings from 1981-85, the hardest audio era.

  uv run python eval/book.py extract BOOK.epub   # chapters + glossary -> data/book/ (git-ignored)
  uv run python eval/book.py match               # chapter <-> talk by shared 5-word phrases
  uv run python eval/book.py add                 # 6-min window per talk where the book is densest
                                                 #   -> manifest ("set": "book"), audio, wav, draft, legacy

The book is edited for print (fillers removed, sentences reworked), so it is not a verbatim
reference; eval/silver.py uses it to settle disagreements between systems and to spell
names and terms. The book text stays in data/book/ and is never committed or published.
"""
import argparse
import html
import json
import re
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "asr"))
sys.path.insert(0, str(REPO / "eval"))
from common import DATA, MANIFEST, SR, log  # noqa: E402

BOOK = DATA / "book"
TRANSCRIPTS = Path("~/Documents/talks/all").expanduser()
OLD_JSON = Path("~/Documents/talks/all_json").expanduser()
N = 5
# contents page of the 1988 Shambhala edition: (chapter, first page); "END" = glossary page
TOC = [("The Search", 7), ("The Barrier Gate", 15), ("An Introduction to Zazen", 25),
       ("A Talk on The Heart Sutra", 31), ("Are You Awake?", 41), ("Ceaseless Practice", 47),
       ("Mountains and Rivers", 61), ("The Sound of Rain", 69), ("The Goddess's Neither Male Nor Female", 81),
       ("Like a Dream", 93), ("Accomplishing Buddha's Great Wisdom", 103), ("Transmission of the Light", 111),
       ("Painting Spring", 125), ("Neither Difficult Nor Easy", 135), ("Medicine and Sickness Cure Each Other", 147),
       ("Picking and Choosing, Coming and Going", 157), ("The Sacred Teachings of Work", 167),
       ("The Art of Seeing", 175), ("Zen Mind, Well Mind", 183), ("Sages and Warriors Living Together", 193),
       ("END", 203)]


def toks(s):
    return re.findall(r"[a-z]+", s.lower())


def grams(words):
    return {tuple(words[i:i + N]) for i in range(len(words) - N + 1)}


def extract(args):
    """Read page files straight from the epub zip (never extracted to disk)."""
    pages = {}
    with zipfile.ZipFile(args.epub) as z:
        for name in z.namelist():
            m = re.search(r"page_(\d+)\.x?html?$|page_(\d+)\.xml$", name)
            if m:
                raw = z.read(name).decode("utf-8", errors="replace")
                raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S)
                txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()
                pages[int(m.group(1) or m.group(2))] = re.sub(r"^Page \d+ ", "", txt)
    chapters = []
    for (title, a), (_, b) in zip(TOC, TOC[1:]):
        text = " ".join(pages.get(p, "") for p in range(a, b))
        chapters.append({"title": title, "pages": [a, b - 1], "text": text})
    gloss = " ".join(pages.get(p, "") for p in range(203, 210))
    BOOK.mkdir(parents=True, exist_ok=True)
    (BOOK / "chapters.json").write_text(json.dumps(chapters, ensure_ascii=False, indent=1))
    (BOOK / "glossary.txt").write_text(gloss)
    log(f"{len(chapters)} chapters, {sum(len(c['text'].split()) for c in chapters)} words -> {BOOK}")


def match(args):
    """Each chapter vs every legacy transcript; accept a talk when it shares far more
    5-word phrases than any other and predates the book (1988)."""
    from goldset import METADATA  # noqa
    sys.path.insert(0, str(REPO / "transcriber"))
    from build_context import load_metadata
    meta = load_metadata(METADATA)
    chapters = json.loads((BOOK / "chapters.json").read_text())
    cg = [grams(toks(c["text"])) for c in chapters]
    index = defaultdict(set)
    for i, g in enumerate(cg):
        for x in g:
            index[x].add(i)
    hits = defaultdict(Counter)
    for f in sorted(TRANSCRIPTS.glob("*.txt")):
        for x in grams(toks(f.read_text(errors="replace"))) & index.keys():
            for i in index[x]:
                hits[i][f.stem] += 1
    out = []
    for i, c in enumerate(chapters):
        top = hits[i].most_common(3)
        if not top:
            continue
        (tid, n1), n2 = top[0], (top[1][1] if len(top) > 1 else 0)
        share, ratio = n1 / max(1, len(cg[i])), n1 / max(1, n2)
        date = (meta.get(tid, {}).get("Date") or "").strip()
        year = int(date[:4]) if date[:4].isdigit() else None
        ok = share >= 0.10 and ratio >= 1.9 and (year is None or year <= 1988)
        out.append({"chapter": c["title"], "talk_id": tid, "share": round(share, 3), "ratio": round(ratio, 2),
                    "date": date, "title": meta.get(tid, {}).get("Title"), "accepted": ok,
                    "runner_up": top[1][0] if len(top) > 1 else None})
        log(f"  {'OK ' if ok else '-- '} {c['title'][:36]:36s} {tid} {100 * share:4.1f}% x{ratio:.1f} {date[:10]}")
    (BOOK / "matches.json").write_text(json.dumps(out, indent=1))
    log(f"{sum(m['accepted'] for m in out)} accepted matches -> {BOOK / 'matches.json'}")


def best_window(segs, cgrams, length):
    """Start time of the `length`-second window whose legacy text shares most book phrases."""
    best, best_t = -1, 0.0
    for i, s in enumerate(segs):
        inside = [x["text"] for x in segs[i:] if x["end"] <= s["start"] + length]
        n = len(grams(toks(" ".join(inside))) & cgrams)  # phrases may span segment boundaries
        if n > best:
            best, best_t = n, s["start"]
    return best_t, best


def add(args):
    from goldset import AUDIO_URL, LEGACY, snap
    import requests
    sys.path.insert(0, str(REPO / "transcriber"))
    from build_context import load_metadata
    from goldset import METADATA
    meta = load_metadata(METADATA)
    man = json.loads(MANIFEST.read_text())
    have = {c["clip_id"] for c in man["clips"]}
    chapters = {c["title"]: c for c in json.loads((BOOK / "chapters.json").read_text())}
    speech = [c for c in man["clips"] if c["kind"] == "speech" and "old_logprob" in c]
    added = 0
    for m in json.loads((BOOK / "matches.json").read_text()):
        if not m["accepted"]:
            continue
        tid = m["talk_id"]
        old = json.loads((OLD_JSON / f"{tid}.json").read_text())
        segs = old["segments"]
        cg = grams(toks(chapters[m["chapter"]]["text"]))
        t0, nhit = best_window(segs, cg, args.excerpt_sec)
        mp3 = DATA / "audio" / f"{tid}.mp3"
        if not mp3.exists():
            r = requests.get(AUDIO_URL.format(id=tid), timeout=300)
            r.raise_for_status()
            mp3.parent.mkdir(parents=True, exist_ok=True)
            mp3.write_bytes(r.content)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    str(mp3)], capture_output=True, text=True).stdout or 0)
        start = round(snap(mp3, max(0.0, t0)), 2)
        end = round(snap(mp3, min(dur - 1, start + args.excerpt_sec)), 2)
        cid = f"{tid}_b{int(start):05d}"
        if cid in have:
            continue
        wav = DATA / "goldset" / "clips" / f"{cid}.wav"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}",
                        "-i", str(mp3), "-ac", "1", "-ar", str(SR), str(wav)], check=True)
        inside = [s for s in segs if start <= (s["start"] + s["end"]) / 2 < end]
        text = " ".join(s["text"].strip() for s in inside)
        (REPO / "eval" / "goldset" / "drafts" / f"{cid}.txt").write_text(text + "\n")
        (DATA / "outputs" / LEGACY / f"{cid}.json").write_text(json.dumps({
            "clip_id": cid, "system": LEGACY, "text": text,
            "segments": [{"start": round(s["start"] - start, 2), "end": round(s["end"] - start, 2),
                          "text": s["text"].strip()} for s in inside],
            "words": None, "audio_sec": round(end - start, 2), "wall_sec": None, "context": None}, indent=1))
        lp = [s["avg_logprob"] for s in inside if s.get("no_speech_prob", 0) < 0.5]
        lp = sum(lp) / len(lp) if lp else -9
        # difficulty on the same scale as the stratified set: nearest existing clip's label
        diff = min(speech, key=lambda c: abs(c["old_logprob"] - lp))["difficulty"] if speech else "unknown"
        date = (meta.get(tid, {}).get("Date") or m["date"] or "").strip()
        man["clips"].append({
            "clip_id": cid, "kind": "speech", "set": "book", "talk_id": tid, "start": start, "end": end,
            "window": "book", "title": meta.get(tid, {}).get("Title") or m["title"],
            "speaker": "John Daido Loori", "speaker_group": "Daido", "era": "1980s",
            "year": int(date[:4]) if date[:4].isdigit() else None, "content": "book",
            "difficulty": diff, "old_logprob": round(lp, 3), "snapped": True,
            "book_chapter": m["chapter"], "book_phrase_hits": nhit})
        added += 1
        log(f"  {cid}: {m['chapter']} ({nhit} shared phrases in window)")
    MANIFEST.write_text(json.dumps(man, indent=1, ensure_ascii=False) + "\n")
    log(f"added {added} book clips; now run: uv run python eval/goldset.py vad")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("extract")
    s.add_argument("epub")
    sub.add_parser("match")
    s = sub.add_parser("add")
    s.add_argument("--excerpt-sec", type=float, default=360)
    a = ap.parse_args()
    {"extract": extract, "match": match, "add": add}[a.cmd](a)


if __name__ == "__main__":
    main()
