#!/usr/bin/env python3
"""Evidência mecânica sobre o uso do kit neste projeto.

Uso: python scripts/evidencia.py [pasta] [--json] [--marco]

**Por que este script existe.** O caso de referência do kit declara os próprios números
como "relato, não medição", e numa avaliação recente o kit tirou 88 em economia de
contexto, 84 em honestidade e **35 em evidência de que funciona**. O 35 não era falta de
qualidade: era falta de MEDIDA. A primeira auditoria de campo saiu, mas custou uma sessão
inteira de scripts descartáveis — e o que custa uma sessão só acontece uma vez.

Tudo aqui sai de `git` e dos arquivos. Nenhuma pergunta a ninguém, nenhum julgamento de
semântica, nenhum número vindo do que um documento diz sobre si mesmo — e isso é regra,
não estilo: o kit já declarou "188 itens, 18 julgados" quando eram 284 e 26, e declarou
"Passagens de revisão: 1" num registro com achados espalhados por 7 datas.

**Este script não escreve nada, exceto com `--marco`.** Relata. E fecha dizendo, com todas
as letras, o que ele NÃO consegue medir — porque relatório que não declara o próprio limite
é exatamente o material com que se fabrica um 88 medido no lugar errado.

`--marco` é a única exceção, e ela nasceu de uma medição embaraçosa: a última linha deste
relatório pedia, por escrito, "guarde a saída de --json", e a taxa de cumprimento no único
projeto real medido foi **zero em oito dias**. Um critério de conclusão congelado exigia a
SÉRIE ("H7 depende de ver a tendência, não o número final") e não existia um único ponto
intermediário — nem para provar a queda que salvaria, nem para provar a subida que condena.
É a lição do próprio kit apontada para ele mesmo: *regra que a máquina não cobra é pedido,
não regra.* Então o pedido virou comando: `--marco` grava `e_qa/evidencia_AAMMDD.json` e
imprime o delta contra o marco anterior.
"""
import json
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

for _f in (sys.stdout, sys.stderr):
    if hasattr(_f, "reconfigure"):
        # Mesma razão do QA-01: num Windows pt-BR a saída redirecionada usa cp1252, e um
        # `·` derruba o script no meio do relatório.
        _f.reconfigure(errors="replace")

CONTEXTO = "a_context/a_context_source.md"
DECISOES = "a_context/c_decisions.md"
BACKLOG = "b_process/c_backlog.md"
CHANGELOG = "d_history/a_changelog.md"
ARQUIVO_MORTO = "e_qa/decisions_archive.md"
SKILLS = "b_process/skills"
# Tetos cobrados pelo check.py. O projeto declara os dele em `.kit-config.json`, e o
# relatório imprime OS DOIS números quando eles diferem: a ocupação contra o teto que
# vale ali, e o padrão do kit ao lado. A distância entre eles é informação — mostra
# quanto o teto foi afrouxado — e escondê-la seria medir com a régua que o medido escolheu.
TETOS_PADRAO = {CONTEXTO: 4000, DECISOES: 12000, BACKLOG: 12000}
CONFIG = ".kit-config.json"
JSON = "--json" in sys.argv
MARCO = "--marco" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
# As quatro origens de um achado. `portão` é a que interessa medir: é a única afirmação
# deste kit sobre o MUNDO ("o portão pegou N defeitos que ninguém tinha visto") e não sobre
# o próprio processo ("o registro está completo"). Sem ela, todo número aqui é o kit se
# elogiando por ter seguido a própria regra.
ORIGENS = {"PORTÃO": "portão", "PORTAO": "portão", "REVISÃO": "revisão", "REVISAO": "revisão",
           "DONO": "dono", "USUÁRIO": "usuário", "USUARIO": "usuário"}


def achar_vault(p: Path) -> Path:
    if (p / "a_context").is_dir():
        return p
    # Padrão da equipe: `e_doc/0_Context/`. A busca por `*_Project_DOCs` fica para os
    # projetos criados antes do v13.14 — ver achar_vault() do check.py.
    if (p / "e_doc" / "0_Context" / "a_context").is_dir():
        return p / "e_doc" / "0_Context"
    cand = sorted(q for q in p.glob("*_Project_DOCs") if (q / "a_context").is_dir())
    return cand[0] if len(cand) == 1 else p


