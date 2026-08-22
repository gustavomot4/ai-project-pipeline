---
tags: [readme, guia]
status: atual
---
# Pipeline de projetos de aplicação com IA

Kit reutilizável para tirar uma **aplicação** do zero com agentes de IA e **sustentá-la até a entrega**, mantendo rigor (portões objetivos, decisões rastreáveis, revisão adversarial) e gastando pouco contexto (orçamento numérico, leitura sob demanda, evolução por delta).

Mapa do vault: [[INDEX]]. Caminho executável: [[a_roadmap|ROTEIRO]]. **Este README é o único lugar com "por quês" e com os limites** — os arquivos que os agentes carregam são só instrução.

## Onde este kit para (leia antes de adotar)
Nenhuma ferramenta serve para tudo, e o kit fica mais útil quando você sabe onde ele deixa de servir.

| Contexto | Serve? | O que trava |
|---|---|---|
| App pequeno/médio, **um dono** | **Sim, é o alvo** | nada; use o modo curto se for pequeno |
| **Projeto que já existe** | Sim, desde a v5 | comece por [[b_process/skills/existing-project-adoption/SKILL\|adocao-projeto-existente]], que produz CONTEXT/PLANO do código real. Quanto maior o sistema, mais o teto de 4.000 chars aperta |
| **Sustentar o que já roda** | Sim, desde a v5 | [[b_process/skills/debugging-diagnosis/SKILL\|depuração]] · [[b_process/skills/performance/SKILL\|performance]] · [[b_process/skills/observability/SKILL\|observabilidade]] · [[b_process/skills/dependencies-supply-chain/SKILL\|dependências]] |
| Time de 2–4 pessoas | Parcialmente | `WIP` é declarado no cabeçalho do [[c_backlog|BACKLOG]] (`Em andamento (máx N)`) e o script cobra esse número — suba-o. Mas não há atribuição por pessoa nem merge de decisões concorrentes |
| App grande (30+ módulos) | **Não** | o [[a_context_source|CONTEXT]] de 4.000 chars não representa 30 módulos em "Pronto:". Solução parcial: `a_context/modules.md` com a lista e o CONTEXT guardando só a contagem |
| Projeto longo (100+ decisões) | Com atrito | o teto de 12.000 chars do [[c_decisions|DECISIONS]] dá ~66 linhas; o arquivamento em `e_qa/decisions_archive.md` é **manual** e ninguém lembra |
| Multi-repo / monorepo grande | Não | o kit assume um repositório e um `CONTEXT` |
| CI/CD, revisão por pares | Não cobre | o único automatismo é o pre-commit de `scripts/check.py` |

**A limitação honesta mais importante:** o kit tem **284** itens de checklist (118 no [[b_checklist|CHECKLIST]] + 166 nos `b_process/skills/`); `scripts/check.py` julga **33** deles (15 reprovam o commit, 18 avisam) — cerca de 12%. Estes números são **cobrados por `scripts/test_check.py`**: a frase mais honesta do kit não pode ser a que envelhece em silêncio (ela já tinha envelhecido uma vez, dizendo 188/18). O resto depende de você rodar a seção certa do [[b_checklist|CHECKLIST]]. Isto é um kit de disciplina com algumas travas automáticas — não um sistema que impede erro.

**A primeira evidência de que funciona, com o custo junto:** [[c_field_evaluation_tapgo_260813|avaliação de campo]] — um projeto real de 46 commits medido por sessão isolada, com o critério de sucesso hasheado ANTES dos dados. Nove hipóteses de nove no lado positivo (98% de commits com ID, ~0% de regeneração, 3 de 3 sabotagens do portão reprovadas) e o imposto declarado: **15% das sessões** foram administrar o orçamento do próprio kit, e a medição achou uma checagem que enxergava 12% do que dizia enxergar. É **n = 1**: ataca a falta de evidência, não a resolve.

