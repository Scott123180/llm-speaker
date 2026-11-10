#!/usr/bin/env python3
"""Build per-talk ASR context (prompt + ranked term list) from the glossary.

For each talk this combines:
  1. Metadata   - speaker, title, caption, koan collection/case.
  2. In-talk    - glossary terms found in the talk's existing (first-pass)
                  transcript, including *misheard* forms ("Yakujo" means
                  Hyakujo was spoken).
  3. Speaker    - terms this speaker uses often that Whisper tends to get wrong.

Terms are ranked by how often Whisper gets them wrong across the corpus
("difficulty"), so the limited prompt budget goes to terms that need help.

Output: one JSON file per talk in --output-dir with
  prompt  - short natural-language text for Whisper `initial_prompt`/`hotwords`
  terms   - ranked list for NeMo phrase boosting / speech-LLM context

Stdlib only. Example:
  python3 transcriber/build_context.py \
      --metadata ~/Downloads/metadata_export__20261109-20_16.csv \
      --transcripts ~/Documents/talks/all \
      --ids 24769 24798
"""
import argparse
import csv
import difflib
import io
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOKEN_RE = re.compile(r"[a-z0-9]+")
ADDRESS_RE = re.compile(r"\b(Roshi|Sensei|Osho)\b")
DICT_FILES = ["/usr/share/dict/american-english", "/usr/share/dict/british-english"]
# Categories that should only come from metadata or in-talk evidence, never priors.
NO_PRIOR = {"teacher-guest", "sangha-zmm"}

csv.field_size_limit(sys.maxsize)


def tokens(text):
    return tuple(TOKEN_RE.findall(text.lower()))


def split_list(s):
    return [x.strip() for x in (s or "").split(";") if x.strip()]


def load_dictionary():
    words = set()
    for f in DICT_FILES:
        try:
            with open(f, encoding="utf-8", errors="ignore") as fh:
                words |= {w.strip().lower() for w in fh}
        except OSError:
            pass
    return words


class Glossary:
    def __init__(self, path, dictionary):
        with open(path, newline="", encoding="utf-8") as fh:
            self.entries = list(csv.DictReader(fh))
        # phrase (token tuple) -> list of (entry index, kind, surface form)
        self.index = defaultdict(list)
        self.max_len = 1
        for i, e in enumerate(self.entries):
            e["valid"] = [e["term"]] + split_list(e["same_as"])
            # misheard items are "wrong" or "wrong>right" (explicit target form)
            e["misheard_target"] = {}
            e["misheard_forms"] = []
            for item in split_list(e["misheard"]):
                wrong, _, right = item.partition(">")
                e["misheard_forms"].append(wrong.strip())
                if right.strip():
                    e["misheard_target"][wrong.strip()] = right.strip()
            e["detectable"] = False
            for kind, forms in (("valid", e["valid"]), ("misheard", e["misheard_forms"])):
                for form in forms:
                    tok = tokens(form)
                    if not tok:
                        continue
                    # Plain-English aliases ("Washing", "just sitting") would fire
                    # on ordinary speech, so they only count in metadata. The main
                    # term is always detectable ("koan", "dharma").
                    plain = form != e["term"] and all(t in dictionary for t in tok)
                    if kind == "valid" and not plain:
                        e["detectable"] = True
                    self.index[tok].append((i, kind, form, plain))
                    self.max_len = max(self.max_len, len(tok))

    def find(self, text, allow_plain=False, min_plain_tokens=2):
        """Yield (entry index, kind, surface form) for every phrase match."""
        tok = tokens(text)
        for start in range(len(tok)):
            for n in range(min(self.max_len, len(tok) - start), 0, -1):
                hits = self.index.get(tok[start:start + n])
                if not hits:
                    continue
                for i, kind, form, plain in hits:
                    if plain and not (allow_plain and n >= min_plain_tokens):
                        continue
                    yield i, kind, form
                break  # longest match wins at this position

    def entry_for_name(self, name):
        tok = tokens(name)
        for i, kind, _, _ in self.index.get(tok, []):
            if kind == "valid":
                return i
        return None


