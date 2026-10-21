# Pendências para o próximo ajuste do AED (notebook 01)

Notas acumuladas para implementar de uma vez na próxima versão do notebook de AED.

**Status (16/10/2026): itens 1 a 5 implementados no `MVP_GenZ_Alcool_01_AED_v2.ipynb` e no *Relatório de Análise Exploratória de Dados v2.md*.** Novos comentários entram a partir do item 6, para a v3.

## 1. Mapa de vazios em três categorias (16/10/2026)

**Problema:** o mapa da seção 4.1 pinta de preto qualquer vazio e dá a impressão de base muito incompleta, mas quase todo o preto é vazio estrutural.

**O que fazer:**
- Refazer o mapa com três cores: **pulo legítimo** (pergunta não se aplica: `q37` para mulheres, `q38` para homens, `q36`/`q37`/`q38` para quem não bebe), **variável inexistente no ano** (`q37a/b`, `q38a/b` fora de 2006-2008; `tipo_fone` até 2021; `chave` não publicada; `q35` em 2024) e **faltante de verdade** (não resposta a uma pergunta que se aplicava).
- Incluir uma tabela com a classificação de cada coluna (estrutural, troca de nome, recuperável, faltante) e destacar que as sete colunas da análise (`ano`, `cidade`, `fet`, `q7`, `fesc`, `alcabu`, `pesorake2025`) têm 0% de vazio.
- Usar o vocabulário do Módulo 3: "não aplicável" (não imputar nem remover), MCAR/MAR/MNAR.

**Riscos a registrar na leitura (os que o mapa não mostra):**
1. **Branco pode ser imputação:** `fesc` é imputada pelo Ministério quando `q8a` = 777/888 (cerca de 8.170 casos, 1%). Ligado à decisão D8.
2. **`alcabu` trata vazio como "não":** correto quando o vazio é pulo. Até 2023 dá para checar o pulo com `q35`; em 2024 `q35` não foi publicada, então não é possível provar que todo vazio é pulo e não recusa. Incluir a checagem do pulo (2009-2023) e declarar a limitação de 2024.
3. **Não resposta à pesquisa inteira:** quem não atende ou não tem telefone não aparece no mapa. O peso rake corrige a composição por sexo, idade e escolaridade, mas não diferenças de comportamento. Somada à troca do fixo pelo celular (2023-2024), é o maior risco da comparação 2010 x 2024. Possível MNAR; só pode ser declarado.

## 2. Nota de rodapé em todas as perguntas do questionário (16/10/2026)

**Pedido:** sempre que o notebook mencionar **qualquer pergunta do questionário** (`q6`, `q7`, `q8a`, `q8b`, `q35`, `q36`, `q37`, `q38` e as variantes antigas `q37a`, `q37b`, `q38a`, `q38b`), marcar com nota sobrescrita (¹, ², ³...) e pôr a legenda logo abaixo do bloco onde a pergunta aparece (texto markdown, tabelas e títulos de gráfico). Ampliado em 16/10/2026: o pedido original valia só para `q37` e `q38`.

**Numeração:** cada pergunta mantém o **mesmo número no notebook inteiro** (por exemplo, `q37` é sempre ¹), para a nota ser reconhecível em qualquer seção. Montar uma tabela-mestra pergunta → número → redação e repetir só as notas usadas em cada bloco.

**Legenda (texto a transcrever literalmente do questionário oficial antes de implementar):**
- Exemplos provisórios: `q37` (só homens) "Nos últimos 30 dias, o senhor chegou a consumir 5 ou mais doses de bebida alcoólica em uma única ocasião?"; `q38` (só mulheres) mesma pergunta, com 4 ou mais doses.
- Cada legenda traz: redação da pergunta, a quem é feita (filtro/pulo), códigos de resposta e período em que vale.
- Para `q37`/`q38`, incluir a definição de dose usada pelo Vigitel (lata de cerveja, taça de vinho, dose de destilado).
- Fonte: questionários nos apêndices dos relatórios Vigitel (redação de 2009/2010 em diante; 2006-2008 para as variantes antigas).

**Cuidados na implementação:**
- Toda redação é provisória até ser conferida no apêndice do relatório; não colar texto de memória.
- As variantes antigas (`q37a`, `q37b`, `q38a`, `q38b`) recebem nota própria, com a redação de 2006-2008, já que a pergunta mudou.
- **Variáveis derivadas também ganham nota** (decidido pelo usuário em 16/10/2026): `fet`, `fesc`, `q8_anos`, `alcabu` e `pesorake2025`, com a mesma numeração fixa das perguntas. A legenda traz como a variável é calculada e o que isso implica para a leitura:
  - `fet`: 6 faixas a partir de `q6`; 18-24 é o grupo "jovem".
  - `q8_anos`: combinação de `q8a` e `q8b` pela tabela oficial de conversão (item 2.3 das *Orientações*); pode ter decimais imputados.
  - `fesc`: 3 faixas (0-8, 9-11, 12+ anos) a partir de `q8_anos`; **imputada** quando `q8a` = 777/888.
  - `alcabu`: 1 se `q37` = 1 ou `q38` = 1, 0 nos demais casos, inclusive quem não bebe; denominador = toda a população adulta. Rotina oficial do dicionário.
  - `pesorake2025`: peso rake (Censo 2022 para 2010-2024, pesos antigos para 2006-2009); escala muda em 2010.
- Em células de código e saídas impressas não dá para usar sobrescrito de forma confiável: a nota vale para o texto markdown; nos gráficos, usar o número no rótulo e a legenda na leitura logo abaixo.

## 3. Leitura da seção 12 (pesos) mais didática (16/10/2026)

