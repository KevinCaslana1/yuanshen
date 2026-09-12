"""Coupled Picard solver, streaming sampler and checkpoint support for Q2."""

from __future__ import annotations

import csv
import json
import math
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median
from typing import Dict, Iterable, List, Sequence, Tuple

from src.common.numerics import NonuniformRadialGrid, RadialGrid, make_boundary_clustered_grid, make_radial_grid
from src.q1.model import radial_control_volume_factors
from src.common.paths import PROJECT_ROOT, resolve_project_path

from .config import Q2RunConfig
from .environment import EnvironmentProvider
from .model import boundary_flux_pair, interface_values, solve_system, tridiagonal_residual_linf, assemble_variable_radial_system
from .properties import cp_array, conductivity_array, density_array, diffusivity_array


class Q2NonConvergenceError(RuntimeError):
    """Raised when one coupled time step fails the configured Picard gate."""


@dataclass(frozen=True)
class StepDiagnostic:
    time_s: float
    scheme: str
    environment_temperature_c: float
    environment_moisture_kg_kg: float
    picard_iterations: int
    temperature_residual: float
    moisture_residual: float
    temperature_linear_residual: float
    moisture_linear_residual: float
    surface_heat_internal_w_m2: float
    surface_heat_robin_w_m2: float
    surface_heat_boundary_residual_w_m2: float
    surface_moisture_internal_kg_m2_s: float
    surface_moisture_robin_kg_m2_s: float
    surface_moisture_boundary_residual_kg_m2_s: float
    surface_k_w_m_k: float
    surface_D_m2_s: float
    mass_step_residual: float
    heat_step_residual_j: float
    property_min: Dict[str, float]
    property_max: Dict[str, float]
    picard_history: Tuple[Tuple[float, float], ...]
    temperature_min_k: float = 0.0
    temperature_max_k: float = 0.0
    moisture_min_kg_kg: float = 0.0
    moisture_max_kg_kg: float = 0.0
    center_heat_flux_w_m2: float = 0.0
    center_moisture_flux_kg_m2_s: float = 0.0


@dataclass
class Q2RunResult:
    config: Q2RunConfig
    grid: RadialGrid | NonuniformRadialGrid
    times_s: Tuple[float, ...]
    snapshots: Dict[float, Tuple[Tuple[float, ...], Tuple[float, ...]]] = field(default_factory=dict)
    diagnostics: Tuple[StepDiagnostic, ...] = ()
    diagnostic_summary: Dict[str, float] = field(default_factory=dict)
    picard_count_history: Tuple[int, ...] = ()
    last_diagnostic: StepDiagnostic | None = None
    final_temperature_k: Tuple[float, ...] = ()
    final_moisture: Tuple[float, ...] = ()
    output_path: str = ""
    diagnostics_path: str = ""
    checkpoint_path: str = ""
    passive_event_bracket_s: Tuple[float, float] | None = None
    complete: bool = True

    @property
    def picard_counts(self) -> Tuple[int, ...]:
        return self.picard_count_history or tuple(row.picard_iterations for row in self.diagnostics)

    def snapshot_at(self, time_s: float) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
        key = min(self.snapshots, key=lambda value: abs(value - float(time_s)))
        if abs(key - float(time_s)) > 1.0e-8:
            raise KeyError(f"snapshot {time_s} s was not recorded")
        return self.snapshots[key]


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def grid_for_config(config: Q2RunConfig):
    required = tuple(index * 0.001 for index in range(21))
    if config.candidate == "A":
        return make_boundary_clustered_grid(config.parameters.radius_m, config.n_intervals, config.cluster_power, required)
    return make_radial_grid(config.parameters.radius_m, config.n_intervals)


def _scale_residual(new: Sequence[float], old: Sequence[float]) -> float:
    scale = max(1.0, max((abs(value) for value in new), default=1.0))
    return max((abs(a - b) for a, b in zip(new, old)), default=0.0) / scale


