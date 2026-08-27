---
tags: [auditoria, kit, medicao, criterio]
status: RASCUNHO — não congelado
data: 2026-08-27
---
# Critério de conclusão do TAP GO — o que decide se o kit fica ou morre

**Estado: RASCUNHO.** Ele só vale depois de você revisar os limiares e o documento ser
hasheado (comando no fim). Enquanto não houver hash, isto é opinião — não critério.

**Para que serve.** No fim do TAP GO você vai olhar um monte de número e decidir se o kit
valeu. Se o critério for escrito naquele momento, você vai escolher — sem má-fé, todo mundo
faz — os números que confirmam o que já quer. Este documento existe para tirar essa escolha
de você, escrevendo **agora** o que conta como sucesso, o que conta como fracasso, e o que
te faria abandonar o kit.

Mesma disciplina da [[c_field_evaluation_tapgo_260813|avaliação de campo de 13/08]]
(hash `127735d7…`, nove hipóteses com limiar fixado antes dos dados) — com uma diferença:
lá o critério media **mecanismos**; aqui ele precisa medir **valor**, e para isso a
seção 3 é obrigatória.

---

## 0. A regra do jogo (vale contra você)

1. **Limiar não se renegocia.** Um número que ficou a 2% do limiar é um número que não
   bateu. Se ficar tentado a "arredondar", releia esta linha.
2. **Dado que não existe reprova por falta de dado** — não vira "provavelmente estava ok".
3. **Ninguém edita este arquivo depois do hash.** Correção necessária = arquivo novo,
   datado, dizendo o que mudou e por quê. O hash antigo fica.
4. **A conclusão é escrita antes de olhar a seção 3.** Você responde H1–H9 primeiro, escreve
   o veredito parcial, e só então abre o resultado do recorte de controle. Sem isso, o
   controle vira validação do que você já concluiu.

---

## 1. A pergunta que este documento responde — e a que ele não responde

**Não responde:** "o kit fez o TAP GO ficar pronto mais rápido / melhor?" Isso exigiria o
mesmo projeto construído sem ele, e ele não existe. Nenhum número aqui vai responder isso, e
qualquer frase final que sugira o contrário é desonesta.

**Responde três coisas, e elas bastam para decidir:**
- **os mecanismos morderam?** (H1–H5) — falsificável, medido pelo `evidencia`;
- **quanto custaram?** (H6–H9) — também medido;
- **num recorte pareado dentro do próprio projeto, o trabalho feito com o kit saiu melhor
  que o feito sem?** (seção 3) — o único pedaço que fala de valor, com n pequeno e dito
  como tal.

---

## 2. As hipóteses, com limiar fixado agora

Cada uma tem o sinal de que **funcionou** e o de que **não funcionou**. Fonte: saída de
`python scripts/task.py evidencia` no fim do projeto, salva em `e_qa/`.

| # | Hipótese | Passa se | Reprova se |
|---|---|---|---|
| **H1** | A lista-morta impede re-proposta | ≥ 12 `D-NN` REJEITADOS **e** nenhum rejeitado reaparecendo depois como adotado sem `SUPERSEDE` | rejeitadas < 8% das decisões, ou um rejeitado voltando sem registro |
| **H2** | O portão pega o que o humano não pegaria | ≥ 5 `QA-NN` com **origem = portão** (campo novo, seção 4) | 0 achados de origem "portão" — nesse caso o portão só cobra formato |
| **H3** | O orçamento segura | no máximo **1** elevação de teto até o fim, registrada em `D-NN`, e nenhum registro acima do teto no último commit | 2+ elevações, ou registro estourado no fim — orçamento que cede sob pressão é lembrete |
| **H4** | A pergunta sobe em vez de ser chutada | ≥ 20 `Q-NN` com ≥ 70% respondidas, e nenhuma aberta há mais de 30 dias no encerramento | < 50% respondidas — fila que o dono não atende não é fila, é depósito |
| **H5** | Delta, não regeneração | 0 reescritas integrais dos arquivos de estado | qualquer reescrita integral não justificada |
| **H6** | Commit rastreável | ≥ 80% dos commits citam um ID | < 65% |
| **H7** | O processo não come o produto | commits que **só** tocam processo ≤ **45%** no período pós-atualização, e a série temporal mostrando queda | > 55%, ou subindo com o projeto — hoje o número é **61,5%** |
| **H8** | As skills pagam o próprio custo | ≥ 14 das 24 com rastro no changelog | < 10 — catálogo que não dispara é superfície não testada |
| **H9** | O portão não é contornado | ≤ 5% dos commits com `SEM-PORTAO:`, todos com motivo legível | > 10%, ou marcador usado como carimbo sem motivo real |

**H7 é o mais importante desta tabela** e é o mais provável de reprovar. Ele é a versão
medida da crítica que o benchmarking fez ao BMAD e ao Spec Kit — e que se aplicava a nós.

