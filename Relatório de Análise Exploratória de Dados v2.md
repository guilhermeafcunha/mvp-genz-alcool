# Relatório de Análise Exploratória de Dados v2

**Relatório consolidado da exploração da base, antes das decisões de tratamento.** Documento companheiro do notebook `MVP_GenZ_Alcool_01_AED_v2.ipynb`.

**Projeto:** MVP Geração Z e consumo de álcool (PSP8, Prof. André Luiz Marques Serrano, EPR/FT/UnB)

**Autor:** Guilherme Augusto Fontes Cunha

**Versão:** v2, 16 out. 2026. Substitui a v1, que existia só como notebook. Incorpora os comentários do autor registrados em `PENDENCIAS_AED.md` (itens 1 a 5) e os achados novos da leitura dos questionários. O histórico está na seção 9.

**Etapa do ciclo:** 1 (busca) e 2 (coleta e análise exploratória). **Nenhuma decisão de tratamento foi tomada**: a seção 6 lista as decisões em aberto, para o autor.

**Arquivos de referência:** notebook `notebooks/aed/MVP_GenZ_Alcool_01_AED_v2.ipynb` (com as saídas), tabelas em `notebooks/aed/saidas_aed_v2/`, figuras em `figuras_relatorio_v2/`, documentação oficial em `docs_fonte/`.

**Como ler as notas:** toda variável citada recebe um número sobrescrito fixo, o mesmo do notebook (q37 é sempre ¹ e q38 é sempre ²). A redação oficial de cada pergunta e a definição de cada variável derivada estão no Apêndice A.

---

## 1. Resumo

| Tema | Achado | Consequência |
|---|---|---|
| Fonte | Vigitel 2006-2024 harmonizado: 833.217 entrevistas, 486 colunas, 18 edições (não existe 2022) | É a base ideal: oficial, num arquivo só, com peso e indicador prontos |
| Indicador | `alcabu`¹⁸ reproduzido em 100% dos registros a partir de `q37`¹/`q38`² (e `q37b`¹¹/`q38b`¹² em 2006-2008) | Pode ser usado como está |
| Vazios | Quase todos são pulo de questionário ou variável inexistente no ano; faltante de verdade só em 346 respostas de `q8a`⁷ (2006) | Os vazios não ameaçam a análise; as sete colunas da análise têm 0% de vazio |
| Pergunta de doses | Mudou de "mais do que 5/4 doses" para "5/4 ou mais" **em 2010**; a base guarda 2009 já na coluna nova | 2010 é o primeiro ano comparável, como o README previu; 2009 não pode ser juntado a 2010+ |
| Modo de coleta | 2010 só fixo; 2024 com mais de 90% celular. Em 2023, celular 27,0% contra fixo 15,5% no mesmo ano | A comparação 2010 x 2024 mistura comportamento e método |
| Filtro de 2024 | `q35`³ ("costuma beber?") foi substituída por `R501`¹³/`R502`¹⁴ ("bebeu nos últimos 12 meses?") | Mais gente entra no bloco de álcool em 2024; tende a elevar a prevalência |
| Pesos | Escala muda em 2010; de 2010 em diante a soma acompanha o número de entrevistas | Prevalência dentro do ano é correta; juntar anos exige normalizar |
| Amostra | Jovens: 7.364 (2010) para 2.294 (2024); cerca de 85 por capital em 2024 | P5 com 2024 isolado não tem precisão |
| Prévia | Jovens: 21,9% (2010), 25,9% (2019), 22,7% (2024). Jovens mulheres sobem de 14,8% para 25,4%; jovens homens caem de 28,9% para 19,8% só em 2024 | A premissa do README (queda entre jovens) não aparece; o movimento forte é por sexo |

---

## 2. O que foi feito até agora

| Data | Passo |
|---|---|
| 16/10/2026 | Busca da fonte; download do ZIP oficial, do dicionário, das orientações, da nota metodológica e dos relatórios |
| 16/10/2026 | Notebook AED v1: leitura fiel, conferência, vazios, dicionário, chave, cobertura, modo de coleta, idade, escolaridade, medida, pesos, prévia e decisões em aberto (D1 a D12) |
| 16/10/2026 | Revisão do autor; comentários acumulados em `PENDENCIAS_AED.md` (itens 1 a 5) |
| 16/10/2026 | Leitura dos questionários dos relatórios 2008, 2009, 2010, 2023 e 2006-2024 para as notas das variáveis; achados novos (seções 4.2 e 4.3) |
| 16/10/2026 | Notebook AED v2 e este relatório |

