# Timeline contract (R1–R13) / Contrato da timeline

Status: **specification only — no editor UI exists in this repo yet.** / **Só especificação — ainda não há interface.**
Goal: someone who did not make the episode can change captions, add background music and fix cuts without breaking it.

| # | Requirement | Requisito |
|---|---|---|
| R1 | The EDL (JSON) is the single source of truth; the video is a render of it | O EDL (JSON) é a fonte única da verdade |
| R2 | Stable ids for every clip/caption/track | Ids estáveis |
| R3 | Each item has `origin: human \| generated` and `locked` (AI-generated seals can't be removed silently) | Origem humano/gerado + travado |
| R4 | Time in **integer frames** + fps (no float drift) | Tempo em quadros inteiros + fps |
| R5 | Assets referenced by content hash | Ativos por hash de conteúdo |
| R6 | Atomic operations with undo/redo | Operações atômicas com desfazer/refazer |
| R7 | Per-segment hash ⇒ re-render only what changed (reuses `engine/rend_cache.py`) | Hash por trecho ⇒ re-renderiza só o que mudou |
| R8 | Preview levels (draft → full) | Níveis de prévia |
| R9 | Local-first: server on `127.0.0.1`, no cloud needed | Local primeiro |
| R10 | Editable: caption text/style, music track + ducking, trim/cut, replace a line's audio | Editável: legenda, trilha, cortes, fala |
| R11 | Every edit re-runs loudness QA | Toda edição refaz o QA de loudness |
| R12 | Export: mp4 + EDL JSON (+ SRT) | Exporta mp4 + EDL (+ SRT) |
| R13 | Collaboration: EDL diffs are readable in git | Colaboração: diffs legíveis no git |

Open question: build on an existing open timeline (evaluate first) or write a minimal one — decided in Phase 3 with a benchmark.
