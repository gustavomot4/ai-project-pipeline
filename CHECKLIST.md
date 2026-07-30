---
tags: [checklist, portao]
status: atual
---
# CHECKLIST.md — portões por tipo de entrega

> Use a seção do tipo da entrega. Falhou um item ⇒ devolve pedindo **delta**, nunca "refaz tudo".
> Cada skill em `skills/` traz o portão detalhado do seu papel; este arquivo é o portão que **você** roda antes de aceitar.

## Qualquer entrega
- [ ] Passou no portão objetivo do [[CONTEXT]] (não em "parece bom")?
- [ ] Veio como **delta** (só o alterado), não regeneração?
- [ ] Decisão → D-NN · bug → QA-NN citado no commit · pendência do dono → Q-NN?
- [ ] [[CONTEXT]] atualizado por substituição (≤ 4.000 chars) e o datado foi para o [[CHANGELOG]]?
- [ ] Nenhum dado/fonte inventado (lacuna continua declarada)?
- [ ] O agente disse o que **você** precisa rodar na máquina real?

## Arquitetura (antes do primeiro código)
- [ ] A forma (monólito modular × microserviços × MFE) está registrada como D-NN, **com o gatilho** que faria mudar?
- [ ] Se distribuiu algo: o portão de existência foi respondido com fatos (times reais, observabilidade existente), não com intenção?
- [ ] Mapa de módulos/serviços × dado dono × dependências, acíclico?
- [ ] Representações obrigatórias declaradas no [[CONTEXT]] (dinheiro inteiro, data UTC, ID opaco, unidades)?

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
- [ ] **Relatório registrado** em `dev/qa-AAAA-MM-DD.md` — sem relatório, a fase não aconteceu, mesmo com placar zero?
- [ ] As 12 frentes da skill percorridas, com o que não deu para verificar declarado?
- [ ] Cada achado tem reprodução (comando + observado × esperado) e severidade?
- [ ] Crítico e alto corrigidos, citados no commit, com teste de regressão?
- [ ] `git grep` por segredo e varredura de cruft executados?
- [ ] Doc × comportamento conferidos (divergência é achado)?

## Infraestrutura / IaC
- [ ] `up -d` sobe o sistema num ambiente limpo, com healthcheck verde?
- [ ] Derrubar e subir de novo **preserva os dados** (comprovado)?
- [ ] Versão em execução é consultável em runtime?
- [ ] Imagem base pinada; imagem final sem ferramenta de build; não roda como root?
- [ ] Nenhum segredo na imagem (inclusive em camada intermediária), no repositório ou em `.tf`?
- [ ] Se há atualização automática: **rollback testado na máquina real**, sem perda de dado?
- [ ] Se usa Terraform: `plan` revisado com todo `destroy`/`replace` explicado; state remoto com lock; ambientes isolados?
- [ ] Custo mensal declarado e dentro da restrição do [[CONTEXT]]?

## Documentos
- [ ] Estado numérico só no [[CONTEXT]] — os outros docs **apontam**, não repetem?
- [ ] Doc novo tem status (atual/rascunho/histórico/congelado) + data?
- [ ] Nenhum par de números conflitante entre docs?
- [ ] O documento descreve o comportamento **real** do código?

## Empacotamento e entrega
- [ ] Zip só com fonte + docs + dados curados (sem dependências instaladas, `.git`, banco, backup, segredo)?
- [ ] **Abriu o zip e conferiu** a lista de arquivos e o peso (MB, não GB)?
- [ ] Existe `RUNBOOK.md` se o sistema roda continuamente (rotina · o que fazer quando falha · o que NUNCA fazer)?
- [ ] O critério de "pronto" é comportamental: o usuário final faz o fluxo principal **sem assistência**?
