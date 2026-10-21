"""
analise.py: indicadores das perguntas P1 a P5 e sensibilidades (notebook 05).

Todas as prevalencias sao ponderadas pelo peso normalizado por edicao (D4). O intervalo de 95% e aproximado,
pelo n efetivo de Kish; o intervalo de uma diferenca entre grupos independentes combina os dois erros-padrao.

As comparacoes entre geracoes sao padronizadas pela idade simples (D14): a janela de observacao (2010-2024) faz
os millennials aparecerem sobretudo aos 22-24 anos e a geracao Z sobretudo aos 18-20, e o consumo abusivo sobe
com a idade dentro dos 18-24. A prevalencia padronizada e a media simples das prevalencias de cada idade
(padrao uniforme), sempre sobre as mesmas idades para as geracoes comparadas.
"""
import numpy as np
import pandas as pd

ORDEM_GER = ["millennials", "zillennials", "geracao_z"]
ROTULO_GER = {"millennials": "Millennials (1986-1992)", "zillennials": "Zillennials (1993-1998)",
              "geracao_z": "Geração Z (1999-2006)"}
ORDEM_ESC = ["0 a 8 anos", "9 a 11 anos", "12 anos e mais"]
# faixas de idade para a padronizacao quando as celulas de idade simples ficam pequenas (capitais, P5)
FAIXA_JOVEM = {18: "18-19", 19: "18-19", 20: "20-21", 21: "20-21", 22: "22-24", 23: "22-24", 24: "22-24"}


def prevalencia(df, por=None, y="alcabu", w="peso_norm"):
    """Prevalencia ponderada (%) com IC 95% aproximado (Kish). `por` = lista de colunas de agrupamento."""
    g = df.assign(_wy=df[w] * df[y], _w2=df[w] ** 2)
    grupos = g.groupby(por, observed=True) if por else g.assign(_t=1).groupby("_t")
    r = grupos.agg(n=(y, "size"), sw=(w, "sum"), swy=("_wy", "sum"), sw2=("_w2", "sum")).reset_index()
    p = r["swy"] / r["sw"]
    r["n_efetivo"] = r["sw"] ** 2 / r["sw2"]
    r["prev"] = p * 100
    r["ep"] = np.sqrt(p * (1 - p) / r["n_efetivo"]) * 100
    r["ic_inf"], r["ic_sup"] = r["prev"] - 1.96 * r["ep"], r["prev"] + 1.96 * r["ep"]
    return r.drop(columns=["sw", "swy", "sw2", "_t"], errors="ignore")


def prevalencia_padronizada(df, por, y="alcabu", w="peso_norm", estrato="idade", idades="comuns"):
    """Padronizacao direta pela idade (D14): prevalencia de cada grupo de `por` calculada como media das
    prevalencias de cada valor de `estrato` (idade simples ou faixa), com padrao uniforme por ano de idade.

    idades="comuns": o padrao usa so os estratos observados em TODOS os grupos (por exemplo, a geracao Z por
    telefone fixo nao chega aos 23-24 anos, entao a comparacao fica nos 18-22). idades="todas": o padrao usa todos
    os estratos do recorte, e o grupo que nao tem algum deles fica sem estimativa (NaN).
    Devolve as mesmas colunas de `prevalencia`, mais `idades_padrao` (estratos usados)."""
    por = list(por)
    cel = prevalencia(df, por + [estrato], y=y, w=w)
    n_grupos = len(cel[por].drop_duplicates())
    presentes = cel.groupby(estrato, observed=True).size()
    usar = presentes[presentes == n_grupos].index if idades == "comuns" else presentes.index
    cel = cel[cel[estrato].isin(usar)]
    # peso do padrao: proporcional ao numero de anos de idade de cada estrato (uniforme por ano de idade)
    anos = df[df[estrato].isin(usar)].groupby(estrato, observed=True)["idade"].nunique()
    padrao = anos / anos.sum()
    cel = cel.assign(_a=cel[estrato].map(padrao).astype(float))
    cel = cel.assign(_c=cel["prev"] * cel["_a"], _v=(cel["ep"] * cel["_a"]) ** 2)
    r = cel.groupby(por, observed=True).agg(n=("n", "sum"), n_estratos=(estrato, "size"), _a=("_a", "sum"),
                                            prev=("_c", "sum"), _v=("_v", "sum")).reset_index()
    completo = np.isclose(r["_a"], 1.0)
    r["prev"] = np.where(completo, r["prev"], np.nan)
    r["ep"] = np.where(completo, np.sqrt(r["_v"]), np.nan)
    r["ic_inf"], r["ic_sup"] = r["prev"] - 1.96 * r["ep"], r["prev"] + 1.96 * r["ep"]
    r["idades_padrao"] = ", ".join(str(v) for v in sorted(usar))
    return r.drop(columns=["_a", "_v", "n_estratos"])


