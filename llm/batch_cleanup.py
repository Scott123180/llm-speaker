#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request


def call_ollama(host, model, text, timeout, keep_alive):
    payload = {
        "model": model,
        "prompt": text,
        "stream": False,
    }
    if keep_alive:
        payload["keep_alive"] = keep_alive
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{host.rstrip('/')}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
    decoded = json.loads(body.decode("utf-8"))
    response = decoded.get("response", "")
    stats = {
        "prompt_eval_count": decoded.get("prompt_eval_count"),
        "prompt_eval_duration": decoded.get("prompt_eval_duration"),
        "eval_count": decoded.get("eval_count"),
        "eval_duration": decoded.get("eval_duration"),
        "total_duration": decoded.get("total_duration"),
    }
    return response, stats


def build_output_path(input_path, input_dir, output_dir, ext):
    rel_path = os.path.relpath(input_path, input_dir)
    rel_dir = os.path.dirname(rel_path)
    name = os.path.basename(rel_path)
    if ext and name.endswith(ext):
        base = name[: -len(ext)]
        out_name = f"{base}_cleaned{ext}"
    else:
        out_name = f"{name}_cleaned{ext}"
    return os.path.join(output_dir, rel_dir, out_name)


def iter_input_files(input_dir, ext):
    for root, _, files in os.walk(input_dir):
        for name in sorted(files):
            if ext and not name.endswith(ext):
                continue
            yield os.path.join(root, name)


def main():
    parser = argparse.ArgumentParser(
        description="Batch-clean text files using an Ollama model."
    )
    parser.add_argument("--input-dir", required=True, help="Directory with input files.")
    parser.add_argument("--output-dir", required=True, help="Directory for output files.")
    parser.add_argument("--model", default="llama70-G200-smallctx", help="Ollama model name.")
    parser.add_argument(
        "--host", default="http://localhost:11434", help="Ollama server host."
    )
    parser.add_argument(
        "--ext", default=".txt", help="File extension to process (default: .txt)."
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Per-request timeout in seconds.",
    )
    parser.add_argument(
        "--keep-alive",
        default="24h",
        help="Keep model loaded for this duration (e.g., 24h).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output files if they exist.",
    )
    parser.add_argument(
        "--metrics",
        action="store_true",
        help="Print per-file timing and throughput metrics.",
    )
    args = parser.parse_args()

    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    def process_file(input_path):
        start = time.perf_counter()
        output_path = build_output_path(
            input_path, input_dir, output_dir, args.ext
        )
        if not args.overwrite and os.path.exists(output_path):
            return ("skip", output_path, None, None, 0.0)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        if not text.strip():
            cleaned = ""
            stats = None
        else:
            cleaned, stats = call_ollama(
                args.host, args.model, text, args.timeout, args.keep_alive
            )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned)
        elapsed = time.perf_counter() - start
        return ("wrote", output_path, stats, len(cleaned), elapsed)

    input_paths = list(iter_input_files(input_dir, args.ext))
    total = len(input_paths)
    total_start = time.perf_counter()
    total_chars = 0
    total_eval_count = 0
    total_eval_duration = 0.0

    for input_path in input_paths:
        try:
            status, output_path, stats, char_count, elapsed = process_file(input_path)
            if status == "skip":
                print(f"skip (exists): {output_path}", file=sys.stderr)
            else:
                print(f"wrote: {output_path}", file=sys.stderr)
                if args.metrics:
                    metric = format_metrics(stats, char_count, elapsed)
                    print(f"metrics: {output_path}: {metric}", file=sys.stderr)
                total_chars += char_count
                if stats:
                    total_eval_count += stats.get("eval_count") or 0
                    total_eval_duration += (stats.get("eval_duration") or 0) / 1e9
        except urllib.error.URLError as exc:
            print(f"error: {input_path}: {exc}", file=sys.stderr)
            sys.exit(1)

    if total == 0:
        print("no matching files found", file=sys.stderr)
    if args.metrics and total > 0:
        total_elapsed = time.perf_counter() - total_start
        metric = format_totals(total_elapsed, total_chars, total_eval_count, total_eval_duration)
        print(f"metrics: total: {metric}", file=sys.stderr)


def format_metrics(stats, char_count, elapsed):
    if elapsed <= 0:
        elapsed = 0.000001
    parts = [f"time={elapsed:.2f}s"]
    if char_count:
        parts.append(f"chars/sec={int(char_count / elapsed)}")
    if stats:
        eval_count = stats.get("eval_count")
        eval_duration = stats.get("eval_duration")
        if eval_count and eval_duration:
            eval_seconds = eval_duration / 1e9
            if eval_seconds > 0:
                parts.append(f"tok/sec={eval_count / eval_seconds:.2f}")
        total_duration = stats.get("total_duration")
        if total_duration:
            parts.append(f"ollama_time={total_duration / 1e9:.2f}s")
    return ", ".join(parts)


def format_totals(total_elapsed, total_chars, total_eval_count, total_eval_duration):
    if total_elapsed <= 0:
        total_elapsed = 0.000001
    parts = [f"time={total_elapsed:.2f}s"]
    if total_chars:
        parts.append(f"chars/sec={int(total_chars / total_elapsed)}")
    if total_eval_count and total_eval_duration:
        if total_eval_duration > 0:
            parts.append(f"tok/sec={total_eval_count / total_eval_duration:.2f}")
    return ", ".join(parts)


if __name__ == "__main__":
    main()
