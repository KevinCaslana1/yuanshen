"""Diagnose Q1's early moisture initial layer on short, staged runs.

This experiment deliberately stops at 10 s. It records the t=0 Robin
compatibility residual, the sqrt(D*t) diagnostic scale, a non-Cartesian
uniform-grid reference ladder, and short-time raw differences. It never
changes the official input/initial condition and never writes a workbook.
"""

from __future__ import annotations

import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q1.config import DEFAULT_PARAMETERS, Q1RunConfig
from src.q1.inputs import BoundaryProvider
from src.q1.solver import Q1Result, run_m1


OUTPUT_DIR = ROOT / "experiments" / "EXP-Q1-INITIAL-LAYER"
EARLY_TIMES_S = (0.25, 0.5, 1.0, 2.0, 5.0, 10.0)
RADIUS_M = DEFAULT_PARAMETERS.radius_m
COMMON_POSITIONS_M = (RADIUS_M - 0.0005, RADIUS_M - 0.00025, RADIUS_M, 0.019)


def _config(n_intervals: int, time_step_s: float, end_time_s: float = 10.0) -> Q1RunConfig:
    return Q1RunConfig(
        end_time_s=end_time_s,
        time_step_s=time_step_s,
        n_intervals=n_intervals,
        interpolation="linear",
        surface_boundary="robin",
    )


def _sample(result: Q1Result, time_s: float, position_m: float) -> float:
    time_index = round(time_s / result.config.time_step_s)
    position_index = round(position_m / result.grid.dr_m)
    if abs(result.times_s[time_index] - time_s) > 1.0e-10:
        raise ValueError(f"time is not aligned: {time_s}")
    if abs(position_index * result.grid.dr_m - position_m) > 1.0e-12:
        raise ValueError(f"position is not aligned: {position_m}")
    return result.moistures_kg_kg[time_index][position_index]


def _case_summary(result: Q1Result, runtime_seconds: float) -> Dict[str, Any]:
    local_positions = (
        RADIUS_M,
        RADIUS_M - result.grid.dr_m,
        RADIUS_M - 2.0 * result.grid.dr_m,
    )
    return {
        "n_intervals": result.grid.n_intervals,
        "dr_m": result.grid.dr_m,
        "time_step_s": result.config.time_step_s,
        "end_time_s": result.times_s[-1],
        "runtime_seconds": runtime_seconds,
        "picard_max_iterations": max(result.picard_iterations[1:]),
        "local_layer_positions_cm": [position * 100.0 for position in local_positions],
        "local_layer_moisture_at_times": {
            str(time_s): [_sample(result, time_s, position) for position in local_positions]
            for time_s in EARLY_TIMES_S
        },
        "common_position_moisture_at_times": {
            str(time_s): [_sample(result, time_s, position) for position in COMMON_POSITIONS_M]
            for time_s in EARLY_TIMES_S
        },
    }


def _compare(
    first: Q1Result,
    second: Q1Result,
    times_s: Sequence[float],
    positions_m: Sequence[float],
) -> Dict[str, Any]:
    differences = [
        [abs(_sample(first, time_s, position) - _sample(second, time_s, position)) for position in positions_m]
        for time_s in times_s
    ]
    values = [value for row in differences for value in row]
    max_index = values.index(max(values))
    time_index, position_index = divmod(max_index, len(positions_m))
    return {
        "times_s": list(times_s),
        "positions_cm": [position * 100.0 for position in positions_m],
        "linf": max(values),
        "mean_abs": sum(values) / len(values),
        "rmse": math.sqrt(sum(value * value for value in values) / len(values)),
        "max_location": {
            "time_s": times_s[time_index],
            "distance_cm": positions_m[position_index] * 100.0,
        },
        "by_time": [
            {"time_s": time_s, "linf": max(row), "mean_abs": sum(row) / len(row)}
            for time_s, row in zip(times_s, differences)
        ],
        "by_position": [
            {
                "distance_cm": position * 100.0,
                "linf": max(row[position_index] for row in differences),
                "mean_abs": sum(row[position_index] for row in differences) / len(differences),
            }
            for position_index, position in enumerate(positions_m)
        ],
    }


def _order_and_richardson(coarse: float, fine: float) -> Dict[str, float | None]:
    if coarse <= 0.0 or fine <= 0.0:
        return {"observed_order": None, "richardson_remaining_error": None}
    order = math.log(coarse / fine, 2.0)
    remaining = fine / (2.0**order - 1.0) if order > 0.0 else None
    return {"observed_order": order, "richardson_remaining_error": remaining}


