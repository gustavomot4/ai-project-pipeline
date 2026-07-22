# DECISIONS.md — decisões (D-NN), questões abertas (Q-NN) e QA (QA-NN)

> **Append-only:** decisão nova = linha nova; reversão = linha nova com `SUPERSEDE D-XX`, nunca editar a antiga.
> **Teto: 2 frases por linha.** Evidência longa (números, ICs, ângulos testados) vira nota em `dev/<slug>.md` linkada na coluna Evidência — senão este arquivo incha e a Fase 5, que o carrega inteiro, fica cara.

## Decisões
| # | Data | Status | Decisão (curta) | Evidência (número-chave + link) |
|---|---|---|---|---|
| D-01 | <data> | ADOTADO | <ex.: Stack = Python + SQLite> | <motivo em 1 frase> |
| D-02 | <data> | REJEITADO | <ex.: feature X no módulo Y> | <o número que matou; detalhe: `dev/gate-x.md`> |
| D-03 | <data> | SUPERSEDE D-01 | <nova escolha> | <o que mudou> |

## Questões abertas (Q-NN — decisões do DONO, não do agente)
| # | Questão | Decidir quando |
|---|---|---|
| Q-01 | <ex.: subir o teto do parâmetro Y?> | <marco/condição, ex.: com os números da M4> |

## Achados de QA (QA-NN — citados no commit: `fix: QA-NN …`)
| # | Data | Sev. | Onde | O que quebrava | Correção |
|---|---|---|---|---|---|
| QA-01 | <data> | <Crítico/Alto/Médio/Baixo> | `arquivo:linha` | <invariante quebrada> | <o que mudou> |
