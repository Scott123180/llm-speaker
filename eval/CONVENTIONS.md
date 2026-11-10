# Gold-set transcription conventions

How to turn a draft (`eval/goldset/drafts/{clip_id}.txt`) into a reference
(`eval/goldset/refs/{clip_id}.txt`). Consistency matters more than any single rule.
Scoring normalizes case, punctuation, fillers and numbers, but **term spelling and
real words count**.

## Workflow

1. Copy the draft to `refs/` with the same name.
2. Play `data/goldset/clips/{clip_id}.wav` (6 min) at 0.75–1× speed and fix the text while listening.
   Any player works. A subtitle editor (e.g. Subtitle Edit, Aegisub) or VLC with hotkeys is fastest.
3. Save as plain UTF-8 text. Line breaks are fine anywhere.

A reference that is byte-identical to its draft is ignored, so the report never scores
an uncorrected draft.

## What to write

- **Verbatim words, clean style.** Write what is said, including repeated words that carry
  meaning ("very, very"). Leave out pure fillers ("um", "uh") and false starts that are
  abandoned mid-word. (Fillers are ignored by scoring anyway.)
- **Glossary spellings.** Use `glossary/glossary.csv` spellings for the form *actually spoken*:
  if the teacher says "Joshu", write Joshu, not Zhaozhou. No macrons (Dogen, koan, Shobogenzo).
  If a term is not in the glossary, spell it as best you can and add a row to the glossary.
- **Unintelligible audio:** write `[inaudible]`. Bracketed text is dropped before scoring, so
  whatever a system outputs there counts as insertions. Use it sparingly, only where a careful
  listener genuinely can't tell.
- **Chanting / sung liturgy:** transcribe the words if you can make them out (liturgy texts are
  known). Otherwise write `[chanting]`, which is treated like `[inaudible]`.
- **Other speakers** (questions, introductions): transcribe them like the main speaker. If
  you want to mark who speaks, start the line with `Q:` / `A:`. These markers are stripped before scoring.
- **Numbers:** write them as spoken ("case forty-two" or "case 42"; both normalize the same way).
- **Punctuation and casing:** normal written English. It isn't counted in the main WER, but it is
  used for the formatting score.

## Non-speech clips

`data/goldset/clips/{clip_id}.wav` where `kind = nonspeech` in `eval/goldset/manifest.json`
should contain no words at all (bells, silence, room noise). If you listen to one and
it *does* contain speech or chant, set `"verified": "speech"` for that clip in the manifest
and it will be dropped from the hallucination count. Set `"verified": true` once confirmed.

## Effort

About 2–3 hours per hour of audio when starting from a decent draft, so roughly 8–12 hours
for all 40 clips. The report becomes useful at around 15–20 corrected clips. Spread them
across strata (the manifest lists era, speaker, content and difficulty for each clip).
