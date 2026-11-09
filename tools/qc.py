"""Checagens numéricas do render / Numeric checks for a render (ffmpeg + ffprobe, stdlib).

  qc.py info   video            resumo técnico (tamanho, fps, quadros, codecs, áudio)
  qc.py hook   video [min=0.5]  GANCHO: energia de movimento dos 2 primeiros segundos; FALHA se abre parado
  qc.py sheet  video [cada=2] [colunas=6]   folha de contato (um quadro a cada N s) + índice de tempos
  qc.py phone  video t1,t2,...  quadros em 390 px de largura (conferência de celular)
  qc.py black  video            trechos pretos (>= 0,1 s)
  qc.py freeze video [min=1.5]  trechos congelados
  qc.py dup    video            quadros consecutivos idênticos
  qc.py loud   video            loudness integrada, LRA, pico real e silêncios (< -50 dB, >= 0,5 s)
  qc.py all    video            tudo acima que não precisa de argumento; sai com 1 se o gancho falhar

Saída em $QC_OUT (padrão: ./review/qc-<nome>/). Nada é apagado. Isto MEDE; não ouve nem enxerga: alguém precisa olhar
a folha de contato e ouvir o áudio.

Baseado no qc.py do cinecode (MIT, © 2026 Sarp Yıldız); reescrito e traduzido. Veja THIRD_PARTY.md.
"""
import math, os, re, subprocess, sys
from pathlib import Path

FF = ["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error"]


class Falhou(Exception):
    pass