---

## 3. A fonte e o arquivo

| Item | Valor |
|---|---|
| Fonte | Ministério da Saúde, SVSA/DAENT, *Vigitel Brasil 2006-2024*, base harmonizada |
| Página | <https://svs.aids.gov.br/daent/cgdnt/vigitel/> |
| Arquivo | `vigitel-2006-2024-peso-rake-csv.zip` (87.121.523 bytes), com um CSV de 577 MB |
| SHA-256 do ZIP | `40139996d11deb2f52730c90f14e2df4bf5e53aba3cf1848fce391c93ff77993` |
| Publicação | 24/08/2026 (versão sem rótulos, para evitar divergência com o dicionário) |
| Coleta | 16/10/2026 |
| Licença do portal | Creative Commons Atribuição-SemDerivações 3.0 |
| Peso indicado pela orientação oficial | `pesorake2025`¹⁹ (Censo 2022 para 2010-2024) |

**Por que esta base.** É a fonte oficial do indicador de consumo abusivo citado no README; junta todas as edições num arquivo com um dicionário único; traz o peso recalibrado pelo Censo 2022 e o indicador `alcabu`¹⁸ pronto.

**Como o arquivo foi lido.** O CSV mistura codificações (1.555 linhas não são UTF-8, todas em campos de texto livre) e tem 408 linhas com campos entre aspas e vírgulas dentro. A leitura usa `latin-1`, respeita as aspas e mantém todas as linhas, com um recorte de 21 colunas (as das perguntas e as de controle). Os campos de texto livre ficam fora: não respondem às perguntas e podem conter informação pessoal.

---

## 4. Achados da exploração

### 4.1 Vazios: três categorias (item 1 das pendências)

![Vazios em três categorias](figuras_relatorio_v2/aed2_fig1_vazios_tres_categorias.png)

A v1 pintava de preto qualquer vazio. A v2 separa:

| Categoria | Significado | Onde aparece | Volume |
|---|---|---|---|
| Pulo legítimo | A pergunta não se aplicava | `q36`⁴ (quem não bebe), `q37`¹/`q38`² (outro sexo ou bebe menos de uma vez por mês), versões antigas | 534 mil em `q36`⁴; 556 mil em `q37`¹; 588 mil em `q38`² |
| Inexistente no ano | A variável não existia ou não foi publicada | `chave` (2006-2013 e 2024), `tipo_fone` (até 2021), `regiao` (2012), `q35`³ (2024), versões antigas fora do seu período | coluna inteira vazia no ano |
| Faltante de verdade | Devia haver resposta e não há | `q8a`⁷ em 2006 | 346 respostas (0,04% da base) |

As sete colunas que respondem às perguntas (`ano`, `cidade`, `fet`¹⁵, `q7`⁶, `fesc`¹⁷, `alcabu`¹⁸, `pesorake2025`¹⁹) têm 0% de vazio em todos os anos.

**O que o mapa não mostra:**
1. **Imputação:** `fesc`¹⁷ não tem vazios porque o Ministério imputa a escolaridade de quem respondeu 777 ou 888 em `q8a`⁷ (8.170 casos, 1%).
2. **Vazio tratado como "não":** o `alcabu`¹⁸ vale 0 quando `q37`¹/`q38`² estão vazias. A conferência mostra que, em todas as edições (inclusive 2024), 100% de quem bebe pelo menos uma vez por mês respondeu e ninguém fora do filtro respondeu. O vazio é pulo, e o 0 está correto. Em 2024 não dá para saber por que alguém ficou fora do bloco (nunca bebeu, não bebeu em 12 meses ou recusou), porque `R501`¹³ e `R502`¹⁴ não foram publicadas.
3. **Não resposta à pesquisa:** quem não atendeu o telefone não aparece. O peso corrige sexo, idade e escolaridade, mas não diferenças de comportamento; pode ser MNAR e só pode ser declarado.

### 4.2 A medida de consumo e o questionário (achado novo da v2)

**A pergunta de doses mudou em 2010.** Os questionários dos relatórios mostram:

