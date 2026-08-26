---
tags: [inicio, guia]
status: atual
---
# Primeiros passos — para quem NÃO construiu este kit

> Todos os outros documentos daqui foram escritos por quem já conhecia o kit. Este foi
> escrito para você, que chegou agora. Ele cabe em quinze minutos e diz, de propósito,
> **o que ignorar** — porque a maior fraqueza medida deste kit é custo de adoção, e um guia
> que manda ler tudo piora exatamente o problema que ele deveria resolver.

## Em uma frase

O kit é uma pasta de documentação que entra no seu projeto e faz três coisas: **guarda as
decisões (inclusive as recusadas)**, **trava o commit quando a higiene falha**, e **limita o
quanto a IA lê a cada sessão**. O resto é apoio para essas três.

## A primeira hora

```
python scripts/new_project.py ../meu-app --name "Meu App" --code src
cd ../meu-app && git init
python 77777777_*_Project_DOCs/scripts/task.py hook
```

Pronto: o portão passa a rodar em todo commit. Agora abra **um** arquivo,
`a_context/a_context_source.md`, e preencha o objetivo, as restrições e a stack. Ele tem teto
de 4.000 caracteres e é o único que **toda** sessão de IA carrega — por isso cada caractere
ali é pago de novo em cada conversa.

Rode `python scripts/task.py check` e conserte o que ele reclamar. Fim da primeira hora.

## O que IGNORAR no começo

| Ignore | Até quando |
|---|---|
| As 24 skills em `b_process/skills/` | até saber qual módulo você vai construir. Você vai usar 3 ou 4, não 24 |
| O `b_checklist.md` (118 itens) | até a primeira entrega. É lista de conferência, não de leitura |
| `d_history/` e `e_qa/` | **sempre.** São históricos. Nenhuma sessão precisa deles |
| O caso de referência | é exemplo de formato, não manual |
| `arquivar.py`, `evidencia.py` | até o projeto ter uns 30 commits |

Se alguém mandar você "ler o kit inteiro", está errado — o próprio `CLAUDE.md` proíbe isso.

## Quando NÃO usar este kit

Esta seção existe porque um kit honesto precisa dizer onde ele atrapalha. **Não use se:**

- **O trabalho tem menos de uma semana.** A cerimônia não se paga. Um `AGENTS.md` de vinte
  linhas resolve melhor.
- **Você não vai usar IA para escrever o código.** Quase tudo aqui existe para conter agente
  de IA. Sem isso, sobra burocracia.
- **Você precisa de isolamento ou permissão fina** (sandbox, allowlist de comando). O kit não
  faz isso — o portão dele pega o *commit*, não a *ação*. Use as duas travas de agente
  (`task.py escopo` e `task.py portao`) e as permissões da sua ferramenta de IA para essa
  metade: elas cobrem o caminho de quem tem pressa, não o de quem quer burlar.
- **A equipe é grande e distribuída.** O kit foi medido com **uma** pessoa e **um**
  repositório. Não há papéis, permissões nem regras de time.
- **Você quer garantia de que vai ficar mais rápido.** Ninguém mediu isso. As duas únicas
  medições independentes que existem no mercado sobre processo pesado apontam para **mais**
  custo, não menos. O que este kit entrega e é medido é *rastro*, não *velocidade*.

## Os três hábitos que fazem valer

Se você guardar só três coisas deste kit, guarde estas:

1. **Registre o que foi RECUSADO, não só o que foi decidido.** É uma linha assim no
   `c_decisions.md`:

   ```
   | D-07 | 2026-08-22 | REJEITADO | Banco em servidor próprio | +R$ 40/mês contra R$ 0 do arquivo local |
   ```

   Sem ela, a IA repropõe toda semana o que já morreu, e alguém precisa lembrar o argumento
   de novo. (Este exemplo está em bloco de código de propósito: o portão confere se todo
   `D-NN` citado existe de verdade, e pegou este guia na primeira vez que o escrevi.)
2. **Achou bug fora do seu escopo? Registre `QA-NN` e siga.** Não conserte de carona. O diff
   inchado é como uma sessão vira três.
3. **Regra de negócio ambígua não é sua para decidir.** Abra `Q-NN` e pare. É melhor uma
   pergunta hoje que uma reescrita na semana que vem.

## Quando o portão reprovar

Ele diz o que fazer em cada mensagem. Duas regras de conduta:

- **Não desligue — e, se desligar, diga por quê.** `git commit --no-verify` existe para a
  emergência, não para o costume. Com a trava do pulo ligada (`task.py portao`), a mensagem
  precisa trazer `SEM-PORTAO: <motivo>`; sem ela, o commit é recusado. Não é burocracia: sem
  esse rastro ninguém — nem o `evidencia` — consegue dizer quantas vezes o portão foi pulado,
  e portão com taxa de contorno desconhecida não tem taxa de contorno zero.
- **Se ele reclamar de algo que não é problema de verdade, isso é um defeito DELE.** Anote e
  conte para quem mantém o kit. Portão que dá alarme falso ensina a ignorar alarme.

## Para onde ir depois

- **Construir de fato:** [[a_roadmap|ROTEIRO]], fase por fase.
- **Entender os termos** (`D-NN`, portão, contexto-fonte): [[f_glossary_and_primer|PRIMER]].
- **As 7 regras e onde o kit para:** [[README]].
- **Medir o que o kit produziu no seu projeto:** `python scripts/task.py evidencia`.
