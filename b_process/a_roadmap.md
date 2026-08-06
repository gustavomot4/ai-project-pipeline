---
tags: [roteiro, execucao]
status: atual
---
# ROTEIRO — do dia 1 à entrega

> O caminho completo, em ordem, com **qual skill usar**, **o que você entrega ao agente** e **o portão que fecha cada passo**. Siga na ordem: cada sessão assume que a anterior passou no portão.
> Regra que atravessa tudo: uma skill por sessão · sempre por delta · nada avança sem portão objetivo.

## Antes de começar (15 minutos, você sozinho)
1. Crie o repositório de código do projeto (vazio) — separado deste vault.
2. `python scripts/install_hook.py` — sem isso, os portões automáticos só rodam se você lembrar.
3. Instale as skills (`b_process/skills/*/`) na sua ferramenta, ou deixe os `SKILL.md` à mão para colar.
4. Escolha o perfil da stack: [[b_web_nextjs|web-nextjs]] · [[c_data_python|dados-python]] · [[a_generic|genérico]]. Os blocos dele entram no [[a_context_source|CONTEXT]] na Fase 0.
5. Responda em uma frase: **quem usa isso e o que muda na vida dessa pessoa?** Se você não consegue, a Fase 0 vai extrair — mas o projeto começa mais caro.

---

## Fase 0 — Contexto (1 sessão)

**O projeto já existe?** Então esta fase é [[b_process/skills/existing-project-adoption/SKILL|adocao-projeto-existente]], não bootstrap: o mapa se faz do **código**, não do que o dono lembra nem do README. Ela entrega o mesmo `a_context/a_context_source.md`, mais um `a_context/b_plan.md` retroativo, as decisões já tomadas como `D-NN [retroativa]` e a lista do que ninguém soube explicar (`Q-NN`). **Portão extra:** nenhum arquivo de código alterado na sessão, e o baseline registrado (builda? testes passam? sobe do zero? é este o código em produção?). Depois dela, siga daqui como qualquer projeto.

| | |
|---|---|
| **Skill** | [[b_process/skills/context-bootstrap/SKILL\|bootstrap-contexto]] |
| **Entrega ao agente** | a descrição crua do projeto — nada mais |
| **Você recebe** | ≤5 perguntas, depois o [[a_context_source|CONTEXT]] preenchido + candidatas a D-NN |
| **Portão** | `python scripts/check.py` passa (≤4.000 chars) **e** você lê o CONTEXT e concorda com cada linha |

Cuide de 3 campos, porque eles evitam a maior parte do retrabalho:
- **Restrições inegociáveis** — o que torna a entrega inválida.
- **Representações obrigatórias** — dinheiro inteiro, data UTC, ID opaco. Declarar isso aqui é o que evita 6 versões de schema depois.
- **Critério de aceite** — o comando que fica verde. "Parece bom" não é critério.

Não coube em 4.000 caracteres? O excedente vai para `a_context/<tema>.md`, não para prosa comprimida.

---

## Fase 1 — Forma e plano (2 sessões)

**1a. Decidir a forma.** Skill: [[b_process/skills/architecture-monolith/SKILL|arquitetura-monolito]] (default) ou [[b_process/skills/architecture-microservices/SKILL|arquitetura-microservicos]] se você acha que precisa distribuir — ela tem portão de existência e provavelmente vai reprovar; isso é o sistema funcionando. Mesma coisa para [[b_process/skills/frontend-mfe/SKILL|frontend-mfe]].
**Portão:** D-01 registrado com a forma escolhida **e o gatilho** que faria mudar.

**1b. Gerar o plano.** Skill: [[b_process/skills/planner/SKILL|planejador]]; entrega: [[a_context_source|CONTEXT]]. Você recebe o [[b_plan|PLANO]] com módulos, contratos, portão por módulo e milestones.
**Portão:** para cada módulo, você consegue responder "outro agente implementaria isso lendo só o contrato?". Se não, devolva pedindo delta. Aprovado = **congelado** como D-NN.

**1c. Conferir se os artefatos contam a mesma história.** Skill: [[b_process/skills/artifact-consistency/SKILL|consistencia-artefatos]], em **sessão separada** — quem escreveu o plano é a última pessoa que deveria julgar se ele cobre o contexto. Somente leitura: ela lê CONTEXT + PLANO + BACKLOG + DECISIONS e procura módulo sem tarefa, tarefa sem módulo, restrição inegociável sem portão, critério de aceite sem número, plano adotando o que o DECISIONS rejeitou e termo com dois nomes.
**Portão:** zero achados CRÍTICOS · todo módulo com ao menos uma tarefa · toda restrição inegociável com um portão que a verifica.

