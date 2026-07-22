# CHECKLIST.md — portões por tipo de entrega

> Use a seção do tipo da entrega. Falhou um item ⇒ devolve pedindo **delta**, nunca "refaz tudo".

## Qualquer entrega
- [ ] Passou no portão objetivo do `CONTEXT.md` (não em "parece bom")?
- [ ] Veio como **delta** (só o alterado), não regeneração?
- [ ] Decisão → D-NN · bug → QA-NN citado no commit · pendência do dono → Q-NN?
- [ ] `CONTEXT.md` atualizado por substituição (≤ 4.000 chars) e o datado foi para o `CHANGELOG.md`?
- [ ] Nenhum dado/fonte inventado (lacuna continua declarada)?

## Código
- [ ] Teste do módulo veio junto e está verde **na máquina do dono** (sandbox é indicativo, não portão)
- [ ] Bordas cobertas: vazio, zero, ausente, desconhecido, divisão por zero
- [ ] Invariantes do domínio intactos (somas, unidades, datas UTC…)
- [ ] Integração externa foi escrita a partir de **amostra real** (payload/estrutura), não de suposição?
- [ ] Mudou fórmula/contrato de saída? ⇒ bump de versão + rebuild documentado

## Afirmação numérica ("melhorou X")
- [ ] Número com incerteza (IC/n/seed declarados), não adjetivo
- [ ] Comparação pareada com baseline, sem vazamento treino/teste
- [ ] Sem regressão nas métricas não-alvo
- [ ] Amostra insuficiente foi declarada como "reprova por falta de dado", não maquiada

## QA (Fase 4)
- [ ] Sessão de QA tem **relatório registrado** (`dev/qa-AAAA-MM-DD.md`) — achado incidental não conta como Fase 4
- [ ] Cada achado tem reprodução (comando + observado × esperado)
- [ ] Crítico/alto corrigidos e citados no commit

## Documentos
- [ ] Estado numérico só no `CONTEXT.md` — os outros docs **apontam**, não repetem
- [ ] Doc novo tem status (atual/rascunho/histórico/congelado) + data
- [ ] Nenhum par de números conflitante entre docs (varra versões/contagens citadas)

## Empacotamento (Fase 6)
- [ ] Zip só com fonte + docs + dados curados (sem `.venv`/`node_modules`/`.git`/bancos/backups/segredos)
- [ ] **Abriu o zip e conferiu** a lista de arquivos e o peso (MB, não GB)?
