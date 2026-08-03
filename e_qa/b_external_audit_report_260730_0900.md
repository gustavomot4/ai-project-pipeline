---
tags: [auditoria, evidencia, externa]
status: historico
data: 2026-07-30
---
# Auditoria externa adversarial do kit — 2026-07-30

> **Estado: corrigido.** Este laudo avaliou o commit `51c272a` (kit v4) e deu **58/100**.
> Os 8 itens da tabela "Correções, em ordem de retorno" foram aplicados na **v5** e verificados
> por teste — ver [[b_kit_changelog|CHANGELOG-KIT]]. Os números abaixo descrevem o kit **antes**
> da correção e ficam registrados como estavam: relatório que se reescreve depois do conserto
> não serve como evidência. O que mudou, medido:
>
> | Achado | v4 (medido) | v5 (medido) |
> |---|---|---|
> | Segredos reais detectados | 0 de 8 | **8 de 8** (0 falso-positivo em 12 iscas) |
> | `--historico-completo` | varria 0 commits | varre todos |
> | Markdown do app bloqueando commit | sim (FALHA) | não (AVISO, só no vault) |
> | `checar.py` com CSV de 17 MB ignorado | 12,3 s | **1,5 s** |
> | Timeout do `git log` | `pass` silencioso | aviso explícito |
> | Template do `CONTEXT.md` vazio | 3.541 / 4.000 chars | **2.677 / 4.000** |
> | Contrato de leitura do agente | ausente | `CLAUDE.md` |

**Postura:** tudo é considerado falho até prova executada. Nada aqui é opinião: cada afirmação
tem comando rodado, número medido ou linha de código citada. O kit não recebe crédito por ter
sido escrito por um LLM, nem desconto por isso.

**Método:** leitura integral dos 45 arquivos `.md`/`.py` (2.388 linhas), execução de
`scripts/checar.py` em 6 cenários construídos, criação de projeto real via `novo-projeto.py`,
plantio de segredos, medição de sobreposição textual entre as 17 skills por 6-gramas,
e teste de carga com repositório de 120 commits e artefatos de 17 MB / 200 MB.

---

## Placar

| # | Quesito | Nota | Veredito em uma linha |
|---|---|---:|---|
| 1 | **Segurança (varredura de segredo)** | **18** | Reprovado. 0 de 8 segredos reais detectados; a flag de varredura profunda varre zero commits. |
| 2 | Qualidade dos scripts | **44** | `checar.py` tem bug funcional e falsos-positivos que treinam o usuário a burlar o portão. |
| 3 | Escalabilidade (P/M/G) | **55** | Pequeno sim, médio com atrito, grande não — e o próprio kit já admite. |
| 4 | Gasto de tokens | **64** | Doutrina boa e medível; ~2.400 tokens/sessão de custo fixo não contabilizado. |
| 5 | Utilidade real | **69** | Vale como disciplina; ~9% dos itens têm trava automática. |
| 6 | Organização do projeto | **80** | Fonte única, IDs rastreáveis e mapa de leitura funcionam de verdade. |
| 7 | Enxutez (nada inútil ocupando espaço) | **82** | 177 KB, zero arquivo morto. Ponto mais forte junto com o próximo. |
| 8 | Honestidade da documentação | **85** | Declara os próprios limites e marca o que não foi verificado. Raro. |
| | **Média ponderada** | **58** | Doutrina sólida, automação quebrada. |

Ponderação usada: segurança e scripts ×2 (são o que o kit promete automatizar), demais ×1.

---

## 1 — Segurança: 18/100

### 1.1 O scanner de segredo detecta 0 de 8 segredos reais [verificado]

Plantei 8 segredos em formato realista num `.md` versionado e rodei `scripts/checar.py`.

> **As iscas abaixo estão inutilizadas de propósito** — o corpo de cada token virou `XXXX`.
> A primeira versão deste laudo trazia as iscas intactas e o **push protection do GitHub barrou
> o push**, classificando duas delas como "Stripe API Key" e "Stripe Live API Restricted Key".
> Estavam marcadas com `checar:ignore`, o que calou o scanner do kit e não calou o do GitHub —
> corretamente. Amostra de segredo em documentação se **inutiliza**, não se isenta. Lição
> incorporada em [[d_agent_learnings|APRENDIZADOS]].

