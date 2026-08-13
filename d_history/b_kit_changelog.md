---
tags: [changelog, kit]
status: atual
---
# CHANGELOG do KIT — histórico do próprio pipeline

> **Este arquivo é do kit, não do seu projeto.** O histórico do projeto que você constrói mora no [[a_changelog|CHANGELOG]] da raiz, que nasce zerado.
> `docs/` não é copiada para projetos novos (`scripts/new_project.py` a exclui) — por isso o histórico do kit vive aqui e nunca polui o changelog do projeto.
> Regra de evolução: lição que aparece em 2+ projetos vira regra do kit e ganha uma entrada aqui. Ver [[README]] → "Como o kit evolui".

## [kit v13.2] — 2026-08-13
**Primeira avaliação de campo do kit, e ela achou o portão mentindo.** Um projeto real
construído com o kit v13.1 foi medido por uma sessão isolada, com o critério de sucesso escrito
e hasheado ANTES de qualquer arquivo do projeto ser aberto. O kit saiu bem em 9 de 9 hipóteses
— e a mesma medição encontrou uma checagem que tinha parado de checar sem que nada gritasse.
- **Skill:** nenhuma (sessão de evolução do próprio kit, fora do ciclo de projeto)

- **QA-14 · a checagem 10 enxergava 12% do que dizia enxergar.** `sem_codigo()` descarta o
  trecho entre crases antes de procurar `D-NN`/`Q-NN`/`QA-NN` citados — e a casa escreve
  `` `D-13` ``, não D-13. No projeto medido, **300 de 341 citações estavam entre crases**: o
  portão anunciava "ID inexistente" entre as falhas e reprovava ~12% dos casos. Corrigido com
  `sem_bloco_de_codigo()`, que remove só o bloco cercado; `sem_codigo()` fica como está para os
  wikilinks, onde descartar o exemplo entre crases é o comportamento certo.
  **Verificado nos dois sentidos:** com a correção revertida, a isca 10 reprova e só ela
  (1 falha em 3 testes); com a correção, a suíte inteira passa (38 testes).
  **E o canário que já existia continuava verde** com o defeito presente — porque escrevia
  `D-77` SEM crases, isto é, sabotava de um jeito que a casa nunca escreve.

- **O conserto estrutural, que vale mais que o defeito:** `TestTodaChecagemTemIsca` dá a CADA
  uma das 14 FALHAS numeradas uma isca canônica — o caso concreto que aquela checagem existe
  para pegar — e `test_toda_falha_numerada_tem_isca` compara o conjunto de iscas com os números
  do cabeçalho do `check.py`. FALHA nova sem isca reprova; isca que deixa de pegar o próprio
  caso reprova. É a generalização que faltava: o comentário da checagem 13 já nomeava a doença
  ("checagem que emudece é pior que checagem que não existe, porque o verde continua saindo"),
  a lição estava escrita neste mesmo arquivo, e a checagem 10 a tinha duas telas acima.
  Uma contraprova junto (`test_kit_entregue_passa_sem_isca`): sem sabotagem o portão não pode
  reprovar, senão uma isca que reprova por acidente passaria por isca que funciona.

- **Instrumentação da sessão (aviso novo, o 13º):** o changelog do projeto passa a declarar
  `- **Skill:** <nome>` por entrada datada, e o `check.py` avisa quando as 3 mais recentes não
  o trazem — ou quando o nome não existe em `b_process/skills/`. Motivo medido: a avaliação de
  campo não conseguiu responder "qual dos 24 agentes pagou o próprio custo" com evidência
  mecânica, porque **o kit não registrava qual skill rodava**; a resposta ficou em `[suposto]`
  por falta de um dado que custa uma linha. Mora no changelog de propósito — nenhuma sessão o
  carrega, então o dado custa **zero contexto**. É aviso, não falha: projeto que já existe não
  vai reescrever histórico para adotar isto. `README` (26→27 julgados, 12→13 avisos, cobrado
  pelo teste de honestidade), `CLAUDE.md` e o template de fecho de sessão acompanham.

**Conhecido e NÃO consertado aqui (regra 4 — achado vira nota, não commit de carona):**
- **A checagem 9 é `substring`:** um `.gitignore` contendo só um COMENTÁRIO que cita `.env`,
  `*.pem` etc. passa. Medido ao escrever a isca 9 — que, na primeira versão, também não
  sabotava nada (trocar `.env` deixava `.env.local`, que contém `.env`). Mesma espécie do QA-14.
- **Cinco melhorias levantadas pela avaliação e adiadas:** número que um script pode calcular
  não se digita (o campo "Passagens de revisão" do projeto medido dizia 1 com 3 no arquivo);
  `task.py arquivar` (5 de 34 sessões do projeto medido foram encolher arquivo à mão);
  aviso de achado vencido e de pergunta do dono com prazo estourado; card de faxina por módulo
  como papel de primeira classe; e trocar o caso de referência — que se declara "relato, não
  medição" — pela medição de campo, **com o imposto junto** (15% das sessões em manutenção do
  próprio processo, 43% dos commits sem código).

## [kit v13.1] — 2026-08-05
**Double check de ponta a ponta antes de usar o kit num projeto real.** Seis defeitos, **todos
introduzidos nesta mesma sessão** — enquanto o dia inteiro era gasto caçando divergência doc ×
código em quatro kits alheios e neste. A ironia é o dado: quem mais mexe é quem mais deriva, e
por isso deriva tem de ser cobrada por máquina, não por atenção.

- **QA-09 · projeto novo nascia com o CI e a suíte do KIT.** `.github/workflows/check.yml` era
  copiado **para dentro da pasta de documentação**, onde o GitHub Actions nem procura, rodando
  comandos com caminho de kit. E `scripts/test_check.py` ia junto, **reprovando com 9 falhas no
  primeiro `task.py test`** — porque testa scripts do kit, inclusive um (`new_project.py`) que
  nem é instalado. Suíte que nasce vermelha ensina a ignorar suíte. Os dois entraram na lista
  de exclusão, e o `task.py` explica em vez de só reclamar quando a tarefa não existe ali.
- **QA-10 · quatro documentos diziam "23 agentes"** depois que a 24ª entrou (`INDEX`, `README`,
  `skills/README`, `PRIMER`).
