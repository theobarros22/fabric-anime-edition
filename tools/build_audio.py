"""Build timeline + voice track from a script / Monta timeline e faixa de voz a partir do roteiro.

script.json:  {"gap":0.38, "lead":0.7, "target_lufs":-17, "lines":[{"id":"01","speaker":"TITO","text":"...","wav":"audio/01.wav"}]}
For each line: trims silence at both ends, matches loudness to target_lufs, computes a 30 fps mouth
envelope (RMS, NOT syllable-accurate), per-word times ("words": from palavras/NN.json if present, else
estimated from the envelope, see tools/palavras.py) and lays lines out one after another.
Outputs in the episode dir: timeline.json, timeline.js (window.TL=...), voice.wav.
usage: python tools/build_audio.py examples/demo
Requires: ffmpeg, numpy, soundfile.
"""
import json, os, re, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palavras import palavras_da_fala


def run(*a): subprocess.run(a, check=True, capture_output=True)


def lufs(p):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", p, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1])


def main(ep):
    S = json.load(open(os.path.join(ep, "script.json"), encoding="utf-8"))
    gap, t, tgt = S.get("gap", 0.38), S.get("lead", 0.7), S.get("target_lufs", -17.0)
    work = os.path.join(ep, "build"); os.makedirs(work, exist_ok=True); lines = []
    for L in S["lines"]:
        src = os.path.join(ep, L["wav"]); a = os.path.join(work, f"{L['id']}_trim.wav"); b = os.path.join(work, f"{L['id']}_lv.wav")
        run("ffmpeg", "-y", "-i", src, "-af",
            "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
            "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.12,areverse,aresample=44100", "-ac", "1", a)
        g = tgt - lufs(a)
        run("ffmpeg", "-y", "-i", a, "-af", f"volume={g:.2f}dB,alimiter=limit=0.89:level=disabled", b)
        x, sr = sf.read(b); d = len(x) / sr; hop = int(sr / 30)
        env = np.array([np.sqrt(np.mean(x[k:k + hop] ** 2)) for k in range(0, len(x), hop)])
        hi = np.percentile(env, 92) + 1e-9; m = np.clip(env / hi, 0, 1); m = np.where(m < 0.12, 0, m)
        ln = dict(n=L["id"], v=L["speaker"], txt=L.get("text", ""), start=round(t, 3), dur=round(d, 3),
                  env=[round(float(q), 2) for q in m], wav=os.path.relpath(b, ep))
        w, origem = palavras_da_fala(ep, ln, ln["env"], d)           # tempo por palavra (relativo ao início da fala)
        ln["words"] = [dict(w=q["w"], t0=round(t + q["t0"], 3), t1=round(t + q["t1"], 3)) for q in w]; ln["words_src"] = origem
        lines.append(ln)
        t += d + L.get("gap", gap)   # optional per-line gap after this line
    total = round(t + 1.0, 2); tl = dict(lines=lines, total=total)
    json.dump(tl, open(os.path.join(ep, "timeline.json"), "w", encoding="utf-8"))
    open(os.path.join(ep, "timeline.js"), "w", encoding="utf-8").write("window.TL=" + json.dumps(tl) + ";")
    vo = np.zeros(int(total * 44100) + 44100)
    for l in lines:
        x, sr = sf.read(os.path.join(ep, l["wav"])); s = int(l["start"] * 44100); vo[s:s + len(x)] += x
    sf.write(os.path.join(ep, "voice.wav"), vo, 44100)
    print(f"ok: {len(lines)} lines, {total}s")


if __name__ == "__main__":
    main(sys.argv[1])
