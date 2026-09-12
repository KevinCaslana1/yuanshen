"""Run the authorized Q2 V2 production double run in a new directory.

This runner is fail-closed: it never reuses or overwrites Q2_FREEZE_RUN and
never creates result2.xlsx.  Accuracy confirmation and deliverable generation
are separate later gates.
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q2 import Q2RunConfig, Q2Parameters, run_q2
from src.q2.solver import grid_for_config
from scripts.run_q2_production_freeze import (
    ATTACHMENT1_SHA256,
    EXPECTED_TEMPLATE_SHA256,
    INPUT,
    OFFICIAL_TEMPLATE,
    PAPER_RADII_CM,
    PAPER_TIMES_S,
    Q1_FINAL,
    Q1_FINAL_SHA256,
    Q1_FREEZE_REFERENCE,
    Q1_FREEZE_REFERENCE_SHA256,
    Q1_FIGURES,
    SAFETY_TAIL_S,
    VALIDATED_ENVELOPE_S,
    compare_csv_exact,
    environment_record,
    git_sha,
    git_status,
    parse_diagnostics,
    project_relative,
    q1_integrity_snapshot,
    run_regression,
    sha256,
    strip_t0_and_validate,
    tree_sha256,
)


V2 = ROOT / "experiments" / "Q2_FREEZE_RUN_V2"
EVENT_BRACKET = (207034.5, 207034.75)
FINAL_HORIZON = int(EVENT_BRACKET[1] + SAFETY_TAIL_S + 0.999999999)
PASSIVE_THRESHOLD = 0.15


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_config() -> Q2RunConfig:
    return Q2RunConfig(
        end_time_s=float(FINAL_HORIZON),
        time_step_s=0.25,
        early_time_step_s=0.015625,
        early_time_end_s=2.0,
        candidate="A",
        n_intervals=640,
        cluster_power=2.0,
        scheme="bdf2",
        interface_mean="harmonic",
        interpolation="linear",
        post_attachment_mode="constant",
        post_temperature_c=49.99525,
        post_moisture_kg_kg=0.049988,
        output_interval_s=1.0,
        picard_tolerance=1.0e-8,
        picard_max_iterations=50,
        picard_relaxation=1.0,
        reset_bdf2_at_environment_transition=True,
        input_path=Path("A题/附件/附件1.xlsx"),
    )


def run_one(name: str, config: Q2RunConfig) -> dict[str, Any]:
    run_dir = V2 / name
    run_dir.mkdir(parents=True, exist_ok=False)
    raw_path = run_dir / "official_samples_raw.csv"
    diagnostics_path = run_dir / "diagnostics_1s.csv"
    checkpoint_path = run_dir / "checkpoint_final.json"
    record_times = sorted(set(PAPER_TIMES_S + EVENT_BRACKET + (float(FINAL_HORIZON),)))
    started = time.perf_counter()
    result = run_q2(
        config,
        record_times=record_times,
        output_path=raw_path,
        diagnostics_path=diagnostics_path,
        checkpoint_path=checkpoint_path,
        passive_event_threshold_kg_kg=PASSIVE_THRESHOLD,
        diagnostics_interval_s=1.0,
    )
    runtime = time.perf_counter() - started
    sampled_path = run_dir / "official_samples.csv"
    sampled_shape = strip_t0_and_validate(raw_path, sampled_path, FINAL_HORIZON)
    diagnostics = parse_diagnostics(diagnostics_path, FINAL_HORIZON, config)
    grid = grid_for_config(config)
    if not result.complete:
        raise RuntimeError(f"{name} did not complete at the requested final horizon")
    if result.passive_event_bracket_s != EVENT_BRACKET:
        raise RuntimeError(f"{name} event bracket changed: {result.passive_event_bracket_s} != {EVENT_BRACKET}")
    return {
        "run": name,
        "status": "PASS_EXECUTION_ONLY",
        "fresh_start": True,
        "restart_path": None,
        "runtime_s": runtime,
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
            "early_time_step_s": config.early_time_step_s,
            "early_time_end_s": config.early_time_end_s,
            "early_phase": "BE first step, then BDF2",
            "step_size_change": "BE first step after t=2 s, then BDF2",
            "environment_transition": "BE first step after exactly t=14400 s, then BDF2",
            "coupling": "temperature-moisture Picard",
            "interface_mean": config.interface_mean,
        },
        "sampled_output": {"path": project_relative(sampled_path), **sampled_shape},
        "raw_output": {"path": project_relative(raw_path), "rows_including_header": sum(1 for _ in raw_path.open(encoding="utf-8"))},
        "diagnostics": {"path": project_relative(diagnostics_path), "summary": diagnostics},
        "checkpoint": {"path": project_relative(checkpoint_path), "count": 1, "sha256": sha256(checkpoint_path)},
        "passive_event_bracket_s": list(EVENT_BRACKET),
        "final_horizon_s": FINAL_HORIZON,
        "memory_estimate_bytes": len(grid.nodes_m) * 8 * 64,
        "output_bytes": {"raw": raw_path.stat().st_size, "sampled": sampled_path.stat().st_size, "diagnostics": diagnostics_path.stat().st_size},
    }


def main() -> int:
    if V2.exists() and any(V2.iterdir()):
        raise SystemExit("Q2_FREEZE_RUN_V2 exists and is non-empty; refusing to reuse an attempt")
    V2.mkdir(parents=True, exist_ok=True)
    config = make_config()
    baseline = q1_integrity_snapshot()
    preflight_dir = V2 / "preflight"
    preflight_dir.mkdir()
    regression = run_regression(preflight_dir)
    if regression["status"] != "PASS":
        raise SystemExit("V2 production blocked: regression tests failed")
    write_json(V2 / "input_hashes.json", {
        "official_source_root": "A题",
        "official_input_sha256": sha256(INPUT),
        "official_result2_template_sha256": sha256(OFFICIAL_TEMPLATE),
        "q1_final_sha256": sha256(Q1_FINAL),
        "q1_freeze_reference_sha256": sha256(Q1_FREEZE_REFERENCE),
        "q1_figure_tree_sha256": baseline["q1_figure_tree_sha256"],
        "official_source_tree_sha256": baseline["official_source_tree_sha256"],
    })
    write_json(V2 / "environment.json", environment_record(config))
    grid = grid_for_config(config)
    write_json(V2 / "config.json", {
        "status": "V2_NUMERICAL_REMEDIATION_CANDIDATE_PENDING_ACCURACY",
        "code_commit": git_sha(),
        "validated_envelope_s": VALIDATED_ENVELOPE_S,
        "passive_event_threshold_kg_kg": PASSIVE_THRESHOLD,
        "safety_tail_s": SAFETY_TAIL_S,
        "event_bracket_s": list(EVENT_BRACKET),
        "final_horizon_s": FINAL_HORIZON,
        "run_1_and_run_2_must_start_from_t0": True,
        "official_sample_rule": "time_s=1..final_horizon, radius_cm=0.0..2.0 at 0.1 cm; t=0 retained only in raw internal output",
        "model": {"geometry": "1D fixed-radius cylindrical radial", "physics": ["rho(C)", "cp(C)", "k(C)", "D(C,T)"], "boundaries": ["center symmetry", "Robin heat", "Robin moisture"], "coupling": "coupled Picard", "forbidden": ["latent heat", "shrinkage", "Q4 moving boundary", "unapproved new physics"]},
        "numerical": {"candidate": "A", "grid": {"type": type(grid).__name__, "requested_intervals": config.n_intervals, "actual_cell_count": len(grid.nodes_m) - 1, "actual_node_count": len(grid.nodes_m), "cluster_power": config.cluster_power, "min_dr_m": getattr(grid, "min_dr_m", getattr(grid, "dr_m", None)), "max_dr_m": getattr(grid, "max_dr_m", getattr(grid, "dr_m", None)), "min_dr_cm": getattr(grid, "min_dr_m", getattr(grid, "dr_m", None)) * 100.0, "max_dr_cm": getattr(grid, "max_dr_m", getattr(grid, "dr_m", None)) * 100.0}, "time_step_s": config.time_step_s, "early_time_step_s": config.early_time_step_s, "early_time_end_s": config.early_time_end_s, "first_step": "Backward Euler", "step_size_change_restart": "Backward Euler", "environment_transition_restart": "Backward Euler", "subsequent_steps": "BDF2", "interface_mean": config.interface_mean, "picard_tolerance": config.picard_tolerance, "picard_max_iterations": config.picard_max_iterations, "picard_relaxation": config.picard_relaxation},
        "environment": {"within_attachment1": "piecewise linear", "post_attachment": "constant", "post_temperature_c": config.post_temperature_c, "post_moisture_kg_kg": config.post_moisture_kg_kg, "input_path": project_relative(INPUT)},
        "accuracy_criterion": {"temperature_estimated_uncertainty_c": 2.5e-5, "moisture_estimated_uncertainty_kg_kg": 2.5e-5, "official_requirement": False},
        "checkpoint_policy": {"fresh_final_checkpoint_per_run": True, "checkpoint_count_per_run": 1, "restart_for_production": False},
        "config": config.as_dict(),
    })
    write_json(V2 / "preflight.json", {"status": "PASS", "code_commit": git_sha(), "git_status": git_status(), "python": {"executable": sys.executable, "version": sys.version, "implementation": platform.python_implementation(), "platform": platform.platform()}, "dependencies": {"openpyxl": __import__("openpyxl").__version__, "numpy": __import__("numpy").__version__, "matplotlib": __import__("matplotlib").__version__}, "q1_integrity": baseline, "regression": regression, "production_source_rule": "Q2_FREEZE_RUN_V2 only after accuracy confirmation; old Q2_FREEZE_RUN is provenance-only"})

    print(f"[Q2 V2] starting fresh Run 1 to {FINAL_HORIZON} s; n=640, early dt=.015625 through 2 s, main dt=.25", flush=True)
    run1 = run_one("run_1", config)
    write_json(V2 / "run_1_execution.json", run1)
    if q1_integrity_snapshot() != baseline:
        raise RuntimeError("Q1 integrity changed after V2 Run 1")
    print(f"[Q2 V2] Run 1 complete in {run1['runtime_s']:.1f} s; starting fresh Run 2", flush=True)
    run2 = run_one("run_2", config)
    write_json(V2 / "run_2_execution.json", run2)
    if q1_integrity_snapshot() != baseline:
        raise RuntimeError("Q1 integrity changed after V2 Run 2")
    compare = {
        "raw_output": compare_csv_exact(V2 / "run_1/official_samples_raw.csv", V2 / "run_2/official_samples_raw.csv"),
        "sampled_output": compare_csv_exact(V2 / "run_1/official_samples.csv", V2 / "run_2/official_samples.csv"),
        "diagnostics": compare_csv_exact(V2 / "run_1/diagnostics_1s.csv", V2 / "run_2/diagnostics_1s.csv"),
        "event_bracket_equal": run1["passive_event_bracket_s"] == run2["passive_event_bracket_s"],
        "final_horizon_equal": run1["final_horizon_s"] == run2["final_horizon_s"],
    }
    compare["status"] = "PASS" if all(value is True or value.get("status") == "PASS" for value in compare.values()) else "FAIL"
    if compare["status"] != "PASS":
        raise SystemExit("V2 production determinism comparison failed")
    output_hashes = {
        "config_sha256": sha256(V2 / "config.json"),
        "environment_sha256": sha256(V2 / "environment.json"),
        "run_1": {name: sha256(V2 / "run_1" / filename) for name, filename in {"raw_output": "official_samples_raw.csv", "sampled_output": "official_samples.csv", "diagnostics": "diagnostics_1s.csv", "checkpoint": "checkpoint_final.json"}.items()},
        "run_2": {name: sha256(V2 / "run_2" / filename) for name, filename in {"raw_output": "official_samples_raw.csv", "sampled_output": "official_samples.csv", "diagnostics": "diagnostics_1s.csv", "checkpoint": "checkpoint_final.json"}.items()},
    }
    write_json(V2 / "output_hashes.json", output_hashes)
    write_json(V2 / "determinism.json", compare)
    write_json(V2 / "lineage.json", {"manifest_version": "Q2_PRODUCTION_LINEAGE_V2", "formal_result_source": None, "attempt_status": "PENDING_ACCURACY_CONFIRMATION", "delivery_status": "NOT_DELIVERY_SOURCE_UNTIL_ACCURACY_PASS", "run_1_status": "CANDIDATE_PENDING_ACCURACY", "run_2_status": "DETERMINISM_REFERENCE_PENDING_ACCURACY", "failed_baseline": "experiments/Q2_FREEZE_RUN", "entries": [{"path": project_relative(V2 / "run_1" / filename), "status": "CANDIDATE_PENDING_ACCURACY", "sha256": sha256(V2 / "run_1" / filename), "run": "run_1", "role": role} for role, filename in (("raw_output", "official_samples_raw.csv"), ("sampled_output", "official_samples.csv"), ("diagnostics", "diagnostics_1s.csv"), ("checkpoint", "checkpoint_final.json"))] + [{"path": project_relative(V2 / "run_2" / filename), "status": "DETERMINISM_REFERENCE_PENDING_ACCURACY", "sha256": sha256(V2 / "run_2" / filename), "run": "run_2", "role": role} for role, filename in (("raw_output", "official_samples_raw.csv"), ("sampled_output", "official_samples.csv"), ("diagnostics", "diagnostics_1s.csv"), ("checkpoint", "checkpoint_final.json"))], "fail_closed_policy": "formal loaders require an accuracy-confirmed production status and verified SHA-256"})
    write_json(V2 / "metrics.json", {"status": "PENDING_ACCURACY_CONFIRMATION", "experiment": "Q2_FREEZE_RUN_V2", "canonical_result_source": None, "delivery_status": "NOT_DELIVERY_SOURCE_UNTIL_ACCURACY_PASS", "run_1": run1, "run_2": run2, "determinism": compare, "production_horizon": {"passive_event_bracket_s": list(EVENT_BRACKET), "safety_tail_s": SAFETY_TAIL_S, "final_horizon_s": FINAL_HORIZON, "validated_envelope_s": VALIDATED_ENVELOPE_S}, "q1_integrity_final": q1_integrity_snapshot(), "official_source_tree_sha256_final": tree_sha256(ROOT / "A题"), "candidate_workbook_generated": False})
    write_json(V2 / "validation.json", {"status": "PENDING_ACCURACY_CONFIRMATION", "run_determinism": compare, "fail_closed": True, "candidate_workbook_generated": False, "official_source_modified": False, "q1_frozen_assets_modified": False, "q3_q4_started": False})
    print("[Q2 V2] execution and determinism PASS; accuracy confirmation remains mandatory", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
