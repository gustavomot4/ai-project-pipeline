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


# As travas que vivem em `.claude/settings.json`. Uma entrada por trava, e não um `if` por
# trava: a segunda (o pulo do portão) nasceu como cópia da primeira, e cópia é onde as duas
# começam a divergir em silêncio.
TRAVAS = {
    "--escopo": {
        "script": "escopo_hook.py",
        "matcher": "Edit|Write|NotebookEdit|MultiEdit",
        "nome": "trava de escopo",
        "efeito": [
            "   A partir de agora, escrita fora da pasta do módulo em andamento é recusada.",
            "   Ela só age quando há UMA tarefa em andamento, ela declara **Módulo:**, e o",
            "   módulo declara **Pasta:** no PLANO. Em qualquer outra situação, libera e diz por quê.",
        ],
    },
    "--portao": {
        "script": "portao_hook.py",
        "matcher": "Bash",
        "nome": "trava do pulo",
        "efeito": [
            "   A partir de agora, `git commit --no-verify` sem motivo declarado é recusado.",
            "   Pular continua permitido — em silêncio, não: a mensagem precisa trazer",
            "   'SEM-PORTAO: <motivo>', e `task.py evidencia` passa a contar os pulos.",
        ],
    },
}


def trava_de_agente(aqui: Path, topo: Path, remover: bool, flag: str) -> int:
    """Liga (ou desliga) uma trava do Claude Code em `.claude/settings.json`.

    É o único ponto do kit que fala com um agente específico, e por isso mora aqui e não
    dentro do `check.py`: o portão de higiene continua sendo Python puro rodando em git, em
    CI e na mão. Quem não usa Claude Code perde estas travas e mais nada.
    """
    import json
    trava = TRAVAS[flag]
    cfg = topo / ".claude" / "settings.json"
    dados = {}
    if cfg.exists():
        try:
            dados = json.loads(cfg.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"ERRO: {cfg} não é JSON válido. Revise-o à mão antes de instalar a trava.")
            return 1
    try:
        rel = (aqui / trava["script"]).relative_to(topo).as_posix()
    except ValueError:
        print(f"ERRO: {trava['script']} está fora do repositório em {topo}.")
        return 1

    # O comando NÃO pode ser um caminho relativo. Ele é resolvido contra o diretório de
    # trabalho do agente, não contra o repositório — e no momento em que a sessão passa a
    # trabalhar em OUTRA pasta, o caminho aponta para um arquivo que não existe, o hook
    # morre, e o Claude Code trata a morte do hook como BLOQUEIO. Medido em uso: com a
    # trava do pulo instalada assim, uma sessão que mudou de projeto ficou sem executar
    # nenhum comando. Hook que bloqueia por bug próprio é o pior caso do kit, e estava aqui.
    #
    # Três exigências, e a linha abaixo atende as três:
    #   1. achar o script com o cwd em qualquer lugar -> CLAUDE_PROJECT_DIR, e o caminho
    #      absoluto da instalação como reserva;
    #   2. FALHAR ABERTO se o script não estiver lá (outra máquina, outro clone, arquivo
    #      removido) -> sai 0 em silêncio, em vez de travar o trabalho;
    #   3. viajar no git — por isso a variável de ambiente vem PRIMEIRO: quem clonar em
    #      outra máquina continua protegido sem reinstalar nada.
    base = topo.as_posix()
    comando = (
        'python -c "import os,sys,runpy;'
        + "b=os.environ.get('CLAUDE_PROJECT_DIR') or r'" + base + "';"
        + "p=os.path.join(b,'" + rel + "');"
        + "sys.exit(0) if not os.path.exists(p) else runpy.run_path(p,run_name='__main__')\""
    )
    # A entrada é reconhecida pelo NOME DO SCRIPT, não pelo comando inteiro: o comando
    # carrega um caminho absoluto que muda de máquina para máquina, e comparar o comando
    # inteiro faria `--remover` não achar a própria instalação num clone.
    assinatura = trava["script"]
    ganchos = dados.setdefault("hooks", {}).setdefault("PreToolUse", [])
    # Reconhece a entrada pelo COMANDO e não por índice: o dono pode ter outros hooks, e
    # mexer no que não é nosso é como se apaga trabalho alheio sem perceber.
    nossos = [g for g in ganchos
              if any(assinatura in (h.get("command") or "") for h in g.get("hooks", []))]
    if remover:
        if not nossos:
            print(f"Nada a remover (a {trava['nome']} não está instalada).")
            return 0
        dados["hooks"]["PreToolUse"] = [g for g in ganchos if g not in nossos]
        cfg.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"OK: {trava['nome']} removida de {cfg}.")
        return 0
    if nossos:
        print(f"A {trava['nome']} já está instalada em {cfg}.")
        return 0

    ganchos.append({"matcher": trava["matcher"],
                    "hooks": [{"type": "command", "command": comando}]})
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {trava['nome']} instalada em {cfg}.")
    for linha in trava["efeito"]:
        print(linha)
    print(f"   Desligar: python scripts/install_hook.py {flag} --remover")
    return 0


def main() -> int:
    aqui = Path(__file__).resolve().parent          # .../scripts
    raiz = aqui.parent                              # a pasta de documentação (ou o kit)
    topo = topo_do_repo(raiz)
    for flag in TRAVAS:
        if flag in sys.argv:
            if topo is None:
                print("ERRO: não é um repositório git. Rode `git init` primeiro.")
                return 1
            return trava_de_agente(aqui, topo, "--remover" in sys.argv, flag)
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
