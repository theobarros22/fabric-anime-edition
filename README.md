# Fabric Anime Edition

**🇬🇧 English** · [🇧🇷 Português](README.pt-BR.md)

> An open, code-first factory for **2D flat-vector animated shorts** (3D-ready by design):
> scripts → characters → voices → cuts → caption/mouth sync → editable timeline → vertical video.

<p align="center"><img src="media/gifs/brazolia_ep1_preview.gif" width="260" alt="Sample episode preview"> &nbsp; <img src="media/gifs/demo_preview.gif" width="260" alt="Synthetic-voice demo"></p>

Born from a real production pipeline (satirical shorts set in the fictional country *Brazólia*). This repo extracts
**only what proved itself** from that work and leaves the rest of the studio behind, so that newcomers can contribute
without having to understand a large private engine.

## What works today (honest status)

| Piece | Status | Where |
|---|---|---|
| Frame = pure function of time `R(t)`, rendered with Playwright → ffmpeg | ✅ working | `engine/rend_cache.py` |
| Content-hash frame cache (identical frames are rendered once) | ✅ measured: demo 12.7 s → 2.3 s on re-run, identical output | `engine/rend_cache.py` |
| 5 official 2D characters, 4 expressions, mouth open/close from audio level | ✅ working | `characters/personagens.js`, `media/characters/` |
| Script → timeline → voice track with per-line loudness matching and 30 fps mouth envelope | ✅ working | `tools/build_audio.py` |
| One-command render + loudness check (target ≈ −14 LUFS, TP ≤ −1.5 dBTP) | ✅ working | `tools/render_episode.py`, `tools/qa_audio.py` |
| Paid-API safety: never pay twice for the same input; preview must be approved first | ✅ tested | `voice/job_estado.py` |
| Voice providers beyond one commercial API (open TTS: Chatterbox, Qwen3-TTS) | 🧪 candidates, **not benchmarked** | [docs/ROADMAP.md](docs/ROADMAP.md) |
| Script/character assistant (LLM-guided) | 📝 designed, not built | [docs/ROADMAP.md](docs/ROADMAP.md) |
| Editable timeline (change captions, add music, fix cuts) | 📝 contract written, UI not built | [docs/TIMELINE_CONTRACT.md](docs/TIMELINE_CONTRACT.md) |
| 3D characters | 📝 placeholder only — no 3D has been produced yet | `experimental/` (planned) |

**Limits you should know:** lip-sync follows the audio *volume*, not phonemes. Loudness is *measured*, not *heard* —
a human must still listen. The sample video's voices come from a commercial TTS service (see [LICENSE-ASSETS.md](LICENSE-ASSETS.md)).

## Samples

| | |
|---|---|
| ![cast](media/characters/ELENCO_completo_2D.png) | **Cast sheets** — Tito, Bozo, Gengivão, Cabeça de Ovo, Nove Dedos (`media/characters/`) |
| ![sheet](media/frames/brazolia_ep1_contact_sheet.jpg) | **Frames from a real episode** (56 s, 1080×1920): [`media/video/brazolia_ep1_sample.mp4`](media/video/brazolia_ep1_sample.mp4) |

- 🎬 Real sample (Portuguese, AI voices, labeled satire): `media/video/brazolia_ep1_sample.mp4`
- 🎬 Fully reproducible demo (synthetic beeps instead of voices): `media/video/demo_synthetic_voices.mp4` ← rebuild it yourself below.

## Quick start

```bash
pip install -r requirements.txt && playwright install chromium   # + ffmpeg on PATH
python tools/render_episode.py examples/demo        # → examples/demo/out.mp4
python tools/fichas.py                              # regenerate character sheets
pytest -q                                           # tests
```

An episode is just a folder: `episode.html` (defines `window.R(t)`), `script.json`, audio files, `personagens.js`.
Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) first; the visual rules are in [STYLE.md](STYLE.md).

## Contributing

We want collaborators — especially for: open-source voice backends, the timeline editor, a script assistant,
more characters in the **same 2D style**, and a first 3D experiment. Start with [CONTRIBUTING.md](CONTRIBUTING.md)
and the roadmap. Rule #1: **no change ships without a before/after measurement** on the same clip.

## Responsible use

Satire with a fictional country and fictional characters, always labeled as satire and AI-generated.
Do not use this to impersonate real people or to produce deceptive political content. See [DISCLAIMER.md](DISCLAIMER.md).

## License

Code: [MIT](LICENSE). Characters, sample media, fonts and voices: [LICENSE-ASSETS.md](LICENSE-ASSETS.md) (not MIT).
