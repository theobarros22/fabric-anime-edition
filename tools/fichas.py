"""Generate character sheets (PNG) from characters/personagens.js / Gera as fichas dos personagens.
usage: python tools/fichas.py [OUT_DIR]     (needs playwright+chromium)
"""
import json, os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
out = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, "media", "characters")
CHARS = [("tito", "TITO", "Tito"), ("bozo", "BOZO", "Bozo"), ("gengivao", "GENGIVÃO", "Gengivão"),
         ("ovo", "CABEÇA DE OVO", "Cabeça de Ovo"), ("nove", "NOVE DEDOS", "Nove Dedos")]
EXPR = ["neutro", "bravo", "surpreso", "rindo"]
TPL = """<html><head><style>body{margin:0;background:#412D24}text{font-family:'Anton','Impact',sans-serif;fill:#FFF4E3}</style></head><body>
<svg id=s xmlns=http://www.w3.org/2000/svg width=1920 height=1080 viewBox="0 0 1920 1080"></svg><script>%s</script><script>
const D=%s;let h='<rect width=1920 height=1080 fill=#412D24 /><rect width=1920 height=230 fill=#3A281F />';
h+=`<text x=80 y=130 font-size=92>${D.nome}</text><text x=84 y=180 font-size=30 style="fill:#CBB79C;font-family:Arial,sans-serif;font-weight:700">OFFICIAL 2D STYLE SHEET · FICTIONAL SATIRE CHARACTER</text>`;
const xs=[300,740,1180,1620],ms=[0,.9,.4,0];
D.expr.forEach((e,i)=>{const o={expr:e,m:ms[i]};if(D.k==='ovo')o.martelo=-20;if(D.k==='tito'&&i==1)o.dedo=28;
h+=busto(D.k,o,xs[i],560,1.12)+`<text x=${xs[i]} y=980 font-size=38 text-anchor=middle>${e.toUpperCase()}${ms[i]>.5?' (SPEAKING)':''}</text>`});
document.getElementById('s').innerHTML=h;</script></body></html>"""
js = open(os.path.join(ROOT, "characters", "personagens.js"), encoding="utf-8").read()
os.makedirs(out, exist_ok=True); tmp = os.path.join(out, "_tmp.html")
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1920, "height": 1080})
    for k, nome, _ in CHARS:
        open(tmp, "w", encoding="utf-8").write(TPL % (js, json.dumps(dict(k=k, nome=nome, expr=EXPR))))
        pg.goto("file://" + tmp); pg.wait_for_timeout(200); pg.screenshot(path=os.path.join(out, f"{k.upper()}_ficha_2D.png"))
    b.close()
os.remove(tmp); print("ok", out)