| # | Formato plantado | O que ele exercita |
|---|---|---|
| 1 | `DB_PASSWORD = "<senha>"` com `# ver <ticket-4412>` no fim | comentário com `<>` desligava a linha inteira |
| 2 | `API_KEY=<chave-estilo-stripe>` **sem aspas** | formato `.env`, o vazamento mais comum |
| 3 | `SECRET_KEY=<valor-sem-aspas>` com prefixo de framework | valor sem aspas e sem prefixo conhecido |
| 4 | `DATABASE_URL = "postgres://admin:<senha>@prod.db:5432/main"` | senha em connection string |
| 5 | `Authorization: Bearer <jwt>` | JWT em três segmentos |
| 6 | `STRIPE_SK = "<chave-restrita-stripe>"` entre aspas | prefixo `rk_live`, ausente dos padrões |
| 7 | `password: "<senha>"` com `# TODO xxx revisar` no fim | `xxx` no comentário desligava a linha |
| 8 | `api_key: "<chave>"` com `# não é exemplo` no fim | a palavra "exemplo" desligava a linha |

Os valores de teste reais (com entropia, para exercitar os padrões de verdade) vivem nos comandos
da suíte de regressão, fora do repositório — é lá que o número 8/8 é reproduzido.

**Resultado: 8 plantados → 0 detectados.** Saída do script: `OK: ... segredos ...`, exit 0,
commit liberado. Duas causas, ambas em `scripts/checar.py`:

**(a) O filtro anti-falso-positivo é largo demais** (linha 158):

```python
EXEMPLO = re.compile(r"(?i)\.example|\.sample|<[^>]*>|xxx+|change[_-]?me|your[_-]|placeholder|exemplo|EXEMPLO")
```

Ele descarta a **linha inteira**. Qualquer linha que contenha `<...>`, `xxx`, ou a palavra
"exemplo" fica invisível — inclusive `DB_PASSWORD = "SenhaXXX" # ver <ticket-4412>` e
`password: "SenhaXXX" # TODO xxx revisar`. Comentário de código derruba a checagem.

**(b) Os padrões exigem aspas e cobrem poucos formatos** (linha 151):

O regex de chave literal termina em `\s*[:=]\s*['\"]`. O formato mais comum de vazamento no
mundo — a linha de `.env` sem aspas, `API_KEY=sk_live_...` — **não é coberto**. Também ausentes:
connection string com senha embutida (`postgres://user:senha@host`), JWT/Bearer, e prefixos
Stripe reais (`sk_live_`, `rk_live_` usam underscore; o padrão do script exige `sk-` com hífen).

Único acerto na bateria: `aws_secret_access_key:` com aspas e sem comentário na linha.

### 1.2 `--historico-completo` varre ZERO commits [verificado] — bug funcional

`scripts/checar.py:182`:

```python
PROFUNDIDADE = "0" if "--historico-completo" in sys.argv else "30"
```

Isso monta `git log -p -0`, que em git significa **zero commits**, não "todos". Medido:

```
git log -p -0     ->         0 bytes de diff
git log -p -30    ->      8215 bytes
git log -p -1000  ->    171535 bytes
```

Sintoma que confirma: `--historico-completo` roda em **0,33 s** contra 1,49 s do modo padrão.
A varredura "completa" é mais rápida porque não varre nada.

**Impacto:** esta é exatamente a flag de que a Fase 6 (`skills/revisao-entrega`) depende para
cumprir a promessa "segredo na árvore **e no histórico**". Quem rodar a varredura profunda antes
de entregar recebe `OK: ... segredos ...` sem que um único commit tenha sido lido.

**Correção:** `PROFUNDIDADE = "" if "--historico-completo" in sys.argv else "-30"` e usar o valor
direto (omitindo o argumento quando vazio), ou `"--all"`.

### 1.3 Falha aberta com mensagem verde

Dois caminhos onde o portão passa sem ter checado, e o usuário lê "OK":

- **Janela de 30 commits:** plantei um segredo, removi da árvore, e fiz 35 commits depois.
  Detectado em `t+2`; **invisível em `t+35`**, com exit 0. Segredo comprometido continua
  comprometido — o kit sabe disso (a própria mensagem de erro diz), mas para de olhar.
- **`except (subprocess.SubprocessError, OSError): pass`** (linha 194): se o `git log` estourar
  o `timeout=25`, a exceção é engolida **sem aviso** e a mensagem final continua listando
  "segredos" entre os itens aprovados.

Isto é o anti-padrão que a própria `skills/guardrails-review` classifica como achado (frente 6,
"erros silenciosos" / "fallback que mascara falta de dado"). O kit reprova a si mesmo.

