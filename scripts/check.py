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
                                       16. Teto de orçamento elevado sem registro no DECISIONS
                                       17. Registro declarado em .kit-config.json acima do teto
                                       18. Linha de registro acima do limite declarado

AVISOS (não reprovam; com --avisos-reprovam, reprovam)
  frontmatter ausente · placeholders · templates em rascunho · nota órfã ·
  arquivo grande não varrido · varredura de histórico que não rodou ·
  portão automático (pre-commit) não instalado · módulo do PLANO sem tarefa ·
  description de skill sem fronteira negativa · CONTEXT perto do teto ·
  DECISIONS perto do teto · BACKLOG perto do teto · registro declarado perto do teto ·
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
from collections import Counter
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

# --- Orçamentos ---------------------------------------------------------------------
# A tese central do kit é "orçamento cobrado por script". Ela foi FALSEADA pelo próprio
# kit no primeiro projeto real: o backlog chegou a 191.591 caracteres (1.596% do teto) e
# o registro de decisões a 157%, DEPOIS de o teto dele ter sido elevado de 12.000 para
# 20.000 dentro do projeto. O portão não impediu nada — porque o teto que aperta é
# editável por quem está sendo apertado, e a edição não deixava rastro nenhum.
#
# Agora deixa. `TETOS_PADRAO` é o kit e não se mexe; `TETOS` é o projeto e pode subir —
# só que subir sem registrar reprova (FALHA 16). Um limite que sobe em silêncio não é
# limite, é lembrete.
TETOS_PADRAO = {CONTEXTO: 4000, DECISOES: 12000, BACKLOG: 12000}

# O projeto NÃO sobe o teto editando este arquivo. Ele declara em `.kit-config.json`, no
# vault, e o `check.py` continua byte a byte igual ao do kit.
#
# Isto nasceu de um custo medido, não de gosto: o primeiro projeto real precisou de um teto
# maior e de um TERCEIRO registro (os `QA-NN` saíram do DECISIONS para `a_context/d_qa.md`),
# e a única saída que o kit oferecia era editar o `check.py`. Resultado: o portão do projeto
# virou um FORK do portão do kit — 8 versões atrasado, com uma cegueira já corrigida aqui e
# marcado como "PROTEGIDO" em toda atualização. O projeto passou a medir a si mesmo com uma
# régua que não era mais a régua. Customização por edição de script é dívida com juros.
#
#   {"tetos": {"a_context/c_decisions.md": 20000, "a_context/d_qa.md": 8000},
#    "registros": ["a_context/d_qa.md"],
#    "medir_sem_padding": true,
#    "linha_max": {"limite": 400, "isentas": ["D-75", "D-76"]},
#    "candidatas": "nao_citadas"}
#
# `tetos`      — teto em caracteres, por caminho (relativo ao vault).
# `registros`  — arquivos que também DEFINEM IDs D-/Q-/QA-, além do DECISIONS.
# `medir_sem_padding` — mede o CONTEÚDO das tabelas, sem o padding de alinhamento.
# `linha_max`  — {"limite": N, "isentas": [ID, ...]}: linha de registro acima de N reprova.
# `candidatas` — "mais_antigas" (padrão) | "nao_citadas": critério do que arquivar.
#
# Subir teto continua exigindo um D-NN (FALHA 16). O que muda é onde a elevação mora: num
# dado versionado, e não numa linha de código que ninguém consegue atualizar depois.
#
# As três últimas chaves nasceram do MESMO projeto e do MESMO custo que as duas primeiras.
# Ele havia escrito no fork três regras que o kit não tinha; o `--upgrade` do v13.10 devolveu
# o portão do kit e as três sumiram SEM UMA LINHA DE AVISO. Duas delas seguravam hipótese de
# auditoria: sem `medir_sem_padding` o registro passou de 18.858 para 19.422 medidos sem uma
# palavra nova (um formatador de Markdown já somou 2.048 de padding puro naquele arquivo, e
# o teto é 20.000); sem `candidatas` o aviso voltou a apontar as REJEITADAS, que são a
# lista-morta que a fase de evolução varre. Regra que o projeto precisa e o kit não tem vira
# fork; fork vira régua que não é mais a régua. Configuração é a saída, e é por isso que
# CHAVE DESCONHECIDA REPROVA (abaixo): a chave que some calada é a doença, não o remédio.
CONFIG = ".kit-config.json"

