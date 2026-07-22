#!/usr/bin/env python3
"""Higiene do kit. Uso: python scripts/checar.py [pasta-do-projeto]"""
import re
import sys
from pathlib import Path

raiz = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
falhas = []

IGNORAR = {".git", ".venv", "venv", "node_modules", ".obsidian", "__pycache__"}


def visiveis(padrao):
    return [p for p in raiz.rglob(padrao) if not (IGNORAR & set(p.parts))]


# 1. Orçamento do CONTEXT.md (regra 1)
ctx = raiz / "CONTEXT.md"
if ctx.exists():
    n = len(ctx.read_text(encoding="utf-8"))
    if n > 4000:
        falhas.append(
            f"CONTEXT.md com {n} caracteres (orçamento: 4.000). "
            "Corte: detalhe -> contexto/, decisão -> DECISIONS.md, datado -> CHANGELOG.md."
        )
else:
    falhas.append("CONTEXT.md não encontrado na raiz.")

# 1b. DECISIONS.md inchado (projeto longo)
dec = raiz / "DECISIONS.md"
if dec.exists() and len(dec.read_text(encoding="utf-8")) > 12000:
    falhas.append(
        "DECISIONS.md acima de 12.000 caracteres — arquive SUPERSEDIDAS/rejeitadas antigas em dev/decisions-arquivo.md."
    )

# 2. Fonte única (regra 6)
for nome in ("BACKLOG.md", "CONTEXT.md", "DECISIONS.md"):
    achados = visiveis(nome)
    if len(achados) > 1:
        caminhos = ", ".join(str(p.relative_to(raiz)) for p in achados)
        falhas.append(f"{nome} duplicado ({caminhos}) — fonte única!")

# 3. Máximo 1 item em andamento
bl = raiz / "BACKLOG.md"
if bl.exists():
    txt = bl.read_text(encoding="utf-8")
    bloco = re.search(r"## Em andamento.*?(?=\n## |\Z)", txt, re.S)
    if bloco and len(re.findall(r"^- \[ \]", bloco.group(0), re.M)) > 1:
        falhas.append("BACKLOG.md: mais de 1 item 'Em andamento' — termine ou despromova.")

# 4. Cruft óbvio
cruft = [p for pat in ("*.bak", "*.tmp", "*.orig", ".fuse_hidden*") for p in visiveis(pat)]
if cruft:
    falhas.append("Cruft: " + ", ".join(str(p.relative_to(raiz)) for p in cruft[:10]))

if falhas:
    print("FALHOU:")
    for f in falhas:
        print(" -", f)
    sys.exit(1)
print("OK: contexto no orçamento, fonte única, WIP<=1, sem cruft.")
