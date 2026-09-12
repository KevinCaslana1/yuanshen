"""Run the Q2 numerical-accuracy remediation studies.

This script is deliberately limited to numerical diagnostics.  It never
touches A题/, the official result templates, deliverables/, or the old
Q2_FREEZE_RUN production attempt.  All calculations retain Python float
precision; rounding is used only for human-readable CSV labels.
"""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import math
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q2 import Q2RunConfig, Q2Parameters, run_q2
from src.q2.environment import EnvironmentProvider
from src.q2.model import boundary_flux_pair
from src.q2.properties import diffusivity
from src.q2.solver import grid_for_config


FREEZE = ROOT / "experiments" / "Q2_FREEZE_RUN"
ROOT_OUT = ROOT / "experiments" / "Q2_ACCURACY_REMEDIATION"
TRANSITION_OUT = ROOT / "experiments" / "EXP-Q2-ACC-T-TRANSITION"
INITIAL_OUT = ROOT / "experiments" / "EXP-Q2-ACC-C-INITIAL"
SPATIAL_OUT = ROOT / "experiments" / "EXP-Q2-ACC-SPATIAL"
SPATIAL_FURTHER_OUT = ROOT / "experiments" / "EXP-Q2-ACC-SPATIAL-FURTHER"
TEMPORAL_OUT = ROOT / "experiments" / "EXP-Q2-ACC-TEMPORAL"
TEMPORAL_FURTHER_OUT = ROOT / "experiments" / "EXP-Q2-ACC-TEMPORAL-FURTHER"
TIME_POLICY_OUT = ROOT / "experiments" / "EXP-Q2-NUM-REMEDY-C-TIME"

RADII_CM = (0.0, 1.0, 1.5, 1.9, 2.0)
THRESHOLD_T = 2.5e-5
THRESHOLD_C = 2.5e-5


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_base_config() -> Q2RunConfig:
    payload = json.loads((FREEZE / "config.json").read_text(encoding="utf-8"))
    config = dict(payload["config"])
    config["input_path"] = Path(config["input_path"])
    config["parameters"] = Q2Parameters(**config["parameters"])
    return Q2RunConfig(**config)


def make_config(base: Q2RunConfig, *, end_time_s: float, dt: float | None = None,
                n_intervals: int | None = None, cluster_power: float | None = None,
                reset: bool | None = None) -> Q2RunConfig:
    values: dict[str, Any] = {"end_time_s": end_time_s}
    if dt is not None:
        values["time_step_s"] = dt
    if n_intervals is not None:
        values["n_intervals"] = n_intervals
    if cluster_power is not None:
        values["cluster_power"] = cluster_power
    if reset is not None:
        values["reset_bdf2_at_environment_transition"] = reset
    return replace(base, **values)


def radius_indices(result) -> dict[float, int]:
    return {
        radius: min(range(len(result.grid.nodes_m)), key=lambda i: abs(result.grid.nodes_m[i] * 100.0 - radius))
        for radius in RADII_CM
    }


def save_snapshots(path: Path, result, times: Iterable[float]) -> dict[str, dict[str, float]]:
    indices = radius_indices(result)
    rows: list[dict[str, float]] = []
    for time_s in times:
        temperature_k, moisture = result.snapshot_at(time_s)
        for radius in RADII_CM:
            index = indices[radius]
            rows.append({
                "time_s": float(time_s),
                "radius_cm": float(radius),
                "temperature_K": float(temperature_k[index]),
                "temperature_C": float(temperature_k[index] - 273.15),
                "moisture_kg_kg": float(moisture[index]),
            })
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return {f"{row['time_s']:.12g}|{row['radius_cm']:.12g}": row for row in rows}


