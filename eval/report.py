#!/usr/bin/env python3
"""Score every system in data/outputs/ and write the bake-off comparison report.

  uv run python eval/report.py            # -> reports/ASR bake-off.md + eval/results/metrics.json

Works before any references exist (speed, hallucination on non-speech clips,
glossary spelling, loops, agreement, side-by-side examples). As corrected
references appear in eval/goldset/refs/{clip_id}.txt, reference-based metrics
(WER/CER, term recall/insertions, per-stratum WER with CIs) are added automatically.
"""
import json
import math
import random
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import jiwer
from whisper_normalizer.english import EnglishTextNormalizer

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "transcriber"))
from build_context import Glossary, load_dictionary  # noqa: E402

OUT = REPO / "data" / "outputs"
GOLD = REPO / "eval" / "goldset"
REPORT = REPO / "reports" / "ASR bake-off.md"
METRICS = REPO / "eval" / "results" / "metrics.json"
ARCHIVE_HOURS = 6500
BASELINE = "legacy-whisper-cli"
ANCHORS = ["whisper-large-v3+ctx", "whisper-large-v3", "whisper-turbo+ctx", "whisper-turbo"]
NORM = EnglishTextNormalizer()
EXCLUDED = []


def norm(text):
    return re.sub(r"\s+", " ", NORM(text or "")).strip()


def load():
    manifest = json.loads((GOLD / "manifest.json").read_text())["clips"]
    systems = {}
    for d in sorted(p for p in OUT.iterdir() if p.is_dir()):
        outs = {p.stem: json.loads(p.read_text()) for p in d.glob("*.json") if not p.name.startswith("_")}
        run = json.loads((d / "_run.json").read_text()) if (d / "_run.json").exists() else {}
        if outs:
            systems[d.name] = {"outs": outs, "run": run}
    # non-speech clips a listener marked as actually containing speech are excluded
    manifest = [c for c in manifest if not (c["kind"] == "nonspeech" and c.get("verified") == "speech")]
    global EXCLUDED
    EXCLUDED = [c for c in manifest if c.get("exclude")]
    manifest = [c for c in manifest if not c.get("exclude")]
    refs = {}
    for p in (GOLD / "refs").glob("*.txt"):
        raw = p.read_text().strip()
        draft = GOLD / "drafts" / p.name
        if raw and not (draft.exists() and draft.read_text().strip() == raw):  # uncorrected copies don't count
            refs[p.stem] = re.sub(r"(?m)^\s*[QA]:\s*", "", raw)  # strip speaker markers
    return manifest, systems, refs


def order(systems):
    def key(s):
        return (s != BASELINE, s.split("+")[0], "+" in s)
    return sorted(systems, key=key)


# ---------------------------------------------------------------- metrics
def loop_flag(text):
    w = norm(text).split()
    for n in (1, 2, 3, 4, 5, 6):
        run = 1
        for i in range(n, len(w) - n + 1, n):
            run = run + 1 if w[i:i + n] == w[i - n:i] else 1
            if run >= (8 if n == 1 else 4):
                return True
    return False


def _toks(s):
    return re.findall(r"[a-z']+", (s or "").lower())


def echo_segments(o, n=4):
    """Segments that mostly repeat the context prompt instead of transcribing audio
    (at least half of their 4-grams occur in the prompt). Returns [(start, end)]."""
    ctx = o.get("context")
    if not ctx:
        return []
    pt = _toks(" ".join(ctx) if isinstance(ctx, list) else ctx)
    grams = {tuple(pt[i:i + n]) for i in range(len(pt) - n + 1)}
    out = []
    for s in o.get("segments") or []:
        st = _toks(s["text"])
        if len(st) < 3:
            continue
        hits = sum(1 for i in range(len(st) - n + 1) if tuple(st[i:i + n]) in grams)
        if hits >= max(1, 0.5 * (len(st) - n + 1)):
            out.append((s["start"], s["end"]))
    return out


