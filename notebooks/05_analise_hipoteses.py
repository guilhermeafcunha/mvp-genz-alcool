# Databricks notebook source
# MAGIC %md
# MAGIC # 05. Análise: perguntas P1 a P5 e teste da hipótese
# MAGIC
# MAGIC **Etapa do roteiro:** 3.5 (b) Solução do problema. Os dados vêm do **modelo estrela** (fato + dimensões); as
# MAGIC contas estão em `scripts/analise.py` e as figuras em `scripts/graficos.py` (numeradas na ordem da apresentação,
# MAGIC `f01` a `f12`, mais a `f03a` da padronização pela idade; as `f13` e `f14` são do notebook 06).
# MAGIC
# MAGIC **Hipótese (README, versão 2 do objetivo):** na mesma idade (18 a 24 anos), a prevalência de consumo abusivo
# MAGIC de álcool diminui de uma geração para a seguinte (millennials → zillennials → geração Z), nos dois sexos e em
# MAGIC todas as faixas de escolaridade, e a diferença não se explica por uma tendência geral da população.
# MAGIC
# MAGIC **Método:** prevalências ponderadas pelo peso normalizado por edição (D4), com intervalo de 95% aproximado pelo
# MAGIC *n* efetivo de Kish. Uma diferença é **significativa** quando o seu intervalo de 95% não inclui o zero. Como o
# MAGIC desenho amostral completo (estratos) não é usado, os intervalos são aproximados.
# MAGIC
# MAGIC **Padronização pela idade (D14):** a janela 2010-2024 faz os millennials aparecerem sobretudo aos 22-24 anos e a
# MAGIC geração Z sobretudo aos 18-20, e o consumo abusivo sobe com a idade. Por isso, toda comparação entre gerações usa a
# MAGIC prevalência **padronizada pela idade simples**: a média das prevalências de cada idade de 18 a 24, com peso igual
# MAGIC por ano de idade, sempre sobre as mesmas idades para as gerações comparadas. A prevalência sem padronizar aparece
# MAGIC ao lado (`prev_bruta`) para mostrar o tamanho do viés; ela era a leitura da versão anterior desta análise.

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

# MAGIC %md
# MAGIC ## Dados: o modelo estrela, desnormalizado para a análise

# COMMAND ----------

f = spark.sql(f"""
    SELECT f.entrevista_id, e.ano, c.capital, c.uf, c.regiao, g.geracao, fe.faixa_etaria, x.sexo, s.escolaridade,
           f.idade, f.modo_coleta, f.escolaridade_estimada, f.alcabu, f.bebe_mensal, f.costuma_beber_q35,
           f.peso_norm
    FROM {T('fato_entrevista')} f
    JOIN {T('dim_edicao')} e ON e.edicao_sk = f.edicao_sk
    JOIN {T('dim_capital')} c ON c.capital_sk = f.capital_sk
    JOIN {T('dim_geracao')} g ON g.geracao_sk = f.geracao_sk
    JOIN {T('dim_faixa_etaria')} fe ON fe.faixa_etaria_sk = f.faixa_etaria_sk
    JOIN {T('dim_sexo')} x ON x.sexo_sk = f.sexo_sk
    JOIN {T('dim_escolaridade')} s ON s.escolaridade_sk = f.escolaridade_sk""").toPandas()
f["escolaridade_estimada"] = f["escolaridade_estimada"].astype(bool)
print(f"{len(f):,} entrevistas de 2010 em diante | jovens das três gerações: {len(an.jovens(f)):,}")
resultados = {}

# COMMAND ----------

# MAGIC %md
# MAGIC ## Contexto: a série histórica, quem observamos e o efeito do celular

# COMMAND ----------

serie = an.prevalencia(f, ["ano", "faixa_etaria"])
resultados["res_serie_faixa_etaria"] = serie
gr.serie_faixa_etaria(serie, FIG_DIR)

jov_todos = f[f["faixa_etaria"] == "18 a 24"]
cob = pd.crosstab(jov_todos["ano"], jov_todos["geracao"]).reset_index()
cob["celular_%"] = cob["ano"].map(f.groupby("ano")["modo_coleta"].apply(lambda m: (m == "celular").mean() * 100))
gr.cobertura_geracoes(cob, FIG_DIR)