> Esta sessão custa 15 minutos e existe porque o `check.py` **não consegue** fazer o trabalho dela: ele julga forma (orçamento, link, ID, segredo) de modo determinístico; módulo esquecido e adjetivo sem número são significado, e nenhum script julga significado.

---

## Fase 2 — Dados e domínio (1 sessão por módulo)
| | |
|---|---|
| **Skill** | [[b_process/skills/backend-domain/SKILL\|backend-dominio]] |
| **Entrega** | [[a_context_source|CONTEXT]] + contrato do módulo + os arquivos que ele toca |
| **Portão** | migration roda num banco vazio · invariantes testados (inclusive tentando violar direto no banco) · transação não deixa efeito parcial |

Comece pelo schema. Escreva os invariantes como frases verificáveis **antes** do código — eles viram teste e, quando possível, constraint no banco.

**O projeto nasce de uma fonte de dados externa (coleta, planilha, API de terceiro)?** Então esta fase começa uma sessão antes, com [[b_process/skills/data-analysis/SKILL|dados-analise]]: trazer uma **amostra real** da estrutura. Modelar schema em cima de payload imaginado é a armadilha mais cara já paga por este kit — 6 ciclos de QA num projeto, 6 versões de schema em outro.
**Portão extra:** amostra real anexada em `a_context/integrations.md` · coleta interrompida no meio preserva o já coletado.

---

## Fase 3 — Borda, UI e acesso (1 sessão por módulo)
Ordem: acesso → borda → tela.

| Passo | Skill | Portão |
|---|---|---|
| Acesso, se houver área sensível | [[b_process/skills/authentication/SKILL\|autenticacao]] | matriz `área × exigência` em D-NN; **cada** rota sensível testada sem sessão (página redireciona **e** API 401) |
| Borda, se a tela junta várias fontes | [[b_process/skills/backend-bff/SKILL\|backend-bff]] | teste com upstream fora e lento; falha parcial explícita no payload |
| Serviço↔serviço, se houver mais de um | [[b_process/skills/microservice-sync/SKILL\|microservice-sync]] | timeout comprovado; retry seguro (idempotência) |
| Telas | [[b_process/skills/frontend-uiux/SKILL\|frontend-uiux]] | 4 estados por tela · fluxo crítico no viewport mínimo · nenhum texto técnico vazando |

Na sessão de autenticação, responda antes de aprovar: **o que exatamente você quer proteger?** Trancar o fluxo principal de trabalho é o erro que se paga duas vezes — uma para implementar, outra para remover.

---

## Fase 4 — Testes e revisão (2 sessões, em ordem)

**4a. Testes.** Skill: [[b_process/skills/testing/SKILL|testes]]. Unitário nas regras e bordas; **um teste de sistema ponta a ponta por fluxo que gera valor**.
**Portão:** suíte verde **na sua máquina** · roda duas vezes com o mesmo resultado · lacunas declaradas (não maquiadas).

**4b. Revisão adversarial.** Skill: [[b_process/skills/guardrails-review/SKILL|guardrails-review]], em **sessão separada** — o mesmo contexto que construiu não enxerga o próprio ponto cego.
**Portão:** relatório em `e_qa/<n>_qa_pass<NN>_report_<AAMMDD>_<HHMM>.md` · 12 frentes percorridas · cada achado com reprodução · crítico/alto corrigidos, cada correção com teste de regressão citando `QA-NN`.

> **Não pare na primeira passagem.** Os defeitos que mais custam — segredo de sessão fixo, boot aceitando placeholder, divergência entre doc e código — não aparecem em teste de feature; aparecem em ataque dirigido, e raramente no primeiro. Repita 4a↔4b até o placar de crítico/alto zerar de verdade. (O [[b_reference_case_spo|caso de referência]] relata 14 passagens até chegar lá; é relato, não medição — trate como ordem de grandeza.)

> **Critério de saída do laço — sem ele, "repita até zerar" é laço infinito.** Se o placar de crítico/alto **não cair em 3 passagens consecutivas**, **pare o laço de QA** e abra sessão de [[b_process/skills/artifact-consistency/SKILL|consistencia-artefatos]] ou [[b_process/skills/planner/SKILL|planejador]]. Achado que reaparece três vezes não é bug: é sintoma de plano errado, e continuar revisando queima sessões atacando o efeito. O sinal é objetivo e sai dos relatórios que a Fase 4b já escreve — não depende de o agente se autoavaliar.

---

## Fase 5 — Empacotar e operar (1–2 sessões)
| | |
|---|---|
| **Skill** | [[b_process/skills/iac-docker-terraform/SKILL\|iac-docker-terraform]] |
| **Portão** | `up -d` num ambiente limpo · derrubar e subir **preserva os dados** · versão consultável em runtime · nenhum segredo na imagem/repo |

