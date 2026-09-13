"""Certify Q4 spatial asymptotics using several non-equidistant fits.

All inputs use dt=2 s.  Method A is a free-p nonlinear fit evaluated by
one-dimensional minimization with a linear solve for (t_inf, a) at each p.
Methods B and C are fixed linear least-squares fits for p=2 and p=2 plus a
scaled n^-3 correction.  No equal-ratio Richardson shortcut is used.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "Q4_SPATIAL_CONVERGENCE_FINAL"
SPATIAL_OUT = ROOT / "experiments" / "Q4_SPATIAL_CONVERGENCE_FINAL"


def load_runs() -> dict[int, dict[str, Any]]:
    old = json.loads((ROOT / "experiments/Q4_CONVERGENCE_FINAL/q4_error_decomposition.json").read_text(encoding="utf-8"))
    configs = old["configs"]
    runs: dict[int, dict[str, Any]] = {}
    for key, n in (("B_n96_dt2", 96), ("D_n144_dt2", 144), ("E_n192_dt2", 192)):
        row = configs[key]
        runs[n] = {
            "n": n,
            "dt_s": 2.0,
            "t4_s": float(row["t4_s"]),
            "t4_h": float(row["t4_h"]),
            "root_bracket_width_s": float(row["root_bracket_width_s"]),
            "R_t4_cm": 1.2,
            "controlling_point": row["controlling_point"],
            "max_abs_step_mass_residual": float(row["max_abs_step_mass_residual"]),
            "max_abs_robin_residual": float(row["max_abs_robin_residual"]),
            "max_picard_iterations": float(row["max_picard_iterations"]),
            "source": "experiments/Q4_CONVERGENCE_FINAL/q4_error_decomposition.json",
        }
    for n, label in ((256, "F"), (320, "G"), (384, "H"), (512, "I")):
        path = SPATIAL_OUT / f"spatial_run_{label}_n{n}_dt2.json"
        if not path.exists():
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        root = raw["root_refinement"]
        runs[n] = {
            "n": n,
            "dt_s": float(raw["dt_s"]),
            "t4_s": float(root["t_cross_linear_s"]),
            "t4_h": float(root["t_cross_linear_h"]),
            "root_bracket_width_s": float(root["bracket_width_s"]),
            "R_t4_cm": float(root["R_t4_cm"]),
            "controlling_point": root["controlling_point"],
            "max_abs_step_mass_residual": float(raw["conservation"]["max_abs_step"]),
            "max_abs_robin_residual": float(raw["robin"]["max_abs_flux_residual"]),
            "max_picard_iterations": float(raw["picard"]["max_iterations"]),
            "max_nonlinear_residual": float(raw["picard"]["max_nonlinear_residual"]),
            "runtime_s": float(raw["runtime_s"]),
            "source": path.relative_to(ROOT).as_posix(),
        }
    return dict(sorted(runs.items()))


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    augmented = [row[:] + [value] for row, value in zip(matrix, vector)]
    size = len(vector)
    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1.0e-20:
            raise RuntimeError("singular least-squares normal matrix")
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        scale = augmented[col][col]
        augmented[col] = [value / scale for value in augmented[col]]
        for row in range(size):
            if row == col:
                continue
            factor = augmented[row][col]
            augmented[row] = [a - factor * b for a, b in zip(augmented[row], augmented[col])]
    return [augmented[row][-1] for row in range(size)]


def linear_fit(ns: list[int], ys: list[float], columns: list[list[float]], method: str, p: float | None = None) -> dict[str, Any]:
    design = [[1.0] + [column[i] for column in columns] for i in range(len(ns))]
    width = len(design[0])
    normal = [[sum(row[i] * row[j] for row in design) for j in range(width)] for i in range(width)]
    rhs = [sum(design[k][i] * ys[k] for k in range(len(ns))) for i in range(width)]
    beta = solve_linear_system(normal, rhs)
    predicted = [sum(design[k][i] * beta[i] for i in range(width)) for k in range(len(ns))]
    residuals = [predicted[i] - ys[i] for i in range(len(ns))]
    payload: dict[str, Any] = {
        "n": ns,
        "p": p,
        "t_inf_s": beta[0],
        "t_inf_h": beta[0] / 3600.0,
        "coefficients_scaled_s": beta[1:],
        "predicted_t4_s": predicted,
        "residuals_s": residuals,
        "max_abs_fit_residual_s": max(abs(x) for x in residuals),
        "l2_fit_residual_s": math.sqrt(sum(x * x for x in residuals)),
        "method": method,
    }
    return payload


def free_p_objective(p: float, ns: list[int], ys: list[float]) -> tuple[float, dict[str, Any]]:
    reference = float(max(ns))
    column = [(reference / n) ** p for n in ns]
    fit = linear_fit(ns, ys, [column], "free-p intermediate", p=p)
    return sum(x * x for x in fit["residuals_s"]), fit


def free_p_fit(ns: list[int], ys: list[float]) -> dict[str, Any]:
    # Coarse scan avoids assuming that the objective is unimodal outside the
    # observed asymptotic range; golden search then resolves the best basin.
    grid = [(0.5 + 3.5 * i / 700.0) for i in range(701)]
    best_index = min(range(len(grid)), key=lambda i: free_p_objective(grid[i], ns, ys)[0])
    left = grid[max(0, best_index - 2)]
    right = grid[min(len(grid) - 1, best_index + 2)]
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    c = right - (right - left) / phi
    d = left + (right - left) / phi
    for _ in range(120):
        if free_p_objective(c, ns, ys)[0] < free_p_objective(d, ns, ys)[0]:
            right, d = d, c
            c = right - (right - left) / phi
        else:
            left, c = c, d
            d = left + (right - left) / phi
    p = (left + right) / 2.0
    _, fit = free_p_objective(p, ns, ys)
    fit["method"] = "free-p nonlinear fit: t(n)=t_inf+a*n^(-p)"
    fit["p_search_interval"] = [0.5, 4.0]
    return fit


def fixed_p_fit(ns: list[int], ys: list[float], p: float) -> dict[str, Any]:
    reference = float(max(ns))
    return linear_fit(ns, ys, [[(reference / n) ** p for n in ns]], f"fixed-p={p:g} fit: t(n)=t_inf+a*n^(-{p:g})", p=p)


def p2_p3_fit(ns: list[int]) -> dict[str, Any]:
    reference = float(max(ns))
    return linear_fit(
        ns,
        [RUNS[n]["t4_s"] for n in ns],
        [[(reference / n) ** 2 for n in ns], [(reference / n) ** 3 for n in ns]],
        "fixed p=2 plus n^(-3) correction",
        p=2.0,
    )


def main() -> None:
    global RUNS
    RUNS = load_runs()
    available = sorted(RUNS)
    fits: list[dict[str, Any]] = []
    for ns in ([192, 256, 320, 384, 512], [256, 320, 384, 512]):
        if all(n in RUNS for n in ns):
            fits.append({"family": "A_free_p", "fit": free_p_fit(ns, [RUNS[n]["t4_s"] for n in ns])})
    for count in (3, 4, 5):
        ns = available[-count:]
        if len(ns) == count:
            fits.append({"family": "B_fixed_p2", "fit": fixed_p_fit(ns, [RUNS[n]["t4_s"] for n in ns], 2.0)})
    for count in (4, 5):
        ns = available[-count:]
        if len(ns) == count:
            fits.append({"family": "C_p2_plus_p3", "fit": p2_p3_fit(ns)})

    estimates = [float(item["fit"]["t_inf_h"]) for item in fits]
    ordered = sorted(estimates)
    median = ordered[len(ordered) // 2] if len(ordered) % 2 else (ordered[len(ordered) // 2 - 1] + ordered[len(ordered) // 2]) / 2.0
    envelope = max(estimates) - min(estimates)
    last_grid_h = RUNS[512]["t4_h"]
    max_last_grid_relation = max(abs(last_grid_h - estimate) for estimate in estimates)
    conservative_uncertainty = envelope + max_last_grid_relation
    payload = {
        "experiment": "Q4_FINAL_ASYMPTOTIC_CERTIFICATION",
        "status": "SPATIAL_ASYMPTOTIC_RECORDED_TEMPORAL_VERIFICATION_PENDING",
        "method": "dt=2 s; fresh t=0 spatial runs; non-equidistant direct fits",
        "available_runs": available,
        "runs": RUNS,
        "spatial_continuum_estimates": fits,
        "spatial_estimate": {
            "recommended_method": "median of free-p, fixed-p=2 and p=2+n^-3 reasonable fit estimates",
            "recommended_t_inf_h": median,
            "recommended_t_inf_s": median * 3600.0,
            "method_envelope_h": envelope,
            "last_grid_n512_t4_h": last_grid_h,
            "max_last_grid_to_continuum_relation_h": max_last_grid_relation,
            "conservative_spatial_uncertainty_h": conservative_uncertainty,
            "target_reporting_resolution_h": 0.00005,
        },
        "fit_residual_note": "Free-p fits use 4/5 points; fixed-p=2 and p=2+n^-3 fits report residuals. No three-point zero-residual claim is used as evidence.",
        "next_required": "run n=384, dt=1 s fresh from t=0; do not run n=640",
    }
    output = OUT / "q4_final_asymptotic_spatial_estimates.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "spatial_estimate": payload["spatial_estimate"], "fits": fits}, ensure_ascii=False))


if __name__ == "__main__":
    RUNS: dict[int, dict[str, Any]] = {}
    main()
