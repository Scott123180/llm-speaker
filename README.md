# llm-speaker


# Setup

Tailored to Ubuntu. Uses [uv](https://docs.astral.sh/uv/) instead of a hand-made venv: the
Python version is pinned in `.python-version` and every package in `uv.lock`, so OS Python
upgrades can't break the environment.

```bash
sudo apt install ffmpeg
uv sync                               # main env (Python 3.14): faster-whisper, eval tools, requests, rich
uv sync --project asr/envs/nemo       # optional: NVIDIA NeMo / Parakeet (Python 3.12)
uv sync --project asr/envs/qwen       # optional: Qwen3-ASR (Python 3.12)
```

Run scripts with `uv run python <script>` (no activation needed).

See `ROADMAP.md` for where the project is headed, `CLAUDE.md` for a map of the code,
and `reports/` for the research report and the ASR bake-off results.

# Utilities

## Max tokens estimator
`llm/max_tokens.py` scans a directory of text files and reports the file with the
highest word count plus an approximate token count using the 3/4 rule.

Usage:
```bash
uv run python llm/max_tokens.py --input-dir /path/to/texts
```

Options:
- `--ext .txt` to filter by file extension (default: `.txt`).

## Split files by token size
`llm/split_by_tokens.py` separates text files into `small/` and `large/`
directories based on an approximate token count.

The goal of this is to run a more efficient model with a context window of 16k tokens, and then separately run a script with a context window of around 50k tokens to process the really large files.

Alternate approaches could include chunking, but I think we have the vRAM on these cloud machines, so lets just not chunk.

Usage:
```bash
uv run python llm/split_by_tokens.py --input-dir /path/to/texts
```

Options:
- `--threshold 15000` to change the cutoff.
- `--ext .txt` to filter by file extension.
- `--dry-run` to preview moves without changing files.
