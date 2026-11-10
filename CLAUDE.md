# llm-speaker

A pipeline for transcribing and refining the Zen Mountain Monastery archive of dharma talks
(~7,000 talks, ~6,500 h of audio). The direction (see `ROADMAP.md`) is to get transcripts right
**at the ASR stage** using per-talk domain context, then apply only small, verifiable fixes, with
every choice measured on a hand-corrected gold set.

## Project Purpose

1. Download audio (now served from CloudFront: `https://d2f7aw4s8anu7j.cloudfront.net/audio/{id}.mp3`)
2. Transcribe with ASR plus per-talk context (glossary + metadata + first-pass transcript)
3. Structure and correct transcripts (legacy: whole-transcript Llama rewrites; planned: pause-based
   paragraphs + glossary-constrained edits)
4. Merge the best transcript variant into structured JSON metadata
5. Build a searchable index for downstream consumption

Related repo: `~/git/asr-llm-pipeline` holds the newer multi-stage LLM structuring pipeline
(stage runner, fallback, resume). `schema-mapper/03_transcript_merger.py` reads its `final/` output.

## Directory Structure

```
asr/                # ASR runners writing a common JSON format (faster-whisper, Parakeet, Qwen3-ASR)
  common.py         # ffmpeg decoding, CUDA lib preload, output schema, GPU memory monitor
  envs/nemo/        # isolated uv project for NeMo (Python 3.12)
  envs/qwen/        # isolated uv project for Qwen3-ASR (Python 3.12, pins transformers)
eval/               # gold set, scoring and the bake-off report
  goldset.py        # select / download / cut gold-set clips
  goldset/          # manifest.json, drafts/ (from legacy transcripts), refs/ (hand-corrected)
  report.py         # metrics + reports/ASR bake-off.md
  run_bakeoff.sh    # run every system and regenerate the report
  CONVENTIONS.md    # how to correct drafts into references
glossary/           # glossary.csv (names/terms, correct + misheard forms) and README
transcriber/        # build_context.py (per-talk ASR prompts/term lists); transcribe.sh (legacy CLI loop)
llm/                # Legacy LLM text cleanup (batch_cleanup.py, Modelfiles)
schema-mapper/      # CSV→JSON pipeline (01-06 scripts + run_all.sh)
content_fetcher/    # Audio downloader (concurrent, rich progress bars)
reports/            # Research report and generated bake-off report
research_notes/     # Sourced notes behind the research report
data/               # (git-ignored) audio, gold-set clips, ASR outputs, logs
```

## Setup (uv)

```bash
uv sync                                   # main env: Python 3.14, faster-whisper, eval tools
uv sync --project asr/envs/nemo           # NeMo / Parakeet (Python 3.12)
uv sync --project asr/envs/qwen           # Qwen3-ASR (Python 3.12)
# system: ffmpeg; NVIDIA driver (CUDA 12 libs for CTranslate2 come from pip wheels)
```

Run things with `uv run ...` (no activation needed). Notes:
- `av` is capped below 19 because faster-whisper 1.2.1 passes an argument removed in PyAV 19.
- CTranslate2 needs `libcublas.so.12`/`libcudnn.so.9` from the `nvidia-*-cu12` wheels; `asr/common.py`
  `preload_cuda_libs()` loads them (no `LD_LIBRARY_PATH` needed).
- Set `HF_HUB_DISABLE_XET=1` if Hugging Face downloads stall.

## Running

### Per-talk ASR context
```bash
uv run python transcriber/build_context.py \
  --metadata ~/Downloads/metadata_export__20261109-20_16.csv \
  --transcripts ~/Documents/talks/all        # -> transcriber/context/{id}.json (~45 s for all talks)
```

### Gold set and ASR bake-off
```bash
uv run python eval/goldset.py select && uv run python eval/goldset.py download && uv run python eval/goldset.py cut
bash eval/run_bakeoff.sh                     # all systems, resumable; then writes reports/ASR bake-off.md
uv run python eval/report.py                 # regenerate the report (e.g. after correcting references)
```

### Legacy transcription (Whisper CLI loop)
`transcriber/transcribe.sh`: OpenAI Whisper CLI `turbo`, no prompt, no VAD. Superseded by `asr/`.

### LLM text cleanup (legacy)
```bash
ollama serve
uv run python llm/batch_cleanup.py --input-dir RAW --output-dir CLEAN --model llama70-G200-tinyctx --metrics
```
Caution: the `llama8-cleanup-v5b/v6a` Modelfiles set `num_ctx 4800`, which is smaller than a full talk.

### Schema mapper
```bash
cd schema-mapper/ && bash run_all.sh     # scripts 01–06; 01 tolerates the HTML preamble in new exports
```

### Download audio
```bash
uv run python -m content_fetcher         # reads IDs from content_fetcher/other_talks.txt
```

## Data locations (local)

| What | Where |
|---|---|
| Metadata export (latest) | `~/Downloads/metadata_export__20261109-20_16.csv` (35 lines of HTML before the header) |
| Legacy Whisper transcripts | `~/Documents/talks/all/{id}.txt`, with segments in `~/Documents/talks/all_json/{id}.json` |
| Structured transcripts | `~/git/asr-llm-pipeline/final/{id}.txt` |

## Transcript Lineage Stages

| Stage | Description |
|---|---|
| `transcript_raw` | Direct Whisper output (legacy CLI) |
| `transcript_structured` | Segmented into paragraphs (Llama) |
| `transcript_cleaned` | Errors corrected, wording refined (Llama) |
| `transcript_curated` | Domain-aware refinement (not yet implemented) |
| `transcript_published` | Final canonical text (not yet implemented) |

Current quality gate: `likeness.py` requires >90% similarity to raw. The roadmap replaces this with gold-set metrics.

## Glossary rules

- `glossary/glossary.csv`: `same_as` = other correct spoken forms (never corrected into each other);
  `misheard` = observed Whisper errors, optionally `wrong>right`.
- A word that is a real name/term elsewhere must not be listed as misheard (e.g. Sankai, Koen, hosan, Ingo/Engo).
- Plain romanization, no macrons.

## Key Files

| File | Purpose |
|---|---|
| `transcriber/build_context.py` | Per-talk prompt + ranked term list from glossary, metadata and first-pass transcript |
| `asr/run_whisper.py` / `run_parakeet.py` / `run_qwen.py` | Bake-off ASR runners (common output format) |
| `eval/report.py` | Scoring and comparison report |
| `schema-mapper/01_csv_talk_mapper.py` | CSV metadata → individual talk JSON files |
| `schema-mapper/03_transcript_merger.py` | Merge best transcript variant into JSON |
| `schema-mapper/05_build_index.py` | Build searchable index |
| `llm/batch_cleanup.py` | HTTP → Ollama for bulk transcript cleanup (legacy) |
| `llm/accuracy/likeness.py` | Similarity score between transcript variants |

## Development Approach

Spec-driven development templates live in `spec_driven_development/`. `ROADMAP.md` tracks phases and
decisions. Audio, clips, model outputs and generated contexts are excluded from git (see `.gitignore`).
