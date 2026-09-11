"""Diagnose Q1 discretization error without generating a deliverable workbook.

This is the numerical-convergence diagnosis stage. It reruns the already
authorized M1 configurations, compares identical physical times and output
positions, computes norms/order/Richardson estimates, and writes compact error
localization SVG plots plus JSON evidence.
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


OUTPUT_DIR = ROOT / "experiments" / "EXP-Q1-NUM-DIAG"
FULL_TIMES_S = tuple(range(1, 1801))
FULL_POSITIONS_M = tuple(index * 0.001 for index in range(21))
PAPER_TIMES_S = (100, 300, 600, 900, 1200, 1500, 1800)
PAPER_POSITIONS_M = (0.0, 0.005, 0.01, 0.015, 0.02)
FIELDS = ("temperature_c", "moisture_kg_kg")


def _config(n_intervals: int, time_step_s: float) -> Q1RunConfig:
    return Q1RunConfig(
        end_time_s=1800.0,
        time_step_s=time_step_s,
        n_intervals=n_intervals,
        interpolation="linear",
        surface_boundary="robin",
    )


def _run(n_intervals: int, time_step_s: float) -> Q1Result:
    config = _config(n_intervals, time_step_s)
    boundary = BoundaryProvider.from_attachment1(ROOT / config.input_path)
    return run_m1(config, boundary, DEFAULT_PARAMETERS)


def _time_indices(result: Q1Result, times_s: Sequence[int]) -> Tuple[int, ...]:
    indices = tuple(round(time_s / result.config.time_step_s) for time_s in times_s)
    if any(
        index >= len(result.times_s) or abs(result.times_s[index] - time_s) > 1.0e-9
        for index, time_s in zip(indices, times_s)
    ):
        raise ValueError("result history does not contain all requested physical times")
    return indices


def _space_indices(result: Q1Result, positions_m: Sequence[float]) -> Tuple[int, ...]:
    indices = tuple(round(position / result.grid.dr_m) for position in positions_m)
    if any(index < 0 or index > result.grid.n_intervals for index in indices):
        raise ValueError("requested output position is outside the solver grid")
    if any(
        abs(index * result.grid.dr_m - position) > 1.0e-12
        for index, position in zip(indices, positions_m)
    ):
        raise ValueError("solver grid is not exactly aligned with the output positions")
    return indices


def _field_rows(
    result: Q1Result,
    field: str,
    times_s: Sequence[int],
    positions_m: Sequence[float],
) -> List[List[float]]:
    time_indices = _time_indices(result, times_s)
    space_indices = _space_indices(result, positions_m)
    if field == "temperature_c":
        return [
            [result.temperatures_k[time_index][space_index] - 273.15 for space_index in space_indices]
            for time_index in time_indices
        ]
    if field == "moisture_kg_kg":
        return [
            [result.moistures_kg_kg[time_index][space_index] for space_index in space_indices]
            for time_index in time_indices
        ]
    raise ValueError(f"unknown field: {field}")


def _differences(first: Sequence[Sequence[float]], second: Sequence[Sequence[float]]) -> List[List[float]]:
    return [
        [abs(left - right) for left, right in zip(first_row, second_row)]
        for first_row, second_row in zip(first, second)
    ]


def _raw_norms(
    differences: Sequence[Sequence[float]],
    times_s: Sequence[int],
    positions_m: Sequence[float],
) -> Dict[str, Any]:
    values = [value for row in differences for value in row]
    squared_sum = sum(value * value for value in values)
    max_value = max(values)
    max_flat_index = values.index(max_value)
    row_index, column_index = divmod(max_flat_index, len(positions_m))
    return {
        "linf": max_value,
        "mean_abs": sum(values) / len(values),
        "rmse": math.sqrt(squared_sum / len(values)),
        "max_location": {
            "time_s": times_s[row_index],
            "distance_cm": positions_m[column_index] * 100.0,
        },
        "cell_count": len(values),
    }


def _rounded_disagreement(
    first: Sequence[Sequence[float]],
    second: Sequence[Sequence[float]],
    times_s: Sequence[int],
    positions_m: Sequence[float],
) -> Dict[str, Any]:
    # Decimal ROUND_HALF_UP is intentionally used to match official output
    # formatting; import locally to keep the raw-norm code straightforward.
    from decimal import Decimal, ROUND_HALF_UP

    quantum = Decimal("0.0001")
    locations: List[Dict[str, Any]] = []
    different = 0
    for row_index, (first_row, second_row) in enumerate(zip(first, second)):
        for column_index, (left, right) in enumerate(zip(first_row, second_row)):
            left_rounded = Decimal(str(left)).quantize(quantum, rounding=ROUND_HALF_UP)
            right_rounded = Decimal(str(right)).quantize(quantum, rounding=ROUND_HALF_UP)
            if left_rounded != right_rounded:
                different += 1
                if len(locations) < 20:
                    locations.append(
                        {
                            "time_s": times_s[row_index],
                            "distance_cm": positions_m[column_index] * 100.0,
                            "first_rounded": str(left_rounded),
                            "second_rounded": str(right_rounded),
                            "raw_abs_difference": abs(left - right),
                        }
                    )
    return {
        "different_count": different,
        "total_cells": len(times_s) * len(positions_m),
        "different_fraction": different / (len(times_s) * len(positions_m)),
        "different_locations_first_20": locations,
    }


def _region_metrics(
    first: Q1Result,
    second: Q1Result,
    field: str,
    times_s: Sequence[int],
    positions_m: Sequence[float],
) -> Dict[str, Any]:
    first_rows = _field_rows(first, field, times_s, positions_m)
    second_rows = _field_rows(second, field, times_s, positions_m)
    differences = _differences(first_rows, second_rows)
    return {
        "raw": _raw_norms(differences, times_s, positions_m),
        "rounded": _rounded_disagreement(first_rows, second_rows, times_s, positions_m),
    }


def _comparison(first: Q1Result, second: Q1Result, first_label: str, second_label: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"first": first_label, "second": second_label, "fields": {}}
    regions = {
        "full_grid": (FULL_TIMES_S, FULL_POSITIONS_M),
        "center": (FULL_TIMES_S, (0.0,)),
        "surface": (FULL_TIMES_S, (0.02,)),
        "paper_table_points": (PAPER_TIMES_S, PAPER_POSITIONS_M),
    }
    for field in FIELDS:
        result["fields"][field] = {
            region: _region_metrics(first, second, field, times_s, positions_m)
            for region, (times_s, positions_m) in regions.items()
        }
    return result


def _localization(first: Q1Result, second: Q1Result, label: str) -> Dict[str, Any]:
    output: Dict[str, Any] = {"comparison": label, "fields": {}}
    for field in FIELDS:
        first_rows = _field_rows(first, field, FULL_TIMES_S, FULL_POSITIONS_M)
        second_rows = _field_rows(second, field, FULL_TIMES_S, FULL_POSITIONS_M)
        differences = _differences(first_rows, second_rows)
        max_by_time = [max(row) for row in differences]
        mean_by_time = [sum(row) / len(row) for row in differences]
        max_by_radius = [max(row[column] for row in differences) for column in range(len(FULL_POSITIONS_M))]
        mean_by_radius = [
            sum(row[column] for row in differences) / len(differences)
            for column in range(len(FULL_POSITIONS_M))
        ]
        global_max = max(max_by_time)
        global_mean = sum(value for row in differences for value in row) / (len(FULL_TIMES_S) * len(FULL_POSITIONS_M))
        surface_band_columns = [index for index, position in enumerate(FULL_POSITIONS_M) if position >= 0.018]
        surface_band_sum = sum(row[index] for row in differences for index in surface_band_columns)
        total_sum = sum(value for row in differences for value in row)
        early_indices = [index for index, time_s in enumerate(FULL_TIMES_S) if time_s <= 300]
        early_max = max(max_by_time[index] for index in early_indices)
        peak_time_index = max_by_time.index(global_max)
        peak_radius_index = max_by_radius.index(global_max)
        output["fields"][field] = {
            "max_abs_by_time": [
                {"time_s": time_s, "max_abs": value, "mean_abs": mean_by_time[index]}
                for index, (time_s, value) in enumerate(zip(FULL_TIMES_S, max_by_time))
            ],
            "max_abs_by_radius": [
                {"distance_cm": position * 100.0, "max_abs": value, "mean_abs": mean_by_radius[index]}
                for index, (position, value) in enumerate(zip(FULL_POSITIONS_M, max_by_radius))
            ],
            "global_max_location": {
                "time_s": FULL_TIMES_S[peak_time_index],
                "distance_cm": FULL_POSITIONS_M[peak_radius_index] * 100.0,
                "max_abs": global_max,
            },
            "early_t_le_300s_max_abs": early_max,
            "early_max_fraction_of_global": early_max / global_max if global_max else 0.0,
            "surface_band_r_ge_1_8cm_mean_abs_share": surface_band_sum / total_sum if total_sum else 0.0,
            "full_grid_mean_abs": global_mean,
        }
    return output


def _observed_order(coarse: float, fine: float) -> float | None:
    if coarse <= 0.0 or fine <= 0.0:
        return None
    return math.log(coarse / fine, 2.0)


def _richardson(fine_difference: float, order: float | None) -> float | None:
    if order is None or order <= 0.0 or abs(2.0**order - 1.0) < 1.0e-14:
        return None
    return fine_difference / (2.0**order - 1.0)


def _convergence_summary(comparisons: Dict[str, Dict[str, Any]], coarse_key: str, fine_key: str) -> Dict[str, Any]:
    summary: Dict[str, Any] = {}
    for field in FIELDS:
        summary[field] = {}
        for region in ("full_grid", "center", "surface", "paper_table_points"):
            summary[field][region] = {}
            for norm in ("linf", "mean_abs", "rmse"):
                coarse_error = comparisons[coarse_key]["fields"][field][region]["raw"][norm]
                fine_error = comparisons[fine_key]["fields"][field][region]["raw"][norm]
                order = _observed_order(coarse_error, fine_error)
                summary[field][region][norm] = {
                    "coarse_error": coarse_error,
                    "fine_error": fine_error,
                    "observed_order": order,
                    "richardson_remaining_error": _richardson(fine_error, order),
                }
    return summary


def _svg_line_plot(path: Path, x_values: Sequence[float], series: Dict[str, Sequence[float]], x_label: str, y_label: str) -> None:
    width, height = 920, 480
    left, right, top, bottom = 80, 30, 35, 70
    plot_width, plot_height = width - left - right, height - top - bottom
    flat_values = [value for values in series.values() for value in values]
    y_max = max(flat_values) if flat_values else 1.0
    y_max = y_max * 1.08 if y_max > 0.0 else 1.0
    x_min, x_max = min(x_values), max(x_values)

    def x_map(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * plot_width if x_max > x_min else left + plot_width / 2

    def y_map(value: float) -> float:
        return top + plot_height - value / y_max * plot_height

    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd"]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" stroke="#333"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#333"/>',
        f'<text x="{width / 2}" y="{height - 20}" text-anchor="middle" font-family="Arial" font-size="15">{x_label}</text>',
        f'<text x="18" y="{height / 2}" text-anchor="middle" transform="rotate(-90 18 {height / 2})" font-family="Arial" font-size="15">{y_label}</text>',
        f'<text x="{width / 2}" y="20" text-anchor="middle" font-family="Arial" font-size="16">Q1 error localization</text>',
    ]
    for tick in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = top + plot_height * (1.0 - tick)
        value = y_max * tick
        lines.append(f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" y2="{y:.2f}" stroke="#e5e5e5"/>')
        lines.append(f'<text x="{left - 8}" y="{y + 4:.2f}" text-anchor="end" font-family="Arial" font-size="11">{value:.3g}</text>')
    for index, (label, values) in enumerate(series.items()):
        points = " ".join(f"{x_map(x):.2f},{y_map(y):.2f}" for x, y in zip(x_values, values))
        y_legend = top + 18 + index * 18
        lines.append(f'<polyline points="{points}" fill="none" stroke="{colors[index % len(colors)]}" stroke-width="2"/>')
        lines.append(f'<line x1="{width - 210}" y1="{y_legend - 5}" x2="{width - 185}" y2="{y_legend - 5}" stroke="{colors[index % len(colors)]}" stroke-width="3"/>')
        lines.append(f'<text x="{width - 178}" y="{y_legend}" font-family="Arial" font-size="12">{label}</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_plots(localizations: Dict[str, Dict[str, Any]]) -> List[str]:
    paths: List[str] = []
    for field, field_label in (("temperature_c", "temperature"), ("moisture_kg_kg", "moisture")):
        time_series: Dict[str, Sequence[float]] = {}
        radius_series: Dict[str, Sequence[float]] = {}
        for key, localization in localizations.items():
            time_series[key] = [item["max_abs"] for item in localization["fields"][field]["max_abs_by_time"]]
            radius_series[key] = [item["max_abs"] for item in localization["fields"][field]["max_abs_by_radius"]]
        time_path = OUTPUT_DIR / f"{field_label}_error_by_time.svg"
        radius_path = OUTPUT_DIR / f"{field_label}_error_by_radius.svg"
        _svg_line_plot(time_path, [float(value) for value in FULL_TIMES_S], time_series, "time (s)", "max absolute error")
        _svg_line_plot(radius_path, [value * 100.0 for value in FULL_POSITIONS_M], radius_series, "distance from center (cm)", "max absolute error")
        paths.extend([str(time_path.relative_to(ROOT)), str(radius_path.relative_to(ROOT))])
    return paths


def main() -> int:
    started = time.perf_counter()
    runs = {
        "N80_dt0.25": _run(80, 0.25),
        "N160_dt0.25": _run(160, 0.25),
        "N320_dt0.25": _run(320, 0.25),
        "N320_dt1.0": _run(320, 1.0),
        "N320_dt0.5": _run(320, 0.5),
    }
    spatial_comparisons = {
        "N80_vs_N160": _comparison(runs["N80_dt0.25"], runs["N160_dt0.25"], "N80_dt0.25", "N160_dt0.25"),
        "N160_vs_N320": _comparison(runs["N160_dt0.25"], runs["N320_dt0.25"], "N160_dt0.25", "N320_dt0.25"),
    }
    temporal_comparisons = {
        "dt1.0_vs_dt0.5": _comparison(runs["N320_dt1.0"], runs["N320_dt0.5"], "N320_dt1.0", "N320_dt0.5"),
        "dt0.5_vs_dt0.25": _comparison(runs["N320_dt0.5"], runs["N320_dt0.25"], "N320_dt0.5", "N320_dt0.25"),
    }
    localizations = {
        "space_N160_vs_N320": _localization(runs["N160_dt0.25"], runs["N320_dt0.25"], "N160_dt0.25 -> N320_dt0.25"),
        "time_dt0.5_vs_dt0.25": _localization(runs["N320_dt0.5"], runs["N320_dt0.25"], "N320_dt0.5 -> N320_dt0.25"),
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plot_paths = _write_plots(localizations)
    payload: Dict[str, Any] = {
        "experiment_id": "EXP-Q1-NUM-DIAG",
        "status": "COMPLETED",
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "input_hashes": {"A题/附件/附件1.xlsx": "7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7"},
        "scope": {
            "full_grid": {"times_s": "1..1800", "positions_cm": "0.0..2.0 step 0.1", "cells_per_field": 37800},
            "paper_table_points": {"times_s": list(PAPER_TIMES_S), "positions_cm": [value * 100.0 for value in PAPER_POSITIONS_M], "cells_per_field": 35},
            "same_physical_times_and_positions": True,
        },
        "configs": {
            key: {
                "n_intervals": result.config.n_intervals,
                "dr_m": result.grid.dr_m,
                "time_step_s": result.config.time_step_s,
                "end_time_s": result.config.end_time_s,
                "picard_tolerance": result.config.picard_tolerance,
                "picard_max_iterations": result.config.picard_max_iterations,
            }
            for key, result in runs.items()
        },
        "spatial_comparisons": spatial_comparisons,
        "temporal_comparisons": temporal_comparisons,
        "spatial_observed_order_and_richardson": _convergence_summary(spatial_comparisons, "N80_vs_N160", "N160_vs_N320"),
        "temporal_observed_order_and_richardson": _convergence_summary(temporal_comparisons, "dt1.0_vs_dt0.5", "dt0.5_vs_dt0.25"),
        "error_localization": localizations,
        "artifact_paths": ["experiments/EXP-Q1-NUM-DIAG/metrics.json", *plot_paths],
        "runtime_seconds": time.perf_counter() - started,
    }
    (OUTPUT_DIR / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "config.json").write_text(
        json.dumps(
            {
                "experiment_id": payload["experiment_id"],
                "code_commit": payload["code_commit"],
                "input_hashes": payload["input_hashes"],
                "configs": payload["configs"],
                "scope": payload["scope"],
                "artifact_paths": payload["artifact_paths"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "notes.md").write_text(
        "# EXP-Q1-NUM-DIAG\n\n"
        "Raw L∞/mean-absolute/RMSE norms, observed order, Richardson-style remaining-error estimates, "
        "and time/radius localization for the complete Q1 output grid. No workbook was generated.\n\n"
        f"Status: `{payload['status']}`\nRuntime: `{payload['runtime_seconds']:.6f} s`\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("Evidence written to experiments/EXP-Q1-NUM-DIAG")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
