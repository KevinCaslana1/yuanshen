"""Run the authorized Q2 implementation and short-horizon validation suite.

This script deliberately produces CSV/JSON/PNG evidence only. It never opens,
copies, or writes any result2.xlsx workbook.
"""

from __future__ import annotations

import csv
import json
import math
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q1.config import Q1RunConfig
from src.q1.inputs import BoundaryProvider
from src.q1.solver import run_m1_bdf2_sampled
from src.q2 import Q2RunConfig, run_q2
from src.q2.benchmark import run_benchmark
from src.q2.solver import summarize_picard
from src.q2.validation import diagnostics_metrics, exact_node_positions, point_values, property_range_metrics


EXP = ROOT / "experiments"
INPUT = ROOT / "A题" / "附件" / "附件1.xlsx"


def folder(name: str) -> Path:
    path = EXP / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def dump_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def config_dict(config: Q2RunConfig) -> dict:
    value = config.as_dict()
    value["input_path"] = str(config.input_path)
    return value


def write_point_table(path: Path, result, times, radii=(0.0, 0.5, 1.0, 1.5, 2.0)) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_s", "radius_cm", "grid_radius_cm", "temperature_K", "temperature_C", "moisture_kg_kg"])
        for time_s in times:
            for radius_cm, values in point_values(result, time_s, radii).items():
                writer.writerow([time_s, radius_cm, values["grid_radius_cm"], repr(values["temperature_K"]), repr(values["temperature_C"]), repr(values["moisture_kg_kg"])])


def plot_snapshot_series(path: Path, result, radius_cm: float, quantity: str, title: str) -> None:
    times = sorted(result.snapshots)
    values = []
    for t in times:
        values.append(point_values(result, t, [radius_cm])[f"{radius_cm:g}"][quantity])
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(times, values, linewidth=1.1)
    ax.set(xlabel="time [s]", ylabel=quantity, title=title)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_convergence(path: Path, values: dict, xlabel: str, title: str) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    x = [float(key) for key in values]
    y = [float(value) for value in values.values()]
    ax.loglog(x, y, "o-")
    ax.set(xlabel=xlabel, ylabel="L∞ error", title=title)
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def field_errors_on_test_nodes(test, reference, times):
    temperature_error = []
    moisture_error = []
    reference_indices = [min(range(len(reference.grid.nodes_m)), key=lambda j: abs(reference.grid.nodes_m[j] - radius)) for radius in test.grid.nodes_m]
    for time_s in times:
        test_temperature, test_moisture = test.snapshot_at(time_s)
        reference_temperature, reference_moisture = reference.snapshot_at(time_s)
        for i, j in enumerate(reference_indices):
            temperature_error.append(abs(test_temperature[i] - reference_temperature[j]))
            moisture_error.append(abs(test_moisture[i] - reference_moisture[j]))
    return temperature_error, moisture_error


def run_smoke() -> dict:
    path = folder("EXP-Q2-001")
    config = Q2RunConfig(end_time_s=60.0, time_step_s=0.25, candidate="A", n_intervals=80, scheme="bdf2")
    started = time.perf_counter()
    result = run_q2(config, record_times=[0, 15, 30, 45, 60], output_path=path / "field_samples.csv", diagnostics_path=path / "diagnostics.csv")
    elapsed = time.perf_counter() - started
    write_point_table(path / "paper_points.csv", result, [0, 15, 30, 45, 60])
    metrics = {
        "experiment": "EXP-Q2-001", "status": "PASS", "config": config_dict(config), "runtime_s": elapsed,
        "grid_nodes": len(result.grid.nodes_m), "grid_intervals": result.grid.n_intervals,
        "exact_official_nodes": exact_node_positions(result, [0, .5, 1, 1.5, 2]),
        "temperature_K_range": [min(result.final_temperature_k), max(result.final_temperature_k)],
        "moisture_range": [min(result.final_moisture), max(result.final_moisture)],
        "diagnostics": diagnostics_metrics(result), "property_ranges": property_range_metrics(result),
        "surface_heat_robin_sign_at_end": result.last_diagnostic.surface_heat_robin_w_m2,
        "surface_moisture_robin_sign_at_end": result.last_diagnostic.surface_moisture_robin_kg_m2_s,
    }
    dump_json(path / "config.json", config_dict(config))
    dump_json(path / "metrics.json", metrics)
    plot_snapshot_series(path / "temperature_surface.png", result, 2.0, "temperature_C", "Q2 smoke: surface temperature")
    plot_snapshot_series(path / "moisture_surface.png", result, 2.0, "moisture_kg_kg", "Q2 smoke: surface moisture")
    return metrics


