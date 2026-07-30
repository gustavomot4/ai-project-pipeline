---
tags: [readme, guia]
status: atual
---
# Pipeline de projetos de aplicação com IA

Kit genérico e reutilizável para tirar uma **aplicação** do zero com agentes de IA e **sustentá-la do início ao fim** — qualquer stack, qualquer domínio — mantendo **rigor** (portões objetivos, decisões rastreáveis, revisão adversarial) e gastando o **mínimo de tokens** (contexto com orçamento numérico, leitura sob demanda, evolução por delta).

Comece por [[INICIO]] (mapa) e siga o [[ROTEIRO]] (o caminho executável). Este README é o único lugar com "por quês" — os arquivos que os agentes carregam são só instrução. As evidências medidas que originaram cada regra estão em [[docs/ANALISE-USO-SCB|docs/ANALISE-USO-SCB]]; a história do kit, em [[docs/CHANGELOG-KIT|docs/CHANGELOG-KIT]].

## O que este kit tem que um pipeline genérico não tem
1. **12 agentes como skills instaláveis** ([[skills/LEIA-ME|skills/]]): domínio, BFF, integração síncrona, UI/UX, MFE, autenticação, monólito, microserviços, IaC, testes, guardrails e dados/análise. Cada um com regras numeradas, portão em checklist e as **armadilhas já pagas** por projetos reais.
2. **Portões de existência** nas skills estruturais: MFE e microserviços começam perguntando *isto deve existir?* — e reprovar é o resultado esperado na maioria dos casos. É o que impede a IA de construir arquitetura que ninguém precisa.
3. **Um [[ROTEIRO]] em ordem**, ligando fase → agente → portão, para que o resultado não dependa de você lembrar a sequência.
4. **Um caso de referência destilado** ([[exemplos/caso-spo]]) com números reais de entrega, para aferir o que "pronto" significa.
5. **Higiene automatizada**: `scripts/checar.py` reprova o que as regras proíbem (contexto estourado, estado duplicado, link quebrado, skill inválida) em vez de confiar na sua memória.

## Como começar
1. **Projeto novo:** `python scripts/novo-projeto.py ../meu-app` — copia o kit já limpo (sem `docs/`, `exemplos/`, `.git`) e com os templates zerados. Ou abra esta pasta como vault do Obsidian e trabalhe aqui ([[GUIA-OBSIDIAN]]).
2. Instale as skills de [[skills/LEIA-ME|skills/]] na sua ferramenta de IA.
3. Siga o [[ROTEIRO]]. Ele começa com uma sessão de [[prompts/00-bootstrap-contexto]] que entrevista você (≤5 perguntas) e devolve o [[CONTEXT]] preenchido.
4. Escolha o perfil da stack em `perfis/` (não tem o seu? use `perfil-generico`, que extrai as restrições por método) e cole os blocos no [[CONTEXT]].
5. Daí em diante, só o ciclo de sessão. O kit segura o resto: decisões, QA, evolução, entrega, operação.

## O que vem na caixa
```
INICIO.md ROTEIRO.md GUIA-OBSIDIAN.md README.md
CONTEXT.md      ← contexto-fonte, ≤4.000 chars, com Mapa de leitura e Protocolo do agente
PLANO.md        ← módulos, contratos, milestones com portão (congela após aprovação)
DECISIONS.md    ← D-NN (2 frases + link) · Q-NN (dono) · QA-NN · regra de arquivamento
BACKLOG.md      ← fonte única de tarefas, com lane "Ações do dono"
CHANGELOG.md    ← histórico datado do PROJETO (fora do contexto)
CHECKLIST.md    ← portões por tipo de entrega, camada por camada
APRENDIZADOS.md ← lições vivas, já com as herdadas
skills/         ← os 12 agentes (SKILL.md instalável)
prompts/00–06   ← papéis por fase (curtos, imperativos)
perfis/         ← web-nextjs · dados-python · genérico (método p/ qualquer stack)
templates/      ← modelos de D-NN, QA-NN e fecho de sessão (plugin Templates)
contexto/       ← docs de domínio por tema (nasce vazio, leitura sob demanda)
dev/            ← evidências e relatórios de QA — nunca carregados
exemplos/       ← caso de referência destilado          ┐ só do kit:
docs/           ← análise de uso + changelog do kit     ┘ não vão para o projeto
scripts/        ← checar.py (higiene) · novo-projeto.py (bootstrap)
```
Projeto que roda continuamente ganha ainda um `RUNBOOK.md` na entrega (exigido pela Fase 6).

