#!/usr/bin/env python3
"""Congela um arquivo: depois disto, mudar o conteúdo dele reprova o commit.

    python scripts/congelar.py <arquivo> [<arquivo> ...]       # congela (todos, ou nenhum)
    python scripts/congelar.py --liberar <arquivo> "<motivo>"  # libera, deixando rastro
    python scripts/congelar.py                                 # lista e confere

O caminho é relativo à pasta de onde você chama — também quando chama pelo `task.py`.

**Por que isto existe.** O kit já congelava documento — à mão. O critério de conclusão do
TAP GO foi congelado com um hash no changelog e uma instrução escrita dentro dele: "se o
número não bater, este arquivo foi editado depois do congelamento". O hash foi calculado numa
cópia CRLF do Windows; o `.gitattributes` (`eol=lf`) normalizou o arquivo no commit; e dali
em diante a instrução passou a acusar de adulteração um documento INTACTO — `a9f129bd…` no
changelog, `07179f33…` no disco, e `a9f129bd…` é exatamente o mesmo blob com CRLF. Ninguém
percebeu porque ninguém rodou: verificação que ninguém executa é portão que emudeceu antes de
nascer. Congelar é o que torna um experimento honesto — o critério escrito antes do dado, o
recorte fechado antes da primeira tarefa —, e isso não pode depender de alguém lembrar.

**O hash.** Em texto, toda sequência de CR antes de um LF vira LF — o ponto fixo da conversão
do git. Nos tipos marcados `text` (.md, .py, .json, .sh) o git tira UM CR por CRLF, e "CR CR
LF" no disco vira "CR LF" no commit; em `text=auto`, um CR solto faz o git não converter
nada. Nos dois casos, só o ponto fixo faz o disco de quem congelou, o blob e o checkout do CI
darem o mesmo número. Em binário (NUL nos primeiros 8000 bytes — a heurística de diff do git,
não a de fim de linha), o sha256 é cru, e um CR a mais é mudança de verdade. Limite conhecido:
um `.md` com NUL é convertido pelo git e hasheado cru aqui.

**O registro é append-only, e quem confere é o portão, não a boa vontade.** `--liberar` exige
motivo e grava linha nova. Uma linha de congelamento comentada, um recongelamento com outro
hash sem LIBERADO no meio, o registro apagado ou uma linha antiga editada (estes dois contra o
que o git já guardou): tudo isso reprova. Recalcular o hash e anexar é o remendo que um agente
faz ao ler "hash não bate" — e foi uma revisão adversarial desta mesma versão que mostrou que
ele passava verde.

O `check.py` (FALHA 19) e o `evidencia.py` carregam ESTE arquivo em vez de copiar a regra: o
formato do registro e a conta do hash moram num lugar só.
"""
import hashlib
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

REGISTRO = ".kit-congelados"
CABECALHO = (
    "# Arquivos congelados: o CONTEUDO deles nao muda mais, e o check.py reprova se mudar.\n"
    "# Hash = sha256 do conteudo com todo CR antes de LF removido (ponto fixo do git: disco,\n"
    "# blob e clone do CI concordam); binario (NUL nos primeiros 8000 bytes) vai cru.\n"
    "# Nao edite a mao: use `python scripts/task.py congelar`. Append-only - a ultima linha\n"
    "# de cada arquivo vale, e liberar tambem deixa rastro.\n"
)
ESTADOS = {"CONGELADO", "LIBERADO"}
# Tudo o que `str.splitlines()` trata como fim de linha. Um destes no caminho ou no motivo
# parte a linha do registro em duas, e o próprio script deixa de conseguir lê-lo.
QUEBRAS = "\r\n\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029"
COMENTADA = re.compile(r"^#\s*(CONGELADO|LIBERADO)\s*\|")
USO = """Uso:
  python scripts/congelar.py <arquivo> [<arquivo> ...]       congela (todos, ou nenhum)
  python scripts/congelar.py --liberar <arquivo> "<motivo>"  libera, deixando rastro
  python scripts/congelar.py                                 lista e confere
O caminho é relativo à pasta de onde você chama — também via task.py congelar."""