def load_metadata(path):
    raw = Path(path).expanduser().read_text(encoding="utf-8", errors="replace")
    start = raw.find('"Resource ID(s)"')  # some exports have an HTML preamble
    if start < 0:
        sys.exit(f"no 'Resource ID(s)' header found in {path}")
    rows = csv.DictReader(io.StringIO(raw[start:]))
    return {(r.get("Resource ID(s)") or "").strip(): r for r in rows}


def resolve(entry, kind, form):
    """Map a matched surface form to the correct spelling it stands for."""
    def norm(s):
        return re.sub(r"[^a-z]", "", s.lower())

    if kind == "valid":
        # spacing/hyphen variants of the main term ("Shobo Genzo") -> "Shobogenzo"
        return entry["term"] if norm(form) == norm(entry["term"]) else form
    if form in entry["misheard_target"]:
        return entry["misheard_target"][form]

    # closest correct spelling to what Whisper heard ("Yakujo" -> "Hyakujo"),
    # ignoring spaces/hyphens; near-ties go to the main term, then to plain
    # spellings over Wade-Giles ("Ma-tsu") or spaced variants ("Shobo Genzo").
    def score(v):
        r = difflib.SequenceMatcher(None, norm(v), norm(form)).ratio()
        return (round(r, 1), v == entry["term"], not re.search(r"[-' ]", v))

    return max(entry["valid"], key=score)


def scan_corpus(gloss, transcript_dir, metadata):
    """Per-talk hit counts, corpus-wide difficulty, and the spellings each
    speaker actually uses for each entry."""
    per_talk = {}
    df_valid, df_mis = Counter(), Counter()
    usage = defaultdict(lambda: defaultdict(Counter))  # speaker -> entry -> form counts
    resolved_cache = {}
    for f in sorted(Path(transcript_dir).expanduser().glob("*.txt")):
        speaker = (metadata.get(f.stem, {}).get("Speaker") or "").strip()
        hits = defaultdict(Counter)  # entry -> Counter{(kind, form): n}
        for i, kind, form in gloss.find(f.read_text(encoding="utf-8", errors="ignore")):
            hits[i][(kind, form)] += 1
            key = (i, kind, form)
            if key not in resolved_cache:
                resolved_cache[key] = resolve(gloss.entries[i], kind, form)
            usage[speaker][i][resolved_cache[key]] += 1
            usage[None][i][resolved_cache[key]] += 1
        for i, c in hits.items():
            if any(k == "valid" for k, _ in c):
                df_valid[i] += 1
            if any(k == "misheard" for k, _ in c):
                df_mis[i] += 1
        per_talk[f.stem] = hits
    difficulty = {}
    for i, e in enumerate(gloss.entries):
        # If no correct spelling can be detected we can't measure the error
        # rate; treat as easy rather than inflate it from misheard hits alone.
        difficulty[i] = (df_mis[i] + 1) / (df_valid[i] + df_mis[i] + 2) if e["detectable"] else 0.0
    return per_talk, difficulty, usage


def speaker_priors(per_talk, metadata, gloss):
    """For each speaker: share of their talks that mention each entry."""
    talks_by = defaultdict(list)
    for tid, hits in per_talk.items():
        spk = (metadata.get(tid, {}).get("Speaker") or "").strip()
        if spk:
            talks_by[spk].append(hits)
    priors = {}
    for spk, talks in talks_by.items():
        c = Counter(i for hits in talks for i in hits)
        priors[spk] = {i: n / len(talks) for i, n in c.items()}
    return priors


def best_form(entry, hits_for_entry, speaker_usage, global_usage):
    """Pick the spoken form to show: what this talk used, else what this
    speaker usually says (Daido: "Hyakujo"; Shugen: "Baizhang"), else overall."""
    if hits_for_entry:
        talk = Counter()
        for (kind, form), n in hits_for_entry.items():
            talk[resolve(entry, kind, form)] += n
        return talk.most_common(1)[0][0]
    for usage in (speaker_usage, global_usage):
        if usage:
            return usage.most_common(1)[0][0]
    return entry["term"]