def _compatibility(boundary: BoundaryProvider) -> Dict[str, Any]:
    temperature_environment_c, moisture_environment = boundary.at(0.0)
    initial_temperature_c = 28.0
    initial_moisture = 2.55
    diffusivity = DEFAULT_PARAMETERS.diffusivity_m2_s(initial_moisture)
    temperature_residual = -DEFAULT_PARAMETERS.heat_transfer_w_m2_k * (
        initial_temperature_c - temperature_environment_c
    )
    moisture_residual = -DEFAULT_PARAMETERS.mass_transfer_m_s * (
        initial_moisture - moisture_environment
    )
    return {
        "time_s": 0.0,
        "temperature": {
            "initial_field_c": initial_temperature_c,
            "environment_c": temperature_environment_c,
            "initial_radial_gradient_c_per_m": 0.0,
            "robin_residual_w_m2": temperature_residual,
            "status": "COMPATIBLE_WITHIN_REPRESENTATION" if abs(temperature_residual) < 1.0e-14 else "INCOMPATIBLE",
        },
        "moisture": {
            "initial_field_kg_kg": initial_moisture,
            "environment_kg_kg": moisture_environment,
            "initial_radial_gradient_kg_kg_per_m": 0.0,
            "D_at_initial_m2_s": diffusivity,
            "initial_jump_kg_kg": initial_moisture - moisture_environment,
            "robin_residual_m_s": moisture_residual,
            "outward_flux_m_s": -moisture_residual,
            "status": "INCOMPATIBLE_INITIAL_TRACE" if abs(moisture_residual) > 1.0e-14 else "COMPATIBLE_WITHIN_REPRESENTATION",
        },
        "interpretation": "diagnostic hypothesis only; do not modify initial field or official input",
    }


