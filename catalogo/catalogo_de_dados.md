# Catálogo de dados

Gerado por `scripts/gerar_catalogo.py` a partir das próprias tabelas (tipo, domínio e nulos calculados nos dados).
Fonte: Vigitel Brasil 2006-2024, base harmonizada (Ministério da Saúde, 24/08/2026; ZIP `vigitel-2006-2024-peso-rake-csv.zip`). A bronze (`bronze_vigitel`) é cópia fiel do CSV, com as 486 colunas como texto e `linha_origem`;
o dicionário das colunas originais é o oficial (`docs_fonte/dicionario-vigitel-2006-2024.xlsx`).

## silver_vigitel

**Linhagem:** Origem: Vigitel Brasil 2006-2024, base harmonizada (Ministério da Saúde, 24/08/2026; ZIP `vigitel-2006-2024-peso-rake-csv.zip`). Bronze (cópia fiel, 486 colunas) para silver pelo notebook 02 (`etl.montar_silver`, regras S1 a S11; testes em `etl.validar_silver`).
**Linhas:** 615.877

| Atributo | Tipo | Descrição | Domínio | Obrigatoriedade |
|---|---|---|---|---|
| `entrevista_id` | texto | Identificador da entrevista: edição + número da linha no arquivo original (S2, D10). | 615877 valores distintos (ex.: 2010-217341; 2010-217342; 2010-217343) | Obrigatório (sem nulos) |
| `linha_origem` | inteiro | Número do registro no CSV original (1 = primeira linha após o cabeçalho); rastreabilidade até a fonte. | 217341 a 833217 | Obrigatório (sem nulos) |
| `chave_oficial` | texto | Coluna `chave` do Ministério, só como referência: existe em 2014-2023 e se repete (D10). | 295968 valores distintos (ex.: 00210121030; 00210141029; 00210211030) | Admite nulo (38.0% das linhas) |
| `ano` | inteiro | Edição do Vigitel (2010 a 2024, sem 2022) (S1, D1, D5). | 2010 a 2024 | Obrigatório (sem nulos) |
| `edicao_pandemia` | booleano | Verdadeiro em 2020 e 2021 (S3, D11). | {False, True} | Obrigatório (sem nulos) |
| `edicao_filtro_novo` | booleano | Verdadeiro em 2024, quando o filtro do bloco de álcool passou a ser 'bebeu nos últimos 12 meses' (S3, D13). | {False, True} | Obrigatório (sem nulos) |
| `cidade_cod` | inteiro | Código da capital no dicionário oficial (1 a 27). | 1 a 27 | Obrigatório (sem nulos) |
| `capital` | texto | Nome da capital ou Distrito Federal. | 27 valores distintos (ex.: Aracaju; Belo Horizonte; Belém) | Obrigatório (sem nulos) |
| `uf` | texto | Sigla da unidade da federação. | 27 valores distintos (ex.: AC; AL; AM) | Obrigatório (sem nulos) |
| `regiao` | texto | Região derivada da capital (S4, D12); a coluna regiao original não é usada. | {Centro-Oeste; Nordeste; Norte; Sudeste; Sul} | Obrigatório (sem nulos) |
| `modo_coleta` | texto | Telefone da entrevista: fixo (todas até 2021) ou celular (S5). | {celular; fixo} | Obrigatório (sem nulos) |
| `idade` | inteiro | Idade declarada (q6). | 18 a 120 | Obrigatório (sem nulos) |
| `faixa_etaria_cod` | inteiro | Faixa etária oficial (fet), código 1 a 6. | {1; 2; 3; 4; 5; 6} | Obrigatório (sem nulos) |
| `faixa_etaria` | texto | Faixa etária oficial com rótulo (18 a 24 ... 65 e mais). | {18 a 24; 25 a 34; 35 a 44; 45 a 54; 55 a 64; 65 e mais} | Obrigatório (sem nulos) |
| `sexo` | texto | Sexo (q7). | {feminino; masculino} | Obrigatório (sem nulos) |
| `ano_nascimento` | inteiro | Ano da edição menos a idade (erro de até 1 ano) (S7, D2). | 1890 a 2006 | Obrigatório (sem nulos) |
| `geracao` | texto | Geração pelo ano de nascimento: millennials (1986-1992), zillennials (1993-1998), geracao_z (1999-2006) ou outra (S7, D2). | {geracao_z; millennials; outra; zillennials} | Obrigatório (sem nulos) |
| `anos_estudo` | numérico | Anos de estudo calculados pelo Ministério (q8_anos). | 0 a 22 | Obrigatório (sem nulos) |
| `escolaridade_cod` | inteiro | Faixa de escolaridade oficial (fesc), código 1 a 3. | {1; 2; 3} | Obrigatório (sem nulos) |
| `escolaridade` | texto | Faixa de escolaridade com rótulo (0 a 8, 9 a 11, 12 anos e mais) (S8). | {0 a 8 anos; 12 anos e mais; 9 a 11 anos} | Obrigatório (sem nulos) |
| `escolaridade_estimada` | booleano | Verdadeiro quando q8a = 777 ou 888 e a escolaridade foi estimada pelo Ministério (S8, D8). | {False, True} | Obrigatório (sem nulos) |
| `alcabu` | inteiro | Indicador oficial de consumo abusivo (5+ doses homem, 4+ mulher, numa ocasião, últimos 30 dias); 0 para quem não bebe (S9). | {0; 1} | Obrigatório (sem nulos) |
| `frequencia_cod` | inteiro | Frequência de consumo (q36): 1 a 4 semanal ou mais, 5 menos de 1 dia por semana, 6 menos de 1 dia por mês; nulo fora do bloco de álcool. | {1; 2; 3; 4; 5; 6} | Admite nulo (64.3% das linhas) |
| `bebe_mensal` | inteiro | 1 se bebe pelo menos uma vez por mês (q36 de 1 a 5); definição própria do trabalho (S10, D6). | {0; 1} | Obrigatório (sem nulos) |
| `costuma_beber_q35` | inteiro | 1 se respondeu 'sim' à q35 ('costuma beber?'); nulo em 2024, quando a pergunta não existe; só conferência (S10, D6). | {0; 1} | Admite nulo (4.4% das linhas) |
| `respondeu_doses` | inteiro | 1 se respondeu q37 ou q38 (perguntas de doses); usado para conferir o pulo do questionário. | {0; 1} | Obrigatório (sem nulos) |
| `peso` | numérico | Peso amostral oficial (pesorake2025). | 30826.6 a 3.68576e+07 | Obrigatório (sem nulos) |
| `peso_norm` | numérico | Peso normalizado para somar 1 em cada edição (S11, D4). | 4.66194e-07 a 0.00126821 | Obrigatório (sem nulos) |