def load_snapshot_index(path: Path) -> dict[str, dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return {
        sample_key(float(row["time_s"]), float(row["radius_cm"])): {
            key: float(value) for key, value in row.items() if key not in {"time_s", "radius_cm"}
        } | {"time_s": float(row["time_s"]), "radius_cm": float(row["radius_cm"])}
        for row in rows
    }


def row_to_dict(row) -> dict[str, Any]:
    return {
        "time_s": float(row.time_s),
        "scheme": row.scheme,
        "environment_temperature_c": float(row.environment_temperature_c),
        "environment_moisture_kg_kg": float(row.environment_moisture_kg_kg),
        "picard_iterations": int(row.picard_iterations),
        "temperature_residual": float(row.temperature_residual),
        "moisture_residual": float(row.moisture_residual),
        "temperature_linear_residual": float(row.temperature_linear_residual),
        "moisture_linear_residual": float(row.moisture_linear_residual),
        "surface_heat_internal_w_m2": float(row.surface_heat_internal_w_m2),
        "surface_heat_robin_w_m2": float(row.surface_heat_robin_w_m2),
        "surface_heat_boundary_residual_w_m2": float(row.surface_heat_boundary_residual_w_m2),
        "surface_moisture_internal_kg_m2_s": float(row.surface_moisture_internal_kg_m2_s),
        "surface_moisture_robin_kg_m2_s": float(row.surface_moisture_robin_kg_m2_s),
        "surface_moisture_boundary_residual_kg_m2_s": float(row.surface_moisture_boundary_residual_kg_m2_s),
        "surface_k_w_m_k": float(row.surface_k_w_m_k),
        "surface_D_m2_s": float(row.surface_D_m2_s),
        "mass_step_residual": float(row.mass_step_residual),
        "heat_step_residual_j": float(row.heat_step_residual_j),
    }


def selected_diagnostics(result, start: float, end: float) -> list[dict[str, Any]]:
    return [row_to_dict(row) for row in result.diagnostics if start - 1e-9 <= row.time_s <= end + 1e-9]


def run_short_case(name: str, config: Q2RunConfig, out_dir: Path, record_times: tuple[float, ...], *, full_diagnostics: bool = False) -> dict[str, Any]:
    case_dir = out_dir / name
    case_dir.mkdir(parents=True, exist_ok=False)
    write_json(case_dir / "config.json", config.as_dict())
    diagnostics_path = None if full_diagnostics else case_dir / "diagnostics_interval_0.25s.csv"
    result = run_q2(
        config,
        record_times=record_times,
        diagnostics_path=diagnostics_path,
        diagnostics_interval_s=None if full_diagnostics else 0.25,
    )
    snapshot_index = save_snapshots(case_dir / "snapshots.csv", result, record_times)
    local_diagnostics = selected_diagnostics(result, 14390.0, 14420.0) if full_diagnostics else []
    if full_diagnostics:
        write_json(case_dir / "diagnostics_window.json", local_diagnostics)
    summary = {
        "name": name,
        "config": config.as_dict(),
        "complete": bool(result.complete),
        "grid": {
            "requested_intervals": config.n_intervals,
            "actual_cell_count": len(result.grid.nodes_m) - 1,
            "actual_node_count": len(result.grid.nodes_m),
            "min_dr_m": float(result.grid.min_dr_m if hasattr(result.grid, "min_dr_m") else result.grid.dr_m),
            "max_dr_m": float(result.grid.max_dr_m if hasattr(result.grid, "max_dr_m") else result.grid.dr_m),
            "min_dr_cm": float((result.grid.min_dr_m if hasattr(result.grid, "min_dr_m") else result.grid.dr_m) * 100.0),
            "cluster_power": config.cluster_power,
        },
        "diagnostic_summary": {key: value for key, value in result.diagnostic_summary.items() if isinstance(value, (int, float)) and math.isfinite(float(value))},
        "snapshot_path": str((case_dir / "snapshots.csv").relative_to(ROOT)).replace("\\", "/"),
    }
    if diagnostics_path is not None:
        summary["diagnostics_path"] = str(diagnostics_path.relative_to(ROOT)).replace("\\", "/")
        summary["diagnostics_sha256"] = sha256(diagnostics_path)
    write_json(case_dir / "metrics.json", summary)
    del result
    gc.collect()
    return {"summary": summary, "snapshots": snapshot_index}


def sample_key(time_s: float, radius: float) -> str:
    return f"{float(time_s):.12g}|{float(radius):.12g}"


def compare_snapshot_maps(left: dict[str, dict[str, float]], right: dict[str, dict[str, float]]) -> dict[str, Any]:
    temperature_errors: list[float] = []
    moisture_errors: list[float] = []
    by_radius: dict[str, dict[str, float]] = {}
    common_keys = sorted(set(left).intersection(right))
    for key in common_keys:
        row = left[key]
        time_s, radius = float(row["time_s"]), float(row["radius_cm"])
        a = left[key]
        b = right[key]
        et = abs(float(a["temperature_C"]) - float(b["temperature_C"]))
        ec = abs(float(a["moisture_kg_kg"]) - float(b["moisture_kg_kg"]))
        temperature_errors.append(et)
        moisture_errors.append(ec)
        radius_key = f"{radius:g}"
        item = by_radius.setdefault(radius_key, {"temperature_Linf_C": 0.0, "moisture_Linf_kg_kg": 0.0})
        item["temperature_Linf_C"] = max(item["temperature_Linf_C"], et)
        item["moisture_Linf_kg_kg"] = max(item["moisture_Linf_kg_kg"], ec)
    def metrics(values: list[float]) -> tuple[float, float]:
        return max(values, default=0.0), math.sqrt(sum(value * value for value in values) / len(values)) if values else 0.0
    t_linf, t_l2 = metrics(temperature_errors)
    c_linf, c_l2 = metrics(moisture_errors)
    return {
        "sample_count": len(temperature_errors),
        "temperature_Linf_C": t_linf,
        "temperature_L2_RMS_C": t_l2,
        "moisture_Linf_kg_kg": c_linf,
        "moisture_L2_RMS_kg_kg": c_l2,
        "by_radius": by_radius,
    }


def observed_order(coarse: float, fine: float, ratio: float = 2.0) -> float:
    return math.log(coarse / fine, ratio) if coarse > 0.0 and fine > 0.0 else float("nan")


def initial_compatibility(base: Q2RunConfig) -> None:
    INITIAL_OUT.mkdir(parents=True, exist_ok=False)
    env = EnvironmentProvider.from_attachment1(
        base.input_path,
        method=base.interpolation,
        post_attachment_mode=base.post_attachment_mode,
        post_temperature_c=base.post_temperature_c,
        post_moisture_kg_kg=base.post_moisture_kg_kg,
    )
    grid = grid_for_config(base)
    p = base.parameters
    c0 = float(p.initial_moisture_kg_kg)
    t0_k = float(p.initial_temperature_c + 273.15)
    _, c_inf = env.at(0.0)
    d0 = float(diffusivity(c0, t0_k))
    internal, robin, residual = boundary_flux_pair(c0, c0, grid, d0, p.mass_transfer_m_s, c_inf)
    payload = {
        "experiment": "EXP-Q2-ACC-C-INITIAL",
        "status": "INCOMPATIBLE_INITIAL_DATA_AND_ROBIN_CONDITION" if abs(residual) > 0.0 else "COMPATIBLE",
        "classification_scope": "Q2 numerical initial-layer finding only",
        "config": base.as_dict(),
        "initial_temperature_c": float(p.initial_temperature_c),
        "initial_moisture_kg_kg": c0,
        "surface_environment_moisture_at_t0_kg_kg": float(c_inf),
        "hm_m_s": float(p.mass_transfer_m_s),
        "D_at_C0_T0_m2_s": d0,
        "discrete_initial_gradient_moisture_kg_kg_per_m": 0.0,
        "discrete_diffusion_flux_kg_m2_s": float(internal),
        "Robin_flux_kg_m2_s": float(robin),
        "Robin_residual_internal_minus_Robin_kg_m2_s": float(residual),
        "do_not_infer": "This does not establish that the real material necessarily has a physical boundary layer.",
    }
    write_json(INITIAL_OUT / "metrics.json", payload)
    (INITIAL_OUT / "notes.md").write_text(
        "# EXP-Q2-ACC-C-INITIAL\n\n"
        "The uniform official Q2 initial moisture and the t=0 Robin boundary are evaluated without altering either input. "
        "The result is classified only as a Q2 numerical initial-layer finding. It is not a physical-material claim.\n",
        encoding="utf-8",
    )


def transition_study(base: Q2RunConfig) -> None:
    TRANSITION_OUT.mkdir(parents=True, exist_ok=True)
    local_times = tuple(float(value) for value in range(14390, 14421))
    summary: dict[str, Any] = {
        "experiment": "EXP-Q2-ACC-T-TRANSITION",
        "hypothesis": "H-Q2-ACC-T-001",
        "window_s": [14390.0, 14420.0],
        "radii_cm": list(RADII_CM),
        "candidate_rule": "BE exactly at the 14400 s transition, then BDF2; frozen environment and physics unchanged",
        "runs": {},
        "comparisons_to_fine_reference": {},
    }
    dts = (0.25, 0.125, 0.0625, 0.03125)
    maps: dict[str, dict[str, dict[str, float]]] = {}
    expected_names = [f"{label}_dt{dt:g}" for label in ("current", "event_aligned") for dt in dts]
    existing_complete = all((TRANSITION_OUT / name / "snapshots.csv").is_file() and (TRANSITION_OUT / name / "metrics.json").is_file() for name in expected_names)
    existing_any = any((TRANSITION_OUT / name).exists() for name in expected_names)
    if existing_complete:
        for name in expected_names:
            maps[name] = load_snapshot_index(TRANSITION_OUT / name / "snapshots.csv")
            summary["runs"][name] = json.loads((TRANSITION_OUT / name / "metrics.json").read_text(encoding="utf-8"))
    else:
        if existing_any:
            raise RuntimeError("transition experiment directory is incomplete; refusing to mix or overwrite attempts")
        for reset in (False, True):
            label = "event_aligned" if reset else "current"
            for dt in dts:
                records = tuple(sorted(set(local_times + (14400.0 + dt,))))
                name = f"{label}_dt{dt:g}"
                case = run_short_case(name, make_config(base, end_time_s=14420.0, dt=dt, reset=reset), TRANSITION_OUT, records, full_diagnostics=(dt <= 0.25 and dt >= 0.0625))
                maps[name] = case["snapshots"]
                summary["runs"][name] = case["summary"]
    for reset in (False, True):
        label = "event_aligned" if reset else "current"
        fine_name = f"{label}_dt0.03125"
        for dt in dts[:-1]:
            name = f"{label}_dt{dt:g}"
            comparison = compare_snapshot_maps(maps[name], maps[fine_name])
            summary["comparisons_to_fine_reference"][name] = comparison
        d01 = compare_snapshot_maps(maps[f"{label}_dt0.25"], maps[f"{label}_dt0.125"])
        d12 = compare_snapshot_maps(maps[f"{label}_dt0.125"], maps[f"{label}_dt0.0625"])
        d23 = compare_snapshot_maps(maps[f"{label}_dt0.0625"], maps[f"{label}_dt0.03125"])
        summary.setdefault("nested_convergence", {})[label] = {
            "dt0.25_vs_dt0.125_raw": d01,
            "dt0.125_vs_dt0.0625_raw": d12,
            "dt0.0625_vs_dt0.03125_raw": d23,
            "observed_order_from_nested_raw_differences": {
                "temperature_0.25_to_0.125": observed_order(d01["temperature_Linf_C"], d12["temperature_Linf_C"]),
                "moisture_0.25_to_0.125": observed_order(d01["moisture_Linf_kg_kg"], d12["moisture_Linf_kg_kg"]),
                "temperature_0.125_to_0.0625": observed_order(d12["temperature_Linf_C"], d23["temperature_Linf_C"]),
                "moisture_0.125_to_0.0625": observed_order(d12["moisture_Linf_kg_kg"], d23["moisture_Linf_kg_kg"]),
            },
            "conservative_fine_coarse_bound": {
                "temperature_C": d23["temperature_Linf_C"],
                "moisture_kg_kg": d23["moisture_Linf_kg_kg"],
                "interpretation": "fine/coarse raw difference bound; not called Richardson uncertainty",
            },
        }
    write_json(TRANSITION_OUT / "metrics.json", summary)
    (TRANSITION_OUT / "notes.md").write_text(
        "# EXP-Q2-ACC-T-TRANSITION\n\n"
        "Current and event-aligned runs use the same Attachment 1 interpolation, post-14400 constants, physical parameters, Robin conditions, harmonic interface rule, initial state and horizon. "
        "The only change is the numerical multistep restart at exactly 14400 s. All comparisons retain full floating-point values.\n",
        encoding="utf-8",
    )


def spatial_isolation(base: Q2RunConfig) -> None:
    SPATIAL_OUT.mkdir(parents=True, exist_ok=False)
    dt = 0.015625
    times = tuple(float(value) for value in (0.0, 0.25, 0.5, 1.0, 1.5, 2.0))
    cases: dict[str, dict[str, Any]] = {}
    for n_intervals in (80, 160, 320):
        name = f"n{n_intervals}_dt{dt:g}"
        cases[name] = run_short_case(name, make_config(base, end_time_s=2.0, dt=dt, n_intervals=n_intervals, reset=False), SPATIAL_OUT, times, full_diagnostics=False)
    names = tuple(cases)
    comparisons = {}
    for left, right in zip(names, names[1:]):
        comparisons[f"{left}_vs_{right}"] = compare_snapshot_maps(cases[left]["snapshots"], cases[right]["snapshots"])
    metrics = {
        "experiment": "EXP-Q2-ACC-SPATIAL",
        "fixed_time_step_s": dt,
        "time_interval_s": [0.0, 2.0],
        "radii_cm": list(RADII_CM),
        "grid_sequence": [cases[name]["summary"]["grid"] for name in names],
        "runs": {name: cases[name]["summary"] for name in names},
        "raw_pairwise_differences": comparisons,
        "finest_grid_conservative_bound": comparisons[f"{names[-2]}_vs_{names[-1]}"],
    }
    write_json(SPATIAL_OUT / "metrics.json", metrics)
    (SPATIAL_OUT / "notes.md").write_text(
        "# EXP-Q2-ACC-SPATIAL\n\n"
        f"Spatial isolation fixes dt={dt:g} s and compares the current clustered grid with n=160 and n=320 requested intervals. "
        "The actual cell count/minimum dr are recorded in metrics.json.\n",
        encoding="utf-8",
    )


def spatial_further_refinement(base: Q2RunConfig) -> None:
    SPATIAL_FURTHER_OUT.mkdir(parents=True, exist_ok=False)
    dt = 0.015625
    times = tuple(float(value) for value in (0.0, 0.25, 0.5, 1.0, 1.5, 2.0))
    cases: dict[str, dict[str, Any]] = {}
    for n_intervals in (320, 640):
        name = f"n{n_intervals}_dt{dt:g}"
        cases[name] = run_short_case(name, make_config(base, end_time_s=2.0, dt=dt, n_intervals=n_intervals, reset=False), SPATIAL_FURTHER_OUT, times, full_diagnostics=False)
    left, right = tuple(cases)
    metrics = {
        "experiment": "EXP-Q2-ACC-SPATIAL-FURTHER",
        "fixed_time_step_s": dt,
        "time_interval_s": [0.0, 2.0],
        "radii_cm": list(RADII_CM),
        "grid_sequence": [cases[name]["summary"]["grid"] for name in cases],
        "runs": {name: cases[name]["summary"] for name in cases},
        "raw_pairwise_difference": compare_snapshot_maps(cases[left]["snapshots"], cases[right]["snapshots"]),
        "interpretation": "further spatial refinement to test whether the n=320 surface layer is below the fixed 2.5e-5 gate",
    }
    write_json(SPATIAL_FURTHER_OUT / "metrics.json", metrics)
    (SPATIAL_FURTHER_OUT / "notes.md").write_text(
        "# EXP-Q2-ACC-SPATIAL-FURTHER\n\n"
        "This supplemental run extends the fixed-dt spatial isolation from n=320 to n=640.\n",
        encoding="utf-8",
    )


def temporal_isolation(base: Q2RunConfig) -> None:
    TEMPORAL_OUT.mkdir(parents=True, exist_ok=False)
    times = tuple(float(value) for value in (0.0, 0.25, 0.5, 1.0, 1.5, 2.0))
    cases: dict[str, dict[str, Any]] = {}
    for dt in (0.25, 0.125, 0.0625, 0.03125):
        name = f"dt{dt:g}_n320"
        cases[name] = run_short_case(name, make_config(base, end_time_s=2.0, dt=dt, n_intervals=320, reset=False), TEMPORAL_OUT, times, full_diagnostics=False)
    names = tuple(cases)
    comparisons = {}
    for left, right in zip(names, names[1:]):
        comparisons[f"{left}_vs_{right}"] = compare_snapshot_maps(cases[left]["snapshots"], cases[right]["snapshots"])
    orders = {}
    for first, second, third in zip(names, names[1:], names[2:]):
        coarse_fine = comparisons[f"{first}_vs_{second}"]
        fine_finer = comparisons[f"{second}_vs_{third}"]
        orders[f"{first}_to_{second}_vs_{third}"] = {
            "temperature": observed_order(coarse_fine["temperature_Linf_C"], fine_finer["temperature_Linf_C"]),
            "moisture": observed_order(coarse_fine["moisture_Linf_kg_kg"], fine_finer["moisture_Linf_kg_kg"]),
        }
    metrics = {
        "experiment": "EXP-Q2-ACC-TEMPORAL",
        "fixed_spatial_grid": cases[names[-1]]["summary"]["grid"],
        "time_interval_s": [0.0, 2.0],
        "radii_cm": list(RADII_CM),
        "runs": {name: cases[name]["summary"] for name in names},
        "raw_pairwise_differences": comparisons,
        "observed_order_from_nested_raw_differences": orders,
        "finest_grid_conservative_bound": comparisons[f"{names[-2]}_vs_{names[-1]}"],
        "interpretation": "pairwise fine/coarse bounds; no two-level difference is labelled Richardson uncertainty",
    }
    write_json(TEMPORAL_OUT / "metrics.json", metrics)
    (TEMPORAL_OUT / "notes.md").write_text(
        "# EXP-Q2-ACC-TEMPORAL\n\n"
        "Temporal isolation fixes the n=320 clustered spatial grid and compares dt=.25/.125/.0625/.03125 s. "
        "The reported orders use nested raw differences and the finest pair is retained as a conservative bound.\n",
        encoding="utf-8",
    )


def temporal_further_refinement(base: Q2RunConfig) -> None:
    TEMPORAL_FURTHER_OUT.mkdir(parents=True, exist_ok=False)
    times = tuple(float(value) for value in (0.0, 0.25, 0.5, 1.0, 1.5, 2.0))
    cases: dict[str, dict[str, Any]] = {}
    for dt in (0.03125, 0.015625, 0.0078125):
        name = f"dt{dt:g}_n640"
        cases[name] = run_short_case(name, make_config(base, end_time_s=2.0, dt=dt, n_intervals=640, reset=False), TEMPORAL_FURTHER_OUT, times, full_diagnostics=False)
    names = tuple(cases)
    comparisons = {
        f"{left}_vs_{right}": compare_snapshot_maps(cases[left]["snapshots"], cases[right]["snapshots"])
        for left, right in zip(names, names[1:])
    }
    orders = {}
    for first, second, third in zip(names, names[1:], names[2:]):
        coarse_fine = comparisons[f"{first}_vs_{second}"]
        fine_finer = comparisons[f"{second}_vs_{third}"]
        orders[f"{first}_to_{second}_vs_{third}"] = {
            "temperature": observed_order(coarse_fine["temperature_Linf_C"], fine_finer["temperature_Linf_C"]),
            "moisture": observed_order(coarse_fine["moisture_Linf_kg_kg"], fine_finer["moisture_Linf_kg_kg"]),
        }
    metrics = {
        "experiment": "EXP-Q2-ACC-TEMPORAL-FURTHER",
        "fixed_spatial_grid": cases[names[-1]]["summary"]["grid"],
        "time_interval_s": [0.0, 2.0],
        "radii_cm": list(RADII_CM),
        "runs": {name: cases[name]["summary"] for name in names},
        "raw_pairwise_differences": comparisons,
        "observed_order_from_nested_raw_differences": orders,
        "finest_grid_conservative_bound": comparisons[f"{names[-2]}_vs_{names[-1]}"],
        "interpretation": "supplemental temporal isolation on n=640; pairwise fine/coarse bounds are not Richardson uncertainty",
    }
    write_json(TEMPORAL_FURTHER_OUT / "metrics.json", metrics)
    (TEMPORAL_FURTHER_OUT / "notes.md").write_text(
        "# EXP-Q2-ACC-TEMPORAL-FURTHER\n\n"
        "Supplemental temporal isolation on n=640 for selecting a V2 time step.\n",
        encoding="utf-8",
    )


def early_time_policy_study(base: Q2RunConfig) -> None:
    TIME_POLICY_OUT.mkdir(parents=True, exist_ok=False)
    times = tuple(float(value) for value in (0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 60.0, 1800.0))
    fixed = run_short_case(
        "fixed_dt0.25_n640",
        make_config(base, end_time_s=1800.0, dt=0.25, n_intervals=640, reset=True),
        TIME_POLICY_OUT,
        times,
        full_diagnostics=False,
    )
    policy_config = make_config(base, end_time_s=1800.0, dt=0.25, n_intervals=640, reset=True)
    policy_config = replace(policy_config, early_time_step_s=0.015625, early_time_end_s=2.0)
    policy = run_short_case("early_dt0.015625_until2s_then0.25_n640", policy_config, TIME_POLICY_OUT, times, full_diagnostics=False)
    fine_path = ROOT / "experiments/EXP-Q2-ACC-TEMPORAL-FURTHER/dt0.015625_n640/snapshots.csv"
    fine = load_snapshot_index(fine_path) if fine_path.is_file() else {}
    early_keys = {key: value for key, value in fine.items() if float(value["time_s"]) <= 2.0 + 1e-12}
    policy_early = {key: value for key, value in policy["snapshots"].items() if float(value["time_s"]) <= 2.0 + 1e-12}
    metrics = {
        "experiment": "EXP-Q2-NUM-REMEDY-C-TIME",
        "motivation": "Temporal isolation proved the t=1 s surface moisture error is time-dominated before this policy was tested.",
        "policy": policy["summary"]["config"],
        "fixed_dt_comparison_config": fixed["summary"]["config"],
        "policy_vs_fixed_dt0.25": compare_snapshot_maps(policy["snapshots"], fixed["snapshots"]),
        "policy_vs_uniform_dt0.015625_through2s": compare_snapshot_maps(policy_early, early_keys) if early_keys else {"status": "REFERENCE_NOT_AVAILABLE"},
        "policy_diagnostic_summary": policy["summary"]["diagnostic_summary"],
        "fixed_diagnostic_summary": fixed["summary"]["diagnostic_summary"],
        "scope": "short-horizon numerical evidence only; not a production approval",
    }
    write_json(TIME_POLICY_OUT / "metrics.json", metrics)
    (TIME_POLICY_OUT / "notes.md").write_text(
        "# EXP-Q2-NUM-REMEDY-C-TIME\n\n"
        "This experiment is authorized only because the fixed-spatial temporal isolation showed that t=1 s surface moisture is time-dominated. "
        "It uses dt=0.015625 s through t=2 s, then restarts with BE at the step-size change and uses dt=0.25 s afterwards. "
        "No physical input, boundary value, property, or interface rule is changed.\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("initial", "transition", "spatial", "spatial-further", "temporal", "temporal-further", "time-policy", "all"), default="all")
    args = parser.parse_args()
    base = load_base_config()
    ROOT_OUT.mkdir(parents=True, exist_ok=True)
    if args.stage in {"initial", "all"}:
        initial_compatibility(base)
    if args.stage in {"transition", "all"}:
        transition_study(base)
    if args.stage in {"spatial", "all"}:
        spatial_isolation(base)
    if args.stage in {"spatial-further", "all"}:
        spatial_further_refinement(base)
    if args.stage in {"temporal", "all"}:
        temporal_isolation(base)
    if args.stage in {"temporal-further", "all"}:
        temporal_further_refinement(base)
    if args.stage in {"time-policy", "all"}:
        early_time_policy_study(base)
    write_json(ROOT_OUT / "manifest.json", {
        "status": "COMPLETE",
        "script": "scripts/run_q2_accuracy_remediation.py",
        "stages_requested": args.stage,
        "experiments": [
            "experiments/EXP-Q2-ACC-C-INITIAL",
            "experiments/EXP-Q2-ACC-T-TRANSITION",
            "experiments/EXP-Q2-ACC-SPATIAL",
            "experiments/EXP-Q2-ACC-SPATIAL-FURTHER",
            "experiments/EXP-Q2-ACC-TEMPORAL",
            "experiments/EXP-Q2-ACC-TEMPORAL-FURTHER",
            "experiments/EXP-Q2-NUM-REMEDY-C-TIME",
        ],
        "accuracy_gate_unchanged": {"temperature_C": THRESHOLD_T, "moisture_kg_kg": THRESHOLD_C},
        "official_result2_generated": False,
    })
    print(json.dumps({"status": "COMPLETE", "stage": args.stage, "output": str(ROOT_OUT.relative_to(ROOT)).replace("\\", "/")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