def impressao(dados: bytes) -> str:
    """sha256 do conteúdo, com o fim de linha no ponto fixo do git (ver o docstring do módulo).
    Sem isto o mesmo arquivo tem dois hashes — um no Windows que o escreveu, outro no git que o
    guardou —, e o congelamento acusa quem não mexeu em nada."""
    if b"\0" in dados[:8000]:
        return hashlib.sha256(dados).hexdigest()
    return hashlib.sha256(re.sub(rb"\r+\n", b"\n", dados)).hexdigest()


def _git(pasta: Path, *args):
    """encoding fixo: o git emite UTF-8, e `text=True` sozinho decodifica com o encoding do
    sistema — é o QA-01, que já derrubou três scripts deste kit."""
    try:
        return subprocess.run(["git", "-C", str(pasta), *args], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None


def _ignorado(vault: Path, alvo: Path) -> bool:
    """O `.gitignore` esconde o arquivo do git? Aí congelar é armadilha: o registro vai para o
    commit, o arquivo não, e o CI dá o congelado como apagado para sempre."""
    r = _git(vault, "check-ignore", "-q", str(alvo))
    return r is not None and r.returncode == 0


def _caminho_valido(c: str) -> bool:
    p = Path(c)
    return (bool(c) and not p.is_absolute() and ".." not in p.parts and "\\" not in c
            and "|" not in c and not any(q in c for q in QUEBRAS))


def ler_registro(vault: Path):
    """Devolve `(vigente, erros)`.

    `vigente` = {caminho: (estado, hash ou None, data, motivo ou None)}, com a ÚLTIMA linha de
    cada caminho. `erros` = o que não se deixa ler, ou o que o registro não pode conter.
    Registro que o dono acha que tem e o script não entende é congelamento que não existe —
    dizer isso em voz alta é trabalho de quem chama; aqui só não se engole nada em silêncio."""
    arq = vault / REGISTRO
    vigente, erros = {}, []
    if not arq.exists():
        return vigente, erros
    try:
        # `utf-8-sig`: o PowerShell 5.1 grava UTF-8 com BOM, e o BOM não é conteúdo.
        texto = arq.read_bytes().decode("utf-8-sig")
    except UnicodeDecodeError as erro:
        return {}, [f"o registro não é UTF-8 (byte inválido na posição {erro.start}) — "
                    "regrave-o em UTF-8"]
    for n, linha in enumerate(texto.splitlines(), 1):
        bruta = linha.strip()
        if not bruta:
            continue
        if bruta.startswith("#"):
            if COMENTADA.match(bruta):
                erros.append(f"linha {n}: congelamento COMENTADO — desistir é com --liberar e "
                             "motivo, não com '#'")
            continue
        partes = [p.strip() for p in linha.split("|", 4)]
        if len(partes) < 4 or partes[0] not in ESTADOS:
            erros.append(f"linha {n} ilegível: {bruta[:80]}")
            continue
        estado, hash_, data, caminho = partes[:4]
        extra = partes[4] if len(partes) > 4 else ""
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data):
            erros.append(f"linha {n}: data que não é AAAA-MM-DD ({data[:20]})")
            continue
        if not _caminho_valido(caminho):
            erros.append(f"linha {n}: caminho que não é relativo ao vault ({caminho[:60]})")
            continue
        if estado == "CONGELADO":
            if extra:
                erros.append(f"linha {n}: linha CONGELADO com campo a mais — duas linhas "
                             f"coladas? ({bruta[:80]})")
                continue
            if not re.fullmatch(r"[0-9a-f]{64}", hash_):
                erros.append(f"linha {n}: hash fora do formato do registro (sha256 minúsculo do "
                             f"conteúdo em LF, gerado pelo task.py congelar) ({hash_[:20]})")
                continue
            anterior = vigente.get(caminho)
            if anterior and anterior[0] == "CONGELADO" and anterior[1] != hash_:
                erros.append(f"linha {n}: {caminho} recongelado com OUTRO conteúdo sem LIBERADO "
                             "antes — é o remendo de quem recalculou o hash para calar o portão")
                continue
        elif not extra:
            erros.append(f"linha {n}: liberação sem motivo — é o que este registro existe para impedir")
            continue
        vigente[caminho] = (estado, hash_ if estado == "CONGELADO" else None, data, extra or None)
    return vigente, erros


