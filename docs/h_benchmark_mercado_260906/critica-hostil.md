---
tags: [benchmark, revisao, rodada-2]
status: atual
---
<!-- revisao adversarial das notas do benchmarking (rodada 2) · saida bruta do agente revisor, nao editada -->

**NOTA DE MÉTODO (leia antes):** não me foi entregue o texto dos critérios C1–C12, só os vetores de notas. Deduzi o eixo de cada critério do padrão das notas e das justificativas de refutação coladas. Onde a dedução sustenta o ataque, marco `[critério inferido]`. Ataques de consistência interna (nota vs. fraqueza declarada no próprio verbete; par de ferramentas com prosa igual e nota diferente) valem independentemente do rótulo. Fatos sobre ferramentas vêm marcados `[suposto]`.

---

## VÍCIO ESTRUTURAL — três defeitos do instrumento que contaminam todas as respostas

**1. O instrumento não resolve.** Cinco das 13 alternativas empatam em **exatamente 38/60**: Cursor Rules (3,2,4,4,1,3,2,3,4,4,4,4), Claude Code nativo (vetor **idêntico**, dígito por dígito), Kiro (38), Devin (38), Gemini CLI (38). Uma escala de 12 critérios × 0–5 tem 61 totais possíveis e colocou 38% do campo em um único ponto. Isso não é uma medição, é um valor central para onde tudo é puxado.

**2. Cursor Rules e Claude Code nativo têm os 12 dígitos iguais.** Isso é impossível como resultado de medição independente. E é falso na prática: o Claude Code tem hook `PreToolUse` que bloqueia por código de saída [suposto]; as rules do Cursor não têm camada de execução nenhuma [suposto] — o próprio verbete do Cursor diz "as regras não são cobradas por nada: entram no prompt". C1 e C8 não podem empatar. Pior: os dois **convergiram para o mesmo vetor através da refutação** (Cursor perdeu C6, Claude perdeu C6 e C8). A revisão está uniformizando, não discriminando.

**3. Um terço da escala é "sou um produto de empresa", contado quatro vezes.** Somando C9+C10+C11+C12: Copilot 17, Cursor/Claude/Kiro/Devin 16, Codex/Gemini/Cline 15 — contra kit **6**, ADR **7**, AGENTS.md **7**. Agora some só C1–C8 (a capacidade de processo propriamente dita): Codex 29, Aider 28, **kit 25**, Gemini 23, Cursor 22, Claude 22, Kiro 22, Devin 22, BMAD 21, Spec Kit 21, Cline 20, ADR 18, AGENTS.md 17. **O kit é 3º em processo e 14º em total.** Toda a distância dele para o topo vem de um bloco de quatro critérios que mede se existe uma empresa por trás. Isso é uma diferença de categoria vendida como diferença de qualidade — e é o motivo pelo qual o total 31/60 não carrega informação.

**4. A assimetria da auditoria é quantificável.** Cinco verbetes foram refutados (Spec Kit −1, Cursor −1, Claude −2, Aider −1, Kiro 0) = **−1,0 ponto por verbete auditado**. Oito verbetes não foram auditados e perderam **zero**. E os dois primeiros colocados do ranking inteiro — Codex 44 e Copilot 41 — são justamente os **não auditados**. O pódio é feito de números não verificados. Correção mínima exigida: aplicar deságio declarado de −1 a cada verbete não auditado, ou publicar o ranking com faixa de incerteza. Qualquer frase da forma "o kit fica em Nº X" precisa ser riscada do documento.

---

## 1. ONDE A NOTA ESTÁ ALTA DEMAIS

### O kit primeiro — captura do critério

O kit tira **20 de 25** (80% do teto) nos cinco critérios que descrevem exatamente o que ele foi construído para fazer (C1, C2, C3, C4, C8) e **11 de 35** (31%) nos outros sete. Um instrumento em que o artefato medido satura precisamente os eixos que são a sua lista de funcionalidades não é um instrumento: é um espelho. E C1, C3, C4 e C8 são **o mesmo mecanismo contado quatro vezes** — "processo cobrado por script/hook". Dezesseis pontos por uma ideia só.

