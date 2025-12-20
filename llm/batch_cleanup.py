#!/usr/bin/env python3
import argparse
import concurrent.futures
import json
import os
import sys
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
    return decoded.get("response", "")


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
    parser.add_argument("--model", default="llama70-cleanup", help="Ollama model name.")
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
        "--parallel",
        type=int,
        default=1,
        help="Number of parallel requests to send (default: 1).",
    )
    args = parser.parse_args()
    if args.parallel < 1:
        parser.error("--parallel must be >= 1")

    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    def process_file(input_path):
        output_path = build_output_path(
            input_path, input_dir, output_dir, args.ext
        )
        if not args.overwrite and os.path.exists(output_path):
            return ("skip", output_path, None)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        if not text.strip():
            cleaned = ""
        else:
            cleaned = call_ollama(
                args.host, args.model, text, args.timeout, args.keep_alive
            )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned)
        return ("wrote", output_path, None)

    input_paths = list(iter_input_files(input_dir, args.ext))
    total = len(input_paths)
    had_error = False

    if args.parallel == 1:
        for input_path in input_paths:
            try:
                status, output_path, _ = process_file(input_path)
                if status == "skip":
                    print(f"skip (exists): {output_path}", file=sys.stderr)
                else:
                    print(f"wrote: {output_path}", file=sys.stderr)
            except urllib.error.URLError as exc:
                print(f"error: {input_path}: {exc}", file=sys.stderr)
                sys.exit(1)
    else:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=args.parallel
        ) as executor:
            future_map = {
                executor.submit(process_file, path): path
                for path in input_paths
            }
            for future in concurrent.futures.as_completed(future_map):
                input_path = future_map[future]
                try:
                    status, output_path, _ = future.result()
                    if status == "skip":
                        print(f"skip (exists): {output_path}", file=sys.stderr)
                    else:
                        print(f"wrote: {output_path}", file=sys.stderr)
                except urllib.error.URLError as exc:
                    print(f"error: {input_path}: {exc}", file=sys.stderr)
                    had_error = True
                except Exception as exc:
                    print(f"error: {input_path}: {exc}", file=sys.stderr)
                    had_error = True

    if total == 0:
        print("no matching files found", file=sys.stderr)
    if had_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
