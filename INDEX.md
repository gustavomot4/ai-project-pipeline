---
tags: [inicio, moc]
status: atual
---
# 🚀 Pipeline de apps com IA — mapa do vault

> Esta nota é **só um mapa**: cada linha aponta e sai da frente. O caminho executável está no [[a_roadmap|ROTEIRO]]; os porquês e os limites, no [[README]].
> **Primeira vez aqui?** Comece pelo [[f_glossary_and_primer|Primer]] — para que o pipeline serve e o que cada termo quer dizer (delta, portão, D-NN, contexto-fonte…).
> Primeira vez no Obsidian? [[a_obsidian_guide|Guia do Obsidian]].

## Começar
1. Projeto novo: `python scripts/new_project.py ../meu-app --name "Meu App" --code src`
2. `cd ../meu-app && git init && python 77777777_*_Project_DOCs/scripts/task.py hook` — a higiene passa a rodar sozinha em todo commit
3. Abra o [[a_roadmap|ROTEIRO]] e siga da Fase 0

> **Todos os comandos moram em um lugar só:** `python scripts/task.py --help`.
> Projeto que já usa o kit e ficou para trás: `python scripts/new_project.py <projeto> --upgrade --dry-run` mostra o que mudaria no **processo**, sem tocar na verdade do projeto.

> **Onde cada coisa mora** e como se nomeia: [[e_repository_standard|padrão do repositório]]. Este kit **é** a pasta de documentação desse padrão — `new_project.py` o instala num projeto como `77777777_<TAG>_Project_DOCs/`.

## Os arquivos do dia a dia
| Arquivo | Para quê |
|---|---|
| [[f_glossary_and_primer\|PRIMER]] | **comece aqui:** para que serve, o ciclo e o glossário dos termos |
| [[a_roadmap|ROTEIRO]] | o caminho do dia 1 à entrega, fase por fase |
| [[CLAUDE]] | contrato de leitura do agente — a ferramenta carrega sozinha |
| [[a_context_source|CONTEXT]] | contexto-fonte (≤4.000 chars) — o único que TODA sessão carrega |
| [[b_plan|PLANO]] | módulos, contratos e milestones (congelado após aprovação) |
| [[c_decisions|DECISIONS]] | D-NN decisões · Q-NN pendências suas · QA-NN achados |
| [[c_backlog|BACKLOG]] | fonte única de tarefas |
| [[b_checklist|CHECKLIST]] | os portões que **você** roda antes de aceitar uma entrega |
| [[d_agent_learnings|APRENDIZADOS]] | lições vivas (já vem com as herdadas) |
| [[e_repository_standard|PADRÃO]] | estrutura, nomes de arquivo e convenções de commit |
| [[a_changelog|CHANGELOG]] | histórico datado do projeto (nenhuma sessão carrega) |
| [[README]] | as 7 regras, seu papel e **onde o kit para** |

## Os 24 agentes ([[b_process/skills/README|skills/]])
Cada um é uma skill instalável, com regras e portão próprios. **Uma skill por sessão.**

**Fases:** [[b_process/skills/context-bootstrap/SKILL|bootstrap-contexto]] (projeto novo) · [[b_process/skills/existing-project-adoption/SKILL|adocao-projeto-existente]] (projeto que já roda) · [[b_process/skills/planner/SKILL|planejador]] · [[b_process/skills/artifact-consistency/SKILL|consistencia-artefatos]] · [[b_process/skills/evolution-auditor/SKILL|auditor-evolucao]] · [[b_process/skills/delivery-review/SKILL|revisao-entrega]] · [[b_process/skills/retrospective/SKILL|retrospectiva]]
**Arquitetura:** [[b_process/skills/architecture-monolith/SKILL|monolito]] (default) · [[b_process/skills/architecture-microservices/SKILL|microserviços]]
**Backend:** [[b_process/skills/backend-domain/SKILL|domínio]] · [[b_process/skills/backend-bff/SKILL|BFF]] · [[b_process/skills/microservice-sync/SKILL|integração síncrona]]
**Frontend:** [[b_process/skills/frontend-uiux/SKILL|UI/UX]] · [[b_process/skills/frontend-mfe/SKILL|MFE]]
**Transversais:** [[b_process/skills/authentication/SKILL|autenticação]] · [[b_process/skills/iac-docker-terraform/SKILL|IaC]] · [[b_process/skills/testing/SKILL|testes]] · [[b_process/skills/guardrails-review/SKILL|guardrails]] · [[b_process/skills/dependencies-supply-chain/SKILL|dependências]] · [[b_process/skills/privacy-personal-data/SKILL|privacidade]]
**Sistema vivo:** [[b_process/skills/debugging-diagnosis/SKILL|depuração]] · [[b_process/skills/performance/SKILL|performance]] · [[b_process/skills/observability/SKILL|observabilidade]]
**Dados:** [[b_process/skills/data-analysis/SKILL|dados e análise]]

## Apoio
| Pasta | Para quê |
|---|---|
| [[a_generic\|b_process/profiles/]] | restrições prontas por stack: [[b_web_nextjs\|web-nextjs]] · [[c_data_python\|dados-python]] · [[a_generic\|genérico]] (método p/ qualquer stack) |
| [[b_process/templates/README\|b_process/templates/]] | modelos de D-NN, QA-NN e fecho de sessão |
| [[a_context/README\|a_context/]] | domínio por tema, leitura sob demanda (nasce vazia) |
| [[e_qa/README\|e_qa/]] | relatórios de QA e auditoria, com timestamp no nome — nenhuma sessão carrega |
| [[b_reference_case_spo\|c_technical_docs/]] | caso de referência (narrativa, não medição — ver a ressalva lá) |

## Higiene
`python scripts/task.py check` — reprova orçamento estourado, estado duplicado, WIP acima do declarado, skill fora do esquema, link quebrado, segredo versionado, ID inexistente e tarefa apontando módulo que não existe. Com o hook instalado, roda em todo commit.

Antes de entregar, `python scripts/task.py check-all`: no dia a dia a varredura de segredo olha só os 30 commits recentes, e o script diz qual alcance usou.

`python scripts/task.py test` roda os testes de regressão dos próprios scripts — os mesmos que o CI roda em Linux **e Windows**, porque os dois bugs de encoding que o kit já pagou não reproduzem no Linux.
