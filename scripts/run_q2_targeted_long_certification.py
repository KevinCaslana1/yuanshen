"""Run the authorized targeted Q2 long-horizon certification screen.

This is deliberately not a V3 production run.  It compares the proposed
n=320/cluster=3 grid with a moderate n=160/cluster=2 grid at selected long
times using dt=1 s to test spatial propagation and late-time stability.  The
formal time-accuracy evidence remains in EXP-Q2-ACC-T-FORMAL and
EXP-Q2-ACC-C-FORMAL.
"""

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

from src.q2 import Q2RunConfig, run_q2
from scripts.run_q2_accuracy_remediation import load_base_config, sha256


OUT = ROOT / "experiments" / "EXP-Q2-ACC-LONG-TARGETED"
GATE_T = 2.5e-5
GATE_C = 2.5e-5
OFFICIAL_RADII_CM = tuple(0.1 * index for index in range(21))
SELECTED_TIMES_S = (
    10800.0,   # 3 h
    21600.0,   # 6 h
    43200.0,   # 12 h
    86400.0,   # 24 h
    129600.0,  # 36 h
    172800.0,  # 48 h
    207033.0,
    207034.0,
    207035.0,
    207036.0,
    228635.0,
)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def radius_indices(result) -> dict[float, int]:
    indices: dict[float, int] = {}
    for radius in OFFICIAL_RADII_CM:
        index = min(range(len(result.grid.nodes_m)), key=lambda i: abs(result.grid.nodes_m[i] * 100.0 - radius))
        if abs(result.grid.nodes_m[index] * 100.0 - radius) > 1.0e-10:
            raise RuntimeError(f"requested radius {radius:g} cm is not an explicit grid node")
        indices[float(radius)] = index
    return indices


