"""Q1 B0 lumped exchange baseline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .config import DEFAULT_PARAMETERS, Q1Parameters, Q1RunConfig
from .inputs import BoundaryProvider, celsius_to_kelvin


@dataclass(frozen=True)
class BaselineResult:
    config: Q1RunConfig
    times_s: Tuple[float, ...]
    temperatures_k: Tuple[float, ...]
    moistures_kg_kg: Tuple[float, ...]


def run_b0(
    config: Q1RunConfig,
    boundary: BoundaryProvider,
    parameters: Q1Parameters = DEFAULT_PARAMETERS,
) -> BaselineResult:
    area_to_volume = 2.0 / parameters.radius_m
    heat_rate = parameters.heat_transfer_w_m2_k * area_to_volume / (
        parameters.density_kg_m3 * parameters.heat_capacity_j_kg_k
    )
    moisture_rate = parameters.mass_transfer_m_s * area_to_volume
    temperature = celsius_to_kelvin(config.initial_temperature_c)
    moisture = config.initial_moisture_kg_kg
    times = [0.0]
    temperatures = [temperature]
    moistures = [moisture]
    for step in range(1, int(round(config.end_time_s / config.time_step_s)) + 1):
        time_s = step * config.time_step_s
        environment_c, environment_moisture = boundary.at(time_s)
        dt = config.time_step_s
        temperature = (temperature + dt * heat_rate * celsius_to_kelvin(environment_c)) / (1.0 + dt * heat_rate)
        moisture = (moisture + dt * moisture_rate * environment_moisture) / (1.0 + dt * moisture_rate)
        times.append(time_s)
        temperatures.append(temperature)
        moistures.append(moisture)
    return BaselineResult(config, tuple(times), tuple(temperatures), tuple(moistures))
