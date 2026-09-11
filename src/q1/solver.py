"""Q1 M1 solver: constant-property heat field and nonlinear moisture field."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import List, Sequence, Tuple

from src.common.numerics import NonuniformRadialGrid, RadialGrid, make_boundary_clustered_grid, make_radial_grid

from .config import DEFAULT_PARAMETERS, Q1Parameters, Q1RunConfig
from .inputs import BoundaryProvider, celsius_to_kelvin
from .model import (
    arithmetic_face_values,
    boundary_flux_outward,
    implicit_bdf2_radial_step,
    implicit_nonuniform_radial_step,
    implicit_radial_step,
)


class PicardConvergenceError(RuntimeError):
    pass


@dataclass(frozen=True)
class Q1Result:
    config: Q1RunConfig
    grid: RadialGrid | NonuniformRadialGrid
    times_s: Tuple[float, ...]
    temperatures_k: Tuple[Tuple[float, ...], ...]
    moistures_kg_kg: Tuple[Tuple[float, ...], ...]
    picard_iterations: Tuple[int, ...]
    heat_flux_in_w_m2: Tuple[float, ...]
    moisture_flux_out_m_s: Tuple[float, ...]

    @property
    def temperatures_c(self) -> Tuple[Tuple[float, ...], ...]:
        return tuple(tuple(value - 273.15 for value in row) for row in self.temperatures_k)


def _assert_finite(values: List[float], label: str) -> None:
    if not all(isfinite(value) for value in values):
        raise FloatingPointError(f"non-finite values in {label}")


def run_m1(
    config: Q1RunConfig,
    boundary: BoundaryProvider,
    parameters: Q1Parameters = DEFAULT_PARAMETERS,
) -> Q1Result:
    """Run M1 without writing any workbook or modifying official inputs."""

    if config.end_time_s > boundary.times_s[-1]:
        raise ValueError("Q1 run would require boundary extrapolation")
    grid = make_radial_grid(parameters.radius_m, config.n_intervals)
    node_count = config.n_intervals + 1
    temperature = [celsius_to_kelvin(config.initial_temperature_c)] * node_count
    moisture = [config.initial_moisture_kg_kg] * node_count
    times = [0.0]
    temperatures = [tuple(temperature)]
    moistures = [tuple(moisture)]
    picard_iterations = [0]
    heat_fluxes = [0.0]
    moisture_fluxes = [0.0]

    heat_capacity = parameters.density_kg_m3 * parameters.heat_capacity_j_kg_k
    current_time = 0.0
    steps = int(round(config.end_time_s / config.time_step_s))
    for _ in range(steps):
        next_time = current_time + config.time_step_s
        temperature_environment_c, moisture_environment = boundary.at(next_time)
        temperature_environment_k = celsius_to_kelvin(temperature_environment_c)

        temperature = implicit_radial_step(
            temperature,
            grid,
            config.time_step_s,
            heat_capacity,
            [parameters.conductivity_w_m_k] * config.n_intervals,
            parameters.heat_transfer_w_m2_k,
            temperature_environment_k,
            config.surface_boundary,
        )
        _assert_finite(temperature, "temperature")

        moisture_guess = list(moisture)
        for iteration in range(1, config.picard_max_iterations + 1):
            node_diffusivities = [parameters.diffusivity_m2_s(value) for value in moisture_guess]
            moisture_new = implicit_radial_step(
                moisture,
                grid,
                config.time_step_s,
                1.0,
                arithmetic_face_values(node_diffusivities),
                parameters.mass_transfer_m_s,
                moisture_environment,
                config.surface_boundary,
            )
            _assert_finite(moisture_new, "moisture")
            scale = max(1.0e-30, max(abs(value) for value in moisture_new))
            error = max(abs(new - old) for new, old in zip(moisture_new, moisture_guess)) / scale
            moisture_guess = moisture_new
            if error < config.picard_tolerance:
                break
        else:
            raise PicardConvergenceError(f"Q1 moisture Picard failed at t={next_time} s; error={error}")
        moisture = moisture_guess

        current_time = next_time
        times.append(current_time)
        temperatures.append(tuple(temperature))
        moistures.append(tuple(moisture))
        picard_iterations.append(iteration)
        heat_fluxes.append(parameters.heat_transfer_w_m2_k * (temperature_environment_k - temperature[-1]))
        moisture_fluxes.append(boundary_flux_outward(moisture[-1], moisture_environment, parameters.mass_transfer_m_s))

    return Q1Result(
        config=config,
        grid=grid,
        times_s=tuple(times),
        temperatures_k=tuple(temperatures),
        moistures_kg_kg=tuple(moistures),
        picard_iterations=tuple(picard_iterations),
        heat_flux_in_w_m2=tuple(heat_fluxes),
        moisture_flux_out_m_s=tuple(moisture_fluxes),
    )


def run_m1_nonuniform(
    config: Q1RunConfig,
    boundary: BoundaryProvider,
    parameters: Q1Parameters = DEFAULT_PARAMETERS,
    cluster_power: float = 2.0,
    required_output_positions_m: Sequence[float] = (),
) -> Q1Result:
    """Run M1 on a boundary-clustered conservative radial grid candidate."""

    if config.end_time_s > boundary.times_s[-1]:
        raise ValueError("Q1 run would require boundary extrapolation")
    grid = make_boundary_clustered_grid(
        parameters.radius_m,
        config.n_intervals,
        cluster_power,
        required_nodes_m=required_output_positions_m,
    )
    node_count = grid.n_intervals + 1
    temperature = [celsius_to_kelvin(config.initial_temperature_c)] * node_count
    moisture = [config.initial_moisture_kg_kg] * node_count
    times = [0.0]
    temperatures = [tuple(temperature)]
    moistures = [tuple(moisture)]
    picard_iterations = [0]
    heat_fluxes = [0.0]
    moisture_fluxes = [0.0]

    heat_capacity = parameters.density_kg_m3 * parameters.heat_capacity_j_kg_k
    current_time = 0.0
    steps = int(round(config.end_time_s / config.time_step_s))
    for _ in range(steps):
        next_time = current_time + config.time_step_s
        temperature_environment_c, moisture_environment = boundary.at(next_time)
        temperature_environment_k = celsius_to_kelvin(temperature_environment_c)
        temperature = implicit_nonuniform_radial_step(
            temperature,
            grid,
            config.time_step_s,
            heat_capacity,
            [parameters.conductivity_w_m_k] * grid.n_intervals,
            parameters.heat_transfer_w_m2_k,
            temperature_environment_k,
            config.surface_boundary,
        )
        _assert_finite(temperature, "temperature")

        moisture_guess = list(moisture)
        for iteration in range(1, config.picard_max_iterations + 1):
            node_diffusivities = [parameters.diffusivity_m2_s(value) for value in moisture_guess]
            moisture_new = implicit_nonuniform_radial_step(
                moisture,
                grid,
                config.time_step_s,
                1.0,
                arithmetic_face_values(node_diffusivities),
                parameters.mass_transfer_m_s,
                moisture_environment,
                config.surface_boundary,
            )
            _assert_finite(moisture_new, "moisture")
            scale = max(1.0e-30, max(abs(value) for value in moisture_new))
            error = max(abs(new - old) for new, old in zip(moisture_new, moisture_guess)) / scale
            moisture_guess = moisture_new
            if error < config.picard_tolerance:
                break
        else:
            raise PicardConvergenceError(f"Q1 nonuniform moisture Picard failed at t={next_time} s; error={error}")
        moisture = moisture_guess
        current_time = next_time
        times.append(current_time)
        temperatures.append(tuple(temperature))
        moistures.append(tuple(moisture))
        picard_iterations.append(iteration)
        heat_fluxes.append(parameters.heat_transfer_w_m2_k * (temperature_environment_k - temperature[-1]))
        moisture_fluxes.append(boundary_flux_outward(moisture[-1], moisture_environment, parameters.mass_transfer_m_s))

    return Q1Result(
        config=config,
        grid=grid,
        times_s=tuple(times),
        temperatures_k=tuple(temperatures),
        moistures_kg_kg=tuple(moistures),
        picard_iterations=tuple(picard_iterations),
        heat_flux_in_w_m2=tuple(heat_fluxes),
        moisture_flux_out_m_s=tuple(moisture_fluxes),
    )


def run_m2(
    config: Q1RunConfig,
    boundary: BoundaryProvider,
    parameters: Q1Parameters = DEFAULT_PARAMETERS,
    reference_moisture_kg_kg: float | None = None,
) -> Q1Result:
    """Run the constant-D radial comparison model without writing files.

    M2 shares M1's heat equation, grid, implicit step, and boundary. Only
    moisture diffusivity is fixed at ``D(C_ref)``; by default ``C_ref`` is
    the configured initial moisture.
    """

    if config.end_time_s > boundary.times_s[-1]:
        raise ValueError("Q1 run would require boundary extrapolation")
    reference = config.initial_moisture_kg_kg if reference_moisture_kg_kg is None else reference_moisture_kg_kg
    if reference <= 0.0:
        raise ValueError("M2 reference moisture must be positive")
    grid = make_radial_grid(parameters.radius_m, config.n_intervals)
    node_count = config.n_intervals + 1
    temperature = [celsius_to_kelvin(config.initial_temperature_c)] * node_count
    moisture = [config.initial_moisture_kg_kg] * node_count
    times = [0.0]
    temperatures = [tuple(temperature)]
    moistures = [tuple(moisture)]
    picard_iterations = [0]
    heat_fluxes = [0.0]
    moisture_fluxes = [0.0]

    heat_capacity = parameters.density_kg_m3 * parameters.heat_capacity_j_kg_k
    constant_diffusivity = parameters.diffusivity_m2_s(reference)
    current_time = 0.0
    steps = int(round(config.end_time_s / config.time_step_s))
    for _ in range(steps):
        next_time = current_time + config.time_step_s
        temperature_environment_c, moisture_environment = boundary.at(next_time)
        temperature_environment_k = celsius_to_kelvin(temperature_environment_c)
        temperature = implicit_radial_step(
            temperature,
            grid,
            config.time_step_s,
            heat_capacity,
            [parameters.conductivity_w_m_k] * config.n_intervals,
            parameters.heat_transfer_w_m2_k,
            temperature_environment_k,
            config.surface_boundary,
        )
        moisture = implicit_radial_step(
            moisture,
            grid,
            config.time_step_s,
            1.0,
            [constant_diffusivity] * config.n_intervals,
            parameters.mass_transfer_m_s,
            moisture_environment,
            config.surface_boundary,
        )
        _assert_finite(temperature, "temperature")
        _assert_finite(moisture, "moisture")
        current_time = next_time
        times.append(current_time)
        temperatures.append(tuple(temperature))
        moistures.append(tuple(moisture))
        picard_iterations.append(1)
        heat_fluxes.append(parameters.heat_transfer_w_m2_k * (temperature_environment_k - temperature[-1]))
        moisture_fluxes.append(boundary_flux_outward(moisture[-1], moisture_environment, parameters.mass_transfer_m_s))

    return Q1Result(
        config=config,
        grid=grid,
        times_s=tuple(times),
        temperatures_k=tuple(temperatures),
        moistures_kg_kg=tuple(moistures),
        picard_iterations=tuple(picard_iterations),
        heat_flux_in_w_m2=tuple(heat_fluxes),
        moisture_flux_out_m_s=tuple(moisture_fluxes),
    )


def run_m1_bdf2(
    config: Q1RunConfig,
    boundary: BoundaryProvider,
    parameters: Q1Parameters = DEFAULT_PARAMETERS,
    startup_step_s: float | None = None,
    startup_duration_s: float = 1.0,
) -> Q1Result:
    """Run the M1-NUM-T2 BDF2 candidate with optional early BE substeps.

    The physical equations, parameters, boundary conditions and Picard
    handling match ``run_m1``. Only the time integrator changes after the
    startup phase; this function is kept separate so the original M1 remains
    the Backward-Euler reference implementation. With ``startup_step_s`` set,
    the interval ``0..startup_duration_s`` uses BE substeps, followed by one
    normal-size BE restart step and then BDF2. The restart avoids applying a
    fixed-step BDF2 stencil across a step-size change.
    """

    if config.end_time_s > boundary.times_s[-1]:
        raise ValueError("Q1 run would require boundary extrapolation")
    if startup_step_s is not None and startup_step_s <= 0.0:
        raise ValueError("startup_step_s must be positive")
    if startup_duration_s < 0.0:
        raise ValueError("startup_duration_s must be non-negative")
    grid = make_radial_grid(parameters.radius_m, config.n_intervals)
    node_count = config.n_intervals + 1
    temperature = [celsius_to_kelvin(config.initial_temperature_c)] * node_count
    moisture = [config.initial_moisture_kg_kg] * node_count
    previous_temperature = list(temperature)
    previous_moisture = list(moisture)
    times = [0.0]
    temperatures = [tuple(temperature)]
    moistures = [tuple(moisture)]
    picard_iterations = [0]
    heat_fluxes = [0.0]
    moisture_fluxes = [0.0]

    heat_capacity = parameters.density_kg_m3 * parameters.heat_capacity_j_kg_k
    current_time = 0.0
    be_restart_pending = True
    while current_time < config.end_time_s - 1.0e-12:
        in_early_startup = (
            startup_step_s is not None
            and current_time < min(startup_duration_s, config.end_time_s) - 1.0e-12
        )
        if in_early_startup:
            step_dt = min(startup_step_s, startup_duration_s - current_time)
            use_bdf2 = False
        else:
            step_dt = config.time_step_s
            use_bdf2 = not be_restart_pending
            be_restart_pending = False
        next_time = min(config.end_time_s, current_time + step_dt)
        step_dt = next_time - current_time
        temperature_environment_c, moisture_environment = boundary.at(next_time)
        temperature_environment_k = celsius_to_kelvin(temperature_environment_c)

        if not use_bdf2:
            temperature_new = implicit_radial_step(
                temperature,
                grid,
                step_dt,
                heat_capacity,
                [parameters.conductivity_w_m_k] * config.n_intervals,
                parameters.heat_transfer_w_m2_k,
                temperature_environment_k,
                config.surface_boundary,
            )
        else:
            temperature_new = implicit_bdf2_radial_step(
                temperature,
                previous_temperature,
                grid,
                config.time_step_s,
                heat_capacity,
                [parameters.conductivity_w_m_k] * config.n_intervals,
                parameters.heat_transfer_w_m2_k,
                temperature_environment_k,
                config.surface_boundary,
            )
        _assert_finite(temperature_new, "temperature")

        moisture_guess = list(moisture)
        for iteration in range(1, config.picard_max_iterations + 1):
            node_diffusivities = [parameters.diffusivity_m2_s(value) for value in moisture_guess]
            if not use_bdf2:
                moisture_new = implicit_radial_step(
                    moisture,
                    grid,
                    step_dt,
                    1.0,
                    arithmetic_face_values(node_diffusivities),
                    parameters.mass_transfer_m_s,
                    moisture_environment,
                    config.surface_boundary,
                )
            elif use_bdf2:
                moisture_new = implicit_bdf2_radial_step(
                    moisture,
                    previous_moisture,
                    grid,
                    step_dt,
                    1.0,
                    arithmetic_face_values(node_diffusivities),
                    parameters.mass_transfer_m_s,
                    moisture_environment,
                    config.surface_boundary,
                )
            _assert_finite(moisture_new, "moisture")
            scale = max(1.0e-30, max(abs(value) for value in moisture_new))
            error = max(abs(new - old) for new, old in zip(moisture_new, moisture_guess)) / scale
            moisture_guess = moisture_new
            if error < config.picard_tolerance:
                break
        else:
            raise PicardConvergenceError(f"Q1 BDF2 moisture Picard failed at t={next_time} s; error={error}")

        previous_temperature = temperature
        previous_moisture = moisture
        temperature = temperature_new
        moisture = moisture_guess
        current_time = next_time
        times.append(current_time)
        temperatures.append(tuple(temperature))
        moistures.append(tuple(moisture))
        picard_iterations.append(iteration)
        heat_fluxes.append(parameters.heat_transfer_w_m2_k * (temperature_environment_k - temperature[-1]))
        moisture_fluxes.append(boundary_flux_outward(moisture[-1], moisture_environment, parameters.mass_transfer_m_s))

    return Q1Result(
        config=config,
        grid=grid,
        times_s=tuple(times),
        temperatures_k=tuple(temperatures),
        moistures_kg_kg=tuple(moistures),
        picard_iterations=tuple(picard_iterations),
        heat_flux_in_w_m2=tuple(heat_fluxes),
        moisture_flux_out_m_s=tuple(moisture_fluxes),
    )
