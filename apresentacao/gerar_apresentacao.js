// Gera a apresentacao do MVP (pptxgenjs). Uso: node gerar_apresentacao.js <pasta_figuras> <saida.pptx> <apply_theme.js>
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const [FIG, SAIDA, APPLY] = process.argv.slice(2);
const { applyTheme } = require(APPLY);

const THEME = {
  name: "Geracao Z e Alcool",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B1F24", lt1: "FFFFFF", dk2: "0F2A4A", lt2: "EEF2F7",
    accent1: "1F5FAE", accent2: "EB6834", accent3: "7FA7D9", accent4: "B8B6AD", accent5: "C0392B", accent6: "2E7D32",
    hlink: "1F5FAE", folHlink: "6B4FA0",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.title = "Geração Z e álcool: a geração Z bebe menos?";
pres.author = "Guilherme Augusto Fontes Cunha";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const W = 13.333, H = 7.5;

// ---------------------------------------------------------------- layouts
pres.defineSlideMaster({
  title: "CAPA", background: { color: THEME.colors.dk2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.0, w: 11.7, h: 1.9, fontSize: 44, bold: true, color: C.background1, fontFace: THEME.headFontFace, valign: "bottom", align: "left" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.1, w: 11.7, h: 1.6, fontSize: 18, color: C.accent3, valign: "top" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTEUDO", background: { color: THEME.colors.lt1 },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.9, fontSize: 30, bold: true, color: C.text2, fontFace: THEME.headFontFace, valign: "middle" }, text: "" } },
    { text: { text: "MVP PSP8 · Geração Z e álcool · Vigitel 2010-2024", options: { x: 0.6, y: 7.0, w: 8, h: 0.3, fontSize: 10, color: C.accent4 } } },
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.6, h: 0.3, fontSize: 10, color: THEME.colors.accent4, align: "right" },
});
pres.defineSlideMaster({
  title: "SECAO", background: { color: THEME.colors.lt2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.6, w: 11.7, h: 1.3, fontSize: 40, bold: true, color: C.text2, fontFace: THEME.headFontFace, valign: "bottom", align: "left" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.0, w: 11.7, h: 1.2, fontSize: 18, color: C.accent1, valign: "top" }, text: "" } },
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.6, h: 0.3, fontSize: 10, color: THEME.colors.accent4, align: "right" },
});

// ---------------------------------------------------------------- utilitarios
function tamanhoPng(arquivo) {
  const b = fs.readFileSync(arquivo);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
function figura(slide, nome, x, y, w, h) {
  const arq = path.join(FIG, nome);
  const t = tamanhoPng(arq);
  const r = Math.min(w / t.w, h / t.h);
  const iw = t.w * r, ih = t.h * r;
  slide.addImage({ path: arq, x: x + (w - iw) / 2, y: y + (h - ih) / 2, w: iw, h: ih, objectName: nome, altText: nome });
}
function texto(slide, t, o) {
  slide.addText(t, Object.assign({ isTextBox: true, fontSize: 16, color: C.text1, valign: "top", margin: 0.05 }, o));
}
function destaque(slide, numero, rotulo, x, y, w, cor) {
  texto(slide, numero, { x, y, w, h: 0.9, fontSize: 44, bold: true, color: cor || C.accent1, fontFace: THEME.headFontFace, valign: "bottom" });
  texto(slide, rotulo, { x, y: y + 0.95, w, h: 0.8, fontSize: 14, color: C.text1 });
}
function cartao(slide, x, y, w, h, titulo, corpo, cor, nome) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: nome });
  texto(slide, titulo, { x: x + 0.25, y: y + 0.2, w: w - 0.5, h: 0.5, fontSize: 18, bold: true, color: cor || C.accent1 });
  const lista = Array.isArray(corpo) ? corpo.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < corpo.length - 1 } })) : corpo;
  texto(slide, lista, { x: x + 0.25, y: y + 0.75, w: w - 0.5, h: h - 0.95, fontSize: 15, paraSpaceAfter: 6 });
}
function circuloNum(slide, n, x, y, cor) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: 0.55, h: 0.55, fill: { color: cor || C.accent1 }, line: { color: cor || C.accent1 } });
  texto(slide, String(n), { x, y, w: 0.55, h: 0.55, fontSize: 16, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0 });
}
function conteudo(secao, titulo) {
  const s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: secao });
  s.addText(titulo, { placeholder: "title" });
  return s;
}

// ================================================================ ABERTURA
pres.addSection({ title: "Abertura" });
let s = pres.addSlide({ masterName: "CAPA", sectionTitle: "Abertura" });
s.addText("A geração Z bebe menos?", { placeholder: "title" });
s.addText([
  { text: "Consumo abusivo de álcool por geração nas capitais brasileiras, Vigitel 2010-2024", options: { breakLine: true } },
  { text: "MVP de pipeline de dados em nuvem (Databricks) · PSP8, Prof. André Luiz Marques Serrano, EPR/FT/UnB", options: { breakLine: true, fontSize: 14, color: C.background2 } },
  { text: "Guilherme Augusto Fontes Cunha", options: { fontSize: 14, color: C.background2 } },
], { placeholder: "body" });
s.addNotes(`Abertura (30 s).
Bom dia. A pergunta deste MVP é simples e tem cara de manchete: a geração Z bebe menos? A indústria de bebidas já aposta que sim e investe em linhas sem álcool. Eu fui verificar com os microdados oficiais do Ministério da Saúde, o Vigitel, e montei um pipeline de dados no Databricks para responder.
Spoiler: na mesma idade, não. O que muda é outra coisa: homens e mulheres jovens estão ficando parecidos.`);

