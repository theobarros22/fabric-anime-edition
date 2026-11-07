"""End-to-end smoke test: demo episode renders 12 frames; frames are cached on the 2nd run."""
import json, os, shutil, subprocess, sys, pytest
pytest.importorskip("playwright"); pytest.importorskip("soundfile")
ROOT = os.path.join(os.path.dirname(__file__), "..")


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg missing")
def test_demo(tmp_path):
    ep = tmp_path / "demo"; shutil.copytree(os.path.join(ROOT, "examples", "demo"), ep, ignore=shutil.ignore_patterns("build", ".frame_cache", "out.mp4"))
    shutil.copy(os.path.join(ROOT, "characters", "personagens.js"), ep)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_audio.py"), str(ep)], check=True)
    out = []
    for _ in range(2):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "engine", "rend_cache.py"), str(ep), str(tmp_path / "fr"), "--n", "12"], capture_output=True, text=True, check=True)
        out.append(json.loads(r.stdout.strip().splitlines()[-1]))
    assert out[0]["rendered"] > 0 and out[1]["rendered"] == 0 and out[1]["reused"] == 12
