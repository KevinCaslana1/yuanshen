"""Prescribed-shrinkage Q4 material-coordinate BE/Picard solver."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import numpy as np

from src.common.numerics import make_radial_grid
from src.q2.environment import EnvironmentProvider
from src.q2.model import assemble_variable_radial_system, boundary_flux_pair, interface_values, solve_system, tridiagonal_residual_linf
from src.q4.properties import cp_array, conductivity_array, density_array, diffusivity_array
from src.q4.radius import RadiusLaw


@dataclass
class Q4State:
    time_s: float
    radius_cm: float
    temperature_k: List[float]
    moisture: List[float]
    picard_iterations: int = 0
    nonlinear_residual: float = 0.0
    linear_residual: float = 0.0
    radius_rate_cm_s: float = 0.0
    mass_step_residual: float = 0.0
    robin_residual: float = 0.0

    @property
    def cmax(self) -> float:
        return max(self.moisture)

    @property
    def critical_xi(self) -> float:
        return float(np.argmax(np.asarray(self.moisture))) / float(len(self.moisture) - 1)

    @property
    def mean_moisture(self) -> float:
        xi = np.linspace(0.0, 1.0, len(self.moisture))
        return float(2.0 * np.trapezoid(np.asarray(self.moisture) * xi, xi))


def _gradient(values: Sequence[float], xi: np.ndarray) -> np.ndarray:
    return np.gradient(np.asarray(values, dtype=float), xi, edge_order=2)


def advance_q4(
    state: Q4State,
    dt_s: float,
    *,
    radius_law: RadiusLaw,
    environment: EnvironmentProvider,
    n_intervals: int,
    picard_tolerance: float = 1e-9,
    picard_max_iterations: int = 40,
) -> Q4State:
    """Advance one BE/Picard step on a fixed material-coordinate lattice."""

    if dt_s <= 0.0:
        raise ValueError("dt_s must be positive")
    next_time = state.time_s + dt_s
    radius_cm = radius_law.radius_cm(next_time)
    radius_m = radius_cm / 100.0
    old_T = list(state.temperature_k)
    old_C = list(state.moisture)
    grid = make_radial_grid(radius_m, n_intervals)
    xi = np.linspace(0.0, 1.0, n_intervals + 1)
    midpoint = state.time_s + 0.5 * dt_s
    rate_m_s = radius_law.radius_rate_cm_s(midpoint) / 100.0
    alpha = 0.0 if radius_m <= 0.0 else rate_m_s / radius_m
    env_temp_c, env_moisture = environment.at(next_time)
    T_guess, C_guess = list(old_T), list(old_C)
    last_heat_system = last_moisture_system = None
    final_picard_residual = float("inf")
    for iteration in range(1, picard_max_iterations + 1):
        grad_T = _gradient(T_guess, xi)
        grad_C = _gradient(C_guess, xi)
        T_source = (alpha * xi * grad_T).tolist()
        C_source = (alpha * xi * grad_C).tolist()
        rho = density_array(C_guess)
        heat_capacity = [a * b for a, b in zip(rho, cp_array(C_guess))]
        k_faces = interface_values(conductivity_array(C_guess), "harmonic")
        heat_system = assemble_variable_radial_system(old_T, grid, dt_s, heat_capacity, k_faces, 25.0, env_temp_c + 273.15, scheme="be", source_values=T_source)
        T_new = solve_system(heat_system)
        d_faces = interface_values(diffusivity_array(C_guess, T_new), "harmonic")
        moisture_system = assemble_variable_radial_system(old_C, grid, dt_s, [1.0] * len(old_C), d_faces, 8.0e-7, env_moisture, scheme="be", source_values=C_source)
        C_new = solve_system(moisture_system)
        if min(C_new) <= 0.0 or not all(math.isfinite(v) for v in C_new):
            raise ValueError(f"Q4 nonphysical moisture at t={next_time:g} s")
        final_picard_residual = max(
            max(abs(a - b) / max(1.0, abs(a), abs(b)) for a, b in zip(T_new, T_guess)),
            max(abs(a - b) / max(1.0, abs(a), abs(b)) for a, b in zip(C_new, C_guess)),
        )
        T_guess, C_guess = list(T_new), list(C_new)
        last_heat_system, last_moisture_system = heat_system, moisture_system
        if final_picard_residual <= picard_tolerance:
            break
    else:
        raise ValueError(f"Q4 Picard failed at t={next_time:g} s")

    d_nodes = diffusivity_array(C_guess, T_guess)
    d_faces = interface_values(d_nodes, "harmonic")
    internal, robin, robin_residual = boundary_flux_pair(C_guess[-1], C_guess[-2], grid, d_faces[-1], 8.0e-7, env_moisture)
    # For a shrinking cylindrical control volume, total moisture changes by
    # external Robin loss plus the prescribed moving-boundary term.
    old_mean = 2.0 * np.trapezoid(np.asarray(old_C) * xi, xi)
    new_mean = 2.0 * np.trapezoid(np.asarray(C_guess) * xi, xi)
    previous_radius_m = state.radius_cm / 100.0
    mass_step_residual = (radius_m**2 * new_mean - previous_radius_m**2 * old_mean) / max(radius_m**2, 1e-30)
    # The normalized balance residual is retained as a diagnostic; its sign
    # convention is explicit and is not used to alter the solution.
    moving_term = alpha * C_guess[-1]
    mass_step_residual -= dt_s * (-2.0 * robin / max(radius_m, 1e-30) + moving_term)
    return Q4State(
        time_s=next_time, radius_cm=radius_cm, temperature_k=T_guess, moisture=C_guess,
        picard_iterations=iteration, nonlinear_residual=final_picard_residual,
        linear_residual=max(tridiagonal_residual_linf(last_heat_system, T_guess), tridiagonal_residual_linf(last_moisture_system, C_guess)),
        radius_rate_cm_s=rate_m_s * 100.0, mass_step_residual=mass_step_residual, robin_residual=robin_residual,
    )


def initial_state(n_intervals: int, radius_cm: float = 2.0) -> Q4State:
    n = n_intervals + 1
    return Q4State(0.0, radius_cm, [301.15] * n, [2.55] * n)


def map_to_physical_radii(state: Q4State, radii_cm: Sequence[float]) -> List[float | None]:
    """Map current material field to fixed physical radii; blank outside R."""

    radius = float(state.radius_cm)
    xi = np.linspace(0.0, 1.0, len(state.moisture))
    result: List[float | None] = []
    for r in radii_cm:
        r = float(r)
        if r > radius + 1e-12:
            result.append(None)
        elif abs(r - radius) <= 1e-12:
            result.append(float(state.moisture[-1]))
        else:
            result.append(float(np.interp(r / radius, xi, np.asarray(state.moisture))))
    return result


def material_profile_csv_row(state: Q4State) -> Dict[str, float]:
    row = {"time_s": state.time_s, "radius_cm": state.radius_cm, "cmax": state.cmax, "center": state.moisture[0], "surface": state.moisture[-1], "mean": state.mean_moisture, "picard_iterations": state.picard_iterations, "nonlinear_residual": state.nonlinear_residual, "linear_residual": state.linear_residual, "radius_rate_cm_s": state.radius_rate_cm_s, "mass_step_residual": state.mass_step_residual, "robin_residual": state.robin_residual}
    return row
