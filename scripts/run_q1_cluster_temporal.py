"""Temporal ladder for the benchmarked boundary-clustered real-Q1 grid."""

from __future__ import annotations

import json
import math
import platform
import subprocess
import sys
import time
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Sequence

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q1.config import DEFAULT_PARAMETERS, Q1RunConfig
from src.q1.inputs import BoundaryProvider
from src.q1.solver import Q1Result, run_m1_nonuniform


OUTPUT_DIR = ROOT / "experiments" / "EXP-Q1-CLUSTER-TEMPORAL"
TIMES_S = (0.25, 0.5, 1.0, 2.0, 5.0, 10.0)
POSITIONS_M = (0.018, 0.019, 0.02)
OUTPUT_POSITIONS_M = tuple(index * 0.001 for index in range(21))


def _config(time_step_s: float, n_intervals: int = 640) -> Q1RunConfig:
    return Q1RunConfig(
        end_time_s=10.0,
        time_step_s=time_step_s,
        n_intervals=n_intervals,
        interpolation="linear",
        surface_boundary="robin",
    )


def _sample(result: Q1Result, time_s: float, position_m: float) -> float:
    time_index = next(index for index, value in enumerate(result.times_s) if abs(value - time_s) < 1.0e-10)
    position_index = min(range(len(result.grid.nodes_m)), key=lambda index: abs(result.grid.nodes_m[index] - position_m))
    if abs(result.grid.nodes_m[position_index] - position_m) > 1.0e-12:
        raise ValueError(f"position is not an explicit grid node: {position_m}")
    return result.moistures_kg_kg[time_index][position_index]


def _compare(first: Q1Result, second: Q1Result) -> Dict[str, Any]:
    differences = [
        [abs(_sample(first, time_s, position) - _sample(second, time_s, position)) for position in POSITIONS_M]
        for time_s in TIMES_S
    ]
    values = [value for row in differences for value in row]
    max_index = values.index(max(values))
    time_index, position_index = divmod(max_index, len(POSITIONS_M))
    return {
        "positions_cm": [position * 100.0 for position in POSITIONS_M],
        "linf": max(values),
        "mean_abs": sum(values) / len(values),
        "rmse": math.sqrt(sum(value * value for value in values) / len(values)),
        "max_location": {"time_s": TIMES_S[time_index], "distance_cm": POSITIONS_M[position_index] * 100.0},
        "by_time": [
            {"time_s": time_s, "r1.8cm_abs": row[0], "r1.9cm_abs": row[1], "r2.0cm_abs": row[2], "max_abs": max(row)}
            for time_s, row in zip(TIMES_S, differences)
        ],
    }


def _order(coarse: float, fine: float) -> Dict[str, float | None]:
    if coarse <= 0.0 or fine <= 0.0:
        return {"observed_order": None, "richardson_remaining_error": None}
    p = math.log(coarse / fine, 2.0)
    return {"observed_order": p, "richardson_remaining_error": fine / (2.0**p - 1.0) if p > 0.0 else None}


def _rounding_certification(value: float, uncertainty: float) -> Dict[str, Any]:
    """Certify four-decimal rounding only when the uncertainty interval is safe."""
    rounded = Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    scaled = value * 10000.0
    fractional = scaled - math.floor(scaled)
    distance_to_threshold = abs(fractional - 0.5) / 10000.0
    certified = uncertainty < distance_to_threshold
    return {
        "rounded_4dp_half_up": float(rounded),
        "uncertainty_interval_kg_kg": [value - uncertainty, value + uncertainty],
        "distance_to_nearest_half_up_threshold_kg_kg": distance_to_threshold,
        "status": "ROUNDING_CERTIFIED" if certified else "ROUNDING_AMBIGUOUS",
    }


def _summary(result: Q1Result, runtime_seconds: float) -> Dict[str, Any]:
    surface_index = len(result.grid.nodes_m) - 1
    return {
        "runtime_seconds": runtime_seconds,
        "n_intervals_actual": result.grid.n_intervals,
        "min_dr_m": result.grid.min_dr_m,
        "max_dr_m": result.grid.max_dr_m,
        "history_length": len(result.times_s),
        "picard_max_iterations": max(result.picard_iterations[1:]),
        "surface_moisture_at_t1": _sample(result, 1.0, 0.02),
        "surface_node_cm": result.grid.nodes_m[surface_index] * 100.0,
        "official_output_nodes_present": all(
            any(abs(node - position) < 1.0e-12 for node in result.grid.nodes_m)
            for position in OUTPUT_POSITIONS_M
        ),
    }


