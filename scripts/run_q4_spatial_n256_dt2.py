"""Run the Q4 n=256, dt=2 s spatial refinement from a fresh t=0 state.

This is an isolated convergence run.  It deliberately uses the standalone
independent audit implementation rather than src/q4 and never resumes from a
checkpoint or an earlier field.  The crossing step is locally refined only to
separate root-location resolution from the spatial field error.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from run_q34_independent_audit import ATT1, ATT2, ROOT, LinearEnvironment, PchipRadius, THRESHOLD, advance, initial


OUT = ROOT / "experiments" / "Q4_SPATIAL_CONVERGENCE_FINAL"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    env = LinearEnvironment(ATT1)
    radius = PchipRadius(ATT2)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 256
    label = {256: "F", 320: "G", 384: "H"}.get(n, f"n{n}")
    dt = 2.0
    horizon = 230400.0
    state = initial(n)
    started = time.perf_counter()
    max_mass = 0.0
    cumulative_mass = 0.0
    max_robin = 0.0
    max_picard = 0.0
    max_nonlinear = 0.0
    steps = 0
    coarse_bracket = None

    while state.t < horizon - 1e-12:
        previous = state
        state, diag = advance(state, min(dt, horizon - state.t), radius, radius.derivative, env, "Q4", n)
        steps += 1
        max_mass = max(max_mass, abs(diag["mass_step_residual"]))
        cumulative_mass += abs(diag["mass_step_residual"])
        max_robin = max(max_robin, abs(diag["robin_residual"]))
        max_picard = max(max_picard, diag["picard_iterations"])
        max_nonlinear = max(max_nonlinear, diag["nonlinear_residual"])
        if float(max(state.C)) < THRESHOLD <= float(max(previous.C)):
            coarse_bracket = (previous, state)
            break

    if coarse_bracket is None:
        raise RuntimeError("n=256, dt=2 s did not cross the Q4 threshold")

    low, high = coarse_bracket
    root_dt = dt / 32.0
    root_prev = low
    refined = None
    root_steps = 0
    while root_prev.t < high.t - 1e-12:
        root_next = advance(root_prev, min(root_dt, high.t - root_prev.t), radius, radius.derivative, env, "Q4", n)[0]
        root_steps += 1
        if float(max(root_next.C)) < THRESHOLD <= float(max(root_prev.C)):
            refined = (root_prev, root_next)
            break
        root_prev = root_next

    if refined is None:
        raise RuntimeError("local root refinement did not bracket the Q4 threshold")

    root_low, root_high = refined
    c0, c1 = float(max(root_low.C)), float(max(root_high.C))
    fraction = (c0 - THRESHOLD) / (c0 - c1)
    t_cross = root_low.t + max(0.0, min(1.0, fraction)) * (root_high.t - root_low.t)
    elapsed = time.perf_counter() - started
    result = {
        "name": f"{label}_n{n}_dt2",
        "n_intervals": n,
        "dt_s": dt,
        "horizon_s": horizon,
        "initial_state": "fresh t=0; no checkpoint or E-state reuse",
        "runtime_s": elapsed,
        "full_steps_to_event": steps,
        "coarse_bracket_s": [low.t, high.t],
        "root_refinement": {
            "substeps": root_steps,
            "substep_dt_s": root_dt,
            "bracket_s": [root_low.t, root_high.t],
            "bracket_width_s": root_high.t - root_low.t,
            "t_cross_linear_s": t_cross,
            "t_cross_linear_h": t_cross / 3600.0,
            "R_t4_cm": float(radius(t_cross)),
            "R_t4_rate_cm_s": float(radius.derivative(t_cross)),
            "cmax_before": c0,
            "cmax_after": c1,
            "critical_radius_after_cm": float(root_high.C.argmax() * root_high.radius_cm / n),
            "controlling_point": "center / xi=0" if root_high.C.argmax() == 0 else "not center",
        },
        "conservation": {
            "max_abs_step": max_mass,
            "cumulative_abs_step": cumulative_mass,
            "definition": "moving-volume balance with Robin loss and prescribed boundary motion",
        },
        "robin": {"max_abs_flux_residual": max_robin},
        "picard": {"max_iterations": max_picard, "max_nonlinear_residual": max_nonlinear},
        "sources": {"environment_sha256": env.source_sha256, "radius_sha256": radius.source_sha256},
        "status": "COMPLETED",
    }
    output = OUT / f"spatial_run_{label}_n{n}_dt2.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