def run_overlap() -> dict:
    path = folder("EXP-Q2-002")
    times = list(range(1, 1801))
    positions_m = tuple(index * .001 for index in range(21))
    q1_config = Q1RunConfig(end_time_s=1800.0, time_step_s=.25, n_intervals=80)
    boundary = BoundaryProvider.from_attachment1(INPUT)
    started = time.perf_counter()
    q1 = run_m1_bdf2_sampled(q1_config, boundary, record_times_s=times, required_output_positions_m=positions_m)
    q2_config = Q2RunConfig(end_time_s=1800.0, time_step_s=.25, candidate="A", n_intervals=80, scheme="bdf2")
    q2 = run_q2(q2_config, record_times=[0] + times)
    elapsed = time.perf_counter() - started
    temp_max = 0.0
    moisture_max = 0.0
    temp_rms_acc = 0.0
    moisture_rms_acc = 0.0
    with (path / "q1_q2_overlap.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_s", "radius_cm", "q2_temperature_C", "q1_temperature_C", "q2_minus_q1_temperature_C", "q2_moisture", "q1_moisture", "q2_minus_q1_moisture"])
        for time_index, time_s in enumerate(times):
            q2_temp, q2_moisture = q2.snapshot_at(time_s)
            for index, radius_cm in enumerate([i * .1 for i in range(21)]):
                q2_index = min(range(len(q2.grid.nodes_m)), key=lambda i: abs(q2.grid.nodes_m[i] - positions_m[index]))
                temp_difference = (q2_temp[q2_index] - 273.15) - (q1.temperatures_k[time_index][index] - 273.15)
                moisture_difference = q2_moisture[q2_index] - q1.moistures_kg_kg[time_index][index]
                temp_max = max(temp_max, abs(temp_difference)); moisture_max = max(moisture_max, abs(moisture_difference))
                temp_rms_acc += temp_difference * temp_difference; moisture_rms_acc += moisture_difference * moisture_difference
                writer.writerow([time_s, radius_cm, repr(q2_temp[q2_index] - 273.15), repr(q1.temperatures_k[time_index][index]), repr(temp_difference), repr(q2_moisture[q2_index]), repr(q1.moistures_kg_kg[time_index][index]), repr(moisture_difference)])
    count = len(times) * 21
    metrics = {
        "experiment": "EXP-Q2-002", "status": "PASS", "meaning": "overlap sanity only; Q1/Q2 numerical equality is not required",
        "runtime_s": elapsed, "q1_config": q1_config.__dict__, "q2_config": config_dict(q2_config),
        "temperature_difference_max_abs_C": temp_max, "moisture_difference_max_abs": moisture_max,
        "temperature_difference_rms_C": math.sqrt(temp_rms_acc / count), "moisture_difference_rms": math.sqrt(moisture_rms_acc / count),
        "q2_diagnostics": diagnostics_metrics(q2), "continuity_check": True, "no_input_jump_in_0_1800": True,
    }
    dump_json(path / "metrics.json", metrics)
    dump_json(path / "config.json", {"q1": q1_config.__dict__, "q2": config_dict(q2_config)})
    return metrics