# O contrato inteiro num lugar só. Chave fora daqui não é ignorada: reprova.
CHAVES_CONFIG = {"tetos", "registros", "medir_sem_padding", "linha_max", "candidatas"}
CANDIDATAS_VALIDAS = {"mais_antigas", "nao_citadas"}


def _config_do_projeto() -> dict:
    alvo = raiz / CONFIG
    if not alvo.exists():
        return {}
    import json as _json
    try:
        dados = _json.loads(alvo.read_text(encoding="utf-8"))
    except (ValueError, OSError) as erro:
        # Config quebrada REPROVA, e não "vale o padrão em silêncio": teto que o dono acha
        # que declarou e o script ignorou é pior que teto nenhum.
        falhas.append(f"{CONFIG} não é JSON válido ({erro}) — corrija antes de commitar.")
        return {}
    if not isinstance(dados, dict):
        falhas.append(f"{CONFIG} precisa ser um objeto JSON.")
        return {}
    return dados


_cfg = _config_do_projeto()
TETOS = dict(TETOS_PADRAO)
for _arq, _valor in (_cfg.get("tetos") or {}).items():
    if isinstance(_valor, int) and _valor > 0:
        TETOS[_arq] = _valor
    else:
        falhas.append(f"{CONFIG}: teto de {_arq} precisa ser um inteiro positivo (veio {_valor!r}).")
# Registros extras: onde mais um ID pode NASCER. Sem isto, um projeto que move os `QA-NN`
# para arquivo próprio vê todos eles virarem "ID fantasma" — e a saída que sobrava era
# editar o portão, que é exatamente o que esta configuração existe para evitar.
REGISTROS_EXTRAS = [r for r in (_cfg.get("registros") or []) if isinstance(r, str)]

# Chave desconhecida REPROVA, pelo mesmo motivo que JSON quebrado reprova: o dono acha que
# declarou, o script ignora, e o verde continua saindo por cima de uma regra que nao existe.
# Um erro de digitacao em `linha_max` custa exatamente o que custou o `--upgrade` que apagou
# a regra sem avisar. Falso verde e o pior estado do portao: pior que vermelho, e pior que
# portao nenhum, porque este mente com autoridade.
_desconhecidas = sorted(set(_cfg) - CHAVES_CONFIG)
if _desconhecidas:
    falhas.append(
        f"{CONFIG}: chave(s) que este kit nao conhece: {', '.join(_desconhecidas)} - "
        f"as validas sao {', '.join(sorted(CHAVES_CONFIG))}. Chave ignorada em silencio "
        "vira regra que o dono acha que tem e nao tem; corrija o nome ou remova a chave."
    )

# `medir_sem_padding` (o CONTEUDO, sem o alinhamento das tabelas). Medido no primeiro
# projeto real em 2026-08-12: ao salvar o registro de decisoes, um formatador de Markdown
# alinhou as colunas e somou 2.048 caracteres de padding PURO - 17% do arquivo, sem uma
# palavra nova. O portao passou a reprovar num commit que so respondia uma questao, e foi
# preciso desalinhar tudo a mao para voltar. Orcamento que conta espaco de alinhamento mede
# o FORMATADOR do editor, nao o texto, e some ou volta conforme quem salvou por ultimo.
# Fica OPCIONAL, e o padrao continua `len()`: a regua que conta tudo e a mais facil de
# explicar, e projeto sem tabela em registro nao paga nada por ela. Quem usa, declara.
SEM_PADDING = bool(_cfg.get("medir_sem_padding"))


def medida(texto: str) -> int:
    """Regua dos orcamentos. Com `medir_sem_padding`, as celulas viram `a|b|c` antes de
    contar - o mesmo conteudo mede igual em qualquer editor. So mede; NUNCA reescreve o
    arquivo: o alinhamento continua livre para quem edita."""
    if not SEM_PADDING:
        return len(texto)
    linhas = []
    for linha in texto.split("\n"):
        if linha.lstrip().startswith("|"):
            linha = re.sub(r" *\| *", "|", linha.strip())
        linhas.append(linha)
    return len("\n".join(linhas))


