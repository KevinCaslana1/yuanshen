"""Run and audit the frozen Q1 production configuration.

This script is intentionally separate from candidate generation.  It runs the
selected solver twice from a clean experiment directory, stores the complete
internal fields in compressed provenance files, and writes only audit data
under ``experiments/Q1_FREEZE_RUN``.  It never writes an official or candidate
workbook.
"""

from __future__ import annotations

import dataclasses
import gzip
import hashlib
import json
import math
import os
import pickle
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Sequence, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_inputs import EXPECTED, sha256
from src.common.numerics import NonuniformRadialGrid
from src.common.paths import assert_not_official_output
from src.q1.config import DEFAULT_PARAMETERS, Q1RunConfig
from src.q1.inputs import BoundaryProvider
from src.q1.model import radial_control_volume_factors
from src.q1.solver import Q1Result, run_m1_bdf2


FREEZE_DIR = ROOT / "experiments" / "Q1_FREEZE_RUN"
OUTPUT_POSITIONS_M = tuple(index * 0.001 for index in range(21))
PAPER_TIMES_S = (100, 300, 600, 900, 1200, 1500, 1800)
PAPER_POSITIONS_M = (0.0, 0.005, 0.01, 0.015, 0.02)
FROZEN_CLUSTER_POWER = 2.0
FROZEN_CONFIG = Q1RunConfig(
    end_time_s=1800.0,
    time_step_s=0.25,
    n_intervals=320,
    interpolation="linear",
    surface_boundary="robin",
)


def _jsonable_config(config: Q1RunConfig) -> Dict[str, Any]:
    values = dataclasses.asdict(config)
    values["input_path"] = str(config.input_path)
    return values


def _grid_payload(result: Q1Result) -> Dict[str, Any]:
    grid = result.grid
    payload: Dict[str, Any] = {
        "type": type(grid).__name__,
        "radius_m": grid.radius_m,
        "n_intervals": grid.n_intervals,
        "nodes_m": list(grid.nodes_m),
    }
    if isinstance(grid, NonuniformRadialGrid):
        payload.update({"min_dr_m": grid.min_dr_m, "max_dr_m": grid.max_dr_m})
    else:
        payload["dr_m"] = grid.dr_m
    return payload


def _result_payload(result: Q1Result) -> Dict[str, Any]:
    return {
        "schema_version": "Q1_FREEZE_INTERNAL_OUTPUT_V1",
        "config": _jsonable_config(result.config),
        "grid": _grid_payload(result),
        "times_s": list(result.times_s),
        "temperatures_k": [list(row) for row in result.temperatures_k],
        "moistures_kg_kg": [list(row) for row in result.moistures_kg_kg],
        "picard_iterations": list(result.picard_iterations),
        "heat_flux_in_w_m2": list(result.heat_flux_in_w_m2),
        "moisture_flux_out_m_s": list(result.moisture_flux_out_m_s),
    }


