# Geração Z e consumo de álcool: a geração Z bebe menos, e isso vale para todas as classes sociais?

MVP de pipeline de dados em nuvem. Disciplina PSP8, Prof. André Serrano (EPR/FT/UnB).
Autor: Guilherme Augusto Fontes Cunha.

**Versão do objetivo:** 2 (16/10/2026). A formulação original, que comparava o ano de 2010 com o ano mais recente, está no [Anexo A](#anexo-a-formulação-anterior-do-objetivo-v1). A mudança veio da análise exploratória (*Relatório de Análise Exploratória de Dados v2*): a comparação entre anos misturava comportamento com mudanças de método da pesquisa, e a pergunta de negócio é sobre gerações. O problema, o decisor e a fonte continuam os mesmos.

> **Situação em 21/10/2026: entrega parcial.** O pipeline completo (coleta, bronze, silver, gold em esquema estrela, qualidade e análise) está pronto e foi validado por execução local, com as mesmas regras e funções que rodam no Databricks. As perguntas P1 a P5 já têm resposta (seção 9). Faltam a execução no Databricks Free Edition com as capturas de tela, a discussão geral e a autoavaliação. O que já foi feito, dia a dia, e o que falta estão na [seção 10](#10-situação-do-projeto-e-próximos-passos).

## 1. Objetivo

### 1.1 Contexto e problema de negócio

A indústria de bebidas tem investido em linhas sem álcool e de baixo teor alcoólico, com a percepção de que as gerações mais jovens bebem menos que as anteriores. Para essa indústria, e para bares e restaurantes que dependem do público jovem, a pergunta relevante não é apenas se os jovens bebem menos, mas **quem** dentro desse público bebe menos, e **se a mudança é da geração** (e portanto acompanha essas pessoas quando envelhecem) ou passageira.

Se a redução for restrita aos jovens de maior escolaridade e renda, o produto sem álcool é uma aposta de nicho, posicionada como premium. Se a redução for generalizada entre as classes sociais, trata-se de uma mudança estrutural do mercado jovem, que justifica estratégias de portfólio, preço e distribuição de massa. E se a geração mais nova apenas adia o consumo pesado para idades mais altas, o mercado sem álcool jovem é real, mas não substitui o consumo adulto no longo prazo.

**Decisor:** área de estratégia e portfólio de uma empresa de bebidas.
**Decisões apoiadas:**
1. Posicionar as linhas sem álcool voltadas ao público jovem como produto de nicho (alta escolaridade e renda) ou como produto de massa.
2. Tratar a demanda jovem por produtos sem álcool como estrutural (investimento de longo prazo) ou como fase de idade (investimento de curto prazo).

**Custo do erro:** posicionar como nicho uma tendência que é ampla significa perder mercado; posicionar como massa uma tendência que é restrita significa investir em distribuição e preço sem demanda correspondente. Tratar como estrutural uma mudança que é só adiamento superdimensiona o investimento de longo prazo.

Secundariamente, o resultado interessa à política de saúde pública, ao indicar se as ações de prevenção ao consumo abusivo devem ser diferenciadas por geração, sexo e nível socioeconômico.

### 1.2 Hipótese

> Na mesma idade (18 a 24 anos), a prevalência de consumo abusivo de álcool nas capitais brasileiras diminui de uma geração para a seguinte (millennials → zillennials → geração Z), nos dois sexos e em todas as faixas de escolaridade, e essa diferença não se explica por uma tendência geral da população no mesmo período.

A hipótese será considerada refutada, total ou parcialmente, se: (a) a prevalência aos 18-24 anos não diminuir de uma geração para a seguinte; (b) a diminuição ocorrer só em parte das faixas de escolaridade ou só em um dos sexos; ou (c) os adultos mais velhos mudarem na mesma direção e intensidade no mesmo período, o que indicaria uma tendência da época, e não um efeito geracional.

### 1.3 Decisões conceituais

**Geração, idade e época.** Comparar jovens e idosos em um mesmo ano mistura o efeito da idade com o da geração. Por isso a análise fixa a idade (18 a 24 anos) e compara gerações, identificadas pelo ano de nascimento (ano da edição menos a idade declarada, com erro de até um ano por causa do aniversário):

| Geração | Nascidos em | Observados aos 18-24 anos nas edições | Convenção |
|---|---|---|---|
| Millennials | 1986-1992 | 2010-2016 | Pew Research Center (DIMOCK, 2019): millennials de 1981 a 1996; o recorte começa em 1986 porque a série usada começa em 2010 |
| Zillennials | 1993-1998 | 2011-2021 | Faixa de transição em torno do corte do Pew (1996/1997). Não tem definição oficial: é convenção deste trabalho |
| Geração Z | 1999-2006 | 2017-2024 | Pew: geração Z a partir de 1997; o recorte começa em 1999 para não se sobrepor aos zillennials |

Com a idade fixa, comparar gerações também é comparar épocas diferentes. A P3 trata disso: compara a mudança dos jovens com a dos adultos mais velhos no mesmo período e acompanha cada geração ao envelhecer.

**Classe social.** A base não mede a renda de forma adequada para estratificação. A escolaridade será usada como proxy de nível socioeconômico, o que é uma limitação declarada: escolaridade e renda são correlacionadas, mas não equivalentes.

**Medida de consumo.** Indicador oficial de consumo abusivo do Vigitel (`alcabu`; desde 2024, "consumo episódico pesado"): cinco ou mais doses para homens, ou quatro ou mais para mulheres, em uma mesma ocasião nos últimos 30 dias. Essa redação vale desde 2010; até 2009 a pergunta era "mais do que" cinco ou quatro doses. Por isso a análise usa só as edições de 2010 em diante.

**Pesos amostrais.** Por se tratar de pesquisa por amostragem, todas as prevalências serão calculadas com o peso fornecido pela própria pesquisa (`pesorake2025`). Ao juntar edições numa mesma geração, o peso de cada edição é normalizado para somar 1, para que cada ano conte igual. Proporções sem ponderação não representam a população das capitais (BRUCE; BRUCE, 2019).

**Mesma idade, de fato (padronização pela idade).** A faixa de 18 a 24 anos não basta para comparar gerações "na mesma idade". Como a série começa em 2010 e termina em 2024, os millennials aparecem sobretudo aos 22-24 anos e a geração Z sobretudo aos 18-20 (figura f03a), e o consumo abusivo sobe com a idade. Por isso, toda comparação entre gerações usa a **prevalência padronizada pela idade simples**: a média das prevalências de cada idade de 18 a 24, com peso igual por ano de idade (padronização direta). A prevalência sem padronizar é mostrada ao lado para medir o viés. Decisão D14, de 18/10/2026, tomada na revisão da análise; a primeira versão dos resultados não tinha essa correção.

### 1.4 Perguntas de negócio

| # | Pergunta | Decisão que apoia |
|---|---|---|
| P1 | Na mesma idade (18 a 24 anos), quanto a prevalência de consumo abusivo de cada geração difere da anterior (millennials, zillennials, geração Z)? Em quantos pontos percentuais? | Confirma ou não a tendência que sustenta o investimento em linhas sem álcool |
| P2 | A diferença entre gerações ocorre em todas as faixas de escolaridade ou se concentra em alguma delas? | Decisão central: posicionamento de nicho ou de massa |
| P3 | A diferença é da geração ou da época? A mudança dos jovens é maior que a dos adultos de 35 a 44 anos no mesmo período? E cada geração mantém a diferença quando envelhece (por exemplo, aos 25-29 anos)? | Investimento estrutural ou de curto prazo; muda o público-alvo da estratégia |
| P4 | A diferença entre gerações é igual entre homens e mulheres? | Segmentação de comunicação e produto |
| P5 | Quais regiões ou capitais concentram as maiores e as menores diferenças entre gerações? | Priorização regional de lançamento e distribuição |

### 1.5 Tipo de análise

O problema é **descritivo e diagnóstico**: as perguntas são respondidas por prevalências ponderadas, estratificadas por geração, escolaridade, sexo e local, com SQL e PySpark no Databricks. Não há variável-alvo a prever que justifique o uso de Machine Learning nesta etapa.

### 1.6 Fonte de dados

**Vigitel** (Vigilância de Fatores de Risco e Proteção para Doenças Crônicas por Inquérito Telefônico), Ministério da Saúde. Inquérito anual, realizado desde 2006, com adultos residentes nas capitais dos estados e no Distrito Federal. Base usada: *Vigitel Brasil 2006-2024*, versão harmonizada publicada em 24/08/2026 em <https://svs.aids.gov.br/daent/cgdnt/vigitel/>, com 833.217 entrevistas.

**Pendências antes da coleta (situação em 16/10/2026):**
- ~~confirmar a disponibilidade dos microdados de cada ano e a licença de uso~~: disponíveis de 2006 a 2024, exceto 2022; licença do portal Creative Commons Atribuição-SemDerivações 3.0;
- ~~verificar se as variáveis de escolaridade e de consumo abusivo mantêm a mesma definição ao longo da série~~: a escolaridade (`fesc`) é estável; a pergunta de consumo abusivo mudou em 2010 (seção 1.3);
- ~~verificar anos com mudanças metodológicas ou interrupções na coleta~~: não há 2022; entrada do celular em 2023-2024; novo filtro de entrada do bloco de álcool em 2024. Detalhes no *Relatório de Análise Exploratória de Dados v2*.

### 1.7 Escopo e limitações previstas

- **Cobertura:** apenas capitais e Distrito Federal; os resultados não se estendem ao interior nem às áreas rurais.
- **Medida:** o indicador mede prevalência (proporção de pessoas que bebem de forma abusiva), não o volume consumido nem dependência; portanto, não mede diretamente o tamanho do mercado.
- **Autodeclaração:** o consumo é informado pelo próprio entrevistado por telefone, sujeito a viés de desejabilidade social.
- **Modo de coleta:** millennials e zillennials foram entrevistados só por telefone fixo; a geração Z, em parte por celular, que tende a registrar mais consumo. Uma comparação de sensibilidade usa só a parte da geração Z entrevistada por fixo.
- **Geração e época:** com a idade fixa, as gerações são observadas em anos diferentes; a P3 controla, mas não elimina, essa sobreposição.
- **Proxy:** escolaridade substitui renda como indicador de classe social.
- **Dados pessoais:** os microdados são anonimizados pela fonte; mesmo assim, por envolverem informação de saúde, a análise trabalhará apenas com resultados agregados, em conformidade com a LGPD (BRASIL, 2018).

## 2. Plataforma e arquitetura

**Databricks Free Edition** (Unity Catalog, Delta Lake, computação serverless), catálogo `workspace`, esquema `genz_alcool`. Arquitetura em camadas:

```
site do Ministério ──> Volume raw (ZIP, SHA-256) ──> bronze_vigitel (cópia fiel, 486 colunas)
   ──> silver_vigitel (2010+, regras S1-S11) ──> gold: fato_entrevista + 6 dimensões
   ──> qa_* (qualidade) e res_* (perguntas P1 a P5)
```

As regras ficam em módulos Python (`scripts/`) chamados pelos notebooks, para poderem ser testadas fora do cluster (`tests/rodar_local.py`). A gravação no Delta é feita em lotes, porque a base (833 mil linhas) passa do limite de uma única mensagem do Databricks Free Edition.

## 3. Dados: origem, licença e coleta

| Item | Valor |
|---|---|
| Fonte | Ministério da Saúde, SVSA/DAENT, *Vigitel Brasil 2006-2024*, base harmonizada publicada em 24/08/2026 |
| Endereço | <https://svs.aids.gov.br/daent/cgdnt/vigitel/> |
| Arquivo | `vigitel-2006-2024-peso-rake-csv.zip`, 87.121.523 bytes, SHA-256 `40139996d11deb2f52730c90f14e2df4bf5e53aba3cf1848fce391c93ff77993` |
| Conteúdo | um CSV de 577 MB: 833.217 entrevistas, 486 colunas, separador vírgula, codificação mista (lido como latin-1) |
| Licença | Creative Commons Atribuição-SemDerivações 3.0 (portal do Ministério). O MVP não redistribui o arquivo: o notebook 01 baixa do site oficial. Licença do código e registro da licença dos dados em [`LICENSE`](LICENSE) |
| Coleta | 16/10/2026; automática no notebook 01 (ou envio manual do ZIP ao Volume) |
| Documentação | dicionário, orientações, nota metodológica e relatórios em `docs_fonte/` |

## 4. Estrutura do repositório

| Pasta ou arquivo | Conteúdo |
|---|---|
| `notebooks/01` a `05` | pipeline do Databricks: coleta e bronze, silver, gold (estrela), qualidade, análise |
| `notebooks/06_correlatos.py` | análise complementar: o que anda junto com o consumo abusivo (seção 9.2) |
| `notebooks/aed/` | notebooks de análise exploratória (v1 a v3; o v3 roda no Colab e no Databricks), o gerador deles e as tabelas de saída |
| `scripts/` | `vigitel_etl.py` (regras de ETL), `qualidade.py`, `analise.py`, `graficos.py`, `gerar_catalogo.py` |
| `tests/rodar_local.py` | simulador local (duckdb) que executa os notebooks 01 a 06 sem cluster |
| `catalogo/` | catálogo de dados (`.md` e `.csv`) e modelo estrela |
| `DECISOES_TRATAMENTO.md` | decisões D1 a D14, alternativas e motivos |
| `Relatório de Análise Exploratória de Dados v3.md` | exploração e decisões, com os motivos do autor (a v2 fica como registro) |
| `POSSIVEIS_DESCOBERTAS.md` | achados preliminares a confirmar |
| `PENDENCIAS_AED.md` | comentários do autor sobre a exploração, acumulados e implementados por versão |
| `resultados/figuras/`, `figuras_relatorio_v2/` | figuras da análise (f01 a f14) e do relatório de exploração v2 |
| `evidencias/` | registros de execução (local, por enquanto; as capturas do Databricks entram aqui) |
| `apresentacao/` | apresentação dos resultados (`.pptx` e `.pdf`) e o script que a gera |
| `docs_fonte/` | documentação oficial do Vigitel: dicionário, orientações, nota metodológica e relatórios |
| `LICENSE` | licença do código (MIT) e registro da licença dos dados |

Os microdados brutos (`dados/raw/`) não são versionados, por causa da licença e do tamanho (577 MB descompactados): o notebook 01 baixa o arquivo do site oficial e confere o SHA-256.

## 5. Como reproduzir

**No Databricks (evidência exigida):**
1. *Workspace > Create > Git folder* com este repositório, <https://github.com/guilhermeafcunha/mvp-genz-alcool> (ou importe a pasta inteira, mantendo `notebooks/` e `scripts/` lado a lado: os notebooks localizam `scripts/` sozinhos).
2. Execute `notebooks/01_coleta_bronze` a `05_analise_hipoteses`, em ordem. O 01 cria o esquema e o Volume e baixa o ZIP; se não houver acesso à internet, envie o ZIP para `/Volumes/workspace/genz_alcool/raw/` e execute de novo.
3. Tire os screenshots das células "Verificação" de cada notebook e do Volume (pasta `evidencias/`).

**Exploração no Colab:** abra `notebooks/aed/MVP_GenZ_Alcool_01_AED_v3.ipynb` e use *Executar tudo*.

**Teste local:** `pip install -r requirements.txt`, coloque o ZIP em `dados/raw/` e rode `python tests/rodar_local.py dados/raw/vigitel-2006-2024-peso-rake-csv.zip`.

## 6. Modelagem

Esquema estrela, com a fato no grão de entrevista (615.877 linhas, edições de 2010 a 2024) e seis dimensões: edição, capital, geração, escolaridade, faixa etária e sexo. Diagrama e motivo em [`catalogo/modelo_estrela.md`](catalogo/modelo_estrela.md); dicionário completo, com tipo, domínio, obrigatoriedade e linhagem de cada atributo, em [`catalogo/catalogo_de_dados.md`](catalogo/catalogo_de_dados.md).

## 7. ETL e regras de negócio

As regras S1 a S11 da silver aplicam as decisões de tratamento tomadas pelo autor depois da análise exploratória (detalhe e motivos em `DECISOES_TRATAMENTO.md` e no relatório v3, seção 6):

| Regra | O que faz | Decisão |
|---|---|---|
| S1 | só edições de 2010 em diante, filtro pelo ano | D5 |
| S2 | `entrevista_id` = edição + linha do arquivo | D10 |
| S3 | marcadores de pandemia (2020-2021) e de filtro novo (2024) | D11, D13 |
| S4 | capital, UF e região derivadas do código da capital | D12 |
| S5 | modo de coleta (fixo até 2021) | D2, D13 |
| S6 | idade, faixa etária e sexo com rótulos | — |
| S7 | ano de nascimento e geração | D2 |
| S8 | escolaridade oficial e marcador de escolaridade estimada | D7, D8 |
| S9 | indicador oficial de consumo abusivo (`alcabu`) | D6 |
| S10 | bebe ao menos 1x por mês (`q36`) e "costuma beber" (`q35`, só conferência até 2023) | D6 |
| S11 | peso normalizado para somar 1 por edição | D4 |
| — | texto livre e as demais colunas ficam só na bronze | D12 |

A edição de 2022 não existe e não é imputada (D1).

## 8. Qualidade dos dados

O notebook 04 verifica 16 regras em seis dimensões (completude, unicidade, consistência, conformidade, acurácia e atualidade). Na execução local, todas as regras de verificação passaram (zero violações): bronze com as mesmas 833.217 linhas do CSV, silver com todas as 615.877 entrevistas de 2010 em diante, chave única, faixa etária e escolaridade coerentes, pulo das perguntas de doses conferido em 100% dos casos e peso normalizado somando 1 em cada edição. Registros informativos: 7.477 escolaridades estimadas pelo Ministério (D8), 35.280 entrevistas por celular (D2, D13) e a chave oficial repetida (D10).

## 9. Resultados (execução local; confirmar no Databricks)

Os números abaixo vêm da execução local do pipeline (`evidencias/log_execucao_local_pipeline.txt`), com as mesmas regras e funções que rodam no Databricks. Prevalências ponderadas, aos 18-24 anos, **padronizadas pela idade simples** (seção 1.3 e D14); IC 95% aproximado (Kish). Diferenças com \* têm intervalo que não inclui o zero.

**Revisão de 18/10/2026.** A primeira versão destes resultados comparava as gerações sem padronizar pela idade e mostrava uma queda total de −2,1 p.p. Essa queda vinha em boa parte de a geração Z ter sido observada mais nova: na mesma idade, ela desaparece (figura f03a e última linha da f11). Os números sem padronizar ficam na tabela para mostrar o tamanho do viés.

| | Millennials (1986-92) | Zillennials (1993-98) | Geração Z (1999-2006) | Geração Z − millennials | Sem padronizar (versão anterior) |
|---|---|---|---|---|---|
| Total | 21,1% | 22,2% | 22,3% | +1,1 p.p. (−1,1 a +3,3) | −2,1 p.p. (−3,9 a −0,2)\* |
| Homens | 28,1% | 26,7% | 24,0% | −4,0 p.p. (−7,3 a −0,8)\* | −8,1 p.p. (−10,9 a −5,3)\* |
| Mulheres | 14,1% | 17,8% | 20,5% | +6,4 p.p. (+3,6 a +9,2)\* | +3,9 p.p. (+1,5 a +6,3)\* |

**Cada geração contra a anterior (P1).** Millennials → zillennials: +1,1 p.p. no total (−0,4 a +2,5), −1,4 nos homens (n.s.) e +3,8 nas mulheres (+2,0 a +5,6)\*. Zillennials → geração Z: 0,0 no total, −2,6 nos homens e +2,6 nas mulheres, nenhuma significativa. Padronizando também pela escolaridade dos millennials (D7), o total fica em 21,2%, 22,6% e 22,7%: a mudança de escolaridade não explica a diferença.

**Por escolaridade (P2).** Geração Z − millennials: +0,6 p.p. (0 a 8 anos de estudo), +2,0 (9 a 11) e +1,2 (12 ou mais), nenhuma significativa. Não há sinal de queda concentrada nos mais escolarizados, mas também não há queda em nenhuma faixa.

**Geração ou época (P3).** Nas mesmas edições, os adultos de 35 a 44 anos subiram 3,8 p.p. (19,2% → 23,0%) e os jovens, 1,1 p.p.: a diferença das diferenças é de −2,7 p.p. (−5,1 a −0,3)\*. Os jovens não beberam menos em termos absolutos, mas subiram menos que a tendência da época. Ao envelhecer, os homens zillennials ficam cerca de 1,4 p.p. abaixo dos millennials tanto aos 18-24 quanto aos 25-29 (curvas paralelas); as mulheres zillennials ficam acima nas duas faixas. A leitura anterior de "adiamento" vinha do viés de idade e não se sustenta.

**Por quê (decomposição, D6).** Homens: a proporção que bebe ao menos uma vez por mês quase não muda (43% → 41%); o que cai é o exagero entre os que bebem (65% → 58%). Mulheres: mais bebem (25% → 35%), e o exagero entre as que bebem fica estável (56% → 58%).

**Capitais (P5).** Só Aracaju tem diferença fora da margem (−6,1 p.p.); com 27 capitais, cerca de uma é esperada só pelo acaso. Nenhuma região tem diferença significativa (de −0,5 p.p. no Norte a +4,5 no Sul). A maioria das capitais do Sul e do Sudeste (exceto o Rio de Janeiro) sobe e a maioria das do Nordeste (exceto Salvador) cai, mas dentro da margem.

**Robustez.** As mulheres sobem em cinco dos seis cenários com significância (de +5,1 a +8,1 p.p.); só na geração Z por telefone fixo (+2,7) o intervalo inclui o zero. A queda dos homens (de −2,4 a −4,1 p.p.) perde a significância em três cenários: só 18 a 21 anos, sem 2024 e geração Z só por fixo.

**Veredito pelos critérios da seção 1.2:** (a) **não atendido**: na mesma idade, a geração Z não tem prevalência menor que a dos millennials (+1,1 p.p., n.s.); (b) **não atendido**: os homens caem e as mulheres sobem, e nenhuma faixa de escolaridade cai; (c) atendido: os jovens subiram menos que os adultos de 35 a 44 no mesmo período. **A hipótese é refutada no que tem de central:** a geração Z não bebe em excesso menos que os millennials na mesma idade. O que existe é uma convergência entre os sexos (de 14 para 3,5 p.p.), com uma queda masculina moderada e pouco robusta e uma alta feminina robusta, e um consumo jovem que cresce menos que o dos adultos. Na versão sem padronizar, o critério (a) era atendido e a hipótese era "parcialmente refutada"; a mudança vem só da correção do método, com os critérios inalterados.

### 9.1 Figuras (em `resultados/figuras/`, na ordem da apresentação)

| # | Figura | Mensagem |
|---|---|---|
| f01 | ![](resultados/figuras/f01_serie_faixa_etaria.png) | Série 2010-2024 por faixa etária, com as rupturas (sem 2022, entrada do celular) |
| f02 | ![](resultados/figuras/f02_cobertura_geracoes.png) | Quem observamos: jovens entrevistados por geração e edição, e a % de celular |
| f03a | ![](resultados/figuras/f03a_idade_por_geracao.png) | Por que padronizar: o consumo sobe com a idade, e cada geração foi observada em idades diferentes (D14) |
| f03 | ![](resultados/figuras/f03_p1_geracoes.png) | P1: na mesma idade, a geração Z não bebe em excesso menos que os millennials (padronizada, sem padronizar e padronizada também pela escolaridade) |
| f04 | ![](resultados/figuras/f04_p4_convergencia_sexos.png) | P4: os sexos convergem (distância de 14 para 3,5 p.p.) |
| f05 | ![](resultados/figuras/f05_decomposicao.png) | Por que muda: quem bebe x quanto exagera, por sexo |
| f06 | ![](resultados/figuras/f06_p2_escolaridade.png) | P2: por escolaridade, nenhuma diferença significativa |
| f07 | ![](resultados/figuras/f07_p3_jovens_x_adultos.png) | P3: no mesmo período, os adultos de 35-44 subiram mais que os jovens |
| f08 | ![](resultados/figuras/f08_p3_envelhecimento.png) | P3: cada geração ao envelhecer (curvas paralelas nos homens) |
| f09 | ![](resultados/figuras/f09_p5_mapa_capitais.png) | P5: mapa das capitais |
| f10 | ![](resultados/figuras/f10_p5_capitais.png) | P5: diferença e margem de erro por capital |
| f11 | ![](resultados/figuras/f11_sensibilidades.png) | Robustez: as seis sensibilidades e, na última linha, a leitura sem padronizar |
| f12 | ![](resultados/figuras/f12_modo_coleta_2023.png) | Limitação: fixo x celular no mesmo ano |
| f13 | ![](resultados/figuras/f13_correlatos.png) | Correlatos do consumo abusivo (notebook 06) |
| f14 | ![](resultados/figuras/f14_correlatos_destaque.png) | Destaques dos correlatos |

### 9.2 Análise complementar: o que anda junto com o consumo abusivo (notebook 06)

Entre jovens de 18 a 24, diferença de consumo abusivo entre quem tem e quem não tem cada característica, ajustada por sexo e edição. Classificação de expectativa feita antes de olhar os dados.

| Característica | % dos jovens | Diferença ajustada (IC 95%) | Todos os adultos | Leitura |
|---|---|---|---|---|
| Fuma cigarro | 8% | +37,8 p.p. (+34,6 a +41,0) | +21,3 | Esperado (uso conjunto); mais forte nos jovens |
| Usa cigarro eletrônico (2019+) | 8% | +34,0 p.p. (+27,3 a +40,8) | +35,0 | Esperado; metade dos jovens que usam vape bebe em excesso |
| Diagnóstico de depressão (2020+) | 10% | +8,3 p.p. (+2,4 a +14,2) | −0,4 | **Só entre os jovens**; não passa no critério rígido (Bonferroni) |
| Refrigerante 5x+/semana | 28% | +8,3 p.p. (+6,6 a +10,0) | +6,9 | Inesperado; passa no critério rígido |
| Trabalha | 62% | +7,4 p.p. (+6,1 a +8,7) | +10,3 | Renda própria |
| Tela no lazer 3h+/dia (2016+) | 81% | +6,6 p.p. (+4,3 a +9,0) | +9,6 | **Contraria a ideia** de que o jovem "fica no celular em vez de sair para beber" |
| 12+ anos de estudo | 33% | +5,2 p.p. (+3,8 a +6,6) | +5,8 | Mais escolaridade, mais consumo abusivo |
| Preta ou parda (x branca) | 58% | −2,4 p.p. (−3,8 a −1,0) | +1,2 | Inesperado: só entre os jovens |
| Sono curto, dificuldade para dormir (2024) | 25-40% | n.s. | — | Só 2024, amostra pequena |
| Hipertensão, diabetes, inatividade | — | n.s. | — | Improváveis, confirmados como sem associação |

**Cuidados:** associação não é causa e pode ser nos dois sentidos; com 21 testes, cerca de 1 "significativo" pode ser acaso, e por isso a tabela completa (`res_correlatos`) traz também o critério de Bonferroni; o ajuste é só por sexo e edição. Apostas online (pergunta nova de 2024) não puderam ser testadas: a resposta não foi publicada na base.

A discussão completa, a autoavaliação e as evidências do Databricks serão acrescentadas após a execução na nuvem.

## 10. Situação do projeto e próximos passos

### 10.1 O que já foi feito

| Data | Etapa | Onde está |
|---|---|---|
| 16/10/2026 | Coleta do arquivo oficial (87 MB, SHA-256 conferido) e leitura da documentação do Vigitel | seção 3; `docs_fonte/` |
| 16/10/2026 | Análise exploratória v1 e v2: mapa de vazios em três categorias, pesos, mudanças de método (2010, celular, 2024) e prévia das perguntas | `notebooks/aed/`; *Relatório de Análise Exploratória de Dados v2* |
| 16/10/2026 | Objetivo reescrito por geração (versão 2), mantendo a versão 1 no Anexo A | seção 1 |
| 16/10/2026 | Decisões de tratamento D1 a D13, com alternativas e motivos | `DECISOES_TRATAMENTO.md` |
| 16/10/2026 | Pipeline do Databricks: notebooks 01 a 05, módulos de ETL, qualidade e análise, simulador local | `notebooks/`, `scripts/`, `tests/` |
| 16/10/2026 | Catálogo de dados (tipo, domínio, obrigatoriedade e linhagem) e modelo estrela | `catalogo/` |
| 16 e 17/10/2026 | Análise exploratória v3, que já aplica as decisões; achados preliminares; análise complementar dos correlatos (notebook 06) | `notebooks/aed/`; *Relatório v3*; `POSSIVEIS_DESCOBERTAS.md` |
| 17/10/2026 | Primeira versão da apresentação dos resultados | `apresentacao/` |
| 18/10/2026 | Decisão D14: comparação entre gerações padronizada pela idade simples. Resultados, figuras, registros de execução e apresentação refeitos; a hipótese passa de "parcialmente refutada" a "refutada no que tem de central" | seções 1.3 e 9; `resultados/figuras/`; `evidencias/` |
| 21/10/2026 | Publicação no GitHub, `LICENSE` e PDF da apresentação gerado de novo a partir da versão revisada | este repositório |

### 10.2 O que falta (checklist do enunciado)

- [x] Objetivo e perguntas de negócio documentados e íntegros, inclusive a formulação anterior (seção 1 e Anexo A).
- [x] Origem, licença e data de coleta registradas (seção 3 e `LICENSE`).
- [ ] Dados persistidos na plataforma de nuvem: executar os notebooks 01 a 06 no Databricks Free Edition (até aqui, só a execução local).
- [x] Modelo de dados descrito e catálogo com domínios e linhagem (seção 6 e `catalogo/`).
- [x] Transformação e carga documentadas, com as regras de negócio explícitas (seção 7).
- [x] Análise de qualidade em seis dimensões (seção 8), a confirmar na nuvem.
- [x] Resposta a cada pergunta, com figura e discussão (seção 9), a confirmar na nuvem.
- [ ] Discussão geral conectando as respostas às duas decisões de negócio.
- [ ] Autoavaliação: perguntas respondidas e não respondidas, limitações, o que faria diferente e extensões para uso contínuo.
- [ ] Capturas de tela do Databricks (Volume, células "Verificação" e resultados), legíveis e citadas no ponto do texto que sustentam (`evidencias/`).
- [x] Repositório público no GitHub (link a conferir em janela anônima antes da postagem).

## Referências

BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD). Brasília, DF: Presidência da República, 2018.

BRASIL. Ministério da Saúde. **Vigitel Brasil 2006-2024**: vigilância de fatores de risco e proteção para doenças crônicas por inquérito telefônico. Brasília: Ministério da Saúde, 2025.

BRASIL. Ministério da Saúde. **Vigitel Brasil 2006-2024**: base de dados harmonizada e orientações para análise. Brasília: Ministério da Saúde, 2026. Disponível em: <https://svs.aids.gov.br/daent/cgdnt/vigitel/>. Acesso em: 16 out. 2026.

BRUCE, P.; BRUCE, A. **Estatística prática para cientistas de dados**. Rio de Janeiro: Alta Books, 2019.

DIMOCK, M. **Defining generations**: where Millennials end and Generation Z begins. Washington, DC: Pew Research Center, 2019.

PROVOST, F.; FAWCETT, T. **Data science for business**. Sebastopol: O'Reilly Media, 2013.

---

## Anexo A: formulação anterior do objetivo (v1)

Formulação original, mantida como registro. Foi substituída em 16/10/2026 porque, na análise exploratória, a comparação entre os anos de 2010 e 2024 se mostrou exposta a três mudanças de método concentradas nas pontas (pergunta de doses nova em 2010; celular e novo filtro de entrada em 2023-2024), e porque o interesse do autor é o recorte por geração, incluindo a transição zillennial.

**Título original:** Geração Z e consumo de álcool: a queda é generalizada entre as classes sociais?

**Decisão apoiada (original):** posicionar as linhas sem álcool voltadas ao público jovem como produto de nicho (alta escolaridade e renda) ou como produto de massa.

**Hipótese original:**

> A prevalência de consumo abusivo de álcool entre adultos de 18 a 24 anos nas capitais brasileiras diminuiu entre 2010 e o ano mais recente disponível, e essa queda ocorre em todas as faixas de escolaridade, de forma mais intensa do que entre adultos de faixas etárias mais velhas no mesmo período.

A hipótese seria considerada refutada, total ou parcialmente, se: (a) a prevalência entre jovens não diminuísse no período; (b) a queda se concentrasse em apenas parte das faixas de escolaridade; ou (c) a queda dos jovens fosse equivalente à das demais faixas etárias, o que indicaria uma tendência geral da população, e não um efeito geracional.

**Decisão conceitual original sobre geração e idade:** a análise fixava a faixa etária e comparava os anos: pessoas de 18 a 24 anos em 2010, nascidas aproximadamente entre 1986 e 1992 (geração millennial), seriam comparadas com pessoas de 18 a 24 anos no ano mais recente, majoritariamente da geração Z, pela convenção do Pew Research Center (DIMOCK, 2019).

**Perguntas originais:**

| # | Pergunta | Decisão que apoia |
|---|---|---|
| P1 | A prevalência de consumo abusivo entre adultos de 18 a 24 anos diminuiu entre 2010 e o ano mais recente disponível? Em quantos pontos percentuais? | Confirma ou não a existência da tendência que sustenta o investimento em linhas sem álcool |
| P2 | A variação entre os jovens ocorre em todas as faixas de escolaridade ou se concentra em alguma delas? | Decisão central: posicionamento de nicho ou de massa |
| P3 | A variação entre os jovens é maior do que a observada entre adultos de 35 a 44 anos no mesmo período? | Distingue efeito geracional de tendência geral, o que muda o público-alvo da estratégia |
| P4 | A variação entre os jovens difere entre homens e mulheres? | Segmentação de comunicação e produto |
| P5 | Quais capitais apresentam as maiores e as menores variações entre os jovens? | Priorização regional de lançamento e distribuição |

**O que a exploração mostrou para a formulação original** (prévia, não teste): jovens com 21,9% em 2010 e 22,7% em 2024, sem queda; na comparação só por telefone fixo (2010 x 2019), alta de 4,0 p.p.
