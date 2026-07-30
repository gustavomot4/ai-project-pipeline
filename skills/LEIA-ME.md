---
tags: [skills, indice]
status: atual
---
# skills/ — os agentes do pipeline

Cada pasta aqui é uma **skill instalável** (`SKILL.md` com `name` e `description` no frontmatter), no padrão do Claude Code / Cowork. Duas formas de usar:

- **Instalada:** copie a pasta `skills/<nome>/` para o diretório de skills da sua ferramenta e invoque por nome (ex.: `/backend-dominio`). A `description` faz a skill disparar sozinha quando a tarefa combina.
- **Colada:** abra o `SKILL.md` e cole o conteúdo na sessão. Funciona em qualquer ferramenta de IA.

Em qualquer um dos casos, a sessão recebe **a skill + o [[CONTEXT]] + só o arquivo do momento**. Nunca o repositório inteiro.

## Os 12 agentes

### Arquitetura (decidem a forma antes de existir código)
| Skill | Quando usar | O que ela protege |
|---|---|---|
| [[skills/arquitetura-monolito/SKILL\|arquitetura-monolito]] | estruturar o projeto; é o **default** | fronteiras internas reais, sem custo distribuído |
| [[skills/arquitetura-microservicos/SKILL\|arquitetura-microservicos]] | avaliar/fatiar em serviços | tem portão de existência: reprova sem time e observabilidade |

### Backend
| Skill | Quando usar | O que ela protege |
|---|---|---|
| [[skills/backend-dominio/SKILL\|backend-dominio]] | regra de negócio, schema, migration, API | invariantes, dinheiro inteiro, transação, migration aditiva |
| [[skills/backend-bff/SKILL\|backend-bff]] | camada de borda para uma tela específica | timeout, falha parcial explícita, segredo fora do cliente |
| [[skills/microservice-sync/SKILL\|microservice-sync]] | serviço chamando serviço | timeout, retry seguro, idempotência, circuit breaker |

### Frontend
| Skill | Quando usar | O que ela protege |
|---|---|---|
| [[skills/frontend-uiux/SKILL\|frontend-uiux]] | telas, componentes, formulários | 4 estados, mobile-first, erro em linguagem de gente |
| [[skills/frontend-mfe/SKILL\|frontend-mfe]] | dividir o front em remotes | portão de existência: reprova com 1 time só |

### Transversais
| Skill | Quando usar | O que ela protege |
|---|---|---|
| [[skills/autenticacao/SKILL\|autenticacao]] | login, sessão, PIN, rota protegida | segredo por instalação, autorização no servidor, nega por padrão |
| [[skills/iac-docker-terraform/SKILL\|iac-docker-terraform]] | Docker, compose, Terraform, deploy | artefato pronto (sem build no cliente), rollback testado, `plan` como portão |
| [[skills/testes/SKILL\|testes]] | teste unitário e de sistema | bordas, invariantes, regressão por QA-NN, determinismo |
| [[skills/guardrails-review/SKILL\|guardrails-review]] | revisar antes de entregar | 12 frentes de ataque, achado com reprodução, relatório registrado |

### Dados e análise
| Skill | Quando usar | O que ela protege |
|---|---|---|
| [[skills/dados-analise/SKILL\|dados-analise]] | coleta, parser/ETL, feature, modelo, métrica, qualquer afirmação numérica | amostra real antes do parser, ausente ≠ zero, número com incerteza, zero vazamento treino/teste, rebuild ao mudar fórmula |

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

`autenticacao` entra assim que existir área sensível. `microservice-sync` só se houver mais de um serviço. `frontend-mfe` só se o portão de existência aprovar. `dados-analise` entra **antes** de `backend-dominio` quando o projeto nasce de uma fonte de dados externa — é ela que traz a amostra real sem a qual o schema é chute.

## Regras que valem para todas
1. **Uma skill por sessão.** Duas skills na mesma sessão = duas responsabilidades disputando o contexto.
2. **Delta, nunca regeneração.**
3. **Portão objetivo antes de "pronto".** Cada skill traz o seu; o [[CHECKLIST]] é o portão da entrega.
4. **Escopo é o módulo da sessão.** Precisa mexer em outro? Pare e avise.
5. **Registre:** decisão → D-NN · bug → QA-NN · pendência do dono → Q-NN, em [[DECISIONS]].
6. **O portão final roda na máquina do dono** — sandbox é indicativo.

## Criar uma skill nova
Copie o formato: frontmatter com `name` (minúsculas, com hífen) e `description` (quando disparar **e** quando não disparar), depois papel, contexto que recebe, regras numeradas, portão em checklist, saída e armadilhas pagas. Se a skill decide algo estrutural, dê a ela um **STEP 0** com portão de existência — é o que impede a IA de construir o que não deveria existir.