## fato_entrevista

**Linhagem:** Origem: silver_vigitel. Notebook 03 (`etl.montar_gold`): chaves das dimensões; sem agregação (mesmo grão da silver).
**Linhas:** 615.877

| Atributo | Tipo | Descrição | Domínio | Obrigatoriedade |
|---|---|---|---|---|
| `entrevista_id` | texto | Identificador da entrevista: edição + número da linha no arquivo original (S2, D10). | 615877 valores distintos (ex.: 2010-217341; 2010-217342; 2010-217343) | Obrigatório (sem nulos) |
| `edicao_sk` | inteiro | Chave da edição (igual ao ano). | 2010 a 2024 | Obrigatório (sem nulos) |
| `capital_sk` | inteiro | Chave da capital (código oficial 1 a 27). | 1 a 27 | Obrigatório (sem nulos) |
| `geracao_sk` | inteiro | Chave da geração (1 millennials, 2 zillennials, 3 geração Z, 9 outra). | {1; 2; 3; 9} | Obrigatório (sem nulos) |
| `escolaridade_sk` | inteiro | Chave da escolaridade (1 a 3). | {1; 2; 3} | Obrigatório (sem nulos) |
| `faixa_etaria_sk` | inteiro | Chave da faixa etária (1 a 6). | {1; 2; 3; 4; 5; 6} | Obrigatório (sem nulos) |
| `sexo_sk` | inteiro | Chave do sexo (1 masculino, 2 feminino). | {1; 2} | Obrigatório (sem nulos) |
| `idade` | inteiro | Idade declarada (q6). | 18 a 120 | Obrigatório (sem nulos) |
| `ano_nascimento` | inteiro | Ano da edição menos a idade (erro de até 1 ano) (S7, D2). | 1890 a 2006 | Obrigatório (sem nulos) |
| `modo_coleta` | texto | Telefone da entrevista: fixo (todas até 2021) ou celular (S5). | {celular; fixo} | Obrigatório (sem nulos) |
| `escolaridade_estimada` | booleano | Verdadeiro quando q8a = 777 ou 888 e a escolaridade foi estimada pelo Ministério (S8, D8). | {False, True} | Obrigatório (sem nulos) |
| `alcabu` | inteiro | Indicador oficial de consumo abusivo (5+ doses homem, 4+ mulher, numa ocasião, últimos 30 dias); 0 para quem não bebe (S9). | {0; 1} | Obrigatório (sem nulos) |
| `bebe_mensal` | inteiro | 1 se bebe pelo menos uma vez por mês (q36 de 1 a 5); definição própria do trabalho (S10, D6). | {0; 1} | Obrigatório (sem nulos) |
| `costuma_beber_q35` | inteiro | 1 se respondeu 'sim' à q35 ('costuma beber?'); nulo em 2024, quando a pergunta não existe; só conferência (S10, D6). | {0; 1} | Admite nulo (4.4% das linhas) |
| `peso` | numérico | Peso amostral oficial (pesorake2025). | 30826.6 a 3.68576e+07 | Obrigatório (sem nulos) |
| `peso_norm` | numérico | Peso normalizado para somar 1 em cada edição (S11, D4). | 4.66194e-07 a 0.00126821 | Obrigatório (sem nulos) |
| `linha_origem` | inteiro | Número do registro no CSV original (1 = primeira linha após o cabeçalho); rastreabilidade até a fonte. | 217341 a 833217 | Obrigatório (sem nulos) |

