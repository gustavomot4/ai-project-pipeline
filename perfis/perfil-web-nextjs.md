# Perfil — app web / Next.js (tipo SPO)

> Para apps web full-stack. Cole os itens relevantes no `CONTEXT.md`. Defaults destilados do SPO —
> ajuste. O objetivo é declarar as restrições da stack **antes** do primeiro código (foi o que
> causou 6 versões de schema em 7 dias no SPO).

## Stack típica
Next.js (App Router) · TypeScript estrito · Prisma · SQLite/Postgres · Tailwind · Docker.

## Restrições da stack (cole no CONTEXT.md) — declarar ANTES de modelar dados
- **Dinheiro em `Int` (centavos)**, nunca `Float`. Taxas em **basis points** (`1,99%` = `199`).
- **IDs opacos** (`cuid`/`uuid`), nunca inteiros sequenciais como ID público.
- **Datas em UTC** (ISO 8601); "dia comercial" via fuso fixo num util único.
- **Prisma + SQLite:** sem `enum` nativo (usar `String` + validação na app); cuidado com `DateTime`
  (preferir armazenamento explícito). ← *foi exatamente isto que forçou retrabalho de schema no SPO.*
- **TypeScript:** `strict` + `noUncheckedIndexedAccess`; evitar `any`.
- **Segredo de sessão** gerado/peristido por instalação, **nunca versionado**; `.env.example` recusa
  placeholder em produção.

## Critério de aceite (o "portão") — sugestão
- **`npm run typecheck` + `npm run build`** passam (variável não usada **quebra** o build em prod).
- Rotas protegidas testadas (sem auth → 401/redirect); rate-limit nas rotas sensíveis.
- Migrations seguem **expand/contract** (aditivas primeiro; remoção só na release seguinte).
- Passou pelo **QA adversarial** (Fase 4) sem achado crítico/alto aberto.

## Entrega / operação (o que o SPO fez bem — reuse)
- **Docker** como runtime oficial (reprodutibilidade); `output: 'standalone'` para imagem enxuta.
- **Backup do banco** antes de cada atualização; retenção N cópias.
- **GitOps** opcional (CI → registry → manifesto → updater com health-check + rollback) se for
  distribuir para máquinas que você não acessa. Documente em `RUNBOOK.md` + ADR.
- Docs **em camadas por público**: README técnico · guia do usuário final · runbook do operador.

## Armadilhas conhecidas (do SPO)
- **CRLF × LF:** force LF em `.sh` via `.gitattributes` (script quebra no Linux/Docker).
- **Cruft no repo:** `docker-compose.yml.bak` e `.fuse_hidden` vazaram para o versionamento — `.gitignore` + Fase 6.
- **Commits "FIX: correções":** amarre cada commit a um QA-NN/D-NN.

## Estrutura de pastas sugerida
```
projeto/
├── CONTEXT.md  DECISIONS.md  CHANGELOG.md  CHECKLIST.md  README.md  RUNBOOK.md
├── prompts/                  (copiados deste kit)
├── prisma/ (schema + migrations)
├── src/app/ (páginas + api)   src/lib/   src/components/   src/types/
├── deploy/ (se GitOps)        .github/workflows/
└── Dockerfile  docker-compose.yml  .env.example  .gitignore
```
