"""
vigitel_etl.py: regras de ETL do MVP Geracao Z e alcool (Vigitel 2006-2024).

Usado pelos notebooks 01 a 04 do Databricks e pelo simulador local (tests/rodar_local.py).
Cada regra da silver cita a decisao de tratamento que a originou (DECISOES_TRATAMENTO.md, D1 a D13).
"""
import hashlib
import io
import zipfile

import numpy as np
import pandas as pd

# ---------------------------------------------------------------- constantes da fonte
URL_BASE = "https://svs.aids.gov.br/daent/cgdnt/vigitel/"
ARQ_ZIP = "vigitel-2006-2024-peso-rake-csv.zip"
SHA256_ZIP = "40139996d11deb2f52730c90f14e2df4bf5e53aba3cf1848fce391c93ff77993"
LINHAS_CSV = 833_217          # registros (sem o cabecalho)
COLUNAS_CSV = 486
ENCODING = "latin-1"          # o CSV mistura latin-1 e UTF-8 em campos de texto livre; latin-1 aceita qualquer byte

# Colunas que seguem da bronze para a silver (o resto, inclusive o texto livre, fica so na bronze: D12)
COLUNAS_ANALISE = ["linha_origem", "chave", "ano", "cidade", "tipo_fone", "q6", "fet", "q7", "q8a", "q8_anos",
                   "fesc", "q35", "q36", "q37", "q38", "alcabu", "pesorake2025"]

CAPITAIS = {
    1: ("Aracaju", "Nordeste"), 2: ("Belém", "Norte"), 3: ("Belo Horizonte", "Sudeste"), 4: ("Boa Vista", "Norte"),
    5: ("Campo Grande", "Centro-Oeste"), 6: ("Cuiabá", "Centro-Oeste"), 7: ("Curitiba", "Sul"),
    8: ("Florianópolis", "Sul"), 9: ("Fortaleza", "Nordeste"), 10: ("Goiânia", "Centro-Oeste"),
    11: ("João Pessoa", "Nordeste"), 12: ("Macapá", "Norte"), 13: ("Maceió", "Nordeste"), 14: ("Manaus", "Norte"),
    15: ("Natal", "Nordeste"), 16: ("Palmas", "Norte"), 17: ("Porto Alegre", "Sul"), 18: ("Porto Velho", "Norte"),
    19: ("Recife", "Nordeste"), 20: ("Rio Branco", "Norte"), 21: ("Rio de Janeiro", "Sudeste"),
    22: ("Salvador", "Nordeste"), 23: ("São Luís", "Nordeste"), 24: ("São Paulo", "Sudeste"),
    25: ("Teresina", "Nordeste"), 26: ("Vitória", "Sudeste"), 27: ("Distrito Federal", "Centro-Oeste"),
}
UF = {1: "SE", 2: "PA", 3: "MG", 4: "RR", 5: "MS", 6: "MT", 7: "PR", 8: "SC", 9: "CE", 10: "GO", 11: "PB", 12: "AP",
      13: "AL", 14: "AM", 15: "RN", 16: "TO", 17: "RS", 18: "RO", 19: "PE", 20: "AC", 21: "RJ", 22: "BA", 23: "MA",
      24: "SP", 25: "PI", 26: "ES", 27: "DF"}
FAIXA_ETARIA = {1: "18 a 24", 2: "25 a 34", 3: "35 a 44", 4: "45 a 54", 5: "55 a 64", 6: "65 e mais"}
ESCOLARIDADE = {1: "0 a 8 anos", 2: "9 a 11 anos", 3: "12 anos e mais"}
SEXO = {1: "masculino", 2: "feminino"}
# D2: geracoes pelo ano de nascimento (convencao do trabalho; Pew Research Center para millennials e geracao Z)
GERACOES = [("millennials", 1986, 1992), ("zillennials", 1993, 1998), ("geracao_z", 1999, 2006)]
ANO_INICIAL = 2010            # D5: pergunta de doses atual ("5 ou mais") a partir de 2010


# ---------------------------------------------------------------- coleta e bronze
def sha256_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def nome_csv(caminho_zip):
    with zipfile.ZipFile(caminho_zip) as z:
        return z.namelist()[0]