## dim_edicao

**Linhagem:** Origem: silver_vigitel (ano, modo de coleta). Notebook 03.
**Linhas:** 14

| Atributo | Tipo | Descrição | Domínio | Obrigatoriedade |
|---|---|---|---|---|
| `edicao_sk` | inteiro | Chave da edição (igual ao ano). | 2010 a 2024 | Obrigatório (sem nulos) |
| `ano` | inteiro | Edição do Vigitel (2010 a 2024, sem 2022) (S1, D1, D5). | 2010 a 2024 | Obrigatório (sem nulos) |
| `entrevistas` | inteiro | Número de entrevistas da edição de 2010 em diante. | 21690 a 54339 | Obrigatório (sem nulos) |
| `pct_celular` | numérico | Percentual de entrevistas por celular na edição. | {0.0; 49.9; 90.4} | Obrigatório (sem nulos) |
| `pandemia` | booleano | Verdadeiro em 2020 e 2021. | {False, True} | Obrigatório (sem nulos) |
| `filtro_bloco_alcool` | texto | Filtro de entrada do bloco de álcool na edição. | {bebeu nos ultimos 12 meses (R502); costuma beber (q35)} | Obrigatório (sem nulos) |

## dim_capital

**Linhagem:** Origem: dicionário oficial (códigos 1 a 27) e divisão regional do IBGE. Notebook 03 (D12).
**Linhas:** 27

| Atributo | Tipo | Descrição | Domínio | Obrigatoriedade |
|---|---|---|---|---|
| `capital_sk` | inteiro | Chave da capital (código oficial 1 a 27). | 1 a 27 | Obrigatório (sem nulos) |
| `capital` | texto | Nome da capital ou Distrito Federal. | 27 valores distintos (ex.: Aracaju; Belo Horizonte; Belém) | Obrigatório (sem nulos) |
| `uf` | texto | Sigla da unidade da federação. | 27 valores distintos (ex.: AC; AL; AM) | Obrigatório (sem nulos) |
| `regiao` | texto | Região derivada da capital (S4, D12); a coluna regiao original não é usada. | {Centro-Oeste; Nordeste; Norte; Sudeste; Sul} | Obrigatório (sem nulos) |

## dim_geracao

**Linhagem:** Origem: convenção do trabalho (D2), baseada no Pew Research Center (DIMOCK, 2019). Notebook 03.
**Linhas:** 4

| Atributo | Tipo | Descrição | Domínio | Obrigatoriedade |
|---|---|---|---|---|
| `geracao_sk` | inteiro | Chave da geração (1 millennials, 2 zillennials, 3 geração Z, 9 outra). | {1; 2; 3; 9} | Obrigatório (sem nulos) |
| `geracao` | texto | Geração pelo ano de nascimento: millennials (1986-1992), zillennials (1993-1998), geracao_z (1999-2006) ou outra (S7, D2). | {geracao_z; millennials; outra; zillennials} | Obrigatório (sem nulos) |
| `nascimento_inicio` | inteiro | Primeiro ano de nascimento da geração. | {1986; 1993; 1999} | Admite nulo (25.0% das linhas) |
| `nascimento_fim` | inteiro | Último ano de nascimento da geração. | {1992; 1998; 2006} | Admite nulo (25.0% das linhas) |

## dim_escolaridade

**Linhagem:** Origem: dicionário oficial (fesc). Notebook 03.
**Linhas:** 3

| Atributo | Tipo | Descrição | Domínio | Obrigatoriedade |
|---|---|---|---|---|
| `escolaridade_sk` | inteiro | Chave da escolaridade (1 a 3). | {1; 2; 3} | Obrigatório (sem nulos) |
| `escolaridade` | texto | Faixa de escolaridade com rótulo (0 a 8, 9 a 11, 12 anos e mais) (S8). | {0 a 8 anos; 12 anos e mais; 9 a 11 anos} | Obrigatório (sem nulos) |

## dim_faixa_etaria

**Linhagem:** Origem: dicionário oficial (fet). Notebook 03.
**Linhas:** 6

| Atributo | Tipo | Descrição | Domínio | Obrigatoriedade |
|---|---|---|---|---|
| `faixa_etaria_sk` | inteiro | Chave da faixa etária (1 a 6). | {1; 2; 3; 4; 5; 6} | Obrigatório (sem nulos) |
| `faixa_etaria` | texto | Faixa etária oficial com rótulo (18 a 24 ... 65 e mais). | {18 a 24; 25 a 34; 35 a 44; 45 a 54; 55 a 64; 65 e mais} | Obrigatório (sem nulos) |

## dim_sexo

**Linhagem:** Origem: dicionário oficial (q7). Notebook 03.
**Linhas:** 2

| Atributo | Tipo | Descrição | Domínio | Obrigatoriedade |
|---|---|---|---|---|
| `sexo_sk` | inteiro | Chave do sexo (1 masculino, 2 feminino). | {1; 2} | Obrigatório (sem nulos) |
| `sexo` | texto | Sexo (q7). | {feminino; masculino} | Obrigatório (sem nulos) |
