#!/usr/bin/env python3
"""Download a Hugging Face model repo into data/models/{repo}/ with resumable curl.

huggingface_hub's own transfers (xet and plain HTTP) stalled on this connection
while curl on the same URLs ran at full speed, so runners use these local copies
when present (see common.local_model).

  python3 asr/fetch_model.py Systran/faster-whisper-large-v3 nvidia/parakeet-tdt-0.6b-v3
"""
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

DEST = Path(__file__).resolve().parent.parent / "data" / "models"
SKIP = (".gitattributes", ".md", ".png", ".jpg")


def files(repo):
    with urllib.request.urlopen(f"https://huggingface.co/api/models/{repo}", timeout=60) as r:
        info = json.load(r)
    names = [s["rfilename"] for s in info.get("siblings", []) if not s["rfilename"].endswith(SKIP)]
    nemo = [n for n in names if n.endswith(".nemo")]
    return nemo or [n for n in names if not n.endswith(".gguf") and not n.startswith(".")]


def fetch(repo):
    out = DEST / repo
    for name in files(repo):
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://huggingface.co/{repo}/resolve/main/{name}"
        for attempt in range(1, 6):
            # -C - resumes partial files; --retry handles transient resets
            rc = subprocess.run(["curl", "-sSL", "--fail", "-C", "-", "--retry", "5", "--retry-all-errors",
                                 "--speed-limit", "20000", "--speed-time", "60", "-o", str(target), url]).returncode
            if rc in (0, 33):  # 33 = range not satisfiable: already complete
                break
            print(f"  retry {attempt} {name} (curl exit {rc})", file=sys.stderr)
        else:
            sys.exit(f"failed: {repo}/{name}")
        print(f"  {repo}/{name}: {target.stat().st_size / 1e6:.0f} MB", file=sys.stderr)
    (out / ".complete").touch()


if __name__ == "__main__":
    for repo in sys.argv[1:]:
        fetch(repo)
