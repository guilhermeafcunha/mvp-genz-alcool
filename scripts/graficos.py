"""
graficos.py: figuras da apresentacao (notebooks 05 e 06). Cada funcao recebe tabelas ja calculadas e salva um PNG.

Cores com funcao fixa: geracoes em tons de azul (mais escuro = mais nova), homens azul, mulheres laranja,
contexto cinza. Toda figura traz a identidade tambem no rotulo (legivel em preto e branco).
"""
import os

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd

COR_GER = {"millennials": "#b8b6ad", "zillennials": "#7fa7d9", "geracao_z": "#1f5fae"}
ROT_GER = {"millennials": "Millennials\n(1986-92)", "zillennials": "Zillennials\n(1993-98)", "geracao_z": "Geração Z\n(1999-2006)"}
COR_SEXO = {"masculino": "#2a78d6", "feminino": "#eb6834"}
CINZA = "#b8b6ad"
ORDEM_GER = ["millennials", "zillennials", "geracao_z"]
FONTE = "Fonte: Vigitel 2010-2024 (Ministério da Saúde). Prevalências ponderadas; IC 95% aproximado."
# figuras que comparam geracoes: prevalencias padronizadas pela idade simples (D14)
FONTE_PADR = FONTE.replace("ponderadas;", "ponderadas e padronizadas pela idade (18 a 24, peso igual por ano de idade);")

plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "axes.titlesize": 12, "font.size": 10})


def _salvar(fig, pasta, nome, fonte=FONTE):
    fig.text(0.01, -0.02, fonte, fontsize=7.5, color="#666", ha="left", va="top")
    fig.tight_layout()
    fig.savefig(os.path.join(pasta, nome), bbox_inches="tight", dpi=150)
    plt.show()


def pct(ax, eixo="y"):
    (ax.yaxis if eixo == "y" else ax.xaxis).set_major_formatter(mtick.PercentFormatter(decimals=0))


# ---------------------------------------------------------------- contexto
def serie_faixa_etaria(t, pasta):
    """t: prevalencia por ano e faixa_etaria (colunas ano, faixa_etaria, prev, ic_inf, ic_sup)."""
    fig, ax = plt.subplots(figsize=(10, 4.6))
    fim = t[t["ano"] == t["ano"].max()].set_index("faixa_etaria")["prev"].sort_values()
    pos, ultimo = {}, -99
    for fx, v in fim.items():          # afasta rotulos que ficariam a menos de 1,3 p.p.
        ultimo = max(v, ultimo + 1.3)
        pos[fx] = ultimo
    for fx in sorted(t["faixa_etaria"].unique()):
        r = t[t["faixa_etaria"] == fx].sort_values("ano")
        destaque = {"18 a 24": "#1f5fae", "35 a 44": "#eb6834"}.get(fx)
        ax.plot(r["ano"], r["prev"], marker="o" if destaque else None, ms=4, lw=2.2 if destaque else 1,
                color=destaque or CINZA, zorder=3 if destaque else 2)
        if destaque:
            ax.fill_between(r["ano"], r["ic_inf"], r["ic_sup"], color=destaque, alpha=0.12, lw=0)
        ax.text(r["ano"].iloc[-1] + 0.25, pos[fx], fx, va="center", fontsize=8,
                color=destaque or "#777", fontweight="bold" if destaque else None)
    ax.axvspan(2021.5, 2022.5, color="#eeeeee", zorder=0)
    ax.text(2022, ax.get_ylim()[1] * 0.97, "sem\n2022", ha="center", va="top", fontsize=8, color="#666")
    ax.axvline(2022.5, color="#999", ls=":", lw=1)
    ax.text(2022.6, 1, "entra o celular", fontsize=8, color="#666")
    ax.set_xticks(range(2010, 2025, 2))
    ax.set_xlim(2009.5, 2025.8)
    ax.set_ylim(0, None)
    pct(ax)
    ax.set_title("Consumo abusivo de álcool por faixa etária, capitais, 2010-2024")
    _salvar(fig, pasta, "f01_serie_faixa_etaria.png")


