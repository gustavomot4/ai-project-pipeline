---
tags: [benchmark, revisao, rodada-2]
status: atual
---
<!-- critica de completude e evidencia independente (rodada 2) · saida bruta do agente revisor, nao editada -->

# Crítica de COMPLETUDE — o que falta no benchmarking

---

## (a) As perguntas que um gestor cético faz e o documento não responde

**1. "Quanto custou?"** — Não há um único número de custo do próprio kit. O documento cobra custo dos outros com precisão cirúrgica (BMAD: 82,1k + 96,5k tokens num passo, ~US$200/ciclo, 12–16 h de planejamento; Memory Bank: US$30 → US$230 num mês; Aider: 16.419 tokens de repo map contra limite de 1.024) e não apresenta **nenhum** equivalente para si: nem tokens por sessão, nem R$ dos 187 commits, nem segundos do `check.py` por commit, nem horas do dono. C6=1 é uma nota honesta, mas o gestor não pede a nota — pede a fatura. Um benchmark que mede o custo de 13 concorrentes e não mede o próprio tem um buraco no lugar mais visível.

**2. "O que foi entregue de produto?"** — 62,6% dos commits tocam só processo e 4 commits tocam só produto. O documento reporta isso como CONTRA e para aí. Falta a outra metade: que funcionalidade existe hoje no projeto real? Os 12 critérios são todos de **mecanismo** (tem portão? tem registro? tem papéis?) e nenhum é de **desfecho** (defeito escapado, lead time, retrabalho, taxa de falha de mudança). O placar 31×44 é um placar de aparato, não de resultado — e o documento nunca diz isso ao leitor.

**3. "Qual o peso de cada critério?"** — A soma é reta: C7 (portabilidade) vale o mesmo que C3 (portão). Ninguém decide assim. Sem pesos declarados, "31/60 vs 44/60" é aritmética sem semântica, e um gestor que reordenar os pesos inverte o ranking em dois minutos. O documento precisa ou declarar pesos, ou dizer explicitamente que o total **não é** para decidir.

**4. "O portão já disse não alguma vez?"** — 0 pulos de portão declarados em 187 commits. Isso tem duas leituras opostas — disciplina perfeita, ou portão que nunca morde — e falta o número que as separa: **quantas vezes o `check.py` falhou e obrigou uma correção**. Existe a taxa de rejeição das decisões (9,8%), que é exatamente a métrica análoga; a do portão está ausente. E há uma contradição não resolvida: 25 dos últimos 30 commits do repositório do próprio kit violam o padrão de mensagem que o kit exige — ou o hook não está instalado lá, ou não bloqueia. O documento registra o fato e não explica o mecanismo.

**5. "E quando forem 6 pessoas?"** — C11 (distribuição em equipe) foi criado nesta rodada, mas o kit não tem evidência nenhuma para ele. O único evento de distribuição observado na história do kit — copiar para o projeto real — **já divergiu** (dois tetos elevados e um registro que o kit nem prevê). Ou seja: a taxa de deriva medida em N=1 fork é 100%. O documento não extrapola isso para 6 forks, e deveria.

**6. "Qual o custo de sair?"** — Não há plano de reversão. Adotar significa 5 registros, hooks de commit-msg, hook de PreToolUse, 24 skills e um portão Python de 78 KB com suíte própria de 141 testes. Se em 3 meses a equipe desistir, quanto custa arrancar? O documento cobra "aprisionamento a fornecedor" de Devin, Kiro e Gemini CLI (com razão) e não aplica o mesmo teste ao aprisionamento a **uma pessoa**.

**7. "Por que 4.000 caracteres?"** — É o único número falseável do kit, e ele já foi movido duas vezes, com a elevação registrada como decisão. Do lado de fora isso lê como catraca: o teto sobe quando aperta, e o ato de subir vira ponto de disciplina. Falta a justificativa original do 4.000 e falta uma regra que impeça a terceira elevação.

