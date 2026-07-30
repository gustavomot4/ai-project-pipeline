#!/usr/bin/env python3
"""Cria um projeto novo a partir deste kit, já limpo.

Uso:
    python scripts/novo-projeto.py ../meu-app
    python scripts/novo-projeto.py ../meu-app --nome "Caixa da Loja"

Copia o kit para a pasta destino excluindo o que é **só do kit** (docs/, exemplos/,
.git, estado de sessão do Obsidian) e zerando os templates. O passo "copie tudo exceto
.git" do README era manual e levava junto o histórico e a análise de OUTRO projeto —
o que viola a regra 6 (estado num lugar só) logo no primeiro dia.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

# Só do kit: nunca vai para um projeto.
EXCLUIR_PASTAS = {".git", "docs", "exemplos", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}
EXCLUIR_ARQUIVOS = {".obsidian/workspace.json", "scripts/novo-projeto.py"}
# Padrões de cruft que nunca devem ser propagados.
EXCLUIR_SUFIXOS = (".bak", ".tmp", ".orig", ".pyc")
# Links para o que ficou no kit têm de virar texto: senão o projeto novo nasce
# com wikilink quebrado e reprovando no primeiro `checar.py`.
SO_DO_KIT = ("docs/", "exemplos/")

raiz = Path(__file__).resolve().parent.parent


def deslinkar(texto: str) -> str:
    """[[exemplos/caso-spo|caso]] -> *caso (fica no kit)* — o alvo não existe no projeto."""

    def troca(m):
        alvo, _, alias = m.group(1).partition("|")
        alvo = alvo.rstrip("\\").strip()
        if not alvo.startswith(SO_DO_KIT):
            return m.group(0)
        rotulo = (alias.strip() or alvo.rsplit("/", 1)[-1]).rstrip("\\")
        return f"*{rotulo} (fica no kit)*"

    return re.sub(r"\[\[([^\]\n]+)\]\]", troca, texto)


def copiar(destino: Path) -> int:
    n = 0
    for origem in sorted(raiz.rglob("*")):
        if origem.is_dir():
            continue  # pastas nascem junto com o primeiro arquivo; pasta vazia é cruft
        rel = origem.relative_to(raiz)
        if any(parte in EXCLUIR_PASTAS for parte in rel.parts):
            continue
        if rel.as_posix() in EXCLUIR_ARQUIVOS or origem.name.endswith(EXCLUIR_SUFIXOS):
            continue
        alvo = destino / rel
        alvo.parent.mkdir(parents=True, exist_ok=True)
        if origem.suffix == ".md":
            alvo.write_text(deslinkar(origem.read_text(encoding="utf-8")), encoding="utf-8")
        else:
            shutil.copy2(origem, alvo)
        n += 1
    return n


def ajustar(destino: Path, nome: str | None) -> None:
    """Aponta o CHANGELOG do projeto para o do kit (que ficou para trás) e nomeia o projeto."""
    changelog = destino / "CHANGELOG.md"
    if changelog.exists():
        txt = changelog.read_text(encoding="utf-8")
        txt = txt.replace(
            "> Histórico do **kit** (não do seu projeto) → [[docs/CHANGELOG-KIT|CHANGELOG-KIT]]. "
            "Nunca misture os dois: `scripts/novo-projeto.py` zera este arquivo e deixa o do kit para trás.\n",
            "> Este arquivo nasceu zerado por `scripts/novo-projeto.py`. O histórico do kit ficou no kit.\n",
        )
        changelog.write_text(txt, encoding="utf-8")

    if nome:
        for arquivo in ("CONTEXT.md", "PLANO.md"):
            p = destino / arquivo
            if p.exists():
                p.write_text(p.read_text(encoding="utf-8").replace("<NOME DO PROJETO>", nome), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Cria um projeto novo a partir deste kit.")
    ap.add_argument("destino", help="pasta do projeto novo (será criada)")
    ap.add_argument("--nome", help="nome do projeto, para preencher CONTEXT.md e PLANO.md")
    ap.add_argument("--forcar", action="store_true", help="permite destino já existente e não vazio")
    args = ap.parse_args()

    destino = Path(args.destino).resolve()
    if destino == raiz:
        print("ERRO: destino é o próprio kit.")
        return 1
    if destino.exists() and any(destino.iterdir()) and not args.forcar:
        print(f"ERRO: {destino} já existe e não está vazia. Use --forcar se for intencional.")
        return 1
    destino.mkdir(parents=True, exist_ok=True)

    n = copiar(destino)
    ajustar(destino, args.nome)

    print(f"OK: {n} arquivos copiados para {destino}")
    print("   Ficaram para trás (são só do kit): docs/, exemplos/, .git/")
    print()
    print("Próximos passos:")
    print(f"  1. cd {destino} && git init")
    print("  2. Abra a pasta como vault do Obsidian (ver GUIA-OBSIDIAN.md)")
    print("  3. Instale as skills de skills/ na sua ferramenta de IA")
    print("  4. Sessão com prompts/00-bootstrap-contexto.md → preenche o CONTEXT.md")
    print("  5. python scripts/checar.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