Se o sistema roda continuamente na máquina de outra pessoa: publique a imagem num registry e faça a máquina consumir **versão pinada** — build na máquina do cliente é lento, frágil e sem rastro. Atualização automática só depois de o **rollback ser testado na máquina real**, e com `RUNBOOK.md` escrito.

**Sistema que roda continuamente exige uma sessão de [[b_process/skills/observability/SKILL|observabilidade]] antes de entregar.** O teste é uma pergunta: quando quebrar às 14h de uma terça, o dono descobre o que houve sem abrir o código? Sem isso, todo incidente futuro vira uma sessão de arqueologia — e a Fase 6 não deveria aprovar.
**Guarda dado de pessoas?** [[b_process/skills/privacy-personal-data/SKILL|privacidade-dados-pessoais]] entra junto com o schema (Fase 2), não aqui: coluna criada sem finalidade escrita vira obrigação permanente, e retenção retroativa é migração dolorosa.

---

## Fase 6 — Entrega (1 sessão)
| | |
|---|---|
| **Skill** | [[b_process/skills/delivery-review/SKILL\|revisao-entrega]] |
| **Entrega ao agente** | acesso à pasta + [[b_checklist|CHECKLIST]] |
| **Portão** | zip **aberto e conferido** (lista de arquivos + peso em MB) · nenhum segredo/dependência/banco dentro · estado numérico só no [[a_context_source|CONTEXT]] · `RUNBOOK.md` se o sistema opera |

---

## Depois da entrega — sustentar (o ciclo que não acaba)
A Fase 6 fecha a construção, não o projeto. Daqui em diante o roteiro deixa de ser uma linha e vira um gatilho por situação:

| Situação | Skill | Portão que não se negocia |
|---|---|---|
| "quebrou", "está errado", "deu erro" | [[b_process/skills/debugging-diagnosis/SKILL\|depuracao-diagnostico]] | reprodução determinística **antes** de qualquer edição · causa provada (liga/desliga) · teste de regressão citando `QA-NN` |
| "está lento" | [[b_process/skills/performance/SKILL\|performance]] | baseline medido antes · gargalo apontado por profiler, não por intuição · uma mudança por vez |
| "não sei o que aconteceu ontem" | [[b_process/skills/observability/SKILL\|observabilidade]] | o dono responde às 3 perguntas sem abrir o código · nada sensível em log |
| subir biblioteca, CVE reportada | [[b_process/skills/dependencies-supply-chain/SKILL\|dependencias-supply-chain]] | uma atualização por vez, suíte verde entre elas · CVE tratada, mitigada com prova, ou aceita com `D-NN` |
| ideia de melhoria depois do baseline | [[b_process/skills/evolution-auditor/SKILL\|auditor-evolucao]] | lista-morta percorrida · portão escrito antes do experimento |

Duas regras de encaminhamento que evitam sessão desperdiçada:

- **"Está lento" × "está lento desde ontem".** O segundo é depuração, não performance: algo mudou, e achar o quê é mais barato que otimizar o que já estava rápido.
- **Precisou depurar duas vezes o mesmo sintoma?** O que faltou foi observabilidade. A terceira sessão de arqueologia custa mais que instrumentar de uma vez.

---

## Fecho de milestone — retrospectiva (1 sessão)
Skill: [[b_process/skills/retrospective/SKILL|retrospectiva]]; entrega: o trabalho recém-feito. Saída: 3–7 lições em [[d_agent_learnings|APRENDIZADOS]], incluindo os erros do agente. Lição que aparecer em 2 projetos vira regra do kit.

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
Esse fecho é onde o processo mais vaza — pular um passo é o que faz o estado divergir e o histórico sumir. No Obsidian, insira [[c_session_closing|fecho-de-sessao]] (`Ctrl/Cmd+P` → *Insert template*) e vá marcando: fica visível o que faltou.

> Seu papel em cada passo (guardião do portão, decisor, operador da máquina real) e as frases que economizam sessão estão no [[README]] — aqui não se repetem, para o roteiro continuar sendo só o caminho.

## Ritmo esperado
Um app pequeno (o porte do caso em [[b_reference_case_spo|caso de referência]]) leva da ordem de **10 dias** de sessões dirigidas: ~1 dia de contexto e plano, ~5 de implementação, ~2 de QA em passagens repetidas, ~1 de empacotamento, ~1 de entrega e ajustes. Projeto pequeno pode rodar o **modo curto** (0 → 2 → 4 → 6): pula-se fase, **não se pula regra** — contexto orçado, delta, D-NN e portão objetivo existem em qualquer tamanho.