def _write_internal_reference(result: Q1Result, path: Path) -> str:
    assert_not_official_output(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _result_payload(result)
    with gzip.open(path, "wb", compresslevel=6) as stream:
        pickle.dump(payload, stream, protocol=pickle.HIGHEST_PROTOCOL)
    return sha256(path)


def _position_indices(result: Q1Result, positions_m: Sequence[float]) -> Tuple[int, ...]:
    indices = []
    for position in positions_m:
        index = min(range(len(result.grid.nodes_m)), key=lambda candidate: abs(result.grid.nodes_m[candidate] - position))
        if abs(result.grid.nodes_m[index] - position) > 1.0e-12:
            raise ValueError(f"frozen grid does not contain official output position {position} m")
        indices.append(index)
    return tuple(indices)


def _time_index(result: Q1Result, time_s: float) -> int:
    index = min(range(len(result.times_s)), key=lambda candidate: abs(result.times_s[candidate] - time_s))
    if abs(result.times_s[index] - time_s) > 1.0e-9:
        raise ValueError(f"frozen time grid does not contain required output time {time_s} s")
    return index


def _weighted(values: Iterable[float], factors: Sequence[float], capacity: float = 1.0) -> float:
    geometry_factor = 2.0 * math.pi * DEFAULT_PARAMETERS.length_m
    return geometry_factor * capacity * sum(value * factor for value, factor in zip(values, factors))


def _balance_stats(result: Q1Result) -> Dict[str, float]:
    factors = radial_control_volume_factors(result.grid)
    heat_capacity = DEFAULT_PARAMETERS.density_kg_m3 * DEFAULT_PARAMETERS.heat_capacity_j_kg_k
    max_mass = 0.0
    max_energy = 0.0
    for index in range(1, len(result.times_s)):
        dt_s = result.times_s[index] - result.times_s[index - 1]
        if index == 1:
            temperature_storage = _weighted(
                (new - old for new, old in zip(result.temperatures_k[index], result.temperatures_k[index - 1])),
                factors,
                heat_capacity,
            )
            moisture_storage = _weighted(
                (new - old for new, old in zip(result.moistures_kg_kg[index], result.moistures_kg_kg[index - 1])),
                factors,
            )
        else:
            temperature_storage = _weighted(
                (
                    1.5 * new - 2.0 * old + 0.5 * previous
                    for new, old, previous in zip(
                        result.temperatures_k[index],
                        result.temperatures_k[index - 1],
                        result.temperatures_k[index - 2],
                    )
                ),
                factors,
                heat_capacity,
            )
            moisture_storage = _weighted(
                (
                    1.5 * new - 2.0 * old + 0.5 * previous
                    for new, old, previous in zip(
                        result.moistures_kg_kg[index],
                        result.moistures_kg_kg[index - 1],
                        result.moistures_kg_kg[index - 2],
                    )
                ),
                factors,
            )
        surface_area_factor = 2.0 * math.pi * DEFAULT_PARAMETERS.length_m * result.grid.radius_m
        mass_residual = moisture_storage + surface_area_factor * result.moisture_flux_out_m_s[index] * dt_s
        energy_residual = temperature_storage - surface_area_factor * result.heat_flux_in_w_m2[index] * dt_s
        max_mass = max(max_mass, abs(mass_residual))
        max_energy = max(max_energy, abs(energy_residual))
    return {
        "max_mass_balance_residual": max_mass,
        "max_energy_balance_residual": max_energy,
    }


def _sample_rows(result: Q1Result, times_s: Sequence[int], positions_m: Sequence[float]) -> Dict[str, list[list[float]]]:
    time_indices = [_time_index(result, float(time_s)) for time_s in times_s]
    position_indices = _position_indices(result, positions_m)
    temperatures = []
    moistures = []
    for time_index in time_indices:
        temperatures.append([
            result.temperatures_k[time_index][position_index] - 273.15
            for position_index in position_indices
        ])
        moistures.append([
            result.moistures_kg_kg[time_index][position_index]
            for position_index in position_indices
        ])
    return {"temperature_c": temperatures, "moisture_kg_kg": moistures}


def _round_half_up(value: float) -> str:
    from decimal import Decimal, ROUND_HALF_UP

    return format(Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP), "f")