def ler_bruto_em_lotes(caminho_zip, tamanho_lote=20_000):
    """Le o CSV de dentro do ZIP, tudo como texto, em lotes. Vazio vira nulo; nenhum valor e alterado.

    Acrescenta `linha_origem`: numero do registro no arquivo (1 = primeira linha depois do cabecalho).
    """
    inicio = 1
    with zipfile.ZipFile(caminho_zip) as z, z.open(nome_csv(caminho_zip)) as f:
        texto = io.TextIOWrapper(f, encoding=ENCODING, newline="")
        for lote in pd.read_csv(texto, dtype=str, keep_default_na=False, na_values=[""], chunksize=tamanho_lote):
            lote.insert(0, "linha_origem", np.arange(inicio, inicio + len(lote), dtype="int64"))
            inicio += len(lote)
            yield lote


# ---------------------------------------------------------------- silver
def _num(s):
    return pd.to_numeric(s, errors="coerce")


def geracao_de(ano_nasc):
    """D2: millennials (1986-1992), zillennials (1993-1998), geracao Z (1999-2006); fora disso, 'outra'."""
    out = pd.Series("outra", index=ano_nasc.index, dtype=object)
    for nome, ini, fim in GERACOES:
        out[(ano_nasc >= ini) & (ano_nasc <= fim)] = nome
    return out


def montar_silver(bronze):
    """Aplica as regras S1 a S13 (decisoes D1 a D13). Recebe a bronze (colunas de COLUNAS_ANALISE, texto)."""
    b = bronze[COLUNAS_ANALISE].copy()
    ano = _num(b["ano"]).astype("int64")

    # S1 (D5): so edicoes a partir de 2010; o filtro e pelo ano, nunca pelo nome da coluna (2009 esta em q37/q38)
    b, ano = b[ano >= ANO_INICIAL].copy(), ano[ano >= ANO_INICIAL]
    s = pd.DataFrame(index=b.index)

    # S2 (D10): chave substituta = edicao + numero da linha no arquivo; a chave oficial fica so como referencia
    s["entrevista_id"] = ano.astype(str) + "-" + b["linha_origem"].astype("int64").map("{:06d}".format)
    s["linha_origem"] = b["linha_origem"].astype("int64")
    s["chave_oficial"] = b["chave"]
    s["ano"] = ano
    # S3 (D11, D13): marcadores de edicao para as sensibilidades
    s["edicao_pandemia"] = ano.isin([2020, 2021])
    s["edicao_filtro_novo"] = ano.eq(2024)

    # S4 (D12): capital e regiao derivadas do codigo da capital (a coluna regiao original nao e usada)
    cid = _num(b["cidade"]).astype("int64")
    s["cidade_cod"] = cid
    s["capital"] = cid.map(lambda c: CAPITAIS[c][0])
    s["uf"] = cid.map(UF)
    s["regiao"] = cid.map(lambda c: CAPITAIS[c][1])

    # S5: modo de coleta; ate 2021 so havia telefone fixo (a coluna vem vazia porque nao havia o que distinguir)
    fone = b["tipo_fone"].fillna("").str.strip().str.lower()
    s["modo_coleta"] = np.where(ano <= 2021, "fixo", np.where(fone == "celular", "celular", "fixo"))

    # S6: perfil
    s["idade"] = _num(b["q6"]).astype("int64")
    s["faixa_etaria_cod"] = _num(b["fet"]).astype("int64")
    s["faixa_etaria"] = s["faixa_etaria_cod"].map(FAIXA_ETARIA)
    s["sexo"] = _num(b["q7"]).astype("int64").map(SEXO)

    # S7 (D2): ano de nascimento (erro de ate 1 ano por causa do aniversario) e geracao
    s["ano_nascimento"] = s["ano"] - s["idade"]
    s["geracao"] = geracao_de(s["ano_nascimento"])

    # S8 (D7, D8): escolaridade oficial (fesc) e marcador de escolaridade estimada pelo Ministerio
    s["anos_estudo"] = _num(b["q8_anos"])
    s["escolaridade_cod"] = _num(b["fesc"]).astype("int64")
    s["escolaridade"] = s["escolaridade_cod"].map(ESCOLARIDADE)
    s["escolaridade_estimada"] = b["q8a"].isin(["777", "888"])

    # S9: indicador oficial (reproduzivel: q37 = 1 ou q38 = 1 a partir de 2009)
    s["alcabu"] = _num(b["alcabu"]).astype("int64")
    # S10 (D6): decomposicao; "bebe ao menos uma vez por mes" pela q36 (1 a 5); q35 so como conferencia ate 2023
    s["frequencia_cod"] = _num(b["q36"]).astype("Int64")
    s["bebe_mensal"] = s["frequencia_cod"].isin([1, 2, 3, 4, 5]).astype("int64")
    s["costuma_beber_q35"] = pd.array(np.where(ano <= 2023, (b["q35"] == "1").astype(int), -1), dtype="Int64")
    s.loc[s["costuma_beber_q35"] == -1, "costuma_beber_q35"] = pd.NA
    s["respondeu_doses"] = (b["q37"].notna() | b["q38"].notna()).astype("int64")

    # S11 (D4): peso original e peso normalizado para somar 1 em cada edicao
    s["peso"] = _num(b["pesorake2025"]).astype("float64")
    s["peso_norm"] = s["peso"] / s.groupby("ano")["peso"].transform("sum")
    return s.reset_index(drop=True)


