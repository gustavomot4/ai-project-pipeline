---
tags: [template]
status: atual
---
| QA-NN | {{date:YYYY-MM-DD}} | <Crítico/Alto/Médio/Baixo> | <portão/revisão/dono/usuário> | `arquivo:linha` | <a invariante que quebrava> | <o que mudou> | _(aberto)_ |

<%*
Lembretes (apague esta parte ao colar):
- CONTE AS CÉLULAS: são OITO, e a última é "Fechado em". Este modelo já emitiu SEIS — faltavam
  `Origem` e `Fechado em` — e o efeito não era cosmético: `scripts/check.py` lê a ÚLTIMA célula
  como "Fechado em", então numa linha curta ele lia "o que mudou", que nunca está vazio e nunca
  diz "aberto". Todo achado escrito por este modelo nascia contado como FECHADO, e a checagem de
  achado vencido nunca disparava nele. Modelo que não bate com o cabeçalho é a "checagem que
  emudece" entrando pela porta de quem escreve.
- ORIGEM é quem achou: `portão` (o check.py/hook reprovou) · `revisão` (passagem de guardrails)
  · `dono` (você viu usando) · `usuário` (chegou de fora). Escreva no instante em que a linha
  nasce — depois ninguém lembra, e é o único número do kit que não é circular.
- Achado sem REPRODUÇÃO não é achado: comando exato + observado × esperado, no relatório `dev/qa-{{date:YYYY-MM-DD}}.md`.
- Severidade é do EFEITO, não do esforço: dado errado que o usuário acredita > tela feia.
  Crítico = perda/corrupção de dado, segredo exposto, acesso indevido, dinheiro errado.
  Alto    = fluxo crítico quebra, invariante violada, falha silenciosa em caminho comum.
  Médio   = borda quebra, mensagem enganosa, doc divergindo do comportamento.
  Baixo   = cosmético, cruft, inconsistência sem efeito prático.
- Correção de crítico/alto entra com TESTE DE REGRESSÃO citando o QA-NN no commit (`fix: QA-NN …`).
- Marque `[verificado]` ou `[suspeita]` — suspeita não corrigida continua aberta.
%>
