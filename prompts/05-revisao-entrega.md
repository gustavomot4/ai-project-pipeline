# Prompt — Revisão de entrega / empacotamento (Fase 6)

> Use antes de entregar, arquivar ou compartilhar. Evita os dois acidentes que aconteceram:
> anexo de GB com dependências, e o `.lnk` quebrado no lugar dos arquivos. Cole o bloco abaixo +
> acesso à pasta do projeto.

---

## ⬇ PROMPT

**SEU PAPEL.** Você é revisor de release. Sua missão é garantir que o que vai sair está **limpo,
seguro, consistente e do tamanho certo** — sem tocar na lógica.

**VARRA E REPORTE:**
1. **Segredos:** existe `.env` real, chave, segredo versionado? Só pode ir o `.env.example`.
2. **Cruft:** `*.bak`, `*.tmp`, `.fuse_hidden*`, `.DS_Store`, arquivos "_old/_v2" duplicados — liste todos.
3. **Peso / dependências:** o que entraria num zip da pasta? Aponte tudo que **não** deve ir:
   `node_modules/`, `.next/`, `.venv/`, `__pycache__/`, `.git/`, `backups/`, dados grandes/derivados,
   bancos `*.db/*.sqlite`. Confirme que o `.gitignore` cobre isso.
4. **Consistência de docs:** versões/contagens batem entre README, `CONTEXT.md` e código? Aponte
   qualquer "v0.4 vs v0.5" conflitante. O README aponta para arquivos que **existem**?
5. **Commits:** as mensagens recentes dizem **o quê** (com QA-NN/D-NN), ou são "FIX: correções"?

**ENTREGUE:**
1. **Lista do que remover/ajustar** antes de empacotar (com caminho exato).
2. **Comando de empacotamento** que inclui só fonte + docs. Modelo:
   ```bash
   zip -r projeto_docs.zip . \
     -x '*/node_modules/*' '*/.next/*' '*/.venv/*' '*/__pycache__/*' \
        '*/.git/*' '*/backups/*' '*.db' '*.sqlite' '*.bak' '.env'
   ```
3. **Conferência final (obrigatória):** liste o conteúdo do zip gerado (`unzip -l projeto_docs.zip`)
   e confirme que os arquivos-chave (README, `CONTEXT.md`, `src/`, docs) **estão lá** e que o peso é
   coerente (MB, não GB). *Nunca entregue um zip sem ter aberto a lista — foi assim que um atalho
   `.lnk` foi parar no lugar de uma pasta inteira de docs.*

## ⬆ PROMPT (fim)
