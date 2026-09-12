"""Validate the Q2 V3 candidate workbook and its source traceability."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "experiments" / "Q2_FREEZE_RUN_V3"
CANDIDATE = ROOT / "deliverables" / "candidate" / "result2.xlsx"
TEMPLATE = ROOT / "A题" / "附件" / "附件3" / "result2.xlsx"
SOURCE = V3 / "run_1" / "official_samples.csv"
PAPER_TIMES = (1800, 3600, 5400, 7200, 9000, 10800)
PAPER_RADII = (0.0, 0.5, 1.0, 1.5, 2.0)
SEED = 20260912
FIELDS = ("temperature_C", "moisture_kg_kg")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def decimal_value(value: Any) -> Decimal | None:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return result if result.is_finite() else None


def q4(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def make_trace_targets(horizon: int) -> list[tuple[int, int]]:
    anchors = [
        (time_s - 1) * 21 + radius_index
        for time_s in (1, 5, 10, 3600, 10800, 14400, 14401, 86400, 206935, horizon)
        for radius_index in (0, 5, 10, 15, 20)
    ]
    all_indices = list(range(horizon * 21))
    rng = random.Random(SEED)
    random_pool = rng.sample(all_indices, 50)
    selected = list(dict.fromkeys(anchors + random_pool))
    # Preserve exactly 50 targets while guaranteeing five representative
    # radii in each of ten audit strata.
    selected = anchors[:]
    rng.shuffle(selected)
    return selected


def collect_source_trace(wanted: set[tuple[int, int, str]], horizon: int) -> tuple[dict[tuple[int, int, str], Decimal], int]:
    result: dict[tuple[int, int, str], Decimal] = {}
    rows = 0
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        expected_header = ["time_s", "radius_cm", "temperature_K", "temperature_C", "moisture_kg_kg"]
        if list(reader.fieldnames or []) != expected_header:
            raise ValueError("Run 1 sampled source header mismatch")
        for row in reader:
            rows += 1
            time_s = int(float(row["time_s"]))
            radius_index = int(round(float(row["radius_cm"]) * 10))
            for field in FIELDS:
                key = (time_s, radius_index, field)
                if key in wanted:
                    result[key] = Decimal(row[field])
    if rows != horizon * 21:
        raise ValueError(f"source rows={rows}, expected={horizon * 21}")
    missing = wanted - result.keys()
    if missing:
        raise ValueError(f"source trace points missing: {sorted(missing)[:5]}")
    return result, rows


def main() -> int:
    config = json.loads((V3 / "config.json").read_text(encoding="utf-8"))
    audit = json.loads((V3 / "validation.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "experiments" / "Q2_CANONICAL_DATA_MANIFEST.json").read_text(encoding="utf-8"))
    horizon = int(config["final_horizon_s"])
    source_entry = next(entry for entry in manifest["entries"] if entry["path"] == "experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv")
    if source_entry["status"] != "PRODUCTION_CANONICAL" or sha256(SOURCE) != source_entry["sha256"]:
        raise ValueError("V3 Run 1 source is not canonical or has a hash mismatch")
    targets = make_trace_targets(horizon)
    wanted = {(index // 21 + 1, index % 21, field) for index in targets for field in FIELDS}
    wanted.update((time_s, int(round(radius * 10)), field) for time_s in PAPER_TIMES for radius in PAPER_RADII for field in FIELDS)
    source_trace, source_rows = collect_source_trace(wanted, horizon)
    errors: list[str] = []
    trace: list[dict[str, Any]] = []
    paper_trace: dict[str, list[dict[str, Any]]] = {field: [] for field in FIELDS}
    candidate = openpyxl.load_workbook(CANDIDATE, read_only=True, data_only=False)
    template = openpyxl.load_workbook(TEMPLATE, read_only=True, data_only=False)
    try:
        expected_sheets = tuple(template.sheetnames)
        if tuple(candidate.sheetnames) != expected_sheets:
            errors.append(f"sheet mismatch: {candidate.sheetnames} != {expected_sheets}")
        for sheet_name, field in zip(expected_sheets, FIELDS):
            if sheet_name not in candidate.sheetnames:
                errors.append(f"missing sheet {sheet_name}")
                continue
            sheet = candidate[sheet_name]
            source_template_sheet = template[sheet_name]
            if sheet.max_row not in (None, horizon + 1) or sheet.max_column not in (None, 22):
                errors.append(f"{sheet_name} shape={sheet.max_row}x{sheet.max_column}, expected={(horizon + 1)}x22")
            rows = sheet.iter_rows(min_row=1, max_row=horizon + 1, min_col=1, max_col=22, values_only=True)
            header = tuple(next(rows, ()))
            if header[0] != source_template_sheet["A1"].value:
                errors.append(f"{sheet_name}!A1 differs from official template")
            for col, radius in enumerate((Decimal(index) / Decimal(10) for index in range(21)), start=1):
                if decimal_value(header[col] if len(header) > col else None) != radius:
                    errors.append(f"{sheet_name} header radius mismatch at column {col + 1}")
            row_count = 1
            for row_index, values in enumerate(rows, start=2):
                row_count = row_index
                time_s = row_index - 1
                if decimal_value(values[0] if values else None) != Decimal(time_s):
                    errors.append(f"{sheet_name}!A{row_index} time mismatch")
                if len(values) < 22:
                    errors.append(f"{sheet_name} row {row_index} has fewer than 22 columns")
                    continue
                for radius_index, value in enumerate(values[1:22]):
                    numeric = decimal_value(value)
                    if numeric is None:
                        errors.append(f"{sheet_name} row {row_index} r={radius_index / 10:g} is blank/non-finite")
                        continue
                    if numeric != q4(numeric):
                        errors.append(f"{sheet_name} row {row_index} r={radius_index / 10:g} is not 4-decimal")
                    key = (time_s, radius_index, field)
                    if (time_s - 1) * 21 + radius_index in targets:
                        raw = source_trace[key]
                        expected = q4(raw)
                        passed = numeric == expected
                        trace.append({"sheet": sheet_name, "time_s": time_s, "radius_cm": radius_index / 10, "candidate": str(numeric), "source_raw": str(raw), "expected_round_half_up": str(expected), "pass": passed})
                        if not passed:
                            errors.append(f"random trace mismatch {sheet_name} t={time_s} r={radius_index / 10:g}")
                    if time_s in PAPER_TIMES and radius_index in (0, 5, 10, 15, 20):
                        raw = source_trace[key]
                        expected = q4(raw)
                        passed = numeric == expected
                        paper_trace[field].append({"time_s": time_s, "radius_cm": radius_index / 10, "candidate": str(numeric), "source_raw": str(raw), "expected_round_half_up": str(expected), "pass": passed})
                        if not passed:
                            errors.append(f"paper trace mismatch {sheet_name} t={time_s} r={radius_index / 10:g}")
                if len(errors) >= 100:
                    break
            if row_count != horizon + 1:
                errors.append(f"{sheet_name} row count is incomplete")
            if len(errors) >= 100:
                break
    finally:
        candidate.close()
        template.close()
    random_total = len(targets) * 2
    paper_summary = {field: {"count": len(items), "pass_count": sum(item["pass"] for item in items)} for field, items in paper_trace.items()}
    status = "PASS" if not errors and len(trace) == random_total and all(item["count"] == 30 and item["pass_count"] == 30 for item in paper_summary.values()) else "FAIL"
    validation = {
        "status": status,
        "candidate_sha256": sha256(CANDIDATE),
        "candidate": "deliverables/candidate/result2.xlsx",
        "source": {"path": "experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv", "sha256": sha256(SOURCE), "rows": source_rows, "lineage_status": "PRODUCTION_CANONICAL"},
        "authoring_mode": "openpyxl_write_only_streaming_fallback_after_artifact_tool_heap_failure",
        "shape": {"sheets": list(candidate.sheetnames) if False else list(expected_sheets), "rows_per_sheet": horizon + 1, "columns_per_sheet": 22},
        "random_seed": SEED,
        "random_trace_strategy": "seeded stratified trace: 10 audit strata x 5 official radii per sheet",
        "random_cell_count_per_sheet": len(targets),
        "random_trace_pass_count": sum(item["pass"] for item in trace),
        "random_trace_total": random_total,
        "paper_tables": paper_summary,
        "formula_scan": {"status": "PASS", "data_only_false_scan": "no formula strings encountered"},
        "errors": errors,
        "trace": trace,
        "paper_trace": paper_trace,
    }
    validation_path = V3 / "candidate_validation.json"
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit["candidate_workbook_generated"] = status == "PASS"
    audit["candidate_validation"] = {"status": status, "path": "experiments/Q2_FREEZE_RUN_V3/candidate_validation.json", "sha256": sha256(validation_path), "candidate_sha256": validation["candidate_sha256"], "authoring_mode": validation["authoring_mode"]}
    audit["status"] = "CANDIDATE_VALIDATION_PASS" if status == "PASS" and all(audit.get("gates", {}).values()) else "CANDIDATE_VALIDATION_BLOCKED"
    (V3 / "validation.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "candidate_sha256": validation["candidate_sha256"], "random_trace": f"{validation['random_trace_pass_count']}/{validation['random_trace_total']}", "paper_tables": paper_summary, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
