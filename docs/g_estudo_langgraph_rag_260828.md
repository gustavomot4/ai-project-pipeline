---
tags: [estudo, kit, langgraph, rag]
status: atual
data: 2026-08-28
---
# Vale a pena colocar LangGraph e RAG no kit?

**Resposta: não para os dois — mas por motivos diferentes, e nenhum deles é o motivo que matou
o MCP.** Quatro pesquisas independentes com busca na web, um agente encarregado de fazer o
**melhor caso a favor**, e um agente encarregado de destruir as duas ideias *e* o advogado.
O advogado achou um erro de medição que invalidava metade da acusação; o matador achou um erro
do advogado que invalidava a defesa. As duas correções estão registradas aqui.

> **Em uma frase cada um.** *LangGraph* é uma biblioteca para **você construir** o robô de IA:
> ela define os passos, guarda o estado e decide o que vem depois. *RAG* é achar trecho de
> texto **por significado** em vez de por palavra exata: você pica os documentos, transforma
> cada pedaço em números e, na pergunta, traz os mais parecidos.

## O que este estudo corrigiu antes de concluir

**1. O corpus não tem 45 mil caracteres. Tem 1,18 milhão.** O número de 45 mil, usado na
primeira análise, era a soma de **quatro arquivos vivos**. Medido em disco, o vault do projeto
real tem **80 arquivos markdown e 1.176.231 caracteres — cerca de 336 mil tokens**. A própria
Anthropic publica que abaixo de ~200.000 tokens a base deve ir inteira no prompt, sem RAG:
**esse limiar já foi cruzado**. O argumento "o corpus é pequeno demais para justificar busca"
estava errado, e ele sustentava metade da rejeição.

**2. A "amnésia de 29%" não existe.** O advogado contou 27 identificadores de decisão que só
aparecem em arquivo que o `CLAUDE.md` manda não ler, e chamou isso de amnésia estrutural. O
matador refez a conta e achou a causa: o arquivo vivo lista os retirados em **notação de
intervalo** (`D-01..D-05`), e o `grep` literal por `D-03` não casa com isso. Os 27 estão todos
indexados numa linha de ~200 caracteres com ponteiro para o arquivo-morto. **Cobertura real:
100%.** O advogado demonstrou a fraqueza do grep caindo nela — e leu o resultado ao contrário.

## O que mata cada um

### LangGraph — o estado já está persistido, e o checkpointer chama-se git

LangGraph vende quatro coisas: nós, arestas, estado e retomada durável. As três primeiras não
têm onde encaixar, porque **quem executa é o Claude Code** — o kit não constrói runtime. A
quarta, a única defensável, **já existe**: o estado do processo é o working tree. Contexto,
decisões, backlog e changelog estão em disco, versionados, com histórico, diff e retomada por
`git checkout`. Um checkpointer do LangGraph é *estritamente pior* nessa função, porque grava
um blob que o dono não lê nem edita à mão — e "o dono edita entre os turnos" é regra escrita
do próprio kit.

O custo, medido, não é retórico:

| | |
|---|---|
| Pacotes instalados por `pip install langgraph` (dry-run nesta máquina) | **20 pacotes, 3,2 MB** |
| Dependências do kit hoje | **0** |
| Releases desde o 1.0 (out/2025) até ago/2026 | ~31, com 2 saltos de *minor* e 1 versão retirada do ar |
| Issues abertas no repositório | 478, sendo 190 com rótulo *bug* |
| Quebra dentro de versão de correção | issue #6363: parâmetro obrigatório novo em release de patch |
| Linhas para um fluxo "usa ferramenta até terminar" | ~50 no harness da Anthropic · ~400 em LangGraph · **0 no kit**, porque é o Claude Code |

O post-mortem mais citado do ecossistema (Octomind, "Why we no longer use LangChain") descreve
o modo de falha: mais de 12 meses em produção, removido quando a equipe passou a gastar tanto
tempo entendendo as abstrações quanto construindo funcionalidade.

### RAG — a lista-morta já está viva no arquivo vivo, por regra

O melhor caso a favor era: *"as 10 decisões rejeitadas existem para impedir retrabalho, e
perguntar 'já rejeitamos algo parecido?' exige lembrar o vocabulário exato de semanas atrás —
onde grep falha e similaridade ganha."* O argumento é bom. Ele só é falso **neste kit**, e o
próprio arquivo diz por quê:

> Desde `D-74`, só as REJEITADAS guardam linha viva — são a lista-morta que a fase de evolução
> varre sem abrir o arquivo-morto.

Medição: `grep -c "REJEITADO"` no arquivo vivo → **10 de 10**. O kit já resolveu, com uma linha
de política e zero dependências, exatamente o problema que o RAG foi convocado para resolver.

Some-se o que a pesquisa achou sobre o terreno:

- a equipe do **Claude Code removeu** o pipeline de embeddings e o banco vetorial em maio de
  2025 — o kit estaria reimplementando por fora, com uma pessoa, o que o fornecedor descartou;
- **Amazon Science (AAAI 2026)**: busca por palavra-chave dentro de agente atinge **94,5% da
  fidelidade** do RAG com banco vetorial, sem nenhum banco vetorial;
