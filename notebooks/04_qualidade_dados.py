# Databricks notebook source
# MAGIC %md
# MAGIC # 04. Análise de qualidade dos dados
# MAGIC
# MAGIC **Etapa do roteiro:** 3.5 (a) Qualidade de dados. Dimensões: completude, unicidade, consistência, conformidade,
# MAGIC acurácia (plausibilidade) e atualidade. As regras estão em `scripts/qualidade.py`. Resultado em três tabelas:
# MAGIC `qa_checagens` (regras, ocorrências e tratamento), `qa_perfil_atributos` (completude e cardinalidade de cada
# MAGIC atributo da silver) e `qa_cobertura` (jovens por edição e geração, e % de entrevistas por celular).
# MAGIC
# MAGIC A análise exploratória (notebook de AED v3 e relatório) já mostrou que quase todo vazio da base é pulo de
# MAGIC questionário ou variável inexistente no ano; aqui as regras são reaplicadas sobre a silver, como teste automático.

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
import qualidade as qa

CATALOGO, ESQUEMA = "workspace", "genz_alcool"
T = lambda nome: f"{CATALOGO}.{ESQUEMA}.{nome}"
silver = spark.table(T("silver_vigitel")).toPandas()
cont = spark.sql(f"""SELECT COUNT(*) AS total, SUM(CASE WHEN CAST(ano AS INT) >= {etl.ANO_INICIAL} THEN 1 ELSE 0 END) AS desde_2010
                     FROM {T('bronze_vigitel')}""").toPandas().iloc[0]
print(f"Silver: {len(silver):,} linhas | Bronze: {int(cont.total):,} linhas ({int(cont.desde_2010):,} de 2010 em diante)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Regras de qualidade, ocorrências e tratamento

# COMMAND ----------

checks = qa.checagens(silver, int(cont.total), int(cont.desde_2010))
display(checks)
assert not (checks["situacao"] == "VIOLAÇÃO").any(), "Há violação de qualidade: ver a tabela acima"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Perfil por atributo da silver

# COMMAND ----------

perfil = qa.perfil_atributos(silver)
display(perfil)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Cobertura: jovens de 18 a 24 anos por edição e geração

# COMMAND ----------

cobertura = qa.cobertura(silver)
display(cobertura)

# COMMAND ----------

for nome, pdf in {"qa_checagens": checks, "qa_perfil_atributos": perfil, "qa_cobertura": cobertura}.items():
    pdf = pdf.copy()
    pdf.columns = [str(c).replace("%", "pct").replace(" ", "_") for c in pdf.columns]
    etl.gravar_tabela(spark, pdf, T(nome))
print("Tabelas de qualidade gravadas.")
