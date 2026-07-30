---
tags: [inicio, moc]
status: atual
---
# 🚀 Pipeline de Apps com IA — comece aqui

Kit para tirar uma **aplicação** do zero com agentes de IA e sustentá-la até a entrega: contexto orçado, decisões rastreáveis, portões objetivos, revisão adversarial e 12 agentes especializados. Primeira vez no Obsidian? [[GUIA-OBSIDIAN]].

> **Se você só vai ler uma coisa, leia o [[ROTEIRO]]** — é o caminho completo, em ordem, com qual agente usar em cada passo e o portão que fecha cada um.

## 🧭 Os arquivos que você vai usar todo dia
| Arquivo | Para quê |
|---|---|
| [[ROTEIRO]] | o caminho do dia 1 à entrega, fase por fase |
| [[CONTEXT]] | contexto-fonte do projeto (≤4.000 chars) — o único que TODA sessão carrega |
| [[PLANO]] | módulos, contratos e milestones (congelado após aprovação) |
| [[DECISIONS]] | D-NN decisões · Q-NN pendências suas · QA-NN bugs |
| [[BACKLOG]] | fonte única de tarefas |
| [[CHECKLIST]] | os portões que **você** roda antes de aceitar uma entrega |
| [[APRENDIZADOS]] | lições vivas (já vem com as herdadas) |
| [[CHANGELOG]] | histórico datado do projeto (nenhuma sessão carrega) |
| [[templates/LEIA-ME\|templates/]] | modelos de D-NN, QA-NN e **fecho de sessão** — o ritual em um clique |
| [[README]] | as 7 regras e como o kit evolui |

## 🤖 Os agentes ([[skills/LEIA-ME|skills/]])
Cada um é uma skill instalável, com regras e portão próprios. **Uma skill por sessão.**

**Arquitetura:** [[skills/arquitetura-monolito/SKILL|monolito]] (default) · [[skills/arquitetura-microservicos/SKILL|microserviços]]
**Backend:** [[skills/backend-dominio/SKILL|domínio]] · [[skills/backend-bff/SKILL|BFF]] · [[skills/microservice-sync/SKILL|integração síncrona]]
**Frontend:** [[skills/frontend-uiux/SKILL|UI/UX]] · [[skills/frontend-mfe/SKILL|MFE]]
**Transversais:** [[skills/autenticacao/SKILL|autenticação]] · [[skills/iac-docker-terraform/SKILL|IaC (Docker/Terraform)]] · [[skills/testes/SKILL|testes]] · [[skills/guardrails-review/SKILL|guardrails (review)]]
**Dados:** [[skills/dados-analise/SKILL|dados e análise]] (coleta, parser, métrica, modelo — quando o entregável é **um número**)

## 📋 Prompts de fase ([[prompts/00-bootstrap-contexto|prompts/]])
[[prompts/00-bootstrap-contexto|00 bootstrap]] · [[prompts/01-planejador|01 plano]] · [[prompts/02-implementador|02 implementação]] · [[prompts/03-qa-adversarial|03 QA]] · [[prompts/04-auditor-evolucao|04 evolução]] · [[prompts/05-revisao-entrega|05 entrega]] · [[prompts/06-retrospectiva|06 retrospectiva]]

## 🏁 Primeiros 30 minutos
1. **Projeto novo?** `python scripts/novo-projeto.py ../meu-app --nome "Meu App"` — copia o kit limpo, sem o que é só do kit. Vai trabalhar aqui mesmo? Pule este passo.
2. Leia o [[ROTEIRO]] até o fim da Fase 1 (5 min).
3. Instale as skills na sua ferramenta de IA, ou deixe os `SKILL.md` à mão para colar.
4. Abra uma sessão com [[prompts/00-bootstrap-contexto]] e descreva seu projeto cru. Responda as ≤5 perguntas.
5. Escolha o perfil da sua stack em `perfis/` e cole as restrições no [[CONTEXT]].
6. Rode `python scripts/checar.py` — se passar, seu [[CONTEXT]] está no orçamento e você tem um projeto começado.

## 📐 Padrão de qualidade
[[exemplos/caso-spo]] destila um app real construído com este kit: ~10 dias, 14 passagens de revisão, 84 achados corrigidos, entregue e rodando na máquina do cliente. Use como aferição do que "pronto" significa — e como lista de armadilhas que você não precisa pagar de novo.
