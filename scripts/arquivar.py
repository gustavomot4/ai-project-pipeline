#!/usr/bin/env python3
"""Candidatas a arquivamento no registro de decisões — e, com `--backlog`, no BACKLOG.

Uso: python scripts/arquivar.py [pasta] [--aplicar] [--incluir-rejeitadas]
     python scripts/arquivar.py [pasta] --backlog [--aplicar]

O modo `--backlog` é a saída da checagem 15. Ele existe porque o BACKLOG era o único
registro sem teto E sem arquivamento, sendo a leitura de ABERTURA de toda sessão de
trabalho: medido no primeiro projeto real, 191.591 caracteres dos quais 173.818 (91%)
eram os 72 cards JÁ FECHADOS. Card fechado vira uma linha com ID e `**Módulo:**`
preservados; a íntegra vai para `e_qa/backlog_archive.md`.

O critério é o do `D-43` do primeiro projeto real construído com o kit: **sai da tabela
quem nenhum `.md` vivo cita.** O critério anterior ("fica o que o código cita") tornava o
corte inalcançável — medido lá: o corte máximo que o honrava ainda deixava o arquivo acima
do teto.

Por que este script existe: 5 das 34 sessões daquele projeto foram gastas encolhendo
arquivo à mão, e a parte cara nunca foi mover o texto — foi DECIDIR o que podia sair.
Isso é mecânico, e mecânico é trabalho de script.

**Relata por padrão; só escreve com `--aplicar`.** O `check.py` declara, em código, que
"script não escreve na verdade de ninguém": o registro de decisões é a verdade do dono.
A exceção existe, é explícita, e exige um ato deliberado — não um efeito colateral.

**REJEITADAS ficam, por padrão.** Elas são a lista-morta: o que impede a IA de re-propor o
que já morreu, e a única coisa que a sessão de evolução varre. No projeto medido, duas
passagens de arquivamento as preservaram DE PROPÓSITO, com a razão escrita — a tese do kit
se defendendo da pressão do próprio orçamento. Use `--incluir-rejeitadas` para abrir mão
disso conscientemente.
"""
import re
import sys
from datetime import date
from pathlib import Path

for _f in (sys.stdout, sys.stderr):
    if hasattr(_f, "reconfigure"):
        _f.reconfigure(errors="replace")

DECISOES = "a_context/c_decisions.md"
ARQUIVO = "e_qa/decisions_archive.md"
BACKLOG = "b_process/c_backlog.md"
ARQUIVO_BL = "e_qa/backlog_archive.md"
IGNORAR = {".git", ".venv", "venv", "node_modules", ".obsidian", "__pycache__",
           ".pytest_cache", ".mypy_cache", ".ruff_cache", ".next", "dist", "build"}
# Citam IDs de OUTROS projetos ou são o próprio registro: não contam como "alguém cita".
HISTORICAS = {"d_history", "e_qa", "docs"}

args = [a for a in sys.argv[1:] if not a.startswith("--")]
APLICAR = "--aplicar" in sys.argv
INCLUIR_REJEITADAS = "--incluir-rejeitadas" in sys.argv
SO_BACKLOG = "--backlog" in sys.argv
inicio = Path(args[0] if args else ".").resolve()


def achar_vault(p: Path) -> Path:
    if (p / "a_context").is_dir():
        return p
    cand = sorted(q for q in p.glob("*_Project_DOCs") if (q / "a_context").is_dir())
    return cand[0] if len(cand) == 1 else p


def sem_bloco_de_codigo(texto: str) -> str:
    """Só o bloco cercado. NÃO remove o trecho entre crases: a casa escreve `D-13`, e
    descartá-lo foi o QA-14 — a checagem enxergava 12% das citações e imprimia verde."""
    return re.sub(r"```.*?```", "", texto, flags=re.S)


raiz = achar_vault(inicio)


def cards_do_backlog(texto: str):
    """Cards como BLOCOS. Cópia deliberada da função de mesmo nome em `check.py`, pelo
    motivo já escrito lá para `sem_bloco_de_codigo`: o kit não tem módulo compartilhado."""
    marcas = [m.start() for m in re.finditer(r"^- \[[ xX]\]", texto, re.M)]
    for ini, fim in zip(marcas, marcas[1:] + [len(texto)]):
        bloco = texto[ini:fim]
        secao = re.search(r"^## ", bloco, re.M)
        yield ini, (bloco[:secao.start()] if secao else bloco)


def id_do_card(bloco: str):
    """O ID do card, ou None. `None` é resposta legítima e importante: a linha de exemplo
    do template é `- [x] T-… — <tarefa>`, com reticência no lugar do número. Arquivar o
    exemplo do template seria o script apagando a documentação que ensina a usá-lo — e o
    ponteiro sairia com `?` no lugar do ID, que é pior que não arquivar: ID que não resolve
    quebra a checagem 10, que é justamente quem cobra o ponteiro."""
    m = re.match(r"^- \[[xX]\]\s*`?([A-Z]+-\d+)`?", bloco.splitlines()[0])
    return m.group(1) if m else None