# `linha_max`: o teto do ARQUIVO so morde quando ja e tarde, e quem esta no meio de uma
# sessao corta o que estiver a mao - nao o que devia sair. O custo real esta na linha que
# carrega a INTEGRA da evidencia em vez de delega-la a uma nota. Medido no mesmo projeto:
# 141, 175 e 238 quando a linha delega; 922 e 978 quando nao delega.
# `isentas` e lista CONGELADA, nao janela movel: linha que ja estava viva quando o limite
# foi adotado nao pode ser reescrita num registro append-only, e checagem que nasce vermelha
# em linha que ninguem PODE consertar ensina a ignorar o script. A lista mora no dado
# versionado e aparece no diff - ID novo ali e decisao do dono, nao descuido.
LINHA_MAX = None
ISENTAS_LINHA = ()
_lm = _cfg.get("linha_max")
if isinstance(_lm, dict):
    _limite = _lm.get("limite")
    if isinstance(_limite, int) and _limite > 0:
        LINHA_MAX = _limite
    else:
        falhas.append(
            f"{CONFIG}: linha_max.limite precisa ser um inteiro positivo (veio {_limite!r})."
        )
    _isentas = _lm.get("isentas") or []
    if isinstance(_isentas, list) and all(isinstance(i, str) for i in _isentas):
        ISENTAS_LINHA = tuple(_isentas)
    else:
        falhas.append(
            f"{CONFIG}: linha_max.isentas precisa ser uma lista de IDs (veio {_isentas!r})."
        )
elif _lm is not None:
    falhas.append(
        f'{CONFIG}: linha_max precisa ser um objeto {{"limite": N, "isentas": [...]}} '
        f"(veio {_lm!r})."
    )

# `candidatas`: qual criterio o aviso do DECISIONS usa para apontar o que arquivar.
# "mais_antigas" e o padrao do kit. "nao_citadas" sai do criterio do projeto que decidiu
# que deixa a tabela quem NENHUM `.md` vivo cita - e existe porque o padrao, num projeto que
# preserva as REJEITADAS de proposito, aponta justamente para elas: a lista-morta que a fase
# de evolucao varre sem abrir o arquivo. Aviso que manda apagar a memoria de rejeicao ensina
# a re-propor o que ja morreu, que e o oposto do que o registro existe para fazer.
CANDIDATAS = _cfg.get("candidatas", "mais_antigas")
if CANDIDATAS not in CANDIDATAS_VALIDAS:
    falhas.append(
        f"{CONFIG}: candidatas precisa ser "
        f"{' ou '.join(sorted(CANDIDATAS_VALIDAS))} (veio {CANDIDATAS!r})."
    )
    CANDIDATAS = "mais_antigas"
# Avisar a 90% do teto em vez de só reprovar a 100%: quando o teto estoura, quem escreve
# está no meio de uma sessão de trabalho e corta o que estiver à mão — não o que devia sair.
PERTO = 0.90


def mil(n: int) -> str:
    """12000 -> '12.000'. O texto do portão sempre imprimiu assim; com o teto virando
    variável, a formatação precisou virar função em vez de literal escrito à mão."""
    return f"{n:,}".replace(",", ".")


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
elif medida(texto_ctx) > TETOS[CONTEXTO]:
    falhas.append(
        f"{CONTEXTO} com {medida(texto_ctx)} caracteres (orçamento: {mil(TETOS[CONTEXTO])}). "
        f"Corte: detalhe -> a_context/<tema>.md, decisão -> {DECISOES}, datado -> d_history/a_changelog.md."
    )
elif medida(texto_ctx) > TETOS[CONTEXTO] * PERTO:
    # O aviso dá a chance de mover um tema com calma, antes da parede (ver PERTO).
    avisos.append(
        f"{CONTEXTO} com {medida(texto_ctx)}/{mil(TETOS[CONTEXTO])} caracteres "
        f"({100*medida(texto_ctx)//TETOS[CONTEXTO]}%) — "
        "mova um tema para a_context/<tema>.md agora, não na sessão em que estourar."
    )

# 2. Registro de decisões inchado (projeto longo)
dec = raiz / DECISOES
texto_dec = corpo.get(dec, "")
if texto_dec and medida(texto_dec) > TETOS[DECISOES]:
    falhas.append(
        f"{DECISOES} acima de {mil(TETOS[DECISOES])} caracteres — arquive SUPERSEDIDAS/rejeitadas "
        "antigas em e_qa/decisions_archive.md (IDs preservados) e deixe um ponteiro."
    )