def _run_metrics(result: Q1Result, runtime_seconds: float, reference_path: Path, reference_hash: str) -> Dict[str, Any]:
    balance = _balance_stats(result)
    positions = _position_indices(result, OUTPUT_POSITIONS_M)
    all_temperatures = [value for row in result.temperatures_k for value in row]
    all_moistures = [value for row in result.moistures_kg_kg for value in row]
    paper = _sample_rows(result, PAPER_TIMES_S, PAPER_POSITIONS_M)
    formal = _sample_rows(result, tuple(range(1, 1801)), OUTPUT_POSITIONS_M)
    return {
        "status": "PASS",
        "runtime_seconds": runtime_seconds,
        "internal_step_count": len(result.times_s) - 1,
        "internal_output_shape": {
            "time_layers": len(result.times_s),
            "spatial_nodes": len(result.grid.nodes_m),
            "temperature_unit": "K",
            "moisture_unit": "kg/kg",
        },
        "formal_output_shape": {"times": 1800, "positions": 21, "cells_per_field": 37800},
        "official_output_positions_present": len(positions) == 21,
        "formal_output_times_present": len(formal["temperature_c"]) == 1800,
        "temperature_range_c": [min(all_temperatures) - 273.15, max(all_temperatures) - 273.15],
        "moisture_range_kg_kg": [min(all_moistures), max(all_moistures)],
        "picard_iteration_stats": {
            "steps": len(result.picard_iterations) - 1,
            "min": min(result.picard_iterations[1:]),
            "max": max(result.picard_iterations[1:]),
            "mean": sum(result.picard_iterations[1:]) / (len(result.picard_iterations) - 1),
        },
        "balance_stats": balance,
        "internal_output_reference": {
            "path": str(reference_path.relative_to(ROOT)),
            "sha256": reference_hash,
            "format": "gzip-pickle payload with complete internal time layers and spatial nodes",
        },
        "paper_tables": paper,
        "paper_tables_rounded_half_up": {
            field: [[_round_half_up(value) for value in row] for row in rows]
            for field, rows in paper.items()
        },
    }


def _validation(metrics: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "finite_and_bounded_temperature": all(math.isfinite(value) for value in metrics["temperature_range_c"]),
        "finite_and_nonnegative_moisture": all(math.isfinite(value) and value >= 0.0 for value in metrics["moisture_range_kg_kg"]),
        "formal_output_shape": metrics["formal_output_shape"] == {"times": 1800, "positions": 21, "cells_per_field": 37800},
        "formal_output_times_present": metrics["formal_output_times_present"],
        "official_output_positions_present": metrics["official_output_positions_present"],
        "picard_converged_within_config": metrics["picard_iteration_stats"]["max"] <= FROZEN_CONFIG.picard_max_iterations,
        "mass_balance_abs_le_1e-10": metrics["balance_stats"]["max_mass_balance_residual"] <= 1.0e-10,
        "energy_balance_abs_le_1e-5": metrics["balance_stats"]["max_energy_balance_residual"] <= 1.0e-5,
    }
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "observed": {
        "max_mass_balance_residual": metrics["balance_stats"]["max_mass_balance_residual"],
        "max_energy_balance_residual": metrics["balance_stats"]["max_energy_balance_residual"],
        "max_picard_iterations": metrics["picard_iteration_stats"]["max"],
    }}


def _environment() -> Dict[str, Any]:
    return {
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "os_name": os.name,
        "cwd": str(Path.cwd()),
        "implementation": platform.python_implementation(),
    }


