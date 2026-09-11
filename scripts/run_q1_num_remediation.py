"""Evaluate the isolated BDF2 numerical-method candidate for Q1.

M1 with Backward Euler remains the reference. This experiment changes only
the time integrator to BDF2 after a BE startup step and writes evidence; it
does not generate result1.xlsx.
"""

from __future__ import annotations

import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_q1_num_diag import (
    FULL_POSITIONS_M,
    FULL_TIMES_S,
    PAPER_POSITIONS_M,
    PAPER_TIMES_S,
    _comparison,
    _field_rows,
)
from src.q1.config import DEFAULT_PARAMETERS, Q1RunConfig
from src.q1.inputs import BoundaryProvider
from src.q1.solver import Q1Result, run_m1, run_m1_bdf2


OUTPUT_DIR = ROOT / "experiments" / "EXP-Q1-NUM-REMEDIATION"


def _config(time_step_s: float) -> Q1RunConfig:
    return Q1RunConfig(
        end_time_s=1800.0,
        time_step_s=time_step_s,
        n_intervals=320,
        interpolation="linear",
        surface_boundary="robin",
    )


def _run(method: str, time_step_s: float) -> tuple[Q1Result, float]:
    config = _config(time_step_s)
    boundary = BoundaryProvider.from_attachment1(ROOT / config.input_path)
    started = time.perf_counter()
    if method == "BE":
        result = run_m1(config, boundary, DEFAULT_PARAMETERS)
    elif method == "BDF2":
        result = run_m1_bdf2(config, boundary, DEFAULT_PARAMETERS)
    else:
        raise ValueError(method)
    return result, time.perf_counter() - started


def _orders(comparison_coarse: Dict[str, Any], comparison_fine: Dict[str, Any]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {}
    for field in ("temperature_c", "moisture_kg_kg"):
        summary[field] = {}
        for region in ("full_grid", "center", "surface", "paper_table_points"):
            summary[field][region] = {}
            for norm in ("linf", "mean_abs", "rmse"):
                coarse = comparison_coarse["fields"][field][region]["raw"][norm]
                fine = comparison_fine["fields"][field][region]["raw"][norm]
                order = math.log(coarse / fine, 2.0) if coarse > 0.0 and fine > 0.0 else None
                remaining = fine / (2.0**order - 1.0) if order is not None and order > 0.0 else None
                summary[field][region][norm] = {
                    "coarse_error": coarse,
                    "fine_error": fine,
                    "observed_order": order,
                    "richardson_remaining_error": remaining,
                }
    return summary


def _run_summary(result: Q1Result, runtime_seconds: float) -> Dict[str, Any]:
    temperatures = [value - 273.15 for row in result.temperatures_k for value in row]
    moistures = [value for row in result.moistures_kg_kg for value in row]
    iterations = result.picard_iterations[1:]
    return {
        "time_step_s": result.config.time_step_s,
        "n_intervals": result.grid.n_intervals,
        "runtime_seconds": runtime_seconds,
        "picard_max_iterations": max(iterations),
        "picard_mean_iterations": sum(iterations) / len(iterations),
        "temperature_range_c": [min(temperatures), max(temperatures)],
        "moisture_range_kg_kg": [min(moistures), max(moistures)],
        "history_length": len(result.times_s),
        "final_time_s": result.times_s[-1],
    }


def _rounding_safety(
    result: Q1Result,
    field: str,
    region: str,
    estimated_remaining_error: float | None,
) -> Dict[str, Any]:
    regions = {
        "full_grid": (FULL_TIMES_S, FULL_POSITIONS_M),
        "center": (FULL_TIMES_S, (0.0,)),
        "surface": (FULL_TIMES_S, (0.02,)),
        "paper_table_points": (PAPER_TIMES_S, PAPER_POSITIONS_M),
    }
    times_s, positions_m = regions[region]
    rows = _field_rows(result, field, times_s, positions_m)
    threshold_distance: list[float] = []
    locations: list[dict[str, Any]] = []
    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):
            scaled = value * 10000.0
            fractional_part = scaled - math.floor(scaled)
            distance = abs(fractional_part - 0.5) / 10000.0
            threshold_distance.append(distance)
            locations.append(
                {
                    "time_s": times_s[row_index],
                    "distance_cm": positions_m[column_index] * 100.0,
                    "distance_to_threshold": distance,
                }
            )
    min_index = threshold_distance.index(min(threshold_distance))
    estimated = estimated_remaining_error if estimated_remaining_error is not None else float("nan")
    unsafe = [distance <= estimated for distance in threshold_distance] if math.isfinite(estimated) else []
    min_margin = min(distance - estimated for distance in threshold_distance) if math.isfinite(estimated) else None
    return {
        "estimated_remaining_error": estimated_remaining_error,
        "rounding_half_unit": 0.5e-4,
        "min_distance_to_rounding_threshold": min(threshold_distance),
        "mean_distance_to_rounding_threshold": sum(threshold_distance) / len(threshold_distance),
        "min_margin_distance_minus_estimated_error": min_margin,
        "unsafe_count_estimated_error_ge_threshold_distance": sum(unsafe),
        "unsafe_fraction": sum(unsafe) / len(threshold_distance) if unsafe else 0.0,
        "closest_threshold_location": locations[min_index],
        "cell_count": len(threshold_distance),
    }


