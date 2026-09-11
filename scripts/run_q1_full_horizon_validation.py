"""Run full-horizon Q1 convergence checks for the authorized production candidates.

This script never writes a workbook. It compares the same physical output
times/positions for clustered conservative FVM + BDF2 runs and uses estimated
discretization uncertainty as the primary team numerical criterion.
"""

from __future__ import annotations

import json
import math
import platform
import subprocess
import sys
import time
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q1.config import DEFAULT_PARAMETERS, Q1RunConfig
from src.q1.inputs import BoundaryProvider
from src.q1.solver import Q1SampledResult, run_m1_bdf2_sampled


FULL_TIMES_S = tuple(range(1, 1801))
FULL_POSITIONS_M = tuple(index * 0.001 for index in range(21))
PAPER_TIMES_S = (100, 300, 600, 900, 1200, 1500, 1800)
PAPER_POSITIONS_M = (0.0, 0.005, 0.01, 0.015, 0.02)
FIELDS = ("temperature_c", "moisture_kg_kg")
ACCURACY_TARGETS = {"temperature_c": 5.0e-5, "moisture_kg_kg": 5.0e-5}
ROUNDING_QUANTUM = Decimal("0.0001")


def _config(time_step_s: float, n_intervals: int) -> Q1RunConfig:
    return Q1RunConfig(
        end_time_s=1800.0,
        time_step_s=time_step_s,
        n_intervals=n_intervals,
        interpolation="linear",
        surface_boundary="robin",
    )


def _run(boundary: BoundaryProvider, time_step_s: float, n_intervals: int) -> Q1SampledResult:
    return run_m1_bdf2_sampled(
        _config(time_step_s, n_intervals),
        boundary,
        DEFAULT_PARAMETERS,
        cluster_power=2.0,
        required_output_positions_m=FULL_POSITIONS_M,
        record_times_s=FULL_TIMES_S,
    )


def _position_indices(result: Q1SampledResult, positions_m: Sequence[float]) -> Tuple[int, ...]:
    indices = []
    for position in positions_m:
        index = min(range(len(result.stored_positions_m)), key=lambda candidate: abs(result.stored_positions_m[candidate] - position))
        if abs(result.stored_positions_m[index] - position) > 1.0e-12:
            raise ValueError(f"sampled result does not contain requested output position {position}")
        indices.append(index)
    return tuple(indices)


def _time_indices(result: Q1SampledResult, times_s: Sequence[int]) -> Tuple[int, ...]:
    indices = []
    for time_s in times_s:
        index = min(range(len(result.times_s)), key=lambda candidate: abs(result.times_s[candidate] - time_s))
        if abs(result.times_s[index] - time_s) > 1.0e-9:
            raise ValueError(f"sampled result does not contain requested output time {time_s}")
        indices.append(index)
    return tuple(indices)


def _field_rows(
    result: Q1SampledResult,
    field: str,
    times_s: Sequence[int],
    positions_m: Sequence[float],
) -> List[List[float]]:
    time_indices = _time_indices(result, times_s)
    position_indices = _position_indices(result, positions_m)
    source = result.temperatures_k if field == "temperature_c" else result.moistures_kg_kg
    rows = []
    for time_index in time_indices:
        row = [source[time_index][position_index] for position_index in position_indices]
        if field == "temperature_c":
            row = [value - 273.15 for value in row]
        rows.append(row)
    return rows


def _flatten(rows: Iterable[Iterable[float]]) -> List[float]:
    return [value for row in rows for value in row]


def _raw_stats(
    first: Sequence[float],
    second: Sequence[float],
    times_s: Sequence[int],
    positions_m: Sequence[float],
) -> Dict[str, Any]:
    differences = [abs(left - right) for left, right in zip(first, second)]
    max_value = max(differences)
    max_index = differences.index(max_value)
    time_index, position_index = divmod(max_index, len(positions_m))
    return {
        "linf": max_value,
        "mean_abs": sum(differences) / len(differences),
        "rmse": math.sqrt(sum(value * value for value in differences) / len(differences)),
        "location_of_maximum_error": {
            "time_s": times_s[time_index],
            "distance_cm": positions_m[position_index] * 100.0,
        },
        "cell_count": len(differences),
    }


