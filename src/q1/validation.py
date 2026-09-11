"""Runtime checks for Q1 implementation experiments."""

from __future__ import annotations

from math import isfinite
from typing import Dict

from .config import DEFAULT_PARAMETERS
from .solver import Q1Result
from .model import radial_control_volume_factors


def _weighted_integral(values, factors) -> float:
    return sum(value * factor for value, factor in zip(values, factors))


def validate_m1_result(result: Q1Result) -> Dict[str, float | bool]:
    grid = result.grid
    factors = radial_control_volume_factors(grid)
    initial_temperature = result.temperatures_k[0][0]
    initial_moisture = result.moistures_kg_kg[0][0]
    all_values = [value for row in result.temperatures_k for value in row]
    all_values.extend(value for row in result.moistures_kg_kg for value in row)
    finite = all(isfinite(value) for value in all_values)
    initial_ok = all(abs(value - initial_temperature) < 1.0e-12 for value in result.temperatures_k[0]) and all(
        abs(value - initial_moisture) < 1.0e-12 for value in result.moistures_kg_kg[0]
    )
    time_ok = all(right > left for left, right in zip(result.times_s, result.times_s[1:]))
    max_picard = max(result.picard_iterations)

    moisture_initial_mass = 2.0 * 3.141592653589793 * _weighted_integral(result.moistures_kg_kg[0], factors)
    moisture_final_mass = 2.0 * 3.141592653589793 * _weighted_integral(result.moistures_kg_kg[-1], factors)
    moisture_loss = sum(
        result.config.time_step_s * 2.0 * 3.141592653589793 * grid.radius_m * flux
        for flux in result.moisture_flux_out_m_s[1:]
    )
    mass_residual = (moisture_initial_mass - moisture_final_mass) - moisture_loss

    heat_capacity = DEFAULT_PARAMETERS.density_kg_m3 * DEFAULT_PARAMETERS.heat_capacity_j_kg_k
    heat_storage_change = 2.0 * 3.141592653589793 * heat_capacity * _weighted_integral(
        [value - initial_temperature for value in result.temperatures_k[-1]], factors
    )
    heat_input = sum(
        result.config.time_step_s * 2.0 * 3.141592653589793 * grid.radius_m * flux
        for flux in result.heat_flux_in_w_m2[1:]
    )
    energy_residual = heat_storage_change - heat_input
    return {
        "finite": finite,
        "initial_ok": initial_ok,
        "time_ok": time_ok,
        "max_picard_iterations": max_picard,
        "mass_balance_residual": mass_residual,
        "energy_balance_residual": energy_residual,
        "temperature_initial_c": initial_temperature - 273.15,
        "temperature_final_surface_c": result.temperatures_k[-1][-1] - 273.15,
        "moisture_initial_center": result.moistures_kg_kg[0][0],
        "moisture_final_center": result.moistures_kg_kg[-1][0],
        "moisture_final_surface": result.moistures_kg_kg[-1][-1],
    }
