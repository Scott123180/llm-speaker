"""
Utilities for scoring how closely a transcript matches an original script.

Formatting differences (punctuation, spacing, capitalization, newlines) are
ignored by normalizing both inputs before computing similarity.
"""

from __future__ import annotations

import argparse
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable, List


_WORD_RE = re.compile(r"\b[\w']+\b")


def _normalize(text: str) -> List[str]:
    """
    Lowercase, strip punctuation, and return a list of word tokens.
    """

    tokens = _WORD_RE.findall(text.lower())
    return tokens


def likeness_ratio(original: str, transcribed: str) -> float:
    """
    Compute a likeness score between two strings.

    The score is a ratio in [0, 1], where 1.0 means the texts are identical
    once formatting differences are removed. Word changes (insert/delete/
    replace) lower the score.
    """

    a = _normalize(original)
    b = _normalize(transcribed)

    if not a and not b:
        return 1.0

    matcher = SequenceMatcher(None, a, b, autojunk=False)
    return matcher.ratio()


def likeness_ratio_from_files(original_path: Path | str, transcribed_path: Path | str) -> float:
    """
    Convenience wrapper to compute likeness for two files.
    """

    original_text = Path(original_path).read_text(encoding="utf-8")
    transcribed_text = Path(transcribed_path).read_text(encoding="utf-8")
    return likeness_ratio(original_text, transcribed_text)


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute likeness score between an original script and a transcript."
    )
    parser.add_argument("original", type=Path, help="Path to the original text file")
    parser.add_argument("transcribed", type=Path, help="Path to the transcribed text file")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> None:
    args = _parse_args(argv)
    score = likeness_ratio_from_files(args.original, args.transcribed)
    print(f"Likeness score: {score:.4f}")


if __name__ == "__main__":
    main()