s = conteudo("Abertura", "O problema de negócio");
cartao(s, 0.6, 1.5, 5.9, 2.4, "Decisão 1: nicho ou massa?", "Se só os jovens mais escolarizados bebem menos, a linha sem álcool é um produto premium, de nicho. Se a queda atinge todas as classes, é mercado de massa.", C.accent1, "card_d1");
cartao(s, 6.85, 1.5, 5.9, 2.4, "Decisão 2: estrutural ou fase?", "Se a geração Z leva o hábito para a vida adulta, o investimento é de longo prazo. Se só adia o consumo, é uma fase de idade.", C.accent2, "card_d2");
texto(s, "Decisor: área de estratégia e portfólio de uma empresa de bebidas", { x: 0.6, y: 4.3, w: 12.1, h: 0.45, fontSize: 18, bold: true, color: C.text2 });
texto(s, [
  { text: "Errar para nicho numa tendência ampla: perder mercado.", options: { bullet: true, breakLine: true } },
  { text: "Errar para massa numa tendência restrita: investir em distribuição sem demanda.", options: { bullet: true, breakLine: true } },
  { text: "Interesse secundário: saúde pública (prevenção por geração, sexo e classe).", options: { bullet: true } },
], { x: 0.6, y: 4.85, w: 12.1, h: 1.8, fontSize: 16, paraSpaceAfter: 6 });
s.addNotes(`O problema de negócio (1 min).
O decisor é a área de estratégia de uma empresa de bebidas. São duas decisões. A primeira: posicionar a linha sem álcool como nicho, para jovens de alta escolaridade e renda, ou como produto de massa. A segunda, que surgiu ao longo do trabalho: tratar a demanda jovem como estrutural, que acompanha essas pessoas quando envelhecem, ou como uma fase.
O custo do erro é dos dois lados: subestimar a tendência perde mercado; superestimar gasta com distribuição sem demanda. Para isso eu preciso saber não só SE os jovens bebem menos, mas QUEM bebe menos.`);

s = conteudo("Abertura", "Hipótese e perguntas");
texto(s, "Na mesma idade (18 a 24 anos), o consumo abusivo de álcool diminui de uma geração para a seguinte, nos dois sexos e em todas as faixas de escolaridade, e isso não é uma tendência geral da população.",
  { x: 0.6, y: 1.35, w: 12.1, h: 1.0, fontSize: 18, italic: true, color: C.text2 });
const perguntas = [
  ["P1", "Quanto cada geração difere da anterior, aos 18-24?"],
  ["P2", "A diferença ocorre em todas as faixas de escolaridade?"],
  ["P3", "É efeito de geração ou da época?"],
  ["P4", "É igual entre homens e mulheres?"],
  ["P5", "Quais capitais concentram as maiores diferenças?"],
];
perguntas.forEach(([p, q], i) => {
  const x = 0.6 + i * 2.48;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.75, w: 2.25, h: 3.1, rectRadius: 0.12, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: "card_" + p });
  texto(s, p, { x: x + 0.2, y: 2.95, w: 1.85, h: 0.8, fontSize: 36, bold: true, color: C.accent1, fontFace: THEME.headFontFace });
  texto(s, q, { x: x + 0.2, y: 3.85, w: 1.85, h: 1.9, fontSize: 16 });
});
texto(s, "Consumo abusivo = 5+ doses (homens) ou 4+ doses (mulheres) numa ocasião, nos últimos 30 dias (indicador oficial do Vigitel).",
  { x: 0.6, y: 6.15, w: 12.1, h: 0.5, fontSize: 12, color: C.text2 });
s.addNotes(`Hipótese e perguntas (1 min).
A hipótese: na mesma idade, cada geração bebe em excesso menos que a anterior, nos dois sexos, em todas as classes, e isso não é só uma tendência da época.
Ela se desdobra em cinco perguntas, que vou responder uma a uma. Uma definição importante: "consumo abusivo" é o indicador oficial do Ministério: cinco ou mais doses para homens, quatro ou mais para mulheres, numa mesma ocasião, nos últimos 30 dias. Não mede dependência; mede episódios de exagero.`);

