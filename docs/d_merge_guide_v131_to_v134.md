---
tags: [guia, kit, merge]
status: atual
data: 2026-08-13
---
# Roteiro do merge — `kit v13.1` → `v13.4` num projeto com portão customizado

**Para que serve:** o `--upgrade` marca `scripts/check.py` como PROTEGIDO quando o projeto o
editou, e o kit só oferece `--forcar` (sobrescreve e perde a customização) ou nada. Este roteiro
é o caminho do meio: portar à mão o que mudou no kit, preservando o que o projeto mudou.

**Delta a portar** (`git diff c9b6bd0 -- scripts/check.py` no kit): **+137 / −5**, em 8 blocos.
**O que o projeto tem a mais e não pode ser perdido** (no caso medido, `D-50`): a função
`medida()` (orçamento sem o padding de tabela), o registro dividido `QA_REG` = `a_context/d_qa.md`,
e o orçamento de 8.000 desse arquivo.

> **Antes de começar:** árvore limpa e um `git commit` no projeto. Todo o resto se revisa com
> `git diff` e se desfaz com `git checkout`.

---

## Passo 0 — a medição de antes (é o que prova o depois)

```
python 77777777_*_Project_DOCs/scripts/check.py
```
Anote o resultado. No projeto medido: **exit 0**, 2 avisos de orçamento.

---

## Os 8 blocos

### 1. Cabeçalho: a lista de AVISOS
No docstring, a lista depois de `AVISOS (não reprovam…)` ganha quatro entradas:

```
  sessão sem skill declarada no changelog · ocupação declarada divergindo do arquivo ·
  questão do dono ausente do CONTEXT · achado grave aberto há mais de 14 dias
```

> Se o projeto tiver `test_check.py` cobrando os números do README, ajuste-os. No caso medido
> não tem — o kit exclui a suíte de projetos novos —, então nada cobra isso lá.

### 2. Import
```python
from datetime import date
```

### 3. Constantes (junto de `PLANO`, `DECISOES`, `BACKLOG`)
```python
CHANGELOG = "d_history/a_changelog.md"          # histórico datado; nenhuma sessão carrega
ARQUIVO_MORTO = "e_qa/decisions_archive.md"     # íntegra das linhas retiradas da tabela
```

### 4. `sem_bloco_de_codigo()` — o QA-14
Logo depois de `sem_codigo()`, **sem tocar nela** (o `sem_codigo` continua certo para wikilink):

```python
def sem_bloco_de_codigo(texto):
    """Só o bloco cercado. É o filtro certo para a checagem de ID (10).

    Medido: 300 de 341 citações de ID estavam ENTRE CRASES — a casa escreve `D-13`, não D-13.
    Filtrando por `sem_codigo`, a checagem enxergava 12% e imprimia verde sobre os outros 88%.
    """
    return re.sub(r"```.*?```", "", texto, flags=re.S)
```

### 5. Checagem 9 — o QA-15
Dentro do `else:` do `.gitignore`, trocar a leitura por:

```python
    # QA-15: só as linhas EFETIVAS. Um .gitignore que apenas COMENTA os padrões
    # ("# nunca commite .env, *.pem…") satisfazia a checagem por substring sem ignorar nada.
    texto_gi = "\n".join(l for l in gi.read_text(encoding="utf-8").splitlines()
                         if l.strip() and not l.lstrip().startswith("#"))
```

### 6. Checagens 10/11 — QA-14 + QA-16 · **ESTE É O BLOCO DE CONFLITO**
No projeto medido este bloco foi reescrito pelo `D-50` (dois registros). As mudanças são
**três linhas**, e vão na versão do projeto, não na do kit:

```python
    # (a) logo depois de `definidos = set(ocorrencias)`  — QA-16
    morto = raiz / ARQUIVO_MORTO
    arquivados = set(re.findall(r"\b((?:D|Q|QA)-\d+)\b", corpo.get(morto, ""))) if morto.exists() else set()

    # (b) na varredura de citações — QA-14
    for i in set(re.findall(r"\b((?:D|Q|QA)-\d+)\b", sem_bloco_de_codigo(corpo[nota]))):

    # (c) no filtro de fantasmas — QA-16
    fantasmas = {i: v for i, v in citados.items()
                 if i not in definidos and i not in arquivados
                 and not re.fullmatch(r"(D|Q|QA)-0*(0|NN)", i)}
```
E a mensagem, adaptada aos dois registros do projeto:
```python
        falhas.append(f"ID citado que não existe em {DECISOES}, {QA_REG} nem em {ARQUIVO_MORTO}: {detalhe}")
```

