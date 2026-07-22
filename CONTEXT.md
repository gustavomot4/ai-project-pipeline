# CONTEXT.md — <NOME DO PROJETO>

> ⚠️ REGRA DE OURO: este arquivo tem **teto de ~1 página** e é **atualizado por substituição**.
> Nada de "▶ Atualização tal data" no fim. Histórico datado → `CHANGELOG.md`. Decisões → `DECISIONS.md`.
> Este é o ÚNICO arquivo que toda sessão de IA recebe por padrão. Se ele incha, toda sessão fica cara.

## Objetivo (3 linhas, no máximo)
<O que o sistema faz e para quem. Uma frase de valor. Uma frase de não-objetivo.>

## Restrições inegociáveis (violou = inválido)
- <ex.: roda local / custo R$0 / sem dado pago>
- <ex.: probabilidades, nunca certezas — ou o equivalente do seu domínio>
- <ex.: nenhum segredo versionado no repo>
- <ex.: registro/auditoria imutável, se aplicável>

## Stack + restrições da stack  ← preencha ANTES de pedir código (lição do SPO)
- **Stack:** <linguagem, framework, banco, runtime>
- **Restrições da stack** (o que essa combinação NÃO suporta / exige):
  - <ex.: Prisma + SQLite: sem enum nativo (usar String); evitar DateTime nativo>
  - <ex.: dinheiro sempre em Int (centavos); taxas em basis points>
  - <ex.: IDs opacos (cuid/uuid), nunca sequenciais>
- (Veja `perfis/` e cole aqui os itens do perfil escolhido.)

## Critério de aceite (o "portão") ← defina no dia 1
Nada entra como pronto sem passar nisto:
- <ex.: `npm run typecheck` + `npm run build` passam>
- <ex.: teste do módulo verde / backtest com IC que não cruza zero>
- <ex.: revisão do agente de QA adversarial sem achado crítico/alto aberto>

## Estado atual (só o presente — reescreva, não acumule)
- **Versão/baseline atual:** <ex.: v1.0 — só a atual>
- **O que está pronto:** <módulos concluídos>
- **Tarefa ativa:** <a única coisa em andamento agora>
- **Próximo passo:** <o que vem depois>

## Mapa rápido (onde está o quê)
- Plano: `PLANO.md` · Decisões: `DECISIONS.md` · Backlog: `BACKLOG.md` · Histórico: `CHANGELOG.md`
- Código: `<pasta>` · Testes: `<pasta>` · Prompts: `prompts/`

## Retomada para uma sessão nova (handoff)
Se você é um agente novo pegando o projeto, faça nesta ordem:
1. Leia este arquivo → `DECISIONS.md` (o que já foi decidido/rejeitado) → `BACKLOG.md`.
2. Estado em 1 linha: <preencha>.
3. Valide o ambiente: `<comando para rodar os testes/build>`.
4. Pegue a "Tarefa ativa" acima. Trabalhe por **delta**; registre D-NN/QA-NN; atualize este arquivo por substituição.