def _comparison(first: Q1SampledResult, second: Q1SampledResult, first_label: str, second_label: str) -> Dict[str, Any]:
    regions = {
        "full_grid": (FULL_TIMES_S, FULL_POSITIONS_M),
        "center_line": (FULL_TIMES_S, (0.0,)),
        "surface_line": (FULL_TIMES_S, (0.02,)),
        "paper_table_points": (PAPER_TIMES_S, PAPER_POSITIONS_M),
    }
    result: Dict[str, Any] = {"first": first_label, "second": second_label, "fields": {}}
    for field in FIELDS:
        result["fields"][field] = {}
        for region, (times_s, positions_m) in regions.items():
            first_rows = _field_rows(first, field, times_s, positions_m)
            second_rows = _field_rows(second, field, times_s, positions_m)
            result["fields"][field][region] = _raw_stats(
                _flatten(first_rows),
                _flatten(second_rows),
                times_s,
                positions_m,
            )
    return result


def _observed_order(coarse_error: float, fine_error: float) -> float | None:
    if coarse_error <= 0.0 or fine_error <= 0.0:
        return None
    return math.log(coarse_error / fine_error, 2.0)


def _remaining_error(error: float, order: float | None) -> float | None:
    if order is None or order <= 0.0:
        return None
    denominator = 2.0**order - 1.0
    return error / denominator if denominator > 0.0 else None


def _richardson_is_stable(order: float | None) -> bool:
    """Use local Richardson only when its denominator is numerically meaningful."""
    return order is not None and 0.5 <= order <= 4.0


def _convergence_summary(comparisons: Dict[str, Dict[str, Any]], coarse_key: str, fine_key: str) -> Dict[str, Any]:
    summary: Dict[str, Any] = {}
    for field in FIELDS:
        summary[field] = {}
        for region in ("full_grid", "center_line", "surface_line", "paper_table_points"):
            summary[field][region] = {}
            for norm in ("linf", "mean_abs", "rmse"):
                coarse_error = comparisons[coarse_key]["fields"][field][region][norm]
                fine_error = comparisons[fine_key]["fields"][field][region][norm]
                order = _observed_order(coarse_error, fine_error)
                summary[field][region][norm] = {
                    "coarse_error": coarse_error,
                    "fine_error": fine_error,
                    "observed_order": order,
                    "remaining_error_for_coarse_configuration": _remaining_error(coarse_error, order),
                    "remaining_error_for_fine_configuration": _remaining_error(fine_error, order),
                }
    return summary


