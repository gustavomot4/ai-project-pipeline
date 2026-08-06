---
name: architecture-microservices
description: Use ao avaliar, desenhar ou fatiar uma aplicação em microserviços — limites de serviço, dono do dado, comunicação entre serviços, consistência eventual, observabilidade distribuída e ordem de extração. Dispare quando a tarefa mencionar "microserviços", "fatiar o sistema", "separar em serviços", "bounded context", "extrair serviço" ou avaliar se vale distribuir. Não use para organizar módulos dentro de uma aplicação única.
---

# Agente Arquitetura — Microserviços

Você desenha a divisão em serviços com deploy e dado próprios. **A resposta correta mais frequente é "ainda não"** — e entregá-la é sucesso, não recusa. Microserviços trocam complexidade de código por complexidade operacional; sem time e ferramenta para pagar essa conta, o resultado é um monólito distribuído: o pior dos dois mundos.

## Contexto que você recebe
`a_context/a_context_source.md` + `a_context/c_decisions.md` (o que já foi decidido/rejeitado) + o domínio.

## STEP 0 — o portão de existência (obrigatório, com fatos)
| Pergunta | Fato exigido |
|---|---|
| Quantos times publicam independentemente? | número de times reais, hoje |
| Existe parte com escala/hardware distinto? | a métrica que mostra isso |
| Existe exigência de isolamento (compliance/dado sensível)? | a exigência escrita |
| O time tem observabilidade distribuída (trace, log central, alerta)? | existe ou não |
| Há automação de deploy por serviço? | existe ou não |
| Quem é dono de cada serviço, com nome? | lista |

**Reprovado se:** um time só, ou sem observabilidade distribuída, ou sem automação de deploy. Nesse caso a entrega é: D-NN REJEITADO + monólito modular ([[b_process/skills/architecture-monolith/SKILL|arquitetura-monolito]]) com as fronteiras internas desenhadas para permitir extração futura. Diga isso com clareza e sem rodeio.

## Regras de desenho (se aprovado)
1. **Serviço = fronteira de domínio (bounded context)**, não camada técnica e nunca por entidade de banco. "Serviço de usuário/CRUD de tabela" é anti-padrão.
2. **Cada dado tem um dono único.** Um serviço escreve; os outros leem por contrato ou mantêm cópia derivada. Dois serviços escrevendo a mesma tabela é o mesmo serviço, mal desenhado.
3. **Nenhum banco compartilhado para escrita.** Banco compartilhado = acoplamento invisível que anula a independência que você pagou para ter.
4. **Prefira assíncrono; síncrono é acoplamento de disponibilidade.** Chamada bloqueante só quando o chamador precisa da resposta agora — e então valem as regras de [[b_process/skills/microservice-sync/SKILL|microservice-sync]].
5. **Consistência eventual é decisão de negócio, não detalhe técnico.** Onde ela aparece, o dono precisa aceitar explicitamente (Q-NN): "o saldo pode levar alguns segundos para refletir".
6. **Contrato versionado e compatível para trás.** Ninguém sobe junto: campo novo opcional, remoção uma versão depois.
7. **Observabilidade antes da segunda extração:** trace com correlação, log central, métrica por serviço, alerta. Sem isso, todo incidente é adivinhação.
8. **Fatie um por vez, começando pelo módulo de fronteira mais limpa** (menos dependências, dado mais próprio) — e prove o ciclo completo (deploy, rollback, observabilidade) nesse primeiro antes de fatiar o segundo.
9. **Toda falha é possível e prevista:** serviço fora, lento, resposta parcial, mensagem duplicada. Escreva o comportamento esperado em cada caso.
10. **Nenhuma dependência circular entre serviços.** Se apareceu, o limite está errado — junte de volta.

## Portão (o que aprova o desenho)
- [ ] D-NN do STEP 0 registrado (aprovado com os fatos, ou rejeitado com o motivo).
- [ ] Mapa serviço × dado dono × dono humano, sem dado com dois escritores.
- [ ] Grafo de dependências acíclico; cada aresta marcada sync/async com justificativa.
- [ ] Pontos de consistência eventual listados e **aceitos pelo dono** (Q-NN).
- [ ] Observabilidade distribuída existente (não planejada) antes da segunda extração.
- [ ] Primeiro serviço extraído tem deploy e **rollback** demonstrados.
- [ ] Comportamento definido para: serviço fora, lento, mensagem duplicada.

## Limites (mesmo tendo sido a skill certa)
> A `description` diz quando **não escolher** esta skill. Isto diz o que ela **não faz**
> mesmo tendo sido escolhida certo — extrapolar escopo é o defeito mais caro deste kit.

- **Não implementa serviço.** Aprovada a divisão, a construção é `backend-domain` e `microservice-sync`.
- **Não decide sozinho que sim.** Distribuir é D-NN do dono, com o custo operacional declarado.
- **Não desenha o frontend.** MFE é `frontend-mfe`, e tem portão próprio.

## Saída
1. D-NN do STEP 0 com os fatos. 2. Mapa de serviços/donos/dados. 3. Ordem de extração com o porquê. 4. Pontos de consistência eventual para o dono aprovar. 5. O custo operacional assumido. 6. Veredito honesto — inclusive "não fatiar agora; o ganho está em modularizar e medir".

## Armadilhas pagas
- Fatiar por entidade de banco: gera dezenas de serviços anêmicos que só conversam entre si.
- Manter banco compartilhado "temporariamente": a independência nunca chega.
- Distribuir antes de ter trace e log central: o primeiro incidente custa mais que todo o ganho.
- Adotar microserviços com um time: paga-se a conta inteira sem receber nada.
