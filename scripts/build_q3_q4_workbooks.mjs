import fs from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = fileURLToPath(new URL("../", import.meta.url)).replace(/\\$/, "");
const candidate = `${root}/deliverables/candidate`;
const experiments = `${root}/experiments`;
const paper = `${candidate}/paper`;
const tables = `${candidate}/tables`;

function columnName(index) {
  let n = index + 1;
  let result = "";
  while (n > 0) {
    const rem = (n - 1) % 26;
    result = String.fromCharCode(65 + rem) + result;
    n = Math.floor((n - 1) / 26);
  }
  return result;
}

function parseCsv(text) {
  return text.trimEnd().split(/\r?\n/).map((line) => line.split(","));
}

function numberOrBlank(value) {
  if (value === "" || value === undefined || value === null) return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : value;
}

async function importTemplate(path) {
  const bytes = await fs.readFile(path);
  return SpreadsheetFile.importXlsx(bytes);
}

async function writeOfficialMatrix(templatePath, sourceCsv, outputPath, kind) {
  const workbook = await importTemplate(templatePath);
  const sheet = workbook.worksheets.getItemAt(0);
  const templateHeader = sheet.getRange("A1").values[0][0];
  const templateSurface = sheet.getRange("F1").values[0][0];
  const parsed = parseCsv(await fs.readFile(sourceCsv, "utf8"));
  const rows = [];
  if (kind === "q3") {
    rows.push([templateHeader, ...Array.from({ length: 21 }, (_, i) => i / 10)]);
    for (const source of parsed.slice(1)) rows.push([Number(source[0]), ...source.slice(1, 22).map(numberOrBlank)]);
  } else {
    rows.push([templateHeader, ...Array.from({ length: 20 }, (_, i) => i / 10), templateSurface]);
    for (const source of parsed.slice(1)) rows.push([Number(source[0]), ...source.slice(1, 22).map(numberOrBlank)]);
  }
  const end = `${columnName(rows[0].length - 1)}${rows.length}`;
  sheet.getRange(`A1:${end}`).values = rows;
  sheet.getRange(`A1:${end}`).format.font = { name: "Microsoft YaHei", size: 10 };
  sheet.getRange(`A1:${columnName(rows[0].length - 1)}1`).format = {
    fill: "#D9EAF7",
    font: { name: "Microsoft YaHei", size: 10, bold: true, color: "#000000" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
  };
  sheet.getRange(`A2:A${rows.length}`).format.numberFormat = "0.0000";
  sheet.getRange(`B2:${columnName(rows[0].length - 1)}${rows.length}`).format.numberFormat = "0.0000";
  sheet.getRange(`A1:${end}`).format.borders = { preset: "all", style: "thin", color: "#D9D9D9" };
  sheet.freezePanes.freezeRows(1);
  sheet.showGridLines = false;
  sheet.getRange(`A:${columnName(rows[0].length - 1)}`).format.columnWidth = 14;
  sheet.getRange("A:A").format.columnWidth = 16;
  const xlsx = await SpreadsheetFile.exportXlsx(workbook);
  await xlsx.save(outputPath);
}

async function writeTable(sourceCsv, outputPath) {
  const rows = parseCsv(await fs.readFile(sourceCsv, "utf8")).map((row, rowIndex) =>
    row.map((value, colIndex) => {
      if (rowIndex === 0 || colIndex === 0) return value;
      return numberOrBlank(value);
    }),
  );
  const workbook = Workbook.create();
  const sheet = workbook.worksheets.add("Table");
  const end = `${columnName(rows[0].length - 1)}${rows.length}`;
  sheet.getRange(`A1:${end}`).values = rows;
  sheet.getRange(`A1:${end}`).format.font = { name: "Microsoft YaHei", size: 10 };
  sheet.getRange(`A1:${columnName(rows[0].length - 1)}1`).format = {
    fill: "#D9EAF7",
    font: { name: "Microsoft YaHei", size: 10, bold: true },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
  };
  if (rows.length > 1) sheet.getRange(`B2:${columnName(rows[0].length - 1)}${rows.length}`).format.numberFormat = "0.0000";
  sheet.getRange(`A1:${end}`).format.borders = { preset: "all", style: "thin", color: "#D9D9D9" };
  sheet.freezePanes.freezeRows(1);
  sheet.showGridLines = false;
  sheet.getRange(`A:${columnName(rows[0].length - 1)}`).format.columnWidth = 16;
  const xlsx = await SpreadsheetFile.exportXlsx(workbook);
  await xlsx.save(outputPath);
}

await fs.mkdir(`${candidate}/tables`, { recursive: true });
await fs.mkdir(`${paper}/tables`, { recursive: true });
await writeOfficialMatrix(
  `${root}/A题/附件/附件3/result3.xlsx`,
  `${experiments}/Q3_PRODUCTION/q3_result3_matrix_full_precision.csv`,
  `${candidate}/result3.xlsx`,
  "q3",
);
await writeOfficialMatrix(
  `${root}/A题/附件/附件3/result4.xlsx`,
  `${experiments}/Q4_PRODUCTION/q4_result4_matrix_full_precision.csv`,
  `${candidate}/result4.xlsx`,
  "q4",
);
await writeTable(`${experiments}/Q3_PRODUCTION/table5.csv`, `${tables}/q3_table5.xlsx`);
await fs.copyFile(`${tables}/q3_table5.xlsx`, `${paper}/tables/table5_q3.xlsx`);
await writeTable(`${experiments}/Q4_PRODUCTION/table6.csv`, `${tables}/q4_table6.xlsx`);
await fs.copyFile(`${tables}/q4_table6.xlsx`, `${paper}/tables/table6_q4.xlsx`);
