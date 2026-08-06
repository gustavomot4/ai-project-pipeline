---
name: frontend-mfe
description: Use ao avaliar, desenhar ou implementar micro frontends — dividir uma aplicação em remotes independentes, Module Federation, host/shell, versionamento de contrato entre remotes, dependências compartilhadas e deploy independente. Dispare quando a tarefa mencionar "MFE", "micro frontend", "Module Federation", "shell", "remote", "monorepo de frontend" ou dividir o front por time. Não use para uma SPA única sem divisão.
---

# Agente Frontend — Micro Frontends (MFE)

Você desenha e implementa a divisão do frontend em partes que podem ser desenvolvidas e publicadas separadamente. **Seu primeiro trabalho é decidir se isso deve existir** — MFE resolve problema de organização (times/deploys independentes), não problema técnico de código grande.

## Contexto que você recebe
`a_context/a_context_source.md` + `a_context/b_plan.md` (contrato do shell e dos remotes) + o remote da sessão.

## STEP 0 — o portão de existência (obrigatório antes de qualquer código)
Responda com fatos, não intenção:
1. **Quantos times/pessoas publicam frontend hoje, independentemente?** Menos de 2 ⇒ **MFE reprovado**: registre D-NN REJEITADO e entregue uma SPA modular. Isso não é preguiça, é o resultado correto.
2. **Existe necessidade real de deploy independente** (uma parte precisa subir sem esperar a outra)? Se não, reprovado.
3. **Alguma parte precisa de ciclo de vida próprio** (produto legado, aquisição, tecnologia diferente)?
4. **Quem é o dono do shell?** Sem dono do shell, MFE vira ninguém-responsável-pelo-todo.

Aprovado só com ≥1 sim forte. Escreva no D-NN o custo que você está assumindo: build mais complexo, versionamento entre remotes, duplicação de dependências, debug distribuído.

## Regras de desenho
1. **Divida por domínio de negócio, nunca por camada técnica.** "Checkout", "Catálogo", "Conta" — não "componentes", "formulários".
2. **O shell é fino:** roteamento, sessão/identidade, layout comum, tratamento de remote que não carrega. Regra de negócio no shell é vazamento.
3. **Contrato entre remotes é versionado e explícito** (props de entrada, eventos de saída). Remote não lê o estado interno de outro. Mudança de contrato = bump de versão + D-NN.
4. **Dependências compartilhadas declaradas com faixa de versão** (framework, design system). Duas versões do framework no mesmo bundle é o defeito clássico — verifique o bundle final, não a intenção.
5. **Falha isolada:** remote que não carrega degrada a área dele com mensagem, não derruba a aplicação. Isso é requisito, não bônus.
6. **Estado compartilhado é mínimo e unidirecional:** sessão/usuário/tema vêm do shell para baixo. Barramento de eventos global sem contrato documentado é proibido.
7. **Design system é dependência compartilhada versionada**, senão a UI divergente reaparece em cada remote.
8. **Cada remote é publicável e testável sozinho** — se só builda dentro do monorepo inteiro, a independência é fictícia.

## Portão (o que aprova a entrega)
- [ ] D-NN do STEP 0 registrado (adotado com justificativa **ou** rejeitado com o motivo).
- [ ] Shell carrega o remote em desenvolvimento e com o artefato publicado.
- [ ] **Teste de remote ausente:** derrube um remote e mostre que o resto da aplicação continua utilizável.
- [ ] Bundle final inspecionado: nenhuma dependência crítica duplicada em versões diferentes.
- [ ] Remote builda e roda isolado, com contrato documentado (entradas/eventos).
- [ ] Deploy independente demonstrado: publicar o remote A não exige republicar o shell.

## Limites (mesmo tendo sido a skill certa)
> A `description` diz quando **não escolher** esta skill. Isto diz o que ela **não faz**
> mesmo tendo sido escolhida certo — extrapolar escopo é o defeito mais caro deste kit.

- **Não implementa antes do portão de existência.** Reprovar é resultado válido e frequente.
- **Não decide a arquitetura do backend.**
- **Não trata dependência compartilhada como detalhe** — é o que faz MFE falhar em produção.

## Saída
1. D-NN do STEP 0. 2. Mapa remotes × domínios × donos. 3. Contratos (entradas/eventos/versão). 4. Delta do código. 5. Roteiro de verificação para o dono, incluindo o teste de remote ausente. 6. O custo operacional que o projeto acabou de assumir.

## Armadilhas pagas
- Adotar MFE com um time só: paga-se todo o custo de coordenação sem nenhum benefício de independência.
- Descobrir a duplicação de framework em produção, pelo peso do bundle, em vez de no portão.
- Shell que acumula regra de negócio "só por enquanto" e vira o monólito que o MFE ia evitar.
