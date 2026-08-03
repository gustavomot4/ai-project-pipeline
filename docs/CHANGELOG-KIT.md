---
tags: [changelog, kit]
status: atual
---
# CHANGELOG do KIT — histórico do próprio pipeline

> **Este arquivo é do kit, não do seu projeto.** O histórico do projeto que você constrói mora no [[CHANGELOG]] da raiz, que nasce zerado.
> `docs/` não é copiada para projetos novos (`scripts/novo-projeto.py` a exclui) — por isso o histórico do kit vive aqui e nunca polui o changelog do projeto.
> Regra de evolução: lição que aparece em 2+ projetos vira regra do kit e ganha uma entrada aqui. Ver [[README]] → "Como o kit evolui".

## [kit v5] — 2026-07-30
Correções dirigidas pela **auditoria externa adversarial** registrada em [[docs/AUDITORIA-EXTERNA-2026-07-30|AUDITORIA-EXTERNA-2026-07-30]] (placar 58/100 no commit `51c272a`). A v4 declarou ter fechado a lacuna de segurança; a auditoria mediu que **não fechou**. Cada item abaixo tem teste executado antes e depois.

- **Corrigido (crítico) — `--historico-completo` varria ZERO commits.** `PROFUNDIDADE = "0"` montava `git log -p -0`, que em git significa nenhum commit, não todos. Sintoma que denunciava: a varredura "completa" rodava em 0,33 s contra 1,49 s da parcial. A flag de que a Fase 6 depende era uma no-op que imprimia `OK`. Agora o limite é omitido (varre tudo), com timeout de 120 s.
- **Corrigido (crítico) — o scanner de segredo detectava 0 de 8 segredos reais.** Duas causas: (a) o filtro anti-exemplo descartava a **linha inteira**, então um comentário `# ver <ticket-4412>` ou `# TODO xxx` desligava a checagem — agora ele avalia **só o trecho casado**; (b) os padrões exigiam aspas, e a linha de `.env` (`API_KEY=sk_live_…`), o formato mais comum de vazamento, passava — agora valor sem aspas também casa (com exigência de dígito, para não casar com prosa). Novas famílias: senha em connection string, JWT, Stripe `sk_live`/`rk_live`, GitLab PAT. **Medido: 8/8 detectados, 0/12 falsos-positivos.** Isenção explícita por linha com a marca `checar:ignore` — para o que é **comprovadamente inerte**, não para amostra que só parece falsa: essa se inutiliza trocando o corpo do token por `XXXX`. O push protection do GitHub barrou o primeiro push deste laudo justamente por iscas isentadas mas intactas, e estava certo (lição em [[APRENDIZADOS]]).
- **Corrigido (crítico de uso) — "nota órfã" era FALHA e varria o repositório inteiro.** Qualquer `content/blog/*.md`, doc de pacote ou `NOTAS.md` de módulo do próprio app bloqueava **todo** commit por motivo cosmético. O efeito real não é atrito: é o dono adotar `git commit --no-verify` por hábito e desligar junto o portão de segredo, o orçamento e a fonte única. Virou **AVISO**, e só dentro do vault.
- **Corrigido — o script ignorava o `.gitignore`.** `IGNORAR` era uma lista fixa de 9 nomes. Um CSV de 17 MB em `open-data/` (que o próprio `.gitignore` do kit exclui!) custava **12,3 s em cada commit**; um provider Terraform de 200 MB, 402 MB de RSS. Agora o universo da varredura é `git ls-files --cached --others --exclude-standard`, e arquivo acima de 1 MB é pulado **com aviso** — nunca em silêncio. **Medido: 12,3 s → 1,5 s.**
- **Corrigido — falha aberta com mensagem verde.** O `except … : pass` no `git log` engolia timeout e erro, e a linha final continuava listando "segredos" entre os itens aprovados. É o anti-padrão que a própria `guardrails-review` classifica como achado (frente 6). Agora vira aviso explícito, e a mensagem de sucesso **declara o alcance**: "árvore versionada + últimos 30 commits".
- **Corrigido — falso-positivo de ID.** Citar um `QA-07` herdado em [[APRENDIZADOS]] reprovava o commit, contra a orientação do próprio arquivo. `dev/` e `APRENDIZADOS` entraram na isenção que `docs/` já tinha.
- **Corrigido — o hook bloqueava TODO commit no Windows.** Achado em uso real, não em teste: `command -v python3` encontra o *App Execution Alias* que o Windows instala em `WindowsApps` — um `python3.exe` que está no PATH, não executa nada e imprime "Python não foi encontrado; executar sem argumentos para instalar do Microsoft Store". O hook tomava o stub por interpretador e reprovava commits limpos. É a mesma doença dos outros achados, com o sinal trocado: falha **fechada** pelo motivo errado empurra para `--no-verify` tão rápido quanto falha aberta. Agora o hook testa se o candidato **roda** (`python3` → `python` → `py`, o Launcher do Windows), não se ele existe; sem nenhum Python funcional, avisa alto e deixa passar — ambiente quebrado não é commit sujo, e confundir os dois foi o defeito.
- **Adicionado — `.gitattributes`.** `* text=auto eol=lf`: o repositório guarda LF e o Windows fica com CRLF na cópia local. Elimina o aviso em todo `git add` e impede que um shell script versionado com CRLF quebre no Git Bash.
- **Adicionado — `CLAUDE.md`.** Não havia contrato de leitura: um agente aberto na pasta não carregava o [[CONTEXT]] sozinho, e o "Protocolo do agente" morava dentro do arquivo que o agente só lia se alguém o entregasse à mão.
- **Corrigido — 20% do orçamento do CONTEXT era instrução ao agente.** O "Protocolo do agente" (780 chars) saiu do [[CONTEXT]] para o `CLAUDE.md`. O template vazio ocupava **3.541 dos 4.000 chars**; agora sobra margem real para contexto de projeto.
- **Corrigido — números desatualizados.** "~160 itens" / "8 de 163" viraram a contagem medida: **188** itens de checklist no kit, **16** com trava automática (~9%).