def jovens(f):
    return f[(f["faixa_etaria"] == "18 a 24") & f["geracao"].isin(ORDEM_GER)]


def diferencas(tab, chaves=(), base="millennials", sucessivas=False):
    """Diferenca de cada geracao para a base, com IC 95% (grupos independentes).
    sucessivas=True acrescenta a comparacao de cada geracao com a anterior (geracao Z - zillennials)."""
    linhas = []
    grupos = tab.groupby(list(chaves)) if chaves else [((), tab)]
    pares = [(g, base) for g in ORDEM_GER if g != base]
    if sucessivas:
        pares += [(ORDEM_GER[i + 1], ORDEM_GER[i]) for i in range(1, len(ORDEM_GER) - 1)]
    for k, t in grupos:
        t = t.set_index("geracao")
        for g, b in pares:
            if b not in t.index or g not in t.index or pd.isna(t.loc[g, "prev"]) or pd.isna(t.loc[b, "prev"]):
                continue
            d = t.loc[g, "prev"] - t.loc[b, "prev"]
            ep = np.hypot(t.loc[g, "ep"], t.loc[b, "ep"])
            linha = dict(zip(chaves, k if isinstance(k, tuple) else (k,)))
            linha.update(comparacao=f"{g} - {b}", diferenca_pp=d, ic_inf=d - 1.96 * ep, ic_sup=d + 1.96 * ep,
                         significativa=bool(abs(d) > 1.96 * ep))
            linhas.append(linha)
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- P1
def p1(f):
    """P1: consumo abusivo aos 18-24 por geracao.
    prev / ep / ic_*: padronizada pela idade simples (D14), estimativa principal;
    prev_bruta / ep_bruta: sem padronizar (so o peso D4), para mostrar o tamanho do vies de idade;
    prev_padr_escolaridade: padronizada pela idade e, alem disso, pela escolaridade dos millennials (D7)."""
    j = jovens(f)
    bruta = prevalencia(j, ["geracao"])[["geracao", "prev", "ep"]].rename(columns={"prev": "prev_bruta", "ep": "ep_bruta"})
    padr = prevalencia_padronizada(j, ["geracao"])
    # D7 sobre a padronizada por idade: media das prevalencias por escolaridade com a composicao dos millennials
    comp = j[j["geracao"] == "millennials"].groupby("escolaridade")["peso_norm"].sum()
    comp = comp / comp.sum()
    por_esc = prevalencia_padronizada(j, ["geracao", "escolaridade"])
    por_esc["peso_comp"] = por_esc["escolaridade"].map(comp)
    esc = (por_esc.assign(_c=por_esc["prev"] * por_esc["peso_comp"], _v=(por_esc["ep"] * por_esc["peso_comp"]) ** 2)
           .groupby("geracao").agg(prev_padr_escolaridade=("_c", "sum"), _v=("_v", "sum")).reset_index())
    esc["ep_padr_escolaridade"] = np.sqrt(esc["_v"])
    out = padr.merge(bruta, on="geracao").merge(esc.drop(columns="_v"), on="geracao")
    return out.set_index("geracao").loc[ORDEM_GER].reset_index()


def por_idade(f, por=("geracao",)):
    """Prevalencia por idade simples (18 a 24) e geracao: a evidencia do vies de idade (D14).
    peso_pct: participacao de cada idade no peso da geracao (sem padronizar)."""
    j = jovens(f)
    t = prevalencia(j, list(por) + ["idade"])
    w = j.groupby(list(por) + ["idade"])["peso_norm"].sum()
    t["peso_pct"] = (w / w.groupby(level=list(range(len(por)))).transform("sum") * 100).values
    return t