// ================================================================ DADOS E METODO
pres.addSection({ title: "Dados e método" });
s = conteudo("Dados e método", "Dados e pipeline no Databricks");
const etapas = [["Site do Ministério", "ZIP oficial, SHA-256"], ["Bronze", "cópia fiel, 486 colunas"], ["Silver", "2010+, regras S1-S11"], ["Gold", "estrela: fato + 6 dimensões"], ["Qualidade", "16 regras, 0 violações"], ["Análise", "P1-P5, sensibilidades"]];
etapas.forEach(([t, d], i) => {
  const x = 0.6 + i * 2.1;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.55, w: 1.8, h: 1.35, rectRadius: 0.1, fill: { color: i === 3 ? C.accent1 : C.background2 }, line: { color: i === 3 ? C.accent1 : C.background2 }, objectName: "etapa_" + i });
  texto(s, t, { x: x + 0.1, y: 1.65, w: 1.6, h: 0.45, fontSize: 15, bold: true, align: "center", color: i === 3 ? C.background1 : C.text2 });
  texto(s, d, { x: x + 0.1, y: 2.12, w: 1.6, h: 0.7, fontSize: 12, align: "center", color: i === 3 ? C.background1 : C.text1 });
  if (i < etapas.length - 1) s.addShape(pres.shapes.RIGHT_TRIANGLE, { x: x + 1.86, y: 2.08, w: 0.18, h: 0.3, rotate: 0, fill: { color: C.accent4 }, line: { color: C.accent4 } });
});
destaque(s, "833.217", "entrevistas telefônicas, 2006-2024 (18 edições; não existe 2022)", 0.6, 3.45, 3.8);
destaque(s, "615.877", "entrevistas de 2010 em diante na análise (pergunta de doses atual)", 4.75, 3.45, 3.8, C.text2);
destaque(s, "61.035", "jovens de 18 a 24 anos das três gerações", 8.9, 3.45, 3.8, C.accent2);
texto(s, "Fonte: Ministério da Saúde, Vigitel Brasil 2006-2024, base harmonizada (24/08/2026), capitais e Distrito Federal. Licença CC BY-ND 3.0. Prevalências ponderadas pelo peso oficial, normalizado por edição, e padronizadas pela idade nas comparações entre gerações.",
  { x: 0.6, y: 5.75, w: 12.1, h: 0.8, fontSize: 12, color: C.text2 });
s.addNotes(`Dados e pipeline (1 min 30 s).
A base é o Vigitel, o inquérito telefônico anual do Ministério da Saúde nas 27 capitais: 833 mil entrevistas de 2006 a 2024, num único arquivo harmonizado publicado em agosto de 2026.
O pipeline segue a arquitetura em camadas no Databricks: o ZIP oficial vai para um Volume, conferido pelo SHA-256; a bronze é uma cópia fiel das 486 colunas; a silver aplica as regras S1 a S11, que vêm das decisões de tratamento; a gold é um modelo estrela, com a entrevista como fato e seis dimensões; depois vêm 16 regras de qualidade, todas sem violação, e a análise.
Uso as edições de 2010 em diante porque foi quando a pergunta de doses passou a ser "cinco ou mais"; antes era "mais do que cinco".`);

s = conteudo("Dados e método", "A série histórica não mostra queda entre os jovens");
figura(s, "f01_serie_faixa_etaria.png", 0.6, 1.35, 8.6, 5.4);
texto(s, [
  { text: "Jovens (azul): 21,9% em 2010 e 22,7% em 2024", options: { bullet: true, breakLine: true } },
  { text: "2022 não existe", options: { bullet: true, breakLine: true } },
  { text: "Em 2023-2024 entra o celular e muda o filtro do questionário", options: { bullet: true, breakLine: true } },
  { text: "Comparar anos mistura comportamento com método", options: { bullet: true, bold: true, color: C.accent2 } },
], { x: 9.5, y: 1.6, w: 3.25, h: 4.8, fontSize: 16, paraSpaceAfter: 10 });
s.addNotes(`Série histórica (1 min).
Este é o primeiro olhar. A linha azul são os jovens de 18 a 24, a laranja, os adultos de 35 a 44. Comparando 2010 com 2024, os jovens ficam praticamente iguais: 21,9 e 22,7%.
Só que a comparação entre anos tem três armadilhas: não existe 2022; em 2023 e 2024 a pesquisa passou a ligar para celular; e em 2024 mudou a pergunta que abre o bloco de álcool. Ou seja, comparar 2010 com 2024 mistura mudança de comportamento com mudança de método. Isso me levou à principal decisão do trabalho, no próximo slide.`);

s = conteudo("Dados e método", "Decisão-chave: comparar gerações, e não anos");
figura(s, "f02_cobertura_geracoes.png", 0.6, 1.35, 7.6, 3.6);
const geracoes = [["Millennials", "nascidos em 1986-1992", "observados aos 18-24 em 2010-2016, só fixo", C.accent4], ["Zillennials", "nascidos em 1993-1998", "observados em 2011-2021, só fixo", C.accent3], ["Geração Z", "nascidos em 1999-2006", "observados em 2017-2024, 33% celular", C.accent1]];
geracoes.forEach(([g, n, o, cor], i) => {
  const y = 1.45 + i * 1.2;
  s.addShape(pres.shapes.OVAL, { x: 8.6, y: y + 0.12, w: 0.42, h: 0.42, fill: { color: cor }, line: { color: cor } });
  texto(s, g, { x: 9.2, y, w: 3.5, h: 0.42, fontSize: 18, bold: true, color: C.text2 });
  texto(s, n + "; " + o, { x: 9.2, y: y + 0.42, w: 3.5, h: 0.7, fontSize: 13 });
});
texto(s, [
  { text: "Geração = ano da pesquisa menos a idade. Sempre na mesma idade (18 a 24).", options: { bullet: true, breakLine: true } },
  { text: "Junta vários anos por geração: margem de erro de ±1 p.p., contra ±3 de um ano isolado.", options: { bullet: true, breakLine: true } },
  { text: "Millennials x zillennials: comparação toda por telefone fixo, sem mudança de método.", options: { bullet: true } },
], { x: 0.6, y: 5.2, w: 12.1, h: 1.6, fontSize: 15, paraSpaceAfter: 6 });
s.addNotes(`Decisão-chave (1 min 30 s).
Em vez de comparar anos, eu comparo gerações na mesma idade. A geração é o ano da pesquisa menos a idade: millennials nascidos de 1986 a 1992, zillennials, a geração de transição, de 1993 a 1998, e a geração Z de 1999 a 2006, sempre observados aos 18-24 anos.
O gráfico mostra quantos jovens de cada geração foram entrevistados em cada edição, e a linha laranja mostra a entrada do celular.
Duas vantagens: juntando vários anos por geração, a margem de erro cai de três para um ponto; e a comparação millennials contra zillennials é toda feita por telefone fixo, sem mudança de método. Essa foi uma das 14 decisões de tratamento, todas registradas com alternativas e motivos no relatório.`);

