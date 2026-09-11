"""Run the approved Q2 production freeze from a fresh t=0 state.

The script deliberately separates horizon discovery from the two formal
production runs.  Discovery is a passive observer run to 72 h.  Run 1 and
Run 2 both restart from the official initial state and use the exact frozen
configuration.  No workbook is generated here.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from statistics import median
from typing import Any, Iterable

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q2 import Q2RunConfig, run_q2
from src.q2.environment import EnvironmentProvider
from src.q2.solver import grid_for_config


FREEZE = ROOT / "experiments" / "Q2_FREEZE_RUN"
INPUT = ROOT / "A题" / "附件" / "附件1.xlsx"
OFFICIAL_TEMPLATE = ROOT / "A题" / "附件" / "附件3" / "result2.xlsx"
Q1_FINAL = ROOT / "deliverables" / "final" / "result1.xlsx"
Q1_FREEZE_REFERENCE = ROOT / "experiments" / "Q1_FREEZE_RUN" / "run_1" / "internal_output_reference.pkl.gz"
Q1_FIGURES = ROOT / "figures" / "q1"
VALIDATED_ENVELOPE_S = 259200.0
PASSIVE_THRESHOLD = 0.15
SAFETY_TAIL_S = 21600.0
PAPER_TIMES_S = (1800.0, 3600.0, 5400.0, 7200.0, 9000.0, 10800.0)
PAPER_RADII_CM = (0.0, 0.5, 1.0, 1.5, 2.0)
Q1_FINAL_SHA256 = "06b67b1f688d84a701ac4d2f4b0f47a1624069877df6724faf071a48af177b5c"
Q1_FREEZE_REFERENCE_SHA256 = "f13667b5fe8e4c1e1a7635b18ab4c7aaa9e3fef5111b893a9ce79b6deb3fad17"
ATTACHMENT1_SHA256 = "7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7"
EXPECTED_TEMPLATE_SHA256 = "23b261b295c1b787d000eebbca6521c37075107b6fcf78724f8d395ce1798ff4"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_sha256(path: Path) -> str:
    """Hash a file tree by sorted relative names and file hashes."""
    if path.is_file():
        return sha256(path)
    rows = []
    for item in sorted((candidate for candidate in path.rglob("*") if candidate.is_file()), key=lambda p: p.as_posix()):
        rows.append((item.relative_to(path).as_posix(), sha256(item)))
    return hashlib.sha256(json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def project_relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def git_sha(ref: str = "HEAD") -> str:
    return subprocess.check_output(["git", "rev-parse", ref], cwd=ROOT, text=True).strip()


def git_status() -> str:
    return subprocess.check_output(["git", "status", "--short", "--branch"], cwd=ROOT, text=True).strip()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    left, right = math.floor(position), math.ceil(position)
    if left == right:
        return ordered[left]
    return ordered[left] + (position - left) * (ordered[right] - ordered[left])


def make_config(end_time_s: float) -> Q2RunConfig:
    return Q2RunConfig(
        end_time_s=end_time_s,
        time_step_s=0.25,
        candidate="A",
        n_intervals=80,
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
        input_path=Path("A题/附件/附件1.xlsx"),
    )


def q1_integrity_snapshot() -> dict[str, Any]:
    if not Q1_FINAL.is_file() or not Q1_FREEZE_REFERENCE.is_file() or not INPUT.is_file() or not OFFICIAL_TEMPLATE.is_file():
        raise FileNotFoundError("Q1 or official input/template integrity file is missing")
    actual_q1_final = sha256(Q1_FINAL)
    actual_q1_reference = sha256(Q1_FREEZE_REFERENCE)
    actual_attachment = sha256(INPUT)
    actual_template = sha256(OFFICIAL_TEMPLATE)
    if actual_q1_final != Q1_FINAL_SHA256:
        raise RuntimeError(f"Q1 final hash mismatch before production: {actual_q1_final}")
    if actual_q1_reference != Q1_FREEZE_REFERENCE_SHA256:
        raise RuntimeError(f"Q1 freeze reference hash mismatch before production: {actual_q1_reference}")
    if actual_attachment != ATTACHMENT1_SHA256:
        raise RuntimeError(f"Attachment 1 hash mismatch before production: {actual_attachment}")
    if actual_template != EXPECTED_TEMPLATE_SHA256:
        raise RuntimeError(f"official result2 template hash mismatch before production: {actual_template}")
    return {
        "q1_final_sha256": actual_q1_final,
        "q1_freeze_reference_sha256": actual_q1_reference,
        "q1_figure_tree_sha256": tree_sha256(Q1_FIGURES),
        "official_source_tree_sha256": tree_sha256(ROOT / "A题"),
        "q1_final_tag_sha": git_sha("q1-final"),
        "attachment1_sha256": actual_attachment,
        "official_result2_template_sha256": actual_template,
    }


def assert_q1_unchanged(baseline: dict[str, Any], label: str) -> None:
    current = q1_integrity_snapshot()
    for key, value in baseline.items():
        if current.get(key) != value:
            raise RuntimeError(f"Q1 frozen integrity changed {label}: {key}: {value} -> {current.get(key)}")


def environment_record(config: Q2RunConfig) -> dict[str, Any]:
    provider = EnvironmentProvider.from_attachment1(
        config.input_path,
        method=config.interpolation,
        post_attachment_mode=config.post_attachment_mode,
        post_temperature_c=config.post_temperature_c,
        post_moisture_kg_kg=config.post_moisture_kg_kg,
    )
    exact = provider.at(provider.last_time_s)
    epsilon = 1.0e-9
    post_epsilon = provider.at(provider.last_time_s + epsilon)
    post_step = provider.at(provider.last_time_s + config.time_step_s)
    return {
        "source_path": project_relative(INPUT),
        "source_sha256": provider.source_sha256,
        "interpolation": config.interpolation,
        "attachment_time_range_s": [provider.times_s[0], provider.last_time_s],
        "attachment_raw_count": provider.raw_count,
        "rule": "piecewise linear on Attachment 1; constant post-attachment environment",
        "post_attachment_mode": config.post_attachment_mode,
        "post_temperature_c": config.post_temperature_c,
        "post_moisture_kg_kg": config.post_moisture_kg_kg,
        "transition_assertion": {
            "at_14400_s": list(exact),
            "at_14400_plus_epsilon_s": list(post_epsilon),
            "at_14400_plus_dt_s": list(post_step),
            "epsilon_s": epsilon,
            "boundary_jump_at_epsilon": [post_epsilon[0] - exact[0], post_epsilon[1] - exact[1]],
            "boundary_jump_at_dt": [post_step[0] - exact[0], post_step[1] - exact[1]],
            "no_smoothing": True,
        },
    }


def run_regression(path: Path) -> dict[str, Any]:
    command = [sys.executable, "-m", "pytest", "-q"]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    (path / "pytest.stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (path / "pytest.stderr.txt").write_text(completed.stderr, encoding="utf-8")
    return {"command": command, "returncode": completed.returncode, "status": "PASS" if completed.returncode == 0 else "FAIL"}


def strip_t0_and_validate(raw_path: Path, sampled_path: Path, end_time_s: int) -> dict[str, Any]:
    expected_radii = tuple(round(index * 0.1, 1) for index in range(21))
    expected_time = 1
    t0_rows = 0
    rows = 0
    last_time = 0
    with raw_path.open(newline="", encoding="utf-8") as source, sampled_path.open("w", newline="", encoding="utf-8") as target:
        reader = csv.DictReader(source)
        if tuple(reader.fieldnames or ()) != ("time_s", "radius_cm", "temperature_K", "temperature_C", "moisture_kg_kg"):
            raise RuntimeError(f"unexpected raw output header: {reader.fieldnames}")
        writer = csv.DictWriter(target, fieldnames=reader.fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in reader:
            time_s = float(row["time_s"])
            radius_cm = float(row["radius_cm"])
            values = (float(row["temperature_K"]), float(row["temperature_C"]), float(row["moisture_kg_kg"]))
            if not all(math.isfinite(value) for value in values):
                raise RuntimeError(f"non-finite official raw output at {row}")
            if time_s == 0.0:
                t0_rows += 1
                continue
            if abs(time_s - round(time_s)) > 1.0e-9:
                raise RuntimeError(f"non-integer official output time: {time_s}")
            time_int = int(round(time_s))
            if time_int != expected_time:
                if time_int == last_time:
                    raise RuntimeError(f"duplicate official output time {time_int}")
                raise RuntimeError(f"missing or shifted official output time: expected {expected_time}, found {time_int}")
            current_radius_index = rows % 21
            if abs(radius_cm - expected_radii[current_radius_index]) > 1.0e-9:
                raise RuntimeError(f"official output radius mismatch at t={time_int}: expected {expected_radii[current_radius_index]}, found {radius_cm}")
            writer.writerow(row)
            rows += 1
            last_time = time_int
            if rows % 21 == 0:
                expected_time += 1
        if t0_rows != 21:
            raise RuntimeError(f"expected exactly 21 internal t=0 rows, found {t0_rows}")
        if expected_time != end_time_s + 1 or rows != end_time_s * 21:
            raise RuntimeError(f"sampled output shape mismatch: rows={rows}, expected={end_time_s * 21}, last_time={last_time}")
    return {"t0_rows_removed": t0_rows, "sampled_rows": rows, "time_start_s": 1, "time_end_s": end_time_s, "radii_cm": list(expected_radii)}


def parse_diagnostics(path: Path, end_time_s: int, config: Q2RunConfig) -> dict[str, Any]:
    expected_header = [
        "time_s", "scheme", "environment_temperature_c", "environment_moisture_kg_kg", "picard_iterations", "temperature_residual", "moisture_residual",
        "temperature_linear_residual", "moisture_linear_residual", "surface_heat_internal_w_m2", "surface_heat_robin_w_m2", "surface_heat_boundary_residual_w_m2",
        "surface_moisture_internal_kg_m2_s", "surface_moisture_robin_kg_m2_s", "surface_moisture_boundary_residual_kg_m2_s", "surface_k_w_m_k", "surface_D_m2_s",
        "mass_step_residual", "heat_step_residual_j", "property_min_json", "property_max_json", "picard_history_json", "temperature_min_k", "temperature_max_k",
        "moisture_min_kg_kg", "moisture_max_kg_kg", "center_heat_flux_w_m2", "center_moisture_flux_kg_m2_s",
    ]
    row_count = 0
    expected_time = 1
    counts: list[float] = []
    mass_max_abs = heat_max_abs = 0.0
    mass_sum = heat_sum = mass_sum_sq = heat_sum_sq = mass_abs_sum = heat_abs_sum = 0.0
    temp_min = temp_max = moisture_min = moisture_max = float("nan")
    property_ranges = {key: [float("inf"), float("-inf")] for key in ("rho", "cp", "k", "D")}
    picard_temp_max = picard_moisture_max = linear_temp_max = linear_moisture_max = 0.0
    robin_heat_max = robin_moisture_max = center_heat_max = center_moisture_max = 0.0
    surface_d_min, surface_d_max = float("inf"), float("-inf")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if list(reader.fieldnames or ()) != expected_header:
            raise RuntimeError("diagnostics header mismatch")
        for row in reader:
            parsed: dict[str, Any] = dict(row)
            for key in expected_header:
                if key in {"scheme", "property_min_json", "property_max_json", "picard_history_json"}:
                    continue
                if key == "picard_iterations":
                    parsed[key] = int(row[key])
                else:
                    parsed[key] = float(row[key])
                if not math.isfinite(float(parsed[key])):
                    raise RuntimeError(f"non-finite diagnostic field {key} at {row.get('time_s')}")
            time_int = int(round(parsed["time_s"]))
            if time_int != expected_time:
                raise RuntimeError(f"diagnostic time sequence mismatch at row {row_count + 1}: expected {expected_time}, found {time_int}")
            expected_time += 1
            parsed["property_min"] = json.loads(row["property_min_json"])
            parsed["property_max"] = json.loads(row["property_max_json"])
            parsed["picard_history"] = json.loads(row["picard_history_json"])
            if parsed["picard_iterations"] < 1 or parsed["picard_iterations"] > config.picard_max_iterations:
                raise RuntimeError(f"Picard iteration gate violation at t={parsed['time_s']}")
            if parsed["moisture_min_kg_kg"] <= 0.0:
                raise RuntimeError(f"non-positive moisture at t={parsed['time_s']}")
            for bounds in (parsed["property_min"], parsed["property_max"]):
                if set(bounds) != {"rho", "cp", "k", "D"} or not all(math.isfinite(float(value)) and float(value) > 0.0 for value in bounds.values()):
                    raise RuntimeError(f"invalid property diagnostic at t={parsed['time_s']}")
            row_count += 1
            counts.append(float(parsed["picard_iterations"]))
            mass_value, heat_value = parsed["mass_step_residual"], parsed["heat_step_residual_j"]
            mass_max_abs = max(mass_max_abs, abs(mass_value)); heat_max_abs = max(heat_max_abs, abs(heat_value))
            mass_sum += mass_value; heat_sum += heat_value
            mass_sum_sq += mass_value * mass_value; heat_sum_sq += heat_value * heat_value
            mass_abs_sum += abs(mass_value); heat_abs_sum += abs(heat_value)
            if math.isnan(temp_min):
                temp_min, temp_max = parsed["temperature_min_k"], parsed["temperature_max_k"]
                moisture_min, moisture_max = parsed["moisture_min_kg_kg"], parsed["moisture_max_kg_kg"]
            else:
                temp_min = min(temp_min, parsed["temperature_min_k"]); temp_max = max(temp_max, parsed["temperature_max_k"])
                moisture_min = min(moisture_min, parsed["moisture_min_kg_kg"]); moisture_max = max(moisture_max, parsed["moisture_max_kg_kg"])
            for key in property_ranges:
                property_ranges[key][0] = min(property_ranges[key][0], float(parsed["property_min"][key]))
                property_ranges[key][1] = max(property_ranges[key][1], float(parsed["property_max"][key]))
            picard_temp_max = max(picard_temp_max, parsed["temperature_residual"]); picard_moisture_max = max(picard_moisture_max, parsed["moisture_residual"])
            linear_temp_max = max(linear_temp_max, parsed["temperature_linear_residual"]); linear_moisture_max = max(linear_moisture_max, parsed["moisture_linear_residual"])
            robin_heat_max = max(robin_heat_max, abs(parsed["surface_heat_boundary_residual_w_m2"])); robin_moisture_max = max(robin_moisture_max, abs(parsed["surface_moisture_boundary_residual_kg_m2_s"]))
            center_heat_max = max(center_heat_max, abs(parsed["center_heat_flux_w_m2"])); center_moisture_max = max(center_moisture_max, abs(parsed["center_moisture_flux_kg_m2_s"]))
            surface_d_min = min(surface_d_min, parsed["surface_D_m2_s"]); surface_d_max = max(surface_d_max, parsed["surface_D_m2_s"])
    if row_count != end_time_s:
        raise RuntimeError(f"diagnostic time sequence mismatch: rows={row_count}, expected={end_time_s}")
    summary: dict[str, Any] = {
        "steps": row_count,
        "non_converged_steps": 0,
        "picard_iterations": {"min": min(counts), "median": median(counts), "p95": percentile(counts, 0.95), "max": max(counts)},
        "temperature_range_k": [temp_min, temp_max],
        "temperature_range_c": [temp_min - 273.15, temp_max - 273.15],
        "moisture_range_kg_kg": [moisture_min, moisture_max],
        "property_ranges": property_ranges,
        "picard_residual_max": {"temperature": picard_temp_max, "moisture": picard_moisture_max},
        "linear_residual_max": {"temperature": linear_temp_max, "moisture": linear_moisture_max},
        "mass_residual": {"max_abs": mass_max_abs, "rms": math.sqrt(mass_sum_sq / row_count), "cumulative_signed": mass_sum, "cumulative_abs": mass_abs_sum},
        "discrete_heat_residual": {"max_abs_j": heat_max_abs, "rms_j": math.sqrt(heat_sum_sq / row_count), "cumulative_signed_j": heat_sum, "cumulative_abs_j": heat_abs_sum},
        "robin_residual": {"heat_max_abs_w_m2": robin_heat_max, "moisture_max_abs_kg_m2_s": robin_moisture_max},
        "center_symmetry": {"heat_flux_max_abs_w_m2": center_heat_max, "moisture_flux_max_abs_kg_m2_s": center_moisture_max},
        "surface_D_range_m2_s": [surface_d_min, surface_d_max],
        "time_step_residual": {"temperature_max": picard_temp_max, "moisture_max": picard_moisture_max},
    }
    return summary


def run_one(run_name: str, config: Q2RunConfig, event_bracket: tuple[float, float], root: Path) -> dict[str, Any]:
    run_dir = root / run_name
    run_dir.mkdir(parents=True, exist_ok=False)
    raw_path = run_dir / "official_samples_raw.csv"
    diag_path = run_dir / "diagnostics_1s.csv"
    checkpoint_path = run_dir / "checkpoint_final.json"
    final_horizon = int(round(config.end_time_s))
    record_times = sorted(set(PAPER_TIMES_S + event_bracket + (config.end_time_s,)))
    started = time.perf_counter()
    result = run_q2(
        config,
        record_times=record_times,
        output_path=raw_path,
        diagnostics_path=diag_path,
        checkpoint_path=checkpoint_path,
        passive_event_threshold_kg_kg=PASSIVE_THRESHOLD,
        diagnostics_interval_s=1.0,
    )
    runtime = time.perf_counter() - started
    if not result.complete or result.passive_event_bracket_s != event_bracket:
        raise RuntimeError(f"{run_name} completion/event mismatch: complete={result.complete}, event={result.passive_event_bracket_s}, expected={event_bracket}")
    sampled_path = run_dir / "official_samples.csv"
    sampled_shape = strip_t0_and_validate(raw_path, sampled_path, final_horizon)
    diagnostics = parse_diagnostics(diag_path, final_horizon, config)
    grid = grid_for_config(config)
    memory_estimate_bytes = len(grid.nodes_m) * 8 * 64
    payload = {
        "run": run_name,
        "status": "PASS",
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
            "official_radii_cm": list(tuple(index * 0.1 for index in range(21))),
        },
        "method": {"first_step": "Backward Euler", "subsequent_steps": "BDF2", "coupling": "temperature-moisture Picard", "interface_mean": config.interface_mean},
        "sampled_output": {"path": project_relative(sampled_path), **sampled_shape},
        "raw_output": {"path": project_relative(raw_path), "rows_including_header": sum(1 for _ in raw_path.open(encoding="utf-8"))},
        "diagnostics": {"path": project_relative(diag_path), "summary": diagnostics},
        "checkpoint": {"path": project_relative(checkpoint_path), "count": 1, "sha256": sha256(checkpoint_path)},
        "passive_event_bracket_s": list(event_bracket),
        "final_horizon_s": final_horizon,
        "memory_estimate_bytes": memory_estimate_bytes,
        "output_bytes": {"raw": raw_path.stat().st_size, "sampled": sampled_path.stat().st_size, "diagnostics": diag_path.stat().st_size},
    }
    write_json(run_dir / "metrics.json", payload)
    return payload


def compare_csv_exact(left: Path, right: Path) -> dict[str, Any]:
    if sha256(left) == sha256(right):
        return {"status": "PASS", "mode": "byte/hash identical", "left_sha256": sha256(left), "right_sha256": sha256(right)}
    max_diffs: dict[str, float] = {}
    rows = 0
    with left.open(newline="", encoding="utf-8") as lhs, right.open(newline="", encoding="utf-8") as rhs:
        lreader, rreader = csv.DictReader(lhs), csv.DictReader(rhs)
        if lreader.fieldnames != rreader.fieldnames:
            return {"status": "FAIL", "mode": "header mismatch"}
        for lrow, rrow in zip(lreader, rreader):
            if lrow.get("time_s") != rrow.get("time_s") or lrow.get("radius_cm") != rrow.get("radius_cm"):
                return {"status": "FAIL", "mode": "key mismatch", "rows_compared": rows}
            for key in lreader.fieldnames or ():
                if key in {"time_s", "radius_cm", "scheme", "property_min_json", "property_max_json", "picard_history_json"}:
                    continue
                try:
                    delta = abs(float(lrow[key]) - float(rrow[key]))
                except (TypeError, ValueError):
                    delta = 0.0 if lrow[key] == rrow[key] else float("inf")
                max_diffs[key] = max(max_diffs.get(key, 0.0), delta)
            rows += 1
        if next(lreader, None) is not None or next(rreader, None) is not None:
            return {"status": "FAIL", "mode": "length mismatch", "rows_compared": rows}
    return {"status": "PASS" if all(value <= 1.0e-14 for value in max_diffs.values()) else "FAIL", "mode": "machine precision comparison", "rows_compared": rows, "max_abs_differences": max_diffs}


def build_lineage(run1: dict[str, Any], run2: dict[str, Any]) -> dict[str, Any]:
    entries = []
    for run, status in ((run1, "PRODUCTION_CANONICAL"), (run2, "DETERMINISM_REFERENCE")):
        for key in ("raw_output", "sampled_output", "diagnostics", "checkpoint"):
            info = run[key] if key in run else {}
            path = info.get("path")
            if not path:
                continue
            abs_path = ROOT / path
            entries.append({"path": path, "status": status, "sha256": sha256(abs_path), "run": run["run"], "role": key})
    entries.extend([
        {"path": "experiments/EXP-Q2-016-LONG-ENV-A-last-raw/official_samples_recovered.csv", "status": "VALIDATION_ONLY", "reason": "old recovered validation source; not formal production"},
        {"path": "experiments/EXP-Q2-016-LONG-ENV-A-last-raw/diagnostics_1s_recovered.csv", "status": "VALIDATION_ONLY", "reason": "old recovered validation source; not formal production"},
        {"path": "experiments/EXP-Q2-016-LONG-ENV-A-last-raw/official_samples.csv", "status": "NONCANONICAL_DUPLICATE", "reason": "old interrupted raw duplicate"},
        {"path": "experiments/EXP-Q2-016-LONG-ENV-A-last-raw/diagnostics_1s.csv", "status": "NONCANONICAL_DUPLICATE", "reason": "old interrupted diagnostic duplicate"},
        {"path": "experiments/EXP-Q2-012-ENVIRONMENT", "status": "VALIDATION_ONLY", "reason": "old sensitivity/decision evidence"},
        {"path": "experiments/EXP-Q2-013-INTERPOLATION", "status": "VALIDATION_ONLY", "reason": "old sensitivity/decision evidence"},
        {"path": "experiments/EXP-Q2-014-BC-SENSITIVITY", "status": "VALIDATION_ONLY", "reason": "old sensitivity evidence"},
        {"path": "experiments/EXP-Q2-015-INTERFACE-MEAN", "status": "VALIDATION_ONLY", "reason": "old sensitivity evidence"},
    ])
    return {
        "manifest_version": "Q2_PRODUCTION_LINEAGE_V1",
        "formal_result_source": "experiments/Q2_FREEZE_RUN/run_1",
        "run_1_status": "PRODUCTION_CANONICAL",
        "run_2_status": "DETERMINISM_REFERENCE",
        "entries": entries,
        "fail_closed_policy": "formal loaders require PRODUCTION_CANONICAL and verified SHA-256",
    }


def main() -> int:
    if FREEZE.exists():
        if any(FREEZE.iterdir()):
            raise SystemExit("Q2_FREEZE_RUN must be absent or empty before production; refusing to reuse old data")
    else:
        FREEZE.mkdir(parents=True)
    preflight_dir = FREEZE / "preflight"
    preflight_dir.mkdir()
    baseline = q1_integrity_snapshot()
    regression = run_regression(preflight_dir)
    if regression["status"] != "PASS":
        raise SystemExit("Q2 production blocked: regression tests failed")
    if git_status() != f"## {subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()}" and not git_status().startswith("## "):
        raise SystemExit("Q2 production blocked: could not read Git status")

    discovery_config = make_config(VALIDATED_ENVELOPE_S)
    write_json(FREEZE / "input_hashes.json", {
        "official_source_root": "A题",
        "official_input_sha256": sha256(INPUT),
        "official_result2_template_sha256": sha256(OFFICIAL_TEMPLATE),
        "q1_final_sha256": sha256(Q1_FINAL),
        "q1_freeze_reference_sha256": sha256(Q1_FREEZE_REFERENCE),
        "q1_figure_tree_sha256": baseline["q1_figure_tree_sha256"],
        "official_source_tree_sha256": baseline["official_source_tree_sha256"],
    })
    write_json(FREEZE / "environment.json", environment_record(discovery_config))
    write_json(FREEZE / "preflight.json", {
        "status": "PASS",
        "code_commit": git_sha(),
        "git_status": git_status(),
        "python": {"executable": sys.executable, "version": sys.version, "implementation": platform.python_implementation(), "platform": platform.platform()},
        "dependencies": {
            "openpyxl": __import__("openpyxl").__version__,
            "numpy": __import__("numpy").__version__,
            "matplotlib": __import__("matplotlib").__version__,
        },
        "q1_integrity": baseline,
        "regression": regression,
        "production_source_rule": "run_1 only; all old validation/recovered/duplicate/sensitivity artifacts excluded",
    })

    print("[Q2] discovering passive event bracket from fresh t=0 to 72 h", flush=True)
    discovery_dir = FREEZE / "horizon_discovery"
    discovery_dir.mkdir()
    started = time.perf_counter()
    discovery_result = run_q2(
        discovery_config,
        diagnostics_path=discovery_dir / "diagnostics_3600s.csv",
        passive_event_threshold_kg_kg=PASSIVE_THRESHOLD,
        diagnostics_interval_s=3600.0,
    )
    discovery_runtime = time.perf_counter() - started
    bracket = discovery_result.passive_event_bracket_s
    if bracket is None:
        raise SystemExit("Q2 FREEZE RUN BLOCKED: passive event bracket was not detected")
    event_low, event_high = bracket
    final_horizon = int(math.ceil(event_high) + SAFETY_TAIL_S)
    if final_horizon > int(VALIDATED_ENVELOPE_S):
        raise SystemExit("Q2 FREEZE RUN BLOCKED: PRODUCTION HORIZON OUTSIDE VALIDATED ENVELOPE")
    if final_horizon <= 0 or final_horizon % 1 != 0:
        raise SystemExit("invalid non-integer final production horizon")
    write_json(discovery_dir / "metrics.json", {
        "status": "PASS",
        "fresh_start": True,
        "runtime_s": discovery_runtime,
        "config": discovery_config.as_dict(),
        "passive_threshold_kg_kg": PASSIVE_THRESHOLD,
        "passive_event_bracket_s": list(bracket),
        "safety_tail_s": SAFETY_TAIL_S,
        "final_horizon_s": final_horizon,
        "validated_envelope_s": VALIDATED_ENVELOPE_S,
        "diagnostics_path": project_relative(discovery_dir / "diagnostics_3600s.csv"),
    })
    production_config = make_config(float(final_horizon))
    grid = grid_for_config(production_config)
    config_payload = {
        "status": "FROZEN",
        "code_commit": git_sha(),
        "validated_envelope_s": VALIDATED_ENVELOPE_S,
        "passive_event_threshold_kg_kg": PASSIVE_THRESHOLD,
        "safety_tail_s": SAFETY_TAIL_S,
        "event_bracket_s": list(bracket),
        "final_horizon_s": final_horizon,
        "run_1_and_run_2_must_start_from_t0": True,
        "official_sample_rule": "time_s=1..final_horizon, radius_cm=0.0..2.0 at 0.1 cm; t=0 retained only in raw internal output",
        "model": {"geometry": "1D fixed-radius cylindrical radial", "physics": ["rho(C)", "cp(C)", "k(C)", "D(C,T)"], "boundaries": ["center symmetry", "Robin heat", "Robin moisture"], "coupling": "coupled Picard", "forbidden": ["latent heat", "shrinkage", "Q4 moving boundary", "unapproved new physics"]},
        "numerical": {"candidate": "A", "grid": {"type": type(grid).__name__, "requested_intervals": production_config.n_intervals, "actual_cell_count": len(grid.nodes_m) - 1, "actual_node_count": len(grid.nodes_m), "cluster_power": production_config.cluster_power, "min_dr_m": getattr(grid, "min_dr_m", getattr(grid, "dr_m", None)), "max_dr_m": getattr(grid, "max_dr_m", getattr(grid, "dr_m", None)), "min_dr_cm": getattr(grid, "min_dr_m", getattr(grid, "dr_m", None)) * 100.0, "max_dr_cm": getattr(grid, "max_dr_m", getattr(grid, "dr_m", None)) * 100.0}, "time_step_s": production_config.time_step_s, "first_step": "Backward Euler", "subsequent_steps": "BDF2", "interface_mean": production_config.interface_mean, "picard_tolerance": production_config.picard_tolerance, "picard_max_iterations": production_config.picard_max_iterations, "picard_relaxation": production_config.picard_relaxation},
        "environment": {"within_attachment1": "piecewise linear", "post_attachment": "constant", "post_temperature_c": production_config.post_temperature_c, "post_moisture_kg_kg": production_config.post_moisture_kg_kg, "input_path": project_relative(INPUT)},
        "accuracy_criterion": {"temperature_estimated_uncertainty_c": 2.5e-5, "moisture_estimated_uncertainty_kg_kg": 2.5e-5, "official_requirement": False},
        "checkpoint_policy": {"fresh_final_checkpoint_per_run": True, "checkpoint_count_per_run": 1, "restart_for_production": False},
        "config": production_config.as_dict(),
    }
    write_json(FREEZE / "config.json", config_payload)
    config_hash = sha256(FREEZE / "config.json")
    assert_q1_unchanged(baseline, "before Run 1")
    print(f"[Q2] passive bracket={event_low:g}..{event_high:g} s; final_horizon={final_horizon} s", flush=True)

    run1 = run_one("run_1", production_config, bracket, FREEZE)
    assert_q1_unchanged(baseline, "after Run 1")
    print(f"[Q2] Run 1 complete in {run1['runtime_s']:.1f} s; starting independent Run 2", flush=True)
    run2 = run_one("run_2", production_config, bracket, FREEZE)
    assert_q1_unchanged(baseline, "after Run 2")
    print(f"[Q2] Run 2 complete in {run2['runtime_s']:.1f} s", flush=True)

    run_compare = {
        "raw_output": compare_csv_exact(FREEZE / "run_1" / "official_samples_raw.csv", FREEZE / "run_2" / "official_samples_raw.csv"),
        "sampled_output": compare_csv_exact(FREEZE / "run_1" / "official_samples.csv", FREEZE / "run_2" / "official_samples.csv"),
        "diagnostics": compare_csv_exact(FREEZE / "run_1" / "diagnostics_1s.csv", FREEZE / "run_2" / "diagnostics_1s.csv"),
        "event_bracket_equal": run1["passive_event_bracket_s"] == run2["passive_event_bracket_s"],
        "final_horizon_equal": run1["final_horizon_s"] == run2["final_horizon_s"],
    }
    run_compare["status"] = "PASS" if all(value is True or value.get("status") == "PASS" for value in run_compare.values()) else "FAIL"
    if run_compare["status"] != "PASS":
        raise SystemExit("Q2 production determinism comparison failed; candidate generation is blocked")
    output_hashes = {
        "config_sha256": config_hash,
        "environment_sha256": sha256(FREEZE / "environment.json"),
        "run_1": {name: sha256(FREEZE / "run_1" / filename) for name, filename in {"raw_output": "official_samples_raw.csv", "sampled_output": "official_samples.csv", "diagnostics": "diagnostics_1s.csv", "checkpoint": "checkpoint_final.json"}.items()},
        "run_2": {name: sha256(FREEZE / "run_2" / filename) for name, filename in {"raw_output": "official_samples_raw.csv", "sampled_output": "official_samples.csv", "diagnostics": "diagnostics_1s.csv", "checkpoint": "checkpoint_final.json"}.items()},
    }
    write_json(FREEZE / "output_hashes.json", output_hashes)
    write_json(FREEZE / "lineage.json", build_lineage(run1, run2))
    write_json(FREEZE / "determinism.json", run_compare)
    write_json(FREEZE / "metrics.json", {
        "status": "PRODUCTION_RUNS_COMPLETE",
        "experiment": "Q2_FREEZE_RUN",
        "canonical_result_source": "experiments/Q2_FREEZE_RUN/run_1",
        "run_1": run1,
        "run_2": run2,
        "determinism": run_compare,
        "production_horizon": {"passive_event_bracket_s": list(bracket), "safety_tail_s": SAFETY_TAIL_S, "final_horizon_s": final_horizon, "validated_envelope_s": VALIDATED_ENVELOPE_S},
        "q1_integrity_final": q1_integrity_snapshot(),
        "official_source_tree_sha256_final": tree_sha256(ROOT / "A题"),
        "candidate_workbook_generated": False,
    })
    write_json(FREEZE / "validation.json", {"status": "PENDING_ACCURACY_AND_CANDIDATE_VALIDATION", "run_determinism": run_compare, "fail_closed": True})
    print("[Q2] production run and determinism gates passed; accuracy/candidate/figures are next", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