def conferir_registro_no_git(vault: Path) -> list:
    """O registro contra o que o git já guardou. Sumiu do disco estando no HEAD, ou o conteúdo
    do HEAD deixou de ser prefixo do atual (alguém editou ou apagou linha antiga): os dois
    soltam congelados sem deixar LIBERADO. Sem git, ou com o registro ainda fora do HEAD, não
    há o que conferir — e aí não se inventa erro."""
    arq = vault / REGISTRO
    topo = _git(vault, "rev-parse", "--show-toplevel")
    if topo is None or topo.returncode != 0 or not topo.stdout.strip():
        return []
    try:
        rel = arq.resolve().relative_to(Path(topo.stdout.strip()).resolve()).as_posix()
    except ValueError:
        return []
    head = _git(vault, "show", f"HEAD:{rel}")
    if head is None or head.returncode != 0:
        return []
    if not arq.exists():
        return ["o registro de congelados está no git (HEAD) e sumiu do disco — apagá-lo solta "
                "todos os congelados de uma vez, sem motivo nenhum"]

    def linhas(s: str) -> list:
        # Por LINHA, e não por texto: a quebra no fim do arquivo (que editor tira e põe sozinho)
        # e o espaço no fim da linha não são conteúdo. Comparando texto, um registro sem a última
        # quebra fazia o próprio congelar.py recusar — foi um teste desta versão que pegou.
        return [ln.rstrip() for ln in s.lstrip("\ufeff").replace("\r\n", "\n").splitlines()]

    antes = linhas(head.stdout)
    agora = linhas(arq.read_bytes().decode("utf-8-sig", errors="replace"))
    if agora[:len(antes)] != antes:
        return ["o registro perdeu ou mudou linhas que já estavam no git — ele é append-only: "
                "desistir de um congelado é uma linha LIBERADO nova, não edição"]
    return []


def conferir(vault: Path):
    """`([(caminho, situação)], erros)` para cada congelado vigente. Situação: `integro`,
    `editado` ou `ausente`. Liberado não entra: ele saiu do congelamento com rastro."""
    vigente, erros = ler_registro(vault)
    saida = []
    for caminho, (estado, hash_, _data, _motivo) in sorted(vigente.items()):
        if estado != "CONGELADO":
            continue
        alvo = vault / caminho
        if not alvo.is_file():
            saida.append((caminho, "ausente"))
        elif impressao(alvo.read_bytes()) != hash_:
            saida.append((caminho, "editado"))
        else:
            saida.append((caminho, "integro"))
    return saida, erros


def _resolver(vault: Path, bruto: str):
    """O arquivo pedido, relativo à pasta de ONDE SE CHAMOU, e o caminho dele dentro do vault
    (ou None, se estiver fora). Não existe segunda tentativa a partir do vault: ela escolhia um
    arquivo de mesmo nome noutra pasta e congelava — ou liberava — o errado."""
    alvo = Path(bruto)
    if not alvo.is_absolute():
        alvo = Path.cwd() / alvo
    alvo = alvo.resolve()
    try:
        return alvo, alvo.relative_to(vault.resolve()).as_posix()
    except ValueError:
        return alvo, None


def _fora_do_registro(vault: Path, alvo: Path, rel):
    if rel is None:
        return (f"{alvo} está fora do vault ({vault}). O caminho é relativo à pasta de onde você "
                "chamou, e só se congela o que o portão enxerga.")
    if rel == REGISTRO:
        return f"{REGISTRO} é o próprio registro — ele cresce por construção, não se congela."
    if not _caminho_valido(rel):
        return f"caminho que o registro não consegue guardar (| ou quebra de linha no nome): {rel!r}"
    return None


def _nao_congelavel(vault: Path, alvo: Path, bruto: str):
    if alvo.is_dir():
        return f"{bruto} é pasta — congele os arquivos dela (ex.: task.py congelar {bruto}/*.md)."
    if not alvo.is_file():
        return f"{bruto} não existe (procurei em {alvo})."
    if _ignorado(vault, alvo):
        return (f"{bruto} está num caminho que o .gitignore ignora: o registro iria para o commit "
                "e o arquivo não, e o CI o daria como apagado para sempre.")
    return None


def _anexar(vault: Path, linha: str) -> None:
    arq = vault / REGISTRO
    if not arq.exists():
        arq.write_text(CABECALHO, encoding="utf-8", newline="\n")
    elif not arq.read_bytes().endswith(b"\n"):
        # Anexar a um arquivo sem quebra no fim cola a linha nova na anterior, e as duas
        # viram uma linha que o check.py reprovaria sem ninguém ter errado.
        with arq.open("a", encoding="utf-8", newline="\n") as f:
            f.write("\n")
    with arq.open("a", encoding="utf-8", newline="\n") as f:
        f.write(linha + "\n")


