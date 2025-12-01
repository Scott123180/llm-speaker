# Likeness Scoring

Utilities for comparing an original script to a transcribed version while ignoring formatting differences (spacing, punctuation, capitalization, newlines). Word changes (add/remove/replace) lower the score.

# Installation

Python 3.10+; no third-party deps (uses difflib).
Ensure the repo is on your PYTHONPATH or install as a package if you have packaging in place.

# Usage

CLI:

```bash
python -m llm.accuracy.likeness path/to/original.txt path/to/transcribed.txt
# -> Likeness score: 0.9733
```

```python
Library:

from llm.accuracy.likeness import likeness_ratio, likeness_ratio_from_files

score = likeness_ratio("Hello, world!", "hello world")
score_files = likeness_ratio_from_files("original.txt", "transcribed.txt")
```

Returns a float in [0, 1], where 1.0 means word-level matches after normalization.

# How it works
- Normalizes both texts: lowercase, strip punctuation, tokenize words (\b[\w']+\b).
- Compares word sequences with difflib.SequenceMatcher(autojunk=False).
- Empty vs empty -> 1.0; otherwise ratio reflects insert/delete/replace operations.
# Tuning
- Adjust `_WORD_RE` in llm/accuracy/likeness.py if you want to keep/hide certain punctuation (e.g., hyphens).
- Swap SequenceMatcher for other distance metrics (e.g., Levenshtein on tokens) if you need different behavior.
# Testing ideas
- Identical text with different casing/punctuation -> expect 1.0.
- Added/removed words -> score drops.
- Empty vs non-empty -> 0.0; empty vs empty -> 1.0.
- Long transcripts with minor typos -> verify scores are stable and intuitive.