### 1.4 O que está certo, para registro

`.gitignore` é bem construído e cobre o que precisa; a checagem nº 10 (cobrir `.env`, `*.pem`,
`*.key`, `id_rsa`, `credentials.json`, `*.p12`) funciona e é uma boa trava barata. A intenção do
desenho está correta — a implementação é que não sustenta.

---

## 2 — Qualidade dos scripts: 44/100

### 2.1 A checagem que mais dispara é a de menor valor — e destrói o portão inteiro

`checar.py` reprova qualquer `.md` que nenhum wikilink aponte ("nota órfã"). Num vault isso faz
sentido. **Num projeto de código, não.** Teste com estrutura banal:

```
content/blog/faq.md · content/blog/guia.md · content/blog/tutorial.md
content/blog/politica-de-privacidade.md · src/pagamentos/NOTAS.md
→ FALHOU: 5 notas órfãs · exit 1 · commit bloqueado
```

Um site Next.js com conteúdo em markdown, um monorepo com doc por pacote, uma pasta `docs/` de
API — todos bloqueiam **todo commit**, para sempre, por um motivo cosmético. O usuário tem duas
saídas: editar o script, ou adotar `git commit --no-verify` por hábito. A segunda é a que
acontece — e ela desliga junto a varredura de segredo, o orçamento e a fonte única.

**Este é o achado de maior impacto prático do laudo**, acima até do 1.2: um portão que
o usuário aprende a pular não é um portão degradado, é um portão ausente com falsa sensação
de cobertura.

**Correção:** rebaixar "nota órfã" de FALHA para AVISO, e restringir o escopo a `.md` na raiz
e nas pastas do kit (`contexto/`, `dev/`, `templates/`, `perfis/`, `skills/`).

### 2.2 O script ignora o `.gitignore` [verificado]

`IGNORAR` (linha 30) é uma lista fixa de 9 nomes. Não lê `.gitignore` — nem o que o próprio kit
escreve nele. Consequências medidas:

| Cenário | Medido |
|---|---|
| `open-data/` com CSV de 17 MB (ignorado no `.gitignore` do kit!) | **12,3 s por commit** |
| `.terraform/` com provider de 200 MB (o kit tem skill de IaC) | 4,1 s e **402 MB de RSS** |

`p.read_text()` (linha 176) carrega o arquivo **inteiro** em memória antes de tentar decodificar.
Um dump de banco, uma imagem Docker exportada ou um `.bin` de modelo de alguns GB fazem o
pre-commit hook consumir memória proporcional ao maior arquivo do repositório. Sem cap de tamanho,
sem checagem de binário por magic bytes, sem `git check-ignore`.

**Correção:** trocar `visiveis()` por `git ls-files` quando houver `.git`, e pular arquivos
acima de ~1 MB.

### 2.3 Falso-positivo em ID citado

Citar um `QA-07` de projeto anterior em `APRENDIZADOS.md` (uso legítimo e previsto pelo próprio
arquivo, que fala em "lições herdadas") reprova o commit. `docs/` é isento na linha 218;
`APRENDIZADOS.md` não é.

### 2.4 O que está certo

- **`novo-projeto.py`: aprovado sem ressalva.** Rodei de verdade: 49 arquivos, remove `.git`,
  `docs/`, `exemplos/`, e a função `deslinkar()` converte os wikilinks órfãos corretamente —
  o projeto novo nasce passando no `checar.py`. Testei o caminho contrário (cópia manual com `cp`)
  e ele produz 6 wikilinks quebrados. O script resolve um problema real, e resolve certo.
- **`instalar-hook.py`: aprovado.** Detecta hook pré-existente de outra origem e se recusa a
  sobrescrever, marca o próprio hook, tem `--remover` idempotente, usa `rev-parse --git-path`
  (funciona em worktree). Bem escrito.
- `checar.py` roda em 0,29 s no kit limpo e as 13 checagens têm mensagens de erro que dizem
  o que fazer, não só o que quebrou. A engenharia de mensagem é boa.

---

## 3 — Escalabilidade: 55/100

Preenchi o `CONTEXT.md` com conteúdo realista e enxuto e medi:

| Porte | `CONTEXT.md` preenchido | Cabe em 4.000? | Veredito |
|---|---:|---|---|
| Pequeno (3 módulos, 1 questão) | 3.512 chars | sim, sobram 488 | **funciona** |
| Médio (8 módulos, 3 temas, 3 questões) | 3.681 chars | sim, sobram 319 | **funciona, sem folga** |
| Grande (30+ módulos) | — | não | reprovado, como o próprio README declara |

