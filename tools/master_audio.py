"""Master de áudio em 2 passadas, linear / Two-pass LINEAR loudness master (ffmpeg, stdlib).

Passada 1 mede; passada 2 aplica UM ganho fixo (linear=true), então a dinâmica da mix fica intacta. Se o LRA
medido passar do alvo o ffmpeg troca em silêncio para o modo dinâmico (compressor): este script avisa.
Com --video o pico é mirado 0,5-0,7 dB abaixo porque o AAC sobe o pico; depois mede o ARQUIVO FINAL e, se o
pico passar do teto, baixa o limitador e codifica de novo.

uso:  master_audio.py mix.wav master.wav
      master_audio.py voice.wav episodio.mp4 --video quadros.mp4 [--I -14] [--TP -1.5] [--LRA 20] [--limit]
Saída: código 0 = dentro do alvo (I ±1 LU, pico <= TP); 1 = fora do alvo. Mede, não ouve: alguém precisa ouvir.

Baseado no master_audio.py do cinecode (MIT, © 2026 Sarp Yıldız); reescrito/traduzido para este projeto.
Veja THIRD_PARTY.md.
"""
import argparse, json, re, subprocess, sys


def roda(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode: sys.exit(f"ffmpeg falhou:\n{p.stderr[-3000:]}")
    return p.stderr


def ultimo_json(txt):
    b = re.findall(r"\{[^{}]*\}", txt, re.S)
    if not b: sys.exit("não achei o JSON do loudnorm na saída do ffmpeg")
    return json.loads(b[-1])


def mede_arquivo(path):
    err = roda(["ffmpeg", "-hide_banner", "-nostdin", "-i", path, "-filter_complex", "ebur128=peak=true", "-f", "null", "-"])
    resumo = err[err.rfind("Summary:"):]
    g = lambda k: (re.search(rf"{k}:\s+(-?[\d.]+|-inf)", resumo) or [None, "?"])[1]
    return {k: g(k) for k in ("I", "LRA", "Peak")}


def duracao(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout.strip() or 0)


def mestre(mix, saida, video=None, I=-14.0, TP=None, LRA=20.0, limit=False, say=print):
    teto = TP if TP is not None else -1.5                       # o que o QC exige do arquivo final (qa_audio.py)
    mira = TP if TP is not None else (-2.0 if video else -1.0)  # AAC sobe ~0,5-0,7 dB: mira mais baixo
    alvo = f"I={I}:TP={mira}:LRA={LRA}"
    mede = lambda pre: ultimo_json(roda(["ffmpeg", "-hide_banner", "-nostdin", "-i", mix, "-af", f"{pre}loudnorm={alvo}:print_format=json", "-f", "null", "-"]))
    pre = ""; m = mede(pre)
    say(f"passada 1: I={m['input_i']} LUFS  pico={m['input_tp']} dBTP  LRA={m['input_lra']} LU")
    try: mudo = not float(m["input_i"]) > -70
    except ValueError: mudo = True
    if mudo: sys.exit("trilha sem som acima de -70 LUFS: nada para normalizar")
    ganho = I - float(m["input_i"]); ceil = mira - 1.5

    def limitado(ganho, ceil):
        for _ in range(4):
            pre = f"volume={ganho:.2f}dB,alimiter=limit={10 ** (ceil / 20):.4f}:attack=5:release=60:level=0:latency=1,"
            m = mede(pre)
            say(f"limitador: +{ganho:.2f} dB e teto {ceil:.1f} dBFS -> I={m['input_i']} LUFS pico={m['input_tp']} dBTP")
            sobra = float(m["input_tp"]) + (I - float(m["input_i"])) - (mira - 0.3)
            if sobra <= 0: break
            ceil -= sobra + 0.3; ganho += sobra + 0.3
        return pre, m, ganho, ceil

    if limit and float(m["input_tp"]) + ganho > mira - 0.5: pre, m, ganho, ceil = limitado(ganho, ceil)
    for tent in range(4):
        if float(m["input_lra"]) > LRA: say(f"AVISO: LRA {m['input_lra']} > {LRA}: o loudnorm roda em modo DINÂMICO. Suba --LRA.")
        af = (f"{pre}loudnorm={alvo}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
              f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=json")
        if video:
            vd, md = duracao(video), duracao(mix)
            if tent == 0 and abs(vd - md) > 0.1: say(f"AVISO: mix {md:.2f} s e imagem {vd:.2f} s; a imagem manda ({'silêncio completa o fim' if md < vd else 'áudio cortado no último quadro'})")
            cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-i", video, "-i", mix, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                   "-af", af + ",apad", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-shortest", saida]
        else:
            cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-i", mix, "-af", af, "-ar", "48000", "-c:a", "pcm_s24le", saida]
        r = ultimo_json(roda(cmd)); modo = r.get("normalization_type", "?")
        say(f"passada 2: modo={modo}  saída I={r['output_i']}  pico={r['output_tp']}  LRA={r['output_lra']}")
        if modo != "linear": say("AVISO: rodou em modo dinâmico; a mix foi comprimida. Baixe os picos antes ou suba --LRA.")
        v = mede_arquivo(saida); say(f"medido no arquivo final: I={v['I']} LUFS  LRA={v['LRA']} LU  pico={v['Peak']} dBFS")
        try: ok_i, pico = abs(float(v["I"]) - I) <= 1.0, float(v["Peak"])
        except ValueError: break
        if ok_i and pico <= teto: return True, v
        if not ok_i or tent == 3: return False, v
        sobra = pico - teto + 0.3
        say(f"pico codificado {sobra - 0.3:.1f} dB acima: limitador {sobra:.1f} dB mais baixo e codifica de novo")
        pre, m, ganho, ceil = limitado(ganho + sobra, ceil - sobra)
    return True, v


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mix"); ap.add_argument("saida"); ap.add_argument("--video")
    ap.add_argument("--I", type=float, default=-14.0); ap.add_argument("--TP", type=float, default=None)
    ap.add_argument("--LRA", type=float, default=20.0); ap.add_argument("--limit", action="store_true")
    a = ap.parse_args()
    ok, v = mestre(a.mix, a.saida, a.video, a.I, a.TP, a.LRA, a.limit)
    print("OK" if ok else "FALHOU: fora do alvo (I ±1 LU, pico <= TP). Baixe os picos da mix e rode de novo.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
