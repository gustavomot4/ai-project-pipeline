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
import hashlib
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

# Rede de segurança da SAÍDA (o gêmeo do QA-01). Saída redirecionada num Windows pt-BR
# usa cp1252, não UTF-8: um caractere fora dele — uma seta, um "≤" — mata o script na
# hora de IMPRIMIR, depois de todo o trabalho feito. `errors="replace"` degrada em vez
# de matar, e não muda nada no console, que já é UTF-8.
for _fluxo in (sys.stdout, sys.stderr):
    if hasattr(_fluxo, "reconfigure"):
        _fluxo.reconfigure(errors="replace")

# Só do kit: nunca vão para um projeto (histórico e evidências DESTE repositório).
# `docs/` é a pasta da auditoria do PRÓPRIO kit (ver e_qa/README.md) — excluída por
# PASTA de propósito: relatório novo do kit fica de fora sozinho, sem ninguém precisar
# lembrar de acrescentar o nome do arquivo aqui.
# `.github/` é o CI DO KIT e não vai para projeto nenhum: ele acabaria dentro da pasta de
# documentação, onde o GitHub Actions nem procura, rodando comandos com caminho de kit.
EXCLUIR_PASTAS = {".git", ".github", "__pycache__", ".pytest_cache", ".venv", "venv",
                  "node_modules", "docs"}
