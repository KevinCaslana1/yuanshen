"""Targeted Q2 runs needed for the human model-decision packet.

This script is deliberately narrower than the long-horizon production run.  It
does not write a workbook, does not invoke Q3 stopping logic, and records only
decision checkpoints plus compact diagnostics.  The boundary study uses
dt=2 s as a targeted long-horizon sensitivity screen; the interface study uses
the production spatial and temporal resolution so its long-horizon comparison
is not confounded by a second time discretisation.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q2 import Q2RunConfig, run_q2
from scripts.run_q2_long_horizon import (
    EXP,
    compare_result_to_main,
    dump,
    ensure_folder,
    field_difference,
    load_main_official_snapshots,
)


TARGET_TIMES = (10800.0, 21600.0, 86400.0, 172800.0, 259200.0)
INTERFACE_TARGET_TIMES = (21600.0, 86400.0, 172800.0, 259200.0)
RADIUS_POINTS = (0.0, 1.0, 1.5, 2.0)


def base_config(*, time_step_s: float, interface_mean: str = "harmonic") -> Q2RunConfig:
    return Q2RunConfig(
        end_time_s=259200.0,
        time_step_s=time_step_s,
        candidate="A",
        n_intervals=80,
        scheme="bdf2",
        interface_mean=interface_mean,
        interpolation="linear",
        post_attachment_mode="constant",
        post_temperature_c=50.165,
        post_moisture_kg_kg=0.04986,
        output_interval_s=time_step_s,
    )


def _checkpoint_field_summary(result, time_s: float) -> dict:
    temperature, moisture = result.snapshot_at(time_s)
    indices = {
        str(radius): min(
            range(len(result.grid.nodes_m)),
            key=lambda index: abs(result.grid.nodes_m[index] * 100.0 - radius),
        )
        for radius in RADIUS_POINTS
    }
    return {
        "temperature_C": {
            str(radius): temperature[index] - 273.15
            for radius, index in indices.items()
        },
        "moisture_kg_kg": {
            str(radius): moisture[index]
            for radius, index in indices.items()
        },
    }


def run_boundary_long_target() -> dict:
    path = ensure_folder("EXP-Q2-021-DECISION-TARGETS")
    base = base_config(time_step_s=2.0)
    configs = {
        "base": base,
        "h_minus10": replace(
            base,
            parameters=replace(
                base.parameters,
                heat_transfer_w_m2_k=base.parameters.heat_transfer_w_m2_k * 0.9,
            ),
        ),
        "h_plus10": replace(
            base,
            parameters=replace(
                base.parameters,
                heat_transfer_w_m2_k=base.parameters.heat_transfer_w_m2_k * 1.1,
            ),
        ),
        "hm_minus10": replace(
            base,
            parameters=replace(
                base.parameters,
                mass_transfer_m_s=base.parameters.mass_transfer_m_s * 0.9,
            ),
        ),
        "hm_plus10": replace(
            base,
            parameters=replace(
                base.parameters,
                mass_transfer_m_s=base.parameters.mass_transfer_m_s * 1.1,
            ),
        ),
    }
    runs = {}
    runtimes = {}
    for name, config in configs.items():
        started = time.perf_counter()
        runs[name] = run_q2(
            config,
            record_times=(0.0,) + TARGET_TIMES,
            diagnostics_path=path / f"diagnostics_{name}.csv",
            diagnostics_interval_s=21600.0,
            passive_event_threshold_kg_kg=0.15,
        )
        runtimes[name] = time.perf_counter() - started

    impacts = {}
    for name, result in runs.items():
        if name == "base":
            continue
        by_time = {
            str(int(t)): field_difference(result, runs["base"], t)
            for t in TARGET_TIMES
        }
        impacts[name] = {
            "runtime_s": runtimes[name],
            "passive_event_bracket_s": result.passive_event_bracket_s,
            "passive_event_bracket_shift_s_vs_base": (
                None
                if result.passive_event_bracket_s is None
                or runs["base"].passive_event_bracket_s is None
                else [
                    result.passive_event_bracket_s[0]
                    - runs["base"].passive_event_bracket_s[0],
                    result.passive_event_bracket_s[1]
                    - runs["base"].passive_event_bracket_s[1],
                ]
            ),
            "checkpoints": by_time,
            "max_over_checkpoints": {
                key: max(row[key] for row in by_time.values())
                for key in (
                    "temperature_Linf_K",
                    "temperature_L2_RMS_K",
                    "moisture_Linf",
                    "moisture_L2_RMS",
                    "inventory_abs",
                )
            },
        }

    payload = {
        "experiment": "EXP-Q2-021-DECISION-TARGETS-BC-LONG",
        "status": "PASS" if all(run.complete for run in runs.values()) else "FAIL",
        "purpose": "Targeted 3 h and 72 h h/hm sensitivity evidence for D-Q2-BOUNDARY-COEFFICIENTS",
        "screen_is_not_production_accuracy": True,
        "base_config": base.as_dict(),
        "target_times_s": list(TARGET_TIMES),
        "diagnostics_interval_s": 21600.0,
        "runs": {
            name: {
                "config": config.as_dict(),
                "runtime_s": runtimes[name],
                "complete": runs[name].complete,
                "diagnostic_summary": runs[name].diagnostic_summary,
                "passive_event_bracket_s": runs[name].passive_event_bracket_s,
                "checkpoint_fields": {
                    str(int(t)): _checkpoint_field_summary(runs[name], t)
                    for t in TARGET_TIMES
                },
            }
            for name, config in configs.items()
        },
        "impacts_vs_base": impacts,
        "workbook_written": False,
        "q3_event_stop": False,
    }
    dump(path / "boundary_long_target_metrics.json", payload)
    return payload


def _write_interface_rows(path: Path, rows: list[dict]) -> None:
    fields = [
        "time_s",
        "radius_cm",
        "temperature_signed_error_C",
        "temperature_absolute_error_C",
        "moisture_signed_error",
        "moisture_absolute_error",
    ]
    with (path / "interface_long_target_points.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "time_s": row["level_time_s"],
                "radius_cm": row["radius_cm"],
                "temperature_signed_error_C": row["temperature_signed_error_C"],
                "temperature_absolute_error_C": row["temperature_absolute_error_C"],
                "moisture_signed_error": row["moisture_signed_error"],
                "moisture_absolute_error": row["moisture_absolute_error"],
            })


def run_interface_long_target() -> dict:
    path = ensure_folder("EXP-Q2-021-DECISION-TARGETS")
    config = base_config(time_step_s=0.25, interface_mean="arithmetic")
    started = time.perf_counter()
    result = run_q2(
        config,
        record_times=(0.0,) + INTERFACE_TARGET_TIMES,
        diagnostics_path=path / "diagnostics_interface_arithmetic.csv",
        diagnostics_interval_s=21600.0,
    )
    runtime = time.perf_counter() - started
    main = load_main_official_snapshots()
    metrics, rows = compare_result_to_main(result, main, INTERFACE_TARGET_TIMES)
    _write_interface_rows(path, rows)
    payload = {
        "experiment": "EXP-Q2-021-DECISION-TARGETS-INTERFACE-LONG",
        "status": "PASS" if result.complete else "FAIL",
        "purpose": "Targeted long-horizon arithmetic-vs-harmonic evidence for D-Q2-INTERFACE-MEAN",
        "reference": "canonical ENV-A harmonic Candidate A n=80 dt=0.25 s recovered 72 h output",
        "config": config.as_dict(),
        "runtime_s": runtime,
        "comparison_times_s": list(INTERFACE_TARGET_TIMES),
        "errors_vs_canonical_harmonic": metrics,
        "points_csv": "experiments/EXP-Q2-021-DECISION-TARGETS/interface_long_target_points.csv",
        "diagnostic_summary": result.diagnostic_summary,
        "workbook_written": False,
        "q3_event_stop": False,
    }
    dump(path / "interface_long_target_metrics.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("boundary-long", "interface-long", "all"))
    args = parser.parse_args()
    if args.mode == "boundary-long":
        print(json.dumps(run_boundary_long_target(), ensure_ascii=False, indent=2))
    elif args.mode == "interface-long":
        print(json.dumps(run_interface_long_target(), ensure_ascii=False, indent=2))
    else:
        print(json.dumps({
            "boundary": run_boundary_long_target(),
            "interface": run_interface_long_target(),
        }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
