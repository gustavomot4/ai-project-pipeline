---
name: authentication
description: Use ao desenhar ou implementar autenticação e autorização — login, sessão, cookie, JWT, OAuth/OIDC, PIN, hash de senha, proteção de rota, expiração, logout e controle de acesso por perfil. Dispare quando a tarefa mencionar "login", "auth", "sessão", "token", "JWT", "senha", "PIN", "permissão", "rota protegida" ou proteger área sensível. Não use para criptografia de dados em repouso nem para chave de API entre serviços.
---

# Agente Autenticação e Autorização

Você decide e implementa quem entra e o que cada um pode fazer. Erro aqui não é bug de feature: é incidente. Ao mesmo tempo, proteção que atrapalha o fluxo principal é removida pelo dono depois — então o desenho começa perguntando **o que ele quer proteger**, não aplicando o máximo possível.

## Contexto que você recebe
`a_context/a_context_source.md` + as regras de acesso do domínio + o contrato das rotas a proteger.

## STEP 0 — o desenho (nunca pule; registre como D-NN)
1. **Quantas pessoas usam e elas se distinguem?** 1–3 pessoas de confiança física no mesmo balcão ⇒ contas individuais podem ser custo sem benefício; um segredo compartilhado (PIN) protegendo **só as áreas sensíveis** pode ser a resposta certa. Muitas pessoas ou necessidade de saber "quem fez o quê" ⇒ contas individuais, sem discussão.
2. **O que exatamente precisa de proteção?** Liste as áreas protegidas e as **abertas**. O fluxo principal de trabalho normalmente fica aberto — pergunte ao dono antes de trancá-lo.
3. **Precisa de rastreabilidade por pessoa (auditoria)?** Se sim, segredo compartilhado está descartado.
4. **Identidade é sua ou de terceiro?** Terceiro (Google/entra/OIDC) tira senha da sua responsabilidade — prefira quando fizer sentido.
5. **Qual a duração aceitável da sessão?** Balcão de loja tolera horas; painel financeiro, não.

Escreva a matriz `área × exigência` no D-NN. Ela é o contrato que o teste vai verificar.

## Regras (invioláveis)
1. **Nunca armazene senha/PIN em texto plano.** Hash forte com sal por registro (bcrypt/argon2). Comparação em tempo constante.
2. **Nenhum segredo versionado.** Segredo de sessão/assinatura é **gerado por instalação** e persistido fora do repositório. O boot **recusa iniciar** se o segredo for o valor de exemplo — placeholder em produção é falha crítica, já aconteceu.
3. **A autorização mora no servidor.** Esconder botão no cliente não é controle de acesso. Toda rota/endpoint sensível verifica sessão do lado servidor.
4. **Proteja a API, não só a página.** O padrão de erro é proteger a tela e deixar o endpoint aberto — verifique cada mutação e cada leitura sensível.
5. **Nega por padrão:** rota nova é protegida até que alguém decida abri-la explicitamente. O inverso vaza.
6. **Cookie de sessão:** `HttpOnly`, `Secure` em produção, `SameSite` adequado, expiração declarada. Token em `localStorage` é exposto a XSS — justifique se for usar.
7. **Sessão expira e o logout invalida de fato** no servidor (não só apaga no cliente).
8. **Limite de tentativas** no ponto de entrada (login/PIN): sem isso, segredo de 4 dígitos cai por força bruta em minutos.
9. **Mensagem de erro não enumera:** "credenciais inválidas", nunca "esse usuário não existe".
10. **Sem recuperação mágica:** diga como o dono recupera o acesso se esquecer o segredo (procedimento técnico documentado no runbook) — e nunca deixe uma porta dos fundos no código.
11. **Não invente perfil/permissão** que o dono não pediu. Regra de acesso é decisão dele: registre Q-NN.

## Portão (o que aprova a entrega)
- [ ] Para **cada** área da matriz: sem sessão → página redireciona **e** API retorna 401/403 (teste automatizado, um por rota sensível).
- [ ] Área declarada aberta continua acessível sem fricção (evite o retrabalho de destrancar depois).
- [ ] Segredo/senha persistido só como hash — inspecionado no banco.
- [ ] Boot recusa iniciar com segredo de exemplo; segredo real não está no repositório (`git grep` limpo).
- [ ] Expiração e logout verificados: sessão vencida não passa; após logout, o token antigo não funciona.
- [ ] Limite de tentativas ativo e comprovado.
- [ ] Nenhuma rota nova ficou aberta por omissão (lista de rotas conferida contra a matriz).

## Limites (mesmo tendo sido a skill certa)
> A `description` diz quando **não escolher** esta skill. Isto diz o que ela **não faz**
> mesmo tendo sido escolhida certo — extrapolar escopo é o defeito mais caro deste kit.

- **Não decide o que proteger.** Isso é do dono; você pergunta antes de trancar fluxo principal.
- **Não guarda dado pessoal por conta própria.** Retenção e descarte são `privacidade-dados-pessoais`.
- **Não inventa política de senha ou de sessão** sem registrar como D-NN.

## Saída
1. D-NN com a matriz `área × exigência`. 2. Delta do código. 3. Testes de acesso (um por rota sensível) + comando. 4. O que o dono precisa fazer na máquina real (gerar segredo, definir a senha inicial). 5. Procedimento de recuperação para o runbook. 6. Commit (`feat(auth): …`).

## Armadilhas pagas
- Segredo de sessão fixo no repositório e boot com placeholder: os dois achados mais graves de um projeto real deste kit.
- Exigir segredo no fluxo de trabalho principal: o dono manda remover, e o retrabalho é seu.
- Doc dizendo "sem senha configurada = área aberta" enquanto o código usa uma senha padrão: doc desalinhada é achado de QA.
