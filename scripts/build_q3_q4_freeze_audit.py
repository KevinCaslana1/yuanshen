"""Assemble the read-only Q3/Q4 candidate freeze audit package.

The script consumes existing Q3/Q4 validation output and the Q2 Chinese
publication validation record.  It does not run a solver, write a workbook,
or copy a candidate workbook into final.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
Q2_VALIDATION = ROOT / "experiments/Q2_CHINESE_FIGURE_LOCALIZATION/validation.json"
Q34_VALIDATION = ROOT / "deliverables/candidate/Q3_Q4_VALIDATION.json"
OUTPUT = ROOT / "experiments/Q3_Q4_CANDIDATE/final_freeze_audit.json"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def main() -> int:
    q2 = json.loads(Q2_VALIDATION.read_text(encoding="utf-8"))
    q34 = json.loads(Q34_VALIDATION.read_text(encoding="utf-8"))
    if q2["status"] != "PASS" or q34["status"] != "PASS":
        raise RuntimeError("cannot assemble a passing freeze audit from a failed validation record")
    audit = {
        "schema_version": "Q3_Q4_FINAL_FREEZE_AUDIT_V1",
        "date": "2026-09-12",
        "status": "CANDIDATE_AUDIT_PASS_WAITING_FOR_HUMAN_APPROVAL",
        "q1": {
            "status": "FROZEN",
            "finding": "pointwise error zero-crossing / cancellation dip",
        },
        "q2": {
            "status": "FROZEN",
            "numeric_result_changed": False,
            "result2_sha256": q2["q2_frozen_integrity"]["sha256_current"],
            "chinese_publication_figures": {
                "status": q2["q2_chinese_figure_localization"]["status"],
                "figure_count": q2["q2_chinese_figure_localization"]["figure_count"],
                "png_count": q2["q2_chinese_figure_localization"]["png_count"],
                "svg_count": q2["q2_chinese_figure_localization"]["svg_count"],
                "png_dpi": q2["q2_chinese_figure_localization"]["all_png_dpi_ge_300"],
                "data_trace": q2["q2_chinese_figure_localization"]["data_trace"],
                "chinese_text_validation": q2["q2_chinese_figure_localization"]["chinese_text_validation"],
                "validation_record": rel(Q2_VALIDATION),
            },
        },
        "q3": q34["q3"],
        "q4": q34["q4"],
        "q3_q4_candidate_validation": {
            "status": q34["status"],
            "workbooks": q34["workbooks"],
            "figures": q34["figures"],
            "figure_trace": q34["figure_trace"],
            "validation_record": rel(Q34_VALIDATION),
        },
        "finalization": {
            "q3_q4_human_freeze_approval": "PENDING",
            "candidate_to_final_copy_performed": False,
            "remote_push": False,
            "q3_final_workbook": None,
            "q4_final_workbook": None,
        },
        "protected_paths": {
            "A题": "unchanged",
            "src/q1": "unchanged",
            "src/q2": "unchanged",
            "deliverables/final/result2.xlsx": "unchanged",
            "deliverables/final/figures/q2": "unchanged",
        },
        "historical_failure_retained": "experiments/Q2_FREEZE_RUN_V3_FAILED_HORIZON_20260912",
    }
    OUTPUT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "path": rel(OUTPUT)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
