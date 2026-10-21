"""
Simulador local de Spark/Databricks (duckdb + pandas) para testar os notebooks sem cluster.

Uso (a partir da raiz do repositorio):
    python tests/rodar_local.py dados/raw/vigitel-2006-2024-peso-rake-csv.zip
    python tests/rodar_local.py dados/raw/vigitel-2006-2024-peso-rake-csv.zip --so 05,06   (reaproveita o banco)

Executa notebooks/01 a 06 em sequencia, trocando apenas o caminho do Volume pelo arquivo local.
Nao substitui a execucao no Databricks (que e a evidencia exigida); serve para detectar erros antes.
O banco duckdb fica em tests/_local.duckdb (apagado a cada execucao).
"""
import os
import re
import sys
from pathlib import Path

import duckdb
import matplotlib
import pandas as pd

matplotlib.use("Agg")
RAIZ = Path(__file__).resolve().parent.parent


class FakeDF:
    def __init__(self, pdf, con=None):
        self.pdf, self.con = pdf, con

    def toPandas(self):
        return self.pdf.copy()

    @property
    def write(self):
        return FakeWriter(self)


class FakeWriter:
    def __init__(self, df):
        self.df, self.m = df, "error"

    def format(self, _):
        return self

    def mode(self, m):
        self.m = m
        return self

    def option(self, *_):
        return self

    def saveAsTable(self, nome):
        con = self.df.con
        con.register("_tmp", self.df.pdf)
        if self.m == "append":
            con.execute(f"INSERT INTO {nome} SELECT * FROM _tmp")
        else:
            con.execute(f"CREATE OR REPLACE TABLE {nome} AS SELECT * FROM _tmp")
        con.unregister("_tmp")


def _tipo(t):
    return {"BIGINT": "Int64", "DOUBLE": "float64", "BOOLEAN": "boolean"}.get(t.upper(), "string")


class FakeSpark:
    def __init__(self, arquivo_db, reaproveitar=False):
        for p in (arquivo_db, Path(str(arquivo_db) + ".wal")):
            if Path(p).exists() and not reaproveitar:
                Path(p).unlink()
        self.con = duckdb.connect(str(arquivo_db))
        self.con.execute(f"ATTACH '{Path(arquivo_db).with_name('_workspace.duckdb')}' AS workspace")

    def sql(self, q):
        q = q.strip()
        if q.upper().startswith(("CREATE VOLUME", "COMMENT ON")):
            return FakeDF(pd.DataFrame(), self.con)
        m = re.match(r"SHOW TABLES IN (\w+)\.(\w+)", q, re.I)
        if m:
            q = (f"SELECT table_name AS tableName FROM information_schema.tables "
                 f"WHERE table_catalog='{m.group(1)}' AND table_schema='{m.group(2)}' ORDER BY 1")
        return FakeDF(self.con.execute(q).df(), self.con)

    def table(self, nome):
        return self.sql(f"SELECT * FROM {nome}")

    def createDataFrame(self, dados, schema):
        cols = [c.split() for c in schema.split(", ")]
        pdf = dados.copy() if isinstance(dados, pd.DataFrame) else pd.DataFrame(dados, columns=[c[0] for c in cols])
        for nome, tipo in cols:
            pdf[nome] = pdf[nome].astype(_tipo(tipo))
        return FakeDF(pdf, self.con)


def executar(caminho_nb, ns, zip_local):
    src = Path(caminho_nb).read_text(encoding="utf-8")
    src = src.replace('f"/Volumes/{CATALOGO}/{ESQUEMA}/{VOLUME}/{etl.ARQ_ZIP}"', repr(str(zip_local)))
    celulas = re.split(r"^# COMMAND ----------\s*$", src, flags=re.M)
    for i, c in enumerate(celulas):
        linhas = [l for l in c.splitlines() if not l.startswith("# MAGIC") and not l.startswith("# Databricks notebook source")]
        codigo = "\n".join(linhas).strip()
        if not codigo:
            continue
        try:
            exec(compile(codigo, f"{Path(caminho_nb).name}[celula {i}]", "exec"), ns)
        except Exception:
            print(f"\n*** ERRO em {Path(caminho_nb).name}, celula {i}:\n{codigo[:400]}\n")
            raise


def main():
    zip_local = Path(sys.argv[1]).resolve()
    figs = RAIZ / "resultados" / "figuras"
    figs.mkdir(parents=True, exist_ok=True)
    os.environ["FIG_DIR"] = str(figs)
    os.chdir(RAIZ / "notebooks")
    # --so 05,06 reaproveita o banco da execucao anterior e roda so esses notebooks
    so = sys.argv[sys.argv.index("--so") + 1].split(",") if "--so" in sys.argv else None
    spark = FakeSpark(RAIZ / "tests" / "_local.duckdb", reaproveitar=bool(so))

    def display(x):
        pdf = x.toPandas() if hasattr(x, "toPandas") else (x.data if hasattr(x, "data") else x)
        with pd.option_context("display.width", 250, "display.max_columns", 30, "display.max_colwidth", 60):
            print(pdf.head(30).to_string())

    ns = {"spark": spark, "display": display, "__name__": "__main__"}
    import matplotlib.pyplot as plt
    plt.show = lambda *a, **k: plt.close("all")
    for nb in sorted((RAIZ / "notebooks").glob("0[1-6]_*.py")):
        if so and nb.name[:2] not in so:
            continue
        print(f"\n===== {nb.name} =====", flush=True)
        executar(nb, ns, zip_local)
    print("\nTODOS OS NOTEBOOKS EXECUTARAM SEM ERRO")
    return spark


if __name__ == "__main__":
    main()