s = conteudo("Dados e método", "Na mesma idade, de fato: padronizar pela idade");
figura(s, "f03a_idade_por_geracao.png", 0.6, 1.35, 8.4, 3.9);
destaque(s, "4% x 29%", "do peso vem dos jovens de 18 anos: millennials x geração Z", 9.3, 1.5, 3.4, C.accent2);
texto(s, [
  { text: "O consumo abusivo sobe com a idade: cerca de 14% aos 18 e 27% aos 24", options: { bullet: true, breakLine: true } },
  { text: "A janela 2010-2024 mostra os millennials mais velhos e a geração Z mais nova", options: { bullet: true, breakLine: true } },
  { text: "Correção (D14): média das 7 idades, com peso igual para cada uma, nas mesmas idades para todas as gerações", options: { bullet: true, bold: true, color: C.accent1 } },
], { x: 0.6, y: 5.4, w: 12.1, h: 1.45, fontSize: 15, paraSpaceAfter: 6 });
s.addNotes(`Padronização pela idade (1 min 30 s).
Fixar a faixa de 18 a 24 anos não basta. Como a série começa em 2010 e termina em 2024, os millennials aparecem sobretudo aos 22, 23 e 24 anos, e a geração Z sobretudo aos 18 e 19. Do peso dos millennials, só 4% vem dos jovens de 18 anos; na geração Z, 29%.
O gráfico da esquerda mostra por que isso importa: o consumo abusivo sobe com a idade, de cerca de 14% aos 18 para 27% aos 24. Sem corrigir, a geração Z parece beber menos só porque foi entrevistada mais nova.
A correção é uma padronização direta: calculo a prevalência de cada idade e tiro a média das sete, com o mesmo peso para todas as gerações. Essa decisão, a D14, entrou na revisão da análise e mudou o resultado principal, como vocês vão ver.`);

s = conteudo("Dados e método", "Limitação: o celular muda a resposta");
figura(s, "f12_modo_coleta_2023.png", 0.6, 1.35, 7.4, 5.4);
destaque(s, "+11,5 p.p.", "diferença entre celular e fixo no mesmo ano (2023), todas as idades", 8.4, 1.6, 4.3, C.accent2);
texto(s, [
  { text: "Quem tem fixo é outro público (mais velho, casa estruturada)", options: { bullet: true, breakLine: true } },
  { text: "No celular a pessoa responde sozinha, sem a família por perto", options: { bullet: true, breakLine: true } },
  { text: "O peso amostral não corrige isso: por isso as sensibilidades", options: { bullet: true } },
], { x: 8.4, y: 3.7, w: 4.3, h: 2.8, fontSize: 15, paraSpaceAfter: 8 });
s.addNotes(`Limitação do método (1 min).
Em 2023 o Vigitel entrevistou metade por fixo e metade por celular, e isso permite uma comparação no mesmo ano: quem respondeu pelo celular declarou 27% de consumo abusivo, contra 15,5% no fixo.
Parte disso é que o fixo alcança outro público, mais velho. Parte é que, no celular, a pessoa responde sozinha, sem constrangimento. O peso amostral não corrige isso.
Por isso, mais adiante, mostro sensibilidades: por exemplo, a geração Z só com entrevistas por fixo. Como o celular tende a aumentar o consumo declarado, a sensibilidade só por fixo mostra quanto do resultado pode vir do modo de coleta.`);

// ================================================================ RESULTADOS
pres.addSection({ title: "Resultados" });
s = pres.addSlide({ masterName: "SECAO", sectionTitle: "Resultados" });
s.addText("Resultados", { placeholder: "title" });
s.addText("P1 a P5, robustez e veredito", { placeholder: "body" });
s.addNotes(`Agora os resultados, pergunta por pergunta.`);

s = conteudo("Resultados", "P1. Na mesma idade, a geração Z não bebe menos");
figura(s, "f03_p1_geracoes.png", 0.6, 1.35, 7.6, 5.4);
destaque(s, "+1,1 p.p.", "geração Z em relação aos millennials, aos 18-24, padronizada pela idade (IC 95%: −1,1 a +3,3)", 8.6, 1.6, 4.1);
texto(s, [
  { text: "21,1% → 22,2% → 22,3%; nenhuma diferença significativa", options: { bullet: true, breakLine: true } },
  { text: "Sem padronizar (círculo), aparecia −2,1 p.p.: a queda vinha da idade", options: { bullet: true, breakLine: true } },
  { text: "Padronizada também pela escolaridade (losango): quase igual", options: { bullet: true } },
], { x: 8.6, y: 3.6, w: 4.1, h: 3.0, fontSize: 15, paraSpaceAfter: 8 });
s.addNotes(`P1 (1 min).
Na mesma idade, os millennials tinham 21,1% de consumo abusivo; os zillennials, 22,2%; a geração Z, 22,3%. A diferença da geração Z para os millennials é de mais 1,1 ponto, e o intervalo inclui o zero: não há queda.
O círculo branco é a leitura sem padronizar, a da primeira versão deste trabalho: ali aparecia uma queda de 2,1 pontos. Ela vinha de a geração Z ter sido entrevistada mais nova.
O losango é a média padronizada também pela escolaridade dos millennials, e quase não muda: a escolaridade não explica nada aqui.
Mas o total esconde dois movimentos opostos, no próximo slide.`);

