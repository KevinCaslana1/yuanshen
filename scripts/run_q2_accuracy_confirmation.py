"""Run the minimum direct Q2 production accuracy confirmation.

The approved production run is compared over every official second and all
21 official radii against one finer temporal run and one finer spatial run.
A second coarser temporal run supplies an observed-order check.  No workbook
is written by this script.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q2 import Q2RunConfig, run_q2


FREEZE = ROOT / "experiments" / "Q2_FREEZE_RUN"
THRESHOLD_T = 2.5e-5
THRESHOLD_C = 2.5e-5
PAPER_TIMES = (1800, 3600, 5400, 7200, 9000, 10800)
PAPER_RADII = (0.0, 0.5, 1.0, 1.5, 2.0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def csv_samples(path: Path) -> Iterator[tuple[int, int, float, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            time_s = int(round(float(row["time_s"])))
            radius_index = int(round(float(row["radius_cm"]) * 10.0))
            yield time_s, radius_index, float(row["temperature_C"]), float(row["moisture_kg_kg"])


def grouped_samples(path: Path, skip_t0: bool) -> Iterator[tuple[int, list[float], list[float]]]:
    current_time = None
    t_values: list[float] = []
    c_values: list[float] = []
    for time_s, radius_index, temperature, moisture in csv_samples(path):
        if skip_t0 and time_s == 0:
            continue
        if current_time is None:
            current_time = time_s
        if time_s != current_time:
            if len(t_values) != 21 or len(c_values) != 21:
                raise ValueError(f"sample group {current_time} is incomplete")
            yield current_time, t_values, c_values
            current_time = time_s
            t_values, c_values = [], []
        if radius_index < 0 or radius_index >= 21:
            raise ValueError(f"radius index outside official grid: {radius_index}")
        if radius_index < len(t_values) and t_values[radius_index] is not None:
            raise ValueError(f"duplicate sample key t={time_s}, r={radius_index}")
        while len(t_values) <= radius_index:
            t_values.append(None)  # type: ignore[arg-type]
            c_values.append(None)  # type: ignore[arg-type]
        t_values[radius_index] = temperature
        c_values[radius_index] = moisture
    if current_time is not None:
        if len(t_values) != 21 or len(c_values) != 21:
            raise ValueError(f"sample group {current_time} is incomplete")
        yield current_time, t_values, c_values


def compare(left: Path, right: Path, horizon: int, output_path: Path | None = None, *, left_skip_t0: bool = False, right_skip_t0: bool = True, extra_selected_times: set[int] | None = None) -> dict[str, Any]:
    left_iter = grouped_samples(left, skip_t0=left_skip_t0)
    right_iter = grouped_samples(right, skip_t0=right_skip_t0)
    radius_t_max = [0.0] * 21; radius_c_max = [0.0] * 21
    max_t = max_c = 0.0; sum_t_sq = sum_c_sq = 0.0; count = 0; times = 0
    selected: dict[str, dict[str, float]] = {}
    writer = None
    output_handle = None
    if output_path is not None:
        output_handle = output_path.open("w", newline="", encoding="utf-8")
        writer = csv.writer(output_handle, lineterminator="\n")
        writer.writerow(["time_s", "temperature_Linf_C", "temperature_L2_RMS_C", "moisture_Linf_kg_kg", "moisture_L2_RMS_kg_kg", *[f"temperature_abs_error_r{r / 10:g}_cm" for r in range(21)], *[f"moisture_abs_error_r{r / 10:g}_cm" for r in range(21)]])
    expected_time = 1
    try:
        for left_row, right_row in zip(left_iter, right_iter):
            time_left, t_left, c_left = left_row
            time_right, t_right, c_right = right_row
            if time_left != time_right or time_left != expected_time:
                raise ValueError(f"sample time mismatch: left={time_left}, right={time_right}, expected={expected_time}")
            t_errors = [abs(a - b) for a, b in zip(t_left, t_right)]
            c_errors = [abs(a - b) for a, b in zip(c_left, c_right)]
            t_linf, c_linf = max(t_errors), max(c_errors)
            for index in range(21):
                radius_t_max[index] = max(radius_t_max[index], t_errors[index]); radius_c_max[index] = max(radius_c_max[index], c_errors[index])
            max_t = max(max_t, t_linf); max_c = max(max_c, c_linf)
            sum_t_sq += sum(value * value for value in t_errors); sum_c_sq += sum(value * value for value in c_errors); count += 21; times += 1
            if time_left in PAPER_TIMES or time_left in {horizon} or time_left in (extra_selected_times or set()):
                selected[str(time_left)] = {"temperature_Linf_C": t_linf, "moisture_Linf_kg_kg": c_linf, "temperature_surface_C": t_errors[20], "moisture_surface_kg_kg": c_errors[20]}
            if writer is not None:
                writer.writerow([time_left, t_linf, math.sqrt(sum(value * value for value in t_errors) / 21), c_linf, math.sqrt(sum(value * value for value in c_errors) / 21), *t_errors, *c_errors])
            expected_time += 1
        if next(left_iter, None) is not None or next(right_iter, None) is not None:
            raise ValueError("sample lengths differ")
    finally:
        if output_handle is not None:
            output_handle.close()
    if times != horizon:
        raise ValueError(f"comparison covers {times} time layers, expected {horizon}")
    return {"time_layers": times, "official_points": count, "temperature_Linf_C": max_t, "temperature_L2_RMS_C": math.sqrt(sum_t_sq / count), "moisture_Linf_kg_kg": max_c, "moisture_L2_RMS_kg_kg": math.sqrt(sum_c_sq / count), "temperature_max_abs_by_radius_C": radius_t_max, "moisture_max_abs_by_radius_kg_kg": radius_c_max, "selected_times": selected}


def run_reference(name: str, config: Q2RunConfig, record_times: tuple[float, ...]) -> dict[str, Any]:
    directory = FREEZE / "accuracy_reference" / name
    directory.mkdir(parents=True, exist_ok=False)
    raw = directory / "official_samples_raw.csv"
    diagnostics = directory / "diagnostics_3600s.csv"
    started = time.perf_counter()
    result = run_q2(config, record_times=record_times, output_path=raw, diagnostics_path=diagnostics, diagnostics_interval_s=3600.0)
    runtime = time.perf_counter() - started
    if not result.complete:
        raise RuntimeError(f"accuracy reference did not complete: {name}")
    return {"name": name, "runtime_s": runtime, "config": config.as_dict(), "raw_path": str(raw.relative_to(ROOT)).replace("\\", "/"), "raw_sha256": sha256(raw), "diagnostics_path": str(diagnostics.relative_to(ROOT)).replace("\\", "/"), "complete": result.complete}


def main() -> int:
    config_payload = json.loads((FREEZE / "config.json").read_text(encoding="utf-8"))
    horizon = int(config_payload["final_horizon_s"])
    from src.q2.config import Q2Parameters
    config_dict = dict(config_payload["config"])
    config_dict["input_path"] = Path(config_dict["input_path"])
    config_dict["parameters"] = Q2Parameters(**config_dict["parameters"])
    production = Q2RunConfig(**config_dict)
    production_sample = FREEZE / "run_1" / "official_samples.csv"
    target_times = tuple(float(value) for value in sorted(set(PAPER_TIMES + (horizon,))))
    references = {}
    references["temporal_dt0.125"] = run_reference("temporal_dt0.125", replace(production, time_step_s=0.125), target_times)
    references["temporal_dt0.5"] = run_reference("temporal_dt0.5", replace(production, time_step_s=0.5), target_times)
    references["spatial_n160"] = run_reference("spatial_n160", replace(production, n_intervals=160), target_times)
    comparison_dir = FREEZE / "accuracy_confirmation"
    comparison_dir.mkdir()
    event_times = set(range(max(1, int(math.floor(config_payload["event_bracket_s"][0])) - 1), int(math.ceil(config_payload["event_bracket_s"][1])) + 2))
    temporal_fine = compare(production_sample, ROOT / references["temporal_dt0.125"]["raw_path"], horizon, comparison_dir / "production_vs_temporal_dt0.125_by_time.csv", extra_selected_times=event_times)
    temporal_coarse = compare(ROOT / references["temporal_dt0.5"]["raw_path"], ROOT / references["temporal_dt0.125"]["raw_path"], horizon, comparison_dir / "temporal_dt0.5_vs_dt0.125_by_time.csv", left_skip_t0=True, extra_selected_times=event_times)
    spatial = compare(production_sample, ROOT / references["spatial_n160"]["raw_path"], horizon, comparison_dir / "production_vs_spatial_n160_by_time.csv", extra_selected_times=event_times)
    def observed_order(coarse: float, fine: float, ratio: float = 2.0) -> float:
        return math.log(coarse / fine) / math.log(ratio) if coarse > 0.0 and fine > 0.0 else float("nan")
    orders = {"temporal_dt0.5_to_dt0.25_against_dt0.125": {"temperature": observed_order(temporal_coarse["temperature_Linf_C"], temporal_fine["temperature_Linf_C"]), "moisture": observed_order(temporal_coarse["moisture_Linf_kg_kg"], temporal_fine["moisture_Linf_kg_kg"])}}
    formal = {"temperature_Linf_C": max(temporal_fine["temperature_Linf_C"], spatial["temperature_Linf_C"]), "temperature_L2_RMS_C": max(temporal_fine["temperature_L2_RMS_C"], spatial["temperature_L2_RMS_C"]), "moisture_Linf_kg_kg": max(temporal_fine["moisture_Linf_kg_kg"], spatial["moisture_Linf_kg_kg"]), "moisture_L2_RMS_kg_kg": max(temporal_fine["moisture_L2_RMS_kg_kg"], spatial["moisture_L2_RMS_kg_kg"])}
    validation = {"status": "PASS" if formal["temperature_Linf_C"] <= THRESHOLD_T and formal["temperature_L2_RMS_C"] <= THRESHOLD_T and formal["moisture_Linf_kg_kg"] <= THRESHOLD_C and formal["moisture_L2_RMS_kg_kg"] <= THRESHOLD_C else "FAIL", "criterion": {"temperature_uncertainty_max_C": THRESHOLD_T, "moisture_uncertainty_max_kg_kg": THRESHOLD_C, "official_requirement": False}, "comparison_interval_s": [1, horizon], "reference_runs": references, "temporal": {"against_dt0.125": temporal_fine, "coarse_dt0.5_against_dt0.125": temporal_coarse, "observed_order": orders}, "spatial": {"against_n160": spatial}, "formal_output_region_estimate": formal, "required_checkpoints_s": list(PAPER_TIMES) + [horizon], "passive_event_neighborhood": {"bracket_s": config_payload["event_bracket_s"], "integer_seconds_checked": list(range(max(1, int(math.floor(config_payload["event_bracket_s"][0])) - 1), int(math.ceil(config_payload["event_bracket_s"][1])) + 2))}}
    (FREEZE / "accuracy_confirmation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "formal_output_region_estimate": formal, "temporal_observed_order": orders, "reference_runtimes_s": {key: value["runtime_s"] for key, value in references.items()}}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