EXCLUIR_ARQUIVOS = {
    ".obsidian/workspace.json",
    "scripts/new_project.py",
    # Testa os scripts DO KIT (inclusive o `new_project.py`, que nem vai junto). Copiado
    # para um projeto, ele reprova no primeiro `task.py test` — e suíte que nasce vermelha
    # ensina a ignorar suíte, que é o vício que este kit combate em todo lugar.
    "scripts/test_check.py",
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
    """Kit -> projeto. O conteúdo do kit VIRA a pasta de docs; três arquivos vão para a raiz.
    Grava o manifesto de impressões: é ele que, na atualização, distingue "arquivo do kit
    intocado" de "o dono customizou isto" — sem essa distinção, `--upgrade` apaga trabalho."""
    n, manifesto = 0, {}
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
        dados = (deslinkar(origem.read_text(encoding="utf-8")).encode("utf-8")
                 if origem.suffix == ".md" else origem.read_bytes())
        alvo.write_bytes(dados)
        manifesto[rel.as_posix()] = impressao(dados)
        n += 1
    escrever_manifesto(destino / pasta_docs, manifesto)
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


# ---------------------------------------------------------------------------------
# ATUALIZAÇÃO DE PROJETO EXISTENTE
#
# O buraco que isto fecha: até aqui `new_project.py` era cópia de mão única. Um projeto
# criado com a v7 nunca recebia nada da v8 — todo conserto de portão, toda skill nova e
# todo teste ficavam encalhados no repositório do kit. Kit que evolui e não alcança os
# projetos que gerou é kit que evolui sozinho.
#
# A divisão abaixo é a única coisa que torna isto seguro, e ela é EXPLÍCITA de propósito:
# heurística por pasta não serve, porque `b_process/c_backlog.md` mora numa pasta de
# processo e é ESTADO DO PROJETO. Errar esse limite apaga trabalho do dono.
# ---------------------------------------------------------------------------------
# Processo: o kit é dono, pode reescrever.
DO_KIT = (
    "CLAUDE.md", "INDEX.md",
    "b_process/a_roadmap.md", "b_process/b_checklist.md",
    "b_process/e_repository_standard.md", "b_process/f_glossary_and_primer.md",
    "b_process/skills/", "b_process/profiles/", "b_process/templates/",
    "c_technical_docs/a_obsidian_guide.md",
    "scripts/",
)
# Verdade do projeto: NUNCA tocar. Cada item aqui já foi (ou seria) perda de trabalho.
#   a_context/          -> contexto, plano, decisões: é o projeto
#   b_process/c_backlog -> mora em "processo", mas é estado
#   d_agent_learnings   -> o kit semeia, o projeto acrescenta as próprias lições
#   d_history/, e_qa/   -> histórico e evidência do projeto
#   README, .gitignore  -> gerados/editados por projeto
NUNCA = ("a_context/", "b_process/c_backlog.md", "b_process/d_agent_learnings.md",
         "d_history/", "e_qa/", "README.md", ".gitignore")

MARCA_VERSAO = ".kit-version"
MANIFESTO = ".kit-manifest"


def impressao(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()[:16]


def ler_manifesto(docs: Path) -> dict:
    """`caminho -> impressão do que o KIT escreveu ali`. É o que permite distinguir
    "arquivo intocado" de "o dono customizou isto".

    Sem manifesto (projeto criado antes desta versão) o resultado é `{}`, e a
    atualização trata TUDO como possivelmente customizado — ou seja, não sobrescreve
    nada sem `--forcar`. Falha fechada: perder customização do dono em silêncio é pior
    que exigir uma flag."""
    arq = docs / MANIFESTO
    if not arq.exists():
        return {}
    saida = {}
    for linha in arq.read_text(encoding="utf-8").splitlines():
        partes = linha.split(None, 1)
        if len(partes) == 2:
            saida[partes[1].strip()] = partes[0].strip()
    return saida


def escrever_manifesto(docs: Path, dados: dict) -> None:
    corpo = ["# Impressão do que o KIT escreveu. Não edite: é o que protege as suas",
             "# customizações de serem sobrescritas por `new_project.py --upgrade`."]
    corpo += [f"{h}  {c}" for c, h in sorted(dados.items())]
    (docs / MANIFESTO).write_text("\n".join(corpo) + "\n", encoding="utf-8")


def versao_do_kit() -> str:
    """Derivada do changelog, não mantida à mão — lista mantida a dedo sai de sincronia."""
    changelog = raiz / "d_history/b_kit_changelog.md"
    if changelog.exists():
        m = re.search(r"^##\s*\[([^\]]+)\]", changelog.read_text(encoding="utf-8"), re.M)
        if m:
            return m.group(1).strip()
    return "desconhecida"


def achar_docs(projeto: Path) -> Path | None:
    candidatos = sorted(p for p in projeto.glob("*_Project_DOCs") if (p / "a_context").is_dir())
    if len(candidatos) == 1:
        return candidatos[0]
    return None


def arvore_suja(projeto: Path) -> bool:
    """Exigir árvore limpa não é frescura: é o que torna a atualização REVISÁVEL
    (`git diff`) e REVERSÍVEL (`git checkout`). Sem isso o dono não distingue o que o
    script mudou do que ele mesmo estava editando."""
    try:
        saida = subprocess.run(["git", "-C", str(projeto), "status", "--porcelain"],
                               capture_output=True, text=True, check=True, timeout=20,
                               encoding="utf-8", errors="replace").stdout
    except (subprocess.SubprocessError, OSError):
        return False  # sem git não há o que sujar; a decisão é do dono
    return bool(saida.strip())


def atualizar(projeto: Path, simular: bool, forcar: bool) -> int:
    docs = achar_docs(projeto)
    if docs is None:
        print(f"ERRO: não achei uma pasta *_Project_DOCs em {projeto}.")
        return 1
    if arvore_suja(projeto) and not (simular or forcar):
        print("ERRO: a árvore do projeto tem mudanças não commitadas.")
        print("      Commite antes — é o que permite revisar a atualização com `git diff`")
        print("      e desfazê-la com `git checkout`. Ou use --dry-run, ou --forcar.")
        return 1

    manifesto = ler_manifesto(docs)
    novos, mudados, protegidos, iguais = [], [], [], 0
    for origem in sorted(raiz.rglob("*")):
        if origem.is_dir():
            continue
        rel = origem.relative_to(raiz).as_posix()
        if any(parte in EXCLUIR_PASTAS for parte in Path(rel).parts):
            continue
        if rel in EXCLUIR_ARQUIVOS or origem.name.endswith(EXCLUIR_SUFIXOS):
            continue
        if any(rel == n or rel.startswith(n) for n in NUNCA):
            continue
        if not any(rel == d or rel.startswith(d) for d in DO_KIT):
            continue
        alvo = (projeto if rel in NA_RAIZ else docs) / rel
        novo = (deslinkar(origem.read_text(encoding="utf-8")).encode("utf-8")
                if origem.suffix == ".md" else origem.read_bytes())
        item = (rel, alvo, novo)
        if not alvo.exists():
            novos.append(item)
            continue
        atual = alvo.read_bytes()
        if atual == novo:
            iguais += 1
        elif manifesto.get(rel) != impressao(atual):
            # O arquivo no projeto não é o que o kit escreveu: alguém o editou (ou o
            # projeto é anterior ao manifesto). Sobrescrever aqui apaga trabalho.
            protegidos.append(item)
        else:
            mudados.append(item)

    versao = versao_do_kit()
    anterior = docs / MARCA_VERSAO
    print(f"Atualização para {versao} em {docs.name}/")
    print(f"   versão atual do projeto: {anterior.read_text(encoding='utf-8').strip() if anterior.exists() else 'não registrada'}")
    print(f"   {len(novos)} novo(s) · {len(mudados)} atualizável(is) · {len(protegidos)} protegido(s) · {iguais} sem mudança")
    for rotulo, lista in (("NOVO", novos), ("ATUALIZA", mudados), ("PROTEGIDO", protegidos)):
        for rel, *_ in lista:
            print(f"   {rotulo:10} {rel}")

    if protegidos and not forcar:
        print("\n   PROTEGIDO = você editou este arquivo do kit, ou ele é anterior ao manifesto.")
        print("   Ele NÃO será tocado. Para trazer a versão do kit por cima (perdendo a sua),")
        print("   rode de novo com --forcar — e revise o diff antes de commitar.")

    if simular:
        print("\n(--dry-run: nada foi escrito.)")
        return 0

    a_escrever = novos + mudados + (protegidos if forcar else [])
    if not a_escrever:
        print("\nNada a fazer: o processo já está nesta versão.")
        return 0

    for _rel, alvo, dados in a_escrever:
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_bytes(dados)
    for rel, _alvo, dados in a_escrever:
        manifesto[rel] = impressao(dados)
    escrever_manifesto(docs, manifesto)
    (docs / MARCA_VERSAO).write_text(versao + "\n", encoding="utf-8")

    print(f"\nOK: processo atualizado para {versao}.")
    print("   NADA foi tocado em a_context/, d_history/, e_qa/, no backlog nem nos aprendizados.")
    if protegidos and not forcar:
        print(f"   {len(protegidos)} arquivo(s) preservado(s) por customização — releia a lista acima.")
    print(f"   Revise com: git -C {projeto} diff")
    print(f"   Depois rode: python {docs.name}/scripts/check.py")
    print("   Arquivo removido do kit NÃO é apagado do projeto — confira o diff se algo ficou órfão.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Cria um projeto novo no padrão do repositório.")
    ap.add_argument("destino", help="pasta do projeto novo (será criada)")
    ap.add_argument("--name", "--nome", dest="nome", help="nome do projeto (obrigatório ao criar)")
    ap.add_argument("--tag", help="sigla da pasta de docs (default: derivada do nome)")
    ap.add_argument("--code", "--codigo", dest="codigo", default="src", help="pasta do código (default: src)")
    ap.add_argument("--forcar", "--force", action="store_true", help="permite destino já existente e não vazio")
    ap.add_argument("--upgrade", "--atualizar", dest="upgrade", action="store_true",
                    help="atualiza o PROCESSO de um projeto existente, sem tocar na verdade dele")
    ap.add_argument("--dry-run", "--simular", dest="simular", action="store_true",
                    help="com --upgrade: só mostra o que mudaria")
    args = ap.parse_args()

    if args.upgrade:
        return atualizar(Path(args.destino).resolve(), simular=args.simular, forcar=args.forcar)
    if not args.nome:
        ap.error("--nome é obrigatório ao criar (use --upgrade para atualizar um projeto existente)")

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
    # Sem marca de versão não existe pergunta respondível "em que kit este projeto está?",
    # e sem essa pergunta a atualização vira adivinhação.
    (destino / pasta_docs / MARCA_VERSAO).write_text(versao_do_kit() + "\n", encoding="utf-8")

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
    # `->` em ASCII, não a seta U+2192: ela não existe em cp1252, e com a saída
    # REDIRECIDA num Windows pt-BR este print matava o script — depois de já ter criado
    # o projeto inteiro. É o gêmeo do QA-01 do outro lado: aquele era decodificar a
    # saída do git, este é codificar a nossa.
    print("  5. Sessão com a skill `context-bootstrap` -> preenche o contexto-fonte")
    print(f"  6. python {pasta_docs}/scripts/check.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