- **QA-11 · a mesma skill tinha dois nomes de fase:** o roteiro numerava `1c`, a skill e o
  índice diziam `Fase 1b`. Alinhado em **1c** (1a = arquitetura, 1b = plano, 1c = consistência).
- **QA-12 · o `b_checklist.md` não conhecia a Fase 1c.** O portão da fase existia no roteiro e
  na skill, e o arquivo que o dono usa para aceitar entrega não tinha uma linha sobre ele.
- **QA-13 · `.pytest_cache/README.md` gerava aviso falso** ("nota sem frontmatter") na primeira
  execução numa máquina com pytest instalado — sobre arquivo que não é nota e que o dono não
  escreveu. Aviso falso ensina a ignorar aviso: regra do kit, violada pelo kit.
- **`README` e `INDEX` não mencionavam nada do que foi construído hoje** — `task.py`,
  `--upgrade`, LICENSE, `docs/`, o CI. A árvore de arquivos do README listava três scripts de
  cinco.

**E o conserto estrutural, que vale mais que os seis:** `TestDocumentacaoNaoMente` conta os
agentes nos diretórios e cobra o número em toda a documentação, verifica que todo
`scripts/*.py` citado existe, e que toda skill aparece no índice. Verificado nos dois sentidos:
reintroduzir "23 agentes" reprova; criar skill fora do índice reprova. Nenhum portão pegava
isso antes — o `check.py` conferia que os **links resolvem**, nunca que as **afirmações
conferem**.

## [kit v13] — 2026-08-05
**Validação de um relatório externo que comparou este kit a sete frameworks.** As medições
dele conferem — `CLAUDE.md` 2.821, CONTEXT 2.768/69%, skills 5.489/2.464/7.570, `check.py`
533 linhas: todas exatas. As recomendações, nem todas. Três adotadas, três reduzidas, três
recusadas — e o achado mais valioso da rodada não estava no relatório.

- **QA-08 · a frase mais honesta do kit tinha envelhecido.** O README declarava "188 itens de
  checklist; o script julga 18 (12 reprovam, 6 avisam) — cerca de 10%". Real: **278 itens, 26
  julgados (14 + 12), 9%**. O relatório externo citou exatamente essa frase como a força única
  do kit ("nenhum concorrente declara a própria taxa de cobertura") — sem conferi-la. É a
  divergência doc × código que o kit classifica como achado de QA, na afirmação que o kit mais
  usa para se descrever. Corrigido **e cobrado por teste**: `TestHonestidadeDeclarada` conta os
  itens nos arquivos e o cabeçalho do `check.py`, e reprova se o README divergir. O teste pegou
  uma deriva na hora — um item de checklist que eu mesmo tinha acabado de acrescentar.
- **Aviso antes da parede (checagens 15 e 16).** CONTEXT acima de 90% e DECISIONS acima de 80%
  agora avisam, com candidatos a arquivamento listados. Quem estoura o teto está no meio de uma
  sessão e corta o que está à mão, não o que devia sair. Fecha a fraqueza que o próprio README
  declarava: *"o arquivamento é manual e ninguém lembra"* — o mesmo argumento do QA-04, que
  valia contra o kit e não tinha sido aplicado a ele.
- **Tema de `a_context/` fora do mapa de leitura agora avisa.** A regra "doc fora do mapa nunca
  é lido" era do kit e nada a cobrava: o arquivo existia, custava manutenção e ninguém o abria.
  A máquina **julga**; escrever o mapa continua sendo do dono — script não escreve na verdade
  de ninguém.
- **Critério de saída do laço 4a↔4b.** O roteiro dizia "repita até o placar zerar" sem condição
  de parada. Agora: placar de crítico/alto que não cai em **3 passagens consecutivas** encerra o
  laço e manda para `consistencia-artefatos` ou `planejador` — achado que reaparece três vezes
  não é bug, é sintoma de plano errado.
- **Releia do disco** (`CLAUDE.md`, regra 0). O dono edita entre os turnos; o estado que o
  agente lembra pode ter três turnos de idade. Custo: 150 caracteres no único arquivo pago em
  toda sessão — e vale.
- **Filtro de admissão no APRENDIZADOS:** incomum · opinativo · tribal · consistente. Lição que
  falha nos quatro é redescrição do óbvio ocupando arquivo que toda retrospectiva futura lê.

**Recusado, com o motivo:**
- **Placar de trajetória em arquivo (`trend.py`).** A ideia — sinal antes da parede — foi
  adotada como aviso de orçamento. O **mecanismo** proposto não sobrevive: `check.py` roda
  dentro do pre-commit, e arquivo escrito ali não entra no commit (ou o hook teria de dar
  `git add`, o que é pior); e uma linha anexada por commit vira ruído de diff e conflito de
  merge. A parte do placar de QA exigiria varrer `e_qa/`, que o `CLAUDE.md` proíbe ler.
- **Calibragem de complexidade 1–10 por módulo.** O número seria atribuído pelo agente — que é
  exatamente o defeito de sensor que o próprio relatório recusa no `drift_score` do SDD, sem
  aplicar a si mesmo. E colide com a regra do kit: número sem evidência não passa no portão.
- **Anotar supersessão na decisão antiga (D-03 recebe "supersedido por D-14").** Viola
  append-only, que é invariante do kit. O mecanismo já existe na linha nova (`SUPERSEDE D-XX`).
- **Envelhecimento de Q-NN em dias.** Exigiria coluna de data no DECISIONS. O kit amarra Q-NN a
  uma **condição** ("decidir quando"), não a um prazo, de propósito: pendência de dono destrava
  por marco, não por calendário.

## [kit v12] — 2026-08-05
**Comparação com o `SuperClaude-Org/SuperClaude_Framework` v4.3.0 — foco nos agentes, feita
sobre o pacote instalado (`pip download`), não sobre o README.** 20 agentes, esquema de corpo
rígido, 447 KB de markdown. O resultado foi o mais preciso de todas as comparações: **cada kit
tinha exatamente metade da mesma solução.**

- **A medição que organiza tudo.** As `description` deles: **0/20** dizem quando NÃO escolher o
  agente. As daqui: **21/24** já dizem (`Não use para X, é Y`). No corpo, o inverso: **15/20**
  deles têm `## Boundaries` com *Will / Will Not*; **0/24** daqui tinham qualquer fronteira
  explícita. Ou seja: este kit impede o agente errado de **disparar**; o deles impede o agente
  certo de **extrapolar**. Duas metades do mesmo problema.
