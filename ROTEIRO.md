---
tags: [roteiro, execucao]
status: atual
---
# ROTEIRO — do dia 1 à entrega

> O caminho completo, em ordem, com **qual skill usar**, **o que você entrega ao agente** e **o portão que fecha cada passo**. Siga na ordem: cada sessão assume que a anterior passou no portão.
> Regra que atravessa tudo: uma skill por sessão · sempre por delta · nada avança sem portão objetivo.

## Antes de começar (15 minutos, você sozinho)
1. Crie o repositório de código do projeto (vazio) — separado deste vault.
2. Instale as skills (`skills/*/`) na sua ferramenta, ou deixe os `SKILL.md` à mão para colar.
3. Responda em uma frase: **quem usa isso e o que muda na vida dessa pessoa?** Se você não consegue, a Fase 0 vai extrair — mas o projeto começa mais caro.

---

## Fase 0 — Contexto (1 sessão)
| | |
|---|---|
| **Entrega ao agente** | [[prompts/00-bootstrap-contexto]] + a descrição crua do projeto |
| **Skill** | nenhuma (é entrevista, não construção) |
| **Você recebe** | ≤5 perguntas, depois o [[CONTEXT]] preenchido + candidatas a D-NN |
| **Portão** | `python scripts/checar.py` passa (≤4.000 chars) **e** você lê o CONTEXT e concorda com cada linha |

Cuide de 3 campos, porque eles evitam a maior parte do retrabalho:
- **Restrições inegociáveis** — o que torna a entrega inválida.
- **Representações obrigatórias** — dinheiro inteiro, data UTC, ID opaco. Declarar isso aqui é o que evita 6 versões de schema depois.
- **Critério de aceite** — o comando que fica verde. "Parece bom" não é critério.

Não coube em 4.000 caracteres? O excedente vai para `contexto/<tema>.md`, não para prosa comprimida.

---

## Fase 1 — Forma e plano (2 sessões)

**1a. Decidir a forma.** Skill: [[skills/arquitetura-monolito/SKILL|arquitetura-monolito]] (default) ou [[skills/arquitetura-microservicos/SKILL|arquitetura-microservicos]] se você acha que precisa distribuir — ela tem portão de existência e provavelmente vai reprovar; isso é o sistema funcionando. Mesma coisa para [[skills/frontend-mfe/SKILL|frontend-mfe]].
**Portão:** D-01 registrado com a forma escolhida **e o gatilho** que faria mudar.

**1b. Gerar o plano.** Entrega: [[prompts/01-planejador]] + [[CONTEXT]]. Você recebe o [[PLANO]] com módulos, contratos, portão por módulo e milestones.
**Portão:** para cada módulo, você consegue responder "outro agente implementaria isso lendo só o contrato?". Se não, devolva pedindo delta. Aprovado = **congelado** como D-NN.

---

## Fase 2 — Dados e domínio (1 sessão por módulo)
| | |
|---|---|
| **Skill** | [[skills/backend-dominio/SKILL\|backend-dominio]] |
| **Entrega** | [[CONTEXT]] + contrato do módulo + os arquivos que ele toca |
| **Portão** | migration roda num banco vazio · invariantes testados (inclusive tentando violar direto no banco) · transação não deixa efeito parcial |

Comece pelo schema. Escreva os invariantes como frases verificáveis **antes** do código — eles viram teste e, quando possível, constraint no banco.

**O projeto nasce de uma fonte de dados externa (coleta, planilha, API de terceiro)?** Então esta fase começa uma sessão antes, com [[skills/dados-analise/SKILL|dados-analise]]: trazer uma **amostra real** da estrutura. Modelar schema em cima de payload imaginado é a armadilha mais cara já paga por este kit — 6 ciclos de QA num projeto, 6 versões de schema em outro.
**Portão extra:** amostra real anexada em `contexto/integracoes.md` · coleta interrompida no meio preserva o já coletado.

---

## Fase 3 — Borda, UI e acesso (1 sessão por módulo)
Ordem: acesso → borda → tela.

| Passo | Skill | Portão |
|---|---|---|
| Acesso, se houver área sensível | [[skills/autenticacao/SKILL\|autenticacao]] | matriz `área × exigência` em D-NN; **cada** rota sensível testada sem sessão (página redireciona **e** API 401) |
| Borda, se a tela junta várias fontes | [[skills/backend-bff/SKILL\|backend-bff]] | teste com upstream fora e lento; falha parcial explícita no payload |
| Serviço↔serviço, se houver mais de um | [[skills/microservice-sync/SKILL\|microservice-sync]] | timeout comprovado; retry seguro (idempotência) |
| Telas | [[skills/frontend-uiux/SKILL\|frontend-uiux]] | 4 estados por tela · fluxo crítico no viewport mínimo · nenhum texto técnico vazando |