def validar_silver(bronze, silver):
    """Testes automaticos das regras da silver. Levanta AssertionError se algo falhar."""
    esperado = int((_num(bronze["ano"]) >= ANO_INICIAL).sum())
    assert len(silver) == esperado, f"silver com {len(silver)} linhas, esperado {esperado}"
    assert silver["ano"].min() >= ANO_INICIAL, "S1: ha edicao anterior a 2010"
    assert silver["entrevista_id"].is_unique, "S2: entrevista_id repetido"
    obrig = ["capital", "regiao", "idade", "faixa_etaria", "sexo", "escolaridade", "alcabu", "peso", "peso_norm"]
    nulos = silver[obrig].isna().sum()
    assert nulos.sum() == 0, f"nulos em colunas obrigatorias: {nulos[nulos > 0].to_dict()}"
    somas = silver.groupby("ano")["peso_norm"].sum()
    assert np.allclose(somas, 1.0), "S11: peso_norm nao soma 1 em alguma edicao"
    faixa = pd.cut(silver["idade"], [17, 24, 34, 44, 54, 64, 200], labels=[1, 2, 3, 4, 5, 6]).astype(int)
    assert (faixa == silver["faixa_etaria_cod"]).all(), "faixa etaria incoerente com a idade"
    # pulo: so responde as doses quem bebe ao menos uma vez por mes, e todos esses respondem
    assert (silver["respondeu_doses"] == silver["bebe_mensal"]).all(), "S10: pulo das perguntas de doses nao confere"
    assert (silver.loc[silver["bebe_mensal"] == 0, "alcabu"] == 0).all(), "alcabu = 1 para quem nao bebe mensalmente"
    assert silver.loc[silver["ano"] == 2024, "costuma_beber_q35"].isna().all(), "S10: q35 deveria ser nula em 2024"
    return True


# ---------------------------------------------------------------- gold (modelo estrela)
def montar_gold(silver):
    """Fato no grao de entrevista e seis dimensoes. Devolve dict nome -> DataFrame."""
    s = silver
    dim_edicao = (s.groupby("ano").agg(entrevistas=("ano", "size"),
                                      pct_celular=("modo_coleta", lambda m: round((m == "celular").mean() * 100, 1)))
                  .reset_index())
    dim_edicao["edicao_sk"] = dim_edicao["ano"]
    dim_edicao["pandemia"] = dim_edicao["ano"].isin([2020, 2021])
    dim_edicao["filtro_bloco_alcool"] = np.where(dim_edicao["ano"] == 2024, "bebeu nos ultimos 12 meses (R502)",
                                                 "costuma beber (q35)")
    dim_edicao = dim_edicao[["edicao_sk", "ano", "entrevistas", "pct_celular", "pandemia", "filtro_bloco_alcool"]]

    dim_capital = pd.DataFrame([(c, n, UF[c], r) for c, (n, r) in CAPITAIS.items()],
                               columns=["capital_sk", "capital", "uf", "regiao"])
    dim_geracao = pd.DataFrame([(i + 1, n, a, b) for i, (n, a, b) in enumerate(GERACOES)] + [(9, "outra", None, None)],
                               columns=["geracao_sk", "geracao", "nascimento_inicio", "nascimento_fim"])
    dim_geracao[["nascimento_inicio", "nascimento_fim"]] = dim_geracao[["nascimento_inicio", "nascimento_fim"]].astype("Int64")
    dim_escolaridade = pd.DataFrame(list(ESCOLARIDADE.items()), columns=["escolaridade_sk", "escolaridade"])
    dim_faixa_etaria = pd.DataFrame(list(FAIXA_ETARIA.items()), columns=["faixa_etaria_sk", "faixa_etaria"])
    dim_sexo = pd.DataFrame(list(SEXO.items()), columns=["sexo_sk", "sexo"])

    sk_ger = dict(zip(dim_geracao["geracao"], dim_geracao["geracao_sk"]))
    fato = pd.DataFrame({
        "entrevista_id": s["entrevista_id"],
        "edicao_sk": s["ano"],
        "capital_sk": s["cidade_cod"],
        "geracao_sk": s["geracao"].map(sk_ger).astype("int64"),
        "escolaridade_sk": s["escolaridade_cod"],
        "faixa_etaria_sk": s["faixa_etaria_cod"],
        "sexo_sk": s["sexo"].map({v: k for k, v in SEXO.items()}).astype("int64"),
        "idade": s["idade"],
        "ano_nascimento": s["ano_nascimento"],
        "modo_coleta": s["modo_coleta"],
        "escolaridade_estimada": s["escolaridade_estimada"],
        "alcabu": s["alcabu"],
        "bebe_mensal": s["bebe_mensal"],
        "costuma_beber_q35": s["costuma_beber_q35"],
        "peso": s["peso"],
        "peso_norm": s["peso_norm"],
        "linha_origem": s["linha_origem"],
    })
    return {"fato_entrevista": fato, "dim_edicao": dim_edicao, "dim_capital": dim_capital,
            "dim_geracao": dim_geracao, "dim_escolaridade": dim_escolaridade,
            "dim_faixa_etaria": dim_faixa_etaria, "dim_sexo": dim_sexo}


