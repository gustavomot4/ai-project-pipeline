#!/usr/bin/env python3
"""Testes de regressão dos scripts do kit.  Uso: python scripts/test_check.py

Só biblioteca padrão (`unittest`): o kit não tem dependências, e um teste que exige
`pip install` não roda na máquina de quem mais precisa dele.

Cada teste aqui existe porque o bug já aconteceu de verdade, não porque era plausível:

  QA-01  caminho com acento derrubava os scripts em Windows pt-BR (cp1252)
  QA-02  `.git` como ARQUIVO (worktree/submódulo) pulava a varredura de HISTÓRICO
         em silêncio — segredo no histórico, mensagem verde, exit 0
  QA-03  a linha final anunciava "últimos 30 commits" mesmo sem ter lido nenhum
  QA-04  nada cobrava a instalação do próprio portão
  QA-14  a checagem de ID filtrava o trecho entre crases: 300 de 341 citações
         de um projeto real eram invisíveis, e o portão imprimia verde

O teste do acento é o motivo de este arquivo rodar em CI no Windows: num Linux com
locale UTF-8 o bug do QA-01 NÃO reproduz — foi exatamente esse falso "passou" que fez
a auditoria original medir errado.
"""
import ast
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

# O filho tem de EMITIR UTF-8 para o teste poder decodificar como UTF-8. Sem isto, num
# Windows pt-BR o check.py escreve em cp1252 (saída redirecionada usa o codepage do
# sistema), o teste decodifica como UTF-8, e `assertIn("histórico do git")` falha com o
# código CERTO — o teste acusava um bug que não existia. É a mesma classe do QA-01,
# cometida dentro do arquivo que existe para guardá-lo.
AMBIENTE_UTF8 = dict(os.environ, PYTHONIOENCODING="utf-8")


def apagar(caminho: Path):
    """O git marca objetos como somente-leitura. No Windows o `rmtree` então morre com
    PermissionError (WinError 5); no Linux passa. Daí este teste nunca ter falhado no
    sandbox."""
    def forcar(func, alvo, _erro):
        os.chmod(alvo, stat.S_IWRITE)
        func(alvo)

    chave = "onexc" if sys.version_info >= (3, 12) else "onerror"
    shutil.rmtree(caminho, **{chave: forcar})


def area_temporaria():
    """`ignore_cleanup_errors` pelo mesmo motivo: a faxina do TemporaryDirectory também
    tropeça nos objetos somente-leitura do git, e o teste não pode falhar na faxina."""
    if sys.version_info >= (3, 10):
        return tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
    return tempfile.TemporaryDirectory()

KIT = Path(__file__).resolve().parent.parent
GIT_ID = ["-c", "user.email=teste@kit", "-c", "user.name=teste"]
# Isca de teste, não é chave real. Montada em pedaços de propósito: escrita inteira,
# ela casa com o próprio scanner do kit e FAZ O KIT REPROVAR — foi o que aconteceu na
# primeira versão deste arquivo, e o efeito colateral foi pior que o incômodo: o teste
# do worktree passou pelo motivo errado, porque o check reprovava por causa da isca e
# não por causa do histórico. Teste que passa pelo motivo errado é pior que teste
# ausente. A marca `checar:ignore` cobre o caso de alguém remontar a string.
ISCA = "api_key=" + "sk_" + "live_" + "9ZqR4TvBn2LpQxWm7YdG3H"  # checar:ignore


def git(repo, *args, **kw):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace", **kw)


def rodar_check(cwd, env=None, extra=(), script=None):
    # `script` explícito porque num PROJETO o check.py mora em <docs>/scripts/, não na
    # raiz — e é de dentro da raiz que ele tem de ser capaz de rodar.
    alvo = Path(script) if script else Path(cwd) / "scripts" / "check.py"
    return subprocess.run([sys.executable, str(alvo), *extra],
                          cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          env=env or AMBIENTE_UTF8, timeout=180)