| Edições | Coluna na base | Redação | Limite real |
|---|---|---|---|
| 2006-2008 | `q37b`¹¹, `q38b`¹² | "mais do que 5 doses" (homem) / "mais do que 4" (mulher) | 6+ / 5+ |
| 2009 | `q37`¹, `q38`² | "mais do que 5 doses" / "mais do que 4" | 6+ / 5+ |
| 2010-2024 | `q37`¹, `q38`² | "cinco ou mais doses" / "quatro ou mais" | 5+ / 4+ |

As *Orientações* (item 3.3) dizem que a redação mudou "a partir de 2010", e o questionário de 2009 confirma. A base, porém, guarda 2009 já na coluna nova, o que na v1 pareceu uma contradição com o documento. Consequências: 2010 é o primeiro ano da pergunta atual, o que sustenta a escolha do README; 2009 não é comparável com 2010 em diante; o salto de 2009 para 2010 na série pode ter parte artificial.

**A pergunta de entrada mudou duas vezes.** `q35`³ ("costuma consumir bebida alcoólica?") teve codificações diferentes em 2006, 2007-2019 e 2020-2023, e não existe em 2024: foi substituída por `R501`¹³ ("já consumiu na vida?") e `R502`¹⁴ ("consumiu nos últimos 12 meses?"). O dicionário rotula o código 2 de 2020+ como "sim, mas não no último mês", mas o questionário de 2023 traz 2 = "não" e 3 = "nunca".

**O filtro de 2024 é mais largo.** Entre todos os adultos, a parte fora do bloco de álcool caiu de 58,4% (2023) para 42,7% (2024), e "bebe menos de 1 dia por mês" subiu de 8,6% para 19,8%. Quem bebe menos de uma vez por mês continua pulando as doses, mas "menos de 1 dia por semana" subiu de 7,4% para 10,1%, e esse grupo responde às doses.

### 4.3 Modo de coleta: fixo e celular (item 5 das pendências)

Até 2021 só telefone fixo; em 2023, metade por celular; em 2024, mais de 90%. A troca é uma limitação porque:
1. **Quem é alcançado muda:** o jovem com fixo em 2010 era, em geral, quem morava com os pais; em 2024 o celular alcança quase todos.
2. **Como a pessoa responde muda:** no fixo de casa, com a família por perto, há mais viés de desejabilidade social.
3. **O peso não corrige:** ajusta sexo, idade, escolaridade e capital, mas não o comportamento associado a ter fixo.

**Evidência de 2023 (prevalência ponderada, IC 95% aproximado):**

| | Celular | Fixo |
|---|---|---|
| Todas as idades, 2023 | 27,0% (25,4 a 28,7), n = 10.832 | 15,5% (14,2 a 16,9), n = 10.858 |
| Jovens 18-24, 2023 | 25,7% (20,9 a 30,5), n = 1.232 | 19,5% (14,0 a 25,1), n = 592 |
| Todas as idades, 2024 | 23,2% (22,3 a 24,2), n = 24.448 | 11,7% (9,6 a 13,8), n = 2.600 |
| Jovens 18-24, 2024 | 24,8% (21,3 a 28,2), n = 2.187 | 10,5% (2,4 a 18,7), n = 107 |

O fixo tem muito mais idosos (38% das entrevistas de 2023 contra 9% no celular), mas a diferença aparece também entre os jovens. O peso é calibrado para a amostra total do ano, não por modo, então a tabela é indicativa.

### 4.4 Pesos (item 3 das pendências)

![Pesos por edição](figuras_relatorio_v2/aed2_fig3_pesos_por_ano.png)

O peso diz quantas pessoas cada entrevistado representa. Leitura do gráfico: escala log (cada marca é 10 vezes a anterior), caixa com os 50% centrais, linha na mediana, bigodes sem os extremos.

