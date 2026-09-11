from __future__ import annotations

from pathlib import Path

from src.q1.config import DEFAULT_PARAMETERS, Q1RunConfig
from src.q1.inputs import BoundaryProvider
from src.q1.solver import run_m1_bdf2, run_m1_bdf2_sampled


def test_bdf2_early_startup_keeps_integer_output_time_aligned() -> None:
    root = Path(__file__).resolve().parents[1]
    boundary = BoundaryProvider.from_attachment1(root / "A题" / "附件" / "附件1.xlsx")
    config = Q1RunConfig(
        end_time_s=1.5,
        time_step_s=0.25,
        n_intervals=32,
        interpolation="linear",
        surface_boundary="robin",
    )
    result = run_m1_bdf2(
        config,
        boundary,
        DEFAULT_PARAMETERS,
        startup_step_s=0.125,
        startup_duration_s=1.0,
    )

    assert result.times_s[0] == 0.0
    assert any(abs(time_s - 1.0) < 1.0e-12 for time_s in result.times_s)
    assert abs(result.times_s[-1] - 1.5) < 1.0e-12
    assert len(result.times_s) > round(config.end_time_s / config.time_step_s) + 1
    assert all(value == value for row in result.moistures_kg_kg for value in row)


def test_sampled_bdf2_runs_on_clustered_grid_and_preserves_output_nodes() -> None:
    root = Path(__file__).resolve().parents[1]
    boundary = BoundaryProvider.from_attachment1(root / "A题" / "附件" / "附件1.xlsx")
    positions = tuple(index * 0.001 for index in range(21))
    config = Q1RunConfig(
        end_time_s=2.0,
        time_step_s=0.25,
        n_intervals=16,
        interpolation="linear",
        surface_boundary="robin",
    )
    result = run_m1_bdf2_sampled(
        config,
        boundary,
        DEFAULT_PARAMETERS,
        cluster_power=2.0,
        required_output_positions_m=positions,
        record_times_s=(1.0, 2.0),
    )

    assert result.grid.n_intervals > config.n_intervals
    assert result.stored_positions_m == positions
    assert result.times_s == (1.0, 2.0)
    assert result.internal_step_count == 8
    assert result.max_picard_iterations >= 1
    assert result.max_mass_balance_residual < 1.0e-10
