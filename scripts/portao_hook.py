#!/usr/bin/env python3
"""Trava do pulo: pular o portão continua permitido, mas deixa rastro.

O relatório `python scripts/task.py evidencia` tem uma seção chamada "O que este relatório
NÃO mede", e um dos itens dela era:

    "Se um commit passou com --no-verify. Não fica rastro no histórico."

Era o buraco mais constrangedor do kit inteiro: o portão de higiene é a coisa que ele mais
vende, e o modo de burlá-lo era invisível — inclusive para a medição que o kit faz de si
mesmo. Um portão cuja taxa de contorno é desconhecida não tem taxa de contorno conhecida
igual a zero; tem taxa desconhecida, e o documento que os confundir está mentindo.

Este hook `PreToolUse` NÃO proíbe o pulo. Proibir seria pior: o `--no-verify` existe porque
às vezes é legítimo (conserto de emergência, commit de material que o portão julga errado),
e trava fechada demais ensina a desinstalar o hook — que é a doença da "checagem que
emudece" vista do outro lado. Ele exige apenas que o pulo **se declare**, na única superfície
que sobrevive à sessão: a mensagem do commit.

    git commit --no-verify -m "fix: sobe hotfix    SEM-PORTAO: CI fora do ar, rodo o check na volta"

Com o marcador, passa. Sem o marcador, recusa e explica. E, porque agora existe rastro,
`evidencia.py` passa a contar os pulos — o item saiu de "não medido" para uma linha do
relatório.

    Instale com:  python scripts/install_hook.py --portao
    Remova com:   python scripts/install_hook.py --portao --remover

**FALHA ABERTA em toda dúvida**, como a trava de escopo: entrada ilegível, comando que não é
git, shell que não dá para separar em palavras — passa, e diz por quê em stderr.

Limite conhecido e NÃO fechado (regra 5: lacuna declarada fica declarada): quem quiser
burlar sem rastro ainda consegue — `git -c core.hooksPath=/dev/null commit`, `HUSKY=0`,
desinstalar o hook, ou simplesmente rodar o git fora do agente. Esta trava cobre o caminho
que a pessoa (ou a IA) toma quando está com pressa, não o de quem quer fraudar.
"""
import json
import re
import shlex
import sys

for _f in (sys.stdout, sys.stderr):
    if hasattr(_f, "reconfigure"):
        _f.reconfigure(errors="replace")

MARCADOR = "SEM-PORTAO:"
# `-n` é o atalho oficial de `--no-verify` no `git commit`. Formas agrupadas (`-nm`) também
# valem, e por isso a checagem de atalho olha letra a letra dentro do bloco de uma hífen só.
LONGAS = {"--no-verify"}


def passa(motivo: str):
    print(f"[portao] liberado: {motivo}", file=sys.stderr)
    sys.exit(0)


def pula_o_portao(palavras) -> bool:
    """Verdadeiro quando este comando é um `git commit`/`git push` que desliga os hooks.

    Trabalha sobre palavras já separadas pelo shlex, e não sobre a string crua, porque
    `-m "corrigi o --no-verify do outro script"` contém o texto e não desliga nada. Casar
    substring aqui seria bloquear commit por falar do assunto — aviso falso, que é a coisa
    que o kit mais condena.
    """
    verbo = None
    for i, p in enumerate(palavras):
        if p == "git":
            verbo = None
            continue
        if verbo is None and p in {"commit", "push"} and i and palavras[i - 1] == "git":
            verbo = p
            continue
        if verbo is None:
            continue
        if p in LONGAS:
            return True
        # Atalho: `-n`, `-nm`, `-an`. Um `--algo` nunca entra aqui (dois hifens).
        if re.fullmatch(r"-[A-Za-z]+", p) and "n" in p[1:] and verbo == "commit":
            return True
        if p in {"&&", "||", ";", "|"}:
            verbo = None
    return False


def main() -> int:
    try:
        evento = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        passa("não consegui ler a entrada do hook")

    if evento.get("tool_name") != "Bash":
        sys.exit(0)

    comando = (evento.get("tool_input") or {}).get("command") or ""
    if "git" not in comando:
        sys.exit(0)

    try:
        palavras = shlex.split(comando)
    except ValueError:
        passa("não consegui separar o comando em palavras (aspas abertas?)")

    if not pula_o_portao(palavras):
        sys.exit(0)

    if MARCADOR in comando:
        motivo = comando.split(MARCADOR, 1)[1].strip().strip('"\'').splitlines()[0]
        print(f"[portao] pulo declarado, e ele fica no histórico: {motivo[:120]}", file=sys.stderr)
        sys.exit(0)

    print(
        f"BLOQUEADO: este commit desliga o portão de higiene e não diz por quê.\n\n"
        f"Pular o portão é permitido — pular em silêncio, não. O motivo tem de ficar no\n"
        f"histórico, senão ninguém (nem a medição do próprio kit) consegue saber quantas\n"
        f"vezes o portão foi contornado, e um portão com taxa de contorno desconhecida não\n"
        f"tem taxa de contorno igual a zero.\n\n"
        f"Acrescente o marcador à mensagem do commit:\n"
        f'  git commit --no-verify -m "fix: … {MARCADOR} <o motivo, em uma linha>"\n\n'
        f"Saídas melhores, em ordem:\n"
        f"  1. Conserte o que o portão apontou — quase sempre é mais rápido que justificar.\n"
        f"  2. Se o portão está ERRADO, isso é achado: registre QA-NN e pule com o marcador.\n"
        f"  3. Se é emergência, pule com o marcador e volte a rodar `python scripts/check.py` depois.\n",
        file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
