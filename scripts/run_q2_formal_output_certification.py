"""Targeted Q2 formal-output accuracy certification.

The delivery gate is evaluated only on the declared integer-second x official
radius lattice.  Non-integer solver states remain in a separate diagnostic
record so that boundedness and propagation can be checked without silently
turning an internal probe into a delivery-point failure.

This script does not run Q2_FREEZE_RUN_V3, generate result2.xlsx, or create
formal Q2 figures.
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import math
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q2 import Q2RunConfig, run_q2
from scripts.run_q2_accuracy_remediation import load_base_config, sha256


TRANSITION_OUT = ROOT / "experiments" / "EXP-Q2-ACC-T-FORMAL"
EARLY_OUT = ROOT / "experiments" / "EXP-Q2-ACC-C-FORMAL"
GATE_T = 2.5e-5
GATE_C = 2.5e-5
OFFICIAL_RADII_CM = tuple(0.1 * index for index in range(21))
TRANSITION_RADII_CM = (0.0, 0.5, 1.0, 1.5, 1.9, 2.0)
TRANSITION_INTEGER_TIMES = tuple(float(value) for value in range(14395, 14501))
TRANSITION_LOCAL_TIMES = (14400.25, 14400.50, 14400.75)
EARLY_TIMES = (1.0, 2.0, 3.0, 4.0, 5.0, 10.0, 20.0, 30.0, 60.0, 100.0, 300.0, 600.0, 1800.0)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def radius_indices(result, radii_cm: Iterable[float]) -> dict[float, int]:
    result_indices = {}
    for radius in radii_cm:
        index = min(range(len(result.grid.nodes_m)), key=lambda i: abs(result.grid.nodes_m[i] * 100.0 - radius))
        if abs(result.grid.nodes_m[index] * 100.0 - radius) > 1.0e-10:
            raise RuntimeError(f"requested radius {radius:g} cm is not an explicit grid node")
        result_indices[float(radius)] = index
    return result_indices


def save_snapshots(path: Path, result, times: Iterable[float], radii_cm: Iterable[float]) -> dict[str, dict[str, float]]:
    indices = radius_indices(result, radii_cm)
    rows: list[dict[str, float]] = []
    for time_s in times:
        temperature_k, moisture = result.snapshot_at(time_s)
        for radius in radii_cm:
            index = indices[float(radius)]
            rows.append({
                "time_s": float(time_s),
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


def load_snapshots(path: Path) -> dict[str, dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            f"{float(row['time_s']):.12g}|{float(row['radius_cm']):.12g}": {
                key: float(value) for key, value in row.items()
            }
            for row in csv.DictReader(handle)
        }


def compare(left: dict[str, dict[str, float]], right: dict[str, dict[str, float]]) -> dict[str, Any]:
    common = sorted(set(left) & set(right))
    t_values: list[float] = []
    c_values: list[float] = []
    t_max = {"absolute_error": -1.0}
    c_max = {"absolute_error": -1.0}
    by_radius: dict[str, dict[str, float]] = {}
    for key in common:
        a, b = left[key], right[key]
        signed_t = float(a["temperature_C"] - b["temperature_C"])
        signed_c = float(a["moisture_kg_kg"] - b["moisture_kg_kg"])
        abs_t, abs_c = abs(signed_t), abs(signed_c)
        t_values.append(abs_t)
        c_values.append(abs_c)
        location = {"time_s": float(a["time_s"]), "radius_cm": float(a["radius_cm"])}
        if abs_t > t_max["absolute_error"]:
            t_max = {"absolute_error": abs_t, "signed_error": signed_t, **location}
        if abs_c > c_max["absolute_error"]:
            c_max = {"absolute_error": abs_c, "signed_error": signed_c, **location}
        item = by_radius.setdefault(str(a["radius_cm"]), {"temperature_Linf_C": 0.0, "moisture_Linf_kg_kg": 0.0})
        item["temperature_Linf_C"] = max(item["temperature_Linf_C"], abs_t)
        item["moisture_Linf_kg_kg"] = max(item["moisture_Linf_kg_kg"], abs_c)

    def rms(values: list[float]) -> float:
        return math.sqrt(sum(value * value for value in values) / len(values)) if values else 0.0

    return {
        "sample_count": len(common),
        "temperature_Linf_C": max(t_values, default=0.0),
        "temperature_L2_RMS_C": rms(t_values),
        "moisture_Linf_kg_kg": max(c_values, default=0.0),
        "moisture_L2_RMS_kg_kg": rms(c_values),
        "temperature_max_location": t_max,
        "moisture_max_location": c_max,
        "by_radius": by_radius,
    }


def run_case(name: str, config: Q2RunConfig, out_dir: Path, times: tuple[float, ...], radii: tuple[float, ...], diagnostics_interval_s: float) -> dict[str, Any]:
    case_dir = out_dir / name
    case_dir.mkdir(parents=True, exist_ok=False)
    write_json(case_dir / "config.json", config.as_dict())
    diagnostics_path = case_dir / "diagnostics.csv"
    result = run_q2(config, record_times=times, diagnostics_path=diagnostics_path, diagnostics_interval_s=diagnostics_interval_s)
    snapshots_path = case_dir / "snapshots.csv"
    snapshot_index = save_snapshots(snapshots_path, result, times, radii)
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
        "diagnostic_summary": {key: value for key, value in result.diagnostic_summary.items() if isinstance(value, (int, float)) and math.isfinite(float(value))},
        "snapshots": str(snapshots_path.relative_to(ROOT)).replace("\\", "/"),
        "diagnostics": {
            "path": str(diagnostics_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(diagnostics_path),
        },
    }
    write_json(case_dir / "metrics.json", summary)
    del result
    gc.collect()
    return {"summary": summary, "snapshots": snapshot_index}


def transition_formal(base: Q2RunConfig) -> None:
    TRANSITION_OUT.mkdir(parents=True, exist_ok=False)
    times = tuple(sorted(set(TRANSITION_INTEGER_TIMES + TRANSITION_LOCAL_TIMES)))
    candidate = replace(base, end_time_s=14500.0, time_step_s=0.25, n_intervals=320, cluster_power=3.0, reset_bdf2_at_environment_transition=True, early_time_step_s=0.015625, early_time_end_s=2.0)
    reference = replace(candidate, time_step_s=0.125)
    print("[Q2 formal] transition candidate dt=.25", flush=True)
    a = run_case("candidate_dt0.25_n320_cluster3", candidate, TRANSITION_OUT, times, TRANSITION_RADII_CM, 0.25)
    print("[Q2 formal] transition reference dt=.125", flush=True)
    b = run_case("reference_dt0.125_n320_cluster3", reference, TRANSITION_OUT, times, TRANSITION_RADII_CM, 0.25)
    a_integer = {key: value for key, value in a["snapshots"].items() if float(value["time_s"]).is_integer() and 14395 <= float(value["time_s"]) <= 14500}
    b_integer = {key: value for key, value in b["snapshots"].items() if float(value["time_s"]).is_integer() and 14395 <= float(value["time_s"]) <= 14500}
    a_local = {key: value for key, value in a["snapshots"].items() if not float(value["time_s"]).is_integer()}
    b_local = {key: value for key, value in b["snapshots"].items() if not float(value["time_s"]).is_integer()}
    metrics = {
        "experiment": "EXP-Q2-ACC-T-FORMAL",
        "status": "FORMAL_OUTPUT_AUDIT",
        "formal_scope": {"times_s": [14395.0, 14500.0], "cadence_s": 1.0, "radii_cm": list(TRANSITION_RADII_CM)},
        "internal_probe_times_s": list(TRANSITION_LOCAL_TIMES),
        "candidate": a["summary"],
        "reference": b["summary"],
        "formal_integer_output_comparison": compare(a_integer, b_integer),
        "internal_probe_comparison": compare(a_local, b_local),
        "gate": {"temperature_C": GATE_T, "moisture_kg_kg": GATE_C},
        "internal_spike_delivery_impact": "NO" if compare(a_integer, b_integer)["temperature_Linf_C"] <= GATE_T and compare(a_integer, b_integer)["moisture_Linf_kg_kg"] <= GATE_C else "YES",
        "not_a_full_horizon_confirmation": True,
    }
    write_json(TRANSITION_OUT / "metrics.json", metrics)
    (TRANSITION_OUT / "notes.md").write_text(
        "# EXP-Q2-ACC-T-FORMAL\n\n"
        "The integer-second formal output lattice is evaluated separately from "
        "the non-integer 14400.25/14400.50/14400.75 s internal probes. Both "
        "runs start at t=0 with the frozen physics, ENV-B values, harmonic "
        "interfaces, n=320/cluster_power=3, early refinement, and event-aligned "
        "BE restart. Raw differences are not Richardson uncertainty.\n",
        encoding="utf-8",
    )


def early_formal(base: Q2RunConfig) -> None:
    EARLY_OUT.mkdir(parents=True, exist_ok=False)
    candidate = replace(base, end_time_s=1800.0, time_step_s=0.25, n_intervals=320, cluster_power=3.0, reset_bdf2_at_environment_transition=True, early_time_step_s=0.015625, early_time_end_s=2.0)
    reference = replace(base, end_time_s=1800.0, time_step_s=0.015625, n_intervals=640, cluster_power=2.0, reset_bdf2_at_environment_transition=False, early_time_step_s=None, early_time_end_s=0.0)
    print("[Q2 formal] early candidate n320/cluster3", flush=True)
    a = run_case("candidate_dt0.25_n320_cluster3", candidate, EARLY_OUT, EARLY_TIMES, OFFICIAL_RADII_CM, 1.0)
    print("[Q2 formal] early spatial-temporal reference n640/cluster2 dt=.015625", flush=True)
    b = run_case("reference_dt0.015625_n640_cluster2", reference, EARLY_OUT, EARLY_TIMES, OFFICIAL_RADII_CM, 1.0)
    metrics = {
        "experiment": "EXP-Q2-ACC-C-FORMAL",
        "status": "FORMAL_OUTPUT_AUDIT",
        "formal_scope": {"times_s": list(EARLY_TIMES), "radii_cm": list(OFFICIAL_RADII_CM)},
        "candidate": a["summary"],
        "reference": b["summary"],
        "formal_output_comparison": compare(a["snapshots"], b["snapshots"]),
        "gate": {"temperature_C": GATE_T, "moisture_kg_kg": GATE_C},
        "not_a_full_horizon_confirmation": True,
    }
    write_json(EARLY_OUT / "metrics.json", metrics)
    (EARLY_OUT / "notes.md").write_text(
        "# EXP-Q2-ACC-C-FORMAL\n\n"
        "The candidate is evaluated only on the requested formal integer times "
        "and all 21 official radii. The n=640/cluster_power=2 dt=.015625 s "
        "reference starts from the same official initial condition and uses the "
        "same frozen physics. Differences are raw fine/coarse comparisons, not "
        "optimistic Richardson uncertainty.\n",
        encoding="utf-8",
    )


def early_formal_policy_reference(base: Q2RunConfig) -> None:
    """Re-certify early outputs against a finer reference with the same policy."""
    if not EARLY_OUT.is_dir():
        raise RuntimeError("run --stage early before --stage early-policy")
    candidate_case = EARLY_OUT / "candidate_dt0.25_n320_cluster3"
    candidate_metrics_path = candidate_case / "metrics.json"
    candidate_snapshots_path = candidate_case / "snapshots.csv"
    if not candidate_metrics_path.is_file() or not candidate_snapshots_path.is_file():
        raise RuntimeError("formal early candidate artifacts are missing")
    old_metrics_path = EARLY_OUT / "metrics.json"
    old_metrics = json.loads(old_metrics_path.read_text(encoding="utf-8")) if old_metrics_path.is_file() else None
    reference_name = "reference_policy_dt0.125_n640_cluster2"
    reference_case = EARLY_OUT / reference_name
    reference_config = replace(base, end_time_s=1800.0, time_step_s=0.125, n_intervals=640, cluster_power=2.0, reset_bdf2_at_environment_transition=True, early_time_step_s=0.015625, early_time_end_s=2.0)
    if reference_case.exists():
        raise RuntimeError(f"refusing to overwrite existing reference case: {reference_case}")
    print("[Q2 formal] early same-policy reference n640/cluster2 dt=.125", flush=True)
    reference = run_case(reference_name, reference_config, EARLY_OUT, EARLY_TIMES, OFFICIAL_RADII_CM, 1.0)
    candidate_summary = json.loads(candidate_metrics_path.read_text(encoding="utf-8"))
    candidate = {"summary": candidate_summary, "snapshots": load_snapshots(candidate_snapshots_path)}
    comparison = compare(candidate["snapshots"], reference["snapshots"])
    metrics = {
        "experiment": "EXP-Q2-ACC-C-FORMAL",
        "status": "FORMAL_OUTPUT_AUDIT",
        "formal_scope": {"times_s": list(EARLY_TIMES), "radii_cm": list(OFFICIAL_RADII_CM)},
        "candidate": candidate["summary"],
        "reference": reference["summary"],
        "formal_output_comparison": comparison,
        "same_policy_as_candidate": True,
        "prior_uniform_reference_comparison": old_metrics.get("formal_output_comparison") if old_metrics else None,
        "gate": {"temperature_C": GATE_T, "moisture_kg_kg": GATE_C},
        "not_a_full_horizon_confirmation": True,
    }
    write_json(EARLY_OUT / "metrics.json", metrics)
    (EARLY_OUT / "notes.md").write_text(
        "# EXP-Q2-ACC-C-FORMAL\n\n"
        "The candidate is evaluated on the requested integer times and all 21 "
        "official radii. The selected reference uses the same early-time policy "
        "(dt=.015625 s through t=2 s, then BE restart) with a finer main dt=.125 s "
        "and n=640/cluster_power=2. The earlier uniform-dt reference remains in "
        "the directory as a diagnostic of policy sensitivity; it is not mixed into "
        "the formal candidate/reference comparison. All values retain full float "
        "precision and are raw differences, not optimistic Richardson estimates.\n",
        encoding="utf-8",
    )


def early_formal_policy5(base: Q2RunConfig) -> None:
    """Test whether extending the fine-step startup window removes the t=3 s dip."""
    if not EARLY_OUT.is_dir():
        raise RuntimeError("run --stage early before --stage early-policy5")
    candidate_name = "candidate_dt0.25_n320_cluster3_early5"
    reference_name = "reference_policy_dt0.125_n640_cluster2_early5"
    candidate_config = replace(
        base,
        end_time_s=1800.0,
        time_step_s=0.25,
        n_intervals=320,
        cluster_power=3.0,
        reset_bdf2_at_environment_transition=True,
        early_time_step_s=0.015625,
        early_time_end_s=5.0,
    )
    reference_config = replace(
        base,
        end_time_s=1800.0,
        time_step_s=0.125,
        n_intervals=640,
        cluster_power=2.0,
        reset_bdf2_at_environment_transition=True,
        early_time_step_s=0.015625,
        early_time_end_s=5.0,
    )
    if (EARLY_OUT / candidate_name).exists() or (EARLY_OUT / reference_name).exists():
        raise RuntimeError("refusing to overwrite existing early5 certification cases")
    print("[Q2 formal] early5 candidate n320/cluster3", flush=True)
    candidate = run_case(candidate_name, candidate_config, EARLY_OUT, EARLY_TIMES, OFFICIAL_RADII_CM, 1.0)
    print("[Q2 formal] early5 same-policy reference n640/cluster2 dt=.125", flush=True)
    reference = run_case(reference_name, reference_config, EARLY_OUT, EARLY_TIMES, OFFICIAL_RADII_CM, 1.0)
    comparison = compare(candidate["snapshots"], reference["snapshots"])
    prior_metrics_path = EARLY_OUT / "metrics.json"
    prior_metrics = json.loads(prior_metrics_path.read_text(encoding="utf-8")) if prior_metrics_path.is_file() else {}
    metrics = {
        "experiment": "EXP-Q2-ACC-C-FORMAL",
        "status": "FORMAL_OUTPUT_AUDIT",
        "formal_scope": {"times_s": list(EARLY_TIMES), "radii_cm": list(OFFICIAL_RADII_CM)},
        "candidate": candidate["summary"],
        "reference": reference["summary"],
        "formal_output_comparison": comparison,
        "same_policy_as_candidate": True,
        "early_refinement_end_s": 5.0,
        "policy2_comparison": prior_metrics.get("formal_output_comparison"),
        "gate": {"temperature_C": GATE_T, "moisture_kg_kg": GATE_C},
        "not_a_full_horizon_confirmation": True,
    }
    write_json(EARLY_OUT / "metrics.json", metrics)
    (EARLY_OUT / "notes.md").write_text(
        "# EXP-Q2-ACC-C-FORMAL\n\n"
        "The first same-policy audit (fine startup through t=2 s) exceeded the "
        "moisture gate at t=3 s, immediately after the main-step switch. This "
        "follow-up extends the identical fine startup policy through t=5 s. "
        "The n=640/cluster_power=2 reference uses the same t=5 s policy and a "
        "main dt=.125 s. The formal lattice remains the requested integer times "
        "and all 21 official radii. Values retain full float precision; the "
        "comparison is raw fine/coarse error, not Richardson extrapolation.\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("transition", "early", "early-policy", "early-policy5", "all"), default="all")
    args = parser.parse_args()
    base = load_base_config()
    if args.stage in {"transition", "all"}:
        transition_formal(base)
    if args.stage in {"early", "all"}:
        early_formal(base)
    if args.stage in {"early-policy", "all"}:
        early_formal_policy_reference(base)
    if args.stage == "early-policy5":
        early_formal_policy5(base)
    print(json.dumps({"status": "COMPLETE", "stage": args.stage}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
