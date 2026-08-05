---
tags: [obsidian, guia]
status: atual
---
# Como este pipeline roda no Obsidian

Este vault foi montado para ser operado dentro do [Obsidian](https://obsidian.md) — app gratuito de notas em Markdown. Nada aqui depende dele para funcionar (é tudo `.md` puro, e as skills funcionam em qualquer ferramenta de IA), mas no Obsidian a navegação, os backlinks e o grafo tornam o pipeline muito mais fácil de conduzir.

## Abrir o vault
1. Instale o Obsidian (Windows, Mac ou Linux).
2. `Open folder as vault` → selecione **a pasta que contém este arquivo** (a mesma que tem o `README.md` e a pasta `b_process/skills/`).
3. Ele lê a configuração de `.obsidian/` e abre direto em [[INDEX]].
4. Confie no vault se ele perguntar — é conteúdo local, sem scripts.

> **A raiz do vault é a raiz do repositório git.** Não abra a pasta-mãe: se o vault ficar um nível acima, links de caminho como `[[b_process/skills/README|skills/]]` param de resolver e `scripts/check.py` acusa. Se isso acontecer, o próprio script diz quais links quebraram.

## O que já vem configurado
- **Abre em [[INDEX]]**, o mapa de navegação.
- **Favoritos** na barra lateral: Início, Roteiro, Contexto, Decisões, Backlog, Checklist, Skills, Templates.
- **Plugins do núcleo ativos:** Grafo, Busca, Backlinks, Outline, Tags, Command palette, Page preview, Templates, Propriedades.
- **Templates apontando para `b_process/templates/`** — D-NN, QA-NN e fecho de sessão prontos para inserir.
- **Grafo com cores por tema:** skills, decisões, prompts, exemplos e modelos em grupos distintos.

## Os modelos (o que mais poupa tempo no dia a dia)
`Ctrl/Cmd+P` → *Templates: Insert template* → escolha:

| Modelo | Cola em | Quando |
|---|---|---|
| [[a_decision\|decisao]] | tabela de Decisões do [[c_decisions|DECISIONS]] | assunto fechado — inclusive rejeição |
| [[b_qa_finding\|achado-qa]] | tabela de Achados do [[c_decisions|DECISIONS]] | cada achado de uma passagem de QA |
| [[c_session_closing\|fecho-de-sessao]] | nota do dia | **toda** vez que uma sessão termina |

Vale atribuir um atalho de teclado em `Settings → Hotkeys → Templates: Insert template` — o fecho de sessão é o passo mais pulado do pipeline, e é onde o estado começa a divergir.

## Como navegar
- **Links `[[...]]`:** clique para pular entre notas. O [[a_roadmap|ROTEIRO]] linka direto a skill de cada fase.
- **Backlinks** (rodapé da nota): quem aponta para cá. Útil para ver todo lugar que cita uma decisão.
- **Grafo (Ctrl/Cmd+G):** [[INDEX]], [[a_context_source|CONTEXT]] e [[b_process/skills/README|skills/]] são os hubs.
- **Busca (Ctrl/Cmd+Shift+F):** procure por `D-`, `Q-`, `QA-`, `T-` para saltar ao item rastreável.
- **Tags:** `#skills`, `#decisoes`, `#checklist`, `#roteiro`, `#exemplo`, `#template`.

## Convenções deste vault
- **Frontmatter** em toda nota: `tags`, `status` (atual/rascunho/histórico/congelado), `data` quando relevante.
- **`status: rascunho`** marca os arquivos que ainda são template esperando você preencher ([[a_context_source|CONTEXT]], [[b_plan|PLANO]], [[c_decisions|DECISIONS]], [[c_backlog|BACKLOG]], [[a_changelog|CHANGELOG]]). Troque para `atual` quando preencher — e o `scripts/check.py` avisa se você esqueceu placeholders.
- **Links internos** em vez de caminhos: `[[c_decisions|DECISIONS]]`, não `a_context/c_decisions.md`.
- **IDs rastreáveis:** `D-NN` decisão · `Q-NN` pendência do dono · `QA-NN` achado · `T-NN` tarefa · `A-NN` ação do dono.

## Trabalhar com as skills a partir do vault
Os `SKILL.md` são notas normais — leia e navegue aqui, e mantenha as pastas de `b_process/skills/` instaladas na sua ferramenta de IA. Ao ajustar uma skill (porque você aprendeu algo no seu projeto), edite aqui e reinstale: o vault é a fonte da verdade.

## Plugins da comunidade (opcionais)
Não vêm instalados, para o vault abrir sem downloads. Nada do pipeline depende deles:
- **Kanban** — ver o [[c_backlog|BACKLOG]] como quadro arrastável.
- **Dataview** — tabelas automáticas (ex.: todo `status: rascunho` que falta preencher).
- **Templater** — modelos com lógica, se os de `b_process/templates/` ficarem pequenos para você.

`Settings → Community plugins → Browse`.

## Higiene
Duas linhas, uma vez cada:

```
python scripts/task.py hook       # uma vez: o portão passa a rodar sozinho em todo commit
python scripts/task.py check      # quando quiser conferir à mão
python scripts/task.py            # sem argumento = check
python scripts/task.py --help     # todas as tarefas
```

`task.py` é o **único** lugar onde os comandos do kit moram. Não é `Makefile` porque
`make` não existe num Windows por padrão, e o kit não tem dependência externa nenhuma.

**Esta página não lista o que reprova e o que só avisa** — a lista mora no cabeçalho do `scripts/check.py`, que é a fonte da verdade. Lista repetida em documentação derrapa em silêncio quando o script muda, e divergência doc × código é achado de QA pela regra do próprio kit. Rode o script e leia a saída: cada falha diz o que cortar e para onde.

Sem o `install_hook.py` o portão só roda quando você lembra — e commit sem saída nenhuma parece commit aprovado.

A pasta `.obsidian/` fica fora da validação. Ela **é versionada** de propósito — é o que faz o vault abrir pronto para quem clonar —, com exceção de `workspace.json`, que muda a cada abertura e está no `.gitignore`.

## Levar o pipeline para um projeto novo
`python scripts/new_project.py ../meu-app --nome "Meu App"`. O conteúdo do kit vira a pasta de documentação do projeto (`77777777_<TAG>_Project_DOCs/`), com `CLAUDE.md`, `.gitignore` e `.gitattributes` na raiz e uma pasta `src/` para o código. Preenche o nome no [[a_context_source|CONTEXT]] e no [[b_plan|PLANO]] e zera o [[a_changelog|CHANGELOG]].

**Ficam no kit**, porque são história deste repositório e não do seu projeto: o changelog do kit, o caso de referência e os relatórios de auditoria do próprio kit. Os wikilinks que apontavam para eles viram texto puro na cópia — senão o projeto novo nasceria com link quebrado e reprovando no primeiro `check.py`. A pasta destino já abre como vault configurado.
