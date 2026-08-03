#!/usr/bin/env python3
"""Higiene do pipeline. Uso: python scripts/check.py [pasta] [--avisos-reprovam]

Cada checagem existe porque uma regra do kit era só prosa e alguém a pulou.
As regras que a máquina consegue julgar, ela julga aqui; o que sobra é honestamente
do dono (ver "Limites conhecidos" no README).

Os caminhos seguem o padrão do repositório (b_process/e_repository_standard.md):
documentação em a_context/ b_process/ c_technical_docs/ d_history/ e_qa/.
Mudou o padrão? O bloco de constantes no topo é o único lugar a mexer.

FALHAS (código 1)
  1. Orçamento do contexto-fonte        7. Wikilink sem destino
  2. Registro de decisões inchado       8. Segredo versionado (árvore + histórico)
  3. Fonte única (contexto/plano/dec.)  9. .gitignore sem cobertura mínima de segredo
  4. WIP acima do declarado            10. IDs D-/Q-/QA- citados que não existem
  5. Cruft óbvio                       11. IDs duplicados no DECISIONS
  6. Skill sem name/description        12. "Em andamento" divergindo entre BACKLOG e CONTEXT

AVISOS (não reprovam; com --avisos-reprovam, reprovam)
  frontmatter ausente · placeholders · templates em rascunho · nota órfã ·
  arquivo grande não varrido · varredura de histórico que não rodou

Marque uma linha com `checar:ignore` para isentá-la da varredura de segredo
(use só quando o valor for comprovadamente falso — a marca fica visível no diff).
"""
import re
import subprocess
import sys
from pathlib import Path

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ESTRITO = "--avisos-reprovam" in sys.argv
raiz = Path(args[0] if args else ".").resolve()
falhas, avisos = [], []


def achar_vault(inicio: Path) -> Path:
    """No kit, a documentação É a raiz. Num projeto, ela vira `77777777_<TAG>_Project_DOCs/`.
    Sem isto o hook precisaria saber o nome da pasta de docs de cada projeto."""
    if (inicio / "a_context").is_dir():
        return inicio
    candidatos = sorted(p for p in inicio.glob("*_Project_DOCs") if (p / "a_context").is_dir())
    if len(candidatos) == 1:
        return candidatos[0]
    if len(candidatos) > 1:
        nomes = ", ".join(p.name for p in candidatos)
        print(f"FALHOU:\n - Mais de uma pasta de documentação ({nomes}) — o padrão pede uma só.")
        sys.exit(1)
    return inicio


