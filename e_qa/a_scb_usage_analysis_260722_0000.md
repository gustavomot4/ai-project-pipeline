---
tags: [analise, kit, evidencia]
status: historico
data: 2026-07-22
---
# Análise do uso do kit no SCB — evidências para a v2

**Data:** 2026-07-22 · **Método:** leitura completa do kit v1 (568 linhas) e do vault SCB de 21/07 (docs, 40 decisões, changelog, código). Tamanhos medidos nos arquivos reais (caracteres; tokens ≈ chars/3 em PT-BR). Nada abaixo é opinião sem arquivo ou número citado.

## Veredito
O núcleo do kit está **validado na prática**: portão objetivo, D-NN append-only, delta e QA-NN funcionaram exatamente como projetados. Mas o kit **falhou na sua promessa central — economia de tokens**: os dois arquivos mais carregados (CONTEXT e DECISIONS) incharam *dentro das regras*, os 6 prompts foram 100% reescritos pelo projeto por serem prolixos, e o estado se espalhou por 4 arquivos e divergiu. O projeto SCB é bom; várias das melhores práticas dele **não vieram do kit** — foram inventadas no caminho. A v2 absorve essas invenções e corrige as falhas com regras mensuráveis.

## O que funcionou (mantido na v2)
| Mecanismo | Evidência no SCB |
|---|---|
| Portão objetivo (IC que não cruza zero etc.) | 9+ gates de evolução: 2–3 adoções, ~7 rejeições, todas com números (D-19..D-33). O portão barrou ideias plausíveis-mas-inúteis — inclusive 2 ângulos de SoT antes do 3º passar. |
| D-NN append-only | 40 decisões em 7 dias; reversão registrada sem apagar (D-40, artilharia construída e cortada); sessões retomadas sem re-litigar. |
| QA-NN citado em commit | QA-01..QA-10 rastreados. |
| Delta / port em vez de reescrita | D-02; disciplina citada em todos os docs do projeto. |
| Lacuna declarada, nunca inventada | Sustentada sob pressão: stats do BRA ausentes → 2ª fonte real (D-34), não chute. |
| CHANGELOG fora do contexto | 173 linhas que nenhuma sessão pagou. Funcionou como desenhado. |

## O que falhou (com número)

**1. "≤ 1 página" sem número virou parede de prosa.** O "Estado atual" do SCB tem **1.930 caracteres (~640 tokens) num único parágrafo** com 15+ referências a D-NN — relido em TODA sessão, ilegível para humano e redundante com DECISIONS.md. A regra foi cumprida na letra e violada no espírito: "1 página" não é um limite, é um convite à compressão. → *v2: orçamento de 4.000 chars no arquivo inteiro, estado em 6 bullets de formato fixo, validado por `scripts/checar.py`.*

**2. DECISIONS.md sem teto + Fase 5 carrega ele inteiro.** "Uma linha por decisão" não sobreviveu ao primeiro contato: D-32 tem ~350 palavras (3 ângulos testados, ICs, recomendação). O arquivo chegou a **23.101 chars (~7.700 tokens)** — pagos integralmente em cada sessão de evolução, o maior custo recorrente do sistema. A necessidade é real (a evidência importa); o lugar é que estava errado. → *v2: linha ≤ 2 frases + evidência longa em `dev/<slug>.md` linkada.*

**3. Estado espalhado em 4 lugares → divergiu de verdade.** Versão/métricas viviam em CONTEXT ("Estado atual"), Indice ("Estado — espelho rápido"), README ("Estado 2026-07-21") e BACKLOG. Flagrante: card do BACKLOG pedindo rebuild com "esperado **63 testes** / E0 **0,5899**" (números da v0.2) convivendo com card vizinho dizendo "**85 testes** / E0 **0,5894**" (v0.4). E havia **dois BACKLOGs** — raiz e `scb_analytics/BACKLOG.md` (o original "sumiu do vault", foi recriado, e o velho ficou para trás com cards da era M3). O CHECKLIST v1 até alertava contra "v0.4 vs v0.5 conflitante", mas nenhuma regra atacava a causa: duplicação de estado. → *v2: regra 6 (estado num lugar só), checagem de fonte única no script, varredura anti-duplicação na Fase 6.*

**4. Prompts: 6 de 6 reescritos pelo projeto — o template falhou.** Os prompts v1 gastam 30–45% do texto em narrativa dirigida ao Gustavo ("lição do SPO", "foi assim que o `.lnk`…", molduras "## ⬇ PROMPT"): o 03-qa tem **3.400 chars (~1.130 tokens)** e o 04-auditor **3.460**, contra **~1.870 (~620 tokens)** das versões que o SCB reescreveu — mesma função, ~45% mais barato e mais imperativo. Quando o usuário refaz 100% dos templates, o defeito é do template. → *v2: prompts no formato do SCB (papel · "contexto que você recebe" · regras · saída), racional movido para README/este doc.*