**8. "11 de 24 skills nunca dispararam. Por que continuam no kit?"** — Reportado como CONTRA, sem consequência. Qual o custo de manter 46% de processo morto, e por que a resposta não é apagá-las?

**9. "Vocês mediram o desfecho de alguém que não seja o autor?"** — Zero usuários externos. Autor, avaliador e beneficiário são a mesma pessoa, o que o documento declara — mas declarar não substitui o dado que falta: nenhum grupo de controle, nenhum piloto com segunda pessoa, e nenhum desenho de experimento proposto para obtê-lo.

---

## (b) O critério impossível de falsear: **C8 — Honestidade sobre limites**

C8 pergunta: *"declara por escrito o que NÃO faz e onde falha?"*. O kit se dá 4.

Três razões pelas quais ele ganha por construção, independentemente da qualidade real:

**1. Nenhuma observação possível baixa a nota.** Se o kit funcionar, é honesto e funciona. Se o kit falhar, o documento que declarou a falha **sobe** de nota. As seis linhas de CONTRA desta apresentação — 62,6% de commits de processo, 11 skills mortas, 25/30 commits fora do padrão, deriva da cópia, N=1 sem controle — são, pela régua de C8, *evidência a favor*. Um critério em que a prova contra vira ponto a favor não é um critério; é um laço fechado. Em termos popperianos: nenhum resultado o refuta.

**2. A régua não se aplica ao objeto.** A régua diz que 4 = "cobrado por máquina". Não existe máquina que cobre veracidade de auto-avaliação. O que o script cobra é que *exista um arquivo dizendo algo*; se o texto for autodepreciação decorativa que não muda nenhuma linha de código, a nota é a mesma. O 4 mede a presença de um gênero literário, não a de uma virtude.

**3. O campo de comparação é estruturalmente enviesado.** O avaliador lê **documentação de produto** dos 13 concorrentes. Nenhum fornecedor publica "eis o que não fazemos e onde falhamos" na página de vendas — não por desonestidade, por marketing e jurídico. Então C8 separa "manifesto escrito pelo autor para si mesmo" de "landing page", e o kit é o único participante do primeiro gênero. Repare no resultado: kit=4; Aider=4 e Copilot=4 (também com cultura de doc aberta); Kiro, Devin, Gemini CLI, Cursor, Claude Code=3; BMAD, Spec Kit, Memory Bank, AGENTS.md=2; ADR=1. A coluna reproduz a distância entre projeto pessoal e produto comercial, não entre honesto e desonesto.

**Como consertar sem apagar o critério** (ele é legítimo, o problema é a operacionalização): troque "declara o que não faz" por **"declara uma condição de fracasso verificável e a publica junto do resultado"**. Nota 4 exige um número pré-registrado que, se dado, condena o kit — e o teste rodado. Assim o kit cai para 2 hoje (declara limites em prosa, não pré-registra nada) e pode subir de verdade amanhã.

**Vices-campeões, pela mesma lógica:**
- **C2 (memória de decisão)** — o documento admite que é auto-retrato, mas ainda pontua. É pelo menos verificável (o artefato existe, é durável, é legível fora da ferramenta), então é um viés de *seleção de critério*, não de falseabilidade.
- **C3 (portão automático)** — mede **existência** de mecanismo, nunca **eficácia**. Não tem denominador. É por isso que o kit tira 4 num critério que o próprio repositório do kit viola em 83% dos últimos 30 commits. Uma régua honesta para C3 seria: 4 = mecanismo existe; 5 = mecanismo existe **e** a taxa de bloqueio/violação em uso real está publicada.

---

## (c) O ACHADO PRINCIPAL: a evidência independente existe, é recente, e aponta contra o miolo do kit

### C.1 — O estudo que o documento usa como arma contra dois concorrentes e evita como espelho