def sem_bloco_de_codigo(texto: str) -> str:
    return re.sub(r"```.*?```", "", texto, flags=re.S)


def git(repo: Path, *a):
    """encoding fixo: o git emite UTF-8 e `text=True` sozinho decodifica com o encoding do
    SISTEMA. É o QA-01, e ele já derrubou três scripts deste kit."""
    try:
        r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
        return r.stdout if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def ler(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def linhas_de_tabela(texto: str, prefixo: str):
    """Linhas `| D-07 | data | STATUS | ...`, com ou sem crases. O arquivo-morto escreve
    o ID entre crases; a tabela viva, não. Ler só um dos formatos foi o QA-14."""
    for ln in texto.splitlines():
        if not ln.lstrip().startswith("|"):
            continue
        col = [c.strip().strip("`") for c in ln.strip().strip("|").split("|")]
        if col and re.fullmatch(rf"{prefixo}-\d+", col[0]):
            yield col, ln


# ---------------------------------------------------------------- coleta
raiz = achar_vault(Path(args[0] if args else ".").resolve())
if not (raiz / "a_context").is_dir():
    print(f"FALHOU:\n - não achei um vault do kit em {raiz} (esperava a_context/).")
    sys.exit(1)

topo = raiz
while topo.parent != topo and not (topo / ".git").exists():
    topo = topo.parent
tem_git = (topo / ".git").exists() and git(topo, "rev-parse", "HEAD") is not None
prefixo = "" if topo == raiz else raiz.relative_to(topo).as_posix() + "/"

texto = {a: ler(raiz / a) for a in (CONTEXTO, DECISOES, BACKLOG, CHANGELOG, ARQUIVO_MORTO)}
# O QA pode ter saído do DECISIONS para arquivo próprio (o primeiro projeto real fez isso).
# Procurar em vez de assumir: registro que mudou de casa não pode virar zero no relatório.
extras = [p for p in (raiz / "a_context").glob("*.md") if re.search(r"qa", p.stem, re.I)]
universo = "\n".join(list(texto.values()) + [ler(p) for p in extras])

R = {"projeto": raiz.name, "medido_em": date.today().isoformat()}

# --- orçamentos
TETOS = dict(TETOS_PADRAO)
cfg = raiz / CONFIG
if cfg.exists():
    try:
        declarados = (json.loads(cfg.read_text(encoding="utf-8")) or {}).get("tetos") or {}
    except (ValueError, OSError):
        declarados = {}
    TETOS.update({a: v for a, v in declarados.items() if isinstance(v, int) and v > 0})

R["orcamentos"] = {}
for arq, teto in TETOS.items():
    corpo_arq = texto.get(arq) or ler(raiz / arq)
    if corpo_arq:
        R["orcamentos"][arq] = {"chars": len(corpo_arq), "teto": teto,
                                "padrao": TETOS_PADRAO.get(arq),
                                "pct": round(100 * len(corpo_arq) / teto, 1)}

# --- D-NN
dec = {}
for col, _ in list(linhas_de_tabela(texto[DECISOES], "D")) + list(linhas_de_tabela(texto[ARQUIVO_MORTO], "D")):
    dec.setdefault(col[0], col)
rejeitadas = [i for i, c in dec.items() if len(c) > 2 and "REJEIT" in c[2].upper()]
nums = sorted(int(i[2:]) for i in dec)
R["decisoes"] = {
    "total": len(dec),
    "rejeitadas": len(rejeitadas),
    "pct_rejeitadas": round(100 * len(rejeitadas) / len(dec), 1) if dec else 0.0,
    "lista_morta": sorted(rejeitadas, key=lambda x: int(x[2:])),
    "ids_vagos": [f"D-{n:02d}" for n in range(min(nums), max(nums) + 1) if n not in nums] if nums else [],
}

# --- Q-NN
q = {}
for col, ln in list(linhas_de_tabela(texto[DECISOES], "Q")) + list(linhas_de_tabela(texto[ARQUIVO_MORTO], "Q")):
    q.setdefault(col[0], (col, ln))
# "RESPONDIDA", "fechada por", ou o título riscado com ~~: as três formas que a casa usa.
respondidas = [i for i, (col, ln) in q.items()
               if re.search(r"RESPONDIDA|fechada por|~~", ln, re.I)]
abertas = sorted(set(q) - set(respondidas), key=lambda x: int(x[2:]))

# Questão do dono cujo MARCO já passou.
#
# A primeira avaliação de campo registrou "2 questões com prazo estourado que o próprio kit
# registrou e não cobrou". A tentação é contar dias — e ela está errada: as duas linhas reais
# diziam "antes de T-10" e "antes de E-3". O que venceu não foi uma data, foi um MARCO: a
# tarefa fechou e a pergunta ficou aberta. Um contador de calendário não pega nenhuma das
# duas (o projeto inteiro durou 4 dias, menos que qualquer prazo razoável), e ainda cobraria
# toda questão nova de um projeto curto.
#
# Isto mora AQUI, e não no check.py, de propósito: a fila é do DONO, e só ele a fecha. Aviso
# no portão do agente seria cobrança sem saída — a espécie que o kit chama de ruído, e ruído
# deixa de ser lido. Este relatório é o único lugar em que quem pode agir está lendo.
fechados_no_backlog = set(re.findall(r"^\s*-\s*\[x\]\s*`?([A-Za-z]{1,2}-\d+)`?",
                                     texto[BACKLOG], re.M | re.I))
fechados_no_backlog = {i.upper() for i in fechados_no_backlog}
vencidas = []
for ident in abertas:
    col = q[ident][0]
    # Procura o marco em qualquer célula depois do ID, e ignora outros Q-NN: o marco é uma
    # tarefa ou etapa, nunca outra pergunta.
    marcos = {m.upper() for c in col[1:] for m in re.findall(r"\b([A-Za-z]{1,2}-\d+)\b", c)}
    passados = sorted(m for m in marcos if not m.startswith("Q-") and m in fechados_no_backlog)
    if passados:
        vencidas.append((ident, ", ".join(passados)))
R["questoes"] = {"total": len(q), "respondidas": len(respondidas), "abertas": abertas,
                 "vencidas_por_marco": vencidas}

# --- QA-NN
qa = {}
tem_coluna_origem = False
for fonte in [texto[DECISOES], texto[ARQUIVO_MORTO]] + [ler(p) for p in extras]:
    # "Coluna ausente" e "coluna vazia" são diagnósticos DIFERENTES e pedem ações
    # diferentes — dizer um pelo outro é o relatório mentindo com número certo.
    if re.search(r"^\|\s*#\s*\|.*\bOrigem\b", fonte, re.M | re.I):
        tem_coluna_origem = True
    for col, ln in linhas_de_tabela(fonte, "QA"):
        qa.setdefault(col[0], (col, ln))
sev, datas, abertos, origem = Counter(), Counter(), [], Counter()
for i, (col, ln) in qa.items():
    d = next((c for c in col if re.fullmatch(r"20\d\d-\d\d-\d\d", c)), None)
    s = next((c.upper() for c in col if c.upper() in
              ("CRÍTICO", "CRITICO", "ALTO", "MÉDIO", "MEDIO", "BAIXO")), "?")
    sev[s] += 1
    # Procura a origem em QUALQUER célula, e não numa posição fixa: projeto que põe a
    # coluna em outro lugar continua sendo lido. Sem a coluna, a chave é "não declarada" —
    # que é diferente de zero, e o relatório diz isso em voz alta lá embaixo.
    origem[next((ORIGENS[c.strip().upper()] for c in col
                 if c.strip().upper() in ORIGENS), "não declarada")] += 1
    if d:
        datas[d] += 1
    if "aberto" in col[-1].lower():
        abertos.append((i, s, d))
R["achados"] = {
    "total": len(qa), "por_severidade": dict(sev), "por_origem": dict(origem),
    "tem_coluna_origem": tem_coluna_origem,
    # "Passagens de revisão" era campo escrito à mão, e envelheceu: um projeto declarava 1
    # com achados em 7 datas. Datas distintas é a mesma pergunta, medida.
    "passagens_medidas": len(datas), "datas": sorted(datas),
    "abertos": len(abertos), "fechados": len(qa) - len(abertos),
    "abertos_detalhe": sorted(abertos, key=lambda x: x[2] or ""),
}

# --- skills
disp = sorted(d.name for d in (raiz / SKILLS).iterdir() if d.is_dir()) if (raiz / SKILLS).is_dir() else []
censo = Counter()
fontes_skill = [texto[CHANGELOG]] + [ler(p) for p in (raiz / "e_qa").glob("*.md")] \
    if (raiz / "e_qa").is_dir() else [texto[CHANGELOG]]
for bruto in fontes_skill:
    for linha in re.findall(r"\*\*Skill:\*\*\s*(.*)", bruto):
        casa = [s for s in disp if s in linha]
        if casa:
            censo[max(casa, key=len)] += 1
R["skills"] = {
    "disponiveis": len(disp), "dispararam": len(censo),
    "uso": censo.most_common(),
    "nunca_dispararam": [s for s in disp if not censo[s]],
}

# --- git
R["git"] = {"disponivel": tem_git}
if tem_git:
    bruto = git(topo, "log", "--pretty=format:@@%H|%ad|%s", "--date=short", "--name-only") or ""
    commits, atual = [], None
    for ln in bruto.splitlines():
        if ln.startswith("@@"):
            if atual:
                commits.append(atual)
            h, d, s = ln[2:].split("|", 2)
            atual = {"h": h[:7], "d": d, "s": s, "f": []}
        elif ln.strip() and atual is not None:
            atual["f"].append(ln.strip())
    if atual:
        commits.append(atual)

    cita = sum(1 for c in commits if re.search(r"\b(D|QA|Q)-\d+", c["s"]))
    # Pulos DECLARADOS do portão (ver scripts/portao_hook.py). Este número mede o que a
    # trava consegue ver: o pulo que passou pelo agente com o marcador. Pulo feito fora do
    # agente, ou antes de a trava existir, continua invisível — e por isso o relatório
    # imprime "pelo menos", nunca um total.
    pulos = [c for c in commits if "SEM-PORTAO" in c["s"].upper()]
    tipos = Counter()
    modulos = Counter()
    for c in commits:
        proc = [f for f in c["f"] if prefixo and f.startswith(prefixo)]
        outro = [f for f in c["f"] if not (prefixo and f.startswith(prefixo))]
        tipos["so_processo" if proc and not outro else
              "so_produto" if outro and not proc else
              "misto" if proc and outro else "vazio"] += 1
        # Escopo: quantas "áreas" do produto um commit toca. Área = 1º nível abaixo da
        # pasta de código, que é o mais perto de "módulo" que dá para saber sem julgar.
        areas = {f.split("/")[1] for f in outro if f.count("/") >= 2 and "test" not in f}
        if areas:
            modulos[len(areas)] += 1
    R["git"].update({
        "commits": len(commits),
        "citam_id": cita,
        "pulos_declarados": len(pulos),
        "pulos_detalhe": [f"{c['h']} {c['d']} {c['s'][:80]}" for c in pulos[:5]],
        "pct_citam_id": round(100 * cita / len(commits), 1) if commits else 0.0,
        "mistura": dict(tipos),
        # `None`, e não `0.0`, quando o vault É a raiz do repositório: ali não existe
        # "produto" do qual separar o processo, e um zero seria a leitura mais elogiosa
        # possível de algo que nem foi medido. O relatório já dizia isso em texto; o JSON
        # dizia 0.0 — e é o JSON que a série de marcos compara, então a mentira viajava.
        "pct_so_processo": (round(100 * tipos["so_processo"] / len(commits), 1)
                            if commits and prefixo else None),
        "escopo": dict(sorted(modulos.items())),
        "dias_com_commit": len({c["d"] for c in commits}),
    })

    # delta x regeneração: quantas linhas um commit mexe nos registros, e quantas vezes
    # alguém apagou o arquivo quase inteiro (o oposto de "delta, nunca regeneração").
    R["git"]["delta"] = {}
    num = git(topo, "log", "--pretty=format:@@%h", "--numstat") or ""
    porarq = defaultdict(list)
    for ln in num.splitlines():
        p = ln.split("\t")
        if len(p) == 3 and p[0] != "-":
            porarq[p[2]].append((int(p[0]), int(p[1])))
    for arq in (CONTEXTO, DECISOES, BACKLOG):
        ev = porarq.get(prefixo + arq, [])
        if not ev:
            continue
        vivo = len(texto[arq].splitlines()) or 1
        R["git"]["delta"][arq] = {
            "commits_que_tocam": len(ev),
            "mediana_linhas": int(statistics.median(a + d for a, d in ev)),
            "reescritas_integrais": sum(1 for _, d in ev if d >= 0.7 * vivo),
        }

if JSON:
    print(json.dumps(R, ensure_ascii=False, indent=2))
    sys.exit(0)


# ---------------------------------------------------------------- relatório
def titulo(t):
    print(f"\n{t}\n" + "-" * len(t))


def _pontos(r: dict) -> dict:
    """Os números que fazem sentido comparar entre dois marcos. Deliberadamente poucos:
    série de tudo é ruído, e o que se quer ver é a TENDÊNCIA de meia dúzia de coisas."""
    return {
        "commits só-processo (%)": (r.get("git") or {}).get("pct_so_processo"),
        "achados": (r.get("achados") or {}).get("total"),
        "achados de origem portão": ((r.get("achados") or {}).get("por_origem") or {}).get("portão"),
        "decisões rejeitadas": (r.get("decisoes") or {}).get("rejeitadas"),
        "skills com rastro": (r.get("skills") or {}).get("dispararam"),
        "questões respondidas": (r.get("questoes") or {}).get("respondidas"),
    }


if MARCO:
    pasta = raiz / "e_qa"
    pasta.mkdir(exist_ok=True)
    destino = pasta / f"evidencia_{date.today().strftime('%y%m%d')}.json"
    anteriores = sorted(p for p in pasta.glob("evidencia_*.json") if p != destino)
    destino.write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"MARCO GRAVADO: {destino.relative_to(raiz)}")
    if not anteriores:
        print("  Primeiro marco deste projeto. Ele sozinho não é série — é o ponto zero.")
        print("  Rode de novo ao fechar o próximo milestone, e aí haverá tendência.")
    else:
        velho_p = anteriores[-1]
        try:
            velho = json.loads(velho_p.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            velho = {}
        print(f"  Comparando com {velho_p.name} (medido em {velho.get('medido_em', '?')}):")
        antes, agora = _pontos(velho), _pontos(R)
        for chave, novo in agora.items():
            ant = antes.get(chave)
            if novo is None and ant is None:
                continue
            if ant is None:
                print(f"    {chave:<26} {novo}  (não havia medida antes)")
                continue
            if novo is None:
                print(f"    {chave:<26} — deixou de ser medido (era {ant})")
                continue
            d = round(novo - ant, 1)
            seta = "=" if d == 0 else ("+" if d > 0 else "")
            print(f"    {chave:<26} {ant} -> {novo}   ({seta}{d if d else ''})")
        print("  Um delta NÃO diz se melhorou: 'mais achados' pode ser mais revisão ou mais")
        print("  defeito, e 'menos commits de processo' pode ser disciplina ou abandono.")
        print("  Quem julga o sinal é você; o script só garante que a série exista.")
    print()


print(f"EVIDÊNCIA MECÂNICA — {R['projeto']} — medido em {R['medido_em']}")
print("Tudo abaixo saiu do git e dos arquivos. Nada saiu do que um documento diz de si.")

titulo("Orçamentos")
afrouxados = []
for arq, o in R["orcamentos"].items():
    aviso = "  <== ESTOURADO" if o["pct"] > 100 else ("  <== perto do teto" if o["pct"] >= 80 else "")
    print(f"  {arq:<32} {o['chars']:>7} / {o['teto']:<6} {o['pct']:>5}%{aviso}")
    if o.get("padrao") and o["teto"] > o["padrao"]:
        afrouxados.append(f"{arq} ({o['padrao']} -> {o['teto']})")
    elif o.get("padrao") is None:
        afrouxados.append(f"{arq} (registro que o kit não prevê)")
if not R["orcamentos"]:
    print("  nenhum registro encontrado.")
else:
    print("  (teto = o que vale NESTE projeto: o padrão do kit, ou o que ele declarou em")
    print("   .kit-config.json. O portão cobra a elevação com um D-NN — teto que sobe em")
    print("   silêncio não é teto, é lembrete.)")
    if afrouxados:
        print("  tetos afrouxados em relação ao padrão do kit:")
        for linha in afrouxados:
            print(f"    {linha}")
        print("   A distância entre o teto do projeto e o do kit é informação, não erro:")
        print("   ela mostra quanto o desenho original não coube.")

d = R["decisoes"]
titulo("Decisões (D-NN) — a lista-morta é a tese central do kit")
print(f"  registradas: {d['total']}")
print(f"  REJEITADAS:  {d['rejeitadas']} ({d['pct_rejeitadas']}%)")
if d["rejeitadas"]:
    print(f"    {' '.join(d['lista_morta'][:14])}")
else:
    print("    NENHUMA. Um registro 100% 'adotado' é diário do que aconteceu — qualquer")
    print("    agente escreve isso. É a rejeição que prova que houve escolha.")
if d["ids_vagos"]:
    print(f"  IDs sem linha em lugar nenhum: {', '.join(d['ids_vagos'])}")

qq = R["questoes"]
titulo("Questões do dono (Q-NN) — o agente parou em vez de decidir sozinho")
print(f"  abertas ao todo: {qq['total']}   respondidas: {qq['respondidas']}")
if qq["abertas"]:
    print(f"  ainda esperando você: {', '.join(qq['abertas'])}")
if qq["vencidas_por_marco"]:
    print("  MARCO JÁ PASSOU e a pergunta continua aberta:")
    for ident, marcos in qq["vencidas_por_marco"]:
        print(f"    {ident:<7} o card {marcos} está fechado no BACKLOG")
    print("    A tarefa andou sem a resposta — ou ela foi decidida sem você e ninguém")
    print("    registrou, ou foi construída sobre um chute. As duas precisam de uma linha.")

a = R["achados"]
titulo("Achados (QA-NN)")
print(f"  total: {a['total']}   abertos: {a['abertos']}   fechados: {a['fechados']}")
print(f"  severidade: " + " · ".join(f"{k} {v}" for k, v in a["por_severidade"].items()))
print(f"  origem:     " + " · ".join(f"{k} {v}" for k, v in a["por_origem"].items()))
_nd = a["por_origem"].get("não declarada", 0)
if _nd == a["total"] and a["total"] and not a["tem_coluna_origem"]:
    print("    A coluna 'Origem' NÃO EXISTE na sua tabela, então nenhum achado a declara.")
    print("    Isso não é 'o portão pegou zero': é 'ninguém sabe'. E é a diferença entre")
    print("    medir o kit e o kit se elogiar por ter seguido a própria regra. Acrescente")
    print("    a coluna (portão/revisão/dono/usuário); os antigos podem ficar em branco.")
elif _nd == a["total"] and a["total"]:
    print("    A coluna existe e está VAZIA — diagnóstico diferente do anterior, e a ação")
    print("    também: aqui não falta estrutura, falta preencher no próximo achado.")
elif _nd:
    print(f"    ({_nd} sem origem declarada — provavelmente anteriores à coluna.)")
print(f"  passagens de revisão MEDIDAS (datas distintas): {a['passagens_medidas']}")
if a["abertos_detalhe"]:
    print("  abertos, do mais velho:")
    for i, s, dt in a["abertos_detalhe"][:8]:
        idade = ""
        if dt:
            try:
                idade = f"{(date.today() - date(*map(int, dt.split('-')))).days} dias"
            except ValueError:
                idade = ""
        print(f"    {i:<7} {s:<8} {dt or '?':<12} {idade}")

s = R["skills"]
titulo("Skills — qual pagou o próprio custo")
print(f"  disponíveis: {s['disponiveis']}   dispararam alguma vez: {s['dispararam']}")
for nome, n in s["uso"]:
    print(f"    {n:>4}  {nome}")
if s["nunca_dispararam"]:
    print(f"  nunca dispararam ({len(s['nunca_dispararam'])}): {', '.join(s['nunca_dispararam'])}")
    print("    ATENÇÃO: 'nunca disparou' tem DUAS causas — não foi usada, ou não era")
    print("    aplicável a este projeto. O script não sabe distinguir; quem julga é você.")

titulo("Git")
if not tem_git:
    print("  SEM repositório git legível aqui. Metade deste relatório depende dele, e")
    print("  essa metade NÃO foi medida — não é 'zero', é 'não verificado'.")
else:
    g = R["git"]
    print(f"  commits: {g['commits']}   em {g['dias_com_commit']} dias distintos")
    print(f"  citam um ID no assunto: {g['citam_id']} ({g['pct_citam_id']}%)")
    print(f"  pulos do portão declarados: pelo menos {g['pulos_declarados']} "
          f"(commits com 'SEM-PORTAO:')")
    for linha in g.get("pulos_detalhe", []):
        print(f"    {linha}")
    if not g["pulos_declarados"]:
        print("    Zero AQUI significa 'nenhum pulo declarado', não 'nenhum pulo'. A trava")
        print("    do pulo (task.py portao) só cobre o commit feito pelo agente.")
    if prefixo:
        print(f"  processo x produto: " + " · ".join(f"{k} {v}" for k, v in g["mistura"].items()))
        print(f"  commits que só tocam processo: {g['pct_so_processo']}%")
    else:
        print("  processo x produto: NÃO MEDIDO — o vault é a raiz do repositório, então")
        print("  este repo é o próprio kit e não existe 'produto' para separar.")
    if g.get("escopo"):
        print("  áreas do produto por commit: "
              + " · ".join(f"{k} área(s): {v}" for k, v in g["escopo"].items()))
    if g.get("delta"):
        print("  delta x regeneração:")
        for arq, v in g["delta"].items():
            print(f"    {arq:<32} {v['commits_que_tocam']:>4} toques · mediana "
                  f"{v['mediana_linhas']:>3} linhas · {v['reescritas_integrais']} reescrita(s) integral(is)")

titulo("O que este relatório NÃO mede")
print("  1. Se o kit AJUDOU. Isso exigiria o mesmo projeto feito sem ele, e não existe.")
print("     Todo número aqui descreve o que aconteceu COM o kit, nunca o que teria")
print("     acontecido sem — e a diferença entre as duas coisas é a pergunta inteira.")
print("  2. Se uma skill era aplicável. 'Nunca disparou' não é acusação.")
print("  3. Quantos commits pularam o portão SEM declarar. O pulo declarado agora é contado")
print("     acima; o pulo feito fora do agente, ou com o hook desligado, segue invisível.")
print("  4. Quanto de contexto uma sessão gastou de fato. Ele mede o TAMANHO do arquivo")
print("     que a regra manda ler; quanto o agente carregou é comportamento, não arquivo.")
print("  5. Qualidade. Um registro pode estar completo, datado, dentro do teto — e errado.")
print("  6. Se a ORIGEM declarada é verdadeira. Quem escreve 'portão' na linha é quem")
print("     achou o defeito, e ninguém confere. O campo tira o número de irrespondível")
print("     para autodeclarado — que é melhor, e não é o mesmo que verificado.")
print("\n  `python scripts/task.py marco` grava este relatório em e_qa/evidencia_AAMMDD.json")
print("  e mostra o delta contra o anterior. Um projeto é um relato; a série é a medida —")
print("  e tendência não se reconstrói depois, só se acumula.")