def _pointwise_uncertainty(
    coarse: Q1SampledResult,
    middle: Q1SampledResult,
    fine: Q1SampledResult,
    field: str,
    coarse_label: str,
    middle_label: str,
    fine_label: str,
) -> Dict[str, Any]:
    coarse_rows = _field_rows(coarse, field, FULL_TIMES_S, FULL_POSITIONS_M)
    middle_rows = _field_rows(middle, field, FULL_TIMES_S, FULL_POSITIONS_M)
    fine_rows = _field_rows(fine, field, FULL_TIMES_S, FULL_POSITIONS_M)
    coarse_remaining: List[List[float | None]] = []
    fine_remaining: List[List[float | None]] = []
    coarse_richardson_remaining: List[List[float | None]] = []
    fine_richardson_remaining: List[List[float | None]] = []
    coarse_raw_error: List[List[float]] = []
    fine_raw_error: List[List[float]] = []
    fine_orders: List[List[float | None]] = []
    fine_estimate_methods: List[List[str]] = []
    fallback_count = 0
    for coarse_row, middle_row, fine_row in zip(coarse_rows, middle_rows, fine_rows):
        coarse_row_remaining: List[float | None] = []
        fine_row_remaining: List[float | None] = []
        coarse_row_richardson: List[float | None] = []
        fine_row_richardson: List[float | None] = []
        coarse_row_raw: List[float] = []
        fine_row_raw: List[float] = []
        order_row: List[float | None] = []
        method_row: List[str] = []
        for coarse_value, middle_value, fine_value in zip(coarse_row, middle_row, fine_row):
            coarse_error = abs(coarse_value - middle_value)
            fine_error = abs(middle_value - fine_value)
            order = _observed_order(coarse_error, fine_error)
            coarse_richardson = _remaining_error(coarse_error, order)
            fine_richardson = _remaining_error(fine_error, order)
            if _richardson_is_stable(order):
                coarse_estimate = coarse_richardson
                fine_estimate = fine_richardson
                method = "LOCAL_RICHARDSON"
            else:
                # A near-zero/non-positive local order makes the Richardson
                # denominator ill-conditioned or nonphysical. Keep the raw
                # adjacent fine-level difference as a transparent local
                # uncertainty envelope instead of manufacturing a huge value.
                coarse_estimate = max(coarse_error, fine_error)
                fine_estimate = max(coarse_error, fine_error)
                method = "RAW_ADJACENT_FINE_ENVELOPE"
                fallback_count += 1
            order_row.append(order)
            coarse_row_remaining.append(coarse_estimate)
            fine_row_remaining.append(fine_estimate)
            coarse_row_richardson.append(coarse_richardson)
            fine_row_richardson.append(fine_richardson)
            coarse_row_raw.append(coarse_error)
            fine_row_raw.append(fine_error)
            method_row.append(method)
        coarse_remaining.append(coarse_row_remaining)
        fine_remaining.append(fine_row_remaining)
        coarse_richardson_remaining.append(coarse_row_richardson)
        fine_richardson_remaining.append(fine_row_richardson)
        coarse_raw_error.append(coarse_row_raw)
        fine_raw_error.append(fine_row_raw)
        fine_orders.append(order_row)
        fine_estimate_methods.append(method_row)

    def _maximum(grid: Sequence[Sequence[float | None]]) -> Dict[str, Any]:
        candidates = [
            (value, row_index, column_index)
            for row_index, row in enumerate(grid)
            for column_index, value in enumerate(row)
            if value is not None
        ]
        if not candidates:
            return {"value": None, "location": None}
        value, row_index, column_index = max(candidates, key=lambda item: item[0])
        return {
            "value": value,
            "location": {
                "time_s": FULL_TIMES_S[row_index],
                "distance_cm": FULL_POSITIONS_M[column_index] * 100.0,
            },
        }

    return {
        "coarse_configuration": coarse_label,
        "middle_configuration": middle_label,
        "fine_configuration": fine_label,
        "coarse_remaining_error": coarse_remaining,
        "fine_remaining_error": fine_remaining,
        "coarse_richardson_remaining_error": coarse_richardson_remaining,
        "fine_richardson_remaining_error": fine_richardson_remaining,
        "coarse_raw_error": coarse_raw_error,
        "fine_raw_error": fine_raw_error,
        "fine_observed_order": fine_orders,
        "fine_estimate_method": fine_estimate_methods,
        "richardson_fallback_count": fallback_count,
        "maximum_coarse_remaining_error": _maximum(coarse_remaining),
        "maximum_fine_remaining_error": _maximum(fine_remaining),
    }


def _rounding_distance(value: float) -> float:
    scaled = value * 10000.0
    fraction = scaled - math.floor(scaled)
    return abs(fraction - 0.5) / 10000.0


def _rounding_status(value: float, uncertainty: float) -> str:
    return "ROUNDING_CERTIFIED" if uncertainty < _rounding_distance(value) else "ROUNDING_AMBIGUOUS"


