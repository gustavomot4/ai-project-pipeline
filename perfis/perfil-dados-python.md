# Perfil — dados / Python (tipo SCM)

> Para projetos de análise/modelagem/dados em Python. Cole os itens relevantes no `CONTEXT.md`
> (seção "Stack + restrições" e "Critério de aceite"). São defaults destilados do SCM — ajuste.

## Stack típica
Python 3.x · NumPy/pandas · SQLite · pytest · (opcional) Flask para UI local.

## Restrições da stack (cole no CONTEXT.md)
- Ambiente isolado: **`.venv`** sempre; `requirements.txt` com **teto de major** nas libs.
- Dados crus e derivados **não** vão no git (`*.sqlite`, `*.npy`, snapshots grandes). Versione só os
  **`*.example`** e os dados curados pequenos. O build dos dados deve ser **reproduzível e determinístico**
  (seed fixa em qualquer Monte Carlo/aleatório).
- Nenhuma previsão/cálculo lê a internet **no momento do cálculo** — só snapshots em disco (se o seu
  projeto tiver essa exigência).

## Critério de aceite (o "portão") — sugestão
- **`pytest -q` verde** + cobertura dos invariantes (somas de probabilidade, monotonia, bordas λ→0).
- Para qualquer mudança que afete números: **ΔMétrica com intervalo de confiança que não cruza zero**
  (bootstrap, seed fixa), comparado a um baseline trivial — e **sem regressão** das outras métricas.
- **Anti-look-ahead** explícito: features ponto-no-tempo, treino/teste separados por data.

## Armadilhas conhecidas (do SCM — já te custaram token)
- **Cache `.pyc` velho** pode rodar código antigo → use `PYTHONPYCACHEPREFIX=/tmp/pyc` ou limpe
  `__pycache__` antes de validar uma edição.
- **Não regenere o documento de planejamento inteiro** a cada revisão — congele a versão e use changelog.
- Não confunda "passou no backtest histórico" com "muda o caso real de hoje" — reporte os dois separados.

## Estrutura de pastas sugerida
```
projeto/
├── CONTEXT.md  DECISIONS.md  CHANGELOG.md  BACKLOG.md  CHECKLIST.md  README.md
├── prompts/                  (copiados deste kit)
├── pacote/                   código (um módulo por arquivo: ingest, engine, features, predictor…)
├── tests/                    um test_*.py por módulo
├── dados/                    só *.example e curados pequenos (o resto é .gitignore)
└── requirements.txt
```
