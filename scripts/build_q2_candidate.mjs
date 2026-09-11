import fs from "node:fs";
import fsp from "node:fs/promises";
import readline from "node:readline";
import crypto from "node:crypto";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const ROOT = "D:/数学建模（原神）";
const FREEZE = `${ROOT}/experiments/Q2_FREEZE_RUN`;
const TEMPLATE = `${ROOT}/A题/附件/附件3/result2.xlsx`;
const CANDIDATE = `${ROOT}/deliverables/candidate/result2.xlsx`;
const MANIFEST = `${ROOT}/experiments/Q2_CANONICAL_DATA_MANIFEST.json`;
const SOURCE = `${FREEZE}/run_1/official_samples.csv`;
const BATCH_SIZE = 2000;

function hashFile(path) {
  const hash = crypto.createHash("sha256");
  const data = fs.readFileSync(path);
  hash.update(data);
  return hash.digest("hex");
}

function roundHalfUp(text, places = 4) {
  const raw = String(text).trim();
  const negative = raw.startsWith("-");
  const unsigned = negative || raw.startsWith("+") ? raw.slice(1) : raw;
  const [wholePart, fractionPart = ""] = unsigned.split(".");
  const scale = 10 ** places;
  const fraction = (fractionPart + "0".repeat(places + 1)).slice(0, places + 1);
  let scaled = BigInt(wholePart || "0") * BigInt(scale) + BigInt(fraction.slice(0, places) || "0");
  if (fraction[places] >= "5") scaled += 1n;
  const signed = negative ? -scaled : scaled;
  return Number(signed) / scale;
}

async function main() {
  const config = JSON.parse(await fsp.readFile(`${FREEZE}/config.json`, "utf8"));
  const hashes = JSON.parse(await fsp.readFile(`${FREEZE}/output_hashes.json`, "utf8"));
  const manifest = JSON.parse(await fsp.readFile(MANIFEST, "utf8"));
  const entry = manifest.entries.find((item) => item.path === "experiments/Q2_FREEZE_RUN/run_1/official_samples.csv");
  if (!entry || entry.status !== "PRODUCTION_CANONICAL") throw new Error("formal run_1 source is not PRODUCTION_CANONICAL");
  const sourceHash = hashFile(SOURCE);
  if (sourceHash !== hashes.run_1.sampled_output || sourceHash !== entry.sha256) throw new Error("run_1 source hash does not match frozen lineage");
  if (fs.existsSync(CANDIDATE)) throw new Error(`refusing to overwrite existing candidate: ${CANDIDATE}`);
  await fsp.mkdir(`${ROOT}/deliverables/candidate`, { recursive: true });
  await fsp.copyFile(TEMPLATE, CANDIDATE);
  const input = await FileBlob.load(CANDIDATE);
  const workbook = await SpreadsheetFile.importXlsx(input);
  const temperature = workbook.worksheets.getItem("温度");
  const moisture = workbook.worksheets.getItem("水分浓度");
  const radii = Array.from({ length: 21 }, (_, index) => index / 10);
  temperature.getRange("B1:V1").values = [radii];
  moisture.getRange("B1:V1").values = [radii];
  const tBatch = [];
  const cBatch = [];
  let currentTime = null;
  let tValues = [];
  let cValues = [];
  let rowsWritten = 0;

  function flush() {
    if (!tBatch.length) return;
    const start = 1 + rowsWritten - tBatch.length;
    temperature.getRangeByIndexes(start, 0, tBatch.length, 22).values = tBatch.splice(0, tBatch.length);
    moisture.getRangeByIndexes(start, 0, cBatch.length, 22).values = cBatch.splice(0, cBatch.length);
  }

  const stream = fs.createReadStream(SOURCE, { encoding: "utf8" });
  const lines = readline.createInterface({ input: stream, crlfDelay: Infinity });
  for await (const line of lines) {
    if (!line || line.startsWith("time_s,")) continue;
    const parts = line.split(",");
    if (parts.length !== 5) throw new Error(`malformed source row: ${line}`);
    const time = Number(parts[0]);
    const radiusIndex = Math.round(Number(parts[1]) * 10);
    if (!Number.isInteger(time) || time < 1 || time > config.final_horizon_s || radiusIndex < 0 || radiusIndex > 20) throw new Error(`invalid source key: ${line}`);
    if (currentTime === null) currentTime = time;
    if (time !== currentTime) {
      if (tValues.length !== 21 || cValues.length !== 21) throw new Error(`source time ${currentTime} does not have 21 radii`);
      tBatch.push([currentTime, ...tValues]);
      cBatch.push([currentTime, ...cValues]);
      rowsWritten += 1;
      if (tBatch.length >= BATCH_SIZE) flush();
      currentTime = time;
      tValues = [];
      cValues = [];
    }
    if (tValues[radiusIndex] !== undefined) throw new Error(`duplicate source key t=${time}, radius=${radiusIndex / 10}`);
    tValues[radiusIndex] = roundHalfUp(parts[3]);
    cValues[radiusIndex] = roundHalfUp(parts[4]);
  }
  if (currentTime !== null) {
    if (tValues.length !== 21 || cValues.length !== 21) throw new Error(`source time ${currentTime} does not have 21 radii`);
    tBatch.push([currentTime, ...tValues]);
    cBatch.push([currentTime, ...cValues]);
    rowsWritten += 1;
  }
  flush();
  if (rowsWritten !== Number(config.final_horizon_s)) throw new Error(`wrote ${rowsWritten} time rows, expected ${config.final_horizon_s}`);
  for (const sheet of [temperature, moisture]) {
    sheet.getRange(`A2:V${config.final_horizon_s + 1}`).format.numberFormat = "0.0000";
    sheet.getRange(`A2:A${config.final_horizon_s + 1}`).format.numberFormat = "0";
  }
  workbook.recalculate();
  const check = await workbook.inspect({ kind: "table", range: "温度!A1:V5", include: "values,formulas", tableMaxRows: 5, tableMaxCols: 22, maxChars: 5000 });
  console.log(check.ndjson);
  const preview = await workbook.render({ sheetName: "温度", range: "A1:V12", scale: 1.5, format: "png" });
  await fsp.writeFile(`${ROOT}/experiments/Q2_FREEZE_RUN/candidate_preview.png`, new Uint8Array(await preview.arrayBuffer()));
  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(CANDIDATE);
  console.log(JSON.stringify({ status: "PASS", candidate: CANDIDATE, source_sha256: sourceHash, rows_written: rowsWritten, candidate_sha256: hashFile(CANDIDATE) }, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exitCode = 1;
});
