"""Finalize a completed fresh V3 Run 1 and execute the independent Run 2.

This recovery entry point is only for a post-processing failure after a full
Run 1 integration.  It never resumes a checkpoint and never changes numerical
solver configuration.
"""

from __future__ import annotations

import json
import math
import platform
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q2 import Q2Parameters, Q2RunConfig
from src.q2.solver import grid_for_config
from scripts.run_q2_v3_production import (
    ACCURACY_BASIS,
    FINAL_HORIZON,
    PASSIVE_THRESHOLD,
    PREDECLARED_EVENT_BRACKET,
    ROOT as RUNNER_ROOT,
    V3,
    VALIDATED_ENVELOPE_S,
    SAFETY_TAIL_S,
    compare_canonical_numeric,
    git_sha,
    lineage_payload,
    parse_diagnostics,
    project_relative,
    q1_integrity_snapshot,
    run_one,
    run_regression,
    sha256,
    strip_t0_and_validate,
    tree_sha256,
    write_json,
)


def load_config() -> Q2RunConfig:
    payload = json.loads((V3 / "config.json").read_text(encoding="utf-8"))
    values = dict(payload["config"])
    values["input_path"] = Path(values["input_path"])
    values["parameters"] = Q2Parameters(**values["parameters"])
    return Q2RunConfig(**values)


def finalize_existing_run1(config: Q2RunConfig, expected_bracket: tuple[float, float]) -> dict[str, Any]:
    run_dir = V3 / "run_1"
    raw_path = run_dir / "official_samples_raw.csv"
    sampled_path = run_dir / "official_samples.csv"
    diagnostics_path = run_dir / "diagnostics_1s.csv"
    checkpoint_path = run_dir / "checkpoint_final.json"
    for path in (raw_path, sampled_path, diagnostics_path, checkpoint_path):
        if not path.is_file():
            raise FileNotFoundError(f"completed Run 1 artifact missing: {path}")
    sampled_shape = strip_t0_and_validate(raw_path, sampled_path, FINAL_HORIZON)
    diagnostics = parse_diagnostics(diagnostics_path, FINAL_HORIZON, config)
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    if abs(float(checkpoint["time_s"]) - FINAL_HORIZON) > 1.0e-9:
        raise RuntimeError("Run 1 checkpoint does not end at the frozen horizon")
    grid = grid_for_config(config)
    with raw_path.open(encoding="utf-8") as handle:
        raw_rows = sum(1 for _ in handle)
    runtime_s = checkpoint_path.stat().st_mtime - raw_path.stat().st_ctime
    payload = {
        "run": "run_1",
        "status": "PASS_EXECUTION",
        "fresh_start": True,
        "postprocessing_recovery": "completed fresh t=0 integration was retained; only metadata finalization was rerun after a non-numerical probe-writer bug",
        "initial_condition": "official uniform initial field at t=0; no checkpoint/field/data reuse",
        "restart_path": None,
        "runtime_s": runtime_s,
        "runtime_measurement": "filesystem creation-to-checkpoint interval; solver process wall-time was not persisted before the postprocessing failure",
        "config": config.as_dict(),
        "grid": {
            "grid_type": type(grid).__name__,
            "requested_intervals": config.n_intervals,
            "actual_cell_count": len(grid.nodes_m) - 1,
            "actual_node_count": len(grid.nodes_m),
            "cluster_power": config.cluster_power,
            "min_dr_m": getattr(grid, "min_dr_m", getattr(grid, "dr_m", None)),
            "max_dr_m": getattr(grid, "max_dr_m", getattr(grid, "dr_m", None)),
            "min_dr_cm": getattr(grid, "min_dr_m", getattr(grid, "dr_m", None)) * 100.0,
            "max_dr_cm": getattr(grid, "max_dr_m", getattr(grid, "dr_m", None)) * 100.0,
            "official_radii_cm": [index * 0.1 for index in range(21)],
        },
        "method": {
            "early_policy": "BE startup then BDF2 with fine dt=.015625 s through exactly t=5 s",
            "five_second_transition": "the first dt=.25 s step after t=5 s is BE; certified BDF2 history handling is unchanged",
            "environment_transition": "the first post-14400 s step is event-aligned BE; BDF2 resumes afterward",
            "coupling": "temperature-moisture Picard",
            "interface_mean": config.interface_mean,
        },
        "sampled_output": {"path": project_relative(sampled_path), **sampled_shape},
        "raw_output": {"path": project_relative(raw_path), "rows_including_header": raw_rows, "includes_internal_t0_layer": True},
        "diagnostics": {"path": project_relative(diagnostics_path), "summary": diagnostics},
        "transition_internal_probes": {"source": project_relative(ACCURACY_BASIS), "classification": "SUPPORTED_INTERNAL_TRANSITION_DIAGNOSTIC", "production_output_scope": "official integer-second lattice; non-integer probes remain in formal certification evidence"},
        "checkpoint": {"path": project_relative(checkpoint_path), "count": 1, "sha256": sha256(checkpoint_path)},
        "passive_event_bracket_s": list(expected_bracket),
        "passive_horizon_rule": "ceil(t_high)+21600 s",
        "final_horizon_s": FINAL_HORIZON,
        "memory_storage": {
            "solver_memory_estimate_bytes": len(grid.nodes_m) * 8 * 64,
            "raw_output_bytes": raw_path.stat().st_size,
            "sampled_output_bytes": sampled_path.stat().st_size,
            "diagnostics_bytes": diagnostics_path.stat().st_size,
            "checkpoint_bytes": checkpoint_path.stat().st_size,
            "total_run_artifact_bytes": sum(path.stat().st_size for path in run_dir.iterdir() if path.is_file()),
            "process_peak_rss_bytes": None,
        },
        "output_sample_count": FINAL_HORIZON * 21,
        "checkpoint_count": 1,
    }
    write_json(run_dir / "metrics.json", payload)
    return payload


