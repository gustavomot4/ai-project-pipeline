---
tags: [contexto, indice]
status: atual
---
# contexto/ — domínio por tema (leitura sob demanda)

O [[CONTEXT]] tem orçamento de 4.000 caracteres; o conhecimento de domínio que não cabe lá mora aqui, fatiado por tema. **Nenhuma sessão carrega esta pasta por padrão** — cada arquivo entra no "Mapa de leitura" do [[CONTEXT]] com a condição que justifica lê-lo.

## Comece vazio
Esta pasta nasce vazia de propósito. Crie um arquivo só quando um tema **não couber** no [[CONTEXT]] e alguma tarefa realmente precisar dele. Pasta cheia de documento que ninguém lê é custo de manutenção, não organização.

## Temas que a maioria dos apps acaba precisando
| Arquivo sugerido | Conteúdo | Ler quando |
|---|---|---|
| `regras-de-negocio.md` | as regras numeradas (RN-001…), cada uma marcada confirmada/assumida | a tarefa toca a regra |
| `fluxos.md` | os fluxos de uso passo a passo (FLUXO-001…) | mexer numa tela/fluxo |
| `modelo-de-dados.md` | entidades, donos do dado, decisões de tipo e o porquê | mexer no schema |
| `glossario.md` | termos do domínio — garante que agente e dono falam a mesma língua | dúvida de vocabulário |
| `integracoes.md` | contratos e **amostras reais** de payload de cada dependência externa | escrever/alterar integração |
| `usuarios.md` | quem usa, nível técnico, aparelho, restrições de acessibilidade | decisão de UX |

## Regras
1. **Um tema por arquivo**, com frontmatter: `tags`, `status` (atual/rascunho/histórico/congelado) e `data`.
2. **Registre a origem de cada afirmação:** confirmada pelo dono × assumida pelo agente. Assumida que ninguém validou é dívida, e precisa aparecer como Q-NN em [[DECISIONS]].
3. **Doc congelado** (contrato, modelo de dados) muda por versão + D-NN, nunca por edição silenciosa.
4. **Estado numérico vigente NÃO mora aqui** (versão, contagens, métricas) — mora só no [[CONTEXT]]; aqui os docs apontam.
5. Ao criar um arquivo, **adicione a linha dele no Mapa de leitura do [[CONTEXT]]**. Doc fora do mapa nunca é lido.
6. Amostra real de payload vale mais que descrição de payload. Cole a amostra.
