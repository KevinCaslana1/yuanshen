from pathlib import Path

import pytest

from src.q2 import Q2RunConfig, Q2NonConvergenceError, run_q2
from src.q2.solver import summarize_picard


ROOT = Path(__file__).resolve().parents[1]


def test_q2_smoke_is_finite_deterministic_and_records_diagnostics() -> None:
    config = Q2RunConfig(end_time_s=4.0, time_step_s=0.25, n_intervals=20)
    first = run_q2(config, record_times=[0.0, 2.0, 4.0])
    second = run_q2(config, record_times=[0.0, 2.0, 4.0])
    assert first.snapshot_at(4.0) == second.snapshot_at(4.0)
    assert len(first.diagnostics) == 16
    assert max(row.picard_iterations for row in first.diagnostics) <= config.picard_max_iterations
    assert all(abs(row.surface_heat_boundary_residual_w_m2) < 100.0 for row in first.diagnostics)
    assert all(abs(row.surface_moisture_boundary_residual_kg_m2_s) < 1e-5 for row in first.diagnostics)
    assert max(row.mass_step_residual for row in first.diagnostics) < 1e-6
    assert summarize_picard(first)["picard_max"] >= 1


def test_q2_streams_output_without_result2_workbook(tmp_path: Path) -> None:
    output = tmp_path / "q2.csv"
    diagnostics = tmp_path / "diagnostics.csv"
    result = run_q2(Q2RunConfig(end_time_s=2.0, time_step_s=0.5, candidate="B", n_intervals=20, scheme="be"), output_path=output, diagnostics_path=diagnostics)
    assert result.complete
    assert output.exists() and diagnostics.exists()
    assert "result2.xlsx" not in {path.name for path in tmp_path.iterdir()}
    assert output.read_text(encoding="utf-8").splitlines()[0].startswith("time_s,radius_cm")
    assert len(output.read_text(encoding="utf-8").splitlines()) == 1 + 3 * 21


def test_q2_nonconvergence_fails_closed() -> None:
    config = Q2RunConfig(end_time_s=1.0, time_step_s=1.0, n_intervals=8, picard_max_iterations=1, picard_tolerance=1e-20)
    with pytest.raises(Q2NonConvergenceError):
        run_q2(config)
