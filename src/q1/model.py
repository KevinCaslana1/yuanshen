"""Q1 radial finite-volume matrix assembly."""

from __future__ import annotations

from typing import Callable, List, Sequence, Tuple

from src.common.numerics import NonuniformRadialGrid, RadialGrid, thomas_solve


def arithmetic_face_values(node_values: Sequence[float]) -> List[float]:
    if len(node_values) < 2:
        raise ValueError("at least two node values are required")
    return [0.5 * (left + right) for left, right in zip(node_values, node_values[1:])]


def assemble_radial_system(
    old_values: Sequence[float],
    grid: RadialGrid,
    dt_s: float,
    capacity: float,
    face_diffusivities: Sequence[float],
    surface_transfer: float,
    environment_value: float,
    surface_boundary: str = "robin",
) -> Tuple[List[float], List[float], List[float], List[float]]:
    """Assemble a backward-Euler nodal FVM system.

    `capacity` is the storage coefficient (rho*cp for temperature and 1 for
    concentration). `face_diffusivities` contains one value per radial face.
    The surface condition is `a*u_r = surface_transfer*(u_inf-u_s)`.
    """

    n = grid.n_intervals
    if len(old_values) != n + 1 or len(face_diffusivities) != n:
        raise ValueError("radial system dimensions do not match grid")
    if dt_s <= 0.0 or capacity <= 0.0 or surface_transfer < 0.0:
        raise ValueError("invalid radial system coefficients")
    if surface_boundary not in {"robin", "dirichlet"}:
        raise ValueError("surface_boundary must be robin or dirichlet")

    dr = grid.dr_m
    radius = grid.radius_m
    lower = [0.0] * (n + 1)
    diagonal = [0.0] * (n + 1)
    upper = [0.0] * (n + 1)
    rhs = [float(value) for value in old_values]

    center_coefficient = 4.0 * dt_s * face_diffusivities[0] / (capacity * dr * dr)
    diagonal[0] = 1.0 + center_coefficient
    upper[0] = -center_coefficient

    for index in range(1, n):
        r_left = (index - 0.5) * dr
        r_right = (index + 0.5) * dr
        left_coefficient = dt_s * r_left * face_diffusivities[index - 1] / (capacity * index * dr**3)
        right_coefficient = dt_s * r_right * face_diffusivities[index] / (capacity * index * dr**3)
        lower[index] = -left_coefficient
        diagonal[index] = 1.0 + left_coefficient + right_coefficient
        upper[index] = -right_coefficient

    surface_half_radius = radius - 0.5 * dr
    surface_volume_factor = 0.5 * (radius * radius - surface_half_radius * surface_half_radius)
    surface_storage = capacity * surface_volume_factor
    if surface_boundary == "dirichlet":
        diagonal[n] = 1.0
        rhs[n] = environment_value
        return lower, diagonal, upper, rhs
    inner_coefficient = dt_s * surface_half_radius * face_diffusivities[-1] / (surface_storage * dr)
    external_coefficient = dt_s * radius * surface_transfer / surface_storage
    lower[n] = -inner_coefficient
    diagonal[n] = 1.0 + inner_coefficient + external_coefficient
    rhs[n] += external_coefficient * environment_value
    return lower, diagonal, upper, rhs


def implicit_radial_step(
    old_values: Sequence[float],
    grid: RadialGrid,
    dt_s: float,
    capacity: float,
    face_diffusivities: Sequence[float],
    surface_transfer: float,
    environment_value: float,
    surface_boundary: str = "robin",
) -> List[float]:
    system = assemble_radial_system(
        old_values,
        grid,
        dt_s,
        capacity,
        face_diffusivities,
        surface_transfer,
        environment_value,
        surface_boundary,
    )
    return thomas_solve(*system[:3], system[3])


