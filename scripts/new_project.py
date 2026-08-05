#!/usr/bin/env python3
"""Cria um projeto novo no padrão do repositório, já limpo e pronto para o primeiro commit.

Uso:
    python scripts/new_project.py ../meu-app --name "Caixa da Loja"
    python scripts/new_project.py ../meu-app --name "Caixa da Loja" --code src --tag CAIXA

O que ele monta (os itens do "checklist para abrir projeto novo" do padrão, executáveis):

    meu-app/
    ├── 77777777_<TAG>_Project_DOCs/   ← este kit, instalado como a pasta de docs
    │   ├── INDEX.md  a_context/  b_process/  c_technical_docs/  d_history/  e_qa/  scripts/
    ├── <pasta_de_codigo>/             ← nasce com o README técnico
    ├── CLAUDE.md                      ← contrato de leitura, na raiz (a ferramenta carrega)
    ├── README.md                      ← porta de entrada, na estrutura da seção 8 do padrão
    ├── .gitignore
    └── .gitattributes

Por que existe: o passo "copie tudo exceto .git" era manual e levava junto o histórico e a
análise de OUTRO projeto — o que viola "uma verdade por assunto" logo no primeiro dia.
"""
import argparse
import re
import shutil
import sys
import unicodedata
from datetime import date
from pathlib import Path

# Só do kit: nunca vão para um projeto (histórico e evidências DESTE repositório).
# `docs/` é a pasta da auditoria do PRÓPRIO kit (ver e_qa/README.md) — excluída por
# PASTA de propósito: relatório novo do kit fica de fora sozinho, sem ninguém precisar
# lembrar de acrescentar o nome do arquivo aqui.
EXCLUIR_PASTAS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules", "docs"}
EXCLUIR_ARQUIVOS = {
    ".obsidian/workspace.json",
    "scripts/new_project.py",
    "d_history/b_kit_changelog.md",
    "c_technical_docs/b_reference_case_spo.md",
}
EXCLUIR_SUFIXOS = (".bak", ".tmp", ".orig", ".pyc")
# Vão para a RAIZ do projeto; todo o resto do kit vira a pasta de documentação.
NA_RAIZ = {"CLAUDE.md", ".gitignore", ".gitattributes"}

raiz = Path(__file__).resolve().parent.parent

# Wikilinks para o que ficou no kit têm de virar texto: senão o projeto novo nasce
# com link quebrado e reprovando no primeiro `check.py`. DERIVADO das exclusões acima,
# não listado à mão — lista mantida a dedo é a que sai de sincronia com a realidade.
SO_DO_KIT = tuple(
    {Path(a).stem for a in EXCLUIR_ARQUIVOS if a.endswith(".md")}
    | {p.stem for p in (raiz / "docs").rglob("*.md")}
)


def sigla(nome: str) -> str:
    """'Caixa da Loja' -> 'CAIXADALOJA'. Sem acento, sem espaço, maiúsculo — vira o <TAG> de
    77777777_<TAG>_Project_DOCs, cujo prefixo numérico mantém a pasta sempre no topo da árvore."""
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]", "", sem_acento).upper()[:12] or "PROJ"


def deslinkar(texto: str) -> str:
    """[[b_reference_case_spo|caso]] -> *caso (fica no kit)* — o alvo não existe no projeto."""

    def troca(m):
        alvo, _, alias = m.group(1).partition("|")
        alvo = alvo.rstrip("\\").strip()
        if not any(k in alvo for k in SO_DO_KIT):
            return m.group(0)
        rotulo = (alias.strip() or alvo.rsplit("/", 1)[-1]).rstrip("\\")
        return f"*{rotulo} (fica no kit)*"

    return re.sub(r"\[\[([^\]\n]+)\]\]", troca, texto)


