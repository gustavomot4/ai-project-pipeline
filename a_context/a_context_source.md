---
tags: [contexto, fonte-unica, template]
status: rascunho
---
# CONTEXT.md — <NOME DO PROJETO>

> **Orçamento: ≤ 4.000 caracteres** (valide com `python scripts/check.py`). Atualize **por substituição** — reescreva a seção, nunca anexe no fim.
> Histórico datado → [[a_changelog|CHANGELOG]] · decisão + evidência → [[c_decisions|DECISIONS]] · detalhe de domínio → `a_context/`.
> Este é o único arquivo que TODA sessão carrega: cada caractere aqui é pago em cada sessão.
> Preencha na Fase 0 com [[b_process/skills/context-bootstrap/SKILL|bootstrap-contexto]]. Formato de referência: [[b_reference_case_spo|caso de referência]].

## Objetivo (3 linhas)
<O que o app faz e para quem. Uma frase de valor. Um não-objetivo explícito.>

## Restrições inegociáveis (violou = inválido)
- <ex.: roda local · custo R$ 0 · nenhum segredo versionado · não inventar dado — lacuna declarada fica declarada>

## Arquitetura (decida na Fase 1, congele como D-NN)
- **Forma:** <monólito modular | microserviços | monólito + 1 serviço extraído> — use [[b_process/skills/architecture-monolith/SKILL|arquitetura-monolito]] ou [[b_process/skills/architecture-microservices/SKILL|arquitetura-microservicos]] para decidir com portão.
- **Frontend:** <SPA única | MFE> · **Borda:** <API direta | BFF> · **Auth:** <sessão | OIDC/JWT>

## Stack + restrições da stack (preencha ANTES de pedir código)
- **Stack:** <linguagem, framework, banco, runtime, infra>
- **Restrições:** <o que a stack NÃO suporta/exige — copie do perfil em `b_process/profiles/`>
- **Representações obrigatórias:** <dinheiro em Int/centavos · datas UTC ISO · IDs opacos · encoding>
- **Quem roda o quê:** agente = código + testes indicativos no sandbox · dono = testes/build oficiais, migrations em produção, deploy, git push

## Critério de aceite (o portão)
- <comando objetivo, ex.: `npm run typecheck && npm run build` verdes na máquina do dono>
- <cobertura/teste, ex.: teste de sistema do fluxo crítico verde ponta a ponta>
- <segurança, ex.: rota sensível sem sessão → 401; nenhum segredo no repo>

## Estado atual (formato fixo — 1 linha por item, SEM prosa corrida)
- **Versão:** <baseline vigente, só ela>
- **Pronto:** <módulos concluídos, só nomes>
- **Em andamento (máx 1):** <a única tarefa ativa>
- **Próximo:** <o passo seguinte>
- **Bloqueado/pendente:** <o que espera o dono ou dado externo>
- **Questões abertas:** <só os IDs Q-NN — detalhe no DECISIONS>

## Temas de domínio em `a_context/` (o agente lê SOB DEMANDA)
- `a_context/<tema>.md` — <liste aqui os temas do projeto e quando cada um é relevante>

> Mapa de leitura completo e protocolo do agente: [[CLAUDE]]. Ficam lá, e não aqui, porque a
> ferramenta os carrega sozinha — dentro deste arquivo custariam 20% do orçamento em toda sessão.
