"""One command: script -> timeline -> frames (cached) -> mp4 + loudness check.
usage: python tools/render_episode.py examples/demo [--fps 30]
Writes EPISODE/out.mp4 (H.264 + AAC, 1080x1920). / Gera EPISODE/out.mp4.
"""
import argparse, json, os, subprocess, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
ap = argparse.ArgumentParser(); ap.add_argument("episode"); ap.add_argument("--fps", type=int, default=30); a = ap.parse_args()
ep = os.path.abspath(a.episode); fr = os.path.join(ep, "build", "frames"); shutil.rmtree(fr, ignore_errors=True)
py = sys.executable
subprocess.run([py, os.path.join(HERE, "build_audio.py"), ep], check=True)
subprocess.run([py, os.path.join(ROOT, "engine", "rend_cache.py"), ep, fr, "--fps", str(a.fps)], check=True)
out = os.path.join(ep, "out.mp4")
audio = os.path.join(ep, "voice.wav")
music = json.load(open(os.path.join(ep, "script.json"), encoding="utf-8")).get("music")
if music:
    sys.path.insert(0, HERE); from mixmusic import mix
    audio = mix(ep, audio, os.path.join(ep, "build", "mix.wav"), music)
sys.path.insert(0, HERE); from master_audio import mestre
os.makedirs(os.path.join(ep, "build"), exist_ok=True)
quadros = os.path.join(ep, "build", "quadros.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(a.fps), "-i", os.path.join(fr, "f%05d.jpg"), "-c:v", "libx264",
                "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-an", quadros], check=True)
ok, _ = mestre(audio, out, video=quadros, I=-14.0, limit=True, say=print)   # master em 2 passadas + medida no arquivo final
subprocess.run([py, os.path.join(HERE, "qa_audio.py"), out])
print("ok", out)