def ponteiro_de(bloco: str) -> str:
    """A linha que FICA no lugar do card. Preserva duas coisas de propósito: o ID, porque
    o changelog e o DECISIONS o citam e a checagem 10 o cobra; e o `**Módulo:**`, porque a
    checagem 13 lê exatamente esse marcador para saber se um módulo do PLANO tem tarefa —
    engolir o marcador junto com o card faria o módulo virar órfão no dia do arquivamento,
    e o portão acusaria uma lacuna que o arquivamento acabara de inventar."""
    primeira = bloco.splitlines()[0]
    ident = id_do_card(bloco) or "?"
    modulo = re.search(r"\*\*M[óo]dulo:?\*\*:?\s*(M\d+)", bloco)
    titulo = re.sub(r"^- \[[xX]\]\s*`?[A-Z]+-\d+`?\s*[—–\-:]?\s*", "", primeira)
    titulo = re.sub(r"\s*·.*$", "", titulo)
    # Fora TODO `*`, crase e `_`: cortar um título no caractere 57 fecha metade de um
    # `**negrito**` e deixa a linha com marcação desbalanceada, que contamina o render do
    # resto do arquivo. Ponteiro é resumo, não card — não precisa de ênfase, e um ID que
    # perca as crases continua sendo achado pela checagem 10, que lê os dois formatos.
    titulo = re.sub(r"[*`_]", "", titulo).strip()
    if len(titulo) > 60:
        # No espaço, não no meio da palavra: `conte os ded…` é ruído, `conte os…` é resumo.
        titulo = titulo[:60].rsplit(" ", 1)[0].rstrip(" ,;:-–—") + "…"
    partes = [f"- [x] {ident}"]
    if titulo:
        partes.append(f"— {titulo}")
    if modulo:
        partes.append(f"· **Módulo:** {modulo.group(1)}")
    partes.append("· íntegra em [[backlog_archive]]")
    return " ".join(partes) + "\n"


if SO_BACKLOG:
    alvo = raiz / BACKLOG
    if not alvo.exists():
        print(f"FALHOU:\n - {BACKLOG} não encontrado em {raiz}.")
        sys.exit(1)
    texto_bl = alvo.read_text(encoding="utf-8")
    fechados, ignorados = [], []
    for ini, bloco in cards_do_backlog(texto_bl):
        if not re.match(r"^- \[[xX]\]", bloco):
            continue  # card ABERTO é trabalho, não histórico: nunca entra aqui
        alinha = ponteiro_de(bloco)
        if id_do_card(bloco) is None:
            ignorados.append((bloco, "sem ID legível (linha de exemplo do template?)"))
        elif len(alinha) >= len(bloco):
            # Card de uma linha curta já É o próprio ponteiro. Trocá-lo por um ponteiro
            # MAIOR seria o script inchando o arquivo que ele existe para encolher.
            ignorados.append((bloco, "o ponteiro não seria menor que o card"))
        else:
            fechados.append((ini, bloco, alinha))
    print(f"BACKLOG: {len(texto_bl)} caracteres em {alvo.relative_to(raiz)}")
    for bloco, porque in ignorados:
        print(f"  ignorado — {porque}: {bloco.splitlines()[0][:70]}")
    if not fechados:
        print("\nNenhum card arquivável. Se o arquivo está grande, o peso não está em card\n"
              "fechado: card ABERTO é trabalho (vira entrega ou o dono despromove) e prosa\n"
              "de seção é texto do dono — o script não poda nem um nem outro.")
        sys.exit(0)
    ganho = sum(len(b) - len(p) for _, b, p in fechados)
    print(f"Cards fechados arquiváveis: {len(fechados)}, ocupando {sum(len(b) for _, b, _ in fechados)} caracteres.")
    print(f"Economia estimada: {ganho} caracteres ({100 * ganho // max(1, len(texto_bl))}% do arquivo).")
    print("\nCada card fechado vira esta linha (ID e Módulo preservados):")
    for _, _, p in fechados[:5]:
        print("  " + p.rstrip())
    if len(fechados) > 5:
        print(f"  … e mais {len(fechados) - 5}.")
    if not APLICAR:
        print("\nNada foi escrito. Para aplicar: --backlog --aplicar")
        sys.exit(0)

    novo = texto_bl
    for ini, bloco, alinha in reversed(fechados):
        novo = novo[:ini] + alinha + novo[ini + len(bloco):]
    alvo.write_text(novo, encoding="utf-8")

    destino = raiz / ARQUIVO_BL
    destino.parent.mkdir(parents=True, exist_ok=True)
    cabeca = "" if destino.exists() else (
        "---\ntags: [qa, arquivo]\nstatus: atual\n---\n# Cards de backlog arquivados\n\n"
        "> Íntegra dos cards FECHADOS retirados de `b_process/c_backlog.md`. O ID nunca é\n"
        "> reciclado e nada é revertido: a linha viva lá continua com o ID e o `**Módulo:**`.\n"
        "> **Somente leitura.** Reabrir tarefa é card NOVO no BACKLOG, nunca edição aqui.\n\n")
    with destino.open("a", encoding="utf-8") as f:
        f.write(cabeca + f"\n## Retirados do BACKLOG em {date.today().isoformat()}\n\n"
                + "".join(b if b.endswith("\n") else b + "\n" for _, b, _ in fechados))
    print(f"\nAplicado: {len(texto_bl)} -> {len(novo)} caracteres ({len(texto_bl) - len(novo)} a menos).")
    print(f"Íntegras em {ARQUIVO_BL}. Rode `python scripts/check.py` para confirmar o teto.")
    sys.exit(0)

