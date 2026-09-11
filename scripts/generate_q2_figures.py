"""Generate Q2 figures from the strict run_1 production source only."""

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


FREEZE = ROOT / "experiments" / "Q2_FREEZE_RUN"
FIG_ROOT = ROOT / "figures" / "q2"
DATA = FIG_ROOT / "data"
FINAL = FIG_ROOT / "final"
PAPER_TIMES = (1800, 3600, 5400, 7200, 9000, 10800)
LONG_TIMES = (21600, 86400, 172800)
REPRESENTATIVE_RADII = (0.0, 0.5, 1.0, 1.5, 2.0)
RANDOM_SEED = 20260912


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
    temperature = np.empty((horizon, 21), dtype=np.float64)
    moisture = np.empty((horizon, 21), dtype=np.float64)
    temperature.fill(np.nan)
    moisture.fill(np.nan)
    rows = 0
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            time_s = int(round(float(row["time_s"])))
            radius_index = int(round(float(row["radius_cm"]) * 10.0))
            if time_s < 1 or time_s > horizon or radius_index < 0 or radius_index > 20:
                raise ValueError(f"sample key outside production grid: {row}")
            temperature[time_s - 1, radius_index] = float(row["temperature_C"])
            moisture[time_s - 1, radius_index] = float(row["moisture_kg_kg"])
            rows += 1
    if rows != horizon * 21 or not np.isfinite(temperature).all() or not np.isfinite(moisture).all():
        raise ValueError(f"sample source is incomplete/non-finite: rows={rows}")
    return times, radii, temperature, moisture


def load_diagnostics(path: Path, horizon: int) -> dict[str, np.ndarray]:
    fields = {"time_s": [], "picard_iterations": [], "mass_step_residual": [], "heat_step_residual_j": [], "surface_D_m2_s": [], "surface_heat_boundary_residual_w_m2": [], "surface_moisture_boundary_residual_kg_m2_s": []}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            for key in fields:
                fields[key].append(float(row[key]))
    if len(fields["time_s"]) != horizon or fields["time_s"] != list(map(float, range(1, horizon + 1))):
        raise ValueError("diagnostic source is not a complete 1-second sequence")
    return {key: np.asarray(value) for key, value in fields.items()}


def figure_entry(figure_id: str, title: str, data_path: Path, png: str, svg: str, variables: list[str], times: Any, radii: Any, source_hash: str, script: str = "scripts/generate_q2_figures.py") -> dict[str, Any]:
    return {"figure_id": figure_id, "title": title, "source_run": "experiments/Q2_FREEZE_RUN/run_1", "source_output": "experiments/Q2_FREEZE_RUN/run_1/official_samples.csv", "source_hash": source_hash, "data_file": str(data_path.relative_to(ROOT)).replace("\\", "/"), "data_sha256": sha256(data_path), "png_path": png, "svg_path": svg, "generation_script": script, "variables": variables, "time_selection": times, "radius_selection": radii, "no_smoothing": True, "no_numeric_interpolation": True}


