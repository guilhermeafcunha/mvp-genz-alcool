# Databricks notebook source
# MAGIC %md
# MAGIC # 01. Coleta e camada Bronze
# MAGIC
# MAGIC **Projeto:** MVP Geração Z e consumo de álcool (Vigitel 2006-2024) | **Etapa do roteiro:** 3.2 Coleta
# MAGIC
# MAGIC Esta etapa registra a origem do dado, grava o arquivo bruto na nuvem (Volume do Unity Catalog) e cria a
# MAGIC tabela **bronze**: uma cópia fiel do CSV, com **todas as 486 colunas** como texto, mais a linha de origem.
# MAGIC Nenhuma regra de negócio é aplicada aqui.
# MAGIC
# MAGIC | Item | Valor |
# MAGIC |---|---|
# MAGIC | Fonte | Ministério da Saúde, SVSA/DAENT. *Vigitel Brasil 2006-2024*, base harmonizada (24/08/2026) |
# MAGIC | Página | https://svs.aids.gov.br/daent/cgdnt/vigitel/ |
# MAGIC | Arquivo | `vigitel-2006-2024-peso-rake-csv.zip` (87 MB; contém um CSV de 577 MB, vírgula, cabeçalho) |
# MAGIC | Licença | Creative Commons Atribuição-SemDerivações 3.0 (portal) |
# MAGIC | Coleta | Download automático do site oficial para o Volume; se o cluster não tiver internet, envie o ZIP manualmente para o Volume |
# MAGIC
# MAGIC **Evidência:** tire um screenshot da tela do Volume com o arquivo e da saída da seção 4.

# COMMAND ----------

import os, sys

def _pasta_scripts():
    """Localiza scripts/ (o repositório precisa ser importado inteiro, com notebooks/ e scripts/ lado a lado)."""
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
import datetime, shutil, urllib.request
import pandas as pd
import vigitel_etl as etl

CATALOGO, ESQUEMA, VOLUME = "workspace", "genz_alcool", "raw"
CAMINHO_ZIP = f"/Volumes/{CATALOGO}/{ESQUEMA}/{VOLUME}/{etl.ARQ_ZIP}"
T = lambda nome: f"{CATALOGO}.{ESQUEMA}.{nome}"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOGO}.{ESQUEMA}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOGO}.{ESQUEMA}.{VOLUME}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Arquivo no Volume (download do site oficial, se ainda não estiver lá)

# COMMAND ----------

if not os.path.exists(CAMINHO_ZIP):
    url = etl.URL_BASE + etl.ARQ_ZIP
    print("Baixando", url)
    try:
        temporario = "/tmp/" + etl.ARQ_ZIP
        pedido = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (MVP PSP8 UnB)"})
        with urllib.request.urlopen(pedido, timeout=600) as r, open(temporario, "wb") as f:
            shutil.copyfileobj(r, f, length=1 << 20)
        shutil.copyfile(temporario, CAMINHO_ZIP)
    except Exception as erro:
        raise RuntimeError(f"Download falhou ({erro}). Envie o ZIP para {CAMINHO_ZIP} pelo Catalog "
                           "(Upload to this volume) e rode de novo.")

tamanho = os.path.getsize(CAMINHO_ZIP)
sha256 = etl.sha256_arquivo(CAMINHO_ZIP)
print(f"Arquivo: {CAMINHO_ZIP}\nTamanho: {tamanho:,} bytes\nSHA-256: {sha256}")
assert sha256 == etl.SHA256_ZIP, "O ZIP não é a versão usada no MVP (SHA-256 diferente). Confira a data de publicação."

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Leitura do CSV bruto e gravação da Bronze, em lotes
# MAGIC
# MAGIC O CSV é lido de dentro do ZIP, **tudo como texto** e em lotes de 20 mil linhas (a base tem 833 mil linhas e 486
# MAGIC colunas; um único lote passaria do limite de memória e de mensagem do Databricks Free Edition). A codificação é
# MAGIC `latin-1` porque o arquivo mistura latin-1 e UTF-8 em campos de texto livre (achado da AED, seção 2.1); célula vazia
# MAGIC vira nulo. A única coluna acrescentada é `linha_origem` (número do registro no arquivo), base da chave substituta
# MAGIC da silver (D10). O texto livre fica **só** nesta camada (D12).

# COMMAND ----------

linhas_bronze = etl.gravar_lotes(spark, etl.ler_bruto_em_lotes(CAMINHO_ZIP), T("bronze_vigitel"))
print(f"Bronze gravada: {linhas_bronze:,} linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Log de coleta

# COMMAND ----------

data_coleta = datetime.date.today().isoformat()
log = pd.DataFrame([dict(
    arquivo=etl.ARQ_ZIP, caminho_volume=CAMINHO_ZIP, csv_interno=etl.nome_csv(CAMINHO_ZIP), data_coleta=data_coleta,
    bytes=int(tamanho), sha256=sha256, linhas=int(linhas_bronze), colunas_csv=etl.COLUNAS_CSV,
    formato="ZIP com CSV, virgula, cabecalho, codificacao mista (lido como latin-1)",
    fonte="Ministerio da Saude, SVSA/DAENT, Vigitel Brasil 2006-2024 (base harmonizada, 24/08/2026)",
    url=etl.URL_BASE, licenca="CC BY-ND 3.0 (portal)")])
etl.gravar_tabela(spark, log, T("bronze_coleta_log"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Verificação (tirar screenshot desta saída)

# COMMAND ----------

n = spark.sql(f"SELECT COUNT(*) AS n FROM {T('bronze_vigitel')}").toPandas().iloc[0, 0]
display(spark.sql(f"SELECT * FROM {T('bronze_coleta_log')}"))
display(spark.sql(f"SELECT ano, COUNT(*) AS entrevistas FROM {T('bronze_vigitel')} GROUP BY ano ORDER BY ano"))
assert n == etl.LINHAS_CSV, f"Bronze com {n} linhas; o CSV tem {etl.LINHAS_CSV}"
print(f"OK: bronze persistida no Delta com {n:,} linhas, as mesmas do CSV.")
