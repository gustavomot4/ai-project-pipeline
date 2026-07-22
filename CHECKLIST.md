# CHECKLIST.md — antes de aceitar um output da IA

> Rode esta lista antes de dar "aceito" em qualquer entrega da IA — um módulo, um doc, um deploy.
> É a sua trava contra o desperdício e contra "parece bom, então tá bom".

## Qualidade / correção
- [ ] Passou no **portão objetivo** definido no `CONTEXT.md` (teste / IC / typecheck / build / QA)?
- [ ] Cada afirmação de ganho tem **número e incerteza** ("Brier −0,004 IC>0"), não "melhorou"?
- [ ] Casos de borda cobertos (entrada vazia, zero, ausente, nome desconhecido)?
- [ ] Sem invariante quebrada (probabilidades somam 1; dinheiro em Int; datas em UTC; etc.)?

## Eficiência / anti-desperdício
- [ ] A mudança veio como **delta**, não como regeração do arquivo inteiro?
- [ ] `CONTEXT.md` foi atualizado **por substituição** e segue ≤1 página?
- [ ] O histórico datado foi para o `CHANGELOG.md` (não ficou no contexto)?
- [ ] Versões/contagens antigas foram **removidas ou marcadas como históricas** (sem "v0.4 vs v0.5" conflitante)?

## Rastreabilidade
- [ ] Decisão que fecha assunto virou **D-NN** em `DECISIONS.md` (com motivo)?
- [ ] Bug corrigido tem **QA-NN** citado no commit/código?
- [ ] Mensagem de commit diz **o quê** (`fix(vendas): QA-071 …`), não "FIX: correções"?

## Higiene / entrega
- [ ] Sem **segredo** versionado (`.env` real, chaves) — só `.env.example`?
- [ ] Sem **cruft** (`*.bak`, `*.tmp`, `.fuse_hidden`, `.DS_Store`, temporários)?
- [ ] `.gitignore` cobre deps/build/banco/backups?
- [ ] Para compartilhar: zip só de **fonte + docs** (sem `.venv`/`node_modules`/`.git`/backups)?
- [ ] **Abriu o zip e conferiu** que os arquivos certos estão lá? (lição do `.lnk` quebrado)