1. **O salto de 2009 para 2010 é mudança de escala, não de população.** 2006-2009: mediana de cerca de 250, soma de cerca de 30 milhões (próxima da população adulta das capitais). 2010-2024: mediana de cerca de 500 mil, soma de dezenas de bilhões. As *Orientações* dizem que `pesorake2025`¹⁹ junta pesos antigos e recalibrados, mas não explicam a escala. De 2010 em diante a soma acompanha o número de entrevistas (peso médio estável, de 1,2 a 1,4 milhão).
2. **Para prevalência não importa**, desde que calculada dentro de cada ano: multiplicar todos os pesos por uma constante não muda a razão. **Importa** ao juntar anos (normalizar antes) e ao estimar totais de pessoas.
3. **A variação dentro do ano é proposital:** amostra parecida por capital (um entrevistado de São Paulo representa muito mais gente que um de Palmas) e correção de grupos que atendem pouco. O custo é precisão, medido pelo *n* efetivo de Kish.
4. **Correção:** na conversa de 16/10/2026 foi dito que os pesos de 2023-2024 subiram "porque a amostra encolheu". Isso estava errado: em 2020-2021 a amostra também caiu à metade e o peso médio não subiu. Em 2023-2024 subiu só a mediana (532 mil em 2019; 602 mil em 2023; 698 mil em 2024), com a média estável. Os pesos do fixo são bem maiores que os do celular (mediana de 733 mil contra 506 mil em 2023; 1,9 milhão contra 648 mil em 2024), o que explica parte da mudança, mas não toda: o próprio celular de 2024 tem mediana acima da de 2019. Hipótese em aberto.

### 4.5 Idade e escolaridade

- `fet`¹⁵ é coerente com `q6`⁵ em todos os registros. Há 46 idades acima de 100 anos, fora das faixas da análise.
- `fesc`¹⁷ bate com a faixa recalculada a partir de `q8_anos`¹⁶ em 100% dos registros, mas é imputada nos 777/888 de `q8a`⁷. Em 2006 `q8a`⁷ usa outra codificação.
- **Composição dos jovens mudou** (com peso): 0 a 8 anos caiu de 14,4% (2010) para 8,3% (2024); 9 a 11 anos subiu de 54,4% para 58,7%. Sem peso, a amostra superestima a alta escolaridade (39,5% contra 31,2% em 2010). A P2 precisa ser respondida dentro de cada faixa.

### 4.6 Amostra e precisão

![Amostra por edição](figuras_relatorio_v2/aed2_fig2_amostra_por_ano.png)

Jovens entrevistados: 7.364 em 2010, 4.031 em 2019, 2.294 em 2024. Na faixa de 0 a 8 anos de estudo, pouco mais de 100 jovens nas edições recentes. Por capital, a mediana caiu de 270 jovens (2010) para 84 (2024); 20 das 27 capitais têm menos de 100 jovens em 2024.

### 4.7 Chave e outros

- `chave` só existe de 2014 a 2023 e, mesmo nesses anos, se repete (147 mil registros com chave repetida). Não serve como identificador.
- 58 mil linhas são idênticas nas 21 colunas do recorte; sem chave confiável, não há como distinguir pessoas com respostas iguais, e elas não são removidas.

---

## 5. Primeiro olhar sobre as perguntas (exploratório, não é o teste)

Prevalências ponderadas por `pesorake2025`¹⁹, com IC 95% aproximado pelo *n* efetivo de Kish. O IC 95% é a faixa onde o valor verdadeiro provavelmente está; quanto menos entrevistas, mais larga.

### P1 e P3: jovens contra 35 a 44 anos

![P1 e P3](figuras_relatorio_v2/aed2_fig4_p1_p3_faixa_etaria.png)

| Faixa | 2010 | 2019 | 2024 | 2010 → 2019 | 2010 → 2024 |
|---|---|---|---|---|---|
| 18 a 24 | 21,9% | 25,9% | 22,7% | +4,0 p.p. | +0,8 p.p. |
| 35 a 44 | 19,7% | 21,3% | 26,3% | +1,6 p.p. | +6,6 p.p. |

A comparação mais limpa é 2010 x 2019 (mesma pergunta, só telefone fixo). Nela os jovens **sobem** 4,0 p.p. e a faixa de 35 a 44 anos, 1,6 p.p. A alta das faixas mais velhas parece vir sobretudo de 2023-2024, quando o método mudou. Em nenhuma das duas comparações aparece a queda que o README supõe.

### P2: jovens por escolaridade

![P2](figuras_relatorio_v2/aed2_fig5_p2_escolaridade.png)

As três faixas oscilam muito de um ano para outro, sem tendência comum clara (2010 → 2024: 0 a 8 anos, 22,5% → 20,7%; 9 a 11, 18,5% → 22,3%; 12 e mais, 27,7% → 23,8%). A faixa de 0 a 8 anos tem pouco mais de 100 jovens nas edições recentes.

### P4: jovens por sexo

![P4](figuras_relatorio_v2/aed2_fig6_p4_sexo.png)

