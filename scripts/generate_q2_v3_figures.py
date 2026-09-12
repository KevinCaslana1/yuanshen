"""Generate the Q2 V3 figures from the production-canonical Run 1 source."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q2.lineage import production_csv_path
from src.q2.properties import diffusivity

V3 = ROOT / "experiments" / "Q2_FREEZE_RUN_V3"
FIG_ROOT = ROOT / "figures" / "q2"
DATA = FIG_ROOT / "data"
FINAL = FIG_ROOT / "final"
PAPER_TIMES = (1800, 3600, 5400, 7200, 9000, 10800)
LONG_TIMES = (21600, 86400, 172800)
REPRESENTATIVE_RADII = (0.0, 0.5, 1.0, 1.5, 2.0)
SEED = 20260912


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, header: list[str], rows: Any) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def save_figure(stem: str) -> tuple[str, str]:
    png = FINAL / f"{stem}.png"
    svg = FINAL / f"{stem}.svg"
    plt.savefig(png, dpi=300, bbox_inches="tight")
    plt.savefig(svg, bbox_inches="tight")
    plt.close()
    return str(png.relative_to(ROOT)).replace("\\", "/"), str(svg.relative_to(ROOT)).replace("\\", "/")


def load_samples(source: Path, horizon: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    times = np.arange(1, horizon + 1, dtype=np.int64)
    radii = np.arange(21, dtype=np.float64) / 10.0
    temperature = np.full((horizon, 21), np.nan, dtype=np.float64)
    moisture = np.full((horizon, 21), np.nan, dtype=np.float64)
    rows = 0
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        expected = ["time_s", "radius_cm", "temperature_K", "temperature_C", "moisture_kg_kg"]
        if list(reader.fieldnames or []) != expected:
            raise ValueError("production source header mismatch")
        for row in reader:
            time_s = int(float(row["time_s"]))
            radius_index = int(round(float(row["radius_cm"]) * 10.0))
            if not (1 <= time_s <= horizon and 0 <= radius_index <= 20):
                raise ValueError(f"source key outside official grid: {row}")
            temperature[time_s - 1, radius_index] = float(row["temperature_C"])
            moisture[time_s - 1, radius_index] = float(row["moisture_kg_kg"])
            rows += 1
    if rows != horizon * 21 or not np.isfinite(temperature).all() or not np.isfinite(moisture).all():
        raise ValueError(f"production source is incomplete/non-finite: rows={rows}")
    return times, radii, temperature, moisture


def load_diagnostics(path: Path, horizon: int) -> dict[str, np.ndarray]:
    keys = ("time_s", "picard_iterations", "mass_step_residual", "heat_step_residual_j")
    fields = {key: [] for key in keys}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            for key in keys:
                fields[key].append(float(row[key]))
    if len(fields["time_s"]) != horizon or fields["time_s"] != list(map(float, range(1, horizon + 1))):
        raise ValueError("diagnostic source is not a complete 1-second sequence")
    return {key: np.asarray(value) for key, value in fields.items()}


def figure_entry(figure_id: str, title: str, data_path: Path, png: str, svg: str, variables: list[str], times: Any, radii: Any, source_hash: str) -> dict[str, Any]:
    return {
        "figure_id": figure_id,
        "title": title,
        "source_run": "experiments/Q2_FREEZE_RUN_V3/run_1",
        "source_output": "experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv",
        "source_hash": source_hash,
        "data_file": str(data_path.relative_to(ROOT)).replace("\\", "/"),
        "data_sha256": sha256(data_path),
        "png_path": png,
        "svg_path": svg,
        "generation_script": "scripts/generate_q2_v3_figures.py",
        "variables": variables,
        "time_selection": times,
        "radius_selection": radii,
        "no_smoothing": True,
        "no_numeric_interpolation": True,
    }


def main() -> int:
    config = json.loads((V3 / "config.json").read_text(encoding="utf-8"))
    hashes = json.loads((V3 / "output_hashes.json").read_text(encoding="utf-8"))
    horizon = int(config["final_horizon_s"])
    source = production_csv_path("experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv")
    source_hash = sha256(source)
    if source_hash != hashes["run_1"]["sampled_output"]:
        raise ValueError("production source hash mismatch")
    DATA.mkdir(parents=True, exist_ok=True)
    FINAL.mkdir(parents=True, exist_ok=True)
    times, radii, temperature, moisture = load_samples(source, horizon)
    diagnostics = load_diagnostics(V3 / "run_1" / "diagnostics_1s.csv", horizon)
    entries: list[dict[str, Any]] = []

    profile_times = tuple(time_s for time_s in PAPER_TIMES + LONG_TIMES + (horizon,) if time_s <= horizon)
    profile_t = DATA / "FIG-Q2-01_temperature_radial_profiles.csv"
    profile_c = DATA / "FIG-Q2-02_moisture_radial_profiles.csv"
    write_csv(profile_t, ["time_s", *[f"radius_{r:.1f}_cm" for r in radii]], [[time_s, *temperature[time_s - 1].tolist()] for time_s in profile_times])
    write_csv(profile_c, ["time_s", *[f"radius_{r:.1f}_cm" for r in radii]], [[time_s, *moisture[time_s - 1].tolist()] for time_s in profile_times])
    for values, title, ylabel, stem, data_path, figure_id, key in ((temperature, "Q2 temperature radial profiles", "Temperature (°C)", "FIG-Q2-01_temperature_radial_profiles", profile_t, "FIG-Q2-01", "temperature_C"), (moisture, "Q2 moisture radial profiles", "Moisture (kg/kg)", "FIG-Q2-02_moisture_radial_profiles", profile_c, "FIG-Q2-02", "moisture_kg_kg")):
        for time_s in profile_times:
            plt.plot(radii, values[time_s - 1], label=f"{time_s / 3600:g} h")
        plt.xlabel("Radius (cm)")
        plt.ylabel(ylabel)
        plt.title(title)
        plt.grid(True, alpha=0.25)
        plt.legend(ncol=2)
        png, svg = save_figure(stem)
        entries.append(figure_entry(figure_id, title, data_path, png, svg, [key], list(profile_times), "all official radii", source_hash))

    heat_t = DATA / "FIG-Q2-03_temperature_time_radius_heatmap.npz"
    heat_c = DATA / "FIG-Q2-04_moisture_time_radius_heatmap.npz"
    np.savez_compressed(heat_t, time_s=times, radius_cm=radii, temperature_C=temperature)
    np.savez_compressed(heat_c, time_s=times, radius_cm=radii, moisture_kg_kg=moisture)
    for values, title, label, stem, data_path, figure_id, key in ((temperature, "Q2 temperature time-radius heatmap", "Temperature (°C)", "FIG-Q2-03_temperature_time_radius_heatmap", heat_t, "FIG-Q2-03", "temperature_C"), (moisture, "Q2 moisture time-radius heatmap", "Moisture (kg/kg)", "FIG-Q2-04_moisture_time_radius_heatmap", heat_c, "FIG-Q2-04", "moisture_kg_kg")):
        plt.imshow(values, origin="lower", aspect="auto", extent=[0, 2, 1, horizon], interpolation="none")
        plt.xlabel("Radius (cm)")
        plt.ylabel("Time (s)")
        plt.title(title)
        plt.colorbar(label=label)
        png, svg = save_figure(stem)
        entries.append(figure_entry(figure_id, title, data_path, png, svg, [key], f"all {horizon} sampled seconds", "0.0..2.0 cm at 0.1 cm", source_hash))

    history_t = DATA / "FIG-Q2-05_temperature_time_histories.csv"
    history_c = DATA / "FIG-Q2-06_moisture_time_histories.csv"
    columns = [int(round(r * 10)) for r in REPRESENTATIVE_RADII]
    write_csv(history_t, ["time_s", *[f"radius_{r:.1f}_cm" for r in REPRESENTATIVE_RADII]], [[int(time_s), *temperature[time_s - 1, columns].tolist()] for time_s in times])
    write_csv(history_c, ["time_s", *[f"radius_{r:.1f}_cm" for r in REPRESENTATIVE_RADII]], [[int(time_s), *moisture[time_s - 1, columns].tolist()] for time_s in times])
    for values, title, ylabel, stem, data_path, figure_id, key in ((temperature, "Q2 representative temperature histories", "Temperature (°C)", "FIG-Q2-05_temperature_time_histories", history_t, "FIG-Q2-05", "temperature_C"), (moisture, "Q2 representative moisture histories", "Moisture (kg/kg)", "FIG-Q2-06_moisture_time_histories", history_c, "FIG-Q2-06", "moisture_kg_kg")):
        for radius in REPRESENTATIVE_RADII:
            plt.plot(times, values[:, int(round(radius * 10))], label=f"r={radius:g} cm")
        plt.xlabel("Time (s)")
        plt.ylabel(ylabel)
        plt.title(title)
        plt.grid(True, alpha=0.25)
        plt.legend()
        png, svg = save_figure(stem)
        entries.append(figure_entry(figure_id, title, data_path, png, svg, [key], f"all {horizon} sampled seconds", list(REPRESENTATIVE_RADII), source_hash))

    difference = moisture[:, 0] - moisture[:, 20]
    diff_data = DATA / "FIG-Q2-07_center_surface_moisture_difference.csv"
    write_csv(diff_data, ["time_s", "center_minus_surface_moisture_kg_kg"], [[int(time_s), float(value)] for time_s, value in zip(times, difference)])
    plt.plot(times, difference)
    plt.axhline(0.0, color="black", linewidth=0.8)
    plt.xlabel("Time (s)")
    plt.ylabel("C(center)-C(surface) (kg/kg)")
    plt.title("Q2 center-surface moisture difference")
    plt.grid(True, alpha=0.25)
    png, svg = save_figure("FIG-Q2-07_center_surface_moisture_difference")
    entries.append(figure_entry("FIG-Q2-07", "Q2 center-surface moisture difference", diff_data, png, svg, ["center_minus_surface_moisture_kg_kg"], f"all {horizon} sampled seconds", [0.0, 2.0], source_hash))

    representative_d = np.empty((horizon, 3), dtype=np.float64)
    for column, radius_index in enumerate((0, 10, 20)):
        representative_d[:, column] = [diffusivity(float(c), float(t) + 273.15) for c, t in zip(moisture[:, radius_index], temperature[:, radius_index])]
    d_data = DATA / "FIG-Q2-08_representative_diffusivity.csv"
    write_csv(d_data, ["time_s", "D_center_m2_s", "D_r1cm_m2_s", "D_surface_m2_s"], [[int(time_s), *row.tolist()] for time_s, row in zip(times, representative_d)])
    for column, radius in enumerate((0.0, 1.0, 2.0)):
        plt.plot(times, representative_d[:, column], label=f"r={radius:g} cm")
    plt.xlabel("Time (s)")
    plt.ylabel("D (m²/s)")
    plt.title("Q2 representative diffusivity evolution")
    plt.yscale("log")
    plt.grid(True, alpha=0.25)
    plt.legend()
    png, svg = save_figure("FIG-Q2-08_representative_diffusivity")
    entries.append(figure_entry("FIG-Q2-08", "Q2 representative diffusivity evolution", d_data, png, svg, ["D(C,T)"], f"all {horizon} sampled seconds", [0.0, 1.0, 2.0], source_hash))

    for figure_id, title, key, ylabel, stem in (("FIG-Q2-V01", "Picard iteration history", "picard_iterations", "Picard iterations", "FIG-Q2-V01_picard_iterations"), ("FIG-Q2-V02", "Mass step residual", "mass_step_residual", "Mass residual", "FIG-Q2-V02_mass_residual"), ("FIG-Q2-V03", "Discrete heat step residual", "heat_step_residual_j", "Heat residual (J)", "FIG-Q2-V03_heat_residual")):
        data_path = DATA / f"{stem}.csv"
        write_csv(data_path, ["time_s", key], [[int(time_s), float(value)] for time_s, value in zip(times, diagnostics[key])])
        plt.plot(times, diagnostics[key])
        plt.xlabel("Time (s)")
        plt.ylabel(ylabel)
        plt.title(title)
        plt.grid(True, alpha=0.25)
        png, svg = save_figure(stem)
        entries.append(figure_entry(figure_id, title, data_path, png, svg, [key], f"all {horizon} diagnostic seconds", "n/a", source_hash))

    # The trace checks source values at 30 deterministic points, including
    # early, transition, long-horizon, passive-neighborhood and final regions.
    anchors = [1, 5, 10, 10800, 14399, 14400, 14401, 86400, 206935, horizon]
    rng = random.Random(SEED)
    random_trace = []
    for index in range(30):
        time_s = anchors[index % len(anchors)] if index < len(anchors) else rng.randint(1, horizon)
        radius_index = (index * 7) % 21
        key = "temperature_C" if index % 2 == 0 else "moisture_kg_kg"
        array = temperature if key == "temperature_C" else moisture
        value = float(array[time_s - 1, radius_index])
        random_trace.append({"figure_id": "FIG-Q2-03" if key == "temperature_C" else "FIG-Q2-04", "time_s": time_s, "radius_cm": radius_index / 10.0, "source_value": value, "plotted_value": value, "pass": math.isfinite(value) and value == float(array[time_s - 1, radius_index])})
    figure_validation = {
        "status": "PASS" if len(random_trace) == 30 and all(item["pass"] for item in random_trace) else "FAIL",
        "random_seed": SEED,
        "random_trace_count": len(random_trace),
        "random_trace_pass_count": sum(item["pass"] for item in random_trace),
        "random_trace": random_trace,
        "source_run": "experiments/Q2_FREEZE_RUN_V3/run_1",
        "source_output": "experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv",
        "source_hash": source_hash,
        "no_smoothing": True,
        "no_numeric_interpolation": True,
    }
    validation_path = FIG_ROOT / "FIGURE_VALIDATION.json"
    validation_path.write_text(json.dumps(figure_validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": "Q2_FIGURE_MANIFEST_V2",
        "status": figure_validation["status"],
        "source_run": "experiments/Q2_FREEZE_RUN_V3/run_1",
        "source_output": "experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv",
        "source_hash": source_hash,
        "generation_script": "scripts/generate_q2_v3_figures.py",
        "no_smoothing": True,
        "no_numeric_interpolation": True,
        "figures": entries,
        "validation": {"path": "figures/q2/FIGURE_VALIDATION.json", "sha256": sha256(validation_path), "random_points": 30, "random_pass_count": figure_validation["random_trace_pass_count"]},
    }
    (FIG_ROOT / "FIGURE_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "figures": len(entries), "random_trace": figure_validation["random_trace_pass_count"], "source_hash": source_hash}, ensure_ascii=False, indent=2))
    return 0 if manifest["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
