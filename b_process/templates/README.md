---
tags: [templates, indice]
status: atual
---
# templates/ — os modelos que tornam o ritual barato

O kit exige três registros que, escritos à mão, são esquecidos ou saem em formato diferente a cada vez: a **decisão**, o **achado de QA** e o **fecho de sessão**. Aqui eles são um clique.

## Usar no Obsidian
O plugin **Templates** (core, já ativo) está apontado para esta pasta. Coloque o cursor onde o texto deve entrar e chame `Insert template` (paleta de comandos, `Ctrl/Cmd+P`) — ou atribua um atalho em `Settings → Hotkeys → Templates: Insert template`.

| Modelo | Onde colar | Quando |
|---|---|---|
| [[a_decision\|decisao]] | tabela "Decisões" do [[c_decisions|DECISIONS]] | assunto fechado — inclusive quando a decisão é **rejeitar** |
| [[b_qa_finding\|achado-qa]] | tabela "Achados de QA" do [[c_decisions|DECISIONS]] | cada achado de uma sessão de [[b_process/skills/guardrails-review/SKILL\|guardrails-review]] |
| [[c_session_closing\|fecho-de-sessao]] | nota de rascunho, ou direto na conversa com o agente | **toda** vez que uma sessão termina |

`{{date}}` é substituído pela data de hoje na inserção. Fora do Obsidian, copie e cole — são markdown puro.

## Por que o fecho de sessão virou template
O ciclo de fechamento (D-NN → CONTEXT por substituição → CHANGELOG datado → commit citando IDs) está descrito em prosa no [[README]], no [[a_roadmap|ROTEIRO]], no [[a_context_source|CONTEXT]] e no [[b_checklist|CHECKLIST]] — quatro lugares, nenhum acionável no momento em que você precisa dele. Pular um passo é o que faz o estado divergir (regra 6) e o histórico sumir (regra 2). Como lista marcável, o passo esquecido fica visível.

## Criar um modelo novo
Arquivo `.md` nesta pasta, com frontmatter. Mantenha **curto e marcável**: modelo que exige edição pesada não é usado duas vezes.
