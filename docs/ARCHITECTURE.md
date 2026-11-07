# Architecture / Arquitetura

```
script.json ──► tools/build_audio.py ──► timeline.json + timeline.js + voice.wav
                                              │
episode.html (window.R(t)) + personagens.js ──┴─► engine/rend_cache.py ──► frames/*.jpg ──► ffmpeg ──► out.mp4 ──► tools/qa_audio.py
                                                   (Playwright, content-hash cache)
```

**EN**
- **Pure frame function.** `R(t)` paints an SVG from time only. This gives deterministic frames, free seeking, and a cache: the renderer hashes `document.body.innerHTML` (+ all episode source files) and screenshots only unseen frames.
- **Characters** are code: `busto(name, {expr, m, blink, dedo, martelo}, x, y, scale)` returns SVG. `m` (0..1) is mouth opening, taken from the line's RMS envelope.
- **Timeline** (`timeline.json`): lines with `start`, `dur`, `env` (30 fps mouth), `txt`. Today it is generated; the editable version follows [TIMELINE_CONTRACT.md](TIMELINE_CONTRACT.md).
- **Audio**: per-line silence trim → loudness match to −17 LUFS → laid on a gap grid → final loudnorm −14 LUFS / TP −2.5 in encode, then **measured after AAC**.
- **Known limits**: mouth = volume, not phonemes; Chromium screenshot throughput is the render bottleneck (~25 fps on a 2-core cloud box; GPU not used).

**PT**
- **Quadro como função pura.** `R(t)` pinta o SVG só a partir do tempo: quadros determinísticos, seek grátis e cache — o renderizador faz hash do `innerHTML` (+ arquivos-fonte do episódio) e só tira print do que ainda não viu.
- **Personagens** são código: `busto(nome, {expr, m, blink, dedo, martelo}, x, y, escala)` devolve SVG. `m` (0..1) vem do envelope RMS da fala.
- **Timeline** (`timeline.json`): falas com `start`, `dur`, `env` (boca 30 fps), `txt`. Hoje é gerada; a versão editável segue o [TIMELINE_CONTRACT.md](TIMELINE_CONTRACT.md).
- **Áudio**: corte de silêncio por fala → igualação a −17 LUFS → grade com intervalos → loudnorm final −14 LUFS / TP −2,5 no encode, **medido depois do AAC**.
- **Limites conhecidos**: boca = volume, não fonema; o gargalo é o print do Chromium (~25 qps em máquina de 2 núcleos, sem GPU).