**Gloaguen, Mündler, Müller, Raychev, Vechev (ETH Zurich, SRI Lab) — "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?", arXiv:2602.11988 (fev/2026, rev. jun/2026), MemAgents @ ICLR 2026 — Oral e Runner-up Best Paper.** `[derivado]` — https://arxiv.org/abs/2602.11988 · https://www.sri.inf.ethz.ch/publications/gloaguen2026agentsmd

Do abstract, verbatim: *"providing context files does not generally improve task success rates, while increasing inference cost by over 20% on average"*, e vale *"across different LLMs, coding agents, and for both LLM-generated and developer-committed context files"*. Arquivos escritos por humano: ~+4%; gerados por LLM: ~−3%; ambos aumentam passos e custo `[derivado]`.

**E aqui está a frase que o documento não cita e que muda o diagnóstico do kit** — do próprio abstract: *"while instructions in the context files are well followed by coding agents, repository overviews, although popular and recommended by model providers, are not helpful"*. Conclusão dos autores: contexto serve para *"specifying non-standard coding practices"*, e *"any attempts to improve performance should be rigorously evaluated before deployment"*.

Traduzido para o kit:

| Camada do kit | Categoria no estudo | Veredito |
|---|---|---|
| `CLAUDE.md` (contrato: como trabalhar, delta não regeneração, escopo) + skills | **instruções** — "bem seguidas" | sustentada |
| `a_context_source.md` (**estado** do projeto: versão, métricas, contagens, estado atual) | **repository overview** — "não é útil" | **não sustentada** |

O kit tira **C1=4** por ter orçamento de máquina protegendo um arquivo cujo conteúdo dominante é exatamente a categoria que o estudo isola como *não útil*. E o documento cita este mesmo estudo — corretamente — nas CRÍTICAS de Cursor Rules e de AGENTS.md, e **não o cita na própria coluna**. Essa é, na minha leitura, a maior falha de completude do documento inteiro: usar um estudo como arma contra o adversário e não como espelho é seletividade de evidência, e é o tipo de coisa que um gestor cético descobre em uma busca de trinta segundos — e aí perde a confiança no documento todo, inclusive nas partes boas.

**O documento também cita números que eu não consegui confirmar**: "138 issues reais de 12 repositórios e 4 agentes". Nem o abstract do arXiv nem a página do SRI Lab enunciam essas contagens `[derivado, ausência]`. Ou a fonte é o corpo do PDF (então cite a seção), ou o número entrou por memória e precisa virar `[suposto]`.

### C.2 — O estudo que testa diretamente a única coisa falseável do kit (o orçamento de caracteres)

**McMillan, "Instruction Adherence in Coding Agent Configuration Files: A Factorial Study of Four File-Structure Variables", arXiv:2605.10039 (11/mai/2026).** `[derivado]` — https://arxiv.org/abs/2605.10039

1.650 sessões de **Claude Code CLI**, múltiplos modelos, bases TypeScript, medindo adesão a uma anotação-alvo trivial. Quatro variáveis fatoriais: **tamanho**, posição, arquitetura e conflitos. Resultado: **nenhum efeito estatisticamente significativo após correção para testes múltiplos**, com suporte bayesiano moderado ao nulo para tamanho e conflitos (BF10 entre 0,05 e 0,10). O que **teve** efeito: adesão cai ~5,6% de odds por função gerada dentro da sessão (OR = 0,944) `[derivado]`.

Leitura para o kit: o orçamento de 4.000 caracteres é o mecanismo mais bem-feito do kit e o único cobrado por máquina — e a única medição publicada da variável que ele controla diz que **essa variável não é a alavanca**. A alavanca medida é comprimento de sessão, que o kit não gerencia de forma alguma. Ressalva de qualidade: preprint de autor único, não revisado por pares — mais fraco que o ETH, mas é o único que testa a variável exata e roda na ferramenta exata.

