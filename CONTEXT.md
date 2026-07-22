# CONTEXT.md — <NOME DO PROJETO>

> **Orçamento: ≤ 4.000 caracteres** (valide com `python scripts/checar.py`). Atualize **por substituição** — reescreva a seção, nunca anexe no fim.
> Histórico datado → `CHANGELOG.md`. Decisão + evidência → `DECISIONS.md`. Detalhe de domínio → `contexto/`.
> Este é o único arquivo que TODA sessão carrega: cada caractere daqui é pago em cada sessão.

## Objetivo (3 linhas)
<O que o sistema faz e para quem. Uma frase de valor. Um não-objetivo explícito.>

## Restrições inegociáveis (violou = inválido)
- <ex.: custo R$ 0 · roda local · nenhum segredo versionado · não inventar dados — lacuna declarada fica declarada>

## Stack + restrições da stack (preencha ANTES de pedir código)
- **Stack:** <linguagem, framework, banco, runtime>
- **Restrições:** <o que a stack NÃO suporta/exige — copie do perfil em `perfis/`>
- **Quem roda o quê:** agente = código + testes indicativos no sandbox · dono = testes oficiais, downloads/chaves, git push, deploy

## Critério de aceite (o portão)
- <comando objetivo, ex.: `pytest -q` verde na máquina do dono>
- <métrica com limiar, ex.: Δmétrica pareada com IC que não cruza zero, sem regressão das demais>

## Estado atual (formato fixo — 1 linha por item, SEM prosa corrida)
- **Versão:** <baseline/versão vigente, só ela>
- **Pronto:** <módulos concluídos, só nomes>
- **Em andamento (máx 1):** <a única tarefa ativa>
- **Próximo:** <o passo seguinte>
- **Bloqueado/pendente:** <o que espera o dono ou dado externo>
- **Questões abertas:** <só os IDs Q-NN — detalhe no DECISIONS.md>

## Mapa de leitura (o agente lê SOB DEMANDA, nunca por padrão)
| Arquivo | Ler quando |
|---|---|
| `DECISIONS.md` | Fase 5 (evolução) inteiro; nas demais, só o D-NN citado |
| `PLANO.md` | implementar módulo novo (só o contrato dele) |
| `contexto/<tema>.md` | a tarefa tocar o tema (liste aqui os temas do projeto) |
| `BACKLOG.md` | início de sessão de trabalho |
| `CHANGELOG.md`, `dev/` | **nunca** (só se o dono pedir) |

## Protocolo do agente (toda sessão)
1. Leia este arquivo + o prompt do papel + só o arquivo do momento. **Não varra o repositório.**
2. Trabalhe por **delta**: devolva só trechos alterados/arquivos novos.
3. Fechamento: D-NN/QA-NN registrados → "Estado atual" reescrito por substituição → datado no `CHANGELOG.md` → mensagem de commit (`tipo(escopo): D-NN/QA-NN …`) → lição nova? 1 linha no `APRENDIZADOS.md`.