def _finite_vector(values: Sequence[float], name: str) -> None:
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError(f"{name} contains a non-finite value")


def _weighted(values: Sequence[float], volumes: Sequence[float]) -> float:
    return sum(float(a) * float(v) for a, v in zip(values, volumes))


def _percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (position - lower) * (ordered[upper] - ordered[lower])


def _make_output_writer(path: Path | None, append: bool):
    if path is None:
        return None, None
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a" if append else "w", newline="", encoding="utf-8")
    writer = csv.writer(handle)
    if not append or path.stat().st_size == 0:
        writer.writerow(["time_s", "radius_cm", "temperature_K", "temperature_C", "moisture_kg_kg"])
    return handle, writer


def _truncate_csv_after_time(path: Path | None, time_s: float) -> None:
    """Reconcile append-only evidence with the state recorded by a checkpoint."""
    if path is None or not path.exists():
        return
    temporary = tempfile.NamedTemporaryFile(mode="w", newline="", encoding="utf-8", dir=path.parent, prefix=f"{path.stem}.reconcile-", suffix=path.suffix, delete=False)
    temporary_path = Path(temporary.name)
    try:
        with path.open(newline="", encoding="utf-8") as source:
            reader = csv.reader(source)
            writer = csv.writer(temporary)
            header = next(reader, None)
            if header is None:
                return
            writer.writerow(header)
            time_index = header.index("time_s")
            for row in reader:
                if row and float(row[time_index]) <= time_s + 1.0e-9:
                    writer.writerow(row)
        temporary.close()
        os.replace(temporary_path, path)
    finally:
        if not temporary.closed:
            temporary.close()
        if temporary_path.exists():
            temporary_path.unlink()


def _official_indices(grid) -> Tuple[int, ...]:
    indices = []
    for radius_cm in (index * 0.1 for index in range(21)):
        index = min(range(len(grid.nodes_m)), key=lambda i: abs(grid.nodes_m[i] * 100.0 - radius_cm))
        if abs(grid.nodes_m[index] * 100.0 - radius_cm) > 1.0e-10:
            raise ValueError(f"official output radius {radius_cm:g} cm is not an explicit grid node")
        indices.append(index)
    return tuple(indices)


@dataclass
class OutputSampler:
    """Stream only the official 1 s × 21-radius Q2 samples."""

    writer: object
    grid: object
    indices: Tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if not self.indices:
            self.indices = _official_indices(self.grid)

    def write(self, time_s: float, temperature_k: Sequence[float], moisture: Sequence[float]) -> None:
        _write_sample(self.writer, time_s, self.grid, temperature_k, moisture, self.indices)


def _write_sample(writer, time_s: float, grid, temperature_k: Sequence[float], moisture: Sequence[float], indices: Sequence[int] | None = None) -> None:
    if writer is None:
        return
    selected = tuple(range(len(grid.nodes_m))) if indices is None else tuple(indices)
    for index in selected:
        radius_m = grid.nodes_m[index]
        temperature = temperature_k[index]
        concentration = moisture[index]
        writer.writerow([f"{time_s:.12g}", f"{radius_m * 100.0:.12g}", repr(float(temperature)), repr(float(temperature - 273.15)), repr(float(concentration))])