def main() -> int:
    started = time.perf_counter()
    boundary = BoundaryProvider.from_attachment1(ROOT / "A题" / "附件" / "附件1.xlsx")
    results: Dict[str, Q1Result] = {}
    runtimes: Dict[str, float] = {}
    specs = {
        "cluster640_dt0.25": (640, 0.25),
        "cluster640_dt0.125": (640, 0.125),
        "cluster640_dt0.0625": (640, 0.0625),
        "cluster640_dt0.03125": (640, 0.03125),
        "cluster320_dt0.03125": (320, 0.03125),
        "cluster1280_dt0.0625": (1280, 0.0625),
        "cluster1280_dt0.03125": (1280, 0.03125),
        "cluster1280_dt0.015625_reference": (1280, 0.015625),
        "cluster1280_dt0.0078125_reference": (1280, 0.0078125),
    }
    for label, (n_intervals, dt_s) in specs.items():
        case_started = time.perf_counter()
        results[label] = run_m1_nonuniform(
            _config(dt_s, n_intervals),
            boundary,
            DEFAULT_PARAMETERS,
            cluster_power=2.0,
            required_output_positions_m=OUTPUT_POSITIONS_M,
        )
        runtimes[label] = time.perf_counter() - case_started

    temporal_keys = (
        "cluster640_dt0.25",
        "cluster640_dt0.125",
        "cluster640_dt0.0625",
        "cluster640_dt0.03125",
    )
    temporal_comparisons = {
        f"{coarse}_vs_{fine}": _compare(results[coarse], results[fine])
        for coarse, fine in zip(temporal_keys, temporal_keys[1:])
    }
    spatial_reference_keys = (
        "cluster320_dt0.03125",
        "cluster640_dt0.03125",
        "cluster1280_dt0.03125",
    )
    reference_keys = (
        "cluster1280_dt0.0625",
        "cluster1280_dt0.03125",
        "cluster1280_dt0.015625_reference",
        "cluster1280_dt0.0078125_reference",
    )
    reference_comparison = _compare(results[reference_keys[0]], results[reference_keys[-1]])
    dt_reference_fine = abs(_sample(results[reference_keys[2]], 1.0, 0.02) - _sample(results[reference_keys[3]], 1.0, 0.02))
    dt_reference_coarse = abs(_sample(results[reference_keys[1]], 1.0, 0.02) - _sample(results[reference_keys[2]], 1.0, 0.02))
    reference_order = _order(dt_reference_coarse, dt_reference_fine)
    reference_t1_official_values: Dict[str, Any] = {}
    for position_m in OUTPUT_POSITIONS_M:
        space_coarse = abs(
            _sample(results[spatial_reference_keys[0]], 1.0, position_m)
            - _sample(results[spatial_reference_keys[1]], 1.0, position_m)
        )
        space_fine = abs(
            _sample(results[spatial_reference_keys[1]], 1.0, position_m)
            - _sample(results[spatial_reference_keys[2]], 1.0, position_m)
        )
        time_coarse = abs(
            _sample(results[reference_keys[1]], 1.0, position_m)
            - _sample(results[reference_keys[2]], 1.0, position_m)
        )
        time_fine = abs(
            _sample(results[reference_keys[2]], 1.0, position_m)
            - _sample(results[reference_keys[3]], 1.0, position_m)
        )
        space_order = _order(space_coarse, space_fine)
        time_order = _order(time_coarse, time_fine)
        space_remaining = space_order["richardson_remaining_error"] or 0.0
        time_remaining = time_order["richardson_remaining_error"] or 0.0
        combined_uncertainty = max(space_remaining, time_remaining)
        value = _sample(results[reference_keys[3]], 1.0, position_m)
        rounding = _rounding_certification(value, combined_uncertainty)
        label = f"{position_m * 100.0:.4f}_cm"
        reference_t1_official_values[label] = {
            "position_m": position_m,
            "C_reference_kg_kg": value,
            "space_coarse_difference_kg_kg": space_coarse,
            "space_fine_difference_kg_kg": space_fine,
            "space_observed_order": space_order["observed_order"],
            "space_remaining_error_kg_kg": space_remaining,
            "time_coarse_difference_kg_kg": time_coarse,
            "time_fine_difference_kg_kg": time_fine,
            "time_observed_order": time_order["observed_order"],
            "time_remaining_error_kg_kg": time_remaining,
            "combined_conservative_uncertainty_kg_kg": combined_uncertainty,
            **rounding,
        }
    certified_count = sum(
        row["status"] == "ROUNDING_CERTIFIED" for row in reference_t1_official_values.values()
    )
    ambiguous_count = len(reference_t1_official_values) - certified_count
    payload: Dict[str, Any] = {
        "experiment_id": "EXP-Q1-CLUSTER-TEMPORAL",
        "status": "COMPLETED",
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "input_hashes": {"A题/附件/附件1.xlsx": "7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7"},
        "scope": {
            "end_time_s": 10.0,
            "cluster_power": 2.0,
            "fixed_cluster_base_intervals": 640,
            "temporal_steps_s": [0.25, 0.125, 0.0625, 0.03125],
            "spatial_reference": "cluster base320/base640/base1280 at dt=0.03125",
            "reference": "cluster base1280 at dt=0.0625/0.03125/0.015625/0.0078125",
            "comparison_times_s": list(TIMES_S),
            "comparison_positions_cm": [position * 100.0 for position in POSITIONS_M],
        },
        "cases": {label: _summary(result, runtimes[label]) for label, result in results.items()},
        "temporal_comparisons": temporal_comparisons,
        "cluster1280_reference_comparison": reference_comparison,
        "cluster1280_surface_t1_temporal_order_and_richardson": reference_order,
        "cluster1280_surface_t1_dt0.015625_vs_dt0.0078125": dt_reference_fine,
        "reference_t1_official_values": reference_t1_official_values,
        "rounding_certification": {
            "precision_decimals": 4,
            "threshold_rule": "half-up; certify only if the conservative uncertainty interval does not cross a half-unit threshold",
            "certified_count": certified_count,
            "ambiguous_count": ambiguous_count,
            "total_count": len(reference_t1_official_values),
        },
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
        "cases": payload["cases"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "notes.md").write_text(
        "# EXP-Q1-CLUSTER-TEMPORAL\n\n"
        "Short temporal ladder on the benchmarked boundary-clustered real-Q1 grid. "
        "No physical input or workbook was modified.\n\n"
        f"Status: `{payload['status']}`\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "experiment_id": payload["experiment_id"],
        "status": payload["status"],
        "surface_t1": {label: payload["cases"][label]["surface_moisture_at_t1"] for label in payload["cases"]},
        "temporal_comparisons": {
            label: {"linf": value["linf"], "max_location": value["max_location"]}
            for label, value in temporal_comparisons.items()
        },
        "reference_order": reference_order,
        "runtime_seconds": payload["runtime_seconds"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
