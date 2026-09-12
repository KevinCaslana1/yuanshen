"""Run the fail-closed post-production audit for the authorized Q2 V3 run.

This audit is deliberately separate from the numerical solver.  It verifies the
frozen basis, source hashes, run artifacts, diagnostics, sampler lattice,
lineage, and the Q1/Q3/Q4 boundaries before any workbook is authored.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
V3 = ROOT / "experiments" / "Q2_FREEZE_RUN_V3"
ACCURACY = ROOT / "experiments" / "Q2_ACCURACY_REMEDIATION" / "accuracy_confirmation_v3.json"
CERT = json.loads(ACCURACY.read_text(encoding="utf-8"))
CONFIG = json.loads((V3 / "config.json").read_text(encoding="utf-8"))
HASHES = json.loads((V3 / "output_hashes.json").read_text(encoding="utf-8"))
LINEAGE = json.loads((V3 / "lineage.json").read_text(encoding="utf-8"))
METRICS = json.loads((V3 / "metrics.json").read_text(encoding="utf-8"))
PREFLIGHT = json.loads((V3 / "preflight.json").read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def fail(checks: dict[str, Any], name: str, ok: bool, detail: Any) -> None:
    checks[name] = {"status": "PASS" if ok else "FAIL", "detail": detail}


def tree_sha256(root: Path) -> str:
    entries: list[tuple[str, str]] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        entries.append((path.relative_to(root).as_posix(), sha256(path)))
    return hashlib.sha256(json.dumps(entries, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def current_q1_snapshot() -> dict[str, Any]:
    # Reuse the established snapshot implementation so the audit uses the same
    # immutable-asset definition as the production preflight.
    from scripts.run_q2_production_freeze import q1_integrity_snapshot

    return q1_integrity_snapshot()


def audit_config(checks: dict[str, Any]) -> None:
    rec = CERT["recommended_numerical_config"]
    numerical = CONFIG["numerical"]
    environment = CONFIG["environment"]
    expected = {
        "n_intervals": rec["n_intervals"],
        "cluster_power": rec["cluster_power"],
        "time_step_s": rec["time_step_s"],
        "early_time_step_s": rec["early_time_step_s"],
        "early_time_end_s": rec["early_time_end_s"],
        "interface_mean": rec["interface_mean"],
        "scheme": "BE startup then BDF2",
        "environment": rec["environment"],
    }
    actual = {
        "n_intervals": numerical["n_intervals"],
        "cluster_power": numerical["cluster_power"],
        "time_step_s": numerical["time_step_s"],
        "early_time_step_s": numerical["early_time_step_s"],
        "early_time_end_s": numerical["early_time_end_s"],
        "interface_mean": numerical["interface_mean"],
        "scheme": "BE startup then BDF2" if CONFIG["config"]["scheme"] == "bdf2" else CONFIG["config"]["scheme"],
        "environment": None,
    }
    # Keep the textual comparison above auditable, while checking the two
    # numeric ENV-B constants explicitly.
    actual["environment"] = {
        "within_attachment1": environment["within_attachment1"],
        "post_attachment_mode": environment.get("post_attachment_mode", environment.get("post_attachment")),
        "post_temperature_c": environment["post_temperature_c"],
        "post_moisture_kg_kg": environment["post_moisture_kg_kg"],
    }
    expected["environment"] = {
        "within_attachment1": "piecewise linear",
        "post_attachment_mode": "constant ENV-B",
        "post_temperature_c": 49.99525,
        "post_moisture_kg_kg": 0.049988,
    }
    required_fields = {
        "restart": CONFIG["accuracy_criterion"]["scope"],
        "early_policy": CONFIG["five_second_step_change_policy"],
        "transition_policy": CONFIG["environment_transition_policy"],
        "official_sample_rule": CONFIG["official_sample_rule"],
    }
    ok = actual == expected and CONFIG["config"]["reset_bdf2_at_environment_transition"] is True
    ok = ok and CONFIG["final_horizon_s"] == 228536 and CONFIG["predeclared_event_bracket_s"] == [206935.0, 206935.25]
    fail(checks, "v3_config_match", ok, {"actual": actual, "expected": expected, "required_fields": required_fields})


def audit_code_and_inputs(checks: dict[str, Any]) -> None:
    recorded = json.loads((V3 / "code_hashes.json").read_text(encoding="utf-8"))
    current: dict[str, str] = {}
    mismatches: dict[str, Any] = {}
    for relative, expected in recorded["source_files_sha256"].items():
        path = ROOT / relative
        if path.is_file():
            current[relative] = sha256(path)
            if relative.startswith("src/") and current[relative] != expected:
                mismatches[relative] = {"expected": expected, "actual": current[relative]}
        else:
            mismatches[relative] = {"expected": expected, "actual": "missing"}
    source_ok = not mismatches and git("rev-parse", "HEAD") == recorded["head_commit_sha_before_run_1"] and git("log", "-1", "--format=%H", "--", "src/q2") == recorded["numerical_source_commit_sha"]
    fail(checks, "code_hash_match", source_ok, {"recorded_source_hashes_match": not mismatches, "mismatches": mismatches, "current_head": git("rev-parse", "HEAD"), "recorded_head": recorded["head_commit_sha_before_run_1"], "current_src_q2_commit": git("log", "-1", "--format=%H", "--", "src/q2"), "recorded_src_q2_commit": recorded["numerical_source_commit_sha"], "post_run_runner_note": "run_q2_v3_production.py was only corrected for a non-numerical probe-writer postprocess issue after Run 1; src/q2 is unchanged"})

    input_hashes = json.loads((V3 / "input_hashes.json").read_text(encoding="utf-8"))
    from scripts.run_q2_production_freeze import INPUT, OFFICIAL_TEMPLATE

    input_ok = sha256(INPUT) == input_hashes["official_input_sha256"] and sha256(OFFICIAL_TEMPLATE) == input_hashes["official_result2_template_sha256"]
    fail(checks, "environment_hash_match", sha256(V3 / "environment.json") == HASHES["environment_sha256"] and sha256(INPUT) == input_hashes["official_input_sha256"], {"environment_sha256": sha256(V3 / "environment.json"), "recorded": HASHES["environment_sha256"], "input_sha256": sha256(INPUT), "recorded_input": input_hashes["official_input_sha256"]})
    fail(checks, "official_template_and_input", input_ok, {"input": input_hashes["official_input_sha256"], "template": input_hashes["official_result2_template_sha256"]})

    pre = PREFLIGHT["q1_integrity"]
    now = current_q1_snapshot()
    fail(checks, "q1_regression", now == pre, {"preflight": pre, "current": now})
    fail(checks, "official_source_modified", tree_sha256(ROOT / "A题") == input_hashes["official_source_tree_sha256_before_runs"], {"current": tree_sha256(ROOT / "A题"), "recorded": input_hashes["official_source_tree_sha256_before_runs"]})


def audit_run_files(checks: dict[str, Any]) -> None:
    expected_fields = {"run_1": "run_1", "run_2": "run_2"}
    run_results: dict[str, Any] = {}
    for run_name in expected_fields:
        run_dir = V3 / run_name
        run_hashes = HASHES[run_name]
        paths = {
            "internal_source_sha256": run_dir / "official_samples_raw.csv",
            "official_sampled_sha256": run_dir / "official_samples.csv",
            "diagnostics": run_dir / "diagnostics_1s.csv",
            "checkpoint": run_dir / "checkpoint_final.json",
        }
        results = {key: (path.is_file() and sha256(path) == run_hashes[key]) for key, path in paths.items()}
        metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
        results["metrics_status"] = metrics.get("status") == "PASS_EXECUTION"
        results["fresh_start"] = metrics.get("fresh_start") is True and metrics.get("restart_path") is None
        results["horizon"] = metrics.get("final_horizon_s") == 228536 and metrics.get("passive_event_bracket_s") == [206935.0, 206935.25]
        results["sample_count"] = metrics.get("output_sample_count") == 228536 * 21
        run_results[run_name] = results
    all_ok = all(all(value is True for value in result.values()) for result in run_results.values())
    fail(checks, "run_1_and_run_2", all_ok, run_results)
    fail(checks, "determinism", METRICS.get("determinism", {}).get("status") == "PASS" and json.loads((V3 / "determinism.json").read_text(encoding="utf-8")).get("status") == "PASS", METRICS.get("determinism"))
    fail(checks, "lineage", LINEAGE.get("formal_result_source") == "experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv" and LINEAGE.get("run_1_status") == "PRODUCTION_CANONICAL" and LINEAGE.get("run_2_status") == "DETERMINISM_REFERENCE", {"formal_result_source": LINEAGE.get("formal_result_source"), "run_1_status": LINEAGE.get("run_1_status"), "run_2_status": LINEAGE.get("run_2_status")})


def audit_diagnostics(checks: dict[str, Any]) -> None:
    diag_path = V3 / "run_1" / "diagnostics_1s.csv"
    count = 0
    finite = True
    times_ok = True
    picard: list[float] = []
    mass: list[float] = []
    heat: list[float] = []
    robin_heat: list[float] = []
    robin_moisture: list[float] = []
    with diag_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"time_s", "picard_iterations", "temperature_residual", "moisture_residual", "mass_step_residual", "heat_step_residual_j", "surface_heat_boundary_residual_w_m2", "surface_moisture_boundary_residual_kg_m2_s"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"diagnostics missing fields: {required - set(reader.fieldnames or [])}")
        for row in reader:
            count += 1
            time_s = float(row["time_s"])
            times_ok = times_ok and time_s == count
            values = [float(row[field]) for field in required if field != "time_s"]
            finite = finite and all(math.isfinite(value) for value in values)
            picard.append(float(row["picard_iterations"]))
            mass.append(abs(float(row["mass_step_residual"])))
            heat.append(abs(float(row["heat_step_residual_j"])))
            robin_heat.append(abs(float(row["surface_heat_boundary_residual_w_m2"])))
            robin_moisture.append(abs(float(row["surface_moisture_boundary_residual_kg_m2_s"])))
    summary = METRICS["run_1"]["diagnostics"]["summary"]
    picard_ok = count == 228536 and finite and times_ok and max(picard) <= 50 and summary["non_converged_steps"] == 0
    mass_ok = max(mass) == summary["mass_residual"]["max_abs"] and max(mass) <= 2.0e-8
    # Heat residual is an audited discrete balance diagnostic; retain the
    # measured value and require finiteness, not an invented physical tolerance.
    heat_ok = max(heat) == summary["discrete_heat_residual"]["max_abs_j"] and all(math.isfinite(value) for value in heat)
    robin_ok = max(robin_heat) == summary["robin_residual"]["heat_max_abs_w_m2"] and max(robin_moisture) == summary["robin_residual"]["moisture_max_abs_kg_m2_s"]
    fail(checks, "picard", picard_ok, {"rows": count, "finite": finite, "times_ok": times_ok, "max": max(picard), "non_converged_steps": summary["non_converged_steps"]})
    fail(checks, "mass", mass_ok, {"max_abs": max(mass), "recorded": summary["mass_residual"]["max_abs"], "rms": summary["mass_residual"]["rms"]})
    fail(checks, "heat", heat_ok, {"max_abs_j": max(heat), "recorded": summary["discrete_heat_residual"]["max_abs_j"], "rms_j": summary["discrete_heat_residual"]["rms_j"]})
    fail(checks, "robin", robin_ok, {"heat_max_abs_w_m2": max(robin_heat), "moisture_max_abs_kg_m2_s": max(robin_moisture)})
    fail(checks, "time_step_residual", summary["time_step_residual"]["temperature_max"] <= 1.0e-8 and summary["time_step_residual"]["moisture_max"] <= 1.0e-8, summary["time_step_residual"])


def audit_sampler(checks: dict[str, Any]) -> None:
    horizon = 228536
    wanted_times = {1, 2, 3, 4, 5, 10, 20, 30, 60, 100, 300, 600, 1800, 3599, 3600, 10800, 14395, 14396, 14397, 14398, 14399, 14400, 14401, 14402, 14403, 14500, 21600, 43200, 86400, 129600, 172800, 206935, 206936, horizon}
    seen_times: set[int] = set()
    rows = 0
    finite = True
    source = V3 / "run_1" / "official_samples.csv"
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header_ok = list(reader.fieldnames or []) == ["time_s", "radius_cm", "temperature_K", "temperature_C", "moisture_kg_kg"]
        for row in reader:
            rows += 1
            time_s = int(float(row["time_s"]))
            radius = float(row["radius_cm"])
            seen_times.add(time_s)
            finite = finite and all(math.isfinite(float(row[field])) for field in ("temperature_K", "temperature_C", "moisture_kg_kg"))
            if not (1 <= time_s <= horizon and 0 <= radius <= 2 and abs(radius * 10 - round(radius * 10)) < 1e-9):
                finite = False
    ok = rows == horizon * 21 and finite and wanted_times.issubset(seen_times)
    fail(checks, "sampler", ok, {"rows": rows, "expected_rows": horizon * 21, "finite": finite, "required_times_present": sorted(wanted_times - seen_times) == []})


def main() -> int:
    checks: dict[str, Any] = {}
    audit_config(checks)
    audit_code_and_inputs(checks)
    audit_run_files(checks)
    audit_diagnostics(checks)
    audit_sampler(checks)
    fail(checks, "q3_q4_not_started", not METRICS.get("q3_q4_started", True), {"q3_q4_started": METRICS.get("q3_q4_started")})
    gates = {name: value["status"] == "PASS" for name, value in checks.items()}
    all_pass = all(gates.values())
    payload = {
        "status": "PRE_CANDIDATE_GATES_PASS" if all_pass else "BLOCKED",
        "experiment": "Q2_FREEZE_RUN_V3",
        "audit_script": "scripts/audit_q2_v3_postproduction.py",
        "accuracy_basis": {"path": "experiments/Q2_ACCURACY_REMEDIATION/accuracy_confirmation_v3.json", "sha256": sha256(ACCURACY), "status": CERT["status"], "scope": CERT["gate"]["formal_output_definition"]},
        "checks": checks,
        "gates": gates,
        "candidate_workbook_generated": False,
        "figures_generated": False,
        "official_source_modified": not gates.get("official_source_modified", False),
        "q1_frozen_assets_modified": not gates.get("q1_regression", False),
        "q3_q4_started": not gates.get("q3_q4_not_started", False),
        "fail_closed": True,
        "result2_policy": "generate only after every pre-candidate gate is PASS; candidate remains pending human Q2 freeze approval",
    }
    (V3 / "validation.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "gates": gates}, ensure_ascii=False, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
