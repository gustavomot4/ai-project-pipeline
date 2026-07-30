#!/usr/bin/env python3
"""Higiene do pipeline. Uso: python scripts/checar.py [pasta] [--avisos-reprovam]

Cada checagem existe porque uma regra do kit era só prosa e alguém a pulou.
As regras que a máquina consegue julgar, ela julga aqui; o que sobra é honestamente
do dono (ver "Limites conhecidos" no README).

FALHAS (código 1)
  1. Orçamento do CONTEXT.md            8. Wikilink sem destino
  2. DECISIONS.md inchado               9. Segredo versionado (árvore + histórico)
  3. Fonte única BACKLOG/CONTEXT/DEC.  10. .gitignore sem cobertura mínima de segredo
  4. WIP acima do declarado            11. IDs D-/Q-/QA- citados que não existem
  5. Cruft óbvio                       12. IDs duplicados no DECISIONS
  6. Skill sem name/description        13. "Em andamento" divergindo entre BACKLOG e CONTEXT
  7. Nota órfã (ninguém linka)

AVISOS (não reprovam; com --avisos-reprovam, reprovam)
  frontmatter ausente · placeholders · templates em rascunho
"""
import re
import subprocess
import sys
from pathlib import Path

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ESTRITO = "--avisos-reprovam" in sys.argv
raiz = Path(args[0] if args else ".").resolve()
falhas, avisos = [], []

IGNORAR = {".git", ".venv", "venv", "node_modules", ".obsidian", "__pycache__", ".next", "dist", "build"}
# Notas que existem para serem lidas soltas: não são órfãs por não serem linkadas.
ORFA_OK = {"README", "INICIO", "LEIA-ME", "CHANGELOG-KIT", "ANALISE-USO-SCB"}


def visiveis(padrao):
    return [p for p in raiz.rglob(padrao) if not (set(p.parts) & IGNORAR)]


