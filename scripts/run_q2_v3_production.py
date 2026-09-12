"""Run the authorized Q2 V3 production double run.

This runner is intentionally isolated from the historical Q2 production
directories.  It uses the certified V3 configuration, starts both formal
runs from the official initial condition, and writes no workbook.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q2 import Q2RunConfig, run_q2
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
    parse_diagnostics,
    project_relative,
    q1_integrity_snapshot,
    run_regression,
    sha256,
    strip_t0_and_validate,
    tree_sha256,
)


V3 = ROOT / "experiments" / "Q2_FREEZE_RUN_V3"
ACCURACY_BASIS = ROOT / "experiments" / "Q2_ACCURACY_REMEDIATION" / "accuracy_confirmation_v3.json"
PASSIVE_THRESHOLD = 0.15
FINAL_HORIZON = 228536
PREDECLARED_EVENT_BRACKET = (206935.0, 206935.25)
INTERNAL_TRANSITION_PROBES = (14400.25, 14400.50, 14400.75)
PAPER_TIMES = tuple(float(value) for value in PAPER_TIMES_S)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def git_status() -> str:
    return subprocess.check_output(["git", "status", "--short", "--branch"], cwd=ROOT, text=True).strip()


def source_commit_sha() -> str:
    return subprocess.check_output(["git", "log", "-1", "--format=%H", "--", "src/q2"], cwd=ROOT, text=True).strip()


def make_config() -> Q2RunConfig:
    return Q2RunConfig(
        end_time_s=float(FINAL_HORIZON),
        time_step_s=0.25,
        early_time_step_s=0.015625,
        early_time_end_s=5.0,
        candidate="A",
        n_intervals=320,
        cluster_power=3.0,
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


def assert_q1_unchanged(baseline: dict[str, Any], label: str) -> None:
    current = q1_integrity_snapshot()
    for key, value in baseline.items():
        if current.get(key) != value:
            raise RuntimeError(f"Q1 frozen integrity changed {label}: {key}: {value} -> {current.get(key)}")


def code_hash_record() -> dict[str, Any]:
    source_paths = [
        *sorted((ROOT / "src" / "q2").glob("*.py")),
        ROOT / "src" / "common" / "numerics.py",
        ROOT / "src" / "q1" / "model.py",
        ROOT / "scripts" / "run_q2_v3_production.py",
    ]
    files = {project_relative(path): sha256(path) for path in source_paths if path.is_file()}
    return {
        "recorded_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "expected_numerical_baseline_commit": "8504b2b32aceed013e82486504d512e0f53f9b0b",
        "numerical_source_commit_sha": source_commit_sha(),
        "head_commit_sha_before_run_1": git_sha(),
        "git_status_before_run_1": git_status(),
        "source_files_sha256": files,
        "source_tree_sha256": hashlib.sha256(json.dumps(sorted(files.items()), separators=(",", ":")).encode("utf-8")).hexdigest(),
        "production_lock": "src/q2, production configuration, environment logic, and sampler are frozen after this record",
    }


def accuracy_basis_record() -> dict[str, Any]:
    payload = json.loads(ACCURACY_BASIS.read_text(encoding="utf-8"))
    expected = payload["recommended_numerical_config"]
    return {
        "path": project_relative(ACCURACY_BASIS),
        "sha256": sha256(ACCURACY_BASIS),
        "status_at_freeze": payload["status"],
        "scope_decision": payload["scope_decision"],
        "gate": payload["gate"],
        "recommended_numerical_config": expected,
        "production_basis": "formal-output certification is the accuracy basis; V3 Run 1 is the sole production source",
    }


def write_transition_probes(path: Path, result: Any) -> None:
    fields = ["time_s", "radius_cm", "temperature_K", "temperature_C", "moisture_kg_kg"]
    grid_indices = {}
    for radius in (0.0, 1.0, 1.5, 1.9, 2.0):
        index = min(range(len(result.grid.nodes_m)), key=lambda i: abs(result.grid.nodes_m[i] * 100.0 - radius))
        if abs(result.grid.nodes_m[index] * 100.0 - radius) > 1.0e-10:
            raise RuntimeError(f"official radius {radius:g} cm is not an explicit grid node")
        grid_indices[radius] = index
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for time_s in (14400.0, *INTERNAL_TRANSITION_PROBES, 14401.0):
            temperature_k, moisture = result.snapshot_at(time_s)
            for radius in (0.0, 1.0, 1.5, 1.9, 2.0):
                index = grid_indices[radius]
                writer.writerow({
                    "time_s": repr(time_s),
                    "radius_cm": repr(radius),
                    "temperature_K": repr(float(temperature_k[index])),
                    "temperature_C": repr(float(temperature_k[index] - 273.15)),
                    "moisture_kg_kg": repr(float(moisture[index])),
                })


def run_one(name: str, config: Q2RunConfig, expected_bracket: tuple[float, float]) -> dict[str, Any]:
    run_dir = V3 / name
    run_dir.mkdir(parents=True, exist_ok=False)
    raw_path = run_dir / "official_samples_raw.csv"
    sampled_path = run_dir / "official_samples.csv"
    diagnostics_path = run_dir / "diagnostics_1s.csv"
    checkpoint_path = run_dir / "checkpoint_final.json"
    record_times = sorted(set(PAPER_TIMES + expected_bracket + (14400.0, *INTERNAL_TRANSITION_PROBES, 14401.0, float(FINAL_HORIZON))))
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
    if not result.complete:
        raise RuntimeError(f"{name} did not complete at the requested final horizon")
    actual_bracket = result.passive_event_bracket_s
    if actual_bracket != expected_bracket:
        raise RuntimeError(f"{name} passive event bracket changed: {actual_bracket} != {expected_bracket}")
    derived_horizon = int(math.ceil(actual_bracket[1]) + SAFETY_TAIL_S)
    if derived_horizon != FINAL_HORIZON:
        raise RuntimeError(f"{name} final horizon does not satisfy passive rule: {derived_horizon} != {FINAL_HORIZON}")
    sampled_shape = strip_t0_and_validate(raw_path, sampled_path, FINAL_HORIZON)
    diagnostics = parse_diagnostics(diagnostics_path, FINAL_HORIZON, config)
    grid = grid_for_config(config)
    raw_rows = sum(1 for _ in raw_path.open(encoding="utf-8"))
    payload = {
        "run": name,
        "status": "PASS_EXECUTION",
        "fresh_start": True,
        "initial_condition": "official uniform initial field at t=0; no checkpoint/field/data reuse",
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
            "early_policy": "BE startup then BDF2 with fine dt=.015625 s through exactly t=5 s",
            "five_second_transition": "the first dt=.25 s step after t=5 s is BE; BDF2 history is rebuilt exactly as certified",
            "environment_transition": "the first post-14400 s step is event-aligned BE; BDF2 resumes afterward",
            "coupling": "temperature-moisture Picard",
            "interface_mean": config.interface_mean,
        },
        "sampled_output": {"path": project_relative(sampled_path), **sampled_shape},
        "raw_output": {"path": project_relative(raw_path), "rows_including_header": raw_rows, "includes_internal_t0_layer": True},
        "diagnostics": {"path": project_relative(diagnostics_path), "summary": diagnostics},
        "transition_internal_probes": {"source": project_relative(ACCURACY_BASIS), "classification": "SUPPORTED_INTERNAL_TRANSITION_DIAGNOSTIC", "production_output_scope": "official integer-second lattice; non-integer probes remain in formal certification evidence"},
        "checkpoint": {"path": project_relative(checkpoint_path), "count": 1, "sha256": sha256(checkpoint_path)},
        "passive_event_bracket_s": list(actual_bracket),
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


def compare_canonical_numeric(left: Path, right: Path) -> dict[str, Any]:
    result = compare_csv_exact(left, right)
    result["comparison_scope"] = "all rows and all numeric fields, not only final state"
    return result


def lineage_payload(run1: dict[str, Any], run2: dict[str, Any], hashes: dict[str, Any]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for run, status in ((run1, "PRODUCTION_CANONICAL"), (run2, "DETERMINISM_REFERENCE")):
        run_dir = V3 / run["run"]
        for filename, role in (
            ("official_samples_raw.csv", "internal_source"),
            ("official_samples.csv", "official_sampled_source"),
            ("diagnostics_1s.csv", "diagnostics"),
            ("checkpoint_final.json", "checkpoint"),
            ("metrics.json", "run_metrics"),
        ):
            path = run_dir / filename
            entries.append({"path": project_relative(path), "status": status, "sha256": sha256(path), "run": run["run"], "role": role})
    return {
        "manifest_version": "Q2_V3_PRODUCTION_LINEAGE_V1",
        "formal_result_source": "experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv",
        "run_1_status": "PRODUCTION_CANONICAL",
        "run_2_status": "DETERMINISM_REFERENCE",
        "old_data_delivery_status": "NOT_DELIVERY_SOURCE",
        "entries": entries,
        "hashes": hashes,
        "fail_closed_policy": "candidate workbook and formal figures require the V3 Run 1 production-canonical path and verified SHA-256",
    }


def main() -> int:
    if V3.exists() and any(V3.iterdir()):
        raise SystemExit("Q2_FREEZE_RUN_V3 exists and is non-empty; refusing to reuse or overwrite an attempt")
    V3.mkdir(parents=True, exist_ok=True)
    config = make_config()
    baseline = q1_integrity_snapshot()
    if sha256(INPUT) != ATTACHMENT1_SHA256 or sha256(OFFICIAL_TEMPLATE) != EXPECTED_TEMPLATE_SHA256:
        raise SystemExit("V3 production blocked: official input/template hash mismatch")
    preflight = V3 / "preflight"
    preflight.mkdir()
    regression = run_regression(preflight)
    if regression["status"] != "PASS":
        raise SystemExit("V3 production blocked: regression tests failed")
    code_hashes = code_hash_record()
    if code_hashes["head_commit_sha_before_run_1"] != "8504b2b32aceed013e82486504d512e0f53f9b0b":
        raise SystemExit(f"V3 production blocked: unexpected HEAD baseline {code_hashes['head_commit_sha_before_run_1']}")
    write_json(V3 / "code_hashes.json", code_hashes)
    write_json(V3 / "accuracy_basis.json", accuracy_basis_record())
    write_json(V3 / "input_hashes.json", {
        "official_source_root": "A题",
        "official_input_sha256": sha256(INPUT),
        "official_result2_template_sha256": sha256(OFFICIAL_TEMPLATE),
        "q1_final_sha256": sha256(Q1_FINAL),
        "q1_freeze_reference_sha256": sha256(Q1_FREEZE_REFERENCE),
        "q1_figure_tree_sha256": baseline["q1_figure_tree_sha256"],
        "official_source_tree_sha256_before_runs": baseline["official_source_tree_sha256"],
    })
    write_json(V3 / "environment.json", {
        **environment_record(config),
        "frozen_transition_s": 14400.0,
        "within_attachment_rule": "piecewise linear for 0 <= t <= 14400 s",
        "post_transition_rule": "constant ENV-B values for t > 14400 s",
        "post_transition_temperature_c": 49.99525,
        "post_transition_moisture_kg_kg": 0.049988,
        "no_smoothing_or_tail_replacement": True,
    })
    write_json(V3 / "config.json", {
        "format": "Q2_PRODUCTION_CONFIG_V3",
        "status": "FROZEN_BEFORE_RUN_1",
        "code_commit_sha": code_hashes["numerical_source_commit_sha"],
        "head_commit_sha_before_run_1": code_hashes["head_commit_sha_before_run_1"],
        "accuracy_basis": project_relative(ACCURACY_BASIS),
        "validated_envelope_s": VALIDATED_ENVELOPE_S,
        "passive_event_threshold_kg_kg": PASSIVE_THRESHOLD,
        "predeclared_event_bracket_s": list(PREDECLARED_EVENT_BRACKET),
        "safety_tail_s": SAFETY_TAIL_S,
        "final_horizon_s": FINAL_HORIZON,
        "final_horizon_rule": "ceil(t_high)+21600 s, verified independently by Run 1 and Run 2",
        "run_1_and_run_2_must_start_from_t0": True,
        "official_sample_rule": "time_s=1..final_horizon, radius_cm=0.0..2.0 at 0.1 cm; t=0 retained only in raw internal output",
        "five_second_step_change_policy": "fine dt=.015625 s through exactly t=5 s; first dt=.25 s step is BE; certified BDF2 history handling is unchanged",
        "environment_transition_policy": "exact t=14400 s; first post-transition step is BE restart; BDF2 resumes afterward",
        "model": {"geometry": "1D fixed-radius cylindrical radial", "physics": ["rho(C)", "cp(C)", "k(C)", "D(C,T)"], "boundaries": ["center symmetry", "Robin heat", "Robin moisture"], "coupling": "coupled Picard", "forbidden": ["latent heat", "shrinkage", "Q4 moving boundary", "unapproved new physics"]},
        "numerical": {"candidate": "A", "n_intervals": 320, "cluster_power": 3.0, "interface_mean": "harmonic", "time_step_s": 0.25, "early_time_step_s": 0.015625, "early_time_end_s": 5.0, "first_step": "Backward Euler", "subsequent_steps": "BDF2", "step_size_change_restart": "Backward Euler", "environment_transition_restart": "Backward Euler", "picard_tolerance": 1.0e-8, "picard_max_iterations": 50, "picard_relaxation": 1.0},
        "environment": {"within_attachment1": "piecewise linear", "post_attachment": "constant ENV-B", "post_temperature_c": 49.99525, "post_moisture_kg_kg": 0.049988, "input_path": project_relative(INPUT)},
        "accuracy_criterion": {"temperature_C": 2.5e-5, "moisture_kg_kg": 2.5e-5, "scope": "formal-output lattice, not all internal states"},
        "checkpoint_policy": {"fresh_final_checkpoint_per_run": True, "checkpoint_count_per_run": 1, "restart_for_production": False},
        "config": config.as_dict(),
    })
    write_json(V3 / "preflight.json", {
        "status": "PASS",
        "code_hashes": code_hashes,
        "python": {"executable": sys.executable, "version": sys.version, "implementation": platform.python_implementation(), "platform": platform.platform()},
        "dependencies": {"openpyxl": __import__("openpyxl").__version__, "numpy": __import__("numpy").__version__, "matplotlib": __import__("matplotlib").__version__},
        "q1_integrity": baseline,
        "regression": regression,
        "production_source_rule": "V3 Run 1 only; old production, remediation, recovered, duplicate, and sensitivity artifacts are not delivery sources",
    })
    write_json(V3 / "lineage.json", {"manifest_version": "Q2_V3_PRODUCTION_LINEAGE_V1", "status": "PENDING_RUNS", "formal_result_source": None, "entries": []})
    write_json(V3 / "validation.json", {"status": "PENDING_PRODUCTION_RUNS", "fail_closed": True, "candidate_workbook_generated": False, "q1_regression": regression, "official_source_modified": False, "q1_frozen_assets_modified": False, "q3_q4_started": False})

    print(f"[Q2 V3] starting fresh Run 1: horizon={FINAL_HORIZON} s; n=320/cluster3; early dt=.015625 through 5 s; main dt=.25", flush=True)
    run1 = run_one("run_1", config, PREDECLARED_EVENT_BRACKET)
    assert_q1_unchanged(baseline, "after Run 1")
    print(f"[Q2 V3] Run 1 complete in {run1['runtime_s']:.1f} s; starting fresh Run 2", flush=True)
    run2 = run_one("run_2", config, PREDECLARED_EVENT_BRACKET)
    assert_q1_unchanged(baseline, "after Run 2")
    print(f"[Q2 V3] Run 2 complete in {run2['runtime_s']:.1f} s", flush=True)

    determinism = {
        "raw_output": compare_canonical_numeric(V3 / "run_1/official_samples_raw.csv", V3 / "run_2/official_samples_raw.csv"),
        "official_sampled_output": compare_canonical_numeric(V3 / "run_1/official_samples.csv", V3 / "run_2/official_samples.csv"),
        "diagnostics": compare_canonical_numeric(V3 / "run_1/diagnostics_1s.csv", V3 / "run_2/diagnostics_1s.csv"),
        "event_bracket_equal": run1["passive_event_bracket_s"] == run2["passive_event_bracket_s"],
        "final_horizon_equal": run1["final_horizon_s"] == run2["final_horizon_s"],
    }
    determinism["status"] = "PASS" if all(value is True or value.get("status") == "PASS" for value in determinism.values()) else "FAIL"
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
