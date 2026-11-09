import time, hashlib
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br=pw.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
    pg=br.new_page(viewport={"width":540,"height":960}); pg.goto("http://127.0.0.1:8765/spike.html"); pg.wait_for_function("window.READY===true",timeout=15000)
    print("webgl:",pg.evaluate("!!document.createElement('canvas').getContext('webgl2')"))
    h=[]
    for t in (0.5,1.0,0.5):
        pg.evaluate(f"R({t})"); b=pg.screenshot(type="jpeg",quality=92); h.append(hashlib.sha1(b).hexdigest()[:10])
    print("deterministico (t=0.5 duas vezes igual):",h[0]==h[2],"| t=1.0 diferente:",h[1]!=h[0])
    t0=time.time(); n=30
    for i in range(n): pg.evaluate(f"R({i/30})"); pg.screenshot(type="jpeg",quality=92)
    print("ms/quadro 540x960:",round((time.time()-t0)/n*1000,1))
    pg.evaluate("R(1.2)"); pg.screenshot(path="frame.jpg",type="jpeg",quality=92)
    br.close()
