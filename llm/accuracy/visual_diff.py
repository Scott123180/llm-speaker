"""
Visualize differences between two text files using word-token diffing.

This ignores formatting (punctuation/whitespace) by tokenizing words, then
shows the mismatched spans in a readable, wrapped format.
"""

from __future__ import annotations

import argparse
import re
import textwrap
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable, List

_WORD_RE = re.compile(r"\b[\w']+\b")


@dataclass(frozen=True)
class DiffSpan:
    tag: str
    a_start: int
    a_end: int
    b_start: int
    b_end: int

    @property
    def a_len(self) -> int:
        return self.a_end - self.a_start

    @property
    def b_len(self) -> int:
        return self.b_end - self.b_start


def _tokenize(text: str) -> List[str]:
    return _WORD_RE.findall(text.lower())


def _wrap_words(words: List[str], width: int) -> str:
    if not words:
        return "(empty)"
    return textwrap.fill(" ".join(words), width=width)


def _collect_diffs(a: List[str], b: List[str]) -> List[DiffSpan]:
    matcher = SequenceMatcher(None, a, b, autojunk=False)
    spans: List[DiffSpan] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            spans.append(DiffSpan(tag, i1, i2, j1, j2))
    return spans


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Show a visual diff between two files by tokenizing words "
            "(ignores punctuation/whitespace)."
        )
    )
    parser.add_argument("original", type=Path, help="Path to the original text file")
    parser.add_argument("compared", type=Path, help="Path to the compared text file")
    parser.add_argument(
        "--max-chunks",
        type=int,
        default=10,
        help="Maximum number of mismatch chunks to display (default: 10)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=100,
        help="Wrap width for displayed snippets (default: 100)",
    )
    parser.add_argument(
        "--context",
        type=int,
        default=8,
        help="Number of surrounding tokens to show around a mismatch (default: 8)",
    )
    parser.add_argument(
        "--sort",
        choices=("size", "order"),
        default="size",
        help="Sort mismatches by size or file order (default: size)",
    )
    return parser.parse_args(argv)


def _clip(seq: List[str], start: int, end: int, context: int) -> List[str]:
    left = max(0, start - context)
    right = min(len(seq), end + context)
    return seq[left:right]


def main(argv: Iterable[str] | None = None) -> None:
    args = _parse_args(argv)

    a_text = args.original.read_text(encoding="utf-8")
    b_text = args.compared.read_text(encoding="utf-8")

    a_tokens = _tokenize(a_text)
    b_tokens = _tokenize(b_text)

    spans = _collect_diffs(a_tokens, b_tokens)

    if args.sort == "size":
        spans = sorted(spans, key=lambda s: s.a_len, reverse=True)

    print(f"Tokens: original={len(a_tokens)} compared={len(b_tokens)}")
    print(f"Diff chunks: {len(spans)} (showing up to {args.max_chunks})\n")

    for idx, span in enumerate(spans[: args.max_chunks], start=1):
        a_snip = _clip(a_tokens, span.a_start, span.a_end, args.context)
        b_snip = _clip(b_tokens, span.b_start, span.b_end, args.context)

        print(f"Chunk {idx}: {span.tag}")
        print(
            f"  original[{span.a_start}:{span.a_end}] (len={span.a_len}) | "
            f"compared[{span.b_start}:{span.b_end}] (len={span.b_len})"
        )
        print("  original:")
        print(textwrap.indent(_wrap_words(a_snip, args.width), "    "))
        print("  compared:")
        print(textwrap.indent(_wrap_words(b_snip, args.width), "    "))
        print()


if __name__ == "__main__":
    main()
