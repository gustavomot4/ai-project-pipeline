---
tags: [agente, contrato]
status: atual
---
# Contrato de leitura do agente

Este arquivo é carregado sozinho pela ferramenta em toda sessão. Ele existe para que o
`a_context/a_context_source.md` não precise gastar o próprio orçamento explicando como ser lido.

## O que carregar, nesta ordem

1. **`a_context/a_context_source.md`** — sempre, inteiro. É a fonte única de estado do projeto.
2. **Uma** skill de `b_process/skills/`, a do papel desta sessão. Duas skills = duas responsabilidades
   disputando o contexto.
3. **Só o arquivo do momento** — o módulo que esta sessão toca, mais nada.

**Não varra o repositório.** Não leia `d_history/a_changelog.md` nem `e_qa/` por conta própria: são grandes,
são históricos, e nenhuma sessão precisa deles. Se faltar informação, peça — não procure.

| Arquivo | Ler quando |
|---|---|
| `a_context/b_plan.md` | implementar módulo novo — só o contrato dele |
| `a_context/c_decisions.md` | sessão de evolução (inteiro); nas demais, só o D-NN citado |
| `a_context/<tema>.md` | a tarefa tocar o tema |
| `b_process/c_backlog.md` | início de sessão de trabalho |
| `d_history/a_changelog.md`, `e_qa/` | **nunca**, salvo pedido explícito do dono |

## Como trabalhar

0. **Releia do disco.** Antes de agir sobre um arquivo, leia-o de novo — mesmo que já o
   tenha visto nesta conversa. O dono edita entre os turnos, e o estado que você lembra
   pode ter três turnos de idade.
1. **Delta, nunca regeneração.** Só os trechos alterados. Arquivo novo pode vir inteiro.
2. **Escopo é o módulo desta sessão.** Precisa mexer em outro? **Pare e avise.**
3. Antes de depurar "bug": é código ou é **falta de dado**? Cheque o dado primeiro.
4. Bug pré-existente encontrado? Registre `QA-NN`; não conserte de carona.
5. **Lacuna declarada fica declarada.** Nunca invente dado, fonte ou número.
6. Regra de negócio ambígua não é sua para decidir: registre `Q-NN` e pare.
7. Termine dizendo o que o **dono** roda na máquina real (teste oficial, migration, restart —
   processo vivo tem cache). Seu sandbox é indicativo, nunca portão.

## Fechamento de sessão

```
D-NN / QA-NN / Q-NN registrados em a_context/c_decisions.md
   → "Estado atual" de a_context/a_context_source.md reescrito POR SUBSTITUIÇÃO
     (nunca anexado no fim)
   → linha datada em d_history/a_changelog.md
   → commit citando os IDs:  TIPO: o que mudou (D-NN/QA-NN)
   → lição nova? 1 linha em b_process/d_agent_learnings.md
```

Antes de commitar: `python scripts/check.py`. Antes de entregar (Fase 6):
`python scripts/check.py --historico-completo`.

## Limites deste kit (não os contorne em silêncio)

O `a_context/a_context_source.md` tem orçamento de **4.000 caracteres**, cobrado por script. Não coube? O excedente
vai para `a_context/<tema>.md` — **nunca** para prosa comprimida, e nunca estourando o teto.
Estado numérico (versão, métricas, contagens) mora **só** no `a_context/a_context_source.md`; todo outro documento
aponta para lá.

Se uma regra aqui atrapalhar a tarefa, diga isso ao dono em vez de contorná-la.