Contrapeso honesto: **Chroma, "Context Rot: How Increasing Input Tokens Impacts LLM Performance" (2025)**, 18 modelos de fronteira, desempenho degradando com o comprimento da entrada muito antes de a janela encher `[derivado]` — https://www.trychroma.com/research/context-rot. Relatório de laboratório de fornecedor, não revisado por pares. É a **única** evidência publicada que apoia um mecanismo que o kit tem: manter o contexto pequeno é defensável como **controle de custo e de degradação**, não como controle de aderência.

### C.3 — A evidência que destrói a base probatória do kit (auto-relato)

**METR, "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity", arXiv:2507.09089.** `[derivado]` — https://arxiv.org/abs/2507.09089 · https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
RCT, 16 desenvolvedores experientes, 246 tarefas nos próprios repositórios. Previram +24% de aceleração, relataram +20% depois de fazer o trabalho, e ficaram **19% mais lentos**. Lacuna percepção-realidade: ~39 pontos percentuais.

**E a atualização, que quase ninguém cita — METR, 24/fev/2026.** `[derivado]` — https://metr.org/blog/2026-02-24-uplift-update/
Novo experimento com agentes do fim de 2025: 57 desenvolvedores, 800+ tarefas. Coorte original: **−18%, IC de −38% a +9%**. Novos: **−4%, IC de −15% a +9%** — ambos os intervalos cruzam o zero. A METR identificou viés de seleção grave (*"30% to 50% of developers told us that they were choosing not to submit some tasks because they did not want to do them without AI"*) e agora afirma que *"it is likely that developers are more sped up from AI tools now — in early 2026"*, com *"only very weak evidence for the size of this increase"*. Estão redesenhando a metodologia.

**A regra da casa manda dizer isto em voz alta: o "19% mais lentos" NÃO deve ser citado como fato corrente em 2026.** Quem citar como fato está fazendo com a METR o que teme que façam com o kit. O que **sobrevive** e é devastador para este benchmark é a outra metade: a medição mais rigorosa que existe sobre desenvolvimento assistido por IA é a de que **o julgamento do próprio praticante sobre sua produtividade está errado, por larga margem, e no sentido otimista**. Toda a evidência de eficácia do kit é o julgamento do autor sobre o próprio kit. Não há defesa contra isso a não ser controle — que o kit não tem, e cujo desenho o documento nem propõe.

### C.4 — O lado que apoia processo (e que o documento também precisa publicar)

- **DORA, 2025 State of AI-assisted Software Development** (~5.000 profissionais, 100+ h de entrevistas) `[derivado]` — https://dora.dev/research/publications/ · https://cloud.google.com/devops/state-of-devops. Tese: IA é **amplificador** — acelera quem tem fundação e amplifica a disfunção de quem não tem. Adoção de IA correlaciona com **mais throughput E mais instabilidade** (mais falhas de mudança, mais retrabalho).
- **DORA AI Capabilities Model — as sete capacidades** `[derivado]` — https://services.google.com/fh/files/misc/2025_dora_ai_capabilities_model.pdf: *clear and communicated AI stance · healthy data ecosystems · AI-accessible internal data · strong version control practices · working in small batches · user-centric focus · quality internal platforms*.
  **Repare no que não está na lista**: registro de decisões, skills de papel, orçamento de contexto, padrão de mensagem de commit, registro de QA em markdown. Das mecânicas do kit, **uma** mapeia para a lista — *strong version control practices*. É o achado mais acionável do conjunto: o corpo de evidência mais amplo que existe sobre desempenho de equipe com IA não contém quase nada do que o kit implementa.