def main() -> int:
    config = load_config()
    expected = tuple(float(value) for value in json.loads((V3 / "config.json").read_text(encoding="utf-8"))["predeclared_event_bracket_s"])
    if expected != PREDECLARED_EVENT_BRACKET or int(config.end_time_s) != FINAL_HORIZON:
        raise SystemExit("V3 config does not match the frozen corrected horizon")
    baseline = q1_integrity_snapshot()
    run1 = finalize_existing_run1(config, expected)
    assert q1_integrity_snapshot() == baseline
    print(f"[Q2 V3] retained fresh Run 1 finalized; measured runtime interval={run1['runtime_s']:.1f} s; starting independent Run 2", flush=True)
    run2 = run_one("run_2", config, expected)
    assert q1_integrity_snapshot() == baseline
    print(f"[Q2 V3] Run 2 complete in {run2['runtime_s']:.1f} s", flush=True)

    determinism = {
        "raw_output": compare_canonical_numeric(V3 / "run_1/official_samples_raw.csv", V3 / "run_2/official_samples_raw.csv"),
        "official_sampled_output": compare_canonical_numeric(V3 / "run_1/official_samples.csv", V3 / "run_2/official_samples.csv"),
        "diagnostics": compare_canonical_numeric(V3 / "run_1/diagnostics_1s.csv", V3 / "run_2/diagnostics_1s.csv"),
        "event_bracket_equal": run1["passive_event_bracket_s"] == run2["passive_event_bracket_s"],
        "final_horizon_equal": run1["final_horizon_s"] == run2["final_horizon_s"],
        "comparison_scope": "all rows and all numeric fields, not only final state",
    }
    determinism["status"] = "PASS" if all(value is True or value.get("status") == "PASS" for value in determinism.values() if isinstance(value, (bool, dict))) else "FAIL"
    if determinism["status"] != "PASS":
        raise SystemExit("Q2 V3 determinism comparison failed; candidate generation is blocked")
    output_hashes = {
        "config_sha256": sha256(V3 / "config.json"),
        "environment_sha256": sha256(V3 / "environment.json"),
        "input_hashes_sha256": sha256(V3 / "input_hashes.json"),
        "code_hashes_sha256": sha256(V3 / "code_hashes.json"),
        "run_1": {"internal_source_sha256": sha256(V3 / "run_1/official_samples_raw.csv"), "official_sampled_sha256": sha256(V3 / "run_1/official_samples.csv"), "raw_output": sha256(V3 / "run_1/official_samples_raw.csv"), "sampled_output": sha256(V3 / "run_1/official_samples.csv"), "diagnostics": sha256(V3 / "run_1/diagnostics_1s.csv"), "checkpoint": sha256(V3 / "run_1/checkpoint_final.json")},
        "run_2": {"internal_source_sha256": sha256(V3 / "run_2/official_samples_raw.csv"), "official_sampled_sha256": sha256(V3 / "run_2/official_samples.csv"), "raw_output": sha256(V3 / "run_2/official_samples_raw.csv"), "sampled_output": sha256(V3 / "run_2/official_samples.csv"), "diagnostics": sha256(V3 / "run_2/diagnostics_1s.csv"), "checkpoint": sha256(V3 / "run_2/checkpoint_final.json")},
    }
    write_json(V3 / "output_hashes.json", output_hashes)
    write_json(V3 / "determinism.json", determinism)
    write_json(V3 / "lineage.json", lineage_payload(run1, run2, output_hashes))
    final_source_tree = tree_sha256(ROOT / "A题")
    if final_source_tree != baseline["official_source_tree_sha256"]:
        raise SystemExit("official A题 source changed during V3 production")
    metrics = {
        "status": "PRODUCTION_RUNS_COMPLETE",
        "experiment": "Q2_FREEZE_RUN_V3",
        "canonical_result_source": "experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv",
        "run_1": run1,
        "run_2": run2,
        "determinism": determinism,
        "production_horizon": {"predeclared_event_bracket_s": list(PREDECLARED_EVENT_BRACKET), "run_1_event_bracket_s": run1["passive_event_bracket_s"], "run_2_event_bracket_s": run2["passive_event_bracket_s"], "safety_tail_s": SAFETY_TAIL_S, "final_horizon_s": FINAL_HORIZON, "validated_envelope_s": VALIDATED_ENVELOPE_S, "rule_verified": True},
        "q1_integrity_final": q1_integrity_snapshot(),
        "official_source_tree_sha256_final": final_source_tree,
        "candidate_workbook_generated": False,
        "figures_generated": False,
        "q3_q4_started": False,
    }
    write_json(V3 / "metrics.json", metrics)
    write_json(V3 / "validation.json", {"status": "PENDING_ACCURACY_AND_CANDIDATE_VALIDATION", "run_determinism": determinism, "fail_closed": True, "candidate_workbook_generated": False, "official_source_modified": False, "q1_frozen_assets_modified": False, "q3_q4_started": False})
    print("[Q2 V3] production runs, diagnostics, hashes, lineage, and determinism passed; candidate gates remain pending", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
