#!/usr/bin/env python3
"""Instala o pre-commit que roda scripts/check.py antes de cada commit.

    python scripts/install_hook.py            # instala
    python scripts/install_hook.py --remover   # desinstala

Por que isto existe: o kit tem 188 itens de checklist e apenas 16 têm trava
automática. O resto dependia de você lembrar de rodar o script.
Um portão que só funciona quando alguém lembra não é portão. Com o hook, a
higiene passa a ser o padrão e pular vira ato deliberado (`git commit --no-verify`).
"""
import stat
import subprocess
import sys
from pathlib import Path

# O git emite caminhos em UTF-8. `text=True` SOZINHO decodifica com o encoding do
# SISTEMA — cp1252 num Windows pt-BR — e um caminho com acento ("Área de Trabalho",
# nome real da pasta sob OneDrive KFM em português) derruba a thread leitora com
# UnicodeDecodeError. Como ele é ValueError, os `except` abaixo não pegam: `stdout`
# volta None e o erro que aparece é um AttributeError longe da causa.
UTF8 = {"encoding": "utf-8", "errors": "replace"}

# Rede de segurança da SAÍDA (o gêmeo do QA-01). Saída redirecionada num Windows pt-BR
# usa cp1252, não UTF-8: um caractere fora dele — uma seta, um "≤" — mata o script na
# hora de IMPRIMIR, depois de todo o trabalho feito. `errors="replace"` degrada em vez
# de matar, e não muda nada no console, que já é UTF-8.
for _fluxo in (sys.stdout, sys.stderr):
    if hasattr(_fluxo, "reconfigure"):
        _fluxo.reconfigure(errors="replace")

MARCA = "# pipeline-projetos-IA: portão de higiene"
# O padrão põe a documentação em `77777777_<TAG>_Project_DOCs/`, então `scripts/check.py`
# raramente está na raiz do repositório. O caminho é calculado na instalação e gravado
# no hook — o script se acha sozinho a partir dali.
CAMINHO_CHECK = "@@CHECK@@"
# `command -v python3` não serve no Windows: o sistema instala em WindowsApps um
# atalho python3.exe que ESTÁ no PATH, não executa nada e imprime "Python não foi
# encontrado; executar sem argumentos para instalar do Microsoft Store". O hook
# tomava esse stub por interpretador e bloqueava TODO commit — falha fechada pelo
# motivo errado, que ensina o mesmo `--no-verify` que a auditoria condenou.
# Por isso aqui se testa se o candidato RODA, não se ele existe.
CORPO = f"""#!/bin/sh
{MARCA}
# Remova com: python {CAMINHO_CHECK.replace('check.py', 'install_hook.py')} --remover
# Pule uma vez com: git commit --no-verify

cd "$(git rev-parse --show-toplevel)" || exit 1

PY=""
for cand in python3 python py; do
  if "$cand" -c "import sys; sys.exit(0)" >/dev/null 2>&1; then PY="$cand"; break; fi
done

if [ -z "$PY" ]; then
  echo ""
  echo "AVISO: nenhum Python executável encontrado — o portão de higiene NÃO rodou."
  echo "       Isto é falha de ambiente, não commit limpo. Instale o Python e rode"
  echo "       'python {CAMINHO_CHECK}' antes de confiar neste commit."
  echo ""
  exit 0
fi

"$PY" "{CAMINHO_CHECK}" || {{
  echo ""
  echo "commit bloqueado pelo portão de higiene ({CAMINHO_CHECK})."
  echo "Corrija o que está acima, ou use 'git commit --no-verify' se souber o que está fazendo."
  exit 1
}}
"""


def dir_hooks(raiz: Path) -> Path | None:
    try:
        saida = subprocess.run(
            ["git", "-C", str(raiz), "rev-parse", "--git-path", "hooks"],
            capture_output=True, text=True, check=True, **UTF8,
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        return None
    caminho = Path(saida)
    return caminho if caminho.is_absolute() else raiz / caminho


def topo_do_repo(inicio: Path) -> Path | None:
    try:
        saida = subprocess.run(
            ["git", "-C", str(inicio), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True, **UTF8,
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        return None
    return Path(saida).resolve()


def main() -> int:
    aqui = Path(__file__).resolve().parent          # .../scripts
    raiz = aqui.parent                              # a pasta de documentação (ou o kit)
    topo = topo_do_repo(raiz)
    hooks = dir_hooks(raiz)
    if hooks is None or topo is None:
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

    # O hook roda a partir do topo do repositório; o caminho do check.py é relativo a ele.
    # Num projeto no padrão isso vira 77777777_<TAG>_Project_DOCs/scripts/check.py.
    try:
        rel_check = (aqui / "check.py").relative_to(topo).as_posix()
    except ValueError:
        print(f"ERRO: {aqui / 'check.py'} está fora do repositório em {topo}.")
        return 1
    corpo = CORPO.replace("@@CHECK@@", rel_check)

    ja_existe = hook.exists()
    if ja_existe and MARCA not in hook.read_text(encoding="utf-8"):
        print(f"ERRO: já existe um pre-commit de outra origem em {hook}.")
        print(f"      Revise-o à mão e acrescente a linha: python {rel_check} || exit 1")
        return 1

    hook.write_text(corpo, encoding="utf-8", newline="\n")
    hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"OK: hook {'atualizado' if ja_existe else 'instalado'} em {hook}")
    print(f"   A partir de agora todo commit roda {rel_check} e falha se a higiene falhar.")
    print("   Pular uma vez: git commit --no-verify")
    return 0


if __name__ == "__main__":
    sys.exit(main())
