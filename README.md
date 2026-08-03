---
tags: [readme, guia]
status: atual
---
# Pipeline de projetos de aplicação com IA

Kit reutilizável para tirar uma **aplicação** do zero com agentes de IA e **sustentá-la até a entrega**, mantendo rigor (portões objetivos, decisões rastreáveis, revisão adversarial) e gastando pouco contexto (orçamento numérico, leitura sob demanda, evolução por delta).

Mapa do vault: [[INICIO]]. Caminho executável: [[ROTEIRO]]. **Este README é o único lugar com "por quês" e com os limites** — os arquivos que os agentes carregam são só instrução.

## Onde este kit para (leia antes de adotar)
Nenhuma ferramenta serve para tudo, e o kit fica mais útil quando você sabe onde ele deixa de servir.

| Contexto | Serve? | O que trava |
|---|---|---|
| App pequeno/médio, **um dono** | **Sim, é o alvo** | nada; use o modo curto se for pequeno |
| Time de 2–4 pessoas | Parcialmente | `WIP` é declarado no cabeçalho do [[BACKLOG]] (`Em andamento (máx N)`) e o script cobra esse número — suba-o. Mas não há atribuição por pessoa nem merge de decisões concorrentes |
| App grande (30+ módulos) | **Não** | o [[CONTEXT]] de 4.000 chars não representa 30 módulos em "Pronto:". Solução parcial: `contexto/modulos.md` com a lista e o CONTEXT guardando só a contagem |
| Projeto longo (100+ decisões) | Com atrito | o teto de 12.000 chars do [[DECISIONS]] dá ~66 linhas; o arquivamento em `dev/decisions-arquivo.md` é **manual** e ninguém lembra |
| Multi-repo / monorepo grande | Não | o kit assume um repositório e um `CONTEXT` |
| CI/CD, revisão por pares | Não cobre | o único automatismo é o pre-commit de `scripts/checar.py` |

**A limitação honesta mais importante:** o kit tem **188** itens de checklist (69 no [[CHECKLIST]] + 104 nos `skills/`); `scripts/checar.py` julga **16** deles — cerca de 9%. O resto depende de você rodar a seção certa do [[CHECKLIST]]. Isto é um kit de disciplina com algumas travas automáticas — não um sistema que impede erro.

**A segunda:** a varredura de segredo é uma rede de arrasto, não uma garantia. Ela cobre 11 famílias de padrão e foi medida contra 8 formatos reais de vazamento (8/8, 0 falsos-positivos em 12 iscas) — mas um segredo em formato que ela não conhece passa. Ver [[docs/AUDITORIA-EXTERNA-2026-07-30|a auditoria]], que mediu a versão anterior detectando **0 de 8**.

## Como começar
1. **Projeto novo:** `python scripts/novo-projeto.py ../meu-app --nome "Meu App"` — copia o kit limpo (sem `docs/`, `exemplos/`, `.git`) e nomeia os templates.
2. `python scripts/instalar-hook.py` — todo commit passa a rodar `scripts/checar.py`. Sem isso, os portões automáticos viram opcionais.
3. Instale as skills de [[skills/LEIA-ME|skills/]] na sua ferramenta de IA (ou deixe os `SKILL.md` à mão para colar).
4. Siga o [[ROTEIRO]]. Ele começa com [[skills/bootstrap-contexto/SKILL|bootstrap-contexto]], que entrevista você (≤5 perguntas) e devolve o [[CONTEXT]] preenchido.
5. Escolha o perfil da stack em [[perfis/perfil-generico|perfis/]] e cole os blocos no [[CONTEXT]].

## O que vem na caixa
```
INICIO.md ROTEIRO.md GUIA-OBSIDIAN.md README.md
CLAUDE.md       ← contrato de leitura do agente (carregado sozinho pela ferramenta)
CONTEXT.md      ← contexto-fonte do projeto, ≤4.000 chars
PLANO.md        ← módulos, contratos, milestones com portão (congela após aprovação)
DECISIONS.md    ← D-NN (2 frases + link) · Q-NN (dono) · QA-NN · regra de arquivamento
BACKLOG.md      ← fonte única de tarefas, com lane "Ações do dono" e WIP declarado
CHANGELOG.md    ← histórico datado do PROJETO (fora do contexto)
CHECKLIST.md    ← portões por tipo de entrega, camada por camada
APRENDIZADOS.md ← lições vivas, já com as herdadas
skills/         ← os 17 agentes (SKILL.md instalável) — inclusive os de fase
perfis/         ← web-nextjs · dados-python · genérico (método p/ qualquer stack)
templates/      ← modelos de D-NN, QA-NN e fecho de sessão (plugin Templates)
contexto/       ← docs de domínio por tema (nasce vazio, leitura sob demanda)
dev/            ← evidências e relatórios de QA — nunca carregados
exemplos/       ← caso de referência          ┐ só do kit:
docs/           ← análise de uso + changelog  ┘ não vão para o projeto
scripts/        ← checar.py · instalar-hook.py · novo-projeto.py
```
Projeto que roda continuamente ganha ainda um `RUNBOOK.md` na entrega (exigido pela Fase 6).

