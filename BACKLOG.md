---
tags: [backlog, template]
status: rascunho
---
# BACKLOG.md — quadro de tarefas (fonte única)

> **Só existe UM backlog: este.** Não crie outro em subpastas — dois quadros divergem, sempre (`scripts/checar.py` acusa).
> Estado numérico (versão, métricas, contagens) NÃO mora aqui — mora no [[CONTEXT]]. Aqui, só tarefas.
> Todo card com portão: como se sabe que terminou. Sem portão, a tarefa não entra em "Em andamento".

## Ações do dono (máquina real)
- [ ] A-01 — <ex.: rodar os testes oficiais / criar o repositório / configurar credencial / aprovar o plano>

## A fazer
- [ ] T-01 — <tarefa> · **Portão:** <checagem objetiva> · **Skill:** <ex.: [[skills/testes/SKILL|testes]]>

## Em andamento (máx 1 — espelha "Em andamento" do [[CONTEXT]])
<!-- O número em "máx N" é o limite que scripts/checar.py cobra. Solo = 1.
     Time de N pessoas: troque para "máx N" aqui; o script passa a aceitar N. -->
- [ ] T-00 — <a tarefa do momento>

## Feito (mover para cá; detalhe no [[CHANGELOG]])
- [x] T-… — <tarefa>

## Ideias (não comprometidas)
- <solta; só vira T-NN quando promovida com portão escrito>
