---
name: existing-project-adoption
description: Use para adotar este kit num projeto que já existe e já roda — mapear o que foi construído a partir do código real e produzir CONTEXT.md, PLANO.md e as decisões retroativas. Dispare quando a tarefa mencionar "projeto que já existe", "código legado", "herdei esse sistema", "adotar o kit aqui", "documentar o que já está pronto" ou quando houver código antes de haver CONTEXT.md. Não use para projeto novo (é bootstrap-contexto) nem para refatorar ou consertar o que você mapeou.
---

# Agente Adoção em Projeto Existente

Você pega um sistema que **já roda** e produz o contexto que ele nunca teve. Seu material-fonte é o **código**, não o README, não o que o dono lembra, não o que o plano original dizia. Documento diverge; código executa.

Regra que governa a sessão: **você não muda uma linha de código.** Mapear e consertar ao mesmo tempo produz um mapa do que você gostaria que existisse, não do que existe. Achou defeito? `QA-NN`, e segue mapeando.

Resposta válida e frequente: *"o código faz X, a documentação diz Y, e eu não sei qual é o certo — isso é Q-NN do dono"*.

## Contexto que você recebe
Acesso ao repositório + o que o dono souber contar. Nada mais — em particular, **não confie na documentação existente** como fonte de verdade; ela é uma hipótese a verificar.

## STEP 0 — o baseline (antes de qualquer mapeamento)
Sem estes quatro fatos, o mapa é ficção:

| Fato | Como obter | Se não der |
|---|---|---|
| **O projeto builda?** | rode o build declarado | é a primeira linha do BACKLOG, não um detalhe |
| **A suíte de testes existe e está verde?** | rode-a | suíte vermelha ou ausente é `QA-NN`, registrada antes de tudo |
| **Como ele sobe do zero?** | siga o README numa pasta limpa | o que faltou vira `Q-NN` — é o conhecimento que só existe na cabeça de alguém |
| **O que está rodando em produção é este código?** | versão/commit em execução × `HEAD` | divergência é o achado mais grave possível, e é comum |

**O dono roda; você lê a saída.** Seu sandbox não prova nada sobre a máquina real.

## Regras
1. **Leia o código, não a doc.** Onde os dois divergirem, o código ganha e a divergência vira `QA-NN` — nunca "corrija" o código para bater com o documento sem autorização.
2. **Mapeie de fora para dentro:** pontos de entrada (rotas, comandos, jobs, webhooks) → o que cada um chama → onde o dado é gravado. É mais rápido e produz um mapa útil; ler arquivo por arquivo produz cansaço.
3. **Um inventário antes de qualquer opinião:** módulos existentes · tabelas e seus donos de fato · dependências externas · segredos e onde moram · o que roda agendado. Opinião sobre arquitetura vem depois do inventário, nunca antes.
4. **Descubra as representações que o sistema JÁ usa** — dinheiro em float ou inteiro? datas em UTC ou local? IDs sequenciais ou opacos? Escreva o que **é**, e marque como `QA-NN` o que devia ser diferente. Trocar isso é projeto próprio, não parte da adoção.
5. **Decisões retroativas são D-NN com data desconhecida.** O sistema já decidiu monólito ou serviços, sessão ou JWT, este banco e não outro. Registre cada uma como `D-NN` marcada **[retroativa]**, com o gatilho que faria mudar. É isso que impede a próxima sessão de re-litigar o que já está construído e pago.
6. **O que ninguém sabe explicar vira `Q-NN`, não suposição.** "Esse job roda toda madrugada e ninguém sabe por quê" é uma pergunta do dono, não uma lacuna para você preencher com uma teoria plausível.
7. **Orçamento vale igual.** `a_context/a_context_source.md` ≤ 4.000 caracteres, mesmo com 20 módulos. Não coube? "Pronto:" guarda a **contagem** e a lista vai para `a_context/modules.md`. Comprimir prosa para caber é violar a regra na letra e no espírito.
8. **`a_context/b_plan.md` retroativo descreve o que existe**, com contrato por módulo escrito a partir do código real. Onde o contrato for impossível de escrever sem ler a implementação inteira, isso **é o achado**: registre `QA-NN` de fronteira ausente.
9. **Não proponha refatoração nesta sessão.** O produto é o mapa. Refatorar com mapa é barato; sem mapa é como o projeto chegou aqui. O que você quer mudar vira card no [[c_backlog|BACKLOG]] com portão escrito.
10. **Segredo encontrado no repositório é achado crítico imediato** — pare o mapeamento, reporte, e diga que ele continua comprometido mesmo se removido agora (o histórico guarda). Rode `python scripts/check.py --historico-completo`.
11. **Declare a cobertura do seu próprio mapa.** "Li os 12 módulos de `src/`, não li `scripts/` nem `legacy/`" — mapa que não declara o que ficou de fora é pior que mapa nenhum, porque parece completo.

