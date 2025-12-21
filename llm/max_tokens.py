#!/usr/bin/env python3
import argparse
import os
import re
import sys
import statistics


WORD_RE = re.compile(r"\S+")


def count_words(text):
    return len(WORD_RE.findall(text))


def approx_tokens_from_words(words):
    # 0.75 words/token => tokens ~= words / 0.75 = words * 4/3
    return int(round(words * 4 / 3))


def iter_files(input_dir, ext):
    for root, _, files in os.walk(input_dir):
        for name in sorted(files):
            if ext and not name.endswith(ext):
                continue
            yield os.path.join(root, name)


def main():
    parser = argparse.ArgumentParser(
        description="Find max words/tokens across text files in a directory."
    )
    parser.add_argument("--input-dir", required=True, help="Directory to scan.")
    parser.add_argument("--ext", default=".txt", help="File extension to include.")
    args = parser.parse_args()

    input_dir = os.path.abspath(args.input_dir)
    if not os.path.isdir(input_dir):
        print(f"not a directory: {input_dir}", file=sys.stderr)
        sys.exit(1)

    max_path = None
    max_words = -1
    max_tokens = -1
    token_counts = []

    seen = 0
    for path in iter_files(input_dir, args.ext):
        seen += 1
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        words = count_words(text)
        tokens = approx_tokens_from_words(words)
        token_counts.append(tokens)
        if words > max_words:
            max_words = words
            max_tokens = tokens
            max_path = path

    if seen == 0:
        print("no matching files found", file=sys.stderr)
        sys.exit(1)

    total_tokens = sum(token_counts)
    avg_tokens = statistics.mean(token_counts)

    token_counts.sort()
    median_tokens = int(round(statistics.median(token_counts)))

    deciles = []
    n = len(token_counts)
    for i in range(10):
        start = (i * n) // 10
        end = ((i + 1) * n) // 10
        if end == 0:
            q_min = q_max = 0
        else:
            q_min = token_counts[start]
            q_max = token_counts[end - 1]
        deciles.append((q_min, q_max, end - start))

    print(f"max_file: {max_path}")
    print(f"max_words: {max_words}")
    print(f"approx_tokens: {max_tokens}")
    print(f"total_tokens: {total_tokens}")
    print(f"avg_tokens: {avg_tokens:.2f}")
    print(f"median_tokens: {median_tokens}")
    for idx, (q_min, q_max, count) in enumerate(deciles, start=1):
        print(f"decile_{idx}: {q_min}-{q_max} (count: {count})")


if __name__ == "__main__":
    main()
