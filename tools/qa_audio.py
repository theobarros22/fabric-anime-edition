"""Measure loudness / Mede loudness. Target ~ -14 LUFS, true peak <= -1.5 dBTP (measure AFTER AAC).
usage: python tools/qa_audio.py file.mp4   -> prints JSON, exit 1 if outside tolerance.
NOTE: this measures; it does not listen. A human must still listen. / Mede, não ouve: alguém precisa ouvir.
"""
import json, re, subprocess, sys
p = sys.argv[1]
o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", p, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1]); P = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", o)[-1])
ok = abs(I + 14) <= 1.0 and P <= -1.5
print(json.dumps(dict(lufs=I, true_peak_dbfs=P, ok=ok))); sys.exit(0 if ok else 1)
