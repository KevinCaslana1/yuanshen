import pytest

from src.common.numerics import make_radial_grid
from src.q2.model import assemble_variable_radial_system, boundary_flux_pair, interface_values, solve_system


def test_interface_means_are_explicit_and_positive() -> None:
    assert interface_values([1.0, 3.0], "arithmetic") == [2.0]
    assert interface_values([1.0, 3.0], "harmonic") == pytest.approx([1.5])
    with pytest.raises(ValueError):
        interface_values([0.0, 1.0], "harmonic")


def test_constant_field_is_unchanged_without_robin_drive() -> None:
    grid = make_radial_grid(0.02, 8)
    system = assemble_variable_radial_system([5.0] * 9, grid, 1.0, [1.0] * 9, [0.3] * 8, 0.0, 0.0)
    assert solve_system(system) == pytest.approx([5.0] * 9)


def test_variable_coefficient_system_is_conservative_and_robin_pair_is_auditable() -> None:
    grid = make_radial_grid(0.02, 4)
    system = assemble_variable_radial_system([1.0] * 5, grid, 1.0, [2.0] * 5, [0.2, 0.3, 0.4, 0.5], 2.0, 0.0)
    solution = solve_system(system)
    assert all(value > 0 for value in solution)
    internal, robin, residual = boundary_flux_pair(solution[-1], solution[-2], grid, 0.5, 2.0, 0.0)
    assert internal == pytest.approx(-0.5 * (solution[-1] - solution[-2]) / grid.dr_m)
    assert robin == pytest.approx(2.0 * solution[-1])
    assert residual == pytest.approx(internal - robin)