| Sexo e faixa | 2010 | 2019 | 2024 |
|---|---|---|---|
| Mulheres 18-24 | 14,8% | 23,4% | 25,4% |
| Mulheres 25-34 | 14,1% | 20,3% | 20,5% |
| Mulheres 35-44 | 10,9% | 14,6% | 20,5% |
| Homens 18-24 | 28,9% | 28,5% | 19,8% |
| Homens 25-34 | 34,7% | 32,5% | 31,1% |
| Homens 35-44 | 30,5% | 29,3% | 32,7% |

- **Mulheres:** a alta das jovens já era visível em 2019, ainda só com fixo, então resiste à troca de método. As mulheres de 25 a 44 anos subiram quase tanto, o que sugere uma mudança das mulheres em geral, e não da geração Z.
- **Homens:** os jovens são o único grupo masculino que caiu, o que lembra um efeito de geração. A queda, porém, aparece só em 2024, o ano da amostra menor, do celular e do novo filtro.
- **Cuidado de leitura:** o indicador mede consumo episódico pesado nos últimos 30 dias, e não dependência ou "problemas com álcool".

### P5: capitais

![P5](figuras_relatorio_v2/aed2_fig7_p5_capitais.png)

15 capitais subiram e 12 caíram de 2010 para 2024. As maiores altas (São Paulo, Vitória, Curitiba) e quedas (Fortaleza, Rio de Janeiro, Recife) têm intervalos largos: a largura mediana do IC passou de 11 p.p. (2010) para 18 p.p. (2024). Só em Fortaleza os intervalos não se sobrepõem. Florianópolis, com 53 jovens em 2024, tem intervalo de 15% a 40%. Um ranking com 2024 isolado seria enganoso.

---

## 6. Decisões de tratamento em aberto

Nada foi decidido. As linhas marcadas com "v2" são novas ou mudaram.

| # | Problema | Opções |
|---|---|---|
| D1 | Não existe edição de 2022 | Série com lacuna; interpolar só em gráfico; nunca imputar |
| D2 | Ano final: 2024 com mais de 90% celular; 2010 só fixo; em 2023 celular e fixo diferem muito (v2) | Usar 2024 e declarar; 2019 como sensibilidade; 2023-2024 juntos; só o fixo de 2023 contra 2010 |
| D3 | Amostra de jovens de 2024 é cerca de 1/3 da de 2010 | Anos isolados; triênios. **v2:** o triênio inicial não pode incluir 2009; opção 2010-2012 contra 2021-2024 (sem 2022) |
| D4 | Escalas de peso diferentes antes e depois de 2010 | Calcular dentro do ano; se juntar anos, normalizar o peso para somar 1 em cada ano |
| D5 | **v2:** pergunta de doses mudou em 2010; 2009 guardado na coluna nova | Série a partir de 2010; 2006-2009 só como contexto, com a ruptura marcada |
| D6 | `q35`³ muda de codificação e não existe em 2024 | Não usar `q35`³ como indicador; usar só `alcabu`¹⁸ |
| D7 | Composição dos jovens por escolaridade mudou | P2 dentro de cada faixa; opcionalmente padronizar pela composição de 2010 |
| D8 | `fesc`¹⁷ imputada quando `q8a`⁷ = 777/888 | Aceitar a imputação oficial; ou excluir os imputados e medir o efeito |
| D9 | Capitais com poucos jovens e intervalos largos | Ranking com IC; agrupar por região; juntar anos; só destacar diferenças fora do IC |
| D10 | `chave` vazia ou repetida | Chave substituta (ano + número da linha) na bronze |
| D11 | 2020-2021 coletados na pandemia | Manter com nota; excluir de médias de período |
| D12 | Texto livre com codificação mista; `regiao` vazia em 2012 | Texto livre fora do recorte; região a partir de `cidade` |
| D13 | **v2:** filtro de entrada de 2024 mais largo (`R502`¹⁴ no lugar de `q35`³) | Declarar com a D2; 2019 ou 2021-2023 como sensibilidade; comparar a distribuição de `q36`⁴ |

---

## 7. Fontes consultadas

### 7.1 Dados
- BRASIL. Ministério da Saúde. *Vigitel Brasil 2006-2024: base de dados harmonizada, formato CSV* (`vigitel-2006-2024-peso-rake-csv.zip`). Publicada em 24/08/2026. Disponível em <https://svs.aids.gov.br/daent/cgdnt/vigitel/>. Acesso em 16/10/2026.

