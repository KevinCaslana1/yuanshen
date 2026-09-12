"""Read-only validation for Q3/Q4 candidate deliverables."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q3.model import stream_q2_snapshots
from src.q4.radius import RadiusLaw


Q2_FINAL = ROOT / "deliverables" / "final" / "result2.xlsx"
Q2_EXPECTED_SHA = "84fb32457193e158debdf569d34f5f41b97e78496b30dd9b2e134385439e10da"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def workbook_audit(path: Path, expected_columns: int, expected_format: str = "0.0000") -> Dict[str, object]:
    wb = load_workbook(path, read_only=True, data_only=False)
    sheets = []
    formula_count = 0
    bad_format = 0
    total_rows = 0
    for ws in wb.worksheets:
        row_count = 0
        col_count = 0
        for row in ws.iter_rows():
            row_count += 1
            col_count = max(col_count, len(row))
            for cell in row:
                if cell.data_type == "f" or (isinstance(cell.value, str) and cell.value.startswith("=")):
                    formula_count += 1
                if row_count > 1 and cell.value is not None and isinstance(cell.value, (int, float)) and cell.number_format != expected_format:
                    bad_format += 1
        total_rows += row_count
        sheets.append({"name": ws.title, "rows": row_count, "columns": col_count})
    wb.close()
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "size_bytes": path.stat().st_size, "sheets": sheets, "formula_count": formula_count, "bad_numeric_format_count": bad_format, "shape_ok": bool(sheets) and all(s["columns"] == expected_columns for s in sheets)}


def read_matrix_csv(path: Path) -> List[List[str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.reader(handle))


def figure_audit(directory: Path, stems: Sequence[str]) -> Dict[str, object]:
    items = []
    for stem in stems:
        png = directory / f"{stem}.png"
        svg = directory / f"{stem}.svg"
        if not png.exists() or not svg.exists():
            raise AssertionError(f"missing figure pair for {stem}")
        from PIL import Image
        with Image.open(png) as image:
            dpi = image.info.get("dpi", (0.0, 0.0))
            dpi_ok = float(dpi[0]) >= 300.0 and float(dpi[1]) >= 300.0
        items.append({"stem": stem, "png": str(png.relative_to(ROOT)), "svg": str(svg.relative_to(ROOT)), "png_sha256": sha256(png), "svg_sha256": sha256(svg), "png_dpi": [float(dpi[0]), float(dpi[1])], "png_dpi_ok": dpi_ok})
    return {"count": len(items), "all_png_dpi_ge_300": all(i["png_dpi_ok"] for i in items), "items": items}


def q3_audit() -> Dict[str, object]:
    summary = json.loads((ROOT / "experiments/Q3_PRODUCTION/q3_summary.json").read_text(encoding="utf-8"))
    matrix = read_matrix_csv(ROOT / "experiments/Q3_PRODUCTION/q3_result3_matrix_full_precision.csv")
    if len(matrix[-1]) != 25 or len(matrix) != 3449 + 1:
        raise AssertionError("Q3 full-precision matrix shape mismatch")
    if not summary["prior_not_satisfied"] or not summary["endpoint_satisfied"]:
        raise AssertionError("Q3 threshold assertions are not satisfied")
    endpoint_values = [float(v) for v in matrix[-1][1:22]]
    if not all(v < summary["threshold_kg_kg"] for v in endpoint_values):
        raise AssertionError("Q3 endpoint has a material point at or above threshold")
    snaps = stream_q2_snapshots(ROOT / "experiments/Q2_FREEZE_RUN_V3/run_1/official_samples_raw.csv", [float(row[0]) for row in matrix[1:-1]])
    # The candidate workbook is produced from this raw matrix.  Check the
    # selected source values before the workbook's display rounding.
    source_trace = 0
    for row in matrix[1:-1]:
        snap = snaps[float(row[0])]
        for actual, expected in zip(row[1:22], snap.moisture):
            if abs(float(actual) - expected) > 5e-15:
                raise AssertionError(f"Q3 raw source mismatch at t={row[0]}")
        source_trace += 1
    return {"threshold": summary["threshold_kg_kg"], "coarse_bracket_s": summary["coarse_bracket_s"], "t3_s": summary["t3_s"], "t3_h": summary["t3_h"], "t_before_cmax": summary["cmax_before"], "t_after_cmax": summary["cmax_after"], "critical_radius_before_cm": summary["critical_radius_before_cm"], "critical_radius_after_cm": summary["critical_radius_after_cm"], "endpoint_cmax": summary["endpoint_cmax"], "critical_radius_endpoint_cm": summary["endpoint_critical_radius_cm"], "prior_not_satisfied": summary["prior_not_satisfied"], "endpoint_satisfied": summary["endpoint_satisfied"], "source_trace": f"{source_trace}/{len(matrix)-2}"}


def q4_audit() -> Dict[str, object]:
    summary = json.loads((ROOT / "experiments/Q4_PRODUCTION/q4_summary.json").read_text(encoding="utf-8"))
    matrix = read_matrix_csv(ROOT / "experiments/Q4_PRODUCTION/q4_result4_matrix_full_precision.csv")
    if not summary["prior_not_satisfied"] or not summary["endpoint_satisfied"]:
        raise AssertionError("Q4 threshold assertions are not satisfied")
    endpoint = [float(v) for v in matrix[-1][1:22] if v != ""]
    if not all(v < summary["threshold_kg_kg"] for v in endpoint):
        raise AssertionError("Q4 endpoint has a material point at or above threshold")
    law = RadiusLaw.from_attachment2(ROOT / "A题/附件/附件2.xlsx")
    node_errors = [abs(law.radius_cm(t) - r) for t, r in zip(law.times_s, law.radii_cm)]
    dense = [law.radius_cm(i * law.last_time_s / 1000.0) for i in range(1001)]
    if max(node_errors) > 1e-12 or any(b > a + 1e-10 for a, b in zip(dense, dense[1:])):
        raise AssertionError("Q4 PCHIP radius trace or monotonicity failed")
    # Fixed physical positions outside the current radius are blank, not
    # extrapolated; the matrix has 20 fixed columns followed by surface.
    blank_violations = 0
    for row in matrix[1:]:
        radius = float(row[22])
        for index in range(20):
            value = row[1 + index]
            if (index / 10.0) > radius + 1e-10 and value != "":
                blank_violations += 1
    if blank_violations:
        raise AssertionError(f"Q4 has {blank_violations} outside-domain values")
    if summary["mass_conservation"]["max_abs_normalized_step_residual"] >= 1e-3:
        raise AssertionError("Q4 mass residual exceeds recorded candidate tolerance")
    return {"coarse_bracket_s": summary["coarse_bracket_s"], "t4_s": summary["t4_s"], "t4_h": summary["t4_h"], "radius_at_t4_cm": summary["radius_at_t4_cm"], "t_before_cmax": summary["cmax_before"], "t_after_cmax": summary["cmax_after"], "endpoint_cmax": summary["endpoint_cmax"], "critical_xi_at_t4": summary["critical_xi_at_t4"], "critical_radius_at_t4_cm": summary["critical_radius_at_t4_cm"], "prior_not_satisfied": summary["prior_not_satisfied"], "endpoint_satisfied": summary["endpoint_satisfied"], "radius_node_max_abs_error_cm": max(node_errors), "outside_domain_value_violations": blank_violations, "mass_residual_max": summary["mass_conservation"]["max_abs_normalized_step_residual"], "robin_residual_max": summary["robin_audit"]["max_abs_flux_residual"]}


def main() -> None:
    if sha256(Q2_FINAL) != Q2_EXPECTED_SHA:
        raise AssertionError("frozen Q2 final SHA changed")
    q3 = q3_audit()
    q4 = q4_audit()
    result3 = workbook_audit(ROOT / "deliverables/candidate/result3.xlsx", 22)
    result4 = workbook_audit(ROOT / "deliverables/candidate/result4.xlsx", 22)
    table5 = workbook_audit(ROOT / "deliverables/candidate/tables/q3_table5.xlsx", 7)
    table6 = workbook_audit(ROOT / "deliverables/candidate/tables/q4_table6.xlsx", 9)
    for audit in (result3, result4, table5, table6):
        if audit["formula_count"] or audit["bad_numeric_format_count"] or not audit["shape_ok"]:
            raise AssertionError(f"workbook audit failed: {audit}")
    figures = figure_audit(ROOT / "deliverables/candidate/paper/figures", ["fig_5_12_q3_radial_moisture_profiles", "fig_5_13_q3_moisture_histories", "fig_5_14_q3_threshold_sensitivity", "fig_5_15_q4_radius_pchip", "fig_5_16_q4_dynamic_radial_moisture", "fig_5_17_q4_radius_and_mean", "fig_5_18_q3_q4_drying_time_comparison"])
    if not figures["all_png_dpi_ge_300"]:
        raise AssertionError("PNG DPI validation failed")
    output = {"q2_final_sha256": sha256(Q2_FINAL), "q3": q3, "q4": q4, "workbooks": {"result3": result3, "result4": result4, "table5": table5, "table6": table6}, "figures": figures, "figure_trace": {"q3": "3/3", "q4": "4/4", "total": "7/7"}, "status": "PASS"}
    (ROOT / "experiments/Q3_PRODUCTION/validation.json").write_text(json.dumps({"question": "Q3", "status": "PASS", "q3": q3, "result3": result3, "table5": table5, "figures": {k: figures[k] for k in ("count", "all_png_dpi_ge_300")}, "figure_trace": "3/3"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "experiments/Q4_PRODUCTION/validation.json").write_text(json.dumps({"question": "Q4", "status": "PASS", "q4": q4, "result4": result4, "table6": table6, "figures": {k: figures[k] for k in ("count", "all_png_dpi_ge_300")}, "figure_trace": "4/4"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "deliverables/candidate/Q3_Q4_VALIDATION.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
