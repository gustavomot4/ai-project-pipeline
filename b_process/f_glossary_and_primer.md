---
tags: [primer, glossario, onboarding, processo]
status: atual
tipo: guia
data: 2026-08-03
aliases: ["Primer", "Glossário", "Comece aqui"]
---
# Primer — para que serve este pipeline, e o que cada palavra quer dizer

> **Comece por aqui** se é a sua primeira vez no repositório. Depois: [[a_roadmap|ROTEIRO]] (o
> caminho executável) e [[README]] (os porquês e os limites). Este documento não repete
> nenhum dos dois — ele existe para você entender o vocabulário antes de encontrá-lo.

---

## 1. O problema que este pipeline resolve

Construir software com agentes de IA funciona muito bem por umas duas horas. Depois começam
seis coisas, e todas já custaram caro em projetos reais:

| O que acontece | Como se sente | Custo já pago |
|---|---|---|
| A IA **refaz tudo** em vez de mexer no trecho certo | "ela consertou o bug e quebrou outras três coisas" | o maior custo isolado de dois projetos |
| O contexto **incha** e é relido em toda sessão | as respostas ficam lentas, caras e mais burras | um "estado atual" de 1.930 caracteres relido em cada sessão |
| O estado **se espalha** por vários documentos e diverge | dois arquivos citando números diferentes, ninguém sabe qual vale | um card dizendo "63 testes" ao lado de outro dizendo "85" |
| A IA **inventa** dado para parecer completa | um número plausível que ninguém consegue rastrear | relatório que mente em silêncio |
| Decisões são **re-discutidas** toda semana | "por que a gente não usa microserviços mesmo?" pela quarta vez | sessões inteiras re-litigando o que já morreu |
| "Parece bom" **passa** como aceite | o defeito aparece na frente do cliente | 6 ciclos de QA por um parser escrito sem ver a fonte real |

Nenhum desses é problema de modelo ruim. São problemas de **processo ausente**. O pipeline é
um conjunto pequeno de hábitos que ataca um por um — e a maior parte deles já é cobrada
automaticamente por `scripts/check.py` a cada commit.

**Em uma frase:** o pipeline existe para que a IA construa por delta, com portão objetivo,
registrando cada decisão, gastando pouco contexto — e para que o que ela não sabe fique
declarado como lacuna em vez de virar invenção.

## 2. O que ele NÃO é

Ser honesto sobre isso é o que faz a equipe confiar no resto:

- **Não é um sistema que impede erro.** O kit tem 188 itens de checklist; o script julga 18
  (~10%). O resto depende de alguém rodar a seção certa. É um kit de **disciplina** com algumas
  travas automáticas.
- **Não é metodologia de gestão.** Não tem estimativa, sprint, atribuição por pessoa nem
  velocity. O `c_backlog.md` é uma lista com limite de trabalho em paralelo, não um Jira.
- **Não substitui code review humano.** A revisão adversarial (`guardrails-review`) é uma IA
  atacando o que outra IA construiu. Ajuda muito e não é a mesma coisa.
- **Não serve para tudo.** A tabela "Onde este kit para" no [[README]] lista onde ele deixa de
  servir — app grande com 30+ módulos, multi-repo, time acima de 4 pessoas. Leia antes de
  prometer para alguém.

---

## 3. O ciclo — 90% do dia a dia é isto

Tudo no pipeline serve a este loop. Se a equipe sair da apresentação sabendo só ele, já valeu:

```
1. ABRIR    uma skill (o papel da sessão) + o contexto-fonte + só o arquivo do momento
2. PEDIR    delta — o trecho que muda, nunca "refaz tudo"
3. PASSAR   pelo portão — a checagem objetiva, rodada na SUA máquina
4. REGISTRAR  decisão → D-NN · bug → QA-NN · pendência sua → Q-NN
5. ATUALIZAR  o "Estado atual" do contexto por substituição
6. DATAR    a linha no changelog
7. COMMITAR citando os IDs
```

Passo 5 e 6 são os que mais se pula, e são exatamente os que fazem o estado divergir e o
histórico sumir. No Obsidian existe um template de fecho de sessão para não esquecer.

---

## 4. Glossário — os termos que aparecem toda hora

