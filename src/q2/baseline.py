"""Finite-cost Q2-B0 fixed-property control.

This module deliberately keeps the same geometry, environment, radial FVM,
and time discretization as a supplied Q2 configuration. Only the Appendix 3
properties are frozen at the initial state and the two fields are advanced
once per time step without coupled Picard iterations. It is a control, not a
replacement for Q2-M1.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, Tuple

from src.common.numerics import NonuniformRadialGrid, RadialGrid
from src.q1.model import radial_control_volume_factors

from .config import Q2RunConfig
from .environment import EnvironmentProvider
from .model import assemble_variable_radial_system, interface_values, solve_system
from .properties import cp, diffusivity, conductivity, density
from .solver import grid_for_config


@dataclass
class Q2BaselineResult:
    config: Q2RunConfig
    grid: RadialGrid | NonuniformRadialGrid
    snapshots: Dict[float, Tuple[Tuple[float, ...], Tuple[float, ...]]] = field(default_factory=dict)
    final_temperature_k: Tuple[float, ...] = ()
    final_moisture: Tuple[float, ...] = ()
    steps: int = 0

    def snapshot_at(self, time_s: float):
        key = min(self.snapshots, key=lambda value: abs(value - float(time_s)))
        if abs(key - float(time_s)) > 1.0e-8:
            raise KeyError(f"snapshot {time_s} s was not recorded")
        return self.snapshots[key]


def run_q2_b0(config: Q2RunConfig, *, record_times: Iterable[float] = ()) -> Q2BaselineResult:
    env = EnvironmentProvider.from_attachment1(
        config.input_path,
        method=config.interpolation,
        post_attachment_mode=config.post_attachment_mode,
        post_temperature_c=config.post_temperature_c,
        post_moisture_kg_kg=config.post_moisture_kg_kg,
    )
    grid = grid_for_config(config)
    n = len(grid.nodes_m)
    params = config.parameters
    # Freeze all properties at the initial state, with the required Kelvin
    # conversion for the diffusivity formula.
    initial_t = params.initial_temperature_c + 273.15
    rho0 = density(params.initial_moisture_kg_kg)
    cp0 = cp(params.initial_moisture_kg_kg)
    k0 = conductivity(params.initial_moisture_kg_kg)
    d0 = diffusivity(params.initial_moisture_kg_kg, initial_t)
    heat_capacity = [rho0 * cp0] * n
    k_faces = interface_values([k0] * n, config.interface_mean)
    d_faces = interface_values([d0] * n, config.interface_mean)
    requested = tuple(sorted(set(float(value) for value in record_times)))
    if any(value < -1.0e-12 or value > config.end_time_s + 1.0e-12 for value in requested):
        raise ValueError("record_times must lie inside the requested baseline horizon")

    temperature = [initial_t] * n
    moisture = [params.initial_moisture_kg_kg] * n
    previous_temperature = None
    previous_moisture = None
    snapshots = {}
    if 0.0 in requested:
        snapshots[0.0] = (tuple(temperature), tuple(moisture))
    current_time = 0.0
    while current_time < config.end_time_s - 1.0e-12:
        next_time = current_time + config.time_step_s
        env_temperature_c, env_moisture = env.at(next_time)
        scheme = "bdf2" if config.scheme == "bdf2" and previous_temperature is not None else "be"
        heat_system = assemble_variable_radial_system(
            temperature, grid, config.time_step_s, heat_capacity, k_faces,
            params.heat_transfer_w_m2_k, env_temperature_c + 273.15,
            scheme=scheme, previous_values=previous_temperature,
        )
        moisture_system = assemble_variable_radial_system(
            moisture, grid, config.time_step_s, [1.0] * n, d_faces,
            params.mass_transfer_m_s, env_moisture,
            scheme=scheme, previous_values=previous_moisture,
        )
        next_temperature = solve_system(heat_system)
        next_moisture = solve_system(moisture_system)
        if not all(math.isfinite(value) and value > 0.0 for value in next_moisture):
            raise ValueError(f"Q2-B0 produced invalid moisture at {next_time:g} s")
        previous_temperature, previous_moisture = temperature, moisture
        temperature, moisture = next_temperature, next_moisture
        current_time = next_time
        for target in requested:
            if abs(target - current_time) < 1.0e-9:
                snapshots[round(target, 12)] = (tuple(temperature), tuple(moisture))
    return Q2BaselineResult(config, grid, snapshots, tuple(temperature), tuple(moisture), int(round(current_time / config.time_step_s)))