def decomposicao(f, por=("geracao",)):
    """D6: consumo abusivo = (bebe ao menos 1x/mes) x (abusivo entre quem bebe ao menos 1x/mes).
    Todas as partes padronizadas pela idade (D14)."""
    j = jovens(f)
    pp = lambda d, y="alcabu": prevalencia_padronizada(d, list(por), y=y)
    a = pp(j)[list(por) + ["n", "prev", "ic_inf", "ic_sup"]].rename(columns={"prev": "abusivo"})
    b = pp(j, "bebe_mensal")[list(por) + ["prev"]].rename(columns={"prev": "bebe_mensal"})
    c = pp(j[j["bebe_mensal"] == 1])[list(por) + ["prev"]].rename(columns={"prev": "abusivo_entre_quem_bebe"})
    q = j[(j["ano"] <= 2023) & j["costuma_beber_q35"].notna()].astype({"costuma_beber_q35": float})
    d = pp(q, "costuma_beber_q35")[list(por) + ["prev"]].rename(columns={"prev": "costuma_beber_q35_ate_2023"})
    return a.merge(b, on=list(por)).merge(c, on=list(por)).merge(d, on=list(por))


# ---------------------------------------------------------------- P2, P4, P5
def por_grupo(f, coluna, filtro=None, padronizar=True, estrato="idade"):
    j = jovens(f if filtro is None else f[filtro])
    if not padronizar:
        return prevalencia(j, ["geracao", coluna])
    if estrato == "faixa_jovem":
        j = j.assign(faixa_jovem=j["idade"].map(FAIXA_JOVEM))
    return prevalencia_padronizada(j, ["geracao", coluna], estrato=estrato)


def p5(f):
    """P5 (D9): capitais em primeiro plano; quando a diferenca da capital nao e significativa, a regiao apoia.
    Nas capitais a padronizacao usa tres faixas (18-19, 20-21, 22-24), porque ha celulas de idade simples com
    15 entrevistas; nas regioes, idade simples (D14)."""
    cap = diferencas(por_grupo(f, "capital", estrato="faixa_jovem"), chaves=("capital",))
    cap = cap[cap["comparacao"] == "geracao_z - millennials"].copy()
    reg = diferencas(por_grupo(f, "regiao"), chaves=("regiao",))
    reg = reg[reg["comparacao"] == "geracao_z - millennials"].set_index("regiao")
    regiao_de = f.drop_duplicates("capital").set_index("capital")["regiao"]
    cap["regiao"] = cap["capital"].map(regiao_de)
    cap["regiao_diferenca_pp"] = cap["regiao"].map(reg["diferenca_pp"])
    cap["regiao_significativa"] = cap["regiao"].map(reg["significativa"])
    cap["leitura"] = np.where(
        cap["significativa"], "capital com diferença própria (fora da margem)",
        np.where(cap["regiao_significativa"], "capital inconclusiva; usar a região (diferença fora da margem)",
                 "capital e região inconclusivas"))
    return cap.sort_values("diferenca_pp").reset_index(drop=True), reg.reset_index()


# ---------------------------------------------------------------- P3
def p3_periodo(f):
    """P3 (a): a mudanca dos jovens (millennials -> geracao Z) contra a dos adultos de 35 a 44 anos nas
    mesmas edicoes em que cada geracao foi observada aos 18-24 (2010-2016 e 2017-2024). Os dois grupos sao
    padronizados pela idade simples (D14). Devolve tambem a diferenca das diferencas com IC 95%."""
    jov = prevalencia_padronizada(jovens(f)[lambda d: d["geracao"].isin(["millennials", "geracao_z"])], ["geracao"])
    adu = f[f["faixa_etaria"] == "35 a 44"].assign(
        periodo=lambda d: np.where(d["ano"] <= 2016, "millennials", "geracao_z"))
    adu = prevalencia_padronizada(adu, ["periodo"]).rename(columns={"periodo": "geracao"})
    linhas = []
    for nome, t in [("jovens 18 a 24", jov), ("adultos 35 a 44 (mesmas edições)", adu)]:
        t = t.set_index("geracao")
        d = t.loc["geracao_z", "prev"] - t.loc["millennials", "prev"]
        ep = np.hypot(t.loc["geracao_z", "ep"], t.loc["millennials", "ep"])
        linhas.append(dict(grupo=nome, periodo_millennials=t.loc["millennials", "prev"],
                           periodo_geracao_z=t.loc["geracao_z", "prev"], diferenca_pp=d, ep=ep,
                           ic_inf=d - 1.96 * ep, ic_sup=d + 1.96 * ep))
    out = pd.DataFrame(linhas)
    dd = out["diferenca_pp"].iloc[0] - out["diferenca_pp"].iloc[1]
    ep_dd = np.hypot(out["ep"].iloc[0], out["ep"].iloc[1])
    dd_tab = pd.DataFrame([dict(diferenca_das_diferencas_pp=dd, ic_inf=dd - 1.96 * ep_dd, ic_sup=dd + 1.96 * ep_dd,
                                significativa=bool(abs(dd) > 1.96 * ep_dd))])
    return out.drop(columns="ep"), dd_tab