Cada verbete: o que é · exemplo concreto · **o que custa ignorar**.

### Delta
**O que é:** a IA devolve **só o trecho alterado**, nunca o arquivo inteiro regenerado.

**Exemplo:** você pede para corrigir o cálculo do troco. Resposta certa: as 4 linhas da função
`calcular_troco` e mais nada. Resposta errada: o arquivo `caixa.py` inteiro reescrito "já
melhorando umas coisas".

**Custa ignorar:** a regeneração reescreve código que estava certo e testado, e o diff fica
grande demais para revisar de verdade — então ninguém revisa. Foi o maior custo isolado
medido em dois projetos. É por isso que a frase "**me manda só o delta**" existe.

### Portão *(gate)*
**O que é:** o critério objetivo que decide se uma entrega é aceita. Escrito **antes** do
trabalho começar, não depois de ver o resultado.

**Exemplo:** portão do módulo de vendas = "a migration roda num banco vazio · o teste de
`venda → fechamento` passa ponta a ponta · tentar deixar o estoque negativo direto no banco
falha". Isso passa ou não passa. Já "a tela ficou boa" não é portão, é opinião.

**Custa ignorar:** sem portão, o aceite vira "parece bom", e o defeito é descoberto pelo
usuário. A frase de segurança é "**isso passou no portão? Mostra o número.**"

### Portão de existência
**O que é:** um tipo especial de portão, no começo de algumas skills, que pergunta se a coisa
**deveria existir**. Reprovar é o resultado esperado na maior parte das vezes.

**Exemplo:** a skill de microserviços pergunta quantos times publicam independentemente hoje.
Um time só ⇒ reprovado, e a entrega é um monólito modular bem desenhado. Isso não é a IA se
recusando a trabalhar; é o sistema funcionando.

**Custa ignorar:** você paga todo o custo operacional de uma arquitetura distribuída sem
receber nenhum dos benefícios dela.

### Contexto-fonte
**O que é:** o arquivo `a_context/a_context_source.md`. É **o único que toda sessão carrega** e
a **única** fonte do estado atual do projeto: versão vigente, o que está pronto, o que está em
andamento, o que está bloqueado.

**Exemplo:**

```
Versão: v0.3 · Pronto: schema, vendas, autenticação
Em andamento: relatorio-de-fechamento · Bloqueado: Q-02 (arredondamento do troco)
```

**Custa ignorar:** se o estado morar em quatro arquivos, os quatro divergem. Aconteceu, está
medido, e é a origem da regra "**fonte única**".

### Orçamento *(de contexto)*
**O que é:** um limite **em número**, não em adjetivo. O contexto-fonte tem 4.000 caracteres, e
`check.py` reprova o commit se estourar.

**Exemplo:** "≤ 1 página" virou, num projeto real, um parágrafo-parede de 1.930 caracteres
relido em toda sessão. "≤ 4.000 caracteres" não tem essa brecha.

**Custa ignorar:** cada caractere ali é pago em **toda** sessão. Não coube? O excedente vai
para `a_context/<tema>.md`, lido sob demanda — nunca para prosa comprimida.

### D-NN — decisão
**O que é:** uma decisão registrada em `a_context/c_decisions.md`, com número sequencial, em no
máximo duas frases. **Append-only**: nunca se apaga nem se edita. Mudou de ideia? Linha nova
com `SUPERSEDE D-XX`.

**Exemplo:**

```
D-01 · ADOTADO · forma = monólito modular
       gatilho para revisar: um segundo time publicando independentemente
```

**Registre também as rejeições:**

```
D-02 · REJEITADO · microserviços no dia 1 · um time só, sem observabilidade distribuída
```

A lista de rejeitados é o que impede a IA (e a equipe) de
re-propor mensalmente o que já morreu.

**Custa ignorar:** sem D-NN, toda sessão re-discute o que já foi decidido, e ninguém lembra
por quê. A frase de segurança é "**cadê o D-NN?**"

### Q-NN — questão aberta
**O que é:** uma pergunta que **só o dono do projeto pode responder**, normalmente regra de
negócio. O agente registra e **para**; não decide.

**Exemplo:**

```
Q-02 · o troco arredonda para cima ou para baixo? · decidir antes do módulo de fechamento
```