def glossary_hits(gloss, text):
    valid, mis = Counter(), Counter()
    for i, kind, form in gloss.find(text or ""):
        e = gloss.entries[i]
        if e["category"] == "title":
            continue
        key = re.sub(r"[^a-z]", "", form.lower())
        (valid if kind == "valid" else mis)[(i, key if kind == "valid" else form)] += 1
    return valid, mis


def wer_counts(ref, hyp):
    r, h = norm(ref), norm(hyp)
    if not r:
        return None
    o = jiwer.process_words(r, h if h else "<empty>")
    c = jiwer.process_characters(r, h if h else "<empty>")
    return {"S": o.substitutions, "D": o.deletions, "I": o.insertions, "N": len(r.split()),
            "cS": c.substitutions, "cD": c.deletions, "cI": c.insertions, "cN": len(r)}


def formatted_wer(ref, hyp):
    """Case- and punctuation-sensitive WER (crude formatting indicator)."""
    f = lambda t: re.sub(r"[“”]", '"', re.sub(r"[‘’]", "'", t or "")).split()
    r, h = f(ref), f(hyp)
    if not r:
        return None
    return jiwer.wer(" ".join(r), " ".join(h) if h else "<empty>")


def agg_wer(rows):
    n = sum(r["N"] for r in rows)
    return (sum(r["S"] + r["D"] + r["I"] for r in rows) / n) if n else None


def bootstrap_diff(a_rows, b_rows, iters=2000, seed=1):
    """95% CI of WER(a) - WER(b) resampling clips (one clip per talk)."""
    rng = random.Random(seed)
    idx = list(range(len(a_rows)))
    diffs = []
    for _ in range(iters):
        s = [rng.choice(idx) for _ in idx]
        diffs.append(agg_wer([a_rows[i] for i in s]) - agg_wer([b_rows[i] for i in s]))
    diffs.sort()
    return diffs[int(0.025 * iters)], diffs[int(0.975 * iters)]


