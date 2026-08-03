---
tags: [plano, template]
status: rascunho
---
# PLANO.md — <NOME DO PROJETO>

> Gerado na Fase 1 com [[b_process/skills/planner/SKILL|planejador]] a partir do [[a_context_source|CONTEXT]]. Aprovado = **congelado** (registre como D-NN em [[c_decisions|DECISIONS]]). Mudança posterior é D-NN novo — nunca replanejar do zero.
> Critério de qualidade: outro agente implementa um módulo lendo **só o contrato dele + [[a_context_source|CONTEXT]]**.
> Estado (o que já está pronto) NÃO mora aqui — mora no [[a_context_source|CONTEXT]].

## Forma da arquitetura
<Monólito modular | monólito + serviço extraído | microserviços. Registre o porquê e o portão que essa escolha tem de passar. Comece pelo monólito modular a menos que exista um motivo medido para não começar — ver [[b_process/skills/architecture-microservices/SKILL|arquitetura-microservicos]].>

## Ordem de build
Dados/schema → domínio/núcleo → borda (API/BFF) → UI → infra/deploy. Justifique qualquer desvio.

## Módulos e contratos
> Repita o bloco por módulo. **≤ 1 página por módulo.** Suposição é **[a confirmar]**, não fato.

### M1 — <nome>
- **Recebe:** <entrada: dados, contrato, evento>
- **Entrega:** <saída observável>
- **Skill responsável:** <ex.: [[b_process/skills/backend-bff/SKILL|backend-bff]]>
- **Portão:** <checagem objetiva que aprova ou reprova>
- **Onde a stack vai doer:** <limite conhecido antes de começar>

### M2 — <nome>
- **Recebe:** …
- **Entrega:** …
- **Skill responsável:** …
- **Portão:** …
- **Onde a stack vai doer:** …

## Milestones com portão (cada uma só abre com o portão da anterior)
| Milestone | Abre quando | Portão de saída |
|---|---|---|
| M-1 <fundação> | <condição> | <checagem objetiva> |
| M-2 <núcleo> | M-1 fechada | <checagem objetiva> |
| M-3 <entrega> | M-2 fechada | <o usuário final consegue fazer X sem assistência> |

## As 3 perguntas que mais mudariam este plano
1. <pergunta>
2. <pergunta>
3. <pergunta>
