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
import re
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
            docs = next(projeto.glob("*_Project_DOCs"))
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
            docs = next(projeto.glob("*_Project_DOCs"))
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

        m2 = re.search(r"julga \*\*(\d+)\*\* deles \((\d+) reprovam o commit, (\d+) avisam\)", readme)
        self.assertIsNotNone(m2, "a frase de cobertura do script sumiu do README")
        decl_soma, decl_falhas, decl_avisos = (int(g) for g in m2.groups())
        self.assertEqual(decl_avisos, avisos,
                         f"README diz {decl_avisos} avisos; o cabeçalho lista {avisos}")
        self.assertEqual(decl_soma, falhas + avisos, "o total julgado não soma")
        self.assertEqual(decl_falhas, falhas,
                         f"README diz {decl_falhas} falhas; o cabeçalho do check.py numera {falhas}")


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