def compute(manifest, systems, refs, gloss):
    speech = [c for c in manifest if c["kind"] == "speech"]
    nonspeech = [c for c in manifest if c["kind"] == "nonspeech"]
    M = {}
    for s, d in systems.items():
        outs, run = d["outs"], d["run"]
        m = {"run": run}
        # non-speech hallucination
        ns = [(c, outs[c["clip_id"]]) for c in nonspeech if c["clip_id"] in outs]
        words = [len(norm(o["text"]).split()) for _, o in ns]
        m["nonspeech"] = {"clips": len(ns), "clips_with_output": sum(1 for w in words if w),
                          "rate": (sum(1 for w in words if w) / len(ns)) if ns else None,
                          "words_total": sum(words),
                          "phrases": Counter(o["text"].strip()[:60] for _, o in ns if norm(o["text"])).most_common(6)}
        # speech, reference-free
        sp = [(c, outs[c["clip_id"]]) for c in speech if c["clip_id"] in outs]
        gv, gm = Counter(), Counter()
        for _, o in sp:
            v, mi = glossary_hits(gloss, o["text"])
            gv.update(v)
            gm.update(mi)
        mins = sum(c["end"] - c["start"] for c, _ in sp) / 60
        text_all = " ".join(o["text"] for _, o in sp)
        nwords = len(text_all.split())
        m["speech"] = {
            "clips": len(sp), "minutes": mins,
            "words_per_min": nwords / mins if mins else None,
            "gloss_valid": sum(gv.values()), "gloss_misheard": sum(gm.values()),
            "gloss_misheard_share": sum(gm.values()) / max(1, sum(gv.values()) + sum(gm.values())),
            "top_misheard": [f for (_, f), _ in gm.most_common(12)],
            "loops": [c["clip_id"] for c, o in sp if loop_flag(o["text"])],
            "echo_clips": [c["clip_id"] for c, o in sp if echo_segments(o)],
            "echo_min": sum(e - s for _, o in sp for s, e in echo_segments(o)) / 60,
            "punct_per_100w": 100 * len(re.findall(r"[.,;:?!]", text_all)) / max(1, nwords),
            "has_word_timestamps": any(o.get("words") for _, o in sp),
        }
        # reference-based
        rows = []
        for c, o in sp:
            if c["clip_id"] not in refs:
                continue
            w = wer_counts(refs[c["clip_id"]], o["text"])
            if not w:
                continue
            rv, _ = glossary_hits(gloss, refs[c["clip_id"]])
            hv, _ = glossary_hits(gloss, o["text"])
            rk = Counter({k[1]: n for k, n in rv.items()})
            hk = Counter({k[1]: n for k, n in hv.items()})
            w.update(clip_id=c["clip_id"], fwer=formatted_wer(refs[c["clip_id"]], o["text"]),
                     term_ref=sum(rk.values()), term_hit=sum(min(n, hk[k]) for k, n in rk.items()),
                     term_ins=sum(max(0, n - rk[k]) for k, n in hk.items()),
                     **{k: c[k] for k in ("era", "speaker_group", "content", "difficulty")})
            rows.append(w)
        if rows:
            n, cn = sum(r["N"] for r in rows), sum(r["cN"] for r in rows)
            tr = sum(r["term_ref"] for r in rows)
            m["ref"] = {
                "clips": len(rows), "wer": agg_wer(rows),
                "sub": sum(r["S"] for r in rows) / n, "del": sum(r["D"] for r in rows) / n,
                "ins": sum(r["I"] for r in rows) / n,
                "cer": sum(r["cS"] + r["cD"] + r["cI"] for r in rows) / cn,
                "fwer": statistics.mean(r["fwer"] for r in rows),
                "term_recall": sum(r["term_hit"] for r in rows) / tr if tr else None,
                "term_ins_per_100_terms": 100 * sum(r["term_ins"] for r in rows) / tr if tr else None,
                "by": {k: {v: agg_wer([r for r in rows if r[k] == v]) for v in sorted({r[k] for r in rows})}
                       for k in ("era", "speaker_group", "content", "difficulty")},
                "rows": rows,
            }
        M[s] = m

    # agreement matrix (normalized WER of row vs column as reference), speech clips only
    names = order(systems)
    agree = {}
    for a in names:
        for b in names:
            if a == b:
                continue
            rr, hh = [], []
            for c in speech:
                oa, ob = systems[a]["outs"].get(c["clip_id"]), systems[b]["outs"].get(c["clip_id"])
                if oa and ob and norm(ob["text"]):
                    rr.append(norm(ob["text"]))
                    hh.append(norm(oa["text"]) or "<empty>")
            agree[(a, b)] = jiwer.wer(rr, hh) if rr else None
    # CIs vs baseline when refs exist
    if BASELINE in M and "ref" in M[BASELINE]:
        base = {r["clip_id"]: r for r in M[BASELINE]["ref"]["rows"]}
        for s, m in M.items():
            if s == BASELINE or "ref" not in m:
                continue
            common = [r for r in m["ref"]["rows"] if r["clip_id"] in base]
            if len(common) >= 5:
                m["ref"]["ci_vs_baseline"] = bootstrap_diff(common, [base[r["clip_id"]] for r in common])
    return M, agree


# ---------------------------------------------------------------- examples
def word_list(o):
    if o.get("words"):
        return [w["word"] for w in o["words"]]
    return (o["text"] or "").split()


def wkey(w):
    return re.sub(r"[^a-z0-9']", "", w.lower()) or "_"


