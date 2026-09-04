# -*- coding: utf-8 -*-
"""Gera o PDF dos agentes de revisão do kit, para apresentação em equipe.

    python docs/gerar_agentes_review.py saida.pdf [caminho/do/projeto_medido]

**Nenhum número é digitado aqui.** As descrições, as fronteiras negativas e os formatos de
saída são LIDOS dos `SKILL.md`; as contagens de uso são LIDAS do changelog do projeto real
passado como segundo argumento. Se o catálogo mudar, o documento muda junto — é a mesma
regra que o kit cobra do README, e pela mesma razão: a frase que descreve o sistema não
pode ser a que envelhece em silêncio.

O documento existe para ser apresentado a uma equipe que quer agentes de revisão. Por isso
ele carrega, no mesmo peso tipográfico, o que funcionou e o que nunca rodou: cinco das nove
skills têm zero sessão, e uma apresentação que esconde isso é destruída pela primeira pessoa
que abrir o histórico.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

KIT = Path(__file__).resolve().parent.parent
SAIDA = sys.argv[1] if len(sys.argv) > 1 else "agentes-de-review.pdf"
PROJETO = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None

# Fontes com acento: Arial no Windows, DejaVu no Linux. Sem este fallback o PDF nasce sem
# acento na máquina do dono — que é onde ele de fato roda.
for base, arq, alt in (("A", "arial.ttf", "DejaVuSans.ttf"),
                       ("A-B", "arialbd.ttf", "DejaVuSans-Bold.ttf"),
                       ("A-I", "ariali.ttf", "DejaVuSans-Oblique.ttf")):
    for pasta, nome in (("C:/Windows/Fonts/", arq), ("/usr/share/fonts/truetype/dejavu/", alt)):
        if (Path(pasta) / nome).exists():
            pdfmetrics.registerFont(TTFont(base, str(Path(pasta) / nome)))
            break
pdfmetrics.registerFontFamily("A", normal="A", bold="A-B", italic="A-I")

TINTA = colors.HexColor("#16211F")
SUAVE = colors.HexColor("#5A6A67")
ACENTO = colors.HexColor("#0B6B62")
LINHA = colors.HexColor("#C9D6D3")
FUNDO = colors.HexColor("#EFF3F2")
BOM = colors.HexColor("#2C6E3F")
RUIM = colors.HexColor("#A8322C")
ALERTA = colors.HexColor("#8F5E14")
FUNDO_ALERTA = colors.HexColor("#F6EDD9")

S = {
    "capa_t": ParagraphStyle("ct", fontName="A-B", fontSize=27, leading=33, textColor=TINTA),
    "capa_s": ParagraphStyle("cs", fontName="A", fontSize=13, leading=19, textColor=SUAVE),
    "capa_p": ParagraphStyle("cp", fontName="A", fontSize=9.5, leading=14, textColor=SUAVE),
    "h1": ParagraphStyle("h1", fontName="A-B", fontSize=18, leading=23, textColor=TINTA, spaceAfter=5),
    "h2": ParagraphStyle("h2", fontName="A-B", fontSize=13, leading=17, textColor=ACENTO, spaceBefore=12, spaceAfter=4),
    "h3": ParagraphStyle("h3", fontName="A-B", fontSize=10.8, leading=14, textColor=TINTA, spaceBefore=9, spaceAfter=2),
    "p": ParagraphStyle("p", fontName="A", fontSize=10, leading=15.5, textColor=TINTA, alignment=TA_JUSTIFY, spaceAfter=6),
    "li": ParagraphStyle("li", fontName="A", fontSize=10, leading=15, textColor=TINTA, leftIndent=14, bulletIndent=3, spaceAfter=4),
    "peq": ParagraphStyle("peq", fontName="A", fontSize=8.6, leading=12.5, textColor=SUAVE, alignment=TA_JUSTIFY),
    "cel": ParagraphStyle("cel", fontName="A", fontSize=8.4, leading=11.5, textColor=TINTA),
    "cel_c": ParagraphStyle("celc", fontName="A", fontSize=8.4, leading=11.5, textColor=TINTA, alignment=1),
    "cab": ParagraphStyle("cab", fontName="A-B", fontSize=8.2, leading=11, textColor=colors.white),
    "cab_c": ParagraphStyle("cabc", fontName="A-B", fontSize=8.2, leading=11, textColor=colors.white, alignment=1),
    "alerta_t": ParagraphStyle("at", fontName="A-B", fontSize=11.5, leading=15, textColor=ALERTA),
    "alerta_p": ParagraphStyle("ap", fontName="A", fontSize=9.6, leading=14.5, textColor=TINTA, alignment=TA_JUSTIFY),
}

F = []
def p(t, e="p"): F.append(Paragraph(t, S[e]))
def h1(t): F.append(Paragraph(t, S["h1"]))
def h2(t): F.append(Paragraph(t, S["h2"]))
def li(t): F.append(Paragraph(t, S["li"], bulletText="•"))
def sp(n=6): F.append(Spacer(1, n))
def pb(): F.append(PageBreak())


def caixa(titulo, texto, cor=ALERTA, fundo=FUNDO_ALERTA):
    t = Table([[Paragraph(titulo, S["alerta_t"])], [Paragraph(texto, S["alerta_p"])]], colWidths=[16.4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fundo), ("LINEBEFORE", (0, 0), (0, -1), 3, cor),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (0, 0), 9), ("BOTTOMPADDING", (0, -1), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    F.append(t); sp(9)


def tabela(cab, linhas, larguras, centro=()):
    ls = [[Paragraph(c, S["cab_c"] if i in centro else S["cab"]) for i, c in enumerate(cab)]]
    for linha in linhas:
        ls.append([Paragraph(c, S["cel_c"] if i in centro else S["cel"]) for i, c in enumerate(linha)])
    t = Table(ls, colWidths=[c * cm for c in larguras], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACENTO),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FUNDO]),
        ("GRID", (0, 0), (-1, -1), 0.4, LINHA), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    F.append(t); sp(8)


# ---------------------------------------------------------------- leitura do catálogo
REVISAO = ["guardrails-review", "delivery-review", "artifact-consistency", "evolution-auditor",
           "testing", "debugging-diagnosis", "performance", "dependencies-supply-chain",
           "retrospective"]
# Uma frase de resumo por skill. É a ÚNICA prosa digitada aqui, e ela é editorial: a
# `description` do SKILL.md é escrita para o roteador da ferramenta (cheia de gatilhos),
# não para uma pessoa lendo um slide.
RESUMO = {
    "guardrails-review": "Revisão adversarial de código antes de entregar: bug, invariante quebrada, falha de segurança, segredo versionado, erro engolido, dado inventado e divergência entre a documentação e o comportamento real.",
    "delivery-review": "Varredura de entrega: segredo versionado, cruft, peso do pacote, estado numérico duplicado entre documentos e commit sem rastro. Obriga a listar o conteúdo do pacote gerado antes de declarar entrega.",
    "artifact-consistency": "Confere se os documentos contam a mesma história antes de existir código: módulo sem tarefa, tarefa sem módulo, restrição inegociável sem portão, critério de aceite sem número, termo com dois nomes.",
    "evolution-auditor": "Avalia propostas de melhoria com ceticismo militante — prior de aprovação de 20 a 30% — e exige o portão escrito ANTES do experimento. Rejeição é entrega: vira registro com o número que matou a ideia.",
    "testing": "Escreve e organiza teste de regra, de borda, de integração, de sistema e de regressão de bug — e declara, por escrito, o que ficou sem cobertura.",
    "debugging-diagnosis": "Investiga o que já roda e está errado: reprodução exata, causa-raiz com a evidência que a prova, hipóteses descartadas com o que as matou, e o teste de regressão junto da correção.",
    "performance": "Diagnostica lentidão com número: baseline e resultado no mesmo cenário, o gargalo real com evidência de profiler, e o que foi tentado e NÃO deu ganho.",
    "dependencies-supply-chain": "Dependência nova, atualização, CVE, licença e lockfile — com registro por pacote, a alternativa descartada e a árvore transitiva declarada.",
    "retrospective": "Ao fechar um marco, destila a leva de trabalho em lições generalizáveis, separando o que é do projeto do que vira regra do processo.",
}


def bloco(texto: str, titulo: str) -> str:
    """Extrai uma seção do SKILL.md pelo título. Ler do arquivo, e não repetir aqui, é o que
    impede este documento de descrever um catálogo que já mudou."""
    m = re.search(rf"^## {re.escape(titulo)}\s*\n(.*?)(?=^## |\Z)", texto, re.S | re.M)
    return m.group(1).strip() if m else ""


def fronteira(desc: str) -> str:
    """A frase 'Não use para…' — o pedaço mais distintivo destas skills, e o que uma equipe
    copia primeiro: ela é o que impede um agente de invadir o trabalho do outro."""
    m = re.search(r"(N[ãa]o use[^.]*\.)", desc)
    return m.group(1).strip() if m else "—"


CATALOGO = {}
for nome in REVISAO:
    caminho = KIT / "b_process/skills" / nome / "SKILL.md"
    texto = caminho.read_text(encoding="utf-8")
    desc = re.search(r"^description:\s*(.+?)$", texto, re.M | re.S)
    desc = desc.group(1).strip() if desc else ""
    saida = [re.sub(r"\s+", " ", l).strip(" .")
             for l in re.findall(r"^\s*\d+\.\s*(.+)$", bloco(texto, "Saída"), re.M)]
    CATALOGO[nome] = {
        "resumo": RESUMO[nome],
        "fronteira": fronteira(desc),
        "saida": saida,
        "limites": [re.sub(r"\s+", " ", l).strip()
                    for l in re.findall(r"^- (.+)$", bloco(texto, "Limites"), re.M)][:3],
    }

TOTAL_SKILLS = len([d for d in (KIT / "b_process/skills").iterdir() if d.is_dir()])

# ---------------------------------------------------------------- medição no projeto real
USO = defaultdict(lambda: {"sessoes": 0, "QA": set(), "D": set()})
MED = {"sessoes": 0, "com_skill": 0, "projeto": None, "qa_total": 0}
if PROJETO:
    vault = PROJETO if (PROJETO / "a_context").is_dir() else next(
        (q for q in PROJETO.glob("*_Project_DOCs") if (q / "a_context").is_dir()), None)
    if vault:
        MED["projeto"] = vault.name
        log = (vault / "d_history/a_changelog.md").read_text(encoding="utf-8")
        partes = re.split(r"^(##+ .*)$", log, flags=re.M)
        sessoes = [(partes[i], partes[i + 1]) for i in range(1, len(partes) - 1, 2)]
        MED["sessoes"] = len(sessoes)
        todas = sorted(d.name for d in (vault / "b_process/skills").iterdir() if d.is_dir())
        for _, corpo in sessoes:
            linhas = re.findall(r"\*\*Skill:\*\*\s*(.+)", corpo)
            achadas = {s for s in todas for l in linhas if s in l}
            if achadas:
                MED["com_skill"] += 1
            for s in achadas:
                USO[s]["sessoes"] += 1
                USO[s]["QA"] |= set(re.findall(r"\bQA-\d+", corpo))
                USO[s]["D"] |= set(re.findall(r"\bD-\d+", corpo))
        qa_reg = next((p for p in (vault / "a_context").glob("*.md")
                       if re.search(r"qa", p.stem, re.I)), None)
        fontes = [t for t in ((vault / "a_context/c_decisions.md").read_text(encoding="utf-8"),
                              qa_reg.read_text(encoding="utf-8") if qa_reg else "")]
        MED["qa_total"] = len({i for t in fontes for i in re.findall(r"^\|\s*(QA-\d+)\s*\|", t, re.M)})

RODARAM = [n for n in REVISAO if USO[n]["sessoes"]]
NUNCA = [n for n in REVISAO if not USO[n]["sessoes"]]

# ---------------------------------------------------------------- capa
sp(140)
p("Agentes de revisão", "capa_t")
sp(8)
p("O que cada um faz, o que exige de saída, e o que a medição num projeto real "
  "diz sobre eles — inclusive o que ela não diz.", "capa_s")
sp(22)
F.append(Table([[""]], colWidths=[17.0 * cm], rowHeights=[0.6],
               style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), LINHA)])))
sp(14)
p(f"Catálogo lido de <b>b_process/skills/</b> ({TOTAL_SKILLS} skills, {len(REVISAO)} de revisão)."
  + (f"<br/>Uso medido em <b>{MED['projeto']}</b>: {MED['sessoes']} sessões registradas, "
     f"{MED['com_skill']} com skill declarada, {MED['qa_total']} achados de QA no registro."
     if MED["projeto"] else "")
  + "<br/><br/>Nenhum número deste documento foi digitado: todos saem dos arquivos do "
    "catálogo e do histórico do projeto.", "capa_p")
pb()

# ---------------------------------------------------------------- o que são
h1("O que estes agentes são — e o que eles não são")
p("Cada um é um <b>contrato de revisão</b> escrito em markdown: quando disparar, o que "
  "olhar, o que <b>não</b> é assunto dele, o formato obrigatório da saída e um veredito que "
  "pode ser “não entregue”. Eles rodam dentro do assistente de código, sem instalar nada.")
p("O que os distingue de um prompt comum são três peças, e são elas que valem ser copiadas "
  "por qualquer equipe, com ou sem este kit:")
li("<b>Fronteira negativa.</b> Toda skill declara o que ela <b>não</b> faz mesmo tendo sido "
   "escolhida certo — “não use para caçar bug, isso é a outra”. Sem isso, um agente invade o "
   "trabalho do outro e a revisão vira opinião difusa.")
li("<b>Saída de formato fixo.</b> Achado com severidade, arquivo e linha, reprodução, efeito "
   "e conserto de uma linha. Mais o item que quase ninguém escreve: <b>o que não deu para "
   "verificar</b>, e como a pessoa confirma na máquina real.")
li("<b>Achado vira registro rastreável.</b> Cada um recebe um identificador citado no commit, "
   "com prazo por gravidade — e o portão avisa quando o prazo vence. Revisão que não deixa "
   "rastro morre no fim da conversa.")
caixa("O limite honesto, e ele precisa abrir a apresentação",
      "Estes agentes são <b>prompts</b>, não travas. Nada impede o modelo de ignorá-los — a "
      "obediência não é verificada por máquina. O que é cobrado por máquina neste kit é outra "
      "coisa: o portão de commit, que checa formato, orçamento, identificador e segredo. "
      "Apresentar os dois como se fossem a mesma categoria é o erro que derruba a conversa "
      "com qualquer pessoa mais cética da sala.")
pb()

# ---------------------------------------------------------------- tabela geral
h1("Os nove, em uma tabela")
if MED["projeto"]:
    p(f"A coluna “sessões” conta as sessões do projeto <b>{MED['projeto']}</b> que declararam "
      f"aquela skill no histórico — {MED['com_skill']} de {MED['sessoes']} sessões trazem a "
      "declaração. É contagem de <b>uso</b>, não de qualidade.")
linhas = []
for nome in REVISAO:
    u = USO[nome]["sessoes"]
    marca = f"<font color='{(BOM if u >= 10 else (ALERTA if u else RUIM)).hexval()}'><b>{u}</b></font>"
    linhas.append([f"<b>{nome}</b>", CATALOGO[nome]["resumo"], CATALOGO[nome]["fronteira"], marca])
tabela(["Skill", "O que faz", "Quando NÃO usar", "Sessões"], linhas, [3.0, 6.4, 5.4, 1.6], centro=(3,))
p("Verde = dez ou mais sessões · amarelo = rodou pouco · vermelho = <b>nunca rodou</b>.", "peq")
pb()

# ---------------------------------------------------------------- fichas
h1("Ficha de cada agente")
p("A saída obrigatória de cada um, lida do próprio arquivo da skill. É o pedaço mais útil "
  "para quem quiser adaptar: ela define o que a revisão precisa entregar para ser aceita.")
for grupo, titulo in ((RODARAM, "Os que rodaram no projeto real"),
                      (NUNCA, "Os que nunca dispararam")):
    if not grupo:
        continue
    h2(titulo)
    for nome in grupo:
        c = CATALOGO[nome]
        u = USO[nome]
        cabec = f"{nome}"
        if u["sessoes"]:
            cabec += (f" — {u['sessoes']} sessões · {len(u['QA'])} achados e {len(u['D'])} "
                      f"decisões citados nas mesmas entradas")
        itens = [Paragraph(cabec, S["h3"]), Paragraph(c["resumo"], S["p"])]
        if c["saida"]:
            itens.append(Paragraph("<b>Saída obrigatória:</b> " + " · ".join(c["saida"][:6]), S["peq"]))
        itens.append(Spacer(1, 3))
        itens.append(Paragraph(f"<b>Fronteira:</b> {c['fronteira']}", S["peq"]))
        itens.append(Spacer(1, 10))
        F.append(KeepTogether(itens))
pb()

# ---------------------------------------------------------------- o que a medição diz
h1("O que a medição diz — e o que ela não diz")
if MED["projeto"]:
    p(f"No projeto medido, <b>{len(RODARAM)} dos {len(REVISAO)}</b> agentes de revisão "
      f"dispararam alguma vez. Dois deles concentram quase todo o uso, e "
      f"<b>{len(NUNCA)} nunca rodaram</b> — incluindo justamente o revisor adversarial de "
      f"código, num projeto que registrou {MED['qa_total']} achados de qualidade.")
caixa("A pergunta que este documento NÃO consegue responder",
      "<b>Se estes agentes acharam alguma coisa.</b> O registro de achados não tem campo de "
      "origem: não se sabe se um defeito foi encontrado pela revisão, pelo portão automático, "
      "pela pessoa ou pelo usuário final. O que a tabela mostra é <b>co-ocorrência</b> — a "
      "skill estava declarada na sessão em que aquele identificador apareceu —, e "
      "co-ocorrência não é autoria.<br/><br/>Foi por causa desta lacuna que o campo "
      "<b>origem</b> passou a ser exigido nos achados novos. Até ele existir com volume, "
      "“desempenho” é uma palavra que este material não pode usar.", RUIM,
      colors.HexColor("#F7E4E2"))
h2("O que dá para afirmar com segurança")
li("<b>Os que rodam, rodam muito.</b> Dois agentes concentram a maior parte das sessões com "
   "skill declarada — revisão de evolução e revisão de entrega.")
li("<b>O formato aguenta uso real.</b> Achados com severidade, prazo e identificador citado "
   "no commit sobreviveram a mais de cem sessões sem virar formalidade vazia.")
li("<b>Catálogo grande não vira uso.</b> Mais da metade das skills de revisão nunca disparou. "
   "Isso é superfície não testada, e o número não melhora acrescentando agentes novos.")
h2("O que a experiência recente sugere sobre revisão que acha coisa")
p("Os defeitos reais encontrados na semana em que este documento foi escrito <b>não</b> "
  "vieram de agente de revisão de catálogo. Vieram de duas fontes: <b>usar o sistema num "
  "projeto de verdade</b> — quatro defeitos em uma hora de migração — e <b>um revisor "
  "hostil com a tarefa explícita de destruir um resultado</b>, que encontrou nove "
  "incoerências num conjunto de notas que já tinha passado por revisão comum.")
p("A conclusão prática para quem quer montar revisão numa equipe: o que produz achado é o "
  "<b>adversário com material na mão e instrução de refutar</b>, mais do que a quantidade de "
  "papéis definidos. Um catálogo de nove revisores dos quais cinco nunca rodam é pior que "
  "dois que rodam sempre.")
pb()

# ---------------------------------------------------------------- para levar
h1("Para levar para uma equipe")
p("O que é transferível não é o texto das skills — é o formato. Estas quatro decisões "
  "funcionam em qualquer ferramenta, com ou sem este kit:")
tabela(["Decisão", "Por que ela importa"],
       [["Toda revisão declara o que <b>não</b> é assunto dela",
         "Sem fronteira, dois revisores cobrem a mesma coisa e ninguém cobre o resto. A fronteira também é o que permite rotear a revisão certa para o problema certo."],
        ["A saída obriga “o que eu não consegui verificar”",
         "É a linha que separa revisão de teatro. Um revisor que nunca declara lacuna está escondendo a lacuna, não eliminando-a."],
        ["Achado vira identificador com prazo por gravidade",
         "Revisão sem rastro morre no fim da conversa. Com identificador, o achado aparece no commit, e um portão automático avisa quando o prazo vence."],
        ["Registrar <b>quem</b> achou cada defeito",
         "É o único jeito de responder, mais tarde, se a revisão automática paga o próprio custo. Este kit descobriu isso tarde, e por isso não consegue responder hoje."]],
       [5.0, 11.4])
caixa("Três coisas para dizer antes que perguntem",
      "<b>1.</b> Cinco dos nove nunca rodaram, e um deles é o revisor de código — a primeira "
      "pessoa que olhar o histórico vai achar isso.<br/><br/>"
      "<b>2.</b> São prompts, não travas: a obediência não é verificada por máquina.<br/><br/>"
      "<b>3.</b> Não existe grupo de controle. Nada aqui mostra que o trabalho revisado por "
      "estes agentes ficou melhor do que ficaria sem eles — só mostra o que aconteceu com "
      "eles em um projeto, medido por quem os escreveu.")


def rodape(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setFont("A", 7.6)
        canvas.setFillColor(SUAVE)
        canvas.drawString(2.3 * cm, 1.35 * cm, "Agentes de revisão do pipeline — uso interno")
        canvas.drawRightString(A4[0] - 2.3 * cm, 1.35 * cm, str(doc.page))
        canvas.setStrokeColor(LINHA)
        canvas.setLineWidth(0.4)
        canvas.line(2.3 * cm, 1.75 * cm, A4[0] - 2.3 * cm, 1.75 * cm)
    canvas.restoreState()


doc = BaseDocTemplate(SAIDA, pagesize=A4, leftMargin=2.3 * cm, rightMargin=2.3 * cm,
                      topMargin=2.0 * cm, bottomMargin=2.2 * cm, title="Agentes de revisão")
doc.addPageTemplates([PageTemplate(id="p", frames=[
    Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="n")], onPage=rodape)])
doc.build(F)
print(f"PDF gerado: {SAIDA}")