- **DORA 2026, ROI of AI-Assisted Software Development** `[derivado]` — https://www.infoq.com/news/2026/05/dora-roi-ai-assisted-dev-report/: "imposto de instabilidade" — cálculo-exemplo de **−US$344.000** em indisponibilidade quando a taxa de falha de mudança sobe de 5% para 6%; ganhos de 35–40% em greenfield contra **≤10% em legado complexo**.
- **He, Miller, Agarwal, Kästner, Vasilescu (CMU) — "Speed at the Cost of Quality: How Cursor AI Increases Short-Term Velocity and Long-Term Complexity in Open-Source Projects", arXiv:2511.04427** `[derivado]` — https://arxiv.org/abs/2511.04427. Diferenças-em-diferenças, projetos do GitHub que adotaram Cursor contra grupo de controle pareado: ganho de velocidade grande e **transitório**, aumento **persistente** de avisos de análise estática e de complexidade; a dívida técnica resultante é apontada como fator principal da desaceleração de longo prazo. Conclusão dos autores: QA precisa de mais peso. Preprint (autores de credibilidade alta).
- **GitClear, 2025** (211 milhões de linhas) `[derivado]` — https://www.gitclear.com/ai_assistant_code_quality_2025_research: blocos com 5+ linhas duplicadas ×8 em 2024; linhas copiadas/coladas de 8,3% → 12,3% (2021–2024); linhas movidas (proxy de refatoração) **−39,9%**; churn de 4,5% → 5,7%. Relatório de fornecedor, não revisado por pares.
- **Cui, Demirer, Jaffe, Musolff, Peng, Salz — "The Effects of Generative AI on High-Skilled Work: Three Field Experiments with Software Developers", Management Science** `[derivado]` — https://pubsonline.informs.org/doi/10.1287/mnsc.2025.00535. RCTs na Microsoft, na Accenture e numa Fortune 100 de eletrônicos; **os maiores ganhos vão para os desenvolvedores menos experientes**. (A cifra de "+26% de tarefas concluídas" é `[suposto]` — reconheço de memória e não consegui confirmá-la nas fontes que abri.) É o contrapeso legítimo à METR e é relevante para uma equipe de 6 com mistura de senioridade.
- **Buchgeher et al., IEEE Access 2023** (900+ repositórios) `[derivado]`, já no documento: ~50% dos repositórios com ADR param entre 1 e 5 registros; média 6,03. Reenquadre: é a **taxa-base de decaimento de processo voluntário**. Os 112 registros do kit em 11 dias são ~18× a média — com portão de máquina e o autor mais motivado que o kit jamais terá. Os dois fatos importam: o portão funciona, e a amostra é a mais favorável possível.

### C.5 — Síntese honesta, incluindo o resultado desfavorável ao kit

**Não existe, hoje, nenhuma evidência controlada e publicada de que uma camada de processo pesada e auto-autorada melhore o desfecho no desenvolvimento assistido por IA.** Os dois estudos que medem diretamente o mecanismo central do kit — arquivos de contexto de repositório (ETH) e estrutura de arquivo de configuração (McMillan) — encontram efeito nulo sobre sucesso, com custo mensurável (>20% de inferência, mais passos). O documento tem obrigação de publicar isso na coluna do kit, e não só na dos concorrentes.

**O que sobrevive à evidência, e é do kit:** o **portão de máquina**. O estudo do CMU mede exatamente o modo de falha que um portão pré-commit ataca (avisos e complexidade que sobem e não voltam), o DORA mede o imposto de instabilidade, e o GitClear mede a duplicação. Um portão que roda antes do commit é a peça do kit com o melhor apoio empírico independente — e, ironicamente, é a peça que o próprio repositório do kit contorna em 25 dos últimos 30 commits.

**O que não sobrevive:** as 24 skills de papel, os 5 registros, o hook de mensagem de commit, e o orçamento de contexto como *ritual de governança* (ele sobrevive como controle de custo, não como controle de aderência).

---

## (d) A recomendação honesta para uma equipe de 6 pessoas decidindo hoje

**Combinar — e a combinação não é "kit + uma das 13". É: a ferramenta que a equipe já paga, mais quatro peças pequenas, das quais só uma vem do kit.**

