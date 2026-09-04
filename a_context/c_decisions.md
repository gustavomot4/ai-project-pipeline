---
tags: [decisoes, template]
status: rascunho
---
# DECISIONS.md — decisões (D-NN), questões abertas (Q-NN) e QA (QA-NN)

> **Append-only:** decisão nova = linha nova; reversão = linha nova com `SUPERSEDE D-XX`, nunca editar a antiga.
> **Teto: 2 frases por linha.** Evidência longa (números, ângulos testados, análise de opções) vira nota em `e_qa/<slug>.md` linkada na coluna Evidência — senão este arquivo incha e a Fase 5, que o carrega inteiro, fica cara.
> **Projeto longo:** passou de ~12.000 caracteres, mova SUPERSEDIDAS e rejeitadas antigas para `e_qa/decisions_archive.md` (IDs preservados) e deixe um ponteiro aqui.
> **Registre as rejeições.** Um projeto saudável rejeita mais do que adota — a lista de rejeitados é o que impede a IA de re-propor o que já morreu. Exemplo real: [[b_reference_case_spo|caso de referência]].

## Decisões
| # | Data | Status | Decisão (curta) | Evidência (número-chave + link) |
|---|---|---|---|---|
| D-01 | <data> | ADOTADO | <ex.: forma = monólito modular> | <o que decidiu; detalhe: `e_qa/<slug>.md`> |
| D-02 | <data> | REJEITADO | <ex.: microserviços desde o dia 1> | <o custo/número que matou> |
| D-03 | <data> | SUPERSEDE D-01 | <nova escolha> | <o que mudou> |

## Questões abertas (Q-NN — decisões do DONO, não do agente)
> **Respondida = a linha diz `RESPONDIDA` (ou vem riscada) e aponta o `D-NN` que a fechou.**
> Enquanto isso não acontece a questão é aberta, e o `check.py` cobra que ela apareça no
> [[a_context_source|CONTEXT]] — fila que o dono não vê não é fila, é espera.
| # | Questão | Decidir quando |
|---|---|---|
| Q-01 | <ex.: quais formas de pagamento entram no escopo?> | <marco/condição> |

## Achados de QA (QA-NN — citados no commit: `fix: QA-NN …`)
> Preenchido pelas sessões de [[b_process/skills/guardrails-review/SKILL|guardrails-review]]. Relatório completo de cada passagem em `e_qa/<n>_qa_pass<NN>_report_<AAMMDD>_<HHMM>.md`; aqui fica só a linha rastreável.
>
> **`Sev.`** é `Crítico` · `Alto` · `Médio` · `Baixo`, e é do EFEITO, nunca do esforço.
> **`Origem` = quem achou:** `portão` (o `scripts/check.py` ou um hook reprovou) · `revisão`
> (uma passagem de `guardrails-review`) · `dono` (você viu usando) · `usuário` (chegou de fora).
> É **um campo por achado, escrito no instante em que a linha nasce** — e é o único número
> deste kit que não é ele se elogiando por seguir a própria regra: "o portão pegou N defeitos
> que ninguém tinha visto" é afirmação sobre o mundo, não sobre o processo. Sem a coluna, esse
> número não é zero: é irrespondível, e um kit que não sabe se o próprio portão pega alguma
> coisa está vendendo a parte que ele mais anuncia sem nenhuma medida atrás.

| # | Data | Sev. | Origem | Onde | O que quebrava | Correção | Fechado em |
|---|---|---|---|---|---|---|---|
| QA-01 | <data> | <gravidade> | <origem> | `arquivo:linha` | <invariante quebrada> | <o que mudou> | _(aberto)_ |
