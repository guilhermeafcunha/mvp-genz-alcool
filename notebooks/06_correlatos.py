# Databricks notebook source
# MAGIC %md
# MAGIC # 06. Exploração: o que anda junto com o consumo abusivo entre jovens?
# MAGIC
# MAGIC **Etapa do roteiro:** 3.5 (b), análise complementar. O Vigitel pergunta muito mais que álcool: fumo, cigarro
# MAGIC eletrônico, tempo de tela, sono, depressão, trabalho, estudo, alimentação. Este notebook mede, entre jovens de
# MAGIC 18 a 24 anos, a **diferença de consumo abusivo entre quem tem e quem não tem cada característica**, ajustada por
# MAGIC sexo e edição (homens bebem mais e as perguntas existem em anos diferentes; sem o ajuste, apareceriam
# MAGIC associações falsas).
# MAGIC
# MAGIC As variáveis vêm da **bronze** (as 486 colunas originais), ligadas à silver pela `linha_origem`: é o motivo de a
# MAGIC bronze guardar o arquivo inteiro. Os códigos foram conferidos no dicionário oficial, porque alguns códigos mudam
# MAGIC de significado entre anos (a `r901`, por exemplo, é "bolsa família" em 2019 e "apostas online" em 2024, e não foi
# MAGIC publicada em 2024).
# MAGIC
# MAGIC **Cuidados de leitura:** (1) associação não é causa, e pode ser nos dois sentidos (beber piora o sono ou dormir
# MAGIC mal leva a beber?); (2) com 21 testes, cerca de 1 pode dar "significativo" por acaso: a coluna
# MAGIC `significativa_bonferroni` aplica um critério mais rígido; (3) o ajuste é só por sexo e edição.

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
import numpy as np
import pandas as pd
import vigitel_etl as etl
import analise as an
import graficos as gr

CATALOGO, ESQUEMA = "workspace", "genz_alcool"
T = lambda nome: f"{CATALOGO}.{ESQUEMA}.{nome}"
FIG_DIR = os.environ.get("FIG_DIR") or (f"/Volumes/{CATALOGO}/{ESQUEMA}/raw/figuras"
                                        if "DATABRICKS_RUNTIME_VERSION" in os.environ else "../resultados/figuras")
os.makedirs(FIG_DIR, exist_ok=True)

# COMMAND ----------

brutas = ", ".join(f"b.{c}" for c in an.colunas_candidatas())
d = spark.sql(f"""
    SELECT s.ano, s.sexo, s.faixa_etaria, s.geracao, s.alcabu, s.peso_norm, {brutas}
    FROM {T('silver_vigitel')} s
    JOIN {T('bronze_vigitel')} b ON b.linha_origem = s.linha_origem""").toPandas()
d = an.montar_exposicoes(d)
print(f"{len(d):,} entrevistas; jovens de 18 a 24: {(d['faixa_etaria'] == '18 a 24').sum():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Tabela de correlatos (jovens de 18 a 24, ajustada por sexo e edição)
# MAGIC `expectativa` é a classificação feita **antes** de olhar os dados (provável, incerta, improvável).
# MAGIC `dif_adultos` repete a conta para todos os adultos: quando a associação só aparece entre os jovens, é mais
# MAGIC interessante.

# COMMAND ----------

corr = an.tabela_correlatos(d)
display(corr.round(1))

# COMMAND ----------

gr.correlatos(corr, FIG_DIR)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Destaques

# COMMAND ----------

destaque = ["usa cigarro eletrônico", "diagnóstico de depressão", "tela no lazer 3h+/dia", "trabalha"]
jov = d[d["faixa_etaria"] == "18 a 24"]
linhas = []
for v in destaque:
    for e in (0, 1):
        s = jov[jov[v] == e]
        linhas.append(dict(variavel=v, exposto=e, n=len(s), prev=np.average(s["alcabu"], weights=s["peso_norm"]) * 100))
dest = pd.DataFrame(linhas)
display(dest.round(1))
gr.correlatos_destaque(dest, FIG_DIR)

# COMMAND ----------

for nome, pdf in {"res_correlatos": corr, "res_correlatos_destaque": dest}.items():
    etl.gravar_tabela(spark, pdf, T(nome))
print("Tabelas de correlatos gravadas.")
