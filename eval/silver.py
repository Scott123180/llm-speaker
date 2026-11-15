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
# function words: family reliability is measured separately for these and for content words
STOP = set("""a an the and or but if so as of at by for from in into on onto to up with about
than then that this these those there here it its it's i me my we us our you your he him his she her
they them their what which who whom whose when where why how is am are was were be been being do does
did have has had will would shall should can could may might must not no yes all any some just very
too also only even well oh now one""".split())
JUDGE = REPO / "eval" / "goldset" / "judge.json"


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
        self.rel = {}  # (family, "content"|"function") -> share of book-settled disputes it got right
        self.judge = []  # reviewed decisions for flagged spans (eval/goldset/judge.json)

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
        if tie:
            best, why = tie_break(clip, col, [n for n, k in cnt.items() if k == c and n is not None])
        tok = next(v for v in col.values() if v and v["n"] == best)
        emit(tok, c / nv, cands, "tie" if tie else "vote")
        if tie:
            out[-1]["pick"] = why
    return pivot, out


def tie_break(clip, col, tied):
    """Pick among equally voted words: a glossary term (or a known mishearing of one) first,
    then a real word over a non-word ("oxherding" over "oxerting"), then the voters whose
    family is most often right on this kind of word (measured against the book)."""
    if len(tied) == 1:
        return tied[0], "only"
    disp = {n: next(v["d"] for v in col.values() if v and v["n"] == n) for n in tied}
    cls = "function" if any(n in STOP for n in tied) else "content"
    backers = {n: [s for s, v in col.items() if v and v["n"] == n] for n in tied}

    def key(n):
        return (is_term(clip, disp[n]) or is_misheard(clip, disp[n]), known_word(clip, disp[n]),
                sum(clip.rel.get((family(s), cls), 0.5) for s in backers[n]))

    ranked = sorted(tied, key=key, reverse=True)  # stable: the pivot's word stays first on equal keys
    a, b = key(ranked[0]), key(ranked[1])
    why = "glossary" if a[0] != b[0] else "word" if a[1] != b[1] else "family" if a[2] != b[2] else "pivot"
    return ranked[0], why


# ------------------------------------------------------------------ glossary and book passes

def is_term(clip, word):
    """Is this word (possessive stripped) a correct glossary spelling of a name/term?"""
    key = gtokens(re.sub(r"['’]s\b", "", word))
    return bool(key) and any(kind == "valid" and not plain for _, kind, _, plain in clip.gloss.index.get(key, []))


def is_misheard(clip, word):
    key = gtokens(re.sub(r"['’]s\b", "", word))
    return bool(key) and any(kind == "misheard" and not plain for _, kind, _, plain in clip.gloss.index.get(key, []))


@lru_cache(maxsize=None)
def _dictionary():
    return frozenset(load_dictionary())


def known_word(clip, word):
    """A dictionary word, a glossary term, a number, or a compound of two dictionary words."""
    w = re.sub(r"['’]s$", "", re.sub(r"^\W+|\W+$", "", word.lower()))
    D = _dictionary()

    def ok(p):
        return (p.isdigit() or p in D or is_term(clip, p)
                or any(p[:k] in D and p[k:] in D for k in range(2, len(p) - 1)))
    parts = [p for p in re.split(r"[-–]", w) if p]
    return bool(parts) and all(ok(p) for p in parts)


def glossary_pass(clip, toks):
    g, i = clip.gloss, 0
    while i < len(toks):
        hit = None
        for n in range(min(g.max_len, len(toks) - i), 0, -1):
            words = [t for t in toks[i:i + n] if t["n"]]
            if not words:
                continue
            text = " ".join(t["w"] for t in words)
            keys = [(gtokens(text), False)]
            if re.search(r"['’]s\W*$", text):  # "Yunmin's" -> look up "Yunmin", keep the 's
                keys.append((gtokens(re.sub(r"['’]s(\W*)$", r"\1", text)), True))
            for key, poss in keys:
                for e, kind, form, plain in g.index.get(key, []):
                    if kind == "misheard" and not plain:
                        hit = (n, g.entries[e], form, poss)
                        break
                if hit:
                    break
            if hit:
                break
        if hit:
            n, entry, form, poss = hit
            right = resolve(entry, "misheard", form)
            rt = gtokens(right)
            if rt and any(clip.evidence[k:k + len(rt)] == rt for k in range(len(clip.evidence))):
                first = toks[i]
                # keep trailing punctuation ("Yakujo." -> "Hyakujo.") and possessives ("Yunmen's")
                tail = re.search(r"['’]s\W*$" if poss else r"[^\w']+$", toks[i + n - 1]["w"])
                fixed = [{"w": w, "n": wnorm(w), "t": first["t"], "agree": first["agree"], "how": "glossary",
                          "was": " ".join(t["w"] for t in toks[i:i + n]), "cands": first.get("cands")}
                         for w in right.split()]
                if tail:
                    fixed[-1]["w"] += tail.group(0)
                # a split voter can leave the end of the term behind ("Tikkadhan Han" -> "... Hanh Han")
                nxt = toks[i + n] if i + n < len(toks) else None
                if (nxt and nxt["n"] and len(nxt["n"]) >= 3 and nxt["agree"] < 1
                        and Levenshtein.normalized_similarity(nxt["n"], fixed[-1]["n"]) >= 0.7):
                    n += 1
                toks[i:i + n] = fixed
                i += len(fixed)
                continue
        i += 1
    return toks