def validar_gold(gold):
    """Integridade referencial e unicidade. Levanta AssertionError se algo estiver inconsistente."""
    f = gold["fato_entrevista"]
    assert f["entrevista_id"].is_unique, "fato com entrevista_id repetido"
    pares = {"edicao_sk": "dim_edicao", "capital_sk": "dim_capital", "geracao_sk": "dim_geracao",
             "escolaridade_sk": "dim_escolaridade", "faixa_etaria_sk": "dim_faixa_etaria", "sexo_sk": "dim_sexo"}
    for col, dim in pares.items():
        orfas = ~f[col].isin(gold[dim][col])
        assert not orfas.any(), f"{orfas.sum()} linhas da fato sem correspondencia em {dim}"
        assert gold[dim][col].is_unique, f"chave repetida em {dim}"
    return {nome: len(df) for nome, df in gold.items()}


# ---------------------------------------------------------------- Spark
def ddl_spark(pdf):
    """Esquema DDL do Spark ('col tipo, ...') a partir dos dtypes do pandas."""
    tipos = []
    for c, t in pdf.dtypes.items():
        n = str(t).lower()
        sp = ("BIGINT" if n.startswith(("int", "uint")) else "DOUBLE" if n.startswith("float")
              else "BOOLEAN" if n.startswith("bool") else "STRING")
        tipos.append(f"{c} {sp}")
    return ", ".join(tipos)


def _preparar(pdf):
    """Converte para tipos que o Spark aceita sem ambiguidade (nulos como None, inteiros anulaveis como objeto)."""
    out = pdf.copy()
    for c, t in out.dtypes.items():
        n = str(t)
        if n in ("Int64", "boolean"):
            out[c] = out[c].astype(object).where(out[c].notna(), None)
        elif n == "object":
            out[c] = out[c].where(out[c].notna(), None)
    return out


def gravar_lotes(spark, lotes, nome):
    """Grava uma sequencia de DataFrames do pandas (mesmas colunas) numa tabela Delta. Devolve o total de linhas."""
    total = 0
    for i, lote in enumerate(lotes):
        df = spark.createDataFrame(_preparar(lote), schema=ddl_spark(lote))
        w = df.write.format("delta")
        if i == 0:
            w.mode("overwrite").option("overwriteSchema", "true").saveAsTable(nome)
        else:
            w.mode("append").saveAsTable(nome)
        total += len(lote)
    return total


def gravar_tabela(spark, pdf, nome, tamanho_lote=50_000):
    """Grava um DataFrame do pandas como tabela Delta, em lotes (bases grandes passam do limite de uma mensagem)."""
    ddl = ddl_spark(pdf)
    for i, inicio in enumerate(range(0, max(len(pdf), 1), tamanho_lote)):
        lote = _preparar(pdf.iloc[inicio:inicio + tamanho_lote])
        df = spark.createDataFrame(lote, schema=ddl)
        w = df.write.format("delta")
        if i == 0:
            w.mode("overwrite").option("overwriteSchema", "true").saveAsTable(nome)
        else:
            w.mode("append").saveAsTable(nome)