elif texto_dec and medida(texto_dec) > TETOS[DECISOES] * PERTO:
    # O README declarava esta fraqueza com todas as letras: "o arquivamento é manual e
    # ninguém lembra". Portão que só roda quando alguém lembra não é portão — foi o
    # argumento do QA-04, e valia contra o próprio kit. O script não arquiva (a decisão
    # é do dono); ele avisa antes da parede e já aponta os candidatos.
    if CANDIDATAS == "nao_citadas":
        # Sai da tabela quem NENHUM `.md` vivo cita. Recorte de "vivo": tudo menos o
        # proprio registro, o arquivo morto e o historico datado - os tres citam por
        # oficio, e contá-los faria todo ID parecer vivo para sempre.
        _vivos = "\n".join(
            txt for cam, txt in corpo.items()
            if cam.name not in (Path(DECISOES).name, Path(ARQUIVO_MORTO).name)
            and "d_history" not in cam.parts
        )
        velhas = [i for i in re.findall(r"^\|\s*(D-\d+)\s*\|", texto_dec, re.M)
                  if not re.search(rf"\b{i}\b", _vivos)]
        # Pool vazio e informacao, nao ausencia de informacao: dizer "as mais antigas"
        # aqui mandaria arquivar linha que o proprio criterio proibe retirar.
        amostra = ", ".join(velhas[:5]) if velhas else (
            "NENHUMA — todo D-NN vivo e citado por algum .md, entao este corte esta "
            "esgotado e o peso nao esta mais em linha morta")
    else:
        velhas = re.findall(r"^\|\s*(D-\d+)\s*\|[^|]*\|\s*(?:ADOTADO|REJEITADO)", texto_dec, re.M)
        amostra = ", ".join(velhas[:5]) if velhas else "as mais antigas"
    avisos.append(
        f"{DECISOES} com {medida(texto_dec)}/{mil(TETOS[DECISOES])} caracteres "
        f"({100*medida(texto_dec)//TETOS[DECISOES]}%) — "
        f"arquive as antigas em e_qa/decisions_archive.md, preservando os IDs. Candidatas: {amostra}."
    )

# 18. Linha de registro acima do limite declarado (`linha_max` na CONFIG).
#     Inerte em projeto que nao declara a chave - o kit nao tem opiniao sobre o tamanho da
#     linha de ninguem. Quem declara, declara junto a lista CONGELADA de isentas, porque
#     registro append-only tem linhas que ninguem PODE consertar e checagem que nasce
#     vermelha nelas ensina a ignorar o script.
#     A regua e a MESMA dos orcamentos (`medida`): duas reguas no mesmo arquivo fariam a
#     linha caber e o arquivo estourar, ou o contrario, sem que nenhum numero explicasse.
if LINHA_MAX:
    longas = []
    for _nome_reg in (DECISOES, *REGISTROS_EXTRAS):
        for linha in corpo.get(raiz / _nome_reg, "").split("\n"):
            achado = re.match(r"\|\s*((?:QA|Q|D)-\d+)\s*\|", linha.strip())
            if not achado or achado.group(1) in ISENTAS_LINHA:
                continue
            n_linha = medida(linha)
            if n_linha > LINHA_MAX:
                longas.append(f"{achado.group(1)} ({n_linha}) em {_nome_reg}")
    if longas:
        falhas.append(
            f"Linha de registro acima de {LINHA_MAX} caracteres medidos "
            f"(`linha_max` em {CONFIG}): {', '.join(longas)}. Mova a evidencia para uma nota "
            "e deixe o PONTEIRO na linha. Nada de prosa comprimida: o que sai da linha entra "
            "na nota, inteiro. Linha que ninguem pode reescrever entra em `linha_max.isentas`, "
            "com o motivo no D-NN que a isentou."
        )

