---
tags: [inicio, moc]
status: atual
---
# 🚀 Pipeline de apps com IA — mapa do vault

> Esta nota é **só um mapa**: cada linha aponta e sai da frente. O caminho executável está no [[ROTEIRO]]; os porquês e os limites, no [[README]].
> Primeira vez no Obsidian? [[GUIA-OBSIDIAN]].

## Começar
1. Projeto novo: `python scripts/novo-projeto.py ../meu-app --nome "Meu App"`
2. `python scripts/instalar-hook.py` — a higiene passa a rodar sozinha em todo commit
3. Abra o [[ROTEIRO]] e siga da Fase 0

## Os arquivos do dia a dia
| Arquivo | Para quê |
|---|---|
| [[ROTEIRO]] | o caminho do dia 1 à entrega, fase por fase |
| [[CONTEXT]] | contexto-fonte (≤4.000 chars) — o único que TODA sessão carrega |
| [[PLANO]] | módulos, contratos e milestones (congelado após aprovação) |
| [[DECISIONS]] | D-NN decisões · Q-NN pendências suas · QA-NN achados |
| [[BACKLOG]] | fonte única de tarefas |
| [[CHECKLIST]] | os portões que **você** roda antes de aceitar uma entrega |
| [[APRENDIZADOS]] | lições vivas (já vem com as herdadas) |
| [[CHANGELOG]] | histórico datado do projeto (nenhuma sessão carrega) |
| [[README]] | as 7 regras, seu papel e **onde o kit para** |

## Os 17 agentes ([[skills/LEIA-ME|skills/]])
Cada um é uma skill instalável, com regras e portão próprios. **Uma skill por sessão.**

**Fases:** [[skills/bootstrap-contexto/SKILL|bootstrap-contexto]] · [[skills/planejador/SKILL|planejador]] · [[skills/auditor-evolucao/SKILL|auditor-evolucao]] · [[skills/revisao-entrega/SKILL|revisao-entrega]] · [[skills/retrospectiva/SKILL|retrospectiva]]
**Arquitetura:** [[skills/arquitetura-monolito/SKILL|monolito]] (default) · [[skills/arquitetura-microservicos/SKILL|microserviços]]
**Backend:** [[skills/backend-dominio/SKILL|domínio]] · [[skills/backend-bff/SKILL|BFF]] · [[skills/microservice-sync/SKILL|integração síncrona]]
**Frontend:** [[skills/frontend-uiux/SKILL|UI/UX]] · [[skills/frontend-mfe/SKILL|MFE]]
**Transversais:** [[skills/autenticacao/SKILL|autenticação]] · [[skills/iac-docker-terraform/SKILL|IaC]] · [[skills/testes/SKILL|testes]] · [[skills/guardrails-review/SKILL|guardrails]]
**Dados:** [[skills/dados-analise/SKILL|dados e análise]]

## Apoio
| Pasta | Para quê |
|---|---|
| [[perfis/perfil-generico\|perfis/]] | restrições prontas por stack: [[perfis/perfil-web-nextjs\|web-nextjs]] · [[perfis/perfil-dados-python\|dados-python]] · [[perfis/perfil-generico\|genérico]] (método p/ qualquer stack) |
| [[templates/LEIA-ME\|templates/]] | modelos de D-NN, QA-NN e fecho de sessão |
| [[contexto/LEIA-ME\|contexto/]] | domínio por tema, leitura sob demanda (nasce vazia) |
| [[dev/LEIA-ME\|dev/]] | evidências e relatórios de QA — nenhuma sessão carrega |
| [[exemplos/caso-spo\|exemplos/]] | caso de referência (narrativa, não medição — ver a ressalva lá) |

## Higiene
`python scripts/checar.py` — reprova orçamento estourado, estado duplicado, WIP acima do declarado, skill inválida, link quebrado, nota órfã, segredo versionado e ID inexistente. Com o hook instalado, roda em todo commit.
