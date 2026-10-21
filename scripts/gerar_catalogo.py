"""
gerar_catalogo.py: gera o Catalogo de Dados (catalogo/catalogo_de_dados.md e .csv) a partir das proprias tabelas.

Tipo, dominio (minimo e maximo ou categorias) e obrigatoriedade (percentual de nulos) sao calculados nos dados;
descricao e linhagem vem dos dicionarios abaixo.

Uso (raiz do repositorio):  python scripts/gerar_catalogo.py dados/raw/vigitel-2006-2024-peso-rake-csv.zip
"""
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vigitel_etl as etl

RAIZ = Path(__file__).resolve().parent.parent
FONTE = "Vigitel Brasil 2006-2024, base harmonizada (Ministério da Saúde, 24/08/2026; ZIP `vigitel-2006-2024-peso-rake-csv.zip`)"

LINHAGEM = {
    "silver_vigitel": f"Origem: {FONTE}. Bronze (cópia fiel, 486 colunas) para silver pelo notebook 02 (`etl.montar_silver`, regras S1 a S11; testes em `etl.validar_silver`).",
    "fato_entrevista": "Origem: silver_vigitel. Notebook 03 (`etl.montar_gold`): chaves das dimensões; sem agregação (mesmo grão da silver).",
    "dim_edicao": "Origem: silver_vigitel (ano, modo de coleta). Notebook 03.",
    "dim_capital": "Origem: dicionário oficial (códigos 1 a 27) e divisão regional do IBGE. Notebook 03 (D12).",
    "dim_geracao": "Origem: convenção do trabalho (D2), baseada no Pew Research Center (DIMOCK, 2019). Notebook 03.",
    "dim_escolaridade": "Origem: dicionário oficial (fesc). Notebook 03.",
    "dim_faixa_etaria": "Origem: dicionário oficial (fet). Notebook 03.",
    "dim_sexo": "Origem: dicionário oficial (q7). Notebook 03.",
}

DESC = {
    "entrevista_id": "Identificador da entrevista: edição + número da linha no arquivo original (S2, D10).",
    "linha_origem": "Número do registro no CSV original (1 = primeira linha após o cabeçalho); rastreabilidade até a fonte.",
    "chave_oficial": "Coluna `chave` do Ministério, só como referência: existe em 2014-2023 e se repete (D10).",
    "ano": "Edição do Vigitel (2010 a 2024, sem 2022) (S1, D1, D5).",
    "edicao_pandemia": "Verdadeiro em 2020 e 2021 (S3, D11).",
    "edicao_filtro_novo": "Verdadeiro em 2024, quando o filtro do bloco de álcool passou a ser 'bebeu nos últimos 12 meses' (S3, D13).",
    "cidade_cod": "Código da capital no dicionário oficial (1 a 27).",
    "capital": "Nome da capital ou Distrito Federal.",
    "uf": "Sigla da unidade da federação.",
    "regiao": "Região derivada da capital (S4, D12); a coluna regiao original não é usada.",
    "modo_coleta": "Telefone da entrevista: fixo (todas até 2021) ou celular (S5).",
    "idade": "Idade declarada (q6).",
    "faixa_etaria_cod": "Faixa etária oficial (fet), código 1 a 6.",
    "faixa_etaria": "Faixa etária oficial com rótulo (18 a 24 ... 65 e mais).",
    "sexo": "Sexo (q7).",
    "ano_nascimento": "Ano da edição menos a idade (erro de até 1 ano) (S7, D2).",
    "geracao": "Geração pelo ano de nascimento: millennials (1986-1992), zillennials (1993-1998), geracao_z (1999-2006) ou outra (S7, D2).",
    "anos_estudo": "Anos de estudo calculados pelo Ministério (q8_anos).",
    "escolaridade_cod": "Faixa de escolaridade oficial (fesc), código 1 a 3.",
    "escolaridade": "Faixa de escolaridade com rótulo (0 a 8, 9 a 11, 12 anos e mais) (S8).",
    "escolaridade_estimada": "Verdadeiro quando q8a = 777 ou 888 e a escolaridade foi estimada pelo Ministério (S8, D8).",
    "alcabu": "Indicador oficial de consumo abusivo (5+ doses homem, 4+ mulher, numa ocasião, últimos 30 dias); 0 para quem não bebe (S9).",
    "frequencia_cod": "Frequência de consumo (q36): 1 a 4 semanal ou mais, 5 menos de 1 dia por semana, 6 menos de 1 dia por mês; nulo fora do bloco de álcool.",
    "bebe_mensal": "1 se bebe pelo menos uma vez por mês (q36 de 1 a 5); definição própria do trabalho (S10, D6).",
    "costuma_beber_q35": "1 se respondeu 'sim' à q35 ('costuma beber?'); nulo em 2024, quando a pergunta não existe; só conferência (S10, D6).",
    "respondeu_doses": "1 se respondeu q37 ou q38 (perguntas de doses); usado para conferir o pulo do questionário.",
    "peso": "Peso amostral oficial (pesorake2025).",
    "peso_norm": "Peso normalizado para somar 1 em cada edição (S11, D4).",
    "edicao_sk": "Chave da edição (igual ao ano).",
    "capital_sk": "Chave da capital (código oficial 1 a 27).",
    "geracao_sk": "Chave da geração (1 millennials, 2 zillennials, 3 geração Z, 9 outra).",
    "escolaridade_sk": "Chave da escolaridade (1 a 3).",
    "faixa_etaria_sk": "Chave da faixa etária (1 a 6).",
    "sexo_sk": "Chave do sexo (1 masculino, 2 feminino).",
    "entrevistas": "Número de entrevistas da edição de 2010 em diante.",
    "pct_celular": "Percentual de entrevistas por celular na edição.",
    "pandemia": "Verdadeiro em 2020 e 2021.",
    "filtro_bloco_alcool": "Filtro de entrada do bloco de álcool na edição.",
    "nascimento_inicio": "Primeiro ano de nascimento da geração.",
    "nascimento_fim": "Último ano de nascimento da geração.",
}