### Não adotar o kit artesanal como está
Fator ônibus 1, zero usuários externos, nenhum caminho de saída documentado, o único evento de distribuição observado já derivou, 62,6% dos commits em processo, e as duas mecânicas que carregam a maior parte dos 31 pontos (C1 contexto, C4 papéis) ficam exatamente onde a evidência publicada mede efeito ~zero.

### Não adotar BMAD nem Spec Kit como fluxo principal
BMAD: 82,1k + 96,5k tokens num único passo e 12–16 h de planejamento antes da primeira linha, com portões julgados por LLM — é a cerimônia com o custo e sem a cobrança. Spec Kit: o `analyze` recomenda, a documentação de extensões diz que hooks não podem bloquear nem falhar; portão que não bloqueia não é portão. Para 6 pessoas, ambos multiplicam o custo por 6 e a garantia por 0.

### Adotar
**Base:** a ferramenta de agente que a organização já licencia (Claude Code, Copilot ou Codex CLI). Escolha por licença existente e portabilidade, não por recurso — o benchmark já mostra que a camada de processo é fina e migra; a camada de fornecedor é grossa e não migra (Devin, Kiro e Gemini CLI provam isso, com o Gemini CLI desligando contas individuais em 18/06/2026).

**1. Portões no CI, não no prompt — a peça do kit que vale a pena.** `pre-commit` + status checks obrigatórios + branch protection. Melhor apoio empírico do conjunto (CMU: avisos e complexidade sobem e ficam; DORA: imposto de instabilidade). **Leve a ideia do `check.py`, descarte a implementação**: porte as verificações para ferramental padrão (framework `pre-commit`, ruff/eslint, pytest) para que o laptop do recém-contratado e o CI rodem a mesma coisa. Um portão Python de 78 KB com suíte própria de 141 testes que leva 821 s é um **segundo produto** para manter, com um único mantenedor.

**2. UM arquivo de contexto por repositório, mínimo, escrito por humano, com teto de tamanho.** Evidência: ETH — humano ~+4%, gerado por LLM ~−3%, "describe only minimal requirements". Use o nome nativo da sua ferramenta (`CLAUDE.md` / `AGENTS.md` / `.github/copilot-instructions.md`). **Escreva instruções e práticas não-padrão; não escreva panorama do repositório** — essa é a categoria que o estudo isola como não útil. **Proíba arquivo de contexto gerado por IA** — é a única coisa que a medição mostra sendo ativamente negativa. Mantenha um teto (4.000 caracteres é um número defensável) entendido como controle de custo, e implementado como *aviso de lint*, não como portão.

**3. ADR com piso, não com cerimônia.** MADR em `/docs/adr`, um arquivo por decisão, com a seção *Considered Options* preenchida — é aí que a melhor ideia do kit (registrar as **rejeições**; 9,8% de taxa de rejeição) transfere sem trazer o resto junto. Contra o decaimento medido por Buchgeher (50% param em 1–5 registros), acrescente **uma** verificação de CI: PR que toca caminhos rotulados como arquiteturais precisa referenciar um ADR. É o mínimo que faz o hábito sobreviver a uma pessoa entediada numa sexta-feira.

**4. O placar certo é o do DORA, não o destes 12 critérios.** *Strong version control practices* e *working in small batches* são as duas capacidades de processo da lista, e as duas são baratas. **Meça as quatro chaves — sobretudo taxa de falha de mudança e retrabalho — nas 6 semanas ANTES de adotar qualquer coisa.** Sem linha de base você termina exatamente na posição da METR: convencido de +20% enquanto está em −19%, sem nenhum jeito de saber.

