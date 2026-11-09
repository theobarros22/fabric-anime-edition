"""Testes de palavras.py, master_audio.py, qc.py e textcheck.py (sintéticos, sem rede)."""
import json, os, shutil, subprocess, sys
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
FF = shutil.which("ffmpeg") is not None


# ---------- palavras ----------
def test_estimar_respeita_pausas_reais():
    from palavras import estimar
    # 3 rajadas de voz separadas por pausas de 0,5 s (15 quadros): 20 + 15 + 20 + 15 + 20 quadros
    env = [0.8] * 20 + [0.0] * 15 + [0.8] * 20 + [0.0] * 15 + [0.8] * 20
    w = estimar("Primeira frase aqui. Segunda frase aqui. Terceira frase aqui.", env, len(env) / 30)
    assert [x["w"] for x in w][:3] == ["Primeira", "frase", "aqui."]
    assert abs(w[2]["t1"] - 20 / 30) < 0.12                     # a 1ª frase termina onde a voz termina
    assert w[3]["t0"] >= 35 / 30 - 0.12                         # a 2ª só começa depois da pausa
    assert all(a["t1"] <= b["t0"] + 1e-6 for a, b in zip(w, w[1:]))   # monotônico, sem sobrepor
    assert all(x["t1"] > x["t0"] for x in w)


def test_estimar_sem_pausa_espalha_por_peso():
    from palavras import estimar
    w = estimar("a internacionalização", [0.5] * 60, 2.0)
    assert (w[1]["t1"] - w[1]["t0"]) > 3 * (w[0]["t1"] - w[0]["t0"])   # palavra longa dura bem mais


def test_ler_json_formatos(tmp_path):
    from palavras import ler_json
    f1 = tmp_path / "a.json"; f1.write_text(json.dumps([{"w": "Oi", "s": 0, "e": 0.3}]))
    f2 = tmp_path / "b.json"; f2.write_text(json.dumps([["Oi", 0, 0.3, 0.9]]))
    f3 = tmp_path / "c.json"; f3.write_text(json.dumps({"segments": [{"words": [{"word": " Oi", "start": 0, "end": 0.3}]}]}))
    for f in (f1, f2, f3): assert ler_json(str(f)) == [{"w": "Oi", "t0": 0.0, "t1": 0.3}]


# ---------- master_audio ----------
@pytest.mark.skipif(not FF, reason="ffmpeg ausente")
def test_master_audio_acerta_alvo_com_video(tmp_path):
    from master_audio import mestre
    mix = tmp_path / "mix.wav"; vid = tmp_path / "v.mp4"; out = tmp_path / "o.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=220:d=4,volume=-30dB,apulsator=hz=1.5", str(mix)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=s=160x90:d=4:r=30", "-pix_fmt", "yuv420p", str(vid)], check=True)
    ok, v = mestre(str(mix), str(out), video=str(vid), limit=True, say=lambda *_: None)
    assert ok and abs(float(v["I"]) + 14) <= 1.0 and float(v["Peak"]) <= -1.5


# ---------- qc ----------
@pytest.mark.skipif(not FF, reason="ffmpeg ausente")
def test_qc_gancho_distingue_movimento_de_quadro_parado(tmp_path):
    import qc
    mov = tmp_path / "mov.mp4"; par = tmp_path / "par.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "mandelbrot=s=160x90:r=30", "-t", "3", "-pix_fmt", "yuv420p", str(mov)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=160x90:d=3:r=30", "-pix_fmt", "yuv420p", str(par)], check=True)
    assert qc.hook(str(mov), str(tmp_path), lambda *_: None) == 0
    assert qc.hook(str(par), str(tmp_path), lambda *_: None) == 1


# ---------- textcheck ----------
def _t(s, x, y, w, h): return {"s": s, "x": x, "y": y, "w": w, "h": h, "id": ""}


def test_textcheck_detecta_fora_sobreposicao_zona_e_leitura():
    from textcheck import analisa
    seguro = (220, 380, 120)
    am = [(0.0, {"texts": [_t("CORTADO", 900, 800, 300, 80), _t("A", 100, 700, 300, 80), _t("B", 150, 720, 300, 80), _t("BAIXO", 100, 1700, 300, 80)], "chars": []}),
          (0.25, {"texts": [_t("CORTADO", 900, 800, 300, 80)], "chars": []})]
    tipos = {a[0] for a in analisa(am, 1080, 1920, seguro, None, [], 0.25)}
    assert {"FORA", "SOBREPOE", "ZONA", "LEITURA"} <= tipos


def test_textcheck_rosto_e_permitir():
    from textcheck import analisa
    am = [(1.0, {"texts": [_t("OLA MUNDO COMPRIDO", 400, 520, 300, 80)], "chars": [{"c": "gengivao", "x": 380, "y": 500, "w": 340, "h": 400}]})] * 6
    assert any(a[0] == "ROSTO" for a in analisa(am, 1080, 1920, (220, 380, 120), None, [], 0.25))
    assert not any(a[0] == "ROSTO" for a in analisa(am, 1080, 1920, (220, 380, 120), None, [(0, 5)], 0.25))