def rodar_script(nome, *args, cwd=None, env=None):
    alvo = Path(cwd or KIT) / "scripts" / nome
    return subprocess.run([sys.executable, str(alvo), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          env=env or AMBIENTE_UTF8, timeout=180)


def montar_kit(destino: Path) -> Path:
    """Cópia do kit em `destino`, já como repositório git."""
    shutil.copytree(KIT, destino, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    git(destino, "init", "-q")
    git(destino, "add", "-A")
    git(destino, *GIT_ID, "commit", "-qm", "base")
    return destino


def vault_de(projeto: Path) -> Path:
    """O vault do projeto, nas duas casas possíveis. Os testes criam projeto com o
    `new_project.py`, que desde o v13.14 instala em `e_doc/0_Context/` (padrão da equipe);
    a casa antiga fica reconhecida porque os scripts também a reconhecem."""
    equipe = projeto / "e_doc" / "0_Context"
    if (equipe / "a_context").is_dir():
        return equipe
    # NAO trocar por vault_de(): a substituicao em massa que criou este helper
    # trocou tambem esta linha, e o helper passou a chamar a si mesmo.
    return next(projeto.glob("*_Project_DOCs"))


def plantar_segredo(repo: Path):
    """Segredo que ENTRA e SAI da árvore: some do working tree, fica no histórico."""
    (repo / "vazou.txt").write_text(ISCA + "\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, *GIT_ID, "commit", "-qm", "add")
    (repo / "vazou.txt").unlink()
    git(repo, "add", "-A")
    git(repo, *GIT_ID, "commit", "-qm", "remove")


class TestEncoding(unittest.TestCase):
    """QA-01 — o git emite UTF-8; `text=True` sozinho decodifica com o encoding do
    SISTEMA (cp1252 num Windows pt-BR) e `UnicodeDecodeError` é ValueError, então os
    `except (SubprocessError, OSError)` não pegam."""

    def test_toda_chamada_ao_git_fixa_o_encoding(self):
        for arquivo in ("check.py", "install_hook.py", "new_project.py"):
            texto = (KIT / "scripts" / arquivo).read_text(encoding="utf-8")
            for bloco in texto.split("subprocess.run(")[1:]:
                cabeca = bloco[:400]
                if '"git"' not in cabeca:
                    continue
                self.assertTrue(
                    "**UTF8" in cabeca or "encoding=" in cabeca,
                    f"{arquivo}: chamada ao git sem encoding fixado — "
                    f"quebra em caminho com acento no Windows pt-BR.\n{cabeca[:200]}",
                )

    def test_scripts_rodam_em_caminho_acentuado(self):
        """No Windows este teste exercita cp1252 de verdade. No Linux ele só garante
        que nada mais quebrou — e é por isso que o CI roda nos dois."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "Área de Trabalho" / "projeto")
            r = rodar_check(repo)
            self.assertNotIn("Traceback", r.stderr, f"check.py estourou:\n{r.stderr[-800:]}")
            r2 = rodar_script("install_hook.py", cwd=repo)
            self.assertNotIn("Traceback", r2.stderr, f"install_hook.py estourou:\n{r2.stderr[-800:]}")

    def test_saida_nao_morre_em_console_cp1252(self):
        """QA-05 — o gêmeo do QA-01, do lado da ESCRITA. Um `→` (U+2192) num `print`
        não existe em cp1252: com a saída REDIRECIONADA num Windows pt-BR o script
        morria de UnicodeEncodeError **depois** de ter criado o projeto inteiro.
        Reproduzível em qualquer SO forçando PYTHONIOENCODING — o que torna este teste
        útil também no Linux, ao contrário do teste do caminho acentuado."""
        cp1252 = dict(os.environ, PYTHONIOENCODING="cp1252")
        with area_temporaria() as tmp:
            kit = montar_kit(Path(tmp) / "kit")
            r = rodar_script("new_project.py", str(Path(tmp) / "novo"), "--nome", "App",
                             cwd=kit, env=cp1252)
            self.assertNotIn("UnicodeEncodeError", r.stderr,
                             f"morreu imprimindo, não checando:\n{r.stderr[-500:]}")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertNotIn("UnicodeEncodeError", rodar_check(kit, env=cp1252).stderr)

    def test_nenhum_print_usa_caractere_fora_do_cp1252(self):
        """O teste acima guarda a REDE (se alguém a remover, ele falha). Este guarda o
        TEXTO: com a rede ligada a seta não mata mais o script, mas sai como `?` na tela
        de quem redireciona. Degradar em silêncio é melhor que morrer, e não escrever o
        caractere é melhor que os dois. `ast` acha o literal na fonte, sem executar."""
        for arquivo in ("check.py", "install_hook.py", "new_project.py", "task.py"):
            arvore = ast.parse((KIT / "scripts" / arquivo).read_text(encoding="utf-8"))
            for no in ast.walk(arvore):
                if not (isinstance(no, ast.Call) and getattr(no.func, "id", "") == "print"):
                    continue
                # `ast.walk` desce em f-string (JoinedStr) também, então cobre os dois casos.
                for parte in ast.walk(no):
                    if not (isinstance(parte, ast.Constant) and isinstance(parte.value, str)):
                        continue
                    for ch in parte.value:
                        try:
                            ch.encode("cp1252")
                        except UnicodeEncodeError:
                            self.fail(
                                f"{arquivo}:{no.lineno} — print com {ch!r} (U+{ord(ch):04X}), "
                                "que não existe em cp1252 e vira '?' num Windows pt-BR. "
                                "Use o equivalente ASCII (`->` em vez de `→`)."
                            )


class TestVarreduraDeHistorico(unittest.TestCase):
    """QA-02 e QA-03 — `.git` é ARQUIVO em worktree e submódulo, então
    `(topo / '.git').is_dir()` respondia 'não é repositório' e a varredura sumia."""

    def test_repo_normal_pega_segredo_no_historico(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            plantar_segredo(repo)
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 1, f"devia reprovar:\n{r.stdout[-600:]}")
            self.assertIn("histórico do git", r.stdout)

    def test_worktree_tambem_pega(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            plantar_segredo(repo)
            wt = Path(tmp) / "wt"
            if git(repo, "worktree", "add", "-q", str(wt)).returncode != 0:
                self.skipTest("git worktree indisponível")
            self.assertTrue((wt / ".git").is_file(), "premissa do teste: .git vira ARQUIVO")
            r = rodar_check(wt)
            # Asserção pelo MOTIVO, não pelo código de saída: exit 1 por qualquer outra
            # falha faria este teste passar sem guardar nada — foi o que aconteceu antes.
            self.assertIn("histórico do git", r.stdout,
                          f"worktree não varreu o HISTÓRICO (segredo passou em silêncio):\n{r.stdout[-600:]}")
            self.assertEqual(r.returncode, 1)

    def test_sem_git_nao_anuncia_commits_que_nao_leu(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            apagar(repo / ".git")
            r = rodar_check(repo)
            self.assertIn("Sem repositório git", r.stdout)
            self.assertNotIn("+ últimos 30 commits", r.stdout,
                             "linha verde afirmou varredura de histórico que não ocorreu")


class TestPortaoInstalado(unittest.TestCase):
    """QA-04 — portão que só roda quando alguém lembra não é portão."""

    def test_avisa_sem_hook_e_cala_depois_de_instalar(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.assertIn("Portão automático NÃO instalado", rodar_check(repo).stdout)
            subprocess.run([sys.executable, str(repo / "scripts" / "install_hook.py")],
                           capture_output=True, timeout=120)
            self.assertNotIn("Portão automático NÃO instalado", rodar_check(repo).stdout)

    def test_hooks_path_customizado_nao_gera_aviso_falso(self):
        """Aviso falso ensina a ignorar aviso — é o vício do `--no-verify` que o kit
        condena. O caminho tem de vir de `git rev-parse --git-path hooks`."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            subprocess.run([sys.executable, str(repo / "scripts" / "install_hook.py")],
                           capture_output=True, timeout=120)
            padrao = repo / ".git" / "hooks" / "pre-commit"
            alternativa = repo / ".githooks"
            alternativa.mkdir(exist_ok=True)
            shutil.copy(padrao, alternativa / "pre-commit")
            padrao.unlink()
            git(repo, "config", "core.hooksPath", ".githooks")
            self.assertNotIn("Portão automático NÃO instalado", rodar_check(repo).stdout)


class TestProjetoNovo(unittest.TestCase):
    """Projeto criado do kit tem de nascer passando no próprio portão."""

    def test_projeto_novo_nasce_limpo(self):
        with area_temporaria() as tmp:
            kit = montar_kit(Path(tmp) / "kit")
            destino = Path(tmp) / "novo"
            r = rodar_script("new_project.py", str(destino), "--nome", "App Teste", cwd=kit)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            docs = vault_de(destino)
            self.assertFalse((docs / "docs").exists(), "auditoria do kit vazou para o projeto")
            # Infraestrutura de desenvolvimento DO KIT não é entregável de projeto. O CI
            # cairia dentro da pasta de docs (onde o Actions não procura) e a suíte de
            # testes reprovaria no primeiro `task.py test` — suíte que nasce vermelha
            # ensina a ignorar suíte.
            self.assertFalse((docs / ".github").exists(), "o CI do kit vazou para o projeto")
            self.assertFalse((docs / "scripts/test_check.py").exists(),
                             "a suíte do kit vazou para o projeto e reprovaria lá")
            for obrigatorio in ("scripts/check.py", "scripts/task.py", "scripts/install_hook.py"):
                self.assertTrue((docs / obrigatorio).exists(), f"{obrigatorio} não foi instalado")
            git(destino, "init", "-q")
            saida = rodar_check(destino, script=docs / "scripts" / "check.py")
            self.assertNotIn("Wikilink(s) sem destino", saida.stdout,
                             "projeto novo nasceu com link quebrado")


class TestAtualizacao(unittest.TestCase):
    """`--upgrade` atualiza o PROCESSO e não pode encostar na VERDADE do projeto.
    O limite não é por pasta: `b_process/c_backlog.md` mora em "processo" e é estado.
    Errar esse limite apaga trabalho do dono — por isso este é o teste mais importante
    do arquivo."""

    def preparar(self, tmp):
        kit = montar_kit(Path(tmp) / "kit")
        projeto = Path(tmp) / "projeto"
        r = rodar_script("new_project.py", str(projeto), "--nome", "App", cwd=kit)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        docs = vault_de(projeto)
        # trabalho do dono, um por categoria de verdade
        (docs / "a_context/c_decisions.md").write_text(
            (docs / "a_context/c_decisions.md").read_text(encoding="utf-8")
            + "\n| D-99 | 2026-08-05 | ADOTADO | decisao do dono | medido |\n", encoding="utf-8")
        for arquivo, marca in (("b_process/c_backlog.md", "\n- [ ] T-99 tarefa do dono\n"),
                               ("b_process/d_agent_learnings.md", "\n- licao do dono\n"),
                               ("d_history/a_changelog.md", "\n## [0.1.0] deploy do dono\n")):
            p = docs / arquivo
            p.write_text(p.read_text(encoding="utf-8") + marca, encoding="utf-8")
        git(projeto, "init", "-q")
        git(projeto, "add", "-A")
        git(projeto, *GIT_ID, "commit", "-qm", "trabalho do dono")
        return kit, projeto, docs

    def test_atualiza_processo_e_preserva_verdade(self):
        with area_temporaria() as tmp:
            kit, projeto, docs = self.preparar(tmp)
            # o kit evolui: skill nova + arquivo de processo alterado
            nova = kit / "b_process/skills/skill-nova/SKILL.md"
            nova.parent.mkdir(parents=True, exist_ok=True)
            # Segue o esquema obrigatório de propósito: esta skill é só um veículo para
            # testar a ATUALIZAÇÃO, e não pode reprovar por outro motivo — teste que falha
            # pela razão errada é o defeito que já custou uma rodada nesta suíte.
            nova.write_text(
                "---\nname: skill-nova\ndescription: nova. Não use para outra coisa (é outra skill).\n---\n"
                "# nova\n## Contexto que você recebe\nx\n## Limites\ny\n## Saída\nz\n", encoding="utf-8")
            roteiro = kit / "b_process/a_roadmap.md"
            roteiro.write_text(roteiro.read_text(encoding="utf-8") + "\n<!-- marca v9 -->\n", encoding="utf-8")

            r = rodar_script("new_project.py", str(projeto), "--upgrade", cwd=kit)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

            # processo chegou
            self.assertTrue((docs / "b_process/skills/skill-nova/SKILL.md").exists())
            self.assertIn("marca v9", (docs / "b_process/a_roadmap.md").read_text(encoding="utf-8"))
            # verdade intacta
            for arquivo, marca in (("a_context/c_decisions.md", "D-99"),
                                   ("b_process/c_backlog.md", "T-99 tarefa do dono"),
                                   ("b_process/d_agent_learnings.md", "licao do dono"),
                                   ("d_history/a_changelog.md", "deploy do dono")):
                self.assertIn(marca, (docs / arquivo).read_text(encoding="utf-8"),
                              f"a atualização apagou trabalho do dono em {arquivo}")
            # e o projeto continua passando no próprio portão
            saida = rodar_check(projeto, script=docs / "scripts" / "check.py")
            self.assertEqual(saida.returncode, 0, saida.stdout)

    def test_dry_run_nao_escreve_e_arvore_suja_recusa(self):
        with area_temporaria() as tmp:
            kit, projeto, docs = self.preparar(tmp)
            nova = kit / "b_process/skills/skill-nova/SKILL.md"
            nova.parent.mkdir(parents=True, exist_ok=True)
            # Segue o esquema obrigatório de propósito: esta skill é só um veículo para
            # testar a ATUALIZAÇÃO, e não pode reprovar por outro motivo — teste que falha
            # pela razão errada é o defeito que já custou uma rodada nesta suíte.
            nova.write_text(
                "---\nname: skill-nova\ndescription: nova. Não use para outra coisa (é outra skill).\n---\n"
                "# nova\n## Contexto que você recebe\nx\n## Limites\ny\n## Saída\nz\n", encoding="utf-8")

            r = rodar_script("new_project.py", str(projeto), "--upgrade", "--dry-run", cwd=kit)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertFalse((docs / "b_process/skills/skill-nova/SKILL.md").exists(),
                             "--dry-run escreveu; ele existe justamente para não escrever")

            (projeto / "sujo.txt").write_text("x", encoding="utf-8")
            r2 = rodar_script("new_project.py", str(projeto), "--upgrade", cwd=kit)
            self.assertEqual(r2.returncode, 1, "aceitou atualizar sobre árvore suja")
            self.assertIn("não commitadas", r2.stdout)


class TestNadaFicaForaDaAtualizacao(unittest.TestCase):
    """`DO_KIT` é uma lista mantida à mão, e lista mantida à mão sai de sincronia.

    Aconteceu: `b_process/g_primeiros_passos.md` nasceu no v13.8, entrou na cópia de projeto
    NOVO (que copia tudo o que não está excluído) e nunca entrou no `DO_KIT`, que é o que a
    ATUALIZAÇÃO usa. Resultado medido no primeiro projeto real: o `INDEX.md` — esse sim
    atualizado — passou a apontar para um arquivo que o projeto nunca receberia, e o portão
    do projeto ficou vermelho com "wikilink sem destino" logo depois de atualizar.

    Este teste fecha a classe: todo arquivo que o kit entrega a um projeto novo tem de ser
    OU processo (o kit atualiza, `DO_KIT`) OU verdade do projeto (`NUNCA`). Não existe
    terceira gaveta, e ficar fora das duas é como o arquivo desaparece na atualização."""

    def test_todo_arquivo_entregue_e_processo_ou_verdade_do_projeto(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("np", KIT / "scripts/new_project.py")
        np = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(np)

        orfaos = []
        for origem in sorted(KIT.rglob("*")):
            if origem.is_dir():
                continue
            rel = origem.relative_to(KIT).as_posix()
            if any(p in np.EXCLUIR_PASTAS for p in Path(rel).parts):
                continue
            if rel in np.EXCLUIR_ARQUIVOS or origem.name.endswith(np.EXCLUIR_SUFIXOS):
                continue
            coberto = any(rel == d or rel.startswith(d) for d in np.DO_KIT + np.NUNCA)
            if not coberto:
                orfaos.append(rel)
        self.assertEqual(orfaos, [],
                         "arquivo entregue a projeto novo e invisível para o --upgrade "
                         "(acrescente a DO_KIT se é processo, ou a NUNCA se é do projeto): "
                         + ", ".join(orfaos))


class TestCustomizacaoPreservada(unittest.TestCase):
    """A atualização NÃO pode sobrescrever arquivo do kit que o dono editou.

    Este teste existe porque a primeira versão do `--upgrade` fazia exatamente isso, em
    silêncio, e só foi descoberto ao comparar com outro kit que resolve customização com
    arquivo de override. O manifesto de impressões é a resposta: sem ele não há como
    distinguir "arquivo do kit intocado" de "o dono adaptou isto ao time dele"."""

    def test_arquivo_customizado_nao_e_sobrescrito(self):
        with area_temporaria() as tmp:
            kit = montar_kit(Path(tmp) / "kit")
            projeto = Path(tmp) / "projeto"
            rodar_script("new_project.py", str(projeto), "--nome", "App", cwd=kit)
            docs = vault_de(projeto)
            self.assertTrue((docs / ".kit-manifest").exists(), "manifesto não foi gravado")

            alvo = docs / "b_process/skills/planner/SKILL.md"
            alvo.write_text(alvo.read_text(encoding="utf-8") + "\n## Regra local do time\n",
                            encoding="utf-8")
            intocado = docs / "b_process/a_roadmap.md"
            git(projeto, "init", "-q")
            git(projeto, "add", "-A")
            git(projeto, *GIT_ID, "commit", "-qm", "customizacao")

            # o kit mexe nos DOIS arquivos
            for arquivo in ("b_process/skills/planner/SKILL.md", "b_process/a_roadmap.md"):
                p = kit / arquivo
                p.write_text(p.read_text(encoding="utf-8") + "\n<!-- v10 -->\n", encoding="utf-8")

            r = rodar_script("new_project.py", str(projeto), "--upgrade", cwd=kit)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("PROTEGIDO", r.stdout)

            self.assertIn("Regra local do time", alvo.read_text(encoding="utf-8"),
                          "a atualização apagou a customização do dono")
            self.assertNotIn("v10", alvo.read_text(encoding="utf-8"),
                             "sobrescreveu arquivo customizado sem --forcar")
            self.assertIn("v10", intocado.read_text(encoding="utf-8"),
                          "arquivo intocado deixou de ser atualizado")

    def test_forcar_traz_a_versao_do_kit(self):
        with area_temporaria() as tmp:
            kit = montar_kit(Path(tmp) / "kit")
            projeto = Path(tmp) / "projeto"
            rodar_script("new_project.py", str(projeto), "--nome", "App", cwd=kit)
            docs = vault_de(projeto)
            alvo = docs / "b_process/skills/planner/SKILL.md"
            alvo.write_text(alvo.read_text(encoding="utf-8") + "\nlocal\n", encoding="utf-8")
            p = kit / "b_process/skills/planner/SKILL.md"
            p.write_text(p.read_text(encoding="utf-8") + "\n<!-- v10 -->\n", encoding="utf-8")
            git(projeto, "init", "-q")
            git(projeto, "add", "-A")
            git(projeto, *GIT_ID, "commit", "-qm", "x")

            r = rodar_script("new_project.py", str(projeto), "--upgrade", "--forcar", cwd=kit)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("v10", alvo.read_text(encoding="utf-8"))


class TestCoberturaModuloTarefa(unittest.TestCase):
    """`### M1 —` no PLANO cruzado com `**Módulo:** M1` no BACKLOG. A ideia é do BMAD
    (toda tarefa marcada com o critério que atende); o valor aqui é que a marcação torna
    determinística uma checagem que antes só existia no olho de quem revisava."""

    def preparar(self, tmp, modulos: str, tarefas: str):
        repo = montar_kit(Path(tmp) / "repo")
        plano = repo / "a_context/b_plan.md"
        plano.write_text(plano.read_text(encoding="utf-8") + "\n" + modulos, encoding="utf-8")
        bl = repo / "b_process/c_backlog.md"
        bl.write_text(bl.read_text(encoding="utf-8") + "\n" + tarefas, encoding="utf-8")
        return repo

    def test_modulo_sem_tarefa_avisa(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "### M7 — cobranca\n- **Recebe:** x\n", "")
            saida = rodar_check(repo).stdout
            self.assertIn("Módulo do PLANO sem tarefa", saida)
            self.assertIn("M7", saida)

    def test_modulo_com_tarefa_nao_avisa(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "### M7 — cobranca\n- **Recebe:** x\n",
                                 "- [ ] T-07 — cobrar · **Módulo:** M7 · **Portão:** teste verde\n")
            self.assertNotIn("Módulo do PLANO sem tarefa", rodar_check(repo).stdout)

    def test_tarefa_apontando_modulo_inexistente_reprova(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "### M7 — cobranca\n- **Recebe:** x\n",
                                 "- [ ] T-08 — algo · **Módulo:** M42 · **Portão:** x\n")
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("módulo inexistente", r.stdout)

    def test_template_nao_preenchido_nao_dispara(self):
        """`### M1 — <nome>` é plano em branco, não lacuna. Aviso falso ensina a ignorar
        aviso — o vício que o kit condena."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.assertNotIn("Módulo do PLANO sem tarefa", rodar_check(repo).stdout)


class TestEsquemaDasSkills(unittest.TestCase):
    """As 24 skills seguiam o mesmo esquema por HÁBITO, não por regra — e hábito não
    sobrevive a uma skill nova escrita com pressa. A ideia da seção de limites vem do
    SuperClaude (`## Boundaries` — Will / Will Not); a diferença é que aqui ela é cobrada.

    Medição que motivou: 21/24 das descriptions daqui já diziam quando NÃO escolher a
    skill (0/20 lá); 0/24 diziam o que a skill não faz depois de escolhida (15/20 lá).
    Cada kit tinha metade."""

    def test_toda_skill_entregue_segue_o_esquema(self):
        for p in sorted((KIT / "b_process/skills").glob("*/SKILL.md")):
            t = p.read_text(encoding="utf-8")
            for secao in ("## Contexto que você recebe", "## Limites", "## Saída"):
                self.assertIn(secao, t, f"{p.parent.name} sem '{secao}'")
            self.assertIn("Não use", t[:900],
                          f"{p.parent.name}: description sem fronteira negativa")

    def test_skill_sem_limites_reprova(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            nova = repo / "b_process/skills/skill-torta/SKILL.md"
            nova.parent.mkdir(parents=True, exist_ok=True)
            nova.write_text("---\nname: skill-torta\ndescription: faz coisas. Não use para outras.\n---\n"
                            "# Torta\n## Contexto que você recebe\nx\n## Saída\ny\n", encoding="utf-8")
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("## Limites", r.stdout)

    def test_description_sem_fronteira_negativa_avisa(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            nova = repo / "b_process/skills/skill-vaga/SKILL.md"
            nova.parent.mkdir(parents=True, exist_ok=True)
            nova.write_text("---\nname: skill-vaga\ndescription: faz coisas boas.\n---\n"
                            "# Vaga\n## Contexto que você recebe\nx\n## Limites\nz\n## Saída\ny\n",
                            encoding="utf-8")
            self.assertIn("fronteira negativa", rodar_check(repo).stdout)


class TestHonestidadeDeclarada(unittest.TestCase):
    """A frase mais distintiva do kit é a que declara a própria cobertura: "N itens de
    checklist, o script julga M". Um agente externo a citou como a força única do kit —
    e ela estava **errada**: dizia 188/18 quando o real era 277/23. A auto-declaração de
    honestidade tinha envelhecido em silêncio, que é a divergência doc × código que o
    próprio kit classifica como achado de QA.

    Este teste existe para que ela não envelheça de novo. Fonte da verdade: os arquivos."""

    def contar(self):
        checklist = len(re.findall(r"^- \[ \]", (KIT / "b_process/b_checklist.md")
                                   .read_text(encoding="utf-8"), re.M))
        skills = sum(len(re.findall(r"^- \[ \]", p.read_text(encoding="utf-8"), re.M))
                     for p in (KIT / "b_process/skills").glob("*/SKILL.md"))
        cab = (KIT / "scripts/check.py").read_text(encoding="utf-8").split('"""')[1]
        # O bloco FALHAS numera em DUAS COLUNAS na mesma linha ("1. ...    7. ..."), então
        # contar por início de linha devolve metade. Conta os IDs distintos do bloco.
        bloco = cab.split("FALHAS", 1)[1].split("AVISOS", 1)[0]
        # `\S` e não `[A-Z…]`: o item "9. .gitignore sem cobertura" começa com ponto, e
        # a classe restrita o engolia — a contagem dava 13 num bloco de 14. Teste que
        # conta errado é pior que teste ausente: ele autoriza o número errado.
        falhas = len({int(n) for n in re.findall(r"\b(\d{1,2})\.\s+\S", bloco)})
        # Avisos são lista em prosa separada por "·" — contáveis do mesmo jeito.
        bloco_av = cab.split("AVISOS", 1)[1].split("\n\n", 1)[0]
        avisos = len([x for x in bloco_av.split("·") if x.strip()])
        return checklist, skills, falhas, avisos

    def test_readme_declara_os_numeros_reais(self):
        checklist, skills, falhas, avisos = self.contar()
        readme = (KIT / "README.md").read_text(encoding="utf-8")
        m = re.search(r"\*\*(\d+)\*\* itens de checklist \((\d+) no .*?\+ (\d+) nos", readme)
        self.assertIsNotNone(m, "a frase de cobertura sumiu do README")
        decl_total, decl_check, decl_skills = (int(g) for g in m.groups())
        self.assertEqual((decl_check, decl_skills), (checklist, skills),
                         f"README diz {decl_check}+{decl_skills}; real é {checklist}+{skills}")
        self.assertEqual(decl_total, checklist + skills, "o total declarado não soma")

        # A capa da apresentação declarava os MESMOS números à mão — "14 falhas e 16 avisos
        # · 57 testes" — e envelhecia sozinha, como o "188 itens, 18 julgados" já tinha
        # envelhecido. A primeira correção foi um teste VIGIANDO a cópia, e estava errada:
        # a checagem 3 deste kit se chama FONTE ÚNICA, e o mesmo dado em dois arquivos não
        # vira verdade por ganhar um guarda — vira verdade quando existe um lugar só.
        # Agora a capa LÊ do check.py, e o que este teste guarda é a AUSÊNCIA do número
        # digitado. O docstring da capa fica de fora: ele cita o erro antigo de propósito.
        capa = KIT / "docs/gerar_apresentacao.py"
        if capa.exists():
            corpo_capa = capa.read_text(encoding="utf-8").split('"""', 2)[-1]
            self.assertIsNone(
                re.search(r"\d+ falhas e \d+ avisos", corpo_capa),
                "a capa voltou a digitar os números do portão em vez de lê-los do check.py")

        m2 = re.search(r"julga \*\*(\d+)\*\* deles \((\d+) reprovam o commit, (\d+) avisam\)", readme)
        self.assertIsNotNone(m2, "a frase de cobertura do script sumiu do README")
        decl_soma, decl_falhas, decl_avisos = (int(g) for g in m2.groups())
        self.assertEqual(decl_avisos, avisos,
                         f"README diz {decl_avisos} avisos; o cabeçalho lista {avisos}")
        self.assertEqual(decl_soma, falhas + avisos, "o total julgado não soma")
        self.assertEqual(decl_falhas, falhas,
                         f"README diz {decl_falhas} falhas; o cabeçalho do check.py numera {falhas}")

        # A PORCENTAGEM também. Ela ficou de fora quando este teste nasceu — o regex parava
        # onde a prosa começava — e envelheceu na primeira vez que alguém mexeu nas contagens:
        # o README passou a dizer "cerca de 9%" com 30/284 = 10,6% no disco, no MESMO dia em que
        # o kit ganhou um aviso cujo propósito é "número que um script calcula não se mantém à
        # mão". Terceira ocorrência da espécie do QA-14/QA-15, e desta vez dentro da frase que
        # existe para não apodrecer. "Cerca de" arredonda; não autoriza divergir.
        m3 = re.search(r"— cerca de (\d+)%", readme)
        self.assertIsNotNone(m3, "a porcentagem de cobertura sumiu do README")
        esperado = round(100 * (falhas + avisos) / (checklist + skills))
        self.assertEqual(int(m3.group(1)), esperado,
                         f"README diz cerca de {m3.group(1)}%; "
                         f"{falhas + avisos}/{checklist + skills} arredonda para {esperado}%")


class TestDocumentacaoNaoMente(unittest.TestCase):
    """Números e nomes que a documentação afirma sobre si mesma, contados dos arquivos.

    Motivo: numa única sessão, uma skill nova entrou e QUATRO documentos continuaram
    dizendo "23 agentes"; a mesma skill se chamava "Fase 1b" enquanto o roteiro a numerava
    como "1c". Nenhum portão pegou — porque o `check.py` verifica que os LINKS resolvem,
    não que as AFIRMAÇÕES conferem. Doc que mente sobre si é a divergência doc × código
    que o próprio kit classifica como achado de QA."""

    def test_contagem_de_agentes_bate_em_toda_documentacao(self):
        real = len(list((KIT / "b_process/skills").glob("*/SKILL.md")))
        for rel in ("INDEX.md", "README.md", "b_process/skills/README.md",
                    "b_process/f_glossary_and_primer.md"):
            texto = (KIT / rel).read_text(encoding="utf-8")
            for n in {int(x) for x in re.findall(r"\b(\d{1,3})\s+agentes\b", texto)}:
                self.assertEqual(n, real, f"{rel} afirma {n} agentes; existem {real}")

    def test_scripts_citados_na_doc_existem(self):
        reais = {p.name for p in (KIT / "scripts").glob("*.py")}
        for p in KIT.rglob("*.md"):
            if "docs" in p.parts or p.name == "b_kit_changelog.md":
                continue  # auditoria histórica descreve versões antigas do kit, de propósito
            for citado in set(re.findall(r"scripts/([a-z_]+\.py)", p.read_text(encoding="utf-8"))):
                self.assertIn(citado, reais,
                              f"{p.relative_to(KIT)} cita scripts/{citado}, que não existe")

    def test_toda_skill_aparece_no_indice_de_skills(self):
        indice = (KIT / "b_process/skills/README.md").read_text(encoding="utf-8")
        for p in sorted((KIT / "b_process/skills").glob("*/SKILL.md")):
            self.assertIn(p.parent.name, indice,
                          f"a skill {p.parent.name} não está no índice — ninguém a encontra")


class TestCanarioDosTemplates(unittest.TestCase):
    """Canário: o `check.py` lê os templates por REGEX, então uma edição cosmética num
    template faz a checagem parar de checar — em silêncio, com o verde continuando a sair.
    É a mesma classe do QA-03 (mensagem que não corresponde ao que rodou), só que na
    entrada em vez da saída.

    Cada teste aqui injeta uma violação REAL nos templates COMO ELES SÃO ENTREGUES e exige
    que o portão a pegue. Se alguém reformatar um cabeçalho e o parser deixar de casar, a
    violação passa e o teste falha — que é exatamente o aviso que faltava.

    Testa o RESULTADO, não o padrão: um teste que só confere se o regex está escrito de
    certa forma quebra junto com a implementação e não protege nada."""

    def anexar(self, repo: Path, rel: str, texto: str):
        p = repo / rel
        p.write_text(p.read_text(encoding="utf-8") + texto, encoding="utf-8")

    def test_limite_de_wip_ainda_e_cobrado_no_template_entregue(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            # 3 itens sob o cabeçalho "Em andamento" que o template declara com máx 1
            self.anexar(repo, "b_process/c_backlog.md", "")
            p = repo / "b_process/c_backlog.md"
            p.write_text(p.read_text(encoding="utf-8").replace(
                "- [ ] T-00 — <a tarefa do momento>",
                "- [ ] T-10 — a\n- [ ] T-11 — b\n- [ ] T-12 — c"), encoding="utf-8")
            r = rodar_check(repo)
            self.assertIn("limite declarado", r.stdout,
                          "o parser de WIP não reconhece mais o cabeçalho do template entregue")

    def test_modulo_e_reconhecido_com_travessao_e_com_dois_pontos(self):
        for separador in ("—", ":", "-"):
            with self.subTest(separador=separador), area_temporaria() as tmp:
                repo = montar_kit(Path(tmp) / "repo")
                self.anexar(repo, "a_context/b_plan.md", f"\n### M7 {separador} cobranca\n- **Recebe:** x\n")
                self.assertIn("M7", rodar_check(repo).stdout,
                              f"módulo com separador {separador!r} deixou de ser reconhecido")

    def test_marcacao_de_modulo_reconhecida_nas_duas_grafias(self):
        for grafia in ("**Módulo:** M7", "**Módulo**: M7", "**Modulo:** M7"):
            with self.subTest(grafia=grafia), area_temporaria() as tmp:
                repo = montar_kit(Path(tmp) / "repo")
                self.anexar(repo, "a_context/b_plan.md", "\n### M7 — cobranca\n- **Recebe:** x\n")
                self.anexar(repo, "b_process/c_backlog.md", f"\n- [ ] T-50 — x · {grafia} · **Portão:** y\n")
                self.assertNotIn("Módulo do PLANO sem tarefa", rodar_check(repo).stdout,
                                 f"a grafia {grafia!r} não foi reconhecida como cobertura")

    def test_limite_declarado_e_lido_nas_variacoes_de_escrita(self):
        """`máx 3` e `limite 3` são a mesma declaração. Antes, só a primeira era lida e a
        segunda caía no default 1 — o script cobrava 1 e AINDA dizia "limite declarado é 1".
        Afirmar ter lido o que não leu é o defeito que este arquivo persegue."""
        for cabecalho in ("## Em andamento (máx 3)", "## Em andamento — limite 3",
                          "## Em andamento (max 3)", "## Em andamento ≤ 3"):
            with self.subTest(cabecalho=cabecalho), area_temporaria() as tmp:
                repo = montar_kit(Path(tmp) / "repo")
                p = repo / "b_process/c_backlog.md"
                t = re.sub(r"^## Em andamento.*$", cabecalho, p.read_text(encoding="utf-8"), count=1, flags=re.M)
                p.write_text(t.replace("- [ ] T-00 — <a tarefa do momento>",
                                       "- [ ] T-10 — a\n- [ ] T-11 — b"), encoding="utf-8")
                # 2 itens sob limite 3: não pode reprovar
                self.assertNotIn("limite declarado", rodar_check(repo).stdout,
                                 f"{cabecalho!r} não foi lido; o limite caiu no default")

    def test_id_fantasma_ainda_e_pego_no_template_entregue(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.anexar(repo, "INDEX.md", "\n\nVer D-77 para o detalhe.\n")
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("D-77", r.stdout,
                          "o parser da tabela de DECISIONS não casa mais com o template entregue")


class TestTodaChecagemTemIsca(unittest.TestCase):
    """Uma isca canônica por FALHA numerada: o caso concreto que aquela checagem existe
    para pegar. Se a checagem emudecer, a isca passa e este teste reprova.

    QA-14, medido no primeiro projeto real construído com o kit: a checagem 10 filtrava a
    nota por `sem_codigo`, que descarta o trecho entre crases — e a casa escreve `D-13`,
    não D-13. Das 341 citações de ID daquele projeto, 300 estavam entre crases: o portão
    enxergava 12% e imprimia verde sobre o resto. Havia canário para esta checagem, e ele
    escrevia `D-77` SEM crases — passava, e a cegueira sobreviveu inclusive a uma auditoria
    externa que citou o portão como ponto forte.

    A lição não é "conserte a checagem 10", é que uma checagem pode parar de checar sem que
    nada grite. `test_toda_falha_numerada_tem_isca` fecha a classe inteira: FALHA nova sem
    isca reprova aqui, e isca que deixa de pegar o próprio caso reprova aqui.

    Testa o RESULTADO (reprovou? disse o quê?), nunca o regex: teste que espelha a
    implementação quebra junto com ela e não protege nada.
    """

    def anexar(self, repo: Path, rel: str, texto: str):
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        antes = p.read_text(encoding="utf-8") if p.exists() else ""
        p.write_text(antes + texto, encoding="utf-8")

    def trocar(self, repo: Path, rel: str, de: str, para: str):
        p = repo / rel
        t = p.read_text(encoding="utf-8")
        self.assertIn(de, t, f"{rel}: a âncora da isca sumiu do template — a isca deixou de sabotar")
        p.write_text(t.replace(de, para, 1), encoding="utf-8")

    def escrever_skill(self, repo: Path, nome: str, corpo: str):
        (repo / "b_process/skills" / nome).mkdir(parents=True, exist_ok=True)
        (repo / "b_process/skills" / nome / "SKILL.md").write_text(corpo, encoding="utf-8")

    # ---- as iscas, uma por FALHA numerada no cabeçalho do check.py ----------
    def iscas(self):
        SEC = "## Contexto que você recebe\nx\n## Limites\ny\n## Saída\nz\n"
        return {
            1: (lambda r: self.anexar(r, "a_context/a_context_source.md", "\n" + "x" * 4100),
                "orçamento: 4.000"),
            2: (lambda r: self.anexar(r, "a_context/c_decisions.md", "\n" + "y" * 12100),
                "acima de 12.000"),
            3: (lambda r: self.anexar(r, "e_qa/c_backlog.md", "---\ntags: [x]\n---\n# copia\n"),
                "duplicado"),
            4: (lambda r: self.trocar(r, "b_process/c_backlog.md",
                                      "- [ ] T-00 — <a tarefa do momento>",
                                      "- [ ] T-10 — a\n- [ ] T-11 — b\n- [ ] T-12 — c"),
                "limite declarado"),
            5: (lambda r: self.anexar(r, "lixo.bak", "sobra de editor\n"),
                "Cruft"),
            6: (lambda r: self.escrever_skill(r, "skill-muda",
                                              "---\nname: skill-muda\n---\n# Muda\n" + SEC),
                "sem 'description:'"),
            7: (lambda r: self.anexar(r, "INDEX.md", "\n\nVer [[destino-que-nao-existe-mesmo]].\n"),
                "sem destino"),
            8: (lambda r: self.anexar(r, "vazou.txt", ISCA + "\n"),
                "segredo versionado"),
            # Sobrescreve o arquivo inteiro: trocar só ".env" deixa ".env.local", que
            # CONTÉM ".env", e a isca não sabotava nada (falso verde, achado ao escrever
            # esta classe). Limite conhecido e NÃO consertado aqui (regra 4): a checagem 9
            # é `substring`, então um .gitignore só de comentários citando os padrões passa.
            # QA-15: a isca é um .gitignore que só COMENTA os padrões. A versão anterior
            # ("node_modules/") provava menos: a checagem era `substring`, então um
            # comentário citando `.env` a satisfazia sem ignorar nada.
            9: (lambda r: (r / ".gitignore").write_text(
                    "# nunca commite .env, *.pem, *.key, id_rsa, credentials.json, *.p12\nnode_modules/\n",
                    encoding="utf-8"),
                ".gitignore sem cobertura"),
            # A isca da 10 escreve o ID ENTRE CRASES de propósito: é como a casa escreve,
            # e era exatamente o caso que passava. Sem crases o teste não prova nada.
            10: (lambda r: self.anexar(r, "INDEX.md", "\n\nVer `D-77` para o detalhe.\n"),
                 "D-77"),
            11: (lambda r: self.anexar(r, "a_context/c_decisions.md",
                                       "\n| D-01 | <data> | ADOTADO | linha repetida | |\n"),
                 "ID duplicado"),
            12: (lambda r: (self.trocar(r, "b_process/c_backlog.md",
                                        "- [ ] T-00 — <a tarefa do momento>", "- [ ] T-42 — a"),
                            self.trocar(r, "a_context/a_context_source.md",
                                        "**Em andamento (máx 1):** <a única tarefa ativa>",
                                        "**Em andamento (máx 1):** T-99 outra coisa")),
                 "'Em andamento' divergente"),
            13: (lambda r: (self.anexar(r, "a_context/b_plan.md", "\n### M7 — cobranca\n- **Recebe:** x\n"),
                            self.anexar(r, "b_process/c_backlog.md",
                                        "\n- [ ] T-80 — x · **Módulo:** M42 · **Portão:** y\n")),
                 "módulo inexistente"),
            14: (lambda r: self.escrever_skill(
                    r, "skill-sem-limites",
                    "---\nname: skill-sem-limites\ndescription: faz coisas. Não use para outras.\n---\n"
                    "# Sem limites\n## Contexto que você recebe\nx\n## Saída\nz\n"),
                 "## Limites"),
            15: (lambda r: self.anexar(
                    r, "b_process/c_backlog.md",
                    "\n## Feito\n" + "".join(
                        f"- [x] T-{i:02d} — tarefa {i} · **Módulo:** M1\n  {'peso ' * 40}\n"
                        for i in range(60))),
                 "c_backlog.md com"),
            # A isca da 16 escreve a CONFIG, que é o caminho real desde o v13.10: o projeto
            # declara o teto num dado versionado em vez de editar o portão. Sabotar o
            # `check.py` provaria a mesma coisa por um caminho que o kit desencoraja.
            16: (lambda r: (r / ".kit-config.json").write_text(
                    '{"tetos": {"a_context/c_decisions.md": 20000}}', encoding="utf-8"),
                 "sobe em silêncio"),
            # A 17 é a 1/2/15 aplicada a um registro que o KIT não conhece: quem o declarou
            # paga orçamento por ele. Sem isto, mover uma tabela para arquivo próprio seria
            # a forma legal de fugir de todo teto — e foi assim que um projeto real chegou
            # a um backlog de 191 mil caracteres.
            17: (lambda r: (
                    (r / ".kit-config.json").write_text(
                        '{"registros": ["a_context/d_qa.md"], "tetos": {"a_context/d_qa.md": 500}}',
                        encoding="utf-8"),
                    (r / "a_context/d_qa.md").write_text(
                        "---\ntags: [qa]\n---\n# QA\n" + "z" * 600, encoding="utf-8"),
                    self.anexar(r, "a_context/c_decisions.md",
                                "| D-50 | 2026-08-27 | ADOTADO | d_qa.md como registro "
                                "proprio dos achados | tabela estourava o DECISIONS |\n")),
                 "orçamento declarado"),
            # A 18 é inerte sem a chave, então a isca declara a chave E a viola. Só
            # `linha_max` na CONFIG: acrescentar um teto aqui reprovaria pela 16 e o
            # `assertIn` passaria pelo motivo errado.
            18: (lambda r: (
                    (r / ".kit-config.json").write_text(
                        '{"linha_max": {"limite": 120}}', encoding="utf-8"),
                    self.anexar(r, "a_context/c_decisions.md",
                                "| D-60 | 2026-08-27 | ADOTADO | decisao curta | "
                                + "evidencia " * 30 + "|\n")),
                 "Linha de registro acima de"),
            # A 19 ANEXA ao registro uma linha com hash que não é o do arquivo: é o estado exato
            # de "alguém editou o congelado depois de congelar", sem rodar o congelar.py dentro
            # da isca. Anexar, e não sobrescrever: sobrescrever acordaria também a checagem de
            # append-only, e a isca reprovaria por dois motivos. O arquivo mora em d_history/.
            19: (lambda r: (
                    (r / "d_history/criterio_isca.md").write_text(
                        "---\ntags: [criterio]\n---\n# Criterio\nlimiar: 2 de 3\n", encoding="utf-8"),
                    self.anexar(r, ".kit-congelados",
                                "CONGELADO | " + "0" * 64 + " | 2026-09-10 | d_history/criterio_isca.md\n")),
                 "congelado editado"),
        }

    def test_toda_falha_numerada_tem_isca(self):
        """O portão do portão: FALHA nova no cabeçalho sem isca aqui reprova."""
        cab = (KIT / "scripts/check.py").read_text(encoding="utf-8").split('"""')[1]
        bloco = cab.split("FALHAS", 1)[1].split("AVISOS", 1)[0]
        numeradas = {int(n) for n in re.findall(r"\b(\d{1,2})\.\s+\S", bloco)}
        self.assertEqual(
            numeradas, set(self.iscas()),
            "toda FALHA numerada precisa da isca que prova que ela ainda pega o próprio caso "
            f"(cabeçalho: {sorted(numeradas)}; iscas: {sorted(self.iscas())})")

    def test_cada_isca_reprova(self):
        for numero, (sabotar, trecho) in sorted(self.iscas().items()):
            with self.subTest(falha=numero), area_temporaria() as tmp:
                repo = montar_kit(Path(tmp) / "repo")
                sabotar(repo)
                r = rodar_check(repo)
                self.assertEqual(r.returncode, 1,
                                 f"FALHA {numero}: a isca passou — a checagem emudeceu.\n{r.stdout}")
                self.assertIn(trecho, r.stdout,
                              f"FALHA {numero}: reprovou, mas por outro motivo.\n{r.stdout}")

    def test_teto_elevado_pela_config_COM_registro_passa(self):
        """A contraprova da 16, e ela importa mais que a isca: a checagem não proíbe subir
        o teto — proíbe subir calado. Sem este teste, a forma mais fácil de "passar" na 16
        seria proibir a elevação, o que quebraria todo projeto grande e ensinaria o dono a
        rodar o portão com --no-verify (a checagem que emudece, vista do outro lado)."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            (repo / ".kit-config.json").write_text(
                '{"tetos": {"a_context/c_decisions.md": 20000}}', encoding="utf-8")
            self.anexar(repo, "a_context/c_decisions.md",
                        "| D-44 | 2026-08-24 | ADOTADO | teto de a_context/c_decisions.md "
                        "para 20.000 | arquivamento esgotado: todo D-NN vivo é citado |\n")
            r = rodar_check(repo)
            self.assertNotIn("sobe em silêncio", r.stdout,
                             f"a elevação estava registrada e mesmo assim reprovou:\n{r.stdout}")

    def test_kit_entregue_passa_sem_isca(self):
        """Contraprova: sem sabotagem, o portão não pode reprovar. Sem isto, uma isca que
        reprova por acidente (e não pelo que ela sabota) passaria despercebida."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 0, f"o kit entregue reprova sozinho:\n{r.stdout}")


class TestChavesDaConfig(unittest.TestCase):
    """As três chaves que o v13.12 acrescentou à CONFIG, e a razão de existirem.

    Um projeto real tinha escrito as três regras no PRÓPRIO `check.py`, porque o kit não
    as oferecia. O `--upgrade` do v13.10 devolveu o portão do kit e as três sumiram sem
    uma linha de aviso — o projeto passou a medir a si mesmo com uma régua que não era
    mais a régua, e não havia como saber. O que estes testes protegem não é a feature: é
    a propriedade de que regra declarada é regra cobrada, e chave que o kit não entende
    reprova em vez de sumir.
    """

    def config(self, repo: Path, texto: str):
        (repo / ".kit-config.json").write_text(texto, encoding="utf-8")

    def anexar(self, repo: Path, rel: str, texto: str):
        p = repo / rel
        p.write_text(p.read_text(encoding="utf-8") + texto, encoding="utf-8")

    # ---- chave desconhecida -------------------------------------------------
    def test_chave_desconhecida_reprova(self):
        """O defeito que originou as três: a chave que some calada."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.config(repo, '{"linha_maxima": {"limite": 400}}')
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 1, f"chave errada passou calada:\n{r.stdout}")
            self.assertIn("linha_maxima", r.stdout)

    def test_config_so_com_chaves_validas_nao_reclama(self):
        """Contraprova: a checagem não pode reprovar quem escreveu certo."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.config(repo, '{"medir_sem_padding": true, "candidatas": "nao_citadas"}')
            self.assertNotIn("nao conhece", rodar_check(repo).stdout)

    # ---- medir_sem_padding --------------------------------------------------
    def tabela_alinhada(self, colunas=2, linhas=40, largura=90):
        """Tabela cujo conteúdo é curto e cujo PADDING é grande — é a forma que um
        formatador de Markdown produz ao alinhar colunas."""
        return "".join(
            "| " + " | ".join("x".ljust(largura) for _ in range(colunas)) + " |\n"
            for _ in range(linhas))

    def test_sem_a_chave_o_padding_conta(self):
        """O padrão do kit não muda: quem não declara continua medido por `len()`."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.anexar(repo, "a_context/c_decisions.md", self.tabela_alinhada(linhas=80))
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 1, f"o padding não contou sem a chave:\n{r.stdout}")
            self.assertIn("acima de 12.000", r.stdout)

    def test_com_a_chave_o_mesmo_arquivo_cabe(self):
        """O mesmo conteúdo, o mesmo teto: só o alinhamento sai da conta. É a prova de
        que a régua mede o texto e não o formatador de quem salvou por último."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.anexar(repo, "a_context/c_decisions.md", self.tabela_alinhada(linhas=80))
            self.config(repo, '{"medir_sem_padding": true}')
            r = rodar_check(repo)
            self.assertNotIn("acima de 12.000", r.stdout)

    def test_a_chave_nao_e_desconto_geral(self):
        """Ela tira o padding, não o conteúdo: texto de verdade acima do teto reprova
        com a chave ligada. Sem este teste, `medir_sem_padding` poderia virar a forma
        legal de fugir do orçamento — que é o oposto do que ela existe para fazer."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.config(repo, '{"medir_sem_padding": true}')
            self.anexar(repo, "a_context/c_decisions.md", "\n" + "y" * 12100)
            self.assertIn("acima de 12.000", rodar_check(repo).stdout)

    # ---- linha_max ----------------------------------------------------------
    def linha(self, ident, tamanho):
        return f"| {ident} | 2026-08-27 | ADOTADO | curta | " + "z" * tamanho + " |\n"

    def test_sem_a_chave_linha_longa_passa(self):
        """Inerte por padrão: o kit não tem opinião sobre o tamanho da linha de ninguém."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.anexar(repo, "a_context/c_decisions.md", self.linha("D-60", 900))
            self.assertNotIn("Linha de registro acima de", rodar_check(repo).stdout)

    def test_isenta_congelada_nao_reprova(self):
        """A contraprova que importa mais que a isca: registro append-only tem linhas que
        ninguém PODE reescrever, e checagem vermelha em linha inconsertável ensina a
        ignorar o script inteiro."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.config(repo, '{"linha_max": {"limite": 120, "isentas": ["D-60"]}}')
            self.anexar(repo, "a_context/c_decisions.md", self.linha("D-60", 900))
            r = rodar_check(repo)
            self.assertNotIn("Linha de registro acima de", r.stdout)

    def test_isencao_e_por_ID_e_nao_perdoa_a_vizinha(self):
        """Isenção que virasse janela móvel apagaria a regra em silêncio."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.config(repo, '{"linha_max": {"limite": 120, "isentas": ["D-60"]}}')
            self.anexar(repo, "a_context/c_decisions.md",
                        self.linha("D-60", 900) + self.linha("D-61", 900))
            saida = rodar_check(repo).stdout
            self.assertIn("D-61", saida)
            self.assertNotIn("D-60 (", saida)

    def test_limite_invalido_reprova_em_vez_de_desligar(self):
        """Valor errado não pode virar "regra desligada": é o falso verde de novo."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.config(repo, '{"linha_max": {"limite": "400"}}')
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 1)
            self.assertIn("linha_max.limite", r.stdout)

    # ---- candidatas ---------------------------------------------------------
    def encher(self, repo: Path, ate=0.95):
        """Leva o DECISIONS ao aviso de 90% sem estourar o teto — é lá que a lista de
        candidatas é impressa."""
        alvo = int(12000 * ate)
        p = repo / "a_context/c_decisions.md"
        atual = p.read_text(encoding="utf-8")
        p.write_text(atual + "\n" + "w" * max(0, alvo - len(atual)), encoding="utf-8")

    def test_padrao_continua_apontando_as_mais_antigas(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.anexar(repo, "a_context/c_decisions.md",
                        "| D-60 | 2026-08-27 | ADOTADO | uma decisao | evidencia |\n")
            self.encher(repo)
            self.assertIn("D-60", rodar_check(repo).stdout)

    def test_nao_citadas_ignora_o_ID_que_algum_md_vivo_cita(self):
        """O caso que motivou a chave: num projeto que preserva as REJEITADAS de
        propósito, o critério antigo apontava justamente para elas — a lista-morta que a
        fase de evolução varre sem abrir o arquivo."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.config(repo, '{"candidatas": "nao_citadas"}')
            self.anexar(repo, "a_context/c_decisions.md",
                        "| D-60 | 2026-08-27 | REJEITADO | nao repetir isto | o numero que matou |\n")
            self.anexar(repo, "INDEX.md", "\n\nA razao esta em `D-60`.\n")
            self.encher(repo)
            saida = rodar_check(repo).stdout
            # O que se prova e a AUSENCIA: o ID citado sai da lista. Que o template tenha
            # outros IDs nao citados e ruido do fixture, nao do criterio.
            self.assertIn("Candidatas:", saida)
            self.assertNotIn("D-60", saida)

    def test_nao_citadas_ainda_aponta_o_ID_que_ninguem_cita(self):
        """Contraprova: a chave não pode virar "nunca aponta nada"."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.config(repo, '{"candidatas": "nao_citadas"}')
            self.anexar(repo, "a_context/c_decisions.md",
                        "| D-60 | 2026-08-27 | ADOTADO | ninguem me cita | x |\n")
            self.encher(repo)
            self.assertIn("D-60", rodar_check(repo).stdout)

    def test_valor_invalido_de_candidatas_reprova(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.config(repo, '{"candidatas": "as_feias"}')
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 1)
            self.assertIn("candidatas", r.stdout)


class TestInstrumentacaoDaSessao(unittest.TestCase):
    """Qual skill rodou na sessão. Sem este campo, "qual agente paga o próprio custo" só se
    responde por arqueologia de git — foi onde a primeira avaliação de campo do kit parou,
    e a resposta ficou em [suposto] por falta de um dado que custa uma linha.

    Mora no changelog porque nenhuma sessão o carrega: custo de contexto zero."""

    def entrada(self, repo: Path, texto: str):
        p = repo / "d_history/a_changelog.md"
        p.write_text(p.read_text(encoding="utf-8") + texto, encoding="utf-8")

    def test_entrada_datada_sem_skill_avisa(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.entrada(repo, "\n## [2026-08-13] — fez alguma coisa\n- Mudou X.\n")
            self.assertIn("Sessão sem skill declarada", rodar_check(repo).stdout)

    def test_entrada_com_skill_valida_cala(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.entrada(repo, "\n## [2026-08-13] — fez alguma coisa\n- **Skill:** planner\n- Mudou X.\n")
            self.assertNotIn("Sessão sem skill declarada", rodar_check(repo).stdout)

    def test_skill_declarada_que_nao_existe_avisa(self):
        """Campo que aceita qualquer texto vira campo que ninguém confere."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.entrada(repo, "\n## [2026-08-13] — x\n- **Skill:** agente-imaginario\n")
            saida = rodar_check(repo).stdout
            self.assertIn("agente-imaginario", saida)
            self.assertIn("não existe", saida)

    def test_template_sem_entrada_datada_nao_avisa(self):
        """O changelog entregue só tem `[Não lançado]` e o modelo comentado: aviso aqui
        seria falso, e aviso falso ensina a ignorar aviso."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.assertNotIn("Sessão sem skill declarada", rodar_check(repo).stdout)

    def test_o_template_de_fecho_pede_o_campo(self):
        """Se o template parar de pedir, o campo some dos projetos e o aviso vira ruído."""
        t = (KIT / "b_process/templates/c_session_closing.md").read_text(encoding="utf-8")
        self.assertIn("**Skill:**", t, "o template de fecho de sessão não pede mais a skill")


class TestNumeroDeclarado(unittest.TestCase):
    """Número que um script calcula não se mantém à mão. O kit já apanhou disso uma vez (a
    frase de cobertura dizia 188/18 com 277/23 no disco) e a correção valeu só para aquele
    número; aqui a lição vira classe."""

    def preparar(self, tmp, linha_estado: str):
        repo = montar_kit(Path(tmp) / "repo")
        p = repo / "a_context/a_context_source.md"
        p.write_text(p.read_text(encoding="utf-8") + "\n" + linha_estado + "\n", encoding="utf-8")
        return repo

    def test_ocupacao_declarada_errada_avisa(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "- **Registro:** 9.999/12.000")
            saida = rodar_check(repo).stdout
            self.assertIn("não se mantém à mão", saida)
            self.assertIn("9999/12000", saida.replace(".", ""))

    def test_ocupacao_declarada_certa_cala(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            real = len((repo / "a_context/c_decisions.md").read_text(encoding="utf-8"))
            p = repo / "a_context/a_context_source.md"
            p.write_text(p.read_text(encoding="utf-8") + f"\n- **Registro:** {real}/12.000\n",
                         encoding="utf-8")
            self.assertNotIn("não se mantém à mão", rodar_check(repo).stdout)

    def test_dois_arquivos_com_o_mesmo_teto_nao_se_atropelam(self):
        """DECISIONS e BACKLOG têm o mesmo teto padrão (12.000). Enquanto a tabela interna
        era indexada pelo NÚMERO do teto, um sobrescrevia o outro e o aviso comparava a
        ocupação declarada com o arquivo errado — acusando divergência onde não havia.
        Defeito cometido ao generalizar a tabela para tetos de projeto, pego por
        `test_ocupacao_declarada_certa_cala`. Este teste fixa a lição na forma geral:
        bater com QUALQUER arquivo daquele teto basta para calar."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            tamanho_backlog = len((repo / "b_process/c_backlog.md").read_text(encoding="utf-8"))
            p = repo / "a_context/a_context_source.md"
            p.write_text(p.read_text(encoding="utf-8") + f"\n- **Backlog:** {tamanho_backlog}/12.000\n",
                         encoding="utf-8")
            saida = rodar_check(repo).stdout
            self.assertNotIn("não se mantém à mão", saida,
                             f"o número bate com o BACKLOG e mesmo assim avisou:\n{saida}")

    def test_numero_alheio_ao_orcamento_nao_dispara(self):
        """`385/385` é suíte de teste, não orçamento. Aviso falso ensina a ignorar aviso."""
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "- **Suíte:** 385/385 verde")
            self.assertNotIn("não se mantém à mão", rodar_check(repo).stdout)


class TestFilaDoDono(unittest.TestCase):
    """Questão aberta que não aparece no CONTEXT não é feita a ninguém: o CONTEXT é o único
    arquivo que TODA sessão carrega. Medido no primeiro projeto real: três Q-NN abertas, duas
    com prazo estourado, e quem registrou o estouro foi uma sessão que por acaso olhou."""

    def preparar(self, tmp, linha_q: str, no_contexto: str):
        repo = montar_kit(Path(tmp) / "repo")
        d = repo / "a_context/c_decisions.md"
        d.write_text(d.read_text(encoding="utf-8") + "\n" + linha_q + "\n", encoding="utf-8")
        c = repo / "a_context/a_context_source.md"
        c.write_text(c.read_text(encoding="utf-8").replace(
            "- **Questões abertas:** <só os IDs Q-NN — detalhe no DECISIONS>",
            f"- **Questões abertas:** {no_contexto}"), encoding="utf-8")
        return repo

    def test_questao_aberta_ausente_do_contexto_avisa(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "| Q-42 | a pergunta | antes de T-10 |", "nenhuma")
            saida = rodar_check(repo).stdout
            self.assertIn("ausente do CONTEXT", saida)
            self.assertIn("Q-42", saida)

    def test_questao_listada_no_contexto_cala(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "| Q-42 | a pergunta | antes de T-10 |", "Q-42")
            self.assertNotIn("ausente do CONTEXT", rodar_check(repo).stdout)

    def test_questao_respondida_nao_conta_como_aberta(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "| Q-42 | ~~a pergunta~~ | **RESPONDIDA 2026-01-01 → D-01** |",
                                 "nenhuma")
            self.assertNotIn("ausente do CONTEXT", rodar_check(repo).stdout)


class TestAchadoVencido(unittest.TestCase):
    """O registro era append-only na CRIAÇÃO e não tinha disciplina de EXPIRAÇÃO: no projeto
    medido, o único QA crítico aberto descrevia uma condição já resolvida havia dias."""

    def preparar(self, tmp, linha_qa: str):
        repo = montar_kit(Path(tmp) / "repo")
        d = repo / "a_context/c_decisions.md"
        d.write_text(d.read_text(encoding="utf-8") + "\n" + linha_qa + "\n", encoding="utf-8")
        return repo

    def dias_atras(self, n):
        return (date.today() - timedelta(days=n)).isoformat()

    def test_critico_antigo_e_aberto_avisa(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "| QA-42 | 2020-01-01 | Crítico | revisão | `x.py:1` | quebrava | — | _(aberto)_ |")
            saida = rodar_check(repo).stdout
            self.assertIn("Achado vencido", saida)
            self.assertIn("QA-42", saida)

    def test_critico_fechado_cala(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "| QA-42 | 2020-01-01 | Crítico | revisão | `x.py:1` | quebrava | — | ✔ 2020-01-02 |")
            self.assertNotIn("Achado vencido", rodar_check(repo).stdout)

    def test_prazo_por_gravidade(self):
        """Prazo por nível, e não um prazo só. Antes era 14 dias para CRÍTICO/ALTO e NADA
        para o resto — e a medição do primeiro projeto real mostrou que isso cobrava
        exatamente o nível que não enrosca: os 8 CRÍTICOS e os 4 ALTOS estavam todos
        fechados, e o que apodrecia eram 5 MÉDIOS parados 13 a 15 dias, sem prazo nenhum.
        Os números vêm do porte do kit: projeto de 2 a 8 semanas."""
        casos = [
            ("Crítico", 10, True,  "CRÍTICO de 10 dias passa dos 7"),
            ("Crítico", 3,  False, "CRÍTICO de 3 dias ainda está no prazo"),
            ("Alto",    10, True,  "ALTO segue o mesmo prazo do CRÍTICO"),
            ("Médio",   20, True,  "MÉDIO de 20 dias passa dos 15"),
            ("Médio",   10, False, "MÉDIO de 10 dias ainda está no prazo"),
        ]
        for sev, idade, deve_avisar, porque in casos:
            with self.subTest(sev=sev, idade=idade), area_temporaria() as tmp:
                repo = self.preparar(tmp, f"| QA-42 | {self.dias_atras(idade)} | {sev} | revisão | "
                                          "`x.py:1` | quebrava | — | _(aberto)_ |")
                saida = rodar_check(repo).stdout
                self.assertEqual("Achado vencido" in saida, deve_avisar, f"{porque}:\n{saida[-400:]}")

    def test_baixo_nunca_vence(self):
        """Decisão, não esquecimento: metade dos achados abertos do projeto medido era
        BAIXO. Um aviso que passa a cobrar o que ninguém vai fazer vira ruído — e aviso que
        vira ruído deixa de ser lido, que é a mesma morte da checagem que emudece."""
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "| QA-42 | 2020-01-01 | Baixo | revisão | `x.py:1` | quebrava | — | _(aberto)_ |")
            self.assertNotIn("Achado vencido", rodar_check(repo).stdout)

    def test_acha_o_registro_que_mudou_de_casa(self):
        """No primeiro projeto real os `QA-NN` saíram do DECISIONS para `a_context/d_qa.md`.
        Uma checagem que só olha a casa antiga não é rigorosa, é cega — e relatar zero
        achado vencido num registro que nem foi lido é a leitura mais elogiosa e mais falsa
        que existe. Procure, não presuma."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            (repo / "a_context/d_qa.md").write_text(
                "---\ntags: [qa]\nstatus: atual\n---\n# QA\n\n"
                "| # | Data | Sev. | Onde | O que quebrava | Correção | Fechado em |\n"
                "|---|---|---|---|---|---|---|\n"
                "| QA-77 | 2020-01-01 | Crítico | `x.py:1` | quebrava | — | _(aberto)_ |\n",
                encoding="utf-8")
            saida = rodar_check(repo).stdout
            self.assertIn("QA-77", saida, f"registro em arquivo próprio não foi lido:\n{saida[-500:]}")

    def test_tabela_sem_a_coluna_diz_que_nao_julgou(self):
        """A doença do QA-14 é emudecer. Sem a coluna, a checagem fala em voz alta."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            d = repo / "a_context/c_decisions.md"
            d.write_text(d.read_text(encoding="utf-8").replace(
                "| O que quebrava | Correção | Fechado em |", "| O que quebrava | Correção |"),
                encoding="utf-8")
            self.assertIn("NÃO rodou", rodar_check(repo).stdout)


class TestOrigemDoAchado(unittest.TestCase):
    """A coluna `Origem` e o defeito que a fez nascer.

    Duas coisas moram aqui porque foram achadas juntas, na mesma leitura:

    1. **O modelo oficial de achado emitia SEIS células contra as SETE do cabeçalho.**
       Não era cosmético: a checagem de achado vencido lê a ÚLTIMA célula como
       "Fechado em", e numa linha curta ela lia "Correção" — que nunca está vazia e nunca
       diz "aberto". Todo achado escrito pelo modelo do próprio kit era contado como
       FECHADO, e a única checagem que cobra prazo dele nunca disparava. A cegueira
       entrou pela porta de QUEM ESCREVE, não pela de quem confere, e por isso o portão
       ficou verde o tempo todo. É a espécie do QA-14 vista de outro ângulo.
    2. **Faltava `Origem`** (`portão`/`revisão`/`dono`/`usuário`), e sem ela a pergunta
       "quantos defeitos o portão pegou?" não tem resposta — nem zero, que seria uma
       resposta. É a única medida deste kit sobre o MUNDO, e não sobre si mesmo.
    """

    def celulas(self, linha: str):
        return [c.strip() for c in linha.strip().strip("|").split("|")]

    def test_o_modelo_de_achado_bate_com_o_cabecalho(self):
        """A regressão que impede o defeito de voltar. Compara os DOIS arquivos reais do
        kit — não uma cópia da regra escrita aqui, que envelheceria junto."""
        cab = None
        for linha in (KIT / "a_context/c_decisions.md").read_text(encoding="utf-8").splitlines():
            if re.match(r"^\|\s*#\s*\|", linha) and "Fechado" in linha:
                cab = self.celulas(linha)
        self.assertIsNotNone(cab, "o cabeçalho da tabela de QA sumiu do DECISIONS")

        modelo = (KIT / "b_process/templates/b_qa_finding.md").read_text(encoding="utf-8")
        linha_modelo = next((l for l in modelo.splitlines()
                             if re.match(r"^\|\s*QA-NN\s*\|", l)), None)
        self.assertIsNotNone(linha_modelo, "o modelo de achado não tem mais a linha da tabela")
        self.assertEqual(
            len(self.celulas(linha_modelo)), len(cab),
            "o modelo de achado escreve um número de células diferente do cabeçalho do "
            "DECISIONS. Foi exatamente assim que TODO achado do kit passou a ser contado "
            "como fechado: a última célula deixa de ser 'Fechado em'. "
            f"cabeçalho ({len(cab)}): {cab} · "
            f"modelo ({len(self.celulas(linha_modelo))}): {self.celulas(linha_modelo)}")

    def test_o_cabecalho_tem_origem(self):
        cab = (KIT / "a_context/c_decisions.md").read_text(encoding="utf-8")
        self.assertTrue(
            re.search(r"^\|\s*#\s*\|.*\bOrigem\b.*Fechado", cab, re.M | re.I),
            "o cabeçalho da tabela de QA perdeu a coluna 'Origem' — sem ela, 'quantos "
            "defeitos o portão pegou' volta a ser irrespondível")

    def preparar(self, tmp, linha_qa, cabecalho=None):
        repo = montar_kit(Path(tmp) / "repo")
        d = repo / "a_context/c_decisions.md"
        corpo = d.read_text(encoding="utf-8")
        if cabecalho:
            corpo = re.sub(r"^\|\s*#\s*\|.*Fechado em \|$", cabecalho, corpo, flags=re.M)
        d.write_text(corpo + "\n" + linha_qa + "\n", encoding="utf-8")
        return repo

    def test_linha_curta_nao_passa_por_fechada(self):
        """A isca do defeito real: linha SEM a célula 'Fechado em', com a de 'Correção'
        preenchida — que é como o modelo antigo escrevia. Antes do conserto isso saía
        silencioso; agora tem de falar."""
        with area_temporaria() as tmp:
            repo = self.preparar(
                tmp, "| QA-42 | 2020-01-01 | Crítico | revisão | `x.py:1` | quebrava | trocou o parser |")
            saida = rodar_check(repo).stdout
            self.assertIn("contagem de células", saida,
                          f"linha curta passou calada — é o defeito de volta:\n{saida[-600:]}")
            self.assertIn("QA-42", saida)

    def test_linha_completa_continua_sendo_julgada(self):
        """Contraprova: o aviso de desalinhamento não pode engolir o de prazo."""
        with area_temporaria() as tmp:
            repo = self.preparar(
                tmp, "| QA-42 | 2020-01-01 | Crítico | revisão | `x.py:1` | quebrava | — | _(aberto)_ |")
            saida = rodar_check(repo).stdout
            self.assertIn("Achado vencido", saida)
            self.assertNotIn("contagem de células", saida)

    def test_tabela_sem_a_coluna_origem_avisa(self):
        with area_temporaria() as tmp:
            repo = self.preparar(
                tmp,
                "| QA-42 | 2020-01-01 | Crítico | `x.py:1` | quebrava | — | _(aberto)_ |",
                cabecalho="| # | Data | Sev. | Onde | O que quebrava | Correção | Fechado em |")
            self.assertIn("sem a coluna 'Origem'", rodar_check(repo).stdout)

    def test_tabela_com_a_coluna_origem_nao_avisa(self):
        with area_temporaria() as tmp:
            repo = self.preparar(
                tmp, "| QA-42 | 2020-01-01 | Crítico | portão | `x.py:1` | quebrava | — | _(aberto)_ |")
            self.assertNotIn("sem a coluna 'Origem'", rodar_check(repo).stdout)

    def test_o_aviso_de_origem_e_aviso_e_nao_falha(self):
        """Registro append-only: reprovar o que a regra proíbe editar é armadilha, não
        portão. A lição já está paga em d_agent_learnings.md."""
        with area_temporaria() as tmp:
            repo = self.preparar(
                tmp,
                "| QA-42 | 2030-01-01 | Baixo | `x.py:1` | quebrava | — | _(aberto)_ |",
                cabecalho="| # | Data | Sev. | Onde | O que quebrava | Correção | Fechado em |")
            r = rodar_check(repo)
            self.assertIn("sem a coluna 'Origem'", r.stdout)
            self.assertEqual(r.returncode, 0, f"virou falha:\n{r.stdout[-500:]}")


class TestArquivar(unittest.TestCase):
    """`task.py arquivar`: a parte cara do arquivamento nunca foi mover o texto, foi DECIDIR
    o que pode sair. Critério do `D-43`: sai quem nenhum `.md` vivo cita.

    Relata por padrão. O `check.py` declara em código que "script não escreve na verdade de
    ninguém" — a exceção é explícita e exige `--aplicar`."""

    def preparar(self, tmp, linhas_d: str, citacao: str = ""):
        repo = montar_kit(Path(tmp) / "repo")
        d = repo / "a_context/c_decisions.md"
        d.write_text(d.read_text(encoding="utf-8") + "\n" + linhas_d + "\n", encoding="utf-8")
        if citacao:
            p = repo / "a_context/b_plan.md"
            p.write_text(p.read_text(encoding="utf-8") + "\n" + citacao + "\n", encoding="utf-8")
        return repo

    def rodar(self, repo, *extra):
        return subprocess.run([sys.executable, str(repo / "scripts/arquivar.py"), str(repo), *extra],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", env=AMBIENTE_UTF8, timeout=120)

    def test_template_puro_nao_tem_candidata(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.assertIn("Nada a arquivar", self.rodar(repo).stdout)

    def test_decisao_que_ninguem_cita_e_candidata(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "| D-42 | 2026-01-01 | ADOTADO | ninguém me cita | |")
            self.assertIn("D-42", self.rodar(repo).stdout)

    def test_decisao_citada_por_arquivo_vivo_fica(self):
        """Inclusive citada ENTRE CRASES, que é como a casa escreve (QA-14)."""
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "| D-42 | 2026-01-01 | ADOTADO | alguém me cita | |",
                                 "O módulo segue `D-42`.")
            saida = self.rodar(repo).stdout
            self.assertIn("Nada a arquivar", saida)
            self.assertIn("D-42", saida.split("Candidatas")[0])

    def test_rejeitada_e_preservada_por_padrao(self):
        """A lista-morta é a tese do kit: ela some só por decisão explícita."""
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "| D-43 | 2026-01-01 | REJEITADO | morreu | |")
            self.assertIn("REJEITADAS preservadas", self.rodar(repo).stdout)
            self.assertIn("D-43", self.rodar(repo, "--incluir-rejeitadas").stdout)

    def test_sem_aplicar_nao_escreve(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "| D-42 | 2026-01-01 | ADOTADO | ninguém me cita | |")
            antes = (repo / "a_context/c_decisions.md").read_text(encoding="utf-8")
            self.rodar(repo)
            self.assertEqual(antes, (repo / "a_context/c_decisions.md").read_text(encoding="utf-8"))

    def test_aplicar_move_e_preserva_a_integra(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp, "| D-42 | 2026-01-01 | ADOTADO | ninguém me cita | |")
            reg = repo / "a_context/c_decisions.md"
            antes = len(reg.read_text(encoding="utf-8"))
            self.rodar(repo, "--aplicar")
            depois = reg.read_text(encoding="utf-8")
            self.assertLess(len(depois), antes)
            self.assertNotIn("| D-42 |", depois)
            self.assertIn("D-42", (repo / "e_qa/decisions_archive.md").read_text(encoding="utf-8"))


class TestIdArquivado(unittest.TestCase):
    """QA-16 — ID retirado da tabela continua sendo ID REAL: é o que "ID preservado, nada
    revertido" significa, e é a regra que o próprio arquivamento do kit promete.

    Medido antes de existir: com a correção do QA-14 sozinha, o primeiro projeto real passava
    a acusar **22 fantasmas** — todos legitimamente arquivados — e o portão reprovaria TODO
    commit. Correção que só funciona em projeto que nunca arquivou não é correção.

    No arquivo-morto o ID vem entre crases (`| `D-05` | 2026-08-06 | …`), então aqui não se
    procura linha de tabela: qualquer ocorrência no arquivo vale como definição."""

    def arquivar(self, repo: Path, linha: str):
        p = repo / "e_qa/decisions_archive.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        cabeca = "" if p.exists() else "---\ntags: [qa, arquivo]\nstatus: atual\n---\n# Registro arquivado\n\n"
        p.write_text((p.read_text(encoding="utf-8") if p.exists() else cabeca) + linha + "\n",
                     encoding="utf-8")

    def citar(self, repo: Path, texto: str):
        p = repo / "INDEX.md"
        p.write_text(p.read_text(encoding="utf-8") + "\n\n" + texto + "\n", encoding="utf-8")

    def test_id_arquivado_nao_e_fantasma(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.arquivar(repo, "| `D-77` | 2026-01-01 | ADOTADO | retirada da tabela | |")
            self.citar(repo, "O módulo segue `D-77`.")
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 0, f"ID arquivado virou fantasma:\n{r.stdout}")

    def test_id_que_nao_esta_em_lugar_nenhum_continua_fantasma(self):
        """Contraprova: sem ela, este conserto poderia ter desligado a checagem 10 inteira."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.arquivar(repo, "| `D-77` | 2026-01-01 | ADOTADO | retirada da tabela | |")
            self.citar(repo, "O módulo segue `D-78`.")
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("D-78", r.stdout)

    def test_arquivado_que_ficou_na_tabela_nao_vira_duplicata(self):
        """A convenção `ADOTADO · ARQUIVADO` deixa a linha NA tabela com a íntegra no arquivo.
        Se a presença no arquivo contasse como definição, isso viraria ID duplicado — falha
        falsa em cima da própria convenção do kit."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.arquivar(repo, "| `D-01` | 2026-01-01 | ADOTADO | a íntegra | |")
            r = rodar_check(repo)
            self.assertNotIn("ID duplicado", r.stdout)
            self.assertEqual(r.returncode, 0, r.stdout)


class TestOrcamentoBacklog(unittest.TestCase):
    """Checagem 15. O BACKLOG era o único registro sem teto E sem arquivamento, sendo a
    leitura de ABERTURA de toda sessão de trabalho. Medido no primeiro projeto real:
    191.591 caracteres, dos quais 173.818 (91%) em 72 cards JÁ FECHADOS."""

    def encher(self, repo, n=60, fechados=True):
        """Cards de VÁRIAS linhas de propósito: o card gordo é o caso que dominou a
        medição (6.142 caracteres num só), e uma contagem por LINHA o subestima em 21%."""
        bl = repo / "b_process/c_backlog.md"
        marca = "x" if fechados else " "
        corpo = "".join(
            f"- [{marca}] T-{i:02d} — tarefa **número {i}** · **Módulo:** M1\n"
            f"  detalhe que só existe para pesar: {'palavra ' * 30}\n"
            for i in range(n))
        bl.write_text(bl.read_text(encoding="utf-8") + "\n## Feito\n" + corpo, encoding="utf-8")
        return bl

    def test_backlog_acima_do_teto_reprova(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.encher(repo)
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 1, f"devia reprovar:\n{r.stdout[-600:]}")
            self.assertIn("c_backlog.md com", r.stdout)
            self.assertIn("card(s) fechado(s)", r.stdout)

    def test_card_ABERTO_nao_e_oferecido_como_candidato(self):
        """Card aberto é trabalho, não histórico. Se o arquivador o levasse, o kit apagaria
        a fila do dono para caber num número — o oposto do que o teto existe para proteger."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.encher(repo, fechados=False)
            r = rodar_script("arquivar.py", str(repo), "--backlog")
            # "arquivável" e não "fechado": o template traz um card fechado de EXEMPLO
            # (`- [x] T-… — <tarefa>`), sem número no ID. Ele é fechado e não é arquivável,
            # e a primeira versão deste modo tentou levá-lo — teria apagado a linha que
            # ensina o formato, deixando um ponteiro com `?` no lugar do ID.
            self.assertIn("Nenhum card arquivável", r.stdout, r.stdout)
            self.assertIn("sem ID legível", r.stdout, "o template tem de ser ignorado COM aviso")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_arquivar_derruba_o_teto_e_preserva_ID_e_modulo(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            bl = self.encher(repo)
            antes = len(bl.read_text(encoding="utf-8"))
            r = rodar_script("arquivar.py", str(repo), "--backlog", "--aplicar")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            depois = bl.read_text(encoding="utf-8")
            self.assertLess(len(depois), antes / 2, "arquivar tem de cortar de verdade")
            # o ID continua resolvendo e o marcador da checagem 13 sobrevive
            self.assertIn("- [x] T-07", depois)
            self.assertIn("**Módulo:** M1", depois)
            self.assertIn("[[backlog_archive]]", depois)
            # e a íntegra não se perdeu
            morto = repo / "e_qa/backlog_archive.md"
            self.assertTrue(morto.exists(), "arquivo-morto do backlog não foi criado")
            self.assertIn("palavra palavra", morto.read_text(encoding="utf-8"))
            self.assertEqual(rodar_check(repo).returncode, 0, "devia ficar verde depois de arquivar")

    def test_ponteiro_nao_deixa_markdown_desbalanceado(self):
        """O título é cortado em 60. Cortar dentro de um `**negrito**` fecha metade da
        marcação e contamina o render do resto do arquivo — pego no caso real."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            bl = self.encher(repo, n=3)
            rodar_script("arquivar.py", str(repo), "--backlog", "--aplicar")
            for linha in bl.read_text(encoding="utf-8").splitlines():
                if "[[backlog_archive]]" not in linha:
                    continue
                titulo = linha.split("—", 1)[1].split("·")[0] if "—" in linha else ""
                self.assertEqual(titulo.count("*"), 0, f"asterisco solto no ponteiro: {linha}")
                self.assertEqual(titulo.count("`") % 2, 0, f"crase ímpar no ponteiro: {linha}")


class TestIdPrometidoNoChangelog(unittest.TestCase):
    """Checagem 10, ponto cego. `d_history/` estava fora da checagem de existência porque
    "cita IDs de outros projetos" — verdade para as lições herdadas, falso para o CHANGELOG
    do próprio projeto. Medido: `D-64` foi prometido numa entrada e nunca entrou na tabela;
    o portão imprimiu verde por 8 dias e quem pegou foi uma sessão seguinte, no olho."""

    def prometer(self, vault: Path):
        log = vault / "d_history/a_changelog.md"
        log.write_text(log.read_text(encoding="utf-8")
                       + "\n## 2026-01-01\n- o `[hidden]` global vira `D-64`.\n", encoding="utf-8")

    def test_avisa_e_nao_reprova(self):
        """AVISO e não falha por desenho: o changelog é append-only, e reprovar num arquivo
        que a regra proíbe editar é portão sem saída — que ensina a usar --no-verify."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.prometer(repo)
            r = rodar_check(repo)
            self.assertIn("ID prometido", r.stdout)
            self.assertIn("D-64", r.stdout)
            self.assertEqual(r.returncode, 0, "é aviso, não falha")
            self.assertEqual(rodar_check(repo, extra=("--avisos-reprovam",)).returncode, 1)

    def test_dispara_tambem_no_layout_de_PROJETO(self):
        """A regressão que este teste guarda é de dentro da própria correção: a primeira
        versão comparava um caminho relativo ao TOPO do repositório contra a constante, que
        é relativa ao VAULT. Num kit (topo == vault) passava; num projeto, onde o vault mora
        em <TAG>_Project_DOCs/, o aviso nascia MUDO — a checagem que emudece, cometida
        dentro do conserto da checagem que emudecia."""
        with area_temporaria() as tmp:
            kit = montar_kit(Path(tmp) / "kit")
            projeto = Path(tmp) / "projeto"
            r = rodar_script("new_project.py", str(projeto), "--nome", "App", cwd=kit)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            docs = vault_de(projeto)
            self.prometer(docs)
            saida = rodar_check(projeto, script=docs / "scripts/check.py").stdout
            self.assertIn("ID prometido", saida, f"aviso nasceu mudo no layout de projeto:\n{saida[-700:]}")

    def test_id_citado_por_doc_vivo_continua_reprovando(self):
        """O aviso não pode virar rebaixamento: ID fantasma em documento VIVO segue falha.
        Sem esta guarda, a correção teria trocado um portão por um aviso."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.prometer(repo)
            ctx = repo / "a_context/a_context_source.md"
            ctx.write_text(ctx.read_text(encoding="utf-8") + "\n- segue `D-64`.\n", encoding="utf-8")
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("ID citado que não existe", r.stdout)
            self.assertNotIn("ID prometido", r.stdout, "não cobre o mesmo defeito duas vezes")


class TestEvidencia(unittest.TestCase):
    """`evidencia.py` existe para atacar o 35 em "evidência de que funciona". Um relatório
    que erra número, ou que apresenta "não medido" como zero, é PIOR que nenhum relatório:
    ele fabrica confiança. Cada teste aqui guarda um erro que já aconteceu de verdade."""

    def relatar(self, repo, *extra):
        r = rodar_script("evidencia.py", str(repo), *extra)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("Traceback", r.stderr, r.stderr[-800:])
        return r.stdout

    def test_censo_conta_skill_declarada_no_relatorio_de_e_qa(self):
        """O defeito que motivou o censo: `artifact-consistency` rodou DUAS vezes no
        primeiro projeto real — reprovou o plano com 3 achados críticos — e não aparecia em
        nenhuma linha `**Skill:**` do changelog, porque o relatório dela mora em `e_qa/`.
        O portão exige que ALGUMA skill seja declarada por sessão, não a certa; então
        contar só o changelog subestimava o uso e chamava de peso morto a skill de melhor
        retorno do kit."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            (repo / "e_qa/relatorio_260807_1543.md").write_text(
                "---\ntags: [qa]\nstatus: atual\n---\n# Relatório\n"
                "- **Skill:** `artifact-consistency`\n", encoding="utf-8")
            saida = self.relatar(repo)
            self.assertIn("artifact-consistency", saida,
                          "skill declarada em e_qa/ ficou fora do censo")

    def test_registro_que_mudou_de_casa_nao_vira_zero(self):
        """No primeiro projeto real os `QA-NN` saíram do DECISIONS para arquivo próprio
        (`a_context/d_qa.md`). Um script que assumisse a casa antiga relataria ZERO achados
        num projeto com 36 — e zero achados é a leitura mais elogiosa possível de um
        registro que na verdade nem foi lido."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            (repo / "a_context/d_qa.md").write_text(
                "---\ntags: [qa]\nstatus: atual\n---\n# QA\n\n"
                "| # | Data | Sev. | Onde | Fechado em |\n|---|---|---|---|---|\n"
                "| QA-40 | 2026-01-02 | CRÍTICO | x | _(aberto)_ |\n"
                "| QA-41 | 2026-01-03 | BAIXO | y | 2026-01-04 |\n", encoding="utf-8")
            saida = self.relatar(repo)
            self.assertIn("QA-40", saida, "achado em arquivo próprio não foi encontrado")
            self.assertIn("CRÍTICO", saida)

    def test_sem_git_diz_NAO_VERIFICADO_e_nao_zero(self):
        """QA-03 de novo, na forma mais cara: anunciar como medido o que não foi lido.
        Sem git, metade do relatório não existe — e tem de dizer isso com todas as letras,
        porque '0 commits' num relatório de evidência lê-se como projeto inativo."""
        with area_temporaria() as tmp:
            repo = Path(tmp) / "repo"
            shutil.copytree(KIT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            saida = self.relatar(repo)
            self.assertIn("NÃO foi medida", saida)
            self.assertNotIn("commits: 0", saida)

    def test_declara_o_que_nao_mede(self):
        """A seção de limites não é enfeite: é o que separa este relatório do 'relato, não
        medição' que o caso de referência do kit já carrega. Sem contrafactual, nenhum
        número aqui responde 'o kit ajudou' — e o relatório tem de dizer isso ele mesmo."""
        with area_temporaria() as tmp:
            saida = self.relatar(montar_kit(Path(tmp) / "repo"))
            self.assertIn("NÃO mede", saida)
            self.assertIn("AJUDOU", saida, "o relatório tem de recusar a pergunta que não pode responder")

    def test_nao_escreve_nada(self):
        """Script de medição que altera o medido é o pior defeito possível desta classe.
        O `arquivar.py` só escreve com `--aplicar`; este não escreve nunca."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            antes = {p: p.stat().st_mtime_ns for p in repo.rglob("*.md")}
            self.relatar(repo)
            self.relatar(repo, "--json")
            depois = {p: p.stat().st_mtime_ns for p in repo.rglob("*.md")}
            self.assertEqual(antes, depois, "evidencia.py tocou em arquivo do projeto")
            self.assertEqual(git(repo, "status", "--porcelain").stdout.strip(), "")

    def test_json_sai_valido_e_com_acento(self):
        """QA-01: o relatório é cheio de `·`, `É` e `ç`. JSON que morre no acento não
        acumula entre projetos — e acumular é a razão de o `--json` existir."""
        with area_temporaria() as tmp:
            dados = json.loads(self.relatar(montar_kit(Path(tmp) / "repo"), "--json"))
            for chave in ("orcamentos", "decisoes", "questoes", "achados", "skills", "git"):
                self.assertIn(chave, dados)
            self.assertEqual(dados["skills"]["disponiveis"], 24)


class TestMarcoEOrigem(unittest.TestCase):
    """A SÉRIE e a ORIGEM — as duas metades que faltavam para o kit conseguir se julgar.

    Ambas nasceram do mesmo achado: um critério de conclusão congelado exigia
    "campo `origem` em cada QA-NN" e "série temporal a cada marco, commitada", e nenhum dos
    dois existia meses depois. O da série é o mais constrangedor: a última linha do próprio
    relatório PEDIA "guarde a saída de --json", por escrito, no lugar mais visível possível —
    e a taxa de cumprimento no único projeto real foi ZERO em oito dias. É a lição do kit
    apontada para ele mesmo: *regra que a máquina não cobra é pedido, não regra.*
    """

    def relatar(self, repo, *extra):
        r = rodar_script("evidencia.py", str(repo), *extra)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("Traceback", r.stderr, r.stderr[-800:])
        return r.stdout

    def com_qa(self, repo, linha, cabecalho=None):
        d = repo / "a_context/c_decisions.md"
        corpo = d.read_text(encoding="utf-8")
        if cabecalho:
            corpo = re.sub(r"^\|\s*#\s*\|.*Fechado em \|$", cabecalho, corpo, flags=re.M)
        d.write_text(corpo + "\n" + linha + "\n", encoding="utf-8")

    def test_origem_declarada_aparece_no_relatorio(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.com_qa(repo, "| QA-42 | 2026-01-01 | Alto | portão | `x.py:1` | quebrava | — | ✔ 2026-01-02 |")
            saida = self.relatar(repo)
            self.assertIn("origem:", saida)
            self.assertIn("portão 1", saida, saida[-900:])

    def test_coluna_ausente_e_coluna_vazia_sao_diagnosticos_diferentes(self):
        """Dizer um pelo outro é o relatório mentindo com número certo — e as ações que
        eles pedem são diferentes: uma é acrescentar estrutura, a outra é preencher."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.com_qa(repo, "| QA-42 | 2026-01-01 | Alto | `x.py:1` | quebrava | — | ✔ 2026-01-02 |",
                        cabecalho="| # | Data | Sev. | Onde | O que quebrava | Correção | Fechado em |")
            self.assertIn("NÃO EXISTE", self.relatar(repo))
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.com_qa(repo, "| QA-42 | 2026-01-01 | Alto |  | `x.py:1` | quebrava | — | ✔ 2026-01-02 |")
            saida = self.relatar(repo)
            self.assertIn("VAZIA", saida)
            self.assertNotIn("NÃO EXISTE", saida)

    def test_questao_cujo_marco_ja_fechou_aparece(self):
        """A isca dos dois casos reais: as Q-NN que "venceram" no projeto medido diziam
        "antes de T-10" e "antes de E-3" — MARCOS, não datas. Um contador de dias não pega
        nenhuma das duas (o projeto inteiro durou 4 dias)."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            d = repo / "a_context/c_decisions.md"
            d.write_text(d.read_text(encoding="utf-8").replace(
                "| Q-01 | <ex.: quais formas de pagamento entram no escopo?> | <marco/condição> |",
                "| Q-09 | de quem é a escolha pendente? | antes de T-10 |"), encoding="utf-8")
            bl = repo / "b_process/c_backlog.md"
            bl.write_text(bl.read_text(encoding="utf-8") + "\n- [x] T-10 — a tarefa que andou sem a resposta\n",
                          encoding="utf-8")
            saida = self.relatar(repo)
            self.assertIn("MARCO JÁ PASSOU", saida, saida[-900:])
            self.assertIn("Q-09", saida)

    def test_questao_com_marco_ainda_aberto_nao_e_cobrada(self):
        """Contraprova. Pergunta aberta cujo marco não chegou é o canal FUNCIONANDO — cobrar
        aí seria transformar o funcionamento normal em prova de fracasso, que foi exatamente
        o erro de régua que a primeira avaliação de campo cometeu e declarou."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            d = repo / "a_context/c_decisions.md"
            d.write_text(d.read_text(encoding="utf-8").replace(
                "| Q-01 | <ex.: quais formas de pagamento entram no escopo?> | <marco/condição> |",
                "| Q-09 | de quem é a escolha pendente? | antes de T-10 |"), encoding="utf-8")
            bl = repo / "b_process/c_backlog.md"
            bl.write_text(bl.read_text(encoding="utf-8") + "\n- [ ] T-10 — ainda aberta\n",
                          encoding="utf-8")
            self.assertNotIn("MARCO JÁ PASSOU", self.relatar(repo))

    def test_marco_grava_o_arquivo_e_compara_com_o_anterior(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            hoje = date.today().strftime("%y%m%d")
            saida = self.relatar(repo, "--marco")
            alvo = repo / "e_qa" / ("evidencia_" + hoje + ".json")
            self.assertTrue(alvo.exists(), "o marco não gravou nada — era o pedido que virou comando")
            self.assertIn("ponto zero", saida, "o primeiro marco tem de dizer que não é série")
            dados = json.loads(alvo.read_text(encoding="utf-8"))
            self.assertIn("achados", dados)

            velho = dict(dados, medido_em="2020-01-01")
            velho["decisoes"] = dict(velho["decisoes"], rejeitadas=99)
            (repo / "e_qa/evidencia_200101.json").write_text(
                json.dumps(velho, ensure_ascii=False), encoding="utf-8")
            alvo.unlink()
            saida2 = self.relatar(repo, "--marco")
            self.assertIn("evidencia_200101.json", saida2)
            self.assertIn("99 ->", saida2, saida2[:900])

    def test_marco_nao_inventa_zero_onde_nao_mediu(self):
        """No repositório do KIT o vault É a raiz, então não existe "produto" do qual
        separar o processo. Um 0,0 ali seria a leitura mais elogiosa possível de algo que
        nem foi medido — e é o JSON que a série compara, então a mentira viajaria."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            r = rodar_script("evidencia.py", str(repo), "--json")
            self.assertIsNone(json.loads(r.stdout)["git"]["pct_so_processo"])


class TestTravaDeEscopo(unittest.TestCase):
    """A regra 2 do CLAUDE.md — "escopo é o módulo desta sessão; precisa mexer em outro?
    pare e avise" — era prosa no prompt, e prosa no prompt é pedido, não trava. Um
    benchmarking do kit contra oito alternativas marcou nota 3 em "papéis especializados"
    exatamente por isso. Estes testes guardam as duas metades: que ela PEGA, e que ela
    FALHA ABERTA — porque hook que bloqueia errado ensina a desligar o hook."""

    def montar(self, tmp, pasta="src/core", modulo="M1"):
        kit = montar_kit(Path(tmp) / "kit")
        projeto = Path(tmp) / "projeto"
        r = rodar_script("new_project.py", str(projeto), "--nome", "App", cwd=kit)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        docs = vault_de(projeto)
        pl = docs / "a_context/b_plan.md"
        pl.write_text(pl.read_text(encoding="utf-8").replace(
            "### M1 — <nome>", f"### {modulo} — motor\n- **Pasta:** {pasta}", 1), encoding="utf-8")
        bl = docs / "b_process/c_backlog.md"
        bl.write_text(bl.read_text(encoding="utf-8").replace(
            "- [ ] T-00 — <a tarefa do momento>",
            f"- [ ] T-07 — mexer no motor · **Módulo:** {modulo} · **Portão:** verde"),
            encoding="utf-8")
        return projeto, docs

    def bater(self, projeto, caminho, ferramenta="Edit"):
        evento = json.dumps({"cwd": str(projeto), "tool_name": ferramenta,
                             "tool_input": {"file_path": str(caminho)}})
        return subprocess.run([sys.executable, str(KIT / "scripts/escopo_hook.py")],
                              input=evento, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", env=AMBIENTE_UTF8, timeout=60)

    def test_bloqueia_fora_do_modulo(self):
        with area_temporaria() as tmp:
            projeto, _ = self.montar(tmp)
            r = self.bater(projeto, projeto / "src/net/index.ts")
            self.assertEqual(r.returncode, 2, f"devia bloquear:\n{r.stdout}{r.stderr}")
            self.assertIn("BLOQUEADO", r.stderr)
            # A mensagem precisa oferecer SAÍDA: portão sem saída ensina --no-verify.
            self.assertIn("PARE e avise", r.stderr)
            self.assertIn("QA-NN", r.stderr)

    def test_libera_dentro_do_modulo(self):
        with area_temporaria() as tmp:
            projeto, _ = self.montar(tmp)
            self.assertEqual(self.bater(projeto, projeto / "src/core/motor.ts").returncode, 0)

    def test_a_documentacao_e_sempre_gravavel(self):
        """Travar a pasta de docs quebraria o fecho de sessão que o próprio kit exige:
        é nela que a sessão registra decisão, achado e changelog."""
        with area_temporaria() as tmp:
            projeto, docs = self.montar(tmp)
            self.assertEqual(self.bater(projeto, docs / "a_context/c_decisions.md").returncode, 0)

    def test_leitura_nunca_bloqueia(self):
        """Ler outro módulo para entender o contrato sempre foi trabalho legítimo."""
        with area_temporaria() as tmp:
            projeto, _ = self.montar(tmp)
            self.assertEqual(self.bater(projeto, projeto / "src/net/x.ts", "Read").returncode, 0)

    def test_falha_aberta_e_diz_por_que(self):
        with area_temporaria() as tmp:
            projeto, docs = self.montar(tmp)
            casos = {}
            # 1. módulo sem **Pasta:** declarada
            pl = docs / "a_context/b_plan.md"
            original = pl.read_text(encoding="utf-8")
            pl.write_text(original.replace("- **Pasta:** src/core\n", ""), encoding="utf-8")
            casos["sem Pasta"] = self.bater(projeto, projeto / "src/net/x.ts")
            pl.write_text(original, encoding="utf-8")
            # 2. duas tarefas em andamento — não dá para saber qual escopo cobrar
            bl = docs / "b_process/c_backlog.md"
            bl.write_text(bl.read_text(encoding="utf-8").replace(
                "- [ ] T-07 — mexer no motor",
                "- [ ] T-08 — outra coisa · **Módulo:** M1\n- [ ] T-07 — mexer no motor"),
                encoding="utf-8")
            casos["duas tarefas"] = self.bater(projeto, projeto / "src/net/x.ts")
            for nome, r in casos.items():
                with self.subTest(caso=nome):
                    self.assertEqual(r.returncode, 0, f"{nome} devia LIBERAR:\n{r.stderr}")
                    self.assertIn("[escopo] liberado:", r.stderr,
                                  f"{nome} liberou em SILÊNCIO — liberação sem motivo não se audita")

    def test_entrada_quebrada_libera(self):
        """Hook que morre com entrada inesperada trava o trabalho por bug próprio."""
        r = subprocess.run([sys.executable, str(KIT / "scripts/escopo_hook.py")],
                           input="isto não é json", capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=AMBIENTE_UTF8, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_instalar_e_remover_nao_mexe_em_hook_alheio(self):
        """`--escopo` escreve em `.claude/settings.json`, que pode ter hooks do dono.
        Apagar o que não é nosso é como se perde trabalho alheio sem perceber."""
        with area_temporaria() as tmp:
            projeto, docs = self.montar(tmp)
            git(projeto, "init", "-q")
            cfg = projeto / ".claude/settings.json"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            cfg.write_text(json.dumps({"hooks": {"PreToolUse": [
                {"matcher": "Bash", "hooks": [{"type": "command", "command": "meu-script.sh"}]}]}}),
                encoding="utf-8")
            rodar_script("install_hook.py", "--escopo", cwd=docs)
            dados = json.loads(cfg.read_text(encoding="utf-8"))
            self.assertEqual(len(dados["hooks"]["PreToolUse"]), 2, "não acrescentou o nosso")
            rodar_script("install_hook.py", "--escopo", "--remover", cwd=docs)
            dados = json.loads(cfg.read_text(encoding="utf-8"))
            self.assertEqual(len(dados["hooks"]["PreToolUse"]), 1, "removeu demais")
            self.assertIn("meu-script.sh", json.dumps(dados), "apagou o hook do dono")


class TestSkillOrfa(unittest.TestCase):
    """De 24 skills, só 10 dispararam no primeiro projeto real — e quatro das que nunca
    rodaram tinham o assunto acontecendo ali. A mais gritante: existe uma checagem no
    `check.py` que se declara "a checagem que a skill guardrails-review exige"; a checagem
    rodava, a skill nunca. O problema não era falta de skill, era falta de ROTEAMENTO."""

    def preparar(self, tmp, skill_rodou=None):
        repo = montar_kit(Path(tmp) / "repo")
        pl = repo / "a_context/b_plan.md"
        pl.write_text(pl.read_text(encoding="utf-8").replace(
            "### M1 — <nome>",
            "### M1 — privacidade\n- **Skill responsável:** "
            "[[b_process/skills/privacy-personal-data/SKILL|privacidade]]", 1), encoding="utf-8")
        log = repo / "d_history/a_changelog.md"
        entrada = f"\n## 2026-01-01\n- **Skill:** `{skill_rodou}`\n" if skill_rodou else ""
        log.write_text(log.read_text(encoding="utf-8") + entrada, encoding="utf-8")
        return repo

    def test_avisa_quando_a_responsavel_nunca_rodou(self):
        with area_temporaria() as tmp:
            saida = rodar_check(self.preparar(tmp, skill_rodou="testing")).stdout
            self.assertIn("nunca rodou", saida)
            self.assertIn("privacy-personal-data", saida)
            self.assertIn("M1", saida)

    def test_cala_quando_ela_rodou(self):
        with area_temporaria() as tmp:
            saida = rodar_check(self.preparar(tmp, skill_rodou="privacy-personal-data")).stdout
            self.assertNotIn("nunca rodou", saida)

    def test_template_por_preencher_nao_vira_aviso(self):
        """`<ex.: …>` é plano não preenchido, não lacuna de roteamento."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            log = repo / "d_history/a_changelog.md"
            log.write_text(log.read_text(encoding="utf-8") + "\n## 2026-01-01\n- **Skill:** `testing`\n",
                           encoding="utf-8")
            self.assertNotIn("nunca rodou", rodar_check(repo).stdout)


class TestConfigDoProjeto(unittest.TestCase):
    """`.kit-config.json` existe por um custo medido: o primeiro projeto real precisou de um
    teto maior e de um terceiro registro (`QA-NN` fora do DECISIONS), e a única saída que o
    kit oferecia era EDITAR o `check.py`. O portão do projeto virou um fork oito versões
    atrasado — com uma cegueira já corrigida no kit — e toda atualização o marcava como
    'PROTEGIDO'. O projeto passou a medir a si mesmo com uma régua que não era mais a régua.

    Estes testes guardam as duas metades: que a configuração FUNCIONA (o projeto não precisa
    editar o script) e que ela não abre buraco (subir teto continua exigindo D-NN)."""

    def montar(self, tmp, config: str, extras=()):
        repo = montar_kit(Path(tmp) / "repo")
        (repo / ".kit-config.json").write_text(config, encoding="utf-8")
        for rel, texto in extras:
            (repo / rel).write_text(texto, encoding="utf-8")
        return repo

    def test_registro_extra_faz_o_ID_existir(self):
        """O caso que criou o fork: com os `QA-NN` em arquivo próprio, o kit os via como
        fantasmas e reprovava todo commit. Declarar o registro resolve sem tocar no script."""
        with area_temporaria() as tmp:
            tabela = ("---\ntags: [qa]\n---\n# QA\n\n| # | Data | Sev. | O que | Fechado em |\n"
                      "|---|---|---|---|---|\n| QA-42 | 2026-08-24 | BAIXO | algo | 2026-08-24 |\n")
            repo = self.montar(tmp, '{"registros": ["a_context/d_qa.md"], '
                                    '"tetos": {"a_context/d_qa.md": 8000}}',
                               [("a_context/d_qa.md", tabela)])
            self.anexar_texto(repo, "INDEX.md", "\n\nVer `QA-42` para o detalhe.\n")
            # O registro extra é decisão: sem o D-NN que o declare, a FALHA 16 reprova.
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("não é registro do kit", r.stdout)
            self.anexar_texto(repo, "a_context/c_decisions.md",
                              "| D-50 | 2026-08-24 | ADOTADO | d_qa.md como registro próprio "
                              "dos achados, teto 8.000 | tabela de QA estourava o DECISIONS |\n")
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 0, f"QA-42 devia existir pelo registro declarado:\n{r.stdout}")

    def test_teto_extra_estourado_reprova(self):
        with area_temporaria() as tmp:
            repo = self.montar(tmp, '{"registros": ["a_context/d_qa.md"], '
                                    '"tetos": {"a_context/d_qa.md": 500}}',
                               [("a_context/d_qa.md", "---\ntags: [qa]\n---\n# QA\n" + "z" * 600)])
            self.anexar_texto(repo, "a_context/c_decisions.md",
                              "| D-50 | 2026-08-24 | ADOTADO | d_qa.md como registro próprio | x |\n")
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("orçamento declarado", r.stdout)

    def test_config_quebrada_reprova_em_vez_de_valer_o_padrao(self):
        """Teto que o dono acha que declarou e o script ignorou é pior que teto nenhum."""
        with area_temporaria() as tmp:
            repo = self.montar(tmp, '{"tetos": {"a_context/c_decisions.md": ')
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("não é JSON válido", r.stdout)

    def test_sem_config_vale_o_padrao_do_kit(self):
        """Sem `.kit-config.json`, o portão usa os tetos e os avisos padrão.

        Este teste dizia outra coisa até o v13.15: que o KIT não podia ter config nenhuma. A
        afirmação estava certa no espírito e errada no sujeito — quem não pode herdar config é
        o PROJETO gerado (guardado por `test_a_config_do_kit_nao_viaja_para_projeto`), e o
        repositório do kit passou a ter a sua, declarando que ele não é projeto da equipe.
        Teste que fixa o sujeito errado reprova a decisão certa; corrigido aqui, com o motivo
        escrito para não voltar."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            (repo / ".kit-config.json").unlink(missing_ok=True)
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 0, r.stdout)
            # Sem config, os avisos do padrão da equipe voltam ligados: é o que "vale o
            # padrão" significa, e sem esta linha o teste passaria com o portão mudo.
            self.assertIn("padrao da equipe",
                          "".join(c for c in __import__("unicodedata").normalize("NFKD", r.stdout.lower())
                                  if not __import__("unicodedata").combining(c)))

    def anexar_texto(self, repo: Path, rel: str, texto: str):
        p = repo / rel
        p.write_text(p.read_text(encoding="utf-8") + texto, encoding="utf-8")


class TestTravaDoPulo(unittest.TestCase):
    """`git commit --no-verify` era o buraco declarado do próprio relatório de evidência:
    "não fica rastro no histórico". A trava não proíbe o pulo — exige que ele se declare,
    para que o número de contornos deixe de ser desconhecido. Como a trava de escopo, ela
    FALHA ABERTA: bloquear demais ensina a desinstalar o hook."""

    def bater(self, comando, ferramenta="Bash"):
        evento = json.dumps({"cwd": str(KIT), "tool_name": ferramenta,
                             "tool_input": {"command": comando}})
        return subprocess.run([sys.executable, str(KIT / "scripts/portao_hook.py")],
                              input=evento, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", env=AMBIENTE_UTF8, timeout=60)

    def test_bloqueia_pulo_mudo(self):
        r = self.bater('git commit --no-verify -m "fix: sobe rapido"')
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("BLOQUEADO", r.stderr)

    def test_bloqueia_o_atalho_de_uma_letra(self):
        """`-n` é `--no-verify` no git commit, e é a forma que quem tem pressa digita."""
        for comando in ('git commit -n -m "x"', 'git commit -nm "x"'):
            with self.subTest(comando=comando):
                self.assertEqual(self.bater(comando).returncode, 2, comando)

    def test_libera_pulo_declarado(self):
        r = self.bater('git commit --no-verify -m "fix: hotfix  SEM-PORTAO: CI fora do ar"')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_commit_normal_passa(self):
        self.assertEqual(self.bater('git commit -m "FEAT: coisa (D-01)"').returncode, 0)

    def test_falar_do_assunto_nao_e_pular(self):
        """A checagem trabalha sobre palavras separadas, não sobre substring: um commit que
        MENCIONA --no-verify na mensagem não desliga nada, e bloqueá-lo seria aviso falso —
        que é como o kit ensina a ignorar avisos."""
        r = self.bater('git commit -m "docs: explica por que --no-verify deixa rastro"')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_falha_aberta_com_entrada_quebrada(self):
        for entrada in ("", "{isto nao e json", '{"tool_name": "Bash"}'):
            with self.subTest(entrada=entrada):
                r = subprocess.run([sys.executable, str(KIT / "scripts/portao_hook.py")],
                                   input=entrada, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", env=AMBIENTE_UTF8, timeout=60)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_outra_ferramenta_nao_e_assunto(self):
        self.assertEqual(self.bater("git commit --no-verify -m x", ferramenta="Edit").returncode, 0)

    def comando_instalado(self, repo: Path) -> str:
        self.assertEqual(rodar_script("install_hook.py", "--portao", cwd=repo).returncode, 0)
        cfg = json.loads((repo / ".claude/settings.json").read_text(encoding="utf-8"))
        return cfg["hooks"]["PreToolUse"][0]["hooks"][0]["command"]

    def test_o_comando_instalado_funciona_de_outro_diretorio(self):
        """O defeito que isto guarda aconteceu em uso, não em teoria: o comando instalado
        era `python scripts/portao_hook.py`, resolvido contra o diretório de TRABALHO do
        agente. Bastou a sessão passar a trabalhar em outro projeto para o caminho apontar
        para o vazio; o hook morreu, e o Claude Code trata hook morto como BLOQUEIO — a
        sessão ficou sem executar nenhum comando. Hook que bloqueia por bug próprio é
        exatamente o que este kit chama de pior que hook nenhum."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            comando = self.comando_instalado(repo)
            outro = Path(tmp) / "outro_lugar"
            outro.mkdir()
            evento = json.dumps({"cwd": str(repo), "tool_name": "Bash",
                                 "tool_input": {"command": 'git commit --no-verify -m "x"'}})
            # CLAUDE_PROJECT_DIR apontando para ESTE repo: é o que o Claude Code faz, e
            # sem fixá-lo o teste herdaria a variável da sessão que o está rodando —
            # resolvendo para outro kit e passando pelo motivo errado.
            ambiente = dict(AMBIENTE_UTF8, CLAUDE_PROJECT_DIR=str(repo))
            r = subprocess.run(comando, shell=True, input=evento, capture_output=True,
                               text=True, encoding="utf-8", errors="replace",
                               cwd=str(outro), env=ambiente, timeout=60)
            self.assertEqual(r.returncode, 2,
                             f"rodando de {outro}, a trava deveria bloquear:\n{r.stdout}{r.stderr}")

    def test_o_comando_instalado_falha_aberto_se_o_script_sumir(self):
        """Outro clone, outra máquina, arquivo removido: a trava desaparece em silêncio.
        Nunca trava o trabalho — é o que separa 'proteção' de 'armadilha'."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            comando = self.comando_instalado(repo)
            (repo / "scripts/portao_hook.py").unlink()
            evento = json.dumps({"cwd": str(repo), "tool_name": "Bash",
                                 "tool_input": {"command": 'git commit --no-verify -m "x"'}})
            ambiente = dict(AMBIENTE_UTF8, CLAUDE_PROJECT_DIR=str(repo))
            r = subprocess.run(comando, shell=True, input=evento, capture_output=True,
                               text=True, encoding="utf-8", errors="replace",
                               cwd=str(repo), env=ambiente, timeout=60)
            self.assertEqual(r.returncode, 0,
                             f"sem o script, a trava tem de sumir e não travar:\n{r.stdout}{r.stderr}")

    def test_instalar_e_remover_nao_mexe_em_hook_alheio(self):
        """Mesmo contrato da trava de escopo: `.claude/settings.json` pode ter hooks do dono."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            cfg = repo / ".claude/settings.json"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            alheio = {"hooks": {"PreToolUse": [
                {"matcher": "Bash", "hooks": [{"type": "command", "command": "echo do dono"}]}]}}
            cfg.write_text(json.dumps(alheio), encoding="utf-8")
            self.assertEqual(rodar_script("install_hook.py", "--portao", cwd=repo).returncode, 0)
            depois = json.loads(cfg.read_text(encoding="utf-8"))
            self.assertEqual(len(depois["hooks"]["PreToolUse"]), 2)
            self.assertEqual(rodar_script("install_hook.py", "--portao", "--remover",
                                          cwd=repo).returncode, 0)
            final = json.loads(cfg.read_text(encoding="utf-8"))
            self.assertEqual(final["hooks"]["PreToolUse"], alheio["hooks"]["PreToolUse"],
                             "a remoção levou junto o hook do dono")


