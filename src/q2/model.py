"""Conservative variable-coefficient cylindrical radial FVM for Q2."""

from __future__ import annotations

from typing import Callable, List, Sequence, Tuple

from src.common.numerics import NonuniformRadialGrid, RadialGrid, thomas_solve
from src.q1.model import radial_control_volume_factors


Grid = RadialGrid | NonuniformRadialGrid


def interface_values(node_values: Sequence[float], method: str = "harmonic") -> List[float]:
    if len(node_values) < 2:
        raise ValueError("at least two node values are required")
    if method not in {"arithmetic", "harmonic"}:
        raise ValueError("method must be arithmetic or harmonic")
    if method == "arithmetic":
        return [0.5 * (a + b) for a, b in zip(node_values, node_values[1:])]
    result = []
    for a, b in zip(node_values, node_values[1:]):
        if a <= 0 or b <= 0:
            raise ValueError("harmonic mean requires positive coefficients")
        result.append(2.0 * a * b / (a + b))
    return result


def _faces(grid: Grid) -> List[float]:
    return [0.5 * (a + b) for a, b in zip(grid.nodes_m, grid.nodes_m[1:])]


def assemble_variable_radial_system(
    old_values: Sequence[float],
    grid: Grid,
    dt_s: float,
    capacities: Sequence[float],
    face_coefficients: Sequence[float],
    surface_transfer: float,
    environment_value: float,
    *,
    scheme: str = "be",
    previous_values: Sequence[float] | None = None,
    source_values: Sequence[float] | None = None,
) -> Tuple[List[float], List[float], List[float], List[float]]:
    """Assemble BE/BDF2 with node storage and conservative face fluxes.

    The physical row is storage*difference = inward diffusion + source. The
    surface equation uses the half-cell volume and an outward-positive Robin
    flux ``transfer*(u_surface-u_environment)``.
    """

    n = len(grid.nodes_m) - 1
    if len(old_values) != n + 1 or len(capacities) != n + 1 or len(face_coefficients) != n:
        raise ValueError("radial system dimensions do not match grid")
    if dt_s <= 0 or surface_transfer < 0 or any(value <= 0 for value in capacities):
        raise ValueError("invalid radial system coefficients")
    if scheme not in {"be", "bdf2"}:
        raise ValueError("scheme must be be or bdf2")
    if scheme == "bdf2" and (previous_values is None or len(previous_values) != n + 1):
        raise ValueError("BDF2 requires a previous vector")
    if source_values is not None and len(source_values) != n + 1:
        raise ValueError("source_values dimensions do not match grid")
    volumes = radial_control_volume_factors(grid)
    faces = _faces(grid)
    nodes = grid.nodes_m
    lower = [0.0] * (n + 1)
    diagonal = [0.0] * (n + 1)
    upper = [0.0] * (n + 1)
    source = list(source_values) if source_values is not None else [0.0] * (n + 1)
    rhs_be = [float(value) + dt_s * source[i] for i, value in enumerate(old_values)]

    center = dt_s * faces[0] * face_coefficients[0] / (capacities[0] * volumes[0] * (nodes[1] - nodes[0]))
    diagonal[0] = 1.0 + center
    upper[0] = -center
    for i in range(1, n):
        left = dt_s * faces[i - 1] * face_coefficients[i - 1] / (capacities[i] * volumes[i] * (nodes[i] - nodes[i - 1]))
        right = dt_s * faces[i] * face_coefficients[i] / (capacities[i] * volumes[i] * (nodes[i + 1] - nodes[i]))
        lower[i] = -left
        diagonal[i] = 1.0 + left + right
        upper[i] = -right
    inner = dt_s * faces[-1] * face_coefficients[-1] / (capacities[-1] * volumes[-1] * (nodes[-1] - nodes[-2]))
    external = dt_s * grid.radius_m * surface_transfer / (capacities[-1] * volumes[-1])
    lower[-1] = -inner
    diagonal[-1] = 1.0 + inner + external
    rhs_be[-1] += external * environment_value

    if scheme == "be":
        return lower, diagonal, upper, rhs_be
    old = list(old_values)
    previous = list(previous_values or [])
    scale = 2.0 / 3.0
    lower_b = [scale * value for value in lower]
    diagonal_b = [1.0 + scale * (value - 1.0) for value in diagonal]
    upper_b = [scale * value for value in upper]
    history = [4.0 / 3.0 * old[i] - 1.0 / 3.0 * previous[i] for i in range(n + 1)]
    forcing = [rhs_be[i] - old[i] for i in range(n + 1)]
    rhs_b = [history[i] + scale * forcing[i] for i in range(n + 1)]
    return lower_b, diagonal_b, upper_b, rhs_b


def solve_variable_radial_system(*args, **kwargs) -> List[float]:
    system = assemble_variable_radial_system(*args, **kwargs)
    return thomas_solve(*system[:3], system[3])


def solve_system(system: Tuple[Sequence[float], Sequence[float], Sequence[float], Sequence[float]]) -> List[float]:
    return thomas_solve(*system[:3], system[3])


def tridiagonal_residual_linf(system, solution: Sequence[float]) -> float:
    lower, diagonal, upper, rhs = system
    residual = []
    for i, value in enumerate(solution):
        lhs = diagonal[i] * value
        if i:
            lhs += lower[i] * solution[i - 1]
        if i + 1 < len(solution):
            lhs += upper[i] * solution[i + 1]
        residual.append(abs(lhs - rhs[i]))
    return max(residual, default=0.0)


def boundary_flux_pair(surface_value: float, inner_value: float, grid: Grid, face_coefficient: float, transfer: float, environment_value: float) -> Tuple[float, float, float]:
    spacing = grid.nodes_m[-1] - grid.nodes_m[-2]
    # Outward-positive Fick/Fourier flux is -a * du/dr. The surface node is
    # the boundary value, so the one-sided discrete gradient is taken over
    # the last node spacing.
    internal_outward = -face_coefficient * (surface_value - inner_value) / spacing
    robin_outward = transfer * (surface_value - environment_value)
    return internal_outward, robin_outward, internal_outward - robin_outward