def oxford(items):
    if len(items) <= 2:
        return " and ".join(items)
    return ", ".join(items[:-1]) + ", and " + items[-1]


def build_talk(tid, meta, gloss, per_talk, difficulty, usage, priors, args):
    entries = gloss.entries
    scores = defaultdict(float)
    reasons = defaultdict(list)
    forms = {}
    evidence = set()  # entries with metadata or in-talk evidence (not just priors)

    speaker = (meta.get("Speaker") or "").strip()
    title = (meta.get("Title") or "").strip()
    caption = re.sub(r"\s+", " ", meta.get("Caption or Other Speaker") or "").strip()
    collection = (meta.get("Koan Collection") or "").strip()
    case = (meta.get("Koan Case #") or "").strip()
    location = (meta.get("Talk Location") or "").strip()

    # 1. Metadata. Speaker may list several people ("A, B"); the first named
    # one is the speaker, the rest are added as terms.
    speakers = [s.strip() for s in speaker.split(",") if s.strip() and s.strip() != "Other"]
    spk_ids = [gloss.entry_for_name(s) for s in speakers]
    spk_idx = spk_ids[0] if spk_ids else None
    for i in spk_ids[1:]:
        if i is not None:
            scores[i] += 5.0
            reasons[i].append("metadata:co-speaker")
            evidence.add(i)
    if len(speakers) > 1:
        speaker = speakers[0]
    for text, label in ((title, "title"), (caption[:600], "caption"), (collection, "collection")):
        for i, kind, form in gloss.find(text, allow_plain=True):
            if i == spk_idx or f"metadata:{label}" in reasons[i]:
                continue
            scores[i] += 3.0 + 2 * difficulty[i]
            reasons[i].append(f"metadata:{label}")
            evidence.add(i)
            if kind == "valid":
                forms.setdefault(i, form)

    # Guest talks: name the presenter from the caption.
    presenter = None
    if spk_idx is None:
        for i, kind, form in gloss.find(caption[:300], allow_plain=True):
            if entries[i]["category"].startswith(("teacher", "sangha")) and kind == "valid":
                presenter = entries[i]["term"]
                break

    # 2. In-talk evidence from the existing transcript
    talk_hits = per_talk.get(tid, {})
    for i, c in talk_hits.items():
        if i == spk_idx:
            continue
        n = sum(c.values())
        mis = sum(v for (k, _), v in c.items() if k == "misheard")
        scores[i] += 1.0 + 4 * difficulty[i] + math.log1p(n) + (1.0 if mis else 0.0)
        reasons[i].append(f"transcript:{n}x" + (f" ({mis} misheard)" if mis else ""))
        evidence.add(i)

    # 3. Speaker priors (only terms Whisper struggles with). Weaker when the
    # talk has its own first-pass transcript as evidence.
    prior_weight = 0.5 if talk_hits else 2.0
    for i, share in priors.get(speaker, {}).items():
        if i == spk_idx or entries[i]["category"] in NO_PRIOR:
            continue
        if share >= args.prior_min_share and difficulty[i] >= args.prior_min_difficulty:
            scores[i] += prior_weight * share * difficulty[i]
            reasons[i].append(f"speaker-prior:{share:.0%}")

    terms, seen_forms = [], set()
    for i in sorted(scores, key=lambda i: -scores[i]):
        e = entries[i]
        form = forms.get(i) or best_form(e, talk_hits.get(i), usage[speaker].get(i), usage[None].get(i))
        if form.lower() in seen_forms:
            continue
        seen_forms.add(form.lower())
        terms.append({
            "form": form,
            "term": e["term"],
            "category": e["category"],
            "score": round(scores[i], 2),
            "difficulty": round(difficulty[i], 2),
            "evidence": i in evidence,
            "reasons": reasons[i],
        })
        if len(terms) >= args.max_terms:
            break

    # Prompt: reads like transcript text, not instructions (Whisper treats it
    # as preceding speech). Natural sentence header, then the hardest terms
    # that have evidence for this talk (or priors, when no first pass exists).
    who = speaker if speaker and speaker != "Other" else (presenter or "")
    if spk_idx is not None:
        address = next((f for f in entries[spk_idx]["valid"] if ADDRESS_RE.search(f)), None)
        who = f"{speaker}, {address}," if address else speaker
    header = f"This is a dharma talk"
    if who:
        header += f" by {who}"
    if location and location != "Other":
        header += f" at {location}"
    header = header.rstrip(",") + "."
    if title:
        header += f" {title}."
    if collection and collection != "Other":
        header += f" {collection}" + (f", case {case}." if case else ".")
    prompt_terms, seen = [], set()
    by_need = sorted(terms, key=lambda t: (-t["difficulty"], -t["score"]))
    for t in by_need:
        if len(prompt_terms) >= args.prompt_max_terms:
            break
        if t["difficulty"] < args.prompt_min_difficulty:
            continue
        if talk_hits and not t["evidence"]:
            continue  # don't suggest words this talk shows no sign of
        if t["form"].lower() in seen or t["form"].lower() in header.lower():
            continue
        candidate = header + " We'll be talking about " + oxford(prompt_terms + [t["form"]]) + "."
        if len(candidate) > args.prompt_chars:
            break
        prompt_terms.append(t["form"])
        seen.add(t["form"].lower())
    prompt = header + (" We'll be talking about " + oxford(prompt_terms) + "." if prompt_terms else "")

    return {
        "id": tid,
        "title": title,
        "speaker": speaker,
        "koan_collection": collection,
        "koan_case": case,
        "has_first_pass": tid in per_talk,
        "prompt": prompt,
        "prompt_est_tokens": round(len(prompt) / 3.2),  # rough GPT-2 BPE estimate
        "terms": terms,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--glossary", default=REPO / "glossary" / "glossary.csv")
    ap.add_argument("--metadata", required=True, help="metadata export CSV")
    ap.add_argument("--transcripts", required=True, help="dir of first-pass transcripts named {id}.txt")
    ap.add_argument("--output-dir", default=REPO / "transcriber" / "context")
    ap.add_argument("--ids", nargs="*", help="only these talk IDs (default: all with metadata)")
    ap.add_argument("--max-terms", type=int, default=40, help="size of ranked term list")
    ap.add_argument("--prompt-chars", type=int, default=450, help="prompt length cap (~140 Whisper tokens)")
    ap.add_argument("--prompt-max-terms", type=int, default=20, help="long lists raise hallucination risk")
    ap.add_argument("--prompt-min-difficulty", type=float, default=0.15,
                    help="skip terms Whisper already gets right from the prompt")
    ap.add_argument("--prior-min-share", type=float, default=0.15)
    ap.add_argument("--prior-min-difficulty", type=float, default=0.4)
    args = ap.parse_args()

    gloss = Glossary(args.glossary, load_dictionary())
    metadata = load_metadata(args.metadata)
    print(f"glossary: {len(gloss.entries)} entries; metadata: {len(metadata)} talks", file=sys.stderr)
    per_talk, difficulty, usage = scan_corpus(gloss, args.transcripts, metadata)
    print(f"scanned {len(per_talk)} transcripts", file=sys.stderr)
    priors = speaker_priors(per_talk, metadata, gloss)

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ids = args.ids or sorted(metadata)
    written = 0
    for tid in ids:
        if tid not in metadata:
            print(f"skip {tid}: not in metadata", file=sys.stderr)
            continue
        ctx = build_talk(tid, metadata[tid], gloss, per_talk, difficulty, usage, priors, args)
        (out / f"{tid}.json").write_text(json.dumps(ctx, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written += 1
    print(f"wrote {written} context files to {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
