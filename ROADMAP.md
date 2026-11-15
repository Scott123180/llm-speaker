# Roadmap

_Last updated: 2026-11-10_

## Direction

Get transcripts right **at the ASR stage**, then make only small, checkable fixes afterwards.
The old pipeline ran Whisper `turbo` with no context and then had Llama rewrite each whole
transcript. Under that pipeline, 40–60% of cleanup outputs failed the similarity gate, and the
research says whole-transcript LLM rewrites tend to *raise* error rates.

The new pipeline:

```
audio ─► VAD / non-speech tagging ─► ASR with per-talk context ─► diarization + teacher ID
      ─► pause-based paragraphs ─► glossary-constrained fixes ─► metric gate ─► talk JSON
```

Every model or setting choice is decided by measuring it on a **hand-corrected gold set**, not
by public leaderboards. Background: [`reports/Dharma talk transcription options.md`](reports/Dharma%20talk%20transcription%20options.md).

## Done so far

- [x] Research report on ASR models, context biasing, diarization, post-correction and evaluation
- [x] Domain glossary: `glossary/glossary.csv` (687 entries: lineage, koan masters, ZMM teachers,
      senior students, guests, texts, liturgy, practice and doctrine terms, places), with misheard
      forms mined from 6,032 existing transcripts. See `glossary/README.md`.
- [x] Per-talk context builder: `transcriber/build_context.py` writes a Whisper prompt and a ranked
      term list for each of the 7,075 talks in about 45 s
- [x] Gold set selected and cut, ASR runners for three engines, and a first bake-off across 13 system
      variants. The report is [`reports/ASR bake-off.md`](reports/ASR%20bake-off.md), with the
      interpretation in `eval/findings.md`. **It has no WER yet: the references still need correcting.**

---

## Phase 0 — Housekeeping (small, do first)

- [x] Commit the Apr 5 working-tree changes (CloudFront audio URL, merger source paths, `num_ctx`),
      plus `glossary/`, `transcriber/build_context.py` and `ROADMAP.md` (branch `asr-upgrade`)
- [x] Replace the broken venv with **uv**: `pyproject.toml` + `uv.lock`, Python pinned to 3.14 in
      `.python-version`. NeMo and Qwen3-ASR get their own uv projects under `asr/envs/` (Python 3.12),
      because their dependency pins conflict.
- [ ] Decide where the new ASR code lives long term. For now it's in this repo (`asr/`, `eval/`);
      `~/git/asr-llm-pipeline` already has staged execution, fallback and resume.
- [x] Update `CLAUDE.md`: new audio host, the `asr-llm-pipeline` relationship, glossary, uv, this roadmap
- [ ] Metadata export issues, to raise with the archive system:
  - [ ] The export starts with about 35 lines of HTML before the CSV header. Both the builder and
        `01_csv_talk_mapper.py` now skip it, but the export itself should be fixed.
  - [ ] Maezumi Roshi's 15 talks are missing from the 2026-11-09 export
- [ ] Note for the existing Llama step: `Modelfile-llama8-cleanup-v6a` has `num_ctx 4800`, which is
      smaller than a full talk. Unchunked input gets truncated. This may explain some gate failures.

## Phase 1 — Evaluation foundation (the one non-negotiable)

Without a gold set, every later choice is a guess.

- [x] **Select excerpts**: 30–50 talks × 5–10 min each (about 3–6 h of audio), stratified by:
  - era / recording medium (1980s cassette → digital)
  - speaker (Daido, Shugen, Ryushin, Hojin, Myotai, Hogen, seniors, guests)
  - content: koan-heavy talks, Q&A / dharma encounter, chanting and bells, long silences
- [x] Add 30–60 short **non-speech clips** (silence, bells, chanting, room noise) to measure hallucination
      _Done: 40 excerpts × 6 min (2 later excluded for unusable audio) + 76 non-speech clips, in
      `eval/goldset/manifest.json`. Drafts come from the legacy transcripts, so the set isn't anchored
      to any new system._
- [x] **Book set:** 12 talks from 1981–85 are also published, edited, in *Mountain Record of Zen Talks*
      (1988). `eval/book.py` matches chapters to recordings by shared phrases and adds a 6-min window per
      talk where the book is densest (`"set": "book"` in the manifest). The book text stays in
      `data/book/`, which git ignores.
- [x] **Silver references** (automatic, no human), built by `eval/silver.py`:
  - a majority vote across one plain system per model family
  - glossary spelling fixes and tie-breaks
  - book confirmation for the book clips
  - per-word confidence and flagged regions
  - leave-one-family-out WER in the report
  - tie-breaks by glossary term, real word, then the family most often right (measured against the book)