- **`## Limites` nas 24 skills.** O que a skill NÃO faz mesmo tendo sido escolhida certo, e onde
  aquilo mora. O conteúdo já existia espalhado nas regras ("Não conserte", "Desenha; não
  implementa"); o que faltava era ser sistemático e achável. Custo real desprezível: como só
  **uma** skill carrega por sessão, +300 caracteres por skill custam 300 por sessão — ao
  contrário do `CLAUDE.md`, onde todo acréscimo é pago sempre.
- **Esquema de skill virou checagem.** As 24 seguiam o mesmo formato por **hábito**, e hábito
  não sobrevive a uma skill nova escrita com pressa. Agora `check.py` reprova skill sem
  `## Contexto que você recebe`, `## Limites` ou `## Saída`, e **avisa** quando a `description`
  não tem fronteira negativa — que é a força distintiva deste kit, até aqui não cobrada.
- **Medição que dispensou adoção:** duplicação de linhas no corpus deles = **1%** (447 KB);
  neste kit = **1,0%** (130 KB). Contra os 12% do BMAD. Nesse eixo os dois já estavam bem, e
  não havia o que copiar — só o que confirmar.
- **Não adotado: os 7 "modos comportamentais"** (Brainstorming, Token-Efficiency, Introspection
  etc.), uma camada ortogonal aos agentes. Duas razões: economia de contexto aqui é
  **estrutural** (teto de 4.000, uma skill por sessão, delta) e não precisa virar modo; e modo ×
  skill é combinatório — 7 modos × 24 skills são 168 combinações para documentar num kit de um
  mantenedor.
- **Também não adotado: `## Triggers` no corpo.** Eles repetem no corpo o que a `description` já
  diz. Duplicação é a doença que este kit mede desde a v10.

## [kit v11] — 2026-08-05
**Comparação com o `zhu1090093659/spec_driven_develop` — o repositório mais próximo deste kit
em restrições (Markdown puro, zero dependência, skills, agnóstico de plataforma).** A ideia
adotada não é um mecanismo deles: é uma vulnerabilidade que o teste deles revelou aqui.

- **QA-07 · checagem que para de checar em silêncio quando o template muda.** O template
  `progress.md` deles carrega um bloco **FORMAT FREEZE** avisando que o exportador lê por
  regex e que um travessão no lugar de dois hifens quebra o parser. Testei: quebra mesmo — o
  nome da tarefa vira `"Unknown"` sem erro nenhum. Fui procurar o equivalente aqui e achei,
  **em código escrito nesta mesma sessão**: `**Módulo**: M42` (dois-pontos fora do negrito)
  zerava a detecção de módulo fantasma, e `### M7: nome` (dois-pontos no lugar do travessão)
  sumia com o módulo inteiro. Nos dois casos, exit 0 e mensagem verde. É o QA-03 do lado da
  ENTRADA: lá a saída afirmava ter varrido o que não varreu; aqui a checagem deixa de checar
  e o verde continua saindo.
- **Correção em duas frentes.** (1) Os parsers ficaram tolerantes ao que é a mesma intenção
  escrita de outro jeito: separador de módulo `— – : . -`, `**Módulo:**` e `**Módulo**:`, e o
  limite de WIP aceita `máx`/`max`/`limite`/`≤`. Este último tinha um defeito próprio: só
  `máx` era lido, e `— limite 3` caía no default 1 — o script cobrava 1 e **ainda dizia**
  "limite declarado é 1". (2) **Canário de templates** (`TestCanarioDosTemplates`): cada teste
  injeta uma violação real nos templates **como são entregues** e exige que o portão a pegue.
  Se alguém reformatar um cabeçalho e o parser deixar de casar, a violação passa e o teste
  falha — o aviso que faltava. Testa o resultado, não o padrão: teste que confere a escrita do
  regex quebra junto com a implementação e não protege nada.
- **Melhor que a solução deles, e vale dizer por quê.** O FORMAT FREEZE é prosa dentro do
  template; prosa deriva e ninguém é obrigado a lê-la — foi a lição do `d_agent_learnings.md`
  que este kit já pagou duas vezes. Canário é máquina.
- **Honestidade sobre o alcance:** o canário guarda o par template↔parser dos casos cobertos
  (WIP, módulo, ID fantasma). Renomear um cabeçalho para algo irreconhecível é pego; uma
  mudança que o regex ainda casa por acaso, não. Ele estreita a janela, não a fecha.
- **Não adotado:** o controle adaptativo por `drift_score` (telemetria por tarefa, limiares de
  20/40/60% disparando anotar/replanejar/reescopar). É a ideia mais original que vi em qualquer
  um dos quatro repositórios, e é séria — mas exige estimativa de esforço por tarefa e coleta
  pós-tarefa disciplinada para produzir número confiável. Num kit de um mantenedor, o custo de
  alimentar o laço excede o valor do sinal, e número mal alimentado é pior que número nenhum:
  vira autoridade sem lastro. Fica registrado como candidato para quando houver várias pessoas
  executando o mesmo plano.

## [kit v10] — 2026-08-05
**Comparação com o `bmad-code-org/BMAD-METHOD` v6.10.0 — feita sobre o pacote instalado
(`npm pack`), não sobre o README.** 318 arquivos, 46 skills, 397 KB só de `SKILL.md`.
Duas ideias adotadas, uma medição que virou argumento para NÃO copiar, e um defeito nosso
descoberto no caminho.

- **QA-06 · `--upgrade` sobrescrevia customização do dono, em silêncio.** Defeito introduzido
  na v9, encontrado ao ver como o BMAD resolve customização (arquivo do kit marcado
  "DO NOT EDIT" + override separado com regras de merge declaradas). Reproduzido: o dono
  adapta uma skill ao time, o kit mexe na mesma skill, a atualização apaga a adaptação.
  Corrigido com **manifesto de impressões** (`.kit-manifest`, sha256 do que o kit escreveu):
  arquivo cujo hash não bate com o registrado é **PROTEGIDO** — reportado e não tocado, a menos
  que o dono peça `--forcar`. Projeto anterior ao manifesto trata tudo como protegido: falha
  fechada, porque perder trabalho em silêncio é pior que exigir uma flag.
- **Cobertura módulo ↔ tarefa virou máquina (checagem 13).** A melhor ideia do BMAD é marcar
  toda tarefa com o critério que ela atende (`(AC: #)`) — traçabilidade **no artefato**, não na
  revisão. Aqui isso vira `### M1 —` no PLANO cruzado com `**Módulo:** M1` no BACKLOG, e o
  `check.py` passa a responder sozinho a pergunta mais cara do projeto: existe módulo que
  ninguém vai construir? Módulo sem tarefa = AVISO (entre congelar o plano e povoar o backlog
  existe intervalo legítimo); tarefa apontando módulo inexistente = FALHA. A passagem 1 da skill
  `artifact-consistency` deixou de ser inteiramente semântica — sobrou para ela o que script não
  vê: marcação existente mas **errada**.
- **`[Fonte: arquivo#seção]` no PLANO.** "Nunca invente dado" já era regra em prosa; o campo é o
  que a torna auditável. Sem fonte, `[a confirmar]`.
- **Medido, e por isso NÃO copiado: o volume.** 12% do corpus deles (124 KB de 1.051 KB em
  `src/`) são linhas repetidas em 3+ arquivos; "MANDATORY EXECUTION RULES" aparece em 31
  arquivos, reforço de papel em 10, e um único `SKILL.md` (retrospective) tem 65 KB — 22× o
  `CLAUDE.md` inteiro deste kit. É a mesma doença do spec-kit, em escala maior. Adotar o
  mecanismo sem adotar o volume foi decisão consciente.

## [kit v9] — 2026-08-05
**O kit passou a alcançar os projetos que gerou.** Comparação com o `github/spec-kit` (mesma
categoria: método, não scaffold) apontou quatro coisas que faltavam. Três foram adotadas; a
quarta — instalador e marketplace de extensões — foi descartada por custo desproporcional a
um kit de um mantenedor.

- **`new_project.py --upgrade` — o buraco estrutural.** Até aqui a cópia era de mão única:
  projeto criado na v7 nunca recebia nada da v8, e todo conserto ficava encalhado no repositório
  do kit. Agora o **processo** (`b_process/skills|profiles|templates`, roteiro, checklist,
  padrão, glossário, `scripts/`, `CLAUDE.md`, `INDEX.md`, guia do Obsidian) é atualizável, e a
  **verdade do projeto** é intocável. O limite é uma lista explícita, não heurística de pasta —
  porque `b_process/c_backlog.md` mora numa pasta de processo e **é estado**, e
  `d_agent_learnings.md` recebe lições do projeto. Errar esse limite apaga trabalho do dono.
  Salvaguardas: `--dry-run`, recusa de árvore git suja (a atualização tem de ser revisável por
  `git diff` e reversível por `git checkout`), escrita só quando o conteúdo difere, e **nada é
  apagado** — arquivo removido do kit é reportado, não deletado. Marca `.kit-version` derivada
  do título deste changelog, escrita na criação e na atualização.
- **Skill nova: `artifact-consistency` (Fase 1b).** É o que o `check.py` não consegue fazer e
  nunca vai: ele julga **forma** de modo determinístico; módulo do PLANO sem tarefa no BACKLOG,
  adjetivo sem número em critério de aceite, plano adotando o que o DECISIONS **rejeitou** e
  termo com dois nomes são **significado**. Sete passagens, severidade pelo efeito, saída com
  tabela de cobertura. Sessão separada por doutrina do próprio kit — quem escreveu o plano é a
  última pessoa que deveria julgar se ele cobre o contexto.
- **Restrição inegociável virou constituição.** O campo já existia no CONTEXT e nada nunca
  conferia contra ele. Agora violação é **CRÍTICO automático** em `guardrails-review` e em
  `artifact-consistency`, e a saída é ajustar o código ou o plano — nunca reinterpretar a
  restrição até ela caber. Mudar a restrição é D-NN novo, em sessão separada.
- **`context-bootstrap`, regra 1b: como escolher quais 5 perguntas.** O teto de 5 já existia; o
  critério, não. Treze áreas marcadas *clara/parcial/ausente*, gasto por impacto × incerteza,
  com recomendação oferecida junto — dono corrige recomendação errada mais rápido do que
  responde pergunta aberta. Área parcial que não muda arquitetura, schema, teste ou validação
  vira suposição declarada, não pergunta.
- **Não adotado, e por quê:** o bloco de *extension hooks* do spec-kit repete o mesmo texto duas
  vezes em cada arquivo de comando (~40% do `clarify.md`), pago em tokens a cada invocação. É a
  doença de "prosa duplicada derrapa" que o `task.py` acabou de curar aqui.

## [kit v8] — 2026-08-05
**O portão passou a rodar fora do sandbox de quem edita.** Um relato de campo de outro agente
(Fase 0 completa num Windows pt-BR sob OneDrive) apontou cinco achados; a validação contra o
código confirmou quatro, corrigiu a severidade de dois e reprovou um dos patches propostos.
Detalhe do que se sustentou e do que não, em `docs/`.

- **QA-01 · encoding fixado nas 5 chamadas ao git** (`check.py`, `install_hook.py`). `text=True`
  sozinho decodifica com o encoding do SISTEMA — cp1252 num Windows pt-BR — e um caminho com
  acento derrubava a thread leitora. `UnicodeDecodeError` é `ValueError`, então os
  `except (SubprocessError, OSError)` passavam ao largo e o dono via um `AttributeError` a duas
  funções da causa. Efeito medido: o portão **nunca tinha rodado na máquina do dono**.
- **QA-02 · `.git` deixou de ser o teste de "estou num repositório".** Em worktree e submódulo
  ele é ARQUIVO, e `(topo / ".git").is_dir()` pulava a varredura de HISTÓRICO em silêncio.
  Medido: com segredo plantado no histórico e removido da árvore, repositório normal reprovava
  (correto) e **worktree imprimia OK com exit 0**. Agora `git rev-parse --show-toplevel
  --git-path hooks` responde numa chamada, e cobre também o git fora do PATH.
- **QA-03 · a linha final passou a sair do que rodou, não da flag.** Anunciava "últimos 30
  commits" mesmo sem ter lido nenhum. O alcance agora vem do bloco que executou.
- **QA-04 · `check.py` cobra a instalação do próprio portão.** "Portão que só roda quando alguém
  lembra não é portão" era regra do kit que não valia para o kit. O caminho vem de
  `--git-path hooks`, então worktree e `core.hooksPath` **não** geram aviso falso — o patch
  originalmente proposto cravava `.git/hooks` e gerava.
- **QA-05 · o gêmeo do QA-01, do lado da ESCRITA — achado rodando na máquina do dono.**
  `new_project.py` imprimia uma seta `→` (U+2192), que não existe em cp1252. Com a saída
  REDIRECIONADA num Windows pt-BR o script morria de `UnicodeEncodeError` **depois** de já ter
  criado o projeto inteiro. Consertado no texto (`->`) e com rede de segurança
  (`sys.stdout.reconfigure(errors="replace")`) nos quatro scripts: degradar é melhor que morrer.
  Guardado por dois testes — um acha o caractere na fonte via `ast`, outro força
  `PYTHONIOENCODING=cp1252` e exige que nada estoure.
- **`scripts/test_check.py` — testes de regressão, só stdlib.** Dez casos, um por bug que já
  aconteceu. Verificados nas duas direções: passam no código bom e **falham** quando o bug é
  reintroduzido. Três defeitos do próprio arquivo, todos achados rodando fora do sandbox:
  a isca de segredo estava literal e fazia o check reprovar por outra causa (teste passando pelo
  motivo errado); a asserção era pelo código de saída e virou pelo MOTIVO; e ele decodificava a
  saída do filho como UTF-8 enquanto o Windows a emitia em cp1252 — **a mesma classe do QA-01,
  cometida dentro do arquivo que existe para guardá-la.** Resolvido com `PYTHONIOENCODING=utf-8`
  no ambiente do filho, igual ao CI. `shutil.rmtree` também ganhou tratamento: o git marca
  objetos como somente-leitura e no Windows a faxina morria com `PermissionError`.
- **CI em Linux e Windows.** Windows não é opcional: o QA-01 não reproduz no Linux, porque com
  `LC_CTYPE=C` o Python liga o UTF-8 Mode sozinho (PEP 540). Foi esse falso "passou" que fez a
  auditoria original medir errado. `fetch-depth: 0`, senão o portão varreria 1 commit.
- **`scripts/task.py` — ponto de entrada único.** Os comandos moravam em prosa espalhada por
  três documentos e já tinham divergido do código em três pontos. Não é `Makefile`: `make` não
  existe num Windows por padrão, e o kit **não tem dependência externa nenhuma** — decisão
  mantida contra a alternativa de adotar `pre-commit` + `detect-secrets`, que resolveria o QA-04
  de graça mas exigiria `pip install` e rede na primeira execução.
- **`docs/` passou a existir de verdade.** O `e_qa/README.md` mandava a auditoria do kit para
  uma pasta inexistente. Os dois relatórios saíram de `e_qa/`; `docs` entrou em
  `PASTAS_HISTORICAS` (senão o portão reprova nos IDs dos projetos-cobaia) e em
  `EXCLUIR_PASTAS`. O `SO_DO_KIT` virou **derivado** das exclusões: relatório novo do kit é só
  gravar em `docs/`, sem editar duas listas à mão.
- **Guia do Obsidian: seção "Higiene" cortada.** Listava 7 das 12 falhas, omitia a varredura de
  segredo e descrevia um limite de WIP que o código não usa mais. Divergência doc × código é
  achado de QA pela regra do próprio kit — agora aponta para o script, que é a fonte da verdade.
- **`context-bootstrap`, regra 8:** ao fechar um Q-NN, perguntar "o que esta resposta acabou de
  tornar decidível?". Era comportamento emergente numa sessão real (gerou três lacunas de
  política que ninguém tinha visto); virou instrução.