def main() -> int:
    started = time.perf_counter()
    boundary = BoundaryProvider.from_attachment1(ROOT / "A题" / "附件" / "附件1.xlsx")
    results: Dict[str, Q1Result] = {}
    runtimes: Dict[str, float] = {}
    case_specs = [
        (320, 0.03125),
        (640, 0.03125),
        (1280, 0.03125),
        (640, 0.25),
        (640, 0.125),
        (640, 0.0625),
        (1280, 0.0625),
        (1280, 0.015625),
    ]
    for n_intervals, dt_s in case_specs:
        key = f"N{n_intervals}_dt{dt_s}"
        started_case = time.perf_counter()
        results[key] = run_m1(_config(n_intervals, dt_s), boundary, DEFAULT_PARAMETERS)
        runtimes[key] = time.perf_counter() - started_case

    spatial_keys = ("N320_dt0.03125", "N640_dt0.03125", "N1280_dt0.03125")
    spatial_comparisons: Dict[str, Any] = {}
    for coarse_key, fine_key in zip(spatial_keys, spatial_keys[1:]):
        comparison = _compare(results[coarse_key], results[fine_key], EARLY_TIMES_S, COMMON_POSITIONS_M)
        spatial_comparisons[f"{coarse_key}_vs_{fine_key}"] = comparison
    spatial_errors = [
        _compare(results[spatial_keys[index]], results[spatial_keys[index + 1]], (1.0,), (RADIUS_M,))["linf"]
        for index in (0, 1)
    ]
    spatial_order = _order_and_richardson(*spatial_errors)

    temporal_keys = ("N640_dt0.25", "N640_dt0.125", "N640_dt0.0625")
    temporal_comparisons: Dict[str, Any] = {}
    for coarse_key, fine_key in zip(temporal_keys, temporal_keys[1:]):
        temporal_comparisons[f"{coarse_key}_vs_{fine_key}"] = _compare(
            results[coarse_key], results[fine_key], EARLY_TIMES_S, COMMON_POSITIONS_M
        )

    reference_temporal_keys = ("N1280_dt0.0625", "N1280_dt0.03125", "N1280_dt0.015625")
    reference_temporal_comparisons: Dict[str, Any] = {}
    for coarse_key, fine_key in zip(reference_temporal_keys, reference_temporal_keys[1:]):
        reference_temporal_comparisons[f"{coarse_key}_vs_{fine_key}"] = _compare(
            results[coarse_key], results[fine_key], EARLY_TIMES_S, COMMON_POSITIONS_M
        )
    temporal_errors = [
        _compare(results[reference_temporal_keys[index]], results[reference_temporal_keys[index + 1]], (1.0,), (RADIUS_M,))["linf"]
        for index in (0, 1)
    ]
    temporal_order = _order_and_richardson(*temporal_errors)

    reference_result = results["N1280_dt0.015625"]
    reference_positions = (RADIUS_M, RADIUS_M - 0.00025, RADIUS_M - 0.0005, 0.019)
    reference_values: Dict[str, Any] = {}
    for position in reference_positions:
        position_key = f"{position * 100.0:.4f}_cm"
        space_error_values = [
            abs(_sample(results[spatial_keys[index]], 1.0, position) - _sample(results[spatial_keys[index + 1]], 1.0, position))
            for index in (0, 1)
        ]
        time_error_values = [
            abs(_sample(results[reference_temporal_keys[index]], 1.0, position) - _sample(results[reference_temporal_keys[index + 1]], 1.0, position))
            for index in (0, 1)
        ]
        space_estimate = _order_and_richardson(*space_error_values)
        time_estimate = _order_and_richardson(*time_error_values)
        space_remaining = space_estimate["richardson_remaining_error"]
        time_remaining = time_estimate["richardson_remaining_error"]
        remaining_candidates = [value for value in (space_remaining, time_remaining) if value is not None]
        reference_values[position_key] = {
            "time_s": 1.0,
            "distance_cm": position * 100.0,
            "C_reference_kg_kg": _sample(reference_result, 1.0, position),
            "space_observed_order": space_estimate["observed_order"],
            "space_remaining_error_kg_kg": space_remaining,
            "time_observed_order": time_estimate["observed_order"],
            "time_remaining_error_kg_kg": time_remaining,
            "combined_conservative_uncertainty_kg_kg": max(remaining_candidates) if remaining_candidates else None,
        }

    D0 = DEFAULT_PARAMETERS.diffusivity_m2_s(2.55)
    diffusion_scales = [
        {
            "time_s": time_s,
            "sqrt_Dt_m": math.sqrt(D0 * time_s),
            "sqrt_Dt_cm": math.sqrt(D0 * time_s) * 100.0,
            "mesh_cells_across_scale": {
                str(n_intervals): math.sqrt(D0 * time_s) / (2.0 * RADIUS_M / n_intervals)
                for n_intervals in (160, 320, 640)
            },
        }
        for time_s in EARLY_TIMES_S
    ]

    payload: Dict[str, Any] = {
        "experiment_id": "EXP-Q1-INITIAL-LAYER",
        "status": "COMPLETED",
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "input_hashes": {"A题/附件/附件1.xlsx": "7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7"},
        "scope": {
            "short_end_time_s": 10.0,
            "early_times_s": list(EARLY_TIMES_S),
            "common_positions_cm": [position * 100.0 for position in COMMON_POSITIONS_M],
            "local_positions": "R, R-dr, R-2dr per grid",
            "staged_non_cartesian_ladder": "space N=320/640/1280 at dt=0.03125; time N=640 at dt=0.25/0.125/0.0625; reference N=1280 at dt=0.0625/0.03125/0.015625",
        },
        "compatibility": _compatibility(boundary),
        "diffusion_scale": {"D_definition": "D(C0) with C0=2.55 kg/kg", "D0_m2_s": D0, "values": diffusion_scales},
        "cases": {key: _case_summary(results[key], runtimes[key]) for key in sorted(results)},
        "spatial_comparisons": spatial_comparisons,
        "spatial_surface_t1_order_and_richardson": spatial_order,
        "temporal_short_comparisons": temporal_comparisons,
        "reference_temporal_comparisons": reference_temporal_comparisons,
        "reference_surface_t1_order_and_richardson": temporal_order,
        "reference_t1_values": reference_values,
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
        "compatibility": payload["compatibility"],
        "diffusion_scale": payload["diffusion_scale"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "notes.md").write_text(
        "# EXP-Q1-INITIAL-LAYER\n\n"
        "Short staged Q1 experiment. It tests the t=0 Robin compatibility hypothesis, "
        "resolves early surface moisture with a non-Cartesian uniform-grid ladder, "
        "and writes no result workbook.\n\n"
        f"Status: `{payload['status']}`\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "experiment_id": payload["experiment_id"],
        "status": payload["status"],
        "compatibility": payload["compatibility"],
        "reference_t1_values": payload["reference_t1_values"],
        "runtime_seconds": payload["runtime_seconds"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
