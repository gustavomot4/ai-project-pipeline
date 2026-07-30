---
tags: [obsidian, guia]
status: atual
---
# Como este pipeline roda no Obsidian

Este vault foi montado para ser operado dentro do [Obsidian](https://obsidian.md) — app gratuito de notas em Markdown. Nada aqui depende dele para funcionar (é tudo `.md` puro, e as skills funcionam em qualquer ferramenta de IA), mas no Obsidian a navegação, os backlinks e o grafo tornam o pipeline muito mais fácil de conduzir.

## Abrir o vault
1. Instale o Obsidian (Windows, Mac ou Linux).
2. `Open folder as vault` → selecione **a pasta que contém este arquivo** (a mesma que tem o `README.md` e a pasta `skills/`).
3. Ele lê a configuração de `.obsidian/` e abre direto em [[INICIO]].
4. Confie no vault se ele perguntar — é conteúdo local, sem scripts.

> **A raiz do vault é a raiz do repositório git.** Não abra a pasta-mãe: se o vault ficar um nível acima, links de caminho como `[[skills/LEIA-ME]]` param de resolver e `scripts/checar.py` acusa. Se isso acontecer, o próprio script diz quais links quebraram.

## O que já vem configurado
- **Abre em [[INICIO]]**, o mapa de navegação.
- **Favoritos** na barra lateral: Início, Roteiro, Contexto, Decisões, Backlog, Checklist, Skills, Templates.
- **Plugins do núcleo ativos:** Grafo, Busca, Backlinks, Outline, Tags, Command palette, Page preview, Templates, Propriedades.
- **Templates apontando para `templates/`** — D-NN, QA-NN e fecho de sessão prontos para inserir.
- **Grafo com cores por tema:** skills, decisões, prompts, exemplos e modelos em grupos distintos.

## Os modelos (o que mais poupa tempo no dia a dia)
`Ctrl/Cmd+P` → *Templates: Insert template* → escolha:

| Modelo | Cola em | Quando |
|---|---|---|
| [[templates/decisao\|decisao]] | tabela de Decisões do [[DECISIONS]] | assunto fechado — inclusive rejeição |
| [[templates/achado-qa\|achado-qa]] | tabela de Achados do [[DECISIONS]] | cada achado de uma passagem de QA |
| [[templates/fecho-de-sessao\|fecho-de-sessao]] | nota do dia | **toda** vez que uma sessão termina |

Vale atribuir um atalho de teclado em `Settings → Hotkeys → Templates: Insert template` — o fecho de sessão é o passo mais pulado do pipeline, e é onde o estado começa a divergir.

## Como navegar
- **Links `[[...]]`:** clique para pular entre notas. O [[ROTEIRO]] linka direto a skill de cada fase.
- **Backlinks** (rodapé da nota): quem aponta para cá. Útil para ver todo lugar que cita uma decisão.
- **Grafo (Ctrl/Cmd+G):** [[INICIO]], [[CONTEXT]] e [[skills/LEIA-ME|skills/]] são os hubs.
- **Busca (Ctrl/Cmd+Shift+F):** procure por `D-`, `Q-`, `QA-`, `T-` para saltar ao item rastreável.
- **Tags:** `#skills`, `#decisoes`, `#checklist`, `#roteiro`, `#exemplo`, `#template`.

## Convenções deste vault
- **Frontmatter** em toda nota: `tags`, `status` (atual/rascunho/histórico/congelado), `data` quando relevante.
- **`status: rascunho`** marca os arquivos que ainda são template esperando você preencher ([[CONTEXT]], [[PLANO]], [[DECISIONS]], [[BACKLOG]], [[CHANGELOG]]). Troque para `atual` quando preencher — e o `scripts/checar.py` avisa se você esqueceu placeholders.
- **Links internos** em vez de caminhos: `[[DECISIONS]]`, não `DECISIONS.md`.
- **IDs rastreáveis:** `D-NN` decisão · `Q-NN` pendência do dono · `QA-NN` achado · `T-NN` tarefa · `A-NN` ação do dono.

## Trabalhar com as skills a partir do vault
Os `SKILL.md` são notas normais — leia e navegue aqui, e mantenha as pastas de `skills/` instaladas na sua ferramenta de IA. Ao ajustar uma skill (porque você aprendeu algo no seu projeto), edite aqui e reinstale: o vault é a fonte da verdade.

## Plugins da comunidade (opcionais)
Não vêm instalados, para o vault abrir sem downloads. Nada do pipeline depende deles:
- **Kanban** — ver o [[BACKLOG]] como quadro arrastável.
- **Dataview** — tabelas automáticas (ex.: todo `status: rascunho` que falta preencher).
- **Templater** — modelos com lógica, se os de `templates/` ficarem pequenos para você.

`Settings → Community plugins → Browse`.

## Higiene
`python scripts/checar.py` na raiz do vault. Ele **reprova** (código 1) quando: o [[CONTEXT]] estoura 4.000 caracteres, o [[DECISIONS]] passa de 12.000, existe mais de um BACKLOG/CONTEXT/DECISIONS, há mais de 1 tarefa em andamento, uma skill está sem `name`/`description`, **um `[[link]]` não tem destino** ou sobrou cruft (`.bak`, `.tmp`, `.orig`). E **avisa** (sem reprovar) sobre placeholders e notas sem frontmatter.

A pasta `.obsidian/` fica fora da validação e do zip de entrega. Ela **é versionada** de propósito — é o que faz o vault abrir pronto para quem clonar —, com exceção de `workspace.json`, que muda a cada abertura e está no `.gitignore`.

## Levar o pipeline para um projeto novo
`python scripts/novo-projeto.py ../meu-app --nome "Meu App"`. Copia tudo menos o que é só do kit (`docs/`, `exemplos/`, `.git`, o estado de sessão do Obsidian), zera o [[CHANGELOG]] e preenche o nome no [[CONTEXT]] e no [[PLANO]]. A pasta destino já abre como vault configurado.
