"""Audit Q1 surface-error cancellation and separated BE convergence.

This script intentionally uses the uniform-grid backward-Euler ``run_m1``
solver.  It is an independent diagnostic of the frozen Q1 production result;
it does not write a workbook or touch ``A题/`` or ``figures/q1/final/``.
All CSV floating-point values are emitted with ``repr`` so that no rounding is
performed before error calculation or storage.
"""

from __future__ import annotations

import csv
import gc
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q1.config import DEFAULT_PARAMETERS, Q1RunConfig
from src.q1.inputs import BoundaryProvider
from src.q1.model import arithmetic_face_values, radial_control_volume_factors
from src.q1.solver import Q1Result, run_m1


SOURCE_RELATIVE = Path("A题") / "附件" / "附件1.xlsx"
SURFACE_DIR = ROOT / "experiments" / "EXP-Q1-SURFACE-DECAY"
TEMPORAL_DIR = ROOT / "experiments" / "EXP-003"
SPATIAL_DIR = ROOT / "experiments" / "EXP-004"

SURFACE_POSITIONS = (
    ("near_surface_1.9cm", 0.019),
    ("surface_2.0cm", 0.02),
)
CONVERGENCE_POSITIONS = (
    ("surface", 0.02),
    ("r_1.5cm", 0.015),
    ("r_1.0cm", 0.01),
    ("center", 0.0),
)
ALL_POSITIONS = SURFACE_POSITIONS + CONVERGENCE_POSITIONS[1:]


@dataclass(frozen=True)
class CaseData:
    label: str
    n_intervals: int
    dt_s: float
    end_time_s: float
    dr_m: float
    times_s: tuple[float, ...]
    profiles: dict[str, tuple[float, ...]]
    runtime_seconds: float

    def value(self, time_s: float, position_m: float) -> float:
        index = round(float(time_s) / self.dt_s)
        if index < 0 or index >= len(self.times_s) or abs(self.times_s[index] - time_s) > 1.0e-10:
            raise ValueError(f"time is not aligned in {self.label}: {time_s}")
        position_index = round(position_m / self.dr_m)
        if abs(position_index * self.dr_m - position_m) > 1.0e-12:
            raise ValueError(f"position is not aligned in {self.label}: {position_m}")
        position_label = next(
            label for label, candidate in ALL_POSITIONS if abs(candidate - position_m) <= 1.0e-15
        )
        return self.profiles[position_label][index]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _code_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _csv_value(value: Any) -> str:
    if isinstance(value, float):
        return repr(value)
    return str(value)


