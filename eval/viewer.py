#!/usr/bin/env python3
"""Local side-by-side viewer: every system's transcript, the silver reference with its
low-confidence flags, the book passage (for book clips) and the clip audio.

  uv run python eval/viewer.py            # build data/viewer/ and serve http://127.0.0.1:8765
  uv run python eval/viewer.py --no-serve # build only

Local only (binds 127.0.0.1): it shows copyrighted book text and archive audio.
Run `uv run python eval/silver.py build` first (and again after new outputs).
"""
import argparse
import http.server
import json
import re
import shutil
import sys
from functools import partial
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "asr"))
sys.path.insert(0, str(REPO / "eval"))
from common import DATA, MANIFEST  # noqa: E402
from silver import OUT_DIR as SILVER, family  # noqa: E402

VIEW = DATA / "viewer"
CLIPS = DATA / "goldset" / "clips"
OUTPUTS = DATA / "outputs"


def build():
    (VIEW / "clips").mkdir(parents=True, exist_ok=True)
    man = [c for c in json.loads(MANIFEST.read_text())["clips"] if c["kind"] == "speech" and not c.get("exclude")]
    systems = sorted(p.name for p in OUTPUTS.iterdir() if p.is_dir())
    index = []
    for c in man:
        cid = c["clip_id"]
        sil = SILVER / f"{cid}.json"
        silver = json.loads(sil.read_text()) if sil.exists() else None
        outs = {}
        for s in systems:
            p = OUTPUTS / s / f"{cid}.json"
            if p.exists():
                o = json.loads(p.read_text())
                outs[s] = {"family": family(s), "text": o.get("text", ""),
                           "segments": [{"start": x["start"], "end": x["end"], "text": x["text"]}
                                        for x in (o.get("segments") or [])],
                           "words": [[w["start"], w["word"]] for w in (o.get("words") or [])] or None,
                           "context": o.get("context")}
        (VIEW / "clips" / f"{cid}.json").write_text(json.dumps({"clip": c, "systems": outs, "silver": silver},
                                                                ensure_ascii=False))
        st = (silver or {}).get("stats", {})
        index.append({"id": cid, "set": c.get("set", "stratified"), "speaker": c.get("speaker"), "era": c.get("era"),
                      "difficulty": c.get("difficulty"), "title": c.get("title"), "chapter": c.get("book_chapter"),
                      "flags": len((silver or {}).get("regions", [])), "words": st.get("words", 0),
                      "high": st.get("high", 0), "voters": len((silver or {}).get("voters", [])),
                      "book_coverage": ((silver or {}).get("book") or {}).get("coverage")})
    (VIEW / "index.json").write_text(json.dumps({"clips": index, "systems": systems}))
    shutil.copy(Path(__file__).with_name("viewer.html"), VIEW / "index.html")
    print(f"viewer: {len(index)} clips, {len(systems)} systems -> {VIEW}")


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serves data/viewer/ and /audio/<clip>.wav only."""

    def translate_path(self, path):
        path = path.split("?", 1)[0].split("#", 1)[0]
        if path.startswith("/audio/"):
            name = Path(path[len("/audio/"):]).name
            return str(CLIPS / name)
        rel = Path(path.lstrip("/")) if path != "/" else Path("index.html")
        target = (VIEW / rel).resolve()
        return str(target) if str(target).startswith(str(VIEW.resolve())) else str(VIEW / "index.html")

    def do_GET(self):
        """Audio with HTTP Range support: browsers need 206 responses to seek ("play from here")."""
        if not self.path.startswith("/audio/"):
            return super().do_GET()
        path = Path(self.translate_path(self.path))
        if not path.is_file():
            return self.send_error(404)
        size = path.stat().st_size
        start, end = 0, size - 1
        rng = self.headers.get("Range", "")
        m = re.match(r"bytes=(\d*)-(\d*)", rng)
        if m and (m.group(1) or m.group(2)):
            if m.group(1):
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) else size - 1
            else:  # suffix range: last N bytes
                start = max(0, size - int(m.group(2)))
            end = min(end, size - 1)
            if start > end:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                return self.end_headers()
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", "audio/wav")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        try:
            with open(path, "rb") as f:
                f.seek(start)
                left = end - start + 1
                while left > 0:
                    chunk = f.read(min(1 << 16, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass  # the browser cancels range requests while seeking

    def log_message(self, *a):
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-serve", action="store_true")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    build()
    if a.no_serve:
        return
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", a.port), partial(Handler, directory=str(VIEW)))
    print(f"open http://127.0.0.1:{a.port}/  (Ctrl-C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
