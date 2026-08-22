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
                                       13. Tarefa apontando módulo que não existe no PLANO
                                       14. Skill fora do esquema (Contexto/Limites/Saída)
                                       15. BACKLOG inchado (card fechado nunca arquivado)

AVISOS (não reprovam; com --avisos-reprovam, reprovam)
  frontmatter ausente · placeholders · templates em rascunho · nota órfã ·
  arquivo grande não varrido · varredura de histórico que não rodou ·
  portão automático (pre-commit) não instalado · módulo do PLANO sem tarefa ·
  description de skill sem fronteira negativa · CONTEXT perto do teto ·
  DECISIONS perto do teto · BACKLOG perto do teto ·
  tema de a_context/ fora do mapa de leitura ·
  sessão sem skill declarada no changelog · ocupação declarada divergindo do arquivo ·
  questão do dono ausente do CONTEXT ·
  achado vencido (7 dias p/ CRÍTICO e ALTO, 15 p/ MÉDIO, BAIXO não vence) ·
  ID prometido no CHANGELOG e nunca registrado ·
  skill declarada responsável no PLANO que nunca rodou

O README declara quantos itens de checklist existem e quantos esta máquina julga.
Esse número é cobrado por `test_check.py` — a frase mais honesta do kit não pode
ser a que envelhece em silêncio.

