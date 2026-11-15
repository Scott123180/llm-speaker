#!/usr/bin/env python3
"""Local side-by-side viewer: every system's transcript, the silver reference with its
low-confidence flags, the book passage (for book clips) and the clip audio.

  uv run python eval/viewer.py            # build data/viewer/ and serve http://127.0.0.1:8765
  uv run python eval/viewer.py --no-serve # build only

Settling flags: select a flagged span (or any words; shift-click extends), listen, then mark it correct,
type the correction, or mark it "can't tell". Decisions are saved to eval/goldset/judge.json as
by=listener, override the automatic reference and the LLM review, and the clip is rebuilt at once.

Local only (binds 127.0.0.1): it shows copyrighted book text and archive audio.
Run `uv run python eval/silver.py build` first (and again after new outputs).
"""
import argparse
import http.server
import json
import re
import shutil
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "asr"))
sys.path.insert(0, str(REPO / "eval"))
from common import DATA, MANIFEST  # noqa: E402
import silver  # noqa: E402
from silver import OUT_DIR as SILVER, family  # noqa: E402

VIEW = DATA / "viewer"
CLIPS = DATA / "goldset" / "clips"
OUTPUTS = DATA / "outputs"


def speech_clips():
    return [c for c in json.loads(MANIFEST.read_text())["clips"] if c["kind"] == "speech" and not c.get("exclude")]


def system_names():
    return sorted(p.name for p in OUTPUTS.iterdir() if p.is_dir())


def write_clip(c, systems):
    """data/viewer/clips/{clip}.json -> its index.json entry."""
    cid = c["clip_id"]
    sil = SILVER / f"{cid}.json"
    ref = json.loads(sil.read_text()) if sil.exists() else None
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
    (VIEW / "clips" / f"{cid}.json").write_text(json.dumps({"clip": c, "systems": outs, "silver": ref},
                                                            ensure_ascii=False))
    st = (ref or {}).get("stats", {})
    return {"id": cid, "set": c.get("set", "stratified"), "speaker": c.get("speaker"), "era": c.get("era"),
            "difficulty": c.get("difficulty"), "title": c.get("title"), "chapter": c.get("book_chapter"),
            "flags": len((ref or {}).get("regions", [])), "words": st.get("words", 0),
            "high": st.get("high", 0), "voters": len((ref or {}).get("voters", [])),
            "listened": sum(1 for t in (ref or {}).get("tokens", []) if t.get("by") == "listener"),
            "book_coverage": ((ref or {}).get("book") or {}).get("coverage")}


def build():
    (VIEW / "clips").mkdir(parents=True, exist_ok=True)
    systems = system_names()
    index = [write_clip(c, systems) for c in speech_clips()]
    (VIEW / "index.json").write_text(json.dumps({"clips": index, "systems": systems}))
    shutil.copy(Path(__file__).with_name("viewer.html"), VIEW / "index.html")
    print(f"viewer: {len(index)} clips, {len(systems)} systems -> {VIEW}")


# ------------------------------------------------------------------ settling flags

LOCK = threading.Lock()
_CLIPS = {}


def clips():
    if not _CLIPS:
        _CLIPS.update({c.id: c for c in silver.load_clips()})
    return _CLIPS


def rebuild(cid):
    """Re-apply the decisions for one clip and refresh its silver reference and viewer files."""
    c = clips()[cid]
    c.judge = silver.load_judge().get(cid, [])
    ref = silver.build(c)
    ref["regions"] = silver.regions(ref)
    (SILVER / f"{cid}.json").write_text(json.dumps(ref, ensure_ascii=False))
    entry = write_clip(next(m for m in speech_clips() if m["clip_id"] == cid), system_names())
    idx = json.loads((VIEW / "index.json").read_text())
    idx["clips"] = [entry if e["id"] == cid else e for e in idx["clips"]]
    (VIEW / "index.json").write_text(json.dumps(idx))
    return entry


def decide(body):
    cid, verdict = str(body.get("clip", "")), body.get("verdict")
    if cid not in clips() or verdict not in ("keep", "fix", "unclear"):
        raise ValueError("unknown clip or verdict")
    toks = json.loads((SILVER / f"{cid}.json").read_text())["tokens"]
    a, b = int(body["start"]), int(body["end"])
    if not 0 <= a <= b < len(toks) or b - a > 2000:
        raise ValueError("bad span")
    frm = " ".join(t["w"] for t in toks[a:b + 1] if t["n"])
    to = " ".join(str(body.get("to", "")).split())[:2000] if verdict == "fix" else frm
    d = {"id": "L" + uuid.uuid4().hex[:10], "clip": cid, "t": toks[a]["t"],
         "before": " ".join([t["w"] for t in toks[:a] if t["n"]][-3:]), "from": frm,
         "after": " ".join([t["w"] for t in toks[b + 1:] if t["n"]][:3]),
         "verdict": verdict, "to": to, "why": " ".join(str(body.get("why", "")).split())[:500],
         "by": "listener", "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    doc = json.loads(silver.JUDGE.read_text()) if silver.JUDGE.exists() else {"decisions": []}
    silver.save_judge(doc["decisions"] + [d])
    return {"ok": True, "id": d["id"], "entry": rebuild(cid)}


def undo(body):
    did = str(body.get("id", ""))
    doc = json.loads(silver.JUDGE.read_text())
    hit = [d for d in doc["decisions"] if d.get("id") == did and d.get("by") == "listener"]
    if not hit:
        raise ValueError("no such listener decision")
    silver.save_judge([d for d in doc["decisions"] if d not in hit])
    return {"ok": True, "entry": rebuild(hit[0]["clip"])}


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

    def do_POST(self):
        """/api/decide and /api/undo. The custom header makes browsers preflight cross-site requests
        (which this server never approves), so other web pages can't write decisions."""
        route = {"/api/decide": decide, "/api/undo": undo}.get(self.path)
        origin = self.headers.get("Origin")
        if route is None:
            return self.send_error(404)
        if self.headers.get("X-Viewer") != "1" or (origin and urlparse(origin).hostname not in ("127.0.0.1", "localhost")):
            return self.send_error(403)
        n = int(self.headers.get("Content-Length") or 0)
        if not 0 < n <= 100_000:
            return self.send_error(413)
        try:
            with LOCK:
                res = route(json.loads(self.rfile.read(n)))
            code = 200
        except (ValueError, KeyError, TypeError) as e:
            res, code = {"ok": False, "error": str(e)}, 400
        out = json.dumps(res).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(out)

    def end_headers(self):
        if self.path.endswith(".json"):
            self.send_header("Cache-Control", "no-store")  # clips change when flags are settled
        super().end_headers()

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
    t0 = time.time()
    clips()  # load every system's output once, for fast rebuilds when a flag is settled
    print(f"loaded {len(_CLIPS)} clips in {time.time() - t0:.0f} s", flush=True)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", a.port), partial(Handler, directory=str(VIEW)))
    print(f"open http://127.0.0.1:{a.port}/  (Ctrl-C to stop)", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