- [x] **LLM review** of every flagged spot, as text only (`eval/goldset/judge.json`; `silver.py worklist` and
      `judge-import`). It chooses only among existing words: 71 fixes, 101 kept, 30 unclear. 31 regions
      across the 50 clips are left to check by ear.
- [x] **Viewer:** `uv run python eval/viewer.py` shows each system side by side with the reference, its
      flags, the book passage and the audio.
- [ ] More voter families make silver references stronger. Only 3 run locally (Whisper, Parakeet, Qwen);
      the A10 cloud run adds Granite, VibeVoice and Nemotron.
- [ ] Optional, to measure errors every system shares: hand-correct a few clips
      (`eval/goldset/drafts/` → `eval/goldset/refs/`, see `eval/CONVENTIONS.md`), starting with the
      viewer's most-flagged clips.
- [ ] **Confirm the non-speech clips by ear**: a handful trigger output in almost every system and
      probably contain faint speech or chanting. Set `verified` in the manifest.
- [x] Transcription conventions doc (`eval/CONVENTIONS.md`)
- [x] **Scoring script** (`eval/report.py`; reference-based parts activate once refs exist):
  - WER/CER after Whisper's `EnglishTextNormalizer` (jiwer)
  - **Glossary-term recall and false insertions** (biased vs. unbiased WER)
  - Hallucination rate on the non-speech clips
  - Punctuation/casing error rate
  - Speaker-attributed WER for Q&A excerpts (later, MeetEval)
  - Confidence intervals by resampling whole talks, not utterances
- [ ] **Baseline**: score the existing raw Whisper transcripts (included as `legacy-whisper-cli`) and the
      existing Llama outputs (not yet)

**Exit criteria:** baseline numbers per stratum. We know where the current pipeline fails.

## Phase 2 — ASR bake-off

Can start as a smoke test on 5–10 talks while the gold set is being built.

| Candidate | Context method | Hardware | Notes |
|---|---|---|---|
| faster-whisper large-v3 / turbo | per-talk `hotwords` prompt; VAD on; `condition_on_previous_text=False` | 3070 Ti | Lowest-effort upgrade; about 3–6 days for the full archive locally |
| Parakeet-TDT-0.6B v3 (NeMo) | GPU phrase boosting with the ranked term list | 3070 Ti | Prior favourite: copes with long term lists, handles 90-min talks in one pass, less prone to hallucination |
| Qwen3-ASR-1.7B | short context in the system prompt, ≤20-min chunks | 3070 Ti | Good benchmarks, but fragile with long or irrelevant term lists |
| Nemotron-3.5-Transcribe | "context terms" prompt | rented H100 | Check its OpenMDW licence first |
| ElevenLabs Scribe v2 (hosted) | keyterms | API | **Gold set only**, as an accuracy ceiling |

- [x] faster-whisper turbo and large-v3, with and without the per-talk prompt
- [x] Parakeet with phrase boosting at alpha 0.3 (hard terms only), 0.5 and 1.0
- [x] Qwen3-ASR plain, with the prose prompt, with VAD, and with VAD plus a term list
- [ ] Re-score everything once references exist, then pick the engine (see findings)
- [ ] Tune `boosting_tree_alpha` and the context builder (prompt length, term count, min difficulty)
      against WER and term false insertions
- [ ] Whisper large-v3 + prompt: detect prompt echo (a window whose text repeats the prompt) and
      redo that window without the prompt; re-test
- [ ] Cloud: Nemotron-3.5-Transcribe (about 60 GB of weights, too big for this PC) and Scribe v2 as a
      ceiling, both on the gold set only

**Findings so far (no WER yet; details in `eval/findings.md`):**
- **Whisper turbo + prompt** is the safe front-runner: misheard terms fall from 13% to 3%, with no
  prompt echo and the same speed (about 2 days for the archive on this PC).
- **Whisper large-v3 + prompt** spells best among the Whisper setups but **echoes the prompt instead of
  transcribing** in 12 of 38 clips (2.3% of speech lost).
- **Qwen3-ASR** needs VAD (without it, it invents text on 97% of silent clips) and takes a term list,
  not prose (prose gets read aloud). It's promising but about 12 days locally.
- **Parakeet** is the fastest and least prone to inventing text, but boosting is double-edged: names
  get fixed, and words like "koan" become "Khan".
- **Every engine needs VAD gating**, and context format is per-engine (prose prompt for Whisper, term
  list for Qwen, phrase list for Parakeet).