### 7.2 Documentação da base (em `docs_fonte/`)
- *Dicionário de dados do Vigitel Brasil 2006-2024* (`dicionario-vigitel-2006-2024.xlsx`), abas *Variáveis_Vigitel* e *Indicadores_Vigitel*.
- *Orientações para análise do Vigitel Brasil 2006-2024* (21/08/2026): edição x ano de coleta, `q8_anos`¹⁶, mudança de redação de `q37`¹/`q38`², peso `pesorake2025`¹⁹.
- *Nota metodológica do Vigitel Brasil 2006-2024* (21/08/2026): revisão dos totais populacionais de Florianópolis e Fortaleza.

### 7.3 Relatórios e questionários (em `docs_fonte/`)
- *Vigitel Brasil 2006-2024* (questionário de 2024, p. 186-199): `R501`¹³, `R502`¹⁴, `q36`⁴, `q37`¹, `q38`².
- *Vigitel Brasil 2010* (questionário, p. 141): `q35`³ a `q38`², redação "5 ou mais".
- *Vigitel Brasil 2009* (questionário, p. 139): redação "mais do que 5" ainda em 2009.
- *Vigitel Brasil 2008* (questionário, p. 109): `q37b`¹¹/`q38b`¹².
- *Vigitel Brasil 2023* (questionário, p. 119): codificação de `q35`³ em 2023.
- *Vigitel Brasil 2006*: definição do indicador em 2006 (o questionário não foi publicado no relatório).
- *Vigitel Brasil 2006-2023: tabagismo e consumo abusivo de álcool*.

---

## 8. Próximos passos

1. O autor decide D1 a D13.
2. Executar o notebook v2 no Colab e no Databricks (só foi executado localmente).
3. Camada tratada (silver) com as decisões aplicadas, e teste formal das hipóteses na camada analítica.
4. Avaliar com o autor se a pergunta de negócio deve ser reformulada à luz da prévia (por exemplo, para o recorte por sexo), mantendo a formulação original documentada, como pede o enunciado do trabalho.

---

## 9. Histórico de versões

| Versão | Data | O que mudou |
|---|---|---|
| v1 | 16/10/2026 | Notebook de exploração inicial (sem relatório) |
| v2 | 16/10/2026 | Vazios em três categorias; notas com a redação oficial de toda pergunta e a definição de toda variável derivada; leitura didática dos pesos, com correção sobre 2023-2024; capitais com prevalência e IC; efeito do modo de coleta; achados novos (pergunta de doses mudou em 2010; filtro de 2024); D3 e D5 revistas, D13 nova; comparação 2010 x 2019 como sensibilidade |

---

## Apêndice A. Notas das variáveis

Fonte das redações: questionários nos apêndices dos relatórios Vigitel 2008, 2009, 2010, 2023 e 2006-2024; dicionário oficial para as versões de 2006 e para as variáveis derivadas.

¹ **q37**: pergunta, só homens: "Nos últimos 30 dias, o Sr. chegou a consumir cinco ou mais doses de bebida alcoólica em uma única ocasião? (cinco doses de bebida alcoólica seriam cinco latas de cerveja, cinco taças de vinho ou cinco doses de cachaça, whisky ou qualquer outra bebida alcoólica destilada)". 1 = sim, 2 = não. Feita só a quem bebe pelo menos uma vez por mês (q36 de 1 a 5). Redação "cinco ou mais" desde 2010; em 2009 a mesma coluna guarda a redação antiga, "mais do que 5 doses" (questionários Vigitel 2009, 2010 e 2006-2024).

² **q38**: pergunta, só mulheres: "Nos últimos 30 dias, a Sra. chegou a consumir quatro ou mais doses de bebida alcoólica em uma única ocasião? (quatro doses de bebida alcoólica seriam quatro latas de cerveja, quatro taças de vinho ou quatro doses de cachaça, whisky ou qualquer outra bebida alcoólica destilada)". 1 = sim, 2 = não. Mesmo filtro e mesma mudança de redação de q37 ("mais do que 4 doses" em 2009).

³ **q35**: pergunta, a todos: "O(a) Sr.(a) costuma consumir bebida alcoólica?". 2007-2019: 1 = sim, 2 = não. 2023: 1 = sim, 2 = não, 3 = nunca, 888 = não quis informar. 2006 e 2020-2021 têm outras codificações. Não existe em 2024: foi substituída por R501 e R502.