m23 = f[f["ano"] == 2023]
modo = pd.concat([an.prevalencia(m23, ["modo_coleta"]).assign(grupo="todas as idades"),
                  an.prevalencia(m23[m23["faixa_etaria"] == "18 a 24"], ["modo_coleta"]).assign(grupo="18 a 24")])
modo = modo.rename(columns={"modo_coleta": "modo"})
resultados["res_modo_coleta_2023"] = modo
display(modo.round(1))
gr.modo_coleta(modo, FIG_DIR)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Por que padronizar pela idade (D14)
# MAGIC Prevalência por idade simples e participação de cada idade no peso de cada geração. Sem padronizar, os millennials
# MAGIC pesam mais nas idades em que se bebe mais (22-24) e a geração Z, nas idades em que se bebe menos (18-20).

# COMMAND ----------

idade = an.por_idade(f)
resultados["res_p1_por_idade"] = idade
display(idade.pivot(index="idade", columns="geracao", values="prev").round(1))
display(idade.pivot(index="idade", columns="geracao", values="peso_pct").round(1))
gr.idade_por_geracao(idade, FIG_DIR)

# COMMAND ----------

# MAGIC %md
# MAGIC ## P1. Quanto cada geração difere da anterior, aos 18-24 anos?
# MAGIC `prev` é a prevalência padronizada pela idade (estimativa principal); `prev_bruta`, a sem padronizar;
# MAGIC `prev_padr_escolaridade` recalcula a padronizada com a composição de escolaridade dos millennials (D7): se for
# MAGIC parecida com `prev`, a diferença não vem da mudança de escolaridade. As diferenças incluem cada geração contra a
# MAGIC anterior (millennials → zillennials → geração Z) e a geração Z contra os millennials.

# COMMAND ----------

p1 = an.p1(f)
d1 = an.diferencas(p1, sucessivas=True)
resultados["res_p1_geracao"] = p1
resultados["res_p1_diferencas"] = d1
display(p1[["geracao", "n", "prev", "ic_inf", "ic_sup", "prev_bruta", "prev_padr_escolaridade"]].round(1))
display(d1.round(1))
gr.p1_geracoes(p1, d1, FIG_DIR)

# COMMAND ----------

# MAGIC %md
# MAGIC ## P1 (desdobramento, D6). Bebem menos vezes ou exageram menos?
# MAGIC Consumo abusivo = bebe ao menos 1x por mês × abusivo entre quem bebe ao menos 1x por mês. `costuma_beber_q35`
# MAGIC é só conferência, até 2023. Todas as partes padronizadas pela idade (D14).

# COMMAND ----------

dec = an.decomposicao(f, por=("geracao", "sexo"))
resultados["res_p1_decomposicao"] = dec
display(dec.round(1))
gr.decomposicao(dec, FIG_DIR)

# COMMAND ----------

# MAGIC %md
# MAGIC ## P2. A diferença ocorre em todas as faixas de escolaridade?

# COMMAND ----------

p2 = an.por_grupo(f, "escolaridade")
d2 = an.diferencas(p2, chaves=("escolaridade",), sucessivas=True)
d2_sens = an.diferencas(an.por_grupo(f, "escolaridade", ~f["escolaridade_estimada"]), chaves=("escolaridade",))
d2 = d2.merge(d2_sens[["escolaridade", "comparacao", "diferenca_pp"]].rename(
    columns={"diferenca_pp": "diferenca_sem_estimada_pp"}), on=["escolaridade", "comparacao"])
resultados["res_p2_escolaridade"] = p2
resultados["res_p2_diferencas"] = d2
display(d2.round(1))
display(an.decomposicao(f, por=("geracao", "escolaridade")).round(1))
gr.p2_heatmap(p2, d2, FIG_DIR, an.ORDEM_ESC)

# COMMAND ----------