- **LICENSE (MIT).** Sem licença, ninguém além do dono podia usar o kit.

## [kit v7] — 2026-08-03
**Adoção do padrão de repositório da equipe.** O kit deixou de ter estrutura própria e passou a
ser exatamente o que o padrão chama de pasta de documentação — com todos os nomes de arquivo e
pasta **em inglês**, conteúdo em português.

- **Estrutura:** raiz plana → `a_context/` (contexto-fonte, plano, decisões) · `b_process/`
  (roteiro, checklist, backlog, aprendizados, padrão, skills, profiles, templates) ·
  `c_technical_docs/` · `d_history/` · `e_qa/` · `scripts/`. `INICIO.md` → `INDEX.md`.
  Prefixo `a_`/`b_`/`c_` = **ordem de leitura** da pasta.
- **Nomes em inglês, conteúdo em português.** Inglês é a língua dos *nomes*, que aparecem em
  caminho, URL, terminal e log, onde acento e espaço custam caro. As 23 skills também:
  `arquitetura-monolito` → `architecture-monolith`, `testes` → `testing`, e o `name:` do
  frontmatter acompanha (é o identificador que a ferramenta consome).
- **Duas exceções declaradas no padrão.** As skills não levam prefixo de ordem — o prefixo
  significa "ordem de leitura" e as skills não se leem em ordem, cada sessão carrega **uma**,
  escolhida pelo gatilho da `description`. E usam `hifen-minusculo`, não `snake_case`, porque
  o nome da pasta **é** o identificador da ferramenta.
