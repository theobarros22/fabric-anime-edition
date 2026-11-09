"""Fabric local editor (MVP) / Editor local do Fabric (MVP).

Edit an episode's captions, line order, gaps and background music, then re-render (only changed frames re-render).
It edits script.json (the source of truth); it does NOT touch any other timeline tool.
Runs on 127.0.0.1 only. / Roda só em 127.0.0.1.

usage: python tools/editor.py examples/demo [--port 8777]
Limits (MVP): no adding/removing lines (each line needs its own audio); reorder + text + gap + music only. Undo = last saves.
"""
import argparse, json, mimetypes, os, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = dict(state="idle", log="", started=None)
MAXTEXT = 300


def validate(new, old, ep):
    """Return (ok, error). Only reorder / text / gap / music may change."""
    if not isinstance(new, dict) or not isinstance(new.get("lines"), list): return False, "lines missing"
    oldmap = {l["id"]: l for l in old["lines"]}
    if sorted(l.get("id") for l in new["lines"]) != sorted(oldmap): return False, "line set must stay the same (reorder only)"
    for l in new["lines"]:
        o = oldmap[l["id"]]
        if l.get("wav") != o["wav"] or l.get("speaker") != o["speaker"]: return False, "wav/speaker cannot change"
        if not isinstance(l.get("text", ""), str) or len(l.get("text", "")) > MAXTEXT: return False, f"text too long (max {MAXTEXT})"
        if "gap" in l and not (isinstance(l["gap"], (int, float)) and 0 <= l["gap"] <= 5): return False, "gap must be 0..5 s"
    for k, lo, hi in (("gap", 0, 5), ("lead", 0, 5)):
        if k in new and not (isinstance(new[k], (int, float)) and lo <= new[k] <= hi): return False, f"{k} out of range"
    m = new.get("music")
    if m is not None:
        f = os.path.realpath(os.path.join(ep, str(m.get("file", ""))))
        if not f.startswith(os.path.realpath(ep) + os.sep) or not os.path.isfile(f): return False, "music file must exist inside the episode folder"
        if not (-40 <= float(m.get("volume_db", -18)) <= 0): return False, "music volume_db must be -40..0 (relative to voice)"
        if not (0 <= float(m.get("duck_db", 10)) <= 30): return False, "duck_db must be 0..30"
    return True, ""


def backups(ep):
    d = os.path.join(ep, "build", "history")
    return sorted(os.path.join(d, f) for f in os.listdir(d)) if os.path.isdir(d) else []


def save(ep, new):
    p = os.path.join(ep, "script.json")
    old = json.load(open(p, encoding="utf-8")); ok, err = validate(new, old, ep)
    if not ok: return False, err
    d = os.path.join(ep, "build", "history"); os.makedirs(d, exist_ok=True)
    json.dump(old, open(os.path.join(d, time.strftime("%Y%m%d-%H%M%S") + f"-{int(time.time()*1000)%1000:03d}.json"), "w", encoding="utf-8"), ensure_ascii=False)
    tmp = p + ".tmp"; json.dump(new, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1); os.replace(tmp, p)
    return True, ""


def undo(ep):
    b = backups(ep)
    if not b: return False, "nothing to undo"
    os.replace(b[-1], os.path.join(ep, "script.json")); return True, ""


def render(ep):
    def run():
        STATE.update(state="rendering", log="", started=time.time())
        r = subprocess.run([sys.executable, os.path.join(HERE, "render_episode.py"), ep], capture_output=True, text=True)
        STATE.update(state="done" if r.returncode == 0 else "error", log=(r.stdout + r.stderr)[-1500:])
    if STATE["state"] == "rendering": return False
    threading.Thread(target=run, daemon=True).start(); return True


def make_handler(ep, port):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def _send(self, code, body, ctype="application/json", extra=None):
            b = body if isinstance(body, bytes) else json.dumps(body).encode()
            self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(b)))
            for k, v in (extra or {}).items(): self.send_header(k, v)
            self.end_headers(); self.wfile.write(b)
        def _host_ok(self): return self.headers.get("Host", "").split(":")[0] in ("127.0.0.1", "localhost")
        def do_GET(self):
            if not self._host_ok(): return self._send(403, {"error": "bad host"})
            if self.path in ("/", "/index.html"): return self._send(200, open(os.path.join(HERE, "editor_ui.html"), "rb").read(), "text/html; charset=utf-8")
            if self.path == "/api/script":
                s = json.load(open(os.path.join(ep, "script.json"), encoding="utf-8"))
                s["_files"] = sorted(f"audio/{f}" for f in os.listdir(os.path.join(ep, "audio")) if f.lower().endswith((".wav", ".mp3", ".m4a"))) if os.path.isdir(os.path.join(ep, "audio")) else []
                s["_undo"] = len(backups(ep)); return self._send(200, s)
            if self.path == "/api/status": return self._send(200, dict(STATE, has_video=os.path.isfile(os.path.join(ep, "out.mp4"))))
            if self.path.startswith("/out.mp4"):
                f = os.path.join(ep, "out.mp4")
                if not os.path.isfile(f): return self._send(404, {"error": "no render yet"})
                data = open(f, "rb").read(); rng = self.headers.get("Range")
                if rng and rng.startswith("bytes="):
                    a, _, b = rng[6:].partition("-"); a = int(a or 0); b = int(b) if b else len(data) - 1
                    return self._send(206, data[a:b + 1], "video/mp4", {"Content-Range": f"bytes {a}-{b}/{len(data)}", "Accept-Ranges": "bytes"})
                return self._send(200, data, "video/mp4", {"Accept-Ranges": "bytes"})
            self._send(404, {"error": "not found"})
        def do_POST(self):
            if not self._host_ok() or self.headers.get("X-Fabric") != "1": return self._send(403, {"error": "forbidden"})
            n = int(self.headers.get("Content-Length") or 0)
            if n > 1_000_000: return self._send(413, {"error": "too large"})
            body = self.rfile.read(n)
            if self.path == "/api/script":
                try: new = json.loads(body)
                except Exception: return self._send(400, {"error": "bad json"})
                new = {k: v for k, v in new.items() if not k.startswith("_")}
                ok, err = save(ep, new); return self._send(200 if ok else 400, {"ok": ok, "error": err})
            if self.path == "/api/undo": ok, err = undo(ep); return self._send(200 if ok else 400, {"ok": ok, "error": err})
            if self.path == "/api/render": ok = render(ep); return self._send(200 if ok else 409, {"ok": ok})
            self._send(404, {"error": "not found"})
    return H


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("episode"); ap.add_argument("--port", type=int, default=8777); a = ap.parse_args()
    ep = os.path.abspath(a.episode)
    if not os.path.isfile(os.path.join(ep, "script.json")): sys.exit("ERROR: script.json not found in " + ep)
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(ep, a.port))
    print(f"Fabric editor: http://127.0.0.1:{a.port}  (Ctrl+C to stop)"); srv.serve_forever()


if __name__ == "__main__":
    main()
