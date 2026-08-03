---
tags: [padrao, processo, meta]
status: atual
tipo: padrao
data: 2026-08-03
aliases: ["Padrão do repositório", "Convenções"]
---
# Padrão do repositório — como todo projeto da equipe é organizado

> Padrão da equipe, aplicado a este kit em 2026-08-03. Quem lê isto: você, e todo agente de
> IA que abrir o repositório. `scripts/new_project.py` monta este esqueleto sozinho — os itens
> da seção 9 são executáveis, não uma lista para seguir à mão.

---

## 1. As 3 regras que sustentam o padrão

1. **Duas pastas, uma raiz limpa.** Toda documentação em `77777777_<TAG>_Project_DOCs/`; todo
   código em uma única pasta. Na raiz ficam só o `README.md`, o `CLAUDE.md` e a configuração
   do repositório.
2. **Uma verdade por assunto.** Cada informação tem **um** dono. Nenhum arquivo repete o que
   outro já diz — ele **aponta**. Duplicata é dívida: envelhece em silêncio e depois mente.
3. **O que não tem dono, não entra.** Arquivo sem papel definido (rascunho vazio, sonda
   descartável, cache, duplicata "por garantia") não é versionado. Se já entrou, sai — o
   histórico do git guarda.

O prefixo `77777777_` não é enfeite: é o que mantém a documentação **sempre no topo** da
árvore, acima de qualquer pasta de código, em qualquer explorador de arquivos.

---

## 2. Estrutura

```
<PROJETO>/
├── 77777777_<TAG>_Project_DOCs/   # documentação
│   ├── INDEX.md                   # nota-casa: mapa de navegação do vault
│   ├── a_context/                 # a VERDADE do projeto
│   ├── b_process/                 # como se TRABALHA (inclui skills/)
│   ├── c_technical_docs/          # runbooks, guias, evidências de operação
│   ├── d_history/                 # changelog datado
│   ├── e_qa/                      # relatórios de QA, com timestamp no nome
│   └── scripts/                   # check.py · install_hook.py
├── <pasta_de_codigo>/             # todo o código + seu README técnico
│   ├── <pacote>/ · tests/ · scripts/
├── CLAUDE.md                      # contrato de leitura do agente
├── .gitattributes                 # fim de linha LF
├── .gitignore
└── README.md                      # porta de entrada
```

**Neste kit** a documentação **é** a raiz: o repositório do kit é o molde da pasta de docs, e
`new_project.py` a instala num projeto com o nome já trocado. É por isso que `check.py`
procura o vault em dois lugares — na própria raiz (kit) e em `*_Project_DOCs/` (projeto).

---

## 3. Nomes de arquivo

| Regra | Exemplo |
|---|---|
| Docs: `prefixo_de_ordem` + `snake_case` **em inglês**, sem acento e sem espaço | `c_decisions.md` |
| O prefixo é a **ordem de leitura** da pasta, não uma categoria | `a_`, `b_`, `c_`… |
| Quando o número já tem significado, ele **manda** (fase, versão, passo) | `04_evolution_auditor.md` = fase 4 |
| Saída de IA datada leva timestamp `AAMMDD_HHMM` no fim | `a_qa_pass04_report_260531_0955.md` |
| Pontos de entrada em MAIÚSCULA (convenção universal; o GitHub renderiza) | `README.md`, `INDEX.md`, `CLAUDE.md` |
| Código segue a convenção da linguagem, não esta | `backtest_harness.py`, `tailwind.config.ts` |
| Teste espelha o módulo | `scb/odds.py` → `tests/test_odds.py` |
| Nada de "Sem título", "novo", "final", "v2", "cópia" | — |

**O conteúdo dos documentos continua em português.** Inglês é a língua dos *nomes*: eles
aparecem em caminho, em URL, em terminal e em log, onde acento e espaço custam caro.

**Duas exceções, ambas deliberadas:**

- **As skills não levam prefixo de ordem.** O prefixo significa "ordem de leitura", e as 23
  skills não se leem em ordem — cada sessão carrega **uma**, escolhida pelo gatilho da
  `description`. Numerá-las inventaria uma sequência que não existe.
- **As skills usam `hifen-minusculo`, não `snake_case`.** O nome da pasta **é** o
  identificador que a ferramenta de IA consome (`/backend-domain`), e a convenção dela é essa.
  Vale a mesma regra do código: convenção da ferramenta ganha.

Renomeou? Use **`git mv`** — o histórico do arquivo sobrevive.

---

## 4. O que cada pasta contém

**`a_context/` — a verdade.** O que o projeto é, o que decidiu e por quê.