def p3_envelhecimento(f):
    """P3 (b): cada geracao acompanhada ao envelhecer (pseudo-coorte), por sexo. Dentro de cada faixa
    (18-24, 25-29, ...) a prevalencia e padronizada pela idade simples (D14); a geracao que ainda nao passou por
    todas as idades da faixa fica de fora (por exemplo, a geracao Z aos 25-29)."""
    g = f[f["geracao"].isin(ORDEM_GER)].copy()
    g["idade_grupo"] = pd.cut(g["idade"], [17, 24, 29, 34, 39], labels=["18-24", "25-29", "30-34", "35-39"])
    partes = []
    for faixa, sub in g.dropna(subset=["idade_grupo"]).groupby("idade_grupo", observed=True):
        t = prevalencia_padronizada(sub, ["geracao", "sexo"], idades="todas")
        partes.append(t.assign(idade_grupo=faixa))
    t = pd.concat(partes, ignore_index=True)
    return t[(t["n"] >= 300) & t["prev"].notna()]


# ---------------------------------------------------------------- sensibilidades e veredito
CENARIOS = {
    "base": lambda f: f,
    "só 18 a 21 anos": lambda f: f[f["idade"] <= 21],
    "sem 2024 (filtro novo e celular)": lambda f: f[f["ano"] != 2024],
    "geração Z só por telefone fixo": lambda f: f[(f["geracao"] != "geracao_z") | (f["modo_coleta"] == "fixo")],
    "sem 2020 e 2021 (pandemia)": lambda f: f[~f["ano"].isin([2020, 2021])],
    "sem escolaridade estimada": lambda f: f[~f["escolaridade_estimada"]],
}
# a mesma base, sem a padronizacao por idade: mostra o efeito da D14
SEM_PADRONIZAR = "base sem padronizar pela idade (antes da D14)"


def sensibilidades(f):
    linhas = []
    cenarios = [(n, c, True) for n, c in CENARIOS.items()] + [(SEM_PADRONIZAR, CENARIOS["base"], False)]
    for nome, filtro, padronizar in cenarios:
        sub = filtro(f)
        for recorte, cond in [("total", None), ("homens", "masculino"), ("mulheres", "feminino")]:
            s = jovens(sub if cond is None else sub[sub["sexo"] == cond])
            tab = prevalencia_padronizada(s, ["geracao"]) if padronizar else prevalencia(s, ["geracao"])
            idades = tab["idades_padrao"].iloc[0] if padronizar else "sem padronizar"
            for _, r in diferencas(tab).iterrows():
                linhas.append(dict(cenario=nome, recorte=recorte, comparacao=r["comparacao"],
                                   diferenca_pp=r["diferenca_pp"], ic_inf=r["ic_inf"], ic_sup=r["ic_sup"],
                                   significativa=r["significativa"], idades_padrao=idades))
    return pd.DataFrame(linhas)