**C2=4 é a nota mais frágil do documento.** 112 decisões em 187 commits em 11 dias = 0,6 decisão registrada por commit, ~10 por dia. Ou o limiar de "decisão" é tão baixo que D-NN registra trivialidade — e aí C2 mede volume de escrita, não memória —, ou o projeto teve 112 decisões arquiteturais em 11 dias, o que não é crível. O documento cita Buchgeher et al. (IEEE Access 2023): mediana de 6,03 ADRs por repositório, <2% acima de 25. O kit produziu 112 em 11 dias. Isso não é uma vitória sobre a literatura, é um sinal de que os dois lados não estão medindo a mesma coisa. **E nada na evidência mostra uma decisão sendo RECUPERADA.** 86,6% dos commits citam um ID — isso mede conformidade de citação, não que o conteúdo da decisão influenciou o código. Memória que nunca foi consultada é depósito. **C2 ≤ 3** até existir evidência de leitura, não de escrita.

**C1=4 (cobrança por máquina) `[critério inferido]`.** "0 pulos de portão declarados" é apresentado como sucesso, mas é indistinguível de: o portão nunca bloqueou nada; o autor nunca criou a condição de bloqueio; ou os desvios saíram por `git commit --no-verify`, que o hook não enxerga [suposto]. A evidência que provaria C1 é "N commits bloqueados e depois corrigidos" — esse número **não existe no dossiê**. Um portão sem nenhum bloqueio registrado em 187 commits não tem evidência de já ter portado. E a contraprova está no próprio dossiê: **25 dos últimos 30 commits do repositório do kit violam o padrão que o kit exige** — 83% de descumprimento, pelo autor, no repositório onde o kit mora. Medido lá em vez de no projeto de estimação, C1 é **2**.

**C3=4 (economia de contexto) `[critério inferido]`.** 3.653/4.000 = 91,3%, **com dois tetos já elevados**. Um orçamento que você levanta quando encosta nele não é orçamento, é sugestão com changelog. Além disso, os 4.000 caracteres cobrem **um** arquivo; as 24 skills, os 5 registros, o CLAUDE.md e os módulos entram na sessão sem medidor nenhum. É o cadeado de uma gaveta apresentado como controle do armário. **C3 = 2.**

**C8=4.** 11 das 24 skills nunca dispararam em projeto nenhum — 46% da superfície é código morto — e as 13 restantes foram exercitadas por um usuário, em um projeto, em 11 dias. Isso é nota do documento de design, não do artefato.

**O número que a rubrica não pontua em lugar nenhum:** 117 de 187 commits (62,6%) tocam só processo; **4** tocam só produto. Razão 29:1 de automanutenção para entrega. Nenhuma das 13 alternativas sobreviveria a esse número publicado sobre si.

### Nas alternativas

- **Copilot C9=5** com a Discussion #187926 aberta e marcada "Unanswered" de fev/2026 a jun/2026 sobre o produto **ignorar o próprio arquivo de instruções**. Se C9 é maturidade/suporte, quatro meses de silêncio oficial sobre a função central não é 5.
- **Copilot C8=4** enquanto a fraqueza do próprio verbete diz "as instruções são viés e não política" — e o Claude Code nativo foi **rebaixado** em C8 (4→3) por exatamente esse argumento ("context, not enforced"). A ferramenta com falha documentada de leitura do próprio arquivo ficou acima da que só foi acusada de conformidade fraca.
- **Aider C1=4 e C8=4** contra a fraqueza declarada no mesmo verbete: "Nenhum portão que bloqueie" e "o commit automático usa `--no-verify` por padrão, ou seja, atropela os hooks de pre-commit que a equipe já tem". Uma ferramenta que **desliga o portão que você já tinha** não pode ter a mesma nota de cobrança que um kit cuja tese inteira é um portão bloqueante.
- **Todas as notas 4+ de BMAD, Cline, AGENTS.md, Copilot, Codex, Devin e Gemini** estão declaradas como NÃO VERIFICADAS. São 8 verbetes, incluindo o 1º e o 2º lugares.

---

## 2. ONDE A NOTA ESTÁ BAIXA DEMAIS

**Zeros são afirmações de ausência, não de "não achei documentação".** O documento tem sete zeros e cada um precisa de prova positiva.