- **Relatórios de QA levam timestamp `AAMMDD_HHMM`.** Só as saídas de IA datadas: documento
  vivo (contexto, backlog, changelog) é atualizado por substituição, e datar no nome criaria
  a duplicação que a regra 2 do padrão proíbe.
- **`new_project.py` reescrito — monta o esqueleto inteiro.** Antes copiava o kit; agora cria
  `77777777_<TAG>_Project_DOCs/` + pasta de código com README técnico + `README.md` da raiz na
  estrutura da seção 7 + `CLAUDE.md` + `.gitignore` + `.gitattributes`. Os sete primeiros itens
  do "checklist para abrir projeto novo" viraram executáveis.
- **`check.py` passou a trabalhar em dois escopos** — e isso era um bug esperando acontecer.
  Com a documentação virando subpasta, `.gitignore`, `.gitattributes` e `CLAUDE.md` passam a
  morar na raiz do repositório, **fora** do vault. O teste do scaffold pegou: o script reprovava
  `.gitignore ausente` e `wikilink sem destino: CLAUDE` num projeto recém-criado e correto.
  Pior, silenciosamente: `git ls-files` rodado de dentro da subpasta **não varreria o código do
  projeto por segredo** — um terço do repositório fora da rede. Agora `raiz` (vault) cobre
  orçamento, links, órfãs, IDs e skills; `topo` (repo) cobre `.gitignore`, cruft e a varredura
  de segredo na árvore e no histórico.