def assemble_nonuniform_radial_system(
    old_values: Sequence[float],
    grid: NonuniformRadialGrid,
    dt_s: float,
    capacity: float,
    face_diffusivities: Sequence[float],
    surface_transfer: float,
    environment_value: float,
    surface_boundary: str = "robin",
) -> Tuple[List[float], List[float], List[float], List[float]]:
    """Assemble the same conservative radial FVM on a nonuniform grid."""

    n = grid.n_intervals
    if len(old_values) != n + 1 or len(face_diffusivities) != n:
        raise ValueError("radial system dimensions do not match grid")
    if dt_s <= 0.0 or capacity <= 0.0 or surface_transfer < 0.0:
        raise ValueError("invalid radial system coefficients")
    if surface_boundary not in {"robin", "dirichlet"}:
        raise ValueError("surface_boundary must be robin or dirichlet")

    nodes = grid.nodes_m
    faces = [0.5 * (left + right) for left, right in zip(nodes, nodes[1:])]
    volumes = [0.5 * faces[0] ** 2]
    volumes.extend(0.5 * (faces[index] ** 2 - faces[index - 1] ** 2) for index in range(1, n))
    volumes.append(0.5 * (grid.radius_m**2 - faces[-1] ** 2))
    lower = [0.0] * (n + 1)
    diagonal = [0.0] * (n + 1)
    upper = [0.0] * (n + 1)
    rhs = [float(value) for value in old_values]

    center = dt_s * faces[0] * face_diffusivities[0] / (capacity * volumes[0] * (nodes[1] - nodes[0]))
    diagonal[0] = 1.0 + center
    upper[0] = -center
    for index in range(1, n):
        left = dt_s * faces[index - 1] * face_diffusivities[index - 1] / (
            capacity * volumes[index] * (nodes[index] - nodes[index - 1])
        )
        right = dt_s * faces[index] * face_diffusivities[index] / (
            capacity * volumes[index] * (nodes[index + 1] - nodes[index])
        )
        lower[index] = -left
        diagonal[index] = 1.0 + left + right
        upper[index] = -right
    if surface_boundary == "dirichlet":
        diagonal[-1] = 1.0
        rhs[-1] = environment_value
        return lower, diagonal, upper, rhs
    inner = dt_s * faces[-1] * face_diffusivities[-1] / (
        capacity * volumes[-1] * (nodes[-1] - nodes[-2])
    )
    external = dt_s * grid.radius_m * surface_transfer / (capacity * volumes[-1])
    lower[-1] = -inner
    diagonal[-1] = 1.0 + inner + external
    rhs[-1] += external * environment_value
    return lower, diagonal, upper, rhs


def implicit_nonuniform_radial_step(
    old_values: Sequence[float],
    grid: NonuniformRadialGrid,
    dt_s: float,
    capacity: float,
    face_diffusivities: Sequence[float],
    surface_transfer: float,
    environment_value: float,
    surface_boundary: str = "robin",
) -> List[float]:
    system = assemble_nonuniform_radial_system(
        old_values,
        grid,
        dt_s,
        capacity,
        face_diffusivities,
        surface_transfer,
        environment_value,
        surface_boundary,
    )
    return thomas_solve(*system[:3], system[3])


def assemble_bdf2_radial_system(
    old_values: Sequence[float],
    previous_values: Sequence[float],
    grid: RadialGrid,
    dt_s: float,
    capacity: float,
    face_diffusivities: Sequence[float],
    surface_transfer: float,
    environment_value: float,
    surface_boundary: str = "robin",
) -> Tuple[List[float], List[float], List[float], List[float]]:
    """Assemble the BDF2 system for the same radial operator as BE.

    For Robin rows, the operator and boundary forcing are scaled by 2/3 and
    the history is ``4/3*u_n - 1/3*u_(n-1)``. Dirichlet rows remain explicit
    algebraic boundary values. This is a numerical-method candidate only; it
    does not change the Q1 physical model.
    """

    if len(previous_values) != len(old_values):
        raise ValueError("BDF2 history vectors must have the same length")
    be_lower, be_diagonal, be_upper, be_rhs = assemble_radial_system(
        old_values,
        grid,
        dt_s,
        capacity,
        face_diffusivities,
        surface_transfer,
        environment_value,
        surface_boundary,
    )
    if surface_boundary == "dirichlet":
        rhs = [4.0 / 3.0 * old - 1.0 / 3.0 * previous for old, previous in zip(old_values, previous_values)]
        rhs[-1] = environment_value
        return [0.0] * len(old_values), [1.0] * len(old_values), [0.0] * len(old_values), rhs

    operator_scale = 2.0 / 3.0
    lower = [operator_scale * value for value in be_lower]
    diagonal = [1.0 + operator_scale * (value - 1.0) for value in be_diagonal]
    upper = [operator_scale * value for value in be_upper]
    history = [4.0 / 3.0 * old - 1.0 / 3.0 * previous for old, previous in zip(old_values, previous_values)]
    boundary_forcing = [be_value - old for be_value, old in zip(be_rhs, old_values)]
    rhs = [value + operator_scale * forcing for value, forcing in zip(history, boundary_forcing)]
    return lower, diagonal, upper, rhs


def implicit_bdf2_radial_step(
    old_values: Sequence[float],
    previous_values: Sequence[float],
    grid: RadialGrid,
    dt_s: float,
    capacity: float,
    face_diffusivities: Sequence[float],
    surface_transfer: float,
    environment_value: float,
    surface_boundary: str = "robin",
) -> List[float]:
    system = assemble_bdf2_radial_system(
        old_values,
        previous_values,
        grid,
        dt_s,
        capacity,
        face_diffusivities,
        surface_transfer,
        environment_value,
        surface_boundary,
    )
    return thomas_solve(*system[:3], system[3])


def radial_control_volume_factors(grid: RadialGrid) -> List[float]:
    dr = grid.dr_m
    factors = [0.125 * dr * dr]
    factors.extend(index * dr * dr for index in range(1, grid.n_intervals))
    inner = grid.radius_m - 0.5 * dr
    factors.append(0.5 * (grid.radius_m * grid.radius_m - inner * inner))
    return factors


def boundary_flux_outward(surface_value: float, environment_value: float, transfer: float) -> float:
    return transfer * (surface_value - environment_value)