> **`arquivados` NÃO entra em `definidos`, de propósito.** A checagem 11 (ID duplicado) tem de
> continuar olhando só as tabelas vivas — senão a convenção `ADOTADO · ARQUIVADO`, que deixa a
> linha na tabela com a íntegra no arquivo, vira duplicata falsa.

> **Sem o (a) e o (c), o (b) trava o projeto.** Medido: com o QA-14 sozinho, o projeto avaliado
> ia de 0 para **22 fantasmas** — todos legitimamente arquivados — e o portão reprovaria todo
> commit.

### 7. Três avisos novos (bloco inteiro, antes do `placeholders = re.findall(...)`)
Copiar do `check.py` do kit **com as três adaptações do Passo A abaixo**:
ocupação declarada · questão do dono ausente do CONTEXT · achado grave vencido.

### 8. Aviso da skill no changelog
Vem no mesmo bloco do passo 7. Nenhuma adaptação.

---

## Passo A — as quatro adaptações (é onde o merge dá errado em silêncio)

**A1 · `len()` → `medida()` no aviso de ocupação.** O kit mede com `len()`; o projeto mede sem o
padding de tabela. Portado cru, o aviso acusa falsamente:
```python
        if texto_alvo and declarado != medida(texto_alvo):
```
e a mensagem também usa `medida(texto_alvo)`.

**A2 · o orçamento do registro dividido entra no dicionário.**
```python
ORCAMENTOS = {4000: (CONTEXTO, texto_ctx), 12000: (DECISOES, texto_dec), 8000: (QA_REG, texto_qa)}
```

**A3 · o achado vencido lê o arquivo certo.** No kit os `QA-NN` moram no DECISIONS; no projeto
medido eles saíram para `d_qa.md` (`D-50`). Trocar **todo** `texto_dec` por `texto_qa` naquele
bloco — inclusive no `elif` que diz "tabela sem a coluna". Sem isso ele procura a tabela no
arquivo errado e reclama para sempre.

**A4 · a fila do dono continua lendo o DECISIONS.** As `Q-NN` não se mudaram; este bloco fica
como está no kit. Confira, não presuma.

---

## Passo B — a verificação (as duas metades, não só a primeira)

```
python 77777777_*_Project_DOCs/scripts/check.py
```

**Esperado no projeto medido, com o merge correto:**

| | Resultado esperado |
|---|---|
| exit | **0** — igual ao passo 0 |
| fantasmas de ID | **0** (eram 22 sem o QA-16) |
| aviso "ocupação declarada" | **calado** se os números do CONTEXT estiverem certos; se falar, o número é que está velho — confira antes de culpar o merge |
| aviso "questão ausente do CONTEXT" | **calado** — `Q-08`, `Q-09` e `Q-11` já estão listadas lá |
| aviso "achado grave vencido" | **calado hoje**; `QA-11` é Crítico e está aberto desde 08/08, então ele fala por volta de **22/08** se a linha não for fechada |
| aviso "sessão sem skill" | **fala** nas 3 entradas mais recentes do changelog — é o comportamento correto, o campo é novo |

**A segunda metade, que é a que costuma não ser rodada:** reverta só a linha (b) do bloco 6 —
`sem_bloco_de_codigo` de volta para `sem_codigo` — e confirme que o portão volta a **passar** com
um ID inexistente entre crases. Se passar nos dois casos, o merge não portou nada.

Sabotagem de 10 segundos para provar que a checagem ficou viva:
```
echo "Ver \`D-999\` aqui." >> 77777777_*_Project_DOCs/a_context/stack.md
python 77777777_*_Project_DOCs/scripts/check.py     # tem de REPROVAR citando D-999
git checkout 77777777_*_Project_DOCs/a_context/stack.md
```

---

## Passo C — o que fazer com os avisos novos que aparecerem

- **"sessão sem skill declarada"** — é o único que vai falar de cara. Adote o campo a partir da
  próxima entrada: uma linha `- **Skill:** <nome>` no changelog. Não reescreva o histórico.
- **Qualquer outro que fale** — antes de mexer no `check.py`, confira se ele está certo. Os três
  foram desenhados a partir deste projeto; se um deles falar, provavelmente está falando a verdade.

## O que NÃO vem neste merge

`b_process/c_backlog.md` (seção de Faxina) e `a_context/c_decisions.md` (coluna `Fechado em`,
convenção de `Q-NN` respondida) são **verdade do projeto** e o `--upgrade` nunca os copia, por
desenho. Se quiser a seção de Faxina, ela é copiar 4 linhas do template do kit à mão — e o
projeto medido já tem a coluna `Fechado em`, então o aviso do passo 7 funciona lá desde o
primeiro dia.