---

## 3. O recorte de controle — a única parte que fala de valor

Sem isto, o resto é "o kit foi usado", não "o kit ajudou".

**Desenho, a ser fixado ANTES de executar:**
- escolha **6 tarefas** de tamanho parecido (mesma ordem de grandeza de arquivos tocados),
  ainda não iniciadas, e liste os IDs aqui embaixo antes de começar qualquer uma;
- **3 com o kit inteiro**, **3 sem nada dele**: agente sem `CLAUDE.md` do kit, sem skills,
  sem registro, sem portão — só o repositório e o pedido;
- alterne (A-B-A-B-A-B) para não concentrar as fáceis de um lado;
- mesmo modelo, mesma pessoa, mesma janela de trabalho.

**O que se mede em cada uma:**

| Medida | Como |
|---|---|
| retrabalho | commits de correção sobre a mesma tarefa nos 7 dias seguintes |
| defeito posterior | `QA-NN` abertos depois, apontando para os arquivos daquela tarefa |
| tempo de sessão | do primeiro ao último commit da tarefa |
| custo em tokens | o que a ferramenta reportar por sessão |

**Tarefas escolhidas (preencher antes de executar):**

| Tarefa | Braço | Iniciada em |
|---|---|---|
| T-__ | com kit | |
| T-__ | sem kit | |
| T-__ | com kit | |
| T-__ | sem kit | |
| T-__ | com kit | |
| T-__ | sem kit | |

**Limiar:** o braço "com kit" precisa mostrar **menos retrabalho ou menos defeito
posterior** em pelo menos 2 das 3 comparações pareadas. Empate conta como derrota do kit —
porque o kit tem custo, e custo empatado é custo perdido.

**Honestidade obrigatória no relatório final:** n=6 tarefas, um operador, sem cegamento. Isso
é indício, não prova. Escreva essa frase junto do resultado, qualquer que ele seja.

---

## 4. O que precisa existir até o fim (instrumentação)

Sem estes quatro, metade da tabela acima não pode ser respondida:

1. **Kit atualizado no projeto** (v13.1 → v13.10) — sem isso não há `evidencia`, nem contagem
   de pulos, nem prazo por gravidade, e o portão continua com a cegueira do `QA-14`.
2. **Campo `origem` em cada `QA-NN` novo**: `portão` · `revisão` · `dono` · `usuário`.
   É o que torna H2 respondível — e é o número menos circular que este projeto pode produzir.
3. **Série temporal, não foto**: a cada marco,
   `python scripts/task.py evidencia --json > e_qa/evidencia_AAMMDD.json`, commitado.
   H7 depende de ver a tendência, não o número final.
4. **O recorte de controle registrado antes de rodar** (tabela da seção 3 preenchida).

---

## 5. O que me faria ABANDONAR o kit

Escrito antes dos dados de propósito. Se nenhuma destas linhas puder acontecer, este
documento não é uma avaliação — é uma cerimônia.

- **Abandono total:** o recorte de controle não mostrar vantagem em 2 das 3 comparações
  **e** H7 reprovar (> 55% de commits só-processo). Seria a demonstração de que o kit cobra
  caro e não entrega diferença observável.
- **Redução ao núcleo:** H2 reprovar (nenhum achado de origem "portão") **ou** H8 reprovar
  (< 10 skills com rastro). Nesse caso sobrevivem só o registro de decisões com rejeições e
  o portão de commit; o resto do processo sai.
- **Morte da tese do orçamento:** H3 reprovar. Se o teto cede sempre que aperta, a economia
  de contexto vira slogan e deve sair da documentação do kit — inclusive do benchmarking.
- **Troca por peças de prateleira:** se o experimento da pilha clássica (Claude Code +
  `AGENTS.md` + `pre-commit` + MADR) replicar as duas forças em uma tarde. Não depende do
  TAP GO, mas entra no mesmo veredito.

---

## 6. A pergunta final, respondida por último e por escrito

> **Você começaria o próximo projeto com este kit — sabendo tudo o que sabe agora?**

Três respostas admitidas, escolhidas depois de tudo acima: **sim, inteiro** · **sim, só o
núcleo** · **não**. Sem "depende" e sem "sim, com ajustes" — se couber ajuste, ele é parte
do núcleo ou não é.

---

## Para congelar

Revise os limiares (são meus, não seus — mexa à vontade **agora**). Depois:

```
python -c "import hashlib,pathlib;p=pathlib.Path('docs/f_criterio_conclusao_tapgo_260827.md');print(hashlib.sha256(p.read_bytes()).hexdigest())"
```

Troque `status: RASCUNHO — não congelado` por `status: CONGELADO`, cole o hash e a data/hora
UTC aqui embaixo, e commite. A partir daí, os limiares são fatos.

- **SHA-256:** _(preencher ao congelar)_
- **Congelado em:** _(preencher ao congelar)_
