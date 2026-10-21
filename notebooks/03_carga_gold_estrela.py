# Databricks notebook source
# MAGIC %md
# MAGIC # 03. Carga no modelo estrela (Silver para Gold)
# MAGIC
# MAGIC **Etapa do roteiro:** 3.3 Modelagem e 3.4 Carga. O modelo é um **esquema estrela** com uma tabela fato no grão
# MAGIC de **entrevista** e seis dimensões. O diagrama está em `catalogo/modelo_estrela.md` e o dicionário em
# MAGIC `catalogo/catalogo_de_dados.md`.
# MAGIC
# MAGIC | Tabela | Tipo | Grão / conteúdo |
# MAGIC |---|---|---|
# MAGIC | `fato_entrevista` | fato | uma entrevista de 2010 em diante: consumo abusivo, bebe ao menos 1x/mês, peso e peso normalizado |
# MAGIC | `dim_edicao` | dimensão | ano da edição, entrevistas, % celular, pandemia, filtro do bloco de álcool |
# MAGIC | `dim_capital` | dimensão | 27 capitais, UF e região (D12) |
# MAGIC | `dim_geracao` | dimensão | millennials, zillennials, geração Z e "outra", com os anos de nascimento (D2) |
# MAGIC | `dim_escolaridade` | dimensão | 0 a 8, 9 a 11, 12 anos e mais |
# MAGIC | `dim_faixa_etaria` | dimensão | seis faixas etárias do Vigitel |
# MAGIC | `dim_sexo` | dimensão | masculino, feminino |

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

silver = spark.table(T("silver_vigitel")).toPandas()
gold = etl.montar_gold(silver)
print("Integridade referencial OK:", etl.validar_gold(gold))

# COMMAND ----------

DESCRICOES = {
    "fato_entrevista": "Fato: uma entrevista do Vigitel de 2010 em diante (consumo abusivo, bebe ao menos 1x por mes, pesos)",
    "dim_edicao": "Dimensao: edicao do Vigitel, entrevistas, % celular, pandemia e filtro do bloco de alcool",
    "dim_capital": "Dimensao: capital, UF e regiao (regiao derivada da capital, decisao D12)",
    "dim_geracao": "Dimensao: geracao pelo ano de nascimento (millennials 1986-92, zillennials 1993-98, geracao Z 1999-2006)",
    "dim_escolaridade": "Dimensao: faixa de escolaridade (0 a 8, 9 a 11, 12 anos e mais)",
    "dim_faixa_etaria": "Dimensao: faixa etaria do Vigitel",
    "dim_sexo": "Dimensao: sexo",
}
for nome, pdf in gold.items():
    etl.gravar_tabela(spark, pdf, T(nome))
    try:
        spark.sql(f"COMMENT ON TABLE {T(nome)} IS '{DESCRICOES[nome]}'")
    except Exception as e:   # comentário é opcional
        print("sem comentario em", nome, "->", type(e).__name__)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verificação (tirar screenshot)

# COMMAND ----------

display(spark.sql(f"SHOW TABLES IN {CATALOGO}.{ESQUEMA}"))

# COMMAND ----------

# A fato junto com as dimensões reproduz as linhas da silver (sem perda nem duplicação)
chk = spark.sql(f"""
    SELECT COUNT(*) AS linhas_fato, (SELECT COUNT(*) FROM {T('silver_vigitel')}) AS linhas_silver
    FROM {T('fato_entrevista')} f
    JOIN {T('dim_edicao')} e ON e.edicao_sk = f.edicao_sk
    JOIN {T('dim_capital')} c ON c.capital_sk = f.capital_sk
    JOIN {T('dim_geracao')} g ON g.geracao_sk = f.geracao_sk
    JOIN {T('dim_escolaridade')} s ON s.escolaridade_sk = f.escolaridade_sk
    JOIN {T('dim_faixa_etaria')} fe ON fe.faixa_etaria_sk = f.faixa_etaria_sk
    JOIN {T('dim_sexo')} x ON x.sexo_sk = f.sexo_sk""").toPandas()
display(chk)
assert chk.linhas_fato.iloc[0] == chk.linhas_silver.iloc[0]
print("OK: modelo estrela carregado e consistente.")

# COMMAND ----------

# Exemplo de consulta no modelo: consumo abusivo ponderado aos 18-24 anos, por geração e sexo
display(spark.sql(f"""
    SELECT g.geracao, x.sexo, COUNT(*) AS entrevistas,
           ROUND(100 * SUM(f.peso_norm * f.alcabu) / SUM(f.peso_norm), 1) AS consumo_abusivo_pct
    FROM {T('fato_entrevista')} f
    JOIN {T('dim_geracao')} g ON g.geracao_sk = f.geracao_sk
    JOIN {T('dim_faixa_etaria')} fe ON fe.faixa_etaria_sk = f.faixa_etaria_sk
    JOIN {T('dim_sexo')} x ON x.sexo_sk = f.sexo_sk
    WHERE fe.faixa_etaria = '18 a 24' AND g.geracao <> 'outra'
    GROUP BY g.geracao_sk, g.geracao, x.sexo ORDER BY g.geracao_sk, x.sexo"""))