def _write_csv(path: Path, headers: Sequence[str], rows: Iterable[Sequence[Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(headers)
        for row in rows:
            writer.writerow([_csv_value(value) for value in row])


def _config(n_intervals: int, dt_s: float, end_time_s: float) -> Q1RunConfig:
    return Q1RunConfig(
        end_time_s=end_time_s,
        time_step_s=dt_s,
        n_intervals=n_intervals,
        interpolation="linear",
        surface_boundary="robin",
    )


def _run_case(
    label: str,
    n_intervals: int,
    dt_s: float,
    end_time_s: float,
    boundary: BoundaryProvider,
) -> CaseData:
    started = time.perf_counter()
    result = run_m1(_config(n_intervals, dt_s, end_time_s), boundary, DEFAULT_PARAMETERS)
    profiles: dict[str, tuple[float, ...]] = {}
    for position_label, position_m in ALL_POSITIONS:
        position_index = round(position_m / result.grid.dr_m)
        if abs(position_index * result.grid.dr_m - position_m) > 1.0e-12:
            raise ValueError(f"requested position is not a node for {label}: {position_m}")
        profiles[position_label] = tuple(row[position_index] for row in result.moistures_kg_kg)
    case = CaseData(
        label=label,
        n_intervals=result.grid.n_intervals,
        dt_s=result.config.time_step_s,
        end_time_s=result.config.end_time_s,
        dr_m=result.grid.dr_m,
        times_s=tuple(result.times_s),
        profiles=profiles,
        runtime_seconds=time.perf_counter() - started,
    )
    del result
    gc.collect()
    print(
        f"completed {label}: n={case.n_intervals}, dr={case.dr_m * 100.0!r} cm, "
        f"dt={case.dt_s!r} s, end={case.end_time_s!r} s, runtime={case.runtime_seconds:.3f} s"
    )
    return case


def _run_trace_case(
    n_intervals: int,
    dt_s: float,
    end_time_s: float,
    boundary: BoundaryProvider,
) -> tuple[Q1Result, list[dict[str, float | int]], float]:
    started = time.perf_counter()
    trace: list[dict[str, float | int]] = []
    result = run_m1(_config(n_intervals, dt_s, end_time_s), boundary, DEFAULT_PARAMETERS, diagnostics=trace)
    return result, trace, time.perf_counter() - started


def _error_metrics(
    test_values: Sequence[float],
    reference_values: Sequence[float],
    times_s: Sequence[float],
) -> dict[str, float]:
    signed = [test - reference for test, reference in zip(test_values, reference_values)]
    absolute = [abs(value) for value in signed]

    def norms(indices: Sequence[int]) -> tuple[float, float]:
        selected = [absolute[index] for index in indices]
        if not selected:
            return 0.0, 0.0
        return max(selected), math.sqrt(sum(value * value for value in selected) / len(selected))

    all_indices = list(range(len(times_s)))
    tail_indices = [index for index, value in enumerate(times_s) if value >= 60.0 - 1.0e-12]
    linf, l2 = norms(all_indices)
    tail_linf, tail_l2 = norms(tail_indices)
    return {
        "linf": linf,
        "l2_rms": l2,
        "tail_60s_linf": tail_linf,
        "tail_60s_l2_rms": tail_l2,
        "signed_min": min(signed),
        "signed_max": max(signed),
        "signed_final": signed[-1],
    }


def _compare_cases(
    test: CaseData,
    reference: CaseData,
    positions: Sequence[tuple[str, float]],
    csv_path: Path | None = None,
) -> dict[str, Any]:
    headers = (
        "test_case",
        "reference_case",
        "time_s",
        "position_label",
        "position_cm",
        "C_ref_kg_kg",
        "C_test_kg_kg",
        "signed_error",
        "absolute_error",
    )
    handle = csv_path.open("w", encoding="utf-8", newline="") if csv_path is not None else None
    writer = csv.writer(handle, lineterminator="\n") if handle is not None else None
    if writer is not None:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        writer.writerow(headers)

    values_by_position: dict[str, list[float]] = {label: [] for label, _ in positions}
    times = list(test.times_s)
    for index, time_s in enumerate(times):
        reference_index = round(time_s / reference.dt_s)
        if abs(reference.times_s[reference_index] - time_s) > 1.0e-10:
            raise ValueError(f"comparison time mismatch: {test.label} vs {reference.label} at {time_s}")
        for position_label, position_m in positions:
            test_value = test.profiles[position_label][index]
            reference_value = reference.profiles[position_label][reference_index]
            signed_error = test_value - reference_value
            absolute_error = abs(signed_error)
            values_by_position[position_label].append(signed_error)
            if writer is not None:
                writer.writerow([
                    test.label,
                    reference.label,
                    _csv_value(float(time_s)),
                    position_label,
                    _csv_value(position_m * 100.0),
                    _csv_value(reference_value),
                    _csv_value(test_value),
                    _csv_value(signed_error),
                    _csv_value(absolute_error),
                ])
    if handle is not None:
        handle.close()

    by_position = {
        label: _error_metrics(
            [test.profiles[label][index] for index in range(len(times))],
            [reference.profiles[label][round(time_s / reference.dt_s)] for time_s in times],
            times,
        )
        for label, _ in positions
    }
    all_signed = [value for values in values_by_position.values() for value in values]
    all_absolute = [abs(value) for value in all_signed]
    tail_indices = [index for index, value in enumerate(times) if value >= 60.0 - 1.0e-12]
    aggregate = {
        "linf": max(all_absolute, default=0.0),
        "l2_rms": math.sqrt(sum(value * value for value in all_signed) / len(all_signed)) if all_signed else 0.0,
        "tail_60s_linf": max((abs(values_by_position[label][index]) for label in values_by_position for index in tail_indices), default=0.0),
        "tail_60s_l2_rms": math.sqrt(
            sum(values_by_position[label][index] ** 2 for label in values_by_position for index in tail_indices)
            / max(1, len(values_by_position) * len(tail_indices))
        ),
        "signed_min": min(all_signed, default=0.0),
        "signed_max": max(all_signed, default=0.0),
    }
    return {
        "test_case": test.label,
        "reference_case": reference.label,
        "test_dt_s": test.dt_s,
        "reference_dt_s": reference.dt_s,
        "test_dr_cm": test.dr_m * 100.0,
        "reference_dr_cm": reference.dr_m * 100.0,
        "sample_count_per_position": len(times),
        "by_position": by_position,
        "aggregate": aggregate,
    }


def _adjacent_order_rows(
    comparison_by_level: dict[str, dict[str, Any]],
    levels: Sequence[str],
    level_values: dict[str, float],
    value_name: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for left, right in zip(levels, levels[1:]):
        row: dict[str, Any] = {
            "coarser_level": left,
            "finer_level": right,
            "coarser_value": level_values[left],
            "finer_value": level_values[right],
        }
        for position_label, metrics in comparison_by_level[left]["by_position"].items():
            coarser_error = metrics[value_name]
            finer_error = comparison_by_level[right]["by_position"][position_label][value_name]
            row[position_label] = (
                math.log(coarser_error / finer_error, 2.0)
                if coarser_error > 0.0 and finer_error > 0.0
                else None
            )
        coarser_error = comparison_by_level[left]["aggregate"][value_name]
        finer_error = comparison_by_level[right]["aggregate"][value_name]
        row["aggregate"] = (
            math.log(coarser_error / finer_error, 2.0)
            if coarser_error > 0.0 and finer_error > 0.0
            else None
        )
        rows.append(row)
    return rows


def _find_zero_crossings(times_s: Sequence[float], signed_errors: Sequence[float]) -> dict[str, Any]:
    crossings: list[dict[str, Any]] = []
    exact_zeros: list[float] = []
    for left_index, (left_time, left_error) in enumerate(zip(times_s, signed_errors)):
        if left_error == 0.0:
            exact_zeros.append(left_time)
        if left_index + 1 >= len(times_s):
            continue
        right_time = times_s[left_index + 1]
        right_error = signed_errors[left_index + 1]
        if left_error * right_error < 0.0:
            crossing_time = left_time - left_error * (right_time - left_time) / (right_error - left_error)
            crossings.append({
                "bracket_s": [left_time, right_time],
                "linear_interpolated_time_s": crossing_time,
                "left_signed_error": left_error,
                "right_signed_error": right_error,
                "classification": "pointwise error zero-crossing / cancellation dip",
            })
    return {"crossings": crossings, "exact_zero_times_s": exact_zeros}


def _surface_rows(test: CaseData, reference: CaseData) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for time_s in range(1, 101):
        for position_label, position_m in SURFACE_POSITIONS:
            test_value = test.value(float(time_s), position_m)
            reference_value = reference.value(float(time_s), position_m)
            signed_error = test_value - reference_value
            rows.append({
                "time_s": float(time_s),
                "position_label": position_label,
                "radius_cm": position_m * 100.0,
                "C_ref_surface": reference_value,
                "C_test_surface": test_value,
                "signed_error": signed_error,
                "absolute_error": abs(signed_error),
            })
    return rows


def _write_surface_csvs(rows: Sequence[dict[str, Any]]) -> None:
    headers = (
        "time_s",
        "position_label",
        "radius_cm",
        "C_ref_surface",
        "C_test_surface",
        "signed_error",
        "absolute_error",
    )
    _write_csv(
        SURFACE_DIR / "surface_error_1_100s.csv",
        headers,
        ([
            row["time_s"],
            row["position_label"],
            row["radius_cm"],
            row["C_ref_surface"],
            row["C_test_surface"],
            row["signed_error"],
            row["absolute_error"],
        ] for row in rows),
    )
    _write_csv(
        SURFACE_DIR / "surface_signed_error_15_45s.csv",
        headers,
        ([
            row["time_s"],
            row["position_label"],
            row["radius_cm"],
            row["C_ref_surface"],
            row["C_test_surface"],
            row["signed_error"],
            row["absolute_error"],
        ] for row in rows if 15.0 <= row["time_s"] <= 45.0),
    )


def _plot_surface(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    by_position = {
        position_label: [row for row in rows if row["position_label"] == position_label]
        for position_label, _ in SURFACE_POSITIONS
    }
    plot_audit: dict[str, Any] = {"smoothing": False, "error_interpolation": False, "x_y_shift": False}
    signed_path = SURFACE_DIR / "signed_error_vs_time.svg"
    figure, axis = plt.subplots(figsize=(9.0, 5.2))
    for position_label, _ in SURFACE_POSITIONS:
        selected = by_position[position_label]
        axis.plot(
            [row["time_s"] for row in selected],
            [row["signed_error"] for row in selected],
            marker=".",
            linewidth=1.2,
            markersize=3.0,
            label=position_label.replace("_", " "),
        )
    axis.axhline(0.0, color="black", linewidth=0.8)
    axis.set_xlabel("time (s)")
    axis.set_ylabel("signed error e = C_test - C_ref (kg/kg)")
    axis.set_title("Q1 signed surface moisture error")
    axis.grid(True, alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(signed_path)
    figure.savefig(signed_path.with_suffix(".png"), dpi=180)
    plt.close(figure)

    masked_nonpositive: list[dict[str, Any]] = []
    absolute_path = SURFACE_DIR / "absolute_error_semilogy.svg"
    figure, axis = plt.subplots(figsize=(9.0, 5.2))
    for position_label, _ in SURFACE_POSITIONS:
        selected = by_position[position_label]
        masked_values = []
        for row in selected:
            value = row["absolute_error"]
            if value <= 0.0:
                masked_nonpositive.append({"time_s": row["time_s"], "position_label": position_label, "value": value})
                masked_values.append(math.nan)
            else:
                masked_values.append(value)
        axis.semilogy(
            [row["time_s"] for row in selected],
            masked_values,
            marker=".",
            linewidth=1.2,
            markersize=3.0,
            label=position_label.replace("_", " "),
        )
    axis.set_xlabel("time (s)")
    axis.set_ylabel("absolute error |C_test - C_ref| (kg/kg)")
    axis.set_title("Q1 absolute surface moisture error (semilogy)")
    axis.grid(True, which="both", alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(absolute_path)
    figure.savefig(absolute_path.with_suffix(".png"), dpi=180)
    plt.close(figure)
    plot_audit["semilogy_nonpositive_points_masked"] = masked_nonpositive
    plot_audit["clip_epsilon"] = None
    plot_audit["source_data"] = "surface_error_1_100s.csv"
    plot_audit["signed_plot"] = "signed_error_vs_time.svg"
    plot_audit["absolute_semilogy_plot"] = "absolute_error_semilogy.svg"
    return plot_audit


def _print_surface_table(rows: Sequence[dict[str, Any]]) -> None:
    print("\nRAW SIGNED ERROR TABLE: 15--45 s, 1 s spacing; no pre-error rounding")
    print("time_s\tradius_cm\tC_ref_surface\tC_test_surface\tsigned_error\tabsolute_error")
    for row in rows:
        if 15.0 <= row["time_s"] <= 45.0:
            print("\t".join(_csv_value(row[key]) for key in (
                "time_s", "radius_cm", "C_ref_surface", "C_test_surface", "signed_error", "absolute_error",
            )))
    print("\nSPOTLIGHT TIMES: 20, 25, 30, 35, 40 s")
    for row in rows:
        if row["time_s"] in {20.0, 25.0, 30.0, 35.0, 40.0}:
            print("\t".join(_csv_value(row[key]) for key in (
                "time_s", "position_label", "C_ref_surface", "C_test_surface", "signed_error", "absolute_error",
            )))


def _boundary_audit(
    boundary: BoundaryProvider,
    result: Q1Result,
    trace: Sequence[dict[str, float | int]],
) -> dict[str, Any]:
    parameters = DEFAULT_PARAMETERS
    integer_times = [float(time_s) for time_s in range(0, 61)]
    c_inf_values = [boundary.at(time_s)[1] for time_s in integer_times]
    increments = [right - left for left, right in zip(c_inf_values, c_inf_values[1:])]
    second_differences = [right - 2.0 * middle + left for left, middle, right in zip(c_inf_values, c_inf_values[1:], c_inf_values[2:])]
    raw_slope = (boundary.moistures_kg_kg[1] - boundary.moistures_kg_kg[0]) / (
        boundary.times_s[1] - boundary.times_s[0]
    )
    expected = [boundary.moistures_kg_kg[0] + raw_slope * time_s for time_s in integer_times]
    surface_volume = radial_control_volume_factors(result.grid)[-1]
    inner_radius = parameters.radius_m - 0.5 * result.grid.dr_m
    trace_rows: list[dict[str, Any]] = [{
        "time_s": 0.0,
        "step_dt_s": 0.0,
        "C_inf": boundary.at(0.0)[1],
        "D_surface": parameters.diffusivity_m2_s(result.moistures_kg_kg[0][-1]),
        "robin_flux": 0.0,
        "literal_one_sided_diffusive_flux": 0.0,
        "literal_diffusive_minus_robin": 0.0,
        "face_diffusive_flux": 0.0,
        "face_diffusive_minus_robin": 0.0,
        "surface_control_volume_balance": 0.0,
        "picard_iterations": 0,
        "picard_final_normalized_residual": 0.0,
        "temperature_matrix_residual_linf": 0.0,
        "moisture_matrix_residual_linf": 0.0,
        "time_step_residual_normalized": 0.0,
        "time_alignment_error_s": 0.0,
    }]
    for step_index, diagnostic in enumerate(trace, start=1):
        time_s = float(diagnostic["time_s"])
        result_index = round(time_s / result.config.time_step_s)
        old_surface = result.moistures_kg_kg[result_index - 1][-1]
        surface = result.moistures_kg_kg[result_index][-1]
        inner_node = result.moistures_kg_kg[result_index][-2]
        c_inf = float(diagnostic["moisture_environment_kg_kg"])
        d_surface = float(diagnostic["surface_diffusivity_m2_s"])
        robin_flux = parameters.mass_transfer_m_s * (surface - c_inf)
        literal_gradient_flux = -d_surface * (surface - inner_node) / result.grid.dr_m
        face_diffusivity = sum((
            parameters.diffusivity_m2_s(surface),
            parameters.diffusivity_m2_s(inner_node),
        )) / 2.0
        face_flux = -face_diffusivity * (surface - inner_node) / result.grid.dr_m
        storage_rate = surface_volume * (surface - old_surface) / result.config.time_step_s
        cv_balance = storage_rate - inner_radius * face_flux + parameters.radius_m * robin_flux
        temperature_scale = max(1.0, max(abs(value) for value in result.temperatures_k[result_index]))
        moisture_scale = max(1.0, max(abs(value) for value in result.moistures_kg_kg[result_index]))
        normalized_time_step_residual = max(
            float(diagnostic["temperature_matrix_residual_linf"]) / temperature_scale,
            float(diagnostic["moisture_matrix_residual_linf"]) / moisture_scale,
        )
        trace_rows.append({
            "time_s": time_s,
            "step_dt_s": float(diagnostic["step_dt_s"]),
            "C_inf": c_inf,
            "D_surface": d_surface,
            "robin_flux": robin_flux,
            "literal_one_sided_diffusive_flux": literal_gradient_flux,
            "literal_diffusive_minus_robin": literal_gradient_flux - robin_flux,
            "face_diffusive_flux": face_flux,
            "face_diffusive_minus_robin": face_flux - robin_flux,
            "surface_control_volume_balance": cv_balance,
            "picard_iterations": int(diagnostic["picard_iterations"]),
            "picard_final_normalized_residual": float(diagnostic["picard_final_normalized_residual"]),
            "temperature_matrix_residual_linf": float(diagnostic["temperature_matrix_residual_linf"]),
            "moisture_matrix_residual_linf": float(diagnostic["moisture_matrix_residual_linf"]),
            "time_step_residual_normalized": normalized_time_step_residual,
            "time_alignment_error_s": abs(time_s - step_index * result.config.time_step_s),
        })
    headers = tuple(trace_rows[0].keys())
    _write_csv(SURFACE_DIR / "boundary_solver_trace_0_60s.csv", headers, ([row[key] for key in headers] for row in trace_rows))

    iteration_counts = Counter(int(row["picard_iterations"]) for row in trace_rows[1:])
    transitions = [
        {"time_s": row["time_s"], "picard_iterations": row["picard_iterations"]}
        for previous, row in zip(trace_rows[1:], trace_rows[2:])
        if row["picard_iterations"] != previous["picard_iterations"]
    ]
    return {
        "interval": "0--60 s",
        "interpolation_method": boundary.method,
        "raw_points_used": [
            {"time_s": boundary.times_s[index], "C_inf": boundary.moistures_kg_kg[index]}
            for index in range(2)
        ],
        "raw_segment_slope_kg_kg_per_s": raw_slope,
        "C_inf_integer_sample_max_abs_second_difference": max((abs(value) for value in second_differences), default=0.0),
        "C_inf_integer_sample_max_abs_increment_deviation_from_first": max(
            (abs(value - increments[0]) for value in increments), default=0.0
        ),
        "C_inf_integer_sample_max_abs_error_from_raw_linear_segment": max(
            (abs(value - reference) for value, reference in zip(c_inf_values, expected)), default=0.0
        ),
        "dt_unique_s": sorted({row["step_dt_s"] for row in trace_rows[1:]}),
        "time_alignment_max_abs_error_s": max((row["time_alignment_error_s"] for row in trace_rows), default=0.0),
        "picard_iteration_counts": dict(sorted(iteration_counts.items())),
        "picard_iteration_transitions": transitions,
        "picard_final_normalized_residual_max": max(
            (row["picard_final_normalized_residual"] for row in trace_rows[1:]), default=0.0
        ),
        "temperature_matrix_residual_linf_max": max(
            (row["temperature_matrix_residual_linf"] for row in trace_rows[1:]), default=0.0
        ),
        "moisture_matrix_residual_linf_max": max(
            (row["moisture_matrix_residual_linf"] for row in trace_rows[1:]), default=0.0
        ),
        "time_step_residual_normalized_max": max(
            (row["time_step_residual_normalized"] for row in trace_rows[1:]), default=0.0
        ),
        "robin_check_15_45s": {
            "literal_one_sided_diffusive_minus_robin_max_abs": max(
                abs(row["literal_diffusive_minus_robin"])
                for row in trace_rows
                if 15.0 <= row["time_s"] <= 45.0
            ),
            "face_diffusive_minus_robin_max_abs": max(
                abs(row["face_diffusive_minus_robin"])
                for row in trace_rows
                if 15.0 <= row["time_s"] <= 45.0
            ),
            "surface_control_volume_balance_max_abs": max(
                abs(row["surface_control_volume_balance"])
                for row in trace_rows
                if 15.0 <= row["time_s"] <= 45.0
            ),
        },
        "trace_csv": "boundary_solver_trace_0_60s.csv",
    }


def _plot_convergence(
    directory: Path,
    filename: str,
    level_values: Sequence[float],
    level_labels: Sequence[str],
    comparison_by_level: dict[str, dict[str, Any]],
    x_label: str,
    title: str,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axes = plt.subplots(1, 2, figsize=(12.0, 4.8))
    for position_label, _ in CONVERGENCE_POSITIONS:
        errors_linf = [comparison_by_level[label]["by_position"][position_label]["linf"] for label in level_labels]
        errors_l2 = [comparison_by_level[label]["by_position"][position_label]["l2_rms"] for label in level_labels]
        axes[0].loglog(level_values, errors_linf, marker="o", label=position_label)
        axes[1].loglog(level_values, errors_l2, marker="o", label=position_label)
    for axis, metric in zip(axes, ("L∞ error", "L2 RMS error")):
        axis.set_xlabel(x_label)
        axis.set_ylabel(metric + " against fixed reference")
        axis.grid(True, which="both", alpha=0.25)
        axis.legend()
    figure.suptitle(title)
    figure.tight_layout()
    figure.savefig(directory / filename)
    figure.savefig(directory / Path(filename).with_suffix(".png"), dpi=180)
    plt.close(figure)


def _case_metadata(case: CaseData) -> dict[str, Any]:
    return {
        "label": case.label,
        "n_intervals": case.n_intervals,
        "dr_m": case.dr_m,
        "dr_cm": case.dr_m * 100.0,
        "dt_s": case.dt_s,
        "end_time_s": case.end_time_s,
        "runtime_seconds": case.runtime_seconds,
        "sample_count": len(case.times_s),
    }


def main() -> int:
    started = time.perf_counter()
    for directory in (SURFACE_DIR, TEMPORAL_DIR, SPATIAL_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    source_path = ROOT / SOURCE_RELATIVE
    boundary = BoundaryProvider.from_attachment1(source_path)
    source_hash = _sha256(source_path)

    surface_test = _run_case("N640_dt0.0625_short", 640, 0.0625, 100.0, boundary)
    surface_reference = _run_case("N1280_dt0.0625_short", 1280, 0.0625, 100.0, boundary)
    surface_rows = _surface_rows(surface_test, surface_reference)
    _write_surface_csvs(surface_rows)
    _print_surface_table(surface_rows)
    surface_plot_audit = _plot_surface(surface_rows)

    signed_by_position: dict[str, dict[str, Any]] = {}
    for position_label, _ in SURFACE_POSITIONS:
        selected = [row for row in surface_rows if row["position_label"] == position_label and 15.0 <= row["time_s"] <= 45.0]
        signed_by_position[position_label] = {
            "minimum_absolute_error": min(selected, key=lambda row: row["absolute_error"]),
            "zero_crossings_15_45s": _find_zero_crossings(
                [row["time_s"] for row in selected],
                [row["signed_error"] for row in selected],
            ),
            "signed_error_at_spotlight": {
                str(int(time_s)): next(row["signed_error"] for row in selected if row["time_s"] == time_s)
                for time_s in (20.0, 25.0, 30.0, 35.0, 40.0)
            },
        }

    all_cases: dict[str, CaseData] = {}
    temporal_specs = (("dt1", 1.0), ("dt0.5", 0.5), ("dt0.25", 0.25), ("dt0.125", 0.125), ("dt0.0625_ref", 0.0625))
    for label, dt_s in temporal_specs:
        all_cases[label] = _run_case(f"N80_{label}", 80, dt_s, 1800.0, boundary)
    temporal_reference = all_cases["dt0.0625_ref"]
    temporal_comparisons: dict[str, dict[str, Any]] = {}
    for label, _ in temporal_specs[:-1]:
        temporal_comparisons[label] = _compare_cases(
            all_cases[label],
            temporal_reference,
            CONVERGENCE_POSITIONS,
            TEMPORAL_DIR / f"{label}_vs_dt0.0625_ref_full.csv",
        )
    temporal_level_values = {label: dt for label, dt in temporal_specs[:-1]}
    temporal_levels = [label for label, _ in temporal_specs[:-1]]
    temporal_orders_linf = _adjacent_order_rows(temporal_comparisons, temporal_levels, temporal_level_values, "linf")
    temporal_orders_l2 = _adjacent_order_rows(temporal_comparisons, temporal_levels, temporal_level_values, "l2_rms")
    _plot_convergence(
        TEMPORAL_DIR,
        "temporal_convergence.svg",
        [temporal_level_values[label] for label in temporal_levels],
        temporal_levels,
        temporal_comparisons,
        "dt (s)",
        "Q1 temporal convergence at fixed dr=0.025 cm",
    )

    spatial_specs = (("dr0.1", 20), ("dr0.05", 40), ("dr0.025", 80), ("dr0.0125_ref", 160))
    spatial_cases: dict[str, CaseData] = {"dr0.025": all_cases["dt0.0625_ref"]}
    for label, n_intervals in spatial_specs:
        if label == "dr0.025":
            continue
        spatial_cases[label] = _run_case(f"{label}_dt0.0625", n_intervals, 0.0625, 1800.0, boundary)
    spatial_reference = spatial_cases["dr0.0125_ref"]
    spatial_comparisons: dict[str, dict[str, Any]] = {}
    for label, _ in spatial_specs[:-1]:
        spatial_comparisons[label] = _compare_cases(
            spatial_cases[label],
            spatial_reference,
            CONVERGENCE_POSITIONS,
            SPATIAL_DIR / f"{label}_vs_dr0.0125_ref_full.csv",
        )
    spatial_level_values = {label: spatial_cases[label].dr_m * 100.0 for label, _ in spatial_specs[:-1]}
    spatial_levels = [label for label, _ in spatial_specs[:-1]]
    spatial_orders_linf = _adjacent_order_rows(spatial_comparisons, spatial_levels, spatial_level_values, "linf")
    spatial_orders_l2 = _adjacent_order_rows(spatial_comparisons, spatial_levels, spatial_level_values, "l2_rms")
    _plot_convergence(
        SPATIAL_DIR,
        "spatial_convergence.svg",
        [spatial_level_values[label] for label in spatial_levels],
        spatial_levels,
        spatial_comparisons,
        "dr (cm)",
        "Q1 spatial convergence at fixed dt=0.0625 s",
    )

    trace_result, trace, trace_runtime = _run_trace_case(80, 0.0625, 60.0, boundary)
    boundary_payload = _boundary_audit(boundary, trace_result, trace)
    boundary_payload["runtime_seconds"] = trace_runtime
    del trace_result
    gc.collect()

    common_metadata = {
        "code_commit_at_run": _code_commit(),
        "python": platform.python_version(),
        "input_hashes": {str(SOURCE_RELATIVE): source_hash},
        "solver": "src.q1.solver.run_m1, uniform conservative radial FVM, backward Euler, linear boundary interpolation, Robin surface",
        "floating_point_policy": "signed and absolute errors are calculated from full-precision Python floats; CSV uses repr; no pre-error rounding",
        "official_source_modified": False,
        "final_result1_regenerated": False,
    }
    surface_payload = {
        "experiment_id": "EXP-Q1-SURFACE-DECAY",
        "status": "COMPLETED",
        **common_metadata,
        "error_definition": {
            "signed_error": "e(t)=C_test(R,t)-C_ref(R,t)",
            "absolute_error": "E(t)=abs(e(t))",
            "test_case": _case_metadata(surface_test),
            "reference_case": _case_metadata(surface_reference),
            "note": "The literal R=2.0 cm surface and the near-surface R=1.9 cm node are both retained; the observed historical valley is checked at both.",
        },
        "raw_table_scope": "15--45 s at 1 s spacing; full 1--100 s data also written",
        "zero_crossing_diagnosis": signed_by_position,
        "plot_audit": surface_plot_audit,
        "boundary_solver_audit": boundary_payload,
        "files": {
            "raw_full_csv": "surface_error_1_100s.csv",
            "raw_15_45_csv": "surface_signed_error_15_45s.csv",
            "trace_csv": "boundary_solver_trace_0_60s.csv",
            "signed_plot": "signed_error_vs_time.svg",
            "absolute_semilogy_plot": "absolute_error_semilogy.svg",
        },
        "runtime_seconds": time.perf_counter() - started,
    }
    (SURFACE_DIR / "metrics.json").write_text(json.dumps(surface_payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (SURFACE_DIR / "config.json").write_text(json.dumps({
        **common_metadata,
        "experiment_id": "EXP-Q1-SURFACE-DECAY",
        "cases": {"test": _case_metadata(surface_test), "reference": _case_metadata(surface_reference)},
    }, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (SURFACE_DIR / "notes.md").write_text(
        "# EXP-Q1-SURFACE-DECAY signed-error audit\n\n"
        "This audit keeps both the signed pointwise error `e=C_test-C_ref` and `abs(e)`. "
        "The test is N640, the reference is N1280, both with `dt=0.0625 s`; positions "
        "1.9 cm and the literal 2.0 cm surface are both included. The CSV values are "
        "full-precision floats. The signed plot is direct data with a zero line; the "
        "absolute plot uses semilogy and masks only exact non-positive points for display, "
        "without replacing their CSV values by epsilon.\n\n"
        "The historical `surface_moisture_error_decay.svg` is preserved. These new plots "
        "are explicit audit artifacts.\n",
        encoding="utf-8",
    )

    temporal_payload = {
        "experiment_id": "EXP-003",
        "status": "COMPLETED",
        **common_metadata,
        "purpose": "Independent time-step convergence audit, separated from spatial error",
        "fixed_spatial_grid": {"n_intervals": 80, "dr_cm": 0.025},
        "time_steps_s": [1.0, 0.5, 0.25, 0.125],
        "reference": _case_metadata(temporal_reference),
        "cases": {label: _case_metadata(all_cases[label]) for label, _ in temporal_specs[:-1]},
        "reference_error_metrics": temporal_comparisons,
        "observed_order_to_fixed_reference_linf": temporal_orders_linf,
        "observed_order_to_fixed_reference_l2_rms": temporal_orders_l2,
        "definition": "L2 is discrete RMS over all native test times in 0--1800 s; tail norms use t>=60 s; errors are test-reference.",
        "files": {"full_data_pattern": "*_vs_dt0.0625_ref_full.csv", "plot": "temporal_convergence.svg"},
    }
    (TEMPORAL_DIR / "metrics.json").write_text(json.dumps(temporal_payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (TEMPORAL_DIR / "config.json").write_text(json.dumps({
        **common_metadata,
        "experiment_id": "EXP-003",
        "fixed_spatial_grid": {"n_intervals": 80, "dr_cm": 0.025},
        "cases": {label: _case_metadata(all_cases[label]) for label, _ in temporal_specs},
    }, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (TEMPORAL_DIR / "notes.md").write_text(
        "# EXP-003 time-step convergence audit\n\n"
        "Uniform radial grid is fixed at `dr=0.025 cm` (N=80). Only `dt` changes: "
        "1, 0.5, 0.25, 0.125 s; `dt=0.0625 s` is the independent reference. "
        "Full-time CSVs contain signed and absolute errors at surface, r=1.5 cm, "
        "r=1.0 cm, and center. L∞ and discrete RMS-L2 are computed over 0--1800 s "
        "and over the t>=60 s tail.\n",
        encoding="utf-8",
    )

    spatial_payload = {
        "experiment_id": "EXP-004",
        "status": "COMPLETED",
        **common_metadata,
        "purpose": "Independent spatial convergence audit, separated from time-step error",
        "fixed_time_step": {"dt_s": 0.0625},
        "spatial_steps_cm": [0.1, 0.05, 0.025],
        "reference": _case_metadata(spatial_reference),
        "cases": {label: _case_metadata(spatial_cases[label]) for label, _ in spatial_specs[:-1]},
        "reference_error_metrics": spatial_comparisons,
        "observed_order_to_fixed_reference_linf": spatial_orders_linf,
        "observed_order_to_fixed_reference_l2_rms": spatial_orders_l2,
        "definition": "L2 is discrete RMS over all common times in 0--1800 s; errors are test-reference.",
        "files": {"full_data_pattern": "*_vs_dr0.0125_ref_full.csv", "plot": "spatial_convergence.svg"},
    }
    (SPATIAL_DIR / "metrics.json").write_text(json.dumps(spatial_payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (SPATIAL_DIR / "config.json").write_text(json.dumps({
        **common_metadata,
        "experiment_id": "EXP-004",
        "fixed_time_step": {"dt_s": 0.0625},
        "cases": {label: _case_metadata(spatial_cases[label]) for label, _ in spatial_specs},
    }, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (SPATIAL_DIR / "notes.md").write_text(
        "# EXP-004 spatial convergence audit\n\n"
        "Uniform backward-Euler time step is fixed at `dt=0.0625 s`. Only `dr` changes: "
        "0.1, 0.05, 0.025 cm; `dr=0.0125 cm` (N=160) is the independent reference. "
        "Full-time CSVs contain signed and absolute errors at surface, r=1.5 cm, "
        "r=1.0 cm, and center, with L∞ and discrete RMS-L2 over 0--1800 s.\n",
        encoding="utf-8",
    )

    print("\nSURFACE ZERO-CROSSING SUMMARY")
    for position_label, details in signed_by_position.items():
        print(position_label, json.dumps(details["zero_crossings_15_45s"], ensure_ascii=False))
    print("\nTEMPORAL OBSERVED ORDER (Linf, against dt=0.0625 reference)")
    print(json.dumps(temporal_orders_linf, ensure_ascii=False, indent=2))
    print("\nSPATIAL OBSERVED ORDER (Linf, against dr=0.0125 reference)")
    print(json.dumps(spatial_orders_linf, ensure_ascii=False, indent=2))
    print(f"\nAUDIT COMPLETE; total runtime={time.perf_counter() - started:.3f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