def cobertura_geracoes(cob, pasta):
    """cob: crosstab ano x geracao (jovens 18-24), com coluna celular_%."""
    fig, ax = plt.subplots(figsize=(10, 4.2))
    base = np.zeros(len(cob))
    for g in ORDEM_GER:
        v = cob[g].values if g in cob else np.zeros(len(cob))
        ax.bar(cob["ano"], v, bottom=base, color=COR_GER[g], label=ROT_GER[g].replace("\n", " "), width=0.8)
        base += v
    ax2 = ax.twinx()
    ax2.plot(cob["ano"], cob["celular_%"], color="#eb6834", marker="o", lw=1.5)
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("% de entrevistas por celular", color="#eb6834")
    ax2.spines["top"].set_visible(False)
    ax.set_xticks(cob["ano"])
    ax.set_ylabel("jovens de 18 a 24 entrevistados")
    ax.legend(frameon=False, loc="upper center", fontsize=8)
    ax.set_title("Quem observamos: jovens entrevistados por geração e edição")
    _salvar(fig, pasta, "f02_cobertura_geracoes.png", "Fonte: Vigitel 2010-2024. Contagem de entrevistas (sem peso).")


def modo_coleta(t, pasta):
    """t: prevalencia por grupo ('todas as idades'/'18 a 24') e modo (fixo/celular), ano 2023."""
    fig, ax = plt.subplots(figsize=(7, 4))
    grupos = ["todas as idades", "18 a 24"]
    x = np.arange(2)
    for i, (modo, cor) in enumerate([("fixo", CINZA), ("celular", "#1f5fae")]):
        r = t[t["modo"] == modo].set_index("grupo").loc[grupos]
        ax.bar(x + (i - 0.5) * 0.38, r["prev"], 0.38, color=cor, label=f"entrevista por {modo}")
        ax.errorbar(x + (i - 0.5) * 0.38, r["prev"], yerr=[r["prev"] - r["ic_inf"], r["ic_sup"] - r["prev"]],
                    fmt="none", ecolor="black", capsize=3, lw=1)
        for xi, v in zip(x + (i - 0.5) * 0.38, r["prev"]):
            ax.text(xi, v / 2, f"{v:.1f}%", ha="center", color="white", fontweight="bold")
    ax.set_xticks(x, ["Todas as idades", "Jovens de 18 a 24"])
    pct(ax)
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("Mesmo ano (2023), resposta diferente:\nquem atende o celular declara mais consumo abusivo")
    _salvar(fig, pasta, "f12_modo_coleta_2023.png")


