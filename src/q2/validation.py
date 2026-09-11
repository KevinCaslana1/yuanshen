"""Auditable metrics for Q2 numerical validation experiments."""

from __future__ import annotations

import math
from typing import Dict, Iterable, Mapping, Sequence

from .solver import Q2RunResult, summarize_picard


def _snapshot_error(test, reference) -> Dict[str, float]:
    temp_errors = []
    moisture_errors = []
    for test_temperature, reference_temperature in zip(test[0], reference[0]):
        temp_errors.append(abs(test_temperature - reference_temperature))
    for test_moisture, reference_moisture in zip(test[1], reference[1]):
        moisture_errors.append(abs(test_moisture - reference_moisture))
    return {
        "temperature_linf_K": max(temp_errors, default=0.0),
        "temperature_l2_rms_K": math.sqrt(sum(value * value for value in temp_errors) / max(1, len(temp_errors))),
        "moisture_linf_kg_kg": max(moisture_errors, default=0.0),
        "moisture_l2_rms_kg_kg": math.sqrt(sum(value * value for value in moisture_errors) / max(1, len(moisture_errors))),
    }


def compare_results(test: Q2RunResult, reference: Q2RunResult) -> Dict[str, float]:
    common = sorted(set(test.snapshots).intersection(reference.snapshots))
    if not common:
        raise ValueError("comparison requires common recorded snapshots")
    metrics = [_snapshot_error(test.snapshots[key], reference.snapshots[key]) for key in common]
    result = {"common_snapshot_count": len(common)}
    for key in metrics[0]:
        result[key] = max(row[key] for row in metrics)
    result["temperature_l2_time_rms_K"] = math.sqrt(sum(row["temperature_l2_rms_K"] ** 2 for row in metrics) / len(metrics))
    result["moisture_l2_time_rms_kg_kg"] = math.sqrt(sum(row["moisture_l2_rms_kg_kg"] ** 2 for row in metrics) / len(metrics))
    return result


def observed_orders(error_by_level: Mapping[float, float]) -> Dict[str, float]:
    levels = sorted(error_by_level, reverse=True)
    result = {}
    for left, right in zip(levels, levels[1:]):
        if error_by_level[left] <= 0 or error_by_level[right] <= 0:
            result[f"{left:g}_to_{right:g}"] = float("nan")
        else:
            result[f"{left:g}_to_{right:g}"] = math.log(error_by_level[left] / error_by_level[right]) / math.log(left / right)
    return result


def diagnostics_metrics(result: Q2RunResult) -> Dict[str, float]:
    if result.diagnostic_summary:
        return dict(result.diagnostic_summary)
    if not result.diagnostics:
        return {"steps": 0}
    rows = result.diagnostics
    return {
        **summarize_picard(result),
        "temperature_boundary_residual_max_w_m2": max(abs(row.surface_heat_boundary_residual_w_m2) for row in rows),
        "moisture_boundary_residual_max_kg_m2_s": max(abs(row.surface_moisture_boundary_residual_kg_m2_s) for row in rows),
        "mass_step_residual_max": max(abs(row.mass_step_residual) for row in rows),
        "heat_step_residual_max_j": max(abs(row.heat_step_residual_j) for row in rows),
        "temperature_linear_residual_max": max(row.temperature_linear_residual for row in rows),
        "moisture_linear_residual_max": max(row.moisture_linear_residual for row in rows),
    }


def property_range_metrics(result: Q2RunResult) -> Dict[str, float]:
    if result.diagnostic_summary:
        return {key: result.diagnostic_summary[key] for key in ("rho_min", "rho_max", "cp_min", "cp_max", "k_min", "k_max", "D_min", "D_max")}
    if not result.diagnostics:
        return {}
    keys = ("rho", "cp", "k", "D")
    return {f"{key}_min": min(row.property_min[key] for row in result.diagnostics) for key in keys} | {f"{key}_max": max(row.property_max[key] for row in result.diagnostics) for key in keys}


def point_values(result: Q2RunResult, time_s: float, radii_cm: Iterable[float]) -> Dict[str, Dict[str, float]]:
    temperature, moisture = result.snapshot_at(time_s)
    output = {}
    for radius_cm in radii_cm:
        index = min(range(len(result.grid.nodes_m)), key=lambda i: abs(result.grid.nodes_m[i] * 100.0 - radius_cm))
        output[f"{radius_cm:g}"] = {
            "temperature_K": temperature[index], "temperature_C": temperature[index] - 273.15,
            "moisture_kg_kg": moisture[index], "grid_radius_cm": result.grid.nodes_m[index] * 100.0,
        }
    return output


def exact_node_positions(result: Q2RunResult, radii_cm: Sequence[float], tolerance_cm: float = 1e-10) -> bool:
    nodes = [value * 100.0 for value in result.grid.nodes_m]
    return all(min(abs(node - radius) for node in nodes) <= tolerance_cm for radius in radii_cm)