**5. Sete invenções necessárias = sete lacunas do kit.** O SCB teve de criar do zero: pasta `contexto/` (4 docs de domínio, 274 linhas), tabela "quem carrega o quê", **Q-NN** (questões que são do dono), lane "Ações do Gustavo" no BACKLOG, **`Aprendizados para agentes.md`** (o melhor arquivo do projeto), versionamento de modelo com rebuild obrigatório (`MODEL_VERSION`), e a distinção **sandbox × máquina real**. Tudo generalizável; tudo ausente do kit v1; tudo incorporado na v2.

**6. Retrabalho que nenhuma regra prevenia.** A saga dos escudos consumiu **6 ciclos de QA (QA-05..QA-10)** porque o coletor foi escrito chutando a estrutura do repositório-fonte — resolvido só quando se criou `--investigar` (olhar a estrutura real primeiro). Mesmo padrão: duvidar do schema da API sem fazer 1 chamada (D-34) e caçar bug no settle quando era **falta de dado** (D-36). → *v2: regra 7 "observe antes de construir" + "é código ou é dado?" no implementador + coletores resilientes (try/finally, resumível) no perfil.*

**7. O kit assume colar-no-chat; agentes leem arquivos sozinhos.** Sem contrato de leitura, um agente com acesso à pasta lê CHANGELOG/dev/vault inteiro e paga tokens à toa (o README do SCB precisou avisar: "não carregar o vault inteiro em sessão"). → *v2: Mapa de leitura (ler sob demanda / nunca ler) + Protocolo do agente dentro do próprio CONTEXT.md.*

## Ressalvas sobre o próprio SCB (rigor vale para os dois lados)
- **A Fase 4 foi marcada "✅ em regime" sem evidência de sessão adversarial dedicada.** [suspeita] Os QA-NN vieram de harness de parser (QA-01..03), feedback do dono com print (QA-04) e da saga dos escudos (QA-05..10) — achados incidentais, não um ataque sistemático ao motor/web. Não há relatório de QA nos docs. Auto-avaliação generosa. → *v2: Fase 4 exige relatório registrado em `dev/qa-data.md`; sem relatório, não conta.*
- **O "espelho rápido" do Indice e o "Estado" do README** — invenções do SCB — são exatamente o anti-padrão que causou a divergência do item 3. Não importados.
- **Métricas repetidas em prosa por toda parte** (0,6131/0,5894 aparecem em CONTEXT, Indice, README, BACKLOG, CHANGELOG): cada repetição é um ponto futuro de inconsistência.
- Números de backtest, "85 testes verdes" e ICs são **claims dos docs** — verificáveis só na máquina do dono. O que este relatório valida é o *processo*; os resultados numéricos permanecem responsabilidade do portão de lá.

## Custo por sessão, antes → depois (estimativa em tokens)
| Item carregado | v1 (real no SCB) | v2 |
|---|---|---|
| Prompt do papel | ~620–1.150 | ~280–560 |
| CONTEXT.md | ~1.580 (sem teto efetivo) | ≤ ~1.300 garantido, legível |
| DECISIONS.md (Fase 5) | ~7.700 | ~2.000 (40 decisões × 2 frases + links) |
Em dezenas de sessões a diferença é de centenas de milhares de tokens só em contexto fixo — sem contar retrabalho evitado (a saga dos escudos, sozinha, custou ~6 sessões).

## Mapa das mudanças v2
| Arquivo | Mudança |
|---|---|
| `README.md` | reescrito: 7 regras (2 novas: estado único, observar antes), papel do dono + frases de segurança (absorve o "Manual do dono" do SCB); único lugar com "por quês" |
| `CONTEXT.md` | orçamento 4.000 chars · Estado em 6 bullets fixos · Mapa de leitura · Protocolo do agente |
| `DECISIONS.md` | linha ≤ 2 frases + evidência em `dev/` · Q-NN e QA-NN formalizados |
| `BACKLOG.md` | lane "Ações do dono" · regra de fonte única |
| `CHECKLIST.md` | seccionado por tipo de entrega (padrão SCB) · itens anti-estado-duplicado · QA exige relatório |
| `prompts/00–05` | reescritos, imperativos, com "Contexto que você recebe" (~metade do custo) |
| `prompts/06` | **novo**: retrospectiva → APRENDIZADOS.md |
| `APRENDIZADOS.md` | **novo**: lições do SCM/SCB já semeadas e generalizadas |
| `contexto/LEIA-ME.md` · `dev/LEIA-ME.md` | **novos**: convenções de docs de domínio e de evidência |
| `scripts/checar.py` | **novo**: valida orçamento, fonte única, WIP≤1, cruft |
| `perfis/*` | + "quem roda o quê", armadilhas pagas do SCB, coletores resilientes |

## O que deliberadamente NÃO mudou
As fases e sua ordem (M0–M7 do SCB mapearam direto nelas); o ceticismo do auditor (prior 20–30%, lista-morta — produziu 7 rejeições honestas); o CHANGELOG fora do contexto; os IDs D-NN/QA-NN; o princípio "lacuna declarada".