def _write_diag(writer, row: StepDiagnostic) -> None:
    if writer is None:
        return
    writer.writerow([
        repr(row.time_s), row.scheme, repr(row.environment_temperature_c), repr(row.environment_moisture_kg_kg), row.picard_iterations,
        repr(row.temperature_residual), repr(row.moisture_residual),
        repr(row.temperature_linear_residual), repr(row.moisture_linear_residual),
        repr(row.surface_heat_internal_w_m2), repr(row.surface_heat_robin_w_m2), repr(row.surface_heat_boundary_residual_w_m2),
        repr(row.surface_moisture_internal_kg_m2_s), repr(row.surface_moisture_robin_kg_m2_s), repr(row.surface_moisture_boundary_residual_kg_m2_s),
        repr(row.surface_k_w_m_k), repr(row.surface_D_m2_s),
        repr(row.mass_step_residual), repr(row.heat_step_residual_j),
        json.dumps(row.property_min, sort_keys=True), json.dumps(row.property_max, sort_keys=True),
        json.dumps(row.picard_history), repr(row.temperature_min_k), repr(row.temperature_max_k),
        repr(row.moisture_min_kg_kg), repr(row.moisture_max_kg_kg),
        repr(row.center_heat_flux_w_m2), repr(row.center_moisture_flux_kg_m2_s),
    ])