**Custa ignorar:** a IA escolhe sozinha, escolhe plausível, e ninguém percebe até o cliente
reclamar do centavo. Regra de negócio ambígua não é da IA para decidir.

### QA-NN — achado de QA
**O que é:** um defeito encontrado, com número, severidade e reprodução. Citado na mensagem do
commit que o corrige.

**Exemplo:**

```
QA-07 · Alto · caixa.py:112 · retry duplica a venda · corrigido com chave de idempotência
commit:  fix(caixa): QA-07 idempotência na venda
```

**Custa ignorar:** o bug volta, agora sem o rastro de que já tinha sido corrigido uma vez. Toda
correção nasce com um **teste de regressão** que falharia na versão antiga.

### Lacuna declarada
**O que é:** o que não se sabe fica **escrito como não sabido**. Nunca preenchido com
estimativa, média ou suposição plausível.

**Exemplo:** "não há dado de vendas de janeiro; o total do trimestre cobre só fev–mar" —
em vez de estimar janeiro pela média dos outros dois.

**Custa ignorar:** é o defeito mais silencioso que existe. Passa em todos os testes, envenena
o número, e alguém decide com base nele. Primo direto disto: **ausente ≠ zero** — campo que
não veio continua nulo, nunca vira `0`, `""` ou a data de hoje.

### Sandbox × máquina real
**O que é:** o que o agente roda no ambiente dele é **indicativo**; o portão de verdade roda na
**sua** máquina. Toda sessão termina dizendo o que você precisa rodar.

**Exemplo:** o agente diz "os testes passaram aqui". Isso não é aceite. Aceite é você rodar
`npm test` na sua máquina e ver verde — com o servidor reiniciado, porque **processo vivo tem
cache** e mascara mudança.

**Custa ignorar:** você aprova algo que funciona só no ambiente do agente. A frase de segurança
é "**rodou na minha máquina ou no sandbox?**"

### Skill *(agente)*
**O que é:** um papel especializado, com regras e portão próprios, num arquivo `SKILL.md`
instalável na ferramenta de IA. São 23 — de fase (bootstrap, planejador, entrega), de
construção (backend, frontend, testes, autenticação) e de sistema vivo (depuração,
performance, observabilidade).

**Regra que vale sempre: uma skill por sessão.** Duas = duas responsabilidades disputando o
mesmo contexto, e nenhuma feita direito.

**Custa ignorar:** a sessão vira conversa genérica, sem portão e sem escopo.

### Observe antes de construir
**O que é:** nenhum parser, integração ou schema é escrito sem uma **amostra real** da estrutura
na mão.

**Exemplo:** antes de escrever o leitor da API do fornecedor, faça uma chamada e olhe o JSON
que volta de verdade — não o que a documentação promete.

**Custa ignorar:** custou **6 ciclos de QA** num projeto e 6 versões de schema em outro. A
frase de segurança é "**viu uma amostra real antes de escrever esse parser?**"

### Fonte única
**O que é:** cada informação tem **um** dono. Estado só no contexto-fonte; histórico só no
changelog; decisão só no registro de decisões. Nenhum documento repete o que outro diz — ele
**aponta**.

**Custa ignorar:** duplicata envelhece em silêncio e depois mente. `check.py` compara o "Em
andamento" entre o backlog e o contexto e reprova divergência.

### Revisão adversarial
**O que é:** uma sessão separada cujo único objetivo é **quebrar** o que foi construído. Não
melhora, não refatora, não elogia — e **não conserta**: reporta e prova.

**Por que sessão separada:** o mesmo contexto que construiu não enxerga o próprio ponto cego.

**Custa ignorar:** os defeitos que mais custam (segredo fixo no código, erro engolido por um
`catch`, doc divergindo do comportamento) não aparecem em teste de feature. Aparecem em ataque
dirigido, e raramente na primeira passagem.

### Retrospectiva
**O que é:** ao fechar um marco, destilar 3–7 lições **generalizáveis** — incluindo os erros do
próprio agente — em `d_agent_learnings.md`.

**Exemplo:** "configurei errado o Postgres" não é lição. "Declare a restrição do banco antes de
modelar" é — e essa custou 6 versões de schema.