class TestPadraoDaEquipe(unittest.TestCase):
    """O padrao de commit da equipe (STF PSS) cobrado por maquina.

    O `check.py` NAO consegue cobrar mensagem: ele roda no `pre-commit`, antes de ela existir.
    Por isso o hook e separado, e por isso ele precisa de teste proprio — a peca que o portao
    nao alcanca e exatamente a que ninguem percebe quando para de funcionar."""

    def bater(self, mensagem: str):
        with area_temporaria() as tmp:
            alvo = Path(tmp) / "MSG"
            alvo.write_text(mensagem, encoding="utf-8")
            return subprocess.run([sys.executable, str(KIT / "scripts/mensagem_hook.py"), str(alvo)],
                                  capture_output=True, text=True, encoding="utf-8",
                                  errors="replace", env=AMBIENTE_UTF8, timeout=60)

    def sem_acento(self, s: str) -> str:
        """Compara sem acento DE VERDADE. A primeira versao trocava um codepoint por vez
        (`\u00e3`) e passava a mao em `á` e `é` — teste que erra a normalizacao reprova o
        codigo certo, que e' pior que teste ausente."""
        import unicodedata
        return "".join(c for c in unicodedata.normalize("NFKD", s.lower())
                       if not unicodedata.combining(c))

    def test_formato_certo_passa(self):
        for m in ("OK: Feat: Adicionar endpoint de execucao (D-12)",
                  "NOK: Fix: Tentativa de correcao no timeout",
                  "OK: Chore: Reorganizar pastas do backend"):
            with self.subTest(m=m):
                self.assertEqual(self.bater(m).returncode, 0, m)

    def test_formato_errado_reprova_e_diz_qual_e_o_erro(self):
        casos = {
            "melhorias no kit": "nao esta no formato",
            "feat: coisa nova": "nao e status",
            "ok: Feat: minuscula": "maiuscula",
            "OK: feature: tipo fora da lista": "nao e um tipo",
            "OK: feat: tipo em minuscula": "capitalizado",
        }
        for m, trecho in casos.items():
            with self.subTest(m=m):
                r = self.bater(m)
                self.assertEqual(r.returncode, 1, f"{m!r} deveria reprovar")
                self.assertIn(trecho, self.sem_acento(r.stderr),
                              f"reprovou, mas sem dizer o motivo certo: {r.stderr}")

    def test_mensagem_do_git_passa(self):
        """Merge, revert, fixup e squash sao escritos pelo GIT. Bloquea-los seria bloquear o
        git — e hook que briga com a ferramenta e hook que o dono desinstala."""
        for m in ("Merge branch 'main'", "Revert \"OK: Feat: x\"", "fixup! OK: Fix: y"):
            with self.subTest(m=m):
                self.assertEqual(self.bater(m).returncode, 0, m)

    def test_comentario_e_linha_vazia_nao_contam(self):
        """A mensagem chega com os comentarios do git (`# Please enter...`). Ler a primeira
        linha crua sem filtrar comentario reprovaria todo commit interativo."""
        msg = "\n# comentario do git\nOK: Doc: Escrever guia\n"
        self.assertEqual(self.bater(msg).returncode, 0)

    def test_falha_aberta_sem_arquivo(self):
        r = subprocess.run([sys.executable, str(KIT / "scripts/mensagem_hook.py")],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=AMBIENTE_UTF8, timeout=60)
        self.assertEqual(r.returncode, 0, "sem arquivo de mensagem, tem de liberar")

    def test_instalar_poe_os_dois_hooks_e_remover_leva_os_dois(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.assertEqual(rodar_script("install_hook.py", cwd=repo).returncode, 0)
            hooks = repo / ".git/hooks"
            self.assertTrue((hooks / "pre-commit").exists(), "pre-commit nao instalado")
            self.assertTrue((hooks / "commit-msg").exists(), "commit-msg nao instalado")
            self.assertEqual(rodar_script("install_hook.py", "--remover", cwd=repo).returncode, 0)
            self.assertFalse((hooks / "commit-msg").exists(), "--remover deixou o commit-msg")

    def test_padrao_equipe_granular_liga_um_por_um(self):
        """A chave grossa obrigava a escolher entre ruido e cegueira. O repositorio do proprio
        kit nao e um projeto da equipe — nome e branch fora do padrao estao CERTOS ali —, mas
        as mensagens de commit dele sao lidas por quem avalia o kit, e ali seguir o padrao e o
        ponto. Desligar os tres para calar dois seria desligar o que funciona."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            (repo / ".kit-config.json").write_text(
                '{"padrao_equipe": {"commit": true, "branch": false, "repositorio": false}}',
                encoding="utf-8")
            saida = self.sem_acento(rodar_check(repo).stdout)
            self.assertIn("fora do padrao da equipe `ok|nok", saida,
                          "o aviso de COMMIT deveria continuar ligado")
            self.assertNotIn("branch `", saida, "o aviso de branch deveria estar desligado")
            self.assertNotIn("repositorio `", saida, "o aviso de nome deveria estar desligado")

    def test_padrao_equipe_com_chave_desconhecida_reprova(self):
        """Mesma regra do resto da config: chave que some calada e a doenca, nao o remedio."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            (repo / ".kit-config.json").write_text(
                '{"padrao_equipe": {"comit": true}}', encoding="utf-8")
            r = rodar_check(repo)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("comit", r.stdout)

    def test_a_config_do_kit_nao_viaja_para_projeto(self):
        """A config do kit desliga avisos que num projeto DA EQUIPE sao corretos. Se ela fosse
        copiada, todo projeto novo nasceria cego para o padrao que o kit acabou de adotar."""
        with area_temporaria() as tmp:
            kit = montar_kit(Path(tmp) / "kit")
            (kit / ".kit-config.json").write_text('{"padrao_equipe": false}', encoding="utf-8")
            projeto = Path(tmp) / "projeto"
            self.assertEqual(rodar_script("new_project.py", str(projeto), "--nome", "App",
                                          cwd=kit).returncode, 0)
            self.assertFalse((vault_de(projeto) / ".kit-config.json").exists(),
                             "a config do kit viajou para o projeto")

    def test_avisos_do_padrao_somem_com_padrao_equipe_false(self):
        """Fork, espelho e o proprio kit sao legitimamente fora do padrao. Sem a chave de
        desligar, o aviso vira ruido — e aviso que vira ruido ensina a ignorar aviso."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.assertIn("padrao da equipe", self.sem_acento(rodar_check(repo).stdout),
                          "os avisos do padrao nao apareceram")
            (repo / ".kit-config.json").write_text('{"padrao_equipe": false}', encoding="utf-8")
            self.assertNotIn("padrao da equipe", self.sem_acento(rodar_check(repo).stdout),
                             "a chave nao desligou os avisos")


    def test_o_aviso_muda_de_pedido_quando_a_trava_ja_esta_posta(self):
        """A CONTAGEM nao muda, e isso e decisao: um repositorio que ignora o padrao nao pode
        ficar verde so por ter instalado o hook depois — calar um aviso verdadeiro e a
        "checagem que emudece" com outro nome. O que muda e o PEDIDO. O texto mandava
        "instale a trava" para quem ja a tinha instalado, e aviso que cobra o que ja foi feito
        vira ruido; adotar o padrao hoje nao reescreve o historico de ontem, e o unico ato
        possivel — garantir as mensagens de amanha — ja estava feito."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            git(repo, *GIT_ID, "commit", "-q", "--allow-empty", "-m", "mensagem fora do padrao")

            antes = rodar_check(repo).stdout
            self.assertIn("instale a trava", antes, "sem hook, o pedido correto e instalar")

            self.assertEqual(rodar_script("install_hook.py", cwd=repo).returncode, 0)
            depois = rodar_check(repo).stdout
            self.assertIn("fora do padrao", self.sem_acento(depois),
                          "a CONTAGEM sumiu — isso deixaria verde quem ignora o padrao")
            self.assertNotIn("instale a trava", depois,
                             "continua mandando instalar o que ja esta instalado")
            self.assertIn("cai sozinha", depois, "o novo texto nao explica a saida real")


