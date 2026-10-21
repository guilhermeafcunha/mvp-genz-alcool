// Gera a apresentacao do MVP (pptxgenjs). Uso: node gerar_apresentacao.js <raiz_do_repositorio> <saida.pptx> <apply_theme.js>
// As figuras vem de resultados/figuras/ (pipeline), figuras_relatorio_v2/ (pre-analise) e evidencias/databricks/ (capturas).
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const [RAIZ, SAIDA, APPLY] = process.argv.slice(2);
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
// Cores das camadas (fixas, nao seguem o tema)
const CAMADA = { raw: "6B6A64", bronze: "9C5B2E", silver: "6E7781", gold: "A87A0C" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.title = "Geração Z e álcool: a geração Z bebe menos?";
pres.author = "Guilherme Augusto Fontes Cunha";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

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
// Encaixa a figura na caixa (x, y, w, h), centralizada; devolve a posicao final
function figura(slide, nome, x, y, w, h, borda) {
  const arq = path.join(RAIZ, nome);
  const t = tamanhoPng(arq);
  const r = Math.min(w / t.w, h / t.h);
  const iw = t.w * r, ih = t.h * r;
  const pos = { x: x + (w - iw) / 2, y: y + (h - ih) / 2, w: iw, h: ih };
  const op = Object.assign({ path: arq, objectName: path.basename(nome), altText: path.basename(nome) }, pos);
  if (borda) op.line = { color: THEME.colors.accent4, width: 0.75 };
  slide.addImage(op);
  return pos;
}
function texto(slide, t, o) {
  slide.addText(t, Object.assign({ isTextBox: true, fontSize: 16, color: C.text1, valign: "top", margin: 0.05 }, o));
}
function lista(itens, extra) {
  return itens.map((t, i) => {
    const [txt, o] = Array.isArray(t) ? t : [t, {}];
    return { text: txt, options: Object.assign({ bullet: true, breakLine: i < itens.length - 1 }, extra || {}, o) };
  });
}
function destaque(slide, numero, rotulo, x, y, w, cor) {
  texto(slide, numero, { x, y, w, h: 0.9, fontSize: 44, bold: true, color: cor || C.accent1, fontFace: THEME.headFontFace, valign: "bottom" });
  texto(slide, rotulo, { x, y: y + 0.95, w, h: 0.8, fontSize: 14, color: C.text1 });
}
function cartao(slide, x, y, w, h, titulo, corpo, cor, nome, tam) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: nome });
  texto(slide, titulo, { x: x + 0.25, y: y + 0.2, w: w - 0.5, h: 0.5, fontSize: 18, bold: true, color: cor || C.accent1 });
  const c = Array.isArray(corpo) ? lista(corpo) : corpo;
  texto(slide, c, { x: x + 0.25, y: y + 0.75, w: w - 0.5, h: h - 0.95, fontSize: tam || 15, paraSpaceAfter: 6 });
}
function circuloNum(slide, n, x, y, cor, d, tam) {
  d = d || 0.55;
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: cor || C.accent1 }, line: { color: cor || C.accent1 } });
  texto(slide, String(n), { x, y, w: d, h: d, fontSize: tam || 16, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0 });
}
function legenda(slide, t, x, y, w) {
  texto(slide, t, { x, y, w, h: 0.35, fontSize: 11, italic: true, color: C.text2 });
}
function linha(slide, x1, y1, x2, y2, cor) {
  slide.addShape(pres.shapes.LINE, {
    x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001,
    flipV: (x2 > x1) !== (y2 > y1) && y1 !== y2, line: { color: cor || THEME.colors.accent4, width: 1.5 },
  });
}
function seta(slide, x, y) {
  slide.addShape(pres.shapes.RIGHT_TRIANGLE, { x, y, w: 0.2, h: 0.32, fill: { color: C.accent4 }, line: { color: C.accent4 } });
}
function conteudo(secao, titulo) {
  const s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: secao });
  s.addText(titulo, { placeholder: "title" });
  return s;
}
function divisoria(secao, titulo, sub, notas) {
  pres.addSection({ title: secao });
  const s = pres.addSlide({ masterName: "SECAO", sectionTitle: secao });
  s.addText(titulo, { placeholder: "title" });
  s.addText(sub, { placeholder: "body" });
  s.addNotes(notas);
  return s;
}
const FIG = (n) => "resultados/figuras/" + n;
const AED = (n) => "figuras_relatorio_v2/" + n;
const EVI = (n) => "evidencias/databricks/" + n;

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
Bom dia. A pergunta deste MVP tem cara de manchete: a geração Z bebe menos? Eu fui verificar com os microdados oficiais do Ministério da Saúde, o Vigitel, e montei um pipeline de dados no Databricks para responder.
Spoiler: na mesma idade, não. O que muda é outra coisa: homens e mulheres jovens estão ficando parecidos.`);

s = conteudo("Abertura", "Por que este tema");
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 1.5, w: 12.1, h: 1.7, rectRadius: 0.12, fill: { color: C.text2 }, line: { color: C.text2 }, objectName: "manchete" });
texto(s, "“A geração Z bebe menos, e isso está dando prejuízo à indústria do álcool.”", { x: 0.95, y: 1.65, w: 11.4, h: 0.85, fontSize: 24, italic: true, color: C.background1, fontFace: THEME.headFontFace, valign: "middle" });
texto(s, "A afirmação que circula nas notícias de mercado e motivou o trabalho", { x: 0.95, y: 2.5, w: 11.4, h: 0.5, fontSize: 14, color: C.accent3 });
const motivos = [
  ["Verificar", "Todos temos percepções pessoais sobre como os jovens bebem. Quis testar a manchete com dados oficiais, e não com impressões."],
  ["Entender quem", "Não basta saber se bebem menos: interessa saber quais jovens, de que sexo e classe, e se a mudança é da geração."],
  ["Ir além", "O Vigitel pergunta muito mais que álcool. Os correlatos abrem outras investigações, com a metodologia certa."],
];
motivos.forEach(([t, d], i) => {
  const x = 0.6 + i * 4.12;
  circuloNum(s, i + 1, x, 3.6, i === 2 ? C.accent2 : C.accent1);
  texto(s, t, { x: x + 0.7, y: 3.6, w: 3.1, h: 0.55, fontSize: 19, bold: true, color: C.text2, valign: "middle" });
  texto(s, d, { x, y: 4.35, w: 3.85, h: 2.2, fontSize: 15 });
});
s.addNotes(`Por que este tema (1 min).
A motivação veio das notícias de mercado: elas dizem que a geração Z bebe menos e que isso está dando prejuízo à indústria de bebidas alcoólicas. Todos nós temos percepções pessoais sobre isso, mas eu quis investigar pelos dados.
Três objetivos: verificar se a afirmação é verdadeira no Brasil; entender quem, dentro do público jovem, muda; e aproveitar que o Vigitel pergunta muito mais que álcool para olhar o que anda junto com o consumo. Essa última parte, os correlatos, pode levar a muitas outras investigações interessantes, com a metodologia correta.`);

s = conteudo("Abertura", "O problema de negócio");
cartao(s, 0.6, 1.5, 5.9, 2.4, "Decisão 1: nicho ou massa?", "Se só os jovens mais escolarizados bebem menos, a linha sem álcool é um produto premium, de nicho. Se a queda atinge todas as classes, é mercado de massa.", C.accent1, "card_d1");
cartao(s, 6.85, 1.5, 5.9, 2.4, "Decisão 2: estrutural ou fase?", "Se a geração Z leva o hábito para a vida adulta, o investimento é de longo prazo. Se só adia o consumo, é uma fase de idade.", C.accent2, "card_d2");
texto(s, "Decisor: área de estratégia e portfólio de uma empresa de bebidas", { x: 0.6, y: 4.3, w: 12.1, h: 0.45, fontSize: 18, bold: true, color: C.text2 });
texto(s, lista([
  "Errar para nicho numa tendência ampla: perder mercado.",
  "Errar para massa numa tendência restrita: investir em distribuição sem demanda.",
  "Interesse secundário: saúde pública (prevenção por geração, sexo e classe).",
]), { x: 0.6, y: 4.85, w: 12.1, h: 1.8, fontSize: 16, paraSpaceAfter: 6 });
s.addNotes(`O problema de negócio (1 min).
O decisor é a área de estratégia de uma empresa de bebidas, com duas decisões. A primeira: posicionar a linha sem álcool para jovens como nicho, de alta escolaridade e renda, ou como produto de massa. A segunda: tratar a demanda jovem como estrutural, que acompanha essas pessoas quando envelhecem, ou como uma fase.
O custo do erro existe dos dois lados. Por isso não basta saber SE os jovens bebem menos: é preciso saber QUEM bebe menos.`);

s = conteudo("Abertura", "Hipótese e perguntas");
texto(s, "Na mesma idade (18 a 24 anos), o consumo abusivo de álcool diminui de uma geração para a seguinte, nos dois sexos e em todas as faixas de escolaridade, e isso não é uma tendência geral da população.",
  { x: 0.6, y: 1.35, w: 12.1, h: 1.0, fontSize: 18, italic: true, color: C.text2 });
[["P1", "Quanto cada geração difere da anterior, aos 18-24?"], ["P2", "A diferença ocorre em todas as faixas de escolaridade?"], ["P3", "É efeito de geração ou da época?"], ["P4", "É igual entre homens e mulheres?"], ["P5", "Quais capitais concentram as maiores diferenças?"]].forEach(([p, q], i) => {
  const x = 0.6 + i * 2.48;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.75, w: 2.25, h: 3.1, rectRadius: 0.12, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: "card_" + p });
  texto(s, p, { x: x + 0.2, y: 2.95, w: 1.85, h: 0.8, fontSize: 36, bold: true, color: C.accent1, fontFace: THEME.headFontFace });
  texto(s, q, { x: x + 0.2, y: 3.85, w: 1.85, h: 1.9, fontSize: 16 });
});
texto(s, "Consumo abusivo = 5+ doses (homens) ou 4+ doses (mulheres) numa ocasião, nos últimos 30 dias (indicador oficial do Vigitel).",
  { x: 0.6, y: 6.15, w: 12.1, h: 0.5, fontSize: 12, color: C.text2 });
s.addNotes(`Hipótese e perguntas (1 min).
A hipótese: na mesma idade, cada geração bebe em excesso menos que a anterior, nos dois sexos, em todas as classes, e isso não é só uma tendência da época. Ela se desdobra em cinco perguntas.
"Consumo abusivo" é o indicador oficial do Ministério: cinco ou mais doses para homens, quatro ou mais para mulheres, numa mesma ocasião, nos últimos 30 dias. Não mede dependência nem volume; mede episódios de exagero.`);

s = conteudo("Abertura", "Roteiro");
const roteiro = [["Pré-análise", "conhecer a base antes de tratar"], ["Decisões", "D1 a D14, com alternativas"], ["Pipeline", "bronze, silver, gold e qualidade"], ["Resultados", "P1 a P5, robustez e veredito"], ["Discussão", "o que fazer com isso"], ["Limitações", "até onde os números vão"]];
roteiro.forEach(([t, d], i) => {
  const x = 0.6 + i * 2.05;
  circuloNum(s, i + 1, x + 0.6, 2.3, i === 3 ? C.accent2 : C.accent1, 0.75, 22);
  if (i < roteiro.length - 1) linha(s, x + 1.4, 2.675, x + 2.6, 2.675);
  texto(s, t, { x, y: 3.25, w: 1.95, h: 0.5, fontSize: 18, bold: true, color: C.text2, align: "center" });
  texto(s, d, { x, y: 3.8, w: 1.95, h: 1.0, fontSize: 14, align: "center" });
});
texto(s, "Todas as figuras vêm do próprio pipeline (resultados/figuras) ou do relatório de análise exploratória; as capturas, da execução no Databricks Free Edition em 21/10/2026.",
  { x: 0.6, y: 5.6, w: 12.1, h: 0.7, fontSize: 14, color: C.text2 });
s.addNotes(`Roteiro (30 s).
Vou seguir a ordem em que o trabalho foi feito: primeiro a pré-análise, que mudou o próprio objetivo; depois as 14 decisões de tratamento; o pipeline em camadas e o modelo estrela; os resultados; a discussão; e, no fim, as limitações.`);

// ================================================================ PRE-ANALISE
divisoria("Pré-análise", "Pré-análise", "Conhecer a base antes de tratar: três versões da análise exploratória (v1 a v3)",
  `Antes de transformar qualquer dado, fiz a análise exploratória em três versões. Ela mudou a formulação do objetivo e gerou as decisões de tratamento.`);

s = conteudo("Pré-análise", "O processo da pré-análise");
const passos = [
  ["Fonte", "dicionário, nota metodológica, licença e SHA-256 do arquivo"],
  ["Vazios", "separar pulo de questionário, variável inexistente e falta real"],
  ["Amostra e pesos", "jovens por edição e escala do peso"],
  ["Método", "rupturas: 2010, sem 2022, celular, filtro de 2024"],
  ["Prévia", "as cinco perguntas, ainda comparando anos"],
  ["Decisões", "objetivo v2 por geração e D1 a D14"],
];
passos.forEach(([t, d], i) => {
  const x = 0.6 + i * 2.05;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.5, w: 1.85, h: 3.2, rectRadius: 0.12, fill: { color: i === 5 ? C.accent1 : C.background2 }, line: { color: i === 5 ? C.accent1 : C.background2 }, objectName: "passo_" + i });
  circuloNum(s, i + 1, x + 0.65, 1.7, i === 5 ? C.accent2 : C.accent1);
  texto(s, t, { x: x + 0.1, y: 2.4, w: 1.65, h: 0.5, fontSize: 17, bold: true, align: "center", color: i === 5 ? C.background1 : C.text2 });
  texto(s, d, { x: x + 0.1, y: 2.95, w: 1.65, h: 1.6, fontSize: 14, align: "center", color: i === 5 ? C.background1 : C.text1 });
  if (i < passos.length - 1) seta(s, x + 1.87, 2.95);
});
cartao(s, 0.6, 5.0, 12.1, 1.7, "Como foi conduzida", "Notebooks gerados por script, uma versão por rodada (v1 a v3). Os comentários do autor sobre cada versão foram acumulados e aplicados juntos na seguinte, e as decisões de tratamento ficaram com o autor, com alternativas e motivos registrados.", C.accent1, "card_aed", 15);
s.addNotes(`Processo da pré-análise (1 min 30 s).
Seis passos. Primeiro, a fonte: li o dicionário e a nota metodológica, registrei a licença e o SHA-256 do arquivo. Depois, os vazios, separados pelo motivo. Em seguida, quantos jovens há em cada ano e como se comportam os pesos. Depois, as mudanças de método da pesquisa ao longo da série. Com isso fiz uma prévia das perguntas, ainda comparando anos. E, por fim, reescrevi o objetivo por geração e tomei as 14 decisões de tratamento.
Os notebooks de exploração são gerados por script, e cada rodada de comentários virou uma nova versão.`);

s = conteudo("Pré-análise", "Quase todo vazio é pulo de questionário, e não dado perdido");
figura(s, AED("aed2_fig1_vazios_tres_categorias.png"), 0.6, 1.35, 8.7, 4.4);
texto(s, lista([
  ["Pulo legítimo (azul): quem não bebe não responde às doses", { breakLine: true }],
  "Inexistente no ano (preto): a pergunta não existia naquela edição",
  ["Falta real: no máximo 0,6% de uma coluna", { bold: true, color: C.accent1 }],
]), { x: 9.6, y: 1.5, w: 3.1, h: 4.3, fontSize: 15, paraSpaceAfter: 10 });
texto(s, "Consequência: nada a imputar. Os vazios viram regra de consistência (pulo conferido em 100% dos casos) e não tratamento.",
  { x: 0.6, y: 5.95, w: 12.1, h: 0.7, fontSize: 15, color: C.text2 });
s.addNotes(`Mapa de vazios (1 min).
Num questionário, vazio quase nunca é dado perdido. Separei os vazios em três motivos. À esquerda, o pulo legítimo: quem não bebe não responde às perguntas de doses. No meio, colunas que simplesmente não existiam naquele ano, como a chave oficial antes de 2014 ou o tipo de telefone. À direita, o que falta de verdade: no máximo 0,6% de uma coluna.
Então não havia nada a imputar. O que fiz foi transformar o pulo em regra de qualidade: quem responde às doses tem que ser quem bebe.`);

s = conteudo("Pré-análise", "Os jovens entrevistados encolheram ao longo da série");
figura(s, AED("aed2_fig2_amostra_por_ano.png"), 0.6, 1.35, 12.1, 4.2);
destaque(s, "8.770 → 2.294", "jovens de 18 a 24 anos entrevistados em 2006 e em 2024", 0.6, 5.45, 5.6, C.accent2);
texto(s, lista([
  "2020-2021: pandemia, amostra pela metade (D11)",
  ["Um ano isolado tem margem de ±3 p.p.: juntar as edições de cada geração (D3)", { bold: true }],
]), { x: 6.6, y: 5.6, w: 6.1, h: 1.2, fontSize: 15, paraSpaceAfter: 6 });
s.addNotes(`Amostra por edição (1 min).
O Vigitel entrevista cerca de 50 mil pessoas por ano, mas o número de jovens caiu muito: de 8.770 em 2006 para 2.294 em 2024. Em 2020 e 2021, na pandemia, a amostra total caiu pela metade.
Com tão poucos jovens, um ano isolado tem margem de erro de uns três pontos. Isso levou à decisão D3: juntar todas as edições em que cada geração foi observada.`);

s = conteudo("Pré-análise", "O peso amostral muda de escala em 2010");
figura(s, AED("aed2_fig3_pesos_por_ano.png"), 0.6, 1.35, 12.1, 4.2);
cartao(s, 0.6, 5.5, 12.1, 1.25, "Decisão D4: normalizar o peso de cada edição para somar 1", "Sem isso, ao juntar edições, os anos com peso maior dominariam a geração. Com a normalização, cada ano conta igual.", C.accent1, "card_d4", 15);
s.addNotes(`Pesos (45 s).
O Vigitel é amostral, então toda prevalência usa o peso da própria pesquisa. Mas a escala do peso muda: até 2009 os pesos estão na casa das centenas; de 2010 em diante, na casa do milhão. Como eu junto várias edições numa mesma geração, normalizei o peso de cada edição para somar 1. Assim cada ano conta igual. É a decisão D4.`);

s = conteudo("Pré-análise", "Comparar anos mistura comportamento com método");
figura(s, AED("aed2_fig4_p1_p3_faixa_etaria.png"), 0.6, 1.35, 8.9, 3.6);
const rupturas = [["2010", "a pergunta de doses passa a ser “5 ou mais” (D5)"], ["2022", "a edição não existe (D1)"], ["2023-24", "entra o celular; em 2024 muda o filtro do bloco de álcool (D2, D13)"]];
rupturas.forEach(([a, d], i) => {
  const y = 1.5 + i * 1.15;
  texto(s, a, { x: 9.8, y, w: 2.9, h: 0.45, fontSize: 20, bold: true, color: C.accent2, fontFace: THEME.headFontFace });
  texto(s, d, { x: 9.8, y: y + 0.45, w: 2.9, h: 0.7, fontSize: 14 });
});
texto(s, "Na prévia (formulação v1), os jovens tinham 21,9% em 2010 e 22,7% em 2024. Mas as três rupturas estão justamente nas pontas da comparação: qualquer diferença entre 2010 e 2024 seria, em parte, efeito de método.",
  { x: 0.6, y: 5.25, w: 12.1, h: 1.2, fontSize: 15, color: C.text2 });
s.addNotes(`Rupturas de método (1 min 30 s).
Esta é a série de consumo abusivo por faixa etária, como vista na exploração: azul são os jovens, laranja os adultos de 35 a 44.
O problema é que a série tem três rupturas de método: em 2010 a pergunta de doses mudou de "mais do que cinco" para "cinco ou mais"; 2022 não existe; e em 2023 e 2024 entrou o celular e, em 2024, mudou a pergunta que abre o bloco de álcool.
A formulação original comparava 2010 com 2024, exatamente as duas pontas afetadas. Foi aqui que decidi mudar o desenho: comparar gerações na mesma idade, e não anos.`);

s = conteudo("Pré-análise", "A prévia já apontava: o sinal estava no sexo");
figura(s, AED("aed2_fig5_p2_escolaridade.png"), 0.6, 1.3, 8.6, 2.7);
figura(s, AED("aed2_fig6_p4_sexo.png"), 0.6, 4.05, 8.6, 2.75);
texto(s, lista([
  "Por escolaridade (acima): oscilação dentro da margem, sem tendência clara em nenhuma faixa",
  ["Por sexo (abaixo): a distância entre homens e mulheres jovens encolhe ao longo da série", { bold: true, color: C.accent2 }],
  "Ainda comparando anos: serviu de pista, não de resposta",
]), { x: 9.5, y: 1.5, w: 3.2, h: 5.2, fontSize: 15, paraSpaceAfter: 10 });
s.addNotes(`Prévia por escolaridade e sexo (1 min).
Na prévia, por escolaridade, as três faixas oscilam dentro das margens, sem uma tendência clara. Por sexo, aparece o que viria a ser o achado central: a distância entre homens e mulheres jovens encolhe ao longo da série, até quase sumir em 2024.
Mas ainda é uma comparação entre anos, sujeita às rupturas que mostrei. Serviu de pista, e foi confirmada depois, já por geração e na mesma idade.`);

s = conteudo("Pré-análise", "Por capital, a comparação de dois anos não tinha precisão");
figura(s, AED("aed2_fig7_p5_capitais.png"), 0.6, 1.3, 5.9, 5.55);
texto(s, lista([
  "Formulação v1: cada capital em 2010 (cinza) e em 2024 (azul)",
  "Diferenças de até ±14 p.p., mas com intervalos enormes",
  "Só Fortaleza sem sobreposição dos intervalos",
  ["Decisão D9: capitais com a margem de erro à vista e a região como apoio; e juntar as edições por geração para ganhar precisão", { bold: true }],
]), { x: 6.9, y: 1.5, w: 5.8, h: 5.2, fontSize: 15, paraSpaceAfter: 10 });
s.addNotes(`Capitais na prévia (1 min).
Na formulação original, comparando 2010 com 2024 em cada capital, as diferenças pareciam grandes, de até 14 pontos, mas os intervalos eram enormes: só Fortaleza não tinha sobreposição.
Isso levou à decisão D9: mostrar cada capital com a margem de erro, usar a região como apoio quando a capital for inconclusiva, e, com a abordagem por geração, juntar várias edições para ganhar precisão.`);

s = conteudo("Pré-análise", "Da pré-análise ao novo objetivo");
cartao(s, 0.6, 1.5, 5.9, 4.0, "Versão 1: comparar anos", ["Jovens de 18-24 em 2010 x no ano mais recente", "Pontas da série afetadas por pergunta nova, celular e filtro novo", "Um ano isolado: poucos jovens e margem de ±3 p.p."], C.text2, "card_v1", 18);
cartao(s, 6.85, 1.5, 5.9, 4.0, "Versão 2: comparar gerações", ["Millennials, zillennials e geração Z, sempre aos 18-24 anos", "Cada geração junta todas as edições em que foi observada", "P3 passa a acompanhar cada geração ao envelhecer"], C.accent1, "card_v2", 18);
seta(s, 6.55, 3.3);
texto(s, "O problema, o decisor e a fonte continuaram os mesmos; mudou o desenho da comparação. A versão 1 fica preservada no Anexo A do README.",
  { x: 0.6, y: 5.8, w: 12.1, h: 0.8, fontSize: 15, color: C.text2 });
s.addNotes(`Novo objetivo (45 s).
O resultado da pré-análise foi reescrever o objetivo. Na versão 1, eu comparava anos. Na versão 2, comparo gerações, sempre na mesma idade, juntando as edições de cada uma. A pergunta de negócio, o decisor e a fonte não mudaram. Como o enunciado pede, a versão original está preservada no anexo do README.`);

// ================================================================ DECISOES
divisoria("Decisões", "Decisões de tratamento", "14 decisões, cada uma com alternativas descartadas e o motivo do autor",
  `Cada problema encontrado na exploração virou uma decisão registrada, com as alternativas descartadas e o motivo. Vou mostrar todas rapidamente e detalhar as duas que mais pesaram.`);

function tabelaDecisoes(titulo, itens) {
  const sl = conteudo("Decisões", titulo);
  texto(sl, "Problema", { x: 1.45, y: 1.3, w: 4.4, h: 0.4, fontSize: 14, bold: true, color: C.accent4 });
  texto(sl, "Decisão", { x: 6.0, y: 1.3, w: 6.7, h: 0.4, fontSize: 14, bold: true, color: C.accent4 });
  itens.forEach(([d, p, dec], i) => {
    const y = 1.75 + i * 0.73;
    if (i % 2 === 0) sl.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: y - 0.04, w: 12.1, h: 0.7, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: "faixa_" + d });
    circuloNum(sl, d, 0.75, y + 0.06, d === "D14" || d === "D2" ? C.accent2 : C.accent1, 0.5, 12);
    texto(sl, p, { x: 1.45, y, w: 4.4, h: 0.62, fontSize: 14, valign: "middle" });
    texto(sl, dec, { x: 6.0, y, w: 6.7, h: 0.62, fontSize: 14, bold: true, color: C.text2, valign: "middle" });
  });
  return sl;
}
s = tabelaDecisoes("Decisões D1 a D7", [
  ["D1", "Não existe a edição de 2022", "Lacuna à vista, sem criar nenhum dado"],
  ["D2", "2010 só fixo; 2024 com celular e filtro novo", "Comparar gerações na mesma idade, e não anos"],
  ["D3", "Poucos jovens num ano isolado", "Juntar todas as edições de cada geração"],
  ["D4", "Pesos em escalas diferentes entre anos", "Normalizar o peso para somar 1 por edição"],
  ["D5", "Pergunta de doses mudou em 2010", "Usar só as edições de 2010 em diante"],
  ["D6", "Pergunta “costuma beber” muda e some em 2024", "Decompor: quem bebe x exagero entre quem bebe"],
  ["D7", "Escolaridade dos jovens mudou entre gerações", "Análise por faixa e média padronizada pela escolaridade"],
]);
s.addNotes(`D1 a D7 (1 min 30 s).
D1: 2022 não existe e não é imputado. D2, a principal: comparar gerações, e não anos. D3: juntar as edições de cada geração. D4: normalizar o peso por edição. D5: só de 2010 em diante, por causa da pergunta de doses. D6: como a pergunta "costuma beber" muda e desaparece em 2024, decompus o consumo abusivo em duas partes, quem bebe e quanto exagera quem bebe. D7: como a escolaridade dos jovens subiu entre as gerações, analiso dentro de cada faixa e também padronizo pela escolaridade.`);

s = tabelaDecisoes("Decisões D8 a D14", [
  ["D8", "Escolaridade estimada pelo Ministério (1%)", "Manter e testar sem esses casos"],
  ["D9", "Poucos jovens por capital", "Capitais com margem de erro; região como apoio"],
  ["D10", "Chave oficial falha e se repete", "Chave = edição + linha do arquivo original"],
  ["D11", "Pandemia: amostra pela metade em 2020-21", "Manter e testar sem esses anos"],
  ["D12", "Texto livre; região vazia em 2012", "Texto livre só na bronze (LGPD); região pela capital"],
  ["D13", "Filtro novo do bloco de álcool em 2024", "Manter e testar sem 2024"],
  ["D14", "Gerações observadas em idades diferentes", "Padronizar pela idade simples (18 a 24)"],
]);
s.addNotes(`D8 a D14 (1 min 30 s).
D8: mantenho a escolaridade estimada e testo sem ela. D9: capitais sempre com margem de erro. D10: como a chave oficial só existe em parte dos anos e se repete, criei uma chave a partir da edição e da linha do arquivo, rastreável até a origem. D11 e D13: pandemia e o filtro novo de 2024 ficam, mas viram testes de sensibilidade. D12: o texto livre, que pode conter dado pessoal, fica só na bronze, por minimização da LGPD.
E a D14, que entrou depois, na revisão: padronizar pela idade. Detalho nos próximos slides.`);

s = conteudo("Decisões", "D2: comparar gerações, e não anos");
figura(s, FIG("f02_cobertura_geracoes.png"), 0.6, 1.35, 7.6, 3.6);
const geracoes = [["Millennials", "nascidos em 1986-1992", "observados aos 18-24 em 2010-2016, só fixo", C.accent4], ["Zillennials", "nascidos em 1993-1998", "observados em 2011-2021, só fixo", C.accent3], ["Geração Z", "nascidos em 1999-2006", "observados em 2017-2024, 33% celular", C.accent1]];
geracoes.forEach(([g, n, o, cor], i) => {
  const y = 1.45 + i * 1.2;
  s.addShape(pres.shapes.OVAL, { x: 8.6, y: y + 0.12, w: 0.42, h: 0.42, fill: { color: cor }, line: { color: cor } });
  texto(s, g, { x: 9.2, y, w: 3.5, h: 0.42, fontSize: 18, bold: true, color: C.text2 });
  texto(s, n + "; " + o, { x: 9.2, y: y + 0.42, w: 3.5, h: 0.7, fontSize: 13 });
});
texto(s, lista([
  "Geração = ano da pesquisa menos a idade. Sempre na mesma idade (18 a 24).",
  "Juntando vários anos por geração, a margem de erro cai para cerca de ±1 p.p.",
  "Millennials x zillennials: comparação toda por telefone fixo, sem mudança de método.",
]), { x: 0.6, y: 5.2, w: 12.1, h: 1.6, fontSize: 15, paraSpaceAfter: 6 });
s.addNotes(`D2 e a figura f02 (1 min 30 s).
A geração é o ano da pesquisa menos a idade: millennials nascidos de 1986 a 1992, zillennials, a geração de transição, de 1993 a 1998, e a geração Z de 1999 a 2006, sempre observados aos 18-24 anos.
O gráfico mostra quantos jovens de cada geração foram entrevistados em cada edição; a linha laranja é a proporção de entrevistas por celular, que só aparece com a geração Z. Duas vantagens: a margem de erro cai para cerca de um ponto, e a comparação millennials contra zillennials é toda por fixo, sem mudança de método.`);

s = conteudo("Decisões", "D14: na mesma idade, de fato");
figura(s, FIG("f03a_idade_por_geracao.png"), 0.6, 1.35, 8.4, 3.9);
destaque(s, "4% x 29%", "do peso vem dos jovens de 18 anos: millennials x geração Z", 9.3, 1.5, 3.4, C.accent2);
texto(s, lista([
  "O consumo abusivo sobe com a idade: cerca de 14% aos 18 e 27% aos 24",
  "A janela 2010-2024 mostra os millennials mais velhos e a geração Z mais nova",
  ["Correção: média das 7 idades, com peso igual para cada uma, nas mesmas idades para todas as gerações", { bold: true, color: C.accent1 }],
]), { x: 0.6, y: 5.4, w: 12.1, h: 1.45, fontSize: 15, paraSpaceAfter: 6 });
s.addNotes(`D14 e a figura f03a (1 min 30 s).
Fixar a faixa de 18 a 24 anos não basta. Como a série começa em 2010 e termina em 2024, os millennials aparecem sobretudo aos 22, 23 e 24 anos, e a geração Z sobretudo aos 18 e 19. Só 4% do peso dos millennials vem dos jovens de 18 anos; na geração Z, 29%.
E o consumo abusivo sobe com a idade. Sem corrigir, a geração Z parece beber menos só porque foi entrevistada mais nova. A correção é uma padronização direta: a média das prevalências das sete idades, com o mesmo peso para todas as gerações. Essa decisão mudou o resultado principal.`);

// ================================================================ PIPELINE
divisoria("Pipeline", "Pipeline no Databricks", "Arquitetura em camadas: raw, bronze, silver e gold, com qualidade e análise",
  `Agora, como os dados foram persistidos e transformados na nuvem, no Databricks Free Edition.`);

s = conteudo("Pipeline", "Do arquivo oficial ao modelo estrela");
const camadas = [
  ["Raw", CAMADA.raw, "Volume do Unity Catalog", ["ZIP oficial do Ministério", "87 MB, SHA-256 conferido", "notebook 01"]],
  ["Bronze", CAMADA.bronze, "bronze_vigitel", ["cópia fiel do CSV", "833.217 linhas x 486 colunas", "gravada em lotes de 20 mil"]],
  ["Silver", CAMADA.silver, "silver_vigitel", ["2010 em diante: 615.877", "28 colunas, regras S1-S11", "sem texto livre (D12)"]],
  ["Gold", CAMADA.gold, "fato + 6 dimensões", ["modelo estrela", "integridade referencial ok", "notebook 03"]],
  ["Consumo", THEME.colors.accent1, "qa_* e res_*", ["16 regras de qualidade", "P1 a P5 e veredito", "notebooks 04 a 06"]],
];
camadas.forEach(([t, cor, tab, itens], i) => {
  const x = 0.6 + i * 2.48;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.5, w: 2.15, h: 1.15, rectRadius: 0.1, fill: { color: cor }, line: { color: cor }, objectName: "camada_" + t });
  texto(s, t, { x, y: 1.55, w: 2.15, h: 0.55, fontSize: 22, bold: true, color: C.background1, align: "center", fontFace: THEME.headFontFace });
  texto(s, tab, { x, y: 2.1, w: 2.15, h: 0.45, fontSize: 13, color: C.background1, align: "center" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.85, w: 2.15, h: 2.45, rectRadius: 0.1, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: "corpo_" + t });
  texto(s, lista(itens), { x: x + 0.1, y: 3.0, w: 1.95, h: 2.2, fontSize: 14, paraSpaceAfter: 6 });
  if (i < camadas.length - 1) seta(s, x + 2.2, 1.92);
});
texto(s, "Site do Ministério → Volume → bronze → silver → gold → qualidade e respostas", { x: 0.6, y: 5.5, w: 12.1, h: 0.45, fontSize: 16, bold: true, color: C.text2 });
texto(s, "As regras ficam em módulos Python (scripts/) chamados pelos notebooks, e podem ser testadas fora do cluster. Catálogo workspace, esquema genz_alcool, Delta Lake, computação serverless.",
  { x: 0.6, y: 5.95, w: 12.1, h: 0.75, fontSize: 14, color: C.text2 });
s.addNotes(`Camadas (1 min 30 s).
O notebook 01 baixa o ZIP oficial do site do Ministério para um Volume do Unity Catalog e confere o SHA-256, para garantir que é exatamente o arquivo usado no trabalho.
A bronze é uma cópia fiel: as 833 mil linhas e as 486 colunas, tudo como texto, mais o número da linha de origem. Nenhuma regra de negócio aqui.
A silver aplica as regras S1 a S11, que são as decisões de tratamento: fica com 2010 em diante, 615.877 entrevistas e 28 colunas, sem texto livre.
A gold é o modelo estrela, no próximo slide. Por fim, as tabelas de qualidade e as de resultados, uma por pergunta.`);

s = conteudo("Pipeline", "Modelo estrela: a entrevista é o fato");
const fx = 4.95, fy = 2.0, fw = 3.45, fh = 4.0;
const dims = [
  ["dim_edicao", "ano, entrevistas, % celular, pandemia, filtro do álcool", "14 edições", 0.6, 1.45],
  ["dim_geracao", "geração e anos de nascimento", "4 linhas", 0.6, 3.3],
  ["dim_escolaridade", "0 a 8, 9 a 11, 12 anos e mais", "3 linhas", 0.6, 5.15],
  ["dim_capital", "capital, UF e região (D12)", "27 capitais", 9.1, 1.45],
  ["dim_faixa_etaria", "seis faixas do Vigitel", "6 linhas", 9.1, 3.3],
  ["dim_sexo", "masculino, feminino", "2 linhas", 9.1, 5.15],
];
dims.forEach(([n, d, card, x, y]) => {
  const esq = x < fx;
  linha(s, esq ? x + 3.6 : fx + fw, y + 0.7, esq ? fx : x, fy + fh / 2, THEME.colors.accent3);
});
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: fx, y: fy, w: fw, h: fh, rectRadius: 0.12, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: "fato" });
texto(s, "fato_entrevista", { x: fx + 0.2, y: fy + 0.15, w: fw - 0.4, h: 0.5, fontSize: 20, bold: true, color: C.background1, fontFace: THEME.headFontFace });
texto(s, "615.877 linhas · grão: 1 entrevista", { x: fx + 0.2, y: fy + 0.65, w: fw - 0.4, h: 0.4, fontSize: 13, color: C.background2 });
texto(s, lista(["entrevista_id (D10)", "6 chaves das dimensões", "alcabu, bebe_mensal (0/1)", "peso e peso_norm (D4)", "idade, ano de nascimento, modo de coleta", "linha_origem (linhagem)"], { color: C.background1 }),
  { x: fx + 0.2, y: fy + 1.15, w: fw - 0.4, h: 2.7, fontSize: 14, paraSpaceAfter: 4 });
dims.forEach(([n, d, card, x, y]) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 3.6, h: 1.4, rectRadius: 0.1, fill: { color: C.background2 }, line: { color: THEME.colors.accent3, width: 1 }, objectName: n });
  texto(s, n, { x: x + 0.15, y: y + 0.08, w: 2.3, h: 0.42, fontSize: 15, bold: true, color: C.text2 });
  texto(s, card, { x: x + 2.35, y: y + 0.1, w: 1.1, h: 0.4, fontSize: 11, color: C.accent1, align: "right" });
  texto(s, d, { x: x + 0.15, y: y + 0.52, w: 3.3, h: 0.8, fontSize: 13 });
});
s.addNotes(`Modelo estrela (1 min 30 s).
Escolhi um esquema estrela porque as cinco perguntas cortam o mesmo fato, a entrevista, por geração, escolaridade, sexo, faixa etária, capital e edição. Cada corte é uma dimensão, e nenhuma pergunta precisa de outra tabela de fatos.
A fato tem uma linha por entrevista, 615.877, com as medidas em 0 ou 1, consumo abusivo e se bebe ao menos uma vez por mês, e os pesos. As prevalências não ficam guardadas: são calculadas na análise como média ponderada.
A linha de origem garante a linhagem até o arquivo oficial. O dicionário completo, com domínio e linhagem de cada atributo, está no catálogo do repositório.`);

s = conteudo("Pipeline", "Qualidade: 16 regras em seis dimensões, nenhuma violação");
figura(s, EVI("18_nb04_checagens_qualidade.png"), 0.6, 1.35, 8.3, 4.3, true);
legenda(s, "Captura do notebook 04 no Databricks (21/10/2026): tabela qa_checagens", 0.6, 5.7, 8.3);
texto(s, lista([
  "Completude, unicidade, consistência, conformidade, acurácia e atualidade",
  "Pulo das doses conferido em 100% dos casos",
  "Peso normalizado soma 1 em cada edição",
  ["Informativas, não erros: 7.477 escolaridades estimadas, 35.280 entrevistas por celular", { bold: true }],
  "Perfil dos 28 atributos da silver: nulos, distintos, mínimo e máximo",
]), { x: 9.2, y: 1.45, w: 3.5, h: 5.3, fontSize: 14, paraSpaceAfter: 8 });
s.addNotes(`Qualidade (1 min).
O notebook 04 aplica 16 regras sobre a silver, nas seis dimensões do roteiro. Todas as regras de verificação passaram, com zero violações. As linhas marcadas como "informativa" não são erros: são características conhecidas, como as escolaridades estimadas pelo Ministério e as entrevistas por celular, que viraram testes de sensibilidade.
Além disso, o perfil dos 28 atributos da silver registra nulos, valores distintos, mínimo e máximo de cada um.`);

s = conteudo("Pipeline", "Evidência: coleta e bronze persistidas no Databricks");
figura(s, EVI("03_nb01_volume_sha256.png"), 0.6, 1.35, 7.6, 4.4, true);
legenda(s, "Notebook 01: o ZIP no Volume, com tamanho e SHA-256 conferidos", 0.6, 5.8, 7.6);
figura(s, EVI("07_nb01_verificacao_bronze_833217.png"), 8.6, 1.35, 4.1, 4.4, true);
legenda(s, "Notebook 01: bronze com 833.217 linhas, as mesmas do CSV", 8.6, 5.8, 4.1);
s.addNotes(`Evidência da coleta (45 s).
Estas são capturas da execução no Databricks Free Edition. À esquerda, o arquivo no Volume, com o tamanho e o SHA-256 iguais aos do arquivo oficial. À direita, a verificação da bronze: entrevistas por ano e a confirmação de que a tabela Delta tem as mesmas 833.217 linhas do CSV.`);

s = conteudo("Pipeline", "Evidência: silver e gold consistentes");
figura(s, EVI("09_nb02_verificacao_geracoes.png"), 0.6, 1.35, 6.6, 2.75, true);
legenda(s, "Notebook 02: jovens de cada geração na silver e as edições em que aparecem", 0.6, 4.15, 6.6);
figura(s, EVI("15_nb03_estrela_consistente.png"), 7.5, 1.35, 5.2, 4.55, true);
legenda(s, "Notebook 03: a fato com as 6 dimensões reproduz as 615.877 linhas da silver", 7.5, 5.95, 5.2);
texto(s, lista(["Millennials: 23.805 jovens; zillennials: 26.745; geração Z: 10.485", "26 tabelas Delta persistidas no esquema genz_alcool"]),
  { x: 0.6, y: 4.6, w: 6.6, h: 1.4, fontSize: 15, paraSpaceAfter: 6 });
s.addNotes(`Evidência da silver e da gold (45 s).
À esquerda, a silver: os jovens de cada geração e as edições em que foram observados, exatamente como no desenho. À direita, o teste do modelo estrela: juntando a fato com as seis dimensões, voltam as mesmas 615.877 linhas da silver, sem perda nem duplicação. No total, 26 tabelas ficaram persistidas no esquema do projeto.`);

// ================================================================ RESULTADOS
divisoria("Resultados", "Resultados", "P1 a P5, robustez e veredito", `Agora os resultados, pergunta por pergunta. Todas as prevalências são ponderadas e, entre gerações, padronizadas pela idade.`);

s = conteudo("Resultados", "A série histórica não mostra queda entre os jovens");
figura(s, FIG("f01_serie_faixa_etaria.png"), 0.6, 1.35, 8.6, 5.4);
texto(s, lista([
  "Jovens (azul): 21,9% em 2010 e 22,7% em 2024",
  "Adultos de 35-44 (laranja) sobem mais no período",
  "Faixa cinza: 2022 não existe; linha pontilhada: entra o celular",
  ["Ponto de partida, não resposta: a resposta vem por geração", { bold: true, color: C.accent2 }],
]), { x: 9.5, y: 1.6, w: 3.25, h: 4.8, fontSize: 15, paraSpaceAfter: 10 });
s.addNotes(`Série no pipeline, f01 (45 s).
Esta é a série calculada no pipeline, de 2010 em diante. Os jovens ficam praticamente estáveis, de 21,9% para 22,7%, enquanto os adultos de 35 a 44 sobem mais. É o ponto de partida; a resposta às perguntas vem da comparação por geração, a seguir.`);

s = conteudo("Resultados", "P1. Na mesma idade, a geração Z não bebe menos");
figura(s, FIG("f03_p1_geracoes.png"), 0.6, 1.35, 7.6, 5.4);
destaque(s, "+1,1 p.p.", "geração Z em relação aos millennials, aos 18-24, padronizada pela idade (IC 95%: −1,1 a +3,3)", 8.6, 1.6, 4.1);
texto(s, lista([
  "21,1% → 22,2% → 22,3%; nenhuma diferença significativa",
  "Sem padronizar (círculo), aparecia −2,1 p.p.: a queda vinha da idade",
  "Padronizada também pela escolaridade (losango): quase igual",
]), { x: 8.6, y: 3.6, w: 4.1, h: 3.0, fontSize: 15, paraSpaceAfter: 8 });
s.addNotes(`P1, f03 (1 min).
Na mesma idade, os millennials tinham 21,1% de consumo abusivo; os zillennials, 22,2%; a geração Z, 22,3%. A diferença é de mais 1,1 ponto, e o intervalo inclui o zero: não há queda.
O círculo branco é a leitura sem padronizar: ali aparecia uma queda de 2,1 pontos, que vinha de a geração Z ter sido entrevistada mais nova. O losango, padronizado também pela escolaridade, quase não muda.
Mas o total esconde dois movimentos opostos.`);

s = conteudo("Resultados", "P4. Sem separar os sexos, nada muda; separando, tudo muda");
figura(s, FIG("f04_p4_convergencia_sexos.png"), 0.6, 1.35, 7.6, 5.4);
destaque(s, "14 → 3,5", "p.p. de distância entre homens e mulheres, de millennials para geração Z", 8.6, 1.6, 4.1, C.accent2);
texto(s, lista([
  ["Homens: −4,0 p.p. (28,1% → 24,0%)", { color: C.accent1, bold: true }],
  ["Mulheres: +6,4 p.p. (14,1% → 20,5%)", { color: C.accent2, bold: true }],
  "Os dois movimentos se cancelam no total",
]), { x: 8.6, y: 3.6, w: 4.1, h: 3.0, fontSize: 16, paraSpaceAfter: 8 });
s.addNotes(`P4, f04: o achado que mais me impressionou (1 min 30 s).
Sem considerar o sexo, não havia diferença entre as gerações. Separando, os homens caem de 28,1% para 24,0%, uma queda leve, e as mulheres sobem de 14,1% para 20,5%, um aumento significativo. Os dois movimentos se cancelam no total.
A distância entre os sexos, que era de 14 pontos entre os millennials, caiu para 3,5 na geração Z. Para o negócio, isso muda o público: "o jovem" não é um público único.`);

s = conteudo("Resultados", "Por que muda: homens moderam, mais mulheres bebem");
figura(s, FIG("f05_decomposicao.png"), 0.6, 1.3, 12.1, 3.95);
cartao(s, 0.6, 5.35, 5.9, 1.45, "Homens", "Quase o mesmo tanto bebe (43% → 41%); quem bebe exagera menos (65% → 58%)", C.accent1, "card_h");
cartao(s, 6.85, 5.35, 5.9, 1.45, "Mulheres", "Mais bebem (25% → 35%); o exagero entre quem bebe fica estável (56% → 58%)", C.accent2, "card_m");
s.addNotes(`Decomposição, f05 (1 min).
Pela decisão D6, separei o consumo abusivo em duas partes: quantos jovens bebem pelo menos uma vez por mês e, entre os que bebem, quantos exageram.
Nos homens, a proporção que bebe quase não muda; o que cai é o exagero entre quem bebe: parece moderação. Nas mulheres, o exagero entre quem bebe é estável; o que sobe é a proporção de mulheres que bebem.`);

s = conteudo("Resultados", "P2. Por escolaridade, nenhuma diferença significativa");
figura(s, FIG("f06_p2_escolaridade.png"), 0.6, 1.4, 8.2, 4.4);
texto(s, lista([
  "De +0,6 a +2,0 p.p. nas três faixas, todas dentro da margem de erro",
  "Sem os casos de escolaridade estimada (D8): mesmo resultado",
  ["Não há queda concentrada em nenhuma classe, nem queda ampla", { bold: true }],
]), { x: 9.1, y: 1.6, w: 3.6, h: 4.5, fontSize: 15, paraSpaceAfter: 10 });
s.addNotes(`P2, f06 (1 min).
Por escolaridade, a aproximação de classe social, a geração Z fica de 0,6 a 2 pontos acima dos millennials nas três faixas, e nenhuma diferença é significativa. Sem os casos de escolaridade estimada, o resultado é o mesmo.
Para a decisão de nicho ou massa: não há um nicho de jovens escolarizados que bebe menos, mas também não há uma queda de massa. A diferença relevante não é de classe, é de sexo.`);

s = conteudo("Resultados", "P3. Os jovens subiram menos que a época");
figura(s, FIG("f07_p3_jovens_x_adultos.png"), 0.6, 1.4, 7.4, 3.8);
destaque(s, "−2,7 p.p.", "jovens (+1,1) em relação aos adultos de 35-44 (+3,8) no mesmo período (IC 95%: −5,1 a −0,3)", 8.4, 1.6, 4.3);
texto(s, "Os jovens não beberam menos, mas cresceram menos que a tendência geral: um efeito relativo de geração, e não uma queda.",
  { x: 0.6, y: 5.5, w: 12.1, h: 1.0, fontSize: 16 });
s.addNotes(`P3, f07 (1 min).
E se todo mundo mudou no mesmo período? Comparei os jovens com os adultos de 35 a 44 anos nas mesmas edições, os dois padronizados pela idade. Os jovens subiram 1,1 ponto; os adultos, 3,8. A diferença das diferenças é de menos 2,7 pontos, significativa.
A época puxou o consumo para cima, e os jovens acompanharam menos.`);

s = conteudo("Resultados", "P3. Ao envelhecer, as curvas ficam paralelas");
figura(s, FIG("f08_p3_envelhecimento.png"), 0.6, 1.35, 12.1, 4.6);
texto(s, "Homens zillennials: 1,4 p.p. abaixo dos millennials aos 18-24 (26,7% x 28,1%) e aos 25-29 (33,4% x 34,8%): curvas paralelas, sem sinal de adiamento. Mulheres zillennials acima nas duas faixas; a geração Z ainda é jovem demais.",
  { x: 0.6, y: 6.0, w: 12.1, h: 0.85, fontSize: 15 });
s.addNotes(`P3, f08 (1 min).
Acompanhei cada geração ao envelhecer. Os homens zillennials ficam cerca de 1,4 ponto abaixo dos millennials tanto aos 18-24 quanto aos 25-29: curvas paralelas, o que sugere uma mudança que acompanha a geração, e não um adiamento. A geração Z ainda é jovem demais para essa comparação; fica para as próximas edições.`);

s = conteudo("Resultados", "P5. Nenhuma região muda de forma clara");
figura(s, FIG("f09_p5_mapa_capitais.png"), 0.6, 1.3, 6.0, 5.6);
texto(s, lista([
  "Só Aracaju fora da margem de erro (−6,1 p.p.); com 27 capitais, uma é esperada só pelo acaso",
  "Nenhuma região significativa (de −0,5 p.p. no Norte a +4,5 no Sul)",
  "Dentro da margem: a maioria do Nordeste cai; Sul e Sudeste (exceto o Rio) sobem",
  ["Capital inconclusiva: usar a região como apoio (D9)", { bold: true }],
]), { x: 7.0, y: 1.5, w: 5.7, h: 5.2, fontSize: 15, paraSpaceAfter: 10 });
s.addNotes(`P5, f09 (1 min).
Cada quadrado é uma capital; azul é queda da geração Z em relação aos millennials, vermelho é alta; borda preta é diferença fora da margem de erro. Só Aracaju tem diferença clara, e com 27 capitais uma é esperada pelo acaso. Nenhuma região é significativa.`);

s = conteudo("Resultados", "P5. Diferença e margem de erro por capital");
figura(s, FIG("f10_p5_capitais.png"), 0.6, 1.25, 6.4, 5.65);
texto(s, lista([
  "Diferença geração Z − millennials aos 18-24 anos, por capital",
  "Azul: o intervalo de 95% não inclui o zero",
  "Cerca de 390 jovens da geração Z por capital: margem de ±5 a 6 p.p.",
  ["Com essa precisão, os dados não sustentam uma priorização regional de lançamento", { bold: true }],
]), { x: 7.3, y: 1.5, w: 5.4, h: 5.0, fontSize: 15, paraSpaceAfter: 10 });
s.addNotes(`P5, f10 (45 s).
O mesmo resultado com as margens de erro. Com cerca de 390 jovens da geração Z por capital, a margem é de 5 a 6 pontos. Por isso, os dados não sustentam uma priorização de capitais para lançamento.`);

s = conteudo("Resultados", "Robustez: alta feminina firme, queda masculina frágil");
figura(s, FIG("f11_sensibilidades.png"), 0.6, 1.35, 8.0, 5.4);
texto(s, lista([
  "Seis cenários e, na última linha, a leitura sem padronizar",
  ["Mulheres: +5,1 a +8,1 p.p., significativa em cinco dos seis", { color: C.accent2, bold: true }],
  ["Homens: −2,4 a −4,1 p.p.; perde a significância aos 18-21, sem 2024 e só por fixo", { color: C.accent1, bold: true }],
  "Sem padronizar, a queda total aparecia: era efeito da idade",
]), { x: 8.9, y: 1.6, w: 3.8, h: 5.0, fontSize: 15, paraSpaceAfter: 10 });
s.addNotes(`Robustez, f11 (1 min).
Refiz tudo em seis cenários, um para cada decisão que poderia mudar o resultado: só 18 a 21 anos, sem 2024, geração Z só por fixo, sem a pandemia, sem a escolaridade estimada.
A alta das mulheres é robusta: significativa em cinco dos seis. A queda dos homens é frágil: perde a significância em três cenários. E a última linha mostra que, sem padronizar, aparecia uma queda total que era efeito da idade.`);

s = conteudo("Resultados", "Veredito: hipótese refutada no que tem de central");
[
  ["(a)", "Na mesma idade, a prevalência da geração Z é menor que a dos millennials?", "Não: +1,1 p.p. (−1,1 a +3,3)", false],
  ["(b)", "A queda ocorre nos dois sexos e nas três faixas de escolaridade?", "Não: homens −4,0; mulheres +6,4; nenhuma faixa de escolaridade cai", false],
  ["(c)", "Os jovens mudam de forma diferente da tendência geral (adultos de 35-44)?", "Sim: jovens +1,1 contra adultos +3,8 (diferença de −2,7; IC −5,1 a −0,3)", true],
].forEach(([c, q, r, ok], i) => {
  const y = 1.5 + i * 1.45;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y, w: 12.1, h: 1.25, rectRadius: 0.1, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: "criterio_" + i });
  s.addShape(pres.shapes.OVAL, { x: 0.85, y: y + 0.27, w: 0.7, h: 0.7, fill: { color: ok ? C.accent6 : C.accent5 }, line: { color: ok ? C.accent6 : C.accent5 } });
  texto(s, ok ? "✓" : "✗", { x: 0.85, y: y + 0.27, w: 0.7, h: 0.7, fontSize: 24, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0 });
  texto(s, c + " " + q, { x: 1.85, y: y + 0.15, w: 10.6, h: 0.5, fontSize: 17, bold: true, color: C.text2 });
  texto(s, r, { x: 1.85, y: y + 0.65, w: 10.6, h: 0.5, fontSize: 15 });
});
texto(s, "Na mesma idade, a geração Z não bebe menos: os sexos é que convergem.", { x: 0.6, y: 6.0, w: 12.1, h: 0.6, fontSize: 22, bold: true, color: C.accent1, fontFace: THEME.headFontFace });
s.addNotes(`Veredito (1 min).
Os critérios estão no README desde a versão 2 do objetivo. A parte central da hipótese, menor prevalência na mesma idade e queda em todos os grupos, não se confirma. Só a terceira parte se confirma: os jovens subiram menos que os adultos no mesmo período.
Na primeira versão, sem padronizar, eu tinha concluído "parcialmente refutada". A correção do método mudou a conclusão, com os mesmos critérios.`);

// ================================================================ EXPLORACAO
pres.addSection({ title: "Exploração" });
s = conteudo("Exploração", "O que anda junto com o consumo abusivo entre jovens");
figura(s, FIG("f13_correlatos.png"), 0.6, 1.3, 6.4, 5.6);
texto(s, lista([
  "21 características do Vigitel, ajustadas por sexo e edição",
  ["Cigarro e vape: +38 e +34 p.p.", { bold: true }],
  ["Depressão: +8 p.p. só entre os jovens (nos adultos, zero)", { bold: true }],
  ["Tela 3h+/dia: +7 p.p. (o celular não substitui o bar)", { bold: true }],
  "Hipertensão, diabetes, inatividade: sem associação, como esperado",
  ["Associação não é causa; com 21 testes, ~1 pode ser acaso", { italic: true, color: C.accent2 }],
]), { x: 7.3, y: 1.5, w: 5.4, h: 5.3, fontSize: 15, paraSpaceAfter: 9 });
s.addNotes(`Correlatos, f13 (1 min 30 s).
O Vigitel pergunta muito mais que álcool. Testei 21 características contra o consumo abusivo entre jovens, ajustando por sexo e ano, e classifiquei a expectativa de cada uma antes de olhar os dados. Vermelho é mais consumo, azul menos, cinza inconclusivo; o traço preto é o mesmo cálculo para todos os adultos.
Os mais fortes, esperados: cigarro e cigarro eletrônico. O curioso: depressão associada a mais consumo só entre os jovens. E o que contraria o senso comum: tela no lazer anda junto com mais consumo, não menos.
Associação não é causa, mas cada um desses achados pode virar uma investigação própria, com a metodologia correta.`);

s = conteudo("Exploração", "Quatro destaques, em números brutos");
figura(s, FIG("f14_correlatos_destaque.png"), 0.6, 1.25, 12.1, 3.6);
texto(s, "Em cada painel: “não” = jovens sem a característica; “sim” = com a característica. A barra é a % do grupo com consumo abusivo.",
  { x: 0.6, y: 4.9, w: 12.1, h: 0.4, fontSize: 14, italic: true, color: C.text2 });
destaque(s, "54%", "dos jovens que usam cigarro eletrônico bebem em excesso (20% de quem não usa)", 0.6, 5.2, 5.8, C.accent5);
destaque(s, "24%", "de quem passa 3h+ por dia em telas no lazer (18% de quem passa menos)", 6.9, 5.2, 5.8, C.accent5);
s.addNotes(`Destaques, f14 (45 s).
Em cada painel, "não" são os jovens sem a característica e "sim", os que têm; a barra é a porcentagem de cada grupo com consumo abusivo. 54% dos jovens que usam cigarro eletrônico bebem em excesso, contra 20% de quem não usa. Com diagnóstico de depressão, 30% contra 21%. Com três horas ou mais de tela, 24% contra 18%. E quem trabalha, 25% contra 17%.`);

// ================================================================ DISCUSSAO
divisoria("Discussão", "Discussão", "O que os números dizem sobre o problema de negócio",
  `Agora, o que esses resultados significam para o problema e para o decisor.`);

s = conteudo("Discussão", "Duas lições de método");
destaque(s, "−2,1 → +1,1", "p.p., geração Z − millennials: sem padronizar e padronizando pela idade", 0.6, 1.35, 5.9, C.accent1);
destaque(s, "−4,0 e +6,4", "p.p., homens e mulheres: dois movimentos que se cancelam no total", 6.85, 1.35, 5.9, C.accent2);
cartao(s, 0.6, 3.25, 5.9, 2.4, "Padronizar públicos diferentes", [
  "Mesma base, mesmo indicador, vereditos opostos",
  "A geração Z parecia beber menos só por ter sido entrevistada mais nova",
], C.accent1, "card_licao1", 16);
cartao(s, 6.85, 3.25, 5.9, 2.4, "O agregado esconde", [
  "Total: sem diferença entre as gerações",
  "Homens: queda leve e frágil; mulheres: alta robusta",
], C.accent2, "card_licao2", 16);
texto(s, "Antes de aceitar uma manchete como “a geração Z bebe menos”, é preciso perguntar: comparada na mesma idade? e dentro de quais grupos?",
  { x: 0.6, y: 5.9, w: 12.1, h: 0.8, fontSize: 18, italic: true, color: C.text2 });
s.addNotes(`Duas lições (1 min 30 s).
O que mais me impressionou no trabalho foram duas coisas. A primeira é a importância da padronização quando se comparam públicos diferentes: a mesma base, com o mesmo indicador, deu uma queda significativa sem padronizar e nenhuma diferença padronizando. A segunda: sem considerar o sexo, não havia diferença; separando, os homens têm uma queda leve e as mulheres, um aumento significativo.
A lição para quem lê notícias de mercado é perguntar sempre: comparado na mesma idade? E dentro de quais grupos?`);

s = conteudo("Discussão", "O que isso significa para as duas decisões");
cartao(s, 0.6, 1.5, 5.9, 3.3, "Decisão 1: nicho ou massa", "Nenhuma faixa de escolaridade bebe menos. A premissa das duas opções (uma queda do consumo) não aparece. A moderação dos homens que bebem aponta mais para baixo teor do que para a substituição do álcool, mas é um sinal frágil.", C.accent1, "card_dec1", 17);
cartao(s, 6.85, 1.5, 5.9, 3.3, "Decisão 2: estrutural ou fase", "Nos homens millennials e zillennials, as curvas são paralelas ao envelhecer: a mudança acompanha a geração, sem adiamento. A geração Z ainda não pode ser acompanhada; a resposta fica para as próximas edições.", C.accent2, "card_dec2", 17);
cartao(s, 0.6, 5.0, 12.1, 1.75, "Saúde pública", "A alta robusta entre as jovens indica que a prevenção ao consumo abusivo não pode mais tomar o público masculino como o único foco.", C.accent5, "card_saude", 15);
s.addNotes(`As duas decisões (1 min 30 s).
Nicho ou massa: a pergunta pressupunha uma queda do consumo, e ela não aparece em nenhuma faixa de escolaridade. Então nenhum dos dois posicionamentos tem base nesta tendência. O que existe, a moderação entre os homens que bebem, aponta mais para baixo teor do que para trocar o álcool, mas é frágil.
Estrutural ou fase: nos homens, as curvas paralelas sugerem uma mudança da geração; para a geração Z, ainda não dá para saber.
E para a saúde pública: a alta entre as jovens é o achado mais sólido, e pede atenção da prevenção.`);

s = conteudo("Discussão", "Recomendação: esperar mais dados antes de investir pesado");
texto(s, "A manchete não se confirma no Brasil, e o custo de agir com base nela é exatamente o erro que o projeto queria evitar.",
  { x: 0.6, y: 1.35, w: 12.1, h: 0.8, fontSize: 18, italic: true, color: C.text2 });
const recs = [
  ["Confirmar com outras fontes", "Além de pesquisa e autorrelato: dados de vendas e de volume (varejo, POF do IBGE, dados da própria empresa)."],
  ["Medir quantidade, não só exagero", "Investigar a relação entre consumo abusivo e quantidade consumida: o mercado é definido pelo volume."],
  ["Olhar para as jovens", "A mudança mais robusta da série: oportunidade de mercado e alerta de saúde pública."],
];
recs.forEach(([t, d], i) => {
  const x = 0.6 + i * 4.12;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.45, w: 3.85, h: 3.6, rectRadius: 0.12, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: "rec_" + i });
  circuloNum(s, i + 1, x + 0.25, 2.7, i === 2 ? C.accent2 : C.accent1, 0.7, 20);
  texto(s, t, { x: x + 0.25, y: 3.55, w: 3.35, h: 0.8, fontSize: 18, bold: true, color: C.text2 });
  texto(s, d, { x: x + 0.25, y: 4.4, w: 3.35, h: 1.55, fontSize: 15 });
});
s.addNotes(`Recomendação (1 min 30 s).
Se eu fosse o decisor, esperaria mais dados antes de um investimento de grande porte. A manchete não se confirma no Brasil, e agir com base nela é justamente o custo de erro que o projeto queria evitar.
Três próximos passos. Primeiro, confirmar com outras fontes além de pesquisa e autorrelato, como dados de vendas e de volume. Segundo, investigar a relação entre o consumo abusivo e a quantidade consumida: o Vigitel mede a ocorrência do exagero, não o volume, e é o volume que define o mercado. Terceiro, olhar para o público feminino jovem, onde está a mudança mais robusta.`);

// ================================================================ LIMITACOES
divisoria("Limitações", "Limitações", "Até onde os números permitem ir", `Para fechar, as limitações que condicionam tudo o que mostrei.`);

s = conteudo("Limitações", "O modo de coleta muda a resposta");
figura(s, FIG("f12_modo_coleta_2023.png"), 0.6, 1.35, 7.4, 5.4);
destaque(s, "+11,5 p.p.", "diferença entre celular e fixo no mesmo ano (2023), todas as idades", 8.4, 1.6, 4.3, C.accent2);
texto(s, lista([
  "Quem tem fixo é outro público (mais velho, casa estruturada)",
  "No celular a pessoa responde sozinha, sem a família por perto",
  ["Só a geração Z tem celular: a sensibilidade só por fixo reduz a alta feminina para +2,7 (n.s.)", { bold: true }],
]), { x: 8.4, y: 3.7, w: 4.3, h: 3.0, fontSize: 15, paraSpaceAfter: 8 });
s.addNotes(`Modo de coleta, f12 (1 min).
Em 2023 o Vigitel entrevistou metade por fixo e metade por celular: quem respondeu pelo celular declarou 11,5 pontos a mais de consumo abusivo. Parte é público diferente, parte é responder sozinho, sem constrangimento.
Isso pesa porque só a geração Z tem entrevistas por celular. Usando só o fixo, a alta feminina cai para 2,7 pontos e deixa de ser significativa. O modo de coleta não explica tudo, mas pesa.`);

s = conteudo("Limitações", "Limitações dos dados e do desenho");
cartao(s, 0.6, 1.4, 5.9, 2.6, "Alcance", ["Só capitais e Distrito Federal", "Recortes de geração do Pew, pensados para os EUA", "Não testa a manchete fora do Brasil"], C.accent1, "lim_alcance", 14);
cartao(s, 6.85, 1.4, 5.9, 2.6, "Medida", ["Autorrelato por telefone (desejabilidade social)", "Prevalência, não volume nem tipo de bebida", "Escolaridade no lugar de renda"], C.accent1, "lim_medida", 14);
cartao(s, 0.6, 4.2, 5.9, 2.6, "Coleta e amostra", ["Celular só na geração Z", "Quem não responde não aparece (possível MNAR)", "Sem 2022; pandemia em 2020-2021"], C.accent2, "lim_coleta", 14);
cartao(s, 6.85, 4.2, 5.9, 2.6, "Desenho", ["Idade, geração e época não se separam por completo", "Poucos casos por capital: n.s. = “não deu para afirmar”", "Muitos testes (21 correlatos, 27 capitais)"], C.accent2, "lim_desenho", 14);
s.addNotes(`Limitações (1 min 30 s).
Quatro grupos. Alcance: só capitais, e com recortes de geração importados dos Estados Unidos. Medida: o consumo é declarado por telefone, e se a norma social sobre o beber feminino mudou, parte da alta pode ser de declaração; além disso, o indicador é de prevalência, não de volume, e a escolaridade substitui a renda. Coleta: o celular só aparece na geração Z, e quem não atende não aparece. Desenho: idade, geração e época não se separam por completo, e muitos resultados não significativos querem dizer "não deu para afirmar", e não "não há diferença".`);

s = conteudo("Limitações", "Autoavaliação: o que foi respondido");
const status = [
  ["P1", "Respondida", "na mesma idade, sem queda; correta só depois da D14", C.accent6],
  ["P2", "Respondida, com poder limitado", "nenhuma faixa cai; vale para escolaridade, não renda", C.accent6],
  ["P3", "Respondida em parte", "geração Z ainda não chegou aos 25-29 anos", C.accent2],
  ["P4", "Respondida", "convergência dos sexos: alta feminina robusta", C.accent6],
  ["P5", "Pouco conclusiva", "uma capital fora da margem, compatível com acaso", C.accent2],
];
status.forEach(([p, st, d, cor], i) => {
  const y = 1.45 + i * 0.95;
  circuloNum(s, p, 0.6, y + 0.05, C.accent1, 0.65, 15);
  texto(s, st, { x: 1.45, y, w: 3.4, h: 0.4, fontSize: 16, bold: true, color: cor });
  texto(s, d, { x: 1.45, y: y + 0.4, w: 5.0, h: 0.45, fontSize: 14 });
});
cartao(s, 6.85, 1.4, 5.9, 4.6, "Dificuldades", [
  "Limites do Free Edition: a bronze precisou ser gravada em lotes de 20 mil linhas",
  "Tempo de execução: só a bronze levou cerca de 5 minutos; cada ajuste exigia rodar a cadeia de novo",
  "Refazer resultados, figuras e apresentação depois da D14",
], C.accent2, "card_dif", 17);
s.addNotes(`Autoavaliação (1 min).
P1, P2 e P4 foram respondidas; a P1 só ficou correta depois da padronização. A P3 foi respondida em parte, porque a geração Z ainda não chegou aos 25-29 anos. A P5 é pouco conclusiva, por falta de amostra por capital.
As dificuldades: os limites do Free Edition, que obrigaram a gravar a bronze em lotes; o tempo de execução; e ter que refazer tudo depois da padronização pela idade.`);

s = conteudo("Limitações", "O que eu faria diferente e os próximos passos");
cartao(s, 0.6, 1.4, 5.9, 5.2, "Se recomeçasse", [
  "Definir a comparação por geração e na mesma idade desde o objetivo",
  "Levantar as mudanças de método da pesquisa no primeiro dia",
  "Levar o pipeline ao Databricks mais cedo",
  "Fixar antes quais testes seriam feitos",
], C.accent1, "card_dif2", 17);
cartao(s, 6.85, 1.4, 5.9, 5.2, "Para uso contínuo", [
  "Job do Databricks a cada nova edição, com a qualidade bloqueando a carga",
  "Painel para o decisor, com a margem de erro sempre visível",
  "Juntar PNS, PeNSE e dados de vendas e volume",
  "Modelo idade-período-coorte e a geração Z aos 25-29",
], C.accent2, "card_ext", 17);
s.addNotes(`Faria diferente e próximos passos (1 min).
Se recomeçasse, definiria a comparação por geração e na mesma idade desde o objetivo, levantaria as mudanças de método no primeiro dia e levaria o pipeline ao Databricks mais cedo.
Para virar uma solução de uso contínuo: um job a cada nova edição do Vigitel, um painel para o decisor, outras fontes, como a PNS e dados de vendas, e um modelo que separe idade, período e geração.`);

s = pres.addSlide({ masterName: "CAPA", sectionTitle: "Limitações" });
s.addText("A geração Z bebe menos? Na mesma idade, não", { placeholder: "title" });
s.addText([
  { text: "Homens −4 p.p., mulheres +6 p.p.: os sexos convergem; sem diferença por classe. Antes de investir, mais dados.", options: { breakLine: true } },
  { text: "Obrigado. Perguntas?", options: { fontSize: 22, bold: true, color: C.background1 } },
], { placeholder: "body" });
s.addNotes(`Encerramento (30 s).
A geração Z bebe menos? Na mesma idade, não. Os homens bebem em excesso um pouco menos, as mulheres, mais: os sexos estão convergindo, e não há diferença por classe social. A minha recomendação ao decisor é buscar mais dados antes de um investimento de grande porte. Obrigado; fico à disposição para perguntas.`);

(async () => {
  await pres.writeFile({ fileName: SAIDA });
  await applyTheme(SAIDA, THEME);
  console.log("ok", SAIDA);
})();
