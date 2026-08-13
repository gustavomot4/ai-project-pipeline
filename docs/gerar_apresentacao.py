# -*- coding: utf-8 -*-
"""Gera o PDF de apresentação do pipeline."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle, PageBreak, KeepTogether)

D = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DJ", D + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DJ-B", D + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DJ-I", D + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DJ-M", D + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DJ", normal="DJ", bold="DJ-B", italic="DJ-I")

TINTA = colors.HexColor("#1a1a1a")
AZUL = colors.HexColor("#1f4e79")
CINZA = colors.HexColor("#5a5a5a")
CLARO = colors.HexColor("#eef2f6")
BORDA = colors.HexColor("#c8d2dc")
DESTAQUE = colors.HexColor("#fff8e1")
BORDA_D = colors.HexColor("#e0c97f")

ss = getSampleStyleSheet()
S = {}
S["body"] = ParagraphStyle("body", parent=ss["Normal"], fontName="DJ", fontSize=9.6,
                           leading=14.6, alignment=TA_JUSTIFY, textColor=TINTA,
                           spaceAfter=7)
S["h1"] = ParagraphStyle("h1", parent=S["body"], fontName="DJ-B", fontSize=17, leading=21,
                         textColor=AZUL, spaceBefore=6, spaceAfter=10, alignment=0)
S["h2"] = ParagraphStyle("h2", parent=S["body"], fontName="DJ-B", fontSize=12.5, leading=16,
                         textColor=AZUL, spaceBefore=13, spaceAfter=6, alignment=0)
S["h3"] = ParagraphStyle("h3", parent=S["body"], fontName="DJ-B", fontSize=10.4, leading=14,
                         textColor=TINTA, spaceBefore=9, spaceAfter=3, alignment=0)
S["li"] = ParagraphStyle("li", parent=S["body"], leftIndent=13, bulletIndent=3, spaceAfter=4)
S["cell"] = ParagraphStyle("cell", parent=S["body"], fontSize=8.5, leading=12, spaceAfter=0,
                           alignment=0)
S["cellb"] = ParagraphStyle("cellb", parent=S["cell"], fontName="DJ-B")
S["mono"] = ParagraphStyle("mono", parent=S["body"], fontName="DJ-M", fontSize=8,
                           leading=11.5, alignment=0, textColor=TINTA, spaceAfter=0)
S["nota"] = ParagraphStyle("nota", parent=S["body"], fontSize=9, leading=13.5,
                           textColor=colors.HexColor("#3a3a3a"), spaceAfter=0)
S["capa_t"] = ParagraphStyle("capa_t", parent=S["body"], fontName="DJ-B", fontSize=27,
                             leading=33, alignment=TA_CENTER, textColor=AZUL, spaceAfter=6)
S["capa_s"] = ParagraphStyle("capa_s", parent=S["body"], fontName="DJ", fontSize=12.5,
                             leading=18, alignment=TA_CENTER, textColor=CINZA, spaceAfter=4)
S["capa_p"] = ParagraphStyle("capa_p", parent=S["body"], fontSize=10, leading=15,
                             alignment=TA_CENTER, textColor=TINTA)

F = []


def h1(t): F.append(Paragraph(t, S["h1"]))
def h2(t): F.append(Paragraph(t, S["h2"]))
def h3(t): F.append(Paragraph(t, S["h3"]))
def p(t): F.append(Paragraph(t, S["body"]))
def sp(h=5): F.append(Spacer(1, h))
def li(t): F.append(Paragraph(t, S["li"], bulletText="\u2022"))
def num(n, t): F.append(Paragraph(t, S["li"], bulletText=f"{n}."))
def pb(): F.append(PageBreak())


def caixa(titulo, texto, cor=DESTAQUE, borda=BORDA_D):
    inner = []
    if titulo:
        inner.append(Paragraph(titulo, ParagraphStyle("bt", parent=S["nota"], fontName="DJ-B",
                                                      textColor=AZUL, spaceAfter=3)))
    inner.append(Paragraph(texto, S["nota"]))
    t = Table([[inner]], colWidths=[16.4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), cor),
        ("BOX", (0, 0), (-1, -1), 0.7, borda),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    F.append(t)
    sp(9)


def codigo(linhas):
    inner = [Paragraph(l.replace(" ", "&nbsp;"), S["mono"]) for l in linhas]
    t = Table([[inner]], colWidths=[16.4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4f6f8")),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDA),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    F.append(t)
    sp(9)


def tabela(cabec, linhas, larguras, fonte_menor=False):
    est = S["cell"] if not fonte_menor else ParagraphStyle("c2", parent=S["cell"], fontSize=7.9,
                                                          leading=11)
    dados = [[Paragraph(c, S["cellb"]) for c in cabec]]
    for ln in linhas:
        dados.append([Paragraph(c, est) for c in ln])
    t = Table(dados, colWidths=[w * cm for w in larguras], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), CLARO),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fafbfc")]),
    ]))
    F.append(t)
    sp(10)


# ============================ CAPA ============================
sp(90)
F.append(Paragraph("Pipeline de Projetos com IA", S["capa_t"]))
F.append(Paragraph("Um processo com portões objetivos para construir software com "
                   "agentes de inteligência artificial", S["capa_s"]))
sp(22)
t = Table([[Paragraph(
    "<b>Guia completo para apresentação</b><br/><br/>"
    "O que é, como funciona o fluxo, o que ele tem de diferente, "
    "como economiza contexto, o que são os agentes e qual o papel do Obsidian.",
    S["capa_p"])]], colWidths=[13 * cm])
t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), CLARO),
                       ("BOX", (0, 0), (-1, -1), 0.8, BORDA),
                       ("LEFTPADDING", (0, 0), (-1, -1), 16),
                       ("RIGHTPADDING", (0, 0), (-1, -1), 16),
                       ("TOPPADDING", (0, 0), (-1, -1), 14),
                       ("BOTTOMPADDING", (0, 0), (-1, -1), 14)]))
F.append(t)
sp(40)
F.append(Paragraph("Versão do kit: <b>v13.4</b> &nbsp;·&nbsp; 24 agentes &nbsp;·&nbsp; "
                   "portão automático com 14 falhas e 16 avisos &nbsp;·&nbsp; 57 testes",
                   S["capa_p"]))
sp(8)
F.append(Paragraph("Documento gerado em 13 de agosto de 2026", S["capa_p"]))
pb()

# ============================ SUMÁRIO ============================
h1("O que você vai encontrar aqui")
p("Este documento foi escrito para você dominar o assunto e conseguir explicá-lo a qualquer "
  "pessoa da banca, inclusive a quem nunca ouviu falar em agentes de IA. Cada termo técnico é "
  "explicado na primeira vez que aparece. Os números citados vêm de arquivos e comandos reais "
  "do projeto — quando algo é estimativa, está dito que é.")
sp(4)
tabela(["Parte", "O que ela responde"], [
    ["1. O problema", "Por que construir software com IA dá errado sem processo"],
    ["2. A ideia em uma frase", "O que o projeto é, em linguagem de banca"],
    ["3. Vocabulário mínimo", "Os seis termos que o resto do documento usa"],
    ["4. A estrutura", "As pastas e o que cada uma guarda"],
    ["5. As 7 regras", "O núcleo do método, com o motivo de cada regra"],
    ["6. O fluxo", "As sete fases, do dia 1 à entrega, com o portão de cada uma"],
    ["7. O ciclo da sessão", "O que se repete 90% do tempo"],
    ["8. Os 24 agentes", "O que é uma skill, quais existem e como se combinam"],
    ["9. Economia de contexto", "O diferencial central, com os números medidos"],
    ["10. Os guardrails", "O que a máquina julga sozinha e o que ela não julga"],
    ["11. Rastreabilidade", "D-NN, Q-NN, QA-NN e a ideia da lista-morta"],
    ["12. O Obsidian", "O que ele acrescenta e por que nada depende dele"],
    ["13. O papel do dono", "O que a IA não faz por você"],
    ["14. A evidência de campo", "A medição num projeto real, com o custo junto"],
    ["15. Onde o kit não serve", "Os limites declarados"],
    ["16. Perguntas prováveis", "O que a banca costuma perguntar, e a resposta"],
    ["Anexo A", "Glossário rápido"],
    ["Anexo B", "A ficha de avaliação preenchida, com justificativa"],
], [3.6, 12.8])
pb()

# ============================ 1. PROBLEMA ============================
h1("1. O problema que o projeto resolve")
p("Quando uma pessoa usa um assistente de inteligência artificial para escrever software, o "
  "assistente não tem memória entre uma conversa e outra. Tudo o que ele precisa saber sobre o "
  "projeto tem de ser <b>recolocado na conversa</b> toda vez. Esse texto recolocado chama-se "
  "<b>contexto</b>, e ele é cobrado: quanto maior, mais caro e mais lento fica cada pedido — e, "
  "acima de certo tamanho, o modelo começa a perder detalhes no meio.")
p("Na prática, três coisas dão errado sempre:")
sp(2)
num(1, "<b>O contexto incha sem ninguém perceber.</b> Cada sessão acrescenta um parágrafo "
        "\"só para o agente entender melhor\", e em duas semanas o arquivo que abre toda conversa "
        "virou uma parede de texto que ninguém lê e todo mundo paga.")
num(2, "<b>O agente regenera em vez de alterar.</b> Peça uma correção pequena e ele devolve o "
        "arquivo inteiro reescrito. Ninguém consegue revisar 500 linhas para achar as 3 que "
        "mudaram, então ninguém revisa — e o erro entra.")
num(3, "<b>As decisões se perdem.</b> O que foi discutido e descartado na segunda-feira volta a "
        "ser proposto na sexta, porque nada registrou que aquilo já tinha morrido.")
sp(6)
caixa("A frase que resume",
      "O projeto não é uma ferramenta de IA. É um <b>processo</b> que impõe disciplina a "
      "qualquer ferramenta de IA — com regras que uma máquina consegue verificar, e não apenas "
      "boas intenções escritas num documento que ninguém abre.")

# ============================ 2. A IDEIA ============================
h1("2. A ideia, em uma frase")
caixa("", "<b>Um kit reutilizável de processo que permite tirar uma aplicação do zero usando "
          "agentes de IA e sustentá-la até a entrega, mantendo rigor — portões objetivos, "
          "decisões rastreáveis, revisão adversarial — e gastando pouco contexto: orçamento "
          "numérico, leitura sob demanda, evolução por delta.</b>", CLARO, BORDA)
p("Desempacotando essa frase, porque cada pedaço dela vira uma pergunta de banca:")
sp(2)
li("<b>\"Kit reutilizável\"</b> — não é o código de um app. É a pasta de processo que se instala "
   "em qualquer projeto novo com um comando, levando junto as regras, os agentes e o portão "
   "automático.")
li("<b>\"Portões objetivos\"</b> — nada é aceito por \"parece bom\". Cada etapa tem um critério "
   "que dá para verificar: um comando que fica verde, um número que passa de um limite, um "
   "arquivo que existe.")
li("<b>\"Decisões rastreáveis\"</b> — toda decisão vira uma linha numerada (D-01, D-02…) que "
   "nunca é apagada, e que os commits do git citam.")
li("<b>\"Revisão adversarial\"</b> — antes de entregar, uma sessão separada tenta <i>quebrar</i> "
   "o que foi construído, em vez de conferir se está bonito.")
li("<b>\"Gastando pouco contexto\"</b> — é o diferencial central, e tem capítulo próprio "
   "(parte 9).")
sp(4)
p("O kit está publicado no GitHub sob licença MIT e é operado dentro do Obsidian, um aplicativo "
  "gratuito de notas. Nada nele depende de uma ferramenta de IA específica: os agentes são "
  "arquivos de texto que funcionam instalados ou simplesmente colados numa conversa.")
sp(6)

# ============================ 3. VOCABULÁRIO ============================
h1("3. Vocabulário mínimo (seis termos)")
p("Estes seis termos aparecem o tempo todo. Se você dominar esta página, o resto do documento "
  "se lê sozinho.")
sp(3)
tabela(["Termo", "O que significa, em linguagem simples"], [
    ["<b>Contexto</b>",
     "Tudo o que é enviado ao modelo de IA junto com o pedido. É o que ele \"sabe\" naquele "
     "momento. Não persiste entre sessões: o que não for reenviado, o agente não sabe."],
    ["<b>Token</b>",
     "A unidade em que o contexto é cobrado — mais ou menos um pedaço de palavra. Em português, "
     "uma estimativa usável é <b>1 token ≈ 3 caracteres</b>. É por isso que o kit orça em "
     "caracteres: caractere se conta com um script, token não."],
    ["<b>Contexto-fonte</b>",
     "O arquivo <font face='DJ-M' size='8'>a_context_source.md</font>: a única fonte de verdade "
     "sobre o estado do projeto, e o único arquivo que <i>toda</i> sessão carrega. Tem teto de "
     "4.000 caracteres, cobrado por script."],
    ["<b>Delta</b>",
     "Só o trecho que mudou, em vez do arquivo inteiro reescrito. Pedir delta é a regra que "
     "mantém o diff revisável e o custo baixo."],
    ["<b>Portão</b>",
     "O critério objetivo que separa \"pronto\" de \"não pronto\". Pode ser automático (um "
     "script que reprova o commit) ou manual (uma seção de checklist que o dono roda)."],
    ["<b>Skill / agente</b>",
     "Um arquivo de texto que define um papel para a IA: o que ela faz, o que ela <i>não</i> "
     "faz, que arquivos recebe e qual portão precisa cumprir. São 24 no kit, e vale a regra de "
     "<b>uma por sessão</b>."],
], [2.9, 13.5])
caixa("Os cinco identificadores rastreáveis",
      "<b>D-NN</b> decisão fechada &nbsp;·&nbsp; <b>Q-NN</b> pendência que é do dono, não do "
      "agente &nbsp;·&nbsp; <b>QA-NN</b> achado de revisão &nbsp;·&nbsp; <b>T-NN</b> tarefa "
      "&nbsp;·&nbsp; <b>A-NN</b> ação que só o dono pode executar na máquina real. "
      "Todos são cobrados pelo script: identificador citado tem de existir, e não pode se repetir.")
pb()

# ============================ 4. ESTRUTURA ============================
h1("4. A estrutura: cinco pastas com responsabilidades separadas")
p("A organização não é estética. Cada pasta responde a uma pergunta diferente, e é isso que "
  "permite dizer <i>qual arquivo uma sessão carrega e qual ela nunca carrega</i> — que é a base "
  "da economia de contexto.")
sp(3)
tabela(["Pasta", "Pergunta que responde", "Conteúdo principal"], [
    ["<font face='DJ-M' size='8'>a_context/</font>", "<b>A verdade:</b> o que este projeto é e "
     "em que pé está",
     "contexto-fonte (≤4.000 caracteres), plano de módulos, registro de decisões, temas de "
     "domínio lidos sob demanda"],
    ["<font face='DJ-M' size='8'>b_process/</font>", "<b>Como se trabalha</b>",
     "roteiro das fases, checklist de portões, backlog de tarefas, aprendizados, e a pasta "
     "<font face='DJ-M' size='8'>skills/</font> com os 24 agentes"],
    ["<font face='DJ-M' size='8'>c_technical_docs/</font>", "<b>Como operar</b>",
     "guia do Obsidian, caso de referência"],
    ["<font face='DJ-M' size='8'>d_history/</font>", "<b>O que aconteceu</b>",
     "changelog datado — pode crescer à vontade, porque <b>nenhuma sessão o carrega</b>"],
    ["<font face='DJ-M' size='8'>e_qa/</font>", "<b>Que evidência sustenta</b>",
     "relatórios de revisão com data e hora no nome, decisões arquivadas"],
    ["<font face='DJ-M' size='8'>scripts/</font>", "<b>O que a máquina cobra</b>",
     "o portão automático, os testes, o instalador do hook, o criador de projetos"],
], [3.4, 5.0, 8.0])
p("Além das pastas, três arquivos na raiz carregam papéis distintos, e essa separação é "
  "deliberada:")
sp(2)
li("<b>README.md</b> — o único lugar com os \"porquês\" e com os limites. Ele é para humanos.")
li("<b>INDEX.md</b> — o mapa de navegação. Aponta e sai da frente.")
li("<b>CLAUDE.md</b> — o <b>contrato de leitura do agente</b>. A ferramenta de IA carrega esse "
   "arquivo sozinha em toda sessão, e ele diz exatamente o que ler, em que ordem, e o que "
   "<b>nunca</b> ler. Ele existe para que o contexto-fonte não precise gastar o próprio "
   "orçamento explicando como ser lido.")
sp(4)
caixa("Por que isso importa para a banca",
      "A pergunta \"como vocês impedem o agente de ler o repositório inteiro?\" tem uma resposta "
      "concreta: existe um contrato de leitura versionado, com uma tabela de <i>ler quando</i>, "
      "e uma linha dizendo que o changelog e a pasta de evidências são <b>nunca</b>. Sem isso, um "
      "agente com acesso à pasta lê tudo e paga por tudo.")

# ============================ 5. AS 7 REGRAS ============================
h1("5. As 7 regras que valem em todas as fases")
p("Cada regra existe porque uma coisa deu errado antes. O motivo está junto, porque regra sem "
  "motivo é a primeira a ser abandonada quando aperta.")
sp(3)
tabela(["#", "Regra", "O motivo real"], [
    ["1", "<b>Contexto com orçamento em número.</b> O contexto-fonte tem teto de 4.000 "
          "caracteres, medido por script e atualizado por substituição.",
     "\"≤ 1 página\" sem número virou, num projeto real, um parágrafo-parede de ~640 tokens "
     "relido em toda sessão. Limite sem número não é limite."],
    ["2", "<b>Histórico fora do contexto.</b> O que é datado vai para o changelog, que nenhuma "
          "sessão carrega.",
     "173 linhas de histórico que nenhuma sessão pagou. Funcionou exatamente como desenhado."],
    ["3", "<b>Delta, nunca regenerar.</b> Só o trecho alterado — em documento e em código.",
     "Regenerar foi o maior custo dos projetos anteriores: diff ilegível, revisão que ninguém "
     "faz, erro que passa."],
    ["4", "<b>Decisão rastreável.</b> Assunto fechado vira D-NN em duas frases; bug vira QA-NN "
          "citado no commit; pendência do dono vira Q-NN.",
     "Sem registro, o que morreu volta. O script cobra: identificador citado tem de existir e "
     "não pode repetir."],
    ["5", "<b>Nada entra sem portão.</b> Critério objetivo definido no dia 1. Rejeição registrada "
          "vale tanto quanto adoção.",
     "\"Parece bom\" não é critério, e sem portão a IA sempre acha que terminou."],
    ["6", "<b>Estado mora num lugar só.</b> Versão, métrica e contagem vigentes ficam apenas no "
          "contexto-fonte; todo outro documento aponta para lá.",
     "Num projeto real o estado vivia em 4 arquivos e divergiu de verdade — dois cards vizinhos "
     "do mesmo quadro citando números de versões diferentes."],
    ["7", "<b>Observe antes de construir.</b> Parser ou integração só com uma amostra real da "
          "estrutura na mão.",
     "Chutar a estrutura de uma fonte de dados custou 6 ciclos de revisão num projeto e 6 "
     "versões de schema em outro."],
], [0.7, 7.4, 8.3], fonte_menor=True)
pb()

# ============================ 6. O FLUXO ============================
h1("6. O fluxo: sete fases, cada uma com seu portão")
p("O roteiro é uma linha do dia 1 à entrega. Cada sessão pressupõe que a anterior passou no "
  "portão — é isso que impede o projeto de avançar sobre uma base que ninguém verificou.")
sp(4)
tabela(["Fase", "O que acontece", "Agente usado", "Portão que fecha"], [
    ["<b>0. Contexto</b><br/>1 sessão",
     "O agente faz até 5 perguntas e devolve o contexto-fonte preenchido. Se o projeto já "
     "existe, o mapa se faz do <b>código</b>, não da memória do dono.",
     "bootstrap-contexto<br/><i>(ou adoção de projeto existente)</i>",
     "O script passa (≤4.000 caracteres) <b>e</b> o dono lê o contexto inteiro e concorda com "
     "cada linha"],
    ["<b>1. Forma e plano</b><br/>3 sessões",
     "Decide a arquitetura; gera o plano com módulos, contratos e portões; e — em sessão "
     "separada — confere se os documentos contam a mesma história.",
     "arquitetura-monolito<br/>planejador<br/>consistência-artefatos",
     "Para cada módulo: \"outro agente implementaria isto lendo só o contrato?\". Aprovado = "
     "<b>plano congelado</b> como decisão"],
    ["<b>2. Dados e domínio</b><br/>1 sessão por módulo",
     "Schema, regra de negócio, migrações. Os invariantes são escritos como frases verificáveis "
     "<b>antes</b> do código.",
     "backend-domínio<br/><i>(dados-análise antes, se o projeto nasce de fonte externa)</i>",
     "Migração roda em banco vazio; invariantes testados inclusive tentando violá-los direto no "
     "banco; transação não deixa efeito parcial"],
    ["<b>3. Borda, UI e acesso</b><br/>1 sessão por módulo",
     "Na ordem: acesso, borda, tela.",
     "autenticação<br/>backend-bff<br/>frontend-uiux",
     "Cada rota sensível testada sem sessão; falha parcial explícita; 4 estados por tela; fluxo "
     "crítico no menor viewport"],
    ["<b>4. Testes e revisão</b><br/>2 sessões, em ordem",
     "Primeiro os testes; depois, em <b>sessão separada</b>, uma revisão que tenta quebrar o "
     "sistema. Repete-se o par até o placar de crítico/alto zerar.",
     "testes<br/>guardrails-review",
     "Suíte verde na máquina do dono, rodando duas vezes com o mesmo resultado; relatório de "
     "revisão registrado com 12 frentes percorridas e cada achado com reprodução"],
    ["<b>5. Empacotar e operar</b><br/>1–2 sessões",
     "Container, deploy, e — se o sistema roda continuamente — uma sessão de observabilidade "
     "antes de entregar.",
     "iac-docker-terraform<br/>observabilidade",
     "Sobe em ambiente limpo; derrubar e subir preserva os dados; versão consultável em tempo de "
     "execução; nenhum segredo na imagem"],
    ["<b>6. Entrega</b><br/>1 sessão",
     "Empacota e confere o que sai.",
     "revisão-entrega",
     "Pacote aberto e conferido; nenhum segredo, dependência ou banco dentro; estado numérico só "
     "no contexto-fonte"],
], [2.3, 4.6, 3.2, 6.3], fonte_menor=True)

h2("O detalhe que mais impressiona banca: o critério de saída do laço de QA")
p("A fase 4 manda repetir teste e revisão \"até zerar\". Isso, sozinho, é um laço infinito. "
  "Então o kit define o critério de parada: <b>se o placar de crítico e alto não cair em três "
  "passagens consecutivas, o laço de QA para</b> e abre-se uma sessão de consistência ou de "
  "replanejamento. O raciocínio: achado que reaparece três vezes não é bug, é sintoma de plano "
  "errado — e continuar revisando queima sessões atacando o efeito. O sinal é objetivo e sai dos "
  "relatórios que a própria fase já escreve; não depende de o agente se autoavaliar.")

h2("Depois da entrega, o roteiro vira gatilho")
p("A entrega fecha a construção, não o projeto. Daqui em diante não há mais uma linha, e sim uma "
  "tabela de situação → agente:")
sp(2)
tabela(["A situação é…", "O agente é…", "E o portão que não se negocia"], [
    ["\"quebrou\", \"deu erro\"", "depuração-diagnóstico",
     "reprodução determinística <b>antes</b> de qualquer edição; causa provada ligando e "
     "desligando; teste de regressão citando o QA-NN"],
    ["\"está lento\"", "performance",
     "baseline medido antes; gargalo apontado por ferramenta, não por intuição; uma mudança por vez"],
    ["\"não sei o que houve ontem\"", "observabilidade",
     "o dono responde às três perguntas sem abrir o código; nada sensível em log"],
    ["subir biblioteca, CVE", "dependências-supply-chain",
     "uma atualização por vez com a suíte verde entre elas; CVE tratada, mitigada com prova, ou "
     "aceita com decisão registrada"],
    ["ideia de melhoria", "auditor-evolução",
     "lista-morta percorrida antes; <b>portão escrito antes do experimento</b>"],
], [3.6, 3.4, 9.4], fonte_menor=True)
caixa("Duas regras de encaminhamento que evitam sessão desperdiçada",
      "<b>\"Está lento\" ≠ \"está lento desde ontem\".</b> O segundo é depuração, não "
      "performance: algo mudou, e achar o quê é mais barato que otimizar o que já estava rápido."
      "<br/><b>Precisou depurar duas vezes o mesmo sintoma?</b> O que faltou foi "
      "observabilidade. A terceira sessão de arqueologia custa mais que instrumentar de uma vez.")
pb()

# ============================ 7. CICLO ============================
h1("7. O ciclo de uma sessão — o que se repete 90% do tempo")
p("As fases dão a ordem geral, mas o dia a dia é este ciclo, sempre igual:")
sp(3)
codigo([
    "uma skill (o papel)  +  o CONTEXTO-FONTE  +  só o arquivo do momento",
    "      |",
    "      +-->  pedir DELTA (só o que muda)",
    "      |",
    "      +-->  rodar o PORTÃO — na máquina do dono, não no sandbox",
    "      |",
    "      +-->  registrar D-NN (decisão) / QA-NN (achado) / Q-NN (pendência do dono)",
    "      |",
    "      +-->  reescrever \"Estado atual\" do CONTEXTO por SUBSTITUIÇÃO",
    "      |",
    "      +-->  linha datada no CHANGELOG (que nenhuma sessão carrega)",
    "      |",
    "      +-->  commit citando os identificadores:  TIPO: o que mudou (D-NN/QA-NN)",
])
p("Repare no que <b>não</b> entra na sessão: o repositório inteiro, o changelog, os relatórios "
  "de revisão, as outras 23 skills. A sessão recebe três coisas e só três.")
sp(3)
caixa("O passo mais pulado, e o que se fez a respeito",
      "O fecho de sessão é onde o processo mais vaza — pular um passo é o que faz o estado "
      "divergir e o histórico sumir. Por isso ele virou um <b>modelo de um clique</b> no "
      "Obsidian, com cada item em caixa de seleção: fica visível o que faltou. Atacar o passo "
      "mais frágil com a menor fricção possível é uma decisão de projeto, não um detalhe.")

# ============================ 8. AGENTES ============================
h1("8. Os 24 agentes")
h2("O que é, tecnicamente, um agente aqui")
p("Cada agente é uma pasta com um arquivo <font face='DJ-M' size='8'>SKILL.md</font>. O arquivo "
  "tem um cabeçalho com <b>nome</b> e <b>descrição</b>, e um corpo com quatro seções "
  "obrigatórias — obrigatórias no sentido literal: o script reprova o commit se faltar uma.")
sp(2)
li("<b>Papel</b> — quem a IA é nessa sessão.")
li("<b>Contexto que você recebe</b> — exatamente quais arquivos entram. É o oposto de \"leia o "
   "repositório\".")
li("<b>Limites</b> — o que o agente <b>não</b> faz mesmo tendo sido escolhido certo. Esta seção é "
   "a que impede o agente de consertar coisas fora do escopo da sessão.")
li("<b>Saída</b> — o artefato que sai, para o dono saber o que esperar.")
sp(3)
p("A <b>descrição</b> tem uma exigência incomum: precisa dizer quando a skill dispara <b>e "
  "quando não dispara</b> (\"Não use para X — isso é da skill Y\"). Sem essa fronteira negativa, "
  "duas skills disputam a mesma tarefa e a errada ganha metade das vezes. O script avisa quando "
  "falta.")
sp(3)
caixa("Uma medição que vale citar",
      "Ao comparar este kit com outro conhecido, mediu-se: <b>21 de 24</b> descrições daqui já "
      "diziam quando <i>não</i> escolher a skill (contra 0 de 20 do outro), mas <b>0 de 24</b> "
      "diziam o que a skill não faz depois de escolhida (contra 15 de 20 lá). Cada kit tinha "
      "metade da resposta — e a seção <b>Limites</b> nasceu disso, agora cobrada por script.")

h2("Os 24, por grupo")
tabela(["Grupo", "Agentes", "O que o grupo protege"], [
    ["<b>Fases</b> (7)",
     "bootstrap-contexto · adoção-projeto-existente · planejador · consistência-artefatos · "
     "auditor-evolução · revisão-entrega · retrospectiva",
     "Que o projeto comece com contexto orçado, plano congelável e documentos que contam a "
     "mesma história"],
    ["<b>Arquitetura</b> (2)", "monolito <i>(padrão)</i> · microserviços",
     "Que a forma seja decidida antes de existir código. A de microserviços tem <b>portão de "
     "existência</b>: reprova se não houver time e observabilidade — e reprovar é o sistema "
     "funcionando"],
    ["<b>Backend</b> (3)", "domínio · bff · integração síncrona",
     "Invariantes, dinheiro em inteiro, transação, timeout, retentativa segura"],
    ["<b>Frontend</b> (2)", "ui/ux · micro-frontend",
     "Quatro estados por tela, mobile-first, erro em linguagem de gente"],
    ["<b>Transversais</b> (6)",
     "autenticação · infraestrutura · testes · guardrails-review · dependências · privacidade",
     "Nega por padrão, rollback testado, regressão amarrada ao achado, licença e CVE, dado "
     "pessoal com finalidade escrita"],
    ["<b>Sistema vivo</b> (3)", "depuração · performance · observabilidade",
     "O projeto passa muito mais tempo sendo mantido que sendo criado — e a versão antiga do kit "
     "só tinha agente para a criação"],
    ["<b>Dados</b> (1)", "dados-análise",
     "Amostra real antes do parser; ausente não é zero; número com incerteza; zero vazamento "
     "entre treino e teste"],
], [2.6, 6.4, 7.4], fonte_menor=True)

h2("Como eles se combinam")
codigo([
    "arquitetura-*  (uma vez, na Fase 1)",
    "   |",
    "   +-- backend-dominio  -->  backend-bff  -->  frontend-uiux",
    "         |                                          |",
    "         +--------------  testes  ------------------+",
    "                            |",
    "                    guardrails-review   (antes de entregar)",
    "                            |",
    "                  iac-docker-terraform  (empacotar e subir)",
])
p("<b>A ordem entre eles importa</b>, e é aí que está boa parte do valor: dados-análise entra "
  "<b>antes</b> de backend-domínio quando o projeto nasce de uma fonte externa — é ela que traz a "
  "amostra real sem a qual o schema é chute. Privacidade entra <b>junto</b> com o schema, não "
  "depois: coluna criada sem finalidade escrita vira obrigação permanente, e retenção retroativa "
  "é migração dolorosa.")

h2("A regra que sustenta tudo: uma skill por sessão")
p("Duas skills na mesma sessão são duas responsabilidades disputando o mesmo contexto — e é "
  "também pagar duas vezes pela mesma instrução. Numa versão anterior existia uma pasta de "
  "prompts separada das skills; mediu-se <b>27% de sobreposição</b> entre o prompt de revisão e a "
  "skill de guardrails, e os dois eram carregados juntos. Os prompts foram absorvidos pelas "
  "skills: um mecanismo só.")
pb()

# ============================ 9. ECONOMIA ============================
h1("9. A economia de contexto — o diferencial central")
p("Este é o capítulo que a banca vai querer ouvir com número. A tese é simples de enunciar: "
  "<b>o custo de um projeto assistido por IA não está no que o modelo escreve; está no que ele "
  "relê a cada sessão.</b> Um arquivo de 2.000 caracteres carregado em 40 sessões custa 40 vezes, "
  "e ninguém percebe porque cada sessão parece barata.")

h2("Os três mecanismos")
sp(2)
num(1, "<b>Orçamento em número, cobrado por máquina.</b> O contexto-fonte tem teto de 4.000 "
        "caracteres — cerca de 1.300 tokens. Não é uma recomendação: o script reprova o commit "
        "acima disso, e avisa a partir de 3.600 para que o corte seja feito com calma, e não no "
        "meio de uma sessão de trabalho.")
num(2, "<b>Três níveis de leitura, declarados por escrito.</b> O contrato de leitura divide os "
        "arquivos em <i>sempre</i> (o contexto-fonte), <i>sob demanda</i> (o tema que a tarefa "
        "tocar) e <b>nunca</b> (changelog e evidências). O terceiro nível é o que mais economiza, "
        "e é o que um agente com acesso à pasta faria errado sozinho.")
num(3, "<b>Delta em vez de regeneração.</b> Vale para documento e para código. Além do custo, é "
        "o que mantém o diff pequeno o bastante para alguém revisar de verdade.")
sp(6)

h2("Os números medidos")
p("Origem: análise de 22/07/2026 sobre um projeto real construído com a versão anterior do kit. "
  "Tamanhos contados nos arquivos; tokens estimados a 3 caracteres por token em português.")
sp(3)
tabela(["O que era carregado", "Antes (medido)", "Depois (garantido)", "O que mudou"], [
    ["<b>Prompt do papel</b>", "~620 a 1.150 tokens", "~280 a 560 tokens",
     "O texto explicava o motivo histórico da regra ao dono. O motivo foi para o README; a "
     "instrução ficou imperativa. <b>~45% mais barato, mesma função.</b>"],
    ["<b>Contexto-fonte</b>", "~1.580 tokens, sem teto efetivo", "≤ ~1.300 tokens, garantido",
     "O \"Estado atual\" era um parágrafo-parede de 1.930 caracteres com mais de 15 referências, "
     "relido em toda sessão. Virou 6 marcadores de formato fixo, cobrados por script."],
    ["<b>Registro de decisões</b>", "~7.700 tokens (23.101 caracteres)", "~2.000 tokens",
     "Era carregado inteiro nas sessões de evolução — <b>o maior custo recorrente do sistema</b>. "
     "Agora a linha tem no máximo 2 frases e a evidência longa vira nota linkada."],
    ["<b>Changelog</b>", "carregado junto com o resto", "<b>zero</b> — nenhuma sessão o carrega",
     "173 linhas de histórico que deixaram de ser pagas."],
], [3.5, 3.6, 3.4, 5.9], fonte_menor=True)
caixa("A frase para a banca",
      "\"Em dezenas de sessões, a diferença é da ordem de <b>centenas de milhares de tokens só em "
      "contexto fixo</b> — sem contar o retrabalho evitado.\" E a ressalva que dá credibilidade: "
      "esses valores são <b>calculados</b> a partir de tamanhos de arquivo reais, com a conversão "
      "de 3 caracteres por token; não são fatura de API.")

h2("O detalhe elegante: o teto mede conteúdo, não formatação")
p("Um caso real vale como exemplo do rigor do método. Num projeto, o formatador de Markdown do "
  "editor alinhou as colunas de uma tabela ao salvar e somou <b>2.048 caracteres de espaço em "
  "branco puro</b> — 17% do arquivo, sem uma palavra nova. O portão passou a reprovar um commit "
  "que só respondia a uma pergunta. O diagnóstico foi que o teto estava medindo <i>formatação</i>. "
  "A correção: a medição passou a descontar o alinhamento de tabela. É o tipo de defeito que só "
  "aparece quando o limite é cobrado por máquina — e que, sem a máquina, teria virado \"o "
  "processo é chato\" e o abandono da regra.")
pb()

# ============================ 10. GUARDRAILS ============================
h1("10. Os guardrails: o que a máquina julga e o que ela não julga")
p("A palavra <i>guardrail</i> aqui significa proteção automática — algo que impede o erro de "
  "passar sem depender de alguém lembrar. O kit tem duas camadas, e é honesto sobre o tamanho "
  "de cada uma.")

h2("Camada 1 — o portão automático")
p("Um script em Python puro, sem nenhuma dependência externa, instalado como <i>hook</i> de "
  "pre-commit: ele roda sozinho a cada commit e, se reprovar, o commit não acontece. Hoje ele "
  "julga <b>14 situações que reprovam</b> e <b>16 que avisam</b>.")
sp(3)
tabela(["Ele reprova quando…", "Ele avisa quando…"], [
    ["orçamento do contexto estourado<br/>"
     "registro de decisões acima do teto<br/>"
     "o mesmo estado em dois arquivos (fonte única)<br/>"
     "mais tarefas em andamento que o limite declarado<br/>"
     "sobra de editor versionada (.bak, .tmp)<br/>"
     "skill sem nome, sem descrição ou fora do esquema<br/>"
     "link interno apontando para nota que não existe<br/>"
     "<b>segredo versionado</b> — na árvore e no histórico<br/>"
     "gitignore sem cobertura mínima de segredo<br/>"
     "identificador citado que não existe<br/>"
     "identificador duplicado<br/>"
     "\"em andamento\" divergindo entre backlog e contexto<br/>"
     "tarefa apontando módulo que não existe no plano",
     "o contexto está perto do teto<br/>"
     "o registro está perto do teto<br/>"
     "há módulo no plano sem nenhuma tarefa<br/>"
     "o portão automático não está instalado<br/>"
     "há nota que ninguém linka<br/>"
     "há tema de domínio fora do mapa de leitura<br/>"
     "a descrição de uma skill não diz quando <i>não</i> usá-la<br/>"
     "a sessão não declarou qual agente rodou<br/>"
     "um número declarado diverge do arquivo medido<br/>"
     "uma pergunta do dono está aberta e ausente do contexto<br/>"
     "um achado grave está aberto há mais de 14 dias<br/>"
     "ainda há texto de modelo por preencher"],
], [8.2, 8.2], fonte_menor=True)

h2("Camada 2 — os portões humanos")
p("O checklist tem 118 itens e as skills trazem mais 166: <b>284 no total</b>. O script julga "
  "<b>30 deles — cerca de 11%</b>. O resto depende de o dono rodar a seção certa.")
sp(3)
caixa("Este é o argumento mais forte do projeto, e é uma limitação",
      "A frase acima está escrita no README <b>e é cobrada por um teste automatizado</b>: se "
      "alguém acrescentar uma checagem sem atualizar o número, a suíte reprova. O motivo é que "
      "essa frase já envelheceu uma vez — dizia 188 itens e 18 julgados quando o real era 277 e "
      "23. Transformar a declaração mais desconfortável do produto num invariante testado é uma "
      "decisão de projeto rara, e é a que mais impressiona quem entende do assunto.")
p("Vale saber dizer isto em voz alta: <b>é um kit de disciplina com algumas travas automáticas, "
  "não um sistema que impede erro.</b> Bancas confiam mais em quem declara o tamanho da própria "
  "cobertura do que em quem promete cobertura total.")

h2("Camada 3 — os testes do próprio processo")
p("O portão também é testado. São <b>57 testes</b>, só com biblioteca padrão do Python, rodando "
  "em integração contínua no Linux e no Windows a cada envio. Dois deles merecem destaque:")
sp(2)
li("<b>Uma isca por checagem.</b> Cada uma das 14 falhas tem um caso concreto que ela "
   "<i>precisa</i> pegar. Se a checagem parar de checar, a isca passa e o teste reprova.")
li("<b>O portão do portão.</b> Um teste compara a lista de iscas com a lista de falhas do "
   "script: falha nova sem isca reprova. Isso fecha a classe inteira do defeito, em vez de "
   "consertar um caso.")
sp(3)
p("A motivação é concreta: uma das checagens tinha <b>parado de checar em silêncio</b>. Ela "
  "descartava o texto escrito entre crases antes de procurar os identificadores — e a casa "
  "escreve os identificadores entre crases. Das 341 citações de um projeto real, <b>300 estavam "
  "invisíveis</b>: o portão enxergava 12% e imprimia verde sobre o resto.")
pb()

# ============================ 11. RASTREABILIDADE ============================
h1("11. Rastreabilidade e a \"lista-morta\"")
p("Toda decisão fechada vira uma linha numerada, com data, status, a decisão em no máximo duas "
  "frases e um link para a evidência longa. O registro é <b>append-only</b>: nunca se edita uma "
  "linha antiga; reverter é escrever uma linha nova que diz que substitui a anterior.")
sp(3)
codigo([
    "| #    | Data       | Status              | Decisão (curta)                         |",
    "|------|------------|---------------------|-----------------------------------------|",
    "| D-01 | 2026-08-06 | ADOTADO             | Forma = aplicação estática, sem backend |",
    "| D-06 | 2026-08-06 | REJEITADO           | Reaproveitar o backend da versão 1      |",
    "| D-57 | 2026-08-12 | ADOTADO · SUPERSEDE | Cai o portão \"sem par repetido\"         |",
])
h2("Por que registrar o que foi REJEITADO")
p("Esta é a ideia central do método e o ponto que melhor diferencia o projeto de um changelog "
  "comum. Um changelog registra o que venceu. Aqui registra-se também <b>o que perdeu, e o número "
  "que o matou</b>. O motivo é específico do trabalho com IA: sem esse registro, o agente "
  "re-propõe na sexta a alternativa que foi descartada na segunda, e a discussão inteira se "
  "repete — pagando contexto e tempo de novo.")
sp(3)
caixa("A prova de que o mecanismo funciona sob pressão",
      "Num projeto real, o registro chegou perto do teto e foi preciso arquivar linhas antigas. "
      "As rejeitadas seriam as candidatas óbvias — elas estão \"mortas\". Em <b>duas passagens "
      "diferentes</b> de arquivamento, elas foram <b>preservadas de propósito</b>, com a razão "
      "escrita: \"são a lista-morta que a sessão de evolução varre\". O mecanismo se defendeu da "
      "pressão do próprio orçamento. Isso não é documentação decorativa.")
p("Os outros identificadores completam a rastreabilidade: <b>Q-NN</b> separa o que é decisão do "
  "<i>dono</i> (regra de negócio, rumo) do que é decisão do agente — e o agente é instruído a "
  "parar e registrar em vez de escolher; <b>QA-NN</b> amarra cada achado de revisão à correção e "
  "ao teste de regressão que o guarda; <b>T-NN</b> e <b>A-NN</b> separam tarefa do agente de ação "
  "que só o dono pode executar na máquina real.")

# ============================ 12. OBSIDIAN ============================
h1("12. O Obsidian e o valor que ele acrescenta")
h2("O que é")
p("O Obsidian é um aplicativo gratuito de notas que trabalha diretamente sobre uma pasta de "
  "arquivos Markdown do seu computador — não é um serviço na nuvem e não tem formato próprio. "
  "\"Vault\" é como ele chama essa pasta. Aqui, <b>o vault é a raiz do repositório git</b>: as "
  "mesmas notas que a pessoa lê no Obsidian são as que o agente de IA lê e as que o git versiona.")

h2("O que ele acrescenta ao processo")
sp(2)
tabela(["Recurso", "O que resolve na prática"], [
    ["<b>Links internos</b> <font face='DJ-M' size='8'>[[assim]]</font>",
     "O roteiro linka direto a skill de cada fase; o plano linka a decisão que o congelou. "
     "Navegar deixa de exigir saber o caminho do arquivo."],
    ["<b>Backlinks</b>",
     "No rodapé de cada nota aparece quem aponta para ela. É como se descobre todo lugar que "
     "cita uma decisão antes de mudá-la — e é o mesmo critério que o script usa para decidir o "
     "que pode ser arquivado."],
    ["<b>Grafo</b>",
     "Mostra o vault como um mapa, colorido por tema, com o índice, o contexto-fonte e as skills "
     "como centros. Serve para enxergar nota órfã e aglomerado inesperado."],
    ["<b>Modelos (templates)</b>",
     "<b>O de maior valor.</b> Decisão, achado de QA e fecho de sessão entram com um atalho de "
     "teclado. Como o fecho de sessão é o passo mais pulado do processo, reduzir sua fricção a um "
     "clique ataca exatamente o ponto por onde o estado começa a divergir."],
    ["<b>Busca e etiquetas</b>",
     "Procurar por <font face='DJ-M' size='8'>D-</font>, <font face='DJ-M' size='8'>Q-</font> ou "
     "<font face='DJ-M' size='8'>QA-</font> salta direto para qualquer item rastreável."],
], [3.6, 12.8])

h2("O ponto que é preciso saber defender")
caixa("Nada no pipeline depende do Obsidian",
      "É tudo Markdown puro. As skills funcionam em qualquer ferramenta de IA, o portão é Python "
      "sem dependências, e o repositório abre normalmente em qualquer editor. O Obsidian é uma "
      "<b>camada de navegação opcional</b> — se a banca perguntar \"e se a equipe não usar "
      "Obsidian?\", a resposta é: continua funcionando igual, perde-se conforto, não capacidade.")
p("Um detalhe de engenharia que vale citar: a pasta de configuração <font face='DJ-M' size='8'>"
  ".obsidian/</font> <b>é versionada de propósito</b> — é o que faz o vault abrir já configurado "
  "para quem clonar o repositório, com favoritos, modelos e cores do grafo prontos. A única "
  "exceção é o arquivo de espaço de trabalho, que muda a cada abertura e está no gitignore. E a "
  "pasta fica fora da validação do script, para não gerar aviso falso — porque <b>aviso falso "
  "ensina a ignorar aviso</b>, que é uma regra do próprio kit.")
pb()

# ============================ 13. PAPEL DO DONO ============================
h1("13. O papel do dono — o que a IA não faz por você")
p("O método é explícito sobre a fronteira. Isso importa numa apresentação porque a pergunta "
  "\"então a IA faz tudo?\" vem sempre.")
sp(3)
tabela(["Papel", "O que significa"], [
    ["<b>Guardião do portão</b>",
     "Aceitar uma entrega é rodar a seção certa do checklist. Se falhar, devolve-se pedindo "
     "<i>delta</i> — nunca \"refaz tudo\"."],
    ["<b>Decisor</b>",
     "Toda pendência Q-NN é do dono. O agente não muda regra de negócio nem rumo: ele registra a "
     "pergunta e para."],
    ["<b>Operador da máquina real</b>",
     "Testes oficiais, migrações, deploy e envio ao repositório remoto. O sandbox do agente é "
     "indicativo, <b>nunca portão</b>."],
    ["<b>Fonte dos dados manuais</b>",
     "O que o dono não preencher fica como <b>lacuna declarada</b> — jamais inventada. Essa é "
     "uma regra dura do kit: o agente não fabrica dado, fonte ou número."],
], [3.8, 12.6])
h2("As frases de segurança")
p("O kit lista perguntas curtas que o dono deve fazer ao agente. Elas economizam sessão inteira "
  "e funcionam como um roteiro de defesa:")
sp(2)
li("\"Isso passou no portão? <b>Mostra o número.</b>\"")
li("\"Cadê o D-NN?\"")
li("\"Me manda <b>só o delta</b>.\"")
li("\"Rodou na <b>minha máquina</b> ou no sandbox?\"")
li("\"Viu uma <b>amostra real</b> antes de escrever esse parser?\"")
li("\"Isso muda alguma <b>decisão ou número</b>?\"")

# ============================ 14. EVIDÊNCIA ============================
h1("14. A evidência de campo")
p("Um processo que só fala bem de si mesmo não convence. Por isso o kit foi <b>medido</b> contra "
  "um projeto real construído com ele — um jogo de disputa de pênaltis, aplicação estática sem "
  "servidor, 46 commits em 4 dias de trabalho e 34 sessões registradas. Dois cuidados dão "
  "credibilidade à medição:")
sp(2)
li("Os agentes que construíram o projeto <b>não sabiam</b> que ele era um teste do kit.")
li("O critério de sucesso foi escrito, datado e assinado por hash <b>antes</b> de qualquer "
   "arquivo do projeto ser aberto. Avaliação que escolhe o critério depois de ver o resultado "
   "não vale nada.")
sp(5)
tabela(["O que se mediu", "Resultado"], [
    ["Commits citando um identificador rastreável", "<b>45 de 46 = 98%</b>"],
    ["Taxa de regeneração de arquivo (o oposto de delta)",
     "<b>~0%</b> — 3 candidatos, os 3 conferidos à mão, nenhum era reescrita"],
    ["Decisões rejeitadas registradas com motivo", "<b>6</b>, 15% das linhas vivas; nenhuma reapareceu"],
    ["Perguntas do dono abertas e respondidas", "11 abertas, <b>8 respondidas (73%)</b>"],
    ["Achados de revisão", "16, em 3 passagens; <b>4 dos 5 críticos fechados</b>"],
    ["Sabotagens do portão (ele reprova de verdade?)", "<b>3 de 3 reprovadas</b>, incluindo bloquear "
     "um commit com chave de acesso"],
    ["Módulos do plano sem tarefa no backlog", "<b>0</b>"],
], [8.6, 7.8])

h2("E o custo, que também foi medido")
p("A parte que dá credibilidade a um relatório é a que não favorece o autor:")
sp(2)
li("<b>15% das sessões</b> (5 de 34) foram gastas administrando o orçamento do próprio processo, "
   "sem uma linha de produto.")
li("<b>43% dos commits</b> não tocam código.")
li("<b>9 defeitos conhecidos</b> ficaram abertos por causa da regra de escopo — um deles de uma "
   "única linha de CSS.")
li("Um modo do produto ficou parado dias esperando uma decisão do dono.")
sp(4)
caixa("O achado mais valioso foi contra o próprio kit",
      "A medição encontrou uma checagem do portão que <b>tinha parado de checar em silêncio</b> "
      "e enxergava 12% dos casos que anunciava cobrir. Descobrir isso vale mais que confirmar "
      "que o processo funciona — e a correção não foi consertar aquele caso, foi criar o teste "
      "que impede a classe inteira do defeito de voltar.")

# ============================ 15. LIMITES ============================
h1("15. Onde o kit não serve (limites declarados)")
p("Estar escrito no próprio README é parte do argumento: nenhuma ferramenta serve para tudo, e "
  "declarar a fronteira é o que faz alguém confiar no que está dentro dela.")
sp(3)
tabela(["Contexto", "Serve?", "O que trava"], [
    ["Aplicação pequena ou média, com <b>um dono</b>", "<b>Sim — é o alvo</b>", "Nada"],
    ["Projeto que já existe", "Sim", "Começa por uma skill de adoção que produz o mapa a partir "
     "do código. Quanto maior o sistema, mais o teto de 4.000 aperta"],
    ["Time de 2 a 4 pessoas", "Parcialmente", "O limite de tarefas simultâneas é configurável, "
     "mas não há atribuição por pessoa nem junção de decisões concorrentes"],
    ["Aplicação grande (30+ módulos)", "<b>Não</b>", "4.000 caracteres não representam 30 módulos"],
    ["Projeto longo (100+ decisões)", "Com atrito", "O teto do registro dá cerca de 66 linhas, e "
     "o arquivamento exige decisão do dono"],
    ["Vários repositórios", "Não", "O kit assume um repositório e um contexto-fonte"],
    ["Integração contínua e revisão por pares", "Não cobre", "O único automatismo é o pre-commit"],
], [6.2, 2.6, 7.6], fonte_menor=True)
p("Há ainda um limite técnico honesto: a varredura de segredos é uma rede de arrasto, não uma "
  "garantia. Ela cobre 11 famílias de padrão e foi medida contra 8 formatos reais de vazamento "
  "(acertou os 8, com zero falsos positivos em 12 iscas) — mas um segredo num formato que ela "
  "não conhece passa. A versão anterior dessa varredura detectava <b>0 de 8</b>, e foi uma "
  "auditoria que revelou isso.")
pb()

# ============================ 16. PERGUNTAS ============================
h1("16. Perguntas prováveis da banca, com resposta pronta")
sp(2)


def qa(q, a):
    F.append(Paragraph(q, ParagraphStyle("q", parent=S["h3"], textColor=AZUL, spaceBefore=10,
                                         spaceAfter=2)))
    F.append(Paragraph(a, S["body"]))


qa("“Isso não é só documentação bonita?”",
   "Não, porque uma parte é <b>cobrada por máquina</b>. Há um script que reprova o commit em 14 "
   "situações, um hook que o roda sozinho e 57 testes que garantem que o próprio script continua "
   "funcionando. E o kit declara o tamanho da parte automática: 30 de 284 itens, cerca de 11%. "
   "Documentação bonita não reprova commit.")
qa("“Qual é o ganho concreto?”",
   "Três, e os três têm número: economia de contexto (o registro de decisões saiu de ~7.700 para "
   "~2.000 tokens por sessão de evolução; o contexto-fonte tem teto garantido); rastreabilidade "
   "(98% dos commits do projeto medido citam um identificador); e revisão possível (taxa de "
   "regeneração de arquivo perto de zero, o que mantém o diff pequeno).")
qa("“Depende de qual IA?”",
   "Não. Os agentes são arquivos Markdown que funcionam instalados na ferramenta ou colados numa "
   "conversa qualquer. O portão é Python de biblioteca padrão. O repositório é Markdown puro. O "
   "que muda de ferramenta para ferramenta é o conforto, não a capacidade.")
qa("“Como vocês impedem a IA de inventar coisa?”",
   "Por três mecanismos combinados: <b>lacuna declarada fica declarada</b> — o agente é instruído "
   "a nunca inventar dado, fonte ou número; regra de negócio ambígua não é dele para decidir, "
   "vira uma pergunta registrada e a sessão para; e o portão final roda <b>na máquina do dono</b>, "
   "não no ambiente do agente, então \"passou\" é um fato verificável e não uma afirmação.")
qa("“E se o agente errar mesmo assim?”",
   "Erra, e o processo assume isso. A fase de revisão é <b>adversarial e em sessão separada</b> — "
   "o mesmo contexto que construiu não enxerga o próprio ponto cego. Cada achado vira um "
   "identificador com reprodução e correção amarrada a um teste de regressão. E existe um "
   "critério de saída do laço, para não revisar para sempre.")
qa("“Vocês mediram, ou é opinião?”",
   "Mediu-se. Há uma avaliação de campo com o critério de sucesso escrito e hasheado antes de "
   "olhar os dados, e ela publica <b>o custo junto com o ganho</b>: 15% das sessões do projeto "
   "foram manutenção do próprio processo. É uma medição de um projeto só — ataca a falta de "
   "evidência, não a resolve.")
qa("“Qual a maior fraqueza?”",
   "A escala do orçamento. O teto do registro de decisões dá cerca de 66 linhas, e quando ele "
   "enche o arquivamento custa trabalho de verdade. Isso está declarado no README, foi medido no "
   "projeto real (a folga projetada era de poucos dias) e a solução — subir o teto — é uma "
   "decisão consciente, não um conserto pendente escondido.")
qa("“Por que Obsidian?”",
   "Por conforto de navegação e pelos modelos de um clique, que atacam o passo mais pulado do "
   "processo. Nada depende dele: é Markdown puro, e o pipeline funciona igual em qualquer editor.")
pb()

# ============================ ANEXO A ============================
h1("Anexo A — Glossário rápido")
tabela(["Termo", "Definição em uma linha"], [
    ["Agente / skill", "Arquivo que define um papel para a IA, com limites e portão próprios"],
    ["Append-only", "Só se acrescenta linha; nunca se edita nem apaga o que já foi registrado"],
    ["Backlog", "A fonte única de tarefas, com um limite declarado de tarefas simultâneas"],
    ["Baseline", "A medição de referência tirada antes de mexer em qualquer coisa"],
    ["Contexto", "Tudo o que é enviado ao modelo junto com o pedido"],
    ["Contexto-fonte", "O arquivo de verdade do projeto; único que toda sessão carrega"],
    ["Delta", "Só o trecho que mudou"],
    ["Frontmatter", "O cabeçalho de metadados no topo de uma nota Markdown"],
    ["Hook de pre-commit", "Programa que o git roda antes de cada commit e que pode bloqueá-lo"],
    ["Invariante", "Uma verdade que o sistema não pode violar nunca (ex.: saldo nunca negativo)"],
    ["Lacuna declarada", "Informação que falta e é registrada como faltando, jamais inventada"],
    ["Lista-morta", "O conjunto de decisões rejeitadas, mantido para impedir que voltem"],
    ["Portão", "Critério objetivo que separa pronto de não pronto"],
    ["Revisão adversarial", "Revisão que tenta quebrar, em sessão separada de quem construiu"],
    ["Sandbox", "O ambiente do agente — indicativo, nunca o portão final"],
    ["Token", "Unidade de cobrança do contexto; ~3 caracteres em português"],
    ["Vault", "A pasta de notas do Obsidian; aqui, a raiz do repositório"],
    ["WIP", "Trabalho em andamento; o kit cobra o limite que o próprio projeto declarou"],
], [3.4, 13.0], fonte_menor=True)
pb()

# ============================ ANEXO B ============================
h1("Anexo B — Ficha de avaliação preenchida")
p("Cada nota abaixo vem com a justificativa e o número que a sustenta, para você defender a "
  "pontuação item por item. Escala de 0 a 4. Campos que dependem de informação que não está no "
  "repositório ficaram em branco de propósito.")
sp(4)
tabela(["Campo", "Resposta", "Justificativa e evidência"], [
    ["<b>Role</b>", "<i>(em branco)</i>",
     "Depende do que a banca entende por \"Role\". Confirmar antes de preencher."],
    ["<b>IDE</b>", "Claude Code / Claude Desktop", "Ferramenta usada nas sessões do projeto."],
    ["<b>LLM</b>", "Claude Opus 5 (esforço MAX)", "Modelo usado nas sessões do projeto."],
], [2.6, 4.0, 9.8], fonte_menor=True)
h3("Domain")
tabela(["Item", "Qual?", "Nota", "Justificativa"], [
    ["<b>MCP</b>", "nenhum", "<b>0</b>",
     "Verificado: não há servidor MCP configurado nem menção a MCP em nenhum arquivo do kit ou do "
     "projeto. A integração é por skills e por hook de git, não por MCP."],
    ["<b>Agent</b>", "24 agentes de papel único", "<b>4</b>",
     "24 agentes com papel, limites e portão próprios, agrupados por fase, arquitetura, backend, "
     "frontend, transversais, sistema vivo e dados. Regra de <b>uma skill por sessão</b>, e a "
     "ordem entre eles é documentada."],
    ["<b>Skill</b>", "24 <font face='DJ-M' size='8'>SKILL.md</font> instaláveis", "<b>4</b>",
     "Formato nativo do Claude Code/Cowork, com nome e descrição no cabeçalho. O <b>esquema é "
     "cobrado por script</b>: skill sem \"Contexto que você recebe\", \"Limites\" ou \"Saída\" "
     "reprova o commit; descrição sem fronteira negativa gera aviso."],
    ["<b>Brain</b>", "contexto-fonte + registro + contrato de leitura", "<b>4</b>",
     "Memória deliberada e orçada: contexto-fonte de 4.000 caracteres como fonte única, registro "
     "append-only de decisões com teto de 12.000, temas de domínio lidos sob demanda, "
     "aprendizados acumulados e um contrato de leitura que declara o que <b>nunca</b> ler. "
     "Limite conhecido e declarado: o teto do registro não escala além de ~66 linhas."],
], [2.0, 3.2, 1.4, 9.8], fonte_menor=True)
h3("SPC — especificação")
tabela(["Item", "Nota", "Justificativa"], [
    ["<b>Functional</b>", "<b>4</b>",
     "Contexto-fonte com objetivo, restrições inegociáveis e critério de aceite objetivo no dia 1; "
     "plano com módulos e milestones; backlog em que <b>todo card tem portão escrito</b>. Uma "
     "sessão dedicada (consistência-artefatos) confere se especificação, plano e tarefas contam a "
     "mesma história, e reprova critério de aceite sem número."],
    ["<b>Technical</b>", "<b>4</b>",
     "Stack e restrições da stack declaradas antes do primeiro código; <b>representações "
     "obrigatórias</b> (dinheiro em inteiro, data UTC, identificador opaco); contrato por módulo "
     "com porta única, dono de estado e portão objetivo; plano congelado por decisão registrada, "
     "e mudança de porta exige nova decisão."],
], [2.6, 1.6, 12.2], fonte_menor=True)
h3("Guardrail")
tabela(["Item", "Nota", "Justificativa"], [
    ["<b>Doc</b>", "<b>4</b>",
     "Contrato de leitura carregado em toda sessão; 7 regras com o motivo de cada uma; checklist "
     "de 118 itens; seção <b>Limites</b> obrigatória nas 24 skills; templates de decisão, achado "
     "e fecho de sessão. E a declaração de cobertura (30 de 284) é <b>cobrada por teste</b>."],
    ["<b>Code</b>", "<b>4</b>",
     "Portão em Python sem dependências, com 14 falhas e 16 avisos, instalado como hook de "
     "pre-commit; varredura de segredo na árvore <b>e no histórico</b>; integração contínua em "
     "Linux e Windows a cada envio. Verificado por sabotagem: 3 de 3 violações plantadas foram "
     "reprovadas, incluindo o bloqueio de um commit com chave de acesso."],
], [2.6, 1.6, 12.2], fonte_menor=True)
h3("Test")
tabela(["Item", "Nota", "Justificativa"], [
    ["<b>Unit</b>", "<b>4</b>",
     "57 testes no kit, só com biblioteca padrão, incluindo <b>uma isca canônica por checagem</b> "
     "e um teste que exige que toda checagem nova tenha a sua. No projeto medido: 385 testes, com "
     "invariantes verificados por sabotagem (reverter a regra à mão reprova o teste)."],
    ["<b>System</b>", "<b>3</b>",
     "O kit testa ponta a ponta os próprios fluxos (criar projeto, atualizar, instalar hook, "
     "rodar o portão sobre um repositório montado do zero). O que impede a nota 4 é o lado do "
     "projeto: há teste de integração entre módulos, mas <b>nenhuma tela tem teste automatizado</b> "
     "— o ambiente roda sem navegador, e a conferência visual ficou como ação manual do dono. "
     "A lacuna está declarada no próprio projeto, não escondida."],
], [2.6, 1.6, 12.2], fonte_menor=True)
h3("Other")
tabela(["Item", "Nota", "Justificativa"], [
    ["<b>GitHub</b>", "<b>4</b>",
     "Repositório público sob licença MIT, com integração contínua rodando o portão em Linux e "
     "Windows a cada envio, hook de pre-commit instalável por comando, e convenção de commit "
     "citando os identificadores — medido em 98% no projeto real."],
    ["<b>Planilha</b>", "<i>vazio</i>",
     "O projeto não usa planilha, e o item veio sem escala. Confirmar o que a banca espera aqui."],
    ["<b>Agnostic</b>", "<b>4</b>",
     "Markdown puro e Python de biblioteca padrão, sem nenhuma dependência externa. As skills "
     "funcionam instaladas ou coladas em qualquer ferramenta de IA; o Obsidian é opcional; roda "
     "em Windows, Linux e Mac, com o encoding testado nos dois sistemas. A única parte específica "
     "de ferramenta é o modo \"instalado\" das skills."],
    ["<b>Explanation</b>", "—",
     "Um processo reutilizável para construir software com agentes de IA mantendo rigor e "
     "gastando pouco contexto. Ele impõe orçamento numérico ao que a IA relê a cada sessão, exige "
     "delta em vez de reescrita, registra decisões — inclusive as rejeitadas — e cobra por "
     "máquina o que dá para cobrar por máquina, declarando com honestidade o tamanho da parte que "
     "continua humana: 30 de 284 itens."],
], [2.6, 1.6, 12.2], fonte_menor=True)


# ============================ RENDER ============================
def rodape(canv, doc):
    canv.saveState()
    canv.setFont("DJ", 7.5)
    canv.setFillColor(CINZA)
    if doc.page > 1:
        canv.drawString(2.3 * cm, 1.25 * cm, "Pipeline de Projetos com IA — guia de apresentação")
        canv.drawRightString(A4[0] - 2.3 * cm, 1.25 * cm, str(doc.page))
        canv.setStrokeColor(BORDA)
        canv.setLineWidth(0.4)
        canv.line(2.3 * cm, 1.65 * cm, A4[0] - 2.3 * cm, 1.65 * cm)
    canv.restoreState()


import sys as _sys
SAIDA = _sys.argv[1] if len(_sys.argv) > 1 else \
    "/home/claude/pdf/pipeline-projetos-ia-apresentacao.pdf"
doc = BaseDocTemplate(SAIDA,
                      pagesize=A4, leftMargin=2.3 * cm, rightMargin=2.3 * cm,
                      topMargin=2.0 * cm, bottomMargin=2.1 * cm,
                      title="Pipeline de Projetos com IA — guia de apresentação",
                      author="Gustavo")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="n")
doc.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=rodape)])
doc.build(F)
print("PDF gerado em", SAIDA)
