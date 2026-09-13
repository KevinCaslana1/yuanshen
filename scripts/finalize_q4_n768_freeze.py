"""Finalize the validated Q4 n=768 candidate and record the freeze audit.

This script performs only the authorized post-validation copies and manifest
updates.  It does not run a solver or alter Q1, Q2, Q3, A题, or src/q2.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAND = ROOT / "deliverables" / "candidate_reaudit"
FINAL = ROOT / "deliverables" / "final"
RUN = ROOT / "experiments" / "Q4_PAPER_FINAL_N768"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def file_record(path: Path) -> dict[str, object]:
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def copy_bytes(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def main() -> None:
    validation = json.loads((CAND / "Q4_N768_VALIDATION.json").read_text(encoding="utf-8"))
    if validation.get("status") != "PASS":
        raise RuntimeError("Q4 candidate validation is not PASS")
    expected_q1 = "06b67b1f688d84a701ac4d2f4b0f47a1624069877df6724faf071a48af177b5c"
    expected_q2 = "84fb32457193e158debdf569d34f5f41b97e78496b30dd9b2e134385439e10da"
    expected_q3 = "08c67308b9b0e67cde2911dd4b701f12c4c024720ad257314bdf16a31d480461"
    protected = {"result1.xlsx": expected_q1, "result2.xlsx": expected_q2, "result3.xlsx": expected_q3}
    for name, expected in protected.items():
        actual = sha256(FINAL / name)
        if actual != expected:
            raise RuntimeError(f"protected workbook changed before Q4 finalization: {name} {actual}")

    q4_figures = [
        "fig_5_15_q4_radius_pchip",
        "fig_5_16_q4_dynamic_radial_moisture",
        "fig_5_17_q4_radius_and_mean",
    ]
    comparison = "fig_5_18_q3_q4_drying_time_comparison"
    old_paths = [FINAL / "result4.xlsx", FINAL / "paper" / "tables" / "table6_q4.csv", FINAL / "paper" / "tables" / "table6_q4.md", FINAL / "paper" / "tables" / "table6_q4.xlsx"]
    old_paths.extend(FINAL / "paper" / "figures" / "q4" / f"{stem}.{ext}" for stem in q4_figures for ext in ("png", "svg"))
    old_paths.extend(FINAL / "paper" / "figures" / "comparison" / f"{comparison}.{ext}" for ext in ("png", "svg"))
    superseded = {"status": "SUPERSEDED_BY_Q4_N768_FREEZE", "captured_before_copy": [file_record(path) for path in old_paths if path.exists()]}
    (RUN / "superseded_final_artifacts.json").write_text(json.dumps(superseded, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    copy_bytes(CAND / "result4.xlsx", FINAL / "result4.xlsx")
    for stem in q4_figures:
        for ext in ("png", "svg"):
            copy_bytes(CAND / "paper" / "figures" / "q4" / f"{stem}.{ext}", FINAL / "paper" / "figures" / "q4" / f"{stem}.{ext}")
    for ext in ("png", "svg"):
        copy_bytes(CAND / "paper" / "figures" / "comparison" / f"{comparison}.{ext}", FINAL / "paper" / "figures" / "comparison" / f"{comparison}.{ext}")
    for name in ("table6_q4.csv", "table6_q4.md", "table6_q4.xlsx"):
        copy_bytes(CAND / "paper" / "tables" / name, FINAL / "paper" / "tables" / name)
    copy_bytes(CAND / "paper" / "tables_word" / "表6_药材烘干过程的水分浓度_Q4.docx", FINAL / "paper" / "tables_word" / "表6_药材烘干过程的水分浓度_Q4.docx")
    copy_bytes(CAND / "paper" / "论文表1-表6_可直接复制.docx", FINAL / "paper" / "论文表1-表6_可直接复制.docx")
    copy_bytes(CAND / "paper" / "论文表1-表6_预览.pdf", FINAL / "paper" / "论文表1-表6_预览.pdf")
    for name in ("q4_summary.json", "q3_q4_comparison.json", "q4_results.md"):
        copy_bytes(CAND / "paper" / name, FINAL / "paper" / name)
    copy_bytes(CAND / "paper" / "TABLE_1_6_TRACE.json", FINAL / "paper" / "TABLE_1_6_TRACE.json")
    copy_bytes(CAND / "paper" / "Q4_N768_FIGURE_TRACE.json", FINAL / "paper" / "Q4_N768_FIGURE_TRACE.json")

    # Record the post-copy test result in the manifest.  The repository tests
    # are lightweight and do not start a numerical production run.
    test = subprocess.run([str(ROOT / ".venv" / "Scripts" / "python.exe"), "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True, check=False)
    test_text = (test.stdout + "\n" + test.stderr).strip()
    test_pass = test.returncode == 0 and "passed" in test_text
    if not test_pass:
        raise RuntimeError(f"pytest failed during Q4 finalization:\n{test_text}")

    final_result = file_record(FINAL / "result4.xlsx")
    paper_table_trace = json.loads((FINAL / "paper" / "TABLE_1_6_TRACE.json").read_text(encoding="utf-8"))
    figure_trace = json.loads((FINAL / "paper" / "Q4_N768_FIGURE_TRACE.json").read_text(encoding="utf-8"))
    l_metrics = json.loads((RUN / "metrics.json").read_text(encoding="utf-8"))
    k_metrics = json.loads((ROOT / "experiments/Q4_PAPER_FINAL_N640/metrics.json").read_text(encoding="utf-8"))
    i_metrics = json.loads((ROOT / "experiments/Q4_SPATIAL_CONVERGENCE_FINAL/spatial_run_I_n512_dt2.json").read_text(encoding="utf-8"))
    q3_summary = json.loads((ROOT / "experiments/Q3_PRODUCTION/q3_summary.json").read_text(encoding="utf-8"))
    convergence = {
        "I_n512_dt2_h": i_metrics["root_refinement"]["t_cross_linear_h"],
        "K_n640_dt2_h": k_metrics["event"]["t4_h"],
        "L_n768_dt2_h": l_metrics["event"]["t4_h"],
        "monotone_decreasing": i_metrics["root_refinement"]["t_cross_linear_s"] > k_metrics["event"]["t4_s"] > l_metrics["event"]["t4_s"],
        "differences_s": {"K_minus_I": k_metrics["event"]["t4_s"] - i_metrics["root_refinement"]["t_cross_linear_s"], "L_minus_K": l_metrics["event"]["t4_s"] - k_metrics["event"]["t4_s"]},
    }
    table6_trace = next(item for item in paper_table_trace["tables"] if item["table"] == "Table6")
    q4_manifest = {
        "schema_version": "Q4_FINAL_FREEZE_MANIFEST_V2",
        "status": "FROZEN",
        "freeze_approval_status": "APPROVED",
        "q4_version": "DEADLINE FAST-FINAL; direct paper production L",
        "solver_rerun_during_postprocess": False,
        "production": {"run": "L_n768_dt2", "n_intervals": 768, "dt_s": 2.0, "initial_state": "fresh t=0; no checkpoint or prior-grid state reuse", "horizon_s": 230400.0},
        "supporting_run": {"run": "K_n640_dt2", "n_intervals": 640, "dt_s": 2.0, "initial_state": "fresh t=0; no checkpoint or prior-grid state reuse"},
        "convergence": convergence,
        "event": l_metrics["event"],
        "workbook": {"candidate": file_record(CAND / "result4.xlsx"), "final": final_result, "byte_identical": sha256(CAND / "result4.xlsx") == sha256(FINAL / "result4.xlsx"), "validation": validation["workbook"]},
        "table5": {"status": "UNCHANGED", "trace": next(item["trace"] for item in paper_table_trace["tables"] if item["table"] == "Table5")},
        "table6": {"source": "experiments/Q4_PAPER_FINAL_N768/paper_samples.csv", "source_sha256": sha256(RUN / "paper_samples.csv"), "trace": table6_trace["trace"], "outputs": [file_record(FINAL / "paper" / "tables" / name) for name in ("table6_q4.csv", "table6_q4.md", "table6_q4.xlsx")]},
        "figures": {"run": "L_n768_dt2", "manifest": "deliverables/final/paper/Q4_N768_FIGURE_TRACE.json", "figure_groups": 4, "png": 4, "svg": 4, "png_ge_300_dpi": "4/4", "data_trace": "4/4", "chinese_text": "4/4", "files": [file_record(FINAL / "paper" / "figures" / "q4" / f"{stem}.{ext}") for stem in q4_figures for ext in ("png", "svg")] + [file_record(FINAL / "paper" / "figures" / "comparison" / f"{comparison}.{ext}") for ext in ("png", "svg")]},
        "merged_documents": {"word": file_record(FINAL / "paper" / "论文表1-表6_可直接复制.docx"), "pdf": file_record(FINAL / "paper" / "论文表1-表6_预览.pdf")},
        "q3_q4_comparison": {"path": "deliverables/final/paper/q3_q4_comparison.json", "q3_t3_h": q3_summary["t3_h"], "q4_t4_h": l_metrics["event"]["t4_h"]},
        "q1_q2_q3_protection": {"result1_sha256": sha256(FINAL / "result1.xlsx"), "result2_sha256": sha256(FINAL / "result2.xlsx"), "result3_sha256": sha256(FINAL / "result3.xlsx"), "q1_status": "FROZEN", "q2_status": "FROZEN", "q3_status": "FROZEN"},
        "historical_failed_experiment": "Q2_FREEZE_RUN_V3_FAILED_HORIZON_20260912 retained; not part of final Q4 delivery",
        "superseded_final_snapshot": "experiments/Q4_PAPER_FINAL_N768/superseded_final_artifacts.json",
        "pytest": {"status": "PASS", "summary": test_text.splitlines()[-1] if test_text.splitlines() else test_text},
        "table_trace": "deliverables/final/paper/TABLE_1_6_TRACE.json",
    }
    (FINAL / "Q4_MANIFEST.json").write_text(json.dumps(q4_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    freeze_record = {"record_type": "Q4_FINAL_FREEZE_RECORD", "status": "APPROVED", "manifest": "deliverables/final/Q4_MANIFEST.json", "candidate_validation": "deliverables/candidate_reaudit/Q4_N768_VALIDATION.json", "candidate_commit_base": "b3753824c43803bf46fc73670c40705e3d8a5e73", "q4": q4_manifest, "figure_trace": figure_trace, "created_by": "scripts/finalize_q4_n768_freeze.py"}
    (FINAL / "Q4_FREEZE_RECORD.json").write_text(json.dumps(freeze_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "FROZEN", "result4": final_result, "pytest": test_text.splitlines()[-1] if test_text.splitlines() else test_text}, ensure_ascii=False))


if __name__ == "__main__":
    main()
