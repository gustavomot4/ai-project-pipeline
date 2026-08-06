---
tags: [checklist, portao]
status: atual
---
# CHECKLIST.md — portões por tipo de entrega

> Use a seção do tipo da entrega. Falhou um item ⇒ devolve pedindo **delta**, nunca "refaz tudo".
> Cada skill em `b_process/skills/` traz o portão detalhado do seu papel; este arquivo é o portão que **você** roda antes de aceitar.

## Qualquer entrega
- [ ] Passou no portão objetivo do [[a_context_source|CONTEXT]] (não em "parece bom")?
- [ ] Veio como **delta** (só o alterado), não regeneração?
- [ ] Decisão → D-NN · bug → QA-NN citado no commit · pendência do dono → Q-NN?
- [ ] [[a_context_source|CONTEXT]] atualizado por substituição (≤ 4.000 chars) e o datado foi para o [[a_changelog|CHANGELOG]]?
- [ ] Nenhum dado/fonte inventado (lacuna continua declarada)?
- [ ] O agente disse o que **você** precisa rodar na máquina real?

## Arquitetura (antes do primeiro código)
- [ ] A forma (monólito modular × microserviços × MFE) está registrada como D-NN, **com o gatilho** que faria mudar?
- [ ] Se distribuiu algo: o portão de existência foi respondido com fatos (times reais, observabilidade existente), não com intenção?
- [ ] Mapa de módulos/serviços × dado dono × dependências, acíclico?
- [ ] Representações obrigatórias declaradas no [[a_context_source|CONTEXT]] (dinheiro inteiro, data UTC, ID opaco, unidades)?

## Consistência entre artefatos (Fase 1c — antes do primeiro código)
> Sessão de [[b_process/skills/artifact-consistency/SKILL|consistencia-artefatos]], separada de quem escreveu o plano. Roda `python scripts/task.py check` **antes**: a metade formal já é máquina.
- [ ] Todo módulo do [[b_plan|PLANO]] tem ao menos uma tarefa no [[c_backlog|BACKLOG]] marcada com `**Módulo:** M<N>` — ou está declarado fora do escopo no [[a_context_source|CONTEXT]]?
- [ ] Toda **restrição inegociável** do CONTEXT tem um portão, em algum módulo, que a verifica? (Restrição que ninguém checa é decoração.)
- [ ] Todo critério de aceite é um comando ou um número — nenhum "rápido", "seguro", "intuitivo"?
- [ ] O PLANO não adota nada que o [[c_decisions|DECISIONS]] já **rejeitou**?
- [ ] O mesmo conceito não aparece com dois nomes entre CONTEXT, PLANO e BACKLOG?
- [ ] Zero achados **CRÍTICOS** em aberto antes de escrever a primeira linha de código?

## Backend / domínio
- [ ] Migration roda num banco vazio e recria o schema inteiro?
- [ ] Migration é aditiva (expand/contract)? Remoção só uma release depois?
- [ ] Invariantes do domínio testados — inclusive tentando violar pela via mais baixa (banco)?
- [ ] Operação transacional não deixa efeito parcial quando falha no meio?
- [ ] Escrita que o cliente pode repetir é idempotente (retry/duplo clique não duplica)?
- [ ] Ausente ≠ zero: campo que não veio continua nulo, não virou `0`/`""`/hoje?
- [ ] Mudou fórmula ou contrato de saída? ⇒ bump de versão + D-NN

## Borda (BFF) e integração entre serviços
- [ ] Foi escrito a partir de **amostra real** do payload, não de suposição?
- [ ] Timeout explícito em toda chamada externa, com o valor comprovado por teste?
- [ ] Comportamento definido e testado para: dependência fora, dependência lenta, resposta parcial?
- [ ] Falha parcial é sinalizada no payload em vez de virar zero/vazio silencioso?
- [ ] Erro de upstream não vaza cru para o cliente?
- [ ] Retry só onde é seguro repetir (idempotência garantida antes)?
- [ ] Nenhum segredo de upstream exposto ao cliente?

