from pathlib import Path
import csv

from src.q2 import Q2RunConfig, run_q2


def test_checkpoint_restart_matches_continuous_run(tmp_path: Path) -> None:
    config = Q2RunConfig(end_time_s=8.0, time_step_s=0.25, n_intervals=20)
    continuous = run_q2(config, record_times=[4.0, 8.0])
    checkpoint = tmp_path / "q2_checkpoint.json"
    run_q2(config, record_times=[4.0], checkpoint_path=checkpoint, stop_time_s=4.0)
    restarted = run_q2(config, record_times=[8.0], restart_path=checkpoint)
    assert continuous.snapshot_at(8.0) == restarted.snapshot_at(8.0)
    assert checkpoint.exists()


def test_restart_reconciles_stale_append_only_outputs(tmp_path: Path) -> None:
    config = Q2RunConfig(end_time_s=8.0, time_step_s=0.25, n_intervals=20)
    checkpoint = tmp_path / "q2_checkpoint.json"
    output = tmp_path / "q2_samples.csv"
    diagnostics = tmp_path / "q2_diagnostics.csv"
    run_q2(config, checkpoint_path=checkpoint, output_path=output, diagnostics_path=diagnostics, stop_time_s=4.0)

    with output.open("a", newline="", encoding="utf-8") as handle:
        last = output.read_text(encoding="utf-8").splitlines()[-1].split(",")
        last[0] = "5.0"
        handle.write(",".join(last) + "\n")
    with diagnostics.open("a", newline="", encoding="utf-8") as handle:
        last = diagnostics.read_text(encoding="utf-8").splitlines()[-1].split(",")
        last[0] = "5.0"
        handle.write(",".join(last) + "\n")

    run_q2(config, restart_path=checkpoint, output_path=output, diagnostics_path=diagnostics)
    with output.open(newline="", encoding="utf-8") as handle:
        output_times = [float(row["time_s"]) for row in csv.DictReader(handle)]
    with diagnostics.open(newline="", encoding="utf-8") as handle:
        diagnostic_times = [float(row["time_s"]) for row in csv.DictReader(handle)]
    assert max(output_times) == 8.0
    assert len(output_times) == 9 * 21
    assert diagnostic_times[-1] == 8.0
