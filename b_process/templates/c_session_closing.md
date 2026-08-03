---
tags: [template]
status: atual
---
## Fecho de sessão — {{date:YYYY-MM-DD}} · <papel/skill da sessão>

**Entregue:** <o que saiu desta sessão, 1 linha>
**Portão rodado:** <comando + resultado — na SUA máquina, não no sandbox>

- [ ] Passou no portão objetivo (o número, não "parece bom"). Falhou? → devolve pedindo **delta**, não recomeça.
- [ ] Veio como delta (só o alterado), não regeneração.
- [ ] Decisão fechada → **D-NN** em [[c_decisions|DECISIONS]] (com gatilho, se for estrutural).
- [ ] Bug encontrado → **QA-NN** em [[c_decisions|DECISIONS]] + reprodução em `dev/qa-{{date:YYYY-MM-DD}}.md`.
- [ ] Pendência que é **sua** (não do agente) → **Q-NN** em [[c_decisions|DECISIONS]].
- [ ] "Estado atual" do [[a_context_source|CONTEXT]] reescrito **por substituição** — versão, pronto, em andamento (máx 1), próximo, bloqueado, Q-NN abertas.
- [ ] Nenhum número vigente duplicado fora do [[a_context_source|CONTEXT]] (regra 6).
- [ ] Linha datada no [[a_changelog|CHANGELOG]].
- [ ] [[c_backlog|BACKLOG]] atualizado: card movido, novo card com **portão escrito**.
- [ ] Lição nova? 1 linha em [[d_agent_learnings|APRENDIZADOS]] — inclusive erro do agente.
- [ ] `python scripts/check.py` verde.
- [ ] Commit: `<tipo>(<escopo>): D-NN/QA-NN <resumo>`

**Ficou para o dono (máquina real):** <testes oficiais, migration, deploy, push — o que a IA não pode rodar>
**Próxima sessão começa com:** <papel/skill + o arquivo do momento>
