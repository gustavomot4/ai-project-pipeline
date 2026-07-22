# DECISIONS.md — registro de decisões (ADRs)

> Memória durável do projeto. Uma linha por decisão que "fecha" um assunto. É isto que torna o
> projeto auditável e impede a IA (e você) de re-litigar o que já foi decidido. Foi o ponto mais
> forte dos seus dois projetos (D-NN no SCM, QA-NN no SPO) — aqui ele vira padrão.

## Como usar
- **Adotou algo?** Registre como `ADOTADO` com o motivo e a evidência (número, se houver).
- **Rejeitou algo?** Registre como `REJEITADO` — isto vale ouro: vira a "lista do que já falhou"
  que você cola no prompt do auditor (`04-auditor-evolucao.md`) para não re-explorar o mesmo beco.
- **Nunca apague** uma decisão; se mudou, crie uma nova D-NN que **supersede** a antiga.
- Bugs têm a própria numeração: `QA-NN` (achados do QA adversarial), citados no commit/código.

## Formato
`D-NN | data | ADOTADO/REJEITADO/SUPERSEDE D-XX | título | motivo + evidência`

## Decisões
| ID | Data | Status | Título | Motivo / evidência |
|---|---|---|---|---|
| D-01 | <data> | ADOTADO | <ex.: Stack = Next.js + Prisma + SQLite> | <por quê> |
| D-02 | <data> | ADOTADO | <ex.: Sem ML / sem dado pago> | <restrição de projeto> |
| D-03 | <data> | REJEITADO | <ex.: Enum nativo no Prisma> | <provider=sqlite não suporta → usar String> |

## Achados de QA (do Fase 4)
| ID | Data | Severidade | Onde | O que estava errado | Correção |
|---|---|---|---|---|---|
| QA-01 | <data> | <Crítico/Alto/Médio/Baixo> | `<arquivo:linha>` | <invariante quebrada> | <o que mudou> |