def copiar(destino: Path, pasta_docs: str) -> int:
    """Kit -> projeto. O conteúdo do kit VIRA a pasta de docs; três arquivos vão para a raiz."""
    n = 0
    for origem in sorted(raiz.rglob("*")):
        if origem.is_dir():
            continue  # pasta nasce com o primeiro arquivo; pasta vazia é cruft
        rel = origem.relative_to(raiz)
        if any(parte in EXCLUIR_PASTAS for parte in rel.parts):
            continue
        if rel.as_posix() in EXCLUIR_ARQUIVOS or origem.name.endswith(EXCLUIR_SUFIXOS):
            continue
        alvo = destino / (rel if rel.as_posix() in NA_RAIZ else Path(pasta_docs) / rel)
        alvo.parent.mkdir(parents=True, exist_ok=True)
        if origem.suffix == ".md":
            alvo.write_text(deslinkar(origem.read_text(encoding="utf-8")), encoding="utf-8")
        else:
            shutil.copy2(origem, alvo)
        n += 1
    return n


def nomear(destino: Path, pasta_docs: str, nome: str) -> None:
    """Troca o placeholder do nome e zera o changelog (o histórico do kit fica no kit)."""
    docs = destino / pasta_docs
    changelog = docs / "d_history/a_changelog.md"
    if changelog.exists():
        txt = re.sub(
            r"^> Histórico do \*\*kit\*\*.*$",
            "> Este arquivo nasceu zerado por `scripts/new_project.py`. O histórico do kit ficou no kit.",
            changelog.read_text(encoding="utf-8"), count=1, flags=re.M,
        )
        changelog.write_text(txt, encoding="utf-8")
    for arquivo in ("a_context/a_context_source.md", "a_context/b_plan.md"):
        p = docs / arquivo
        if p.exists():
            p.write_text(p.read_text(encoding="utf-8").replace("<NOME DO PROJETO>", nome), encoding="utf-8")


README = """---
tags: [readme, guia]
status: atual
tipo: guia
data: {data}
---
# {nome}

<O que o sistema faz, para quem, em um parágrafo. Um não-objetivo explícito.>

**Stack:** <linguagem · framework · banco · runtime>

A verdade viva do projeto mora em `{docs}/a_context/a_context_source.md` —
este README é a porta de entrada, não a fonte do estado.

---

## Como este projeto é feito

Pipeline de agentes de IA com portão objetivo em cada fase. O caminho completo está em
`{docs}/b_process/a_roadmap.md`; os agentes, em `{docs}/b_process/skills/`.

O ciclo de **toda** sessão:

> uma skill + o contexto-fonte + só o arquivo do momento → pedir **delta** → passar no
> **portão** (`{docs}/b_process/b_checklist.md`) → registrar **D-NN/QA-NN** →
> atualizar o contexto **por substituição** → datar no changelog → commit citando os IDs.

## Como rodar

```
<comandos, do zero, copiáveis — incluindo os pré-requisitos>
```

## Comandos disponíveis

| Comando | Descrição |
|---|---|
| `python {docs}/scripts/check.py` | portão de higiene (roda sozinho em todo commit) |
| `<comando do projeto>` | <o que faz> |

## Estrutura do projeto

```
{nome_pasta}/
├── {docs}/   ← TODA a documentação
│   ├── INDEX.md              mapa de navegação
│   ├── a_context/            a verdade: contexto-fonte, plano, decisões
│   ├── b_process/            como se trabalha: roteiro, checklist, backlog, skills
│   ├── c_technical_docs/     runbook e guias de operação
│   ├── d_history/            changelog datado (ninguém carrega; só escreve)
│   ├── e_qa/                 relatórios de QA, com timestamp no nome
│   └── scripts/              check.py · install_hook.py
├── {codigo}/   ← TODO o código
├── CLAUDE.md                 contrato de leitura do agente
├── .gitattributes            fim de linha LF
├── .gitignore
└── README.md                 este arquivo
```

Regra de ouro: **documentação em `{docs}/`, código em `{codigo}/`.**
A raiz só tem o README, o CLAUDE.md e a configuração do repositório.

## Convenções

- Nomes de arquivo de doc: `prefixo_de_ordem` + `snake_case` em inglês, sem acento.
  O prefixo é a **ordem de leitura** da pasta. Saída de IA datada leva `_AAMMDD_HHMM`.
- **Uma verdade por assunto:** estado só no contexto-fonte; histórico só no changelog;
  decisão só em `c_decisions.md`. Nenhum doc repete o que outro diz — aponta.
- Todo `.md` de doc começa com YAML: `status` e `data` obrigatórios.
- Commit: `TIPO: o que mudou (por quê)`. Bug cita `QA-NN`, decisão cita `D-NN`.
- O padrão completo está em `{docs}/b_process/e_repository_standard.md`.
"""