s = conteudo("Resultados", "P4. Os sexos estão convergindo");
figura(s, "f04_p4_convergencia_sexos.png", 0.6, 1.35, 7.6, 5.4);
destaque(s, "14 → 3,5", "p.p. de distância entre homens e mulheres, de millennials para geração Z", 8.6, 1.6, 4.1, C.accent2);
texto(s, [
  { text: "Homens: −4,0 p.p. (28,1% → 24,0%)", options: { bullet: true, breakLine: true, color: C.accent1, bold: true } },
  { text: "Mulheres: +6,4 p.p. (14,1% → 20,5%)", options: { bullet: true, breakLine: true, color: C.accent2, bold: true } },
  { text: "As mulheres sobem mais do que os homens caem", options: { bullet: true } },
], { x: 8.6, y: 3.6, w: 4.1, h: 3.0, fontSize: 16, paraSpaceAfter: 8 });
s.addNotes(`P4, o achado central (1 min 30 s).
Este é o slide mais importante. O total estável esconde dois movimentos opostos. Entre os homens, o consumo abusivo cai de 28,1% para 24,0%: quatro pontos. Entre as mulheres, sobe de 14,1% para 20,5%: mais de seis pontos.
A distância entre os sexos, que era de 14 pontos entre os millennials, caiu para 3,5 na geração Z. Para o negócio, isso muda o público: o "jovem que bebe menos" é, no máximo, o homem jovem; a mulher jovem é um público crescente entre quem bebe.`);

s = conteudo("Resultados", "Por que muda: homens moderam, mais mulheres bebem");
figura(s, "f05_decomposicao.png", 0.6, 1.3, 12.1, 3.95);
cartao(s, 0.6, 5.35, 5.9, 1.45, "Homens", "Quase o mesmo tanto bebe (43% → 41%); quem bebe exagera menos (65% → 58%)", C.accent1, "card_h");
cartao(s, 6.85, 5.35, 5.9, 1.45, "Mulheres", "Mais bebem (25% → 35%); o exagero entre quem bebe fica estável (56% → 58%)", C.accent2, "card_m");
s.addNotes(`Decomposição (1 min).
Separei o consumo abusivo em duas partes: quantos jovens bebem pelo menos uma vez por mês, em cinza, e, entre os que bebem, quantos exageram, em azul ou laranja. Tudo padronizado pela idade.
Nos homens, a proporção que bebe quase não muda; o que cai é o exagero entre quem bebe. Nas mulheres, o exagero entre quem bebe é estável; o que sobe é a proporção de mulheres que bebem.
Implicação: o homem jovem não abandonou o álcool, ele modera um pouco. A mulher jovem entrou no consumo.`);

s = conteudo("Resultados", "P2. Por escolaridade, nenhuma diferença significativa");
figura(s, "f06_p2_escolaridade.png", 0.6, 1.4, 8.2, 4.4);
texto(s, [
  { text: "De +0,6 a +2,0 p.p. nas três faixas, todas dentro da margem de erro", options: { bullet: true, breakLine: true } },
  { text: "Sem os casos de escolaridade estimada pelo Ministério: mesmo resultado", options: { bullet: true, breakLine: true } },
  { text: "Não há queda concentrada em nenhuma classe, nem queda ampla", options: { bullet: true, bold: true } },
], { x: 9.1, y: 1.6, w: 3.6, h: 4.5, fontSize: 15, paraSpaceAfter: 10 });
s.addNotes(`P2 (1 min).
Por escolaridade, a proxy de classe social, a geração Z fica de 0,6 a 2 pontos acima dos millennials nas três faixas, e nenhuma diferença é significativa. A sensibilidade sem os casos em que o Ministério estimou a escolaridade dá o mesmo resultado.
Leitura para a decisão de nicho ou massa: não há queda em nenhuma faixa. Então não há um nicho de jovens escolarizados que bebe menos, mas também não há uma queda de massa. A diferença relevante não é de classe, é de sexo.`);

s = conteudo("Resultados", "P3. Os jovens subiram menos que a época");
figura(s, "f07_p3_jovens_x_adultos.png", 0.6, 1.4, 7.4, 3.8);
destaque(s, "−2,7 p.p.", "jovens (+1,1) em relação aos adultos de 35-44 (+3,8) no mesmo período (IC 95%: −5,1 a −0,3)", 8.4, 1.6, 4.3);
texto(s, "Os jovens não beberam menos, mas cresceram menos que a tendência geral: um efeito relativo de geração, e não uma queda.",
  { x: 0.6, y: 5.5, w: 12.1, h: 1.0, fontSize: 16 });
