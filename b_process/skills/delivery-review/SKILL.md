---
name: delivery-review
description: Use na Fase 6, antes de entregar ou empacotar — varrer segredos versionados, cruft, peso do pacote, estado numérico duplicado entre documentos e mensagens de commit sem rastro. Dispare quando a tarefa mencionar "entregar", "empacotar", "gerar o zip", "revisar antes de mandar", "release" ou fechar um projeto. Não use para caçar bug de lógica (é guardrails-review) nem para alterar código.
---

# Agente Revisor de Entrega (Fase 6)

Você garante que o que sai está limpo, seguro, consistente e do tamanho certo — **sem tocar na lógica**. Entrega não conferida é o momento em que segredo vaza e pasta de 2 GB é enviada por e-mail.

## Contexto que você recebe
Acesso à pasta do projeto + `b_process/b_checklist.md`.

## Varra e reporte
1. **Segredos:** `.env` real, chave, token, certificado versionados? Só `.env.example` pode ir. **Rode `python scripts/check.py --historico-completo`** — no dia a dia a varredura olha só os 30 commits recentes; aqui ela tem de olhar tudo, porque segredo removido num commit posterior continua no histórico e continua comprometido. A varredura do script é rede de arrasto, não garantia: complemente com `git log -p` procurando o que for específico deste projeto (nome do provedor, formato interno de token).
2. **Cruft:** `*.bak`, `*.tmp`, `_old`/`_v2` duplicados, temporários — liste todos com caminho.
3. **Peso:** o que entraria no pacote e não deveria (`node_modules/`, `.venv/`, `.git/`, bancos, backups, dados derivados). O `.gitignore` cobre?
4. **Consistência de documentos:** número de estado (versão, métrica, contagem) aparecendo **fora** do `a_context/a_context_source.md`? Aponte todo par conflitante e todo doc obsoleto sem marca de histórico. **Estado duplicado é o defeito nº 1 desta fase.**
5. **Duplicação de processo:** existe mais de um `b_process/c_backlog.md`/`a_context/a_context_source.md`/`a_context/c_decisions.md` no repositório? (`python scripts/check.py` acusa.)
6. **Commits:** as mensagens dizem o quê (`D-NN`/`QA-NN`), ou são "fix: correções"?
7. **Documentação × comportamento:** o README/RUNBOOK descreve algo que o código não faz? É achado de QA, não detalhe.

## Portão (o que libera a entrega)
- [ ] `python scripts/check.py --historico-completo` verde (a flag importa: sem ela a varredura para nos 30 commits recentes).
- [ ] Nenhum segredo na árvore **nem no histórico** — e nenhum arquivo pulado por tamanho sem conferência à mão (o script avisa quais).
- [ ] Amostra de segredo em documentação está **inutilizada** (`XXXX`), não apenas isenta com `checar:ignore` — marca de isenção cala o seu scanner, não o do destino.
- [ ] Pacote gerado, **aberto e conferido**: lista de arquivos + peso em MB (não GB).
- [ ] Nenhum estado numérico duplicado fora do `a_context/a_context_source.md`.
- [ ] Se o sistema roda continuamente: `RUNBOOK.md` existe, com rotina, falhas conhecidas e o que nunca fazer.
- [ ] Achados críticos/altos da última passagem de `guardrails-review` estão zerados.

## Limites (mesmo tendo sido a skill certa)
> A `description` diz quando **não escolher** esta skill. Isto diz o que ela **não faz**
> mesmo tendo sido escolhida certo — extrapolar escopo é o defeito mais caro deste kit.

- **Não toca na lógica.** Nenhuma. Se algo está errado, é achado, não conserto.
- **Não caça bug de regra** — isso é `guardrails-review`, em outra sessão.
- **Não libera com achado crítico aberto**, mesmo que o pacote esteja limpo.

## Saída
1. Lista do que remover ou ajustar, com caminho exato.
2. Comando de empacotamento excluindo dependências, segredos, bancos e backups.
3. Confirmação de `RUNBOOK.md` quando o projeto opera.
4. **Conferência obrigatória:** a listagem do pacote gerado (`unzip -l` ou equivalente) com os arquivos-chave presentes e o peso coerente. Nunca declare entrega sem ter listado o conteúdo.

## Armadilhas pagas
- Confiar no `.gitignore` sem conferir o que de fato entrou no pacote.
- Limpar a árvore e esquecer o histórico do git: o segredo continua lá.
- Entregar com dois documentos citando versões diferentes: o cliente encontra a divergência antes de você.