def chama(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout.replace("\r", ""), r.stderr.replace("\r", "")


def ff(args, diz):
    rc, _, err = chama(FF + args)
    if rc: diz(err.rstrip()); raise Falhou()


def tem_audio(p):
    return bool(chama(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", p])[1].strip())


def duracao(p):
    return float(chama(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p])[1].strip())


def valores(txt, chave):
    return [float(l.split("=")[1]) for l in txt.splitlines() if f"{chave}=" in l]


def info(inp, out, diz):
    diz(f"== info: {inp}")
    diz(chama(["ffprobe", "-v", "error", "-show_entries", "format=duration,size,bit_rate", "-of", "default=nw=1", inp])[1].rstrip())
    v = chama(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
               "stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_read_packets", "-of", "default=nw=1", inp])[1]
    diz(re.sub(r"^nb_read_packets=", "quadros=", v.rstrip(), flags=re.M))
    if tem_audio(inp):
        a = chama(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name,sample_rate,channels,bit_rate", "-of", "default=nw=1", inp])[1]
        diz(re.sub(r"^", "audio_", a.rstrip(), flags=re.M))
    else: diz("audio: nenhum")
    return 0


def hook(inp, out, diz, minimo="0.5"):
    # média da diferença de luma entre quadros seguidos (160 px, cinza) nos 2 primeiros s; todo par de passos >= 0,02
    diz(f"== gancho (os 2 primeiros s precisam se mexer; média mínima {minimo}, movimento >= 0,02 a cada 2 quadros):")
    _, t, _ = chama(["ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-t", "2", "-i", inp, "-vf",
                     "scale=160:-2,format=gray,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-", "-an", "-f", "null", "-"])
    v = valores(t, "YAVG")
    if not v: diz("  nenhum quadro medido: FALHA"); return 1
    media = sum(v) / len(v); baixo = min(max(v[i:i + 2]) for i in range(max(1, len(v) - 1)))
    ok = media >= float(minimo) and baixo >= 0.02
    diz(f"  passos={len(v)} média={media:.2f} mínimo={baixo:.3f}")
    diz("  PASSA" if ok else "  FALHA: abra já com movimento (câmera, ação ou boca); sem título parado nem fade de preto")
    return 0 if ok else 1


def sheet(inp, out, diz, cada="2", colunas="6"):
    n = max(1, math.ceil(duracao(inp) / float(cada))); col = min(int(colunas), n); lin = math.ceil(n / col)
    rotulo = ",drawtext=text='%{pts\\:hms}':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.5" if " drawtext " in chama(["ffmpeg", "-hide_banner", "-filters"])[1] else ""

    def monta(r):
        return ["-y", "-i", inp, "-vf", f"select='isnan(prev_selected_t)+gte(t-prev_selected_t\\,{cada}-0.001)',scale=320:-2{r},tile={col}x{lin}:padding=4:margin=4",
                "-fps_mode", "vfr", "-frames:v", "1", "-update", "1", f"{out}/folha.jpg"]
    rc, _, err = chama(FF + monta(rotulo))
    if rc and rotulo: rc, _, err = chama(FF + monta(""))
    if rc: diz(err.rstrip()); raise Falhou()
    Path(out, "folha-indice.txt").write_text("\n".join(f"linha {i // col + 1} col {i % col + 1}: {int(i * float(cada) // 60):02d}:{i * float(cada) % 60:05.2f}" for i in range(n)) + "\n", encoding="utf-8")
    diz(f"== folha de contato: {out}/folha.jpg (índice: folha-indice.txt, um quadro a cada {cada}s)")
    return 0


def phone(inp, out, diz, tempos=None):
    if not tempos: diz("qc: phone precisa de t1,t2,..."); return 2
    for t in tempos.split(","):
        ff(["-y", "-ss", t, "-i", inp, "-frames:v", "1", "-vf", "scale=390:-2", "-update", "1", f"{out}/celular-{t}s.png"], diz)
    diz(f"== quadros de celular (390 px): {out}/celular-*.png")
    return 0


def black(inp, out, diz):
    diz("== trechos pretos (>= 0,1 s):")
    _, so, se = chama(["ffmpeg", "-hide_banner", "-nostdin", "-i", inp, "-vf", "blackdetect=d=0.1:pic_th=0.98:pix_th=0.10", "-an", "-f", "null", "-"])
    h = re.findall(r"black_start:\S* black_end:\S* black_duration:\S*", se + so); diz("\n".join(h) if h else "nenhum")
    return 0


def freeze(inp, out, diz, minimo="1.5"):
    diz(f"== trechos congelados (>= {minimo} s):")
    _, so, se = chama(["ffmpeg", "-hide_banner", "-nostdin", "-i", inp, "-vf", f"freezedetect=n=-60dB:d={minimo}", "-map", "0:v", "-f", "null", "-"])
    h = re.findall(r"lavfi\.freezedetect\.freeze_[a-z]*: [0-9.]*", se + so); diz("\n".join(h) if h else "nenhum")
    return 0


def dup(inp, out, diz):
    diz("== quadros consecutivos idênticos:")
    _, t, _ = chama(["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error", "-i", inp, "-map", "0:v", "-f", "framemd5", "-"])
    prev, d, i = None, [], 0
    for l in t.splitlines():
        if l.startswith("#"): continue
        h = l.strip().split(",")[-1].strip()
        if h == prev: d.append(i)
        prev, i = h, i + 1
    diz(f"quadros: {i}, repetidos: {len(d)}")
    if d: diz("índices (base 0): " + ", ".join(map(str, d[:50])) + (" ..." if len(d) > 50 else ""))
    return 0


def loud(inp, out, diz):
    if not tem_audio(inp): diz("== loudness: sem faixa de áudio"); return 0
    diz("== loudness (EBU R128, pico real):")
    _, so, se = chama(["ffmpeg", "-hide_banner", "-nostdin", "-i", inp, "-filter_complex", "ebur128=peak=true", "-f", "null", "-"])
    resumo = False
    for l in (se + so).splitlines():
        resumo = resumo or "Summary:" in l
        if resumo and re.search(r"I:|LRA:|Peak:|Threshold:", l): diz("  " + l)
    diz("== silêncios (< -50 dB, >= 0,5 s):")
    _, so, se = chama(["ffmpeg", "-hide_banner", "-nostdin", "-i", inp, "-af", "silencedetect=n=-50dB:d=0.5", "-vn", "-f", "null", "-"])
    h = re.findall(r"silence_start: [0-9.]*|silence_end: [0-9.]* \| silence_duration: [0-9.]*", se + so); diz("\n".join(h) if h else "  nenhum")
    diz("alvos para web: I = -14 LUFS (±1), pico real <= -1,5 dBTP; todo silêncio precisa ser de roteiro")
    return 0


COMANDOS = {"info": info, "hook": hook, "sheet": sheet, "phone": phone, "black": black, "freeze": freeze, "dup": dup, "loud": loud}


def tudo(inp, out, diz, *_):
    rel = []

    def tee(t): diz(t); rel.append(t)
    seg = []; gancho_ok = hook(inp, out, seg.append) == 0
    for passo in (lambda: info(inp, out, tee), lambda: tee("\n".join(seg)), lambda: sheet(inp, out, tee), lambda: black(inp, out, tee),
                  lambda: freeze(inp, out, tee), lambda: dup(inp, out, tee), lambda: loud(inp, out, tee)):
        try: passo()
        except Falhou: pass
    Path(out, "relatorio.txt").write_text("\n".join(rel) + "\n", encoding="utf-8")
    diz(f"== relatório: {out}/relatorio.txt")
    if not gancho_ok: diz("== GANCHO FALHOU (regra dura)"); return 1
    return 0


def main(argv):
    if len(argv) < 2 or argv[0] in ("-h", "--help", "help"): print(__doc__.strip()); return 0 if argv[:1] else 2
    cmd, inp, resto = argv[0], argv[1], argv[2:]
    if cmd != "all" and cmd not in COMANDOS: print(f"qc: comando desconhecido {cmd}", file=sys.stderr); return 2
    if not os.path.isfile(inp): print(f"qc: arquivo não existe: {inp}", file=sys.stderr); return 2
    out = os.environ.get("QC_OUT") or f"./review/qc-{Path(inp).stem}"; os.makedirs(out, exist_ok=True)
    try: return (tudo if cmd == "all" else COMANDOS[cmd])(inp, out, lambda t: print(t, flush=True), *resto)
    except Falhou: return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
