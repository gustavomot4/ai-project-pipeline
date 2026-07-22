# Pipeline para projetos com IA — kit pessoal do Gustavo (v2)

Kit reutilizável para começar e tocar projetos com agentes de IA mantendo **rigor** (portões objetivos, decisões rastreáveis, QA adversarial) e gastando o **mínimo de tokens** (contexto com orçamento numérico, leitura sob demanda, evolução por delta).

**v2 (2026-07-22):** refatorado com as evidências do primeiro projeto real que usou o kit (SCB). O que funcionou, o que falhou e por que cada mudança existe: **`docs/ANALISE-USO-SCB.md`**. Este README é o único lugar com "por quês" — os arquivos que os agentes carregam são só instrução.

## Como usar num projeto novo
Copie tudo **exceto `docs/` e `.git`** para a pasta do projeto. Preencha o `CONTEXT.md` (Fase 0), cole o perfil de `perfis/` e siga as fases. A qualquer momento: `python scripts/checar.py` valida a higiene (orçamento, fonte única, cruft).

## O que vem na caixa
```
├── README.md          ← este guia (humano; nenhuma sessão carrega)
├── CONTEXT.md         ← contexto-fonte, ≤4.000 chars, com Mapa de leitura e Protocolo do agente
├── DECISIONS.md       ← D-NN (2 frases + link) · Q-NN (dono) · QA-NN
├── BACKLOG.md         ← fonte única de tarefas, com lane "Ações do dono"
├── CHANGELOG.md       ← histórico datado (fora do contexto)
├── CHECKLIST.md       ← portões por tipo de entrega
├── APRENDIZADOS.md    ← lições vivas, alimentadas pela retrospectiva
├── prompts/00–06      ← papéis por fase (curtos, imperativos)
├── perfis/            ← dados-python · web-nextjs (restrições prontas p/ colar)
├── contexto/          ← docs de domínio por tema (leitura sob demanda)
├── dev/               ← notas de evidência (gates, relatórios de QA) — nunca carregadas
└── scripts/checar.py  ← valida orçamento do CONTEXT, fonte única, WIP=1, cruft
```

## As 7 regras (valem em todas as fases)
1. **Contexto com orçamento em número.** `CONTEXT.md` ≤ 4.000 caracteres, medível por script, atualizado por substituição. *Por quê: "≤ 1 página" sem número virou, no SCB, um parágrafo-parede de ~640 tokens relido em toda sessão.*
2. **Histórico fora do contexto.** Datado → `CHANGELOG.md`, que nenhuma sessão carrega.
3. **Delta, nunca regenerar.** Só o trecho alterado — em docs e em código. Regenerar foi o maior custo dos projetos SCM/SPO.
4. **Decisão rastreável.** Assunto fechado → D-NN (2 frases; evidência longa em `dev/`). Bug → QA-NN no commit. Decisão pendente do dono → Q-NN. *Por quê do teto: sem ele, o DECISIONS do SCB chegou a ~7.700 tokens e a Fase 5 pagava tudo.*
5. **Nada entra sem portão.** Critério de aceite objetivo no dia 1; "parece bom" não passa. Rejeição registrada vale tanto quanto adoção.
6. **Estado mora num lugar só.** Versões/métricas/contagens vigentes só no `CONTEXT.md`; todo outro doc aponta. *Por quê: no SCB o estado vivia em 4 arquivos e divergiu (backlog pedindo rebuild com números de duas versões atrás).*
7. **Observe antes de construir.** Parser/integração só com amostra real da estrutura na mão. *Por quê: chutar a estrutura de uma fonte custou 6 ciclos de QA no SCB (QA-05..QA-10).*

## As fases e seus portões
| Fase | Prompt | Contexto do agente | Portão |
|---|---|---|---|
| 0 Bootstrap | `00` | descrição crua (ou CONTEXT atual) | CONTEXT ≤ 4k chars + aceite escrito |
| 1 Plano | `01` | CONTEXT | plano aprovado = congelado (D-NN) |
| 2 Dados/schema | `02` | CONTEXT + trecho de dados do plano | schema valida na stack real |
| 3 Implementação | `02` | CONTEXT + contrato do módulo | teste do módulo verde no portão |
| 4 QA adversarial | `03` | CONTEXT + código | **relatório registrado** + crítico/alto corrigidos |
| 5 Evolução | `04` | CONTEXT + DECISIONS | só adota o que passa o portão; rejeição vira D-NN |
| 6 Entrega | `05` | pasta + CHECKLIST | zip conferido; docs sem estado duplicado |
| Retro (fecha milestone) | `06` | trabalho recém-feito | APRENDIZADOS.md atualizado |

## O ciclo de toda sessão (90% do dia a dia)
> prompt do papel + `CONTEXT.md` + só o arquivo do momento → pedir **delta** → passar no **portão** → registrar D-NN/QA-NN → `CONTEXT.md` por substituição, datado no `CHANGELOG.md` → commit citando IDs.

## O papel do dono (o que a IA não faz por você)
1. **Guardião do portão** — aceite = rodar a seção certa do `CHECKLIST.md`; falhou → devolve pedindo delta.
2. **Decisor** — toda Q-NN é sua; agente não muda regra de negócio nem rumo.
3. **Operador da máquina real** — testes oficiais, downloads com chave, push, deploy. O sandbox do agente é indicativo, não portão.
4. **Fonte dos dados manuais** — o que você não preencher fica lacuna declarada, nunca inventada.
5. **Higiene** — `python scripts/checar.py` de vez em quando; conferir que o estado está num lugar só.

**Frases de segurança:** "Isso passou no portão? Mostra o número." · "Cadê o D-NN?" · "Me manda só o delta." · "Rodou na minha máquina ou no sandbox?" · "Viu uma amostra real antes de escrever esse parser?" · "Isso muda alguma decisão ou número?"

## Como o kit evolui
Fim de milestone → prompt `06` → lições no `APRENDIZADOS.md` do projeto → lição repetida em 2+ projetos vira regra aqui (com entrada no `CHANGELOG.md` do kit). O kit é um repositório git: versione as mudanças.
