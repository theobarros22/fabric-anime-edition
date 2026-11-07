"""One command: script -> timeline -> frames (cached) -> mp4 + loudness check.
usage: python tools/render_episode.py examples/demo [--fps 30]
Writes EPISODE/out.mp4 (H.264 + AAC, 1080x1920). / Gera EPISODE/out.mp4.
"""
import argparse, os, subprocess, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
ap = argparse.ArgumentParser(); ap.add_argument("episode"); ap.add_argument("--fps", type=int, default=30); a = ap.parse_args()
ep = os.path.abspath(a.episode); fr = os.path.join(ep, "build", "frames"); shutil.rmtree(fr, ignore_errors=True)
py = sys.executable
subprocess.run([py, os.path.join(HERE, "build_audio.py"), ep], check=True)
subprocess.run([py, os.path.join(ROOT, "engine", "rend_cache.py"), ep, fr, "--fps", str(a.fps)], check=True)
out = os.path.join(ep, "out.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(a.fps), "-i", os.path.join(fr, "f%05d.jpg"), "-i", os.path.join(ep, "voice.wav"),
                "-af", "loudnorm=I=-14:TP=-2.5:LRA=11", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", out], check=True)
subprocess.run([py, os.path.join(HERE, "qa_audio.py"), out])
print("ok", out)
