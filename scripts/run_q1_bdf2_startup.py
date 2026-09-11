"""Compare standard BDF2 startup with early BE substepping for Q1.

The run is intentionally short (0--10 s). Early substeps are used through
1 s, followed by one normal-size BE restart step and then BDF2. Integer and
quarter-second comparison times are sampled from the internal history; no
official output rule or input is changed.
"""

from __future__ import annotations

import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Sequence

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q1.config import DEFAULT_PARAMETERS, Q1RunConfig
from src.q1.inputs import BoundaryProvider
from src.q1.solver import Q1Result, run_m1_bdf2


OUTPUT_DIR = ROOT / "experiments" / "EXP-Q1-BDF2-STARTUP"
TIMES_S = (0.25, 0.5, 1.0, 2.0, 5.0, 10.0)
RADIUS_M = DEFAULT_PARAMETERS.radius_m
POSITIONS_M = (RADIUS_M, RADIUS_M - 0.00025, RADIUS_M - 0.0005, 0.019)


def _config() -> Q1RunConfig:
    return Q1RunConfig(
        end_time_s=10.0,
        time_step_s=0.25,
        n_intervals=640,
        interpolation="linear",
        surface_boundary="robin",
    )


def _sample(result: Q1Result, time_s: float, position_m: float) -> float:
    time_matches = [index for index, value in enumerate(result.times_s) if abs(value - time_s) < 1.0e-10]
    if len(time_matches) != 1:
        raise ValueError(f"time is not uniquely represented: {time_s}")
    position_index = round(position_m / result.grid.dr_m)
    if abs(position_index * result.grid.dr_m - position_m) > 1.0e-12:
        raise ValueError(f"position is not aligned: {position_m}")
    return result.moistures_kg_kg[time_matches[0]][position_index]


def _compare(first: Q1Result, second: Q1Result) -> Dict[str, Any]:
    differences = [
        [abs(_sample(first, time_s, position) - _sample(second, time_s, position)) for position in POSITIONS_M]
        for time_s in TIMES_S
    ]
    values = [value for row in differences for value in row]
    max_index = values.index(max(values))
    time_index, position_index = divmod(max_index, len(POSITIONS_M))
    return {
        "times_s": list(TIMES_S),
        "positions_cm": [position * 100.0 for position in POSITIONS_M],
        "linf": max(values),
        "mean_abs": sum(values) / len(values),
        "rmse": math.sqrt(sum(value * value for value in values) / len(values)),
        "max_location": {"time_s": TIMES_S[time_index], "distance_cm": POSITIONS_M[position_index] * 100.0},
        "by_time": [
            {"time_s": time_s, "linf": max(row), "surface_abs": row[0]}
            for time_s, row in zip(TIMES_S, differences)
        ],
        "by_position": [
            {"distance_cm": position * 100.0, "linf": max(row[index] for row in differences)}
            for index, position in enumerate(POSITIONS_M)
        ],
    }


def _summary(result: Q1Result, runtime_seconds: float) -> Dict[str, Any]:
    return {
        "runtime_seconds": runtime_seconds,
        "history_length": len(result.times_s),
        "final_time_s": result.times_s[-1],
        "picard_max_iterations": max(result.picard_iterations[1:]),
        "surface_moisture_at_times": {str(time_s): _sample(result, time_s, RADIUS_M) for time_s in TIMES_S},
        "moisture_at_t1_positions": {
            str(position * 100.0): _sample(result, 1.0, position) for position in POSITIONS_M
        },
    }


def main() -> int:
    started = time.perf_counter()
    boundary = BoundaryProvider.from_attachment1(ROOT / "A题" / "附件" / "附件1.xlsx")
    config = _config()
    results: Dict[str, Q1Result] = {}
    runtimes: Dict[str, float] = {}

    cases = {"standard": None, "startup_dt0.25": 0.25, "startup_dt0.125": 0.125, "startup_dt0.0625": 0.0625}
    for label, startup_step_s in cases.items():
        case_started = time.perf_counter()
        results[label] = run_m1_bdf2(
            config,
            boundary,
            DEFAULT_PARAMETERS,
            startup_step_s=startup_step_s,
            startup_duration_s=1.0,
        )
        runtimes[label] = time.perf_counter() - case_started

    reference_started = time.perf_counter()
    reference_config = Q1RunConfig(
        end_time_s=10.0,
        time_step_s=0.015625,
        n_intervals=1280,
        interpolation="linear",
        surface_boundary="robin",
    )
    reference = run_m1_bdf2(reference_config, boundary, DEFAULT_PARAMETERS)
    reference_runtime = time.perf_counter() - reference_started

    comparisons = {
        f"standard_vs_{label}": _compare(results["standard"], results[label])
        for label in cases
        if label != "standard"
    }
    reference_comparisons = {
        label: _compare(result, reference)
        for label, result in results.items()
    }
    payload: Dict[str, Any] = {
        "experiment_id": "EXP-Q1-BDF2-STARTUP",
        "status": "COMPLETED",
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "input_hashes": {"A题/附件/附件1.xlsx": "7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7"},
        "scope": {
            "end_time_s": 10.0,
            "normal_time_step_s": 0.25,
            "n_intervals": 640,
            "startup_duration_s": 1.0,
            "comparison_times_s": list(TIMES_S),
            "comparison_positions_cm": [position * 100.0 for position in POSITIONS_M],
            "standard_definition": "BE at first normal step, then fixed-step BDF2",
            "early_definition": "BE substeps through 1 s, one normal-size BE restart step, then fixed-step BDF2",
        },
        "cases": {label: _summary(result, runtimes[label]) for label, result in results.items()},
        "reference": {
            "definition": "independent short standard-BDF2 reference, N=1280, dt=0.015625 s",
            "runtime_seconds": reference_runtime,
            "history_length": len(reference.times_s),
            "surface_moisture_at_times": {str(time_s): _sample(reference, time_s, RADIUS_M) for time_s in TIMES_S},
        },
        "standard_vs_early_comparisons": comparisons,
        "comparison_to_short_reference": reference_comparisons,
        "runtime_seconds": time.perf_counter() - started,
        "candidate_workbook_generated": False,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "config.json").write_text(json.dumps({
        "experiment_id": payload["experiment_id"],
        "code_commit": payload["code_commit"],
        "input_hashes": payload["input_hashes"],
        "scope": payload["scope"],
        "reference": payload["reference"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "notes.md").write_text(
        "# EXP-Q1-BDF2-STARTUP\n\n"
        "Short startup comparison only. The early candidate refines BE through 1 s, "
        "restarts with one normal BE step, and then uses BDF2. No official output "
        "time rule, initial condition, boundary input, or workbook was changed.\n\n"
        f"Status: `{payload['status']}`\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "experiment_id": payload["experiment_id"],
        "status": payload["status"],
        "standard_vs_early_comparisons": {
            label: {"linf": value["linf"], "max_location": value["max_location"]}
            for label, value in comparisons.items()
        },
        "reference_surface_at_t1": payload["reference"]["surface_moisture_at_times"]["1.0"],
        "runtime_seconds": payload["runtime_seconds"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