- **`install_hook.py` grava o caminho relativo do `check.py`** no hook, calculado na instalação:
  num projeto isso vira `77777777_<TAG>_Project_DOCs/scripts/check.py`. E `check.py` acha o
  vault sozinho, procurando `a_context/` na raiz e depois em `*_Project_DOCs/`.
- **Adicionado `b_process/e_repository_standard.md`** — o padrão, que vai junto para todo
  projeto novo. É o documento que torna a convenção replicável em vez de folclore.

## [kit v6] — 2026-08-03
**17 → 23 agentes.** A revisão dos 17 existentes não achou gordura: a sobreposição já era de 0,2% de mediana e cada regra tinha custo real por trás. O defeito estava na **cobertura**: o kit sabia construir e não sabia sustentar. Um projeto passa muito mais tempo sendo mantido do que sendo criado, e para essa fase o kit v5 não tinha agente nenhum.

**Adicionados — sistema vivo (o buraco maior):**
- **`depuracao-diagnostico`** — "quebrou", "está errado". Era o pedido mais frequente do dia a dia e o único sem agente: a doutrina existia espalhada em três skills ("é código ou é falta de dado?", "processo vivo tem cache") sem ninguém para executá-la. Portão: **reprodução determinística antes de qualquer edição**, causa provada por liga/desliga, teste de regressão citando `QA-NN`. STEP 0 obriga as três perguntas que resolvem metade dos casos sem abrir o código.
- **`performance`** — "está lento". Portão: alvo definido pelo dono (`Q-NN` se faltar), baseline com 3 medições, gargalo apontado por **profiler**, uma mudança por vez, volume realista. Recusa explícita de otimizar sem alvo — é o tipo de trabalho que nunca termina e sempre piora a legibilidade.
- **`observabilidade`** — fechava uma incoerência do kit: o default é monólito e a única observabilidade desenhada era a do caso distribuído (`microservice-sync`). Portão: as 3 perguntas respondíveis sem abrir o código, correlação mesmo em monólito, **nada sensível em log**, alerta com dono e ação no `RUNBOOK`.

**Adicionados — cobertura que faltava:**
- **`adocao-projeto-existente`** — **levanta um limite declarado no README** ("kit para tirar aplicação do zero"). Mapeia a partir do código, nunca da documentação, e produz `CONTEXT`/`PLANO` retroativos com `D-NN [retroativa]`. Portão contra-intuitivo e essencial: **nenhum arquivo de código alterado na sessão** — mapear e consertar junto produz o mapa do que se gostaria que existisse.
- **`dependencias-supply-chain`** — a auditoria de 30/07 olhou o código próprio e não olhou o que vem instalado. Portão: lockfile versionado, uma atualização por vez, CVE tratada/mitigada com prova/aceita com `D-NN`, licença conferida, script de pós-instalação conhecido.
- **`privacidade-dados-pessoais`** — o kit tinha autenticação (quem entra) e nada sobre o dado em si. Portão: inventário com finalidade por campo, retenção **implementada** e não só declarada, exclusão e exportação do titular testadas ponta a ponta, nada sensível em log nem em backup. Base legal e prazos são `Q-NN` do dono — a skill declara explicitamente que não dá parecer jurídico.

**Corrigidas — inconsistências nas 17 existentes:**
- `bootstrap-contexto` mandava preencher um "Mapa de leitura" que a v5 tinha movido para o `CLAUDE.md` — instrução órfã apontando para seção inexistente.
- `revisao-entrega` e `guardrails-review` mandavam varrer segredo com `git log -p | grep`, ignorando o `--historico-completo` corrigido na v5. Ambas passaram a exigir a flag, e `revisao-entrega` ganhou o item sobre amostra de segredo **inutilizada, não isentada** (lição do push barrado pelo GitHub).
- `dados-analise` era a única das 17 sem seção "Armadilhas pagas". Ganhou as seis dela, com custo observado.
- Referências cruzadas onde o encaminhamento estava faltando: `guardrails-review` → `depuracao-diagnostico` (quem revisa não conserta), `backend-dominio` → `privacidade-dados-pessoais` (finalidade se decide no schema), `iac` → `observabilidade`.

**Custo assumido, medido:** 17 → 23 descriptions = 7.260 → **10.121** chars (≈ 2.420 → **3.373** tokens fixos por sessão, +39%). Decisão consciente: agente que não dispara custa pouco; agente ausente custa uma sessão inteira improvisando doutrina que já existia escrita. Candidatas a fusão, se um dia o custo apertar: `arquitetura-microservicos` + `microservice-sync`, e `frontend-mfe` dentro de `frontend-uiux` — as quatro raramente disparam num projeto de um dono só, que é o alvo declarado do kit.

## [kit v5] — 2026-07-30
Correções dirigidas pela **auditoria externa adversarial** registrada em [[b_external_audit_report_260730_0900|AUDITORIA-EXTERNA-2026-07-30]] (placar 58/100 no commit `51c272a`). A v4 declarou ter fechado a lacuna de segurança; a auditoria mediu que **não fechou**. Cada item abaixo tem teste executado antes e depois.

