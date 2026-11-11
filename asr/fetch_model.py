#!/usr/bin/env python3
"""Download a Hugging Face model repo into data/models/{repo}/ with resumable curl.

huggingface_hub's own transfers (xet and plain HTTP) stalled on this connection
while curl on the same URLs ran at full speed, so runners use these local copies
when present (see common.local_model). Stdlib only, so it also runs on a fresh
cloud instance before any environment exists.

  python3 asr/fetch_model.py Systran/faster-whisper-large-v3 nvidia/parakeet-tdt-0.6b-v3
  python3 asr/fetch_model.py "AtomicChat/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-GGUF:*Encoder-F16.gguf,*AD-IQ4_NL.gguf"

`repo:glob,glob` selects files by pattern (default: the .nemo file if there is one,
otherwise everything except GGUF and docs). Set HF_TOKEN for gated repos.
"""
import fnmatch
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

DEST = Path(__file__).resolve().parent.parent / "data" / "models"
SKIP = (".gitattributes", ".md", ".png", ".jpg")


def _auth():
    tok = os.environ.get("HF_TOKEN")
    return {"Authorization": f"Bearer {tok}"} if tok else {}


def files(repo, patterns=None):
    req = urllib.request.Request(f"https://huggingface.co/api/models/{repo}", headers=_auth())
    with urllib.request.urlopen(req, timeout=60) as r:
        info = json.load(r)
    names = [s["rfilename"] for s in info.get("siblings", [])]
    if patterns:
        picked = [n for n in names if any(fnmatch.fnmatch(n, p) for p in patterns)]
        if not picked:
            sys.exit(f"{repo}: no files match {patterns}")
        return picked
    names = [n for n in names if not n.endswith(SKIP)]
    nemo = [n for n in names if n.endswith(".nemo")]
    return nemo or [n for n in names if not n.endswith(".gguf") and not n.startswith(".")]


def fetch(spec):
    repo, _, pats = spec.partition(":")
    patterns = [p for p in pats.split(",") if p] or None
    out = DEST / repo
    hdr = [x for k, v in _auth().items() for x in ("-H", f"{k}: {v}")]
    for name in files(repo, patterns):
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://huggingface.co/{repo}/resolve/main/{name}"
        for attempt in range(1, 6):
            # -C - resumes partial files; --retry handles transient resets
            rc = subprocess.run(["curl", "-sSL", "--fail", "-C", "-", "--retry", "5", "--retry-all-errors",
                                 "--speed-limit", "20000", "--speed-time", "60", *hdr,
                                 "-o", str(target), url]).returncode
            if rc in (0, 33):  # 33 = range not satisfiable: already complete
                break
            print(f"  retry {attempt} {name} (curl exit {rc})", file=sys.stderr)
        else:
            sys.exit(f"failed: {repo}/{name}")
        print(f"  {repo}/{name}: {target.stat().st_size / 1e6:.0f} MB", file=sys.stderr)
    (out / ".complete").touch()


if __name__ == "__main__":
    for spec in sys.argv[1:]:
        fetch(spec)
