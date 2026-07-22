# Pipeline para começar projetos com IA — kit pessoal do Gustavo

Kit reutilizável destilado dos seus dois projetos (SCM e SPO). Copie esta pasta inteira para cada projeto novo e siga as fases. O objetivo é **manter o seu rigor** (portão de aceite, decisões rastreáveis, QA adversarial) **gastando muito menos token** (contexto enxuto, evoluir por delta, não regenerar).

## O que vem na caixa
```
pipeline-projetos-IA/
├── README.md            ← este guia (o pipeline em 6 fases)
├── CONTEXT.md           ← contexto-fonte, ENXUTO e atualizado por substituição
├── DECISIONS.md         ← ADRs (D-01, D-02…) — memória durável das decisões
├── CHANGELOG.md         ← o log datado mora AQUI, fora do contexto
├── BACKLOG.md           ← quadro simples de tarefas
├── CHECKLIST.md         ← o que conferir antes de aceitar um output da IA
├── .gitignore           ← evita versionar deps/segredos/cruft
├── prompts/             ← papéis reutilizáveis (cole no início da sessão)
│   ├── 00-bootstrap-contexto.md
│   ├── 01-planejador.md
│   ├── 02-implementador.md
│   ├── 03-qa-adversarial.md
│   ├── 04-auditor-evolucao.md
│   └── 05-revisao-entrega.md
└── perfis/              ← ajustes por tipo de projeto
    ├── perfil-dados-python.md   (tipo SCM)
    └── perfil-web-nextjs.md     (tipo SPO)
```

## As 5 regras que valem em TODAS as fases
Estas regras são o coração do kit — vêm direto das lições da sua análise.

1. **Contexto enxuto e substituível.** O `CONTEXT.md` tem teto de ~1 página e é **atualizado por substituição** (você reescreve o "Estado atual", não anexa no fim). *Por quê:* o `CLAUDE.md` do SCM virou um log de ~30 seções relido a cada sessão — você pagava o histórico inteiro toda vez.
2. **O histórico mora fora do contexto.** Todo "fizemos X em tal data" vai para o `CHANGELOG.md`, que **não** é carregado nas sessões. O contexto guarda só o presente.
3. **Evoluir por delta, nunca regenerar.** Para mudar um doc/código, peça e devolva **só o trecho alterado**. Não reescreva o documento inteiro nem mande a árvore de versões. *Por quê:* o planejamento v1→v5 do SCM guardou ~35k palavras de rewrites; o schema do SPO foi refeito 6× em 7 dias.
4. **Decisão = registro rastreável.** Toda escolha que "fecha" um assunto vira uma linha no `DECISIONS.md` (D-NN) com o motivo. Bug corrigido ganha um ID (QA-NN) citado no commit/código. *Por quê:* foi o que deixou seus dois projetos auditáveis — generalize.
5. **Nada é aceito sem passar no portão.** Defina o critério de aceite **no dia 1** (teste, IC, typecheck, QA adversarial) e só aceite o que passa nele — não o que "parece bom". *Por quê:* é o que impede a IA de "vencer pelo texto".

---

## O pipeline em 6 fases

Cada fase diz: **o que você faz**, **qual prompt usar**, **que contexto o agente recebe** (sempre o mínimo) e **o portão** para liberar a próxima fase.

### Fase 0 — Bootstrap de contexto
- **Faça:** preencha o `CONTEXT.md` (objetivo em 3 linhas, restrições inegociáveis, **restrições da stack**, critério de aceite). Escolha o perfil (`perfis/`) e cole os ajustes dele no `CONTEXT.md`.
- **Prompt:** `00-bootstrap-contexto.md` (ajuda a IA a entrevistar você e fechar o escopo mínimo).
- **Contexto que o agente recebe:** sua descrição crua do projeto.
- **Portão:** o `CONTEXT.md` cabe em 1 página e o **critério de aceite está escrito**. Sem isso, não avance.

### Fase 1 — Planejamento (e congelamento)
- **Faça:** transforme o contexto num plano: arquitetura, módulos, contratos entre módulos, riscos.
- **Prompt:** `01-planejador.md`.
- **Contexto:** `CONTEXT.md` (só ele).
- **Saída:** um `PLANO.md` curto + as primeiras linhas de `DECISIONS.md`.
- **Portão:** o plano está **congelado** (você aprovou). Mudou de ideia depois? Vira um D-NN novo, não um replanejamento do zero.

### Fase 2 — Dados / Schema *(se aplicável)*
- **Faça:** modele dados/schema **já com as restrições da stack** declaradas (a lição do SPO: "sqlite não tem enum nativo", "dinheiro em Int").
- **Prompt:** `02-implementador.md` no papel "schema".
- **Contexto:** `CONTEXT.md` + o trecho de dados do `PLANO.md`.
- **Portão:** schema valida na stack real (migration roda) antes de qualquer tela/endpoint.

### Fase 3 — Implementação (módulo a módulo, por delta)
- **Faça:** construa **um módulo por vez**. A IA devolve o módulo + o teste dele.
- **Prompt:** `02-implementador.md`.
- **Contexto:** `CONTEXT.md` + **só o módulo atual** + os contratos que ele toca. Nunca o projeto inteiro.
- **Portão:** passa no critério de aceite do módulo (teste/typecheck). Só então o próximo.

### Fase 4 — QA adversarial
- **Faça:** uma sessão separada cujo único objetivo é **quebrar** o que você construiu (não melhorar). Cada achado vira QA-NN.
- **Prompt:** `03-qa-adversarial.md`.
- **Contexto:** o código + `CONTEXT.md` (as restrições são o contrato a verificar).
- **Portão:** achados críticos/altos corrigidos e **citados no commit** (`fix: QA-071 …`).

### Fase 5 — Evolução / auditoria *(só depois do baseline congelado)*
- **Faça:** procurar melhorias **com ceticismo** — cada ideia precisa de evidência medida e de passar no portão.
- **Prompt:** `04-auditor-evolucao.md`.
- **Contexto:** `CONTEXT.md` + `DECISIONS.md` (a lista do que já falhou evita re-explorar becos sem saída).
- **Portão:** só adota o que passa no critério objetivo; o resto vira D-NN "rejeitado" (memória para não repetir).

### Fase 6 — Revisão de entrega / empacotamento
- **Faça:** antes de entregar/arquivar, rode o `CHECKLIST.md` e empacote **sem dependências**.
- **Prompt:** `05-revisao-entrega.md`.
- **Portão:** zip contém só fonte + docs (sem `.venv`/`node_modules`/`.git`/backups), sem segredo, sem `*.bak`; e você **abriu o zip e conferiu** que os arquivos certos estão lá (a lição do `.lnk` quebrado).

---

## Ciclo curto do dia a dia
Na prática, 90% das sessões são este loop:

> abrir sessão → colar o **prompt do papel** + o **`CONTEXT.md`** + **só o arquivo do momento** → pedir **delta** → passar no **portão** → registrar **D-NN/QA-NN** → atualizar `CONTEXT.md` **por substituição** e jogar o datado no `CHANGELOG.md`.

Se você fizer só isto, já elimina os dois maiores custos que a análise achou: contexto inchado e regeneração.