**A segunda:** a varredura de segredo é uma rede de arrasto, não uma garantia. Ela cobre 11 famílias de padrão e foi medida contra 8 formatos reais de vazamento (8/8, 0 falsos-positivos em 12 iscas) — mas um segredo em formato que ela não conhece passa. Ver [[b_external_audit_report_260730_0900|a auditoria]], que mediu a versão anterior detectando **0 de 8**.

## Como começar
1. **Projeto novo:** `python scripts/new_project.py ../meu-app --name "Meu App" --code src` — monta o esqueleto inteiro do padrão: pasta de docs, pasta de código, README, `.gitignore`, `.gitattributes`.
2. `cd ../meu-app && git init && python 77777777_*_Project_DOCs/scripts/install_hook.py` — todo commit passa a rodar o `check.py`. Sem isso, os portões automáticos viram opcionais.
3. Instale as skills de [[b_process/skills/README|skills/]] na sua ferramenta de IA (ou deixe os `SKILL.md` à mão para colar).
4. Siga o [[a_roadmap|ROTEIRO]]. Ele começa com [[b_process/skills/context-bootstrap/SKILL|context-bootstrap]], que entrevista você (≤5 perguntas) e devolve o [[a_context_source|CONTEXT]] preenchido.
5. Escolha o perfil da stack em [[a_generic|profiles/]] e cole os blocos no [[a_context_source|CONTEXT]].

## O que vem na caixa
O kit **é** a pasta de documentação do padrão da equipe: `new_project.py` o instala num projeto
como `77777777_<TAG>_Project_DOCs/` e monta o resto do esqueleto em volta. Regras de nome,
estrutura e commit: [[e_repository_standard|padrão do repositório]].

```
INDEX.md          ← nota-casa: mapa de navegação
README.md         ← este arquivo: os porquês e os limites
CLAUDE.md         ← contrato de leitura do agente (a ferramenta carrega sozinha)

a_context/        A VERDADE
  a_context_source.md   contexto-fonte, ≤4.000 chars — o único que TODA sessão carrega
  b_plan.md             módulos, contratos, milestones (congela após aprovação)
  c_decisions.md        D-NN (2 frases + link) · Q-NN (dono) · QA-NN · arquivamento
  <tema>.md             domínio por tema (nasce vazio, leitura sob demanda)

b_process/        COMO SE TRABALHA
  a_roadmap.md              o caminho do dia 1 à entrega, fase por fase
  b_checklist.md            portões por tipo de entrega, camada por camada
  c_backlog.md              fonte única de tarefas, com WIP declarado
  d_agent_learnings.md      lições vivas, já com as herdadas
  e_repository_standard.md  o padrão — vai junto para todo projeto
  skills/                   os 24 agentes (SKILL.md instalável)
  profiles/                 web-nextjs · dados-python · genérico
  templates/                modelos de D-NN, QA-NN e fecho de sessão

c_technical_docs/ guia do Obsidian · caso de referência
d_history/        changelog datado (nenhuma sessão carrega)
e_qa/             relatórios de QA do PROJETO, com timestamp no nome
docs/             auditoria do próprio KIT — não vai para projetos novos
LICENSE           MIT
.github/workflows portão rodando em Linux e Windows a cada push
scripts/
  task.py         ponto de entrada único: check · check-all · test · hook
  check.py        o portão de higiene (15 falhas · 18 avisos)
  test_check.py   testes de regressão dos scripts — só stdlib
  install_hook.py instala o pre-commit
  new_project.py  cria projeto novo · `--upgrade` atualiza o processo de um existente
```
Projeto que roda continuamente ganha ainda um `RUNBOOK.md` na entrega (exigido pela Fase 6).

**Um mecanismo só.** Não existe `prompts/` separado de `b_process/skills/`: os papéis de fase viraram skills. Antes você carregava o prompt *e* a skill na mesma sessão e pagava duas vezes pela mesma instrução (27% de sobreposição medida entre o prompt de QA e a skill de guardrails).