def main() -> int:
    for _f in (sys.stdout, sys.stderr):
        if hasattr(_f, "reconfigure"):
            _f.reconfigure(errors="replace")
    vault = Path(__file__).resolve().parent.parent
    args = sys.argv[1:]
    hoje = date.today().isoformat()

    if args and args[0] in ("-h", "--help", "ajuda"):
        print(USO)
        return 0

    vigente, erros = ler_registro(vault)
    erros = conferir_registro_no_git(vault) + erros

    if not args:
        situacoes, _ = conferir(vault)
        if not situacoes and not erros:
            print("Nenhum arquivo congelado neste vault.")
            print("   Congelar: python scripts/task.py congelar <arquivo>")
            return 0
        for caminho, situacao in situacoes:
            print(f"  {situacao:<8} {caminho}")
        for erro in erros:
            print(f"  ERRO     {erro}")
        return 1 if (erros or any(s != "integro" for _, s in situacoes)) else 0

    if erros:
        print(f"ERRO: {REGISTRO} tem problema(s) — conserte antes de mexer nele:")
        for erro in erros:
            print(f"   {erro}")
        return 1

    if args[0] == "--liberar":
        # `split()` sem argumento consome todo separador que o `splitlines()` usaria.
        motivo = " ".join(" ".join(args[2:]).split())
        if len(args) < 3 or not motivo:
            print('ERRO: liberar exige motivo:  congelar.py --liberar <arquivo> "<motivo>"')
            print("   Liberar é permitido; liberar calado, não — o motivo é o rastro.")
            return 2
        alvo, rel = _resolver(vault, args[1])
        problema = _fora_do_registro(vault, alvo, rel)
        if problema:
            print(f"ERRO: {problema}")
            return 2
        atual = vigente.get(rel)
        if not atual or atual[0] != "CONGELADO":
            print(f"ERRO: {rel} não está congelado — nada a liberar.")
            ativos = sorted(c for c, v in vigente.items() if v[0] == "CONGELADO")
            if ativos:
                print("   Congelados agora: " + ", ".join(ativos))
            return 1
        _anexar(vault, f"LIBERADO  | - | {hoje} | {rel} | {motivo}")
        print(f"OK: {rel} liberado. O motivo fica em {REGISTRO}, para sempre.")
        return 0

    novos, codigo = [], 0
    for bruto in args:
        alvo, rel = _resolver(vault, bruto)
        problema = _fora_do_registro(vault, alvo, rel) or _nao_congelavel(vault, alvo, bruto)
        if problema:
            print(f"ERRO: {problema}")
            codigo = max(codigo, 2)
            continue
        h = impressao(alvo.read_bytes())
        atual = vigente.get(rel)
        if atual and atual[0] == "CONGELADO":
            if atual[1] == h:
                print(f"{rel} já está congelado com este conteúdo ({h[:12]}…). Nada a fazer.")
                continue
            print(f"ERRO: {rel} já está congelado com OUTRO conteúdo "
                  f"({atual[1][:12]}… no registro, {h[:12]}… no disco).")
            print("   Mudar um congelado não é correção, é documento novo: escreva outro arquivo,")
            print("   datado, dizendo o que mudou e por quê — e congele ESSE. Para desistir do")
            print('   congelamento: congelar.py --liberar <arquivo> "<motivo>".')
            codigo = max(codigo, 1)
            continue
        if all(rel != r for r, _ in novos):
            novos.append((rel, h))
    if codigo:
        if novos:
            print("Nada foi congelado: é tudo ou nada, para o registro não ficar pela metade.")
        return codigo
    for rel, h in novos:
        _anexar(vault, f"CONGELADO | {h} | {hoje} | {rel}")
        print(f"OK: {rel} congelado  (sha256 {h[:16]}…)")
    if novos:
        print("   Mudar o conteúdo passa a reprovar no check.py (FALHA 19) — e o commit, com o "
              "pre-commit ligado.")
        print(f"   Commite o(s) arquivo(s) e o {REGISTRO} JUNTOS: congelamento fora do git não "
              "existe para ninguém.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
