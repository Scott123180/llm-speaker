#!/usr/bin/env python3
"""Silver references: automatic (no human) references for the gold-set speech clips.

  uv run python eval/silver.py build    # data/silver/{clip}.json: reference + per-word confidence + flags
  uv run python eval/silver.py score    # leave-one-family-out WER of every system -> eval/results/silver.json

How a reference is made, per clip:
 1. Voters: one *plain* (no context) system per model family (whisper, parakeet, qwen,
    granite, vibevoice, nemotron). Plain variants keep a shared per-talk term list from
    pushing the same wrong term into several voters at once.
 2. Vote: align every voter to the medoid voter (word-level edit alignment) and take the
    majority word in each column, including majority insertions. Ties keep the medoid's word.
 3. Glossary: a known misheard form ("doksan") becomes its correct spelling ("dokusan")
    when that spelling appears in some system's output, the talk's context terms or the book.
 4. Book (clips from *Mountain Record of Zen Talks*): the reference is aligned to the edited
    chapter. A disputed word the book confirms is settled; a disputed word the book does not
    settle, or a glossary term where the book disagrees with every system, is flagged.
 5. Confidence per word: high (>=75% of voters agree, or the book confirms), medium (>=50%,
    or fixed by the glossary), low (otherwise). Low and disputed stretches become flags.

Limits: errors every system makes are invisible unless the book or glossary catches them,
and an edited book can't confirm fillers or false starts. Scoring rebuilds the reference
without the scored system's family, so no system grades itself.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

from rapidfuzz.distance import Levenshtein

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "asr"))
sys.path.insert(0, str(REPO / "transcriber"))
from build_context import Glossary, load_dictionary, resolve, tokens as gtokens  # noqa: E402
from common import CONTEXT_DIR, DATA, MANIFEST  # noqa: E402

OUT_DIR = DATA / "silver"
BOOK = DATA / "book"
OUTPUTS = DATA / "outputs"
# first available system per family is the voter (plain variants only)
VOTERS = {
    "whisper": ["whisper-large-v3", "whisper-turbo"],
    "parakeet": ["parakeet-ft-v1+vad90", "parakeet-ft-v1", "parakeet-v3"],
    "qwen": ["qwen3-asr-1.7b+vad", "qwen3-asr-1.7b"],
    "granite": ["granite-5.0-2b"],
    "vibevoice": ["vibevoice-asr"],
    "nemotron": ["nemotron-3.5-iq4_nl"],
}
HIGH, MEDIUM = 0.75, 0.5
# dropped before voting: some systems write fillers and others don't, and WER ignores them
FILLERS = {"uh", "um", "umm", "uhm", "hmm", "hm", "mm", "mhm", "er", "erm", "ah", "eh"}


def family(system):
    if system.startswith("legacy"):
        return "whisper"
    for f in VOTERS:
        if system.startswith(f):
            return f
    return system.split("-")[0]


def wnorm(word):
    n = "".join(gtokens(word))
    return "" if n in FILLERS else n


# ------------------------------------------------------------------ inputs

class Clip:
    """Everything the builder needs for one clip, loaded once."""

    def __init__(self, clip, outputs, gloss, chapters):
        self.c, self.id = clip, clip["clip_id"]
        self.dur = clip["end"] - clip["start"]
        self.outs = {s: o for s, o in outputs.items() if o is not None}
        self.toks = {s: hyp_tokens(o, self.dur) for s, o in self.outs.items()}
        ctx = CONTEXT_DIR / f"{clip['talk_id']}.json"
        self.context_terms = [t["form"] for t in json.loads(ctx.read_text())["terms"]] if ctx.exists() else []
        self.chapter = chapters.get(clip.get("book_chapter")) if clip.get("book_chapter") else None
        self.book = [{"n": wnorm(w), "d": w} for w in self.chapter.split()] if self.chapter else None
        if self.book:
            self.book = [b for b in self.book if b["n"]]
        self.gloss = gloss
        # token tuples present anywhere: evidence that a correct spelling is plausible here
        ev = " ".join([o.get("text", "") for o in self.outs.values()] + self.context_terms + [self.chapter or ""])
        self.evidence = gtokens(ev)

    def voters(self, exclude_family=None):
        out = []
        for fam, systems in VOTERS.items():
            if fam == exclude_family:
                continue
            s = next((s for s in systems if s in self.toks and self.toks[s]), None)
            if s:
                out.append(s)
        return out


def hyp_tokens(o, dur):
    out = []
    if o.get("words"):
        for w in o["words"]:
            for part in str(w["word"]).split():
                if wnorm(part):
                    out.append({"n": wnorm(part), "d": part, "t": round(float(w["start"]), 2)})
        if out:
            return out
    segs = o.get("segments") or ([{"start": 0.0, "end": dur, "text": o.get("text", "")}] if o.get("text") else [])
    for s in segs:
        parts = [p for p in str(s["text"]).split() if wnorm(p)]
        span = max(0.0, float(s["end"]) - float(s["start"]))
        for k, p in enumerate(parts):
            out.append({"n": wnorm(p), "d": p, "t": round(float(s["start"]) + span * k / max(1, len(parts)), 2)})
    return out


# ------------------------------------------------------------------ alignment and voting

def align(a, b):
    """Word alignment of token lists a, b -> [(i|None, j|None)] in order."""
    pairs = []
    for op in Levenshtein.opcodes([x["n"] for x in a], [x["n"] for x in b]):
        if op.tag in ("equal", "replace"):
            la, lb = op.src_end - op.src_start, op.dest_end - op.dest_start
            for k in range(max(la, lb)):
                pairs.append((op.src_start + k if k < la else None, op.dest_start + k if k < lb else None))
        elif op.tag == "delete":
            pairs += [(i, None) for i in range(op.src_start, op.src_end)]
        else:
            pairs += [(None, j) for j in range(op.dest_start, op.dest_end)]
    return pairs


def medoid(clip, voters):
    if len(voters) <= 2:
        return voters[0]
    cost = {s: sum(Levenshtein.distance([x["n"] for x in clip.toks[s]], [x["n"] for x in clip.toks[t]])
                   for t in voters if t != s) for s in voters}
    return min(voters, key=cost.get)


def vote(clip, voters):
    pivot = medoid(clip, voters)
    P = clip.toks[pivot]
    cols = [{pivot: P[i]} for i in range(len(P))]
    ins = [defaultdict(list) for _ in range(len(P) + 1)]
    for s in voters:
        if s == pivot:
            continue
        last = -1
        for i, j in align(P, clip.toks[s]):
            if i is not None:
                cols[i][s] = clip.toks[s][j] if j is not None else None
                last = i
            else:
                ins[last + 1][s].append(clip.toks[s][j])
    nv = len(voters)
    out = []

    def emit(tok, agree, cands, kind):
        out.append({"w": tok["d"], "n": tok["n"], "t": tok["t"], "agree": round(agree, 2), "how": kind,
                    "cands": cands if agree < 1 else None})

    for k in range(len(P) + 1):
        slot = ins[k]
        if len(slot) * 2 > nv:  # a majority of voters have extra words here
            seqs = Counter(tuple(t["n"] for t in v) for v in slot.values())
            seq, c = seqs.most_common(1)[0]
            src = next(s for s, v in slot.items() if tuple(t["n"] for t in v) == seq)
            cands = {s: " ".join(t["d"] for t in slot.get(s, [])) for s in voters}
            for t in slot[src]:
                emit(t, c / nv, cands, "insert")
        if k == len(P):
            break
        col = cols[k]
        cnt = Counter(v["n"] if v else None for v in col.values())  # pivot counted first: wins ties
        (best, c), *rest = cnt.most_common()
        cands = {s: (v["d"] if v else "") for s, v in col.items()}
        tie = bool(rest) and rest[0][1] == c
        if best is None:
            heard = [v for v in col.values() if v]
            # remember a dropped word for review only if many voters heard it or it is a known term
            if heard and (len(heard) / nv >= 0.4 or any(is_term(clip, v["d"]) for v in heard)):
                out.append({"w": "", "n": "", "t": P[k]["t"], "agree": round(c / nv, 2), "how": "drop",
                            "cands": cands})
            continue
        if c < nv and not is_term(clip, next(v for v in col.values() if v and v["n"] == best)["d"]):
            terms = {v["n"]: v for v in col.values() if v and is_term(clip, v["d"])}
            if len(terms) == 1 and (tie or c * 2 <= nv):  # glossary breaks a tie / weak majority
                tok = next(iter(terms.values()))
                emit(tok, sum(1 for v in col.values() if v and v["n"] == tok["n"]) / nv, cands, "glossary-tiebreak")
                continue
        tok = next(v for v in col.values() if v and v["n"] == best)
        emit(tok, c / nv, cands, "tie" if tie else "vote")
    return pivot, out


# ------------------------------------------------------------------ glossary and book passes

def is_term(clip, word):
    """Is this word (possessive stripped) a correct glossary spelling of a name/term?"""
    key = gtokens(re.sub(r"['’]s\b", "", word))
    return bool(key) and any(kind == "valid" and not plain for _, kind, _, plain in clip.gloss.index.get(key, []))


def glossary_pass(clip, toks):
    g, i = clip.gloss, 0
    while i < len(toks):
        hit = None
        for n in range(min(g.max_len, len(toks) - i), 0, -1):
            words = [t for t in toks[i:i + n] if t["n"]]
            if not words:
                continue
            for e, kind, form, plain in g.index.get(gtokens(" ".join(t["w"] for t in words)), []):
                if kind == "misheard" and not plain:
                    hit = (n, g.entries[e], form)
                    break
            if hit:
                break
        if hit:
            n, entry, form = hit
            right = resolve(entry, "misheard", form)
            rt = gtokens(right)
            if rt and any(clip.evidence[k:k + len(rt)] == rt for k in range(len(clip.evidence))):
                first = toks[i]
                tail = re.search(r"[^\w']+$", toks[i + n - 1]["w"])  # keep "Yakujo." -> "Hyakujo."
                fixed = [{"w": w, "n": wnorm(w), "t": first["t"], "agree": first["agree"], "how": "glossary",
                          "was": " ".join(t["w"] for t in toks[i:i + n]), "cands": first.get("cands")}
                         for w in right.split()]
                if tail:
                    fixed[-1]["w"] += tail.group(0)
                toks[i:i + n] = fixed
                i += len(fixed)
                continue
        i += 1
    return toks


def book_pass(clip, toks):
    """Align to the chapter; settle disputed words the book confirms; flag the rest."""
    words = [t for t in toks if t["n"]]
    if not clip.book or not words:
        return toks, None
    bn = [b["n"] for b in clip.book]
    pos = defaultdict(list)
    for j in range(len(bn) - 4):
        pos[tuple(bn[j:j + 5])].append(j)
    hits = sorted(j for i in range(len(words) - 4) for j in pos.get(tuple(t["n"] for t in words[i:i + 5]), []))
    if len(hits) < 3:
        return toks, {"coverage": 0.0}
    lo, hi = hits[len(hits) // 10], hits[-1 - len(hits) // 10]
    region = clip.book[max(0, lo - 150): hi + 150]
    pairs = align(words, region)
    equal = sum(1 for i, j in pairs if i is not None and j is not None and words[i]["n"] == region[j]["n"])
    terms = {gtokens(f) for e in clip.gloss.entries for f in e["valid"]}
    for i, j in pairs:
        if i is None:
            continue
        t, b = words[i], (region[j] if j is not None else None)
        if j is not None:
            t["bj"] = j  # position in the book region (viewer shows the passage)
        cands = t.get("cands") or {}
        cand_n = {wnorm(v) for v in cands.values() if v}
        if t["agree"] < 1 or t["how"] == "tie":
            if b and b["n"] == t["n"]:
                t["book"] = "confirms"
            elif b and b["n"] in cand_n:
                alt = next(v for v in cands.values() if v and wnorm(v) == b["n"])
                t.update({"was": t["w"], "w": alt, "n": b["n"], "book": "settles", "how": "book"})
            else:
                t["book"] = "unresolved"
        elif b and b["n"] != t["n"] and ((b["n"],) in terms or (t["n"],) in terms):
            t["book"] = "differs"  # all systems agree, the book has another term here
            t["book_word"] = b["d"]
        elif b and b["n"] == t["n"]:
            t["book"] = "confirms"
    return toks, {"coverage": round(equal / max(1, len(words)), 3), "chapter": clip.c.get("book_chapter"),
                  "region": [b["d"] for b in region]}


def confidence(t):
    if t["how"] == "single":  # one voter: nothing to corroborate it
        return "medium" if t.get("book") != "unresolved" else "low"
    if t.get("book") in ("confirms", "settles"):
        return "high"
    if t.get("book") in ("unresolved", "differs"):
        return "low" if t["agree"] < HIGH or t.get("book") == "differs" else "medium"
    if t["how"] in ("glossary", "glossary-tiebreak"):
        return "medium"
    if t["how"] == "tie" or t["agree"] < MEDIUM:
        return "low"
    return "high" if t["agree"] >= HIGH else "medium"


def build(clip, exclude_family=None):
    voters = clip.voters(exclude_family)
    if not voters:
        return None
    if len(voters) == 1:
        toks = [dict(t, agree=1.0, how="single", cands=None, w=t["d"]) for t in clip.toks[voters[0]]]
        pivot = voters[0]
    else:
        pivot, toks = vote(clip, voters)
    toks = glossary_pass(clip, toks)
    toks, book = book_pass(clip, toks)
    for t in toks:
        t["conf"] = confidence(t)
    words = [t for t in toks if t["n"]]
    return {"clip_id": clip.id, "voters": voters, "pivot": pivot, "excluded_family": exclude_family,
            "text": " ".join(t["w"] for t in words), "tokens": toks, "book": book,
            "stats": {"words": len(words), **{k: sum(1 for t in words if t["conf"] == k)
                                               for k in ("high", "medium", "low")},
                      "dropped_disputes": sum(1 for t in toks if not t["n"])}}


def regions(ref, gap=2):
    """Group low-confidence / book-flagged words into regions for review."""
    out, cur = [], None
    for i, t in enumerate(ref["tokens"]):
        flagged = t["conf"] == "low" or t.get("book") in ("unresolved", "differs") or not t["n"]
        if flagged:
            if cur and i - cur["end"] <= gap:
                cur["end"] = i
            else:
                cur = {"start": i, "end": i}
                out.append(cur)
    for r in out:
        span = ref["tokens"][r["start"]:r["end"] + 1]
        r["t"] = span[0]["t"]
        r["kinds"] = sorted({("book-" + t["book"]) if t.get("book") in ("unresolved", "differs") else
                             ("dropped" if not t["n"] else t["how"]) for t in span})
        r["text"] = " ".join(t["w"] for t in span if t["n"])
    return out


# ------------------------------------------------------------------ loading

def load_clips(manifest=None, systems=None):
    gloss = Glossary(REPO / "glossary" / "glossary.csv", load_dictionary())
    chapters = {}
    if (BOOK / "chapters.json").exists():
        chapters = {c["title"]: c["text"] for c in json.loads((BOOK / "chapters.json").read_text())}
    if manifest is None:
        manifest = [c for c in json.loads(MANIFEST.read_text())["clips"] if not c.get("exclude")]
    if systems is None:
        systems = {}
        for d in sorted(p for p in OUTPUTS.iterdir() if p.is_dir()):
            systems[d.name] = {p.stem: json.loads(p.read_text()) for p in d.glob("*.json")
                               if not p.name.startswith("_")}
    clips = []
    for c in manifest:
        if c["kind"] != "speech":
            continue
        outs = {s: o.get(c["clip_id"]) for s, o in systems.items()}
        clips.append(Clip(c, outs, gloss, chapters))
    return clips


def cmd_build(a):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tot = Counter()
    for clip in load_clips():
        ref = build(clip)
        if not ref:
            continue
        ref["regions"] = regions(ref)
        (OUT_DIR / f"{clip.id}.json").write_text(json.dumps(ref, ensure_ascii=False))
        tot.update(ref["stats"])
        tot["clips"] += 1
        tot["regions"] += len(ref["regions"])
    w = max(1, tot["words"])
    print(f"{tot['clips']} silver references in {OUT_DIR}: {tot['words']} words; "
          f"high {100 * tot['high'] / w:.0f}%, medium {100 * tot['medium'] / w:.0f}%, low {100 * tot['low'] / w:.0f}%; "
          f"{tot['regions']} flagged regions")


def score(manifest=None, systems=None, normalize=None):
    """Leave-one-family-out silver WER per system. Returns {system: {...}}."""
    import jiwer
    if normalize is None:
        from whisper_normalizer.english import EnglishTextNormalizer
        _n = EnglishTextNormalizer()

        def normalize(s):
            return re.sub(r"\s+", " ", _n(s or "")).strip()
    clips = load_clips(manifest, {s: d["outs"] for s, d in systems.items()} if systems else None)

    @lru_cache(maxsize=None)
    def ref_for(i, fam):
        r = build(clips[i], fam)
        return (normalize(r["text"]), len(r["voters"]), r["clip_id"]) if r else None

    res = defaultdict(lambda: defaultdict(lambda: {"S": 0, "D": 0, "I": 0, "N": 0, "clips": 0, "voters": []}))
    all_systems = sorted({s for c in clips for s in c.outs})
    for s in all_systems:
        fam = family(s)
        for i, c in enumerate(clips):
            if s not in c.outs:
                continue
            r = ref_for(i, fam)
            if not r or not r[0]:
                continue
            ref, nv, _ = r
            hyp = normalize(c.outs[s].get("text", ""))
            o = jiwer.process_words(ref, hyp or "<empty>")
            for key in ("all", c.c.get("set", "stratified")):
                b = res[s][key]
                b["S"] += o.substitutions
                b["D"] += o.deletions
                b["I"] += o.insertions
                b["N"] += len(ref.split())
                b["clips"] += 1
                b["voters"].append(nv)
    out = {}
    for s, by in res.items():
        out[s] = {k: {"wer": (b["S"] + b["D"] + b["I"]) / b["N"] if b["N"] else None, "clips": b["clips"],
                      "sub": b["S"] / max(1, b["N"]), "del": b["D"] / max(1, b["N"]), "ins": b["I"] / max(1, b["N"]),
                      "voters": round(sum(b["voters"]) / len(b["voters"]), 1)} for k, b in by.items()}
    return out


def cmd_score(a):
    res = score()
    p = REPO / "eval" / "results" / "silver.json"
    p.write_text(json.dumps(res, indent=1))
    print(f"{'system':32s} {'silver WER':>10s} {'stratified':>11s} {'book':>7s} {'voters':>7s}")
    for s, r in sorted(res.items(), key=lambda x: x[1]["all"]["wer"] or 9):
        f = lambda k: f"{100 * r[k]['wer']:.1f}%" if k in r and r[k]["wer"] is not None else "-"
        print(f"{s:32s} {f('all'):>10s} {f('stratified'):>11s} {f('book'):>7s} {r['all']['voters']:>7}")
    print(f"-> {p}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build").set_defaults(fn=cmd_build)
    sub.add_parser("score").set_defaults(fn=cmd_score)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