# 3. Fonte única (regra 6) — o mesmo nome em dois lugares é estado duplicado
# Registro extra declarado em `.kit-config.json` entra aqui: se ele é fonte de ID,
# duas cópias dele são duas verdades — o mesmo motivo dos três de casa.
for nome in {Path(a).name for a in (BACKLOG, CONTEXTO, DECISOES, *REGISTROS_EXTRAS)}:
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
    peso = sum(medida(b) for b in fechados)
    # A saída tem de ser VERDADEIRA. Medido no primeiro projeto real: depois de arquivar
    # 86% do backlog, o portão continuava mandando "arquive" e o arquivador respondia
    # "nenhum card arquivável" — o peso tinha passado para ponteiro, card aberto e prosa,
    # que ele não poda. Portão que manda fazer o que não funciona é portão sem saída, e
    # portão sem saída ensina --no-verify: é a doença que este kit persegue, cometida aqui.
    saida = ("Arquive: `python scripts/arquivar.py --backlog --aplicar` deixa o ID e o "
             "`**Módulo:**` na linha e manda a íntegra para e_qa/backlog_archive.md. "
             "Se ele responder 'nenhum card arquivável', o peso NÃO está em card fechado: "
             "está em card aberto (é trabalho — entregue ou despromova), em prosa de seção "
             "(texto seu) ou nos ponteiros já arquivados. Aí as saídas são podar à mão ou "
             "subir o teto em `.kit-config.json` com o D-NN que a FALHA 16 cobra.")
    if medida(texto_bl) > TETOS[BACKLOG]:
        falhas.append(
            f"{BACKLOG} com {medida(texto_bl)} caracteres (orçamento: {mil(TETOS[BACKLOG])}) — "
            f"{len(fechados)} card(s) fechado(s) ocupam {peso} deles. {saida}"
        )
    elif medida(texto_bl) > TETOS[BACKLOG] * PERTO:
        avisos.append(
            f"{BACKLOG} com {medida(texto_bl)}/{mil(TETOS[BACKLOG])} caracteres "
            f"({100*medida(texto_bl)//TETOS[BACKLOG]}%) — "
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
    # `.kit-config.json` pode declarar registros extras: num projeto real os `QA-NN` saíram
    # do DECISIONS para `a_context/d_qa.md`, e sem isto TODOS eles viravam "ID fantasma" —
    # o que empurrava o dono a editar este script, criando o fork que a configuração existe
    # para acabar. Um ID nasce em QUALQUER registro declarado.
    tabelas = {DECISOES: texto_dec}
    tabelas.update({r: corpo.get(raiz / r, "") for r in REGISTROS_EXTRAS})
    definidos = {i for t in tabelas.values()
                 for i in re.findall(r"^\|\s*((?:D|Q|QA)-\d+)\s*\|", t, re.M)}
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
    # Duplicata é por REGISTRO e também ENTRE registros: o mesmo QA-07 em dois cadernos é
    # o pior caso, porque as duas linhas divergem e nenhuma das duas se sabe cópia.
    ocorrencias = Counter(i for t in tabelas.values()
                          for i in re.findall(r"^\|\s*((?:D|Q|QA)-\d+)\s*\|", t, re.M))
    repetidos = [i for i, n in ocorrencias.items() if n > 1]
    if repetidos:
        onde = ", ".join(sorted(tabelas))
        falhas.append(f"ID duplicado em {onde}: " + ", ".join(sorted(repetidos)) + " — cada ID é único e append-only.")
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
        registros_de_id = {dec} | {raiz / r for r in REGISTROS_EXTRAS}
        if nota in registros_de_id or nota.stem == "d_agent_learnings":
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
# 16. Teto elevado sem registro — a tese do kit, cobrada contra o próprio kit.
# Medido no primeiro projeto real: o teto do DECISIONS subiu de 12.000 para 20.000 dentro
# do projeto, o arquivo bateu em 91% do teto NOVO, e não há uma linha em lugar nenhum
# dizendo quem subiu, quando ou por quê. O portão continuava verde: ele cobrava o número
# que a própria vítima tinha acabado de escolher.
# O script NÃO proíbe subir — a decisão é do dono, e projeto grande às vezes precisa. Ele
# proíbe subir CALADO: a elevação vira uma linha no DECISIONS, com data e motivo, que a
# sessão de evolução vai encontrar quando perguntar "por que este arquivo está enorme?".
def _registrado_no_decisions(*termos) -> bool:
    """Uma linha de D-NN que cite todos os termos. Procura no DECISIONS e nos registros
    extras, porque num projeto que moveu as tabelas de casa a decisão mora com elas."""
    fontes = [texto_dec] + [corpo.get(raiz / r, "") for r in REGISTROS_EXTRAS]
    return any(
        re.search(r"D-\d+", linha) and all(t.lower() in linha.lower() for t in termos)
        for fonte in fontes for linha in fonte.splitlines()
    )


for _alvo, _novo in TETOS.items():
    _padrao = TETOS_PADRAO.get(_alvo)
    if _padrao is not None and _novo <= _padrao:
        continue
    if _padrao is None:
        # Registro que o kit não previu (o terceiro caderno). Nasce da mesma decisão que
        # eleva um teto — o desenho de dois não coube — e por isso paga o mesmo pedágio.
        # Pelo TALO (`d_qa`), não pelo nome com extensão: a casa cita registro por wikilink
        # — `[[d_qa|QA]]` —, e foi exatamente assim que a decisão real apareceu no primeiro
        # projeto. Exigir "d_qa.md" reprovava um projeto que TINHA registrado a decisão.
        # Mesma lição do QA-14: a checagem casa com o jeito que a casa escreve, ou é cega.
        if not _registrado_no_decisions(Path(_alvo).stem):
            falhas.append(
                f"{CONFIG} declara orçamento para {_alvo}, que não é registro do kit, e nenhum "
                f"D-NN menciona esse arquivo — registro novo é decisão de projeto, não detalhe "
                f"de configuração. Registre: `| D-NN | {date.today().isoformat()} | ADOTADO | "
                f"{Path(_alvo).name} como registro próprio, teto {mil(_novo)} | <o que não coube> |`."
            )
        continue
    if not _registrado_no_decisions("teto", str(_novo)) and not _registrado_no_decisions("teto", mil(_novo)):
        falhas.append(
            f"teto de {_alvo} elevado para {mil(_novo)} (padrão do kit: {mil(_padrao)}) sem "
            f"registro no {DECISOES} — teto que sobe em silêncio não é teto, é lembrete. "
            f"Registre a elevação: `| D-NN | {date.today().isoformat()} | ADOTADO | "
            f"teto de {_alvo} para {mil(_novo)} | <o que não coube e por que arquivar não resolveu> |`."
        )

# Orçamento dos registros que o kit não conhece: mesma régua dos três de casa (reprova no
# teto, avisa em 90%), aplicada a qualquer caminho declarado em `tetos`.
for _arq, _teto in TETOS.items():
    if _arq in TETOS_PADRAO:
        continue
    _texto_extra = corpo.get(raiz / _arq, "")
    if not _texto_extra:
        continue
    if medida(_texto_extra) > _teto:
        falhas.append(
            f"{_arq} com {medida(_texto_extra)} caracteres (orçamento declarado: {mil(_teto)}) — "
            "feche, arquive ou promova a ponteiro o que já não é trabalho vivo."
        )
    elif medida(_texto_extra) > _teto * PERTO:
        avisos.append(
            f"{_arq} com {medida(_texto_extra)}/{mil(_teto)} caracteres "
            f"({100*medida(_texto_extra)//_teto}%) — arquive agora, não na sessão em que estourar."
        )

# Todo arquivo com teto entra aqui, inclusive os declarados pelo projeto: a ocupação
# escrita à mão no CONTEXT é conferida contra o arquivo, seja qual for o registro.
#
# LISTA por teto, não par: DECISIONS e BACKLOG têm o MESMO teto padrão (12.000), e um dicionário
# indexado pelo número fazia um sobrescrever o outro em silêncio — o aviso então comparava o
# número declarado com o arquivo errado e acusava divergência onde não havia. Pego pelo teste
# `test_ocupacao_declarada_certa_cala`; é a espécie do QA-14 (checagem que fala sobre outra
# coisa) na sua forma mais fácil de cometer: generalizar um dicionário sem olhar as colisões.
ORCAMENTOS = {}
for arq, teto in TETOS.items():
    ORCAMENTOS.setdefault(teto, []).append((arq, corpo.get(raiz / arq, "")))
if texto_ctx:
    divergentes = []
    for bruto_n, bruto_teto in re.findall(r"(\d[\d.]*)\s*/\s*(\d[\d.]*)", texto_ctx):
        try:
            declarado, teto = int(bruto_n.replace(".", "")), int(bruto_teto.replace(".", ""))
        except ValueError:
            continue
        candidatos = [(n, x) for n, x in ORCAMENTOS.get(teto, []) if x]
        if not candidatos:
            continue
        # Basta bater com UM arquivo daquele teto: "2.164/12.000" pode ser o DECISIONS ou o
        # BACKLOG, e o CONTEXT não diz qual. Acusar sem saber é aviso falso.
        if any(declarado == medida(x) for _, x in candidatos):
            continue
        nome = " ou ".join(n for n, _ in candidatos)
        tamanhos = " ou ".join(str(medida(x)) for _, x in candidatos)
        divergentes.append(f"diz {nome} em {declarado}/{teto}, o arquivo tem {tamanhos}")
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