## As 7 regras (valem em todas as fases)
1. **Contexto com orçamento em número.** [[a_context_source|CONTEXT]] ≤ 4.000 caracteres, medível por script, atualizado por substituição. *Por quê: "≤ 1 página" sem número virou, num projeto real, um parágrafo-parede de ~640 tokens relido em toda sessão.*
2. **Histórico fora do contexto.** Datado → [[a_changelog|CHANGELOG]], que nenhuma sessão carrega.
3. **Delta, nunca regenerar.** Só o trecho alterado — em docs e em código. Regenerar foi o maior custo dos projetos anteriores.
4. **Decisão rastreável.** Assunto fechado → D-NN (2 frases; evidência longa em `e_qa/`). Bug → QA-NN no commit. Pendência do dono → Q-NN. O script cobra: ID citado tem de existir, ID não se repete.
5. **Nada entra sem portão.** Critério de aceite objetivo no dia 1; "parece bom" não passa. Rejeição registrada vale tanto quanto adoção.
6. **Estado mora num lugar só.** Versões/métricas/contagens vigentes só no [[a_context_source|CONTEXT]]; todo outro doc aponta. O script compara "Em andamento" entre [[c_backlog|BACKLOG]] e [[a_context_source|CONTEXT]] e reprova divergência. *Por quê: num projeto real o estado vivia em 4 arquivos e divergiu.*
7. **Observe antes de construir.** Parser/integração só com amostra real da estrutura na mão. *Por quê: chutar a estrutura de uma fonte custou 6 ciclos de QA.*

As fases, os portões e qual skill usar em cada uma estão no [[a_roadmap|ROTEIRO]] — não se repetem aqui.

## O ciclo de toda sessão (90% do dia a dia)
> **uma** skill + [[a_context_source|CONTEXT]] + só o arquivo do momento → pedir **delta** → passar no **portão** → registrar D-NN/QA-NN → [[a_context_source|CONTEXT]] por substituição, datado no [[a_changelog|CHANGELOG]] → commit citando IDs.

No Obsidian o fecho é um clique: `Templates → fecho-de-sessao` ([[b_process/templates/README|templates/]]).

## O papel do dono (o que a IA não faz por você)
1. **Guardião do portão** — aceite = rodar a seção certa do [[b_checklist|CHECKLIST]]; falhou → devolve pedindo delta, nunca "refaz tudo".
2. **Decisor** — toda Q-NN é sua; agente não muda regra de negócio nem rumo.
3. **Operador da máquina real** — testes oficiais, migrations, deploy, push. O sandbox do agente é indicativo, não portão.
4. **Fonte dos dados manuais** — o que você não preencher fica lacuna declarada, nunca inventada.

**Frases de segurança:** "Isso passou no portão? Mostra o número." · "Cadê o D-NN?" · "Me manda só o delta." · "Rodou na minha máquina ou no sandbox?" · "Viu uma amostra real antes de escrever esse parser?" · "Isso muda alguma decisão ou número?"

## Sobre as evidências deste kit
Duas fontes, com pesos diferentes — e vale saber qual é qual:

- **[[a_scb_usage_analysis_260722_0000|docs/ANALISE-USO-SCB]]** é medição: tamanhos de arquivo contados, custos em tokens calculados, com as ressalvas contra o próprio projeto explicitadas. É daí que vêm as regras 1, 4, 6 e 7.
- **[[b_reference_case_spo|exemplos/caso-spo]]** é **narrativa não verificada**: os números ("14 passagens", "84 achados") vêm de relato, sem relatório nem commit anexado. Use como lista de armadilhas plausíveis, não como aferição.

O kit inteiro foi auditado contra si mesmo em 2026-07-30; o que a auditoria reprovou virou correção em [[b_kit_changelog|docs/CHANGELOG-KIT]] (v4).

## Como o kit evolui
Fim de milestone → [[b_process/skills/retrospective/SKILL|retrospectiva]] → lições no [[d_agent_learnings|APRENDIZADOS]] do projeto → lição repetida em 2+ projetos vira regra aqui, com entrada em [[b_kit_changelog|docs/CHANGELOG-KIT]]. Perfil novo nasce salvando um `perfil-generico` preenchido; skill nova nasce copiando o formato de [[b_process/skills/README|skills/]]. O kit é um repositório git: versione as mudanças.
