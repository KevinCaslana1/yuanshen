"""Measure whether nonlinear Picard tolerance contaminates Q1 discretization error."""

from __future__ import annotations

import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q1.config import DEFAULT_PARAMETERS, Q1RunConfig
from src.q1.inputs import BoundaryProvider
from src.q1.solver import Q1Result, run_m1


OUTPUT_DIR = ROOT / "experiments" / "EXP-Q1-PICARD-SENS"
TIMES_S = tuple(range(1, 301))
POSITIONS_M = tuple(index * 0.001 for index in range(21))


def _run(tolerance: float) -> Q1Result:
    config = Q1RunConfig(
        end_time_s=300.0,
        time_step_s=0.25,
        n_intervals=160,
        interpolation="linear",
        surface_boundary="robin",
        picard_tolerance=tolerance,
        picard_max_iterations=50,
    )
    boundary = BoundaryProvider.from_attachment1(ROOT / config.input_path)
    return run_m1(config, boundary, DEFAULT_PARAMETERS)


def _rows(result: Q1Result, field: str) -> List[List[float]]:
    time_indices = tuple(round(time_s / result.config.time_step_s) for time_s in TIMES_S)
    space_indices = tuple(round(position / result.grid.dr_m) for position in POSITIONS_M)
    if field == "temperature_c":
        return [[result.temperatures_k[t][r] - 273.15 for r in space_indices] for t in time_indices]
    return [[result.moistures_kg_kg[t][r] for r in space_indices] for t in time_indices]


def _comparison(first: Q1Result, second: Q1Result) -> Dict[str, Any]:
    fields: Dict[str, Any] = {}
    for field in ("temperature_c", "moisture_kg_kg"):
        first_rows, second_rows = _rows(first, field), _rows(second, field)
        differences = [abs(left - right) for a, b in zip(first_rows, second_rows) for left, right in zip(a, b)]
        index = differences.index(max(differences))
        time_index, position_index = divmod(index, len(POSITIONS_M))
        fields[field] = {
            "linf": max(differences),
            "mean_abs": sum(differences) / len(differences),
            "rmse": math.sqrt(sum(value * value for value in differences) / len(differences)),
            "max_location": {"time_s": TIMES_S[time_index], "distance_cm": POSITIONS_M[position_index] * 100.0},
            "cell_count": len(differences),
        }
    return fields


def _case_summary(result: Q1Result) -> Dict[str, Any]:
    iterations = result.picard_iterations[1:]
    return {
        "picard_tolerance": result.config.picard_tolerance,
        "max_iterations": max(iterations),
        "mean_iterations": sum(iterations) / len(iterations),
        "min_iterations": min(iterations),
        "end_time_s": result.times_s[-1],
        "n_intervals": result.grid.n_intervals,
        "time_step_s": result.config.time_step_s,
    }


def main() -> int:
    started = time.perf_counter()
    results = {str(tolerance): _run(tolerance) for tolerance in (1.0e-6, 1.0e-8, 1.0e-10)}
    payload: Dict[str, Any] = {
        "experiment_id": "EXP-Q1-PICARD-SENS",
        "status": "COMPLETED",
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "input_hashes": {"A题/附件/附件1.xlsx": "7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7"},
        "scope": {
            "end_time_s": 300.0,
            "n_intervals": 160,
            "time_step_s": 0.25,
            "output_times_s": "1..300",
            "output_positions_cm": "0.0..2.0 step 0.1",
            "cells_per_field": len(TIMES_S) * len(POSITIONS_M),
        },
        "cases": {key: _case_summary(result) for key, result in results.items()},
        "comparisons": {
            "tol1e-6_vs_tol1e-8": _comparison(results["1e-06"], results["1e-08"]),
            "tol1e-8_vs_tol1e-10": _comparison(results["1e-08"], results["1e-10"]),
        },
        "reference_discretization_differences": {
            "space_N160_vs_N320_full_grid_linf": {"temperature_c": 2.2996181030521257e-05, "moisture_kg_kg": 0.005651324501566801},
            "time_dt0.5_vs_dt0.25_full_grid_linf": {"temperature_c": 0.0004776183058083916, "moisture_kg_kg": 0.0011657392001822586},
        },
        "runtime_seconds": time.perf_counter() - started,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "config.json").write_text(
        json.dumps(
            {
                "experiment_id": payload["experiment_id"],
                "code_commit": payload["code_commit"],
                "input_hashes": payload["input_hashes"],
                "scope": payload["scope"],
                "cases": payload["cases"],
                "reference_discretization_differences": payload["reference_discretization_differences"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "notes.md").write_text(
        "# EXP-Q1-PICARD-SENS\n\n"
        "Short-window tolerance sensitivity at N=160 and dt=0.25 s. No workbook was generated.\n\n"
        "The 1e-8 versus 1e-10 difference is compared with the previously measured spatial and temporal differences.\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("Evidence written to experiments/EXP-Q1-PICARD-SENS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
