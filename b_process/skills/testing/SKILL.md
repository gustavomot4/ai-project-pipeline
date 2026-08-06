---
name: testing
description: Use ao escrever, organizar ou consertar testes — teste unitário de regra e borda, teste de integração, teste de sistema ponta a ponta do fluxo crítico, dado de teste, dublês (mock/stub), teste de regressão de bug e teste instável (flaky). Dispare quando a tarefa mencionar "teste", "testar", "cobertura", "unitário", "e2e", "integração", "mock", "flaky" ou pedir prova de que algo funciona. Não use para caçar bugs em código existente — isso é guardrails-review.
---

# Agente de Testes — Unitário e de Sistema

Você produz a evidência de que o comportamento é o esperado. Regra de ouro deste kit: **sem teste, a entrega não existe** — e um teste que nunca falharia não é teste.

## Contexto que você recebe
`a_context/a_context_source.md` (as restrições e o critério de aceite são o que você verifica) + o módulo sob teste + seu contrato.

## Duas camadas, dois propósitos
| Camada | Verifica | Custo | Regra |
|---|---|---|---|
| **Unitário** | regra de negócio e bordas, isolado | baixo | é onde mora a maior parte dos testes; roda em segundos |
| **Sistema (ponta a ponta)** | o fluxo crítico funciona junto, de verdade | alto | poucos, sobre os fluxos que dão dinheiro/valor; sem dublê no caminho principal |

Integração fica no meio: verifica a borda com o mundo real (banco, HTTP) usando o componente de verdade, não um dublê.

## Regras
1. **Comece pelo teste que falha.** Escreva o caso, veja falhar, então implemente. Teste escrito depois, que já passa de primeira, frequentemente não testa nada.
2. **Bordas obrigatórias em toda regra:** vazio · zero · negativo · ausente/nulo · desconhecido · divisão por zero · limite exato (e limite ± 1) · duplicado · maior/menor valor plausível. **Ausente ≠ zero** — teste os dois separados.
3. **Invariante do domínio tem teste próprio:** soma dos itens = total, estoque nunca negativo, saldo não muda por leitura, data não retrocede. Invariante é o que o usuário considera "o sistema está certo".
4. **Todo bug corrigido nasce com um teste de regressão** que falharia antes da correção, citando o ID (`QA-NN`). É assim que o bug não volta.
5. **Teste determinístico:** semente fixa em aleatoriedade, tempo injetado (nunca `now()` real no assert), ordenação explícita, sem dependência da ordem de execução entre testes.
6. **Nada de rede real no teste automatizado.** Dependência externa entra por dublê construído a partir de **amostra real** do payload — dublê inventado testa a sua imaginação.
7. **Um assert conceitual por teste**, com nome que descreve o comportamento: `venda_com_desconto_maior_que_subtotal_e_rejeitada`. Nome ruim é teste que ninguém conserta depois.
8. **Fluxo crítico tem teste de sistema ponta a ponta**, exercitando o caminho real do usuário (entrada → persistência → saída visível). Um por fluxo que gera valor.
9. **Cobertura é diagnóstico, não meta.** Perseguir porcentagem gera teste que executa linha sem verificar nada. Pergunte: "que bug este teste pegaria?" Se não houver resposta, apague.
10. **Teste instável é bug de teste, com prazo.** Conserte ou remova — nunca "roda de novo até passar". Suíte em que ninguém confia é pior que suíte inexistente.
11. **Dado de teste é construído no teste** (fábrica/builder), não depende de banco pré-populado nem de ordem de execução. Cada teste limpa o que criou.
12. **O portão roda na máquina do dono.** Sua execução no sandbox é indicativa. Termine dizendo o comando exato dele.

## Portão (o que aprova a entrega)
- [ ] Suíte verde na máquina do dono, com o comando declarado.
- [ ] Cada regra nova tem teste de caminho feliz **e** de borda (lista acima percorrida).
- [ ] Cada invariante do domínio tem teste próprio.
- [ ] Fluxo crítico coberto ponta a ponta, sem dublê no caminho principal.
- [ ] Cada `QA-NN` corrigido tem teste de regressão que falha na versão antiga.
- [ ] Suíte roda duas vezes seguidas com o mesmo resultado e em ordem alterada.
- [ ] Nenhum teste depende de rede, de horário do dia ou de estado deixado por outro teste.

## Limites (mesmo tendo sido a skill certa)
> A `description` diz quando **não escolher** esta skill. Isto diz o que ela **não faz**
> mesmo tendo sido escolhida certo — extrapolar escopo é o defeito mais caro deste kit.

- **Não altera o código sob teste para o teste passar.** Se precisa mudar, é `QA-NN` ou outra sessão.
- **Não escreve teste que nunca falharia.**
- **Não deixa teste instável passar** — flaky que ninguém encara vira suíte ignorada.

## Saída
1. Testes (arquivo novo pode vir inteiro). 2. Comando exato para o dono rodar. 3. Tabela caso → o que ele pega. 4. **O que NÃO está coberto e por quê** (declare a lacuna; não maquie). 5. Testes que exigem ambiente real e como o dono verifica à mão. 6. Commit (`test(escopo): …`).

## Armadilhas pagas
- Teste escrito depois só para "ter teste": passa sempre e não pega nada.
- `now()` real no assert: quebra na virada do dia, do mês ou do fuso.
- Dublê inventado sem amostra real: o teste passa e a integração falha em produção.
- Perseguir cobertura: números altos com suíte que não pega bug nenhum.
