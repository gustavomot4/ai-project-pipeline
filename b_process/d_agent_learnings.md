---
tags: [aprendizados]
status: atual
---
# APRENDIZADOS.md — lições para os próximos agentes (arquivo vivo)

> Alimentado ao fechar milestones ([[b_process/skills/retrospective/SKILL|retrospectiva]]). 1 linha por lição, generalizável, honesta — inclua os SEUS erros. Lição repetida em 2+ projetos → promover a regra do kit ([[README]]).

## Herdadas (não repague estas)
- **Observe antes de construir:** nunca escreva parser/integração sem uma amostra REAL do payload/estrutura. Chutar a estrutura de uma fonte custou 6 ciclos de QA num projeto.
- **"Está quebrado" vs "falta dado":** cheque o estado do dado antes de caçar bug no código.
- **Declare a restrição da stack ANTES de modelar:** descobrir tarde o que o banco/framework não suporta custou 6 versões de schema em 7 dias. O perfil da stack entra no CONTEXT no dia 1.
- **Dinheiro é inteiro (centavos) e taxa é basis point desde a primeira migration:** trocar depois reescreve toda a camada de cálculo. `0.1 + 0.2 ≠ 0.3`.
- **Segredo é gerado por instalação, nunca versionado:** segredo de sessão fixo e boot com placeholder foram os dois achados mais graves de um projeto real. O boot deve recusar iniciar sem segredo próprio.
- **Amostra de segredo em documentação se inutiliza, não se isenta:** trocar o corpo do token por `XXXX` preserva o formato e mata o valor. Isentar a linha (`checar:ignore`, `# nosec`, `# gitleaks:allow`) cala só o *seu* scanner — o do GitHub barrou o push mesmo assim, e estava certo. Isenção serve para o que é comprovadamente inerte, não para o que só *você* sabe que é falso.
- **Fricção de segurança tem de casar com o uso real:** proteção que atrapalha o fluxo principal é removida pelo dono depois — proteja só o que ele quer proteger, e pergunte antes.
- **Máquina de usuário final consome artefato pronto, não compila:** build na máquina do cliente é lento e frágil; publique imagem e faça pull pinado com rollback.
- **Migration em produção é expand/contract:** aditiva primeiro, remoção só uma release depois — mais ainda se o deploy for automático.
- **Automação que roda sozinha precisa de RUNBOOK e rollback testado na máquina real** antes de ser ligada; senão é risco, não conveniência.
- **Doc que descreve comportamento tem de bater com o código:** doc desalinhada do comportamento é bug de doc, e conta como achado de QA.
- **Barato ≠ valioso:** feature fácil que não muda decisão nem número é cruft — pergunte "isso muda algo?" antes de construir.
- **Processo vivo tem cache:** servidor/build antigo mascara sua mudança — reinicie antes de julgar (e avise o dono).
- **Sandbox ≠ máquina real:** o portão final roda na máquina do dono; termine dizendo o que ele precisa rodar.
- **Rejeitar é o portão funcionando:** registre a rejeição com o número/motivo que matou.
- **Honestidade compõe:** reportar fraqueza gera mais confiança do que esconder — e não precisa ser desfeito depois.

## Deste projeto
- <data> — <lição em 1 linha>
