"""Evaluate the benchmarked boundary-clustered FVM on short real Q1 runs."""

from __future__ import annotations

import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Sequence

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q1.config import DEFAULT_PARAMETERS, Q1RunConfig
from src.q1.inputs import BoundaryProvider
from src.q1.solver import Q1Result, run_m1, run_m1_nonuniform


OUTPUT_DIR = ROOT / "experiments" / "EXP-Q1-CLUSTER-SHORT"
TIMES_S = (0.25, 0.5, 1.0, 2.0, 5.0, 10.0)
OUTPUT_POSITIONS_M = tuple(index * 0.001 for index in range(21))
FOCUS_POSITIONS_M = (0.018, 0.019, 0.02)


def _config(n_intervals: int, time_step_s: float = 0.0625) -> Q1RunConfig:
    return Q1RunConfig(
        end_time_s=10.0,
        time_step_s=time_step_s,
        n_intervals=n_intervals,
        interpolation="linear",
        surface_boundary="robin",
    )


def _sample(result: Q1Result, time_s: float, position_m: float) -> float:
    time_index = next(index for index, value in enumerate(result.times_s) if abs(value - time_s) < 1.0e-10)
    position_index = min(
        range(len(result.grid.nodes_m)),
        key=lambda index: abs(result.grid.nodes_m[index] - position_m),
    )
    if abs(result.grid.nodes_m[position_index] - position_m) > 1.0e-12:
        raise ValueError(f"position is not an explicit grid node: {position_m}")
    return result.moistures_kg_kg[time_index][position_index]


def _compare(first: Q1Result, second: Q1Result, positions_m: Sequence[float] = FOCUS_POSITIONS_M) -> Dict[str, Any]:
    differences = [
        [abs(_sample(first, time_s, position) - _sample(second, time_s, position)) for position in positions_m]
        for time_s in TIMES_S
    ]
    values = [value for row in differences for value in row]
    max_index = values.index(max(values))
    time_index, position_index = divmod(max_index, len(positions_m))
    return {
        "positions_cm": [position * 100.0 for position in positions_m],
        "linf": max(values),
        "mean_abs": sum(values) / len(values),
        "rmse": math.sqrt(sum(value * value for value in values) / len(values)),
        "max_location": {"time_s": TIMES_S[time_index], "distance_cm": positions_m[position_index] * 100.0},
        "by_time": [
            {"time_s": time_s, "r1.8cm_abs": row[0], "r1.9cm_abs": row[1], "r2.0cm_abs": row[2], "max_abs": max(row)}
            for time_s, row in zip(TIMES_S, differences)
        ],
    }


def _summary(result: Q1Result, runtime_seconds: float) -> Dict[str, Any]:
    surface_index = len(result.grid.nodes_m) - 1
    local_indices = (surface_index, surface_index - 1, surface_index - 2)
    min_dr = result.grid.min_dr_m if hasattr(result.grid, "min_dr_m") else result.grid.dr_m
    max_dr = result.grid.max_dr_m if hasattr(result.grid, "max_dr_m") else result.grid.dr_m
    return {
        "runtime_seconds": runtime_seconds,
        "n_intervals_actual": result.grid.n_intervals,
        "node_count": len(result.grid.nodes_m),
        "min_dr_m": min_dr,
        "max_dr_m": max_dr,
        "history_length": len(result.times_s),
        "picard_max_iterations": max(result.picard_iterations[1:]),
        "surface_moisture_at_times": {
            str(time_s): result.moistures_kg_kg[next(index for index, value in enumerate(result.times_s) if abs(value - time_s) < 1.0e-10)][surface_index]
            for time_s in TIMES_S
        },
        "local_layer_positions_cm": [result.grid.nodes_m[index] * 100.0 for index in local_indices],
        "local_layer_moisture_at_t1": [result.moistures_kg_kg[next(index for index, value in enumerate(result.times_s) if abs(value - 1.0) < 1.0e-10)][index] for index in local_indices],
        "official_output_nodes_present": all(
            any(abs(node - position) < 1.0e-12 for node in result.grid.nodes_m)
            for position in OUTPUT_POSITIONS_M
        ),
    }


