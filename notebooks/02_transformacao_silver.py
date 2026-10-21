# Databricks notebook source
# MAGIC %md
# MAGIC # 02. Transformação (Bronze para Silver)
# MAGIC
# MAGIC **Etapa do roteiro:** 3.4 Carga (parte de transformação). As regras estão em `scripts/vigitel_etl.py`
# MAGIC (`montar_silver`) e vêm das decisões de tratamento D1 a D13, tomadas pelo autor depois da análise exploratória
# MAGIC (`DECISOES_TRATAMENTO.md` e *Relatório de Análise Exploratória de Dados v3*, seção 6).
# MAGIC
# MAGIC | # | Regra de negócio | Decisão | Motivo |
# MAGIC |---|---|---|---|
# MAGIC | S1 | Só edições de 2010 em diante; filtro pelo **ano**, nunca pelo nome da coluna | D5 | a pergunta de doses mudou para "5 ou mais" em 2010; a base guarda 2009 (pergunta antiga) já na coluna nova |
# MAGIC | S2 | `entrevista_id` = edição + linha do arquivo (ex.: `2024-000815`); `chave` oficial vira `chave_oficial` | D10 | a chave oficial só existe em 2014-2023 e se repete |
# MAGIC | S3 | Marcadores `edicao_pandemia` (2020-2021) e `edicao_filtro_novo` (2024) | D11, D13 | sensibilidades |
# MAGIC | S4 | `capital`, `uf` e `regiao` derivadas do código da capital; a `regiao` original não é usada | D12 | `regiao` vazia em 2012 |
# MAGIC | S5 | `modo_coleta`: fixo até 2021; de 2023 em diante, o informado em `tipo_fone` | D2, D13 | só existia fixo até 2021 |
# MAGIC | S6 | Idade, faixa etária e sexo com rótulos | — | legibilidade |
# MAGIC | S7 | `ano_nascimento` = ano − idade; `geracao`: millennials (1986-1992), zillennials (1993-1998), geração Z (1999-2006), outra | D2 | comparar gerações na mesma idade |
# MAGIC | S8 | `escolaridade` oficial (`fesc`) e `escolaridade_estimada` (q8a = 777/888) | D7, D8 | a escolaridade é estimada pelo Ministério nesses casos |
# MAGIC | S9 | `alcabu` oficial (consumo abusivo) | D6 | reproduzível em 100% a partir de q37/q38 |
# MAGIC | S10 | `bebe_mensal` (q36 de 1 a 5) e `costuma_beber_q35` (só até 2023, como conferência) | D6 | decomposição: quem bebe x quanto exagera, sem perder 2024 |
# MAGIC | S11 | `peso_norm` = peso ÷ soma dos pesos da edição | D4 | juntar edições exige pesos na mesma escala |
# MAGIC | — | Texto livre e as demais 470 colunas não passam para a silver | D12 | minimização (LGPD) |
# MAGIC
# MAGIC Decisões sem transformação de linha: D1 (2022 não é imputado), D3 (resolvida pela D2), D9 (apresentação da P5,
# MAGIC no notebook 05).

# COMMAND ----------

import os, sys

def _pasta_scripts():
    candidatos = [os.getcwd(), os.path.dirname(os.getcwd())]
    try:
        nb = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
        candidatos.insert(0, os.path.dirname(os.path.dirname("/Workspace" + nb)))
    except Exception:
        pass
    for base in candidatos:
        if os.path.exists(os.path.join(base, "scripts", "vigitel_etl.py")):
            return os.path.join(base, "scripts")
    raise ModuleNotFoundError("Pasta scripts/ não encontrada. Importe o repositório inteiro (Git folder) "
                              "mantendo notebooks/ e scripts/ lado a lado. Pastas testadas: " + ", ".join(candidatos))

sys.path.insert(0, _pasta_scripts())
import vigitel_etl as etl

CATALOGO, ESQUEMA = "workspace", "genz_alcool"
T = lambda nome: f"{CATALOGO}.{ESQUEMA}.{nome}"

# COMMAND ----------

colunas = ", ".join(etl.COLUNAS_ANALISE)
bronze = spark.sql(f"SELECT {colunas} FROM {T('bronze_vigitel')}").toPandas()
print(f"Bronze (colunas da análise): {len(bronze):,} linhas")
silver = etl.montar_silver(bronze)
etl.validar_silver(bronze, silver)   # testes automáticos das regras (levanta erro se algo falhar)
print(f"Silver: {len(silver):,} linhas, {silver.shape[1]} colunas | testes: OK")

# COMMAND ----------

etl.gravar_tabela(spark, silver, T("silver_vigitel"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verificação (tirar screenshot)

# COMMAND ----------

display(spark.sql(f"""
    SELECT geracao, faixa_etaria, COUNT(*) AS entrevistas, MIN(ano) AS primeira_edicao, MAX(ano) AS ultima_edicao
    FROM {T('silver_vigitel')}
    WHERE geracao <> 'outra' AND faixa_etaria = '18 a 24'
    GROUP BY geracao, faixa_etaria ORDER BY primeira_edicao"""))

# COMMAND ----------

display(spark.sql(f"""
    SELECT ano, modo_coleta, COUNT(*) AS entrevistas, ROUND(SUM(peso_norm), 6) AS soma_peso_norm
    FROM {T('silver_vigitel')} GROUP BY ano, modo_coleta ORDER BY ano, modo_coleta"""))
