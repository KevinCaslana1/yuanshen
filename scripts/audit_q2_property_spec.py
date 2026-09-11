"""Read-only audit for the official Q2 Appendix 3 property formulas.

This is a formula/unit audit only. It does not solve Q2 or write any workbook.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "EXP-Q2-PROPERTY-POINTS" / "metrics.json"


def rho(c: float) -> float:
    return 650.0 + 128.0 * c


def cp(c: float) -> float:
    return 1450.0 + 2736.0 * c / (c + 1.0)


def k(c: float) -> float:
    return 0.21 + 0.38 * c / (c + 1.0)


def diffusivity(c: float, t_k: float) -> float:
    if c <= 0.0 or t_k <= 0.0:
        raise ValueError("Appendix 3 D(C,T) requires C>0 and T>0")
    return 2.4e-3 * math.exp(-0.45 / c) * math.exp(-3850.0 / t_k)


def main() -> None:
    points = [
        {"C": 2.55, "T_K": 301.15},
        {"C": 2.55, "T_K": 323.15},
        {"C": 1.0, "T_K": 323.15},
        {"C": 0.5, "T_K": 323.15},
        {"C": 0.2, "T_K": 323.15},
        {"C": 0.15, "T_K": 323.15},
    ]
    values = []
    for point in points:
        c = point["C"]
        t_k = point["T_K"]
        values.append(
            {
                **point,
                "rho_kg_m3": rho(c),
                "cp_J_kgK": cp(c),
                "k_W_mK": k(c),
                "D_m2_s": diffusivity(c, t_k),
            }
        )

    c_grid = [0.15, 0.2, 0.5, 1.0, 2.55]
    t_grid = [301.15, 310.0, 323.15]
    d_c = [diffusivity(c, 323.15) for c in c_grid]
    d_t = [diffusivity(2.55, t) for t in t_grid]
    rejected_celsius_value = diffusivity(2.55, 50.0)
    checks = {
        "finite_positive_at_positive_domain_points": all(
            math.isfinite(v[key]) and v[key] > 0.0
            for v in values
            for key in ("rho_kg_m3", "cp_J_kgK", "k_W_mK", "D_m2_s")
        ),
        "D_monotone_in_C_at_323_15K": all(a < b for a, b in zip(d_c, d_c[1:])),
        "D_monotone_in_T_at_C_2_55": all(a < b for a, b in zip(d_t, d_t[1:])),
        "Celsius_misuse_is_detectably_tiny": rejected_celsius_value < 1e-30,
        "zero_C_guard_is_defined": False,
    }
    try:
        diffusivity(0.0, 323.15)
    except ValueError:
        checks["zero_C_guard_is_defined"] = True

    payload = {
        "experiment": "EXP-Q2-PROPERTY-POINTS",
        "status": "COMPLETED_DESIGN_STAGE_AUDIT",
        "source": "A题/A题.pdf Appendix 3",
        "source_sha256": "052d8014bff5727c019b72e44fdffaf5c145ce04050dd938baaf3527db331736",
        "formula_units": {
            "rho": "kg/m^3",
            "cp": "J/(kg·K)",
            "k": "W/(m·K)",
            "D": "m^2/s",
            "C": "kg/kg",
            "T": "K",
        },
        "values": values,
        "D_at_C_grid_323_15K": d_c,
        "D_at_T_grid_C_2_55": d_t,
        "Celsius_misuse_probe_D_at_50": rejected_celsius_value,
        "checks": checks,
        "formal_Q2_solver_run": False,
        "workbook_written": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
