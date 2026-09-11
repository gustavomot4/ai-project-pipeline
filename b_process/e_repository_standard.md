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

1. **A árvore da equipe, com prefixo alfabético.** Sete pastas de topo em ordem fixa
   (`a_backend` `b_middleware` `c_frontend` `d_test` `e_doc` `f_infra` `z_mis`): o prefixo
   existe para que a ordenação seja a mesma em qualquer explorador de arquivos, e para que a
   documentação e a infraestrutura não se percam no meio do código. Na raiz ficam só o
   `README.md`, o `CLAUDE.md` e a configuração do repositório.
2. **Uma verdade por assunto.** Cada informação tem **um** dono. Nenhum arquivo repete o que
   outro já diz — ele **aponta**. Duplicata é dívida: envelhece em silêncio e depois mente.
3. **O que não tem dono, não entra.** Arquivo sem papel definido (rascunho vazio, sonda
   descartável, cache, duplicata "por garantia") não é versionado. Se já entrou, sai — o
   histórico do git guarda.

**Onde o kit mora nessa árvore:** o vault inteiro (contexto, processo, histórico, QA e
scripts) é instalado em **`e_doc/0_Context/`** — a pasta que o padrão define como "contexto e
planejamento". Projetos criados antes do `kit v13.14` têm o vault em
`77777777_<TAG>_Project_DOCs/`, e **todos os scripts continuam reconhecendo as duas casas**:
atualização que deixa de achar o projeto que ela mesma criou não é atualização, é abandono.

---

## 2. Estrutura

```
stf_pss_<ms|ap|cd>_<nome>/
├── a_backend/
│   ├── a_code/                    # código-fonte do backend
│   └── d_doc/                     # DDL e documentação técnica
├── b_middleware/                  # camada intermediária (opcional)
├── c_frontend/
│   ├── a_code/                    # código-fonte
│   └── d_doc/                     # documentação técnica
├── d_test/
│   ├── a_data_dictionary/  b_test_unit/  c_test_integration/  c_test_system/
│   └── d_test_load/  e_test_capacity/  f_test_performance/  g_test_security/
├── e_doc/
│   ├── 0_Context/                 # ← O VAULT DO KIT mora aqui, inteiro
│   │   ├── INDEX.md               # nota-casa: mapa de navegação
│   │   ├── a_context/             # a VERDADE do projeto
│   │   ├── b_process/             # como se TRABALHA (inclui skills/)
│   │   ├── c_technical_docs/      # runbooks, guias, evidências de operação
│   │   ├── d_history/             # changelog datado
│   │   ├── e_qa/                  # relatórios e arquivo-morto
│   │   └── scripts/               # o portão e as ferramentas
│   ├── 1_SPC/                     # especificação funcional e técnica
│   ├── 2_BPM/                     # fluxos de processo
│   ├── 3_MER/                     # modelo de dados
│   └── 4_Class/                   # diagrama de classes
├── f_infra/
│   ├── a_docker/                  # Docker e Docker Compose
│   └── b_terraform/               # Terraform (IaC)
├── z_mis/                         # miscelânea, rascunho
├── CLAUDE.md                      # contrato de leitura (a ferramenta carrega da raiz)
├── README.md  .gitignore  .gitattributes
```

Cada pasta nasce com um `LEIA-ME.md` de uma linha dizendo o que vai nela. Não é enfeite: o git
não versiona pasta vazia, então sem ele a árvore chega pela metade no clone — e a regra 3
("o que não tem dono, não entra") fica sem como ser aplicada a uma pasta que ninguém explicou.

**Nomenclatura de artefato**, dentro de `e_doc/`:
`stf_pss_<tipo>_<nome>_<papel>_<tópico>_<yymmdd_hhMM>.<ext>` — o timestamp é calculado **uma
vez por execução** e repetido em todos os arquivos do mesmo conjunto, para que a leva inteira
seja reconhecível de relance. Por fase: `1_SPC` traz `a_CHAT_functional` · `b_SPC_functional` ·
`c_CHAT_technical` · `d_SPC_technical`; `2_BPM` traz `bpm_a_CHAT_<Op>` · `bpm_b_PRD_<Op>` ·
`bpm_c_BPM_<Op>.drawio`; `3_MER` traz `mer_a_CHAT` · `mer_b_PRD` · `mer_c_MER.mermaid`;
`4_Class` traz `class_a_CHAT` · `class_b_PRD` · `class_c_Class.mermaid`.


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

- **Mensagem de commit — padrão da equipe (STF PSS), cobrado por hook `commit-msg`:**

  ```
  <STATUS>: <Tipo>: <Descrição>
  ```

  `STATUS` é `OK` (completo, funcional e revisado) ou `NOK` (em progresso). `Tipo` é um da
  lista fechada: `Feat` · `Fix` · `Doc` · `Infra` · `Config` · `Chore` · `Deploy` · `Test` ·
  `Style` · `Merge`. Um commit = uma unidade lógica de trabalho, e o detalhe adicional vai no
  **segundo `-m`**, nunca na primeira linha:

  ```
  git commit -m "OK: Fix: Corrigir parser do relatório (QA-07)"              -m "A causa era o padding das tabelas; teste de regressão junto."
  ```

  Instale a trava com `python scripts/install_hook.py` — ela recusa a mensagem fora do
  formato e diz **qual** é o erro (status minúsculo, tipo fora da lista, tipo não
  capitalizado). Merge, revert, fixup e squash gerados pelo git passam sem discussão.
- **Nome da branch:** `<u|v>_<nome>_<ss>` — `u_` para membro veterano, `v_` para membro novo;
  primeira letra do nome mais as iniciais do sobrenome (`u_ezequiel_fc`, `v_ana_ps`).
- **Nome do repositório:** `stf_pss_<tipo>_<nome>`, com `ms` (microserviço), `ap` (aplicação)
  ou `cd` (cross-domain: infra, segurança, mock). Exemplos: `stf_pss_ms_graph`,
  `stf_pss_ap_sat`, `stf_pss_cd_cloud`.
- Os três acima entram como **AVISO** no `check.py`, não como falha — o histórico é imutável
  e renomear repositório é decisão do dono. Projeto legitimamente fora do padrão declara
  `"padrao_equipe": false` em `.kit-config.json`, e os três silenciam.
- **Banco de dados:** tabelas `{TAG}_TP_*` / `{TAG}_TB_*` / `{TAG}_TB_*_CHANGE` e colunas com
  prefixo de tipo (`u_ i_ s_ n_ ts_ b_`) — perfil completo em
  [[d_db_stf_pss|perfil de banco]]. Não é cobrado por máquina: o portão não lê DDL.
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
- [ ] `git init` e `python <docs>/scripts/task.py travas` — **seus**, na máquina real (os hooks de git são por clone)
- [ ] Escrever `a_context_source.md` (fase 0, skill `context-bootstrap`) **antes de qualquer código**
- [ ] Primeiro commit só depois de `check.py` verde
