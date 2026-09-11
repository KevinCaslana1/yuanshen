from __future__ import annotations

import pytest

from src.common.numerics import make_boundary_clustered_grid, make_radial_grid
from src.q1.model import (
    assemble_bdf2_radial_system,
    assemble_nonuniform_radial_system,
    assemble_radial_system,
    radial_control_volume_factors,
)


def test_radial_control_volume_factors_include_center_and_surface_half_cells() -> None:
    grid = make_radial_grid(0.02, 4)
    dr = grid.dr_m
    expected = [
        dr * dr / 8.0,
        dr * dr,
        2.0 * dr * dr,
        3.0 * dr * dr,
        0.5 * (grid.radius_m**2 - (grid.radius_m - 0.5 * dr) ** 2),
    ]
    assert radial_control_volume_factors(grid) == pytest.approx(expected)


def test_robin_surface_row_matches_independent_half_cell_balance() -> None:
    grid = make_radial_grid(0.02, 4)
    dt = 0.5
    capacity = 4.0
    diffusivity = 0.3
    transfer = 2.0
    environment = 7.0
    lower, diagonal, upper, rhs = assemble_radial_system(
        [1.0] * 5,
        grid,
        dt,
        capacity,
        [diffusivity] * 4,
        transfer,
        environment,
    )

    dr = grid.dr_m
    inner_radius = grid.radius_m - 0.5 * dr
    surface_volume_factor = 0.5 * (grid.radius_m**2 - inner_radius**2)
    expected_inner = dt * inner_radius * diffusivity / (capacity * surface_volume_factor * dr)
    expected_external = dt * grid.radius_m * transfer / (capacity * surface_volume_factor)

    assert lower[-1] == pytest.approx(-expected_inner)
    assert diagonal[-1] == pytest.approx(1.0 + expected_inner + expected_external)
    assert upper[-1] == 0.0
    assert rhs[-1] == pytest.approx(1.0 + expected_external * environment)


def test_robin_surface_flux_has_outward_positive_sign() -> None:
    grid = make_radial_grid(0.02, 4)
    _, _, _, rhs = assemble_radial_system(
        [2.0] * 5,
        grid,
        1.0,
        1.0,
        [1.0] * 4,
        0.5,
        1.0,
    )
    # The environment contribution is positive on the RHS, while the larger
    # diagonal coefficient makes the solved surface value move downward.
    assert rhs[-1] > 2.0


def test_dirichlet_surface_row_is_an_explicit_boundary_value() -> None:
    grid = make_radial_grid(0.02, 4)
    lower, diagonal, upper, rhs = assemble_radial_system(
        [2.0] * 5,
        grid,
        1.0,
        1.0,
        [1.0] * 4,
        0.5,
        9.0,
        surface_boundary="dirichlet",
    )
    assert lower[-1] == 0.0
    assert diagonal[-1] == 1.0
    assert upper[-1] == 0.0
    assert rhs[-1] == 9.0


def test_bdf2_robin_row_scales_operator_and_uses_two_history_levels() -> None:
    grid = make_radial_grid(0.02, 4)
    old = [2.0] * 5
    previous = [1.0] * 5
    be = assemble_radial_system(old, grid, 0.5, 4.0, [0.3] * 4, 2.0, 7.0)
    bdf2 = assemble_bdf2_radial_system(previous_values=previous, old_values=old, grid=grid, dt_s=0.5, capacity=4.0, face_diffusivities=[0.3] * 4, surface_transfer=2.0, environment_value=7.0)
    assert bdf2[0][-1] == pytest.approx((2.0 / 3.0) * be[0][-1])
    assert bdf2[1][-1] == pytest.approx(1.0 + (2.0 / 3.0) * (be[1][-1] - 1.0))
    assert bdf2[2][-1] == 0.0
    expected_rhs = 4.0 / 3.0 * old[-1] - 1.0 / 3.0 * previous[-1] + (2.0 / 3.0) * (be[3][-1] - old[-1])
    assert bdf2[3][-1] == pytest.approx(expected_rhs)


def test_nonuniform_grid_preserves_surface_robin_balance() -> None:
    grid = make_boundary_clustered_grid(0.02, 8, cluster_power=2.0)
    old = [1.0] * 9
    dt = 0.25
    capacity = 3.0
    diffusivity = 0.4
    transfer = 1.5
    environment = 5.0
    lower, diagonal, upper, rhs = assemble_nonuniform_radial_system(
        old,
        grid,
        dt,
        capacity,
        [diffusivity] * 8,
        transfer,
        environment,
    )
    faces = [0.5 * (left + right) for left, right in zip(grid.nodes_m, grid.nodes_m[1:])]
    volume = 0.5 * (grid.radius_m**2 - faces[-1] ** 2)
    inner = dt * faces[-1] * diffusivity / (capacity * volume * (grid.nodes_m[-1] - grid.nodes_m[-2]))
    external = dt * grid.radius_m * transfer / (capacity * volume)
    assert lower[-1] == pytest.approx(-inner)
    assert diagonal[-1] == pytest.approx(1.0 + inner + external)
    assert upper[-1] == 0.0
    assert rhs[-1] == pytest.approx(1.0 + external * environment)


def test_boundary_clustered_grid_preserves_required_output_nodes() -> None:
    required = (0.0, 0.001, 0.019, 0.02)
    grid = make_boundary_clustered_grid(0.02, 16, cluster_power=2.0, required_nodes_m=required)
    assert grid.nodes_m[0] == pytest.approx(0.0)
    assert grid.nodes_m[-1] == pytest.approx(0.02)
    for position in required:
        assert any(node == pytest.approx(position) for node in grid.nodes_m)
    assert all(right > left for left, right in zip(grid.nodes_m, grid.nodes_m[1:]))