README_CODIGO = """# {nome} — código

README técnico. A documentação do projeto (contexto, plano, decisões, roteiro) mora em
`../{docs}/`; aqui fica só o que é preciso para **rodar e desenvolver**.

## Rodar

```
<instalar dependências>
<rodar os testes>
<subir a aplicação>
```

## Estrutura

```
{codigo}/
├── <pacote>/     o código da aplicação
├── tests/        1 arquivo de teste por módulo
└── scripts/      utilitários avulsos, rodados à mão
```
"""


def esqueleto(destino: Path, pasta_docs: str, nome: str, codigo: str) -> None:
    """Cria a pasta de código e os READMEs — itens do checklist do padrão que antes ficavam
    para o dono fazer à mão e que, feitos à mão, ficavam para depois."""
    (destino / codigo).mkdir(parents=True, exist_ok=True)
    (destino / codigo / "README.md").write_text(
        README_CODIGO.format(nome=nome, docs=pasta_docs, codigo=codigo), encoding="utf-8"
    )
    (destino / "README.md").write_text(
        README.format(
            nome=nome, docs=pasta_docs, codigo=codigo,
            nome_pasta=destino.name, data=date.today().isoformat(),
        ),
        encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Cria um projeto novo no padrão do repositório.")
    ap.add_argument("destino", help="pasta do projeto novo (será criada)")
    ap.add_argument("--name", "--nome", dest="nome", required=True, help="nome do projeto")
    ap.add_argument("--tag", help="sigla da pasta de docs (default: derivada do nome)")
    ap.add_argument("--code", "--codigo", dest="codigo", default="src", help="pasta do código (default: src)")
    ap.add_argument("--forcar", "--force", action="store_true", help="permite destino já existente e não vazio")
    args = ap.parse_args()

    destino = Path(args.destino).resolve()
    if destino == raiz:
        print("ERRO: destino é o próprio kit.")
        return 1
    if destino.exists() and any(destino.iterdir()) and not args.forcar:
        print(f"ERRO: {destino} já existe e não está vazia. Use --forcar se for intencional.")
        return 1

    pasta_docs = f"77777777_{(args.tag or sigla(args.nome)).upper()}_Project_DOCs"
    destino.mkdir(parents=True, exist_ok=True)

    n = copiar(destino, pasta_docs)
    nomear(destino, pasta_docs, args.nome)
    esqueleto(destino, pasta_docs, args.nome, args.codigo)

    print(f"OK: {args.nome} criado em {destino}")
    print(f"   {n} arquivos de documentação em {pasta_docs}/")
    print(f"   pasta de código: {args.codigo}/")
    print("   Ficaram no kit: changelog do kit, caso de referência e os relatórios de QA do kit.")
    print()
    print("Próximos passos:")
    print(f"  1. cd {destino} && git init")
    print(f"  2. python {pasta_docs}/scripts/install_hook.py")
    print(f"  3. Abra a pasta como vault do Obsidian ({pasta_docs}/c_technical_docs/a_obsidian_guide.md)")
    print(f"  4. Instale as skills de {pasta_docs}/b_process/skills/ na sua ferramenta de IA")
    print("  5. Sessão com a skill `context-bootstrap` → preenche o contexto-fonte")
    print(f"  6. python {pasta_docs}/scripts/check.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
