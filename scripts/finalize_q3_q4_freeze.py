"""Finalize already-validated Q3/Q4 candidate deliverables by byte copy.

The script performs no Q3/Q4 numerical solve.  It consumes the existing
candidate workbooks, tables, figures and validation records, copies them into
the final paper/deliverable directories, and writes freeze manifests.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image
from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[1]
Q2_SHA = "84fb32457193e158debdf569d34f5f41b97e78496b30dd9b2e134385439e10da"
Q3_VALIDATION = ROOT / "experiments/Q3_PRODUCTION/validation.json"
Q4_VALIDATION = ROOT / "experiments/Q4_PRODUCTION/validation.json"
Q34_VALIDATION = ROOT / "deliverables/candidate/Q3_Q4_VALIDATION.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def exact_copy(source: Path, destination: Path) -> dict[str, object]:
    if destination.exists():
        if sha256(source) != sha256(destination) or source.stat().st_size != destination.stat().st_size:
            raise RuntimeError(f"refusing to overwrite mismatched existing final asset: {destination}")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    source_sha = sha256(source)
    destination_sha = sha256(destination)
    if source_sha != destination_sha or source.stat().st_size != destination.stat().st_size:
        raise RuntimeError(f"byte-copy verification failed: {source} -> {destination}")
    return {
        "candidate_path": rel(source),
        "final_path": rel(destination),
        "candidate_sha256": source_sha,
        "final_sha256": destination_sha,
        "candidate_size_bytes": source.stat().st_size,
        "final_size_bytes": destination.stat().st_size,
        "byte_identical": True,
    }


def table_trace(source_csv: Path, final_xlsx: Path) -> dict[str, object]:
    with source_csv.open(encoding="utf-8", newline="") as handle:
        expected = list(csv.reader(handle))
    workbook = load_workbook(final_xlsx, read_only=True, data_only=True)
    sheet = workbook.active
    actual = [list(row) for row in sheet.iter_rows(values_only=True)]
    workbook.close()
    if len(expected) != len(actual) or len(expected[0]) != len(actual[0]):
        raise RuntimeError(f"table shape mismatch: {source_csv} / {final_xlsx}")
    passed = 0
    total = 0
    for expected_row, actual_row in zip(expected, actual):
        for expected_value, actual_value in zip(expected_row, actual_row):
            total += 1
            if expected_value == "":
                ok = actual_value is None
            else:
                try:
                    ok = abs(float(expected_value) - float(actual_value)) <= 5e-12
                except (TypeError, ValueError):
                    ok = expected_value == actual_value
            if ok:
                passed += 1
    return {
        "status": "PASS" if passed == total else "FAIL",
        "cells": f"{passed}/{total}",
        "source_csv_sha256": sha256(source_csv),
        "final_xlsx_sha256": sha256(final_xlsx),
    }


def figure_copy(source_dir: Path, final_dir: Path, stems: list[str], trace: str) -> list[dict[str, object]]:
    records = []
    for stem in stems:
        pair = {}
        for suffix in ("png", "svg"):
            source = source_dir / f"{stem}.{suffix}"
            destination = final_dir / f"{stem}.{suffix}"
            copied = exact_copy(source, destination)
            pair[suffix] = copied
        with Image.open(final_dir / f"{stem}.png") as image:
            dpi = tuple(float(value) for value in image.info.get("dpi", (0.0, 0.0)))
        if dpi[0] < 300.0 or dpi[1] < 300.0:
            raise RuntimeError(f"PNG DPI below 300: {final_dir / f'{stem}.png'}")
        records.append({"stem": stem, "png": pair["png"], "svg": pair["svg"], "png_dpi": dpi, "trace": trace})
    return records


def workbook_record(copy_record: dict[str, object], validation: dict[str, object]) -> dict[str, object]:
    return {
        **copy_record,
        "dimensions": validation["sheets"],
        "formula_count": validation["formula_count"],
        "bad_numeric_format_count": validation["bad_numeric_format_count"],
        "nonfinite_numeric_count": validation["nonfinite_numeric_count"],
        "time_lattice": validation.get("time_lattice"),
    }


def main() -> None:
    q3_validation = json.loads(Q3_VALIDATION.read_text(encoding="utf-8"))
    q4_validation = json.loads(Q4_VALIDATION.read_text(encoding="utf-8"))
    q34_validation = json.loads(Q34_VALIDATION.read_text(encoding="utf-8"))
    q2_final = ROOT / "deliverables/final/result2.xlsx"
    if sha256(q2_final) != Q2_SHA:
        raise RuntimeError("Q2 frozen result2.xlsx SHA changed")
    if q34_validation.get("status") != "PASS":
        raise RuntimeError("Q3/Q4 candidate validation is not PASS")
    if q3_validation["result3"]["time_lattice"]["status"] != "PASS":
        raise RuntimeError("Q3 workbook is not on the official 60 s lattice")
    if q4_validation["result4"]["time_lattice"]["status"] != "PASS":
        raise RuntimeError("Q4 workbook is not on the official 60 s lattice")

    result3_copy = exact_copy(ROOT / "deliverables/candidate/result3.xlsx", ROOT / "deliverables/final/result3.xlsx")
    result4_copy = exact_copy(ROOT / "deliverables/candidate/result4.xlsx", ROOT / "deliverables/final/result4.xlsx")

    final_tables = ROOT / "deliverables/final/paper/tables"
    table_copies = {
        "table5": {
            "csv": exact_copy(ROOT / "deliverables/candidate/paper/tables/table5_q3.csv", final_tables / "table5_q3.csv"),
            "md": exact_copy(ROOT / "deliverables/candidate/paper/tables/table5_q3.md", final_tables / "table5_q3.md"),
            "xlsx": exact_copy(ROOT / "deliverables/candidate/paper/tables/table5_q3.xlsx", final_tables / "table5_q3.xlsx"),
        },
        "table6": {
            "csv": exact_copy(ROOT / "deliverables/candidate/paper/tables/table6_q4.csv", final_tables / "table6_q4.csv"),
            "md": exact_copy(ROOT / "deliverables/candidate/paper/tables/table6_q4.md", final_tables / "table6_q4.md"),
            "xlsx": exact_copy(ROOT / "deliverables/candidate/paper/tables/table6_q4.xlsx", final_tables / "table6_q4.xlsx"),
        },
    }
    table5_trace = table_trace(ROOT / "experiments/Q3_PRODUCTION/table5.csv", final_tables / "table5_q3.xlsx")
    table6_trace = table_trace(ROOT / "experiments/Q4_PRODUCTION/table6.csv", final_tables / "table6_q4.xlsx")
    if table5_trace["status"] != "PASS" or table6_trace["status"] != "PASS":
        raise RuntimeError(f"table trace failed: {table5_trace} / {table6_trace}")

    source_figures = ROOT / "deliverables/candidate/paper/figures"
    q3_stems = ["fig_5_12_q3_radial_moisture_profiles", "fig_5_13_q3_moisture_histories", "fig_5_14_q3_threshold_sensitivity"]
    q4_stems = ["fig_5_15_q4_radius_pchip", "fig_5_16_q4_dynamic_radial_moisture", "fig_5_17_q4_radius_and_mean"]
    comparison_stems = ["fig_5_18_q3_q4_drying_time_comparison"]
    q3_figures = figure_copy(source_figures, ROOT / "deliverables/final/paper/figures/q3", q3_stems, "3/3")
    q4_figures = figure_copy(source_figures, ROOT / "deliverables/final/paper/figures/q4", q4_stems, "4/4")
    comparison_figures = figure_copy(source_figures, ROOT / "deliverables/final/paper/figures/comparison", comparison_stems, "1/1")

    paper_root = ROOT / "deliverables/final/paper"
    supporting_files = []
    for name in ("q3_summary.json", "q4_summary.json", "q3_q4_comparison.json", "q3_results.md", "q4_results.md"):
        supporting_files.append(exact_copy(ROOT / "deliverables/candidate/paper" / name, paper_root / name))

    q3_summary = json.loads((ROOT / "experiments/Q3_PRODUCTION/q3_summary.json").read_text(encoding="utf-8"))
    q4_summary = json.loads((ROOT / "experiments/Q4_PRODUCTION/q4_summary.json").read_text(encoding="utf-8"))
    q3_event_bracket = q3_summary["endpoint_refinement"]["bracket_s"]
    q3_uncertainty = q3_event_bracket[1] - q3_event_bracket[0]
    q4_uncertainty = (q4_summary["coarse_bracket_s"][1] - q4_summary["coarse_bracket_s"][0]) / 64.0

    q3_manifest = {
        "schema_version": "Q3_FINAL_FREEZE_MANIFEST_V1",
        "status": "FROZEN",
        "freeze_approval_status": "APPROVED",
        "solver_rerun_during_freeze": False,
        "q2_final_sha256": Q2_SHA,
        "threshold_kg_kg": q3_summary["threshold_kg_kg"],
        "drying_time_s": q3_summary["t3_s"],
        "drying_time_h": q3_summary["t3_h"],
        "event_bracket_s": q3_summary["coarse_bracket_s"],
        "event_refinement_bracket_s": q3_event_bracket,
        "event_time_uncertainty_s": q3_uncertainty,
        "event_time_uncertainty_method": "width of final local BE/Picard bracket",
        "t_before_max_c": q3_summary["cmax_before"],
        "t_after_max_c": q3_summary["cmax_after"],
        "threshold_proof": "PASS",
        "argmax_radius_before_cm": q3_summary["critical_radius_before_cm"],
        "argmax_radius_after_cm": q3_summary["critical_radius_after_cm"],
        "source": {"q2_raw_path": q3_summary["source_q2_raw"], "q2_raw_sha256": q3_summary["source_q2_raw_sha256"]},
        "workbook": workbook_record(result3_copy, q3_validation["result3"]),
        "table5": {"source_csv": rel(ROOT / "experiments/Q3_PRODUCTION/table5.csv"), "trace": table5_trace, "outputs": table_copies["table5"]},
        "figures": {"count": len(q3_figures), "trace": "3/3", "items": q3_figures},
        "paper_assets_manifest": "deliverables/final/paper/PAPER_ASSET_MANIFEST.json",
    }

    q4_manifest = {
        "schema_version": "Q4_FINAL_FREEZE_MANIFEST_V1",
        "status": "FROZEN",
        "freeze_approval_status": "APPROVED",
        "solver_rerun_during_freeze": False,
        "q2_final_sha256": Q2_SHA,
        "threshold_kg_kg": q4_summary["threshold_kg_kg"],
        "drying_time_s": q4_summary["t4_s"],
        "drying_time_h": q4_summary["t4_h"],
        "event_bracket_s": q4_summary["coarse_bracket_s"],
        "event_time_uncertainty_s": q4_uncertainty,
        "event_time_uncertainty_method": "coarse event bracket width divided by 64 local BE/Picard refinement substeps",
        "t_before_max_c": q4_summary["cmax_before"],
        "t_after_max_c": q4_summary["cmax_after"],
        "threshold_proof": "PASS",
        "argmax_position": {"xi": q4_summary["critical_xi_at_t4"], "radius_cm": q4_summary["critical_radius_at_t4_cm"]},
        "radius_at_t4_cm": q4_summary["radius_at_t4_cm"],
        "radius_source": q4_summary["radius_source"],
        "radius_source_sha256": q4_summary["radius_source_sha256"],
        "radius_interpolation_method": q4_summary["radius_interpolation"],
        "radius_node_max_abs_error_cm": q4_validation["q4"]["radius_node_max_abs_error_cm"],
        "moving_domain_policy": "fixed physical positions with r > R(t) are blank/unavailable; no extrapolation, zero-fill, surface-copy, or nearest-neighbor fill",
        "surface_extraction_policy": "separate model surface value C(R(t),t), not the nearest fixed grid point",
        "outside_domain_value_violations": q4_validation["q4"]["outside_domain_value_violations"],
        "source": {"q4_matrix": rel(ROOT / "experiments/Q4_PRODUCTION/q4_result4_matrix_full_precision.csv"), "q4_matrix_sha256": sha256(ROOT / "experiments/Q4_PRODUCTION/q4_result4_matrix_full_precision.csv")},
        "workbook": workbook_record(result4_copy, q4_validation["result4"]),
        "table6": {"source_csv": rel(ROOT / "experiments/Q4_PRODUCTION/table6.csv"), "trace": table6_trace, "outputs": table_copies["table6"]},
        "figures": {"count": len(q4_figures), "trace": "4/4", "items": q4_figures},
        "paper_assets_manifest": "deliverables/final/paper/PAPER_ASSET_MANIFEST.json",
    }

    asset_records = []
    for label, source, outputs, trace in (
        ("Table5", ROOT / "experiments/Q3_PRODUCTION/table5.csv", table_copies["table5"], table5_trace),
        ("Table6", ROOT / "experiments/Q4_PRODUCTION/table6.csv", table_copies["table6"], table6_trace),
    ):
        asset_records.append({"asset": label, "source": rel(source), "source_sha256": sha256(source), "generator": "existing canonical postprocess artifact; not rerun during freeze", "output": [entry["final_path"] for entry in outputs.values()], "trace_result": trace})
    for label, figures in (("Q3 figures", q3_figures), ("Q4 figures", q4_figures), ("Comparison figures", comparison_figures)):
        for item in figures:
            asset_records.append({"asset": f"{label}: {item['stem']}", "source": item["png"]["candidate_path"], "source_sha256": item["png"]["candidate_sha256"], "generator": "existing validated candidate figure; not redrawn during freeze", "output": [item["png"]["final_path"], item["svg"]["final_path"]], "trace_result": item["trace"]})
    paper_manifest = {
        "schema_version": "Q3_Q4_PAPER_ASSET_MANIFEST_V1",
        "status": "PASS",
        "freeze_approval_status": "APPROVED",
        "solver_rerun": False,
        "asset_count": len(asset_records),
        "tables_count": 2,
        "figure_groups_count": 7,
        "assets": asset_records,
        "supporting_files": supporting_files,
    }

    final_dir = ROOT / "deliverables/final"
    (final_dir / "Q3_MANIFEST.json").write_text(json.dumps(q3_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (final_dir / "Q4_MANIFEST.json").write_text(json.dumps(q4_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (paper_root / "PAPER_ASSET_MANIFEST.json").write_text(json.dumps(paper_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    audit = {
        "schema_version": "Q3_Q4_FINAL_FREEZE_AUDIT_V2",
        "status": "FINAL_FREEZE_COMPLETE",
        "freeze_approval_status": "APPROVED",
        "solver_rerun": False,
        "q1": {"status": "FROZEN", "finding": "pointwise error zero-crossing / cancellation dip"},
        "q2": {"status": "FROZEN", "result2_sha256": Q2_SHA},
        "q3": q3_manifest,
        "q4": q4_manifest,
        "paper_assets": paper_manifest,
        "historical_failure_retained": "experiments/Q2_FREEZE_RUN_V3_FAILED_HORIZON_20260912",
        "remote_push": False,
    }
    (ROOT / "experiments/Q3_Q4_CANDIDATE/final_freeze_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "q3_sha256": q3_manifest["workbook"]["final_sha256"], "q4_sha256": q4_manifest["workbook"]["final_sha256"], "paper_asset_count": paper_manifest["asset_count"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
