"""Build the final Q4 asymptotic certification record without rerunning a solver."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPATIAL = ROOT / "experiments" / "Q4_SPATIAL_CONVERGENCE_FINAL"
OUT = ROOT / "experiments" / "Q4_FINAL_ASYMPTOTIC_CERTIFICATION"


def main() -> None:
    spatial = json.loads((SPATIAL / "q4_final_asymptotic_spatial_estimates.json").read_text(encoding="utf-8"))
    temporal = json.loads((OUT / "temporal_run_J_n384_dt1.json").read_text(encoding="utf-8"))
    previous = json.loads((ROOT / "experiments/Q4_CONVERGENCE_FINAL/q4_error_decomposition.json").read_text(encoding="utf-8"))

    t_dt4_s = float(previous["configs"]["C_n144_dt4"]["t4_s"])
    t_dt2_s = float(previous["configs"]["D_n144_dt2"]["t4_s"])
    t_n384_dt2_s = float(spatial["runs"]["384"]["t4_s"])
    t_n384_dt1_s = float(temporal["root_refinement"]["t_cross_linear_s"])
    delta_4_to_2_s = t_dt2_s - t_dt4_s
    delta_2_to_1_s = t_n384_dt1_s - t_n384_dt2_s
    temporal_order = math.log(abs(delta_4_to_2_s) / abs(delta_2_to_1_s), 2.0)
    t_dt0_n384_s = 2.0 * t_n384_dt1_s - t_n384_dt2_s
    temporal_correction_to_dt0_s = t_dt0_n384_s - t_n384_dt2_s
    spatial_estimate_h = float(spatial["spatial_estimate"]["recommended_t_inf_h"])
    spatial_estimate_s = spatial_estimate_h * 3600.0
    final_t4_s = spatial_estimate_s + temporal_correction_to_dt0_s
    temporal_uncertainty_h = abs(delta_2_to_1_s) / 3600.0
    root_uncertainty_h = float(temporal["root_refinement"]["bracket_width_s"]) / 3600.0
    spatial_uncertainty_h = float(spatial["spatial_estimate"]["conservative_spatial_uncertainty_h"])
    numerical_uncertainty_h = spatial_uncertainty_h + temporal_uncertainty_h + root_uncertainty_h
    temporal_correction_h = temporal_correction_to_dt0_s / 3600.0
    time_corrected_method_estimates = []
    for item in spatial["spatial_continuum_estimates"]:
        estimate_h = float(item["fit"]["t_inf_h"])
        time_corrected_method_estimates.append({
            "family": item["family"],
            "spatial_dt2_t_inf_h": estimate_h,
            "time_corrected_dt0_t_inf_h": estimate_h + temporal_correction_h,
        })
    interpolation = json.loads((ROOT / "experiments/Q4_CONVERGENCE_FINAL/interpolation_sensitivity_n192_dt2.json").read_text(encoding="utf-8"))
    interpolation_delta_h = float(interpolation["difference_linear_minus_pchip"]["absolute_h"])
    p_values = [float(item["fit"]["p"]) for item in spatial["spatial_continuum_estimates"] if item["fit"].get("p") is not None]
    p_drift = max(p_values) - min(p_values)
    spatial_pass = spatial_uncertainty_h <= interpolation_delta_h and p_drift <= 0.05
    temporal_pass = 0.8 <= temporal_order <= 1.2 and delta_4_to_2_s * delta_2_to_1_s > 0.0
    final_status = "PASS" if spatial_pass and temporal_pass else "HOLD"
    payload: dict[str, Any] = {
        "experiment": "Q4_FINAL_ASYMPTOTIC_CERTIFICATION",
        "status": final_status,
        "constraints": {
            "no_solver_rerun_after_required_runs": True,
            "no_n640": True,
            "external_reference_used_as_fit_target": False,
            "frozen_result4_modified": False,
        },
        "spatial": {
            "source": "experiments/Q4_SPATIAL_CONVERGENCE_FINAL/q4_final_asymptotic_spatial_estimates.json",
            "runs": spatial["runs"],
            "estimates": spatial["spatial_continuum_estimates"],
            "recommended_dt2_continuum_h": spatial_estimate_h,
            "recommended_dt2_continuum_s": spatial_estimate_s,
            "method_envelope_h": spatial["spatial_estimate"]["method_envelope_h"],
            "last_grid_to_continuum_relation_h": spatial["spatial_estimate"]["max_last_grid_to_continuum_relation_h"],
            "conservative_spatial_uncertainty_h": spatial_uncertainty_h,
            "p_range": [min(p_values), max(p_values)],
            "p_drift": p_drift,
            "pass": spatial_pass,
        },
        "temporal": {
            "source": "experiments/Q4_FINAL_ASYMPTOTIC_CERTIFICATION/temporal_run_J_n384_dt1.json",
            "n": 384,
            "dt4_reference_h": t_dt4_s / 3600.0,
            "dt2_h": t_n384_dt2_s / 3600.0,
            "dt1_h": t_n384_dt1_s / 3600.0,
            "delta_dt4_to_dt2_s_at_n144": delta_4_to_2_s,
            "delta_dt2_to_dt1_s_at_n384": delta_2_to_1_s,
            "observed_order_q_supporting": temporal_order,
            "direction_consistent": delta_4_to_2_s * delta_2_to_1_s > 0.0,
            "dt0_extrapolated_n384_s": t_dt0_n384_s,
            "dt0_extrapolated_n384_h": t_dt0_n384_s / 3600.0,
            "dt2_to_dt0_correction_s": temporal_correction_to_dt0_s,
            "dt2_to_dt0_correction_h": temporal_correction_h,
            "estimated_remaining_temporal_uncertainty_h": temporal_uncertainty_h,
            "pass": temporal_pass,
        },
        "root_uncertainty_h": root_uncertainty_h,
        "interpolation_sensitivity": {
            "source": "experiments/Q4_CONVERGENCE_FINAL/interpolation_sensitivity_n192_dt2.json",
            "linear_minus_pchip_s": interpolation["difference_linear_minus_pchip"]["delta_s"],
            "absolute_h": interpolation_delta_h,
            "classification": "MODELING / INTERPOLATION SENSITIVITY",
            "production_choice": "PCHIP",
        },
        "final_continuum": {
            "formula": "space dt=2 continuum estimate + n=384 first-order dt=2 to dt=0 correction",
            "space_first_estimate_h": spatial_estimate_h,
            "time_corrected_method_estimates": time_corrected_method_estimates,
            "space_first_to_time_corrected_difference_h": abs(temporal_correction_h),
            "t4_star_s": final_t4_s,
            "t4_star_h": final_t4_s / 3600.0,
            "paper_value_4_decimal_h": round(final_t4_s / 3600.0, 4),
            "R_t4_cm": 1.2,
            "controlling_point": "center / xi=0",
            "difference_from_old_frozen_53_0827_h": final_t4_s / 3600.0 - 53.08270378038297,
            "difference_from_external_51_0823_h": final_t4_s / 3600.0 - 51.0823,
        },
        "uncertainty": {
            "spatial_discretization_h": spatial_uncertainty_h,
            "temporal_discretization_h": temporal_uncertainty_h,
            "root_location_h": root_uncertainty_h,
            "conservative_numerical_total_h": numerical_uncertainty_h,
            "numerical_total_seconds": numerical_uncertainty_h * 3600.0,
            "relative_to_interpolation_sensitivity": numerical_uncertainty_h / interpolation_delta_h,
            "criterion": "final certification requires stable asymptotics and numerical uncertainty not exceeding interpolation sensitivity",
        },
        "decision": {
            "q4_final_numerical_certification": final_status,
            "corrected_candidate_created": False,
            "final_result4_replaced": False,
            "next_action": "stop automatic refinement; await human decision" if final_status == "HOLD" else "await human replacement approval",
        },
    }
    output = OUT / "q4_final_asymptotic_certification.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": final_status, "final_continuum": payload["final_continuum"], "uncertainty": payload["uncertainty"], "spatial_pass": spatial_pass, "temporal_pass": temporal_pass}, ensure_ascii=False))


if __name__ == "__main__":
    main()
