# llm-speaker


# Instructions
These are tailored to Ubuntu linux install.

1. create a venv
`bash setup.sh`

2.  activate python virtual environment
`bash activate_venv.sh`

3. install whisper for transcription
`pip install git+https://github.com/openai/whisper.git`

4. install accompanying whisper dependencies 
`sudo apt update && sudo apt install ffmpeg`

# Utilities

## Max tokens estimator
`llm/max_tokens.py` scans a directory of text files and reports the file with the
highest word count plus an approximate token count using the 3/4 rule.

Usage:
```bash
python3 llm/max_tokens.py --input-dir /path/to/texts
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
python3 llm/split_by_tokens.py --input-dir /path/to/texts
```

Options:
- `--threshold 15000` to change the cutoff.
- `--ext .txt` to filter by file extension.
- `--dry-run` to preview moves without changing files.
