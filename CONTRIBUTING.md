# Contributing / Como colaborar

**EN**
1. Open an issue before big work. Pick something from [docs/ROADMAP.md](docs/ROADMAP.md).
2. **No change without a before/after measurement** on the *same* clip and machine (time, frames identical or QA passed). Put the numbers in the PR.
3. Never commit: API keys, voice IDs of cloned voices, client media, third-party videos/music without a license. `.env.local` is git-ignored.
4. Official style is 2D flat vector ([STYLE.md](STYLE.md)). Other styles go to `experimental/`.
5. Anything AI-generated must stay labeled. Paid generation needs the cost stated in the PR/issue first (use `voice/job_estado.py`).
6. `pytest -q` must pass. Be honest in PR text: say what you did *not* test.

**PT**
1. Abra uma issue antes de algo grande. Escolha um item do [docs/ROADMAP.md](docs/ROADMAP.md).
2. **Nenhuma mudança sem medição antes/depois** no *mesmo* trecho e máquina (tempo, quadros idênticos ou QA aprovado). Ponha os números no PR.
3. Nunca commite: chaves de API, IDs de vozes clonadas, mídia de cliente, vídeos/músicas de terceiros sem licença. `.env.local` é ignorado.
4. O estilo oficial é 2D vetor plano ([STYLE.md](STYLE.md)). Outros estilos vão em `experimental/`.
5. Tudo gerado por IA continua rotulado. Geração paga exige o custo declarado antes (use `voice/job_estado.py`).
6. `pytest -q` precisa passar. Seja honesto no PR: diga o que você *não* testou.
