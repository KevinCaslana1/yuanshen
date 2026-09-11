from pathlib import Path

from src.q2 import Q2RunConfig, run_q2


def test_checkpoint_restart_matches_continuous_run(tmp_path: Path) -> None:
    config = Q2RunConfig(end_time_s=8.0, time_step_s=0.25, n_intervals=20)
    continuous = run_q2(config, record_times=[4.0, 8.0])
    checkpoint = tmp_path / "q2_checkpoint.json"
    run_q2(config, record_times=[4.0], checkpoint_path=checkpoint, stop_time_s=4.0)
    restarted = run_q2(config, record_times=[8.0], restart_path=checkpoint)
    assert continuous.snapshot_at(8.0) == restarted.snapshot_at(8.0)
    assert checkpoint.exists()
