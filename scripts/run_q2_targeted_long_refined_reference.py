"""Add a targeted n=640 reference only through the 48 h checkpoints."""

from __future__ import annotations

import csv
import gc
import json
import math
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q2 import run_q2
from scripts.run_q2_accuracy_remediation import load_base_config, sha256
from scripts.run_q2_targeted_long_certification import compare


OUT = ROOT / "experiments" / "EXP-Q2-ACC-LONG-TARGETED"
CASE = OUT / "reference_dt1_n640_cluster2_through48h"
TIMES_S = (10800.0, 21600.0, 43200.0, 86400.0, 129600.0, 172800.0)
RADII_CM = tuple(0.1 * index for index in range(21))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_snapshots(path: Path) -> dict[str, dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            f"{float(row['time_s']):.12g}|{float(row['radius_cm']):.12g}": {
                key: float(value) for key, value in row.items()
            }
            for row in csv.DictReader(handle)
        }


def main() -> int:
    if not OUT.is_dir() or not (OUT / "candidate_dt1_n320_cluster3" / "snapshots.csv").is_file():
        raise RuntimeError("run the targeted long screen first")
    if CASE.exists():
        raise RuntimeError(f"refusing to overwrite {CASE}")
    CASE.mkdir(parents=True)
    base = load_base_config()
    config = replace(
        base,
        end_time_s=172800.0,
        time_step_s=1.0,
        n_intervals=640,
        cluster_power=2.0,
        reset_bdf2_at_environment_transition=True,
        early_time_step_s=0.015625,
        early_time_end_s=5.0,
    )
    write_json(CASE / "config.json", config.as_dict())
    diagnostics_path = CASE / "diagnostics_3600s.csv"
    print("[Q2 targeted long] refined reference n640/cluster2 dt=1 through 48 h", flush=True)
    result = run_q2(
        config,
        record_times=(0.0,) + TIMES_S,
        diagnostics_path=diagnostics_path,
        diagnostics_interval_s=3600.0,
    )
    indices = {}
    for radius in RADII_CM:
        index = min(range(len(result.grid.nodes_m)), key=lambda i: abs(result.grid.nodes_m[i] * 100.0 - radius))
        if abs(result.grid.nodes_m[index] * 100.0 - radius) > 1.0e-10:
            raise RuntimeError(f"radius {radius:g} cm is not a grid node")
        indices[radius] = index
    rows: list[dict[str, float]] = []
    for time_s in TIMES_S:
        temperature_k, moisture = result.snapshot_at(time_s)
        for radius in RADII_CM:
            index = indices[radius]
            rows.append({
                "time_s": time_s,
                "radius_cm": radius,
                "temperature_K": float(temperature_k[index]),
                "temperature_C": float(temperature_k[index] - 273.15),
                "moisture_kg_kg": float(moisture[index]),
            })
    snapshots_path = CASE / "snapshots.csv"
    with snapshots_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    reference_snapshots = {f"{row['time_s']:.12g}|{row['radius_cm']:.12g}": row for row in rows}
    candidate_snapshots = load_snapshots(OUT / "candidate_dt1_n320_cluster3" / "snapshots.csv")
    candidate_snapshots = {
        key: value for key, value in candidate_snapshots.items()
        if float(value["time_s"]) in TIMES_S
    }
    metrics, comparison_rows = compare(candidate_snapshots, reference_snapshots)
    comparison_path = OUT / "comparison_candidate_n320_vs_reference_n640_3h_to_48h.csv"
    with comparison_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(comparison_rows[0]))
        writer.writeheader()
        writer.writerows(comparison_rows)
    summary = {
        "name": CASE.name,
        "config": config.as_dict(),
        "complete": bool(result.complete),
        "grid": {
            "requested_intervals": config.n_intervals,
            "actual_cell_count": len(result.grid.nodes_m) - 1,
            "actual_node_count": len(result.grid.nodes_m),
            "cluster_power": config.cluster_power,
            "min_dr_m": float(result.grid.min_dr_m if hasattr(result.grid, "min_dr_m") else result.grid.dr_m),
            "max_dr_m": float(result.grid.max_dr_m if hasattr(result.grid, "max_dr_m") else result.grid.dr_m),
        },
        "diagnostic_summary": {
            key: value
            for key, value in result.diagnostic_summary.items()
            if isinstance(value, (int, float)) and math.isfinite(float(value))
        },
        "snapshots": str(snapshots_path.relative_to(ROOT)).replace("\\", "/"),
        "diagnostics": {
            "path": str(diagnostics_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(diagnostics_path),
        },
    }
    write_json(CASE / "metrics.json", summary)
    long_path = OUT / "metrics.json"
    long_metrics = json.loads(long_path.read_text(encoding="utf-8"))
    long_metrics["refined_n640_reference_3h_to_48h"] = {
        "scope": "3/6/12/24/36/48 h formal points, continuous t=0 start, no n=640 full horizon",
        "reference": summary,
        "comparison": metrics,
        "comparison_csv": str(comparison_path.relative_to(ROOT)).replace("\\", "/"),
        "selected_point_gate_pass": metrics["temperature_Linf_C"] <= 2.5e-5 and metrics["moisture_Linf_kg_kg"] <= 2.5e-5,
    }
    write_json(long_path, long_metrics)
    (CASE / "notes.md").write_text(
        "# Targeted n=640 reference\n\n"
        "This is a localized long-horizon reference through 48 h only. It was "
        "added because the n=320 versus n=160 screen was marginally above the "
        "moisture gate at 24 h. It is not an n=640 full-horizon production run.\n",
        encoding="utf-8",
    )
    del result
    gc.collect()
    print(json.dumps({"status": "COMPLETE", "comparison": metrics}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