## Frontend / UI
- [ ] Os 4 estados por tela que busca dado: carregando · vazio · erro · sucesso?
- [ ] Fluxo crítico executado ponta a ponta no **viewport mínimo** e no desktop, com evidência?
- [ ] Nenhum `undefined`/`NaN`/texto técnico na tela; erro em linguagem de gente?
- [ ] Ação irreversível pede confirmação dizendo o que vai acontecer?
- [ ] Teclado percorre o fluxo crítico, com foco visível; `label` ligado a cada input?
- [ ] Formatação (dinheiro, data) acontece só na exibição, sobre valor cru?
- [ ] Se MFE: remote ausente degrada só a própria área; nenhuma dependência crítica duplicada no bundle?

## Autenticação e acesso
- [ ] Matriz `área × exigência` registrada como D-NN e aprovada pelo dono?
- [ ] Para **cada** rota sensível: sem sessão → página redireciona **e** API retorna 401/403 (teste automatizado)?
- [ ] Área declarada aberta continua sem fricção?
- [ ] Senha/PIN só como hash forte com sal; comparação em tempo constante?
- [ ] Segredo gerado por instalação, fora do repositório, e o boot recusa iniciar com o valor de exemplo?
- [ ] Expiração e logout invalidam de fato no servidor?
- [ ] Limite de tentativas ativo no ponto de entrada?
- [ ] Rota nova nasce protegida (nega por padrão)?

## Testes
- [ ] Suíte verde **na máquina do dono**, com o comando declarado?
- [ ] Bordas cobertas: vazio, zero, negativo, ausente, limite ±1, duplicado, divisão por zero?
- [ ] Cada invariante do domínio com teste próprio?
- [ ] Fluxo crítico com teste de sistema ponta a ponta, sem dublê no caminho principal?
- [ ] Cada `QA-NN` corrigido tem teste de regressão que falharia antes?
- [ ] Suíte roda duas vezes, e em ordem alterada, com o mesmo resultado?
- [ ] Nenhum teste depende de rede real, de `now()` ou de estado de outro teste?
- [ ] O que **não** está coberto foi declarado?

## Revisão adversarial (guardrails)
- [ ] **Relatório registrado** em `e_qa/<n>_qa_pass<NN>_report_<AAMMDD>_<HHMM>.md` — sem relatório, a fase não aconteceu, mesmo com placar zero?
- [ ] As 12 frentes da skill percorridas, com o que não deu para verificar declarado?
- [ ] Cada achado tem reprodução (comando + observado × esperado) e severidade?
- [ ] Crítico e alto corrigidos, citados no commit, com teste de regressão?
- [ ] `python scripts/check.py --historico-completo` **e** `git grep` executados; cruft varrido?
- [ ] Doc × comportamento conferidos (divergência é achado)?
- [ ] Amostra real de **log** conferida por dado pessoal e segredo (não basta ler o código que gera o log)?

## Correção de defeito (depuração)
- [ ] Reprodução determinística escrita **antes** da correção — comando, observado × esperado?
- [ ] Foi checado se era **falta de dado** antes de investigar código?
- [ ] Confirmado que o dono estava olhando a versão que de fato roda (cache, build, container)?
- [ ] Causa-raiz **provada** (liga o gatilho, o defeito volta), não inferida por proximidade do deploy?
- [ ] Correção mínima, no módulo dono da causa — sem conserto de carona?
- [ ] Teste de regressão citando `QA-NN`, demonstrado falhando na versão antiga?
- [ ] Nenhum `catch` novo silenciando o sintoma?

## Performance
- [ ] Alvo definido pelo dono (quanto **deveria** demorar) antes de qualquer mudança?
- [ ] Baseline registrado: número, ambiente, volume de dado, versão, 3 medições?
- [ ] Gargalo apontado por **profiler ou plano de execução**, com evidência anexada?
- [ ] Uma mudança por vez, cada uma medida isoladamente?
- [ ] Medição pós no mesmo cenário e com volume realista de dado?
- [ ] Suíte verde; nenhum invariante relaxado para ganhar tempo?
- [ ] Cache novo tem dono, prazo e regra de invalidação escritos?
- [ ] Custo declarado (complexidade, memória, legibilidade) e novo baseline registrado?