def sem_codigo(texto):
    texto = re.sub(r"```.*?```", "", texto, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", texto)


notas = sorted(visiveis("*.md"))
corpo = {p: p.read_text(encoding="utf-8") for p in notas}

# 1. Orçamento do CONTEXT.md (regra 1)
ctx = raiz / "CONTEXT.md"
texto_ctx = corpo.get(ctx, "")
if not ctx.exists():
    falhas.append("CONTEXT.md não encontrado na raiz.")
elif len(texto_ctx) > 4000:
    falhas.append(
        f"CONTEXT.md com {len(texto_ctx)} caracteres (orçamento: 4.000). "
        "Corte: detalhe -> contexto/, decisão -> DECISIONS.md, datado -> CHANGELOG.md."
    )

# 2. DECISIONS.md inchado (projeto longo)
dec = raiz / "DECISIONS.md"
texto_dec = corpo.get(dec, "")
if texto_dec and len(texto_dec) > 12000:
    falhas.append(
        "DECISIONS.md acima de 12.000 caracteres — arquive SUPERSEDIDAS/rejeitadas antigas "
        "em dev/decisions-arquivo.md (IDs preservados) e deixe um ponteiro."
    )

# 3. Fonte única (regra 6)
for nome in ("BACKLOG.md", "CONTEXT.md", "DECISIONS.md"):
    achados = visiveis(nome)
    if len(achados) > 1:
        caminhos = ", ".join(str(p.relative_to(raiz)) for p in achados)
        falhas.append(f"{nome} duplicado ({caminhos}) — fonte única!")

# 4. WIP: o limite é o DECLARADO no cabeçalho do BACKLOG ("Em andamento (máx N)").
#    Projeto solo declara 1; um time de 3 declara 3 e o kit deixa de atrapalhar.
bl = raiz / "BACKLOG.md"
texto_bl = corpo.get(bl, "")
em_andamento = []
if texto_bl:
    bloco = re.search(r"## Em andamento([^\n]*)\n(.*?)(?=\n## |\Z)", texto_bl, re.S)
    if bloco:
        limite = int(m.group(1)) if (m := re.search(r"máx\s*(\d+)", bloco.group(1))) else 1
        em_andamento = re.findall(r"^- \[ \] *(\S+)", bloco.group(2), re.M)
        if len(em_andamento) > limite:
            falhas.append(
                f"BACKLOG.md: {len(em_andamento)} itens 'Em andamento', limite declarado é {limite} "
                "— termine, despromova, ou suba o limite no cabeçalho se o time cresceu."
            )

# 5. Cruft óbvio
cruft = [p for pat in ("*.bak", "*.tmp", "*.orig", ".fuse_hidden*") for p in visiveis(pat)]
if cruft:
    falhas.append("Cruft: " + ", ".join(str(p.relative_to(raiz)) for p in cruft[:10]))

# 6. Skills: existem e têm frontmatter com name + description
dir_skills = raiz / "skills"
if dir_skills.is_dir():
    encontradas = sorted(dir_skills.glob("*/SKILL.md"))
    if not encontradas:
        falhas.append("skills/ existe mas não tem nenhum SKILL.md — os agentes do pipeline estão faltando.")
    for skill in encontradas:
        cabeca = corpo.get(skill, skill.read_text(encoding="utf-8"))[:800]
        rel = skill.relative_to(raiz)
        if not cabeca.startswith("---"):
            falhas.append(f"{rel}: sem frontmatter — a skill não será reconhecida.")
            continue
        if "name:" not in cabeca:
            falhas.append(f"{rel}: frontmatter sem 'name:'.")
        if "description:" not in cabeca:
            falhas.append(f"{rel}: frontmatter sem 'description:' — sem ela a skill não dispara.")

# 7 e 8. Wikilinks: destino que não existe (link quebrado) e nota que ninguém aponta (órfã).
por_caminho = {p.relative_to(raiz).with_suffix("").as_posix() for p in notas}
por_nome = {p.stem for p in notas}
quebrados, apontadas = {}, set()
for nota in notas:
    for bruto in re.findall(r"\[\[([^\]\n]+)\]\]", sem_codigo(corpo[nota])):
        alvo = bruto.split("|")[0].rstrip("\\").split("#")[0].strip()
        if not alvo or alvo.startswith("<") or set(alvo) <= {".", " "}:
            continue
        alvo = alvo[:-3] if alvo.endswith(".md") else alvo
        if alvo in por_caminho or alvo in por_nome:
            apontadas.add(alvo)
            continue
        casa = [c for c in por_caminho if c.endswith("/" + alvo)]
        if casa:
            apontadas.update(casa)
            continue
        quebrados.setdefault(str(nota.relative_to(raiz)), set()).add(alvo)
if quebrados:
    detalhe = "; ".join(f"{a} -> {', '.join(sorted(v))}" for a, v in sorted(quebrados.items())[:8])
    falhas.append(f"Wikilink(s) sem destino: {detalhe}")

orfas = [
    p.relative_to(raiz).as_posix()
    for p in notas
    if p.stem not in ORFA_OK
    and p.stem not in apontadas
    and p.relative_to(raiz).with_suffix("").as_posix() not in apontadas
]
if orfas:
    falhas.append(
        "Nota(s) órfã(s) — ninguém linka, então ninguém lê: " + ", ".join(sorted(orfas)[:8])
    )

# 9. Segredo versionado — a checagem que a skill guardrails-review exige e que faltava aqui.
PADROES = [
    (r"(?i)\b(aws_secret_access_key|aws_access_key_id)\b\s*[:=]", "credencial AWS"),
    (r"\bAKIA[0-9A-Z]{16}\b", "access key AWS"),
    # sem \b à esquerda: DB_PASSWORD / MY_API_KEY não têm fronteira depois do underscore
    (r"(?i)(api[_-]?key|apikey|secret[_-]?key|client[_-]?secret|access[_-]?token|auth[_-]?token|private[_-]?key)\b\s*[:=]\s*['\"][^'\"\s]{12,}", "chave/segredo literal"),
    (r"(?i)(password|senha|passwd|pwd)\b\s*[:=]\s*['\"][^'\"\s]{6,}", "senha literal"),
    (r"-----BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----", "chave privada"),
    (r"\bsk-[A-Za-z0-9]{20,}\b", "token estilo OpenAI"),
    (r"\bgh[pousr]_[A-Za-z0-9]{30,}\b", "token GitHub"),
    (r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b", "token Slack"),
]
EXEMPLO = re.compile(r"(?i)\.example|\.sample|<[^>]*>|xxx+|change[_-]?me|your[_-]|placeholder|exemplo|EXEMPLO")


def varrer(texto, origem, achados):
    for linha_n, linha in enumerate(texto.splitlines(), 1):
        if EXEMPLO.search(linha):
            continue
        for padrao, rotulo in PADROES:
            if re.search(padrao, linha):
                achados.append(f"{origem}:{linha_n} ({rotulo})")
                break


achados_seg = []
for p in visiveis("*"):
    if not p.is_file() or p.suffix in (".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".ico"):
        continue
    try:
        varrer(p.read_text(encoding="utf-8"), p.relative_to(raiz).as_posix(), achados_seg)
    except (UnicodeDecodeError, OSError):
        continue
if (raiz / ".git").is_dir():
    try:
        hist = subprocess.run(
            ["git", "-C", str(raiz), "log", "-p", "--no-color", "-500", "--", "."],
            capture_output=True, text=True, timeout=60, errors="replace",
        ).stdout
        adicionadas = [l[1:] for l in hist.splitlines() if l.startswith("+") and not l.startswith("+++")]
        achados_hist = []
        varrer("\n".join(adicionadas), "histórico do git", achados_hist)
        if achados_hist:
            achados_seg.append(f"histórico do git ({len(achados_hist)} linha[s]) — segredo removido da árvore continua comprometido")
    except (subprocess.SubprocessError, OSError):
        pass
if achados_seg:
    falhas.append("Possível segredo versionado: " + "; ".join(dict.fromkeys(achados_seg))[:400])

# 10. .gitignore cobre o básico de segredo
gi = raiz / ".gitignore"
if not gi.exists():
    falhas.append(".gitignore ausente — o kit assume que ele existe antes do primeiro commit.")
else:
    texto_gi = gi.read_text(encoding="utf-8")
    faltando = [p for p in (".env", "*.pem", "*.key", "id_rsa", "credentials.json", "*.p12") if p not in texto_gi]
    if faltando:
        falhas.append(".gitignore sem cobertura mínima de segredo — faltam: " + ", ".join(faltando))

# 11 e 12. Integridade dos IDs rastreáveis (regra 4).
if texto_dec:
    definidos = set(re.findall(r"^\|\s*((?:D|Q|QA)-\d+)\s*\|", texto_dec, re.M))
    repetidos = [i for i in definidos if len(re.findall(rf"^\|\s*{re.escape(i)}\s*\|", texto_dec, re.M)) > 1]
    if repetidos:
        falhas.append("ID duplicado no DECISIONS.md: " + ", ".join(sorted(repetidos)) + " — cada ID é único e append-only.")
    citados = {}
    for nota in notas:
        # docs/ é histórico do kit e cita IDs de OUTROS projetos: fora da checagem.
        if nota == dec or "docs" in nota.relative_to(raiz).parts:
            continue
        for i in set(re.findall(r"\b((?:D|Q|QA)-\d+)\b", sem_codigo(corpo[nota]))):
            citados.setdefault(i, set()).add(nota.relative_to(raiz).as_posix())
    fantasmas = {i: v for i, v in citados.items() if i not in definidos and not re.fullmatch(r"(D|Q|QA)-0*(0|NN)", i)}
    if fantasmas:
        detalhe = "; ".join(f"{i} (em {', '.join(sorted(v))})" for i, v in sorted(fantasmas.items())[:6])
        falhas.append(f"ID citado que não existe no DECISIONS.md: {detalhe}")

# 13. "Em andamento" tem de bater entre BACKLOG e CONTEXT (regra 6, fonte única).
if em_andamento and texto_ctx:
    linha_ctx = re.search(r"\*\*Em andamento[^:]*:\*\*\s*(.+)", texto_ctx)
    if linha_ctx and "<" not in linha_ctx.group(1):
        if not any(t in linha_ctx.group(1) for t in em_andamento):
            falhas.append(
                f"'Em andamento' divergente: BACKLOG diz {', '.join(em_andamento)}, "
                f"CONTEXT diz \"{linha_ctx.group(1).strip()[:60]}\" — o estado tem de morar num lugar só."
            )

# --- Avisos ---
sem_fm = [p.relative_to(raiz).as_posix() for p in notas if not corpo[p].startswith("---")]
if sem_fm:
    avisos.append(f"{len(sem_fm)} nota(s) sem frontmatter: " + ", ".join(sem_fm[:5]))

placeholders = re.findall(r"<[A-Za-zÀ-ú][^<>\n]{2,60}>", texto_ctx)
if placeholders:
    amostra = ", ".join(dict.fromkeys(placeholders[:3]))
    avisos.append(
        f"CONTEXT.md ainda tem {len(placeholders)} placeholder(s) (ex.: {amostra}). "
        "Rode a Fase 0 (skills/bootstrap-contexto) antes de pedir código."
    )
for nome in ("PLANO.md", "DECISIONS.md", "BACKLOG.md"):
    arq = raiz / nome
    if arq.exists() and re.search(r"^status:\s*rascunho\s*$", arq.read_text(encoding="utf-8"), re.M):
        avisos.append(f"{nome} ainda está em 'status: rascunho' (template não preenchido).")

if avisos:
    print("AVISOS:")
    for a in avisos:
        print(" -", a)
    print()
if ESTRITO:
    falhas.extend(avisos)

if falhas:
    print("FALHOU:")
    for f in falhas:
        print(" -", f)
    print(f"\n{len(falhas)} problema(s). Nada avança até fechar — é para isso que o portão existe.")
    sys.exit(1)

print("OK: orçamento, fonte única, WIP, skills, links, órfãs, segredos, gitignore, IDs e sincronia de estado.")
