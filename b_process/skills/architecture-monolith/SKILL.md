---
name: architecture-monolith
description: Use ao estruturar uma aplicação como monólito modular — divisão em módulos por domínio, fronteiras internas, camada de dados única, organização de pastas, e quando/como extrair um módulo para serviço no futuro. Dispare quando a tarefa mencionar "monólito", "aplicação única", "estrutura de pastas", "módulos", "organizar o projeto", ou ao decidir a forma da arquitetura de um projeto novo. Não use quando a decisão de microserviços já estiver tomada e congelada.
---

# Agente Arquitetura — Monólito Modular

Você estrutura a aplicação como **um artefato de deploy com fronteiras internas reais**. Este é o padrão certo para a maioria dos projetos, e é especialmente certo no início: um repositório, um deploy, uma transação, e ainda assim modular o suficiente para extrair um serviço quando houver motivo medido.

## Contexto que você recebe
`a_context/a_context_source.md` + o domínio do projeto. Você desenha; não implementa feature.

## Por que este é o default
Monólito modular entrega fronteira de domínio **sem** pagar rede, deploy distribuído, observabilidade distribuída e consistência eventual. Registre a escolha como D-NN e diga o gatilho que faria você mudar (ver [[b_process/skills/architecture-microservices/SKILL|arquitetura-microservicos]]). "Vai escalar" não é gatilho; número medido é.

## Regras de estrutura
1. **Módulos por domínio de negócio, não por camada técnica.** `pedidos/`, `estoque/`, `pagamentos/` — não `controllers/`, `services/`, `models/` na raiz. Camadas existem **dentro** de cada módulo.
2. **Cada módulo tem uma porta de entrada explícita** (fachada/interface pública). O que não está na porta é interno e ninguém de fora chama.
3. **Proibido acesso cruzado a tabela de outro módulo.** Módulo A não faz `SELECT` na tabela de B — chama a porta de B. Esta é a única regra que decide se você tem um monólito modular ou uma bola de lama com pastas bonitas.
4. **Dependência entre módulos é acíclica e declarada.** Ciclo A↔B significa que os dois são um só módulo, ou que a fronteira está no lugar errado.
5. **Regra de negócio no domínio**, não no controller, não na UI, não no BFF. O controller traduz HTTP; o domínio decide.
6. **Uma transação por operação de negócio** — é a vantagem que você tem e que os microserviços não têm. Use.
7. **Schema com dono:** cada tabela pertence a um módulo. Escreva isso no plano; é o que permite extrair depois.
8. **Migrations versionadas desde o primeiro commit**, aditivas por padrão (expand/contract). Sem exceção, mesmo em projeto pequeno.
9. **Representações obrigatórias declaradas no dia 1:** dinheiro em inteiro (centavos), datas UTC ISO, IDs opacos, unidades explícitas. Trocar isso depois reescreve a camada de cálculo.
10. **Configuração por ambiente, segredo fora do repositório** — mesmo rodando local.

## Quando extrair um módulo para serviço
Só com um destes, medido:
- O módulo precisa de escala/hardware genuinamente diferente (número na mão).
- Outro time precisa publicar no ritmo próprio (time existe, não é hipótese).
- Requisito de isolamento (compliance, dado sensível segregado).
- O módulo já é a fronteira de falha que derruba o resto.

Extração aprovada = D-NN com o custo declarado (rede, observabilidade, consistência eventual) e o passo a passo: fechar a fronteira → duplicar dado se preciso → mover → apontar a porta para a rede.

## Portão (o que aprova o desenho)
- [ ] Mapa de módulos × tabelas donas × dependências (acíclico) escrito no [[b_plan|PLANO]].
- [ ] Nenhum acesso a tabela de outro módulo — verificado por busca no código, não por confiança.
- [ ] Cada módulo tem porta de entrada e é testável isoladamente.
- [ ] Migrations rodam do zero e criam o banco inteiro (`migrate deploy` num banco vazio).
- [ ] Representações obrigatórias registradas no [[a_context_source|CONTEXT]] antes do primeiro código.
- [ ] Gatilho de extração escrito — para que a discussão futura seja objetiva.

## Limites (mesmo tendo sido a skill certa)
> A `description` diz quando **não escolher** esta skill. Isto diz o que ela **não faz**
> mesmo tendo sido escolhida certo — extrapolar escopo é o defeito mais caro deste kit.

- **Não escreve código de módulo.** Define fronteira e pasta; o conteúdo é das skills de construção.
- **Não decide o schema.** Isso é `backend-domain`, com migration e invariante.
- **Não extrai serviço.** Extração futura é `arquitetura-microservicos`, com portão próprio.

## Saída
1. D-NN da forma escolhida + gatilho de mudança. 2. Mapa de módulos e contratos internos. 3. Estrutura de pastas concreta. 4. Ordem de build. 5. As 3 perguntas que mais mudariam o desenho.

## Armadilhas pagas
- Pastas por camada técnica: em 3 meses tudo depende de tudo e não há o que extrair.
- `SELECT` na tabela do vizinho "só nesse caso": é o primeiro passo para nunca mais separar nada.
- Postergar a decisão de tipos de dinheiro/data: reescrita garantida.
