# APRENDIZADOS.md — lições para os próximos agentes (arquivo vivo)

> Alimentado ao fechar milestones (prompt `06-retrospectiva.md`). 1 linha por lição, generalizável, honesta — inclua os SEUS erros. Lição repetida em 2+ projetos → promover a regra do kit.

## Herdadas (SCM → SCB → kit v2)
- **Observe antes de construir:** nunca escreva parser/integração sem uma amostra REAL do payload/estrutura — chutar a estrutura de uma fonte custou 6 ciclos de QA; duvidar de uma API sem fazer 1 chamada quase custou uma feature.
- **"Está quebrado" vs "falta dado":** cheque o estado do dado antes de caçar bug no código.
- **Salve incremental:** loop de coleta grava com `try/finally` e é resumível; erro ou rate-limit no meio nunca descarta o já feito.
- **Barato ≠ valioso:** feature fácil que não muda decisão/número é cruft — pergunte "isso muda algo?" antes de construir.
- **Ganho não transfere de contexto:** o que passou no portão num dataset/liga/projeto re-passa no novo; o dado mudou.
- **Valide contra um valor conhecido** antes de confiar num cálculo novo.
- **Processo vivo tem cache:** servidor/build antigo mascara sua mudança — reinicie antes de julgar (e avise o dono de reiniciar).
- **Sandbox ≠ máquina real:** o portão final roda na máquina do dono; termine dizendo o que ele precisa rodar.
- **Rejeitar é o portão funcionando:** ~7 rejeições por 2 adoções é saúde, não fracasso; registre a rejeição com o número que matou.
- **Honestidade compõe:** reportar fraqueza (métrica atrás do benchmark, ganho marginal) gera mais confiança do que esconder — e não precisa ser desfeito depois.

## Deste projeto
- <data> — <lição em 1 linha>
