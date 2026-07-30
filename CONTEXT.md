---
tags: [contexto, fonte-unica, template]
status: rascunho
---
# CONTEXT.md — <NOME DO PROJETO>

> **Orçamento: ≤ 4.000 caracteres** (valide com `python scripts/checar.py`). Atualize **por substituição** — reescreva a seção, nunca anexe no fim.
> Histórico datado → [[CHANGELOG]] · decisão + evidência → [[DECISIONS]] · detalhe de domínio → `contexto/`.
> Este é o único arquivo que TODA sessão carrega: cada caractere aqui é pago em cada sessão.
> Preencha na Fase 0 com [[skills/bootstrap-contexto/SKILL|bootstrap-contexto]]. Formato de referência: [[exemplos/caso-spo]].

## Objetivo (3 linhas)
<O que o app faz e para quem. Uma frase de valor. Um não-objetivo explícito.>

## Restrições inegociáveis (violou = inválido)
- <ex.: roda local · custo R$ 0 · nenhum segredo versionado · não inventar dado — lacuna declarada fica declarada>

## Arquitetura (decida na Fase 1, congele como D-NN)
- **Forma:** <monólito modular | microserviços | monólito + 1 serviço extraído> — use [[skills/arquitetura-monolito/SKILL|arquitetura-monolito]] ou [[skills/arquitetura-microservicos/SKILL|arquitetura-microservicos]] para decidir com portão.
- **Frontend:** <SPA única | MFE> · **Borda:** <API direta | BFF> · **Auth:** <sessão | OIDC/JWT>

## Stack + restrições da stack (preencha ANTES de pedir código)
- **Stack:** <linguagem, framework, banco, runtime, infra>
- **Restrições:** <o que a stack NÃO suporta/exige — copie do perfil em `perfis/`>
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

## Mapa de leitura (o agente lê SOB DEMANDA, nunca por padrão)
| Arquivo | Ler quando |
|---|---|
| [[PLANO]] | implementar módulo novo (só o contrato dele) |
| [[DECISIONS]] | Fase 5 (evolução) inteiro; nas demais, só o D-NN citado |
| `contexto/<tema>.md` | a tarefa tocar o tema (liste aqui os temas do projeto) |
| [[BACKLOG]] | início de sessão de trabalho |
| [[CHANGELOG]], `dev/` | **nunca** (só se o dono pedir) |

## Protocolo do agente (toda sessão, qualquer skill)
1. Leia este arquivo + **uma** skill do papel + só o arquivo do momento. **Não varra o repositório.**
2. Trabalhe por **delta**: só trechos alterados; arquivo novo pode vir inteiro.
3. Escopo = o módulo desta sessão. Precisa mexer em outro? **Pare e avise.**
4. Antes de depurar "bug": é código ou é **falta de dado**? Cheque o dado primeiro.
5. Bug pré-existente encontrado? Registre QA-NN; não conserte de carona.
6. Termine dizendo o que o **dono** roda na máquina real (teste oficial, migration, restart — processo vivo tem cache).
7. Fechamento: D-NN/QA-NN registrados → "Estado atual" reescrito por substituição → datado em [[CHANGELOG]] → commit (`tipo(escopo): D-NN/QA-NN …`) → lição nova? 1 linha em [[APRENDIZADOS]].
