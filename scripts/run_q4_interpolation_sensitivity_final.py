"""Quantify PCHIP versus linear radius interpolation at the selected Q4 layer."""

from __future__ import annotations

import json
import time
from pathlib import Path

from run_q34_independent_audit import ATT1, ATT2, ROOT, LinearEnvironment, LinearRadius, PchipRadius, THRESHOLD, advance, initial


OUT = ROOT / "experiments" / "Q4_CONVERGENCE_FINAL"


def run_case(radius, name: str, n: int = 192, dt: float = 2.0) -> dict[str, object]:
    env = LinearEnvironment(ATT1)
    state = initial(n)
    started = time.perf_counter()
    max_mass = 0.0
    max_robin = 0.0
    max_picard = 0.0
    coarse = None
    while state.t < 230400.0 - 1e-12:
        previous = state
        state, diag = advance(state, dt, radius, radius.derivative, env, "Q4", n)
        max_mass = max(max_mass, abs(diag["mass_step_residual"]))
        max_robin = max(max_robin, abs(diag["robin_residual"]))
        max_picard = max(max_picard, diag["picard_iterations"])
        if float(max(state.C)) < THRESHOLD <= float(max(previous.C)):
            coarse = (previous, state)
            break
    if coarse is None:
        raise RuntimeError(f"{name} did not cross the Q4 threshold")
    low, high = coarse
    local_dt = dt / 32.0
    local = low
    refined = None
    while local.t < high.t - 1e-12:
        local_next = advance(local, min(local_dt, high.t - local.t), radius, radius.derivative, env, "Q4", n)[0]
        if float(max(local_next.C)) < THRESHOLD <= float(max(local.C)):
            refined = (local, local_next)
            break
        local = local_next
    if refined is None:
        raise RuntimeError(f"{name} local root refinement failed")
    root_low, root_high = refined
    c0, c1 = float(max(root_low.C)), float(max(root_high.C))
    fraction = max(0.0, min(1.0, (c0 - THRESHOLD) / (c0 - c1)))
    t_cross = root_low.t + fraction * (root_high.t - root_low.t)
    return {
        "name": name,
        "n_intervals": n,
        "dt_s": dt,
        "runtime_s": time.perf_counter() - started,
        "coarse_bracket_s": [low.t, high.t],
        "root_bracket_s": [root_low.t, root_high.t],
        "root_bracket_width_s": root_high.t - root_low.t,
        "t4_s": t_cross,
        "t4_h": t_cross / 3600.0,
        "cmax_before": c0,
        "cmax_after": c1,
        "critical_radius_after_cm": float(root_high.C.argmax() * root_high.radius_cm / n),
        "max_abs_step_mass_residual": max_mass,
        "max_abs_robin_residual": max_robin,
        "max_picard_iterations": max_picard,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pchip = json.loads((OUT / "next_refinement_n192_dt2.json").read_text(encoding="utf-8"))
    linear = run_case(LinearRadius(ATT2), "E_linear_n192_dt2")
    pchip_t4_s = float(pchip["root_refinement"]["t_cross_linear_s"])
    result = {
        "experiment": "Q4_INTERPOLATION_SENSITIVITY_FINAL",
        "status": "COMPLETED",
        "configuration": "selected n=192, dt=2 s with 0.0625 s local root refinement",
        "pchip": {
            "t4_s": pchip_t4_s,
            "t4_h": pchip_t4_s / 3600.0,
            "source": "next_refinement_n192_dt2.json",
        },
        "linear": linear,
        "difference_linear_minus_pchip": {
            "delta_s": float(linear["t4_s"]) - pchip_t4_s,
            "absolute_s": abs(float(linear["t4_s"]) - pchip_t4_s),
            "delta_h": (float(linear["t4_s"]) - pchip_t4_s) / 3600.0,
            "absolute_h": abs(float(linear["t4_s"]) - pchip_t4_s) / 3600.0,
        },
        "interpretation": "Retain PCHIP; linear interpolation is a sensitivity comparison, not a replacement or screenshot-fitting target.",
    }
    (OUT / "interpolation_sensitivity_n192_dt2.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
