---
tags: [perfil, stack]
status: atual
---

# Perfil — app web / Next.js

> Cole os blocos no `a_context/a_context_source.md` **antes de modelar dados** — declarar restrições tarde foi o que causou 6 versões de schema em 7 dias no SPO.

## Stack típica
Next.js (App Router) · TypeScript estrito · Prisma · SQLite/Postgres · Tailwind · Docker.

## Restrições da stack (→ CONTEXT.md, ANTES do primeiro código)
- Dinheiro em `Int` (centavos); taxas em basis points (1,99% = `199`). Nunca Float.
- IDs opacos (cuid/uuid); nunca inteiro sequencial como ID público.
- Datas em UTC (ISO 8601); "dia comercial" num util único de fuso.
- Prisma + SQLite: sem enum nativo (String + validação na app); `DateTime` com cuidado.
- TypeScript `strict` + `noUncheckedIndexedAccess`; sem `any`.
- Segredo de sessão gerado por instalação, nunca versionado; `.env.example` sem valor real.

## Quem roda o quê (→ CONTEXT.md)
- Agente: código + testes. Dono: `npm run typecheck`/`build` oficiais, migrations em produção, deploy, push.
- Dev server/build velho tem cache — restart antes de julgar mudança.

## Critério de aceite (→ CONTEXT.md)
- `typecheck` + `build` passam (variável não usada quebra o build de produção).
- Rotas protegidas testadas (sem auth → 401/redirect); rate-limit nas sensíveis.
- Migrations expand/contract (aditivas primeiro; remoção só na release seguinte).
- QA adversarial sem crítico/alto aberto.

## Armadilhas pagas
- CRLF × LF: force LF em `.sh` via `.gitattributes` (script quebra no Linux/Docker).
- Cruft versionado (`*.bak`, `.fuse_hidden`) — `.gitignore` + Fase 6.
- Commits "fix: correções" — amarre a QA-NN/D-NN.

## Entrega
Docker como runtime oficial (`output: 'standalone'`); backup do banco antes de cada atualização; docs em camadas por público (README técnico · guia do usuário · runbook do operador).
