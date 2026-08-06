---
tags: [skills, indice]
status: atual
---
# skills/ — os agentes do pipeline

Cada pasta aqui é uma **skill instalável** (`SKILL.md` com `name` e `description` no frontmatter), no padrão do Claude Code / Cowork. Duas formas de usar:

- **Instalada:** copie a pasta `b_process/skills/<nome>/` para o diretório de skills da sua ferramenta e invoque por nome (ex.: `/backend-dominio`). A `description` faz a skill disparar sozinha quando a tarefa combina.
- **Colada:** abra o `SKILL.md` e cole o conteúdo na sessão. Funciona em qualquer ferramenta de IA.

Em qualquer um dos casos, a sessão recebe **a skill + o [[a_context_source|CONTEXT]] + só o arquivo do momento**. Nunca o repositório inteiro.

## Os 24 agentes

> **Construir é metade do trabalho.** As 5 skills de *sistema vivo* (adoção, depuração, performance, observabilidade, dependências) existem porque um projeto passa muito mais tempo sendo mantido do que sendo criado — e o kit v4 só tinha agente para a criação.

### Fases (antes eram `prompts/`; viraram skills para não pagar duas vezes pela mesma instrução)
| Skill | Quando usar | O que ela protege |
|---|---|---|
| [[b_process/skills/context-bootstrap/SKILL\|bootstrap-contexto]] | Fase 0 — descrever o projeto **novo** | orçamento do CONTEXT, restrições da stack no dia 1, lacuna declarada |
| [[b_process/skills/existing-project-adoption/SKILL\|adocao-projeto-existente]] | Fase 0 — o projeto **já existe** | mapa feito do código (não da doc), baseline real, decisões retroativas, zero edição |
| [[b_process/skills/planner/SKILL\|planejador]] | Fase 1 — gerar o PLANO | contrato por módulo autossuficiente, milestones encadeadas, plano congelável |
| [[b_process/skills/artifact-consistency/SKILL\|consistencia-artefatos]] | Fase 1c — antes do primeiro código | módulo sem tarefa, restrição inegociável sem portão, critério sem número, plano contra decisão rejeitada |
| [[b_process/skills/evolution-auditor/SKILL\|auditor-evolucao]] | depois do baseline estável | lista-morta, portão antes do experimento, prior de 20–30% |
| [[b_process/skills/delivery-review/SKILL\|revisao-entrega]] | Fase 6 — empacotar | segredo na árvore **e no histórico**, cruft, peso, estado duplicado |
| [[b_process/skills/retrospective/SKILL\|retrospectiva]] | fechar milestone | lição generalizável, erro do agente incluído |


### Arquitetura (decidem a forma antes de existir código)
| Skill | Quando usar | O que ela protege |
|---|---|---|
| [[b_process/skills/architecture-monolith/SKILL\|arquitetura-monolito]] | estruturar o projeto; é o **default** | fronteiras internas reais, sem custo distribuído |
| [[b_process/skills/architecture-microservices/SKILL\|arquitetura-microservicos]] | avaliar/fatiar em serviços | tem portão de existência: reprova sem time e observabilidade |

### Backend
| Skill | Quando usar | O que ela protege |
|---|---|---|
| [[b_process/skills/backend-domain/SKILL\|backend-dominio]] | regra de negócio, schema, migration, API | invariantes, dinheiro inteiro, transação, migration aditiva |
| [[b_process/skills/backend-bff/SKILL\|backend-bff]] | camada de borda para uma tela específica | timeout, falha parcial explícita, segredo fora do cliente |
| [[b_process/skills/microservice-sync/SKILL\|microservice-sync]] | serviço chamando serviço | timeout, retry seguro, idempotência, circuit breaker |

### Frontend
| Skill | Quando usar | O que ela protege |
|---|---|---|
| [[b_process/skills/frontend-uiux/SKILL\|frontend-uiux]] | telas, componentes, formulários | 4 estados, mobile-first, erro em linguagem de gente |
| [[b_process/skills/frontend-mfe/SKILL\|frontend-mfe]] | dividir o front em remotes | portão de existência: reprova com 1 time só |