s.addNotes(`P3, parte 1 (1 min).
Uma pergunta natural: e se todo mundo mudou no mesmo período? Comparei os jovens com os adultos de 35 a 44 anos nas mesmas edições em que cada geração foi observada, os dois grupos padronizados pela idade. Os jovens subiram 1,1 ponto; os adultos, 3,8. A diferença das diferenças é de menos 2,7 pontos, e o intervalo não inclui o zero.
Então a época puxou o consumo para cima, e os jovens acompanharam menos. É um efeito de geração relativo, não uma queda absoluta.`);

s = conteudo("Resultados", "P3. Ao envelhecer, as curvas ficam paralelas");
figura(s, "f08_p3_envelhecimento.png", 0.6, 1.35, 12.1, 4.6);
texto(s, "Homens zillennials: 1,4 p.p. abaixo dos millennials aos 18-24 (26,7% x 28,1%) e aos 25-29 (33,4% x 34,8%): curvas paralelas, sem sinal de adiamento. Mulheres zillennials acima nas duas faixas; a geração Z ainda é jovem demais.",
  { x: 0.6, y: 6.0, w: 12.1, h: 0.85, fontSize: 15 });
s.addNotes(`P3, parte 2 (1 min).
Acompanhei cada geração ao envelhecer, padronizando pela idade dentro de cada faixa. Os homens zillennials ficam cerca de 1,4 ponto abaixo dos millennials tanto aos 18-24 quanto aos 25-29: as curvas são paralelas. Na versão sem padronizar, parecia que eles começavam bem abaixo e alcançavam os millennials depois, o que sugeria adiamento; com a correção, esse sinal some.
As mulheres zillennials ficam acima das millennials nas duas faixas. A geração Z ainda é jovem demais para essa comparação; é uma pergunta para as próximas edições do Vigitel.`);

s = conteudo("Resultados", "P5. Nenhuma região muda de forma clara");
figura(s, "f09_p5_mapa_capitais.png", 0.6, 1.3, 6.0, 5.6);
texto(s, [
  { text: "Só Aracaju fora da margem de erro (−6,1 p.p.); com 27 capitais, uma é esperada só pelo acaso", options: { bullet: true, breakLine: true } },
  { text: "Nenhuma região significativa (de −0,5 p.p. no Norte a +4,5 no Sul)", options: { bullet: true, breakLine: true } },
  { text: "Tendência, dentro da margem: a maioria do Nordeste cai; Sul e Sudeste (exceto o Rio) sobem", options: { bullet: true, breakLine: true } },
  { text: "Capital inconclusiva: usar a região como apoio", options: { bullet: true, bold: true } },
], { x: 7.0, y: 1.5, w: 5.7, h: 5.2, fontSize: 15, paraSpaceAfter: 10 });
s.addNotes(`P5 (1 min 30 s).
Para quem decide distribuição, o mapa: cada quadrado é uma capital; azul é queda do consumo abusivo da geração Z em relação aos millennials, vermelho é alta; borda preta é diferença fora da margem de erro. Nas capitais, a padronização usa três faixas de idade, porque há poucas entrevistas por idade.
Só Aracaju tem diferença clara, e com 27 capitais uma é esperada pelo acaso. Nenhuma região tem diferença significativa. Há uma tendência, dentro da margem: a maior parte do Nordeste cai, e Sul e Sudeste sobem.
Regra de leitura para um empresário: se a sua capital é inconclusiva, use o dado da sua região, que tem mais entrevistas. O detalhe com as margens está no slide do apêndice.`);

s = conteudo("Resultados", "Robustez: alta feminina firme, queda masculina frágil");
figura(s, "f11_sensibilidades.png", 0.6, 1.35, 8.0, 5.4);
texto(s, [
  { text: "Seis cenários e, na última linha, a leitura sem padronizar", options: { bullet: true, breakLine: true } },
  { text: "Mulheres: +5,1 a +8,1 p.p., significativa em cinco dos seis", options: { bullet: true, breakLine: true, color: C.accent2, bold: true } },
  { text: "Homens: −2,4 a −4,1 p.p.; perde a significância aos 18-21, sem 2024 e só por fixo", options: { bullet: true, breakLine: true, color: C.accent1, bold: true } },
  { text: "Sem padronizar, a queda total aparecia: era efeito da idade", options: { bullet: true } },
], { x: 8.9, y: 1.6, w: 3.8, h: 5.0, fontSize: 15, paraSpaceAfter: 10 });
s.addNotes(`Robustez (1 min).
Refiz tudo em seis cenários, um para cada decisão de tratamento que poderia mudar o resultado: a base, só 18 a 21 anos, sem 2024, geração Z só por telefone fixo, sem os anos de pandemia, sem a escolaridade estimada. Cada cenário é padronizado pelas idades que todas as gerações têm.
A alta das mulheres é robusta: significativa em cinco dos seis; só com a geração Z por fixo o intervalo inclui o zero. A queda dos homens é frágil: fica entre 2,4 e 4,1 pontos e perde a significância em três cenários.
A última linha é a leitura sem padronizar: é ali que aparecia a queda total. Ela era efeito da idade, não da geração.`);

