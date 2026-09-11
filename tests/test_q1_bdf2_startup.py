from __future__ import annotations

from pathlib import Path

from src.q1.config import DEFAULT_PARAMETERS, Q1RunConfig
from src.q1.inputs import BoundaryProvider
from src.q1.solver import run_m1_bdf2


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
