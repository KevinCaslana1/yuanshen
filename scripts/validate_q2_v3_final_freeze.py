"""Read-only validation and freeze-record writer for the approved Q2 V3 final.

This script never runs a Q2 solver, rewrites a workbook, or regenerates a figure.
It only reads the copied final artifacts and writes the audit record after every
check has passed.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any

import openpyxl
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "experiments" / "Q2_FREEZE_RUN_V3"
CANDIDATE = ROOT / "deliverables" / "candidate" / "result2.xlsx"
FINAL = ROOT / "deliverables" / "final" / "result2.xlsx"
SOURCE_FIGURES = ROOT / "figures" / "q2" / "final"
FINAL_FIGURES = ROOT / "deliverables" / "final" / "figures" / "q2"
FREEZE_DIR = ROOT / "experiments" / "Q2_FINAL_FREEZE"
FREEZE_RECORD = FREEZE_DIR / "freeze_record.json"
FINAL_MANIFEST = ROOT / "deliverables" / "final" / "Q2_MANIFEST.json"
EXPECTED_CANDIDATE_COMMIT = "0172972"
EXPECTED_HORIZON = 228536
EXPECTED_ROWS = EXPECTED_HORIZON + 1
EXPECTED_COLUMNS = 22
EXPECTED_FIGURE_COUNT = 11
EXPECTED_FIGURE_FILES = EXPECTED_FIGURE_COUNT * 2


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def decimal_value(value: Any) -> Decimal | None:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return number if number.is_finite() else None


def q4(number: Decimal) -> Decimal:
    return number.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def git_output(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def validate_workbook(path: Path) -> dict[str, Any]:
    errors: list[str] = []
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=False)
    sheet_results: list[dict[str, Any]] = []
    try:
        if len(workbook.sheetnames) != 2:
            errors.append(f"sheet count={len(workbook.sheetnames)}, expected 2")
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            row_count = 0
            max_columns = 0
            formula_count = 0
            data_cell_count = 0
            q4_format_count = 0
            bad_cells: list[str] = []
            rows = sheet.iter_rows()
            header = next(rows, ())
            if len(header) != EXPECTED_COLUMNS:
                errors.append(f"{sheet_name}: header columns={len(header)}")
            else:
                for index, cell in enumerate(header[1:], start=0):
                    value = decimal_value(cell.value)
                    expected = Decimal(index) / Decimal(10)
                    if value != expected:
                        errors.append(f"{sheet_name}: radius header mismatch at {index}")
            row_count = 1 if header else 0
            for expected_time, row in enumerate(rows, start=1):
                row_count += 1
                max_columns = max(max_columns, len(row))
                if len(row) != EXPECTED_COLUMNS:
                    if len(bad_cells) < 5:
                        bad_cells.append(f"row {expected_time}: columns={len(row)}")
                    continue
                time_value = decimal_value(row[0].value)
                if time_value != Decimal(expected_time):
                    if len(bad_cells) < 5:
                        bad_cells.append(f"row {expected_time}: time={row[0].value!r}")
                for cell in row[1:]:
                    if isinstance(cell.value, str) and cell.value.startswith("="):
                        formula_count += 1
                    value = decimal_value(cell.value)
                    if value is None:
                        if len(bad_cells) < 5:
                            bad_cells.append(f"{cell.coordinate}: non-finite/non-numeric")
                        continue
                    data_cell_count += 1
                    if value != q4(value) and len(bad_cells) < 5:
                        bad_cells.append(f"{cell.coordinate}: not four-decimal value")
                    if cell.number_format == "0.0000":
                        q4_format_count += 1
                    elif len(bad_cells) < 5:
                        bad_cells.append(f"{cell.coordinate}: format={cell.number_format!r}")
            if row_count != EXPECTED_ROWS:
                errors.append(f"{sheet_name}: rows={row_count}, expected {EXPECTED_ROWS}")
            if max_columns != EXPECTED_COLUMNS:
                errors.append(f"{sheet_name}: columns={max_columns}, expected {EXPECTED_COLUMNS}")
            if formula_count:
                errors.append(f"{sheet_name}: formula_count={formula_count}")
            if data_cell_count != (EXPECTED_ROWS - 1) * (EXPECTED_COLUMNS - 1):
                errors.append(f"{sheet_name}: data_cell_count={data_cell_count}")
            if q4_format_count != data_cell_count:
                errors.append(f"{sheet_name}: q4_format_count={q4_format_count}/{data_cell_count}")
            if bad_cells:
                errors.extend(f"{sheet_name}: {item}" for item in bad_cells)
            sheet_results.append(
                {
                    "sheet": sheet_name,
                    "rows": row_count,
                    "columns": max_columns,
                    "formula_count": formula_count,
                    "data_cell_count": data_cell_count,
                    "numeric_format": "0.0000",
                    "numeric_format_count": q4_format_count,
                    "numeric_format_status": q4_format_count == data_cell_count,
                }
            )
    finally:
        workbook.close()
    return {
        "status": "PASS" if not errors else "FAIL",
        "sheet_count": len(sheet_results),
        "expected_shape_per_sheet": [EXPECTED_ROWS, EXPECTED_COLUMNS],
        "sheets": sheet_results,
        "no_formulas": not any(item["formula_count"] for item in sheet_results),
        "four_decimal_numeric_format": all(item["numeric_format_status"] for item in sheet_results),
        "errors": errors,
    }


def validate_figures() -> dict[str, Any]:
    manifest_path = ROOT / "figures" / "q2" / "FIGURE_MANIFEST.json"
    trace_path = ROOT / "figures" / "q2" / "FIGURE_VALIDATION.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    figures: list[dict[str, Any]] = []
    if manifest.get("status") != "PASS":
        errors.append("source figure manifest is not PASS")
    if trace.get("status") != "PASS":
        errors.append("source figure validation is not PASS")
    if manifest.get("no_smoothing") is not True or manifest.get("no_numeric_interpolation") is not True:
        errors.append("source figure manifest has invalid smoothing/interpolation flags")
    source_entries = manifest.get("figures", [])
    if len(source_entries) != EXPECTED_FIGURE_COUNT:
        errors.append(f"source figure groups={len(source_entries)}, expected {EXPECTED_FIGURE_COUNT}")
    final_files = sorted(
        path for path in FINAL_FIGURES.iterdir()
        if path.is_file() and path.suffix.lower() in {".png", ".svg"}
    ) if FINAL_FIGURES.is_dir() else []
    if len(final_files) != EXPECTED_FIGURE_FILES:
        errors.append(f"final figure files={len(final_files)}, expected {EXPECTED_FIGURE_FILES}")
    for entry in source_entries:
        figure_id = entry["figure_id"]
        stem = Path(entry["png_path"]).stem
        source_png = SOURCE_FIGURES / f"{stem}.png"
        source_svg = SOURCE_FIGURES / f"{stem}.svg"
        final_png = FINAL_FIGURES / source_png.name
        final_svg = FINAL_FIGURES / source_svg.name
        if not source_png.is_file() or not source_svg.is_file():
            errors.append(f"missing source files for {figure_id}")
        if not final_png.is_file() or not final_svg.is_file():
            errors.append(f"missing final files for {figure_id}")
            continue
        source_png_hash = sha256(source_png)
        source_svg_hash = sha256(source_svg)
        final_png_hash = sha256(final_png)
        final_svg_hash = sha256(final_svg)
        if source_png_hash != final_png_hash:
            errors.append(f"PNG hash mismatch for {figure_id}")
        if source_svg_hash != final_svg_hash:
            errors.append(f"SVG hash mismatch for {figure_id}")
        with Image.open(final_png) as image:
            dpi = image.info.get("dpi", (0.0, 0.0))
            dpi_x, dpi_y = float(dpi[0]), float(dpi[1])
            if dpi_x < 299.0 or dpi_y < 299.0:
                errors.append(f"PNG dpi below 300 for {figure_id}: {dpi}")
        figures.append(
            {
                "figure_id": figure_id,
                "png_path": relative(final_png),
                "png_sha256": final_png_hash,
                "png_size_bytes": final_png.stat().st_size,
                "png_dpi": [dpi_x, dpi_y],
                "svg_path": relative(final_svg),
                "svg_sha256": final_svg_hash,
                "svg_size_bytes": final_svg.stat().st_size,
                "source_png_sha256": source_png_hash,
                "source_svg_sha256": source_svg_hash,
            }
        )
    if trace.get("random_trace_count") != 30 or trace.get("random_trace_pass_count") != 30:
        errors.append("source figure trace is not 30/30")
    return {
        "status": "PASS" if not errors else "FAIL",
        "figure_group_count": len(source_entries),
        "figure_file_count": len(final_files),
        "png_svg_groups": "11/11",
        "png_dpi_minimum": 300,
        "trace": "30/30",
        "no_smoothing": True,
        "no_numeric_interpolation": True,
        "files": figures,
        "errors": errors,
    }


def main() -> int:
    errors: list[str] = []
    if not CANDIDATE.is_file() or not FINAL.is_file():
        errors.append("candidate or final workbook is missing")
    if git_output("rev-parse", "HEAD")[:7] != EXPECTED_CANDIDATE_COMMIT:
        errors.append(f"HEAD is not candidate commit {EXPECTED_CANDIDATE_COMMIT}")
    protected = [line for line in git_output("diff", "--name-only", "--", "A题", "src/q2").splitlines() if line]
    if protected:
        errors.append(f"protected paths modified: {protected}")
    if not (ROOT / "experiments" / "Q2_FREEZE_RUN_V3_FAILED_HORIZON_20260912").is_dir():
        errors.append("historical failed horizon experiment is missing")
    candidate_hash = sha256(CANDIDATE)
    final_hash = sha256(FINAL)
    candidate_size = CANDIDATE.stat().st_size
    final_size = FINAL.stat().st_size
    if candidate_hash != final_hash or candidate_size != final_size:
        errors.append("candidate/final workbook hash or size mismatch")

    workbook_validation = validate_workbook(FINAL)
    if workbook_validation["status"] != "PASS":
        errors.extend(workbook_validation["errors"])
    figures = validate_figures()
    if figures["status"] != "PASS":
        errors.extend(figures["errors"])

    v3_validation = json.loads((V3 / "validation.json").read_text(encoding="utf-8"))
    candidate_validation = json.loads((V3 / "candidate_validation.json").read_text(encoding="utf-8"))
    source_figure_validation = json.loads((ROOT / "figures" / "q2" / "FIGURE_VALIDATION.json").read_text(encoding="utf-8"))
    determinism = json.loads((V3 / "determinism.json").read_text(encoding="utf-8"))
    config = json.loads((V3 / "config.json").read_text(encoding="utf-8"))
    run_gate = v3_validation["checks"]["run_1_and_run_2"]["detail"]
    if candidate_validation.get("status") != "PASS" or candidate_validation.get("candidate_sha256") != candidate_hash:
        errors.append("candidate trace evidence/hash mismatch")
    if candidate_validation.get("random_trace_pass_count") != 100 or candidate_validation.get("random_trace_total") != 100:
        errors.append("workbook trace evidence is not 100/100")
    if any(item.get("count") != 30 or item.get("pass_count") != 30 for item in candidate_validation.get("paper_tables", {}).values()):
        errors.append("Table3/4 trace evidence is not 60/60")
    if v3_validation.get("status") != "ALL_DELIVERABLE_GATES_PASS":
        errors.append("V3 gates are not ALL_DELIVERABLE_GATES_PASS")
    if determinism.get("status") != "PASS":
        errors.append("V3 determinism is not PASS")
    if not all(run_gate.get(run, {}).get("fresh_start") is True for run in ("run_1", "run_2")):
        errors.append("Run1/Run2 fresh-start evidence is not PASS")
    if config.get("predeclared_event_bracket_s") != [206935.0, 206935.25] or config.get("final_horizon_s") != EXPECTED_HORIZON:
        errors.append("V3 bracket or final horizon mismatch")

    test_run = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True
    )
    test_output = (test_run.stdout + "\n" + test_run.stderr).strip()
    test_passed = test_run.returncode == 0 and bool(re.search(r"56 passed", test_output))
    if not test_passed:
        errors.append(f"pytest did not report 56 passed: {test_output[-500:]}")

    status = "APPROVED" if not errors else "BLOCKED"
    record = {
        "schema_version": "Q2_V3_FINAL_FREEZE_RECORD_V1",
        "status": status,
        "q2_version": "V3 production freeze",
        "freeze_approval_status": "APPROVED",
        "candidate_commit": EXPECTED_CANDIDATE_COMMIT,
        "run_lineage": {
            "run_1": "independent fresh run from t=0",
            "run_2": "independent fresh run from t=0",
            "run_1_run_2_byte_hash_identical": determinism.get("status") == "PASS",
            "determinism": determinism,
        },
        "passive_interval_s": [206935.0, 206935.25],
        "final_horizon_s": EXPECTED_HORIZON,
        "workbook": {
            "candidate_path": relative(CANDIDATE),
            "final_path": relative(FINAL),
            "candidate_sha256": candidate_hash,
            "final_sha256": final_hash,
            "sha256_identical": candidate_hash == final_hash,
            "candidate_size_bytes": candidate_size,
            "final_size_bytes": final_size,
            "size_identical": candidate_size == final_size,
            "validation": workbook_validation,
            "trace": {
                "random_trace": "100/100",
                "table3_temperature": "30/30",
                "table4_moisture": "30/30",
                "basis": "validated candidate evidence plus byte-identical final copy",
            },
        },
        "figures": figures,
        "tests": {
            "command": "pytest -q",
            "returncode": test_run.returncode,
            "result": "56 passed" if test_passed else test_output,
        },
        "q1_status": "FROZEN; pointwise error zero-crossing / cancellation dip",
        "q3_status": "NOT STARTED",
        "q4_status": "NOT STARTED",
        "historical_failure_retained": "experiments/Q2_FREEZE_RUN_V3_FAILED_HORIZON_20260912",
        "protected_paths": {"A题": "unchanged", "src/q2": "unchanged"},
        "git": {"candidate_commit": EXPECTED_CANDIDATE_COMMIT, "protected_diff_paths": protected},
        "errors": errors,
    }
    if errors:
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 1
    FREEZE_DIR.mkdir(parents=True, exist_ok=True)
    FREEZE_RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    final_manifest = {
        "schema_version": "Q2_V3_FINAL_DELIVERY_MANIFEST_V1",
        "status": "APPROVED",
        "q2_version": "V3 production freeze",
        "freeze_record": relative(FREEZE_RECORD),
        "result2": {"path": relative(FINAL), "sha256": final_hash, "size_bytes": final_size},
        "figures_directory": relative(FINAL_FIGURES),
        "figure_count": figures["figure_group_count"],
        "figure_files": figures["figure_file_count"],
        "figure_sha256": {item["png_path"]: item["png_sha256"] for item in figures["files"]} | {item["svg_path"]: item["svg_sha256"] for item in figures["files"]},
        "candidate_commit": EXPECTED_CANDIDATE_COMMIT,
        "passive_interval_s": [206935.0, 206935.25],
        "final_horizon_s": EXPECTED_HORIZON,
        "trace": {"workbook": "100/100", "table3_table4": "60/60", "figures": "30/30"},
        "tests": "56 passed",
        "freeze_approval_status": "APPROVED",
        "q1_q3_q4_status": {"Q1": "FROZEN", "Q2": "FROZEN", "Q3": "NOT STARTED", "Q4": "NOT STARTED"},
    }
    FINAL_MANIFEST.write_text(json.dumps(final_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "record": relative(FREEZE_RECORD), "manifest": relative(FINAL_MANIFEST), "workbook": record["workbook"], "figures": {k: figures[k] for k in ("figure_group_count", "figure_file_count", "png_svg_groups", "png_dpi_minimum", "trace")}, "tests": record["tests"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
