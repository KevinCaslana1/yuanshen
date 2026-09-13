"""Fit non-equidistant Q4 spatial triplets to t(n)=t_inf+a*n**(-p).

The fit is intentionally spatial-only (all runs use dt=2 s).  It solves the
three-parameter model directly from each three-point triplet, so it does not
apply the equal-ratio Richardson shortcut.  With three observations and three
parameters the pointwise fit residual is a consistency diagnostic, not an
independent uncertainty estimate; adjacent extrapolated limits are reported
as the spatial extrapolation stability check.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "Q4_SPATIAL_CONVERGENCE_FINAL"


def load_runs() -> dict[int, dict[str, Any]]:
    decomposition = json.loads((ROOT / "experiments/Q4_CONVERGENCE_FINAL/q4_error_decomposition.json").read_text(encoding="utf-8"))
    configs = decomposition["configs"]
    runs: dict[int, dict[str, Any]] = {}
    for name, n in (("B_n96_dt2", 96), ("D_n144_dt2", 144), ("E_n192_dt2", 192)):
        row = configs[name]
        runs[n] = {
            "name": name,
            "n_intervals": n,
            "dt_s": row["dt_s"],
            "t4_s": row["t4_s"],
            "t4_h": row["t4_h"],
            "root_bracket_width_s": row["root_bracket_width_s"],
            "R_t4_cm": 1.2,
            "controlling_point": row["controlling_point"],
            "max_abs_step_mass_residual": row["max_abs_step_mass_residual"],
            "max_abs_robin_residual": row["max_abs_robin_residual"],
            "max_picard_iterations": row["max_picard_iterations"],
            "source": "Q4_CONVERGENCE_FINAL/q4_error_decomposition.json",
        }
    for n, label in ((256, "F"), (320, "G"), (384, "H")):
        path = OUT / f"spatial_run_{label}_n{n}_dt2.json"
        if not path.exists():
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        root = raw["root_refinement"]
        runs[n] = {
            "name": raw["name"],
            "n_intervals": n,
            "dt_s": raw["dt_s"],
            "t4_s": root["t_cross_linear_s"],
            "t4_h": root["t_cross_linear_h"],
            "root_bracket_width_s": root["bracket_width_s"],
            "R_t4_cm": root["R_t4_cm"],
            "controlling_point": root["controlling_point"],
            "max_abs_step_mass_residual": raw["conservation"]["max_abs_step"],
            "max_abs_robin_residual": raw["robin"]["max_abs_flux_residual"],
            "max_picard_iterations": raw["picard"]["max_iterations"],
            "source": path.relative_to(ROOT).as_posix(),
            "runtime_s": raw["runtime_s"],
        }
    return dict(sorted(runs.items()))


def model_ratio(p: float, ns: list[float]) -> float:
    values = [math.exp(-p * math.log(n)) for n in ns]
    return (values[0] - values[1]) / (values[1] - values[2])


def fit_triplet(ns_int: list[int], runs: dict[int, dict[str, Any]]) -> dict[str, Any]:
    ns = [float(n) for n in ns_int]
    ys = [float(runs[n]["t4_s"]) for n in ns_int]
    observed_ratio = (ys[0] - ys[1]) / (ys[1] - ys[2])

    def f(p: float) -> float:
        return model_ratio(p, ns) - observed_ratio

    grid = [1.0e-8] + [20.0 * i / 20000.0 for i in range(1, 20001)]
    left = grid[0]
    f_left = f(left)
    right = None
    for candidate in grid[1:]:
        f_candidate = f(candidate)
        if f_left == 0.0 or f_left * f_candidate <= 0.0:
            right = candidate
            break
        left, f_left = candidate, f_candidate
    if right is None:
        raise RuntimeError(f"could not bracket p for triplet {ns_int}")

    for _ in range(160):
        middle = (left + right) / 2.0
        f_middle = f(middle)
        if f(left) * f_middle <= 0.0:
            right = middle
        else:
            left = middle
    p = (left + right) / 2.0
    basis = [math.exp(-p * math.log(n)) for n in ns]
    a = (ys[0] - ys[1]) / (basis[0] - basis[1])
    t_inf_s = ys[0] - a * basis[0]
    predicted = [t_inf_s + a * x for x in basis]
    residuals_s = [predicted[i] - ys[i] for i in range(3)]
    return {
        "n": ns_int,
        "dt_s": 2.0,
        "observed_ratio": observed_ratio,
        "p": p,
        "a_s": a,
        "t_inf_s": t_inf_s,
        "t_inf_h": t_inf_s / 3600.0,
        "predicted_t4_s": predicted,
        "residuals_s": residuals_s,
        "max_abs_fit_residual_s": max(abs(x) for x in residuals_s),
        "l2_fit_residual_s": math.sqrt(sum(x * x for x in residuals_s)),
        "fit_model": "t(n)=t_inf+a*n^(-p); direct non-equidistant three-parameter fit",
    }


def main() -> None:
    runs = load_runs()
    available = sorted(runs)
    triplets: list[list[int]] = []
    for triplet in ([96, 144, 192], [144, 192, 256], [192, 256, 320], [256, 320, 384]):
        if all(n in runs for n in triplet):
            triplets.append(triplet)
    fits = [fit_triplet(triplet, runs) for triplet in triplets]
    limit_differences = []
    p_differences = []
    for older, newer in zip(fits, fits[1:]):
        limit_differences.append({
            "from_triplet": older["n"],
            "to_triplet": newer["n"],
            "signed_h": newer["t_inf_h"] - older["t_inf_h"],
            "absolute_h": abs(newer["t_inf_h"] - older["t_inf_h"]),
        })
        p_differences.append({
            "from_triplet": older["n"],
            "to_triplet": newer["n"],
            "signed": newer["p"] - older["p"],
            "absolute": abs(newer["p"] - older["p"]),
        })
    latest_limit_difference_h = limit_differences[-1]["absolute_h"] if limit_differences else None
    payload = {
        "experiment": "Q4_SPATIAL_CONVERGENCE_FINAL",
        "status": "HOLD_SPATIAL_EXTRAPOLATED_LIMIT_NOT_STABLE" if latest_limit_difference_h is None or latest_limit_difference_h > 0.00005 else "PASS_SPATIAL_EXTRAPOLATED_LIMIT",
        "method": "all runs dt=2 s; fresh t=0; t(n)=t_inf+a*n^(-p); non-equidistant direct fit",
        "available_runs": available,
        "runs": runs,
        "triplet_fits": fits,
        "adjacent_extrapolated_limit_differences": limit_differences,
        "adjacent_observed_order_differences": p_differences,
        "spatial_extrapolation_uncertainty_h": latest_limit_difference_h,
        "target_uncertainty_h": 0.00005,
        "fit_residual_interpretation": "Three points determine three parameters exactly; residual is a consistency check, while triplet-to-triplet limit stability is the uncertainty diagnostic.",
        "next_action": "run n=384, dt=2 s from fresh t=0" if 384 not in runs else "assess spatial stability before any temporal dt=1 verification",
    }
    output = OUT / "spatial_continuum_fits.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "fits": fits, "limit_differences": limit_differences}, ensure_ascii=False))


if __name__ == "__main__":
    main()
