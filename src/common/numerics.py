"""Small deterministic numerical primitives shared by the modeling questions."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import List, Sequence, Tuple


@dataclass(frozen=True)
class RadialGrid:
    """Uniform nodal radial grid including the center and the surface."""

    radius_m: float
    n_intervals: int
    dr_m: float
    nodes_m: Tuple[float, ...]


@dataclass(frozen=True)
class NonuniformRadialGrid:
    """Nodal radial grid with explicitly stored nonuniform spacing."""

    radius_m: float
    n_intervals: int
    min_dr_m: float
    max_dr_m: float
    nodes_m: Tuple[float, ...]


def make_radial_grid(radius_m: float, n_intervals: int) -> RadialGrid:
    if radius_m <= 0.0:
        raise ValueError("radius_m must be positive")
    if n_intervals < 2:
        raise ValueError("n_intervals must be at least 2")
    dr_m = radius_m / float(n_intervals)
    nodes = tuple(index * dr_m for index in range(n_intervals + 1))
    return RadialGrid(radius_m, n_intervals, dr_m, nodes)


def make_boundary_clustered_grid(
    radius_m: float,
    n_intervals: int,
    cluster_power: float = 2.0,
    required_nodes_m: Sequence[float] = (),
) -> NonuniformRadialGrid:
    """Create a monotone grid clustered near the outer radius.

    The map ``r=R*(1-(1-x)**p)`` preserves the center and surface exactly;
    it is a numerical candidate, not a change to the Q1 physical geometry.
    """

    if radius_m <= 0.0:
        raise ValueError("radius_m must be positive")
    if n_intervals < 2:
        raise ValueError("n_intervals must be at least 2")
    if cluster_power <= 1.0:
        raise ValueError("cluster_power must be greater than 1")
    generated_nodes = tuple(
        radius_m * (1.0 - (1.0 - index / float(n_intervals)) ** cluster_power)
        for index in range(n_intervals + 1)
    )
    nodes = tuple(sorted(set(generated_nodes).union(float(value) for value in required_nodes_m)))
    if not nodes or abs(nodes[0]) > 1.0e-14 or abs(nodes[-1] - radius_m) > 1.0e-14:
        raise ValueError("required nodes must stay within the radial domain and include no outside endpoint")
    if any(value <= 0.0 or value >= radius_m for value in nodes[1:-1]):
        raise ValueError("required nodes must be strictly inside the radial domain")
    spacings = tuple(right - left for left, right in zip(nodes, nodes[1:]))
    return NonuniformRadialGrid(radius_m, len(nodes) - 1, min(spacings), max(spacings), nodes)


def thomas_solve(
    lower: Sequence[float],
    diagonal: Sequence[float],
    upper: Sequence[float],
    right_hand_side: Sequence[float],
) -> List[float]:
    """Solve a tridiagonal system without mutating its inputs."""

    n = len(diagonal)
    if n == 0:
        return []
    if len(lower) != n or len(upper) != n or len(right_hand_side) != n:
        raise ValueError("tridiagonal arrays must have the same length")

    lower_work = [float(value) for value in lower]
    diag_work = [float(value) for value in diagonal]
    upper_work = [float(value) for value in upper]
    rhs_work = [float(value) for value in right_hand_side]

    for values in (lower_work, diag_work, upper_work, rhs_work):
        if not all(isfinite(value) for value in values):
            raise ValueError("tridiagonal system contains non-finite values")

    pivot_tolerance = 1.0e-30
    for index in range(1, n):
        pivot = diag_work[index - 1]
        if abs(pivot) <= pivot_tolerance:
            raise ZeroDivisionError(f"near-zero Thomas pivot at row {index - 1}")
        factor = lower_work[index] / pivot
        diag_work[index] -= factor * upper_work[index - 1]
        rhs_work[index] -= factor * rhs_work[index - 1]

    if abs(diag_work[-1]) <= pivot_tolerance:
        raise ZeroDivisionError(f"near-zero Thomas pivot at row {n - 1}")

    solution = [0.0] * n
    solution[-1] = rhs_work[-1] / diag_work[-1]
    for index in range(n - 2, -1, -1):
        if abs(diag_work[index]) <= pivot_tolerance:
            raise ZeroDivisionError(f"near-zero Thomas pivot at row {index}")
        solution[index] = (rhs_work[index] - upper_work[index] * solution[index + 1]) / diag_work[index]
    return solution