⁴ **q36**: pergunta, só a quem bebe: "Com que frequência o(a) Sr.(a) costuma consumir alguma bebida alcoólica?". 1 = 1 a 2 dias por semana, 2 = 3 a 4, 3 = 5 a 6, 4 = todos os dias, 5 = menos de 1 dia por semana, 6 = menos de 1 dia por mês (pula as perguntas de doses). 2006 usa outra codificação.

⁵ **q6**: pergunta, a todos: "Qual sua idade?" (só aceita 18 anos ou mais).

⁶ **q7**: registro do questionário, a todos: "Sexo: 1 = masculino, 2 = feminino".

⁷ **q8a**: pergunta, a todos: "Até que série e grau o(a) Sr.(a) estudou?". 1 = curso primário, 2 = admissão, 3 = ginasial, 4 = 1º grau ou fundamental, 5 = 2º grau ou ensino médio, 6 = 3º grau ou superior, 7 = pós-graduação, 8 = nunca estudou, 777 = não sabe (só aceito se idade > 60), 888 = não quis responder. 2006 usa outra codificação.

⁸ **q8b**: pergunta, a todos: "Qual a última série (ano) o(a) Sr.(a) COMPLETOU?", dentro do grau informado em q8a.

⁹ **q37a**: pergunta de 2006, só homens: primeira etapa da pergunta de doses ("> 2 doses", rótulo do dicionário); quem respondeu sim seguiu para q37b. A redação de 2006 não foi publicada no relatório daquele ano.

¹⁰ **q38a**: pergunta de 2006, só mulheres: primeira etapa ("> 1 dose", rótulo do dicionário); quem respondeu sim seguiu para q38b. Redação de 2006 não publicada no relatório.

¹¹ **q37b**: pergunta de 2006 a 2008, só homens: "Nos últimos 30 dias, o sr chegou a consumir mais do que 5 doses de bebida alcoólica em uma única ocasião?" ("mais do que 5" = 6 ou mais). Questionário Vigitel 2008.

¹² **q38b**: pergunta de 2006 a 2008, só mulheres: "... mais do que 4 doses ..." (5 ou mais). Questionário Vigitel 2008.

¹³ **R501**: pergunta de 2024, a todos: "Na sua vida, o(a) Sr.(a) já consumiu alguma bebida alcoólica?" (não: pula o bloco de álcool). A resposta não foi publicada na base de 2024.

¹⁴ **R502**: pergunta de 2024, a quem já bebeu: "Nos últimos 12 meses o(a) Sr.(a) consumiu alguma bebida alcoólica?" (não: pula o bloco). Substitui q35 como filtro de entrada; resposta não publicada na base de 2024.

¹⁵ **fet**: variável derivada: faixa etária calculada pelo Ministério a partir de q6. 1 = 18 a 24 (os "jovens"), 2 = 25 a 34, 3 = 35 a 44, 4 = 45 a 54, 5 = 55 a 64, 6 = 65 e mais.

¹⁶ **q8_anos**: variável derivada: anos de estudo calculados pelo Ministério combinando q8a e q8b pela tabela do item 2.3 das Orientações (por exemplo, ensino médio completo = 11, superior com 4 anos = 15, pós = 20). Pode ter valores fracionários imputados.

¹⁷ **fesc**: variável derivada: faixa de escolaridade a partir de q8_anos. 1 = 0 a 8 anos, 2 = 9 a 11, 3 = 12 e mais. Imputada pelo Ministério quando q8a = 777 ou 888, porque entra na calibração do peso.

¹⁸ **alcabu**: variável derivada: indicador oficial de consumo abusivo, chamado "consumo episódico pesado" desde 2024. 1 se q37 = 1 ou q38 = 1 (em 2006-2008, q37b ou q38b); 0 nos demais casos, inclusive para quem não bebe ou bebe menos de uma vez por mês. O denominador é toda a população adulta. Rotina do dicionário oficial.

¹⁹ **pesorake2025**: variável derivada: peso amostral de pós-estratificação (rake) por sexo, faixa etária e escolaridade em cada capital. Recalibrado pelo Censo 2022 para 2010-2024; pesos antigos em 2006-2009. A escala muda em 2010, então só deve ser usado dentro de cada ano.