### Transversais
| Skill | Quando usar | O que ela protege |
|---|---|---|
| [[b_process/skills/authentication/SKILL\|autenticacao]] | login, sessão, PIN, rota protegida | segredo por instalação, autorização no servidor, nega por padrão |
| [[b_process/skills/iac-docker-terraform/SKILL\|iac-docker-terraform]] | Docker, compose, Terraform, deploy | artefato pronto (sem build no cliente), rollback testado, `plan` como portão |
| [[b_process/skills/testing/SKILL\|testes]] | teste unitário e de sistema | bordas, invariantes, regressão por QA-NN, determinismo |
| [[b_process/skills/guardrails-review/SKILL\|guardrails-review]] | revisar antes de entregar | 12 frentes de ataque, achado com reprodução, relatório registrado |
| [[b_process/skills/dependencies-supply-chain/SKILL\|dependencias-supply-chain]] | instalar, atualizar ou auditar biblioteca | lockfile versionado, uma atualização por vez, CVE tratada ou aceita com D-NN, licença |
| [[b_process/skills/privacy-personal-data/SKILL\|privacidade-dados-pessoais]] | o sistema guarda dado de pessoas | inventário com finalidade, retenção implementada, exclusão/exportação do titular, nada em log |

### Sistema vivo (o que já roda)
| Skill | Quando usar | O que ela protege |
|---|---|---|
| [[b_process/skills/debugging-diagnosis/SKILL\|depuracao-diagnostico]] | "quebrou", "está errado", "deu erro" | reprodução antes do conserto, causa provada, teste de regressão citando QA-NN |
| [[b_process/skills/performance/SKILL\|performance]] | "está lento" | baseline antes, profiler em vez de intuição, uma mudança por vez, ganho em número |
| [[b_process/skills/observability/SKILL\|observabilidade]] | o sistema roda continuamente | log estruturado, correlação, nada sensível em log, alerta com dono e ação |

### Dados e análise
| Skill | Quando usar | O que ela protege |
|---|---|---|
| [[b_process/skills/data-analysis/SKILL\|dados-analise]] | coleta, parser/ETL, feature, modelo, métrica, qualquer afirmação numérica | amostra real antes do parser, ausente ≠ zero, número com incerteza, zero vazamento treino/teste, rebuild ao mudar fórmula |

> Ela é o par do `perfis/perfil-dados-python` — que existia sem nenhum agente atrás dele. Use quando o entregável for **um número**, não uma tela: aí o portão não é "o teste passa", é "a amostra sustenta a afirmação".

## Como elas se combinam
Ordem típica de uma feature de app:

```
arquitetura-* (uma vez, na Fase 1)
   └─ backend-dominio  →  backend-bff  →  frontend-uiux
         │                                    │
         └────────────  testes  ──────────────┘
                          │
                  guardrails-review  (antes de entregar)
                          │
                iac-docker-terraform  (empacotar/subir)
```

`autenticacao` entra assim que existir área sensível. `microservice-sync` só se houver mais de um serviço. `frontend-mfe` só se o portão de existência aprovar. `dados-analise` entra **antes** de `backend-dominio` quando o projeto nasce de uma fonte de dados externa — é ela que traz a amostra real sem a qual o schema é chute. `privacidade-dados-pessoais` entra junto com o schema, não depois: coluna criada sem finalidade vira obrigação permanente.

Depois que o sistema roda, o ciclo muda de forma:

```
algo quebrou        →  depuracao-diagnostico   (reproduz → prova a causa → corrige com teste)
está lento          →  performance             (baseline → profiler → 1 mudança por vez)
não sei o que houve →  observabilidade         (a resposta é instrumentar, não adivinhar de novo)
subir biblioteca    →  dependencias-supply-chain
projeto herdado     →  adocao-projeto-existente (uma vez, antes de tudo)
```

**A ordem entre elas importa.** "Está lento" sem baseline é `performance`; "está lento **desde ontem**" é `depuracao-diagnostico` — algo mudou, e achar o quê é mais barato que otimizar. Precisar de `depuracao-diagnostico` duas vezes pelo mesmo motivo é sinal de que faltou `observabilidade`.

## Regras que valem para todas
1. **Uma skill por sessão.** Duas skills na mesma sessão = duas responsabilidades disputando o contexto.
2. **Delta, nunca regeneração.**
3. **Portão objetivo antes de "pronto".** Cada skill traz o seu; o [[b_checklist|CHECKLIST]] é o portão da entrega.
4. **Escopo é o módulo da sessão.** Precisa mexer em outro? Pare e avise.
5. **Registre:** decisão → D-NN · bug → QA-NN · pendência do dono → Q-NN, em [[c_decisions|DECISIONS]].
6. **O portão final roda na máquina do dono** — sandbox é indicativo.

## Criar uma skill nova
Copie o formato: frontmatter com `name` (minúsculas, com hífen) e `description` (quando disparar **e** quando não disparar), depois papel, contexto que recebe, regras numeradas, portão em checklist, saída e armadilhas pagas. Se a skill decide algo estrutural, dê a ela um **STEP 0** com portão de existência — é o que impede a IA de construir o que não deveria existir.
