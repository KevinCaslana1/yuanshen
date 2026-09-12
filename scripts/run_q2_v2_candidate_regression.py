"""Run short and transition regression for the numerical Q2 V2 candidate.

This runner uses only the approved numerical changes: early-time refinement,
BE restart at a step-size change, BE restart at the frozen 14400 s environment
transition, and stronger surface clustering.  It does not generate result2.
"""

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


OUT = ROOT / "experiments" / "EXP-Q2-V2-REGRESSION"
LOCAL_TIMES = tuple(14390.0 + 0.25 * index for index in range(441))
TIMES = tuple(sorted(set((0.0, 60.0, 1800.0, 10800.0) + LOCAL_TIMES)))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=False)
    base = load_base_config()
    cases = {}
    for dt in (0.25, 0.125):
        config = replace(
            base,
            end_time_s=14500.0,
            time_step_s=dt,
            n_intervals=320,
            cluster_power=3.0,
            reset_bdf2_at_environment_transition=True,
            early_time_step_s=0.015625,
            early_time_end_s=2.0,
        )
        name = f"dt{dt:g}_n320_cluster3_early2s"
        print(f"[Q2 V2 regression] starting {name} to 14500 s", flush=True)
        cases[name] = run_short_case(name, config, OUT, TIMES, full_diagnostics=False)
        gc.collect()
        print(f"[Q2 V2 regression] completed {name}", flush=True)

    names = tuple(cases)
    comparison = compare_snapshot_maps(cases[names[0]]["snapshots"], cases[names[1]]["snapshots"])
    local_keys = {
        key: value for key, value in cases[names[0]]["snapshots"].items()
        if 14390.0 - 1e-12 <= float(value["time_s"]) <= 14500.0 + 1e-12
    }
    local_reference = {
        key: value for key, value in cases[names[1]]["snapshots"].items()
        if 14390.0 - 1e-12 <= float(value["time_s"]) <= 14500.0 + 1e-12
    }
    metrics = {
        "experiment": "EXP-Q2-V2-REGRESSION",
        "status": "SHORT_AND_TRANSITION_REGRESSION",
        "candidate": cases[names[0]]["summary"]["config"],
        "reference": cases[names[1]]["summary"]["config"],
        "time_points_s": list(TIMES),
        "transition_window_s": [14390.0, 14500.0],
        "raw_pairwise_difference_all_recorded_points": comparison,
        "raw_pairwise_difference_transition_window": compare_snapshot_maps(local_keys, local_reference),
        "conservative_fine_coarse_bound": {
            "temperature_C": comparison["temperature_Linf_C"],
            "moisture_kg_kg": comparison["moisture_Linf_kg_kg"],
            "not_richardson_uncertainty": True,
        },
        "gate": {"temperature_C": 2.5e-5, "moisture_kg_kg": 2.5e-5},
        "all_runs_complete": all(cases[name]["summary"]["complete"] for name in names),
        "official_result2_generated": False,
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "notes.md").write_text(
        "# EXP-Q2-V2-REGRESSION\n\n"
        "The candidate and one finer temporal reference use n=320, cluster_power=3, "
        "the frozen ENV-B convention, harmonic interfaces, early dt=.015625 s through "
        "2 s, and a BE restart at both step-size and environment transitions. The run "
        "covers 0–3 h and the 14390–14500 s transition window. The fine/coarse values "
        "are raw differences and are not labelled Richardson uncertainty.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "COMPLETE", "output": str(OUT.relative_to(ROOT)).replace("\\", "/")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
