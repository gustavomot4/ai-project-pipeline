#!/usr/bin/env python3
"""Portão da MENSAGEM de commit: o padrão da equipe, cobrado por máquina.

    python scripts/mensagem_hook.py <arquivo-da-mensagem>     (o git chama assim)
    python scripts/install_hook.py --mensagem                 (instala)
    python scripts/install_hook.py --mensagem --remover       (desinstala)

O padrão da equipe (STF PSS) define a mensagem como:

    <STATUS>: <Tipo>: <Descrição>

`STATUS` é `OK` (completo, funcional e revisado) ou `NOK` (trabalho em progresso). `Tipo` é um
da lista fechada abaixo. Detalhe adicional vai no SEGUNDO `-m`, não na primeira linha.

Por que isto é hook e não recomendação: até agora o formato do commit era prosa no padrão do
repositório — e prosa no padrão é pedido, não trava. O kit já aprendeu essa lição duas vezes
(a regra de escopo virou `escopo_hook.py`, o pulo do portão virou `portao_hook.py`), e o
argumento é o mesmo: o que não é cobrado por máquina, é cobrado da memória de alguém.

**O `check.py` não consegue fazer isto.** Ele roda no `pre-commit`, que acontece ANTES de a
mensagem existir. Só o `commit-msg` vê a mensagem — daí um hook separado.

FALHA ABERTA em tudo que não é a primeira linha: merge automático do git, revert, fixup,
squash e mensagem vazia (commit abortado) passam sem discussão. Hook que bloqueia o que o
próprio git escreveu ensina a desligar o hook.
"""
import re
import sys
from pathlib import Path

for _f in (sys.stdout, sys.stderr):
    if hasattr(_f, "reconfigure"):
        _f.reconfigure(errors="replace")

STATUS = ("OK", "NOK")
# Lista fechada do padrão da equipe. Ordem igual à da página, para conferência lado a lado.
TIPOS = ("Feat", "Fix", "Doc", "Infra", "Config", "Chore", "Deploy", "Test", "Style", "Merge")
PADRAO = re.compile(rf"^({'|'.join(STATUS)}): ({'|'.join(TIPOS)}): \S.*")
# O git escreve estas sozinho. Bloqueá-las seria bloquear o git.
AUTOMATICAS = ("Merge ", "Revert ", "fixup!", "squash!", "amend!")


def main() -> int:
    if len(sys.argv) < 2:
        print("[mensagem] liberado: sem arquivo de mensagem", file=sys.stderr)
        return 0
    try:
        bruto = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
    except OSError as erro:
        print(f"[mensagem] liberado: não consegui ler a mensagem ({erro})", file=sys.stderr)
        return 0

    linhas = [l for l in bruto.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    if not linhas:
        return 0  # mensagem vazia: o próprio git aborta o commit
    primeira = linhas[0].strip()

    if primeira.startswith(AUTOMATICAS):
        print("[mensagem] liberado: mensagem gerada pelo git", file=sys.stderr)
        return 0
    if PADRAO.match(primeira):
        return 0

    # Diagnóstico específico vale mais que "formato inválido": o erro mais comum é o tipo
    # em minúscula ou fora da lista, e dizer QUAL é o erro evita a segunda tentativa errada.
    diagnostico = "a primeira linha não está no formato do padrão da equipe."
    m = re.match(r"^\s*([A-Za-z]+)\s*:\s*([A-Za-z]+)?", primeira)
    if m:
        st, tp = m.group(1), (m.group(2) or "")
        if st.upper() in STATUS and st not in STATUS:
            diagnostico = f"o status vai em maiúscula: use `{st.upper()}:`, não `{st}:`."
        elif st.upper() not in STATUS:
            diagnostico = f"`{st}` não é status. A linha começa com `OK:` ou `NOK:`."
        elif tp and tp.capitalize() in TIPOS and tp not in TIPOS:
            diagnostico = f"o tipo vai capitalizado: use `{tp.capitalize()}`, não `{tp}`."
        elif tp and tp.capitalize() not in TIPOS:
            diagnostico = f"`{tp}` não é um tipo do padrão."

    print(
        f"COMMIT BLOQUEADO — {diagnostico}\n\n"
        f"  sua mensagem: {primeira[:100]}\n\n"
        f"  formato:  <STATUS>: <Tipo>: <Descrição>\n"
        f"  STATUS :  OK (completo, funcional e revisado) | NOK (em progresso)\n"
        f"  Tipo   :  {' · '.join(TIPOS)}\n\n"
        f"  exemplo:  OK: Feat: Adicionar endpoint de execução de testes (D-12)\n"
        f"            NOK: Fix: Tentativa de correção no timeout (QA-07)\n\n"
        f"Detalhe adicional vai no segundo -m, não na primeira linha:\n"
        f'  git commit -m "OK: Fix: Corrigir parser do relatório (QA-07)" \\\n'
        f'             -m "A causa era o padding das tabelas; teste de regressão junto."\n\n'
        f"A regra do kit continua valendo por cima desta: bug cita o QA-NN e decisão cita o\n"
        f"D-NN, e o portão reprova ID que não existe.\n",
        file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
