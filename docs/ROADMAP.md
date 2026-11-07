# Roadmap

Each phase is done only when its **measured** acceptance criterion passes. / Cada fase só fecha com critério **medido**.

| Phase | Goal / Meta | Acceptance / Aceite | Status |
|---|---|---|---|
| 0 | Extract proven core, demo, tests, docs | `pytest` green, demo renders, cache warm run ≥ 5× faster | ✅ this release |
| 1 | Episode as data: `episode.json` (scenes, characters, captions) → generic `episode.html` renderer; character spec as JSON | Rebuild the sample episode from JSON with pixel-identical frames to the hand-written one | ⬜ |
| 2 | Voice abstraction: `ElevenLabs \| Chatterbox \| Qwen3-TTS \| recorded`, same interface, `job_estado` cost guard | Blind A/B (swapped sides) on a fixed script; objective metrics (WER by ASR round-trip, loudness); a human decides. Candidates only — licenses/quality **unverified** | ⬜ |
| 3 | Editable timeline per [TIMELINE_CONTRACT.md](TIMELINE_CONTRACT.md) | A non-author changes a caption, adds music, trims a cut; only changed segments re-render | ⬜ |
| 4 | Script assistant: LLM suggests script variants, hooks, character casting; human picks | Script → timeline with no manual editing for a 45 s episode | ⬜ |
| 5 | Cut QA: ASR round-trip check that no sentence is cut mid-word (ported from our talking-head tooling) | Detects planted bad cuts on a labeled test set, with a measured false-alarm rate | ⬜ |
| 6 | `experimental/3d`: one character rendered in 3D (e.g. three.js) with the same `R(t)` contract | 5 s clip, same timeline | ⬜ |

## Voice candidates / Vozes candidatas (not yet tested here)
- Chatterbox Multilingual — MIT, pt-BR, clone from ≥10 s, watermarked output (claims from the project page; verify).
- Qwen3-TTS — Apache-2.0, Portuguese, small model (verify quality and speed on your hardware).
- Excluded for licensing/language: XTTS-v2 (non-commercial), F5-TTS (CC-BY-NC, no PT), Dia (EN only).
- Always: record consent for any cloned voice; label AI voices.

## Good first issues / Boas primeiras issues
- Port `limpar_voz` (script-guided filler/retake cleanup) and `juiz_pares` (blind A/B judge) from our internal tools.
- Add Anton `@font-face` to `tools/fichas.py` (sheets currently fall back to Impact/Arial).
- Make the mouth envelope phoneme-aware (viseme) — keep volume mode as default.