def aligned_slice(anchor_words, hyp_words, a0, a1):
    """Hyp words aligned to anchor[a0:a1] via edit-distance alignment."""
    if not hyp_words:
        return ""
    o = jiwer.process_words(" ".join(map(wkey, anchor_words)), " ".join(map(wkey, hyp_words)))
    lo, hi = None, None
    for ch in o.alignments[0]:
        if ch.ref_end_idx <= a0 or ch.ref_start_idx >= a1:
            continue
        if ch.type == "insert":
            continue
        # proportional mapping inside the chunk
        rs, re_, hs, he = ch.ref_start_idx, ch.ref_end_idx, ch.hyp_start_idx, ch.hyp_end_idx
        f0 = (max(a0, rs) - rs) / max(1, re_ - rs)
        f1 = (min(a1, re_) - rs) / max(1, re_ - rs)
        h0, h1 = hs + round(f0 * (he - hs)), hs + round(f1 * (he - hs))
        lo = h0 if lo is None else min(lo, h0)
        hi = h1 if hi is None else max(hi, h1)
    return " ".join(hyp_words[lo:hi]) if lo is not None else ""


def examples(manifest, systems, gloss, max_n=14):
    anchor = next((a for a in ANCHORS if a in systems), None)
    if not anchor:
        return None, []
    names = order(systems)
    speech = [c for c in manifest if c["kind"] == "speech"]
    cands = []
    for c in speech:
        ao = systems[anchor]["outs"].get(c["clip_id"])
        if not ao:
            continue
        aw = word_list(ao)
        # glossary hits in anchor (find positions by scanning word windows)
        for i in range(len(aw)):
            for n in (3, 2, 1):
                frag = " ".join(aw[i:i + n])
                hits = list(gloss.find(frag))
                if hits and len(frag.split()) == n:
                    e = gloss.entries[hits[0][0]]
                    if e["category"] in ("title",):
                        break
                    cands.append((c, i, n, hits[0][0]))
                    break
    random.Random(3).shuffle(cands)
    out, used_clips, used_entries = [], Counter(), set()
    for c, i, n, ei in cands:
        if used_clips[c["clip_id"]] >= 1 or ei in used_entries:
            continue
        aw = word_list(systems[anchor]["outs"][c["clip_id"]])
        a0, a1 = max(0, i - 10), min(len(aw), i + n + 10)
        row = {}
        for s in names:
            o = systems[s]["outs"].get(c["clip_id"])
            row[s] = (" ".join(aw[a0:a1]) if s == anchor else aligned_slice(aw, word_list(o), a0, a1)) if o else ""
        if len({norm(v) for v in row.values()}) < 3:  # want real disagreement
            continue
        t = None
        if systems[anchor]["outs"][c["clip_id"]].get("words"):
            t = systems[anchor]["outs"][c["clip_id"]]["words"][i]["start"]
        out.append({"clip": c, "term": gloss.entries[ei]["term"], "t": t, "row": row})
        used_clips[c["clip_id"]] += 1
        used_entries.add(ei)
        if len(out) >= max_n:
            break
    return anchor, out


# ---------------------------------------------------------------- report
def echo_cell(m):
    if not m["run"] or not (m["run"].get("params") or {}).get("context"):
        return "—"
    sp = m["speech"]
    if not sp["echo_clips"]:
        return "0 clips"
    return f"{len(sp['echo_clips'])} clips ({pct(sp['echo_min'] / sp['minutes'])} of audio)"


def pct(x, d=1):
    return "—" if x is None else f"{100 * x:.{d}f}%"


def fmt(x, d=1):
    return "—" if x is None else f"{x:.{d}f}"