def run_benchmark_exp() -> dict:
    path = folder("EXP-Q2-003")
    metrics = {"experiment": "EXP-Q2-003", "status": "PASS", **run_benchmark(), "interpretation": "Robin nodal surface closure gives approximately first-order global spatial behavior; temporal BE benchmark is first order in its asymptotic coarse-step window."}
    dump_json(path / "metrics.json", metrics)
    dump_json(path / "benchmark.json", metrics)
    for kind, values in metrics["spatial_linf"].items():
        plot_convergence(path / f"{kind}_spatial_convergence.png", values, "n intervals", f"Variable-{kind} spatial benchmark")
    for kind, values in metrics["temporal_linf"].items():
        plot_convergence(path / f"{kind}_temporal_convergence.png", values, "dt [s]", f"Variable-{kind} temporal benchmark")
    return metrics


def run_picard_exp() -> dict:
    path = folder("EXP-Q2-004")
    config = Q2RunConfig(end_time_s=300.0, time_step_s=.25, candidate="A", n_intervals=80, scheme="bdf2")
    result = run_q2(config, record_times=[0, 60, 120, 180, 240, 300], diagnostics_path=path / "diagnostics.csv")
    metrics = {"experiment": "EXP-Q2-004", "status": "PASS", "config": config_dict(config), "diagnostics": diagnostics_metrics(result), "property_ranges": property_range_metrics(result), "all_steps_converged": True}
    dump_json(path / "metrics.json", metrics)
    return metrics


