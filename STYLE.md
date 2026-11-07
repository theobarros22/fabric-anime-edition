# STYLE — read this before drawing anything / leia antes de desenhar

**Official style / Estilo oficial: 2D flat vector (SVG).** Solid fills, no gradients on characters, no outlines heavier than the sheet,
busts (head + shoulders), 4 expressions: `neutro, bravo, surpreso, rindo`, mouth `m` ∈ [0,1].

- Gengivão, Nove Dedos, Cabeça de Ovo are **always 2D**. Papercraft/3D are **experiments** and live under `experimental/` — never mix them into an official episode.
- Palette per character is defined in `characters/personagens.js` (object `C`). Change it there, regenerate sheets with `python tools/fichas.py`.
- Nove Dedos has **4 fingers on the left hand** (identity trait). Cabeça de Ovo carries a gavel (`martelo`).
- Typography: Anton (caption, headline), Arial bold (small labels). Key words in caption are red `#E1251B`.
- Every episode shows a satire / AI label. / Todo episódio mostra selo de sátira/IA.
- A new character PR must include: sheet PNG (4 expressions), palette, and one rendered 3-second clip.