# ---------------------------------------------------------------- P1 e P4
def idade_por_geracao(t, pasta):
    """t: an.por_idade (geracao, idade, prev, peso_pct). Mostra por que a comparacao precisa ser padronizada (D14)."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
    for g in ORDEM_GER:
        r = t[t["geracao"] == g].sort_values("idade")
        a1.plot(r["idade"], r["prev"], marker="o", lw=2.2, color=COR_GER[g], label=ROT_GER[g].replace("\n", " "))
        a2.plot(r["idade"], r["peso_pct"], marker="o", lw=2.2, color=COR_GER[g])
    a1.set_title("Consumo abusivo por idade: sobe com a idade", fontsize=11)
    a2.set_title("Peso de cada idade na geração (sem padronizar)", fontsize=11)
    for ax in (a1, a2):
        ax.set_xticks(range(18, 25))
        ax.set_xlabel("idade")
        ax.set_ylim(0, None)
        pct(ax)
    a2.axhline(100 / 7, color="black", ls=":", lw=1)
    a2.text(24.15, 100 / 7, "padrão\n(1/7)", fontsize=8, va="center")
    a1.legend(frameon=False, fontsize=8)
    fig.suptitle("Por que padronizar: os millennials foram observados mais velhos, a geração Z mais nova",
                 fontweight="bold")
    _salvar(fig, pasta, "f03a_idade_por_geracao.png")


def p1_geracoes(p1, d1, pasta):
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    x = np.arange(3)
    ax.bar(x, p1["prev"], 0.6, color=[COR_GER[g] for g in p1["geracao"]])
    ax.errorbar(x, p1["prev"], yerr=1.96 * p1["ep"], fmt="none", ecolor="black", capsize=4)
    ax.scatter(x, p1["prev_bruta"], marker="o", facecolors="white", edgecolors="black", zorder=4, s=36,
               label="sem padronizar pela idade (leitura anterior)")
    ax.scatter(x, p1["prev_padr_escolaridade"], marker="D", color="black", zorder=4, s=25,
               label="padronizada também pela escolaridade dos millennials")
    for xi, v in zip(x, p1["prev"]):
        ax.text(xi, 2, f"{v:.1f}%", ha="center", color="white", fontweight="bold", fontsize=11)
    dz = d1[d1["comparacao"] == "geracao_z - millennials"].iloc[0]
    ax.annotate(f"{dz['diferenca_pp']:+.1f} p.p.\n(IC {dz['ic_inf']:+.1f} a {dz['ic_sup']:+.1f})", xy=(2, p1["prev"].iloc[2] + 2.2),
                ha="center", fontsize=9, color="#1f5fae", fontweight="bold")
    ax.set_xticks(x, [ROT_GER[g] for g in p1["geracao"]])
    ax.set_ylim(0, 30)
    pct(ax)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.set_ylim(0, 33)
    ax.set_title("P1. Na mesma idade, a geração Z não bebe em excesso menos que os millennials")
    _salvar(fig, pasta, "f03_p1_geracoes.png", FONTE_PADR)


def convergencia_sexos(p4, pasta):
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    x = np.arange(3)
    for sexo, cor in COR_SEXO.items():
        r = p4[p4["sexo"] == sexo].set_index("geracao").loc[ORDEM_GER]
        ax.plot(x, r["prev"], marker="o", ms=8, lw=2.5, color=cor)
        ax.fill_between(x, r["ic_inf"], r["ic_sup"], color=cor, alpha=0.12, lw=0)
        for xi, v in zip(x, r["prev"]):
            ax.text(xi, v + (1.6 if sexo == "masculino" else -2.6), f"{v:.1f}%", ha="center", color=cor, fontweight="bold")
        ax.text(2.12, r["prev"].iloc[-1], "Homens" if sexo == "masculino" else "Mulheres", color=cor, va="center", fontweight="bold")
    h = p4[p4["sexo"] == "masculino"].set_index("geracao").loc[ORDEM_GER, "prev"].values
    m = p4[p4["sexo"] == "feminino"].set_index("geracao").loc[ORDEM_GER, "prev"].values
    for xi in (0, 2):
        ax.annotate("", xy=(xi, m[xi] + 0.6), xytext=(xi, h[xi] - 0.6), arrowprops=dict(arrowstyle="<->", color="#666"))
        ax.text(xi - 0.08, (h[xi] + m[xi]) / 2, f"{h[xi] - m[xi]:.0f} p.p.", ha="right", fontsize=9, color="#666")
    ax.set_xticks(x, [ROT_GER[g] for g in ORDEM_GER])
    ax.set_xlim(-0.5, 2.6)
    ax.set_ylim(0, 36)
    pct(ax)
    ax.set_title("P4. Os sexos estão convergindo: homens caem, mulheres sobem")
    _salvar(fig, pasta, "f04_p4_convergencia_sexos.png", FONTE_PADR)


def decomposicao(dec, pasta):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.3), sharey=True)
    for ax, sexo in zip(axes, ["masculino", "feminino"]):
        t = dec[dec["sexo"] == sexo].set_index("geracao").loc[ORDEM_GER]
        x = np.arange(3)
        b1 = ax.bar(x - 0.2, t["bebe_mensal"], 0.4, color=CINZA, label="bebem ao menos 1x/mês")
        b2 = ax.bar(x + 0.2, t["abusivo_entre_quem_bebe"], 0.4, color=COR_SEXO[sexo], label="exageram, entre os que bebem")
        for barras in (b1, b2):
            for b in barras:
                ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1, f"{b.get_height():.0f}%", ha="center", fontsize=8)
        ax.set_xticks(x, ["Millennials", "Zillennials", "Geração Z"])
        ax.set_title("Homens" if sexo == "masculino" else "Mulheres", color=COR_SEXO[sexo])
        ax.set_ylim(0, 80)
        pct(ax)
        ax.legend(frameon=False, fontsize=8, loc="upper right")
    fig.suptitle("Por que muda: entre os homens que bebem, menos exageram; mais mulheres bebem", fontweight="bold")
    _salvar(fig, pasta, "f05_decomposicao.png", FONTE_PADR)


# ---------------------------------------------------------------- P2, P3
def p2_heatmap(p2, d2, pasta, ordem_esc):
    tab = p2.pivot(index="escolaridade", columns="geracao", values="prev").loc[ordem_esc, ORDEM_GER]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    im = ax.imshow(tab.values, cmap="Blues", vmin=10, vmax=30, aspect="auto")
    for i in range(tab.shape[0]):
        for j in range(tab.shape[1]):
            v = tab.values[i, j]
            ax.text(j, i, f"{v:.1f}%", ha="center", va="center", color="white" if v > 22 else "black", fontweight="bold")
    dz = d2[d2["comparacao"] == "geracao_z - millennials"].set_index("escolaridade").loc[ordem_esc]
    for i, (_, r) in enumerate(dz.iterrows()):
        ax.text(2.62, i, f"{r['diferenca_pp']:+.1f} p.p.{'' if r['significativa'] else ' (n.s.)'}", va="center", fontsize=9)
    ax.text(2.62, -0.62, "Ger. Z − Millennials", fontsize=8, color="#666")
    ax.set_xticks(range(3), [ROT_GER[g].replace("\n", " ") for g in ORDEM_GER], fontsize=8)
    ax.set_yticks(range(len(ordem_esc)), ordem_esc)
    ax.set_xlim(-0.5, 3.4)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("P2. Por escolaridade: nenhuma diferença significativa\nentre as gerações (18-24 anos)", pad=18)
    _salvar(fig, pasta, "f06_p2_escolaridade.png", FONTE_PADR + " n.s. = intervalo inclui o zero.")


def p3_periodo(p3a, pasta):
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    y = np.arange(len(p3a))
    cores = ["#1f5fae", "#eb6834"]
    ax.barh(y, p3a["diferenca_pp"], color=cores, height=0.5)
    ax.errorbar(p3a["diferenca_pp"], y, xerr=[p3a["diferenca_pp"] - p3a["ic_inf"], p3a["ic_sup"] - p3a["diferenca_pp"]],
                fmt="none", ecolor="black", capsize=4)
    for yi, r in zip(y, p3a.itertuples()):
        x = r.ic_sup + 0.3 if r.diferenca_pp > 0 else r.ic_inf - 0.3
        ax.text(x, yi, f"{r.periodo_millennials:.1f}% → {r.periodo_geracao_z:.1f}%\n({r.diferenca_pp:+.1f} p.p.)",
                ha="left" if r.diferenca_pp > 0 else "right", va="center", fontsize=9)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks(y, ["Jovens de 18 a 24\n(millennials → geração Z)", "Adultos de 35 a 44\n(mesmas edições)"])
    ax.set_xlim(-9, 9)
    ax.set_xlabel("variação entre 2010-2016 e 2017-2024 (p.p.)")
    ax.set_title("P3. No mesmo período, os adultos subiram mais que os jovens")
    _salvar(fig, pasta, "f07_p3_jovens_x_adultos.png", FONTE_PADR)


def p3_envelhecimento(p3b, pasta):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    ordem_idade = ["18-24", "25-29", "30-34", "35-39"]
    for ax, sexo in zip(axes, ["masculino", "feminino"]):
        for g in ORDEM_GER:
            r = p3b[(p3b["sexo"] == sexo) & (p3b["geracao"] == g)].copy()
            r["pos"] = r["idade_grupo"].astype(str).map({k: i for i, k in enumerate(ordem_idade)})
            r = r.sort_values("pos")
            ax.errorbar(r["pos"], r["prev"], yerr=1.96 * r["ep"], marker="o", ms=7, lw=2.2, capsize=3,
                        color=COR_GER[g], label=ROT_GER[g].replace("\n", " "))
        ax.set_xticks(range(4), ordem_idade)
        ax.set_xlabel("idade")
        ax.set_title("Homens" if sexo == "masculino" else "Mulheres", color=COR_SEXO[sexo])
        pct(ax)
    axes[0].legend(frameon=False, fontsize=8, loc="lower right")
    fig.suptitle("P3. Ao envelhecer, os zillennials seguem a curva dos millennials (homens) ou ficam acima (mulheres)",
                 fontweight="bold")
    _salvar(fig, pasta, "f08_p3_envelhecimento.png",
            FONTE_PADR.replace("(18 a 24, ", "(dentro de cada faixa, ") + " Grupos com 300 ou mais entrevistas.")


# ---------------------------------------------------------------- P5
FONTE_P5 = FONTE_PADR.replace("pela idade (18 a 24, peso igual por ano de idade)",
                              "pela idade em três faixas (18-19, 20-21, 22-24)")
NOME_CURTO = {"Campo Grande": "C. Grande", "Distrito Federal": "Brasília", "Belo Horizonte": "B. Horizonte",
              "Porto Alegre": "P. Alegre", "Rio de Janeiro": "Rio de Janeiro", "Florianópolis": "Florianópolis"}
GRADE_UF = {"RR": (2, 0), "AP": (4, 0), "AC": (0, 1), "AM": (1, 1), "PA": (3, 1), "MA": (4, 1), "CE": (5, 1),
            "RN": (6, 1), "RO": (1, 2), "MT": (2, 2), "TO": (3, 2), "PI": (4, 2), "PE": (5, 2), "PB": (6, 2),
            "MS": (2, 3), "GO": (3, 3), "DF": (4, 3), "BA": (5, 3), "AL": (6, 3), "SP": (3, 4), "MG": (4, 4),
            "ES": (5, 4), "SE": (6, 4), "PR": (3, 5), "RJ": (4, 5), "SC": (3, 6), "RS": (2, 6)}


def p5_mapa(p5, uf_de, pasta):
    """Mapa em grade: cada quadrado e uma capital, cor = diferenca geracao Z - millennials."""
    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    cmap = matplotlib.colormaps["RdBu"]
    norm = matplotlib.colors.TwoSlopeNorm(vmin=-10, vcenter=0, vmax=10)
    for r in p5.itertuples():
        uf = uf_de[r.capital]
        c, l = GRADE_UF[uf]
        cor = cmap(norm(-r.diferenca_pp))     # azul = queda (menos consumo abusivo), vermelho = alta
        ax.add_patch(plt.Rectangle((c, -l), 0.94, 0.94, color=cor, ec="black" if r.significativa else "white",
                                   lw=2.5 if r.significativa else 1))
        claro = abs(r.diferenca_pp) < 5
        ax.text(c + 0.47, -l + 0.66, uf, ha="center", fontweight="bold", fontsize=11, color="black" if claro else "white")
        ax.text(c + 0.47, -l + 0.42, NOME_CURTO.get(r.capital, r.capital), ha="center", fontsize=6.5,
                color="black" if claro else "white")
        ax.text(c + 0.47, -l + 0.16, f"{r.diferenca_pp:+.1f}", ha="center", fontsize=10, color="black" if claro else "white")
    ax.set_xlim(-0.2, 7.2)
    ax.set_ylim(-6.2, 1.1)
    ax.set_aspect("equal")
    ax.axis("off")
    sm = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.TwoSlopeNorm(vmin=-10, vcenter=0, vmax=10), cmap="RdBu_r")
    cb = fig.colorbar(sm, ax=ax, shrink=0.6, pad=0.02)
    cb.set_label("geração Z − millennials (p.p.)\nazul = menos consumo abusivo")
    ax.set_title("P5. Diferença entre gerações por capital\n(borda preta = diferença fora da margem de erro)")
    _salvar(fig, pasta, "f09_p5_mapa_capitais.png", FONTE_P5)


def p5_forest(p5, pasta):
    fig, ax = plt.subplots(figsize=(8, 9))
    y = np.arange(len(p5))
    cores = np.where(p5["significativa"], "#1f5fae", CINZA)
    ax.hlines(y, p5["ic_inf"], p5["ic_sup"], color=cores, lw=2)
    ax.scatter(p5["diferenca_pp"], y, color=cores, zorder=3)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks(y, [f"{c} ({r})" for c, r in zip(p5["capital"], p5["regiao"])], fontsize=8)
    ax.set_xlabel("diferença geração Z − millennials (p.p.) e IC 95%")
    ax.set_title("P5. Capitais: diferença e margem de erro (azul = fora da margem)")
    _salvar(fig, pasta, "f10_p5_capitais.png", FONTE_P5)


# ---------------------------------------------------------------- sensibilidades e correlatos
def sensibilidades(sens, pasta):
    s = sens[sens["comparacao"] == "geracao_z - millennials"]
    cenarios = list(dict.fromkeys(s["cenario"]))
    fig, ax = plt.subplots(figsize=(9, 4.8))
    y = np.arange(len(cenarios))
    for k, (rec, cor) in enumerate([("total", "#555555"), ("homens", COR_SEXO["masculino"]), ("mulheres", COR_SEXO["feminino"])]):
        r = s[s["recorte"] == rec].set_index("cenario").loc[cenarios]
        yy = y + (k - 1) * 0.22
        ax.hlines(yy, r["ic_inf"], r["ic_sup"], color=cor, lw=2)
        ax.scatter(r["diferenca_pp"], yy, color=cor, zorder=3, label=rec)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks(y, cenarios)
    ax.invert_yaxis()
    ax.set_xlabel("geração Z − millennials (p.p.) e IC 95%")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    ax.set_title("Robustez: as mulheres sobem em quase todos os cenários; a queda dos homens\nperde a significância em três (última linha: a leitura sem padronizar)")
    _salvar(fig, pasta, "f11_sensibilidades.png", FONTE_PADR.replace("(18 a 24, ", "(idades comuns às gerações, "))


def correlatos(c, pasta):
    """c: tabela de associacoes (variavel, dif_ajustada, ic_inf, ic_sup, dif_adultos, grupo)."""
    c = c.sort_values("dif_ajustada")
    fig, ax = plt.subplots(figsize=(9.5, 8))
    y = np.arange(len(c))
    sig = (c["ic_inf"] > 0) | (c["ic_sup"] < 0)
    cores = np.where(~sig, CINZA, np.where(c["dif_ajustada"] > 0, "#c0392b", "#1f5fae"))
    ax.hlines(y, c["ic_inf"], c["ic_sup"], color=cores, lw=2)
    ax.scatter(c["dif_ajustada"], y, color=cores, zorder=3, s=40, label="jovens de 18 a 24")
    ax.scatter(c["dif_adultos"], y, marker="|", color="black", s=120, zorder=4, label="todos os adultos")
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks(y, [f"{v}  ({e:.0f}%)" for v, e in zip(c["variavel"], c["pct_expostos"])], fontsize=8.5)
    ax.set_xlabel("diferença no consumo abusivo: quem tem a característica − quem não tem (p.p.),\najustada por sexo e edição")
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    ax.set_title("Correlatos do consumo abusivo entre jovens de 18 a 24\n(vermelho = mais consumo, azul = menos, cinza = inconclusivo)")
    _salvar(fig, pasta, "f13_correlatos.png",
            FONTE + " Entre parênteses, % de jovens com a característica. Associação não é causa.")


def correlatos_destaque(t, pasta):
    """t: prevalencia de alcabu por geracao em expostos/nao expostos para 3-4 variaveis de destaque."""
    vars_ = list(dict.fromkeys(t["variavel"]))
    fig, axes = plt.subplots(1, len(vars_), figsize=(3.3 * len(vars_), 4), sharey=True)
    for ax, v in zip(np.atleast_1d(axes), vars_):
        r = t[t["variavel"] == v]
        x = np.arange(2)
        vals = [r.loc[r["exposto"] == 0, "prev"].iloc[0], r.loc[r["exposto"] == 1, "prev"].iloc[0]]
        ax.bar(x, vals, color=[CINZA, "#c0392b"], width=0.6)
        for xi, val in zip(x, vals):
            ax.text(xi, val + 1, f"{val:.0f}%", ha="center", fontweight="bold")
        ax.set_xticks(x, ["não", "sim"])
        ax.set_title(v, fontsize=10)
        pct(ax)
    fig.suptitle("Consumo abusivo entre jovens de 18 a 24, por característica", fontweight="bold")
    _salvar(fig, pasta, "f14_correlatos_destaque.png",
            "Fonte: Vigitel (edições em que cada pergunta existe). Prevalências ponderadas, sem ajuste; o ajuste por sexo e edição está na f13.")
