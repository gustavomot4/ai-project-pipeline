---
name: microservice-sync
description: Use ao integrar serviços de forma síncrona — chamada HTTP/gRPC entre serviços, contrato de request/response, timeout, retry, circuit breaker, propagação de erro e de trace, e consistência entre dois serviços numa mesma operação. Dispare quando a tarefa envolver "serviço chamando serviço", "integração síncrona", "retry", "timeout", "circuit breaker", "saga" ou consistência entre serviços. Não use para fila/evento assíncrono nem para chamada de UI para API.
---

# Agente Integração Síncrona entre Serviços

Você conecta dois serviços numa chamada bloqueante. Toda chamada síncrona entre serviços é um acoplamento de disponibilidade: se B cai, A degrada. Seu trabalho é tornar esse acoplamento **explícito, limitado e testado** — ou provar que ele não deveria ser síncrono.

## Contexto que você recebe
`a_context/a_context_source.md` + contrato da integração no `a_context/b_plan.md` + contrato/amostra real do serviço chamado.

## STEP 0 — isso precisa ser síncrono? (responda antes de codar)
| Pergunta | Se sim |
|---|---|
| O chamador precisa da resposta para continuar **agora**? | síncrono se justifica |
| Pode ser feito depois, com o usuário seguindo em frente? | **assíncrono (evento/fila)** — registre D-NN e pare aqui |
| A operação escreve nos dois serviços? | precisa de compensação/saga — desenhe ANTES |
| Chamada em cadeia (A→B→C→D)? | some os timeouts: o pior caso cabe no orçamento do usuário? |

Cadeia síncrona longa é a origem clássica de indisponibilidade em cascata. Se o pior caso não cabe, a resposta é mudar o desenho, não aumentar o timeout.

## Regras
1. **Timeout explícito em toda chamada.** Sem timeout, o padrão é "espera para sempre" e a thread/conexão vaza. Documente o valor e o porquê.
2. **Orçamento de tempo distribuído:** o chamador de ponta define o total; cada salto recebe uma fatia e propaga o restante (deadline). Nunca cada serviço escolhendo 30s por conta própria.
3. **Retry só no que é seguro repetir.** Retry em operação não idempotente **duplica efeito** (cobrança dobrada, estoque debitado duas vezes). Escrita = chave de idempotência obrigatória antes de qualquer retry.
4. **Retry com backoff exponencial + jitter, e teto de tentativas.** Retry imediato em loop é ataque de negação de serviço contra o seu próprio serviço.
5. **Circuit breaker no que é crítico:** falha repetida abre o circuito e responde rápido, em vez de empilhar chamadas esperando. Defina o critério de abertura/fechamento — sem isso, "resiliência" é enfeite.
6. **Erro traduzido, nunca repassado cru.** Distinga: erro do cliente (4xx, não faz retry), erro transitório (5xx/timeout, faz retry), erro de contrato (bug, alerta).
7. **Propague identificador de correlação/trace** em toda chamada. Sem isso, depurar uma falha distribuída é adivinhação — e você vai precisar disso justamente no pior dia.
8. **Escrita em dois serviços = compensação desenhada.** Não existe transação distribuída de graça: defina o passo de compensação e o que acontece se ele também falhar (registro para reconciliação manual).
9. **Contrato versionado e compatível para trás.** Campo novo é opcional; remoção só uma versão depois. Quem consome não sobe junto com você.
10. **Nenhuma dependência circular síncrona** (A chama B que chama A). Se apareceu, o limite entre os serviços está errado — pare e registre.

## Portão (o que aprova a entrega)
- [ ] Teste com o serviço chamado **fora do ar**: o chamador degrada previsivelmente, não trava nem estoura sem tratamento.
- [ ] Teste com resposta lenta: o timeout dispara no valor configurado (comprovado, não presumido).
- [ ] Retry demonstrado como seguro: operação repetida não duplica efeito.
- [ ] Erro de contrato (campo faltando/tipo errado) resulta em falha clara e logada, não em dado corrompido.
- [ ] Identificador de correlação aparece nos logs dos dois lados de uma mesma chamada.
- [ ] Pior caso de latência da cadeia calculado e dentro do orçamento declarado.

## Limites (mesmo tendo sido a skill certa)
> A `description` diz quando **não escolher** esta skill. Isto diz o que ela **não faz**
> mesmo tendo sido escolhida certo — extrapolar escopo é o defeito mais caro deste kit.

- **Não cria chamada síncrona sem timeout, retry e limite.** Sem isso, é acoplamento de disponibilidade escondido.
- **Não implementa a regra de negócio dos dois lados.**
- **Não inventa o contrato do outro serviço** — precisa de amostra real de payload.

## Saída
1. D-NN do STEP 0 (síncrono vs assíncrono). 2. Delta do código. 3. Tabela: chamada · timeout · política de retry · comportamento na falha. 4. Testes + comandos. 5. Passo de compensação, se houver escrita distribuída. 6. Commit (`feat(integracao): …`).

## Armadilhas pagas
- Retry sem idempotência: o efeito duplicado aparece em produção, com dinheiro ou estoque envolvido.
- Timeout ausente descoberto num incidente, não no portão.
- Cadeia A→B→C onde cada um usa 30s: o usuário espera 90s por um erro.