O ponto que o kit não declara: **o template vazio já ocupa 3.541 dos 4.000 chars.** A margem
de manobra vem só de trocar placeholder por texto de tamanho parecido. Um projeto com 5 restrições
inegociáveis em vez de 1, ou 4 critérios de aceite em vez de 3, estoura — e a orientação
("excedente vai para `contexto/<tema>.md`") não vale para restrições e critérios, que são
justamente o que precisa estar no arquivo que toda sessão carrega.

Do orçamento, **1.204 chars (30%) são boilerplate idêntico em todo projeto** — "Mapa de leitura"
+ "Protocolo do agente". É instrução ao agente ocupando o espaço reservado a contexto de projeto.
Em ferramenta que suporta skills, esse bloco deveria viver numa skill base, não no `CONTEXT`.

Outros tetos: `DECISIONS.md` a 12.000 chars ≈ 66 linhas, com arquivamento **manual**; o kit
assume **um repositório** (monorepo e multi-repo quebram a regra de fonte única). Ambos declarados
no README.

---

## 4 — Gasto de tokens: 64/100

### 4.1 O que é medível e está certo

Sobreposição textual entre as 17 skills, medida por 6-gramas idênticos nos 136 pares:

```
maior par:            1,5%  (backend-bff <-> backend-dominio)
mediana:              0,2%
pares acima de 10%:   0
linhas idênticas em 4+ skills: 0
```

A v4 afirma ter eliminado os "27% de sobreposição entre prompt de QA e skill de guardrails".
**A afirmação se sustenta.** Não há duplicação paga duas vezes. Também confirmados como bem
desenhados: histórico fora do contexto, leitura sob demanda, regra do delta.

### 4.2 O custo fixo que ninguém contabiliza

O kit contabiliza o que carrega **dentro** da sessão e ignora o que a ferramenta carrega **por
fora**. Instaladas como skills (o caminho recomendado em `skills/LEIA-ME.md`), as 17 `description`
ficam no prompt de sistema de **toda** sessão:

```
17 descriptions somadas: 7.260 chars ≈ 2.420 tokens (PT-BR, ~3 chars/token)
orçamento do CONTEXT.md:  4.000 chars ≈ 1.333 tokens
→ o custo fixo invisível é 1,8× o orçamento que o kit controla com rigor
```

O kit fiscaliza 4.000 caracteres com script e hook de commit enquanto 7.260 passam sem menção.
Não invalida a doutrina — mas a regra 1 ("contexto com orçamento em número") não está sendo
aplicada à maior parcela fixa do custo.

*Ressalva de método: não consegui rodar um tokenizador real (rede bloqueada no sandbox). Usei a
razão ~3 chars/token que o próprio kit adota em `docs/ANALISE-USO-SCB.md`. Tokenizadores modernos
tendem a 3,2–3,5 em PT-BR, o que torna a estimativa conservadora — o custo real é ligeiramente
menor, e a conclusão de proporção não muda.*

### 4.3 Detalhe menor

8 wikilinks `[[...]]` dentro de 4 dos 17 `SKILL.md`. Instalados fora do Obsidian, viram referência
morta que o agente lê e paga.

---

## 5 — Utilidade real: 69/100

**A cobertura automática é de ~9%, não dos 100% que "portão" sugere.** Contagem:

```
itens '- [ ]' em CHECKLIST.md:        69
itens '- [ ]' em skills/*/SKILL.md:  104
total no kit:                        188
checagens automáticas em checar.py:   16 (13 falhas + 3 avisos)
```

O README declara "~160 itens, o script julga cerca de vinte" — a ordem de grandeza está certa,
os números estão desatualizados (188, e o `instalar-hook.py` ainda cita 163). Imprecisão, não
inflação: **a afirmação erra contra o próprio kit**, o que é o sinal certo.

O que sobra é doutrina — e a doutrina é boa. `skills/guardrails-review` tem 12 frentes de ataque
concretas ("ausente virou 0/''/hoje?", "dinheiro em float", "hora local gravada como UTC",
"retry duplicando efeito") com tabela de severidade e portão que exige relatório em disco.
`APRENDIZADOS.md` traz 15 lições herdadas específicas e caras, não platitudes.
As `description` das skills seguem o padrão correto de disparo (*use quando · dispare quando ·
não use para*) — é o formato que de fato faz uma skill acionar na hora certa.