s = conteudo("Resultados", "Veredito: hipótese refutada");
const criterios = [
  ["(a)", "A prevalência diminui da geração Z para os millennials?", "Não: +1,1 p.p. (−1,1 a +3,3), na mesma idade", false],
  ["(b)", "A queda ocorre nos dois sexos e nas três faixas de escolaridade?", "Não: homens −4,0; mulheres +6,4; escolaridade sem significância", false],
  ["(c)", "É mais que a tendência geral (adultos de 35-44)?", "Sim: jovens +1,1 contra adultos +3,8 (diferença de −2,7; IC −5,1 a −0,3)", true],
];
criterios.forEach(([c, q, r, ok], i) => {
  const y = 1.5 + i * 1.45;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y, w: 12.1, h: 1.25, rectRadius: 0.1, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: "criterio_" + i });
  s.addShape(pres.shapes.OVAL, { x: 0.85, y: y + 0.27, w: 0.7, h: 0.7, fill: { color: ok ? C.accent6 : C.accent5 }, line: { color: ok ? C.accent6 : C.accent5 } });
  texto(s, ok ? "✓" : "✗", { x: 0.85, y: y + 0.27, w: 0.7, h: 0.7, fontSize: 24, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0 });
  texto(s, c + " " + q, { x: 1.85, y: y + 0.15, w: 10.6, h: 0.5, fontSize: 17, bold: true, color: C.text2 });
  texto(s, r, { x: 1.85, y: y + 0.65, w: 10.6, h: 0.5, fontSize: 15 });
});
texto(s, "Na mesma idade, a geração Z não bebe menos: os sexos é que convergem.", { x: 0.6, y: 6.0, w: 12.1, h: 0.6, fontSize: 22, bold: true, color: C.accent1, fontFace: THEME.headFontFace });
s.addNotes(`Veredito (1 min).
Apliquei os critérios de refutação que estão no README desde a versão 2 do objetivo; a correção pela idade mudou o cálculo, não os critérios. Critério (a): na mesma idade, a geração Z não bebe em excesso menos que os millennials. Falha. Critério (b): a queda não acontece nos dois sexos, e por escolaridade nenhuma diferença é significativa. Falha. Critério (c): os jovens subiram menos que os adultos no mesmo período. Atendido.
Então a hipótese é refutada no que tem de central. Na primeira versão, sem padronizar, eu tinha concluído que ela era só parcialmente refutada; a revisão do método mudou a conclusão, e isso é um resultado válido de MVP: o aprendizado é que a manchete "a geração Z bebe menos" não se sustenta na mesma idade.`);

// ================================================================ EXPLORACAO
pres.addSection({ title: "Exploração" });
s = conteudo("Exploração", "O que anda junto com o consumo abusivo entre jovens");
figura(s, "f13_correlatos.png", 0.6, 1.3, 6.4, 5.6);
texto(s, [
  { text: "21 características do Vigitel, ajustadas por sexo e edição", options: { bullet: true, breakLine: true } },
  { text: "Cigarro e vape: +38 e +34 p.p.", options: { bullet: true, breakLine: true, bold: true } },
  { text: "Depressão: +8 p.p. só entre os jovens (nos adultos, zero)", options: { bullet: true, breakLine: true, bold: true } },
  { text: "Tela 3h+/dia: +7 p.p. (o celular não substitui o bar)", options: { bullet: true, breakLine: true, bold: true } },
  { text: "Hipertensão, diabetes, inatividade: sem associação, como esperado", options: { bullet: true, breakLine: true } },
  { text: "Associação não é causa; com 21 testes, ~1 pode ser acaso", options: { bullet: true, italic: true, color: C.accent2 } },
], { x: 7.3, y: 1.5, w: 5.4, h: 5.3, fontSize: 15, paraSpaceAfter: 9 });
s.addNotes(`Exploração (1 min 30 s).
Como bônus, o Vigitel pergunta muito mais que álcool. Testei 21 características contra o consumo abusivo entre jovens, sempre ajustando por sexo e ano. Classifiquei cada uma como provável, incerta ou improvável antes de olhar os dados.
Os mais fortes, esperados: quem fuma ou usa cigarro eletrônico bebe em excesso muito mais.
O mais curioso: diagnóstico de depressão está associado a mais consumo abusivo só entre os jovens; entre os adultos, a diferença é zero. Tem amostra pequena e não passa no teste mais rigoroso, então é uma pista.
E um que contraria o senso comum: jovens com três horas ou mais de tela no lazer bebem mais em excesso, e não menos. A ideia de que a geração Z troca a balada pelo celular não aparece nos dados.
Cuidado: associação não é causa, e com 21 testes cerca de um pode dar positivo por acaso.`);

s = conteudo("Exploração", "Quatro destaques, em números brutos");
figura(s, "f14_correlatos_destaque.png", 0.6, 1.4, 12.1, 4.2);
destaque(s, "54%", "dos jovens que usam cigarro eletrônico bebem em excesso (20% de quem não usa)", 0.6, 5.55, 5.8, C.accent5);
destaque(s, "24%", "de quem passa 3h+ por dia em telas no lazer (18% de quem passa menos)", 6.9, 5.55, 5.8, C.accent5);
s.addNotes(`Destaques (45 s).
Em números brutos, para fixar: 54% dos jovens que usam cigarro eletrônico bebem em excesso, contra 20% de quem não usa. Entre os jovens com diagnóstico de depressão, 30% contra 21%. Com três horas ou mais de tela, 24% contra 18%. E quem trabalha, com renda própria, 25% contra 17%.
Para o negócio: o consumo pesado se concentra num público que também usa nicotina e passa muito tempo em telas, o que é útil para segmentação e comunicação.`);

