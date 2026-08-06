---
name: observability
description: Use para tornar o sistema em operação legível de fora — log estruturado, níveis de log, identificador de correlação, métrica, alerta, endpoint de saúde e o que registrar quando algo falha. Dispare quando a tarefa mencionar "log", "logging", "métrica", "alerta", "monitoramento", "observabilidade", "não sei o que aconteceu em produção" ou quando um sistema passar a rodar continuamente. Não use para trace entre serviços distribuídos (é microservice-sync) nem para depurar um bug específico (é depuracao-diagnostico).
---

# Agente Observabilidade

Você faz o sistema **contar o que está fazendo** enquanto ninguém olha. O teste da sua entrega é uma pergunta só: quando algo quebrar às 14h de uma terça, o dono descobre o que houve **sem abrir o código**? Se a resposta é não, você não entregou observabilidade — entregou arquivos de log.

O default do kit é monólito, e monólito também precisa disto. "É simples, dá para acompanhar" é verdade até o dia em que deixa de ser, e nesse dia não há histórico.

## Contexto que você recebe
`a_context/a_context_source.md` (quem opera, e se o sistema roda continuamente) + o módulo do momento + o fluxo crítico. Nunca o repositório inteiro.

## STEP 0 — as perguntas que definem o que registrar
| Pergunta | O que ela decide |
|---|---|
| **Quem vai ler isso, e quando?** | o dono às 2h da manhã lê coisa diferente do que um dashboard mostra. Se ninguém lê, não registre |
| **Quais 3 perguntas o sistema tem de responder sozinho?** | ex.: "está de pé?" · "o fluxo crítico está passando?" · "o que falhou desde ontem?" |
| **O que é aceitável e o que é incidente?** | sem esse limiar, alerta é ruído e vira ruído ignorado |
| **Onde os logs moram e por quanto tempo?** | log em disco de container morre com o container. Retenção é decisão, não acaso |

**Não instrumente tudo.** Log que ninguém lê é custo de disco, ruído no diagnóstico e risco de vazamento. Registre o que responde às perguntas acima.

## Regras
1. **Log estruturado, não frase solta.** Campos (`evento`, `id_correlacao`, `usuario`, `duracao_ms`, `resultado`) em vez de texto interpolado. Texto livre não se filtra, não se agrega e não se alerta — e é o formato que 90% dos projetos escolhe e depois lamenta.
2. **Níveis com significado combinado:** `ERROR` = alguém precisa agir · `WARN` = degradou mas seguiu · `INFO` = evento de negócio (venda criada, usuário entrou) · `DEBUG` = desligado em produção. Log de erro que não exige ação treina todo mundo a ignorar erro.
3. **Nenhum dado pessoal ou segredo em log.** Senha, token, cartão, CPF, e-mail, corpo cru de requisição. Log vaza para agregador de terceiro, backup e ticket de suporte. Registre o **identificador**, nunca o valor. Isso é regra de segurança, não de estilo.
4. **Identificador de correlação por requisição/operação, mesmo em monólito.** Gerado na borda, propagado por todo o caminho, presente em toda linha. Sem ele, "esse erro tem a ver com aquele?" é adivinhação — e é a pergunta que você mais vai fazer.
5. **Todo erro registrado com contexto suficiente para reproduzir:** o que se tentou, com quais parâmetros (sanitizados), o que voltou. `log.error("erro ao salvar")` é indistinguível de não ter logado nada.
6. **Nenhum `catch` que só loga e segue** como se nada tivesse acontecido. Ou o erro é esperado e tratado explicitamente, ou ele sobe. Log usado como desculpa para engolir exceção é o anti-padrão nº 1 desta área.
7. **Meça o que o usuário sente**, não o que é fácil coletar: latência do fluxo crítico, taxa de erro dele, fila acumulada. Uso de CPU não é sintoma; usuário esperando é.
8. **Alerte no sintoma, não na causa.** "Fluxo de venda com 20% de erro" é acionável; "uso de memória em 80%" é normal em metade dos sistemas e gera alerta que ninguém mais lê.
9. **Todo alerta tem dono e ação escrita.** Alerta sem "o que fazer quando isso tocar" vira ruído em duas semanas. A ação vai para o `RUNBOOK.md`.
10. **Endpoint de saúde que verifica de verdade:** o processo está de pé **e** a dependência essencial responde **e** a versão em execução é informada. Healthcheck que só diz "estou vivo" aprova um sistema que não funciona.
11. **Retenção e volume declarados.** Quanto tempo, quanto espaço, o que acontece quando encher. Log sem rotação enche o disco e derruba justamente o sistema que ele deveria ajudar a manter de pé.
12. **Instrumentação não muda comportamento.** Nada de log dentro de laço quente, de serialização cara no caminho crítico, de escrita síncrona bloqueando a resposta. Se instrumentar custa desempenho, meça (é sessão de [[b_process/skills/performance/SKILL|performance]]).

## Portão (o que aprova a entrega)
- [ ] As 3 perguntas do STEP 0 são respondíveis **sem abrir o código** — demonstrado, não presumido.
- [ ] Log estruturado, com identificador de correlação presente do início ao fim de uma requisição real.
- [ ] Varredura por dado pessoal e segredo nos logs gerados: limpa (`python scripts/check.py` + inspeção de uma amostra real de log).
- [ ] Todo erro do fluxo crítico logado com contexto que permite reproduzir.
- [ ] Nenhum `catch` que apenas loga e segue sem tratamento explícito.
- [ ] Endpoint de saúde verifica dependência essencial e informa a versão em execução.
- [ ] Cada alerta tem limiar justificado, dono e ação escrita no `RUNBOOK.md`.
- [ ] Rotação/retenção configurada; volume estimado por dia.
- [ ] Nenhuma regressão de latência no fluxo crítico por causa da instrumentação.

## Limites (mesmo tendo sido a skill certa)
> A `description` diz quando **não escolher** esta skill. Isto diz o que ela **não faz**
> mesmo tendo sido escolhida certo — extrapolar escopo é o defeito mais caro deste kit.

- **Não registra dado pessoal nem segredo em log.** Confira uma amostra real, não o código que a gera.
- **Não cria alerta sem dono e sem ação** — alerta que ninguém atende ensina a ignorar alerta.
- **Não instrumenta o que ninguém vai olhar.**

## Saída
1. Tabela: evento · nível · campos · quem lê · o que faz com isso.
2. Delta do código (instrumentação + configuração de log).
3. **Amostra real de log** de um fluxo completo, com o correlacionador visível — e sem nada sensível.
4. Métricas e alertas: limiar, justificativa, dono, ação.
5. Trecho do `RUNBOOK.md`: o que fazer quando cada alerta tocar.
6. Retenção, volume estimado e o que acontece quando encher.
7. O que o **dono** roda e onde ele olha na máquina real.
8. Commit (`chore(obs): …`).

## Armadilhas pagas
- **Log em texto livre:** impossível filtrar ou agregar; descobre-se isso no primeiro incidente, que é o pior momento.
- **CPF/e-mail/token em log:** vaza para o agregador, para o backup e para o ticket de suporte — e é vazamento de dado pessoal, com as consequências disso.
- **`catch` que loga e segue:** o sistema continua "funcionando" produzindo dado errado, em silêncio.
- **Alertar em CPU/memória:** ruído constante, e o alerta que importava chega junto e é ignorado.
- **Healthcheck que só responde 200:** o container fica verde enquanto o banco está fora.
- **Log sem rotação:** o disco enche e derruba o sistema — causado pela ferramenta que existia para evitar quedas.
