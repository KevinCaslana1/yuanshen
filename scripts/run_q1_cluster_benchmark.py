"""Benchmark a boundary-clustered radial FVM on a manufactured solution.

This is intentionally isolated from the production solver. It tests the
conservative nonuniform radial control-volume formulas, including center and
surface Robin rows, before any competition-model use is considered.
"""

from __future__ import annotations

import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.numerics import thomas_solve


DIFFUSIVITY = 0.1
SURFACE_TRANSFER = 0.7
RADIUS = 1.0
CLUSTER_POWER = 2.0
END_TIME = 0.01
OUTPUT_DIR = ROOT / "experiments" / "EXP-Q1-CLUSTER-BENCH"


def exact_value(radius: float, time_s: float) -> float:
    return math.exp(-time_s) * (1.0 + radius**4)


def source_value(radius: float, time_s: float) -> float:
    return math.exp(-time_s) * (-1.0 - radius**4 - 16.0 * DIFFUSIVITY * radius**2)


def environment_value(time_s: float) -> float:
    return exact_value(RADIUS, time_s) + DIFFUSIVITY * 4.0 * RADIUS**3 * math.exp(-time_s) / SURFACE_TRANSFER


def clustered_nodes(n_intervals: int) -> List[float]:
    return [RADIUS * (1.0 - (1.0 - index / n_intervals) ** CLUSTER_POWER) for index in range(n_intervals + 1)]


def assemble_nonuniform(
    old_values: Sequence[float],
    nodes: Sequence[float],
    dt_s: float,
    environment: float,
) -> tuple[List[float], List[float], List[float], List[float]]:
    n = len(nodes) - 1
    faces = [0.5 * (left + right) for left, right in zip(nodes, nodes[1:])]
    volumes = [0.5 * faces[0] ** 2]
    volumes.extend(0.5 * (faces[index] ** 2 - faces[index - 1] ** 2) for index in range(1, n))
    volumes.append(0.5 * (RADIUS**2 - faces[-1] ** 2))
    lower = [0.0] * (n + 1)
    diagonal = [0.0] * (n + 1)
    upper = [0.0] * (n + 1)
    rhs = list(old_values)

    center = dt_s * faces[0] * DIFFUSIVITY / (volumes[0] * (nodes[1] - nodes[0]))
    diagonal[0] = 1.0 + center
    upper[0] = -center
    for index in range(1, n):
        left = dt_s * faces[index - 1] * DIFFUSIVITY / (volumes[index] * (nodes[index] - nodes[index - 1]))
        right = dt_s * faces[index] * DIFFUSIVITY / (volumes[index] * (nodes[index + 1] - nodes[index]))
        lower[index] = -left
        diagonal[index] = 1.0 + left + right
        upper[index] = -right
    inner = dt_s * faces[-1] * DIFFUSIVITY / (volumes[-1] * (nodes[-1] - nodes[-2]))
    external = dt_s * RADIUS * SURFACE_TRANSFER / volumes[-1]
    lower[-1] = -inner
    diagonal[-1] = 1.0 + inner + external
    rhs[-1] += external * environment
    return lower, diagonal, upper, rhs


def run_case(n_intervals: int, dt_s: float) -> Dict[str, Any]:
    quotient = END_TIME / dt_s
    if abs(quotient - round(quotient)) > 1.0e-10:
        raise ValueError("benchmark END_TIME must be divisible by dt_s")
    nodes = clustered_nodes(n_intervals)
    values = [exact_value(radius, 0.0) for radius in nodes]
    steps = int(round(quotient))
    for step in range(1, steps + 1):
        time_s = step * dt_s
        lower, diagonal, upper, rhs = assemble_nonuniform(values, nodes, dt_s, environment_value(time_s))
        rhs = [value + dt_s * source_value(radius, time_s) for value, radius in zip(rhs, nodes)]
        values = thomas_solve(lower, diagonal, upper, rhs)
    errors = [abs(value - exact_value(radius, END_TIME)) for value, radius in zip(values, nodes)]
    squared = [(value - exact_value(radius, END_TIME)) ** 2 for value, radius in zip(values, nodes)]
    return {
        "n_intervals": n_intervals,
        "cluster_power": CLUSTER_POWER,
        "minimum_dr": min(right - left for left, right in zip(nodes, nodes[1:])),
        "maximum_dr": max(right - left for left, right in zip(nodes, nodes[1:])),
        "dt_s": dt_s,
        "steps": steps,
        "linf": max(errors),
        "mean_abs": sum(errors) / len(errors),
        "rmse": math.sqrt(sum(squared) / len(squared)),
        "center_abs": errors[0],
        "surface_abs": errors[-1],
    }


def _orders(cases: Sequence[Dict[str, Any]], key: str) -> List[float | None]:
    orders: List[float | None] = []
    for coarse, fine in zip(cases, cases[1:]):
        if coarse[key] <= 0.0 or fine[key] <= 0.0:
            orders.append(None)
        else:
            orders.append(math.log(coarse[key] / fine[key], 2.0))
    return orders


def main() -> int:
    started = time.perf_counter()
    spatial = [run_case(n, 1.0e-6) for n in (40, 80, 160, 320)]
    temporal = [run_case(320, dt) for dt in (2.0e-3, 1.0e-3, 5.0e-4, 2.5e-4)]
    payload: Dict[str, Any] = {
        "experiment_id": "EXP-Q1-CLUSTER-BENCH",
        "status": "COMPLETED",
        "production_input_used": False,
        "production_model_changed": False,
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "benchmark_parameters": {
            "exact_solution": "u(r,t)=exp(-t)*(1+r^4)",
            "source": "exp(-t)*(-1-r^4-16*D*r^2)",
            "robin_environment": "u(R,t)+D*u_r(R,t)/h",
            "radius": RADIUS,
            "diffusivity": DIFFUSIVITY,
            "surface_transfer": SURFACE_TRANSFER,
            "cluster_power": CLUSTER_POWER,
            "end_time_s": END_TIME,
        },
        "spatial_cases": spatial,
        "temporal_cases": temporal,
        "spatial_observed_order": {key: _orders(spatial, key) for key in ("linf", "mean_abs", "rmse", "center_abs", "surface_abs")},
        "temporal_observed_order": {key: _orders(temporal, key) for key in ("linf", "mean_abs", "rmse", "center_abs", "surface_abs")},
        "runtime_seconds": time.perf_counter() - started,
        "candidate_workbook_generated": False,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "config.json").write_text(json.dumps({
        "experiment_id": payload["experiment_id"],
        "code_commit": payload["code_commit"],
        "production_input_used": False,
        "production_model_changed": False,
        "benchmark_parameters": payload["benchmark_parameters"],
        "spatial_cases": payload["spatial_cases"],
        "temporal_cases": payload["temporal_cases"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "notes.md").write_text(
        "# EXP-Q1-CLUSTER-BENCH\n\n"
        "Isolated boundary-clustered nonuniform FVM benchmark. It is not the "
        "production Q1 solver and does not generate a workbook.\n\n"
        f"Status: `{payload['status']}`\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "experiment_id": payload["experiment_id"],
        "status": payload["status"],
        "spatial_observed_order": payload["spatial_observed_order"],
        "temporal_observed_order": payload["temporal_observed_order"],
        "runtime_seconds": payload["runtime_seconds"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