def main() -> int:
    started = time.perf_counter()
    bdf2_runs: Dict[str, Q1Result] = {}
    runtimes: Dict[str, float] = {}
    for dt in (1.0, 0.5, 0.25):
        key = f"dt{dt}"
        bdf2_runs[key], runtimes[key] = _run("BDF2", dt)
    be_result, be_runtime = _run("BE", 0.25)
    bdf2_comparisons = {
        "dt1.0_vs_dt0.5": _comparison(bdf2_runs["dt1.0"], bdf2_runs["dt0.5"], "BDF2_dt1.0", "BDF2_dt0.5"),
        "dt0.5_vs_dt0.25": _comparison(bdf2_runs["dt0.5"], bdf2_runs["dt0.25"], "BDF2_dt0.5", "BDF2_dt0.25"),
    }
    be_vs_bdf2 = _comparison(be_result, bdf2_runs["dt0.25"], "BE_dt0.25", "BDF2_dt0.25")
    bdf2_orders = _orders(
        bdf2_comparisons["dt1.0_vs_dt0.5"],
        bdf2_comparisons["dt0.5_vs_dt0.25"],
    )
    bdf2_rounding_safety = {
        field: {
            region: _rounding_safety(
                bdf2_runs["dt0.25"],
                field,
                region,
                bdf2_orders[field][region]["linf"]["richardson_remaining_error"],
            )
            for region in ("full_grid", "center", "surface", "paper_table_points")
        }
        for field in ("temperature_c", "moisture_kg_kg")
    }
    payload: Dict[str, Any] = {
        "experiment_id": "EXP-Q1-NUM-REMEDIATION",
        "status": "COMPLETED",
        "method": "M1-NUM-T2",
        "method_change_scope": "time_integrator_only; one BE startup step then BDF2; same physics and spatial FVM",
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "input_hashes": {"A题/附件/附件1.xlsx": "7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7"},
        "scope": {
            "n_intervals": 320,
            "full_grid": "1..1800 s x 0.0..2.0 cm",
            "paper_table_points": "100,300,600,900,1200,1500,1800 s x 0,0.5,1,1.5,2 cm",
            "picard_tolerance": 1.0e-8,
        },
        "bdf2_runs": {key: _run_summary(result, runtimes[key]) for key, result in bdf2_runs.items()},
        "backward_euler_reference": _run_summary(be_result, be_runtime),
        "bdf2_comparisons": bdf2_comparisons,
        "bdf2_observed_order_and_richardson": bdf2_orders,
        "bdf2_rounding_safety": bdf2_rounding_safety,
        "backward_euler_vs_bdf2": be_vs_bdf2,
        "runtime_seconds": time.perf_counter() - started,
        "candidate_workbook_generated": False,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "config.json").write_text(
        json.dumps(
            {
                "experiment_id": payload["experiment_id"],
                "code_commit": payload["code_commit"],
                "method": payload["method"],
                "method_change_scope": payload["method_change_scope"],
                "input_hashes": payload["input_hashes"],
                "scope": payload["scope"],
                "bdf2_runs": payload["bdf2_runs"],
                "backward_euler_reference": payload["backward_euler_reference"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "notes.md").write_text(
        "# EXP-Q1-NUM-REMEDIATION\n\n"
        "BDF2 numerical-method candidate versus the retained Backward-Euler reference at N=320. "
        "The candidate changes no physical model and does not generate result1.xlsx.\n\n"
        f"Status: `{payload['status']}`\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("Evidence written to experiments/EXP-Q1-NUM-REMEDIATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
