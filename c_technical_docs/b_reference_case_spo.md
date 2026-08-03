---
tags: [exemplo, caso, referencia]
status: historico
---
# Caso de referência — app de estoque e vendas para uma loja

> **O que é isto:** o destilado de um projeto real construído com este pipeline. Não é o projeto (não há código nem documento copiado aqui).
> **⚠️ Status epistêmico — leia antes de citar qualquer número daqui.** Isto é **relato, não medição.** Nenhum dos números abaixo tem relatório, commit ou artefato anexado a este vault; eles vêm da memória de quem conduziu o projeto. Diferente de [[a_scb_usage_analysis_260722_0000|docs/ANALISE-USO-SCB]], que conta caracteres em arquivos que existem e marca as próprias suspeitas.
> **Use como:** lista de armadilhas plausíveis e referência de *formato* ao preencher [[a_context_source|CONTEXT]], [[c_decisions|DECISIONS]] e [[b_plan|PLANO]]. **Não use como** aferição de qualidade nem como argumento para decidir nada — número sem evidência não passa no portão do próprio kit (regra 5).

## O projeto em 5 linhas
App de gestão de estoque e vendas para uma loja de roupas com 1–2 funcionárias. Roda **local** na máquina da loja, sem nuvem e sem internet obrigatória. Operado por pessoa **não técnica**. Emite um comprovante não fiscal impresso em impressora térmica após cada venda. Fora do escopo, explicitamente: nota fiscal, nuvem, app mobile, cadastro de clientes e de fornecedores.

**Stack:** framework full-stack (front + API no mesmo repositório) · TypeScript estrito · ORM com migrations · banco embarcado em arquivo (com caminho de troca para banco de servidor) · CSS utilitário mobile-first · Docker.
**Forma:** monólito modular. Nunca houve motivo medido para distribuir — e o app entregou tudo.

## Números da entrega
| Marco | Número |
|---|---|
| Do início à validação do MVP com a cliente | ~10 dias |
| Passagens de revisão adversarial antes de entregar | **14** |
| Achados de QA registrados e corrigidos | **84** |
| Versões de schema até estabilizar | 6 (v1.0 → v2.5) — **o custo de não declarar as restrições do banco no dia 1** |
| Decisões registradas | 20, sendo **4 rejeições** (as rejeições evitaram retrabalho maior) |
| Resultado | MVP aprovado pela dona; evoluiu para atualização automática com rollback |

## As decisões que fizeram diferença
1. **Monólito modular, não microserviços.** Um repositório, um deploy, uma transação. Não faltou nada.
2. **Dinheiro em inteiro (centavos) e taxa em basis points**, desde a primeira migration. Nenhum centavo fantasma no fechamento.
3. **Autenticação proporcional ao uso real:** sem contas de usuário; um PIN protegendo **só** relatórios financeiros e configurações. O fluxo de venda ficou aberto.
4. **Comprovante como HTML com CSS de impressão** em vez de biblioteca de impressão — zero dependência, funciona no navegador da máquina com a impressora.
5. **Docker como artefato de distribuição** desde o MVP, com script de duplo clique para a usuária final.
6. **Atualização automática pull-based**: CI publica imagem no registry; a máquina da loja faz *pull* de versão pinada com backup → healthcheck → rollback automático. Substituiu o build na máquina do cliente.
7. **Migrations expand/contract** — obrigatório quando o deploy roda sozinho, sem ninguém olhando.

## As 4 rejeições (e o que as matou)
| Rejeitado | Motivo |
|---|---|
| App desktop nativo (Electron/Tauri) | não responsivo em celular, e sem caminho para nuvem depois |
| Backend e frontend em projetos separados | dois servidores e empacotamento complexo demais para o porte |
| Atualizador genérico de container de prateleira | não tinha o ciclo backup → healthcheck → rollback |
| Orquestrador de containers na máquina da loja | complexidade desproporcional ao problema |

Registrar a rejeição com o motivo é o que impediu a IA de re-propor cada uma delas nas sessões seguintes.

## As armadilhas que este projeto pagou (já viraram regra nas skills)
1. **Restrição do banco descoberta tarde** → 6 versões de schema em 7 dias. O banco embarcado não tinha enum nativo e tratava datas de forma traiçoeira. **Regra:** perfil da stack no CONTEXT antes do primeiro código.
2. **Segredo de sessão fixo no repositório** e **boot aceitando o valor de exemplo** — os dois achados mais graves das 14 passagens. **Regra:** segredo gerado por instalação; boot recusa iniciar com placeholder.
3. **Proteção no lugar errado:** exigir PIN na tela de vendas travava o caixa; a dona mandou remover. **Regra:** pergunte o que ele quer proteger antes de trancar o fluxo principal.
4. **Build na máquina do cliente:** lento, frágil, sem versão rastreável. **Regra:** publique imagem, consuma versão pinada.
5. **Documento descrevendo comportamento que o código não tinha** (dizia que a área ficava aberta; o código usava senha padrão). **Regra:** divergência doc × código é achado de QA.
6. **Fim de linha CRLF/LF** quebrando script dentro do container. **Regra:** normalize antes, não no debug.

## O que "pronto" significou aqui
Não foi "os testes passam". Foi:
- A dona da loja, **sem assistência**, cadastrou um produto com variações, registrou uma venda de vários itens, imprimiu o comprovante, consultou o estoque com os alertas e viu as vendas do dia.
- Zero achados críticos ou altos abertos, após 14 passagens adversariais **registradas**.
- Derrubar e subir o sistema preserva os dados; atualização falha volta sozinha para a versão anterior.
- Backup diário rodando, e um runbook dizendo o que fazer quando falha.

Se o seu projeto chega nesse ponto, ele está no mesmo nível. Para chegar **melhor**: comece já com as restrições da stack declaradas (economiza as 6 versões de schema), com o segredo gerado por instalação (economiza os dois achados críticos), e pergunte o que proteger antes de implementar acesso (economiza um ciclo inteiro de ida e volta).
