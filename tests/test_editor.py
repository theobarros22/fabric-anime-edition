import copy, http.client, json, os, shutil, sys, threading
import pytest
ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import editor
from http.server import ThreadingHTTPServer


@pytest.fixture
def ep(tmp_path):
    d = tmp_path / "demo"; shutil.copytree(os.path.join(ROOT, "examples", "demo"), d, ignore=shutil.ignore_patterns("build", ".frame_cache", "out.mp4"))
    return str(d)


def load(ep): return json.load(open(os.path.join(ep, "script.json"), encoding="utf-8"))


def test_edit_text_reorder_gap_music_and_undo(ep):
    s = load(ep); s["lines"][0]["text"] = "Edited caption"; s["lines"].reverse(); s["lines"][0]["gap"] = 1.0
    s["music"] = {"file": "audio/music_pad.wav", "volume_db": -20, "duck_db": 8}
    assert editor.save(ep, s) == (True, "")
    assert load(ep)["lines"][0]["id"] == s["lines"][0]["id"] and "music" in load(ep)
    assert editor.undo(ep) == (True, ""); assert "music" not in load(ep)


@pytest.mark.parametrize("mut,why", [
    (lambda s: s["lines"].pop(), "removing a line"),
    (lambda s: s["lines"][0].update(wav="audio/02.wav"), "changing wav"),
    (lambda s: s["lines"][0].update(speaker="X"), "changing speaker"),
    (lambda s: s["lines"][0].update(text="x" * 301), "too long"),
    (lambda s: s["lines"][0].update(gap=99), "gap range"),
    (lambda s: s.update(music={"file": "../../etc/passwd"}), "path traversal"),
    (lambda s: s.update(music={"file": "audio/music_pad.wav", "volume_db": 5}), "volume range"),
])
def test_rejects_bad_edits(ep, mut, why):
    s = copy.deepcopy(load(ep)); mut(s)
    assert editor.save(ep, s)[0] is False, why
    assert load(ep) == json.load(open(os.path.join(ROOT, "examples", "demo", "script.json"), encoding="utf-8"))   # file untouched


def test_http_security(ep):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), editor.make_handler(ep, 0)); port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        def req(m, path, body=None, headers=None):
            c = http.client.HTTPConnection("127.0.0.1", port); c.request(m, path, body, headers or {}); r = c.getresponse(); return r.status
        assert req("GET", "/api/script") == 200
        assert req("POST", "/api/undo") == 403                                             # no X-Fabric header (CSRF)
        assert req("GET", "/api/script", headers={"Host": "evil.example"}) == 403           # DNS-rebinding guard
        assert req("POST", "/api/script", b"{}", {"X-Fabric": "1", "Content-Length": "2"}) == 400
    finally:
        srv.shutdown()
