---
tags: [dev, evidencia]
status: atual
---
# dev/ — evidências e relatórios

Evidência longa que não cabe (e não deve caber) no [[DECISIONS]]: números de um portão, análise de opções descartadas, POCs datadas e **os relatórios de revisão adversarial**. Linkada a partir do D-NN/QA-NN correspondente. **Nenhuma sessão carrega esta pasta** — só se o dono pedir.

## O que gravar aqui
| Arquivo | Quando |
|---|---|
| `qa-AAAA-MM-DD.md` | **toda** sessão de [[skills/guardrails-review/SKILL\|guardrails-review]]. Sem relatório, a fase de QA não aconteceu — mesmo com placar zero |
| `<slug>.md` | a evidência de um D-NN: os números, os ângulos testados, o que matou a alternativa |
| `decisions-arquivo.md` | quando o [[DECISIONS]] passar de ~12.000 caracteres: mova para cá as SUPERSEDIDAS e rejeitadas antigas, preservando os IDs |

## Por que os relatórios ficam aqui, e não no contexto
Porque a memória de QA é grande e só interessa quando alguém investiga um achado específico. O que sobe para o [[DECISIONS]] é **uma linha por achado** (`QA-NN`, severidade, onde, o que quebrava, correção). O detalhe — reprodução, saída de comando, o que não deu para verificar — fica no relatório daqui.

Num projeto real deste kit foram 14 passagens e 84 achados: no contexto isso teria custado caro em toda sessão; em `dev/`, custou zero e continuou consultável.