def save_checkpoint(path: str | Path, *, config: Q2RunConfig, env: EnvironmentProvider, grid, time_s: float, temperature_k: Sequence[float], moisture: Sequence[float], previous_temperature_k: Sequence[float] | None, previous_moisture: Sequence[float] | None, previous_step_s: float | None = None, output_cursor: float, diagnostics: Sequence[StepDiagnostic], steps_completed: int | None = None) -> Path:
    """Write a versioned JSON checkpoint without storing the full trajectory."""

    path = resolve_project_path(path)
    if path.suffix.lower() != ".json":
        raise ValueError("Q2 checkpoint path must use .json")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "format": "Q2_CHECKPOINT_V1",
        "time_s": float(time_s),
        "temperature_k": list(map(float, temperature_k)),
        "moisture_kg_kg": list(map(float, moisture)),
        "previous_temperature_k": None if previous_temperature_k is None else list(map(float, previous_temperature_k)),
        "previous_moisture_kg_kg": None if previous_moisture is None else list(map(float, previous_moisture)),
        "previous_step_s": None if previous_step_s is None else float(previous_step_s),
        "output_cursor_s": float(output_cursor),
        "grid_nodes_m": list(map(float, grid.nodes_m)),
        "config": config.as_dict(),
        "environment": {
            "source_path": env.source_path,
            "source_sha256": env.source_sha256,
            "method": env.method,
            "post_attachment_mode": env.post_attachment_mode,
            "post_temperature_c": env.post_temperature_c,
            "post_moisture_kg_kg": env.post_moisture_kg_kg,
        },
        "code_commit_sha": _git_sha(),
        "diagnostics": {
            "steps_completed": len(diagnostics) if steps_completed is None else int(steps_completed),
            "last_picard_iterations": diagnostics[-1].picard_iterations if diagnostics else None,
            "last_temperature_residual": diagnostics[-1].temperature_residual if diagnostics else None,
            "last_moisture_residual": diagnostics[-1].moisture_residual if diagnostics else None,
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _load_checkpoint(path: str | Path, config: Q2RunConfig, env: EnvironmentProvider, grid):
    path = resolve_project_path(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("format") != "Q2_CHECKPOINT_V1":
        raise ValueError("unsupported Q2 checkpoint format")
    if payload["config"] != config.as_dict():
        raise ValueError("checkpoint config does not match the requested run")
    if payload["environment"].get("source_sha256") != env.source_sha256:
        raise ValueError("checkpoint Attachment 1 hash does not match")
    if tuple(payload["grid_nodes_m"]) != tuple(grid.nodes_m):
        raise ValueError("checkpoint grid does not match the requested run")
    return payload


def run_q2(
    config: Q2RunConfig,
    *,
    record_times: Iterable[float] = (),
    output_path: str | Path | None = None,
    diagnostics_path: str | Path | None = None,
    checkpoint_path: str | Path | None = None,
    restart_path: str | Path | None = None,
    stop_time_s: float | None = None,
    passive_event_threshold_kg_kg: float | None = None,
    diagnostics_interval_s: float | None = None,
) -> Q2RunResult:
    """Run Q2-M1 with streamed 1-second samples and compact diagnostics."""

    env = EnvironmentProvider.from_attachment1(
        config.input_path,
        method=config.interpolation,
        post_attachment_mode=config.post_attachment_mode,
        post_temperature_c=config.post_temperature_c,
        post_moisture_kg_kg=config.post_moisture_kg_kg,
    )
    grid = grid_for_config(config)
    n = len(grid.nodes_m)
    params = config.parameters
    volumes = radial_control_volume_factors(grid)
    geometry = 2.0 * math.pi * params.length_m
    requested = tuple(sorted(set(float(value) for value in record_times)))
    run_end = float(config.end_time_s if stop_time_s is None else stop_time_s)
    if run_end <= 0 or run_end > config.end_time_s + 1.0e-10:
        raise ValueError("stop_time_s must be in (0, end_time_s]")
    if abs(run_end / config.time_step_s - round(run_end / config.time_step_s)) > 1.0e-10:
        raise ValueError("stop_time_s must be an integer number of time steps")
    if any(value < -1e-12 or value > run_end + 1e-12 for value in requested):
        raise ValueError("record_times must lie inside the requested run horizon")
    if passive_event_threshold_kg_kg is not None and not math.isfinite(passive_event_threshold_kg_kg):
        raise ValueError("passive event threshold must be finite")
    if diagnostics_interval_s is not None and (diagnostics_interval_s <= 0.0 or not math.isfinite(diagnostics_interval_s)):
        raise ValueError("diagnostics_interval_s must be positive when provided")

    initial_temperature = [params.initial_temperature_c + 273.15] * n
    initial_moisture = [params.initial_moisture_kg_kg] * n
    previous_temperature = None
    previous_moisture = None
    current_time = 0.0
    start_time = 0.0
    previous_step_s = None
    if restart_path is not None:
        payload = _load_checkpoint(restart_path, config, env, grid)
        current_time = float(payload["time_s"])
        start_time = current_time
        initial_temperature = list(map(float, payload["temperature_k"]))
        initial_moisture = list(map(float, payload["moisture_kg_kg"]))
        previous_temperature = None if payload["previous_temperature_k"] is None else list(map(float, payload["previous_temperature_k"]))
        previous_moisture = None if payload["previous_moisture_kg_kg"] is None else list(map(float, payload["previous_moisture_kg_kg"]))
        previous_step_s = payload.get("previous_step_s")
        if current_time >= run_end - 1.0e-12:
            raise ValueError("restart checkpoint is already at or beyond the requested end")
    _finite_vector(initial_temperature, "initial temperature")
    _finite_vector(initial_moisture, "initial moisture")

    out_path = None if output_path is None else resolve_project_path(output_path)
    diag_path = None if diagnostics_path is None else resolve_project_path(diagnostics_path)
    if restart_path is not None:
        checkpoint_cursor = float(payload.get("output_cursor_s", current_time))
        _truncate_csv_after_time(out_path, checkpoint_cursor)
        _truncate_csv_after_time(diag_path, checkpoint_cursor)
    append = restart_path is not None and out_path is not None and out_path.exists()
    out_handle, out_writer = _make_output_writer(out_path, append)
    diag_handle = None
    diag_writer = None
    if diag_path is not None:
        diag_path.parent.mkdir(parents=True, exist_ok=True)
        diag_handle = diag_path.open("a" if restart_path is not None and diag_path.exists() else "w", newline="", encoding="utf-8")
        diag_writer = csv.writer(diag_handle)
        if diag_handle.tell() == 0:
            diag_writer.writerow([
                "time_s", "scheme", "environment_temperature_c", "environment_moisture_kg_kg", "picard_iterations", "temperature_residual", "moisture_residual",
                "temperature_linear_residual", "moisture_linear_residual", "surface_heat_internal_w_m2", "surface_heat_robin_w_m2", "surface_heat_boundary_residual_w_m2",
                "surface_moisture_internal_kg_m2_s", "surface_moisture_robin_kg_m2_s", "surface_moisture_boundary_residual_kg_m2_s",
                "surface_k_w_m_k", "surface_D_m2_s",
                "mass_step_residual", "heat_step_residual_j", "property_min_json", "property_max_json", "picard_history_json",
                "temperature_min_k", "temperature_max_k", "moisture_min_kg_kg", "moisture_max_kg_kg",
                "center_heat_flux_w_m2", "center_moisture_flux_kg_m2_s",
            ])
    snapshots: Dict[float, Tuple[Tuple[float, ...], Tuple[float, ...]]] = {}
    diagnostics: List[StepDiagnostic] = []
    retain_step_diagnostics = diag_path is None
    picard_count_history: List[int] = []
    last_diagnostic = None
    passive_event_bracket = None
    previous_event_value = None
    aggregate = {
        "temperature_residual_max": 0.0, "moisture_residual_max": 0.0,
        "temperature_boundary_residual_max_w_m2": 0.0, "moisture_boundary_residual_max_kg_m2_s": 0.0,
        "mass_step_residual_max": 0.0, "heat_step_residual_max_j": 0.0,
        "temperature_linear_residual_max": 0.0, "moisture_linear_residual_max": 0.0,
        "temperature_boundary_residual_at_last_step_w_m2": 0.0, "moisture_boundary_residual_at_last_step_kg_m2_s": 0.0,
        "center_heat_flux_max_abs_w_m2": 0.0, "center_moisture_flux_max_abs_kg_m2_s": 0.0,
        "temperature_min_k": float("inf"), "temperature_max_k": float("-inf"),
        "moisture_min_kg_kg": float("inf"), "moisture_max_kg_kg": float("-inf"),
    }
    property_minimums = {key: float("inf") for key in ("rho", "cp", "k", "D")}
    property_maximums = {key: float("-inf") for key in ("rho", "cp", "k", "D")}
    sampler = OutputSampler(out_writer, grid) if out_writer is not None else None
    if abs(current_time) < 1.0e-12 and 0.0 in requested:
        snapshots[0.0] = (tuple(initial_temperature), tuple(initial_moisture))
    if abs(current_time) < 1.0e-12:
        if sampler is not None:
            sampler.write(0.0, initial_temperature, initial_moisture)

    T = initial_temperature
    C = initial_moisture
    step_count = int(round(current_time / config.time_step_s))
    while current_time < run_end - 1.0e-12:
        old_T = T
        old_C = C
        old_previous_T = previous_temperature
        old_previous_C = previous_moisture
        step_s = config.time_step_s
        if config.early_time_step_s is not None and current_time < config.early_time_end_s - 1.0e-12:
            step_s = config.early_time_step_s
            if current_time + step_s > config.early_time_end_s:
                step_s = config.early_time_end_s - current_time
        next_time = current_time + step_s
        env_temp_c, env_moisture = env.at(next_time)
        env_temp_k = env_temp_c + 273.15
        at_environment_transition = abs(current_time - env.last_time_s) <= 1.0e-9
        at_step_size_transition = previous_step_s is not None and abs(step_s - previous_step_s) > 1.0e-12
        transition_restart = (config.reset_bdf2_at_environment_transition and at_environment_transition) or at_step_size_transition
        scheme = "bdf2" if config.scheme == "bdf2" and old_previous_T is not None and not transition_restart else "be"
        T_guess = list(old_T)
        C_guess = list(old_C)
        picard_history: List[Tuple[float, float]] = []
        converged = False
        last_heat_system = last_moisture_system = None
        for iteration in range(config.picard_max_iterations):
            density = density_array(C_guess)
            heat_capacity = [rho * value for rho, value in zip(density, cp_array(C_guess))]
            k_nodes = conductivity_array(C_guess)
            k_faces = interface_values(k_nodes, config.interface_mean)
            heat_system = assemble_variable_radial_system(old_T, grid, step_s, heat_capacity, k_faces, params.heat_transfer_w_m2_k, env_temp_k, scheme=scheme, previous_values=old_previous_T)
            T_linear = solve_system(heat_system)
            d_nodes = diffusivity_array(C_guess, T_linear)
            d_faces = interface_values(d_nodes, config.interface_mean)
            moisture_system = assemble_variable_radial_system(old_C, grid, step_s, [1.0] * n, d_faces, params.mass_transfer_m_s, env_moisture, scheme=scheme, previous_values=old_previous_C)
            C_linear = solve_system(moisture_system)
            if any(value <= 0.0 or not math.isfinite(value) for value in C_linear):
                raise Q2NonConvergenceError(f"non-positive/non-finite moisture at t={next_time:g} s, Picard iteration {iteration + 1}")
            relaxation = config.picard_relaxation
            T_next = [relaxation * new + (1.0 - relaxation) * old for new, old in zip(T_linear, T_guess)]
            C_next = [relaxation * new + (1.0 - relaxation) * old for new, old in zip(C_linear, C_guess)]
            t_residual = _scale_residual(T_next, T_guess)
            c_residual = _scale_residual(C_next, C_guess)
            picard_history.append((t_residual, c_residual))
            T_guess, C_guess = T_next, C_next
            last_heat_system, last_moisture_system = heat_system, moisture_system
            if max(t_residual, c_residual) <= config.picard_tolerance:
                converged = True
                break
        if not converged:
            raise Q2NonConvergenceError(f"coupled Picard failed at t={next_time:g} s after {config.picard_max_iterations} iterations; history={picard_history}")

        T, C = T_guess, C_guess
        density = density_array(C)
        heat_capacity = [rho * value for rho, value in zip(density, cp_array(C))]
        k_nodes = conductivity_array(C)
        k_faces = interface_values(k_nodes, config.interface_mean)
        d_nodes = diffusivity_array(C, T)
        d_faces = interface_values(d_nodes, config.interface_mean)
        heat_internal, heat_robin, heat_bc = boundary_flux_pair(T[-1], T[-2], grid, k_faces[-1], params.heat_transfer_w_m2_k, env_temp_k)
        moisture_internal, moisture_robin, moisture_bc = boundary_flux_pair(C[-1], C[-2], grid, d_faces[-1], params.mass_transfer_m_s, env_moisture)
        if scheme == "bdf2":
            t_difference = [1.5 * T[i] - 2.0 * old_T[i] + 0.5 * old_previous_T[i] for i in range(n)]
            c_difference = [1.5 * C[i] - 2.0 * old_C[i] + 0.5 * old_previous_C[i] for i in range(n)]
            balance_scale = 2.0 * step_s
        else:
            t_difference = [T[i] - old_T[i] for i in range(n)]
            c_difference = [C[i] - old_C[i] for i in range(n)]
            balance_scale = step_s
        mass_step_residual = geometry * (_weighted(c_difference, volumes) + params.radius_m * moisture_robin * balance_scale)
        heat_step_residual = geometry * (_weighted([heat_capacity[i] * t_difference[i] for i in range(n)], volumes) + params.radius_m * heat_robin * balance_scale)
        property_values = {
            "rho": density,
            "cp": cp_array(C),
            "k": k_nodes,
            "D": d_nodes,
        }
        property_min = {key: min(values) for key, values in property_values.items()}
        property_max = {key: max(values) for key, values in property_values.items()}
        row = StepDiagnostic(
            time_s=next_time, scheme=scheme, environment_temperature_c=env_temp_c, environment_moisture_kg_kg=env_moisture,
            picard_iterations=len(picard_history),
            temperature_residual=picard_history[-1][0], moisture_residual=picard_history[-1][1],
            temperature_linear_residual=tridiagonal_residual_linf(last_heat_system, T),
            moisture_linear_residual=tridiagonal_residual_linf(last_moisture_system, C),
            surface_heat_internal_w_m2=heat_internal, surface_heat_robin_w_m2=heat_robin, surface_heat_boundary_residual_w_m2=heat_bc,
            surface_moisture_internal_kg_m2_s=moisture_internal, surface_moisture_robin_kg_m2_s=moisture_robin, surface_moisture_boundary_residual_kg_m2_s=moisture_bc,
            surface_k_w_m_k=k_nodes[-1], surface_D_m2_s=d_nodes[-1],
            mass_step_residual=mass_step_residual, heat_step_residual_j=heat_step_residual,
            property_min=property_min, property_max=property_max, picard_history=tuple(picard_history),
            temperature_min_k=min(T), temperature_max_k=max(T),
            moisture_min_kg_kg=min(C), moisture_max_kg_kg=max(C),
            # The radial face at r=0 has zero area, so the discrete center
            # flux is identically zero and is retained explicitly for audit.
            center_heat_flux_w_m2=0.0, center_moisture_flux_kg_m2_s=0.0,
        )
        if retain_step_diagnostics:
            diagnostics.append(row)
        picard_count_history.append(row.picard_iterations)
        last_diagnostic = row
        aggregate["temperature_residual_max"] = max(aggregate["temperature_residual_max"], row.temperature_residual)
        aggregate["moisture_residual_max"] = max(aggregate["moisture_residual_max"], row.moisture_residual)
        aggregate["temperature_boundary_residual_max_w_m2"] = max(aggregate["temperature_boundary_residual_max_w_m2"], abs(row.surface_heat_boundary_residual_w_m2))
        aggregate["moisture_boundary_residual_max_kg_m2_s"] = max(aggregate["moisture_boundary_residual_max_kg_m2_s"], abs(row.surface_moisture_boundary_residual_kg_m2_s))
        aggregate["mass_step_residual_max"] = max(aggregate["mass_step_residual_max"], abs(row.mass_step_residual))
        aggregate["heat_step_residual_max_j"] = max(aggregate["heat_step_residual_max_j"], abs(row.heat_step_residual_j))
        aggregate["temperature_linear_residual_max"] = max(aggregate["temperature_linear_residual_max"], row.temperature_linear_residual)
        aggregate["moisture_linear_residual_max"] = max(aggregate["moisture_linear_residual_max"], row.moisture_linear_residual)
        aggregate["temperature_boundary_residual_at_last_step_w_m2"] = row.surface_heat_boundary_residual_w_m2
        aggregate["moisture_boundary_residual_at_last_step_kg_m2_s"] = row.surface_moisture_boundary_residual_kg_m2_s
        aggregate["center_heat_flux_max_abs_w_m2"] = max(aggregate["center_heat_flux_max_abs_w_m2"], abs(row.center_heat_flux_w_m2))
        aggregate["center_moisture_flux_max_abs_kg_m2_s"] = max(aggregate["center_moisture_flux_max_abs_kg_m2_s"], abs(row.center_moisture_flux_kg_m2_s))
        aggregate["temperature_min_k"] = min(aggregate["temperature_min_k"], row.temperature_min_k)
        aggregate["temperature_max_k"] = max(aggregate["temperature_max_k"], row.temperature_max_k)
        aggregate["moisture_min_kg_kg"] = min(aggregate["moisture_min_kg_kg"], row.moisture_min_kg_kg)
        aggregate["moisture_max_kg_kg"] = max(aggregate["moisture_max_kg_kg"], row.moisture_max_kg_kg)
        for key in property_minimums:
            property_minimums[key] = min(property_minimums[key], row.property_min[key])
            property_maximums[key] = max(property_maximums[key], row.property_max[key])
        if diagnostics_interval_s is None or abs(next_time / diagnostics_interval_s - round(next_time / diagnostics_interval_s)) < 1.0e-9:
            _write_diag(diag_writer, row)
        if diag_handle is not None:
            diag_handle.flush()
        current_time = next_time
        if passive_event_threshold_kg_kg is not None:
            event_value = row.moisture_max_kg_kg - passive_event_threshold_kg_kg
            # Q2's observer is deliberately directional.  A zero touch is not
            # a crossing; only the first transition from g_prev >= 0 to
            # g_now < 0 is eligible for the saved bracket.  This keeps the
            # Q2 horizon controller separate from Q3 root refinement.
            if passive_event_bracket is None and previous_event_value is not None and previous_event_value >= 0.0 and event_value < 0.0:
                passive_event_bracket = (current_time - step_s, current_time)
            previous_event_value = event_value
        step_count += 1
        previous_temperature = list(old_T)
        previous_moisture = list(old_C)
        previous_step_s = step_s
        if abs(current_time / config.output_interval_s - round(current_time / config.output_interval_s)) < 1.0e-9:
            if sampler is not None:
                sampler.write(current_time, T, C)
        for target in requested:
            if abs(target - current_time) < 1.0e-9:
                snapshots[round(target, 12)] = (tuple(T), tuple(C))

    if out_handle is not None:
        out_handle.close()
    if diag_handle is not None:
        diag_handle.close()
    saved_checkpoint = ""
    if checkpoint_path is not None:
        saved_checkpoint = str(save_checkpoint(checkpoint_path, config=config, env=env, grid=grid, time_s=current_time, temperature_k=T, moisture=C, previous_temperature_k=previous_temperature, previous_moisture=previous_moisture, previous_step_s=previous_step_s, output_cursor=current_time, diagnostics=diagnostics, steps_completed=step_count))
    if requested and any(abs(target - current_time) < 1.0e-9 for target in requested):
        snapshots[round(current_time, 12)] = (tuple(T), tuple(C))
    diagnostic_summary = {
        "steps": len(picard_count_history),
        "picard_min": min(picard_count_history, default=0),
        "picard_median": median(picard_count_history) if picard_count_history else float("nan"),
        "picard_p95": _percentile(picard_count_history, 0.95),
        "picard_max": max(picard_count_history, default=0),
        **aggregate,
        **{f"{key}_min": value for key, value in property_minimums.items()},
        **{f"{key}_max": value for key, value in property_maximums.items()},
    }
    return Q2RunResult(
        config=config, grid=grid, times_s=tuple(row.time_s for row in diagnostics), snapshots=snapshots,
        diagnostics=tuple(diagnostics), diagnostic_summary=diagnostic_summary,
        picard_count_history=tuple(picard_count_history), last_diagnostic=last_diagnostic,
        final_temperature_k=tuple(T), final_moisture=tuple(C), output_path=str(out_path or ""), diagnostics_path=str(diag_path or ""),
        checkpoint_path=saved_checkpoint, passive_event_bracket_s=passive_event_bracket,
        complete=abs(current_time - config.end_time_s) < 1.0e-9,
    )


def summarize_picard(result: Q2RunResult) -> Dict[str, float]:
    if result.diagnostic_summary:
        return {key: result.diagnostic_summary[key] for key in ("steps", "picard_min", "picard_median", "picard_p95", "picard_max", "temperature_residual_max", "moisture_residual_max")}
    counts = result.picard_counts
    temp_residuals = [row.temperature_residual for row in result.diagnostics]
    moisture_residuals = [row.moisture_residual for row in result.diagnostics]
    return {
        "steps": len(counts), "picard_min": min(counts, default=0), "picard_median": median(counts) if counts else float("nan"),
        "picard_p95": _percentile(counts, 0.95), "picard_max": max(counts, default=0),
        "temperature_residual_max": max(temp_residuals, default=float("nan")), "moisture_residual_max": max(moisture_residuals, default=float("nan")),
    }