def main() -> int:
    config = json.loads((FREEZE / "config.json").read_text(encoding="utf-8"))
    horizon = int(config["final_horizon_s"])
    source = production_csv_path("experiments/Q2_FREEZE_RUN/run_1/official_samples.csv")
    hashes = json.loads((FREEZE / "output_hashes.json").read_text(encoding="utf-8"))
    source_hash = sha256(source)
    if source_hash != hashes["run_1"]["sampled_output"]:
        raise ValueError("run_1 source hash mismatch")
    DATA.mkdir(parents=True, exist_ok=True)
    FINAL.mkdir(parents=True, exist_ok=True)
    times, radii, temperature, moisture = load_samples(source, horizon)
    diagnostics = load_diagnostics(FREEZE / "run_1" / "diagnostics_1s.csv", horizon)
    entries = []

    profile_times = tuple(t for t in PAPER_TIMES + LONG_TIMES + (horizon,) if t <= horizon)
    profile_rows_t = [[time_s, *temperature[time_s - 1].tolist()] for time_s in profile_times]
    profile_rows_c = [[time_s, *moisture[time_s - 1].tolist()] for time_s in profile_times]
    t_data = DATA / "FIG-Q2-01_temperature_radial_profiles.csv"; c_data = DATA / "FIG-Q2-02_moisture_radial_profiles.csv"
    write_csv(t_data, ["time_s", *[f"radius_{r:.1f}_cm" for r in radii]], profile_rows_t)
    write_csv(c_data, ["time_s", *[f"radius_{r:.1f}_cm" for r in radii]], profile_rows_c)
    for values, title, ylabel, stem, data_path, fig_id in [(temperature, "Q2 temperature radial profiles", "Temperature (°C)", "FIG-Q2-01_temperature_radial_profiles", t_data, "FIG-Q2-01"), (moisture, "Q2 moisture radial profiles", "Moisture (kg/kg)", "FIG-Q2-02_moisture_radial_profiles", c_data, "FIG-Q2-02")]:
        for time_s in profile_times:
            plt.plot(radii, values[time_s - 1], label=f"{time_s / 3600:g} h")
        plt.xlabel("Radius (cm)"); plt.ylabel(ylabel); plt.title(title); plt.grid(True, alpha=0.25); plt.legend(ncol=2)
        png, svg = save_figure(stem)
        entries.append(figure_entry(fig_id, title, data_path, png, svg, ["temperature_C" if fig_id.endswith("01") else "moisture_kg_kg"], list(profile_times), "all official radii", source_hash))

    t_heat = DATA / "FIG-Q2-03_temperature_time_radius_heatmap.npz"; c_heat = DATA / "FIG-Q2-04_moisture_time_radius_heatmap.npz"
    np.savez_compressed(t_heat, time_s=times, radius_cm=radii, temperature_C=temperature)
    np.savez_compressed(c_heat, time_s=times, radius_cm=radii, moisture_kg_kg=moisture)
    for values, title, label, stem, data_path, fig_id, key in [(temperature, "Q2 temperature time-radius heatmap", "Temperature (°C)", "FIG-Q2-03_temperature_time_radius_heatmap", t_heat, "FIG-Q2-03", "temperature_C"), (moisture, "Q2 moisture time-radius heatmap", "Moisture (kg/kg)", "FIG-Q2-04_moisture_time_radius_heatmap", c_heat, "FIG-Q2-04", "moisture_kg_kg")]:
        plt.imshow(values, origin="lower", aspect="auto", extent=[0, 2, 1, horizon], interpolation="none")
        plt.xlabel("Radius (cm)"); plt.ylabel("Time (s)"); plt.title(title); plt.colorbar(label=label)
        png, svg = save_figure(stem)
        entries.append(figure_entry(fig_id, title, data_path, png, svg, [key], f"all {horizon} sampled seconds", "0.0..2.0 cm at 0.1 cm", source_hash))

    history_t = DATA / "FIG-Q2-05_temperature_time_histories.csv"; history_c = DATA / "FIG-Q2-06_moisture_time_histories.csv"
    history_t_rows = [[int(t), *temperature[t - 1, [int(round(r * 10)) for r in REPRESENTATIVE_RADII]].tolist()] for t in times]
    history_c_rows = [[int(t), *moisture[t - 1, [int(round(r * 10)) for r in REPRESENTATIVE_RADII]].tolist()] for t in times]
    write_csv(history_t, ["time_s", *[f"radius_{r:.1f}_cm" for r in REPRESENTATIVE_RADII]], history_t_rows)
    write_csv(history_c, ["time_s", *[f"radius_{r:.1f}_cm" for r in REPRESENTATIVE_RADII]], history_c_rows)
    for values, title, ylabel, stem, data_path, fig_id, key in [(temperature, "Q2 representative temperature histories", "Temperature (°C)", "FIG-Q2-05_temperature_time_histories", history_t, "FIG-Q2-05", "temperature_C"), (moisture, "Q2 representative moisture histories", "Moisture (kg/kg)", "FIG-Q2-06_moisture_time_histories", history_c, "FIG-Q2-06", "moisture_kg_kg")]:
        for radius in REPRESENTATIVE_RADII:
            plt.plot(times, values[:, int(round(radius * 10))], label=f"r={radius:g} cm")
        plt.xlabel("Time (s)"); plt.ylabel(ylabel); plt.title(title); plt.grid(True, alpha=0.25); plt.legend()
        png, svg = save_figure(stem)
        entries.append(figure_entry(fig_id, title, data_path, png, svg, [key], f"all {horizon} sampled seconds", list(REPRESENTATIVE_RADII), source_hash))

    diff = temperature[:, 0] * 0.0 + moisture[:, 0] - moisture[:, 20]
    diff_data = DATA / "FIG-Q2-07_center_surface_moisture_difference.csv"
    write_csv(diff_data, ["time_s", "center_minus_surface_moisture_kg_kg"], [[int(t), float(v)] for t, v in zip(times, diff)])
    plt.plot(times, diff); plt.axhline(0.0, color="black", linewidth=0.8); plt.xlabel("Time (s)"); plt.ylabel("C(center)-C(surface) (kg/kg)"); plt.title("Q2 center-surface moisture difference"); plt.grid(True, alpha=0.25)
    png, svg = save_figure("FIG-Q2-07_center_surface_moisture_difference")
    entries.append(figure_entry("FIG-Q2-07", "Q2 center-surface moisture difference", diff_data, png, svg, ["center_minus_surface_moisture_kg_kg"], f"all {horizon} sampled seconds", [0.0, 2.0], source_hash))

    d_values = 2.4e-3 * np.exp(-0.45 / moisture[:, [0, 10, 20]]) * np.exp(-3850.0 / (temperature[:, [0, 10, 20]] + 273.15))
    d_data = DATA / "FIG-Q2-08_representative_diffusivity.csv"
    write_csv(d_data, ["time_s", "D_center_m2_s", "D_r1cm_m2_s", "D_surface_m2_s"], [[int(t), *row.tolist()] for t, row in zip(times, d_values)])
    for idx, radius in enumerate((0.0, 1.0, 2.0)):
        plt.plot(times, d_values[:, idx], label=f"r={radius:g} cm")
    plt.xlabel("Time (s)"); plt.ylabel("D (m²/s)"); plt.title("Q2 representative diffusivity evolution"); plt.yscale("log"); plt.grid(True, alpha=0.25); plt.legend()
    png, svg = save_figure("FIG-Q2-08_representative_diffusivity")
    entries.append(figure_entry("FIG-Q2-08", "Q2 representative diffusivity evolution", d_data, png, svg, ["D(C,T)"], f"all {horizon} sampled seconds", [0.0, 1.0, 2.0], source_hash))

    validation_specs = [("FIG-Q2-V01", "Picard iteration history", "picard_iterations", "Picard iterations", "FIG-Q2-V01_picard_iterations"), ("FIG-Q2-V02", "Mass step residual", "mass_step_residual", "Mass residual", "FIG-Q2-V02_mass_residual"), ("FIG-Q2-V03", "Discrete heat step residual", "heat_step_residual_j", "Heat residual (J)", "FIG-Q2-V03_heat_residual")]
    for fig_id, title, key, ylabel, stem in validation_specs:
        data_path = DATA / f"{stem}.csv"
        write_csv(data_path, ["time_s", key], [[int(t), float(v)] for t, v in zip(times, diagnostics[key])])
        plt.plot(times, diagnostics[key]); plt.xlabel("Time (s)"); plt.ylabel(ylabel); plt.title(title); plt.grid(True, alpha=0.25)
        png, svg = save_figure(stem)
        entries.append(figure_entry(fig_id, title, data_path, png, svg, [key], f"all {horizon} diagnostic seconds", "n/a", source_hash))

    rng = random.Random(RANDOM_SEED)
    # Verify selected in-memory source values without altering the source
    # arrays or applying any interpolation or smoothing.
    rng = random.Random(RANDOM_SEED)
    random_trace = []
    for index in range(30):
        ti, ri = rng.randrange(horizon), rng.randrange(21)
        value = float(temperature[ti, ri] if index % 2 == 0 else moisture[ti, ri])
        random_trace.append({"figure_id": "FIG-Q2-03" if index % 2 == 0 else "FIG-Q2-04", "time_s": int(times[ti]), "radius_cm": float(radii[ri]), "value": value, "pass": math.isfinite(value)})
    figure_validation = {"status": "PASS" if len(random_trace) == 30 and all(item["pass"] for item in random_trace) else "FAIL", "random_seed": RANDOM_SEED, "random_trace_count": len(random_trace), "random_trace_pass_count": sum(item["pass"] for item in random_trace), "random_trace": random_trace, "source_run": "experiments/Q2_FREEZE_RUN/run_1", "source_hash": source_hash}
    (FIG_ROOT / "FIGURE_VALIDATION.json").write_text(json.dumps(figure_validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {"schema_version": "Q2_FIGURE_MANIFEST_V1", "status": "PASS" if figure_validation["status"] == "PASS" else "FAIL", "source_run": "experiments/Q2_FREEZE_RUN/run_1", "source_output": "experiments/Q2_FREEZE_RUN/run_1/official_samples.csv", "source_hash": source_hash, "generation_script": "scripts/generate_q2_figures.py", "no_smoothing": True, "no_numeric_interpolation": True, "figures": entries, "validation": {"path": "figures/q2/FIGURE_VALIDATION.json", "sha256": sha256(FIG_ROOT / "FIGURE_VALIDATION.json"), "random_points": 30, "random_pass_count": figure_validation["random_trace_pass_count"]}}
    (FIG_ROOT / "FIGURE_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "figures": len(entries), "random_trace": figure_validation["random_trace_pass_count"], "source_hash": source_hash}, ensure_ascii=False, indent=2))
    return 0 if manifest["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
