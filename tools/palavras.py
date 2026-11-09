"""Tempo de cada palavra da fala / Word-level timing for a voice line.

Duas fontes, na ordem / Two sources, in order:
  1. palavras/NN.json  (tempos reais de um ASR, ex.: faster-whisper)  -> exatos ao quadro
  2. envelope de volume da própria fala + texto do roteiro            -> estimativa (±0,1-0,2 s)

A estimativa usa as pausas reais do áudio (trechos sem voz) para dividir o texto, preferindo cortar onde o
roteiro tem pontuação, e espalha as palavras de cada trecho pelo peso (palavra longa dura mais). Depois encosta
cada fronteira no menor volume vizinho. Não substitui um ASR: confira a sincronia de cues duros ouvindo.

Ideias de motionforge/tools/word_timings.py (MIT) e cinecode/scripts/captions.py (MIT); código escrito para este
projeto, em PT-BR. Veja THIRD_PARTY.md.

Formato aceito em palavras/NN.json (tempos relativos ao arquivo build/NN_lv.wav gerado pelo build_audio):
  [{"w":"Urgente","s":0.0,"e":0.4}, ...]  ou  [["Urgente",0.0,0.4], ...]  ou  {"words":[{"word","start","end"}]}
Gerar com faster-whisper:  python tools/palavras.py cmd episodio/build/01_lv.wav
"""
import json, os, re, shlex, sys

FPS = 30


def _peso(p):
    letras = len(re.sub(r"[^\w]", "", p)) or 1
    pausa = 1.2 if re.search(r"[.!?…]$", p) else 0.6 if re.search(r"[,;:]$", p) else 0.0
    return max(2, letras) + 1.5 + pausa


def _pausas(env, minimo=4):
    """Trechos [i,j) de quadros sem voz dentro da fala (não conta o começo nem o fim)."""
    n = len(env); out = []; i = 0
    while i < n:
        if env[i] <= 0:
            j = i
            while j < n and env[j] <= 0: j += 1
            if i > 0 and j < n and j - i >= minimo: out.append((i, j))
            i = j
        else: i += 1
    return out


def _corte_pontuacao(palavras, alvo, lo, hi):
    """Aproxima o corte de uma palavra que termina frase/oração, se houver uma perto."""
    alcance = max(2, round(len(palavras) * 0.08))
    for padrao in (r"[.!?…]$", r"[,;:]$"):
        melhor = None
        for j in range(max(lo + 1, alvo - alcance), min(hi, alvo + alcance) + 1):
            if re.search(padrao, palavras[j - 1]) and (melhor is None or abs(j - alvo) < abs(melhor - alvo)): melhor = j
        if melhor is not None: return melhor
    return alvo


def _espalha(ini, fim, palavras):
    pesos = [_peso(p) for p in palavras]; tot = sum(pesos) or 1.0; t = ini; out = []
    for p, k in zip(palavras, pesos):
        d = (fim - ini) * k / tot; out.append([p, t, t + d]); t += d
    return out


def estimar(txt, env, dur, fps=FPS):
    """-> [{'w','t0','t1'}] em segundos relativos ao começo da fala (0..dur)."""
    palavras = txt.split()
    if not palavras: return []
    n = len(env)
    if n < 2: return [{"w": p, "t0": round(dur * i / len(palavras), 3), "t1": round(dur * (i + 1) / len(palavras), 3)} for i, p in enumerate(palavras)]
    pausas = _pausas(env)
    trechos = [(0 if i == 0 else pausas[i - 1][1], pausas[i][0] if i < len(pausas) else n) for i in range(len(pausas) + 1)]  # trechos de voz entre pausas
    trechos = [(a, b) for a, b in trechos if b > a] or [(0, n)]
    voz = sum(b - a for a, b in trechos); usadas = 0; acc = 0; saida = []
    for k, (a, b) in enumerate(trechos):
        acc += b - a
        ate = len(palavras) if k == len(trechos) - 1 else max(usadas, min(len(palavras), _corte_pontuacao(palavras, round(len(palavras) * acc / voz), usadas, len(palavras) - 1)))
        saida += _espalha(a / fps, b / fps, palavras[usadas:ate]); usadas = ate
    # encosta cada fronteira entre palavras vizinhas (dentro do mesmo trecho) no menor volume por perto
    for i in range(1, len(saida)):
        if abs(saida[i][1] - saida[i - 1][2]) > 1e-6: continue          # fronteira de pausa: já exata
        q = round(saida[i][1] * fps); cand = [x for x in range(max(0, q - 3), min(n, q + 4))]
        if not cand: continue
        melhor = min(cand, key=lambda x: (env[x], abs(x - q))) / fps
        if saida[i - 1][1] + 0.08 < melhor < saida[i][2] - 0.08: saida[i - 1][2] = saida[i][1] = melhor
    return [{"w": p, "t0": round(a, 3), "t1": round(b, 3)} for p, a, b in saida]


def ler_json(caminho):
    d = json.load(open(caminho, encoding="utf-8"))
    if isinstance(d, dict): d = d.get("words") or [w for s in d.get("segments", []) for w in s.get("words", [])]
    out = []
    for w in d:
        if isinstance(w, (list, tuple)): p, a, b = w[0], float(w[1]), float(w[2])
        else: p, a, b = w.get("w", w.get("word", w.get("text", ""))), float(w.get("s", w.get("start"))), float(w.get("e", w.get("end")))
        p = p.strip()
        if p and b > a: out.append({"w": p, "t0": round(a, 3), "t1": round(b, 3)})
    return out


def palavras_da_fala(ep, linha, env, dur):
    """Prefere palavras/NN.json; senão estima. Devolve (lista, origem)."""
    j = os.path.join(ep, "palavras", f"{linha['n']}.json")
    if os.path.exists(j):
        try:
            w = ler_json(j)
            if w: return w, "asr"
        except Exception: pass
    return estimar(linha.get("txt", ""), env, dur), "estimado"


def cmd(wav, idioma="pt"):
    base = os.path.splitext(wav)[0]; q = shlex.quote
    cod = (f"from faster_whisper import WhisperModel as M; import json; s,_=M('small').transcribe({wav!r}, language={idioma!r}, word_timestamps=True); "
           f"json.dump([[w.word,w.start,w.end] for x in s for w in x.words], open({base + '.json'!r},'w'))")
    print("# precisa de: pip install faster-whisper   (baixa o modelo na 1ª vez)\n" + f"python -c {q(cod)}\n"
          f"# depois copie {base}.json para <episodio>/palavras/<NN>.json")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "cmd": cmd(sys.argv[2])
    else: print(__doc__)
