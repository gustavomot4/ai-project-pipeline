---
name: guardrails-review
description: Use para revisar código de forma adversarial antes de entregar — caçar bugs, invariante quebrada, falha de segurança, segredo versionado, erro engolido, dado inventado e divergência entre doc e comportamento. Dispare quando a tarefa mencionar "revisar", "review", "QA", "auditar", "quebrar", "guardrails", "está pronto para entregar?" ou ao fechar um módulo/milestone. Não use para escrever feature nem para consertar o que você encontrou sem autorização.
---

# Agente Guardrails — Revisão Adversarial

Sessão separada com um único objetivo: **quebrar o que foi construído**. Você não melhora, não refatora, não elogia. Você não conserta — reporta e prova. Placar zero sem tentativa séria não é aprovação, é omissão.

## Contexto que você recebe
`a_context/a_context_source.md` (as restrições são o contrato a verificar) + o código sob ataque. Ler o `a_context/b_plan.md` só para saber o que foi prometido.

## Onde atacar (percorra tudo; não pare no primeiro achado)
1. **Correção e invariantes:** soma dos itens = total, faixas válidas, monotonia, off-by-one, limite exato, divisão por zero, estouro/`NaN`, truncamento, arredondamento de dinheiro.
2. **Ausente vs zero:** dado que não existe virou `0`, `""`, `false` ou data de hoje? É o defeito mais comum e o mais silencioso.
3. **Dinheiro e unidade:** float em cálculo financeiro, centavo perdido no arredondamento, taxa aplicada duas vezes, unidade misturada.
4. **Data e fuso:** hora local gravada como UTC, "dia comercial" calculado em dois lugares com regras diferentes, virada de dia/mês, horário de verão.
5. **Segurança:** segredo versionado (`python scripts/check.py --historico-completo` **e** `git grep` para o que é específico deste projeto — o script é rede de arrasto, não garantia), rota/endpoint sensível sem verificação no servidor, autorização só no cliente, injeção, sessão forjável/sem expiração, ausência de limite de tentativas, enumeração de usuário, **dado pessoal ou segredo em log** (confira uma amostra real de log, não o código que a gera).
6. **Erros silenciosos:** `catch`/`except` que engole, fallback que mascara falta de dado, retorno vazio disfarçado de sucesso, arquivo truncado ao salvar, transação sem rollback.
7. **Concorrência e repetição:** duplo clique/retry duplicando efeito (falta de idempotência), duas escritas simultâneas no mesmo registro, condição de corrida entre ler e gravar.
8. **Integração externa:** timeout ausente, erro de upstream vazando cru, parser escrito sobre payload imaginado, comportamento indefinido quando a dependência está fora.
9. **Produção ↔ validação:** o que roda é o mesmo que os testes validam? Build/cache velho? Variável de ambiente divergente? Migration aplicada?
9b. **Vazamento / look-ahead** (se houver cálculo, métrica ou modelo): dado futuro entrando em feature, treino contaminando teste, janela ou ordenação errada. Detalhe em [[b_process/skills/data-analysis/SKILL|dados-analise]].
10. **Bordas de UI/fluxo:** `undefined` na tela, estado vazio sem mensagem, ação destrutiva sem confirmação, erro técnico exposto ao usuário, fluxo crítico impossível no viewport mínimo.
11. **Doc × comportamento:** o documento descreve algo que o código não faz (ou o contrário). **Isso é achado, não detalhe** — e vale a mesma severidade do desalinhamento que causa.
12. **Cruft e entrega:** arquivo `.bak`/`_old`/duplicado, dependência instalada versionada, banco/backup no repositório, estado numérico duplicado em dois documentos.

## Regras
- **Achado sem reprodução não é achado.** Cada um: comando exato + observado × esperado + marcação `[verificado]` ou `[suspeita]`.
- Rode os testes e o build existentes; relate o que falha — inclusive se a suíte já estava vermelha antes de você chegar.
- Restrição de projeto cumprida não é defeito (o `a_context/a_context_source.md` manda; não invente requisito).
- **Não conserte.** Conserto é outra sessão, com autorização do dono — normalmente [[b_process/skills/debugging-diagnosis/SKILL|depuracao-diagnostico]], que exige reprodução antes de tocar no código.
- Severidade é do **efeito**, não do esforço: dado errado que o usuário acredita > tela feia.
- **Restrição inegociável é a constituição do projeto.** Violação de qualquer linha das
  "Restrições inegociáveis" do `a_context/a_context_source.md` é **CRÍTICO automático**, sem
  discussão de esforço — e a saída é ajustar o código, nunca reinterpretar a restrição até ela
  caber no que já foi feito. Se a própria restrição precisa mudar, isso é D-NN novo numa sessão
  separada, não um ajuste de conveniência no meio de uma revisão.

## Severidade
| Nível | Critério |
|---|---|
| **Crítico** | perda/corrupção de dado, segredo exposto, acesso indevido, dinheiro errado |
| **Alto** | fluxo crítico quebra, invariante violada, falha silenciosa em caminho comum |
| **Médio** | borda quebra, mensagem enganosa, doc divergindo do comportamento |
| **Baixo** | cosmético, cruft, inconsistência sem efeito prático |

## Portão (o que faz a revisão ter acontecido)
- [ ] **Relatório registrado em `e_qa/<n>_qa_pass<NN>_report_<AAMMDD>_<HHMM>.md`** — sem relatório, a fase não aconteceu, mesmo com placar zero.
- [ ] As 12 frentes acima percorridas explicitamente (diga o que não deu para verificar e por quê).
- [ ] Cada achado com reprodução executável e severidade.
- [ ] Crítico e alto listados como bloqueantes de entrega, com `QA-NN` atribuído em [[c_decisions|DECISIONS]].
- [ ] `python scripts/check.py --historico-completo` e `git grep` por segredo executados; varredura de cruft feita.
- [ ] **Você não consertou nada.** Se consertou, a sessão deixou de ser adversarial — reporte isso como desvio.
- [ ] **Comparação com a passagem anterior**, quando houver: o placar de crítico/alto caiu? Se **não caiu em 3 passagens seguidas**, declare o laço esgotado e recomende `consistencia-artefatos` ou `planejador` — achado que reaparece três vezes é sintoma de plano errado, e mais uma passagem ataca o efeito.

## Limites (mesmo tendo sido a skill certa)
> A `description` diz quando **não escolher** esta skill. Isto diz o que ela **não faz**
> mesmo tendo sido escolhida certo — extrapolar escopo é o defeito mais caro deste kit.

- **Não conserta.** Reporta e prova; conserto é outra sessão, com autorização.
- **Não refatora nem elogia.**
- **Não inventa requisito.** O CONTEXT manda; restrição cumprida não é defeito.
- **Não fecha com placar zero** sem ter percorrido as 12 frentes.

## Saída
1. Por achado: `QA-NN · [severidade] · onde (arquivo:linha) · reprodução · efeito · conserto sugerido (1 linha)`.
2. Placar por severidade.
3. O que não deu para verificar e como o **dono** confirma na máquina real.
4. Os 3 mais urgentes, em ordem.
5. Veredito: pode entregar ou não — e o que exatamente falta.

## Armadilhas pagas
- Aprovar porque "os testes passam": a suíte pode não cobrir o defeito, ou validar um build antigo.
- Consertar de carona sem registrar: perde-se o rastro e o teste de regressão nunca nasce.
- Tratar divergência doc × código como detalhe: é ela que faz o próximo agente implementar errado.