def main() -> int:
    started = time.perf_counter()
    boundary = BoundaryProvider.from_attachment1(ROOT / "A题" / "附件" / "附件1.xlsx")
    cases: Dict[str, tuple[str, int, float | None]] = {
        "uniform_N320": ("uniform", 320, None),
        "uniform_N640": ("uniform", 640, None),
        "cluster_base320": ("cluster", 320, 2.0),
        "cluster_base640": ("cluster", 640, 2.0),
        "cluster_base1280": ("cluster", 1280, 2.0),
        "uniform_N1280_reference": ("uniform", 1280, None),
    }
    results: Dict[str, Q1Result] = {}
    runtimes: Dict[str, float] = {}
    for label, (kind, n_intervals, cluster_power) in cases.items():
        case_started = time.perf_counter()
        if kind == "uniform":
            results[label] = run_m1(_config(n_intervals), boundary, DEFAULT_PARAMETERS)
        else:
            results[label] = run_m1_nonuniform(
                _config(n_intervals),
                boundary,
                DEFAULT_PARAMETERS,
                cluster_power=cluster_power or 2.0,
                required_output_positions_m=OUTPUT_POSITIONS_M,
            )
        runtimes[label] = time.perf_counter() - case_started

    payload: Dict[str, Any] = {
        "experiment_id": "EXP-Q1-CLUSTER-SHORT",
        "status": "COMPLETED",
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "input_hashes": {"A题/附件/附件1.xlsx": "7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7"},
        "scope": {
            "end_time_s": 10.0,
            "time_step_s": 0.0625,
            "official_output_positions_cm": [position * 100.0 for position in OUTPUT_POSITIONS_M],
            "focus_positions_cm": [position * 100.0 for position in FOCUS_POSITIONS_M],
            "cluster_definition": "r=R*(1-(1-i/N)^2), plus explicit official output nodes",
        },
        "cases": {label: _summary(result, runtimes[label]) for label, result in results.items()},
        "uniform_N320_vs_N640": _compare(results["uniform_N320"], results["uniform_N640"]),
        "cluster_base320_vs_base640": _compare(results["cluster_base320"], results["cluster_base640"]),
        "cluster_base640_vs_base1280": _compare(results["cluster_base640"], results["cluster_base1280"]),
        "cluster_base320_vs_uniform_N1280": _compare(results["cluster_base320"], results["uniform_N1280_reference"]),
        "cluster_base640_vs_uniform_N1280": _compare(results["cluster_base640"], results["uniform_N1280_reference"]),
        "runtime_seconds": time.perf_counter() - started,
        "candidate_workbook_generated": False,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "config.json").write_text(json.dumps({
        "experiment_id": payload["experiment_id"],
        "code_commit": payload["code_commit"],
        "input_hashes": payload["input_hashes"],
        "scope": payload["scope"],
        "cases": payload["cases"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "notes.md").write_text(
        "# EXP-Q1-CLUSTER-SHORT\n\n"
        "Short real-Q1 evaluation of the benchmarked boundary-clustered FVM. "
        "Official 0.1 cm nodes are explicit grid nodes. This is a candidate "
        "comparison only and writes no workbook.\n\n"
        f"Status: `{payload['status']}`\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "experiment_id": payload["experiment_id"],
        "status": payload["status"],
        "uniform_N320_vs_N640": payload["uniform_N320_vs_N640"],
        "cluster_base320_vs_base640": payload["cluster_base320_vs_base640"],
        "cluster_base640_vs_base1280": payload["cluster_base640_vs_base1280"],
        "cluster_base640_vs_uniform_N1280": payload["cluster_base640_vs_uniform_N1280"],
        "runtime_seconds": payload["runtime_seconds"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
