#!/usr/bin/env python3
"""Instala o pre-commit que roda scripts/checar.py antes de cada commit.

    python scripts/instalar-hook.py            # instala
    python scripts/instalar-hook.py --remover   # desinstala

Por que isto existe: a auditoria do kit mediu 8 de 163 itens de checklist
verificados por máquina. O resto dependia de você lembrar de rodar o script.
Um portão que só funciona quando alguém lembra não é portão. Com o hook, a
higiene passa a ser o padrão e pular vira ato deliberado (`git commit --no-verify`).
"""
import stat
import subprocess
import sys
from pathlib import Path

MARCA = "# pipeline-projetos-IA: portão de higiene"
CORPO = f"""#!/bin/sh
{MARCA}
# Remova com: python scripts/instalar-hook.py --remover
# Pule uma vez com: git commit --no-verify

command -v python3 >/dev/null 2>&1 && PY=python3 || PY=python
"$PY" scripts/checar.py || {{
  echo ""
  echo "commit bloqueado pelo portão de higiene (scripts/checar.py)."
  echo "Corrija o que está acima, ou use 'git commit --no-verify' se souber o que está fazendo."
  exit 1
}}
"""


def dir_hooks(raiz: Path) -> Path | None:
    try:
        saida = subprocess.run(
            ["git", "-C", str(raiz), "rev-parse", "--git-path", "hooks"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        return None
    caminho = Path(saida)
    return caminho if caminho.is_absolute() else raiz / caminho


def main() -> int:
    raiz = Path(__file__).resolve().parent.parent
    hooks = dir_hooks(raiz)
    if hooks is None:
        print("ERRO: não é um repositório git (ou o git não está no PATH). Rode `git init` primeiro.")
        return 1
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "pre-commit"

    if "--remover" in sys.argv:
        if hook.exists() and MARCA in hook.read_text(encoding="utf-8"):
            hook.unlink()
            print("OK: hook removido. A higiene volta a depender de você rodar o script.")
        else:
            print("Nada a remover (não há hook deste kit instalado).")
        return 0

    if hook.exists() and MARCA not in hook.read_text(encoding="utf-8"):
        print(f"ERRO: já existe um pre-commit de outra origem em {hook}.")
        print("      Revise-o à mão e acrescente a linha: python scripts/checar.py || exit 1")
        return 1

    hook.write_text(CORPO, encoding="utf-8", newline="\n")
    hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"OK: hook instalado em {hook}")
    print("   A partir de agora todo commit roda scripts/checar.py e falha se a higiene falhar.")
    print("   Pular uma vez: git commit --no-verify")
    return 0


if __name__ == "__main__":
    sys.exit(main())