- `a_context_source.md` — **≤ 4.000 caracteres**, cobrado por `check.py`. Atualizado **por
  substituição**. É o que toda sessão de IA carrega. Estado atual mora **só aqui**.
- `b_plan.md` — plano **congelado**. Mudança de rumo vira decisão nova, não replanejamento.
- `c_decisions.md` — **D-NN** append-only, registrando adoções **e rejeições** (memória contra
  re-explorar o que já falhou), **Q-NN** (decisões do dono) e **QA-NN** (achados).
- `d_*.md`, `e_*.md`… — os temas de domínio do projeto (regras de negócio, schema, fontes de
  dado). Nascem conforme a necessidade, sempre listados no contexto-fonte.

**`b_process/` — como se trabalha.**

- `a_roadmap.md` — o caminho do dia 1 à entrega, fase por fase, com o portão de cada uma.
- `b_checklist.md` — os **portões de aceite** por tipo de entrega.
- `c_backlog.md` — fonte única de tarefas, com WIP declarado no cabeçalho.
- `d_agent_learnings.md` — lições vivas, incluindo os erros do agente.
- `e_repository_standard.md` — este arquivo.
- `skills/` — os agentes instaláveis, um por papel.
- `profiles/` · `templates/` — restrições por stack e modelos de D-NN, QA-NN e fecho.

**`c_technical_docs/`** — runbook de operação, guias, inventários. O que se consulta para
**operar**, não para decidir.

**`d_history/a_changelog.md`** — log datado. **Ninguém carrega em sessão; só se escreve nele.**
É o que permite o contexto-fonte continuar dentro do orçamento.

**`e_qa/`** — relatórios de QA e auditoria, um arquivo por passagem, com timestamp no nome.
Imutáveis: uma passagem registrada não se reescreve depois do conserto — relatório corrigido
a posteriori não serve como evidência. O que muda é uma nota no topo dizendo o que já foi
resolvido.

---

## 5. Cabeçalho dos documentos

Todo `.md` de doc começa com YAML:

```yaml
---
tags: [projeto, tipo]
status: atual | congelado | histórico | rascunho
tipo: contexto | plano | guia | runbook | checklist | padrao
data: AAAA-MM-DD
---
```

`status` e `data` são obrigatórios: é o que separa "isto vale hoje" de "isto é registro do que
valia". `check.py` avisa quando falta.

---

## 6. Git

- **Mensagem de commit:** `TIPO: o que mudou (por quê)`. Tipos em uso: `ADD`, `FIX`, `DOCS`,
  `REFACTOR`, `CHORE`.
- Bug corrigido cita o **QA-NN**; decisão cita o **D-NN**. `check.py` reprova ID que não existe.
- `.gitattributes` normaliza fim de linha para **LF** — evita o churn CRLF↔LF do Windows.
- **Nunca versionar:** `.venv/`, `node_modules/`, `__pycache__/`, bancos regeneráveis,
  `*.zip`, `.env`, tokens e credenciais, rascunhos descartáveis, workspace do editor.
- **Sempre versionar:** dados curados e snapshots que o projeto precisa para rodar do zero.
- **Amostra de segredo em documentação se inutiliza** (`XXXX`), não se isenta — isenção cala o
  seu scanner, não o do destino.

---

## 7. README — a porta de entrada

Responde, nesta ordem: **o que é** + stack · **como o projeto é feito** (o pipeline) · **como
rodar** · **comandos** · **estrutura** · **convenções** · **tecnologias**.

O README **não é a fonte da verdade** do estado: mostra o essencial e aponta para o
contexto-fonte. Quando o código tem README próprio, ele cobre só o técnico.

---

## 8. Checklist para abrir um projeto novo

`python scripts/new_project.py ../meu-app --name "Meu App" --code src` faz os sete primeiros:

- [x] `77777777_<TAG>_Project_DOCs/` com `a_context/`, `b_process/`, `c_technical_docs/`, `d_history/`, `e_qa/`
- [x] as skills e este documento copiados
- [x] pasta de código criada, com README técnico
- [x] `.gitignore` + `.gitattributes` (LF) na raiz
- [x] `README.md` na estrutura da seção 7
- [x] `INDEX.md` como nota-casa do vault
- [x] `CLAUDE.md` na raiz, para a ferramenta carregar sozinha
- [ ] `git init` e `python <docs>/scripts/install_hook.py` — **seus**, na máquina real
- [ ] Escrever `a_context_source.md` (fase 0, skill `context-bootstrap`) **antes de qualquer código**
- [ ] Primeiro commit só depois de `check.py` verde