def write_report(manifest, systems, refs, M, agree, anchor, ex):
    names = order(systems)
    speech = [c for c in manifest if c["kind"] == "speech"]
    nonspeech = [c for c in manifest if c["kind"] == "nonspeech"]
    L = []
    w = L.append
    w("# ASR bake-off")
    w("")
    w(f"_Generated {time.strftime('%Y-%m-%d %H:%M')} by `eval/report.py`. Re-run after adding systems or references._")
    w("")
    w(f"**Gold set:** {len(speech)} speech excerpts ({sum(c['end'] - c['start'] for c in speech) / 3600:.1f} h, "
      f"one per talk, stratified by era / speaker / content / audio difficulty) and {len(nonspeech)} non-speech "
      f"clips ({sum(c['end'] - c['start'] for c in nonspeech) / 60:.0f} min of bells, silence and room noise where VAD "
      f"finds <10% speech). **Corrected references: {len(refs)}/{len(speech)}.**")
    w("")
    findings = REPO / "eval" / "findings.md"
    if findings.exists():
        w("## Findings")
        w("")
        w(f"_Hand-written interpretation (`eval/findings.md`, last edited "
          f"{time.strftime('%Y-%m-%d', time.localtime(findings.stat().st_mtime))}). "
          "The tables below are regenerated each run; re-check this section when they change._")
        w("")
        w(findings.read_text().strip())
        w("")
    if not refs:
        w("> **Accuracy (WER) is not measured yet.** No corrected references exist, so this report shows only what "
          "can be measured without them: speed, hallucination on non-speech, how each system spells glossary terms, "
          "repetition loops, and agreement between systems. Correct the drafts in `eval/goldset/drafts/` into "
          "`eval/goldset/refs/` (see `eval/CONVENTIONS.md`) and re-run to add WER, term recall and per-stratum results.")
        w("")

    w("## Systems")
    w("")
    w("| System | Model | Context | Device | Speed (× real time) | GPU peak | Archive time on this PC* |")
    w("|---|---|---|---|---|---|---|")
    for s in names:
        r = M[s]["run"]
        ctx = (r.get("params") or {}).get("context") or "—"
        rt = r.get("rtfx")
        w(f"| `{s}` | {r.get('model', '?')} | {ctx} | {r.get('device', '?')} | {fmt(rt, 0) if rt else '—'} | "
          f"{(str(r['gpu_peak_mb']) + ' MB') if r.get('gpu_peak_mb') else '—'} | "
          f"{(fmt(ARCHIVE_HOURS / rt / 24, 1) + ' days') if rt else '—'} |")
    w("")
    w(f"\\* {ARCHIVE_HOURS:,} h of audio at the measured speed on short clips (includes per-clip overhead, "
      "so full talks run somewhat faster). `legacy-whisper-cli` = the existing transcripts (Whisper CLI turbo, "
      "no VAD, no prompt, `condition_on_previous_text=True`).")
    w("")

    w("## Summary")
    w("")
    head = ("| System | Non-speech clips with invented text | Glossary terms misheard | Prompt echo | Loops | "
            "Words/min | Punct./100 words |")
    if refs:
        head += " WER | CER | Term recall | Term false insertions /100 |"
    w(head)
    w("|" + "|".join(["---"] * (head.count("|") - 1)) + "|")
    for s in names:
        m = M[s]
        ns, sp = m["nonspeech"], m["speech"]
        row = (f"| `{s}` | {ns['clips_with_output']}/{ns['clips']} ({pct(ns['rate'], 0)}) | "
               f"{pct(sp['gloss_misheard_share'])} ({sp['gloss_misheard']} of {sp['gloss_misheard'] + sp['gloss_valid']}) | "
               f"{echo_cell(m)} | "
               f"{len(sp['loops'])} | {fmt(sp['words_per_min'], 0)} | {fmt(sp['punct_per_100w'], 1)} |")
        if refs:
            rf = m.get("ref", {})
            row += (f" {pct(rf.get('wer'))} | {pct(rf.get('cer'))} | {pct(rf.get('term_recall'))} | "
                    f"{fmt(rf.get('term_ins_per_100_terms'))} |")
        w(row)
    w("")
    w("How to read this:")
    w("- **Non-speech clips with invented text**: any words output on a clip with no speech. All of them are "
      "errors, so lower is better. Most of these clips were *chosen* at spots where the legacy transcripts "
      "invented text, so legacy's score there is near 100% by construction. Compare the new systems with each other.")
    w("- **Glossary terms misheard**: share of glossary hits that use a known *wrong* spelling "
      "(\"Yakujo\" for Hyakujo, \"doksan\" for dokusan). Lower is better. This only counts misspellings "
      "already listed in the glossary, and a prompt can push the share down by inserting terms that weren't "
      "said, so check it against the false-insertion column once references exist.")
    w("- **Prompt echo**: speech clips where a stretch of output repeats the context prompt instead of what was "
      "said (the speech there is lost), and the share of speech audio replaced that way. Only systems given a "
      "prompt or term list can do this; any non-zero value is serious.")
    w("- **Loops**: speech clips where the output repeats a phrase over and over (a classic Whisper failure).")
    w("- **Words/min**: big differences from the other systems suggest dropped audio or invented text.")
    w("")

    if refs:
        w("## Accuracy by stratum (WER)")
        w("")
        for k in ("era", "speaker_group", "content", "difficulty"):
            vals = sorted({v for s in names for v in (M[s].get("ref", {}).get("by", {}).get(k, {}) or {})})
            if not vals:
                continue
            w(f"**{k}**")
            w("")
            w("| System | " + " | ".join(vals) + " |")
            w("|---|" + "---|" * len(vals))
            for s in names:
                by = M[s].get("ref", {}).get("by", {}).get(k, {})
                w(f"| `{s}` | " + " | ".join(pct(by.get(v)) for v in vals) + " |")
            w("")
        w("**Difference from the legacy transcripts** (WER of system minus WER of legacy, 95% bootstrap CI; "
          "negative = better):")
        w("")
        for s in names:
            ci = M[s].get("ref", {}).get("ci_vs_baseline")
            if ci:
                d = M[s]["ref"]["wer"] - M[BASELINE]["ref"]["wer"]
                w(f"- `{s}`: {100 * d:+.1f} points (CI {100 * ci[0]:+.1f} to {100 * ci[1]:+.1f})")
        w("")

    w("## Effect of per-talk context")
    w("")
    # pair each "+variant" with the longest other system name it extends
    pairs = []
    for s in names:
        bases = [b for b in names if s.startswith(b + "+")]
        if bases:
            pairs.append((max(bases, key=len), s))
    if pairs:
        w("| Base → variant | Misheard terms: base → variant | Non-speech output: base → variant | "
          "Disagreement between the two |")
        w("|---|---|---|---|")
        for a, b in pairs:
            w(f"| `{a}` → `{b}` | {pct(M[a]['speech']['gloss_misheard_share'])} → {pct(M[b]['speech']['gloss_misheard_share'])} | "
              f"{M[a]['nonspeech']['clips_with_output']} → {M[b]['nonspeech']['clips_with_output']} clips | "
              f"{pct(agree.get((b, a)))} of words |")
        w("")
        w("Disagreement is the word error rate between the two outputs: how much of the text the context changed.")
        w("")
    else:
        w("_No with/without-context pairs have been run yet._")
        w("")

    w("## Most frequent misheard glossary terms")
    w("")
    w("| System | Top known misspellings in its output |")
    w("|---|---|")
    for s in names:
        w(f"| `{s}` | {', '.join(M[s]['speech']['top_misheard']) or '—'} |")
    w("")

    w("## What systems output on non-speech")
    w("")
    for s in names:
        ph = M[s]["nonspeech"]["phrases"]
        if ph:
            w(f"- `{s}`: " + "; ".join(f"\"{p}\"×{n}" for p, n in ph))
    w("")

    if ex:
        w("## Side-by-side examples")
        w("")
        w(f"Snippets around a glossary term, aligned to `{anchor}`. Each starts a few words before the term. "
          "Listen to the clip (`data/goldset/clips/<clip>.wav`, at the given offset) to judge which is right.")
        w("")
        for e in ex:
            c = e["clip"]
            at = f" at {int(e['t'] // 60)}:{int(e['t'] % 60):02d}" if e["t"] is not None else ""
            w(f"**{e['term']}** — `{c['clip_id']}`{at} · {c['speaker']} · {c['era']} · {c['difficulty']} audio")
            w("")
            w("| System | Text |")
            w("|---|---|")
            for s, t in e["row"].items():
                w(f"| `{s}` | {t.replace('|', '/') or '_(nothing)_'} |")
            w("")

    w("## Agreement between systems")
    w("")
    w("Word error rate of each row's output measured against each column's output, on speech clips. Systems "
      "that agree closely are making the same choices, not necessarily the right ones.")
    w("")
    w("| | " + " | ".join(f"`{s}`" for s in names) + " |")
    w("|---|" + "---|" * len(names))
    for a in names:
        w(f"| `{a}` | " + " | ".join("·" if a == b else pct(agree.get((a, b)), 0) for b in names) + " |")
    w("")

    loops = {s: M[s]["speech"]["loops"] for s in names if M[s]["speech"]["loops"]}
    if loops:
        w("## Clips with repetition loops")
        w("")
        for s, ls in loops.items():
            w(f"- `{s}`: " + ", ".join(f"`{x}`" for x in ls))
        w("")

    w("## Not run here")
    w("")
    w("- **Nemotron-3.5-Transcribe (30B)**: about 60 GB of weights, which is more than this machine's 60 GB "
      "of RAM. Run it on a cloud H100 and drop its outputs into `data/outputs/` to include it.")
    w("- **ElevenLabs Scribe v2 (hosted)**: needs an API key. Intended as an accuracy ceiling on the gold set only.")
    w("")
    w("## Method notes")
    w("")
    w("- Each excerpt is about 6 minutes, cut at pauses found by Silero VAD. All systems get the same 16 kHz audio.")
    w("- `+ctx` systems get the talk's prompt from `transcriber/build_context.py`. It is built from metadata and "
      "the talk's *old* transcript, as it would be in production.")
    w("- WER is computed after Whisper's English normalizer (lowercasing, punctuation and filler words removed, "
      "numbers spelled out).")
    w("- Legacy text is sliced from full-talk transcripts by segment midpoint, so a few words at clip edges may "
      "differ for reasons unrelated to accuracy.")
    w("- Drafts for correction come from the legacy transcripts, so the gold set isn't anchored to any new system.")
    for c in EXCLUDED:
        w(f"- Excluded `{c['clip_id']}` ({c.get('title', '')}): {c['exclude']}.")
    w("- Non-speech clips skew toward the 1980s tapes, where the old transcripts hallucinate most. They are "
      "VAD-confirmed but not yet confirmed by ear (`verified: false` in the manifest).")
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(L) + "\n")


def main():
    manifest, systems, refs = load()
    if not systems:
        sys.exit("no outputs in data/outputs/")
    gloss = Glossary(REPO / "glossary" / "glossary.csv", load_dictionary())
    M, agree = compute(manifest, systems, refs, gloss)
    anchor, ex = examples(manifest, systems, gloss)
    write_report(manifest, systems, refs, M, agree, anchor, ex)
    METRICS.parent.mkdir(parents=True, exist_ok=True)
    slim = {s: {k: v for k, v in m.items() if k != "ref"} | (
        {"ref": {k: v for k, v in m["ref"].items() if k != "rows"}} if "ref" in m else {}) for s, m in M.items()}
    METRICS.write_text(json.dumps({"systems": slim, "refs": len(refs),
                                   "agreement": {f"{a} vs {b}": v for (a, b), v in agree.items()}},
                                  indent=1, default=str))
    print(f"wrote {REPORT} ({len(systems)} systems, {len(refs)} references)", file=sys.stderr)


if __name__ == "__main__":
    main()