### Descartar, explicitamente
- **As 24 skills de papel.** 11 nunca dispararam em projeto nenhum. Proliferação de papéis não tem medição favorável em lugar nenhum, e a implementação mais documentada dela (BMAD) é documentada pela conta de tokens.
- **Os 5 registros → 2.** ADRs (decisões + rejeições) e o rastreador de issues que a equipe já tem. 44 achados de QA e 15 questões em 11 dias são **issues**, não arquivos markdown paralelos. Registro paralelo ao rastreador é trabalho duplicado que ninguém audita.
- **O hook de mensagem de commit exigindo citação de ID.** O próprio repositório do kit o viola em 25 dos últimos 30 commits — essa é a medição de que uma regra que ninguém consegue cumprir é uma regra que todo mundo contorna. Para rastreabilidade, use o vínculo nativo PR↔issue da plataforma.
- **O `check.py` como artefato.** Guarde as verificações, jogue fora o framework.
- **Qualquer arquivo de contexto gerado por IA.**
- **O orçamento de 4.000 caracteres como ritual de governança** — já subiu duas vezes, e cada subida virou ponto de disciplina. Catraca que só gira num sentido.

### O piloto que o documento deveria propor e não propõe
6 semanas · 2 dos 6 desenvolvedores · 1 repositório · quatro chaves DORA medidas 6 semanas **antes** · critério de parada pré-registrado por escrito antes de começar · comparação contra os outros 4 em trabalho comparável. Custo de estar errado, dito em horas de salário na apresentação: no N=1 mais favorável possível, 62,6% dos commits foram processo. Diga esse número vezes seis, em reais, no slide. É a única frase da apresentação que um gestor vai lembrar na semana seguinte.

---

## Nota de método sobre esta crítica

Rotulagem: `[derivado]` = abri a fonte nesta sessão e colei a URL. `[suposto]` = memória, sem confirmação — usei em exatamente dois lugares e os marquei. Os números do kit (187 commits, 62,6%, 3.653/4.000, 821 s, 25/30) vêm do documento avaliado; **não os reproduzi** e não são `[reproduzido]` para mim.

Duas correções factuais que o documento precisa aplicar antes de apresentar:
1. Os números "138 issues, 12 repositórios, 4 agentes" atribuídos ao estudo do ETH **não estão** no abstract do arXiv nem na página do SRI Lab. Confirme na seção do PDF ou rebaixe para `[suposto]`.
2. Se a apresentação citar a METR, cite a **atualização de fev/2026** junto. Citar "19% mais lentos" como fato de 2026 é o mesmo pecado de seletividade que esta crítica aponta em (c).

**Fontes:**
- [METR — Measuring the Impact of Early-2025 AI (arXiv:2507.09089)](https://arxiv.org/abs/2507.09089)
- [METR — We are Changing our Developer Productivity Experiment Design (24/fev/2026)](https://metr.org/blog/2026-02-24-uplift-update/)
- [Gloaguen et al. — Evaluating AGENTS.md (arXiv:2602.11988)](https://arxiv.org/abs/2602.11988)
- [SRI Lab ETH Zurich — página da publicação](https://www.sri.inf.ethz.ch/publications/gloaguen2026agentsmd)
- [McMillan — Instruction Adherence in Coding Agent Configuration Files (arXiv:2605.10039)](https://arxiv.org/abs/2605.10039)
- [He et al. — Speed at the Cost of Quality (arXiv:2511.04427)](https://arxiv.org/abs/2511.04427)
- [Chroma — Context Rot](https://www.trychroma.com/research/context-rot)
- [DORA — Publications](https://dora.dev/research/publications/)
- [DORA — 2025 AI Capabilities Model (PDF)](https://services.google.com/fh/files/misc/2025_dora_ai_capabilities_model.pdf)
- [InfoQ — DORA 2026 ROI of AI-Assisted Development](https://www.infoq.com/news/2026/05/dora-roi-ai-assisted-dev-report/)
- [GitClear — AI Assistant Code Quality 2025](https://www.gitclear.com/ai_assistant_code_quality_2025_research)
- [Cui et al. — Management Science, Three Field Experiments](https://pubsonline.informs.org/doi/10.1287/mnsc.2025.00535)