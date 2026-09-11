"""Measure short-time spatial moisture error decay at the outer boundary."""

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
from src.q1.solver import Q1Result, run_m1
from scripts.run_q1_num_diag import _svg_line_plot


OUTPUT_DIR = ROOT / "experiments" / "EXP-Q1-SURFACE-DECAY"
TIMES_S = tuple(range(1, 101))
POSITIONS_M = (0.019, 0.02)


def _config(n_intervals: int, time_step_s: float) -> Q1RunConfig:
    return Q1RunConfig(
        end_time_s=100.0,
        time_step_s=time_step_s,
        n_intervals=n_intervals,
        interpolation="linear",
        surface_boundary="robin",
    )


def _sample(result: Q1Result, time_s: int, position_m: float) -> float:
    time_index = round(time_s / result.config.time_step_s)
    position_index = round(position_m / result.grid.dr_m)
    if abs(result.times_s[time_index] - time_s) > 1.0e-10:
        raise ValueError(f"time is not aligned: {time_s}")
    if abs(position_index * result.grid.dr_m - position_m) > 1.0e-12:
        raise ValueError(f"position is not aligned: {position_m}")
    return result.moistures_kg_kg[time_index][position_index]


def _comparison(first: Q1Result, second: Q1Result) -> Dict[str, Any]:
    by_time = []
    for time_s in TIMES_S:
        values = [abs(_sample(first, time_s, position) - _sample(second, time_s, position)) for position in POSITIONS_M]
        by_time.append({
            "time_s": time_s,
            "r1.9cm_abs": values[0],
            "r2.0cm_abs": values[1],
            "max_abs": max(values),
        })
    all_values = [value for row in by_time for value in (row["r1.9cm_abs"], row["r2.0cm_abs"])]
    return {
        "coarse": {"n_intervals": first.grid.n_intervals, "dt_s": first.config.time_step_s},
        "fine": {"n_intervals": second.grid.n_intervals, "dt_s": second.config.time_step_s},
        "linf": max(all_values),
        "mean_abs": sum(all_values) / len(all_values),
        "rmse": math.sqrt(sum(value * value for value in all_values) / len(all_values)),
        "by_time": by_time,
    }


def _orders(coarse: Dict[str, Any], fine: Dict[str, Any]) -> Dict[str, Any]:
    output = []
    for coarse_row, fine_row in zip(coarse["by_time"], fine["by_time"]):
        row: Dict[str, Any] = {"time_s": coarse_row["time_s"]}
        for key in ("r1.9cm_abs", "r2.0cm_abs", "max_abs"):
            coarse_error = coarse_row[key]
            fine_error = fine_row[key]
            if coarse_error > 0.0 and fine_error > 0.0:
                order = math.log(coarse_error / fine_error, 2.0)
                remaining = fine_error / (2.0**order - 1.0) if order > 0.0 else None
            else:
                order = None
                remaining = None
            row[f"{key}_observed_order"] = order
            row[f"{key}_richardson_remaining_error"] = remaining
        output.append(row)
    return {"by_time": output}


def main() -> int:
    started = time.perf_counter()
    boundary = BoundaryProvider.from_attachment1(ROOT / "A题" / "附件" / "附件1.xlsx")
    specs = {
        "N320_dt0.0625": (320, 0.0625),
        "N640_dt0.0625": (640, 0.0625),
        "N1280_dt0.0625": (1280, 0.0625),
        "N1280_dt0.03125": (1280, 0.03125),
    }
    results: Dict[str, Q1Result] = {}
    runtimes: Dict[str, float] = {}
    for key, (n_intervals, dt_s) in specs.items():
        case_started = time.perf_counter()
        results[key] = run_m1(_config(n_intervals, dt_s), boundary, DEFAULT_PARAMETERS)
        runtimes[key] = time.perf_counter() - case_started

    coarse_comparison = _comparison(results["N320_dt0.0625"], results["N640_dt0.0625"])
    fine_comparison = _comparison(results["N640_dt0.0625"], results["N1280_dt0.0625"])
    order_rows = _orders(coarse_comparison, fine_comparison)
    t1_row = next(row for row in fine_comparison["by_time"] if row["time_s"] == 1)
    t100_row = next(row for row in fine_comparison["by_time"] if row["time_s"] == 100)
    plot_path = OUTPUT_DIR / "surface_moisture_error_decay.svg"
    payload: Dict[str, Any] = {
        "experiment_id": "EXP-Q1-SURFACE-DECAY",
        "status": "COMPLETED",
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(),
        "input_hashes": {"A题/附件/附件1.xlsx": "7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7"},
        "scope": {
            "end_time_s": 100.0,
            "comparison_times_s": "1..100 s",
            "comparison_positions_cm": [1.9, 2.0],
            "strategy": "N320/N640/N1280 at common dt=0.0625 for spatial comparisons; N1280 dt=0.03125 retained only for time-resolution context",
        },
        "cases": {
            key: {
                "n_intervals": result.grid.n_intervals,
                "dr_m": result.grid.dr_m,
                "dt_s": result.config.time_step_s,
                "runtime_seconds": runtimes[key],
                "picard_max_iterations": max(result.picard_iterations[1:]),
            }
            for key, result in results.items()
        },
        "N320_vs_N640": coarse_comparison,
        "N640_vs_N1280": fine_comparison,
        "pointwise_spatial_order_and_richardson": order_rows,
        "decay_summary": {
            "fine_comparison_t1": t1_row,
            "fine_comparison_t100": t100_row,
            "r1.9cm_t1_to_t100_ratio": t1_row["r1.9cm_abs"] / t100_row["r1.9cm_abs"],
            "r2.0cm_t1_to_t100_ratio": t1_row["r2.0cm_abs"] / t100_row["r2.0cm_abs"],
        },
        "plot": "surface_moisture_error_decay.svg",
        "runtime_seconds": time.perf_counter() - started,
        "candidate_workbook_generated": False,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _svg_line_plot(
        plot_path,
        [float(row["time_s"]) for row in fine_comparison["by_time"]],
        {
            "r=1.9 cm": [row["r1.9cm_abs"] for row in fine_comparison["by_time"]],
            "r=2.0 cm": [row["r2.0cm_abs"] for row in fine_comparison["by_time"]],
        },
        "time (s)",
        "absolute moisture difference (kg/kg)",
    )
    (OUTPUT_DIR / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "config.json").write_text(json.dumps({
        "experiment_id": payload["experiment_id"],
        "code_commit": payload["code_commit"],
        "input_hashes": payload["input_hashes"],
        "scope": payload["scope"],
        "cases": payload["cases"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "notes.md").write_text(
        "# EXP-Q1-SURFACE-DECAY\n\n"
        "Short 0--100 s spatial error-decay experiment at r=1.9 cm and r=2.0 cm. "
        "It does not modify the production initial condition or official input and "
        "does not write a workbook.\n\n"
        f"Status: `{payload['status']}`\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "experiment_id": payload["experiment_id"],
        "status": payload["status"],
        "decay_summary": payload["decay_summary"],
        "runtime_seconds": payload["runtime_seconds"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
