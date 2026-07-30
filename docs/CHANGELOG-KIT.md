---
tags: [changelog, kit]
status: atual
---
# CHANGELOG do KIT — histórico do próprio pipeline

> **Este arquivo é do kit, não do seu projeto.** O histórico do projeto que você constrói mora no [[CHANGELOG]] da raiz, que nasce zerado.
> `docs/` não é copiada para projetos novos (`scripts/novo-projeto.py` a exclui) — por isso o histórico do kit vive aqui e nunca polui o changelog do projeto.
> Regra de evolução: lição que aparece em 2+ projetos vira regra do kit e ganha uma entrada aqui. Ver [[README]] → "Como o kit evolui".

## [kit v3] — 2026-07-30
Passagem de agentes especializados + Obsidian. O kit deixou de ser só um conjunto de documentos e passou a ser um **vault operável com agentes instaláveis**.

- **Adicionado — `skills/`: 12 agentes instaláveis** (`SKILL.md` com frontmatter `name`/`description`, padrão Claude Code / Cowork): arquitetura-monolito, arquitetura-microservicos, backend-dominio, backend-bff, microservice-sync, frontend-uiux, frontend-mfe, autenticacao, iac-docker-terraform, testes, guardrails-review e dados-analise. Cada uma com regras numeradas, portão em checklist e armadilhas já pagas por projetos reais.
- **Adicionado — portões de existência.** As skills estruturais (microserviços, MFE) começam por um STEP 0 que pergunta *isto deve existir?* e **reprovam por padrão**. É o mecanismo que impede a IA de construir arquitetura que ninguém precisa.
- **Adicionado — [[ROTEIRO]]:** o caminho executável do dia 1 à entrega, ligando fase → skill → portão. O README descrevia as fases numa tabela; faltava a ordem operável.
- **Adicionado — [[PLANO]]:** o template que o README v2 já mandava gerar na Fase 1 mas que não existia no kit (lacuna real).
- **Adicionado — [[INICIO]] e [[GUIA-OBSIDIAN]]:** mapa de navegação e manual do vault.
- **Adicionado — [[exemplos/caso-spo]]:** caso de referência destilado de um app real (10 dias, 14 passagens de revisão, 84 achados) — aferição do que "pronto" significa e lista de armadilhas já pagas.
- **Adicionado — `templates/`:** modelos para D-NN, QA-NN e **fecho de sessão** (o ritual que estava descrito em prosa em 4 arquivos e agora é um clique via plugin Templates).
- **Adicionado — `scripts/novo-projeto.py`:** copia o kit para um projeto novo excluindo o que é só do kit (`docs/`, `exemplos/`, `.git`) e zerando os templates. O passo 1 do README era manual e propenso a levar lixo junto.
- **Adicionado — Obsidian:** `.obsidian/` versionado (abre em [[INICIO]], favoritos, grafo com cores por tema, Templates apontando para `templates/`), frontmatter `tags`/`status` em toda nota e wikilinks no lugar de caminhos.
- **Expandido — [[CHECKLIST]]:** de genérico para **portões em camadas** (arquitetura, domínio, borda, frontend, auth, infra, entrega), espelhando o portão de cada skill.
- **Expandido — [[APRENDIZADOS]]:** lições de aplicação (dinheiro inteiro, segredo por instalação, expand/contract, artefato pronto em vez de build no cliente).
- **Expandido — `scripts/checar.py`:** valida skills (frontmatter `name`/`description`), **wikilinks quebrados**, frontmatter ausente e placeholders não preenchidos, além do que já validava.
- **Corrigido — changelog com dois donos.** O `CHANGELOG.md` da raiz acumulava o histórico do kit *e* servia de template para o projeto; ao copiar o kit, o projeto novo nascia com a história de outra coisa. Agora: kit aqui, projeto lá.

## [kit v2.1] — 2026-07-22
- Generalização: `perfil-generico.md` (método p/ qualquer stack), prompt `04` sem viés estatístico, `RUNBOOK.md` exigido na entrega de projeto que opera, modo curto p/ projetos pequenos, arquivamento do DECISIONS em projeto longo (+ checagem no script), roteiro "primeiro dia" no README.

## [kit v2.0] — 2026-07-22
- Refatoração pós-SCB: orçamentos numéricos de contexto, estado em fonte única, prompts imperativos (~metade do custo), regra "observe antes de construir", `APRENDIZADOS.md` + prompt de retrospectiva, `scripts/checar.py`. Evidências medidas: [[docs/ANALISE-USO-SCB|ANALISE-USO-SCB]].

## [kit v1] — baseline
- Kit original, pré-refatoração (568 linhas). O que funcionou e o que falhou está medido em [[docs/ANALISE-USO-SCB|ANALISE-USO-SCB]].