**Pedido:** levar para a leitura da seção 12 a explicação do boxplot dos pesos dada na conversa, para quem não conhece peso amostral.

**Conteúdo a incluir:**
1. **O que é o peso:** quantas pessoas da população cada entrevistado representa. Como ler o gráfico: escala log (cada marca = ×10), caixa = 50% centrais, linha = mediana, bigodes sem os extremos.
2. **Salto 2009 → 2010 é mudança de escala, não de população:** 2006-2009 têm mediana de cerca de 250 e soma de cerca de 30 milhões (próxima da população adulta das capitais); 2010-2024 têm mediana de cerca de 500 mil e soma de cerca de 60 bilhões, o que não pode ser população. A orientação oficial diz que `pesorake2025` junta os pesos antigos (2006-2009) com os recalibrados pelo Censo 2022 (2010-2024). A documentação não explica a escala: não inventar o motivo.
3. **Por que não afeta a análise:** prevalência = soma dos pesos de quem tem o evento ÷ soma de todos os pesos; multiplicar todos os pesos de um ano por uma constante não muda a razão. Afeta, sim: juntar anos numa conta (normalizar antes, decisões D3/D4) e estimar totais de pessoas a partir de 2010 (sairiam em bilhões).
4. **Variação dentro do ano é proposital:** em 2010 o maior peso é cerca de mil vezes o menor. Motivos: amostra parecida por capital (um entrevistado de São Paulo representa muito mais gente que um de Palmas) e correção de grupos que atendem pouco o telefone. Custo: perda de precisão, medida pelo *n* efetivo de Kish, que é o que as margens de erro usam.
5. **2023-2024 (CORRIGIDO):** na conversa foi dito que os pesos subiram "porque a amostra encolheu". **Isso estava errado.** Em 2020-2021 a amostra também caiu à metade (cerca de 27 mil) e o peso médio não subiu; o que caiu foi a soma. De 2010 em diante a soma dos pesos acompanha o número de entrevistas (peso médio estável, de 1,2 a 1,4 milhão), e não a população. Em 2023-2024 subiu só a **mediana** (532 mil em 2019; 602 mil em 2023; 698 mil em 2024), com a média estável: mudou o formato da distribuição. Hipótese a investigar, não afirmar: mudança de composição da amostra com a entrada do celular.

**A implementar junto:** acrescentar à tabela da seção 12 as colunas média e mediana e uma linha de "soma dos pesos ÷ entrevistas", para o leitor ver a relação soma × amostra; e checar a hipótese do item 5 comparando a distribuição dos pesos entre fixo e celular em 2023 e 2024.

## 4. Gráfico das capitais (seção 13.4) com prevalência e IC (16/10/2026)

**Problema:** o gráfico atual mostra só a largura do IC 95% e foi lido como "os jovens bebem mais em todas as capitais". Ele mostra incerteza, não consumo.

**O que fazer:**
- Trocar por um gráfico de pontos com barra de erro: para cada capital, a prevalência de 2010 e a de 2024 como pontos, e o IC 95% como linha horizontal, lado a lado. Ordenar pela variação.
- Manter o título explícito: "prevalência (ponto) e IC 95% (linha)".
- Acrescentar na leitura os números da conversa: 15 capitais subiram e 12 caíram; só Fortaleza (23,7% para 9,3%) tem ICs sem sobreposição; em 2024 Florianópolis tem 53 jovens e IC de 15% a 40%. Avisar que a sobreposição de ICs é critério aproximado; o teste formal fica para a camada analítica.
- Explicar em uma frase o que é o IC 95% e a largura, para leitor leigo.
- Reforçar a conclusão para a P5: ranking com 2024 isolado é enganoso; ligar às decisões D3 e D9.

## 5. Efeito do modo de coleta (fixo x celular) na seção 8 (16/10/2026)

**Pedido:** levar para a seção 8 a explicação de por que a troca de fixo por celular é uma limitação, com a evidência de 2023.

**Conteúdo a incluir:**
1. **Quem é alcançado:** em 2010 só entravam casas com linha fixa; o jovem com fixo em 2010 era, em geral, quem morava com os pais. Em 2024 o celular alcança quase todos. Os "jovens de 2010" e "de 2024" não são o mesmo recorte.
2. **Como a pessoa responde:** no fixo de casa, com a família por perto, há mais viés de desejabilidade social; no celular, a pessoa fala sozinha.
3. **O peso não corrige:** ajusta sexo, idade, escolaridade e capital, mas não o comportamento associado a ter fixo nem o constrangimento.
4. **Evidência (2023, metade fixo e metade celular), prevalência ponderada:** todas as idades, celular 27,0% ±1,6 contra fixo 15,5% ±1,4; jovens 18-24, celular 25,7% ±4,8 contra fixo 19,5% ±5,6. Em 2024: todas as idades 23,2% contra 11,7%; jovens 24,8% contra 10,5% (fixo com só 107 jovens). Ressalva: o peso é calibrado para a amostra total do ano, não por modo; tabela indicativa. Não dá para separar "outro tipo de pessoa" de "resposta mais sincera".
5. **Consequências para a leitura:** 2024 tende a sair mais alto que 2010 só pelo método; a estabilidade dos jovens pode esconder queda real (reabre a hipótese); a alta das outras faixas em 2023-2024 pode ter parte artificial; a alta das jovens mulheres resiste melhor (já visível em 2019, só fixo). Reforça a opção de 2019 como sensibilidade na D2.

**A implementar:** tabela de prevalência por modo (2023 e 2024; todas as idades e jovens) e composição por idade e escolaridade de cada modo.

## 6. (aguardando próximos comentários)