**Custa ignorar:** o projeto seguinte paga o mesmo erro de novo.

### WIP
**O que é:** quantas tarefas podem estar "em andamento" ao mesmo tempo. Declarado no cabeçalho
do backlog e cobrado pelo script. Sozinho = 1; time de 3 = 3.

**Custa ignorar:** cinco coisas começadas e nenhuma passando no portão.

### Vault e frontmatter
**Vault:** o repositório é também um cofre do Obsidian — os `[[links]]` entre documentos
funcionam como navegação. Você não precisa do Obsidian para trabalhar; ele só torna a leitura
mais rápida.

**Frontmatter:** o bloco YAML no topo de todo documento, com `status` (atual / congelado /
histórico / rascunho) e `data`. É o que separa "isto vale hoje" de "isto é registro do que
valia".

### Padrão do repositório
**O que é:** onde cada coisa mora e como se nomeia — duas pastas (documentação e código), raiz
limpa, `prefixo_de_ordem` + `snake_case` em inglês, saída de IA datada com timestamp
`AAMMDD_HHMM`. Detalhe completo em [[e_repository_standard|padrão do repositório]].

**O prefixo `77777777_`** na pasta de documentação não é enfeite: é o que a mantém sempre no
topo da árvore, acima de qualquer pasta de código, em qualquer explorador de arquivos.

---

## 5. Quem faz o quê

O pipeline separa isso de propósito, porque a maior parte dos acidentes acontece quando as
fronteiras ficam confusas.

| A IA faz | Só o dono faz |
|---|---|
| escreve código e testes por delta | **roda o portão** na máquina real |
| propõe decisões e registra as aprovadas | **decide** toda `Q-NN` (regra de negócio, rumo) |
| encontra e reporta defeitos com reprodução | migration em produção, deploy, `git push` |
| declara o que não sabe como lacuna | **fornece o dado** que só ele tem |

Se a IA decidiu uma regra de negócio, alguém errou o processo — não o modelo.

---

## 6. As perguntas que a equipe vai fazer

**"Isso não é burocracia demais para usar um assistente de código?"**
O ciclo inteiro são 7 passos e a maior parte é uma linha de texto. O que custa tempo é o
portão — e ele custa exatamente o tempo que você gastaria descobrindo o defeito depois, com
juros. Comece pelo modo curto: contexto → implementação → QA → entrega. **Pula-se fase, não se
pula regra.**

**"Por que não deixar a IA refazer o arquivo? É mais rápido."**
É mais rápido de pedir e mais lento de revisar. O diff grande não é lido por ninguém, e o
código que estava certo volta diferente. Foi o maior custo medido em dois projetos.

**"Preciso decorar os 24 agentes?"**
Não. No dia a dia você usa cinco ou seis. Os outros existem para quando o assunto aparece —
e é a `description` de cada um que dispara sozinha quando a tarefa combina.

**"Quanto tempo custa adotar num projeto que já existe?"**
Uma sessão com a skill `existing-project-adoption`, que lê o **código** (não a documentação) e
produz o contexto, o plano retroativo e a lista do que ninguém soube explicar. Ela não altera
nenhuma linha de código — mapear e consertar ao mesmo tempo produz o mapa do que você gostaria
que existisse.

**"E se eu esquecer um passo?"**
Boa parte é cobrada no commit pelo `check.py`: orçamento estourado, estado divergente, ID
citado que não existe, segredo versionado, link quebrado. O que ele não cobre está no
[[b_checklist|CHECKLIST]] — e essa parte é sua.

**"O portão automático pega tudo?"**
Não, e isso está medido: 18 checagens automáticas para 188 itens de checklist. Quem afirma que
o processo impede erro está vendendo. O que ele faz é tornar o erro **visível e rastreável**.

---

## 7. As frases que economizam uma sessão inteira

Cole na parede. Cada uma corta um problema específico antes de ele custar caro:

> "Isso passou no portão? Mostra o número."
> "Cadê o D-NN?"
> "Me manda só o delta."
> "Rodou na minha máquina ou no sandbox?"
> "Viu uma amostra real antes de escrever esse parser?"
> "Isso muda alguma decisão ou número?"