def dominio(col):
    s = col.dropna()
    if s.empty:
        return "(vazio)"
    if pd.api.types.is_bool_dtype(s):
        return "{False, True}"
    if pd.api.types.is_numeric_dtype(s) and s.nunique() > 12:
        return f"{s.min():g} a {s.max():g}"
    v = sorted(s.astype(str).unique())
    return "{" + "; ".join(v) + "}" if len(v) <= 12 else f"{len(v)} valores distintos (ex.: {'; '.join(v[:3])})"


def tipo(col):
    n = str(col.dtype).lower()
    return ("booleano" if n.startswith("bool") else "inteiro" if n.startswith("int")
            else "numérico" if n.startswith("float") else "texto")


def main():
    caminho = Path(sys.argv[1])
    with zipfile.ZipFile(caminho) as z, z.open(etl.nome_csv(caminho)) as f:
        bruto = pd.read_csv(f, encoding=etl.ENCODING, dtype=str, keep_default_na=False, na_values=[""],
                            usecols=[c for c in etl.COLUNAS_ANALISE if c != "linha_origem"])
    bruto.insert(0, "linha_origem", range(1, len(bruto) + 1))
    silver = etl.montar_silver(bruto)
    etl.validar_silver(bruto, silver)
    tabelas = {"silver_vigitel": silver, **etl.montar_gold(silver)}
    linhas = []
    for nome, df in tabelas.items():
        for c in df.columns:
            nulos = df[c].isna().mean() * 100
            linhas.append(dict(tabela=nome, atributo=c, tipo=tipo(df[c]), descricao=DESC.get(c, ""),
                               dominio=dominio(df[c]),
                               obrigatoriedade="Obrigatório (sem nulos)" if nulos == 0 else f"Admite nulo ({nulos:.1f}% das linhas)",
                               linhagem=LINHAGEM[nome]))
    cat = pd.DataFrame(linhas)
    faltando = cat.loc[cat["descricao"] == "", "atributo"].unique()
    assert len(faltando) == 0, f"atributos sem descrição: {faltando}"
    (RAIZ / "catalogo").mkdir(exist_ok=True)
    cat.to_csv(RAIZ / "catalogo" / "catalogo_de_dados.csv", index=False, encoding="utf-8-sig")
    md = ["# Catálogo de dados", "",
          "Gerado por `scripts/gerar_catalogo.py` a partir das próprias tabelas (tipo, domínio e nulos calculados nos dados).",
          f"Fonte: {FONTE}. A bronze (`bronze_vigitel`) é cópia fiel do CSV, com as 486 colunas como texto e `linha_origem`;",
          "o dicionário das colunas originais é o oficial (`docs_fonte/dicionario-vigitel-2006-2024.xlsx`).", ""]
    for nome, d in cat.groupby("tabela", sort=False):
        md += [f"## {nome}", "", f"**Linhagem:** {d['linhagem'].iloc[0]}", f"**Linhas:** {len(tabelas[nome]):,}".replace(",", "."), "",
               "| Atributo | Tipo | Descrição | Domínio | Obrigatoriedade |", "|---|---|---|---|---|"]
        md += [f"| `{r.atributo}` | {r.tipo} | {r.descricao} | {r.dominio} | {r.obrigatoriedade} |" for r in d.itertuples()]
        md.append("")
    (RAIZ / "catalogo" / "catalogo_de_dados.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Catálogo: {len(cat)} atributos em {cat['tabela'].nunique()} tabelas")


if __name__ == "__main__":
    main()
