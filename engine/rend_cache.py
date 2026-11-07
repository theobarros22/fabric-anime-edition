"""Content-addressed frame renderer / Renderizador de quadros com cache por conteúdo.

EN: A frame is a pure function of time: window.R(t) paints the SVG, Playwright screenshots it.
    Frames whose DOM is identical are rendered once and reused (inside the episode and across runs).
PT: Quadro = função pura do tempo: window.R(t) pinta o SVG e o Playwright tira o print.
    Quadros com DOM idêntico são renderizados uma vez só e reaproveitados (no episódio e entre execuções).

usage / uso:
  python engine/rend_cache.py EPISODE_DIR OUT_FRAMES_DIR [--cache DIR] [--fps 30] [--size 1080x1920] [--n N]
EPISODE_DIR must contain episode.html (+ timeline.js, characters). Total frames come from TL.total unless --n.
"""
import argparse, hashlib, json, os, shutil, sys, time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode"); ap.add_argument("out")
    ap.add_argument("--cache", default=None); ap.add_argument("--fps", type=float, default=30)
    ap.add_argument("--size", default="1080x1920"); ap.add_argument("--n", type=int, default=0)
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    w, h = map(int, a.size.split("x"))
    ep = os.path.abspath(a.episode); html = os.path.join(ep, "episode.html")
    cache = a.cache or os.path.join(ep, ".frame_cache")
    os.makedirs(a.out, exist_ok=True); os.makedirs(cache, exist_ok=True)
    # the hash covers every source file: change HTML/timeline/characters => new hash / mudou algo => hash novo
    srcs = [html] + sorted(os.path.join(ep, f) for f in os.listdir(ep) if f.endswith((".js", ".json")))
    base = hashlib.sha1(b"".join(open(f, "rb").read() for f in srcs)).hexdigest()[:10]
    t0 = time.time(); rendered = reused = 0
    with sync_playwright() as pw:
        br = pw.chromium.launch(); pg = br.new_page(viewport={"width": w, "height": h})
        pg.goto("file://" + html); pg.wait_for_timeout(600); pg.evaluate("document.fonts.ready")
        total = a.n or int(round(pg.evaluate("window.TL ? window.TL.total : 0") * a.fps))
        if total <= 0: sys.exit("ERROR: no frames (set --n or define window.TL.total)")
        for i in range(total):
            pg.evaluate(f"R({i / a.fps})")
            key = base + hashlib.sha1(pg.evaluate("document.body.innerHTML").encode()).hexdigest()[:20]
            c = os.path.join(cache, key + ".jpg")
            if not os.path.exists(c): pg.screenshot(path=c, type="jpeg", quality=90); rendered += 1
            else: reused += 1
            shutil.copyfile(c, os.path.join(a.out, f"f{i:05d}.jpg"))
        br.close()
    print(json.dumps(dict(frames=total, rendered=rendered, reused=reused, seconds=round(time.time() - t0, 1))))


if __name__ == "__main__":
    main()
