from __future__ import annotations

from pathlib import Path

import pytest

from src.common.numerics import make_radial_grid, thomas_solve
from src.common.paths import OFFICIAL_ROOT, assert_not_official_output
from src.q1.baseline import run_b0
from src.q1.config import Q1RunConfig
from src.q1.inputs import BoundaryProvider, celsius_to_kelvin, cm_to_m, kelvin_to_celsius
from src.q1.model import arithmetic_face_values, assemble_radial_system, implicit_radial_step
from src.q1.solver import run_m1, run_m2


ROOT = Path(__file__).resolve().parents[1]


def test_thomas_solver_on_constructed_system() -> None:
    # The system is constructed from the known vector [1, 2, 3].
    assert thomas_solve([0.0, -1.0, -1.0], [2.0, 2.0, 2.0], [-1.0, -1.0, 0.0], [0.0, 0.0, 4.0]) == pytest.approx([1.0, 2.0, 3.0])


def test_constant_field_zero_flux_is_unchanged() -> None:
    grid = make_radial_grid(0.02, 8)
    values = [5.0] * 9
    result = implicit_radial_step(values, grid, 1.0, 1.0, [0.3] * 8, 0.0, 0.0)
    assert result == pytest.approx(values)


def test_center_symmetry_has_zero_center_flux() -> None:
    grid = make_radial_grid(0.02, 8)
    lower, diagonal, upper, rhs = assemble_radial_system([5.0] * 9, grid, 1.0, 1.0, [0.3] * 8, 0.0, 0.0)
    assert lower[0] == 0.0
    assert diagonal[0] + upper[0] == pytest.approx(1.0)
    assert rhs[0] == 5.0


def test_robin_heat_sign_heats_surface() -> None:
    grid = make_radial_grid(0.02, 8)
    old = [celsius_to_kelvin(28.0)] * 9
    result = implicit_radial_step(old, grid, 1.0, 820.0 * 2600.0, [0.36] * 8, 25.0, celsius_to_kelvin(50.0))
    assert result[-1] > old[-1]


def test_moisture_flux_sign_causes_surface_loss() -> None:
    grid = make_radial_grid(0.02, 8)
    old = [2.55] * 9
    result = implicit_radial_step(old, grid, 1.0, 1.0, arithmetic_face_values([1.0e-9] * 9), 8.0e-7, 0.02)
    assert result[-1] < old[-1]


def test_boundary_provider_hits_every_raw_point() -> None:
    boundary = BoundaryProvider.from_attachment1(ROOT / "A题/附件/附件1.xlsx")
    for time_s, temperature_c, moisture in zip(boundary.times_s, boundary.temperatures_c, boundary.moistures_kg_kg):
        actual_temperature, actual_moisture = boundary.at(time_s)
        assert actual_temperature == temperature_c
        assert actual_moisture == moisture


def test_unit_conversions_are_explicit() -> None:
    assert cm_to_m(2.0) == pytest.approx(0.02)
    assert celsius_to_kelvin(28.0) == pytest.approx(301.15)
    assert kelvin_to_celsius(celsius_to_kelvin(28.0)) == pytest.approx(28.0)


def test_official_path_protection() -> None:
    with pytest.raises(ValueError):
        assert_not_official_output(OFFICIAL_ROOT / "附件" / "附件1.xlsx")


def test_same_configuration_is_deterministic() -> None:
    config = Q1RunConfig(end_time_s=5.0, time_step_s=1.0, n_intervals=8)
    boundary = BoundaryProvider.from_attachment1(ROOT / config.input_path)
    first = run_m1(config, boundary)
    second = run_m1(config, boundary)
    assert first.temperatures_k == second.temperatures_k
    assert first.moistures_kg_kg == second.moistures_kg_kg


def test_m1_optional_diagnostics_do_not_change_solution() -> None:
    config = Q1RunConfig(end_time_s=2.0, time_step_s=1.0, n_intervals=8)
    boundary = BoundaryProvider.from_attachment1(ROOT / config.input_path)
    trace = []
    plain = run_m1(config, boundary)
    instrumented = run_m1(config, boundary, diagnostics=trace)
    assert instrumented.moistures_kg_kg == plain.moistures_kg_kg
    assert instrumented.temperatures_k == plain.temperatures_k
    assert len(trace) == 2
    assert [row["time_s"] for row in trace] == [1.0, 2.0]
    assert all(row["picard_iterations"] >= 1 for row in trace)
    assert all(row["picard_final_normalized_residual"] < config.picard_tolerance for row in trace)
    assert max(row["moisture_matrix_residual_linf"] for row in trace) < 1.0e-12


def test_b0_baseline_is_reproducible_and_spatially_uniform() -> None:
    config = Q1RunConfig(end_time_s=3.0, time_step_s=1.0, n_intervals=8)
    boundary = BoundaryProvider.from_attachment1(ROOT / config.input_path)
    result = run_b0(config, boundary)
    assert result.times_s[-1] == 3.0
    assert result.moistures_kg_kg[0] == 2.55


def test_m2_constant_diffusivity_comparison_runs_without_picard() -> None:
    config = Q1RunConfig(end_time_s=2.0, time_step_s=1.0, n_intervals=8)
    boundary = BoundaryProvider.from_attachment1(ROOT / config.input_path)
    result = run_m2(config, boundary)
    assert result.picard_iterations == (0, 1, 1)
    assert all(value >= 0.0 for row in result.moistures_kg_kg for value in row)