> **O que a auditoria aprovou, para registro:** sobreposição entre as 17 skills medida em **0,2% de mediana** por 6-gramas, zero pares acima de 10% — a promessa da v4 se sustenta. `novo-projeto.py` e `instalar-hook.py` passaram sem ressalva. A tabela "onde este kit para" e o rótulo de "narrativa não verificada" no [[exemplos/caso-spo]] foram apontados como o ponto mais forte do kit.

## [kit v4] — 2026-07-30
Refatoração dirigida por auditoria adversarial do próprio kit. Cada item abaixo fecha um defeito **medido**, não uma impressão.

- **Corrigido — dois mecanismos para o mesmo trabalho.** `prompts/` foi dissolvida em `skills/`. Medição que motivou: `prompts/03-qa-adversarial` × `skills/guardrails-review` tinham 27% de sobreposição de vocabulário, e o ROTEIRO mandava carregar **os dois** na mesma sessão. `00`, `01`, `04`, `05` e `06` viraram skills (`bootstrap-contexto`, `planejador`, `auditor-evolucao`, `revisao-entrega`, `retrospectiva`); `02` foi absorvido pelo "Protocolo do agente" do [[CONTEXT]] (pago uma vez, vale para toda skill); `03` era subconjunto de `guardrails-review`.
- **Corrigido — rigor era prosa.** A auditoria contou **8 de 163** itens de checklist verificados por máquina (5%). `scripts/checar.py` passou a reprovar também: **segredo versionado na árvore e no histórico do git**, `.gitignore` sem cobertura mínima, **nota órfã**, **ID citado que não existe** no DECISIONS, **ID duplicado**, e **"Em andamento" divergente** entre BACKLOG e CONTEXT.
- **Adicionado — `scripts/instalar-hook.py`.** Portão que só roda quando alguém lembra não é portão. O pre-commit torna a higiene o padrão; pular vira ato deliberado (`--no-verify`).
- **Corrigido — a lacuna de segurança mais barata do kit.** A skill `guardrails-review` exigia `git grep` por segredo como item de portão, e `checar.py` tinha **zero** ocorrência de qualquer varredura. Agora varre 8 famílias de padrão, ignora `.example`/placeholder, e olha o histórico — segredo removido da árvore continua comprometido.
- **Corrigido — o kit violava a própria regra 6.** README × ROTEIRO tinham 30% de sobreposição, README × INICIO 28%. Agora cada documento tem um trabalho só: [[INICIO]] mapeia, [[ROTEIRO]] conduz, [[README]] explica os porquês. "Papel do dono" e "frases de segurança" ficaram num lugar só.
- **Corrigido — 5 notas órfãs.** `perfis/` inteira, `contexto/LEIA-ME` e `dev/LEIA-ME` não eram linkadas por ninguém: num vault, nota que ninguém aponta é nota que ninguém lê. Ligadas, e o script agora reprova órfã nova.
- **Corrigido — WIP=1 reprovava time legítimo.** O limite passou a ser o **declarado** no cabeçalho do [[BACKLOG]] (`Em andamento (máx N)`); o script cobra esse número. Solo continua 1; time de 3 declara 3.
- **Adicionado — "Onde este kit para" no [[README]].** Tabela honesta: serve para app pequeno/médio de um dono; não serve para 30+ módulos, 100+ decisões, multi-repo ou CI. O kit dizia "aplicação" e era, na prática, "aplicação pequena a média, solo".
- **Corrigido — narrativa citada como medição.** Os números de [[exemplos/caso-spo]] ("14 passagens", "84 achados") apareciam 10 vezes pelo kit sem um artefato anexado. O arquivo ganhou aviso de status epistêmico e o [[ROTEIRO]] parou de usá-los como argumento. A distinção com [[docs/ANALISE-USO-SCB|ANALISE-USO-SCB]] — que é medição, com as próprias ressalvas — está explícita no README.
- **Adicionado — frente de vazamento/look-ahead** em `guardrails-review` (era a única frente do prompt 03 que a skill não cobria).