- **AGENTS.md C12=0 e ADR C12=1 (reversibilidade) `[critério inferido]`.** Ambos são arquivos markdown versionados no repositório: herdam `git revert`, `git diff`, blame e histórico completo — o mecanismo de desfazer mais confiável do campo. Enquanto isso "checkpoints" proprietários levam 4. O critério está medindo *feature de produto*, não a propriedade. AGENTS.md e ADR deveriam ser **≥3**; o Codex, cujo `/undo` foi **removido** e que tem relato de sobrescrita de arquivo não versionado, ficou com 2 — ou seja, abaixo do que um arquivo em git merece.
- **ADR C10=0.** O título do próprio verbete nomeia três ferramentas. Log4brains tem UI web, busca e site estático gerado [suposto]; adr-tools é CLI com `adr new`/`adr link`/`adr supersede` [suposto]; há extensões de editor e templates prontos [suposto]. Zero é indefensável. O verbete pontua a *prática* em C1/C4 e a *ferramenta* em lugar nenhum.
- **AGENTS.md C10=0 e C4=0.** É o único formato lido nativamente por vários agentes de fornecedores rivais [suposto: Codex, Cursor, Copilot, Gemini CLI, Aider, Jules]. Isso é o oposto de superfície zero.
- **Spec Kit C10=1 e C12=1.** Instala-se como slash-commands dentro de mais de dez agentes diferentes [suposto], contra Kiro (uma IDE, um fornecedor, com fila de espera) que leva **C10=4**. Esse par está invertido em qualquer leitura de alcance.
- **Aider C10=2 / BMAD C10=2.** Aider tem modo navegador, modo watch com comentários `# AI` em qualquer editor e integração por voz [suposto]; BMAD instala em qualquer agente [suposto]. A nota parece punir a *categoria* ("não é uma IDE"), não a capacidade.
- **O padrão mais revelador — medir baixa a nota.** BMAD é o único verbete com números reais de custo (82,1k + 96,5k tokens, ~US$200/ciclo, 12–16 h) e é o único com **C6=1** entre os produtos; Kiro e Devin, sem número medido, ficam em C6=2 apesar de ACU imprevisível e de medidor de fornecedor. O kit teve o overhead medido (62,6%) e também levou **C6=1**. **Todo verbete que ganhou um número real de custo foi para o fundo do C6.** Isso não é coincidência: é o viés do dossiê, quantificado, no eixo do custo.

---

## 3. CALIBRAÇÃO — pares específicos

