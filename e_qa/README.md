---
tags: [dev, evidencia]
status: atual
---
# dev/ — evidências e relatórios

Evidência longa que não cabe (e não deve caber) no [[c_decisions|DECISIONS]]: números de um portão, análise de opções descartadas, POCs datadas e **os relatórios de revisão adversarial**. Linkada a partir do D-NN/QA-NN correspondente. **Nenhuma sessão carrega esta pasta** — só se o dono pedir.

## O que gravar aqui
| Arquivo | Quando |
|---|---|
| `<n>_qa_pass<NN>_report_<AAMMDD>_<HHMM>.md` | **toda** sessão de [[b_process/skills/guardrails-review/SKILL\|guardrails-review]]. Sem relatório, a fase de QA não aconteceu — mesmo com placar zero |
| `<slug>.md` | a evidência de um D-NN: os números, os ângulos testados, o que matou a alternativa |
| `decisions_archive.md` | quando o [[c_decisions|DECISIONS]] passar de ~12.000 caracteres: mova para cá as SUPERSEDIDAS e rejeitadas antigas, preservando os IDs |

## Como se nomeia aqui
Relatório é **saída de IA datada**, então leva timestamp `AAMMDD_HHMM` no fim do nome —
uma passagem, um arquivo, imutável:

```
a_qa_pass01_report_260803_1420.md
b_qa_pass02_report_260804_0915.md
c_external_audit_report_260810_1100.md
```

O prefixo de ordem (`a_`, `b_`, `c_`) mantém a leitura cronológica na pasta; o timestamp diz
**quando** aquela passagem aconteceu. Relatório não se reescreve depois do conserto — o que
muda é uma nota no topo dizendo o que já foi resolvido. Ver [[e_repository_standard|padrão do repositório]].

> Esta pasta é do **projeto**. Auditoria do próprio kit não mora aqui — vai para `docs/`, na raiz do repositório do kit. Essa pasta não é copiada para projetos novos (`new_project.py` a exclui por pasta) e é isenta da checagem de IDs, porque relatório de kit cita `D-NN`/`QA-NN` dos projetos-cobaia, que não existem no DECISIONS daqui. Num projeto criado a partir do kit, `docs/` simplesmente não existe.

## Por que os relatórios ficam aqui, e não no contexto
Porque a memória de QA é grande e só interessa quando alguém investiga um achado específico. O que sobe para o [[c_decisions|DECISIONS]] é **uma linha por achado** (`QA-NN`, severidade, onde, o que quebrava, correção). O detalhe — reprodução, saída de comando, o que não deu para verificar — fica no relatório daqui.

Num projeto real deste kit foram 14 passagens e 84 achados: no contexto isso teria custado caro em toda sessão; em `e_qa/`, custou zero e continuou consultável.
