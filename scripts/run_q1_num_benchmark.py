"""Run an isolated manufactured-solution benchmark for the Q1 radial kernel.

The benchmark does not use the competition input or any Q1 answer. It reuses
only the radial FVM assembly and Thomas solver, adding a test-only source term
for a manufactured solution with a Robin boundary.
"""

from __future__ import annotations

import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Sequence

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.numerics import make_radial_grid, thomas_solve
from src.q1.model import assemble_bdf2_radial_system, assemble_radial_system


DIFFUSIVITY = 0.1
SURFACE_TRANSFER = 0.7
RADIUS = 1.0
END_TIME = 0.01
OUTPUT_DIR = ROOT / "experiments" / "EXP-Q1-NUM-BENCH"


def exact_value(radius: float, time_s: float) -> float:
    return math.exp(-time_s) * (1.0 + radius**4)


def source_value(radius: float, time_s: float) -> float:
    # u_t - D * (u_rr + u_r/r) for u=exp(-t)*(1+r^4); the r=0 limit is finite.
    return math.exp(-time_s) * (-1.0 - radius**4 - 16.0 * DIFFUSIVITY * radius**2)


def environment_value(time_s: float) -> float:
    # D*u_r(R) = h*(u_inf-u(R)) for the outward-positive Robin condition.
    return exact_value(RADIUS, time_s) + DIFFUSIVITY * (4.0 * RADIUS**3) * math.exp(-time_s) / SURFACE_TRANSFER


def _step(old_values: Sequence[float], n_intervals: int, dt_s: float, time_s: float) -> List[float]:
    grid = make_radial_grid(RADIUS, n_intervals)
    lower, diagonal, upper, rhs = assemble_radial_system(
        old_values,
        grid,
        dt_s,
        1.0,
        [DIFFUSIVITY] * n_intervals,
        SURFACE_TRANSFER,
        environment_value(time_s),
    )
    for index, radius in enumerate(grid.nodes_m):
        rhs[index] += dt_s * source_value(radius, time_s)
    return thomas_solve(lower, diagonal, upper, rhs)


def _bdf2_step(
    old_values: Sequence[float],
    previous_values: Sequence[float],
    n_intervals: int,
    dt_s: float,
    time_s: float,
) -> List[float]:
    grid = make_radial_grid(RADIUS, n_intervals)
    lower, diagonal, upper, rhs = assemble_bdf2_radial_system(
        old_values,
        previous_values,
        grid,
        dt_s,
        1.0,
        [DIFFUSIVITY] * n_intervals,
        SURFACE_TRANSFER,
        environment_value(time_s),
    )
    for index, radius in enumerate(grid.nodes_m):
        rhs[index] += (2.0 / 3.0) * dt_s * source_value(radius, time_s)
    return thomas_solve(lower, diagonal, upper, rhs)


def run_case(n_intervals: int, dt_s: float) -> Dict[str, Any]:
    quotient = END_TIME / dt_s
    if abs(quotient - round(quotient)) > 1.0e-10:
        raise ValueError("benchmark END_TIME must be divisible by dt_s")
    grid = make_radial_grid(RADIUS, n_intervals)
    values = [exact_value(radius, 0.0) for radius in grid.nodes_m]
    steps = int(round(quotient))
    for step in range(1, steps + 1):
        values = _step(values, n_intervals, dt_s, step * dt_s)
    exact = [exact_value(radius, END_TIME) for radius in grid.nodes_m]
    errors = [abs(actual - expected) for actual, expected in zip(values, exact)]
    squared = [(actual - expected) ** 2 for actual, expected in zip(values, exact)]
    return {
        "n_intervals": n_intervals,
        "dr": grid.dr_m,
        "dt_s": dt_s,
        "steps": steps,
        "linf": max(errors),
        "mean_abs": sum(errors) / len(errors),
        "rmse": math.sqrt(sum(squared) / len(squared)),
        "center_abs": errors[0],
        "surface_abs": errors[-1],
    }