def _criterion_summary(
    reference: Q1SampledResult,
    space_uncertainty: Dict[str, Any],
    time_uncertainty: Dict[str, Any],
    space_configuration: str,
    time_configuration: str,
) -> Dict[str, Any]:
    output: Dict[str, Any] = {
        "space_configuration": space_configuration,
        "time_configuration": time_configuration,
        "fields": {},
    }
    time_index = {time_s: index for index, time_s in enumerate(reference.times_s)}
    for field in FIELDS:
        source = reference.temperatures_c if field == "temperature_c" else reference.moistures_kg_kg
        combined: List[List[float]] = []
        rounding_distance: List[List[float]] = []
        rounding_status: List[List[str]] = []
        failed_locations: List[Dict[str, Any]] = []
        certified = 0
        ambiguous = 0
        max_uncertainty = -1.0
        max_location: Dict[str, Any] | None = None
        for row_index, (space_row, time_row, values) in enumerate(zip(
            space_uncertainty[field]["fine_remaining_error"],
            time_uncertainty[field]["fine_remaining_error"],
            source,
        )):
            combined_row: List[float] = []
            distance_row: List[float] = []
            status_row: List[str] = []
            for column_index, (space_value, time_value, value) in enumerate(zip(space_row, time_row, values)):
                uncertainty = max(space_value or 0.0, time_value or 0.0)
                combined_row.append(uncertainty)
                distance = _rounding_distance(value)
                status = _rounding_status(value, uncertainty)
                distance_row.append(distance)
                status_row.append(status)
                if status == "ROUNDING_CERTIFIED":
                    certified += 1
                else:
                    ambiguous += 1
                if uncertainty > max_uncertainty:
                    max_uncertainty = uncertainty
                    max_location = {
                        "time_s": FULL_TIMES_S[row_index],
                        "distance_cm": FULL_POSITIONS_M[column_index] * 100.0,
                        "raw_value": value,
                    }
                if uncertainty >= ACCURACY_TARGETS[field] and len(failed_locations) < 20:
                    failed_locations.append({
                        "time_s": FULL_TIMES_S[row_index],
                        "distance_cm": FULL_POSITIONS_M[column_index] * 100.0,
                        "raw_value": value,
                        "estimated_uncertainty": uncertainty,
                    })
            combined.append(combined_row)
            rounding_distance.append(distance_row)
            rounding_status.append(status_row)
        surface_uncertainty = {
            str(time_s): combined[time_index[time_s]][-1]
            for time_s in (1, 10, 60, 100, 300, 600, 1800)
        }
        target = ACCURACY_TARGETS[field]
        values = [value for row in combined for value in row]
        output["fields"][field] = {
            "criterion": f"estimated discretization uncertainty < {target:.1e} in the field output unit",
            "target": target,
            "max_estimated_uncertainty": max(values),
            "location_of_maximum_uncertainty": max_location,
            "mean_estimated_uncertainty": sum(values) / len(values),
            "pass_count": sum(value < target for value in values),
            "fail_count": sum(value >= target for value in values),
            "cell_count": len(values),
            "surface_uncertainty_by_time": surface_uncertainty,
            "rounding_certified_count": certified,
            "rounding_ambiguous_count": ambiguous,
            "rounding_total_count": certified + ambiguous,
            "first_20_criterion_failures": failed_locations,
            "combined_uncertainty_grid": combined,
            "rounding_distance_grid": rounding_distance,
            "rounding_status_grid": rounding_status,
        }
    output["pass"] = all(item["fail_count"] == 0 for item in output["fields"].values())
    return output


def _case_summary(result: Q1SampledResult, runtime_seconds: float) -> Dict[str, Any]:
    return {
        "runtime_seconds": runtime_seconds,
        "requested_base_intervals": result.config.n_intervals,
        "n_intervals_actual": result.grid.n_intervals,
        "minimum_dr_m": result.grid.min_dr_m,
        "maximum_dr_m": result.grid.max_dr_m,
        "clustering_ratio_max_over_min": result.grid.max_dr_m / result.grid.min_dr_m,
        "time_step_s": result.config.time_step_s,
        "end_time_s": result.config.end_time_s,
        "internal_step_count": result.internal_step_count,
        "recorded_output_times": len(result.times_s),
        "recorded_output_positions": len(result.stored_positions_m),
        "picard_max_iterations": result.max_picard_iterations,
        "picard_mean_iterations": result.mean_picard_iterations,
        "temperature_range_c": [value - 273.15 for value in result.temperature_range_k],
        "moisture_range_kg_kg": list(result.moisture_range_kg_kg),
        "max_mass_balance_residual": result.max_mass_balance_residual,
        "max_energy_balance_residual": result.max_energy_balance_residual,
        "official_output_nodes_present": tuple(result.stored_positions_m) == FULL_POSITIONS_M,
    }


