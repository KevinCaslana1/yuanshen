"""Run short-horizon validation for the authorized Q2 V2 numerical candidate."""

from __future__ import annotations

import gc
import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_q2_accuracy_remediation import compare_snapshot_maps, load_base_config, run_short_case


OUT = ROOT / "experiments" / "EXP-Q2-V2-SHORT"
TIMES = (0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 60.0, 300.0, 1800.0)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=False)
    base = load_base_config()
    cases = {}
    for dt in (0.25, 0.125, 0.0625):
        config = replace(
            base,
            end_time_s=1800.0,
            time_step_s=dt,
            n_intervals=640,
            reset_bdf2_at_environment_transition=True,
            early_time_step_s=0.015625,
            early_time_end_s=2.0,
        )
        cases[f"dt{dt:g}"] = run_short_case(f"dt{dt:g}_n640_early2s", config, OUT, TIMES, full_diagnostics=False)
        gc.collect()
    names = tuple(cases)
    comparisons = {
        f"{left}_vs_{right}": compare_snapshot_maps(cases[left]["snapshots"], cases[right]["snapshots"])
        for left, right in zip(names, names[1:])
    }
    metrics = {
        "experiment": "EXP-Q2-V2-SHORT",
        "candidate": cases["dt0.25"]["summary"]["config"],
        "reference_configs": {name: cases[name]["summary"]["config"] for name in names[1:]},
        "time_points_s": list(TIMES),
        "raw_pairwise_differences": comparisons,
        "short_regression_horizons_s": [60.0, 1800.0],
        "all_runs_complete": all(cases[name]["summary"]["complete"] for name in names),
        "production_accuracy_gate": {"temperature_C": 2.5e-5, "moisture_kg_kg": 2.5e-5, "status": "NOT_YET_FORMAL"},
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "notes.md").write_text(
        "# EXP-Q2-V2-SHORT\n\n"
        "Candidate V2 uses n=640, dt=0.25 s after a 0.015625 s early-time phase through 2 s, "
        "a BE restart at the step-size change, and the authorized BE restart at 14400 s. "
        "The dt=.125/.0625 runs use the same early-time policy and are short numerical references.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "COMPLETE", "output": str(OUT.relative_to(ROOT)).replace("\\", "/")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
