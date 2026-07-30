#!/usr/bin/env python3
"""Higiene do pipeline. Uso: python scripts/checar.py [pasta-do-projeto]

Valida as regras que o kit trata como não-negociáveis:
  1. Orçamento do CONTEXT.md (regra 1)          5. Cruft óbvio
  2. DECISIONS.md inchado                        6. Skills presentes e com frontmatter válido
  3. Fonte única de BACKLOG/CONTEXT/DECISIONS    7. Wikilinks que não resolvem (vault quebrado)
  4. Máximo 1 tarefa "Em andamento" (WIP=1)      8. Frontmatter e placeholders (avisos)

Falhas reprovam (código 1). Avisos não — projeto novo começa cheio deles.
"""
import re
import sys
from pathlib import Path

raiz = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
falhas = []
avisos = []

IGNORAR = {".git", ".venv", "venv", "node_modules", ".obsidian", "__pycache__", ".next", "dist", "build"}


def visiveis(padrao):
    return [p for p in raiz.rglob(padrao) if not (set(p.parts) & IGNORAR)]


notas = sorted(visiveis("*.md"))

# 1. Orçamento do CONTEXT.md (regra 1)
ctx = raiz / "CONTEXT.md"
if ctx.exists():
    texto_ctx = ctx.read_text(encoding="utf-8")
    n = len(texto_ctx)
    if n > 4000:
        falhas.append(
            f"CONTEXT.md com {n} caracteres (orçamento: 4.000). "
            "Corte: detalhe -> contexto/, decisão -> DECISIONS.md, datado -> CHANGELOG.md."
        )
else:
    texto_ctx = ""
    falhas.append("CONTEXT.md não encontrado na raiz.")

# 2. DECISIONS.md inchado (projeto longo)
dec = raiz / "DECISIONS.md"
if dec.exists() and len(dec.read_text(encoding="utf-8")) > 12000:
    falhas.append(
        "DECISIONS.md acima de 12.000 caracteres — arquive SUPERSEDIDAS/rejeitadas antigas "
        "em dev/decisions-arquivo.md (IDs preservados) e deixe um ponteiro."
    )

# 3. Fonte única (regra 6)
for nome in ("BACKLOG.md", "CONTEXT.md", "DECISIONS.md"):
    achados = visiveis(nome)
    if len(achados) > 1:
        caminhos = ", ".join(str(p.relative_to(raiz)) for p in achados)
        falhas.append(f"{nome} duplicado ({caminhos}) — fonte única!")

# 4. WIP = 1
bl = raiz / "BACKLOG.md"
if bl.exists():
    txt = bl.read_text(encoding="utf-8")
    bloco = re.search(r"## Em andamento.*?(?=\n## |\Z)", txt, re.S)
    if bloco and len(re.findall(r"^- \[ \]", bloco.group(0), re.M)) > 1:
        falhas.append("BACKLOG.md: mais de 1 item 'Em andamento' — termine ou despromova.")

# 5. Cruft óbvio
cruft = [p for pat in ("*.bak", "*.tmp", "*.orig", ".fuse_hidden*") for p in visiveis(pat)]
if cruft:
    falhas.append("Cruft: " + ", ".join(str(p.relative_to(raiz)) for p in cruft[:10]))

# 6. Skills: existem e têm frontmatter com name + description
dir_skills = raiz / "skills"
if dir_skills.is_dir():
    encontradas = sorted(dir_skills.glob("*/SKILL.md"))
    if not encontradas:
        falhas.append("skills/ existe mas não tem nenhum SKILL.md — os agentes do pipeline estão faltando.")
    for skill in encontradas:
        cabeca = skill.read_text(encoding="utf-8")[:800]
        rel = skill.relative_to(raiz)
        if not cabeca.startswith("---"):
            falhas.append(f"{rel}: sem frontmatter — a skill não será reconhecida.")
            continue
        if "name:" not in cabeca:
            falhas.append(f"{rel}: frontmatter sem 'name:'.")
        if "description:" not in cabeca:
            falhas.append(f"{rel}: frontmatter sem 'description:' — sem ela a skill não dispara.")

# 7. Wikilinks que não resolvem
# O vault vive de [[links]]: link quebrado é instrução que nem você nem o agente conseguem seguir.
por_caminho = {p.relative_to(raiz).with_suffix("").as_posix() for p in notas}
por_nome = {p.stem for p in notas}
quebrados = {}
for nota in notas:
    texto = re.sub(r"```.*?```", "", nota.read_text(encoding="utf-8"), flags=re.S)
    texto = re.sub(r"`[^`\n]*`", "", texto)  # código inline costuma citar [[link]] como exemplo
    for bruto in re.findall(r"\[\[([^\]\n]+)\]\]", texto):
        # dentro de tabela o alias vem como \| — tire a barra antes de separar
        alvo = bruto.split("|")[0].rstrip("\\").split("#")[0].strip()
        if not alvo or alvo.startswith("<") or set(alvo) <= {".", " "}:
            continue  # placeholder de template ou [[...]] usado como exemplo
        alvo = alvo[:-3] if alvo.endswith(".md") else alvo
        if alvo in por_caminho or alvo in por_nome:
            continue
        if any(c.endswith("/" + alvo) for c in por_caminho):
            continue
        quebrados.setdefault(str(nota.relative_to(raiz)), set()).add(alvo)
if quebrados:
    detalhe = "; ".join(f"{arq} -> {', '.join(sorted(a))}" for arq, a in sorted(quebrados.items())[:8])
    falhas.append(f"Wikilink(s) sem destino: {detalhe}")

# 8. Frontmatter ausente e templates não preenchidos (avisos)
sem_fm = [str(p.relative_to(raiz)) for p in notas if not p.read_text(encoding="utf-8").startswith("---")]
if sem_fm:
    avisos.append(
        f"{len(sem_fm)} nota(s) sem frontmatter (tags/status), não agrupadas pelo Obsidian: "
        + ", ".join(sem_fm[:5])
    )

placeholders = re.findall(r"<[A-Za-zÀ-ú][^<>\n]{2,60}>", texto_ctx)
if placeholders:
    amostra = ", ".join(dict.fromkeys(placeholders[:3]))
    avisos.append(
        f"CONTEXT.md ainda tem {len(placeholders)} placeholder(s) por preencher (ex.: {amostra}). "
        "Rode a Fase 0 (prompts/00-bootstrap-contexto) antes de pedir código."
    )
for nome in ("PLANO.md", "DECISIONS.md", "BACKLOG.md"):
    arq = raiz / nome
    if arq.exists() and re.search(r"^status:\s*rascunho\s*$", arq.read_text(encoding="utf-8"), re.M):
        avisos.append(f"{nome} ainda está marcado como 'status: rascunho' (template não preenchido).")

if avisos:
    print("AVISOS:")
    for a in avisos:
        print(" -", a)
    print()

if falhas:
    print("FALHOU:")
    for f in falhas:
        print(" -", f)
    sys.exit(1)

print("OK: contexto no orçamento, fonte única, WIP<=1, skills válidas, links resolvem, sem cruft.")
