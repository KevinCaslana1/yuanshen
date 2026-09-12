"""Build the Q4 A/B/C/D space/time error decomposition record."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "Q4_CONVERGENCE_FINAL"


def load_runs() -> dict[str, dict[str, object]]:
    old = json.loads((ROOT / "experiments/Q34_INDEPENDENT_AUDIT/audit.json").read_text(encoding="utf-8"))
    new = json.loads((OUT / "new_runs_B_C.json").read_text(encoding="utf-8"))
    rows = {
        "A_n96_dt4": next(r for r in old["q4"]["independent_runs"] if r["name"] == "independent_production"),
        "D_n144_dt2": next(r for r in old["q4"]["independent_runs"] if r["name"] == "independent_finer"),
    }
    rows.update({r["name"]: r for r in new["runs"]})
    next_path = OUT / "next_refinement_n192_dt2.json"
    if next_path.exists():
        raw = json.loads(next_path.read_text(encoding="utf-8"))
        root = raw["root_refinement"]
        rows["E_n192_dt2"] = {
            "name": raw["name"],
            "n_intervals": raw["n_intervals"],
            "dt_s": raw["dt_s"],
            "runtime_s": raw["runtime_s"],
            "event": {
                "before_s": root["bracket_s"][0],
                "after_s": root["bracket_s"][1],
                "before_cmax": root["cmax_before"],
                "after_cmax": root["cmax_after"],
                "t_cross_linear_s": root["t_cross_linear_s"],
                "critical_radius_after_cm": root["critical_radius_after_cm"],
            },
            "conservation": {"max_abs_step": raw["conservation"]["max_abs_step"]},
            "robin": {"max_abs_flux_residual": raw["robin"]["max_abs_flux_residual"]},
            "picard": {"max_iterations": raw["picard"]["max_iterations"]},
        }
    return rows


def event_s(row: dict[str, object]) -> float:
    return float(row["event"]["t_cross_linear_s"])


def record_config(name: str, row: dict[str, object]) -> dict[str, object]:
    event = row["event"]
    return {
        "name": name,
        "n_intervals": int(row["n_intervals"]),
        "dt_s": float(row["dt_s"]),
        "runtime_s": float(row["runtime_s"]),
        "t4_s": event_s(row),
        "t4_h": event_s(row) / 3600.0,
        "root_bracket_s": [float(event["before_s"]), float(event["after_s"])],
        "root_bracket_width_s": float(event["after_s"]) - float(event["before_s"]),
        "cmax_before": float(event["before_cmax"]),
        "cmax_after": float(event["after_cmax"]),
        "critical_radius_after_cm": float(event["critical_radius_after_cm"]),
        "controlling_point": "center / xi=0" if float(event["critical_radius_after_cm"]) == 0.0 else "not center",
        "max_abs_step_mass_residual": float(row["conservation"]["max_abs_step"]),
        "max_abs_robin_residual": float(row["robin"]["max_abs_flux_residual"]),
        "max_picard_iterations": float(row["picard"]["max_iterations"]),
    }


def delta(rows: dict[str, dict[str, object]], left: str, right: str) -> dict[str, float]:
    value_s = event_s(rows[left]) - event_s(rows[right])
    return {"signed_s": value_s, "absolute_s": abs(value_s), "signed_h": value_s / 3600.0, "absolute_h": abs(value_s) / 3600.0}


def main() -> None:
    rows = load_runs()
    configs = {name: record_config(name, row) for name, row in rows.items()}
    deltas = {
        "delta_time_n96": delta(rows, "B_n96_dt2", "A_n96_dt4"),
        "delta_time_n144": delta(rows, "D_n144_dt2", "C_n144_dt4"),
        "delta_space_dt4": delta(rows, "C_n144_dt4", "A_n96_dt4"),
        "delta_space_dt2": delta(rows, "D_n144_dt2", "B_n96_dt2"),
    }
    if "E_n192_dt2" in rows:
        deltas["delta_space_dt2_n144_to_n192"] = delta(rows, "E_n192_dt2", "D_n144_dt2")
        deltas["delta_space_dt2_n96_to_n192"] = delta(rows, "E_n192_dt2", "B_n96_dt2")
    max_time_h = max(deltas["delta_time_n96"]["absolute_h"], deltas["delta_time_n144"]["absolute_h"])
    space_effects = [deltas["delta_space_dt4"]["absolute_h"], deltas["delta_space_dt2"]["absolute_h"]]
    if "delta_space_dt2_n144_to_n192" in deltas:
        space_effects.append(deltas["delta_space_dt2_n144_to_n192"]["absolute_h"])
    max_space_h = max(space_effects)
    selected = configs.get("E_n192_dt2", configs["D_n144_dt2"])
    root_error_h = selected["root_bracket_width_s"] / 3600.0
    fine_space_h = deltas.get("delta_space_dt2_n144_to_n192", {"absolute_h": max_space_h})["absolute_h"]
    conservative_uncertainty_h = fine_space_h + max_time_h + root_error_h
    spatial_order = None
    if "delta_space_dt2_n144_to_n192" in deltas:
        spatial_order = math.log(deltas["delta_space_dt2"]["absolute_s"] / deltas["delta_space_dt2_n144_to_n192"]["absolute_s"]) / math.log(1.5)
    payload = {
        "experiment": "Q4_CONVERGENCE_FINAL",
        "status": "HOLD_MINIMUM_REFINEMENT_NOT_WITHIN_PAPER_UNCERTAINTY" if "E_n192_dt2" in rows else "SPATIAL_DOMINANT_NEXT_REFINEMENT_REQUIRED",
        "method": "A/B/C/D crossed event times from independent fresh-t=0 standalone FVM/BE/Picard runs",
        "definitions": {
            "A": "n=96, dt=4 s",
            "B": "n=96, dt=2 s",
            "C": "n=144, dt=4 s",
            "D": "n=144, dt=2 s",
            "delta_time_n96": "B - A",
            "delta_time_n144": "D - C",
            "delta_space_dt4": "C - A",
            "delta_space_dt2": "D - B",
        },
        "configs": configs,
        "deltas": deltas,
        "dominance": {
            "max_abs_temporal_effect_h": max_time_h,
            "max_abs_spatial_effect_h": max_space_h,
            "spatial_to_temporal_ratio": max_space_h / max_time_h,
            "classification": "SPATIAL DOMINANT",
            "decision": "n=192, dt=2 s is the minimum necessary next refinement; no n=144, dt=1 s run was started.",
        },
        "selected_refinement": selected,
        "acceptance": {
            "paper_round4_uncertainty_limit_h": 0.00005,
            "current_best_estimate_h": selected["t4_h"],
            "spatial_raw_error_estimate_h": fine_space_h,
            "temporal_raw_error_estimate_h": max_time_h,
            "event_root_resolution_h": root_error_h,
            "conservative_uncertainty_h": conservative_uncertainty_h,
            "criterion_pass": conservative_uncertainty_h <= 0.00005,
            "richardson_used": False,
            "conclusion": "Current independent field discretization uncertainty remains far above the 0.00005 h paper criterion; do not build a corrected candidate.",
        },
        "paired_spatial_sequence_dt2": {
            "configs": ["B_n96_dt2", "D_n144_dt2", "E_n192_dt2"] if "E_n192_dt2" in rows else ["B_n96_dt2", "D_n144_dt2"],
            "refinement_ratio_n": 1.5,
            "observed_order_diagnostic": spatial_order,
            "use": "trend diagnostic only; no Richardson extrapolation used for acceptance",
        },
        "event_root_error": {
            "definition": "linear interpolation within the crossing time-step bracket; field runs are compared separately from root-location resolution",
            "bracket_widths_s": {name: configs[name]["root_bracket_width_s"] for name in configs},
            "conclusion": "The approximately 904 s A→D spatial effect and 285 s D→E fine spatial change are not root-location artifacts; A–D brackets are 2–4 s and E is locally refined to 0.0625 s.",
        },
        "external_reference": {
            "value_h": 51.0823,
            "role": "comparison reference only, not a target",
            "selected_minus_external_h": selected["t4_h"] - 51.0823,
            "conclusion": "C: the independent Q4 sequence is not converged, so no convergence-based judgment about the external value is made.",
        },
    }
    interpolation_path = OUT / "interpolation_sensitivity_n192_dt2.json"
    if interpolation_path.exists():
        interpolation = json.loads(interpolation_path.read_text(encoding="utf-8"))
        interpolation_summary = dict(interpolation["difference_linear_minus_pchip"])
        interpolation_summary.update({
            "pchip_t4_h": interpolation["pchip"]["t4_h"],
            "linear_t4_h": interpolation["linear"]["t4_h"],
            "interpretation": interpolation["interpretation"],
        })
        payload["interpolation_sensitivity"] = interpolation_summary
    (OUT / "q4_error_decomposition.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["dominance"], ensure_ascii=False))
    for key, value in deltas.items():
        print(key, json.dumps(value, ensure_ascii=False))


if __name__ == "__main__":
    main()
