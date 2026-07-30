---
tags: [decisoes, template]
status: rascunho
---
# DECISIONS.md — decisões (D-NN), questões abertas (Q-NN) e QA (QA-NN)

> **Append-only:** decisão nova = linha nova; reversão = linha nova com `SUPERSEDE D-XX`, nunca editar a antiga.
> **Teto: 2 frases por linha.** Evidência longa (números, ângulos testados, análise de opções) vira nota em `dev/<slug>.md` linkada na coluna Evidência — senão este arquivo incha e a Fase 5, que o carrega inteiro, fica cara.
> **Projeto longo:** passou de ~12.000 caracteres, mova SUPERSEDIDAS e rejeitadas antigas para `dev/decisions-arquivo.md` (IDs preservados) e deixe um ponteiro aqui.
> **Registre as rejeições.** Um projeto saudável rejeita mais do que adota — a lista de rejeitados é o que impede a IA de re-propor o que já morreu. Exemplo real: [[exemplos/caso-spo]].

## Decisões
| # | Data | Status | Decisão (curta) | Evidência (número-chave + link) |
|---|---|---|---|---|
| D-01 | <data> | ADOTADO | <ex.: forma = monólito modular> | <o que decidiu; detalhe: `dev/<slug>.md`> |
| D-02 | <data> | REJEITADO | <ex.: microserviços desde o dia 1> | <o custo/número que matou> |
| D-03 | <data> | SUPERSEDE D-01 | <nova escolha> | <o que mudou> |

## Questões abertas (Q-NN — decisões do DONO, não do agente)
| # | Questão | Decidir quando |
|---|---|---|
| Q-01 | <ex.: quais formas de pagamento entram no escopo?> | <marco/condição> |

## Achados de QA (QA-NN — citados no commit: `fix: QA-NN …`)
> Preenchido pelas sessões de [[skills/guardrails-review/SKILL|guardrails-review]] e `prompts/03`. Relatório completo de cada passagem em `dev/qa-AAAA-MM-DD.md`; aqui fica só a linha rastreável.

| # | Data | Sev. | Onde | O que quebrava | Correção |
|---|---|---|---|---|---|
| QA-01 | <data> | <Crítico/Alto/Médio/Baixo> | `arquivo:linha` | <invariante quebrada> | <o que mudou> |