1. **Cursor Rules ↔ Claude Code nativo** — 12 dígitos idênticos, total 38. Um dos dois está errado em C1 e C8, obrigatoriamente (hooks bloqueantes vs. nenhuma camada de execução) [suposto].
2. **Aider C1=4 ↔ Spec Kit C1=2.** O Spec Kit foi punido com a frase "O portão não é portão". O Aider não tem portão nenhum e ainda desativa o seu com `--no-verify`, e levou 4. Aplicando o mesmo teste, Aider ≤2; se o 4 do Aider é certo, o 2 do Spec Kit é errado. Escolha um.
3. **Copilot C8=4 ↔ Claude Code nativo C8=3.** Mesma natureza (prompt, não política), e só o Copilot tem falha documentada de o produto ignorar o arquivo (#187926). A nota está invertida.
4. **C6 — refutação aplicada só a quem foi auditado.** Cursor caiu 4→3 com a justificativa "não existe orçamento cobrado por máquina". Copilot=4, Codex=4, Aider=4 e AGENTS.md=4 também não têm orçamento cobrado por máquina [suposto] e ninguém encostou neles. O critério foi aplicado exclusivamente aos dois verbetes que sobraram tempo para auditar.
5. **C6 com duas definições no mesmo documento.** A refutação do Cursor argumenta *orçamento cobrado por máquina*; a do Claude nativo argumenta *automação de geração* ("o que é automático é só o primeiro arquivo, `/init`"). São dois critérios diferentes usando o mesmo rótulo. C6 precisa de definição escrita antes de qualquer nota ser mantida.
6. **C2 — ADR=3 ↔ kit=4 ↔ Kiro=2 ↔ BMAD=3.** O teste que o documento usa para punir o Kiro é "não guarda o que foi descartado". O MADR tem seção obrigatória de opções consideradas e prós/contras, e status `Superseded by` [suposto] — é o **único** formato do campo com esquema para alternativa rejeitada. Os documentos do BMAD também não guardam descarte [suposto], e levaram 3. Sob aplicação consistente do próprio teste, ADR ≥ kit em C2.
7. **C4 — Spec Kit=3 ↔ Cline Memory Bank=4 `[critério inferido: amplitude do ciclo coberto]`.** O Spec Kit cobre constituição → spec → plano → tarefas → implementação; o Memory Bank cobre "o que é o projeto" e "o que estou fazendo agora". A nota está de cabeça para baixo.
8. **C9 paga duas vezes pelo tamanho do fornecedor.** Copilot=5 e Codex=5 contra Aider=3 e Gemini=3. C9 recompensa porte corporativo e C7 pune fechamento — mas o bônus de C9 é maior que a punição de C7 nos verbetes da Microsoft/OpenAI. Efeito líquido: +1 estrutural para os dois que ocupam o pódio.
9. **C12 — kit=2 ↔ Aider=4.** Os dois desfazem por git. O Aider ainda usa `--no-verify` e tem issue de sobrescrita [suposto]. Ou os dois ganham o git, ou nenhum ganha.

---

## 4. O QUE FICOU DE FORA (e a ausência mais grave)

**A ausência que muda a conclusão: a categoria de portão de commit padrão de mercado.** `pre-commit` (framework), `commitlint` + Conventional Commits, `husky` + `lint-staged`, `danger`, e — o item decisivo — **branch protection com required status checks no servidor**. Essa categoria faz exatamente o que o `check.py` faz, existe há mais de uma década, tem milhares de contribuidores, e resolve o buraco que o kit **não pode** resolver: hook local é conselho (`--no-verify` mata), check obrigatório no servidor é lei [suposto]. Com essa linha na tabela, o C1=4 do kit vira "reimplementação artesanal, mais fraca, de um padrão existente, ao custo de 78 KB de Python e 141 testes que levam 821 s". É a omissão mais cara do documento.

Faltam também, cada uma por um motivo específico:
- **OpenHands / ex-OpenDevin** [suposto: open source, agnóstico de modelo] — sem ele, "agente autônomo" é representado só por um produto caro e fechado (Devin), o que **infla o C7 do kit por comparação**.
- **Continue.dev** [suposto: OSS, regras em repositório, multi-modelo] — o análogo portátil do Cursor Rules; sem ele, o slot "regras" é ocupado só por produto fechado.
- **Windsurf/Cascade** [suposto] e **JetBrains Junie / AI Assistant** [suposto] — todo o ecossistema JetBrains está ausente.
- **Amazon Q Developer** [suposto] — a AWS aparece só pelo produto novo e com fila de espera.
- **Sourcegraph Amp/Cody** [suposto].
- **Processo humano de RFC / Design Doc (Rust RFC, PEP, design doc do Google)** [suposto] — a alternativa de custo zero aos registros do kit.
- **`.github/pull_request_template.md` com checklist de decisão** — vinte linhas que capturam boa parte de C2/C4 [suposto].
- **Backstage TechDocs / plugin ADR, Linear/Jira decision log** [suposto] — onde equipes de 6+ realmente guardam decisão.

---

## 5. ONDE O KIT ARTESANAL PERDE FEIO — a dizer com todas as letras

**Fator ônibus = 1.** Autor, mantenedor, revisor, único usuário e beneficiário são a mesma pessoa. A base empírica inteira são 187 commits em 11 dias — 17 commits/dia de uma pessoa numa quinzena. As 13 alternativas têm, no mínimo, um rastreador de issues com desconhecidos dentro: o dossiê cita BMAD #1235, Aider #752/#3796, Claude Code #6305/#15441/#18547/#39468, Codex #16784/#9203, Copilot #187926, Cline #1727. O kit tem zero issues externas porque tem zero usuários externos. Frase para o documento: **"Se o autor sair de férias por duas semanas, nada quebra e ninguém percebe. Se sair por seis meses, o kit é um arquivo de 78 KB que ninguém da equipe pode alterar com segurança, com 141 testes cuja intenção mora em uma cabeça só."**

**A divergência de fork já aconteceu com N=1.** A cópia dentro do projeto real divergiu em 11 dias: dois tetos elevados e um registro que o kit nem prevê. E o kit não tem mecanismo de distribuição nem de atualização — sem pacote, sem `npx`, sem comando de upgrade; propaga-se por cópia manual [suposto]. Cursor rules, instruções do Copilot, AGENTS.md, templates de ADR e pre-commit todos têm história de distribuição e versão. **Com 6 pessoas e 4 repositórios você tem 4 dialetos em um mês, e nenhum caminho de volta.** Divergência aqui não é risco: é fato observado na menor amostra possível.

**Concorrência de equipe — defeito estrutural que a rubrica sequer tem critério para medir.** Cinco registros em arquivo único, append-only, com IDs sequenciais alocados localmente (D-NN, QA-NN, Q-NN). Com 6 pessoas: conflito de merge em toda PR paralela e **colisão de ID entre branches**, que o git não resolve semanticamente — duas D-47 diferentes, e o histórico passa a mentir. O ADR contorna isso por construção: um arquivo por decisão, nome com número e slug [suposto]. Isso é invisível em N=1 e fatal em N=6. **Adicione o critério "concorrência multi-autor"; o kit tira 0 ou 1.**

**Conformidade real, não a do projeto de estimação.** No repositório do próprio kit, 25 dos 30 últimos commits violam o padrão exigido. Isso é o autor, com motivação máxima, descumprindo 83% das vezes. **Os 86,6% do projeto real são o teto sob condição ideal com um único autor motivado, não a expectativa para a equipe.**

**Onboarding (C11=1) e imposto de contexto.** 24 skills, 5 registros, orçamento de 4.000 caracteres, quatro tipos de hook e uma gramática de commit própria — sem tutorial, sem curso, sem Stack Overflow. E o ponto que dói: CLAUDE.md, AGENTS.md, ADR e Conventional Commits são formatos que os modelos já conhecem [suposto]; os formatos do kit não são. Toda sessão gasta contexto reensinando as regras da casa — que é exatamente o imposto de +20% de custo de inferência que o próprio dossiê cita do estudo da ETH Zurich, e o kit o paga no tamanho máximo.

**Acoplamento duplo, pior que o dos fechados.** O kit depende de um fornecedor (superfície de hooks e skills do Claude Code, que muda) **e** de um mantenedor único. Aider e Codex CLI dependem de um só desses. C7=2 é generoso.

**Segurança e procurement (critério ausente).** 78 KB de Python rodando a cada commit em 6 máquinas, sem SBOM, sem processo de CVE, sem release assinada, sem licença discutida na evidência [suposto]. Morre no primeiro comitê de segurança.

**Custo por unidade de produto (critério ausente).** 62,6% dos commits só processo, 4 commits só produto. Publique isso como nota, não como rodapé.

---

## 6. O ADR RESOLVE O ESSENCIAL POR QUASE NADA — sim, e o documento precisa dizer

**Sim.** Na maior força alegada do kit, a distância é de **um ponto** (kit C2=4, ADR C2=3). Em custo e portabilidade o ADR ganha por 4 e por 3 (C6 5×1, C7 5×2). Os 6 pontos de vantagem no total (31 × 25) são comprados com 78 KB de Python, 141 testes de 821 s, 24 skills (11 nunca usadas), 4 hooks e uma gramática de commit própria. **Seis pontos de rubrica por esse preço é um péssimo negócio — e a rubrica esconde isso porque não tem eixo de custo por ponto.**

Pior para o kit: sob o teste que o próprio documento usa ("guardar o que foi descartado", usado para rebaixar o design.md do Kiro), o ADR/MADR é o **único** verbete com esquema para isso — status Proposed/Accepted/Deprecated/**Superseded by** e seções obrigatórias de opções consideradas com prós e contras [suposto]. As 112 decisões com 11 rejeitadas (9,8%) do kit são uma taxa, não uma estrutura. Aplicando o teste de forma consistente, **C2 do ADR ≥ C2 do kit, e a vantagem carro-chefe vira zero**.

O contra-argumento honesto a favor do kit é o de disciplina, e ele está no próprio dossiê: Buchgeher et al. (IEEE Access 2023) — ~50% dos repositórios param entre 1 e 5 ADRs, média 6,03, menos de 2% passam de 25. Mas leia o que esse achado diz de verdade: **o ADR falha em adoção, não em capacidade.** A resposta do kit à adoção é um cobrador. E o cobrador está disponível de prateleira: `pre-commit` + `commitlint` + um check de CI que falha quando uma PR toca `src/` sem criar arquivo em `docs/adr/` são umas 30 linhas de YAML [suposto], contra 78 KB de Python. Escreva a frase: **"ADR + 30 linhas de CI reproduzem a tese central do kit por cerca de 2% do código."**

O que o ADR genuinamente **não** faz — e é a única vantagem defensável do kit, então diga isso também para a crítica ser crível: o kit registra **achados** (QA-NN) e **perguntas ao dono** (Q-NN), não só decisões, e obriga o agente a **parar** na ambiguidade em vez de inventar; e tem uma história de realimentação do registro na sessão do LLM sob orçamento de contexto. O ADR não tem equivalente para nada disso [suposto]. Mas isso vale **um ponto**, não uma categoria.

**Conclusão que o documento precisa carregar:** memória de decisão é commodity desde 2011 — grátis, portátil, C6=5 e C7=5. A única alegação não-commodity do kit é "cobrança por máquina do processo do agente, com escopo e orçamento" — e essa alegação nunca foi comparada com o padrão de mercado que faz exatamente isso (pre-commit/commitlint/required checks), porque ele ficou de fora dos 13. Enquanto essa linha não entrar na tabela, o benchmark não testou a hipótese central do kit; testou tudo, menos ela.