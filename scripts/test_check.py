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

O teste do acento é o motivo de este arquivo rodar em CI no Windows: num Linux com
locale UTF-8 o bug do QA-01 NÃO reproduz — foi exatamente esse falso "passou" que fez
a auditoria original medir errado.
"""
import ast
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
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
            docs = next(destino.glob("*_Project_DOCs"))
            self.assertFalse((docs / "docs").exists(), "auditoria do kit vazou para o projeto")
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
        docs = next(projeto.glob("*_Project_DOCs"))
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
            nova.write_text("---\nname: skill-nova\ndescription: nova\n---\n# nova\n", encoding="utf-8")
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
            nova.write_text("---\nname: skill-nova\ndescription: nova\n---\n# nova\n", encoding="utf-8")

            r = rodar_script("new_project.py", str(projeto), "--upgrade", "--dry-run", cwd=kit)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertFalse((docs / "b_process/skills/skill-nova/SKILL.md").exists(),
                             "--dry-run escreveu; ele existe justamente para não escrever")

            (projeto / "sujo.txt").write_text("x", encoding="utf-8")
            r2 = rodar_script("new_project.py", str(projeto), "--upgrade", cwd=kit)
            self.assertEqual(r2.returncode, 1, "aceitou atualizar sobre árvore suja")
            self.assertIn("não commitadas", r2.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