**Mas o valor é 100% dependente de disciplina humana.** Isso é o que o kit é: um kit de
disciplina com 16 travas. O README diz exatamente isso na linha 23. A nota não é mais alta porque
"útil" foi medido contra a promessa de "portão", e a maioria dos portões é honorária.

### Uma lacuna estrutural não declarada

Não existe `CLAUDE.md` nem `AGENTS.md` no kit. Um agente aberto na pasta do projeto **não carrega
o `CONTEXT.md` sozinho** — depende do dono anexar manualmente, toda sessão. O "Protocolo do
agente" está escrito dentro do arquivo que o agente só lê se alguém o entregar. Um `CLAUDE.md` de
10 linhas apontando para o `CONTEXT.md` e proibindo varredura do repositório fecharia isso quase
de graça, e é a maior melhoria de custo-benefício disponível no kit hoje.

---

## 6 — Organização: 80/100

Funciona e é o núcleo defensável. Cada arquivo tem uma responsabilidade e não a divide:
estado no `CONTEXT`, histórico no `CHANGELOG`, decisão no `DECISIONS`, tarefa no `BACKLOG`,
evidência em `dev/`. A regra de fonte única não é só prosa — o script compara "Em andamento" entre
`BACKLOG` e `CONTEXT` e reprova divergência, que é precisamente a falha documentada e medida em
`docs/ANALISE-USO-SCB.md` (dois BACKLOGs, "63 testes" convivendo com "85 testes"). A trava existe
porque o problema aconteceu, e ela ataca a causa.

`D-NN` append-only com `SUPERSEDE`, `Q-NN` para o que é decisão do dono, `QA-NN` citado no commit:
os três resolvem problemas distintos e reais. O `ROTEIRO` é executável de verdade — cada fase diz
qual skill, o que entregar e qual portão fecha. Um kit de processo que erra nisso é comum;
este acerta.

Descontos: teto de 12.000 chars com arquivamento manual; `CHECKLIST` de 69 itens que na prática
ninguém percorre inteiro; nenhuma noção de atribuição por pessoa.

---

## 7 — Enxutez: 82/100

**Não encontrei arquivo morto, duplicado ou de enchimento.** 54 arquivos, 177 KB de conteúdo,
856 KB com `.git`. Cada arquivo do `INICIO.md` existe e é referenciado. Verificações feitas:

- `.obsidian/workspace.json` (5 KB de estado de sessão): corretamente ignorado, **não rastreado**
  no git — confirmado com `git ls-files`. O comentário no `.gitignore` explicando *por que* a
  config do vault é versionada e o estado não é a marca de quem pensou no problema.
- `novo-projeto.py` deixa `docs/` e `exemplos/` para trás: o projeto novo recebe 368 KB, não a
  análise de outro projeto.
- Zero `.bak`/`.tmp`/`.orig`/`__pycache__`.
- 6 commits, cada um uma versão coerente do kit.

Descontos pequenos: 8 wikilinks mortos dentro dos `SKILL.md`; `dev/` e `contexto/` nascem com
`LEIA-ME` e nada mais (justificável — são convenção); os 30% de boilerplate dentro do `CONTEXT`
já contados no quesito 4.

---

## 8 — Honestidade da documentação: 85/100

O quesito em que o kit mais se distingue, e é preciso dizer por quê:

- **Tabela "Onde este kit para"** no README, antes de qualquer venda: seis linhas de "não serve",
  incluindo o veredito **Não** para app grande e multi-repo.
- **`exemplos/caso-spo` marcado como narrativa não verificada**, com a frase "os números vêm de
  relato, sem relatório nem commit anexado. Use como lista de armadilhas plausíveis, não como
  aferição". Separar medição de anedota, e rotular a própria anedota, é o oposto do padrão.
- **`docs/ANALISE-USO-SCB.md` tem seção "Ressalvas sobre o próprio SCB"** com um item marcado
  `[suspeita]` e a admissão "auto-avaliação generosa".
- **A limitação mais desfavorável está no corpo do README**, não em rodapé: "o script julga cerca
  de vinte [de ~160]. Isto é um kit de disciplina com algumas travas automáticas — não um sistema
  que impede erro."

Descontos: os números `~160` / `163` estão desatualizados (188 hoje); `INICIO.md:48` afirma que
`checar.py` "reprova segredo versionado" — verdadeiro na letra, mas a taxa medida de 0/8 torna a
frase enganosa na prática; e a Fase 6 promete varredura de histórico que a flag correspondente
não executa.

