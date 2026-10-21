# Possíveis descobertas do MVP (preliminares)

Achados que surgiram na exploração e na discussão das decisões de tratamento. **Não são resultados**: são números de exploração, sem teste formal e, em parte, sem margem de erro. Devem ser confirmados na camada analítica, depois de aplicadas as decisões D1 a D13.

## 1. Geração Z masculina: modera, não abandona; mulheres jovens: entram no consumo (16/10/2026)

**Achado:** o consumo abusivo pode ser separado em duas partes, quantos bebem × quantos dos que bebem exageram. Nos dois sexos, a mudança entre gerações vem por caminhos diferentes.

Jovens de 18 a 24 anos, prevalência ponderada (peso normalizado por edição), edições de 2010 a 2023 (sem 2024, porque a `q35` não existe nesse ano):

| Geração (nascidos em) | Sexo | Costuma beber (`q35`) | Bebe ao menos 1x/mês (`q36`) | Consumo abusivo (`alcabu`) | Abusivo entre quem bebe ao menos 1x/mês |
|---|---|---|---|---|---|
| Millennials (1986-1992) | Homens | 51,4% | 46,1% | 30,3% | 65,7% |
| Zillennials (1993-1998) | Homens | 45,8% | 40,0% | 25,5% | 63,7% |
| Geração Z (1999-2006) | Homens | 48,6% | 38,5% | 22,8% | 59,2% |
| Millennials (1986-1992) | Mulheres | 32,3% | 26,8% | 15,4% | 57,5% |
| Zillennials (1993-1998) | Mulheres | 34,8% | 28,6% | 17,0% | 59,7% |
| Geração Z (1999-2006) | Mulheres | 39,8% | 30,9% | 17,6% | 57,0% |

- **Homens jovens:** a proporção dos que bebem quase não muda; o que cai é o exagero entre quem bebe (66% → 59%). A geração Z masculina **não está deixando de beber: está moderando**.
- **Mulheres jovens:** o exagero entre quem bebe fica estável (57-60%); o que sobe é a proporção das que bebem (32% → 40%). A alta do consumo abusivo feminino vem de **mais mulheres bebendo**.
- **Todas as idades:** "costuma beber" ficou estável entre os homens (52% em 2010, 53% em 2023) e subiu entre as mulheres (27% → 37%), com a alta começando em 2016, ainda só com telefone fixo.
- **Escolaridade:** a geração Z bebe um pouco mais que os millennials nas três faixas, e o exagero entre quem bebe cai nas três (de 4 a 7 pontos), um sinal de moderação ampla entre as classes sociais (P2).

**Implicação de negócio (se confirmado):** favorece linhas de **baixo teor e moderação** mais do que a abstinência pura: o jovem homem continua bebendo, mas menos por ocasião. Há também um público feminino jovem crescendo entre quem bebe.

**Para confirmar:** recalcular com a decomposição da D6 (`q36`, cobrindo 2024), com margem de erro, comparando na mesma idade (18-21), com sensibilidade sem 2024 e só com entrevistas por fixo.

## 2. Homens: queda a cada geração, já visível só com telefone fixo (16/10/2026)

Consumo abusivo aos 18-24 anos: millennials 30,3%, zillennials 25,5% (ambos só por fixo), geração Z 22,2% (2017-2024, 33% celular). Como o celular tende a aumentar o consumo declarado, a queda da geração Z pode estar subestimada. Mulheres: 15,4% → 17,0% → 19,3%. A distância entre os sexos caiu de 15 para 3 pontos.

**Pista para a P3 (amostra pequena):** os zillennials homens sobem de 25,5% (18-24) para 32,7% (25-29 anos, ±3,4), perto dos millennials na mesma idade (34,6%). Pode ser adiamento, e não abandono, do consumo pesado.

## 3. Correlatos do consumo abusivo entre jovens (17/10/2026)

Notebook `06_correlatos` (execução local): 21 características do Vigitel testadas contra o consumo abusivo, entre jovens de 18 a 24 anos, com ajuste por sexo e edição. Detalhes no README, seção 9.2, e na figura f13.

- **Cigarro e vape:** os mais fortes (+38 e +34 p.p.). Metade dos jovens que usam cigarro eletrônico bebe em excesso. Esperado (uso conjunto), mas é um dado de público para o negócio: o consumo pesado se concentra num grupo que também usa nicotina.
- **Depressão só entre os jovens:** +8,3 p.p. entre jovens com diagnóstico de depressão, e nenhuma diferença entre os adultos em geral (−0,4). É o achado mais "escondido", mas tem amostra pequena (2020+) e não passa no critério rígido de Bonferroni. Pode ser nos dois sentidos.
- **Tela não substitui o bar:** jovens com 3h+ de tela no lazer bebem mais em excesso (+6,6 p.p.), e não menos. Contraria a narrativa de que a geração Z "troca a balada pelo celular".
- **Refrigerante:** +8,3 p.p. para quem toma refrigerante 5x+ por semana, e passa no critério rígido. Hipótese: consumo de bebidas açucaradas como misturador ou padrão de consumo; a confirmar.
- **Raça:** jovens pretos e pardos bebem em excesso menos que brancos (−2,4 p.p.), o que não acontece entre os adultos em geral (+1,2).

**Para confirmar:** repetir no Databricks; testar se as associações mudam entre gerações (por exemplo, a de depressão é maior na geração Z?); ajustar também por escolaridade.