def book_align(clip, words):
    """Align reference words to the matching stretch of the chapter -> (pairs, region) or None."""
    if not clip.book or not words:
        return None
    bn = [b["n"] for b in clip.book]
    pos = defaultdict(list)
    for j in range(len(bn) - 4):
        pos[tuple(bn[j:j + 5])].append(j)
    hits = sorted(j for i in range(len(words) - 4) for j in pos.get(tuple(t["n"] for t in words[i:i + 5]), []))
    if len(hits) < 3:
        return None
    lo, hi = hits[len(hits) // 10], hits[-1 - len(hits) // 10]
    region = clip.book[max(0, lo - 150): hi + 150]
    return align(words, region), region


def family_reliability(clips):
    """Per family and word class, how often its word is the book's in disputes the book settles."""
    tally = defaultdict(lambda: [1, 2])  # Laplace prior: 1 of 2
    for clip in clips:
        voters = clip.voters()
        if not clip.book or len(voters) < 2:
            continue
        _, toks = vote(clip, voters)
        words = [t for t in toks if t["n"] and t["how"] != "insert"]
        ba = book_align(clip, words)
        if not ba:
            continue
        pairs, region = ba
        for i, j in pairs:
            if i is None or j is None or words[i]["agree"] >= 1:
                continue
            b = region[j]["n"]
            cands = words[i]["cands"] or {}
            if b not in {wnorm(v) for v in cands.values() if v}:
                continue  # the book doesn't settle this one (editing, or everyone is wrong)
            cls = "function" if b in STOP else "content"
            for s, v in cands.items():
                tally[(family(s), cls)][0] += wnorm(v) == b if v else 0
                tally[(family(s), cls)][1] += 1
    return {k: round(r / n, 3) for k, (r, n) in tally.items()}


def close(a, b):
    return len(a) >= 4 and len(b) >= 4 and Levenshtein.normalized_similarity(a, b) >= 0.6


def book_pass(clip, toks):
    """Align to the chapter; settle disputed words the book confirms; flag the rest."""
    words = [t for t in toks if t["n"]]
    ba = book_align(clip, words)
    if not ba:
        return toks, ({"coverage": 0.0} if clip.book and words else None)
    pairs, region = ba
    equal = sum(1 for i, j in pairs if i is not None and j is not None and words[i]["n"] == region[j]["n"])
    terms = {gtokens(f) for e in clip.gloss.entries for f in e["valid"]}
    at = {i: j for i, j in pairs if i is not None}
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
            elif (b and any(close(b["n"], c) for c in cand_n | {t["n"]})
                  and anchored(words, region, at, i)
                  and not (any(is_term(clip, v) for v in cands.values() if v) and not is_term(clip, b["d"]))):
                # every voter garbled a word the book has ("sequent"/"sequined" -> "sequential")
                tail = re.search(r"[^\w']+$", t["w"])
                w = re.sub(r"^\W+|\W+$", "", b["d"]) + (tail.group(0) if tail else "")
                t.update({"was": t["w"], "w": w, "n": b["n"], "book": "adopted", "how": "book"})
            else:
                t["book"] = "unresolved"
        elif b and b["n"] != t["n"] and ((b["n"],) in terms or (t["n"],) in terms):
            t["book"] = "differs"  # all systems agree, the book has another term here
            t["book_word"] = b["d"]
        elif b and b["n"] == t["n"]:
            t["book"] = "confirms"
    return toks, {"coverage": round(equal / max(1, len(words)), 3), "chapter": clip.c.get("book_chapter"),
                  "region": [b["d"] for b in region]}


def anchored(words, region, at, i):
    """Both neighbours match the book exactly, so the alignment at i is trustworthy."""
    def same(k):
        return 0 <= k < len(words) and at.get(k) is not None and words[k]["n"] == region[at[k]]["n"]
    return same(i - 1) and same(i + 1)


def confidence(t):
    if t["how"] == "judge":
        return t["judge_conf"]
    if t["how"] == "single":  # one voter: nothing to corroborate it
        return "medium" if t.get("book") != "unresolved" else "low"
    if t.get("book") in ("confirms", "settles"):
        return "high"
    if t.get("book") == "adopted":
        return "medium"  # the book is edited, but every voter's word was a near miss of it
    if t.get("book") == "unresolved":
        return "low" if t["agree"] < MEDIUM or t["how"] == "tie" else "medium"
    # "differs" (all voters agree, the book has another term) is information only: usually editing
    if t["how"] in ("glossary", "glossary-tiebreak"):
        return "medium"
    if t["how"] == "tie" or t["agree"] < MEDIUM:
        return "low"
    return "high" if t["agree"] >= HIGH else "medium"


def judge_pass(clip, toks):
    """Apply reviewed decisions (eval/goldset/judge.json) for flagged spans. A decision names the
    span by the words around it, so it still applies when a leave-one-family-out rebuild changes
    the words inside. "unclear" decisions change nothing (the span stays flagged for a listener)."""
    for d in clip.judge:
        if d["verdict"] == "unclear":
            continue
        W = [k for k, t in enumerate(toks) if t["n"]]
        n = [toks[k]["n"] for k in W]
        bef, frm, aft = ([x for x in map(wnorm, d[f].split()) if x] for f in ("before", "from", "after"))
        best = None
        for p in range(len(bef), len(W) + 1):
            if n[p - len(bef):p] != bef:
                continue
            qs = range(p, min(len(W), p + len(frm) + 4) + 1) if aft else [p + len(frm)]
            for q in qs:
                if q > len(W) or n[q:q + len(aft)] != aft:
                    continue
                t0 = toks[W[p]]["t"] if p < len(W) else toks[W[-1]]["t"]
                if abs(t0 - d["t"]) > 15:
                    continue
                key = (n[p:q] == frm, -abs(t0 - d["t"]))
                if best is None or key > best[0]:
                    best = (key, p, q)
        if best is None:
            continue
        _, p, q = best
        a = W[p - 1] + 1 if p else 0
        b = W[q] if q < len(W) else len(toks)
        first = toks[a] if a < len(toks) else toks[-1]
        was = " ".join(t["w"] for t in toks[a:b] if t["n"])
        toks[a:b] = [{"w": w, "n": wnorm(w), "t": first["t"], "agree": first["agree"], "how": "judge",
                      "judge_conf": "medium", "verdict": d["verdict"], "was": was, "why": d.get("why", ""),
                      "cands": first.get("cands")} for w in d["to"].split() if wnorm(w)]
    return toks


def build(clip, exclude_family=None, judge=True):
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
    if judge:
        toks = judge_pass(clip, toks)
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
        flagged = t["conf"] == "low" or not t["n"]
        if flagged:
            if cur and i - cur["end"] <= gap:
                cur["end"] = i
            else:
                cur = {"start": i, "end": i}
                out.append(cur)
    for r in out:
        span = ref["tokens"][r["start"]:r["end"] + 1]
        r["t"] = span[0]["t"]
        r["kinds"] = sorted({("book-" + t["book"]) if t.get("book") == "unresolved" else
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
    rel = family_reliability(clips)
    judged = load_judge()
    for c in clips:
        c.rel, c.judge = rel, judged.get(c.id, [])
    return clips


def load_judge():
    """Decisions by clip; each "to" may only use words some system, the glossary or the book has."""
    if not JUDGE.exists():
        return {}
    by = defaultdict(list)
    for d in json.loads(JUDGE.read_text())["decisions"]:
        by[d["clip"]].append(d)
    return by


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


def score(manifest=None, systems=None, normalize=None, judge=True):
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
        r = build(clips[i], fam, judge)
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
    res = score(judge=not a.no_judge)
    p = REPO / "eval" / "results" / "silver.json"
    p.write_text(json.dumps(res, indent=1))
    print(f"{'system':32s} {'silver WER':>10s} {'stratified':>11s} {'book':>7s} {'voters':>7s}")
    for s, r in sorted(res.items(), key=lambda x: x[1]["all"]["wer"] or 9):
        f = lambda k: f"{100 * r[k]['wer']:.1f}%" if k in r and r[k]["wer"] is not None else "-"
        print(f"{s:32s} {f('all'):>10s} {f('stratified'):>11s} {f('book'):>7s} {r['all']['voters']:>7}")
    print(f"-> {p}")


def cmd_worklist(a):
    """Every flagged span with its context and each voter's words, for a reviewer (human or LLM)
    who can't hear the audio: they pick among the candidates, the book's word or "unclear"."""
    items, lines = [], []
    for clip in load_clips():
        ref = build(clip, judge=False)
        if not ref:
            continue
        toks = ref["tokens"]
        for t in toks:
            t["conf"] = confidence(t)
        for r in regions(ref):
            i0, i1 = r["start"], r["end"]
            words_before = [t["w"] for t in toks[:i0] if t["n"]]
            words_after = [t["w"] for t in toks[i1 + 1:] if t["n"]]
            span = toks[i0:i1 + 1]
            item = {"id": f"W{len(items) + 1:03d}", "clip": clip.id, "t": r["t"],
                    "before": " ".join(words_before[-3:]), "from": r["text"], "after": " ".join(words_after[:3])}
            items.append(item)
            per, seen = defaultdict(list), set()
            for t in span:
                c = t.get("cands")
                if c is None:
                    for s in ref["voters"]:
                        per[s].append(t["w"] if t["n"] else "")
                elif id(c) not in seen:
                    seen.add(id(c))
                    for s in ref["voters"]:
                        per[s].append(c.get(s) or "")
            t0, t1 = span[0]["t"] - 1, span[-1]["t"] + 2
            ctx = [w["d"] for w in clip.toks.get("whisper-turbo+ctx", []) if t0 <= w["t"] <= t1]
            m, sec = divmod(int(r["t"]), 60)
            lines.append(f"{item['id']} {clip.id} @{m}:{sec:02d} {','.join(r['kinds'])}")
            lines.append(f"  ... {' '.join(words_before[-14:])} [{r['text']}] {' '.join(words_after[:14])} ...")
            lines.append("  " + " | ".join(f"{s.split('-')[0]}: {' '.join(x for x in per[s] if x) or '-'}"
                                           for s in ref["voters"]) + f" | turbo+ctx: {' '.join(ctx) or '-'}")
            bj = [t["bj"] for t in span if "bj" in t]
            if bj and ref["book"] and ref["book"].get("region"):
                reg = ref["book"]["region"]
                lines.append(f"  book: {' '.join(reg[max(0, min(bj) - 8):max(bj) + 9])}")
    out = OUT_DIR / "worklist"
    out.with_suffix(".json").write_text(json.dumps(items, ensure_ascii=False, indent=0))
    out.with_suffix(".txt").write_text("\n".join(lines) + "\n")
    print(f"{len(items)} flagged spans -> {out}.txt / .json")


def cmd_judge_import(a):
    """id<TAB>verdict(fix|keep|unclear)<TAB>to<TAB>why -> merge into eval/goldset/judge.json."""
    items = {x["id"]: x for x in json.loads((OUT_DIR / "worklist.json").read_text())}
    clips = {c.id: c for c in load_clips()}
    terms = {t for e in next(iter(clips.values())).gloss.entries for f in e["valid"] for t in gtokens(f)}
    doc = json.loads(JUDGE.read_text()) if JUDGE.exists() else {"decisions": []}
    keep = {(d["clip"], d["t"], d["from"]): d for d in doc["decisions"]}
    bad = 0
    for line in Path(a.tsv).read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        wid, verdict, to, why = (line.split("\t") + ["", "", ""])[:4]
        x = items[wid.strip()]
        verdict = verdict.strip()
        assert verdict in ("fix", "keep", "unclear"), line
        to = x["from"] if verdict == "keep" and not to.strip() else to.strip()
        allowed = set(clips[x["clip"]].evidence) | terms
        new = [t for t in gtokens(to) if t not in allowed]
        if verdict == "fix" and new:
            print(f"rejected {wid}: {new} not in any system output, the glossary or the book")
            bad += 1
            continue
        keep[(x["clip"], x["t"], x["from"])] = {**{k: x[k] for k in ("clip", "t", "before", "from", "after")},
                                                "verdict": verdict, "to": to, "why": why.strip()}
    doc["about"] = ("Decisions on flagged silver-reference spans by a text-only reviewer (no audio). "
                    "They choose among system outputs, the glossary and the book; 'unclear' needs a listener.")
    doc["decisions"] = sorted(keep.values(), key=lambda d: (d["clip"], d["t"]))
    JUDGE.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    print(f"{len(doc['decisions'])} decisions in {JUDGE} ({bad} rejected)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build").set_defaults(fn=cmd_build)
    sc = sub.add_parser("score")
    sc.add_argument("--no-judge", action="store_true", help="ignore eval/goldset/judge.json")
    sc.set_defaults(fn=cmd_score)
    sub.add_parser("worklist", help="flagged spans for review -> data/silver/worklist.{json,txt}").set_defaults(
        fn=cmd_worklist)
    im = sub.add_parser("judge-import", help="TSV of id<TAB>verdict<TAB>to<TAB>why -> eval/goldset/judge.json")
    im.add_argument("tsv")
    im.set_defaults(fn=cmd_judge_import)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