def run_bdf2_case(n_intervals: int, dt_s: float) -> Dict[str, Any]:
    quotient = END_TIME / dt_s
    if abs(quotient - round(quotient)) > 1.0e-10 or quotient < 2.0:
        raise ValueError("BDF2 benchmark requires at least two steps")
    grid = make_radial_grid(RADIUS, n_intervals)
    previous = [exact_value(radius, 0.0) for radius in grid.nodes_m]
    old = _step(previous, n_intervals, dt_s, dt_s)
    steps = int(round(quotient))
    for step in range(2, steps + 1):
        current = _bdf2_step(old, previous, n_intervals, dt_s, step * dt_s)
        previous, old = old, current
    exact = [exact_value(radius, END_TIME) for radius in grid.nodes_m]
    errors = [abs(actual - expected) for actual, expected in zip(old, exact)]
    squared = [(actual - expected) ** 2 for actual, expected in zip(old, exact)]
    return {
        "n_intervals": n_intervals,
        "dr": grid.dr_m,
        "dt_s": dt_s,
        "steps": steps,
        "linf": max(errors),
        "mean_abs": sum(errors) / len(errors),
        "rmse": math.sqrt(sum(squared) / len(squared)),
        "center_abs": errors[0],
        "surface_abs": errors[-1],
    }


def observed_order(coarse: float, fine: float, refinement: float = 2.0) -> float | None:
    if coarse <= 0.0 or fine <= 0.0:
        return None
    return math.log(coarse / fine) / math.log(refinement)


def _orders(cases: Sequence[Dict[str, Any]], key: str) -> List[float | None]:
    return [
        observed_order(cases[index][key], cases[index + 1][key])
        for index in range(len(cases) - 1)
    ]


def main() -> int:
    started = time.perf_counter()
    spatial_dts = {
        40: 5.0e-5,
        80: 1.25e-5,
        160: 3.125e-6,
        320: 7.8125e-7,
    }
    spatial = [run_case(n, spatial_dts[n]) for n in (40, 80, 160, 320)]
    # These steps are intentionally larger than the spatial error at N=320 so
    # the temporal order is observable rather than round-off/spatial-error
    # dominated.
    temporal = [run_case(320, dt) for dt in (2.0e-3, 1.0e-3, 5.0e-4, 2.5e-4)]
    bdf2_temporal = [run_bdf2_case(320, dt) for dt in (2.0e-3, 1.0e-3, 5.0e-4, 2.5e-4)]
    payload: Dict[str, Any] = {
        "experiment_id": "EXP-Q1-NUM-BENCH",
        "status": "COMPLETED",
        "description": "Manufactured solution u=exp(-t)*(1+r^4) with constant D and Robin boundary",
        "production_input_used": False,
        "production_model_changed": False,
        "python": platform.python_version(),
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "benchmark_parameters": {
            "diffusivity": DIFFUSIVITY,
            "surface_transfer": SURFACE_TRANSFER,
            "radius": RADIUS,
            "end_time_s": END_TIME,
            "exact_solution": "u(r,t)=exp(-t)*(1+r^4)",
            "source": "exp(-t)*(-1-r^4-16*D*r^2)",
            "robin_environment": "u(R,t)+D*u_r(R,t)/h",
        },
        "spatial_cases": spatial,
        "temporal_cases": temporal,
        "bdf2_temporal_cases": bdf2_temporal,
        "spatial_observed_order": {key: _orders(spatial, key) for key in ("linf", "mean_abs", "rmse", "center_abs", "surface_abs")},
        "temporal_observed_order": {key: _orders(temporal, key) for key in ("linf", "mean_abs", "rmse", "center_abs", "surface_abs")},
        "bdf2_temporal_observed_order": {key: _orders(bdf2_temporal, key) for key in ("linf", "mean_abs", "rmse", "center_abs", "surface_abs")},
        "runtime_seconds": time.perf_counter() - started,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "config.json").write_text(
        json.dumps(
            {
                "experiment_id": payload["experiment_id"],
                "code_commit": payload["code_commit"],
                "production_input_used": payload["production_input_used"],
                "production_model_changed": payload["production_model_changed"],
                "benchmark_parameters": payload["benchmark_parameters"],
                "spatial_cases": payload["spatial_cases"],
                "temporal_cases": payload["temporal_cases"],
                "bdf2_temporal_cases": payload["bdf2_temporal_cases"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "notes.md").write_text(
        "# EXP-Q1-NUM-BENCH\n\n"
        "Isolated manufactured-solution benchmark. It reuses only the radial FVM assembly and linear solver; "
        "the source term, exact solution, and Robin environment are test-only.\n\n"
        f"Status: `{payload['status']}`\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("Evidence written to experiments/EXP-Q1-NUM-BENCH")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