**Um mecanismo só.** Não existe `prompts/` separado de `skills/`: os papéis de fase viraram skills. Antes você carregava o prompt *e* a skill na mesma sessão e pagava duas vezes pela mesma instrução (27% de sobreposição medida entre o prompt de QA e a skill de guardrails).

## As 7 regras (valem em todas as fases)
1. **Contexto com orçamento em número.** [[CONTEXT]] ≤ 4.000 caracteres, medível por script, atualizado por substituição. *Por quê: "≤ 1 página" sem número virou, num projeto real, um parágrafo-parede de ~640 tokens relido em toda sessão.*
2. **Histórico fora do contexto.** Datado → [[CHANGELOG]], que nenhuma sessão carrega.
3. **Delta, nunca regenerar.** Só o trecho alterado — em docs e em código. Regenerar foi o maior custo dos projetos anteriores.
4. **Decisão rastreável.** Assunto fechado → D-NN (2 frases; evidência longa em `dev/`). Bug → QA-NN no commit. Pendência do dono → Q-NN. O script cobra: ID citado tem de existir, ID não se repete.
5. **Nada entra sem portão.** Critério de aceite objetivo no dia 1; "parece bom" não passa. Rejeição registrada vale tanto quanto adoção.
6. **Estado mora num lugar só.** Versões/métricas/contagens vigentes só no [[CONTEXT]]; todo outro doc aponta. O script compara "Em andamento" entre [[BACKLOG]] e [[CONTEXT]] e reprova divergência. *Por quê: num projeto real o estado vivia em 4 arquivos e divergiu.*
7. **Observe antes de construir.** Parser/integração só com amostra real da estrutura na mão. *Por quê: chutar a estrutura de uma fonte custou 6 ciclos de QA.*

As fases, os portões e qual skill usar em cada uma estão no [[ROTEIRO]] — não se repetem aqui.

## O ciclo de toda sessão (90% do dia a dia)
> **uma** skill + [[CONTEXT]] + só o arquivo do momento → pedir **delta** → passar no **portão** → registrar D-NN/QA-NN → [[CONTEXT]] por substituição, datado no [[CHANGELOG]] → commit citando IDs.

No Obsidian o fecho é um clique: `Templates → fecho-de-sessao` ([[templates/LEIA-ME|templates/]]).

## O papel do dono (o que a IA não faz por você)
1. **Guardião do portão** — aceite = rodar a seção certa do [[CHECKLIST]]; falhou → devolve pedindo delta, nunca "refaz tudo".
2. **Decisor** — toda Q-NN é sua; agente não muda regra de negócio nem rumo.
3. **Operador da máquina real** — testes oficiais, migrations, deploy, push. O sandbox do agente é indicativo, não portão.
4. **Fonte dos dados manuais** — o que você não preencher fica lacuna declarada, nunca inventada.

**Frases de segurança:** "Isso passou no portão? Mostra o número." · "Cadê o D-NN?" · "Me manda só o delta." · "Rodou na minha máquina ou no sandbox?" · "Viu uma amostra real antes de escrever esse parser?" · "Isso muda alguma decisão ou número?"

## Sobre as evidências deste kit
Duas fontes, com pesos diferentes — e vale saber qual é qual:

- **[[docs/ANALISE-USO-SCB|docs/ANALISE-USO-SCB]]** é medição: tamanhos de arquivo contados, custos em tokens calculados, com as ressalvas contra o próprio projeto explicitadas. É daí que vêm as regras 1, 4, 6 e 7.
- **[[exemplos/caso-spo|exemplos/caso-spo]]** é **narrativa não verificada**: os números ("14 passagens", "84 achados") vêm de relato, sem relatório nem commit anexado. Use como lista de armadilhas plausíveis, não como aferição.

O kit inteiro foi auditado contra si mesmo em 2026-07-30; o que a auditoria reprovou virou correção em [[docs/CHANGELOG-KIT|docs/CHANGELOG-KIT]] (v4).

## Como o kit evolui
Fim de milestone → [[skills/retrospectiva/SKILL|retrospectiva]] → lições no [[APRENDIZADOS]] do projeto → lição repetida em 2+ projetos vira regra aqui, com entrada em [[docs/CHANGELOG-KIT|docs/CHANGELOG-KIT]]. Perfil novo nasce salvando um `perfil-generico` preenchido; skill nova nasce copiando o formato de [[skills/LEIA-ME|skills/]]. O kit é um repositório git: versione as mudanças.
