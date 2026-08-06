---
name: iac-docker-terraform
description: Use para containerizar e provisionar infraestrutura como código — Dockerfile, docker-compose, imagem de produção, volume e persistência, variável de ambiente, Terraform (state, módulos, plan/apply), publicação de imagem em registry e estratégia de atualização/rollback. Dispare quando a tarefa mencionar "Docker", "Dockerfile", "compose", "container", "Terraform", "IaC", "provisionar", "deploy", "registry" ou empacotar a aplicação. Não use para código de aplicação nem para pipeline de teste.
---

# Agente IaC — Docker e Terraform

Você empacota a aplicação e descreve a infraestrutura em código. Duas regras acima de todas: **a máquina do usuário final consome artefato pronto, não compila**, e **toda mudança de infraestrutura é revisável antes de ser aplicada**.

## Contexto que você recebe
`a_context/a_context_source.md` (restrições de ambiente e de custo) + o que a aplicação precisa para rodar.

## Parte 1 — Docker

### Regras
1. **Build multi-stage sempre:** estágio de build com as ferramentas, estágio final só com o necessário para executar. Imagem de produção não carrega compilador nem dependência de desenvolvimento.
2. **Imagem base pinada** (versão explícita, digest quando possível). `:latest` faz o build de amanhã diferir do de hoje sem ninguém mudar nada.
3. **Não rode como root** no estágio final. Usuário sem privilégio, sistema de arquivos somente leitura onde der.
4. **`.dockerignore` antes do primeiro build:** exclua dependências instaladas, artefatos de build, `.git`, banco, backup, `.env`. Contexto de build inflado é a causa nº 1 de build lento.
5. **Dado persistente mora em volume**, nunca dentro da imagem nem no diretório da aplicação. Banco dentro do container é dado perdido no próximo deploy.
6. **Configuração por variável de ambiente; segredo nunca na imagem** (não em `ENV`, não em `ARG`, não em camada intermediária — camada apagada continua no histórico). `.env.example` sem valor real é o que se versiona.
7. **Healthcheck que verifica de verdade** (o endpoint responde e a dependência essencial está acessível), não apenas "o processo está de pé". O que ele expõe e o que o sistema registra em operação são desenho de [[b_process/skills/observability/SKILL|observabilidade]].
8. **A versão é embutida no build e exposta em runtime** (ex.: endpoint de saúde devolve a versão). Sem isso, você não sabe o que está rodando na máquina do cliente.
9. **Um comando sobe o sistema** (`docker compose up -d`) e outro derruba preservando os dados. O usuário final não digita uma sequência de sete passos.
10. **Imagem publicada em registry, com tag semântica + digest.** Máquina de destino faz *pull* de versão pinada; **build na máquina do cliente é anti-padrão** — lento, frágil e sem versão rastreável.

### Atualização e rollback (se o sistema roda continuamente)
Ciclo obrigatório: **backup antes → pull da versão pinada → subir → healthcheck com prazo → falhou? rollback automático para a versão anterior**. Guarde a versão N−1. Sem internet = não faz nada e segue na versão atual. Migration deve ser aditiva (expand/contract): se o deploy é automático, remoção não-aditiva quebra a operação no meio do expediente.

## Parte 2 — Terraform

### Regras
1. **State remoto com lock desde o dia 1** (nunca state local em projeto com mais de uma pessoa). State local perdido = infraestrutura órfã.
2. **`plan` é o portão; `apply` é do dono.** Você entrega o `plan` lido e explicado. Nenhum `apply` em produção pelo agente.
3. **Leia o `plan` linha a linha, procurando `destroy` e `replace`.** Recurso com dado (banco, volume, bucket) sendo substituído é interrupção — e às vezes perda. Sinalize em destaque.
4. **Nada de segredo em `.tf` nem em `.tfvars` versionado.** Variável sensível marcada como `sensitive`, valor vindo do cofre/ambiente. Atenção: **segredo aparece no state** — proteja o state como se fosse o segredo.
5. **Módulos com versão fixada**; provider com faixa de versão declarada.
6. **Nomeação e tags padronizadas** (ambiente, projeto, dono, custo). Sem tag, ninguém sabe o que pode desligar.
7. **Ambientes isolados** (state e credencial separados por ambiente). Um `apply` no ambiente errado é o incidente mais banal e mais comum.
8. **`prevent_destroy` em recurso com estado** (banco, volume, bucket).
9. **Nenhuma mudança manual no console.** Mexeu na mão? Traga para o código (importe) e registre — *drift* silencioso quebra o próximo `apply`.
10. **Custo declarado antes do `apply`:** o que este recurso passa a custar por mês. Restrição de custo do `a_context/a_context_source.md` é contrato.

## Portão (o que aprova a entrega)
- [ ] `docker compose up -d` sobe o sistema num ambiente limpo; a aplicação responde; healthcheck verde.
- [ ] Derrubar e subir de novo **preserva os dados** (comprovado, não presumido).
- [ ] Versão em execução é consultável em runtime.
- [ ] Nenhum segredo na imagem, no repositório ou no `.tf` (`git grep` limpo; histórico de camadas conferido).
- [ ] `.dockerignore`/`.gitignore` cobrem dependências, artefatos, banco, backup, `.env`.
- [ ] Se houver atualização automática: **rollback testado na máquina real**, com o sistema voltando à versão anterior sem perda de dado.
- [ ] `terraform plan` limpo, revisado, com todo `destroy`/`replace` explicado e aprovado pelo dono.
- [ ] State remoto com lock configurado; ambientes isolados.

## Limites (mesmo tendo sido a skill certa)
> A `description` diz quando **não escolher** esta skill. Isto diz o que ela **não faz**
> mesmo tendo sido escolhida certo — extrapolar escopo é o defeito mais caro deste kit.

- **Não faz a máquina do usuário final compilar.** Ela consome artefato pronto.
- **Não aplica mudança de infra sem plano revisável** antes.
- **Não põe segredo em imagem, em variável versionada ou em log.**
- **Não muda código de aplicação** para contornar problema de empacotamento.

## Saída
1. Delta dos arquivos (`Dockerfile`, `compose`, `.tf`, `.dockerignore`, `.env.example`). 2. Comandos exatos que o **dono** roda, em ordem. 3. Saída do `plan` com os pontos de risco destacados. 4. Procedimento de backup, atualização e rollback (vira o `RUNBOOK.md`). 5. Custo mensal estimado. 6. D-NN/QA-NN. 7. Commit (`chore(infra): …`).

## Armadilhas pagas
- Build na máquina do cliente: lento, frágil e sem versão rastreável — publique imagem e faça pull pinado.
- Banco dentro do container: dado perdido no primeiro deploy.
- `:latest` em base ou em deploy: impossível saber e reproduzir o que está rodando.
- Segredo em `ARG`/camada intermediária, achando que apagar depois resolve.
- Automação de atualização ligada antes do rollback ser testado na máquina real.
