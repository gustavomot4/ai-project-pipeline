---
tags: [estudo, kit, mcp]
status: atual
data: 2026-08-22
---
# Vale a pena colocar MCP no kit?

**Resposta: não. Confiança alta.** Quatro pesquisas independentes com busca na web chegaram a
"não" separadamente, e um quinto agente encarregado de *matar a ideia* montou um caso mais
forte que a soma delas. Este documento guarda o porquê, para que a pergunta não volte a cada
seis meses sem resposta.

> **O que é MCP, em uma frase:** um protocolo que deixa a IA conversar com programas externos
> (bancos, GitHub, sistemas de arquivo) através de "ferramentas" que ela enxerga como opções
> disponíveis. Cada ferramenta disponível ocupa espaço na janela de contexto **de toda sessão**,
> tenha sido usada ou não.

## A conta que decide, e ela é aritmética, não filosófica

O kit inteiro existe para gastar menos contexto. O teto que ele cobra por script — 4.000
caracteres no arquivo que toda sessão carrega — vale cerca de **1.000 a 1.150 tokens**.

| O que | Custo por sessão | Contra o teto do kit |
|---|---|---|
| As 4 ferramentas de linha de comando que o kit **já tem** | **0 tokens** | — |
| Servidor MCP mediano (mediana de 7.315 servidores medidos) | 1.984 tokens | **2×** o teto inteiro |
| Um servidor MCP feito sob medida para os 4 scripts do kit | ~495 tokens | metade do teto |
| Servidor de memória oficial da Anthropic (9 ferramentas) | 2.700–5.400 | 2,7× a 5,4× |
| Servidor MCP do GitHub (86 ferramentas) | 14.406 | 14× |
| O único servidor MCP de registro de decisão que existe (73 ferramentas) | 21.900–43.800 | 22× a 44× |

O detalhe que fecha a discussão: **`check.py`, `evidencia.py`, `arquivar.py` e `task.py` custam
zero token de definição**, porque entram pelo Bash — que o Claude Code sempre carrega e nunca
cobra. O custo de *saída* é idêntico pelos dois caminhos (medido: o relatório do `check.py` são
725 caracteres ≈ 181 tokens, iguais nos dois). A diferença está só na definição, e ali o placar
é **0 contra ≥495**.

Qualquer caminho por MCP custa estritamente mais que o caminho atual e **não entrega nenhuma
capacidade nova em troca**.

## Três agravantes que só apareceram quando alguém tentou destruir a ideia

**1. O custo do MCP é incobrável.** Todo teto deste kit existe porque um script reprova o
commit. Não existe `check.py` capaz de reprovar o custo de definição de uma ferramenta MCP:
esse gasto é imposto pelo cliente, fora do repositório, fora da jurisdição do portão. O kit
estaria importando permanentemente ~50% do orçamento que defende, num lugar onde a própria
arquitetura de fiscalização não alcança. **Custo que não se mede não se cobra.**

**2. O campo `instructions` é um segundo arquivo de contexto sem portão.** Todo servidor MCP
tem um campo de instruções que entra na sessão sempre e aceita até 2 KB. É exatamente onde a
prosa sobre o kit iria se acumular — fora do arquivo cobrado, fora do teto, sem script nenhum
olhando. O `CLAUDE.md` proíbe isso com todas as letras: o excedente vai para `a_context/<tema>.md`,
*"nunca para prosa comprimida, e nunca estourando o teto"*. Um servidor MCP cria o vazadouro
que a regra existe para fechar.

**3. O alívio não chega onde dói.** Existe um mecanismo que adia as definições e corta 85% do
custo — mas ele só liga acima de ~10.000 tokens (10% da janela). Um servidor do kit, com 1 a 4
ferramentas, fica muito abaixo do gatilho e **paga o preço cheio em toda sessão**. Caro demais
para compensar, barato demais para ser adiado.

## Manutenção: MCP piora exatamente a nota que já é a pior

O benchmarking mediu que o kit depende de uma pessoa (nota 1) e que 61,5% dos commits do
projeto real tocaram só arquivos de processo. MCP ataca os dois pelo lado errado:

- **É trabalho de processo puro.** Cada hora no servidor engorda os 61,5% e não vira produto.
- **A promessa de zero dependência morre.** Hoje os 8 scripts importam só biblioteca padrão, e
  é isso que permite o CI rodar em Ubuntu **e** Windows sem instalar nada. O SDK oficial de
  Python puxa **17 dependências obrigatórias**. A saída honesta — escrever o protocolo na unha —
  significa manter implementação própria de protocolo com zero linha de teste, ao lado de um
  portão que tem 1.476.
- **O protocolo é alvo móvel.** A revisão de 2026-07-28 depreciou três primitivas de uma vez
  (Sampling, Roots, Logging) e mudou o protocolo de com-estado para sem-estado. A extensão que
  teria exatamente o formato deste kit está "em revisão", sem data e sem adoção.
- **A duplicação que o `task.py` matou voltaria pela porta dos fundos.** MCP não roda em CI, não
  roda no hook de pre-commit, não roda em modo não interativo. Os dois caminhos existiriam para
  sempre — e dois caminhos para a mesma regra, divergindo em silêncio, é a pior classe de defeito
  que um portão pode ter: ele continua verde e para de significar alguma coisa.

## O que o mercado fez

**Nenhum** framework de processo comparável expõe o próprio processo como servidor MCP oficial —
zero de cinco (Spec Kit, BMAD, Kiro, Cline, Cursor). No BMAD, que é o mais parecido com este kit,
pediram MCP **duas vezes** e nunca virou oficial. Onde MCP aparece nesses produtos, ele nunca
carrega o processo: carrega a borda com sistema externo.

E há caso real de arrependimento: em março de 2026 a AWS **depreciou 12 servidores MCP de uma
vez**, e substituiu um deles explicitamente por uma *skill* — o mesmo formato de arquivo que
este kit já usa.

Quando alguém mediu MCP contra linha de comando para a mesma operação, a linha de comando ganhou
por **177×** (16.100 tokens contra 91). No melhor caso publicado a favor do MCP, a diferença cai
para 6–10% — ou seja, **empate**. E empate é derrota para uma proposta que pede superfície nova.

## O que muda a resposta (o gatilho de revisão)

Esta decisão vale enquanto estas três coisas forem verdade. Se qualquer uma virar, reabra:

1. **O kit continuar rodando dentro de um agente que já tem Bash.** Se um dia for preciso operar
   o kit de dentro de uma ferramenta sem terminal, MCP passa a ser o único caminho — e aí o custo
   deixa de ser desperdício e vira o preço de existir.
2. **O carregamento sob demanda continuar exigindo ~10.000 tokens para ligar.** Se ele passar a
   valer para servidores pequenos, o custo cai de ~495 para ~12 tokens e a conta muda de sinal.
3. **A extensão de Skills do MCP continuar em revisão.** Se ela for aprovada e adotada, existe
   um formato oficial para o que o kit já faz à mão, e vale reavaliar.

## A única ideia que sobreviveu

Um servidor MCP merece teste, e **não é um servidor do kit**: é o **Serena**, que faz leitura
semântica de código — a IA pede "a função X" em vez de ler o arquivo inteiro.

Ele é o único candidato que **não duplica nada** do kit, e ataca um custo que o kit nunca
endereçou: o kit controla o que a sessão lê de *documentação*, e não faz nada sobre o que ela lê
de *código*. Números divulgados falam em 98,7% de redução (150.000 → 2.000 tokens) num caso da
Anthropic; o próprio Serena anuncia 99% e usuários relatam ~70%, **sem medição independente**.

Isso é hipótese para testar com número, não recomendação. E o teste é barato: ligar, rodar uma
sessão real, medir.

## O que NÃO foi feito neste estudo

Ninguém rodou `/context` numa sessão real do kit para medir o consumo de verdade. Tudo aqui vem
de fonte publicada mais uma leitura dos arquivos do kit. E há uma armadilha registrada para quem
for medir: o `/context` do Claude Code **infla o custo do MCP em cerca de 3×**, porque conta um
prompt oculto uma vez por ferramenta em vez de uma vez só. O número que aparece na tela é
pessimista.
