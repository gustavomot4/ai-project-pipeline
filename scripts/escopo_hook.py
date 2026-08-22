#!/usr/bin/env python3
"""Trava de escopo: transforma a regra 2 do CLAUDE.md em portão de máquina.

A regra diz: *"Escopo é o módulo desta sessão. Precisa mexer em outro? Pare e avise."*
Até agora isso era **prosa no prompt** — e prosa no prompt é pedido, não trava. Um
benchmarking do kit contra oito alternativas de mercado marcou exatamente esse ponto: o
kit levava nota 3 em "papéis especializados" porque nada impedia a IA de fazer diferente,
enquanto Kiro, Claude Code e Continue restringem por lista de ferramentas validada.

Este script é um hook `PreToolUse` do Claude Code. Ele lê a tarefa em andamento no BACKLOG,
descobre a que módulo ela pertence, procura a pasta declarada desse módulo no PLANO, e
recusa escrita fora dela.

    Instale com:  python scripts/install_hook.py --escopo
    Remova com:   python scripts/install_hook.py --escopo --remover

**FALHA ABERTA, sempre, em toda dúvida.** Hook que bloqueia errado ensina a desligar o hook,
e hook desligado é pior que hook ausente — é a mesma doença da "checagem que emudece", vista
do outro lado. Se faltar declaração, se houver duas tarefas em andamento, se o PLANO não
disser a pasta: passa, e diz por que passou.
"""
import json
import re
import sys
from pathlib import Path

for _f in (sys.stdout, sys.stderr):
    if hasattr(_f, "reconfigure"):
        _f.reconfigure(errors="replace")

BACKLOG = "b_process/c_backlog.md"
PLANO = "a_context/b_plan.md"
# Ferramentas que escrevem. Leitura nunca é bloqueada: ler outro módulo para entender o
# contrato é trabalho legítimo, e foi o que a regra 2 sempre permitiu.
ESCREVEM = {"Edit", "Write", "NotebookEdit", "MultiEdit"}


def achar_vault(inicio: Path):
    """Sobe a árvore procurando a pasta de documentação do kit."""
    atual = inicio.resolve()
    for _ in range(8):
        if (atual / "a_context").is_dir() and (atual / BACKLOG).exists():
            return atual
        candidatos = sorted(q for q in atual.glob("*_Project_DOCs") if (q / "a_context").is_dir())
        if len(candidatos) == 1:
            return candidatos[0]
        if atual.parent == atual:
            break
        atual = atual.parent
    return None


def passa(motivo: str):
    """Libera. O motivo vai para stderr porque hook silencioso é hook que ninguém audita —
    quando esta trava deixar passar algo que devia pegar, o motivo estará escrito."""
    print(f"[escopo] liberado: {motivo}", file=sys.stderr)
    sys.exit(0)