---

## Correções, em ordem de retorno

| # | Onde | O quê | Custo |
|---|---|---|---|
| 1 | `checar.py:182` | `-0` varre zero commits. Trocar por omissão do flag ou `--all`. | 1 linha |
| 2 | `checar.py:134-144` | "Nota órfã" de FALHA → AVISO, limitada às pastas do kit. **É o que impede o `--no-verify` habitual.** | ~5 linhas |
| 3 | `checar.py:151,158` | Cobrir `.env` sem aspas, connection string, JWT, `sk_live_`/`rk_live_`. Aplicar `EXEMPLO` só ao trecho casado, nunca à linha inteira. | ~15 linhas |
| 4 | `checar.py:172-178` | Usar `git ls-files` quando houver `.git`; pular arquivo > 1 MB. Elimina os 12,3 s e o pico de 402 MB. | ~8 linhas |
| 5 | `checar.py:194` | Timeout do `git log` não pode virar `pass` silencioso — vire aviso ou falha. | 2 linhas |
| 6 | raiz | Criar `CLAUDE.md` apontando para `CONTEXT.md` e proibindo varredura do repo. Fecha a dependência de o dono anexar tudo à mão. | ~10 linhas |
| 7 | `CONTEXT.md` | Mover "Protocolo do agente" (780 chars) para skill base ou `CLAUDE.md`; devolve 20% do orçamento. | recorte |
| 8 | `README.md:23`, `instalar-hook.py:7` | Atualizar `~160`/`163` para 188. | 2 linhas |

Itens 1 a 3 são pré-requisito para o kit poder afirmar qualquer coisa sobre segurança.

---

## Veredito

**A doutrina do kit está acima da média e a automação está abaixo do que ela promete.**

O que foi construído com julgamento — a separação de responsabilidades por arquivo, os IDs
rastreáveis, o orçamento numérico, as 17 skills sem sobreposição medível, o `novo-projeto.py`,
a tabela de limites — resiste a inspeção adversarial e resolve problemas que o próprio histórico
do autor documenta. Isso não é teatro de processo.

O que foi construído como código de verificação não resiste: o portão de segredo é decorativo
(0/8), a varredura profunda é uma no-op, e a checagem que mais dispara é cosmética e ensina o
usuário a desligar todas as outras. Um kit cuja tese central é "nada avança sem portão objetivo"
tem, hoje, portões que passam com mensagem verde sem ter checado.

**Serve para:** app pequeno ou médio, um dono, com o dono efetivamente rodando o `CHECKLIST` à mão.
**Não serve, hoje, para:** ser confiado como rede de segurança contra vazamento de segredo.

Com as correções 1 a 4, este laudo passaria de 58 para a faixa de 75.

---

## Pós-escrito: o kit reprovou este laudo, pelos dois motivos descritos nele

Rodei `scripts/checar.py` com este arquivo dentro de `dev/`. Resultado:

```
FALHOU:
 - Nota(s) órfã(s) — ninguém linka, então ninguém lê: dev/AUDITORIA-EXTERNA-2026-07-30.md
 - Possível segredo versionado: dev/AUDITORIA-EXTERNA-2026-07-30.md:74 (credencial AWS)
2 problema(s).
```

Não é ironia, é confirmação experimental dos achados 2.1 e 1.1:

1. **`dev/` é a pasta que o próprio kit designa para "evidências e relatórios de QA"** — e um
   relatório de QA colocado ali bloqueia o commit até que alguém escreva um wikilink para ele.
   O falso-positivo atinge o fluxo que o kit mais quer que aconteça.
2. **O único padrão de segredo que funciona disparou em prosa** que *descreve* o padrão. Enquanto
   8 segredos reais passavam ilesos, a documentação do teste foi barrada.

Resolvido do jeito que o kit manda (ponteiro em `dev/LEIA-ME.md`), não com `--no-verify`.

---

*Auditoria conduzida em 2026-07-30 contra o commit `51c272a`. Todos os cenários de teste são
reproduzíveis a partir dos comandos citados. Ressalva contra este próprio laudo: a avaliação de
"utilidade real" e de "organização" é julgamento estrutural, não medição — só o uso do kit em
um projeto completo comprova ou refuta. As notas de segurança, scripts, tokens e enxutez são
sustentadas por número medido.*