- **GrepRAG (CrossCodeEval)**: `grep` ingênuo 38,61% de acerto exato contra 24,99% do BM25 e
  19,44% do índice de grafo, com recuperação em 0,0186 s contra 0,2582 s;
- o conteúdo do kit é dominado por **correspondência exata** — `D-NN`, `QA-NN`, nomes de skill
  e de arquivo —, que é o pior caso para similaridade vetorial;
- **33 modos de falha** catalogados em pipelines RAG (TrustNLP 2026), cada um virando teste
  novo num portão que já tem 99.

**A honestidade do outro lado, que fica registrada:** existe evidência séria a favor de
embeddings quando a base é grande — a Cursor mediu **+12,5% de acurácia** em teste A/B de
produção, e o SWE-QA mediu 65,2% contra 46,2% a favor da busca semântica em perguntas sobre
repositório. Nenhum desses cenários é o do kit hoje, mas os números existem e não foram
inventados por quem defende o grep.

## A distinção que precisa ficar escrita (senão o kit vira dogma)

O que matou o **MCP** em 22/08 foi aritmética: ~1.984 tokens de definição em **toda sessão**,
e — decisivo — **custo incobrável**, fora da jurisdição do portão.

**Nem LangGraph nem RAG têm esse defeito.** Os dois entram pelo Bash e custam **zero token de
definição**; e um índice é cobrável (o `check.py` pode gravar o hash de cada `.md` e reprovar
commit com índice velho). Rejeitá-los citando o precedente do MCP seria preguiça travestida de
jurisprudência. Eles morrem por motivos próprios: **LangGraph porque o git já é o checkpointer;
RAG porque a lista-morta já está na primeira tela.**

## O que sobreviveu ao ataque

**Um índice lexical de identificadores**, em biblioteca padrão, gerado e cobrado pelo
`check.py`: expandir intervalos (`D-01..D-05`) e emitir `ID → arquivo:linha`. Ele nasceu do
**erro do advogado**, não da tese dele: o `grep` literal realmente erra na notação de
intervalo, e isso é defeito real, reproduzível e cobrável. Zero dependência, zero token de
sessão, sem índice que envelhece em silêncio. Captura o ganho que o RAG prometia sem nada do
que reprova o RAG.

## O experimento que decide, e que ninguém rodou

O advogado escreveu o protocolo e não o executou — mediu o número que ajudava o caso dele em
vez do número que o testava. Ele fica registrado aqui, com o critério **congelado antes**:

> Pegue as 10 decisões rejeitadas e as 27 arquivadas. Formule **20 perguntas reais** no formato
> "já decidimos alguma coisa sobre X?", **sem citar o identificador**. Meça quantas o `grep`
> responde partindo só do enunciado.
>
> **≥ 16 de 20** → RAG rejeitado, questão encerrada.
> **≤ 12 de 20** → a adoção passa a ser obviamente certa.
> **13 a 15** → adota-se apenas o índice lexical acima.

Previsão registrada do matador, para poder ser desmentida: o `grep` passa de 16/20.

## O achado colateral, que vale mais que a pergunta original

Ao medir o corpus para responder sobre RAG, apareceu o ponto cego:

| arquivo | caracteres | × o teto que o kit cobra |
|---|---|---|
| `d_history/a_changelog.md` | 249.516 | **62×** |
| `b_process/c_backlog.md` | 200.832 | **50×** |
| `b_process/d_agent_learnings.md` | 72.564 | 18× |
| `e_qa/decisions_archive.md` | 48.283 | 12× |
| `a_context/b_plan.md` | 40.349 | 10× |

**O kit cobra 4.000 caracteres em um arquivo e não mede os outros 1,17 milhão.** `b_process/`
sozinho é 40% do corpus — processo sobre processo. É o mesmo indicador dos 61,5% de commits que
não tocam produto, agora medido em caracteres em vez de commits.

## Custo de oportunidade — o que fazer com o mesmo esforço

1. **Apontar o teto para onde está a gordura**: `d_agent_learnings.md` e o changelog. Uma
   constante e uma FALHA nova; o mecanismo já existe e já funciona.
2. **Testar por que 14 das 24 skills nunca dispararam.** A hipótese barata é que elas são
   *inalcançáveis*, não supérfluas — vivem em `b_process/skills`, sem despacho automático.
3. **O índice lexical** que sobreviveu ao ataque.
4. **Rodar o experimento das 20 perguntas** antes de qualquer outra coisa sobre busca.

## Veredito

**LangGraph: REJEITADO.** Não há segunda camada de agente para construir, e o estado já está
num checkpointer melhor — o git. Gatilho para reabrir: o kit deixar de ser processo para o
trabalho do dono e virar produto que hospeda agentes para terceiros.

**RAG: REJEITADO, com gatilho registrado.** As duas condições de corpus já foram satisfeitas
(tamanho acima do limiar, conteúdo em arquivo que a regra manda não abrir), mas a condição que
decide — *o `grep` falha em perguntas reais* — nunca foi medida. Enquanto ela não for, a
resposta é não. Se o experimento das 20 perguntas der 12 ou menos, este documento está errado e
a decisão muda.
