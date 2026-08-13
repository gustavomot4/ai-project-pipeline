---
tags: [auditoria, kit, medicao]
status: atual
data: 2026-08-13
---
# Avaliação de campo do kit v13.1 — primeiro projeto real

**O que é:** a primeira **medição** do kit contra um projeto construído com ele, por uma sessão
isolada que não trabalhou no projeto. Substitui nada do [[b_reference_case_spo|caso de
referência]] — que se declara "relato, não medição" — e existe para dar ao kit o que ele não
tinha: evidência de eficácia com número, e o custo junto.

**Projeto medido:** TAP GO v2 — jogo de disputa de pênaltis, SPA estática sem backend
(TypeScript + Vite + Phaser 3), online P2P por WebRTC, 9 módulos, 46 commits em 4 dias de
trabalho, 34 sessões registradas. Os agentes que o construíram **não sabiam** que era teste do
kit: é isso que torna a evidência honesta.

**Disciplina:** o critério de sucesso foi escrito, datado e hasheado
(`sha256 127735d7…fc84`, 2026-08-13T12:14:16Z) **antes** de qualquer arquivo do projeto ser
aberto. Nove hipóteses, cada uma com sinal de funcionando e de não funcionando, e quatro testes
de "atrapalhou", todos com limiar numérico fixado de antemão.

## O que passou

| | Hipótese | Número medido |
|---|---|---|
| H1 | a lista-morta impede re-proposta | **6 REJEITADOS** (15% das linhas vivas), nenhum reaparece |
| H2 | o orçamento segura | CONTEXT 95%, registro 91% — dentro, **no teto** |
| H3 | o portão é real | passa em HEAD · hook instalado · **3 de 3 sabotagens reprovadas** |
| H4 | pergunta sobe em vez de ser chutada | 11 `Q-NN`, **8 respondidas (73%)** |
| H5 | QA acha e fecha | 16 achados em 3 passagens, **4 dos 5 críticos fechados** |
| H6 | commit cita ID | **45 de 46 = 98%** (limiar era 50%) |
| H7 | delta, não regeneração | **~0%** — 3 candidatos, os 3 conferidos à mão, nenhum é reescrita |
| H8 | escopo contido | 12 de 13 commits de módulo no lugar · **24 recusas "regra 4"** |
| H9 | as skills pagam o custo | 9 das 24 com rastro (limiar 8) — **4 pela régua estrita** |

**A evidência que não é circular** (um kit que manda escrever `D-NN` sempre vai mostrar `D-NN`):
as sabotagens do portão; o cruzamento formal que apanhou o CONTEXT afirmando "Pronto, suíte
220/220" sobre código que não estava no git; a taxa de regeneração; e os defeitos deixados
**abertos de propósito** pela regra de escopo — que são custo, não benefício, mas provam que a
regra morde.

## O que não passou

**A checagem de ID enxergava 12% do que dizia enxergar.** `sem_codigo()` descartava o trecho
entre crases, e a casa escreve `` `D-13` ``: das 341 citações do projeto, **300 estavam entre
crases**. Corrigido no `kit v13.2` (`QA-14`), com isca por checagem para a classe inteira.
O canário que já existia escrevia o ID **sem** crases — passava, e a cegueira sobreviveu a uma
auditoria externa que citou o portão como ponto forte.

**O kit não se instrumentava.** Não havia registro de qual skill rodou em cada sessão, então
"qual dos 24 agentes paga o próprio custo" só tinha resposta `[suposto]`. Corrigido no
`kit v13.2`: o changelog passa a declarar `**Skill:**`, cobrado por aviso.

## O imposto, que fica declarado

- **15% das sessões (5 de 34)** foram administrar o orçamento do próprio registro, sem uma
  linha de produto.
- **43% dos commits** não tocam código.
- **9 defeitos conhecidos e abertos** pela regra de escopo, um deles de uma linha de CSS.
- **1 modo do produto parado 4 dias** esperando uma `Q-NN` do dono, e **2 questões com prazo
  estourado** que o próprio kit registrou e não cobrou.
- **1 retrabalho manual** causado pelo teto medir formatação — já corrigido no projeto.

## O veredito, e o defeito do instrumento

Pela **letra** do critério pré-registrado: **ATRAPALHOU** — a cláusula dizia "qualquer teste
T1–T4 disparado", e dois dispararam. Pela **evidência**: 9 de 9 hipóteses no lado positivo.

A régua estava errada, e isto fica escrito porque consertá-la em silêncio depois de ver o
resultado é o que invalida uma avaliação:

- **T3 não tinha controle de taxa-base.** Um canal de escalada que funciona sempre terá uma
  questão aberta e bloqueante em qualquer foto instantânea. O teste transformava o
  funcionamento normal de H4 em prova de fracasso; o certo seria medir a **taxa** (73%) e o
  tempo até a resposta.
- **T4 disparou num incidente que o kit detectou, mediu e corrigiu estruturalmente no mesmo
  dia.** O teste não distinguia "retrabalho induzido e absorvido" de "induzido e recorrente".

**Com a régua consertada e o conserto declarado: AJUDOU, com imposto medido.**

## O que esta medição NÃO prova

- **n = 1.** Um projeto, 4 dias, uma forma de aplicação, um dono. Ataca a falta de evidência;
  não a resolve.
- **Sem contrafactual.** Não existe o mesmo projeto sem o kit, então nenhuma afirmação sobre "o
  agente não teria feito isto sozinho" pode passar de `[derivado]`.
- **Fora do alcance de agente:** o projeto medido não tem teste automatizado de nenhuma tela —
  `vitest` roda em Node sem DOM. Isso é do dono e continua sendo.

## Como repetir

1. Escreva o critério **antes** de abrir o projeto, e guarde o hash.
2. Rode `task.py check-all`, conte `D-NN`/`Q-NN`/`QA-NN` das tabelas, e tire do `git log` a taxa
   de commits com ID e a de regeneração.
3. **Sabote o portão** numa cópia descartável: checagem que não reprova o próprio caso não é
   portão. Foi assim que o `QA-14` apareceu.
4. Some o imposto (sessões sem código, achados abertos, fila do dono) e publique junto.

> A segunda medição rende mais depois que o campo `**Skill:**` do `kit v13.2` acumular algumas
> sessões: ele só registra dali para a frente.
