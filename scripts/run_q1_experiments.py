"""Run the planned Q1 implementation and validation experiments.

This entry point writes only JSON/Markdown evidence under experiments/ and
never creates an official or candidate workbook.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_inputs import sha256
from src.common.numerics import RadialGrid
from src.common.paths import assert_not_official_output
from src.q1.baseline import run_b0
from src.q1.config import DEFAULT_PARAMETERS, Q1RunConfig
from src.q1.inputs import BoundaryProvider
from src.q1.solver import Q1Result, run_m1, run_m2
from src.q1.validation import validate_m1_result


def _boundary(config: Q1RunConfig) -> BoundaryProvider:
    base = BoundaryProvider.from_attachment1(ROOT / config.input_path)
    return BoundaryProvider(base.times_s, base.temperatures_c, base.moistures_kg_kg, method=config.interpolation)


def _config(**overrides: Any) -> Q1RunConfig:
    values = {
        "end_time_s": 1800.0,
        "time_step_s": 1.0,
        "n_intervals": 80,
        "interpolation": "linear",
        "surface_boundary": "robin",
    }
    values.update(overrides)
    return Q1RunConfig(**values)


def _output_indices(grid: RadialGrid) -> Tuple[int, ...]:
    positions_m = [index * 0.001 for index in range(21)]
    indices = tuple(round(position / grid.dr_m) for position in positions_m)
    if any(index < 0 or index > grid.n_intervals for index in indices):
        raise ValueError("official Q1 output point is outside the solver grid")
    return indices


def _weighted_mean(row: Iterable[float], grid: RadialGrid) -> float:
    from src.q1.model import radial_control_volume_factors

    factors = radial_control_volume_factors(grid)
    return sum(value * factor for value, factor in zip(row, factors)) / sum(factors)


def _m1_summary(result: Q1Result) -> Dict[str, Any]:
    indices = _output_indices(result.grid)
    final_t = result.temperatures_c[-1]
    final_c = result.moistures_kg_kg[-1]
    return {
        "end_time_s": result.times_s[-1],
        "n_intervals": result.grid.n_intervals,
        "dr_m": result.grid.dr_m,
        "final_temperature_c_at_output_grid": [final_t[index] for index in indices],
        "final_moisture_at_output_grid": [final_c[index] for index in indices],
        "final_temperature_mean_c": _weighted_mean(result.temperatures_k[-1], result.grid) - 273.15,
        "final_moisture_mean_kg_kg": _weighted_mean(final_c, result.grid),
        "max_picard_iterations": max(result.picard_iterations),
        "picard_iteration_stats": {
            "steps": len(result.picard_iterations) - 1,
            "min": min(result.picard_iterations[1:]),
            "max": max(result.picard_iterations[1:]),
            "mean": sum(result.picard_iterations[1:]) / (len(result.picard_iterations) - 1),
        },
    }


def _validation_record(result: Q1Result) -> Dict[str, Any]:
    metrics = validate_m1_result(result)
    moisture_values = [value for row in result.moistures_kg_kg for value in row]
    checks = {
        "finite": bool(metrics["finite"]),
        "initial_ok": bool(metrics["initial_ok"]),
        "time_ok": bool(metrics["time_ok"]),
        "mass_balance_abs_le_1e-10": abs(float(metrics["mass_balance_residual"])) <= 1.0e-10,
        "energy_balance_abs_le_1e-5": abs(float(metrics["energy_balance_residual"])) <= 1.0e-5,
        "moisture_nonnegative": min(moisture_values) >= -1.0e-12,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "observed": {
            "max_picard_iterations": metrics["max_picard_iterations"],
            "mass_balance_residual": metrics["mass_balance_residual"],
            "energy_balance_residual": metrics["energy_balance_residual"],
        },
    }


def _max_output_difference(first: Q1Result, second: Q1Result) -> Dict[str, float]:
    first_indices = _output_indices(first.grid)
    second_indices = _output_indices(second.grid)
    if first.times_s[-1] != second.times_s[-1]:
        raise ValueError("comparison requires matching final snapshots")
    t_diff = max(
        abs(first.temperatures_k[-1][left] - second.temperatures_k[-1][right])
        for left, right in zip(first_indices, second_indices)
    )
    c_diff = max(
        abs(first.moistures_kg_kg[-1][left] - second.moistures_kg_kg[-1][right])
        for left, right in zip(first_indices, second_indices)
    )
    return {"max_temperature_difference_k": t_diff, "max_moisture_difference_kg_kg": c_diff}


def _run_m1(config: Q1RunConfig) -> Q1Result:
    return run_m1(config, _boundary(config), DEFAULT_PARAMETERS)


def run_experiment(experiment_id: str) -> Dict[str, Any]:
    started = time.perf_counter()
    validation_result: Dict[str, Any]
    if experiment_id == "EXP-001":
        config = _config(end_time_s=10.0, n_intervals=8)
        result = _run_m1(config)
        metrics = validate_m1_result(result)
        metrics.update(_m1_summary(result))
        metrics.update({"boundary_raw_count": _boundary(config).raw_count, "formal_result_generated": False})
        validation_result = _validation_record(result)
        notes = "Non-formal smoke test. No official or candidate workbook was generated."
        configs = {"smoke": config}
    elif experiment_id == "EXP-002":
        config = _config()
        m1 = _run_m1(config)
        m2 = run_m2(config, _boundary(config), DEFAULT_PARAMETERS)
        b0 = run_b0(config, _boundary(config), DEFAULT_PARAMETERS)
        metrics = {
            "m1": _m1_summary(m1),
            "m2": _m1_summary(m2),
            "b0_final_temperature_c": b0.temperatures_k[-1] - 273.15,
            "b0_final_moisture_kg_kg": b0.moistures_kg_kg[-1],
            "m1_minus_b0_final_mean_temperature_c": _weighted_mean(m1.temperatures_k[-1], m1.grid) - 273.15 - (b0.temperatures_k[-1] - 273.15),
            "m1_minus_b0_final_mean_moisture_kg_kg": _weighted_mean(m1.moistures_kg_kg[-1], m1.grid) - b0.moistures_kg_kg[-1],
            "m1_minus_m2_final_mean_temperature_c": _weighted_mean(m1.temperatures_k[-1], m1.grid) - _weighted_mean(m2.temperatures_k[-1], m2.grid),
            "m1_minus_m2_final_mean_moisture_kg_kg": _weighted_mean(m1.moistures_kg_kg[-1], m1.grid) - _weighted_mean(m2.moistures_kg_kg[-1], m2.grid),
        }
        validation_result = {"m1": _validation_record(m1), "m2": _validation_record(m2)}
        notes = "B0 baseline plus M2 constant-D ablation comparison; it does not select a final model."
        configs = {"m1": config, "m2": config, "b0": config}
    elif experiment_id == "EXP-003":
        runs = {str(dt): _run_m1(_config(time_step_s=dt)) for dt in (1.0, 0.5, 0.25)}
        metrics = {
            "runs": {key: _m1_summary(value) for key, value in runs.items()},
            "dt_1_vs_0_5": _max_output_difference(runs["1.0"], runs["0.5"]),
            "dt_0_5_vs_0_25": _max_output_difference(runs["0.5"], runs["0.25"]),
        }
        validation_result = {key: _validation_record(value) for key, value in runs.items()}
        notes = "Time-step sensitivity; differences are reported, not assumed acceptable in advance."
        configs = {key: value.config for key, value in runs.items()}
    elif experiment_id == "EXP-004":
        runs = {str(n): _run_m1(_config(n_intervals=n)) for n in (40, 80, 160)}
        metrics = {
            "runs": {key: _m1_summary(value) for key, value in runs.items()},
            "n_40_vs_80": _max_output_difference(runs["40"], runs["80"]),
            "n_80_vs_160": _max_output_difference(runs["80"], runs["160"]),
        }
        validation_result = {key: _validation_record(value) for key, value in runs.items()}
        notes = "Spatial grid convergence; internal grid is separate from the 0.1 cm output grid."
        configs = {key: value.config for key, value in runs.items()}
    elif experiment_id == "EXP-005":
        robin_config = _config(surface_boundary="robin")
        dirichlet_config = _config(surface_boundary="dirichlet")
        robin = _run_m1(robin_config)
        dirichlet = _run_m1(dirichlet_config)
        metrics = {
            "robin": _m1_summary(robin),
            "dirichlet": _m1_summary(dirichlet),
            "robin_vs_dirichlet": _max_output_difference(robin, dirichlet),
        }
        validation_result = {
            "robin": _validation_record(robin),
            "dirichlet": {"status": "NOT_APPLICABLE", "reason": "The Dirichlet comparison does not use the Robin boundary-flux accounting check."},
        }
        notes = "Boundary sensitivity comparison; Dirichlet is an alternative, not the default."
        configs = {"robin": robin_config, "dirichlet": dirichlet_config}
    elif experiment_id == "EXP-006":
        linear_config = _config(interpolation="linear")
        hold_config = _config(interpolation="zero_order")
        linear = _run_m1(linear_config)
        hold = _run_m1(hold_config)
        metrics = {
            "linear": _m1_summary(linear),
            "zero_order": _m1_summary(hold),
            "linear_vs_zero_order": _max_output_difference(linear, hold),
        }
        validation_result = {"linear": _validation_record(linear), "zero_order": _validation_record(hold)}
        notes = "Input interpolation sensitivity; no smoothing or extrapolation was used."
        configs = {"linear": linear_config, "zero_order": hold_config}
    elif experiment_id == "EXP-007":
        config = _config()
        result = _run_m1(config)
        metrics = validate_m1_result(result)
        metrics.update(_m1_summary(result))
        metrics["temperature_min_c"] = min(value for row in result.temperatures_c for value in row)
        metrics["temperature_max_c"] = max(value for row in result.temperatures_c for value in row)
        metrics["moisture_min_kg_kg"] = min(value for row in result.moistures_kg_kg for value in row)
        metrics["moisture_max_kg_kg"] = max(value for row in result.moistures_kg_kg for value in row)
        validation_result = _validation_record(result)
        notes = "Formal numerical validation evidence for M1. No result workbook was generated."
        configs = {"m1": config}
    else:
        raise ValueError(f"unknown experiment: {experiment_id}")

    elapsed = time.perf_counter() - started
    input_path = ROOT / "A题/附件/附件1.xlsx"
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    serializable_configs = {
        key: {
            field: (str(value) if isinstance(value, Path) else value)
            for field, value in vars(value).items()
        }
        for key, value in configs.items()
    }
    return {
        "experiment_id": experiment_id,
        "status": "COMPLETED",
        "command": f".\\.venv\\Scripts\\python.exe scripts\\run_q1_experiments.py {experiment_id}",
        "code_commit": commit,
        "input_hashes": {"A题/附件/附件1.xlsx": sha256(input_path)},
        "runtime_seconds": elapsed,
        "solver_parameters": serializable_configs,
        "metrics": metrics,
        "validation_result": validation_result,
        "notes": notes,
    }


def write_evidence(payload: Dict[str, Any]) -> Path:
    output_dir = assert_not_official_output(ROOT / "experiments" / payload["experiment_id"])
    output_dir.mkdir(parents=True, exist_ok=True)
    payload["artifact_paths"] = [
        f"experiments/{payload['experiment_id']}/config.json",
        f"experiments/{payload['experiment_id']}/metrics.json",
        f"experiments/{payload['experiment_id']}/notes.md",
    ]
    (output_dir / "config.json").write_text(
        json.dumps(
            {
                "experiment_id": payload["experiment_id"],
                "command": payload["command"],
                "code_commit": payload["code_commit"],
                "input_hashes": payload["input_hashes"],
                "solver_parameters": payload["solver_parameters"],
                "artifact_paths": payload["artifact_paths"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "notes.md").write_text(
        f"# {payload['experiment_id']}\n\n{payload['notes']}\n\nRuntime: `{payload['runtime_seconds']:.6f} s`\n\nStatus: `{payload['status']}`\n",
        encoding="utf-8",
    )
    return output_dir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment", choices=[f"EXP-{index:03d}" for index in range(1, 8)])
    args = parser.parse_args()
    payload = run_experiment(args.experiment)
    path = write_evidence(payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Evidence written to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