## [kit v3] — 2026-07-30
Passagem de agentes especializados + Obsidian. O kit deixou de ser só um conjunto de documentos e passou a ser um **vault operável com agentes instaláveis**.

- **Adicionado — `skills/`: 12 agentes instaláveis** (`SKILL.md` com frontmatter `name`/`description`, padrão Claude Code / Cowork): arquitetura-monolito, arquitetura-microservicos, backend-dominio, backend-bff, microservice-sync, frontend-uiux, frontend-mfe, autenticacao, iac-docker-terraform, testes, guardrails-review e dados-analise. Cada uma com regras numeradas, portão em checklist e armadilhas já pagas por projetos reais.
- **Adicionado — portões de existência.** As skills estruturais (microserviços, MFE) começam por um STEP 0 que pergunta *isto deve existir?* e **reprovam por padrão**. É o mecanismo que impede a IA de construir arquitetura que ninguém precisa.
- **Adicionado — [[ROTEIRO]]:** o caminho executável do dia 1 à entrega, ligando fase → skill → portão. O README descrevia as fases numa tabela; faltava a ordem operável.
- **Adicionado — [[PLANO]]:** o template que o README v2 já mandava gerar na Fase 1 mas que não existia no kit (lacuna real).
- **Adicionado — [[INICIO]] e [[GUIA-OBSIDIAN]]:** mapa de navegação e manual do vault.
- **Adicionado — [[exemplos/caso-spo]]:** caso de referência destilado de um app real (10 dias, 14 passagens de revisão, 84 achados) — aferição do que "pronto" significa e lista de armadilhas já pagas.
- **Adicionado — `templates/`:** modelos para D-NN, QA-NN e **fecho de sessão** (o ritual que estava descrito em prosa em 4 arquivos e agora é um clique via plugin Templates).
- **Adicionado — `scripts/novo-projeto.py`:** copia o kit para um projeto novo excluindo o que é só do kit (`docs/`, `exemplos/`, `.git`) e zerando os templates. O passo 1 do README era manual e propenso a levar lixo junto.
- **Adicionado — Obsidian:** `.obsidian/` versionado (abre em [[INICIO]], favoritos, grafo com cores por tema, Templates apontando para `templates/`), frontmatter `tags`/`status` em toda nota e wikilinks no lugar de caminhos.
- **Expandido — [[CHECKLIST]]:** de genérico para **portões em camadas** (arquitetura, domínio, borda, frontend, auth, infra, entrega), espelhando o portão de cada skill.
- **Expandido — [[APRENDIZADOS]]:** lições de aplicação (dinheiro inteiro, segredo por instalação, expand/contract, artefato pronto em vez de build no cliente).
- **Expandido — `scripts/checar.py`:** valida skills (frontmatter `name`/`description`), **wikilinks quebrados**, frontmatter ausente e placeholders não preenchidos, além do que já validava.
- **Corrigido — changelog com dois donos.** O `CHANGELOG.md` da raiz acumulava o histórico do kit *e* servia de template para o projeto; ao copiar o kit, o projeto novo nascia com a história de outra coisa. Agora: kit aqui, projeto lá.

## [kit v2.1] — 2026-07-22
- Generalização: `perfil-generico.md` (método p/ qualquer stack), prompt `04` sem viés estatístico, `RUNBOOK.md` exigido na entrega de projeto que opera, modo curto p/ projetos pequenos, arquivamento do DECISIONS em projeto longo (+ checagem no script), roteiro "primeiro dia" no README.

## [kit v2.0] — 2026-07-22
- Refatoração pós-SCB: orçamentos numéricos de contexto, estado em fonte única, prompts imperativos (~metade do custo), regra "observe antes de construir", `APRENDIZADOS.md` + prompt de retrospectiva, `scripts/checar.py`. Evidências medidas: [[docs/ANALISE-USO-SCB|ANALISE-USO-SCB]].

## [kit v1] — baseline
- Kit original, pré-refatoração (568 linhas). O que funcionou e o que falhou está medido em [[docs/ANALISE-USO-SCB|ANALISE-USO-SCB]].
