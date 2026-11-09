"""Texto cortado, sobreposto, em zona insegura ou rápido demais / Text that is cut, overlapping, unsafe or too brief.

Mede o SVG de verdade (Playwright): chama window.R(t) em vários instantes e lê a caixa de cada <text>.
  1. FORA     a caixa sai do quadro
  2. SOBREPOE duas caixas de texto se cobrem (>25% da menor)
  3. ZONA     a caixa entra na faixa coberta pela interface do celular (topo / base / lateral direita)
  4. ROSTO    o texto cobre a parte de cima de um personagem (marcado com data-char em busto())
  5. LEITURA  um texto (mesmo id + mesma frase) fica menos tempo na tela do que se precisa para ler:
              necessário = 0,6 s + letras / 14 por segundo, mínimo 1,2 s

uso:  python tools/textcheck.py EPISODIO [--cada 0.25] [--seguro 220,380,120] [--tamanho 1080x1920]
                                         [--ignorar-y 1280,1480] [--permitir 0-2.5] [--json saida.json]
  --seguro T,B,D   zonas do celular em px (topo, base, direita) a 1080x1920 (escala para outros tamanhos)
  --ignorar-y A,B  não confere LEITURA de textos cuja caixa está entre A e B em y (legenda que segue a voz)
  --permitir A-B   ignora avisos entre A e B segundos (pode repetir)
Sai com 1 se achar FORA ou SOBREPOE; ZONA, ROSTO e LEITURA são avisos. Mede, não enxerga: veja a folha de contato.

Ideia de motionforge/tools/textcheck.mjs e readcheck.mjs (MIT); reescrito para SVG do window.R(t). Veja THIRD_PARTY.md.
"""
import argparse, json, os, sys

JS = r"""() => { const out=[]; const els=[...document.querySelectorAll('text')];
 const chars=[...document.querySelectorAll('[data-char]')].map(e=>{const r=e.getBoundingClientRect();return {c:e.getAttribute('data-char'),x:r.left,y:r.top,w:r.width,h:r.height}});
 els.forEach((e,i)=>{const r=e.getBoundingClientRect(); const s=(e.textContent||'').replace(/\s+/g,' ').trim(); if(!s||r.width<1) return;
   out.push({s, x:r.left, y:r.top, w:r.width, h:r.height, id:e.getAttribute('id')||''}) });
 return {texts:out, chars} }"""


def inter(a, b):
    w = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]); h = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
    return max(0, w) * max(0, h)


def analisa(amostras, W, H, seguro, ignorar_y, permitir, cada):
    avisos = []; T, B, D = seguro; vivos = {}
    ok = lambda t: not any(a <= t <= b for a, b in permitir)
    for t, d in amostras:
        tx = d["texts"]
        for e in tx:
            if not ok(t): continue
            if e["x"] < -2 or e["y"] < -2 or e["x"] + e["w"] > W + 2 or e["y"] + e["h"] > H + 2:
                avisos.append(("FORA", t, e["s"], "caixa sai do quadro"))
            if e["y"] < T and e["y"] + e["h"] > 0 and e["h"] > 0 and not (e["y"] + e["h"] <= T * 0.5):
                avisos.append(("ZONA", t, e["s"], f"entra nos {T:.0f}px do topo"))
            if e["y"] + e["h"] > H - B and e["y"] < H: avisos.append(("ZONA", t, e["s"], f"entra nos {B:.0f}px da base"))
            if e["x"] + e["w"] > W - D and e["x"] < W: avisos.append(("ZONA", t, e["s"], f"entra nos {D:.0f}px da direita"))
            for c in d["chars"]:
                topo = {"x": c["x"], "y": c["y"], "w": c["w"], "h": c["h"] * 0.6}
                if inter(e, topo) > 0.12 * min(e["w"] * e["h"], topo["w"] * topo["h"]):
                    avisos.append(("ROSTO", t, e["s"], f"cobre a parte de cima de {c['c']}"))
        for i in range(len(tx)):
            for j in range(i + 1, len(tx)):
                a, b = tx[i], tx[j]
                if ok(t) and inter(a, b) > 0.25 * min(a["w"] * a["h"], b["w"] * b["h"]) and a["s"] != b["s"]:
                    avisos.append(("SOBREPOE", t, f"{a['s']} × {b['s']}", "caixas se cobrem"))
        for e in tx:
            if ignorar_y and ignorar_y[0] <= e["y"] + e["h"] / 2 <= ignorar_y[1]: continue
            k = (e["id"], e["s"]); vivos.setdefault(k, []).append(t)
    for (_, s), ts in vivos.items():                                 # primeiro trecho contínuo de cada texto
        ts.sort(); ini = fim = ts[0]
        for t in ts[1:]:
            if t - fim <= cada * 1.5: fim = t
            else: break
        vis = fim - ini + cada; letras = sum(c.isalnum() for c in s); preciso = max(1.2, 0.6 + letras / 14)
        if vis < preciso - 1e-6 and ok(ini): avisos.append(("LEITURA", ini, s, f"na tela {vis:.2f} s; precisa de {preciso:.2f} s"))
    return avisos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episodio"); ap.add_argument("--cada", type=float, default=0.25); ap.add_argument("--seguro", default="220,380,120")
    ap.add_argument("--tamanho", default="1080x1920"); ap.add_argument("--ignorar-y"); ap.add_argument("--permitir", action="append", default=[])
    ap.add_argument("--json"); a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    W, H = map(int, a.tamanho.split("x")); esc = H / 1920
    seguro = [float(x) * esc for x in a.seguro.split(",")]
    iy = [float(x) for x in a.ignorar_y.split(",")] if a.ignorar_y else None
    perm = [tuple(map(float, p.split("-"))) for p in a.permitir]
    ep = os.path.abspath(a.episodio); amostras = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(); pg = br.new_page(viewport={"width": W, "height": H})
        pg.goto("file://" + os.path.join(ep, "episode.html")); pg.wait_for_timeout(600); pg.evaluate("document.fonts.ready")
        total = pg.evaluate("window.TL ? window.TL.total : 0") or 0
        if total <= 0: sys.exit("ERRO: sem window.TL.total")
        t = 0.0
        while t < total:
            pg.evaluate(f"R({t})"); amostras.append((round(t, 3), pg.evaluate(JS))); t += a.cada
        br.close()
    av = analisa(amostras, W, H, seguro, iy, perm, a.cada)
    vistos = set(); unico = []
    for tipo, t, s, msg in av:                                       # um aviso por (tipo, texto, mensagem), no 1º instante
        k = (tipo, s, msg)
        if k not in vistos: vistos.add(k); unico.append((tipo, t, s, msg))
    for tipo, t, s, msg in sorted(unico, key=lambda x: x[1]): print(f"{tipo:9s} t={t:6.2f}s  “{s[:60]}”  {msg}")
    duros = sum(1 for x in unico if x[0] in ("FORA", "SOBREPOE"))
    print(f"{len(amostras)} instantes medidos; {len(unico)} avisos ({duros} duros)")
    if a.json: json.dump([dict(tipo=x[0], t=x[1], texto=x[2], msg=x[3]) for x in unico], open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.exit(1 if duros else 0)


if __name__ == "__main__":
    main()
