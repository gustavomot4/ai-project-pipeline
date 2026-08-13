#!/usr/bin/env python3
"""Candidatas a arquivamento no registro de decisões.

Uso: python scripts/arquivar.py [pasta] [--aplicar] [--incluir-rejeitadas]

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
IGNORAR = {".git", ".venv", "venv", "node_modules", ".obsidian", "__pycache__",
           ".pytest_cache", ".mypy_cache", ".ruff_cache", ".next", "dist", "build"}
# Citam IDs de OUTROS projetos ou são o próprio registro: não contam como "alguém cita".
HISTORICAS = {"d_history", "e_qa", "docs"}

args = [a for a in sys.argv[1:] if not a.startswith("--")]
APLICAR = "--aplicar" in sys.argv
INCLUIR_REJEITADAS = "--incluir-rejeitadas" in sys.argv
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