# MAGIC %md
# MAGIC ## P3. Efeito de geração ou de época?
# MAGIC (a) A mudança dos jovens (millennials → geração Z) contra a dos adultos de 35 a 44 anos nas mesmas edições, com o
# MAGIC intervalo de 95% da diferença das diferenças. Os dois grupos padronizados pela idade simples (D14).
# MAGIC (b) Cada geração acompanhada ao envelhecer (pseudo-coorte), com pelo menos 300 entrevistas por grupo e padronização
# MAGIC pela idade dentro de cada faixa; a geração que ainda não passou por todas as idades da faixa fica de fora.

# COMMAND ----------

p3a, dd = an.p3_periodo(f)
p3b = an.p3_envelhecimento(f)
resultados["res_p3_periodo"] = p3a
resultados["res_p3_diferenca_das_diferencas"] = dd
resultados["res_p3_envelhecimento"] = p3b
display(p3a.round(1))
display(dd.round(1))
display(p3b.pivot(index=["sexo", "idade_grupo"], columns="geracao", values="prev").round(1))
gr.p3_periodo(p3a, FIG_DIR)
gr.p3_envelhecimento(p3b, FIG_DIR)

# COMMAND ----------

# MAGIC %md
# MAGIC ## P4. A diferença é igual entre homens e mulheres?

# COMMAND ----------

p4 = an.por_grupo(f, "sexo")
d4 = an.diferencas(p4, chaves=("sexo",), sucessivas=True)
resultados["res_p4_sexo"] = p4
resultados["res_p4_diferencas"] = d4
display(d4.round(1))
gr.convergencia_sexos(p4, FIG_DIR)

# COMMAND ----------

# MAGIC %md
# MAGIC ## P5. Capitais em primeiro plano, região como apoio (D9)
# MAGIC Diferença geração Z − millennials aos 18-24 anos. Quando a capital é inconclusiva (intervalo inclui o zero), a
# MAGIC leitura usa a região. Nas capitais, a padronização pela idade usa três faixas (18-19, 20-21, 22-24), porque há
# MAGIC células de idade simples com só 15 entrevistas; nas regiões, idade simples (D14). Com 27 capitais, cerca de uma
# MAGIC diferença "significativa" é esperada só pelo acaso.

# COMMAND ----------

p5, p5_reg = an.p5(f)
resultados["res_p5_capitais"] = p5
resultados["res_p5_regioes"] = p5_reg
display(p5_reg.round(1))
display(p5[["capital", "regiao", "diferenca_pp", "ic_inf", "ic_sup", "significativa", "regiao_diferenca_pp", "leitura"]].round(1))
uf_de = dict(zip(f["capital"], f["uf"]))
gr.p5_mapa(p5, uf_de, FIG_DIR)
gr.p5_forest(p5, FIG_DIR)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sensibilidades (D2, D7, D8, D11, D13, D14) e veredito
# MAGIC Cada cenário é padronizado pelas idades comuns às gerações comparadas (coluna `idades_padrao`). A última linha
# MAGIC repete a base sem padronizar pela idade, para mostrar o efeito da D14. O veredito aplica os critérios (a), (b) e (c)
# MAGIC do README às prevalências padronizadas e guarda, ao lado, a leitura sem padronizar.

# COMMAND ----------

sens = an.sensibilidades(f)
resultados["res_sensibilidades"] = sens
display(sens[sens["comparacao"] == "geracao_z - millennials"]
        .pivot(index="cenario", columns="recorte", values="diferenca_pp").round(1))
display(sens[sens["comparacao"] == "geracao_z - millennials"]
        .pivot(index="cenario", columns="recorte", values="significativa"))
gr.sensibilidades(sens, FIG_DIR)

ver = an.veredito(f)
resultados["res_veredito"] = ver
display(ver)

# COMMAND ----------

for nome, pdf in resultados.items():
    pdf = pdf.copy()
    pdf.columns = [str(c) for c in pdf.columns]
    for c in pdf.columns:
        if str(pdf[c].dtype) == "category":
            pdf[c] = pdf[c].astype(str)
    etl.gravar_tabela(spark, pdf.reset_index(drop=True), T(nome))
print(f"{len(resultados)} tabelas de resultado gravadas; figuras em {FIG_DIR}")
