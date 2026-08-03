---
tags: [agente, contrato]
status: atual
---
# Contrato de leitura do agente

Este arquivo é carregado sozinho pela ferramenta em toda sessão. Ele existe para que o
`CONTEXT.md` não precise gastar o próprio orçamento explicando como ser lido.

## O que carregar, nesta ordem

1. **`CONTEXT.md`** — sempre, inteiro. É a fonte única de estado do projeto.
2. **Uma** skill de `skills/`, a do papel desta sessão. Duas skills = duas responsabilidades
   disputando o contexto.
3. **Só o arquivo do momento** — o módulo que esta sessão toca, mais nada.

**Não varra o repositório.** Não leia `CHANGELOG.md` nem `dev/` por conta própria: são grandes,
são históricos, e nenhuma sessão precisa deles. Se faltar informação, peça — não procure.

| Arquivo | Ler quando |
|---|---|
| `PLANO.md` | implementar módulo novo — só o contrato dele |
| `DECISIONS.md` | sessão de evolução (inteiro); nas demais, só o D-NN citado |
| `contexto/<tema>.md` | a tarefa tocar o tema |
| `BACKLOG.md` | início de sessão de trabalho |
| `CHANGELOG.md`, `dev/` | **nunca**, salvo pedido explícito do dono |

## Como trabalhar

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
D-NN / QA-NN / Q-NN registrados em DECISIONS.md
   → "Estado atual" do CONTEXT.md reescrito POR SUBSTITUIÇÃO (nunca anexado no fim)
   → linha datada no CHANGELOG.md
   → commit citando os IDs:  tipo(escopo): D-NN/QA-NN …
   → lição nova? 1 linha em APRENDIZADOS.md
```

Antes de commitar: `python scripts/checar.py`. Antes de entregar (Fase 6):
`python scripts/checar.py --historico-completo`.

## Limites deste kit (não os contorne em silêncio)

O `CONTEXT.md` tem orçamento de **4.000 caracteres**, cobrado por script. Não coube? O excedente
vai para `contexto/<tema>.md` — **nunca** para prosa comprimida, e nunca estourando o teto.
Estado numérico (versão, métricas, contagens) mora **só** no `CONTEXT.md`; todo outro documento
aponta para lá.

Se uma regra aqui atrapalhar a tarefa, diga isso ao dono em vez de contorná-la.