class TestCongelamento(unittest.TestCase):
    """Congelar é o que torna um experimento honesto: o critério escrito antes do dado.

    O primeiro congelado do kit foi feito à mão, e a mão errou de um jeito que só aparece
    num Windows: o hash saiu da cópia CRLF, o `eol=lf` normalizou o commit, e a instrução de
    verificação escrita dentro do documento passou a acusar de adulteração um arquivo intacto.
    Cada teste aqui guarda uma das formas de um congelamento mentir — acusando quem não
    mexeu, ou calando para quem mexeu."""

    CRITERIO = "d_history/criterio.md"

    def preparar(self, tmp):
        repo = montar_kit(Path(tmp) / "repo")
        (repo / self.CRITERIO).write_text(
            "---\ntags: [criterio]\n---\n# Criterio\nlimiar: 2 de 3\n", encoding="utf-8")
        return repo

    def congelar(self, repo, *args):
        return rodar_script("congelar.py", *args, cwd=repo)

    def sujar(self, repo):
        with (repo / self.CRITERIO).open("a", encoding="utf-8") as f:
            f.write("x")

    def test_congelar_e_depois_conferir_passa(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            r = self.congelar(repo, str(repo / self.CRITERIO))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn(self.CRITERIO, (repo / ".kit-congelados").read_text(encoding="utf-8"))
            c = rodar_check(repo)
            self.assertEqual(c.returncode, 0, c.stdout)

    def test_um_byte_mudado_reprova(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            self.congelar(repo, str(repo / self.CRITERIO))
            self.sujar(repo)
            c = rodar_check(repo)
            self.assertEqual(c.returncode, 1, c.stdout)
            self.assertIn("congelado editado", c.stdout)

    def test_fim_de_linha_nao_e_edicao(self):
        """O defeito que motivou o script, nas DUAS direções: congelado em LF e aberto num
        Windows (CRLF); e congelado numa cópia CRLF e conferido no checkout LF do CI — que é
        exatamente o que aconteceu com o critério do TAP GO. O mesmo conteúdo tem dois sha256
        crus, e congelamento que acusa quem não mexeu ensina a desligá-lo.

        A primeira versão deste teste escrevia o arquivo com `write_text`, que no Windows já
        grava CRLF — e a conversão para CRLF virava CR-CR-LF. O teste acusava o script pelo
        defeito que o script existe para evitar, cometido dentro do próprio teste. Por isso
        os dois estados são montados em BYTES."""
        lf = b"---\ntags: [criterio]\n---\n# Criterio\nlimiar: 2 de 3\n"
        crlf = lf.replace(b"\n", b"\r\n")
        for congelado, conferido, nome in ((lf, crlf, "LF->CRLF"), (crlf, lf, "CRLF->LF")):
            with self.subTest(direcao=nome), area_temporaria() as tmp:
                repo = self.preparar(tmp)
                alvo = repo / self.CRITERIO
                alvo.write_bytes(congelado)
                r = self.congelar(repo, str(alvo))
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                alvo.write_bytes(conferido)
                c = rodar_check(repo)
                self.assertEqual(c.returncode, 0, c.stdout)

    def test_congelado_apagado_reprova(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            self.congelar(repo, str(repo / self.CRITERIO))
            (repo / self.CRITERIO).unlink()
            c = rodar_check(repo)
            self.assertEqual(c.returncode, 1, c.stdout)
            self.assertIn("congelado ausente", c.stdout)

    def test_liberar_exige_motivo_e_deixa_rastro(self):
        """Desistir é permitido; desistir calado, não — o contrato do SEM-PORTAO."""
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            self.congelar(repo, str(repo / self.CRITERIO))
            antes = (repo / ".kit-congelados").read_text(encoding="utf-8")
            r = self.congelar(repo, "--liberar", str(repo / self.CRITERIO))
            self.assertNotEqual(r.returncode, 0, "liberou sem motivo")
            self.assertEqual((repo / ".kit-congelados").read_text(encoding="utf-8"), antes)
            r = self.congelar(repo, "--liberar", str(repo / self.CRITERIO), "limiar mal definido")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            registro = (repo / ".kit-congelados").read_text(encoding="utf-8")
            self.assertIn("LIBERADO", registro)
            self.assertIn("limiar mal definido", registro)
            self.sujar(repo)
            self.assertEqual(rodar_check(repo).returncode, 0, "o liberado continuou cobrado")

    def test_recongelar_com_outro_conteudo_recusa(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            self.congelar(repo, str(repo / self.CRITERIO))
            self.sujar(repo)
            r = self.congelar(repo, str(repo / self.CRITERIO))
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("documento novo", r.stdout)

    def test_registro_ilegivel_reprova(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            (repo / ".kit-congelados").write_text("congelei o criterio ontem\n", encoding="utf-8")
            c = rodar_check(repo)
            self.assertEqual(c.returncode, 1, c.stdout)
            self.assertIn(".kit-congelados", c.stdout)

    def test_fora_do_vault_recusa(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            fora = Path(tmp) / "fora.md"
            fora.write_text("x\n", encoding="utf-8")
            r = self.congelar(repo, str(fora))
            self.assertEqual(r.returncode, 2, r.stdout)
            registro = repo / ".kit-congelados"
            self.assertFalse(registro.exists() and "fora.md" in registro.read_text(encoding="utf-8"))

    def test_evidencia_relata_os_congelados(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            self.congelar(repo, str(repo / self.CRITERIO))
            self.sujar(repo)
            r = rodar_script("evidencia.py", str(repo), "--json")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            dados = json.loads(r.stdout)["instalacao"]["congelados"]
            self.assertIn(self.CRITERIO, dados["editados"])

    def test_projeto_novo_nao_herda_os_congelados_do_kit(self):
        """Os congelados do kit apontam para `docs/`, que não vai para projeto. Herdados,
        fariam o projeto novo nascer reprovando por dois arquivos 'ausentes'."""
        with area_temporaria() as tmp:
            kit = montar_kit(Path(tmp) / "kit")
            destino = Path(tmp) / "novo"
            r = rodar_script("new_project.py", str(destino), "--nome", "App Teste", cwd=kit)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertFalse((vault_de(destino) / ".kit-congelados").exists(),
                             "os congelados do kit vazaram para o projeto")
            self.assertTrue((vault_de(destino) / "scripts/congelar.py").exists(),
                            "o projeto novo não recebeu o congelar.py")

    def test_os_congelados_do_proprio_kit_estao_intactos(self):
        """Os congelados reais do kit — o critério do TAP GO e os critérios do benchmarking —
        conferidos a cada rodada da suíte, em Linux e em Windows."""
        r = rodar_script("congelar.py")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("integro", r.stdout)

    def test_o_criterio_do_tapgo_e_o_mesmo_de_agosto(self):
        """A ponte com o hash antigo. O changelog registrou `a9f129bd…`, calculado sobre a
        cópia CRLF; o registro novo guarda o conteúdo em LF. Se a versão CRLF do arquivo de
        hoje reproduz o hash de agosto, o conteúdo nunca mudou — e a acusação que a instrução
        manual faria hoje é falsa."""
        import hashlib
        atual = (KIT / "docs/f_criterio_conclusao_tapgo_260827.md").read_bytes().replace(b"\r\n", b"\n")
        self.assertEqual(hashlib.sha256(atual.replace(b"\n", b"\r\n")).hexdigest(),
                         "a9f129bd84af97c0f845a7b9c6c96ff0f6b5251386a0edbffb462832fddc8de7")


    # ---- achados da revisão adversarial desta versão, antes do primeiro commit ------------

    def anexar_bytes(self, repo, texto):
        with (repo / ".kit-congelados").open("a", encoding="utf-8", newline="\n") as f:
            f.write(texto)

    def test_cr_cr_lf_sobrevive_ao_commit_e_ao_clone(self):
        """CR-CR-LF no disco vira CR-LF no blob: o git tira UM CR por CRLF. Com a normalização
        antiga, o check local passava e o do CI — que vê o clone — acusava de editado um arquivo
        que ninguém tocou. Aqui o CI é simulado de verdade: commit e git clone."""
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            alvo = repo / "d_history/crcrlf.md"
            alvo.write_bytes(b"---\r\r\ntags: [x]\r\r\n---\r\r\n# Criterio\r\r\nlimiar: 2 de 3\r\r\n")
            self.assertEqual(self.congelar(repo, str(alvo)).returncode, 0)
            git(repo, "add", "-A")
            git(repo, *GIT_ID, "commit", "-qm", "congela")
            clone = Path(tmp) / "clone"
            git(Path(tmp), "clone", "-q", str(repo), str(clone))
            c = rodar_check(clone)
            self.assertEqual(c.returncode, 0, c.stdout)

    def test_task_congelar_usa_a_pasta_de_quem_chama(self):
        """O task.py rodava o congelar no vault: `task.py congelar README.md`, chamado de
        e_qa/, congelava o README.md da RAIZ — e o de e_qa/ ficava editável."""
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            self.assertTrue((repo / "e_qa/README.md").exists())
            r = subprocess.run([sys.executable, str(repo / "scripts/task.py"), "congelar", "README.md"],
                               cwd=str(repo / "e_qa"), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", env=AMBIENTE_UTF8, timeout=120)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            registro = (repo / ".kit-congelados").read_text(encoding="utf-8")
            self.assertIn("| e_qa/README.md", registro)
            self.assertNotIn("| README.md\n", registro)

    def test_arquivo_que_o_gitignore_esconde_nao_se_congela(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            (repo / "backups").mkdir()
            (repo / "backups/crit.md").write_bytes(b"x\n")
            antes = (repo / ".kit-congelados").read_bytes()
            r = self.congelar(repo, str(repo / "backups/crit.md"))
            self.assertNotEqual(r.returncode, 0, r.stdout)
            self.assertIn(".gitignore", r.stdout)
            self.assertEqual((repo / ".kit-congelados").read_bytes(), antes)

    def test_recongelar_a_mao_sem_liberar_reprova(self):
        """O remendo que um agente faz ao ler 'hash não bate': recalcula e anexa."""
        import hashlib
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            self.congelar(repo, str(repo / self.CRITERIO))
            self.sujar(repo)
            novo = hashlib.sha256((repo / self.CRITERIO).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            self.anexar_bytes(repo, f"CONGELADO | {novo} | 2026-09-10 | {self.CRITERIO}\n")
            c = rodar_check(repo)
            self.assertEqual(c.returncode, 1, c.stdout)
            self.assertIn("recongelado", c.stdout)

    def test_comentar_a_linha_reprova(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            self.congelar(repo, str(repo / self.CRITERIO))
            self.sujar(repo)
            reg = repo / ".kit-congelados"
            linhas = reg.read_text(encoding="utf-8").splitlines()
            linhas[-1] = "# " + linhas[-1]
            reg.write_bytes(("\n".join(linhas) + "\n").encode("utf-8"))
            c = rodar_check(repo)
            self.assertEqual(c.returncode, 1, c.stdout)
            self.assertIn("COMENTADO", c.stdout)

    def test_apagar_o_registro_que_esta_no_git_reprova(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            (repo / ".kit-congelados").unlink()
            c = rodar_check(repo)
            self.assertEqual(c.returncode, 1, c.stdout)
            self.assertIn("sumiu do disco", c.stdout)

    def test_editar_linha_antiga_do_registro_reprova(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            reg = repo / ".kit-congelados"
            t = reg.read_bytes().decode("utf-8")
            t2, n = re.subn(r"\| \d{4}-\d{2}-\d{2} \|", "| 1999-01-01 |", t, count=1)
            self.assertEqual(n, 1, "o registro do kit não tem linha com data para editar")
            reg.write_bytes(t2.encode("utf-8"))
            c = rodar_check(repo)
            self.assertEqual(c.returncode, 1, c.stdout)
            self.assertIn("append-only", c.stdout)

    def test_registro_com_bom_passa(self):
        """O PowerShell 5.1 grava UTF-8 com BOM. O BOM não é conteúdo."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            reg = repo / ".kit-congelados"
            reg.write_bytes(b"\xef\xbb\xbf" + reg.read_bytes())
            c = rodar_check(repo)
            self.assertEqual(c.returncode, 0, c.stdout)

    def test_registro_em_cp1252_reprova_com_mensagem_e_sem_traceback(self):
        """Traceback no meio do portão engole todas as outras FALHAs: fecha, mas mudo."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            reg = repo / ".kit-congelados"
            linha = "CONGELADO | " + "0" * 64 + " | 2026-09-10 | d_history/critério.md\n"
            reg.write_bytes(reg.read_bytes() + linha.encode("cp1252"))
            c = rodar_check(repo)
            self.assertEqual(c.returncode, 1, c.stdout + c.stderr)
            self.assertIn("UTF-8", c.stdout)
            self.assertNotIn("Traceback", c.stdout + c.stderr)

    def test_motivo_com_quebra_de_linha_nao_quebra_o_registro(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            self.congelar(repo, str(repo / self.CRITERIO))
            r = self.congelar(repo, "--liberar", str(repo / self.CRITERIO), "linha1\r\nlinha2\u2028fim")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.sujar(repo)
            c = rodar_check(repo)
            self.assertEqual(c.returncode, 0, c.stdout)

    def test_varios_arquivos_de_uma_vez_e_tudo_ou_nada(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            b = repo / "d_history/b.md"
            b.write_bytes(b"b\n")
            r = self.congelar(repo, str(repo / self.CRITERIO), str(b))
            self.assertEqual(r.returncode, 0, r.stdout)
            registro = (repo / ".kit-congelados").read_text(encoding="utf-8")
            self.assertIn(self.CRITERIO, registro)
            self.assertIn("d_history/b.md", registro)
            c = repo / "d_history/c.md"
            c.write_bytes(b"c\n")
            antes = (repo / ".kit-congelados").read_bytes()
            r = self.congelar(repo, str(c), str(repo / "d_history/nao_existe.md"))
            self.assertNotEqual(r.returncode, 0, r.stdout)
            self.assertEqual((repo / ".kit-congelados").read_bytes(), antes, "congelou metade")

    def test_binario_nao_perde_o_cr(self):
        """No binário o git não converte nada: um CR a mais é mudança de verdade."""
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            alvo = repo / "d_history/anexo.bin"
            alvo.write_bytes(b"\x00\x01cabecalho\nresto\n")
            self.assertEqual(self.congelar(repo, str(alvo)).returncode, 0)
            alvo.write_bytes(b"\x00\x01cabecalho\r\nresto\n")
            c = rodar_check(repo)
            self.assertEqual(c.returncode, 1, c.stdout)
            self.assertIn("congelado editado", c.stdout)

    def test_liberado_escrito_a_mao_sem_motivo_reprova(self):
        """O caminho mais provável de um agente contornar: anexar uma linha a um arquivo de
        texto. A CLI sempre grava motivo; quem precisa cobrar a linha escrita à mão é o portão."""
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            self.congelar(repo, str(repo / self.CRITERIO))
            self.anexar_bytes(repo, f"LIBERADO | - | 2026-09-10 | {self.CRITERIO}\n")
            self.sujar(repo)
            c = rodar_check(repo)
            self.assertEqual(c.returncode, 1, c.stdout)
            self.assertIn("sem motivo", c.stdout)

    def test_sem_o_congelar_py_o_portao_falha_fechado(self):
        """Configuração quebrada falha FECHADO: registro sem quem o leia não é 'nada a conferir'."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            (repo / "scripts/congelar.py").unlink()
            c = rodar_check(repo)
            self.assertEqual(c.returncode, 1, c.stdout)
            self.assertIn("NÃO foram conferidos", c.stdout)

    def test_registro_sem_quebra_no_fim_nao_cola_linhas(self):
        with area_temporaria() as tmp:
            repo = self.preparar(tmp)
            reg = repo / ".kit-congelados"
            reg.write_bytes(reg.read_bytes().rstrip(b"\r\n"))
            self.assertEqual(self.congelar(repo, str(repo / self.CRITERIO)).returncode, 0)
            lista = self.congelar(repo)
            self.assertEqual(lista.returncode, 0, lista.stdout)
            self.assertIn(f"integro  {self.CRITERIO}", lista.stdout)
            self.assertEqual(rodar_check(repo).returncode, 0)

    def test_linha_colada_vira_erro_e_nao_caminho_truncado(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            reg = repo / ".kit-congelados"
            reg.write_bytes(reg.read_bytes().rstrip(b"\r\n")
                            + b"CONGELADO | " + b"0" * 64 + b" | 2026-09-10 | d_history/x.md\n")
            c = rodar_check(repo)
            self.assertEqual(c.returncode, 1, c.stdout)
            self.assertIn("campo a mais", c.stdout)


class TestKitInstalado(unittest.TestCase):
    """"O kit tem quatro travas" e "este clone roda quatro travas" são afirmações diferentes.

    O benchmarking de set/2026 creditou ao kit as quatro, e no único projeto real rodava UMA:
    hook de git não viaja com o clone, e nenhum passo de instalação mandava ligar as outras
    três. O relatório de evidência não dizia nada — e todo número dele tinha sido produzido
    com uma trava, não com quatro."""

    def instalacao(self, repo):
        r = rodar_script("evidencia.py", str(repo), "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return json.loads(r.stdout)["instalacao"]

    def sem_config_de_agente(self, repo):
        for nome in ("settings.json", "settings.local.json"):
            cfg = repo / ".claude" / nome
            if cfg.exists():
                cfg.unlink()

    def test_clone_novo_relata_o_que_esta_desligado(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.sem_config_de_agente(repo)
            inst = self.instalacao(repo)
            self.assertEqual(inst["travas_ligadas"], 0, inst)
            self.assertEqual(inst["travas_verificaveis"], 4, inst)
            saida = rodar_script("evidencia.py", str(repo)).stdout
            self.assertIn("travas ligadas: 0 de 4", saida)
            self.assertIn("task.py travas", saida)

    def test_todas_liga_as_quatro_e_repetir_nao_duplica(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.sem_config_de_agente(repo)
            for _ in range(2):
                r = rodar_script("install_hook.py", "--todas", cwd=repo)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(self.instalacao(repo)["travas"],
                             {"pre-commit": True, "commit-msg": True,
                              "escopo": True, "pulo do portão": True})
            texto = (repo / ".claude/settings.json").read_text(encoding="utf-8")
            self.assertEqual(texto.count("escopo_hook.py"), 1, "a trava de escopo duplicou")
            self.assertEqual(texto.count("portao_hook.py"), 1, "a trava do pulo duplicou")

    def test_escopo_e_portao_na_mesma_chamada_ligam_as_duas(self):
        """QA-17: o laço devolvia na primeira trava pedida — `--escopo --portao` ligava só o
        escopo e dizia OK."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.sem_config_de_agente(repo)
            r = rodar_script("install_hook.py", "--escopo", "--portao", cwd=repo)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            travas = self.instalacao(repo)["travas"]
            self.assertTrue(travas["escopo"], travas)
            self.assertTrue(travas["pulo do portão"], "a segunda trava ficou de fora")
            self.assertFalse(travas["pre-commit"],
                             "pedir só as travas de agente não pode instalar hook de git")

    def test_sem_git_diz_nao_verificavel_e_nao_desligada(self):
        """Zero e 'não medido' não dividem a casa (v13.16): sem git, os hooks de commit não
        foram lidos — dizer 'desligados' seria o relatório inventando um fato."""
        with area_temporaria() as tmp:
            repo = Path(tmp) / "repo"
            shutil.copytree(KIT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            inst = self.instalacao(repo)
            self.assertIsNone(inst["travas"]["pre-commit"], inst)
            self.assertIsNone(inst["travas"]["commit-msg"], inst)
            # A cópia leva o .claude/settings.json do kit, com a trava do pulo: sem .git, o
            # censo lê o .claude do próprio vault, e não o da raiz do disco.
            self.assertTrue(inst["travas"]["pulo do portão"], inst)
            self.assertIn("não verificável", rodar_script("evidencia.py", str(repo)).stdout)

    def test_permissao_que_cita_o_script_nao_e_trava(self):
        """O settings.local.json do projeto real tem permissões citando scripts do kit.
        Procurar o nome no texto contaria uma PERMISSÃO como trava."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.sem_config_de_agente(repo)
            (repo / ".claude").mkdir(exist_ok=True)
            (repo / ".claude/settings.local.json").write_text(
                json.dumps({"permissions": {"allow": ["Bash(python scripts/portao_hook.py *)",
                                                      "Bash(python scripts/escopo_hook.py *)"]}}),
                encoding="utf-8")
            travas = self.instalacao(repo)["travas"]
            self.assertFalse(travas["pulo do portão"], travas)
            self.assertFalse(travas["escopo"], travas)

    def test_hook_de_outra_origem_nao_conta(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            (repo / ".git/hooks/pre-commit").write_text("#!/bin/sh\necho oi\n", encoding="utf-8")
            self.assertFalse(self.instalacao(repo)["travas"]["pre-commit"])


    def test_todas_remover_desliga_as_quatro(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.sem_config_de_agente(repo)
            rodar_script("install_hook.py", "--todas", cwd=repo)
            r = rodar_script("install_hook.py", "--todas", "--remover", cwd=repo)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(self.instalacao(repo)["travas"],
                             {"pre-commit": False, "commit-msg": False,
                              "escopo": False, "pulo do portão": False})

    def test_escopo_e_portao_remover_na_mesma_chamada(self):
        """O QA-17 do lado da remoção: o laço antigo removia só a primeira."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.sem_config_de_agente(repo)
            rodar_script("install_hook.py", "--todas", cwd=repo)
            r = rodar_script("install_hook.py", "--escopo", "--portao", "--remover", cwd=repo)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(self.instalacao(repo)["travas"],
                             {"pre-commit": True, "commit-msg": True,
                              "escopo": False, "pulo do portão": False})

    def test_caminho_padrao_nao_liga_travas_de_agente(self):
        """`task.py hook` continua sendo o que era: os dois ganchos de git, e só."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.sem_config_de_agente(repo)
            r = rodar_script("install_hook.py", cwd=repo)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(self.instalacao(repo)["travas"],
                             {"pre-commit": True, "commit-msg": True,
                              "escopo": False, "pulo do portão": False})

    def test_todas_com_pre_commit_alheio_nao_anuncia_sucesso(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.sem_config_de_agente(repo)
            (repo / ".git/hooks/pre-commit").write_text("#!/bin/sh\necho outro\n", encoding="utf-8")
            r = rodar_script("install_hook.py", "--todas", cwd=repo)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("ATENÇÃO", r.stdout)
            self.assertNotIn("commite-o e elas vão junto", r.stdout)


    # ---- achados da lente de travas da revisão adversarial -------------------------------

    def test_trava_cujo_script_sumiu_nao_conta(self):
        """O comando gravado falha aberto quando o script não está no caminho: sai 0 calado.
        Contar a trava pelo nome no settings dava [x] a uma trava que não roda."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.sem_config_de_agente(repo)
            rodar_script("install_hook.py", "--todas", cwd=repo)
            (repo / "scripts/portao_hook.py").unlink()
            inst = self.instalacao(repo)
            self.assertFalse(inst["travas"]["pulo do portão"], inst)
            self.assertTrue(inst["travas"]["escopo"], inst)
            self.assertIn("não existe", rodar_script("evidencia.py", str(repo)).stdout)

    def test_disable_all_hooks_desliga_as_de_agente(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.sem_config_de_agente(repo)
            rodar_script("install_hook.py", "--todas", cwd=repo)
            (repo / ".claude/settings.local.json").write_text('{"disableAllHooks": true}', encoding="utf-8")
            travas = self.instalacao(repo)["travas"]
            self.assertFalse(travas["escopo"], travas)
            self.assertFalse(travas["pulo do portão"], travas)

    def test_settings_ilegivel_nao_vira_desligada(self):
        """Arquivo que existe e não se deixa ler é 'não verificado', não 'desligado'."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.sem_config_de_agente(repo)
            (repo / ".claude").mkdir(exist_ok=True)
            (repo / ".claude/settings.json").write_text('{"hooks": ', encoding="utf-8")
            travas = self.instalacao(repo)["travas"]
            self.assertIsNone(travas["escopo"], travas)
            self.assertIn("ilegível", rodar_script("evidencia.py", str(repo)).stdout)

    def test_settings_com_bom_e_lido(self):
        """O PowerShell 5.1 grava UTF-8 com BOM; o BOM não pode desligar trava nenhuma."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            self.sem_config_de_agente(repo)
            rodar_script("install_hook.py", "--escopo", cwd=repo)
            cfg = repo / ".claude/settings.json"
            cfg.write_bytes(b"\xef\xbb\xbf" + cfg.read_bytes())
            self.assertTrue(self.instalacao(repo)["travas"]["escopo"])

    def test_portao_desligado_nao_promete_reprovar(self):
        """'O portão reprova o próximo commit' com o pre-commit desligado é promessa falsa: o
        commit passa."""
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            with (repo / "docs/f_criterio_conclusao_tapgo_260827.md").open("a", encoding="utf-8") as f:
                f.write("x")
            saida = rodar_script("evidencia.py", str(repo)).stdout
            self.assertNotIn("reprova o próximo commit", saida)
            self.assertIn("o commit", saida)
            self.assertIn("passa, e só o CI pega", saida)

    def test_registro_ilegivel_nao_derruba_o_relatorio(self):
        with area_temporaria() as tmp:
            repo = montar_kit(Path(tmp) / "repo")
            reg = repo / ".kit-congelados"
            reg.unlink()
            reg.mkdir()
            r = rodar_script("evidencia.py", str(repo))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertNotIn("Traceback", r.stderr)

    def test_projeto_com_vault_em_subpasta(self):
        """Vault em e_doc/0_Context: a dica leva o caminho do vault, e as travas do .claude DO
        VAULT — onde uma sessão aberta ali as encontra — são ditas, não ignoradas."""
        with area_temporaria() as tmp:
            kit = montar_kit(Path(tmp) / "kit")
            destino = Path(tmp) / "app"
            r = rodar_script("new_project.py", str(destino), "--nome", "App", cwd=kit)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            git(destino, "init", "-q")
            docs = vault_de(destino)
            (docs / ".claude").mkdir(exist_ok=True)
            (docs / ".claude/settings.json").write_text(json.dumps({"hooks": {"PreToolUse": [
                {"matcher": "Bash", "hooks": [{"type": "command",
                                               "command": "python scripts/portao_hook.py"}]}]}}),
                encoding="utf-8")
            saida = rodar_script("evidencia.py", str(docs), cwd=docs).stdout
            prefixo = docs.relative_to(destino).as_posix()
            self.assertIn(f"python {prefixo}/scripts/task.py travas", saida)
            self.assertIn("NO VAULT", saida)


class TestAsDuasCasasDoVault(unittest.TestCase):
    """Desde o v13.14 o vault nasce em `e_doc/0_Context/` (padrao da equipe). A casa antiga,
    `*_Project_DOCs/`, PRECISA continuar reconhecida: o unico projeto real construido com este
    kit esta nela, e atualizacao que deixa de achar o projeto que ela mesma criou nao e
    atualizacao, e abandono. Estes testes guardam as DUAS casas — a nova porque e o padrao, a
    velha porque e a promessa."""

    def montar(self, tmp, antiga=False):
        kit = montar_kit(Path(tmp) / "kit")
        projeto = Path(tmp) / "projeto"
        r = rodar_script("new_project.py", str(projeto), "--nome", "App", cwd=kit)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        if antiga:
            (projeto / "e_doc" / "0_Context").rename(projeto / "77777777_APP_Project_DOCs")
        # `git init` nao e detalhe: sem repositorio, o `check.py` cai para o vault como topo,
        # e entao o `.gitignore` e o `CLAUDE.md` — que moram na RAIZ do projeto — ficam fora
        # da varredura. O portao reprovaria por ausencia de arquivo que existe.
        git(projeto, "init", "-q")
        git(projeto, "add", "-A")
        git(projeto, *GIT_ID, "commit", "-qm", "OK: Chore: Estrutura inicial")
        return projeto

    def test_nasce_na_casa_do_padrao_da_equipe(self):
        with area_temporaria() as tmp:
            projeto = self.montar(tmp)
            self.assertTrue((projeto / "e_doc/0_Context/a_context").is_dir(),
                            "o vault nao nasceu em e_doc/0_Context")
            for pasta in ("a_backend/a_code", "d_test/b_test_unit", "f_infra/a_docker", "z_mis"):
                self.assertTrue((projeto / pasta).is_dir(), f"{pasta} nao foi criada")
                self.assertTrue((projeto / pasta / "LEIA-ME.md").exists(),
                                f"{pasta} nasceu vazia — o git nao versiona pasta vazia")

    def test_o_portao_acha_o_vault_nas_duas_casas(self):
        for antiga in (False, True):
            with self.subTest(casa="antiga" if antiga else "equipe"), area_temporaria() as tmp:
                projeto = self.montar(tmp, antiga=antiga)
                vault = vault_de(projeto)
                r = rodar_check(projeto, script=vault / "scripts/check.py")
                self.assertNotIn("nao achei", r.stdout.lower())
                self.assertIn("OK:", r.stdout, r.stdout)

    def test_evidencia_e_upgrade_acham_o_vault_nas_duas_casas(self):
        for antiga in (False, True):
            with self.subTest(casa="antiga" if antiga else "equipe"), area_temporaria() as tmp:
                projeto = self.montar(tmp, antiga=antiga)
                kit = Path(tmp) / "kit"
                r = rodar_script("evidencia.py", str(projeto), cwd=kit)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn("EVID", r.stdout)
                r2 = rodar_script("new_project.py", "--upgrade", str(projeto), "--simular", cwd=kit)
                self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
                self.assertNotIn("nao achei", r2.stdout.lower())


class TestAsQuatroBuscasDoVault(unittest.TestCase):
    """As QUATRO implementacoes de `achar_vault` tem de concordar onde devem concordar.

    Elas divergem de proposito, e a divergencia e' legitima: o `check.py` REPROVA quando acha
    duas pastas candidatas (o padrao pede uma so); o `evidencia.py` e o `arquivar.py` seguem
    em frente; o `escopo_hook.py` SOBE a arvore oito niveis, porque roda como hook e nao sabe
    de onde foi chamado. Nenhuma pode virar copia da outra.

    O que elas NAO podem fazer e' discordar sobre onde o vault esta nos layouts que o kit de
    fato usa. Isso ja custou um bug: no v13.14 o vault mudou de `*_Project_DOCs/` para
    `e_doc/0_Context/`, e o hook de escopo continuou comparando o NOME da pasta em vez do
    CAMINHO — passaria a bloquear toda escrita na documentacao, ou seja, a impedir o fecho de
    sessao que o proprio kit exige. Quando o layout mudar de novo, este teste e' quem lembra
    que ha quatro lugares para acertar, e nao um.

    Por que um TESTE e nao um modulo compartilhado: o kit ja tem a licao "duplicata nao vira
    verdade por ganhar um guarda — o certo e' matar a copia, um le do outro". Aqui matar a
    copia e' impedido pelo mecanismo: o `.claude/settings.json` carrega o hook com
    `runpy.run_path`, que NAO poe a pasta do script no caminho de busca, entao
    `import _comum` levanta ModuleNotFoundError — e hook que quebra ao carregar bloqueia
    TODA chamada de ferramenta (ja aconteceu com a trava do pulo). Quando matar a copia e'
    impossivel, o guarda e' a unica opcao que sobra. E ele guarda COMPORTAMENTO, nao texto:
    as quatro continuam livres para divergir no que devem.
    """

    ESPERADAS = 4

    def buscas(self):
        """Descobre TODA funcao `achar_vault` de `scripts/`, em vez de listar os arquivos a
        mao: script novo que ganhar a sua propria copia entra no teste sozinho — que e' o
        modo de falha que este arquivo existe para pegar."""
        achadas = {}
        for arq in sorted(Path(KIT / "scripts").glob("*.py")):
            if arq.name == "test_check.py":
                continue
            src = arq.read_text(encoding="utf-8")
            arvore = ast.parse(src)
            alvo = next((n for n in arvore.body
                         if isinstance(n, ast.FunctionDef) and n.name == "achar_vault"), None)
            if alvo is None:
                continue
            # Namespace com o que a funcao possa precisar: os imports usuais e as constantes
            # simples do proprio modulo (o hook de escopo usa BACKLOG).
            ns = {"Path": Path, "sys": sys, "re": re, "os": os, "subprocess": subprocess}
            for no in arvore.body:
                if (isinstance(no, ast.Assign) and len(no.targets) == 1
                        and isinstance(no.targets[0], ast.Name)
                        and isinstance(no.value, ast.Constant)):
                    ns[no.targets[0].id] = no.value.value
            exec(compile(ast.Module(body=[alvo], type_ignores=[]), arq.name, "exec"), ns)
            achadas[arq.name] = ns["achar_vault"]
        return achadas

    def montar_layouts(self, base: Path):
        """Os tres layouts que existem de verdade, cada um com o vault que a resposta certa
        aponta. O `c_backlog.md` nao e' enfeite: o hook de escopo so reconhece o vault se ele
        estiver la."""
        casas = {}
        for rotulo, dono, dentro in (
            ("casa nova (padrao da equipe)", "nova", "e_doc/0_Context"),
            ("casa antiga (*_Project_DOCs)", "velha", "77777777_APP_Project_DOCs"),
            ("o proprio kit (vault = raiz)", "kit", ""),
        ):
            raiz = base / dono
            vault = raiz / dentro if dentro else raiz
            (vault / "a_context").mkdir(parents=True)
            (vault / "b_process").mkdir(parents=True)
            (vault / "b_process/c_backlog.md").write_text("x", encoding="utf-8")
            casas[rotulo] = (raiz, vault)
        return casas

    def test_encontrou_todas_as_copias(self):
        achadas = self.buscas()
        self.assertGreaterEqual(
            len(achadas), self.ESPERADAS,
            "o teste achou menos copias de achar_vault do que existem (" + str(sorted(achadas))
            + "). Se uma foi renomeada, este guarda passou a vigiar menos do que pensa — "
            "que e' a doenca da checagem que emudece.")

    def test_as_quatro_concordam_nos_layouts_reais(self):
        achadas = self.buscas()
        with area_temporaria() as tmp:
            casas = self.montar_layouts(Path(tmp))
            for rotulo, (entrada, esperado) in casas.items():
                for arq, funcao in achadas.items():
                    with self.subTest(layout=rotulo, script=arq):
                        try:
                            devolveu = funcao(entrada)
                        except SystemExit:
                            self.fail(arq + " REPROVOU num layout legitimo (" + rotulo + ")")
                        self.assertIsNotNone(
                            devolveu, arq + " nao achou o vault em " + rotulo)
                        self.assertEqual(
                            Path(devolveu).resolve(), esperado.resolve(),
                            arq + " discorda das outras em " + rotulo + ": achou "
                            + str(devolveu) + ", esperado " + str(esperado)
                            + ". Sao QUATRO copias de achar_vault e todas precisam saber do "
                            "mesmo layout — foi assim que o v13.14 quebrou o hook de escopo.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
