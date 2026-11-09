"""Mix background music under the voice with ducking / Mistura trilha de fundo sob a voz com ducking.

script.json:  "music": {"file":"audio/music.wav", "volume_db": -18, "duck_db": 10}   (volume_db is relative to the voice; file must be inside the episode dir)
Music is looped/trimmed to the voice length; it is compressed (sidechain) by the voice so speech stays on top.
Measured, not heard: check loudness with tools/qa_audio.py and LISTEN. / Medido, não ouvido: confira e OUÇA.
"""
import os, re, subprocess


def lufs(path):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", o)
    return float(m[-1]) if m else -70.0


def mix(ep, voice_wav, out_wav, music):
    f = os.path.realpath(os.path.join(ep, music["file"]))
    if not f.startswith(os.path.realpath(ep) + os.sep) or not os.path.isfile(f):
        raise SystemExit("ERROR: music file must exist inside the episode folder")
    # volume_db is RELATIVE TO THE VOICE (loudness-matched first): -18 = music 18 LU under the speech
    vol = lufs(voice_wav) - lufs(f) + float(music.get("volume_db", -18)); duck = float(music.get("duck_db", 10))
    # ratio from duck depth: threshold low, ratio high => ~duck dB reduction while voice is present
    ratio = max(2.0, min(20.0, 1 + duck / 2))
    flt = (f"[1:a]aloop=loop=-1:size=2e9,volume={vol}dB[m];[0:a]asplit=2[v][k];"
           f"[m][k]sidechaincompress=threshold=0.02:ratio={ratio:.1f}:attack=20:release=400[md];"
           f"[v][md]amix=inputs=2:duration=first:normalize=0[o]")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", voice_wav, "-i", f, "-filter_complex", flt, "-map", "[o]", out_wav],
                       capture_output=True, text=True)
    if r.returncode: raise SystemExit("ERROR ffmpeg:\n" + r.stderr[-800:])
    return out_wav