def _write_experiment(directory_name: str, payload: Dict[str, Any], notes: str) -> None:
    output_dir = ROOT / "experiments" / directory_name
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "config.json").write_text(json.dumps({
        "experiment_id": payload["experiment_id"],
        "code_commit": payload["code_commit"],
        "input_hashes": payload["input_hashes"],
        "scope": payload["scope"],
        "cases": payload["cases"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "notes.md").write_text(f"# {directory_name}\n\n{notes}\n\nStatus: `{payload['status']}`\n", encoding="utf-8")


def main() -> int:
    started = time.perf_counter()
    boundary = BoundaryProvider.from_attachment1(ROOT / "A题" / "附件" / "附件1.xlsx")
    code_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    input_hashes = {"A题/附件/附件1.xlsx": "7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7"}

    spatial_specs = (
        ("Cluster-L1_base320_dt0.125", 320, 0.125),
        ("Cluster-L2_base640_dt0.125", 640, 0.125),
        ("Cluster-L3_base1280_dt0.125", 1280, 0.125),
    )
    temporal_specs = (
        ("Cluster-L3_dt0.25", 1280, 0.25),
        ("Cluster-L3_dt0.125", 1280, 0.125),
        ("Cluster-L3_dt0.0625", 1280, 0.0625),
    )
    results: Dict[str, Q1SampledResult] = {}
    runtimes: Dict[str, float] = {}
    for label, n_intervals, dt_s in spatial_specs + temporal_specs:
        case_started = time.perf_counter()
        results[label] = _run(boundary, dt_s, n_intervals)
        runtimes[label] = time.perf_counter() - case_started

    spatial_comparisons = {
        "Cluster-L1_vs_L2": _comparison(results[spatial_specs[0][0]], results[spatial_specs[1][0]], spatial_specs[0][0], spatial_specs[1][0]),
        "Cluster-L2_vs_L3": _comparison(results[spatial_specs[1][0]], results[spatial_specs[2][0]], spatial_specs[1][0], spatial_specs[2][0]),
    }
    temporal_comparisons = {
        "dt0.5_vs_dt0.25": _comparison(results[temporal_specs[0][0]], results[temporal_specs[1][0]], temporal_specs[0][0], temporal_specs[1][0]),
        "dt0.25_vs_dt0.125": _comparison(results[temporal_specs[1][0]], results[temporal_specs[2][0]], temporal_specs[1][0], temporal_specs[2][0]),
    }
    spatial_order = _convergence_summary(spatial_comparisons, "Cluster-L1_vs_L2", "Cluster-L2_vs_L3")
    temporal_order = _convergence_summary(temporal_comparisons, "dt0.5_vs_dt0.25", "dt0.25_vs_dt0.125")

    spatial_uncertainties = {
        "temperature_c": _pointwise_uncertainty(
            results[spatial_specs[0][0]], results[spatial_specs[1][0]], results[spatial_specs[2][0]],
            "temperature_c", *[spec[0] for spec in spatial_specs],
        ),
        "moisture_kg_kg": _pointwise_uncertainty(
            results[spatial_specs[0][0]], results[spatial_specs[1][0]], results[spatial_specs[2][0]],
            "moisture_kg_kg", *[spec[0] for spec in spatial_specs],
        ),
    }
    temporal_uncertainties = {
        "temperature_c": _pointwise_uncertainty(
            results[temporal_specs[0][0]], results[temporal_specs[1][0]], results[temporal_specs[2][0]],
            "temperature_c", *[spec[0] for spec in temporal_specs],
        ),
        "moisture_kg_kg": _pointwise_uncertainty(
            results[temporal_specs[0][0]], results[temporal_specs[1][0]], results[temporal_specs[2][0]],
            "moisture_kg_kg", *[spec[0] for spec in temporal_specs],
        ),
    }

    production_candidates: List[Dict[str, Any]] = []
    for space_index, (space_label, _, _) in enumerate(spatial_specs):
        for time_index, (time_label, _, _) in enumerate(temporal_specs):
            # The first tested level uses the coarse Richardson estimate; the
            # finest tested level uses the fine estimate.
            space_uncertainty_key = "coarse_remaining_error" if space_index == 0 else "fine_remaining_error"
            time_uncertainty_key = "coarse_remaining_error" if time_index == 0 else "fine_remaining_error"
            combined_max = 0.0
            field_pass = {}
            for field in FIELDS:
                space_grid = spatial_uncertainties[field][space_uncertainty_key]
                time_grid = temporal_uncertainties[field][time_uncertainty_key]
                values = [
                    max(space_value or 0.0, time_value or 0.0)
                    for space_row, time_row in zip(space_grid, time_grid)
                    for space_value, time_value in zip(space_row, time_row)
                ]
                maximum = max(values)
                combined_max = max(combined_max, maximum)
                field_pass[field] = {
                    "max_estimated_uncertainty": maximum,
                    "target": ACCURACY_TARGETS[field],
                    "pass": maximum < ACCURACY_TARGETS[field],
                }
            production_candidates.append({
                "space_configuration": space_label,
                "time_configuration": time_label,
                "estimated_cost_steps_times_cells": results[space_label].grid.n_intervals * int(round(1800.0 / results[time_label].config.time_step_s)),
                "field_results": field_pass,
                "pass": all(item["pass"] for item in field_pass.values()),
                "combined_max_estimated_uncertainty": combined_max,
            })
    passing_candidates = [candidate for candidate in production_candidates if candidate["pass"]]
    passing_candidates.sort(key=lambda candidate: candidate["estimated_cost_steps_times_cells"])
    selected = passing_candidates[0] if passing_candidates else None

    reference = results[temporal_specs[-1][0]]
    criterion = _criterion_summary(
        reference,
        spatial_uncertainties,
        temporal_uncertainties,
        selected["space_configuration"] if selected else spatial_specs[-1][0],
        selected["time_configuration"] if selected else temporal_specs[-1][0],
    )
    cases = {label: _case_summary(result, runtimes[label]) for label, result in results.items()}
    base_payload: Dict[str, Any] = {
        "status": "COMPLETED",
        "code_commit": code_commit,
        "python": platform.python_version(),
        "input_hashes": input_hashes,
        "scope": {
            "full_horizon_s": "0..1800; formal output times 1..1800",
            "full_grid": "1800 x 21",
            "paper_table_points": "7 x 5",
            "cluster_power": 2.0,
            "official_output_positions_m": list(FULL_POSITIONS_M),
            "accuracy_criterion": "TEAM_NUMERICAL_CRITERION: estimated uncertainty < 5e-5 in each field output unit",
            "rounding_is_auxiliary": True,
        },
        "cases": cases,
        "production_candidates": production_candidates,
        "selected_lowest_cost_passing_candidate": selected,
        "candidate_count_passing": len(passing_candidates),
        "spatial_comparisons": spatial_comparisons,
        "temporal_comparisons": temporal_comparisons,
        "spatial_observed_order_and_richardson": spatial_order,
        "temporal_observed_order_and_richardson": temporal_order,
        "criterion_reference": criterion,
        "runtime_seconds": time.perf_counter() - started,
        "candidate_workbook_generated": False,
    }
    spatial_payload = {
        "experiment_id": "EXP-Q1-FULL-SPATIAL",
        **base_payload,
        "scope": {**base_payload["scope"], "comparison": "Cluster-L1/base320 vs L2/base640 vs L3/base1280 at fixed BDF2 dt=0.125 s"},
        "uncertainty": spatial_uncertainties,
    }
    temporal_payload = {
        "experiment_id": "EXP-Q1-FULL-TEMPORAL",
        **base_payload,
        "scope": {**base_payload["scope"], "comparison": "Cluster-L3/base1280 BDF2 dt=0.5 vs 0.25 vs 0.125 s"},
        "uncertainty": temporal_uncertainties,
    }
    _write_experiment(
        "EXP-Q1-FULL-SPATIAL",
        spatial_payload,
        "Full-horizon spatial convergence for clustered conservative radial FVM with BDF2. No workbook was generated.",
    )
    _write_experiment(
        "EXP-Q1-FULL-TEMPORAL",
        temporal_payload,
        "Full-horizon temporal convergence for clustered conservative radial FVM with BDF2. No workbook was generated.",
    )
    print(json.dumps({
        "status": base_payload["status"],
        "selected_candidate": selected,
        "criterion_pass": criterion["pass"],
        "spatial_max_fine_uncertainty": {field: spatial_uncertainties[field]["maximum_fine_remaining_error"] for field in FIELDS},
        "temporal_max_fine_uncertainty": {field: temporal_uncertainties[field]["maximum_fine_remaining_error"] for field in FIELDS},
        "surface_uncertainty": {field: criterion["fields"][field]["surface_uncertainty_by_time"] for field in FIELDS},
        "runtime_seconds": base_payload["runtime_seconds"],
    }, ensure_ascii=False, indent=2))
    return 0 if selected and criterion["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