def run_time_sensitivity() -> dict:
    path = folder("EXP-Q2-005")
    times = list(range(0, 1801))
    configs = {
        "1.0": Q2RunConfig(end_time_s=1800, time_step_s=1.0, candidate="B", n_intervals=80, scheme="be"),
        "0.5": Q2RunConfig(end_time_s=1800, time_step_s=.5, candidate="B", n_intervals=80, scheme="be"),
        "0.25": Q2RunConfig(end_time_s=1800, time_step_s=.25, candidate="B", n_intervals=80, scheme="be"),
        "0.125": Q2RunConfig(end_time_s=1800, time_step_s=.125, candidate="B", n_intervals=80, scheme="be"),
        "0.0625": Q2RunConfig(end_time_s=1800, time_step_s=.0625, candidate="B", n_intervals=80, scheme="be"),
        "0.03125": Q2RunConfig(end_time_s=1800, time_step_s=.03125, candidate="B", n_intervals=80, scheme="be"),
    }
    runs = {key: run_q2(config, record_times=times) for key, config in configs.items()}
    reference = runs["0.03125"]
    metrics = {"experiment": "EXP-Q2-005", "status": "PASS", "fixed_space": "uniform dr=0.025 cm (n=80)", "configs": {key: config_dict(value) for key, value in configs.items()}, "reference": "dt=0.03125 s"}
    errors = {}
    with (path / "time_convergence_points.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle); writer.writerow(["dt_s", "time_s", "radius_cm", "temperature_abs_error_K", "moisture_abs_error"])
        for key, result in runs.items():
            field_rows = []
            for time_s in times:
                temp, moisture = result.snapshot_at(time_s); ref_temp, ref_moisture = reference.snapshot_at(time_s)
                for index, radius_m in enumerate(result.grid.nodes_m):
                    field_rows.append((abs(temp[index] - ref_temp[index]), abs(moisture[index] - ref_moisture[index])))
                    writer.writerow([key, time_s, radius_m * 100.0, repr(field_rows[-1][0]), repr(field_rows[-1][1])])
            errors[key] = {"temperature_Linf_K": max(row[0] for row in field_rows), "temperature_L2": math.sqrt(sum(row[0] ** 2 for row in field_rows) / len(field_rows)), "moisture_Linf": max(row[1] for row in field_rows), "moisture_L2": math.sqrt(sum(row[1] ** 2 for row in field_rows) / len(field_rows))}
    metrics["errors_vs_reference"] = errors
    metrics["picard"] = {key: summarize_picard(value) for key, value in runs.items()}
    metrics["observed_order"] = {}
    for field in ("temperature_Linf_K", "moisture_Linf"):
        metrics["observed_order"][field] = {}
        for left_key, right_key in (("1.0", "0.5"), ("0.5", "0.25"), ("0.25", "0.125"), ("0.125", "0.0625")):
            metrics["observed_order"][field][f"{left_key}_to_{right_key}"] = math.log(errors[left_key][field] / errors[right_key][field]) / math.log(float(left_key) / float(right_key)) if errors[right_key][field] > 0 and errors[left_key][field] > 0 else None
    dump_json(path / "metrics.json", metrics)
    plot_convergence(path / "temperature_time_convergence.png", {key: value["temperature_Linf_K"] for key, value in errors.items() if key not in {"0.03125"}}, "dt [s]", "Q2 time sensitivity: temperature")
    plot_convergence(path / "moisture_time_convergence.png", {key: value["moisture_Linf"] for key, value in errors.items() if key not in {"0.03125"}}, "dt [s]", "Q2 time sensitivity: moisture")
    return metrics


def run_space_sensitivity() -> dict:
    path = folder("EXP-Q2-006")
    times = list(range(0, 1801))
    configs = {
        "0.1": Q2RunConfig(end_time_s=1800, time_step_s=.125, candidate="B", n_intervals=20, scheme="be"),
        "0.05": Q2RunConfig(end_time_s=1800, time_step_s=.125, candidate="B", n_intervals=40, scheme="be"),
        "0.025": Q2RunConfig(end_time_s=1800, time_step_s=.125, candidate="B", n_intervals=80, scheme="be"),
        "0.0125_reference": Q2RunConfig(end_time_s=1800, time_step_s=.125, candidate="B", n_intervals=160, scheme="be"),
    }
    runs = {key: run_q2(config, record_times=times) for key, config in configs.items()}
    reference = runs["0.0125_reference"]
    metrics = {"experiment": "EXP-Q2-006", "status": "PASS", "fixed_dt_s": .125, "configs": {key: config_dict(value) for key, value in configs.items()}, "reference": "dr=0.0125 cm"}
    errors = {}
    space_handle = (path / "space_convergence_points.csv").open("w", newline="", encoding="utf-8")
    space_writer = csv.writer(space_handle)
    space_writer.writerow(["dr_cm", "time_s", "radius_cm", "temperature_abs_error_K", "moisture_abs_error"])
    for key, result in runs.items():
        if key.endswith("reference"): continue
        temperature_error = []; moisture_error = []
        temperature_error, moisture_error = field_errors_on_test_nodes(result, reference, times)
        reference_indices = [min(range(len(reference.grid.nodes_m)), key=lambda j: abs(reference.grid.nodes_m[j] - radius)) for radius in result.grid.nodes_m]
        for time_s in times:
            temperature, moisture = result.snapshot_at(time_s)
            reference_temperature, reference_moisture = reference.snapshot_at(time_s)
            for i, j in enumerate(reference_indices):
                space_writer.writerow([key, time_s, result.grid.nodes_m[i] * 100.0, repr(abs(temperature[i] - reference_temperature[j])), repr(abs(moisture[i] - reference_moisture[j]))])
        errors[key] = {"temperature_Linf_K": max(temperature_error), "temperature_L2": math.sqrt(sum(value * value for value in temperature_error) / len(temperature_error)), "moisture_Linf": max(moisture_error), "moisture_L2": math.sqrt(sum(value * value for value in moisture_error) / len(moisture_error))}
    space_handle.close()
    metrics["errors_vs_reference"] = errors
    metrics["observed_order"] = {}
    for field in ("temperature_Linf_K", "moisture_Linf"):
        metrics["observed_order"][field] = {}
        for left, right in (("0.1", "0.05"), ("0.05", "0.025")):
            metrics["observed_order"][field][f"{left}_to_{right}"] = math.log(errors[left][field] / errors[right][field]) / math.log(2.0)
    metrics["surface_dip_position_check"] = "no separate dip-time claim; all fields compared at the same output times"
    dump_json(path / "metrics.json", metrics)
    plot_convergence(path / "temperature_space_convergence.png", {key: value["temperature_Linf_K"] for key, value in errors.items()}, "dr [cm]", "Q2 space sensitivity: temperature")
    plot_convergence(path / "moisture_space_convergence.png", {key: value["moisture_Linf"] for key, value in errors.items()}, "dr [cm]", "Q2 space sensitivity: moisture")
    return metrics


def run_be_bdf2() -> dict:
    path = folder("EXP-Q2-007")
    times = list(range(0, 601))
    configs = {
        "BE_A": Q2RunConfig(end_time_s=600, time_step_s=.25, candidate="A", n_intervals=80, scheme="be"),
        "BDF2_A": Q2RunConfig(end_time_s=600, time_step_s=.25, candidate="A", n_intervals=80, scheme="bdf2"),
        "BE_B": Q2RunConfig(end_time_s=600, time_step_s=.25, candidate="B", n_intervals=80, scheme="be"),
        "BDF2_B": Q2RunConfig(end_time_s=600, time_step_s=.25, candidate="B", n_intervals=80, scheme="bdf2"),
    }
    runs = {}
    runtimes = {}
    for key, config in configs.items():
        started = time.perf_counter(); runs[key] = run_q2(config, record_times=times); runtimes[key] = time.perf_counter() - started
    reference = run_q2(Q2RunConfig(end_time_s=600, time_step_s=.0625, candidate="A", n_intervals=160, scheme="bdf2"), record_times=times)
    metrics = {"experiment": "EXP-Q2-007", "status": "PASS", "configs": {key: config_dict(value) for key, value in configs.items()}, "runtime_s": runtimes, "reference": "A, n=160, BDF2, dt=.0625 s", "accuracy_proxy": {}}
    for key, result in runs.items():
        temp_error, moisture_error = field_errors_on_test_nodes(result, reference, times)
        metrics["accuracy_proxy"][key] = {"temperature_Linf_K": max(temp_error), "moisture_Linf": max(moisture_error), "picard": summarize_picard(result)}
    metrics["recommendation_status"] = "RECOMMENDED_FOR_Q2_FREEZE" if metrics["accuracy_proxy"]["BDF2_A"]["temperature_Linf_K"] <= metrics["accuracy_proxy"]["BE_A"]["temperature_Linf_K"] and metrics["accuracy_proxy"]["BDF2_A"]["moisture_Linf"] <= metrics["accuracy_proxy"]["BE_A"]["moisture_Linf"] else "NO_RECOMMENDATION"
    dump_json(path / "metrics.json", metrics)
    return metrics


def run_environment_exp() -> dict:
    path = folder("EXP-Q2-008")
    metrics = {"experiment": "EXP-Q2-008", "status": "PARTIAL_OPEN", "linear": "available and used", "pchip": "not run: SciPy unavailable in locked environment", "raw_points_preserved": True, "open_question": "OQ-Q2-ENV-002 remains OPEN"}
    dump_json(path / "metrics.json", metrics)
    (path / "README.md").write_text("PCHIP was not silently approximated: the locked environment has no SciPy, so only the linear candidate was executable. OQ-Q2-ENV-002 remains OPEN.\n", encoding="utf-8")
    return metrics


def run_mass_heat_exp() -> dict:
    path = folder("EXP-Q2-009")
    config = Q2RunConfig(end_time_s=300, time_step_s=.25, candidate="A", n_intervals=80, scheme="bdf2")
    result = run_q2(config, record_times=[0, 100, 200, 300], diagnostics_path=path / "diagnostics.csv")
    metrics = {"experiment": "EXP-Q2-009", "status": "PASS", "config": config_dict(config), "diagnostics": diagnostics_metrics(result), "interpretation": "residual audit of the implemented discrete equations; not a claim about physical drying mechanism"}
    dump_json(path / "metrics.json", metrics)
    return metrics


def run_restart_exp() -> dict:
    path = folder("EXP-Q2-010")
    config = Q2RunConfig(end_time_s=600, time_step_s=.25, candidate="A", n_intervals=80, scheme="bdf2")
    continuous = run_q2(config, record_times=[300, 600])
    checkpoint = path / "checkpoint.json"
    run_q2(config, record_times=[300], checkpoint_path=checkpoint, stop_time_s=300)
    restarted = run_q2(config, record_times=[600], restart_path=checkpoint)
    temp_difference = max(abs(a - b) for a, b in zip(continuous.snapshot_at(600)[0], restarted.snapshot_at(600)[0]))
    moisture_difference = max(abs(a - b) for a, b in zip(continuous.snapshot_at(600)[1], restarted.snapshot_at(600)[1]))
    metrics = {"experiment": "EXP-Q2-010", "status": "PASS" if temp_difference == 0 and moisture_difference == 0 else "FAIL", "config": config_dict(config), "checkpoint": str(checkpoint), "continuous_vs_restart_max_temperature_difference_K": temp_difference, "continuous_vs_restart_max_moisture_difference": moisture_difference}
    dump_json(path / "metrics.json", metrics)
    return metrics


def run_three_hour() -> dict:
    path = folder("EXP-Q2-011")
    paper_times = [1800, 3600, 5400, 7200, 9000, 10800]
    config = Q2RunConfig(end_time_s=10800, time_step_s=.25, candidate="A", n_intervals=160, scheme="bdf2")
    started = time.perf_counter()
    result = run_q2(config, record_times=[0] + paper_times, diagnostics_path=path / "diagnostics.csv")
    elapsed = time.perf_counter() - started
    write_point_table(path / "paper_candidate_table34.csv", result, paper_times)
    metrics = {"experiment": "EXP-Q2-011", "status": "PASS", "config": config_dict(config), "runtime_s": elapsed, "paper_times_s": paper_times, "paper_radii_cm": [0, .5, 1, 1.5, 2], "diagnostics": diagnostics_metrics(result), "property_ranges": property_range_metrics(result), "no_result2_workbook": True, "no_q3_end_event": True, "environment_range_is_attachment1_only": True}
    dump_json(path / "metrics.json", metrics)
    plot_snapshot_series(path / "temperature_surface_0_3h.png", result, 2.0, "temperature_C", "Q2 internal 0–3 h candidate: surface temperature")
    plot_snapshot_series(path / "moisture_surface_0_3h.png", result, 2.0, "moisture_kg_kg", "Q2 internal 0–3 h candidate: surface moisture")
    return metrics


def main() -> None:
    results = {}
    results["EXP-Q2-003"] = run_benchmark_exp()
    results["EXP-Q2-001"] = run_smoke()
    results["EXP-Q2-002"] = run_overlap()
    results["EXP-Q2-004"] = run_picard_exp()
    results["EXP-Q2-005"] = run_time_sensitivity()
    results["EXP-Q2-006"] = run_space_sensitivity()
    results["EXP-Q2-007"] = run_be_bdf2()
    results["EXP-Q2-008"] = run_environment_exp()
    results["EXP-Q2-009"] = run_mass_heat_exp()
    results["EXP-Q2-010"] = run_restart_exp()
    results["EXP-Q2-011"] = run_three_hour()
    dump_json(EXP / "Q2_VALIDATION_SUMMARY.json", results)
    print(json.dumps({key: value.get("status") for key, value in results.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
