"""Run the non-formal Q1 EXP-001 smoke test; no workbook is written."""

from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q1.config import Q1RunConfig
from src.q1.inputs import BoundaryProvider
from src.q1.solver import run_m1
from src.q1.validation import validate_m1_result


def main() -> int:
    root = ROOT
    config = Q1RunConfig(end_time_s=10.0, time_step_s=1.0, n_intervals=8)
    boundary = BoundaryProvider.from_attachment1(root / config.input_path)
    result = run_m1(config, boundary)
    checks = validate_m1_result(result)
    checks["boundary_raw_count"] = boundary.raw_count
    checks["official_source_untouched_by_design"] = True
    checks["formal_result_generated"] = False
    checks["status"] = "PASS" if checks["finite"] and checks["initial_ok"] and checks["time_ok"] else "FAIL"
    print(json.dumps(checks, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if checks["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