def veredito(f):
    """Aplica os criterios de refutacao do README (a, b, c) na comparacao geracao Z x millennials, com as
    prevalencias padronizadas pela idade (D14). As colunas *_sem_padronizar guardam a leitura anterior."""
    def queda(t):
        return t[(t["comparacao"] == "geracao_z - millennials")]
    caiu = lambda r: r["significativa"] and r["diferenca_pp"] < 0
    estrela = lambda r: "*" if r["significativa"] else ""

    def criterios(padronizar):
        j = jovens(f)
        tab = prevalencia_padronizada(j, ["geracao"]) if padronizar else prevalencia(j, ["geracao"])
        tot = queda(diferencas(tab)).iloc[0]
        sexo = queda(diferencas(por_grupo(f, "sexo", padronizar=padronizar), chaves=("sexo",)))
        esc = queda(diferencas(por_grupo(f, "escolaridade", padronizar=padronizar), chaves=("escolaridade",)))
        a = (caiu(tot), f"{tot['diferenca_pp']:+.1f} p.p. (IC {tot['ic_inf']:+.1f} a {tot['ic_sup']:+.1f})")
        b = (all(caiu(r) for _, r in sexo.iterrows()) and all(caiu(r) for _, r in esc.iterrows()),
             "; ".join([f"{r['sexo']} {r['diferenca_pp']:+.1f}{estrela(r)}" for _, r in sexo.iterrows()]
                       + [f"{r['escolaridade']} {r['diferenca_pp']:+.1f}{estrela(r)}" for _, r in esc.iterrows()]))
        return a, b

    (a, ra), (b, rb) = criterios(True)
    (a0, ra0), (b0, rb0) = criterios(False)
    dd = p3_periodo(f)[1].iloc[0]
    c = bool(dd["significativa"] and dd["diferenca_das_diferencas_pp"] < 0)
    rc = (f"diferença das diferenças: {dd['diferenca_das_diferencas_pp']:+.1f} p.p. "
          f"(IC {dd['ic_inf']:+.1f} a {dd['ic_sup']:+.1f})")
    return pd.DataFrame([
        dict(criterio="(a) a prevalência aos 18-24 diminui da geração Z para os millennials",
             resultado=ra, atende_hipotese=a, resultado_sem_padronizar=ra0, atendia_sem_padronizar=a0),
        dict(criterio="(b) a queda ocorre nos dois sexos e nas três faixas de escolaridade",
             resultado=rb, atende_hipotese=b, resultado_sem_padronizar=rb0, atendia_sem_padronizar=b0),
        dict(criterio="(c) a mudança dos jovens é mais favorável que a dos adultos de 35-44 no mesmo período",
             resultado=rc, atende_hipotese=c, resultado_sem_padronizar="", atendia_sem_padronizar=pd.NA),
    ]).astype({"atendia_sem_padronizar": "boolean"})


# ---------------------------------------------------------------- correlatos (notebook 06)
# Candidatas: (coluna da bronze, regra que define "tem a caracteristica", edicoes em que a pergunta existe).
# Codigos conferidos no dicionario oficial; codigos 777/888 (nao sabe, nao quis responder) ficam fora.
_A = list(range(2010, 2025))
CANDIDATAS = {
    "fuma cigarro": ("fumante", lambda x: x == "1", _A, "provável"),
    "usa cigarro eletrônico": ("eletronico", lambda x: x == "1", [2019, 2020, 2021, 2023, 2024], "provável"),
    "diagnóstico de depressão": ("depressao", lambda x: x == "1", [2020, 2021, 2023, 2024], "provável"),
    "trabalha": ("q47", lambda x: x == "1", _A, "provável"),
    "solteiro(a)": ("civil", lambda x: x == "1", _A, "provável"),
    "12+ anos de estudo": ("fesc", lambda x: x == "3", _A, "provável"),
    "tem plano de saúde": ("q88", lambda x: x.isin(["1", "2"]), _A, "provável"),
    "tela no lazer 3h+/dia": ("tempo_tela_total", lambda x: x == "1", list(range(2016, 2025)), "provável"),
    "dorme menos de 7h": ("r701_hh", lambda x: pd.to_numeric(x, errors="coerce") < 7, [2024], "provável"),
    "dificuldade p/ dormir (quase sempre)": ("r703", lambda x: x.isin(["4", "5"]), [2024], "provável"),
    "estuda (curso/escola)": ("q52", lambda x: x == "1", _A, "provável"),
    "preta ou parda (x branca)": ("q69", lambda x: x.isin(["2", "4"]), _A, "incerta"),
    "refrigerante 5x+/semana": ("refritl5", lambda x: x == "1", _A, "incerta"),
    "TV 3h+/dia": ("tv_d_3", lambda x: x == "1", _A, "incerta"),
    "saúde autoavaliada ruim": ("saruim", lambda x: x == "1", _A, "incerta"),
    "fisicamente inativo": ("inativo", lambda x: x == "1", list(range(2010, 2024)), "incerta"),
    "excesso de peso": ("excpeso_i", lambda x: x == "1", _A, "improvável"),
    "obesidade": ("obesid_i", lambda x: x == "1", _A, "improvável"),
    "frutas e hortaliças regulares": ("flvreg", lambda x: x == "1", _A, "improvável"),
    "hipertensão": ("hart", lambda x: x == "1", _A, "improvável"),
    "diabetes": ("diab", lambda x: x == "1", _A, "improvável"),
}
EXCLUIR = {"q52": ["888"], "civil": ["888"], "q88": ["888"], "q69": ["3", "5", "80", "777", "888"]}


