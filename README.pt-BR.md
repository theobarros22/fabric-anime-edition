# Fabric Anime Edition

[🇬🇧 English](README.md) · **🇧🇷 Português**

[![CI](https://github.com/theobarros22/fabric-anime-edition/actions/workflows/ci.yml/badge.svg)](https://github.com/theobarros22/fabric-anime-edition/actions) ![license](https://img.shields.io/badge/code-MIT-green) ![style](https://img.shields.io/badge/style-2D%20flat%20vector-orange) ![lang](https://img.shields.io/badge/docs-EN%20%7C%20PT--BR-blue) ![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen)

> Uma fábrica aberta, guiada por código, de **vídeos curtos 2D em vetor plano** (pronta para 3D por desenho):
> roteiro → personagens → vozes → cortes → sincronia de legenda/boca → timeline editável → vídeo vertical.

<p align="center"><img src="media/gifs/brazolia_ep1_preview.gif" width="260" alt="Prévia de episódio"> &nbsp; <img src="media/gifs/demo_preview.gif" width="260" alt="Demo com vozes sintéticas"></p>

Nasceu de um pipeline de produção real (curtas satíricos no país fictício *Brazólia*). Este repositório extrai
**somente o que provou funcionar** e deixa o resto do estúdio de fora, para que quem chegar possa colaborar
sem precisar entender um motor grande e privado.

## Por que o Fabric Anime Edition é diferente

A maioria das ferramentas de "vídeo com IA" é um caça-níquel. A maioria dos editores é uma timeline em branco. O Fabric entrega uma **linha de produção repetível, barata e consistente** para vídeos curtos com personagens:

| O que você ganha | Por que importa | Evidência |
|---|---|---|
| **O mesmo personagem em todo quadro e episódio** | Personagens são código (SVG), não imagens geradas — sem rosto mudando, sem sorteio | `characters/personagens.js`, `media/characters/` |
| **Quadros determinísticos** | `R(t)` é função pura do tempo: mesma entrada ⇒ mesmos pixels. Fácil de testar, comparar e revisar | Saída com e sem cache foi idêntica nos nossos benchmarks |
| **Editou uma legenda → só aquele trecho re-renderiza** | O cache usa a *aparência* do quadro como chave, não a timeline inteira | Demo: editar uma fala re-renderizou **45 de 286 quadros** (etapa de render 16,0 s → 4,9 s); adicionar música re-renderizou **0** (2,8 s) |
| **Re-render em segundos** | O cache por hash renderiza cada quadro único uma vez | Demo: **12,7 s → 2,3 s** na 2ª execução; num episódio real medimos −24 % a frio e −87 % com cache quente |
| **Começo sem custo** | O demo não precisa de chave de API nem GPU | `python tools/render_episode.py examples/demo` |
| **Impossível gastar dinheiro sem querer** | A mesma entrada nunca é paga duas vezes; uma prévia curta precisa ser aprovada antes do job pago longo | `voice/job_estado.py` (testado) |
| **Pequeno o bastante para entender em uma hora** | O núcleo inteiro tem **~300 linhas** de Python/JS legível — sem framework para aprender | `engine/`, `tools/`, `voice/` |
| **Colaboração nativa no git** | Tudo é texto (SVG, JS, JSON): diffs e pull requests são revisáveis | sem arquivos de projeto binários |
| **Honesto por desenho** | O README diz o que *ainda não* existe; cada afirmação tem um comando para conferir | tabela de status abaixo |

**Para quem é:** canais de sátira e explicação, animadores independentes que programam, agências que precisam de elenco fixo em volume e pesquisadores de IA/TTS que querem um pipeline real para plugar um modelo de voz.

**O que não é:** um modelo de vídeo generativo, um editor de arrastar-e-soltar (ainda) ou um produto pronto. É um núcleo afiado e testado — e um lugar para construirmos o resto juntos.

## Precisamos de ajuda (escolha uma, abra uma issue, envie um PR)

- 🎙️ **Vozes de código aberto** (Chatterbox, Qwen3-TTS…) atrás de uma interface única — precisa de benchmark A/B cego
- 🎞️ **Timeline editável** (legendas, música, cortes; só o que mudou é re-renderizado)
- 🧠 **Assistente de roteiro e personagens** (LLM sugere ganchos e escala personagens; o humano decide)
- 👄 **Sincronia labial por fonemas** (hoje: só volume)
- 🧊 **Primeiro experimento 3D** com o mesmo contrato `R(t)`
- 🌍 **Traduções e docs** — somos bilíngues (EN/PT); adicione a sua

Chegou agora? Procure issues com o rótulo `good first issue`. Todo PR precisa de medição antes/depois — é a regra que mantém isto rápido.

## O que funciona hoje (status honesto)

| Peça | Status | Onde |
|---|---|---|
| Quadro = função pura do tempo `R(t)`, renderizado com Playwright → ffmpeg | ✅ funciona | `engine/rend_cache.py` |
| Cache de quadros por hash de conteúdo (quadro idêntico é renderizado uma vez) | ✅ medido: demo 12,7 s → 2,3 s na 2ª execução, saída idêntica | `engine/rend_cache.py` |
| 5 personagens 2D oficiais, 4 expressões, boca pelo volume do áudio | ✅ funciona | `characters/personagens.js`, `media/characters/` |
| Roteiro → timeline → faixa de voz com igualação de loudness por fala e envelope de boca a 30 fps | ✅ funciona | `tools/build_audio.py` |
| Render em um comando + checagem de loudness (alvo ≈ −14 LUFS, TP ≤ −1,5 dBTP) | ✅ funciona | `tools/render_episode.py`, `tools/qa_audio.py` |
| Segurança de custo em APIs pagas: nunca pagar duas vezes pela mesma entrada; prévia aprovada antes | ✅ testado | `voice/job_estado.py` |
| Vozes além de uma API comercial (TTS aberto: Chatterbox, Qwen3-TTS) | 🧪 candidatos, **sem benchmark ainda** | [docs/ROADMAP.md](docs/ROADMAP.md) |
| Assistente de roteiro e personagens (guiado por LLM) | 📝 desenhado, não construído | [docs/ROADMAP.md](docs/ROADMAP.md) |
| Editor local MVP: editar legendas, reordenar falas, ajustar pausas, trilha de fundo com ducking, desfazer, re-renderizar | ✅ funciona (testado). Ainda não: cortes/aparas, trocar áudio, adicionar falas | `tools/editor.py`, [docs/TIMELINE_CONTRACT.md](docs/TIMELINE_CONTRACT.md) |
| Personagens 3D | 📝 só um espaço reservado — nenhum 3D foi produzido ainda | `experimental/` (planejado) |

**Limites que você precisa saber:** a sincronia labial segue o *volume* do áudio, não os fonemas. O loudness é
*medido*, não *ouvido* — uma pessoa ainda precisa ouvir. As vozes do vídeo de exemplo vêm de um serviço de TTS
comercial (veja [LICENSE-ASSETS.md](LICENSE-ASSETS.md)).

## Amostras

| | |
|---|---|
| ![elenco](media/characters/ELENCO_completo_2D.png) | **Fichas do elenco** — Tito, Bozo, Gengivão, Cabeça de Ovo, Nove Dedos (`media/characters/`) |
| ![folha](media/frames/brazolia_ep1_contact_sheet.jpg) | **Quadros de um episódio real** (56 s, 1080×1920): [`media/video/brazolia_ep1_sample.mp4`](media/video/brazolia_ep1_sample.mp4) |

- 🖥️ Editor local (legendas, ordem, pausas, música): `python tools/editor.py examples/demo`

  ![editor](media/frames/editor_ui.png)

- 🎬 Exemplo real (português, vozes de IA, sátira rotulada): `media/video/brazolia_ep1_sample.mp4`
- 🎬 Demo reproduzível (bipes sintéticos no lugar das vozes): `media/video/demo_synthetic_voices.mp4` ← refaça você mesmo abaixo.

## Começando

```bash
pip install -r requirements.txt && playwright install chromium   # + ffmpeg no PATH
python tools/render_episode.py examples/demo        # → examples/demo/out.mp4
python tools/editor.py examples/demo                # editor local → http://127.0.0.1:8777
python tools/fichas.py                              # regenera as fichas
pytest -q                                           # testes
```

Um episódio é só uma pasta: `episode.html` (define `window.R(t)`), `script.json`, áudios, `personagens.js`.
Leia primeiro [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md); as regras visuais estão em [STYLE.md](STYLE.md).

## Como colaborar

Procuramos colaboradores — principalmente para: vozes de código aberto, o editor de timeline, um assistente de
roteiro, mais personagens no **mesmo estilo 2D** e um primeiro experimento em 3D. Comece por
[CONTRIBUTING.md](CONTRIBUTING.md) e pelo roadmap. Regra nº 1: **nenhuma mudança entra sem medição antes/depois** no mesmo trecho.

## Uso responsável

Sátira com país e personagens fictícios, sempre rotulada como sátira e como conteúdo gerado por IA.
Não use para imitar pessoas reais nem para produzir conteúdo político enganoso. Veja [DISCLAIMER.md](DISCLAIMER.md).

## Licença

Código: [MIT](LICENSE). Personagens, mídias de exemplo, fontes e vozes: [LICENSE-ASSETS.md](LICENSE-ASSETS.md) (não é MIT).
