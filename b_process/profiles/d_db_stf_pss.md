---
tags: [perfil, stack, banco, padrao-equipe]
status: atual
tipo: perfil
data: 2026-08-28
---
# Perfil de banco — padrão da equipe (STF PSS)

> **Quem lê isto:** a sessão que vai escrever DDL, migration, entidade ou consulta. Copie as
> linhas de "Representações obrigatórias" para o `a_context/a_context_source.md` do projeto —
> é lá que a restrição é lida em **toda** sessão; aqui é a referência, não a verdade.

O padrão da equipe define nomes de tabela e prefixos de coluna. Não é gosto: com o prefixo, o
tipo da coluna é legível na consulta, sem abrir o esquema — e é o que permite revisar uma
migration sem carregar o modelo inteiro no contexto.

## Tabelas

| Padrão | Uso |
|---|---|
| `{TAG}_TP_*` | tabela de **tipo/enum** (domínio fechado) |
| `{TAG}_TB_*` | tabela de **entidade de negócio** |
| `{TAG}_TB_*_CHANGE` | **rastro de alteração** (auditoria) da tabela de mesmo nome |

`{TAG}` é a sigla do microserviço, a mesma do nome do repositório
(`stf_pss_ms_sat` → `SAT_`).

Exemplo, para o serviço SAT:

```
SAT_TP_TEST_STATUS        tipos de status de teste
SAT_TB_TEST_CASE          tabela principal de casos de teste
SAT_TB_TEST_CASE_CHANGE   histórico de alterações da tabela acima
```

## Colunas — o prefixo declara o tipo

| Prefixo | Tipo |
|---|---|
| `u_` | UUID |
| `i_` | Integer / Smallint |
| `s_` | String / Varchar |
| `n_` | Numeric (valor monetário) |
| `ts_` | Timestamp |
| `b_` | Boolean |

```sql
u_test_case_id  UUID PRIMARY KEY
i_status_id     SMALLINT
s_description   VARCHAR(255)
n_duration_ms   NUMERIC(18,2)
ts_executed_at  TIMESTAMPTZ
b_active        BOOLEAN
```

## O que copiar para o contexto-fonte do projeto

Uma linha, dentro de **Representações obrigatórias**:

```
- **Banco:** tabelas `{TAG}_TP_*` / `{TAG}_TB_*` / `{TAG}_TB_*_CHANGE`; colunas com prefixo
  de tipo (`u_ i_ s_ n_ ts_ b_`) — perfil em `b_process/profiles/d_db_stf_pss.md`
```

## O que este perfil NÃO faz

**Não é cobrado por máquina.** O `check.py` não lê DDL: ele não sabe se a sua migration
respeitou o prefixo. Isto aqui é referência para a sessão e material de revisão — na régua do
próprio kit, é nota 3 ("existe e funciona, porém depende da disciplina de quem usa"), não 4.

Um portão possível, se algum dia a divergência custar caro: uma checagem sobre os arquivos
`.sql` do projeto, cobrando prefixo em toda coluna declarada. Ela não existe hoje **porque
nenhum projeto medido com este kit tem banco** — e o kit não escreve checagem para problema
que ninguém teve ainda. Quando existir o primeiro, esta seção vira `D-NN`.