- **Corrigido (crítico) — `--historico-completo` varria ZERO commits.** `PROFUNDIDADE = "0"` montava `git log -p -0`, que em git significa nenhum commit, não todos. Sintoma que denunciava: a varredura "completa" rodava em 0,33 s contra 1,49 s da parcial. A flag de que a Fase 6 depende era uma no-op que imprimia `OK`. Agora o limite é omitido (varre tudo), com timeout de 120 s.
- **Corrigido (crítico) — o scanner de segredo detectava 0 de 8 segredos reais.** Duas causas: (a) o filtro anti-exemplo descartava a **linha inteira**, então um comentário `# ver <ticket-4412>` ou `# TODO xxx` desligava a checagem — agora ele avalia **só o trecho casado**; (b) os padrões exigiam aspas, e a linha de `.env` (`API_KEY=sk_live_…`), o formato mais comum de vazamento, passava — agora valor sem aspas também casa (com exigência de dígito, para não casar com prosa). Novas famílias: senha em connection string, JWT, Stripe `sk_live`/`rk_live`, GitLab PAT. **Medido: 8/8 detectados, 0/12 falsos-positivos.** Isenção explícita por linha com a marca `checar:ignore` — para o que é **comprovadamente inerte**, não para amostra que só parece falsa: essa se inutiliza trocando o corpo do token por `XXXX`. O push protection do GitHub barrou o primeiro push deste laudo justamente por iscas isentadas mas intactas, e estava certo (lição em [[d_agent_learnings|APRENDIZADOS]]).
- **Corrigido (crítico de uso) — "nota órfã" era FALHA e varria o repositório inteiro.** Qualquer `content/blog/*.md`, doc de pacote ou `NOTAS.md` de módulo do próprio app bloqueava **todo** commit por motivo cosmético. O efeito real não é atrito: é o dono adotar `git commit --no-verify` por hábito e desligar junto o portão de segredo, o orçamento e a fonte única. Virou **AVISO**, e só dentro do vault.
- **Corrigido — o script ignorava o `.gitignore`.** `IGNORAR` era uma lista fixa de 9 nomes. Um CSV de 17 MB em `open-data/` (que o próprio `.gitignore` do kit exclui!) custava **12,3 s em cada commit**; um provider Terraform de 200 MB, 402 MB de RSS. Agora o universo da varredura é `git ls-files --cached --others --exclude-standard`, e arquivo acima de 1 MB é pulado **com aviso** — nunca em silêncio. **Medido: 12,3 s → 1,5 s.**
- **Corrigido — falha aberta com mensagem verde.** O `except … : pass` no `git log` engolia timeout e erro, e a linha final continuava listando "segredos" entre os itens aprovados. É o anti-padrão que a própria `guardrails-review` classifica como achado (frente 6). Agora vira aviso explícito, e a mensagem de sucesso **declara o alcance**: "árvore versionada + últimos 30 commits".
- **Corrigido — falso-positivo de ID.** Citar um `QA-07` herdado em [[d_agent_learnings|APRENDIZADOS]] reprovava o commit, contra a orientação do próprio arquivo. `e_qa/` e `APRENDIZADOS` entraram na isenção que `docs/` já tinha.
- **Corrigido — o hook bloqueava TODO commit no Windows.** Achado em uso real, não em teste: `command -v python3` encontra o *App Execution Alias* que o Windows instala em `WindowsApps` — um `python3.exe` que está no PATH, não executa nada e imprime "Python não foi encontrado; executar sem argumentos para instalar do Microsoft Store". O hook tomava o stub por interpretador e reprovava commits limpos. É a mesma doença dos outros achados, com o sinal trocado: falha **fechada** pelo motivo errado empurra para `--no-verify` tão rápido quanto falha aberta. Agora o hook testa se o candidato **roda** (`python3` → `python` → `py`, o Launcher do Windows), não se ele existe; sem nenhum Python funcional, avisa alto e deixa passar — ambiente quebrado não é commit sujo, e confundir os dois foi o defeito.
- **Adicionado — `.gitattributes`.** `* text=auto eol=lf`: o repositório guarda LF e o Windows fica com CRLF na cópia local. Elimina o aviso em todo `git add` e impede que um shell script versionado com CRLF quebre no Git Bash.
- **Adicionado — `CLAUDE.md`.** Não havia contrato de leitura: um agente aberto na pasta não carregava o [[a_context_source|CONTEXT]] sozinho, e o "Protocolo do agente" morava dentro do arquivo que o agente só lia se alguém o entregasse à mão.
- **Corrigido — 20% do orçamento do CONTEXT era instrução ao agente.** O "Protocolo do agente" (780 chars) saiu do [[a_context_source|CONTEXT]] para o `CLAUDE.md`. O template vazio ocupava **3.541 dos 4.000 chars**; agora sobra margem real para contexto de projeto.
- **Corrigido — números desatualizados.** "~160 itens" / "8 de 163" viraram a contagem medida: **188** itens de checklist no kit, **16** com trava automática (~9%).

> **O que a auditoria aprovou, para registro:** sobreposição entre as 17 skills medida em **0,2% de mediana** por 6-gramas, zero pares acima de 10% — a promessa da v4 se sustenta. `novo-projeto.py` e `instalar-hook.py` passaram sem ressalva. A tabela "onde este kit para" e o rótulo de "narrativa não verificada" no [[b_reference_case_spo|caso de referência]] foram apontados como o ponto mais forte do kit.

## [kit v4] — 2026-07-30
Refatoração dirigida por auditoria adversarial do próprio kit. Cada item abaixo fecha um defeito **medido**, não uma impressão.

