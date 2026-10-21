"""
qualidade.py: analise de qualidade da silver (notebook 04).

Dimensoes: completude, unicidade, consistencia, conformidade, acuracia (plausibilidade) e atualidade.
"""
import numpy as np
import pandas as pd


def perfil_atributos(s):
    """Completude, cardinalidade e faixa de valores de cada atributo da silver."""
    linhas = []
    for c in s.columns:
        col = s[c]
        num = pd.api.types.is_numeric_dtype(col) and not pd.api.types.is_bool_dtype(col)
        linhas.append(dict(
            atributo=c, tipo=str(col.dtype), nulos=int(col.isna().sum()),
            pct_nulos=round(col.isna().mean() * 100, 2), distintos=int(col.nunique(dropna=True)),
            minimo=(float(col.min()) if num and col.notna().any() else None),
            maximo=(float(col.max()) if num and col.notna().any() else None),
            exemplos="; ".join(map(str, sorted(col.dropna().astype(str).unique())[:4]))))
    return pd.DataFrame(linhas)


def checagens(s, linhas_bronze, linhas_bronze_2010):
    """Regras de qualidade: o que foi verificado, quantas violacoes e qual tratamento (decisao) se aplica."""
    faixa = pd.cut(s["idade"], [17, 24, 34, 44, 54, 64, 200], labels=[1, 2, 3, 4, 5, 6]).astype(int)
    esc = pd.cut(s["anos_estudo"], [-1, 8.999, 11.999, 99], labels=[1, 2, 3]).astype(int)
    somas = s.groupby("ano")["peso_norm"].sum()
    R = [
        ("completude", "Bronze tem o mesmo número de registros do CSV", abs(linhas_bronze - 833_217),
         "Leitura por lotes, com conferência das linhas físicas"),
        ("completude", "Silver tem todas as entrevistas de 2010 em diante", abs(len(s) - linhas_bronze_2010),
         "D5: filtro pelo ano"),
        ("completude", "Colunas obrigatórias sem nulos (capital, idade, sexo, escolaridade, alcabu, peso)",
         int(s[["capital", "idade", "sexo", "escolaridade", "alcabu", "peso"]].isna().sum().sum()), "Nenhum"),
        ("completude", "Edição de 2022 ausente", int(2022 not in set(s["ano"])), "D1: lacuna mantida, sem imputar"),
        ("unicidade", "entrevista_id único", int(s["entrevista_id"].duplicated().sum()), "D10: chave substituta"),
        ("unicidade", "chave oficial repetida (só referência)", int(s["chave_oficial"].dropna().duplicated().sum()),
         "D10: não usada como identificador"),
        ("consistencia", "Faixa etária coerente com a idade", int((faixa != s["faixa_etaria_cod"]).sum()), "Nenhum"),
        ("consistencia", "Escolaridade coerente com os anos de estudo", int((esc != s["escolaridade_cod"]).sum()), "Nenhum"),
        ("consistencia", "Só responde às doses quem bebe ao menos 1x por mês (pulo de questionário)",
         int((s["respondeu_doses"] != s["bebe_mensal"]).sum()), "Vazio tratado como pulo, e não como faltante"),
        ("consistencia", "alcabu = 1 apenas para quem bebe ao menos 1x por mês",
         int(((s["alcabu"] == 1) & (s["bebe_mensal"] == 0)).sum()), "Nenhum"),
        ("conformidade", "Códigos de capital entre 1 e 27", int((~s["cidade_cod"].between(1, 27)).sum()), "D12: região derivada da capital"),
        ("conformidade", "Peso normalizado soma 1 em cada edição", int((~np.isclose(somas, 1.0)).sum()), "D4"),
        ("acuracia", "Idade entre 18 e 110 anos", int((~s["idade"].between(18, 110)).sum()),
         "Mantidas: fora das faixas da análise (18-24 e 35-44)"),
        ("acuracia", "Escolaridade estimada pelo Ministério (q8a = 777 ou 888)", int(s["escolaridade_estimada"].sum()),
         "D8: mantida; sensibilidade sem esses casos"),
        ("atualidade", "Edição mais recente", int(s["ano"].max()), "Vigitel 2024 (base harmonizada de 24/08/2026)"),
        ("atualidade", "Entrevistas por celular (2023-2024)", int((s["modo_coleta"] == "celular").sum()),
         "D2 e D13: sensibilidades geração Z só por fixo e sem 2024"),
    ]
    out = pd.DataFrame(R, columns=["dimensao", "regra", "ocorrencias", "tratamento"])
    informativas = out["regra"].str.contains("2022|chave oficial|estimada|mais recente|celular|110 anos")
    out["situacao"] = np.where(informativas, "informativa", np.where(out["ocorrencias"] == 0, "ok", "VIOLAÇÃO"))
    return out


def cobertura(s):
    """Entrevistas por edição, modo e geração aos 18-24 anos."""
    j = s[s["faixa_etaria"] == "18 a 24"]
    t = pd.crosstab(j["ano"], j["geracao"])
    t["celular_%"] = s.groupby("ano")["modo_coleta"].apply(lambda m: round((m == "celular").mean() * 100, 1))
    return t.reset_index()