## Observabilidade (sistema que roda continuamente)
- [ ] As 3 perguntas ("está de pé?", "o fluxo crítico passa?", "o que falhou desde ontem?") são respondíveis **sem abrir o código**?
- [ ] Log estruturado, com identificador de correlação do início ao fim de uma requisição real?
- [ ] **Nenhum dado pessoal ou segredo em log** — conferido numa amostra real?
- [ ] Nenhum `catch` que apenas loga e segue sem tratamento explícito?
- [ ] Healthcheck verifica dependência essencial e informa a versão em execução?
- [ ] Cada alerta tem limiar justificado, dono e ação escrita no `RUNBOOK.md`?
- [ ] Rotação e retenção configuradas; volume diário estimado?

## Dependências
- [ ] Lockfile versionado; instalação limpa reproduz exatamente as mesmas versões?
- [ ] Versões pinadas no que vai para produção (nenhuma faixa aberta)?
- [ ] Uma atualização por vez, com suíte verde registrada entre elas?
- [ ] Toda CVE conhecida: atualizada, mitigada **com prova**, ou aceita com `D-NN` e prazo?
- [ ] Dependência nova aprovada como `D-NN`, com árvore transitiva conferida e alternativa descartada?
- [ ] Licenças compatíveis com o uso; nenhuma dependência de desenvolvimento na imagem de produção?
- [ ] Dependências não usadas removidas; nenhum token de registry versionado?

## Dados pessoais (se o sistema guarda cadastro de pessoas)
- [ ] Inventário completo: campo · categoria · finalidade · base legal (`Q-NN`) · retenção · compartilhado com?
- [ ] Todo campo sem finalidade concreta: removido, ou mantido com `D-NN` que justifica?
- [ ] Ambiente de teste **sem** dado de produção (verificado, não presumido)?
- [ ] Exclusão a pedido do titular testada ponta a ponta, com a lista do que **não** é apagado e por quê?
- [ ] Exportação do titular gerada e conferida contra o inventário?
- [ ] Rotina de retenção implementada e testada — não apenas declarada em documento?
- [ ] Cifrado em repouso (sensível) e em trânsito, **inclusive backup**?

## Adoção de projeto existente
- [ ] Baseline registrado com saída real: builda? testes verdes? sobe do zero? é este o código em produção?
- [ ] `a_context/a_context_source.md` descreve o sistema **como ele é**, inclusive as partes feias?
- [ ] Decisões já tomadas registradas como `D-NN [retroativa]`, com gatilho de revisão?
- [ ] Toda incógnita virou `Q-NN` — nenhuma virou suposição escrita como fato?
- [ ] **Nenhum arquivo de código alterado** durante o mapeamento?
- [ ] Cobertura do mapa declarada (o que foi lido e o que ficou de fora)?

## Infraestrutura / IaC
- [ ] `up -d` sobe o sistema num ambiente limpo, com healthcheck verde?
- [ ] Derrubar e subir de novo **preserva os dados** (comprovado)?
- [ ] Versão em execução é consultável em runtime?
- [ ] Imagem base pinada; imagem final sem ferramenta de build; não roda como root?
- [ ] Nenhum segredo na imagem (inclusive em camada intermediária), no repositório ou em `.tf`?
- [ ] Se há atualização automática: **rollback testado na máquina real**, sem perda de dado?
- [ ] Se usa Terraform: `plan` revisado com todo `destroy`/`replace` explicado; state remoto com lock; ambientes isolados?
- [ ] Custo mensal declarado e dentro da restrição do [[a_context_source|CONTEXT]]?

## Documentos
- [ ] Estado numérico só no [[a_context_source|CONTEXT]] — os outros docs **apontam**, não repetem?
- [ ] Doc novo tem status (atual/rascunho/histórico/congelado) + data?
- [ ] Nenhum par de números conflitante entre docs?
- [ ] O documento descreve o comportamento **real** do código?

## Empacotamento e entrega
- [ ] Zip só com fonte + docs + dados curados (sem dependências instaladas, `.git`, banco, backup, segredo)?
- [ ] **Abriu o zip e conferiu** a lista de arquivos e o peso (MB, não GB)?
- [ ] Existe `RUNBOOK.md` se o sistema roda continuamente (rotina · o que fazer quando falha · o que NUNCA fazer)?
- [ ] O critério de "pronto" é comportamental: o usuário final faz o fluxo principal **sem assistência**?