reg = raiz / DECISOES
if not reg.exists():
    print(f"FALHOU:\n - {DECISOES} não encontrado em {raiz}.")
    sys.exit(1)

texto = reg.read_text(encoding="utf-8")
linhas = texto.splitlines(keepends=True)

# Quem é citado por alguém VIVO (fora do registro, fora do histórico/evidência).
citados = set()
for nota in raiz.rglob("*.md"):
    rel = nota.relative_to(raiz)
    if set(nota.parts) & IGNORAR or nota == reg or HISTORICAS & set(rel.parts) \
            or nota.stem == "d_agent_learnings":
        continue
    citados |= set(re.findall(r"\b(D-\d+)\b", sem_bloco_de_codigo(nota.read_text(encoding="utf-8"))))

candidatas, mantidas_por_citacao, rejeitadas_preservadas = [], [], []
for i, linha in enumerate(linhas):
    m = re.match(r"^\|\s*(D-\d+)\s*\|([^|]*)\|([^|]*)\|", linha)
    if not m:
        continue
    ident, _data, status = m.group(1), m.group(2).strip(), m.group(3).upper()
    if _data.startswith("<"):
        continue  # data por preencher = linha de template, não decisão
    if "REJEIT" in status and not INCLUIR_REJEITADAS:
        rejeitadas_preservadas.append(ident)
        continue
    if ident in citados:
        mantidas_por_citacao.append(ident)
        continue
    candidatas.append((i, ident, linha.rstrip("\n")))

print(f"Registro: {len(texto)} caracteres em {reg.relative_to(raiz)}")
print(f"Citadas por arquivo vivo (ficam): {len(mantidas_por_citacao)}"
      + (f" — {', '.join(mantidas_por_citacao[:8])}" if mantidas_por_citacao else ""))
if rejeitadas_preservadas:
    print(f"REJEITADAS preservadas (lista-morta, use --incluir-rejeitadas para soltar): "
          f"{', '.join(rejeitadas_preservadas)}")

if not candidatas:
    print("\nNada a arquivar pelo critério: toda linha não-rejeitada é citada por algum .md vivo.")
    sys.exit(0)

economia = sum(len(l) + 1 for _, _, l in candidatas)
print(f"\nCandidatas ({len(candidatas)}), economia estimada de {economia} caracteres:")
for _, ident, linha in candidatas:
    print(f"  {ident}  {linha[:110]}")

if not APLICAR:
    print("\nNada foi escrito. Para aplicar: --aplicar")
    print("O que --aplicar faz: retira estas linhas da tabela, copia-as íntegras para "
          f"{ARQUIVO} sob uma seção datada, e imprime o ponteiro para você colocar no cabeçalho.")
    sys.exit(0)

fora = {i for i, _, _ in candidatas}
reg.write_text("".join(l for i, l in enumerate(linhas) if i not in fora), encoding="utf-8")

destino = raiz / ARQUIVO
destino.parent.mkdir(parents=True, exist_ok=True)
cabeca = "" if destino.exists() else "---\ntags: [qa, arquivo]\nstatus: atual\n---\n# Registro arquivado\n\n"
bloco = (f"\n## Retiradas da tabela em {date.today().isoformat()}\n"
         "> Íntegra preservada. ID nunca reciclado, nada revertido.\n\n"
         + "\n".join(l for _, _, l in candidatas) + "\n")
with destino.open("a", encoding="utf-8") as f:
    f.write(cabeca + bloco)

novo = reg.read_text(encoding="utf-8")
print(f"\nAplicado: {len(texto)} -> {len(novo)} caracteres ({len(texto) - len(novo)} a menos).")
print(f"Íntegras em {ARQUIVO}.")
print("\nPonteiro para o cabeçalho do registro (prosa é sua, o script não a escreve):")
print("> **Retirados da tabela** (ID preservado, nada revertido): "
      + " ".join(f"`{i}`" for _, i, _ in candidatas) + f" · íntegra em [[decisions_archive]].")
