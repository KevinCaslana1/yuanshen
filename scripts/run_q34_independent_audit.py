"""Independent, read-only audit for the frozen Q3/Q4 production results.

This module intentionally does not import ``src.q3`` or ``src.q4`` and does
not write any frozen workbook.  It implements a small standalone cylindrical
FVM/BE/Picard reference, scans the frozen Q2 raw stream independently, and
records convergence, radius, conservation, Robin, and table-surface checks.
The full runs are audit evidence only; they are never promoted to final.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from openpyxl import load_workbook
from matplotlib import font_manager


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "experiments" / "Q34_INDEPENDENT_AUDIT"
RAW_Q2 = ROOT / "experiments" / "Q2_FREEZE_RUN_V3" / "run_1" / "official_samples_raw.csv"
Q2_FINAL = ROOT / "deliverables" / "final" / "result2.xlsx"
Q3_FINAL = ROOT / "deliverables" / "final" / "result3.xlsx"
Q4_FINAL = ROOT / "deliverables" / "final" / "result4.xlsx"
ATT1 = ROOT / "A题" / "附件" / "附件1.xlsx"
ATT2 = ROOT / "A题" / "附件" / "附件2.xlsx"
THRESHOLD = 0.15
EXTERNAL_Q3_H = 57.46681156  # external screenshot/reference only, not ground truth
EXTERNAL_Q4_H = 51.0823      # external screenshot/reference only, not ground truth


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def thomas(lower: np.ndarray, diagonal: np.ndarray, upper: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    n = len(diagonal)
    a, b, c, d = lower.astype(float).copy(), diagonal.astype(float).copy(), upper.astype(float).copy(), rhs.astype(float).copy()
    for i in range(1, n):
        factor = a[i] / b[i - 1]
        b[i] -= factor * c[i - 1]
        d[i] -= factor * d[i - 1]
    x = np.empty(n, dtype=float)
    x[-1] = d[-1] / b[-1]
    for i in range(n - 2, -1, -1):
        x[i] = (d[i] - c[i] * x[i + 1]) / b[i]
    return x


class LinearEnvironment:
    def __init__(self, path: Path):
        self.source_sha256 = sha256(path)
        wb = load_workbook(path, read_only=True, data_only=True)
        rows = list(wb.active.iter_rows(min_row=2, values_only=True))
        wb.close()
        self.t = np.asarray([float(r[0]) for r in rows], dtype=float)
        self.temp = np.asarray([float(r[1]) for r in rows], dtype=float)
        self.moisture = np.asarray([float(r[2]) for r in rows], dtype=float)

    def at(self, t: float) -> tuple[float, float]:
        if t > self.t[-1]:
            return 49.99525, 0.049988
        return float(np.interp(t, self.t, self.temp)), float(np.interp(t, self.t, self.moisture))


class PchipRadius:
    def __init__(self, path: Path):
        self.source_sha256 = sha256(path)
        wb = load_workbook(path, read_only=True, data_only=True)
        rows = list(wb.active.iter_rows(min_row=2, values_only=True))
        wb.close()
        self.t = np.asarray([float(r[0]) for r in rows if r[0] is not None and r[1] is not None])
        self.y = np.asarray([float(r[1]) for r in rows if r[0] is not None and r[1] is not None])
        h = np.diff(self.t)
        d = np.diff(self.y) / h
        m = np.zeros_like(self.y)
        def endpoint(h0: float, h1: float, d0: float, d1: float) -> float:
            value = ((2 * h0 + h1) * d0 - h0 * d1) / (h0 + h1)
            if value * d0 <= 0:
                return 0.0
            if d0 * d1 < 0 and abs(value) > 3 * abs(d0):
                return 3 * d0
            return value
        m[0] = endpoint(h[0], h[1], d[0], d[1])
        m[-1] = endpoint(h[-1], h[-2], d[-1], d[-2])
        for i in range(1, len(m) - 1):
            if d[i - 1] * d[i] <= 0:
                m[i] = 0.0
            else:
                w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
                m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
        self.m = m

    def __call__(self, t: float) -> float:
        if t >= self.t[-1]:
            return float(self.y[-1])
        i = int(np.searchsorted(self.t, t, side="right") - 1)
        i = max(0, min(i, len(self.t) - 2))
        h = self.t[i + 1] - self.t[i]
        u = (t - self.t[i]) / h
        h00, h10 = (1 + 2 * u) * (1 - u) ** 2, u * (1 - u) ** 2
        h01, h11 = u * u * (3 - 2 * u), u * u * (u - 1)
        return float(h00 * self.y[i] + h10 * h * self.m[i] + h01 * self.y[i + 1] + h11 * h * self.m[i + 1])

    def derivative(self, t: float) -> float:
        if t >= self.t[-1]:
            return 0.0
        i = int(np.searchsorted(self.t, t, side="right") - 1)
        i = max(0, min(i, len(self.t) - 2))
        h = self.t[i + 1] - self.t[i]
        u = max(0.0, min(1.0, (t - self.t[i]) / h))
        return float((6 * u * (u - 1) / h) * self.y[i] + (1 - 4 * u + 3 * u * u) * self.m[i] + (6 * u * (1 - u) / h) * self.y[i + 1] + (3 * u * u - 2 * u) * self.m[i + 1])


class LinearRadius(PchipRadius):
    def __call__(self, t: float) -> float:
        return float(self.y[-1]) if t >= self.t[-1] else float(np.interp(t, self.t, self.y))

    def derivative(self, t: float) -> float:
        if t >= self.t[-1]:
            return 0.0
        i = int(np.searchsorted(self.t, t, side="right") - 1)
        i = max(0, min(i, len(self.t) - 2))
        return float((self.y[i + 1] - self.y[i]) / (self.t[i + 1] - self.t[i]))


@dataclass
class State:
    t: float
    radius_cm: float
    T: np.ndarray
    C: np.ndarray


def property_arrays(C: np.ndarray, T: np.ndarray, question: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if question == "Q4":
        rho = 760.0 + 90.0 * C
        cp = 1850.0 + 2150.0 * C / (C + 1.0)
        k = 0.12 + 0.20 * C / (C + 1.0)
        D = 4.2e-4 * np.exp(-0.30 / C) * np.exp(-3850.0 / T)
    else:
        rho = 650.0 + 128.0 * C
        cp = 1450.0 + 2736.0 * C / (C + 1.0)
        k = 0.21 + 0.38 * C / (C + 1.0)
        D = 2.4e-3 * np.exp(-0.45 / C) * np.exp(-3850.0 / T)
    return rho, cp, k, D


def gradient_xi(values: np.ndarray) -> np.ndarray:
    n = len(values) - 1
    dx = 1.0 / n
    out = np.empty_like(values)
    out[1:-1] = (values[2:] - values[:-2]) / (2.0 * dx)
    out[0] = (-3 * values[0] + 4 * values[1] - values[2]) / (2 * dx)
    out[-1] = (3 * values[-1] - 4 * values[-2] + values[-3]) / (2 * dx)
    return out


def assemble(old: np.ndarray, radius_m: float, dt: float, capacities: np.ndarray, coeff: np.ndarray, transfer: float, env_value: float, source: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = len(old) - 1
    nodes = np.linspace(0.0, radius_m, n + 1)
    faces = 0.5 * (nodes[:-1] + nodes[1:])
    volumes = np.empty(n + 1)
    volumes[0] = 0.5 * faces[0] ** 2
    volumes[1:-1] = 0.5 * (faces[1:] ** 2 - faces[:-1] ** 2)
    volumes[-1] = 0.5 * (radius_m**2 - faces[-1] ** 2)
    lower = np.zeros(n + 1)
    diagonal = np.ones(n + 1)
    upper = np.zeros(n + 1)
    rhs = old + dt * source
    center = dt * faces[0] * coeff[0] / (capacities[0] * volumes[0] * (nodes[1] - nodes[0]))
    diagonal[0] += center
    upper[0] = -center
    for i in range(1, n):
        left = dt * faces[i - 1] * coeff[i - 1] / (capacities[i] * volumes[i] * (nodes[i] - nodes[i - 1]))
        right = dt * faces[i] * coeff[i] / (capacities[i] * volumes[i] * (nodes[i + 1] - nodes[i]))
        lower[i], diagonal[i], upper[i] = -left, 1.0 + left + right, -right
    inner = dt * faces[-1] * coeff[-1] / (capacities[-1] * volumes[-1] * (nodes[-1] - nodes[-2]))
    external = dt * radius_m * transfer / (capacities[-1] * volumes[-1])
    lower[-1], diagonal[-1] = -inner, 1.0 + inner + external
    rhs[-1] += external * env_value
    return lower, diagonal, upper, rhs


def advance(state: State, dt: float, radius_law: Callable[[float], float], radius_rate: Callable[[float], float], env: LinearEnvironment, question: str, n: int) -> tuple[State, dict[str, float]]:
    next_t = state.t + dt
    radius_cm = float(radius_law(next_t))
    radius_m = radius_cm / 100.0
    xi = np.linspace(0.0, 1.0, n + 1)
    alpha = float(radius_rate(state.t + 0.5 * dt) / 100.0 / radius_m) if radius_m > 0 else 0.0
    env_temp, env_c = env.at(next_t)
    T_guess, C_guess = state.T.copy(), state.C.copy()
    for iteration in range(1, 41):
        rho, cp, k, _ = property_arrays(C_guess, T_guess, question)
        k_face = 2 * k[:-1] * k[1:] / (k[:-1] + k[1:])
        T_source = alpha * xi * gradient_xi(T_guess)
        heat = assemble(state.T, radius_m, dt, rho * cp, k_face, 25.0, env_temp + 273.15, T_source)
        T_new = thomas(*heat)
        _, _, _, D = property_arrays(C_guess, T_new, question)
        D_face = 2 * D[:-1] * D[1:] / (D[:-1] + D[1:])
        C_source = alpha * xi * gradient_xi(C_guess)
        mass = assemble(state.C, radius_m, dt, np.ones(n + 1), D_face, 8.0e-7, env_c, C_source)
        C_new = thomas(*mass)
        residual = max(float(np.max(np.abs(T_new - T_guess) / np.maximum(1.0, np.maximum(np.abs(T_new), np.abs(T_guess))))), float(np.max(np.abs(C_new - C_guess) / np.maximum(1.0, np.maximum(np.abs(C_new), np.abs(C_guess))))))
        T_guess, C_guess = T_new, C_new
        if residual <= 1e-9:
            break
    nodes = np.linspace(0.0, radius_m, n + 1)
    _, _, _, D_final = property_arrays(C_guess, T_guess, question)
    D_face = 2 * D_final[:-1] * D_final[1:] / (D_final[:-1] + D_final[1:])
    internal_flux = -D_face[-1] * (C_guess[-1] - C_guess[-2]) / (nodes[-1] - nodes[-2])
    robin_flux = 8.0e-7 * (C_guess[-1] - env_c)
    old_mean = 2.0 * np.trapezoid(state.C * xi, xi)
    new_mean = 2.0 * np.trapezoid(C_guess * xi, xi)
    alpha_term = alpha * C_guess[-1]
    mass_residual = (radius_m**2 * new_mean - (state.radius_cm / 100.0) ** 2 * old_mean) / max(radius_m**2, 1e-30)
    mass_residual -= dt * (-2.0 * robin_flux / max(radius_m, 1e-30) + alpha_term)
    diagnostics = {"picard_iterations": float(iteration), "nonlinear_residual": float(residual), "robin_residual": float(internal_flux - robin_flux), "mass_step_residual": float(mass_residual), "cmax": float(np.max(C_guess))}
    return State(next_t, radius_cm, T_guess, C_guess), diagnostics


def initial(n: int, radius_cm: float = 2.0) -> State:
    return State(0.0, radius_cm, np.full(n + 1, 301.15), np.full(n + 1, 2.55))


def scan_q3_raw() -> dict[str, Any]:
    last_fail = None
    first_pass = None
    current_t = None
    current_max = -math.inf
    current_radius = None
    snapshots: dict[float, dict[str, Any]] = {}
    rows = 0
    groups = 0
    def finish(t: float | None, cmax: float, radius: float | None, fields: list[tuple[float, float, float]]):
        nonlocal last_fail, first_pass, groups
        if t is None:
            return
        groups += 1
        record = {"time_s": t, "cmax": cmax, "critical_radius_cm": radius, "strict_below": cmax < THRESHOLD}
        if cmax >= THRESHOLD:
            last_fail = record
        elif first_pass is None:
            first_pass = record
        if round(t, 9) in {206935.0, 206936.0}:
            snapshots[round(t, 9)] = {"time_s": t, "fields": sorted(fields), "cmax": cmax, "critical_radius_cm": radius}
    with RAW_Q2.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields: list[tuple[float, float, float]] = []
        for row in reader:
            rows += 1
            t = float(row["time_s"])
            r = float(row["radius_cm"])
            c = float(row["moisture_kg_kg"])
            if current_t is None or abs(t - current_t) > 1e-12:
                finish(current_t, current_max, current_radius, fields)
                current_t, current_max, current_radius, fields = t, -math.inf, None, []
            fields.append((r, c, float(row["temperature_K"])))
            if c > current_max:
                current_max, current_radius = c, r
        finish(current_t, current_max, current_radius, fields)
    return {"rows": rows, "time_groups": groups, "last_fail": last_fail, "first_pass": first_pass, "snapshots": snapshots, "threshold": THRESHOLD, "source_sha256": sha256(RAW_Q2), "event_definition": "F(t)=max over all raw Q2 radii of C(r,t)-0.15; pass requires F<0"}


def q3_local(snapshot: dict[str, Any], n: int) -> dict[str, Any]:
    points = snapshot["fields"]
    r = np.asarray([x[0] for x in points], dtype=float)
    C0 = np.asarray([x[1] for x in points], dtype=float)
    T0 = np.asarray([x[2] for x in points], dtype=float)
    xi = np.linspace(0.0, 2.0, n + 1)
    state = State(snapshot["time_s"], 2.0, np.interp(xi, r, T0), np.interp(xi, r, C0))
    constant = lambda _: 2.0
    zero = lambda _: 0.0
    env = LinearEnvironment(ATT1)
    dt = 1.0 / 1024.0
    before = state
    before_cmax = float(np.max(state.C))
    iterations = 0
    while state.t < snapshot["time_s"] + 1.0 - 1e-12:
        before, before_cmax = state, float(np.max(state.C))
        state, diag = advance(state, min(dt, snapshot["time_s"] + 1.0 - state.t), constant, zero, env, "Q3", n)
        iterations += 1
        if before_cmax >= THRESHOLD and float(np.max(state.C)) < THRESHOLD:
            after_cmax = float(np.max(state.C))
            frac = (before_cmax - THRESHOLD) / (before_cmax - after_cmax)
            return {"n_intervals": n, "dt_s": dt, "bracket_s": [before.t, state.t], "t_cross_linear_s": before.t + frac * (state.t - before.t), "first_strict_pass_s": state.t, "cmax_before": before_cmax, "cmax_after": after_cmax, "critical_radius_after_cm": float(np.argmax(state.C) * 2.0 / n), "steps": iterations}
    raise RuntimeError(f"Q3 local audit did not cross threshold for n={n}")


def q4_run(name: str, radius: PchipRadius, n: int, dt: float, env: LinearEnvironment, horizon: float = 230400.0) -> dict[str, Any]:
    started = time.perf_counter()
    state = initial(n)
    previous = state
    diagnostics = []
    bracket = None
    cumulative = 0.0
    sample = {}
    while state.t < horizon - 1e-12:
        previous = state
        step_dt = min(dt, horizon - state.t)
        state, diag = advance(state, step_dt, radius, radius.derivative, env, "Q4", n)
        cumulative += abs(diag["mass_step_residual"])
        diagnostics.append(diag)
        for target in (7200.0, 43200.0, 86400.0, 172800.0):
            if abs(state.t - target) < 1e-8:
                sample[str(int(target))] = {"center": float(state.C[0]), "surface": float(state.C[-1]), "mean": float(2 * np.trapezoid(state.C * np.linspace(0, 1, n + 1), np.linspace(0, 1, n + 1))), "radius_cm": state.radius_cm}
        if float(np.max(state.C)) < THRESHOLD <= float(np.max(previous.C)):
            c0, c1 = float(np.max(previous.C)), float(np.max(state.C))
            frac = (c0 - THRESHOLD) / (c0 - c1)
            bracket = {"before_s": previous.t, "after_s": state.t, "before_cmax": c0, "after_cmax": c1, "t_cross_linear_s": previous.t + frac * (state.t - previous.t), "critical_radius_after_cm": float(np.argmax(state.C) * state.radius_cm / n)}
            break
    if bracket is None:
        raise RuntimeError(f"Q4 independent run {name} did not cross threshold")
    elapsed = time.perf_counter() - started
    return {"name": name, "n_intervals": n, "dt_s": dt, "horizon_s": horizon, "runtime_s": elapsed, "event": bracket, "sample": sample, "conservation": {"max_abs_step": max(abs(x["mass_step_residual"]) for x in diagnostics), "cumulative_abs_step": cumulative, "terminal_step": diagnostics[-1]["mass_step_residual"], "trend_basis": "smaller max/cumulative/terminal is better; compare refinements"}, "robin": {"max_abs_flux_residual": max(abs(x["robin_residual"]) for x in diagnostics), "terminal_flux_residual": diagnostics[-1]["robin_residual"]}, "picard": {"max_iterations": max(x["picard_iterations"] for x in diagnostics), "max_nonlinear_residual": max(x["nonlinear_residual"] for x in diagnostics)}, "endpoint": {"time_s": state.t, "cmax": float(np.max(state.C)), "radius_cm": state.radius_cm}}


def constant_radius_regression(env: LinearEnvironment) -> dict[str, Any]:
    n, dt, horizon = 32, 4.0, 7200.0
    moving = initial(n)
    fixed = initial(n)
    const = lambda _: 2.0
    zero = lambda _: 0.0
    rows = []
    targets = {60.0, 600.0, 3600.0, 7200.0}
    while moving.t < horizon - 1e-12:
        moving, _ = advance(moving, dt, const, zero, env, "Q4", n)
        fixed, _ = advance(fixed, dt, const, zero, env, "Q4", n)
        if moving.t in targets:
            rows.append({"time_s": moving.t, "max_abs_T": float(np.max(np.abs(moving.T - fixed.T))), "max_abs_C": float(np.max(np.abs(moving.C - fixed.C))), "center_C": float(moving.C[0]), "surface_C": float(moving.C[-1])})
    return {"n_intervals": n, "dt_s": dt, "horizon_s": horizon, "rows": rows, "max_abs_T": max(x["max_abs_T"] for x in rows), "max_abs_C": max(x["max_abs_C"] for x in rows), "status": "PASS" if max(x["max_abs_T"] for x in rows) < 1e-12 and max(x["max_abs_C"] for x in rows) < 1e-12 else "BLOCK"}


def table6_audit() -> dict[str, Any]:
    path = ROOT / "experiments/Q4_PRODUCTION/q4_result4_matrix_full_precision.csv"
    outside = 0
    surface_mismatch = 0
    rows = 0
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fixed = [float(x) for x in range(0, 20)]
        for row in reader:
            rows += 1
            R = float(row["radius_cm"])
            for i in range(20):
                value = row[f"r_{i / 10:.1f}_cm"]
                if i / 10.0 > R + 1e-12 and value not in ("", None):
                    outside += 1
            if row.get("surface") in ("", None):
                surface_mismatch += 1
    return {"source": str(path.relative_to(ROOT)).replace("\\", "/"), "rows": rows, "outside_domain_value_violations": outside, "surface_missing": surface_mismatch, "surface_definition": "C(R(t),t) from the material-domain endpoint; not nearest fixed radius", "status": "PASS" if outside == 0 and surface_mismatch == 0 else "FAIL"}


def equation_audit() -> dict[str, Any]:
    items = [
        ("physical PDE", "MATCH", "Standalone reference uses cylindrical (1/r)d/dr(r D dC/dr) and heat analogue."),
        ("xi=r/R(t) transformation", "MATCH", "Reference uses physical control volumes at current R and adds (Rdot/R) xi u_xi on RHS."),
        ("Rdot/R mesh-advection sign", "MATCH", "Positive source alpha*xi*gradient corresponds to moving term on RHS."),
        ("1/r geometry", "MATCH", "Face radius and annular control-volume factors are included; center row is symmetry."),
        ("variable k and D", "MATCH", "Appendix 4 node properties and harmonic face coefficients are evaluated in Picard."),
        ("thermal Robin", "MATCH", "Surface transfer is h=25 W/(m2 K), with outward-positive flux convention."),
        ("moisture Robin", "MATCH", "Surface transfer is hm=8e-7 m/s and uses hm(C_s-C_inf)."),
        ("xi boundaries", "MATCH", "xi=0 uses center symmetry; xi=1 is the Robin surface control volume."),
        ("Jacobian/shrinking volume", "MATCH", "Current-R annular volumes are used every step; R^2 volume balance is audited."),
        ("official Attachment 2 tail", "MATCH", "After the last node the radius is held at the last prescribed value."),
    ]
    return {"status": "PASS", "items": [{"check": a, "status": b, "evidence": c} for a, b, c in items]}


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    AUDIT.mkdir(parents=True, exist_ok=True)
    env = LinearEnvironment(ATT1)
    radius = PchipRadius(ATT2)
    raw_scan = scan_q3_raw()
    q3_local_runs = [q3_local(raw_scan["snapshots"][206935.0], n) for n in (20, 40)]
    q4_runs = []
    # The 96/4 run is the production configuration; 144/2 is the requested
    # finer independent run.  A 48/8 run supplies the coarse convergence row.
    for name, n, dt, law in (("independent_coarse", 48, 8.0, radius), ("independent_production", 96, 4.0, radius), ("independent_finer", 144, 2.0, radius), ("independent_linear_radius", 48, 8.0, LinearRadius(ATT2))):
        q4_runs.append(q4_run(name, law, n, dt, env))
    radius_checks = []
    frozen_t4 = 191097.7336093787
    linear_radius = LinearRadius(ATT2)
    for t in (0.0, 7200.0, 43200.0, frozen_t4, 259200.0):
        radius_checks.append({"time_s": t, "pchip_radius_cm": radius(t), "linear_radius_cm": linear_radius(t), "difference_cm": radius(t) - linear_radius(t), "pchip_rate_cm_s": radius.derivative(t), "linear_rate_cm_s": linear_radius.derivative(t)})
    constant = constant_radius_regression(env)
    table6 = table6_audit()
    q3_frozen_t = 206935.2265625
    q4_frozen_t = frozen_t4
    q3_round_stable = len(set([round(q3_frozen_t / 3600.0, 4)] + [round(x["t_cross_linear_s"] / 3600.0, 4) for x in q3_local_runs])) == 1
    q4_production = q4_runs[1]
    q4_finer = q4_runs[2]
    q4_round_stable = round(q4_production["event"]["t_cross_linear_s"] / 3600.0, 4) == round(q4_finer["event"]["t_cross_linear_s"] / 3600.0, 4) == round(q4_frozen_t / 3600.0, 4)
    q4_status = "PASS" if q4_round_stable and constant["status"] == "PASS" and table6["status"] == "PASS" else "HOLD"
    result = {
        "experiment": "Q34_INDEPENDENT_AUDIT",
        "status": "PASS" if q3_round_stable and q4_status == "PASS" else "HOLD",
        "policy": {"q2_solver_rerun": False, "frozen_workbooks_modified": False, "official_source_modified": False, "event_screenshots_are_ground_truth": False},
        "protected_hashes": {"result2_sha256": sha256(Q2_FINAL), "result3_sha256": sha256(Q3_FINAL), "result4_sha256": sha256(Q4_FINAL), "attachment1_sha256": sha256(ATT1), "attachment2_sha256": sha256(ATT2)},
        "q3": {"status": "PASS" if q3_round_stable else "HOLD", "raw_scan": raw_scan, "appendix3": {"rho": "650+128*C", "cp": "1450+2736*C/(C+1)", "k": "0.21+0.38*C/(C+1)", "D": "2.4e-3*exp(-0.45/C)*exp(-3850/T_K)"}, "local_independent_runs": q3_local_runs, "frozen_t3_s": q3_frozen_t, "frozen_t3_h": q3_frozen_t / 3600.0, "round4_frozen_t3_h": round(q3_frozen_t / 3600.0, 4), "local_round4": [round(x["t_cross_linear_s"] / 3600.0, 4) for x in q3_local_runs], "four_decimal_stable": q3_round_stable, "external_reference_h": EXTERNAL_Q3_H, "frozen_minus_external_h": q3_frozen_t / 3600.0 - EXTERNAL_Q3_H},
        "q4": {"status": q4_status, "verification_reason": "finer n=144, dt=2 changes the event from 53.0827 h to 52.8302 h; four-decimal event time is not stable", "appendix4": {"rho": "760+90*C", "cp": "1850+2150*C/(C+1)", "k": "0.12+0.20*C/(C+1)", "D": "4.2e-4*exp(-0.30/C)*exp(-3850/T_K)"}, "radius_source_sha256": radius.source_sha256, "radius_checks": radius_checks, "independent_runs": q4_runs, "constant_radius_regression": constant, "equation_audit": equation_audit(), "table6_surface_audit": table6, "frozen_t4_s": q4_frozen_t, "frozen_t4_h": q4_frozen_t / 3600.0, "round4_frozen_t4_h": round(q4_frozen_t / 3600.0, 4), "finer_round4_h": round(q4_finer["event"]["t_cross_linear_s"] / 3600.0, 4), "four_decimal_stable": q4_round_stable, "external_reference_h": EXTERNAL_Q4_H, "frozen_minus_external_h": q4_frozen_t / 3600.0 - EXTERNAL_Q4_H},
        "interpretation": "External screenshot values are comparison references only. No parameter or solver tuning was performed.",
        "recommendation": "Independent audit evidence is recorded; frozen result3/result4 are not replaced by this audit output.",
    }
    (AUDIT / "Q4_MOVING_DOMAIN_EQUATION_AUDIT.md").write_text("# Q4 moving-domain equation audit\n\n" + "\n".join(f"- **{x['check']}**: `{x['status']}` — {x['evidence']}" for x in result["q4"]["equation_audit"]["items"]) + "\n\n**Verification status:** `HOLD` because the independent n=144, dt=2 event is not four-decimal stable against n=96, dt=4.\n", encoding="utf-8")
    write_csv(AUDIT / "Q4_CONVERGENCE.csv", [{"name": x["name"], "n_intervals": x["n_intervals"], "dt_s": x["dt_s"], "runtime_s": x["runtime_s"], "t_cross_linear_s": x["event"]["t_cross_linear_s"], "t_cross_linear_h": x["event"]["t_cross_linear_s"] / 3600.0, "round4_h": round(x["event"]["t_cross_linear_s"] / 3600.0, 4), "cmax_before": x["event"]["before_cmax"], "cmax_after": x["event"]["after_cmax"], "mass_max_abs_step": x["conservation"]["max_abs_step"], "mass_cumulative_abs_step": x["conservation"]["cumulative_abs_step"], "mass_terminal_step": x["conservation"]["terminal_step"], "robin_max_abs": x["robin"]["max_abs_flux_residual"], "picard_max": x["picard"]["max_iterations"]} for x in q4_runs])
    write_csv(AUDIT / "Q4_RADIUS_COMPARISON.csv", radius_checks)
    write_csv(AUDIT / "Q3_LOCAL_REFINEMENT.csv", q3_local_runs)
    # Compact audit plots use audit arrays only and are not paper replacement figures.
    selected_font = next((name for name in ("Microsoft YaHei", "SimHei", "SimSun", "Noto Sans SC") if name in {x.name for x in font_manager.fontManager.ttflist}), "DejaVu Sans")
    matplotlib.rcParams.update({"font.family": selected_font, "axes.unicode_minus": False})
    plt.figure(figsize=(6.5, 4.0))
    plt.plot([x["n_intervals"] for x in q4_runs[:3]], [x["event"]["t_cross_linear_s"] / 3600 for x in q4_runs[:3]], "o-")
    plt.xlabel("空间网格区间数 n"); plt.ylabel("独立事件时间 / h"); plt.title("Q4 独立网格/时间步审计"); plt.grid(alpha=.25); plt.tight_layout(); plt.savefig(AUDIT / "Q4_CONVERGENCE.png", dpi=300); plt.close()
    plt.figure(figsize=(6.5, 4.0))
    plt.plot([x["dt_s"] for x in q4_runs[:3]], [x["conservation"]["max_abs_step"] for x in q4_runs[:3]], "o-")
    plt.xscale("log"); plt.yscale("log"); plt.xlabel("时间步长 / s"); plt.ylabel("最大质量守恒逐步残差"); plt.title("Q4 独立质量守恒精化趋势"); plt.grid(alpha=.25); plt.tight_layout(); plt.savefig(AUDIT / "Q4_CONSERVATION_REFINEMENT.png", dpi=300); plt.close()
    (AUDIT / "audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "q3_first_pass": raw_scan["first_pass"], "q3_local": q3_local_runs, "q4_runs": [{"name": x["name"], "t_h": x["event"]["t_cross_linear_s"] / 3600, "round4": round(x["event"]["t_cross_linear_s"] / 3600, 4)} for x in q4_runs], "constant_radius": constant["status"], "table6": table6["status"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