def achar_topo(inicio: Path) -> Path:
    """Raiz do repositório. O padrão põe `.gitignore`, `.gitattributes` e `CLAUDE.md` FORA
    da pasta de documentação — e a varredura de segredo tem de cobrir o código também,
    não só o vault. Sem esta distinção o script varreria um terço do repositório."""
    try:
        saida = subprocess.run(
            ["git", "-C", str(inicio), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True, timeout=15,
        ).stdout.strip()
        return Path(saida).resolve()
    except (subprocess.SubprocessError, OSError):
        return inicio


# DOIS escopos, de propósito:
#   raiz = o vault  -> orçamento, links, órfãs, IDs, WIP, skills
#   topo = o repo   -> .gitignore, cruft, varredura de segredo (árvore + histórico)
raiz = achar_vault(raiz)
topo = achar_topo(raiz)

# --- Layout do padrão do repositório (b_process/e_repository_standard.md) ---------
# Um lugar só define onde cada coisa mora. Mudou o padrão? Mude aqui, e só aqui.
# Os caminhos são relativos à raiz da pasta de documentação (o vault).
CONTEXTO = "a_context/a_context_source.md"      # a verdade: estado, ≤4.000 chars
PLANO = "a_context/b_plan.md"                   # plano congelado
DECISOES = "a_context/c_decisions.md"           # D-NN / Q-NN / QA-NN, append-only
BACKLOG = "b_process/c_backlog.md"              # fonte única de tarefas
SKILLS = "b_process/skills"                     # os agentes instaláveis
# Pastas do vault: só nelas "nota órfã" faz sentido. Markdown do próprio app
# (content/, docs de pacote, README de módulo) não é nota e não bloqueia commit.
PASTAS_VAULT = {"a_context", "b_process", "c_technical_docs", "d_history", "e_qa"}
# Histórico e evidência: citam IDs de OUTROS projetos, ficam fora da checagem de existência.
PASTAS_HISTORICAS = {"d_history", "e_qa"}
# ----------------------------------------------------------------------------------

IGNORAR = {".git", ".venv", "venv", "node_modules", ".obsidian", "__pycache__", ".next", "dist", "build"}
# Notas que existem para serem lidas soltas: não são órfãs por não serem linkadas.
ORFA_OK = {"README", "INDEX", "CLAUDE", "AGENTS"}
# Acima disto o arquivo não é varrido (e o pulo é declarado como aviso, nunca silencioso).
LIMITE_BYTES = 1_000_000


def visiveis(padrao, base=None):
    """Por padrão varre o vault. Passe base=topo para varrer o repositório inteiro."""
    return [p for p in (base or raiz).rglob(padrao) if not (set(p.parts) & IGNORAR)]


def alvos_de_varredura():
    """Universo da varredura de segredo. Com git, é o que o git enxerga — isso respeita
    o .gitignore de graça (sem isso, um CSV de 17 MB em open-data/, já ignorado, era lido
    a cada commit). Sem git, cai para o rglob com a lista fixa de exclusão."""
    if (topo / ".git").is_dir():
        try:
            saida = subprocess.run(
                ["git", "-C", str(topo), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                capture_output=True, text=True, timeout=20, check=True,
            ).stdout
            return [topo / n for n in saida.split("\0") if n]
        except (subprocess.SubprocessError, OSError):
            pass
    return visiveis("*", topo)


def sem_codigo(texto):
    texto = re.sub(r"```.*?```", "", texto, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", texto)


# Notas do repositório inteiro: o padrão deixa CLAUDE.md e README.md fora do vault,
# e um wikilink para eles não pode contar como link quebrado.
notas = sorted(visiveis("*.md", topo))
corpo = {p: p.read_text(encoding="utf-8") for p in notas}

# 1. Orçamento do contexto-fonte (regra 1)
ctx = raiz / CONTEXTO
texto_ctx = corpo.get(ctx, "")
if not ctx.exists():
    falhas.append(f"{CONTEXTO} não encontrado — é onde o padrão do repositório põe o contexto-fonte.")
elif len(texto_ctx) > 4000:
    falhas.append(
        f"{CONTEXTO} com {len(texto_ctx)} caracteres (orçamento: 4.000). "
        f"Corte: detalhe -> a_context/<tema>.md, decisão -> {DECISOES}, datado -> d_history/a_changelog.md."
    )

# 2. Registro de decisões inchado (projeto longo)
dec = raiz / DECISOES
texto_dec = corpo.get(dec, "")
if texto_dec and len(texto_dec) > 12000:
    falhas.append(
        f"{DECISOES} acima de 12.000 caracteres — arquive SUPERSEDIDAS/rejeitadas antigas "
        "em e_qa/decisions_archive.md (IDs preservados) e deixe um ponteiro."
    )

# 3. Fonte única (regra 6) — o mesmo nome em dois lugares é estado duplicado
for nome in (Path(BACKLOG).name, Path(CONTEXTO).name, Path(DECISOES).name):
    achados = visiveis(nome)
    if len(achados) > 1:
        caminhos = ", ".join(str(p.relative_to(raiz)) for p in achados)
        falhas.append(f"{nome} duplicado ({caminhos}) — fonte única!")

# 4. WIP: o limite é o DECLARADO no cabeçalho do BACKLOG ("Em andamento (máx N)").
#    Projeto solo declara 1; um time de 3 declara 3 e o kit deixa de atrapalhar.
bl = raiz / BACKLOG
texto_bl = corpo.get(bl, "")
em_andamento = []
if texto_bl:
    bloco = re.search(r"## Em andamento([^\n]*)\n(.*?)(?=\n## |\Z)", texto_bl, re.S)
    if bloco:
        limite = int(m.group(1)) if (m := re.search(r"máx\s*(\d+)", bloco.group(1))) else 1
        em_andamento = re.findall(r"^- \[ \] *(\S+)", bloco.group(2), re.M)
        if len(em_andamento) > limite:
            falhas.append(
                f"{BACKLOG}: {len(em_andamento)} itens 'Em andamento', limite declarado é {limite} "
                "— termine, despromova, ou suba o limite no cabeçalho se o time cresceu."
            )

# 5. Cruft óbvio
cruft = [p for pat in ("*.bak", "*.tmp", "*.orig", ".fuse_hidden*") for p in visiveis(pat, topo)]
if cruft:
    falhas.append("Cruft: " + ", ".join(str(p.relative_to(topo)) for p in cruft[:10]))

# 6. Skills: existem e têm frontmatter com name + description
dir_skills = raiz / SKILLS
if dir_skills.is_dir():
    encontradas = sorted(dir_skills.glob("*/SKILL.md"))
    if not encontradas:
        falhas.append(f"{SKILLS}/ existe mas não tem nenhum SKILL.md — os agentes do pipeline estão faltando.")
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

# 7. Wikilinks: destino que não existe (link quebrado). A nota órfã virou AVISO — ver abaixo.
por_caminho = {p.relative_to(topo).with_suffix("").as_posix() for p in notas}
por_caminho |= {p.relative_to(raiz).with_suffix("").as_posix() for p in notas if raiz in p.parents}
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
        quebrados.setdefault(nota.relative_to(topo).as_posix(), set()).add(alvo)
if quebrados:
    detalhe = "; ".join(f"{a} -> {', '.join(sorted(v))}" for a, v in sorted(quebrados.items())[:8])
    falhas.append(f"Wikilink(s) sem destino: {detalhe}")

# Nota órfã: AVISO, e só dentro do vault.
# Era FALHA e varria o repositório inteiro — qualquer `content/blog/*.md` ou doc de pacote
# do próprio app bloqueava TODO commit por motivo cosmético. O efeito medido era o pior
# possível: o dono adotava `git commit --no-verify` por hábito e desligava junto o portão
# de segredo, o orçamento e a fonte única. Portão que se aprende a pular não é portão.
orfas = []
for p in notas:
    if p != raiz / p.name and raiz not in p.parents:
        continue  # fora do vault (código do app, README da raiz): não é nota
    rel = p.relative_to(raiz)
    no_vault = len(rel.parts) == 1 or rel.parts[0] in PASTAS_VAULT
    if not no_vault or p.stem in ORFA_OK:
        continue
    if p.stem in apontadas or rel.with_suffix("").as_posix() in apontadas:
        continue
    orfas.append(rel.as_posix())
if orfas:
    avisos.append(
        "Nota(s) órfã(s) no vault — ninguém linka, então ninguém lê: "
        + ", ".join(sorted(orfas)[:8])
    )

# 8. Segredo versionado — a checagem que a skill guardrails-review exige.
#
# Dois erros de desenho que a auditoria de 2026-07-30 mediu (0 de 8 segredos reais
# detectados) e que este bloco corrige:
#   a) o filtro de exemplo descartava a LINHA INTEIRA — um comentário `# ver <ticket-4412>`
#      desligava a checagem. Agora ele avalia só o TRECHO CASADO.
#   b) os padrões exigiam aspas, então a linha de .env (`API_KEY=sk_live_...`), que é o
#      formato mais comum de vazamento, passava. Agora valor sem aspas também casa.
#
# Valor sem aspas: exige dígito, para não casar com prosa ("token: obrigatório").
VALOR = r"""(?:['"](?P<q>[^'"\s]{8,})['"]|(?P<u>(?=[^\s'"]*\d)[^\s'";,)]{12,}))"""
CHAVE = r"(?:api[_-]?key|apikey|secret[_-]?key|client[_-]?secret|access[_-]?token|auth[_-]?token|private[_-]?key|aws_secret_access_key|aws_access_key_id|secret)"
PADROES = [
    # sem \b à esquerda: DB_PASSWORD / MY_API_KEY não têm fronteira depois do underscore
    (rf"(?i){CHAVE}\b\s*[:=]\s*{VALOR}", "chave/segredo literal"),
    (rf"(?i)(?:password|senha|passwd|pwd)\b\s*[:=]\s*{VALOR}", "senha literal"),
    # senha embutida em connection string: postgres://user:SENHA@host
    (r"(?i)\b[a-z][a-z0-9+.-]{2,}://[^\s:@/]{1,64}:(?P<u>[^\s:@/]{6,})@", "senha em connection string"),
    (r"\bAKIA[0-9A-Z]{16}\b", "access key AWS"),
    (r"-----BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----", "chave privada"),
    (r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b", "JWT"),
    (r"\b[sr]k_(live|test)_[A-Za-z0-9]{16,}\b", "chave estilo Stripe"),
    (r"\bsk-[A-Za-z0-9_-]{20,}\b", "token estilo OpenAI"),
    (r"\bgh[pousr]_[A-Za-z0-9]{30,}\b", "token GitHub"),
    (r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b", "token Slack"),
    (r"\bglpat-[A-Za-z0-9_-]{18,}\b", "token GitLab"),
]
# Avaliado SÓ contra o trecho casado (ou contra o valor, quando o padrão o captura).
EXEMPLO = re.compile(r"(?i)<[^>]*>|x{3,}|change[_-]?me|your[_-]|placeholder|exemplo|example|dummy|fake|sample|redacted|\.\.\.|^\$\{|^<%")
ARQUIVO_EXEMPLO = re.compile(r"(?i)(\.example|\.sample|\.template|\.dist)(\.|$)")
ISENTA = re.compile(r"checar:ignore")


def varrer(texto, origem, achados):
    if ARQUIVO_EXEMPLO.search(origem):
        return
    for linha_n, linha in enumerate(texto.splitlines(), 1):
        if ISENTA.search(linha):
            continue
        for padrao, rotulo in PADROES:
            m = re.search(padrao, linha)
            if not m:
                continue
            # o filtro de exemplo olha o valor casado, nunca o resto da linha
            grupos = m.groupdict()
            alvo = grupos.get("q") or grupos.get("u") or m.group(0)
            if EXEMPLO.search(alvo):
                continue
            achados.append(f"{origem}:{linha_n} ({rotulo})")
            break


achados_seg, grandes = [], []
for p in alvos_de_varredura():
    if not p.is_file() or p.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".ico", ".woff", ".woff2"):
        continue
    try:
        if p.stat().st_size > LIMITE_BYTES:
            grandes.append(p.relative_to(topo).as_posix())
            continue
        varrer(p.read_text(encoding="utf-8"), p.relative_to(topo).as_posix(), achados_seg)
    except (UnicodeDecodeError, OSError, ValueError):
        continue
if grandes:
    avisos.append(
        f"{len(grandes)} arquivo(s) acima de 1 MB NÃO varridos por segredo: "
        + ", ".join(sorted(grandes)[:5])
        + " — confira à mão se algum devia ser versionado."
    )

# O histórico é caro de varrer e este script roda em todo commit: por padrão olha
# os 30 commits recentes. A varredura completa é da Fase 6 (skills/revisao-entrega),
# ou aqui com --historico-completo.
COMPLETO = "--historico-completo" in sys.argv
LIMITE_HIST = [] if COMPLETO else ["-30"]  # lista vazia = todos; "-0" significava ZERO commits
if (topo / ".git").is_dir():
    try:
        hist = subprocess.run(
            ["git", "-C", str(topo), "log", "-p", "--no-color", *LIMITE_HIST, "--", "."],
            capture_output=True, text=True, timeout=120 if COMPLETO else 25, errors="replace",
        ).stdout
        adicionadas = [l[1:] for l in hist.splitlines() if l.startswith("+") and not l.startswith("+++")]
        achados_hist = []
        varrer("\n".join(adicionadas), "histórico do git", achados_hist)
        if achados_hist:
            achados_seg.append(f"histórico do git ({len(achados_hist)} linha[s]) — segredo removido da árvore continua comprometido")
    except subprocess.TimeoutExpired:
        # falha aberta com mensagem verde foi achado da auditoria: agora ela aparece
        avisos.append("Varredura do HISTÓRICO estourou o tempo — o histórico NÃO foi verificado nesta rodada.")
    except (subprocess.SubprocessError, OSError) as erro:
        avisos.append(f"Varredura do HISTÓRICO não rodou ({type(erro).__name__}) — o histórico NÃO foi verificado.")
if achados_seg:
    falhas.append("Possível segredo versionado: " + "; ".join(dict.fromkeys(achados_seg))[:400])

# 9. .gitignore cobre o básico de segredo
gi = topo / ".gitignore"
if not gi.exists():
    falhas.append(".gitignore ausente — o kit assume que ele existe antes do primeiro commit.")
else:
    texto_gi = gi.read_text(encoding="utf-8")
    faltando = [p for p in (".env", "*.pem", "*.key", "id_rsa", "credentials.json", "*.p12") if p not in texto_gi]
    if faltando:
        falhas.append(".gitignore sem cobertura mínima de segredo — faltam: " + ", ".join(faltando))

# 10 e 11. Integridade dos IDs rastreáveis (regra 4).
if texto_dec:
    definidos = set(re.findall(r"^\|\s*((?:D|Q|QA)-\d+)\s*\|", texto_dec, re.M))
    repetidos = [i for i in definidos if len(re.findall(rf"^\|\s*{re.escape(i)}\s*\|", texto_dec, re.M)) > 1]
    if repetidos:
        falhas.append(f"ID duplicado em {DECISOES}: " + ", ".join(sorted(repetidos)) + " — cada ID é único e append-only.")
    citados = {}
    for nota in notas:
        # d_history/, e_qa/ e as lições herdadas citam IDs de OUTROS projetos:
        # ficam fora da checagem de existência.
        rel_nota = nota.relative_to(topo)
        if nota == dec or PASTAS_HISTORICAS & set(rel_nota.parts) or nota.stem == "d_agent_learnings":
            continue
        for i in set(re.findall(r"\b((?:D|Q|QA)-\d+)\b", sem_codigo(corpo[nota]))):
            citados.setdefault(i, set()).add(nota.relative_to(topo).as_posix())
    fantasmas = {i: v for i, v in citados.items() if i not in definidos and not re.fullmatch(r"(D|Q|QA)-0*(0|NN)", i)}
    if fantasmas:
        detalhe = "; ".join(f"{i} (em {', '.join(sorted(v))})" for i, v in sorted(fantasmas.items())[:6])
        falhas.append(f"ID citado que não existe em {DECISOES}: {detalhe}")

# 12. "Em andamento" tem de bater entre BACKLOG e CONTEXT (regra 6, fonte única).
if em_andamento and texto_ctx:
    linha_ctx = re.search(r"\*\*Em andamento[^:]*:\*\*\s*(.+)", texto_ctx)
    if linha_ctx and "<" not in linha_ctx.group(1):
        if not any(t in linha_ctx.group(1) for t in em_andamento):
            falhas.append(
                f"'Em andamento' divergente: BACKLOG diz {', '.join(em_andamento)}, "
                f"CONTEXT diz \"{linha_ctx.group(1).strip()[:60]}\" — o estado tem de morar num lugar só."
            )

# --- Avisos ---
sem_fm = [
    p.relative_to(raiz).as_posix()
    for p in notas
    if (p == raiz / p.name or raiz in p.parents) and not corpo[p].startswith("---")
]
if sem_fm:
    avisos.append(f"{len(sem_fm)} nota(s) sem frontmatter: " + ", ".join(sem_fm[:5]))

placeholders = re.findall(r"<[A-Za-zÀ-ú][^<>\n]{2,60}>", texto_ctx)
if placeholders:
    amostra = ", ".join(dict.fromkeys(placeholders[:3]))
    avisos.append(
        f"{CONTEXTO} ainda tem {len(placeholders)} placeholder(s) (ex.: {amostra}). "
        "Rode a Fase 0 (b_process/skills/context-bootstrap) antes de pedir código."
    )
for nome in (PLANO, DECISOES, BACKLOG):
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

alcance = "histórico completo" if COMPLETO else "últimos 30 commits"
print(
    "OK: orçamento, fonte única, WIP, skills, links, gitignore, IDs e sincronia de estado.\n"
    f"    Segredos: árvore versionada + {alcance}."
    + ("" if COMPLETO else " Antes de entregar, rode com --historico-completo.")
)