Marque uma linha com `checar:ignore` para isentá-la da varredura de segredo
(use só quando o valor for comprovadamente falso — a marca fica visível no diff).
"""
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

# O git emite caminhos em UTF-8. `text=True` SOZINHO decodifica com o encoding do
# SISTEMA — cp1252 num Windows pt-BR — e um caminho com acento ("Área de Trabalho",
# nome real da pasta sob OneDrive KFM em português) derruba a thread leitora com
# UnicodeDecodeError. Pior: UnicodeDecodeError é ValueError, então os `except
# (SubprocessError, OSError)` abaixo passam ao largo; `stdout` volta None e o dono vê
# um AttributeError a duas funções da causa. Resultado medido: o portão nunca rodou
# na máquina do dono, e todo "OK" veio do sandbox Linux do agente.
UTF8 = {"encoding": "utf-8", "errors": "replace"}

# Rede de segurança da SAÍDA (o gêmeo do QA-01). Saída redirecionada num Windows pt-BR
# usa cp1252, não UTF-8: um caractere fora dele — uma seta, um "≤" — mata o script na
# hora de IMPRIMIR, depois de todo o trabalho feito. `errors="replace"` degrada em vez
# de matar, e não muda nada no console, que já é UTF-8.
for _fluxo in (sys.stdout, sys.stderr):
    if hasattr(_fluxo, "reconfigure"):
        _fluxo.reconfigure(errors="replace")

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


def info_git(inicio: Path):
    """Devolve (topo do repositório, pasta de hooks) — e `None` nos hooks quando NÃO há
    repositório git acessível. Uma chamada responde as duas perguntas.

    `(topo / ".git").is_dir()` NÃO serve como teste de "estou num repositório", e essa
    era a falha: em worktree e em submódulo o `.git` é ARQUIVO, então a varredura de
    HISTÓRICO era pulada em silêncio e a saída anunciava "últimos 30 commits" mesmo
    assim. Medido: com segredo plantado no histórico e removido da árvore, repositório
    normal REPROVA (correto) e worktree imprime OK com exit 0. Mesma armadilha quando o
    git não está no PATH. `rev-parse` cobre os quatro casos.

    O padrão põe `.gitignore`, `.gitattributes` e `CLAUDE.md` FORA da pasta de
    documentação, e a varredura de segredo tem de cobrir o código também — por isso o
    topo do repositório, e não só o vault.
    """
    try:
        linhas = subprocess.run(
            ["git", "-C", str(inicio), "rev-parse", "--show-toplevel", "--git-path", "hooks"],
            capture_output=True, text=True, check=True, timeout=15, **UTF8,
        ).stdout.splitlines()
    except (subprocess.SubprocessError, OSError):
        return inicio, None
    if len(linhas) < 2 or not linhas[0].strip():
        return inicio, None
    topo_do_repo = Path(linhas[0].strip()).resolve()
    # `--git-path` vem relativo à pasta passada em `-C` (não ao topo), e vem ABSOLUTO
    # em worktree. Respeita `core.hooksPath` de graça — cravar `.git/hooks` não respeita.
    hooks = Path(linhas[1].strip())
    return topo_do_repo, (hooks if hooks.is_absolute() else (inicio / hooks).resolve())


# DOIS escopos, de propósito:
#   raiz = o vault  -> orçamento, links, órfãs, IDs, WIP, skills
#   topo = o repo   -> .gitignore, cruft, varredura de segredo (árvore + histórico)
raiz = achar_vault(raiz)
topo, DIR_HOOKS = info_git(raiz)
TEM_GIT = DIR_HOOKS is not None

# --- Layout do padrão do repositório (b_process/e_repository_standard.md) ---------
# Um lugar só define onde cada coisa mora. Mudou o padrão? Mude aqui, e só aqui.
# Os caminhos são relativos à raiz da pasta de documentação (o vault).
CONTEXTO = "a_context/a_context_source.md"      # a verdade: estado, ≤4.000 chars
PLANO = "a_context/b_plan.md"                   # plano congelado
DECISOES = "a_context/c_decisions.md"           # D-NN / Q-NN / QA-NN, append-only
BACKLOG = "b_process/c_backlog.md"              # fonte única de tarefas
SKILLS = "b_process/skills"                     # os agentes instaláveis
CHANGELOG = "d_history/a_changelog.md"          # histórico datado; nenhuma sessão carrega
ARQUIVO_MORTO = "e_qa/decisions_archive.md"     # íntegra das linhas retiradas da tabela
# Pastas do vault: só nelas "nota órfã" faz sentido. Markdown do próprio app
# (content/, docs de pacote, README de módulo) não é nota e não bloqueia commit.
PASTAS_VAULT = {"a_context", "b_process", "c_technical_docs", "d_history", "e_qa"}
# Histórico e evidência: citam IDs de OUTROS projetos, ficam fora da checagem de existência.
# `docs/` entra aqui porque é onde mora a auditoria do PRÓPRIO kit (ver e_qa/README.md):
# ela cita D-NN e QA-NN dos projetos-cobaia, que nunca existirão no DECISIONS deste repo.
PASTAS_HISTORICAS = {"d_history", "e_qa", "docs"}
# ----------------------------------------------------------------------------------

# `.pytest_cache` e `.mypy_cache` entram porque um `README.md` gerado por ferramenta dentro
# deles disparava "nota sem frontmatter" — aviso falso, sobre arquivo que não é nota e que o
# dono não escreveu. Aviso falso ensina a ignorar aviso: é a regra do próprio kit, e ela
# estava sendo violada na primeira execução real numa máquina com pytest instalado.
IGNORAR = {".git", ".venv", "venv", "node_modules", ".obsidian", "__pycache__",
           ".pytest_cache", ".mypy_cache", ".ruff_cache", ".next", "dist", "build"}
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
    if TEM_GIT:
        try:
            saida = subprocess.run(
                ["git", "-C", str(topo), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                capture_output=True, text=True, timeout=20, check=True, **UTF8,
            ).stdout
            return [topo / n for n in saida.split("\0") if n]
        except (subprocess.SubprocessError, OSError):
            pass
    return visiveis("*", topo)


def sem_codigo(texto):
    """Sem bloco cercado E sem trecho entre crases. Use quando o exemplo entre crases NÃO
    deve contar — o caso do wikilink de demonstração, que não é link de verdade."""
    texto = re.sub(r"```.*?```", "", texto, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", texto)


def sem_bloco_de_codigo(texto):
    """Só o bloco cercado. É o filtro certo para a checagem de ID (10).

    Medido no primeiro projeto real construído com o kit: 300 de 341 citações de ID
    estavam ENTRE CRASES — a casa escreve `D-13`, não D-13. Como a checagem 10 filtrava
    por `sem_codigo`, ela enxergava 12% das citações e imprimia verde sobre os outros 88%.
    É a mesma classe de defeito que o comentário da checagem 13 já nomeava ("checagem que
    emudece é pior que checagem que não existe"): a lição estava escrita neste arquivo e
    não tinha sido aplicada duas checagens acima.
    """
    return re.sub(r"```.*?```", "", texto, flags=re.S)


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
elif len(texto_ctx) > 3600:
    # Avisar a 90% em vez de só reprovar a 100%: quando o teto estoura, quem escreve
    # está no meio de uma sessão de trabalho e vai cortar o que estiver à mão — não o
    # que devia sair. O aviso dá a chance de mover um tema com calma, antes da parede.
    avisos.append(
        f"{CONTEXTO} com {len(texto_ctx)}/4.000 caracteres ({100*len(texto_ctx)//4000}%) — "
        "mova um tema para a_context/<tema>.md agora, não na sessão em que estourar."
    )

# 2. Registro de decisões inchado (projeto longo)
dec = raiz / DECISOES
texto_dec = corpo.get(dec, "")
if texto_dec and len(texto_dec) > 12000:
    falhas.append(
        f"{DECISOES} acima de 12.000 caracteres — arquive SUPERSEDIDAS/rejeitadas antigas "
        "em e_qa/decisions_archive.md (IDs preservados) e deixe um ponteiro."
    )
elif texto_dec and len(texto_dec) > 9600:
    # O README declarava esta fraqueza com todas as letras: "o arquivamento é manual e
    # ninguém lembra". Portão que só roda quando alguém lembra não é portão — foi o
    # argumento do QA-04, e valia contra o próprio kit. O script não arquiva (a decisão
    # é do dono); ele avisa antes da parede e já aponta os candidatos.
    velhas = re.findall(r"^\|\s*(D-\d+)\s*\|[^|]*\|\s*(?:ADOTADO|REJEITADO)", texto_dec, re.M)
    amostra = ", ".join(velhas[:5]) if velhas else "as mais antigas"
    avisos.append(
        f"{DECISOES} com {len(texto_dec)}/12.000 caracteres ({100*len(texto_dec)//12000}%) — "
        f"arquive as antigas em e_qa/decisions_archive.md, preservando os IDs. Candidatas: {amostra}."
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
        # "máx 3", "max 3", "limite 3", "≤ 3" — a mesma intenção escrita de quatro jeitos.
        # Só `máx` era aceito, e as outras caíam no default 1 em SILÊNCIO: o dono declarava
        # 3, o script cobrava 1 e ainda dizia "limite declarado é 1". Mensagem que afirma
        # ter lido o que não leu é o defeito que este arquivo inteiro persegue.
        m = re.search(r"(?:m[áa]x(?:imo)?|limite|≤|<=)\s*[:=]?\s*(\d+)", bloco.group(1), re.I)
        limite = int(m.group(1)) if m else 1
        em_andamento = re.findall(r"^- \[ \] *(\S+)", bloco.group(2), re.M)
        if len(em_andamento) > limite:
            falhas.append(
                f"{BACKLOG}: {len(em_andamento)} itens 'Em andamento', limite declarado é {limite} "
                "— termine, despromova, ou suba o limite no cabeçalho se o time cresceu."
            )


def cards_do_backlog(texto):
    """Cards como BLOCOS, não como linhas: um card vai do seu marcador até o próximo
    marcador ou até o fim da seção. O card de uma linha é o caso comum, mas o de várias
    aparece assim que o dono escreve o procedimento de conferência dentro dele — e foi
    justamente o card gordo que dominou a medição (6.142 caracteres num só).
    Cópia deliberada em `arquivar.py`, pelo motivo já escrito lá para `sem_bloco_de_codigo`:
    o kit não tem módulo compartilhado, e um import entre scripts avulsos quebraria o
    `check.py` rodando de dentro de um projeto, onde o layout é outro."""
    marcas = [m.start() for m in re.finditer(r"^- \[[ xX]\]", texto, re.M)]
    for ini, fim in zip(marcas, marcas[1:] + [len(texto)]):
        bloco = texto[ini:fim]
        secao = re.search(r"^## ", bloco, re.M)
        yield bloco[:secao.start()] if secao else bloco


# 15. Orçamento do BACKLOG. Era o único dos registros SEM teto — e é o mais caro dos três,
#     porque o CLAUDE.md o põe como leitura de ABERTURA de toda sessão de trabalho,
#     enquanto o DECISIONS só é lido inteiro em sessão de evolução.
#     Medido no primeiro projeto real construído com o kit: 191.591 caracteres, 48x o teto
#     do CONTEXT, dos quais 173.818 (91%) eram os 72 cards JÁ FECHADOS que sessão nenhuma
#     precisa — um deles, sozinho, maior que o CONTEXT inteiro. (O número medido por LINHA
#     dava 143.765; a diferença de 30.053 é o corpo dos cards de várias linhas, e é por
#     isso que `cards_do_backlog` conta bloco. Comentário que cita um número que a função
#     ao lado não mede é a mentira mais fácil de escrever neste arquivo.)
#     O DECISIONS arquiva, o QA
#     arquiva; este nunca soltava nada, e ninguém percebia porque nada o media. O teto de
#     4.000 do CONTEXT era cobrado com rigor de duas casas (3.998/4.000) ao lado deste
#     arquivo crescendo livre: economia medida no lugar errado ainda é economia por medir.
#     O teto é o mesmo do DECISIONS de propósito. Este arquivo é lido ao menos tão
#     frequentemente quanto aquele, e um segundo número arbitrário seria mais um número a
#     defender. Saída pronta antes da parede: `python scripts/arquivar.py --backlog`.
#
#     LACUNA DECLARADA, e ela é do tamanho do teto: arquivar TODOS os 72 cards fechados
#     daquele projeto levou 191.591 -> 25.359, ou seja, ainda o DOBRO do teto. O resto não
#     é card: são 7.586 de ponteiros (105 por card arquivado, e crescem sem fim) e 13.991
#     de prosa de seção — cabeçalho, "Pedidos do dono", "Ideias". O arquivador não toca
#     nisso e não deve tocar: é texto do dono, não item de trabalho.
#     O teto NÃO foi afrouxado para caber. Afrouxar teto quando ele aperta é exatamente o
#     que aconteceu com o DECISIONS naquele projeto — 12.000 -> 16.000 -> 20.000, com o
#     arquivamento esgotado no fim — e repetir isso aqui seria trocar um portão por um
#     aviso. Fica declarado que um projeto naquele porte precisa também podar seção, e que
#     o ponteiro que cresce sem fim é problema em aberto, não problema resolvido.
if texto_bl:
    fechados = [b for b in cards_do_backlog(texto_bl) if re.match(r"^- \[[xX]\]", b)]
    peso = sum(len(b) for b in fechados)
    saida = ("Arquive: `python scripts/arquivar.py --backlog --aplicar` deixa o ID e o "
             "`**Módulo:**` na linha e manda a íntegra para e_qa/backlog_archive.md.")
    if len(texto_bl) > 12000:
        falhas.append(
            f"{BACKLOG} com {len(texto_bl)} caracteres (orçamento: 12.000) — "
            f"{len(fechados)} card(s) fechado(s) ocupam {peso} deles. {saida}"
        )
    elif len(texto_bl) > 9600:
        avisos.append(
            f"{BACKLOG} com {len(texto_bl)}/12.000 caracteres ({100*len(texto_bl)//12000}%) — "
            f"{len(fechados)} card(s) fechado(s) pesam {peso}. Arquive agora, "
            "não na sessão em que estourar. " + saida
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
        # Esquema do corpo. Medido: 24/24 das skills tinham "Contexto" e "Saída" por
        # convenção, e NENHUMA tinha limite explícito — a convenção sobrevivia por hábito,
        # e hábito não sobrevive a uma skill nova escrita com pressa.
        #   Contexto = o que a sessão carrega (o oposto de "leia o repositório")
        #   Limites  = o que o agente não faz mesmo tendo sido escolhido certo
        #   Saída    = o artefato, para o dono saber o que esperar
        texto_skill = corpo.get(skill, skill.read_text(encoding="utf-8"))
        for secao in ("## Contexto que você recebe", "## Limites", "## Saída"):
            if secao not in texto_skill:
                falhas.append(f"{rel}: sem a seção '{secao}' — esquema obrigatório de skill.")
        # A `description` é o único texto que a ferramenta lê para ESCOLHER a skill. Sem a
        # fronteira negativa, duas skills disputam a mesma tarefa e a errada ganha metade
        # das vezes. É aviso, não falha: skill em rascunho pode ainda não saber quem é a vizinha.
        if "Não use" not in cabeca:
            avisos.append(
                f"{rel}: description sem 'Não use para … (é <outra skill>)' — "
                "sem fronteira negativa, a skill errada dispara."
            )

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
# `alcance` sai DAQUI, do que realmente rodou — nunca da flag. A linha final anunciava
# "últimos 30 commits" mesmo quando nenhum commit tinha sido lido: mensagem verde que
# não corresponde ao que rodou é a classe de erro que este bloco existe para fechar.
alcance_hist = None
if TEM_GIT:
    try:
        hist = subprocess.run(
            ["git", "-C", str(topo), "log", "-p", "--no-color", *LIMITE_HIST, "--", "."],
            capture_output=True, text=True, timeout=120 if COMPLETO else 25, **UTF8,
        ).stdout
        adicionadas = [l[1:] for l in hist.splitlines() if l.startswith("+") and not l.startswith("+++")]
        achados_hist = []
        varrer("\n".join(adicionadas), "histórico do git", achados_hist)
        if achados_hist:
            achados_seg.append(f"histórico do git ({len(achados_hist)} linha[s]) — segredo removido da árvore continua comprometido")
        alcance_hist = "histórico completo" if COMPLETO else "últimos 30 commits"
    except subprocess.TimeoutExpired:
        # falha aberta com mensagem verde foi achado da auditoria: agora ela aparece
        avisos.append("Varredura do HISTÓRICO estourou o tempo — o histórico NÃO foi verificado nesta rodada.")
    except (subprocess.SubprocessError, OSError) as erro:
        avisos.append(f"Varredura do HISTÓRICO não rodou ({type(erro).__name__}) — o histórico NÃO foi verificado.")
else:
    avisos.append(
        "Sem repositório git acessível (git fora do PATH, ou pasta ainda sem `git init`) — "
        "a varredura de HISTÓRICO não rodou e a de árvore não respeitou o .gitignore."
    )

# Portão que só roda quando alguém lembra não é portão — é a regra do próprio kit, e
# até aqui ela não valia para a instalação do próprio portão. O caminho vem do git
# (`--git-path hooks`), então worktree e `core.hooksPath` não geram aviso falso.
# Testa se o hook RODA o check.py, não a marca literal: assim a checagem não sai de
# sincronia com o texto de `install_hook.py`.
if DIR_HOOKS is not None:
    gancho = DIR_HOOKS / "pre-commit"
    try:
        armado = gancho.is_file() and "check.py" in gancho.read_text(encoding="utf-8", errors="replace")
    except OSError:
        armado = False
    if not armado:
        avisos.append(
            "Portão automático NÃO instalado — este check só roda quando você lembra, e "
            "commit sem saída nenhuma parece commit aprovado. Instale: python scripts/install_hook.py"
        )
if achados_seg:
    falhas.append("Possível segredo versionado: " + "; ".join(dict.fromkeys(achados_seg))[:400])

# 9. .gitignore cobre o básico de segredo
gi = topo / ".gitignore"
if not gi.exists():
    falhas.append(".gitignore ausente — o kit assume que ele existe antes do primeiro commit.")
else:
    # QA-15: só as linhas EFETIVAS. Um .gitignore que apenas COMENTA os padrões
    # ("# nunca commite .env, *.pem…") satisfazia a checagem por substring sem ignorar
    # nada — regra satisfeita pelo TEXTO, não pelo EFEITO. Mesma espécie do QA-14.
    texto_gi = "\n".join(l for l in gi.read_text(encoding="utf-8").splitlines()
                         if l.strip() and not l.lstrip().startswith("#"))
    faltando = [p for p in (".env", "*.pem", "*.key", "id_rsa", "credentials.json", "*.p12") if p not in texto_gi]
    if faltando:
        falhas.append(".gitignore sem cobertura mínima de segredo — faltam: " + ", ".join(faltando))

# 10 e 11. Integridade dos IDs rastreáveis (regra 4).
if texto_dec:
    definidos = set(re.findall(r"^\|\s*((?:D|Q|QA)-\d+)\s*\|", texto_dec, re.M))
    # QA-16: ID arquivado continua sendo ID REAL — é o que "ID preservado, nada revertido"
    # significa. Sem isto, a correção do QA-14 é inutilizável em qualquer projeto que já
    # tenha arquivado: medido no primeiro projeto real, 22 IDs legitimamente retirados da
    # tabela viravam fantasma e o portão passaria a reprovar TODO commit.
    # Aqui não se procura linha de tabela: no arquivo-morto o ID vem entre crases
    # (`| `D-05` | 2026-08-06 | …`), então qualquer ocorrência dele naquele arquivo vale
    # como definição. E de propósito NÃO entra em `definidos`: a checagem 11 (ID duplicado)
    # tem de continuar olhando só a tabela viva, senão a convenção `ARQUIVADO` — linha que
    # FICA na tabela com a íntegra lá — viraria duplicata falsa.
    morto = raiz / ARQUIVO_MORTO
    arquivados = set(re.findall(r"\b((?:D|Q|QA)-\d+)\b", corpo.get(morto, ""))) if morto.exists() else set()
    repetidos = [i for i in definidos if len(re.findall(rf"^\|\s*{re.escape(i)}\s*\|", texto_dec, re.M)) > 1]
    if repetidos:
        falhas.append(f"ID duplicado em {DECISOES}: " + ", ".join(sorted(repetidos)) + " — cada ID é único e append-only.")
    citados = {}
    citados_log = {}
    for nota in notas:
        # e_qa/, docs/ e as lições herdadas citam IDs de OUTROS projetos: ficam fora da
        # checagem de existência. O CHANGELOG do próprio projeto NÃO é esse caso — ele
        # cita os IDs de casa, e tratá-lo como "histórico de terceiro" abriu um buraco
        # medido: no primeiro projeto real, `D-64` foi prometido numa entrada do changelog,
        # nunca entrou na tabela, e o portão imprimiu verde por 8 dias. Quem pegou foi uma
        # sessão seguinte, no olho — exatamente o trabalho que a checagem 10 existe para
        # tirar do olho.
        # Entra como AVISO e não como falha por uma razão de desenho, não de gosto: o
        # changelog é append-only, então reprovar nele é reprovar num arquivo que a regra
        # proíbe editar. Portão sem saída ensina a usar --no-verify, que é pior que o furo.
        rel_nota = nota.relative_to(topo)
        if nota == dec or nota.stem == "d_agent_learnings":
            continue
        historica = bool(PASTAS_HISTORICAS & set(rel_nota.parts))
        # `raiz / CHANGELOG` e não a string: `rel_nota` é relativo ao TOPO do repositório,
        # e num projeto o vault mora em <TAG>_Project_DOCs/ — comparar com a constante,
        # que é relativa ao vault, nunca casava e o aviso nascia mudo. Pego rodando esta
        # checagem contra o projeto real de onde o defeito veio; num kit, onde topo == raiz,
        # a comparação errada teria passado no teste e ido para produção calada.
        if historica and nota != raiz / CHANGELOG:
            continue
        alvo = citados_log if historica else citados
        for i in set(re.findall(r"\b((?:D|Q|QA)-\d+)\b", sem_bloco_de_codigo(corpo[nota]))):
            alvo.setdefault(i, set()).add(rel_nota.as_posix())

    def fantasmas_de(mapa):
        return {i: v for i, v in mapa.items()
                if i not in definidos and i not in arquivados
                and not re.fullmatch(r"(D|Q|QA)-0*(0|NN)", i)}

    fantasmas = fantasmas_de(citados)
    if fantasmas:
        detalhe = "; ".join(f"{i} (em {', '.join(sorted(v))})" for i, v in sorted(fantasmas.items())[:6])
        falhas.append(f"ID citado que não existe em {DECISOES} nem em {ARQUIVO_MORTO}: {detalhe}")
    # Só o que o changelog cita e mais NINGUÉM vivo cita: o que aparece nos dois lugares já
    # reprovou acima, e repetir seria cobrar duas vezes o mesmo defeito.
    prometidos = {i for i in fantasmas_de(citados_log) if i not in citados}
    if prometidos:
        avisos.append(
            f"ID prometido no {CHANGELOG} e nunca registrado: "
            + ", ".join(sorted(prometidos)[:6])
            + f" — registre a linha no {DECISOES}, ou some uma entrada nova dizendo que o "
              "ID ficou vago de propósito. Nunca recicle o número, e nunca edite a entrada "
              "antiga: o changelog é append-only, a correção é linha NOVA."
        )

# 12. "Em andamento" tem de bater entre BACKLOG e CONTEXT (regra 6, fonte única).
# 13. Cobertura módulo <-> tarefa. Metade FORMAL do que a skill artifact-consistency faz
#     no olho: módulo do PLANO que não aparece em nenhuma tarefa do BACKLOG simplesmente
#     não é construído, e ninguém percebe até faltar. A ideia vem do BMAD, que marca toda
#     tarefa com o critério que ela atende — traçabilidade no artefato, não na revisão.
#     Só funciona porque os IDs existem: sem `M1` no plano e `**Módulo:** M1` na tarefa,
#     isto seria julgamento semântico, e script não julga semântica.
texto_plano = corpo.get(raiz / PLANO, "")
if texto_plano and texto_bl:
    # Tolerante ao separador e à posição dos dois-pontos de propósito: `### M1 — nome`,
    # `### M1: nome` e `**Módulo:** M1` / `**Módulo**: M1` são a mesma intenção, e um
    # regex estrito faria a checagem parar de checar em SILÊNCIO na primeira edição
    # cosmética do template. Checagem que emudece é pior que checagem que não existe,
    # porque o verde continua saindo. (Medido: as duas variações abaixo zeravam os
    # achados antes desta correção.)
    modulos = {m.group(1): m.group(2).strip()
               for m in re.finditer(r"^#{2,4}\s+(M\d+)\s*[—–:.-]\s*(.+)$", texto_plano, re.M)}
    citados = set(re.findall(r"\*\*M[óo]dulo:?\*\*:?\s*(M\d+)\b", texto_bl))
    fantasmas = citados - set(modulos)
    if fantasmas:
        falhas.append(
            f"{BACKLOG} aponta módulo inexistente em {PLANO}: " + ", ".join(sorted(fantasmas))
            + " — tarefa apontando para o vazio é escopo sem dono."
        )
    # Módulo ainda com nome de template (`<nome>`) é plano não preenchido, não lacuna.
    sem_tarefa = sorted(i for i, nome in modulos.items()
                        if not nome.lstrip().startswith("<") and i not in citados)
    if sem_tarefa:
        avisos.append(
            "Módulo do PLANO sem tarefa no BACKLOG: " + ", ".join(sem_tarefa)
            + " — ou vira tarefa, ou é declarado fora do escopo no CONTEXT. "
            "(Aviso, não falha: entre congelar o plano e povoar o backlog existe um intervalo legítimo.)"
        )

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

# Tema de domínio que não entrou no mapa de leitura do CONTEXT. A regra é do próprio
# kit — "doc fora do mapa nunca é lido" — e nada a cobrava: o arquivo existia, custava
# manutenção e ninguém o abria. Aqui a máquina JULGA; escrever o mapa continua sendo do
# dono, porque o CONTEXT é a verdade dele e script não escreve na verdade de ninguém.
NUCLEO_CONTEXTO = {"a_context_source", "b_plan", "c_decisions", "README"}
if texto_ctx:
    fora = sorted(p.stem for p in (raiz / "a_context").glob("*.md")
                  if p.stem not in NUCLEO_CONTEXTO and p.stem not in texto_ctx)
    if fora:
        avisos.append(
            "Tema em a_context/ fora do Mapa de leitura do CONTEXT: " + ", ".join(fora)
            + " — doc fora do mapa nunca é lido; ou entra no mapa com a condição que "
            "justifica lê-lo, ou sai do repositório."
        )

# Instrumentação da sessão: QUAL skill rodou.
# Sem este campo, "qual dos agentes paga o próprio custo" só se responde por arqueologia
# de git — foi exatamente onde a primeira avaliação de campo do kit parou, e a conclusão
# ficou em [suposto] por falta de um dado que custa uma linha para existir.
# O changelog é o lugar certo justamente porque NENHUMA sessão o carrega: o dado custa
# zero contexto e fica onde a sessão já escreve de qualquer jeito.
# Aviso, não falha: projeto que já existia não vai reescrever o histórico para adotar isto.
texto_cl = corpo.get(raiz / CHANGELOG, "")
if texto_cl:
    entradas = re.findall(r"^## \[(\d{4}-\d{2}-\d{2})\][^\n]*\n(.*?)(?=^## |\Z)",
                          texto_cl, re.S | re.M)[:3]
    catalogo = {q.parent.name for q in (raiz / SKILLS).glob("*/SKILL.md")}
    problemas = []
    for data_e, bloco_e in entradas:
        m = re.search(r"\*\*Skill:\*\*\s*`?([a-z0-9][a-z0-9-]*)`?", bloco_e)
        if not m:
            problemas.append(f"{data_e} (sem '**Skill:**')")
        elif catalogo and m.group(1) not in catalogo and m.group(1) != "nenhuma":
            problemas.append(f"{data_e} (skill '{m.group(1)}' não existe em {SKILLS}/)")
    if problemas:
        avisos.append(
            "Sessão sem skill declarada no changelog: " + " · ".join(problemas)
            + " — sem este campo ninguém sabe qual agente rodou, e medir o kit vira "
            "arqueologia. Formato: uma linha `- **Skill:** <nome>` na entrada."
        )

# Skill que o PLANO declarou responsável por um módulo e que nunca rodou. Medido no
# primeiro projeto real: de 24 skills, só 10 dispararam — e QUATRO das que nunca rodaram
# tinham o assunto acontecendo no projeto. A mais gritante: existe uma checagem neste
# arquivo que se declara "a checagem que a skill guardrails-review exige"; a checagem
# rodava, a skill nunca. O problema não era falta de skill, era falta de ROTEAMENTO.
# Isto é mecânico de propósito — lê `**Skill responsável:**` do PLANO contra `**Skill:**`
# do changelog. Adivinhar por assunto seria julgar semântica, e script não julga semântica.
texto_plano_sk = corpo.get(raiz / PLANO, "")
texto_log_sk = corpo.get(raiz / CHANGELOG, "")
if texto_plano_sk and texto_log_sk:
    rodaram = {s.lower() for s in re.findall(r"\*\*Skill:\*\*\s*`?([a-z0-9][a-z0-9-]*)", texto_log_sk)}
    orfas = {}
    for mod, skill in re.findall(
            r"^#{2,4}\s+(M\d+)\s*[—–:.-].*?\*\*Skill respons[áa]vel:?\*\*:?\s*(.+?)$",
            texto_plano_sk, re.S | re.M):
        # A declaração costuma vir como wikilink: `[[b_process/skills/testing/SKILL|testes]]`.
        # O nome que vale é o da PASTA, que é o mesmo que o changelog escreve.
        m = re.search(r"skills/([a-z0-9][a-z0-9-]*)/", skill) or re.search(r"`([a-z0-9-]+)`", skill)
        if not m or skill.lstrip().startswith("<") or "…" in skill:
            continue
        if m.group(1).lower() not in rodaram:
            orfas.setdefault(m.group(1), []).append(mod)
    if orfas:
        avisos.append(
            "Skill declarada responsável no PLANO e que nunca rodou: "
            + " · ".join(f"`{s}` ({', '.join(ms)})" for s, ms in sorted(orfas.items()))
            + " — ou ela roda numa sessão, ou o PLANO passa a declarar quem realmente faz "
            "o trabalho. Skill que ninguém alcança é peso morto vestido de cobertura."
        )

# Número que um script calcula não se mantém à mão. O kit já aprendeu isto uma vez — a
# frase de cobertura do README dizia 188/18 quando o real era 277/23 — e a correção valeu
# só para AQUELE número. Aqui a lição vira classe: ocupação declarada no CONTEXT sobre um
# arquivo que este script mede é conferida contra o arquivo.
ORCAMENTOS = {4000: (CONTEXTO, texto_ctx), 12000: (DECISOES, texto_dec)}
if texto_ctx:
    divergentes = []
    for bruto_n, bruto_teto in re.findall(r"(\d[\d.]*)\s*/\s*(\d[\d.]*)", texto_ctx):
        try:
            declarado, teto = int(bruto_n.replace(".", "")), int(bruto_teto.replace(".", ""))
        except ValueError:
            continue
        if teto not in ORCAMENTOS:
            continue
        nome, texto_alvo = ORCAMENTOS[teto]
        if texto_alvo and declarado != len(texto_alvo):
            divergentes.append(f"diz {nome} em {declarado}/{teto}, o arquivo tem {len(texto_alvo)}")
    if divergentes:
        avisos.append(
            f"{CONTEXTO} " + " · ".join(divergentes)
            + " — número que o script calcula não se mantém à mão; atualize ao reescrever o Estado atual."
        )

# A fila do dono só existe se ele a VÊ. O CONTEXT é o único arquivo que toda sessão carrega:
# questão aberta que não aparece lá fica esperando alguém abrir o DECISIONS por conta própria.
# Medido no primeiro projeto real: três Q-NN abertas, duas com prazo estourado, e o achado
# que registrou o estouro foi feito à mão numa sessão que por acaso olhou.
if texto_dec and texto_ctx:
    abertas = [m.group(1) for m in re.finditer(r"^\|\s*(Q-\d+)\s*\|(.*)$", texto_dec, re.M)
               if "RESPONDIDA" not in m.group(2).upper() and "~~" not in m.group(2)
               and "<" not in m.group(2)]
    linha_q = re.search(r"\*\*Quest(?:ões|oes) abertas[^:]*:\*\*\s*(.+)", texto_ctx)
    if abertas and linha_q and "<" not in linha_q.group(1):
        ausentes = [q for q in abertas if q not in linha_q.group(1)]
        if ausentes:
            avisos.append(
                "Questão do dono aberta no " + DECISOES + " e ausente do CONTEXT: "
                + ", ".join(ausentes) + " — o CONTEXT é o único arquivo que toda sessão lê; "
                "fora dele a pergunta não é feita a ninguém."
            )

# Achado que envelhece aberto. O registro é append-only na CRIAÇÃO e não tinha disciplina de
# EXPIRAÇÃO: no projeto medido, o único QA crítico aberto descrevia uma condição já resolvida.
# Só julga se a tabela tiver a coluna — e, quando não tiver, DIZ que não julgou, em vez de
# emudecer (a doença do QA-14).
def prazo_de(sev):
    """Prazo POR GRAVIDADE, e não um prazo só. Antes era 14 dias para CRÍTICO/ALTO e nada
    para o resto — e a medição do primeiro projeto real mostrou que isso cobrava justamente
    o nível que não enrosca: os 8 CRÍTICOS e os 4 ALTOS estavam TODOS fechados, e o que
    apodrecia eram 5 MÉDIOS parados 13-15 dias, sem prazo nenhum.
    Os números vêm do porte a que o kit se propõe — projeto curto ou médio, de 2 a 8
    semanas. Nessa escala, 14 dias para um CRÍTICO é um quarto do projeto.
    BAIXO não vence, e isso é decisão, não esquecimento: metade dos achados abertos daquele
    projeto era BAIXO, e um aviso que passa a cobrar o que ninguém vai fazer vira ruído —
    o gêmeo da doença que este arquivo já persegue, porque aviso que vira ruído deixa de
    ser lido, e checagem que ninguém lê emudeceu do mesmo jeito."""
    s = sev.upper()
    if "CRÍT" in s or "CRIT" in s or "ALTO" in s:
        return 7
    if "MÉD" in s or "MED" in s:
        return 15
    return None


# O registro de QA pode ter saído do DECISIONS para arquivo próprio — o primeiro projeto
# real fez isso, e uma checagem que só olha a casa antiga não é rigorosa, é cega. Procure,
# não presuma: relatar zero achado vencido num registro que nem foi lido é a leitura mais
# elogiosa possível, e a mais falsa.
fontes_qa = [t for t in [texto_dec] + [corpo[p] for p in notas
                                       if p.parent == raiz / "a_context"
                                       and re.search(r"qa", p.stem, re.I)] if t]
com_coluna = [t for t in fontes_qa if re.search(r"^\|\s*#\s*\|.*Fechado", t, re.M | re.I)]
if com_coluna:
    velhos = []
    for texto_fonte in com_coluna:
        for linha in texto_fonte.splitlines():
            if not re.match(r"^\|\s*`?QA-\d+`?\s*\|", linha):
                continue
            celulas = [c.strip().strip("`") for c in linha.strip().strip("|").split("|")]
            if len(celulas) < 5:
                continue
            ident, quando_txt, sev, fechado = celulas[0], celulas[1], celulas[2], celulas[-1]
            if fechado and "ABERTO" not in fechado.upper():
                continue
            prazo = prazo_de(sev)
            if prazo is None:
                continue
            try:
                idade = (date.today() - date.fromisoformat(quando_txt[:10])).days
            except ValueError:
                continue
            if idade > prazo:
                velhos.append(f"{ident} ({sev}, {idade} dias, prazo {prazo})")
    if velhos:
        avisos.append(
            "Achado vencido: " + ", ".join(velhos)
            + " — o prazo é 7 dias para CRÍTICO/ALTO e 15 para MÉDIO (BAIXO não vence). "
            "Ou fecha com data, ou vira card no BACKLOG, ou o dono rebaixa a gravidade. "
            "Registro append-only precisa de disciplina de expiração, senão a linha "
            "descreve um mundo que já acabou."
        )
elif fontes_qa:
    avisos.append(
        "Tabela de QA sem a coluna 'Fechado em' — a checagem de achado vencido NÃO rodou. "
        "Dito em voz alta de propósito: checagem que emudece é pior que checagem que não existe."
    )

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

alcance = alcance_hist or "SEM histórico (não foi verificado — veja o aviso acima)"
print(
    "OK: orçamento, fonte única, WIP, skills, links, gitignore, IDs e sincronia de estado.\n"
    f"    Segredos: árvore versionada + {alcance}."
    + ("" if COMPLETO and alcance_hist else " Antes de entregar, rode com --historico-completo.")
)
