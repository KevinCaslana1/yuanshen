"""Run the missing Q4 space/time error-decomposition configurations.

This entry point imports only the standalone numerical reference implemented in
``run_q34_independent_audit.py``.  It intentionally does not import ``src.q4``
and writes only to ``experiments/Q4_CONVERGENCE_FINAL``.  Frozen workbooks,
historical audit records, and production solver outputs are read-only inputs.
"""

from __future__ import annotations

import json
from pathlib import Path

from run_q34_independent_audit import ATT1, ATT2, ROOT, LinearEnvironment, PchipRadius, q4_run


OUT = ROOT / "experiments" / "Q4_CONVERGENCE_FINAL"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    environment = LinearEnvironment(ATT1)
    radius = PchipRadius(ATT2)
    runs = [
        q4_run("B_n96_dt2", radius, n=96, dt=2.0, env=environment),
        q4_run("C_n144_dt4", radius, n=144, dt=4.0, env=environment),
    ]
    payload = {
        "experiment": "Q4_CONVERGENCE_FINAL",
        "status": "COMPLETED",
        "purpose": "separate temporal and spatial effects before selecting minimum necessary refinement",
        "implementation": "standalone FVM/BE/Picard reference imported from run_q34_independent_audit.py; no src/q4 import",
        "initial_condition": "fresh t=0, T=301.15 K, C=2.55 kg/kg, R=2.0 cm",
        "environment_source_sha256": environment.source_sha256,
        "radius_source_sha256": radius.source_sha256,
        "runs": runs,
    }
    (OUT / "new_runs_B_C.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for run in runs:
        event = run["event"]
        print(json.dumps({
            "name": run["name"],
            "n_intervals": run["n_intervals"],
            "dt_s": run["dt_s"],
            "runtime_s": run["runtime_s"],
            "t_cross_linear_s": event["t_cross_linear_s"],
            "t_cross_linear_h": event["t_cross_linear_s"] / 3600.0,
            "critical_radius_after_cm": event["critical_radius_after_cm"],
            "cmax_before": event["before_cmax"],
            "cmax_after": event["after_cmax"],
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