- **Corrigido — dois mecanismos para o mesmo trabalho.** `prompts/` foi dissolvida em `b_process/skills/`. Medição que motivou: `prompts/03-qa-adversarial` × `skills/guardrails-review` tinham 27% de sobreposição de vocabulário, e o ROTEIRO mandava carregar **os dois** na mesma sessão. `00`, `01`, `04`, `05` e `06` viraram skills (`bootstrap-contexto`, `planejador`, `auditor-evolucao`, `revisao-entrega`, `retrospectiva`); `02` foi absorvido pelo "Protocolo do agente" do [[a_context_source|CONTEXT]] (pago uma vez, vale para toda skill); `03` era subconjunto de `guardrails-review`.
- **Corrigido — rigor era prosa.** A auditoria contou **8 de 163** itens de checklist verificados por máquina (5%). `scripts/check.py` passou a reprovar também: **segredo versionado na árvore e no histórico do git**, `.gitignore` sem cobertura mínima, **nota órfã**, **ID citado que não existe** no DECISIONS, **ID duplicado**, e **"Em andamento" divergente** entre BACKLOG e CONTEXT.
- **Adicionado — `scripts/install_hook.py`.** Portão que só roda quando alguém lembra não é portão. O pre-commit torna a higiene o padrão; pular vira ato deliberado (`--no-verify`).
- **Corrigido — a lacuna de segurança mais barata do kit.** A skill `guardrails-review` exigia `git grep` por segredo como item de portão, e `check.py` tinha **zero** ocorrência de qualquer varredura. Agora varre 8 famílias de padrão, ignora `.example`/placeholder, e olha o histórico — segredo removido da árvore continua comprometido.
- **Corrigido — o kit violava a própria regra 6.** README × ROTEIRO tinham 30% de sobreposição, README × INICIO 28%. Agora cada documento tem um trabalho só: [[INDEX]] mapeia, [[a_roadmap|ROTEIRO]] conduz, [[README]] explica os porquês. "Papel do dono" e "frases de segurança" ficaram num lugar só.
- **Corrigido — 5 notas órfãs.** `b_process/profiles/` inteira, `contexto/LEIA-ME` e `dev/LEIA-ME` não eram linkadas por ninguém: num vault, nota que ninguém aponta é nota que ninguém lê. Ligadas, e o script agora reprova órfã nova.
- **Corrigido — WIP=1 reprovava time legítimo.** O limite passou a ser o **declarado** no cabeçalho do [[c_backlog|BACKLOG]] (`Em andamento (máx N)`); o script cobra esse número. Solo continua 1; time de 3 declara 3.
- **Adicionado — "Onde este kit para" no [[README]].** Tabela honesta: serve para app pequeno/médio de um dono; não serve para 30+ módulos, 100+ decisões, multi-repo ou CI. O kit dizia "aplicação" e era, na prática, "aplicação pequena a média, solo".
- **Corrigido — narrativa citada como medição.** Os números de [[b_reference_case_spo|caso de referência]] ("14 passagens", "84 achados") apareciam 10 vezes pelo kit sem um artefato anexado. O arquivo ganhou aviso de status epistêmico e o [[a_roadmap|ROTEIRO]] parou de usá-los como argumento. A distinção com [[a_scb_usage_analysis_260722_0000|ANALISE-USO-SCB]] — que é medição, com as próprias ressalvas — está explícita no README.
- **Adicionado — frente de vazamento/look-ahead** em `guardrails-review` (era a única frente do prompt 03 que a skill não cobria).

## [kit v3] — 2026-07-30
Passagem de agentes especializados + Obsidian. O kit deixou de ser só um conjunto de documentos e passou a ser um **vault operável com agentes instaláveis**.

- **Adicionado — `b_process/skills/`: 12 agentes instaláveis** (`SKILL.md` com frontmatter `name`/`description`, padrão Claude Code / Cowork): arquitetura-monolito, arquitetura-microservicos, backend-dominio, backend-bff, microservice-sync, frontend-uiux, frontend-mfe, autenticacao, iac-docker-terraform, testes, guardrails-review e dados-analise. Cada uma com regras numeradas, portão em checklist e armadilhas já pagas por projetos reais.
- **Adicionado — portões de existência.** As skills estruturais (microserviços, MFE) começam por um STEP 0 que pergunta *isto deve existir?* e **reprovam por padrão**. É o mecanismo que impede a IA de construir arquitetura que ninguém precisa.
- **Adicionado — [[a_roadmap|ROTEIRO]]:** o caminho executável do dia 1 à entrega, ligando fase → skill → portão. O README descrevia as fases numa tabela; faltava a ordem operável.
- **Adicionado — [[b_plan|PLANO]]:** o template que o README v2 já mandava gerar na Fase 1 mas que não existia no kit (lacuna real).
- **Adicionado — [[INDEX]] e [[a_obsidian_guide|Guia do Obsidian]]:** mapa de navegação e manual do vault.
- **Adicionado — [[b_reference_case_spo|caso de referência]]:** caso de referência destilado de um app real (10 dias, 14 passagens de revisão, 84 achados) — aferição do que "pronto" significa e lista de armadilhas já pagas.
- **Adicionado — `b_process/templates/`:** modelos para D-NN, QA-NN e **fecho de sessão** (o ritual que estava descrito em prosa em 4 arquivos e agora é um clique via plugin Templates).
- **Adicionado — `scripts/new_project.py`:** copia o kit para um projeto novo excluindo o que é só do kit (`docs/`, `exemplos/`, `.git`) e zerando os templates. O passo 1 do README era manual e propenso a levar lixo junto.
- **Adicionado — Obsidian:** `.obsidian/` versionado (abre em [[INDEX]], favoritos, grafo com cores por tema, Templates apontando para `b_process/templates/`), frontmatter `tags`/`status` em toda nota e wikilinks no lugar de caminhos.
- **Expandido — [[b_checklist|CHECKLIST]]:** de genérico para **portões em camadas** (arquitetura, domínio, borda, frontend, auth, infra, entrega), espelhando o portão de cada skill.
- **Expandido — [[d_agent_learnings|APRENDIZADOS]]:** lições de aplicação (dinheiro inteiro, segredo por instalação, expand/contract, artefato pronto em vez de build no cliente).
- **Expandido — `scripts/check.py`:** valida skills (frontmatter `name`/`description`), **wikilinks quebrados**, frontmatter ausente e placeholders não preenchidos, além do que já validava.
- **Corrigido — changelog com dois donos.** O `d_history/a_changelog.md` da raiz acumulava o histórico do kit *e* servia de template para o projeto; ao copiar o kit, o projeto novo nascia com a história de outra coisa. Agora: kit aqui, projeto lá.

## [kit v2.1] — 2026-07-22
- Generalização: `perfil-generico.md` (método p/ qualquer stack), prompt `04` sem viés estatístico, `RUNBOOK.md` exigido na entrega de projeto que opera, modo curto p/ projetos pequenos, arquivamento do DECISIONS em projeto longo (+ checagem no script), roteiro "primeiro dia" no README.

## [kit v2.0] — 2026-07-22
- Refatoração pós-SCB: orçamentos numéricos de contexto, estado em fonte única, prompts imperativos (~metade do custo), regra "observe antes de construir", `b_process/d_agent_learnings.md` + prompt de retrospectiva, `scripts/check.py`. Evidências medidas: [[a_scb_usage_analysis_260722_0000|ANALISE-USO-SCB]].

## [kit v1] — baseline
- Kit original, pré-refatoração (568 linhas). O que funcionou e o que falhou está medido em [[a_scb_usage_analysis_260722_0000|ANALISE-USO-SCB]].
