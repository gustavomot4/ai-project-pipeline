---
tags: [template]
status: atual
---
| QA-NN | {{date:YYYY-MM-DD}} | <Crítico/Alto/Médio/Baixo> | `arquivo:linha` | <a invariante que quebrava> | <o que mudou> |

<%*
Lembretes (apague esta parte ao colar):
- Achado sem REPRODUÇÃO não é achado: comando exato + observado × esperado, no relatório `dev/qa-{{date:YYYY-MM-DD}}.md`.
- Severidade é do EFEITO, não do esforço: dado errado que o usuário acredita > tela feia.
  Crítico = perda/corrupção de dado, segredo exposto, acesso indevido, dinheiro errado.
  Alto    = fluxo crítico quebra, invariante violada, falha silenciosa em caminho comum.
  Médio   = borda quebra, mensagem enganosa, doc divergindo do comportamento.
  Baixo   = cosmético, cruft, inconsistência sem efeito prático.
- Correção de crítico/alto entra com TESTE DE REGRESSÃO citando o QA-NN no commit (`fix: QA-NN …`).
- Marque `[verificado]` ou `[suspeita]` — suspeita não corrigida continua aberta.
%>