## As 7 regras (valem em todas as fases)
1. **Contexto com orçamento em número.** [[CONTEXT]] ≤ 4.000 caracteres, medível por script, atualizado por substituição. *Por quê: "≤ 1 página" sem número virou, num projeto real, um parágrafo-parede de ~640 tokens relido em toda sessão.*
2. **Histórico fora do contexto.** Datado → [[CHANGELOG]], que nenhuma sessão carrega.
3. **Delta, nunca regenerar.** Só o trecho alterado — em docs e em código. Regenerar foi o maior custo dos projetos anteriores.
4. **Decisão rastreável.** Assunto fechado → D-NN (2 frases; evidência longa em `dev/`). Bug → QA-NN no commit. Decisão pendente do dono → Q-NN. *Por quê do teto: sem ele, o DECISIONS de um projeto real chegou a ~7.700 tokens e a fase de evolução, que o carrega inteiro, pagava tudo.*
5. **Nada entra sem portão.** Critério de aceite objetivo no dia 1; "parece bom" não passa. Rejeição registrada vale tanto quanto adoção.
6. **Estado mora num lugar só.** Versões/métricas/contagens vigentes só no [[CONTEXT]]; todo outro doc aponta. *Por quê: num projeto real o estado vivia em 4 arquivos e divergiu — um card do backlog pedia rebuild com números de duas versões atrás.*
7. **Observe antes de construir.** Parser/integração só com amostra real da estrutura na mão. *Por quê: chutar a estrutura de uma fonte custou 6 ciclos de QA.*

## As fases e seus portões
| Fase | Prompt | Skill típica | Portão |
|---|---|---|---|
| 0 Contexto | `00` | — | CONTEXT ≤ 4k chars + você concorda com cada linha |
| 1 Forma e plano | `01` | arquitetura-* | forma em D-NN com gatilho · plano aprovado = congelado |
| 2 Dados/domínio | `02` | backend-dominio · dados-analise | migration roda em banco vazio · invariantes testados |
| 3 Borda/UI/acesso | `02` | bff · uiux · autenticacao · sync | portão da skill + rota sensível testada sem sessão |
| 4 Testes e revisão | `03` | testes → guardrails-review | suíte verde na sua máquina · relatório de QA registrado · crítico/alto zerados |
| 5 Infra | `02` | iac-docker-terraform | sobe limpo · dados persistem · rollback testado |
| 6 Entrega | `05` | — | zip conferido · sem estado duplicado · runbook se opera |
| Retro | `06` | — | APRENDIZADOS atualizado |

**Modo curto (projeto pequeno):** 0 → 2 → 4 → 6. Pula-se fase; não se pula regra.

## O ciclo de toda sessão (90% do dia a dia)
> skill do papel + [[CONTEXT]] + só o arquivo do momento → pedir **delta** → passar no **portão** → registrar D-NN/QA-NN → [[CONTEXT]] por substituição, datado no [[CHANGELOG]] → commit citando IDs.

No Obsidian o fecho é um clique: `Templates → fecho-de-sessao` ([[templates/LEIA-ME|templates/]]).

## O papel do dono (o que a IA não faz por você)
1. **Guardião do portão** — aceite = rodar a seção certa do [[CHECKLIST]]; falhou → devolve pedindo delta.
2. **Decisor** — toda Q-NN é sua; agente não muda regra de negócio nem rumo.
3. **Operador da máquina real** — testes oficiais, migrations, deploy, push. O sandbox do agente é indicativo, não portão.
4. **Fonte dos dados manuais** — o que você não preencher fica lacuna declarada, nunca inventada.
5. **Higiene** — `python scripts/checar.py` de vez em quando; conferir que o estado está num lugar só.

**Frases de segurança:** "Isso passou no portão? Mostra o número." · "Cadê o D-NN?" · "Me manda só o delta." · "Rodou na minha máquina ou no sandbox?" · "Viu uma amostra real antes de escrever esse parser?" · "Isso muda alguma decisão ou número?"

## Como o kit evolui
Fim de milestone → [[prompts/06-retrospectiva]] → lições no [[APRENDIZADOS]] do projeto → lição repetida em 2+ projetos vira regra aqui, com entrada em [[docs/CHANGELOG-KIT|docs/CHANGELOG-KIT]]. Perfil novo nasce salvando um `perfil-generico` preenchido; skill nova nasce copiando o formato de [[skills/LEIA-ME|skills/]]. O kit é um repositório git: versione as mudanças.
