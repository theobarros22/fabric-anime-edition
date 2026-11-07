# AGENTS.md — for AI coding agents / para agentes de IA

- Read `STYLE.md` first. Official style = 2D flat vector. Never restyle official characters.
- Frames must stay a **pure function of time**: `window.R(t)` — no `Date.now()`, no `Math.random()`, no timers, no network.
- Never read or print `.env*`; never write secrets, API keys or voice IDs to files/logs. Paid calls only through `voice/job_estado.py`, only after the user approved the cost.
- Before claiming an improvement: measure before/after on the same clip. State what you did **not** test. You cannot hear audio: report LUFS/TP and say a human must listen.
- Do not push to `main` without the owner's approval.
- Test: `pytest -q`. Demo: `python tools/render_episode.py examples/demo`.