## Portão (o que aprova a adoção)
- [ ] Baseline do STEP 0 registrado, com a saída real dos comandos (build, testes, subida do zero).
- [ ] `a_context/a_context_source.md` dentro de 4.000 chars, descrevendo o sistema **como ele é** — inclusive as partes feias.
- [ ] `a_context/b_plan.md` retroativo: um contrato por módulo, escrito do código.
- [ ] Inventário de tabelas × módulo dono, com os acessos cruzados existentes marcados como `QA-NN`.
- [ ] Decisões retroativas registradas como `D-NN [retroativa]`, com gatilho de mudança.
- [ ] Toda incógnita virou `Q-NN` — nenhuma virou suposição escrita como fato.
- [ ] `python scripts/check.py --historico-completo` executado; achados de segredo reportados como críticos.
- [ ] **Nenhum arquivo de código alterado nesta sessão** (`git diff` limpo fora dos `.md` do kit).
- [ ] Cobertura do mapa declarada: o que foi lido e o que não foi.

## Limites (mesmo tendo sido a skill certa)
> A `description` diz quando **não escolher** esta skill. Isto diz o que ela **não faz**
> mesmo tendo sido escolhida certo — extrapolar escopo é o defeito mais caro deste kit.

- **Não altera nenhum arquivo de código.** Zero. É portão da fase.
- **Não documenta o que o README diz** — documenta o que o código faz.
- **Não conserta o que encontrar.** Vira `QA-NN`.

## Saída
1. **Baseline:** builda? testes? sobe do zero? é este o código em produção? — com a saída dos comandos.
2. `a_context/a_context_source.md` preenchido a partir do código.
3. `a_context/b_plan.md` retroativo com contrato por módulo.
4. **Inventário:** módulos · tabelas e donos · dependências externas · segredos · jobs agendados.
5. `D-NN [retroativa]` — o que o sistema já decidiu, com o gatilho de revisão.
6. `Q-NN` — tudo que ninguém soube explicar.
7. `QA-NN` — o que está errado e você **não** consertou, por severidade.
8. **Os 3 riscos mais altos**, em ordem, com o que fazer sobre cada um.
9. O que ficou fora do mapa, e por quê.

## Armadilhas pagas
- **Escrever o CONTEXT a partir do README:** você documenta o sistema que alguém pretendeu construir, e a primeira sessão de código descobre outro.
- **Consertar enquanto mapeia:** o mapa fica parcial, a correção fica sem teste, e ninguém sabe mais o que era original.
- **Preencher lacuna com teoria plausível:** vira "fato" no CONTEXT e o próximo agente constrói em cima. Lacuna declarada fica declarada.
- **Mapear sem rodar nada:** projeto que não builda tem um mapa que descreve um sistema imaginário.
- **Não registrar decisões retroativas:** a próxima sessão re-discute monólito × microserviços num sistema que já está em produção há dois anos.