def save_snapshots(path: Path, result) -> dict[str, dict[str, float]]:
    indices = radius_indices(result)
    rows: list[dict[str, float]] = []
    for time_s in SELECTED_TIMES_S:
        temperature_k, moisture = result.snapshot_at(time_s)
        for radius in OFFICIAL_RADII_CM:
            index = indices[float(radius)]
            rows.append({
                "time_s": time_s,
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


def compare(left: dict[str, dict[str, float]], right: dict[str, dict[str, float]]) -> tuple[dict[str, Any], list[dict[str, float]]]:
    rows: list[dict[str, float]] = []
    for key in sorted(set(left) & set(right), key=lambda item: tuple(float(x) for x in item.split("|"))):
        a, b = left[key], right[key]
        signed_t = a["temperature_C"] - b["temperature_C"]
        signed_c = a["moisture_kg_kg"] - b["moisture_kg_kg"]
        rows.append({
            "time_s": a["time_s"],
            "radius_cm": a["radius_cm"],
            "temperature_signed_error_C": signed_t,
            "temperature_absolute_error_C": abs(signed_t),
            "moisture_signed_error_kg_kg": signed_c,
            "moisture_absolute_error_kg_kg": abs(signed_c),
        })

    def rms(name: str) -> float:
        values = [row[name] for row in rows]
        return math.sqrt(sum(value * value for value in values) / len(values)) if values else 0.0

    def maximum(abs_name: str, signed_name: str, unit: str) -> dict[str, float | str]:
        row = max(rows, key=lambda item: item[abs_name], default=None)
        if row is None:
            return {"absolute_error": 0.0, "signed_error": 0.0, "unit": unit}
        return {
            "absolute_error": row[abs_name],
            "signed_error": row[signed_name],
            "time_s": row["time_s"],
            "radius_cm": row["radius_cm"],
            "unit": unit,
        }

    by_time: dict[str, dict[str, float]] = {}
    for row in rows:
        item = by_time.setdefault(str(row["time_s"]), {
            "temperature_Linf_C": 0.0,
            "moisture_Linf_kg_kg": 0.0,
        })
        item["temperature_Linf_C"] = max(item["temperature_Linf_C"], row["temperature_absolute_error_C"])
        item["moisture_Linf_kg_kg"] = max(item["moisture_Linf_kg_kg"], row["moisture_absolute_error_kg_kg"])
    metrics = {
        "sample_count": len(rows),
        "temperature_Linf_C": max((row["temperature_absolute_error_C"] for row in rows), default=0.0),
        "temperature_L2_RMS_C": rms("temperature_absolute_error_C"),
        "moisture_Linf_kg_kg": max((row["moisture_absolute_error_kg_kg"] for row in rows), default=0.0),
        "moisture_L2_RMS_kg_kg": rms("moisture_absolute_error_kg_kg"),
        "temperature_max_location": maximum("temperature_absolute_error_C", "temperature_signed_error_C", "C"),
        "moisture_max_location": maximum("moisture_absolute_error_kg_kg", "moisture_signed_error_kg_kg", "kg/kg"),
        "by_time": by_time,
    }
    return metrics, rows


def run_case(name: str, config: Q2RunConfig) -> tuple[dict[str, Any], dict[str, dict[str, float]]]:
    case_dir = OUT / name
    case_dir.mkdir(parents=True, exist_ok=False)
    write_json(case_dir / "config.json", config.as_dict())
    diagnostics_path = case_dir / "diagnostics_3600s.csv"
    result = run_q2(
        config,
        record_times=(0.0,) + SELECTED_TIMES_S,
        diagnostics_path=diagnostics_path,
        diagnostics_interval_s=3600.0,
    )
    snapshots = save_snapshots(case_dir / "snapshots.csv", result)
    summary = {
        "name": name,
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
        "snapshots": str((case_dir / "snapshots.csv").relative_to(ROOT)).replace("\\", "/"),
        "diagnostics": {
            "path": str(diagnostics_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(diagnostics_path),
        },
    }
    write_json(case_dir / "metrics.json", summary)
    del result
    gc.collect()
    return summary, snapshots


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=False)
    base = load_base_config()
    candidate = replace(
        base,
        end_time_s=228635.0,
        time_step_s=1.0,
        n_intervals=320,
        cluster_power=3.0,
        reset_bdf2_at_environment_transition=True,
        early_time_step_s=0.015625,
        early_time_end_s=5.0,
    )
    reference = replace(
        base,
        end_time_s=228635.0,
        time_step_s=1.0,
        n_intervals=160,
        cluster_power=2.0,
        reset_bdf2_at_environment_transition=True,
        early_time_step_s=0.015625,
        early_time_end_s=5.0,
    )
    print("[Q2 targeted long] candidate n320/cluster3 dt=1", flush=True)
    candidate_summary, candidate_snapshots = run_case("candidate_dt1_n320_cluster3", candidate)
    print("[Q2 targeted long] reference n160/cluster2 dt=1", flush=True)
    reference_summary, reference_snapshots = run_case("reference_dt1_n160_cluster2", reference)
    comparison, rows = compare(candidate_snapshots, reference_snapshots)
    comparison_path = OUT / "comparison.csv"
    with comparison_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    old_confirmation_path = ROOT / "experiments" / "Q2_FREEZE_RUN" / "accuracy_confirmation.json"
    old_confirmation = json.loads(old_confirmation_path.read_text(encoding="utf-8"))
    old_long = old_confirmation["temporal"]["against_dt0.125"]["selected_times"]
    old_long = {key: old_long[key] for key in ("1800", "3600", "7200", "10800", "207033", "207034", "207035", "207036", "228635") if key in old_long}
    metrics = {
        "experiment": "EXP-Q2-ACC-LONG-TARGETED",
        "status": "TARGETED_LONG_HORIZON_ACCURACY_CERTIFICATION",
        "purpose": "selected long-time spatial propagation and late-time stability screen; not a full n=640 replay",
        "selected_times_s": list(SELECTED_TIMES_S),
        "passive_event_neighborhood": {
            "bracket_s": [207034.5, 207034.75],
            "integer_seconds_checked": [207033.0, 207034.0, 207035.0, 207036.0],
        },
        "candidate": candidate_summary,
        "reference": reference_summary,
        "raw_pairwise_comparison": comparison,
        "comparison_csv": str(comparison_path.relative_to(ROOT)).replace("\\", "/"),
        "gate": {"temperature_C": GATE_T, "moisture_kg_kg": GATE_C},
        "selected_point_gate_pass": comparison["temperature_Linf_C"] <= GATE_T and comparison["moisture_Linf_kg_kg"] <= GATE_C,
        "reused_old_0_72h_evidence": {
            "source": "experiments/Q2_FREEZE_RUN/accuracy_confirmation.json",
            "scope": "old n=80 ENV-B production candidate time comparison against dt=.125 reference; stability/late-error evidence only",
            "selected_times": old_long,
            "not_a_v3_grid_accuracy_claim": True,
        },
        "unchanged_numerical_elements": [
            "official initial condition",
            "ENV-B post-14400 constants",
            "linear attachment interpolation",
            "harmonic face averaging",
            "h=25 W/(m2 K) and hm=8e-7 m/s",
            "BDF2 production scheme with event-aligned BE restart",
        ],
        "changed_numerical_element_under_screen": "boundary-clustered radial grid: n=320/cluster_power=3 versus n=160/cluster_power=2",
        "time_step_screen_note": "dt=1 s is a targeted long-horizon screen; formal time accuracy is not inferred from this screen and is certified separately on localized formal lattices",
        "workbook_written": False,
    }
    write_json(OUT / "metrics.json", metrics)
    (OUT / "notes.md").write_text(
        "# EXP-Q2-ACC-LONG-TARGETED\n\n"
        "This is a targeted long-horizon certification screen, not an n=640 "
        "full-horizon convergence run. The proposed n=320/cluster_power=3 "
        "configuration and a moderate n=160/cluster_power=2 comparator were "
        "both advanced continuously from t=0 to 228635 s. Selected official "
        "output times cover 3/6/12/24/36/48 h, the passive-event neighborhood, "
        "and the final production point. dt=1 s is used only to make this "
        "long-time spatial/stability screen affordable; formal time accuracy "
        "comes from EXP-Q2-ACC-T-FORMAL and EXP-Q2-ACC-C-FORMAL. Historical "
        "0–72 h evidence is included as stability context and is not silently "
        "treated as a V3-grid accuracy proof.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "COMPLETE", "comparison": comparison}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
