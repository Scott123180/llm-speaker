#!/usr/bin/env python3
import argparse
import os
import re
import shutil
import sys


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


def move_file(src, dest, overwrite):
    if os.path.exists(dest):
        if not overwrite:
            print(f"skip (exists): {dest}", file=sys.stderr)
            return False
        os.remove(dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.move(src, dest)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Split files into small/large directories based on token count."
    )
    parser.add_argument("--input-dir", required=True, help="Directory to scan.")
    parser.add_argument("--ext", default=".txt", help="File extension to include.")
    parser.add_argument(
        "--threshold",
        type=int,
        default=15000,
        help="Token threshold (<= goes to small, > goes to large).",
    )
    parser.add_argument(
        "--small-dir",
        default=None,
        help="Directory for small files (default: <input-dir>/small).",
    )
    parser.add_argument(
        "--large-dir",
        default=None,
        help="Directory for large files (default: <input-dir>/large).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite files if they already exist in destination.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without moving files.",
    )
    args = parser.parse_args()

    input_dir = os.path.abspath(args.input_dir)
    if not os.path.isdir(input_dir):
        print(f"not a directory: {input_dir}", file=sys.stderr)
        sys.exit(1)

    small_dir = os.path.abspath(args.small_dir or os.path.join(input_dir, "small"))
    large_dir = os.path.abspath(args.large_dir or os.path.join(input_dir, "large"))

    moved_small = 0
    moved_large = 0

    for path in iter_files(input_dir, args.ext):
        if os.path.commonpath([path, small_dir]) == small_dir:
            continue
        if os.path.commonpath([path, large_dir]) == large_dir:
            continue

        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        words = count_words(text)
        tokens = approx_tokens_from_words(words)

        rel_path = os.path.relpath(path, input_dir)
        if tokens <= args.threshold:
            dest = os.path.join(small_dir, rel_path)
            action = "small"
        else:
            dest = os.path.join(large_dir, rel_path)
            action = "large"

        if args.dry_run:
            print(f"{action}: {path} -> {dest} ({tokens} tokens)")
            continue

        moved = move_file(path, dest, args.overwrite)
        if moved:
            if action == "small":
                moved_small += 1
            else:
                moved_large += 1

    if not args.dry_run:
        print(f"moved_small: {moved_small}")
        print(f"moved_large: {moved_large}")


if __name__ == "__main__":
    main()