def main() -> int:
    try:
        evento = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        passa("não consegui ler a entrada do hook")

    if evento.get("tool_name") not in ESCREVEM:
        sys.exit(0)  # leitura, busca, comando: não é assunto desta trava

    alvo = (evento.get("tool_input") or {}).get("file_path")
    if not alvo:
        passa("a chamada não trouxe caminho de arquivo")

    vault = achar_vault(Path(evento.get("cwd") or "."))
    if vault is None:
        passa("não achei a pasta de documentação do kit a partir daqui")

    raiz = vault.parent if vault.name.endswith("_Project_DOCs") else vault
    try:
        rel = Path(alvo).resolve().relative_to(raiz).as_posix()
    except ValueError:
        passa("o arquivo está fora do repositório")

    # A própria documentação é sempre gravável: é nela que a sessão registra decisão,
    # achado e fecho. Travar isso quebraria o fecho de sessão que o kit exige.
    if vault != raiz and rel.startswith(vault.name + "/"):
        sys.exit(0)

    texto_bl = (vault / BACKLOG).read_text(encoding="utf-8")
    bloco = re.search(r"## Em andamento([^\n]*)\n(.*?)(?=\n## |\Z)", texto_bl, re.S)
    if not bloco:
        passa(f"o {BACKLOG} não tem seção 'Em andamento'")
    ativas = re.findall(r"^- \[ \] *(\S+)", bloco.group(2), re.M)
    ativas = [t for t in ativas if not t.startswith("<")]
    if len(ativas) != 1:
        passa(f"{len(ativas)} tarefa(s) em andamento — a trava só age com exatamente uma")

    tarefa = ativas[0].strip("`")
    card = re.search(rf"^- \[[ x]\] *`?{re.escape(tarefa)}`?\b.*?(?=^- \[|\Z)",
                     texto_bl, re.S | re.M)
    modulo = re.search(r"\*\*M[óo]dulo:?\*\*:?\s*`?(M\d+)`?", card.group(0)) if card else None
    if not modulo:
        passa(f"a tarefa {tarefa} não declara **Módulo:** — tarefa sem módulo não tem escopo a cobrar")
    mod = modulo.group(1)

    texto_plano = (vault / PLANO).read_text(encoding="utf-8") if (vault / PLANO).exists() else ""
    secao = re.search(rf"^#{{2,4}}\s+{mod}\s*[—–:.-].*?(?=^#{{2,4}}\s|\Z)", texto_plano, re.S | re.M)
    pastas = re.search(r"\*\*Pasta:?\*\*:?\s*(.+)", secao.group(0)) if secao else None
    if not pastas:
        passa(f"o {mod} não declara **Pasta:** no PLANO — sem pasta declarada não há fronteira a cobrar")

    bruto = pastas.group(1).strip()
    # Placeholder por preencher NUNCA vira fronteira. O teste pegou este defeito: o texto
    # de exemplo do template trazia um `·` dentro dele, o separador partiu o placeholder
    # ao meio, e a metade sem `<` virou "pasta declarada" — o que faria a trava bloquear
    # TUDO. Bloquear tudo por causa de um campo não preenchido é o pior modo de falha que
    # este arquivo pode ter, então a checagem é sobre a linha INTEIRA, antes de separar.
    if "<" in bruto or ">" in bruto or "…" in bruto or not bruto:
        passa(f"o **Pasta:** do {mod} está por preencher — placeholder não é fronteira")
    permitidas = [p.strip().strip("`").rstrip("/") for p in re.split(r"[·,;]", bruto)]
    # Caminho com espaço no meio é prosa que escapou, não caminho: o padrão do repositório
    # não usa espaço em nome de pasta, e aceitar prosa aqui traz de volta o mesmo defeito.
    permitidas = [p for p in permitidas if p and " " not in p]
    if not permitidas:
        passa(f"o **Pasta:** do {mod} não tem nenhum caminho utilizável")

    if any(rel == p or rel.startswith(p + "/") for p in permitidas):
        sys.exit(0)

    print(
        f"BLOQUEADO pela trava de escopo (regra 2 do CLAUDE.md).\n"
        f"  Tarefa em andamento: {tarefa} · Módulo: {mod}\n"
        f"  Pasta(s) do módulo:  {' · '.join(permitidas)}\n"
        f"  Você tentou escrever em: {rel}\n\n"
        f"A regra é 'escopo é o módulo desta sessão; precisa mexer em outro? pare e avise'.\n"
        f"Saídas legítimas, em ordem de preferência:\n"
        f"  1. PARE e avise o dono — é o que a regra manda, e quase sempre é a resposta certa.\n"
        f"  2. Se o arquivo pertence mesmo ao {mod}, acrescente a pasta ao **Pasta:** dele no PLANO.\n"
        f"  3. Se é achado de outro módulo, registre QA-NN (regra 4) em vez de consertar de carona.\n"
        f"  4. Se o dono decidiu ampliar o escopo, troque a tarefa em andamento no BACKLOG.\n",
        file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