def colunas_candidatas():
    return sorted({c for c, *_ in CANDIDATAS.values()})


def montar_exposicoes(d):
    """d: silver + colunas brutas das candidatas. Devolve d com uma coluna 0/1/NaN por candidata."""
    out = d.copy()
    for nome, (col, regra, anos, _) in CANDIDATAS.items():
        x = d[col].fillna("").astype(str).str.strip()
        valido = (x != "") & d["ano"].isin(anos) & ~x.isin(EXCLUIR.get(col, []))
        out[nome] = np.where(valido, regra(x).astype(float), np.nan)
    return out


def associacao(d, var):
    """Diferenca de consumo abusivo entre quem tem e quem nao tem a caracteristica, ajustada por sexo e edicao
    (media das diferencas dentro de cada estrato sexo x edicao, ponderada pelo peso do estrato)."""
    s = d[["ano", "sexo", "alcabu", "peso_norm", var]].dropna(subset=[var])
    num = var_ = tot = 0.0
    for _, g in s.groupby(["ano", "sexo"]):
        e, n = g[g[var] == 1], g[g[var] == 0]
        if len(e) < 20 or len(n) < 20:
            continue
        p = lambda h: np.average(h["alcabu"], weights=h["peso_norm"])
        ne = lambda h: h["peso_norm"].sum() ** 2 / (h["peso_norm"] ** 2).sum()
        p1, p0, W = p(e), p(n), g["peso_norm"].sum()
        num += W * (p1 - p0)
        var_ += W ** 2 * (p1 * (1 - p1) / ne(e) + p0 * (1 - p0) / ne(n))
        tot += W
    if tot == 0:
        return None
    dif, ep = num / tot * 100, np.sqrt(var_) / tot * 100
    w = s["peso_norm"]
    return dict(n=len(s), pct_expostos=np.average(s[var], weights=w) * 100,
                prev_expostos=np.average(s.loc[s[var] == 1, "alcabu"], weights=w[s[var] == 1]) * 100,
                prev_nao_expostos=np.average(s.loc[s[var] == 0, "alcabu"], weights=w[s[var] == 0]) * 100,
                dif_ajustada=dif, ic_inf=dif - 1.96 * ep, ic_sup=dif + 1.96 * ep)


def tabela_correlatos(d):
    jov = d[d["faixa_etaria"] == "18 a 24"]
    linhas = []
    for nome, (col, _, anos, expect) in CANDIDATAS.items():
        r = associacao(jov, nome)
        ra = associacao(d, nome)
        if r is None:
            continue
        r.update(variavel=nome, coluna_origem=col, edicoes=f"{min(anos)}-{max(anos)}" if len(anos) > 1 else str(anos[0]),
                 expectativa=expect, dif_adultos=ra["dif_ajustada"] if ra else np.nan)
        linhas.append(r)
    t = pd.DataFrame(linhas)
    t["significativa"] = (t["ic_inf"] > 0) | (t["ic_sup"] < 0)
    # correcao de Bonferroni: com 21 testes, exige-se IC de 99,76% para o mesmo nivel de 5%
    z_b = 3.04
    ep = (t["ic_sup"] - t["ic_inf"]) / (2 * 1.96)
    t["significativa_bonferroni"] = (t["dif_ajustada"].abs() > z_b * ep)
    cols = ["variavel", "expectativa", "coluna_origem", "edicoes", "n", "pct_expostos", "prev_expostos",
            "prev_nao_expostos", "dif_ajustada", "ic_inf", "ic_sup", "significativa", "significativa_bonferroni", "dif_adultos"]
    return t[cols].sort_values("dif_ajustada", ascending=False).reset_index(drop=True)