// ================================================================ CONCLUSAO
pres.addSection({ title: "Conclusão" });
s = conteudo("Conclusão", "O que isso significa para a empresa de bebidas");
cartao(s, 0.6, 1.5, 3.85, 3.9, "Sem queda para apostar", "Na mesma idade, o jovem não bebe em excesso menos que antes, em nenhuma classe. A linha sem álcool para jovens não se apoia neste indicador.", C.accent1, "card_imp1");
cartao(s, 4.74, 1.5, 3.85, 3.9, "Homens moderam", "Entre os homens que bebem, menos exageram (65% → 58%). Há espaço para baixo teor, mas a queda é frágil.", C.accent1, "card_imp2");
cartao(s, 8.88, 1.5, 3.85, 3.9, "Público feminino em alta", "Mais mulheres jovens bebem (25% → 35%). Comunicação e portfólio não podem tratar o público jovem como masculino.", C.accent2, "card_imp3");
texto(s, "Nicho ou massa: nenhuma classe cai, então nenhum dos dois tem base. Estrutural ou fase: sem sinal de adiamento; acompanhar a geração Z aos 25-29.",
  { x: 0.6, y: 5.75, w: 12.1, h: 0.8, fontSize: 16, italic: true, color: C.text2 });
s.addNotes(`Implicações (1 min 30 s).
Voltando às duas decisões. Nicho ou massa: os dados não sustentam nenhum dos dois, porque, na mesma idade, nenhuma faixa de escolaridade bebe em excesso menos. A aposta em linhas sem álcool para jovens pode até ter outras razões, mas não encontra apoio neste indicador.
O que os dados mostram são dois ajustes de rota. Primeiro, entre os homens que bebem, menos exageram: há espaço para baixo teor e moderação, com cautela, porque essa queda é frágil. Segundo, a mulher jovem é um público crescente entre quem bebe; tratar o jovem como público masculino é um erro.
Estrutural ou fase: a correção pela idade tirou o sinal de adiamento. Vale acompanhar a geração Z quando ela chegar aos 25-29.`);

s = conteudo("Conclusão", "Qualidade, limitações e próximos passos");
cartao(s, 0.6, 1.5, 5.9, 4.9, "Qualidade e limitações", ["16 regras de qualidade, nenhuma violação", "Vazios são pulos do questionário, não perda de dado", "Só capitais e Distrito Federal", "Autodeclaração por telefone; celular em 2023-2024", "Geração e época não se separam totalmente", "Idade corrigida por padronização (D14)", "Escolaridade como proxy de renda"], C.accent1, "card_lim");
cartao(s, 6.85, 1.5, 5.9, 4.9, "Próximos passos", ["Executar e documentar no Databricks", "Confirmar os correlatos (depressão e telas) por geração", "Acompanhar a geração Z aos 25-29 nas próximas edições", "Testar apostas online quando a resposta de 2024 for publicada"], C.accent2, "card_prox");
s.addNotes(`Qualidade e próximos passos (1 min).
Sobre a qualidade: 16 regras automáticas, nenhuma violação. Quase todo vazio da base é pulo de questionário, e não dado perdido.
As limitações estão declaradas: só capitais, autodeclaração por telefone, a troca para o celular, a dificuldade de separar geração de época, e a escolaridade como substituta da renda.
Próximos passos: a execução documentada no Databricks, confirmar os achados exploratórios por geração, acompanhar a geração Z quando chegar aos 25-29, e testar apostas online assim que o Ministério publicar essa resposta.`);

s = pres.addSlide({ masterName: "CAPA", sectionTitle: "Conclusão" });
s.addText("A geração Z bebe menos? Na mesma idade, não", { placeholder: "title" });
s.addText([
  { text: "Homens −4 p.p., mulheres +6 p.p.: os sexos convergem; sem diferença por classe", options: { breakLine: true } },
  { text: "Obrigado. Perguntas?", options: { fontSize: 22, bold: true, color: C.background1 } },
], { placeholder: "body" });
s.addNotes(`Encerramento (30 s).
Então, a geração Z bebe menos? Na mesma idade, não. Os homens bebem em excesso um pouco menos, cerca de quatro pontos, e as mulheres, seis pontos mais: os sexos estão convergindo, e não há diferença por classe social. Obrigado; fico à disposição para perguntas.`);

// ================================================================ APENDICE
pres.addSection({ title: "Apêndice" });
s = conteudo("Apêndice", "Apêndice. P5: diferença e margem de erro por capital");
figura(s, "f10_p5_capitais.png", 0.6, 1.25, 6.4, 5.65);
texto(s, [
  { text: "Diferença geração Z − millennials aos 18-24 anos", options: { bullet: true, breakLine: true } },
  { text: "Azul: intervalo de 95% não inclui o zero", options: { bullet: true, breakLine: true } },
  { text: "Cerca de 390 jovens da geração Z por capital: margem de ±5 a 6 p.p.", options: { bullet: true } },
], { x: 7.3, y: 1.5, w: 5.4, h: 3.0, fontSize: 15, paraSpaceAfter: 10 });
s.addNotes(`Apêndice, para perguntas sobre capitais específicas: cada linha mostra a diferença e o intervalo de 95%. Em azul, as capitais com diferença fora da margem de erro.`);

(async () => {
  await pres.writeFile({ fileName: SAIDA });
  await applyTheme(SAIDA, THEME);
  console.log("ok", SAIDA);
})();