Na sessão de autenticação, responda antes de aprovar: **o que exatamente você quer proteger?** Trancar o fluxo principal de trabalho é o erro que se paga duas vezes — uma para implementar, outra para remover.

---

## Fase 4 — Testes e revisão (2 sessões, em ordem)

**4a. Testes.** Skill: [[skills/testes/SKILL|testes]]. Unitário nas regras e bordas; **um teste de sistema ponta a ponta por fluxo que gera valor**.
**Portão:** suíte verde **na sua máquina** · roda duas vezes com o mesmo resultado · lacunas declaradas (não maquiadas).

**4b. Revisão adversarial.** Skill: [[skills/guardrails-review/SKILL|guardrails-review]], em **sessão separada** — o mesmo contexto que construiu não enxerga o próprio ponto cego.
**Portão:** relatório em `dev/qa-AAAA-MM-DD.md` · 12 frentes percorridas · cada achado com reprodução · crítico/alto corrigidos, cada correção com teste de regressão citando `QA-NN`.

> **Isto é o que mais separa um resultado bom de um medíocre.** Num projeto real deste kit, foram 14 passagens e 84 achados corrigidos antes da entrega — os mais graves eram segredo de sessão fixo e boot com placeholder, coisas que nenhum teste de feature pega. Repita 4a↔4b até o placar de crítico/alto zerar de verdade.

---

## Fase 5 — Empacotar e operar (1–2 sessões)
| | |
|---|---|
| **Skill** | [[skills/iac-docker-terraform/SKILL\|iac-docker-terraform]] |
| **Portão** | `up -d` num ambiente limpo · derrubar e subir **preserva os dados** · versão consultável em runtime · nenhum segredo na imagem/repo |

Se o sistema roda continuamente na máquina de outra pessoa: publique a imagem num registry e faça a máquina consumir **versão pinada** — build na máquina do cliente é lento, frágil e sem rastro. Atualização automática só depois de o **rollback ser testado na máquina real**, e com `RUNBOOK.md` escrito.

---

## Fase 6 — Entrega (1 sessão)
| | |
|---|---|
| **Entrega ao agente** | [[prompts/05-revisao-entrega]] + acesso à pasta + [[CHECKLIST]] |
| **Portão** | zip **aberto e conferido** (lista de arquivos + peso em MB) · nenhum segredo/dependência/banco dentro · estado numérico só no [[CONTEXT]] · `RUNBOOK.md` se o sistema opera |

---

## Fecho de milestone — retrospectiva (1 sessão)
Entrega: [[prompts/06-retrospectiva]] + o trabalho recém-feito. Saída: 3–7 lições em [[APRENDIZADOS]], incluindo os erros do agente. Lição que aparecer em 2 projetos vira regra do kit.

---

## O ciclo que você repete 90% do tempo
```
skill do papel + CONTEXT + só o arquivo do momento
   → pedir DELTA
   → rodar o PORTÃO (na sua máquina)
   → registrar D-NN / QA-NN / Q-NN
   → reescrever "Estado atual" do CONTEXT (por substituição)
   → datar no CHANGELOG → commit citando os IDs
```
Esse fecho é onde o processo mais vaza — pular um passo é o que faz o estado divergir e o histórico sumir. No Obsidian, insira [[templates/fecho-de-sessao|fecho-de-sessao]] (`Ctrl/Cmd+P` → *Insert template*) e vá marcando: fica visível o que faltou.

## Seu papel (o que a IA não faz por você)
1. **Guardião do portão** — aceite = rodar a seção certa do [[CHECKLIST]]. Falhou? Devolve pedindo delta, nunca "refaz tudo".
2. **Decisor** — toda Q-NN é sua. O agente não muda regra de negócio nem rumo.
3. **Operador da máquina real** — testes oficiais, migrations, deploy, push. O sandbox do agente é indicativo.
4. **Fonte dos dados** — o que você não informar fica lacuna declarada, nunca inventada.

**Frases que economizam sessões:** "Isso passou no portão? Mostra o número." · "Cadê o D-NN?" · "Me manda só o delta." · "Rodou na minha máquina ou no sandbox?" · "Viu uma amostra real antes de escrever esse parser?" · "Isso muda alguma decisão ou número?"

## Ritmo esperado
Um app pequeno (o porte do caso em [[exemplos/caso-spo]]) leva da ordem de **10 dias** de sessões dirigidas: ~1 dia de contexto e plano, ~5 de implementação, ~2 de QA em passagens repetidas, ~1 de empacotamento, ~1 de entrega e ajustes. Projeto pequeno pode rodar o **modo curto** (0 → 2 → 4 → 6): pula-se fase, **não se pula regra** — contexto orçado, delta, D-NN e portão objetivo existem em qualquer tamanho.
