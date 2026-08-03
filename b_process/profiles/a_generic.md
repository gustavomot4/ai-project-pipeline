---
tags: [perfil, stack]
status: atual
---

# Perfil — genérico (qualquer stack)

> Use quando nenhum perfil pronto servir. Este perfil não dá respostas — dá o **método** para extrair, na Fase 0, as restrições que evitam retrabalho. Cole o resultado no `a_context/a_context_source.md`. Se o tipo de projeto se repetir, salve o preenchido como `perfis/perfil-<tipo>.md` — é assim que nascem perfis novos.

## 1. Restrições da stack — perguntas que extraem o que dói depois
- O que essa combinação de ferramentas **não suporta nativamente**? (tipos, enums, datas, concorrência, tamanhos)
- O que ela **exige em produção** que o tutorial esconde? (build, variáveis de ambiente, permissões, versões mínimas)
- Quais **representações são obrigatórias** no domínio? (dinheiro em inteiro, datas UTC, IDs opacos, encoding, unidades)
- O que **não pode entrar no repositório**? (segredos, dados crus, derivados, binários grandes)
- Há **limite externo**? (cota/rate-limit de API, ToS, licença, teto de custo)

Cada resposta vira 1 linha em "Restrições da stack" do `a_context/a_context_source.md` — **antes** do primeiro código.

## 2. Quem roda o quê (a divisão sempre existe)
- **Agente:** código/docs/testes; verificação indicativa no sandbox.
- **Dono:** o portão oficial (testes/build na máquina real), tudo que usa credencial, deploy, push.
- Liste os **comandos exatos** do dono. O que só o dono vê (UI, hardware, rede), o agente entrega com roteiro de verificação.

## 3. Critério de aceite default (ajuste, não apague)
- Comando(s) objetivo(s) verdes na máquina do dono — teste/build/lint, o que a stack tiver.
- Toda afirmação de "funciona/melhorou" com evidência observável (saída de comando, screenshot, número) — nunca adjetivo.
- QA adversarial (prompt `03`) sem crítico/alto aberto antes de considerar entregue.
- Projeto produz artefato versionável (modelo, schema, contrato)? Mudança = bump de versão + D-NN.

## 4. Operação (se o projeto roda continuamente)
- A entrega inclui `RUNBOOK.md` (1 página): rotina normal · o que fazer quando falha · o que NUNCA fazer.
- Defina o que é medido em operação (log, contador, alerta) — sem medição, incidente vira adivinhação.
