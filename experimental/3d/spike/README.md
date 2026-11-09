# Spike 3D (three.js) / 3D spike — experimental, NOT the official style

**PT-BR.** Pergunta: o modelo "quadro = função pura do tempo" (`window.R(t)`) aguenta uma camada 3D (three.js) com legenda SVG por cima?
Resposta medida: **sim**. Resultado (nuvem, Chromium sem GPU, WebGL por software SwiftShader, 540×960):
- WebGL2 disponível no Chromium headless: sim
- determinístico: o mesmo `t` duas vezes gera o mesmo JPEG (hash igual); `t` diferente gera quadro diferente
- custo: ~57 ms/quadro a 540×960 (só CPU). A 1080×1920 espere ~4× isso na CPU; na GPU do PC deve cair muito (**não medido**)
- a camada SVG (texto/legenda) sobrepõe o canvas 3D normalmente

Limites: um cubo não prova personagem 3D, iluminação nem consistência de elenco. O estilo oficial segue sendo **2D vetor**.
O cache por conteúdo (`engine/rend_cache.py`) hasheia o DOM; um `<canvas>` não aparece no `innerHTML`, então para usar 3D é preciso incluir o estado
da cena (ex.: `t` arredondado) no hash. Isso ainda **não** foi implementado.

**EN.** Question: can the "frame = pure function of time" model host a three.js layer under SVG captions? Measured: yes — deterministic,
~57 ms/frame at 540×960 on CPU-only SwiftShader (GPU not measured). Caveat: the content-hash cache hashes `document.body.innerHTML`, which
does not contain canvas pixels; 3D needs the scene state (e.g. rounded `t`) mixed into the key. Not implemented.

Rodar / run:
```
npm i three@0.170.0 && cp node_modules/three/build/three.module.min.js .
python -m http.server 8765 &   # módulo ES não carrega por file://
python spike.py
```
three.js é MIT (veja THIRD_PARTY.md). Não vendorizado.
