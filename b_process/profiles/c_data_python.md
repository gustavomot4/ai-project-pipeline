---
tags: [perfil, stack]
status: atual
---

# Perfil — dados / Python

> Cole os blocos marcados no `a_context/a_context_source.md` e ajuste. Defaults destilados de SCM + SCB.

## Stack típica
Python 3.11+ · NumPy/pandas · SQLite · pytest · Flask local (opcional) · argparse.

## Restrições da stack (→ CONTEXT.md)
- `.venv` sempre; `requirements.txt` com teto de major.
- Dados crus/derivados fora do git (`*.sqlite`, `*.npy`, snapshots grandes); versione `*.example` + curados pequenos.
- Build de dados reproduzível e determinístico (seed fixa em qualquer aleatório/Monte Carlo).
- Nada lê a internet no momento do cálculo — download é passo à parte, para snapshot em disco.
- SQLite: sem enum nativo (TEXT + CHECK); datas ISO; invariantes declarados no DDL.

## Quem roda o quê (→ CONTEXT.md)
- **Sandbox do agente:** escrever código puro + testes. `pytest` do sandbox é indicativo, **não é o portão**.
- **Máquina do dono:** `pytest -q` oficial, downloads/APIs (chave via env, nunca versionada), rebuilds, git push, servidor web.
- Servidor/processo vivo tem cache: mudança de código exige restart + hard refresh — avise o dono, sempre.

## Critério de aceite (→ CONTEXT.md)
- `pytest -q` verde na máquina do dono, cobrindo invariantes e bordas.
- Mudança que afeta números: Δmétrica pareada com IC (bootstrap, seed fixa) que não cruza zero, sem regressão das demais.
- Anti-look-ahead: features ponto-no-tempo; treino/teste separados por data; teste PIT obrigatório no pytest.
- Fórmula mudou → bump de versão do modelo + rebuild completo documentado.

## Armadilhas pagas (não repague)
- Parser sem amostra real do payload = retrabalho garantido. Peça a amostra primeiro.
- Coletor sem `try/finally` + resume perde tudo num rate-limit (429).
- Cache `.pyc`/processo velho valida código antigo — limpe/reinicie antes de julgar uma edição.
- "Passou no histórico" ≠ "muda o caso real de hoje" — reporte os dois separados.
- Ganho de um dataset/liga não transfere: re-rode o portão no contexto novo.

## Estrutura sugerida
```
projeto/
├── CONTEXT.md DECISIONS.md CHANGELOG.md BACKLOG.md CHECKLIST.md APRENDIZADOS.md README.md
├── skills/ · contexto/ · dev/ (evidências e relatórios de QA)
├── pacote/ (um módulo por arquivo) · tests/ (um test_*.py por módulo)
├── dados/ (*.example + curados pequenos) · scripts/ (coletas que o dono roda)
└── requirements.txt
```