- [ ] Note: no official CUDA build of CTranslate2 (faster-whisper / WhisperX) for ARM64 → use an
      x86 H100 for those, and a GH200 for PyTorch-based models (NeMo, transformers, vLLM)

**Exit criteria:** a chosen engine and settings, justified by gold-set WER, term recall and
hallucination rate.

## Phase 3 — Production transcription run

- [ ] **Audio triage before transcribing**: measure loudness and VAD speech ratio per talk. Flag
      near-silent or broken recordings: 59 talks have legacy transcripts that are more than half
      "Thank you"-style filler, and 88 more are 15–50% filler. Test whether loudness normalization
      rescues any of them (it didn't for 29856), and report the rest to the archive owner.

- [ ] Batch runner: manifest (SQLite/JSON), resumable, atomic writes, a params sidecar per output
      (model, version, prompt or terms used)
- [ ] Output word-level timestamps + segments (JSON), not just text
- [ ] Decide local vs. cloud. Rough costs for about 6,500 h: Parakeet about $20–30 on a GH200;
      Whisper turbo about $115–215; or days to weeks on the 3070 Ti
- [ ] New lineage stage (e.g. `transcript_asr_v2`), keeping the old `transcript_raw` for comparison
- [ ] Spot-check a random sample against the gold-set stratum results

## Phase 4 — Structure and constrained correction

Replaces whole-transcript Llama rewriting.

- [ ] **Paragraphing from pauses** in word timestamps, plus a length cap. The words cannot change.
- [ ] **Glossary-constrained fixes**: an LLM (or rules) proposes `{span → glossary term}` edits for
      low-confidence spans only, and code accepts an edit only if:
  - the span exists verbatim in the transcript
  - the target is in the glossary
  - the two are phonetically similar
  - the talk's edit budget isn't exceeded
- [ ] Optional: run a second ASR system and flag places where it disagrees with the first (ROVER-style)
- [ ] Replace the >90% similarity gate with **metric gates** measured per stage on the gold set
- [ ] Retire `llm/batch_cleanup.py` whole-transcript mode once the above matches or beats it

## Phase 5 — Speakers and non-speech

- [ ] Diarization: Sortformer or Nemotron-3-Diarization. pyannote community-1 needs about 9.5 GB of VRAM
      on long files, which is too much for the 3070 Ti. DiariZen weights are non-commercial.
- [ ] **Teacher voice ID**: enroll each teacher from clean clips (TitaNet/WeSpeaker embeddings),
      then label segments `Teacher name` / `Questioner` / `Introducer`
- [ ] Fill in the **721 talks with no speaker in the metadata**, using voice ID plus intro or
      address cues in the transcript
- [ ] Tag chanting and bells so they don't become fake speakers or hallucinated text
- [ ] Optional: transcribe standard liturgy by aligning it to the known chant text, not by free ASR

## Phase 6 — Integration and publishing

- [ ] Update `schema-mapper/03_transcript_merger.py` for the new stages and timestamped output
- [ ] Extend the index (`05_build_index.py`) with speakers, timestamps and glossary-linked entities
      (e.g. Joshu = Zhaozhou)
- [ ] Define `transcript_curated` (human-reviewed) and `transcript_published`, and a review queue
      sorted by low confidence or high disagreement
- [ ] Optional later: LoRA fine-tune of the chosen model on verified talks (use a low alpha:rank ratio)

---

## Ongoing: glossary loop

- [ ] After each gold-set and production pass, mine new misrecognitions into the `misheard` column
- [ ] Open questions:
  - [ ] Mary Kaijun vs. Kaijin Mold
  - [ ] Ikusei (Shea Ikusei) and Tenfu Loisel: real people?
  - [ ] Museki Tendo
  - [ ] Full names of dharma-name-only entries: Sankai, Kyusan, Mujaku, Choko, Kiju, Joshin
- [ ] Add frequently mentioned people who are still missing (jisha, long-time residents)

## Decisions needed

| Decision | Options | Affects |
|---|---|---|
| Code home | this repo / `asr-llm-pipeline` / merge them | Phase 0+ |
| Usage and licensing of the outputs | internal / public / commercial | DiariZen (non-commercial), Nemotron (OpenMDW), hosted APIs |
| Cloud budget | local only / about $50 / about $300+ | engine choice, timeline |
| Gold-set correction | owner / volunteers / paid | Phase 1 timeline |
| Downstream consumer format | text only / timestamped / speaker-labelled | Phases 3–6 |