def main() -> int:
    started = time.perf_counter()
    FREEZE_DIR.mkdir(parents=True, exist_ok=False)
    boundary_path = ROOT / FROZEN_CONFIG.input_path
    boundary = BoundaryProvider.from_attachment1(boundary_path)
    boundary = BoundaryProvider(boundary.times_s, boundary.temperatures_c, boundary.moistures_kg_kg, method=FROZEN_CONFIG.interpolation)
    code_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    input_hashes = {relative: sha256(ROOT / relative) for relative in EXPECTED}

    config_payload = {
        "status": "Q1_PRODUCTION_CONFIG_FROZEN",
        "selection_basis": "lowest-cost passing candidate from EXP-Q1-FULL-SPATIAL and EXP-Q1-FULL-TEMPORAL",
        "config": _jsonable_config(FROZEN_CONFIG),
        "parameters": dataclasses.asdict(DEFAULT_PARAMETERS),
        "cluster_power": FROZEN_CLUSTER_POWER,
        "startup": "one standard BE step at dt=0.25 s, then fixed-step BDF2",
        "grid": "conservative radial FVM; boundary-clustered grid; explicit official output nodes",
        "physical_model": "Q1 M1 frozen: 1D radial, fixed radius, constant heat properties, nonlinear D(C), Robin heat/mass, original initial condition, Attachment 1 linear interpolation",
        "units": {
            "time_internal": "s",
            "radius_internal": "m",
            "temperature_internal": "K",
            "temperature_output": "°C",
            "moisture": "kg/kg",
            "heat_flux": "W/m²",
            "moisture_flux": "m/s",
        },
        "code_commit": code_commit,
        "input_hashes": input_hashes,
        "environment": _environment(),
    }
    (FREEZE_DIR / "config.json").write_text(json.dumps(config_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (FREEZE_DIR / "environment.json").write_text(json.dumps(_environment(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (FREEZE_DIR / "input_hashes.json").write_text(json.dumps(input_hashes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    run_records = []
    for run_number in (1, 2):
        run_started = time.perf_counter()
        result = run_m1_bdf2(
            FROZEN_CONFIG,
            boundary,
            DEFAULT_PARAMETERS,
            cluster_power=FROZEN_CLUSTER_POWER,
            required_output_positions_m=OUTPUT_POSITIONS_M,
        )
        runtime_seconds = time.perf_counter() - run_started
        run_dir = FREEZE_DIR / f"run_{run_number}"
        reference_path = run_dir / "internal_output_reference.pkl.gz"
        reference_hash = _write_internal_reference(result, reference_path)
        metrics = _run_metrics(result, runtime_seconds, reference_path, reference_hash)
        validation = _validation(metrics)
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (run_dir / "validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        run_records.append({
            "run": run_number,
            "runtime_seconds": runtime_seconds,
            "reference_path": str(reference_path.relative_to(ROOT)),
            "reference_sha256": reference_hash,
            "validation_status": validation["status"],
            "metrics": metrics,
            "validation": validation,
        })
        del result

    deterministic = {
        "status": "PASS" if run_records[0]["reference_sha256"] == run_records[1]["reference_sha256"] else "FAIL",
        "comparison": "exact SHA-256 equality of complete compressed internal output payloads",
        "run_1_sha256": run_records[0]["reference_sha256"],
        "run_2_sha256": run_records[1]["reference_sha256"],
    }
    payload = {
        "experiment_id": "Q1_FREEZE_RUN",
        "status": "COMPLETED" if all(record["validation_status"] == "PASS" for record in run_records) and deterministic["status"] == "PASS" else "BLOCKED",
        "production_config_status": "Q1_PRODUCTION_CONFIG_FROZEN",
        "code_commit": code_commit,
        "input_hashes": input_hashes,
        "environment": _environment(),
        "accuracy_criterion": "TEAM_NUMERICAL_CRITERION: estimated discretization uncertainty < 5e-5 in °C and kg/kg",
        "rounding_rule": "ROUND_HALF_UP to 4 decimals; auxiliary only",
        "run_count": len(run_records),
        "runs": run_records,
        "determinism": deterministic,
        "runtime_seconds_total": time.perf_counter() - started,
        "candidate_workbook_generated": False,
    }
    (FREEZE_DIR / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (FREEZE_DIR / "validation.json").write_text(json.dumps({
        "status": payload["status"],
        "run_validations": [record["validation"] for record in run_records],
        "determinism": deterministic,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (FREEZE_DIR / "notes.md").write_text(
        "# Q1_FREEZE_RUN\n\n"
        "Production configuration frozen after full-horizon spatial/temporal convergence. "
        "The two run directories contain complete compressed internal outputs; candidate "
        "generation is a separate read-only consumer of `run_1`.\n\n"
        f"Status: `{payload['status']}`\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": payload["status"],
        "production_config_status": payload["production_config_status"],
        "determinism": deterministic,
        "run_validations": [record["validation_status"] for record in run_records],
        "runtime_seconds_total": payload["runtime_seconds_total"],
    }, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
