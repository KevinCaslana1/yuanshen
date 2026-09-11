"""Generate the Q1 final figure package from the frozen run only.

The script never imports or calls the Q1 solver.  It reads the immutable
compressed output from ``Q1_FREEZE_RUN/run_1`` and deterministic validation
metrics for the two numerical-method figures.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import pickle
import random
import subprocess
import sys
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import openpyxl


ROOT = Path(__file__).resolve().parents[1]
FREEZE_REFERENCE = ROOT / "experiments" / "Q1_FREEZE_RUN" / "run_1" / "internal_output_reference.pkl.gz"
FINAL_RESULT = ROOT / "deliverables" / "final" / "result1.xlsx"
FIG_ROOT = ROOT / "figures" / "q1"
DATA_ROOT = FIG_ROOT / "data"
FINAL_FIG_ROOT = FIG_ROOT / "final"
EXPECTED_FREEZE_HASH = "f13667b5fe8e4c1e1a7635b18ab4c7aaa9e3fef5111b893a9ce79b6deb3fad17"
PAPER_TIMES_S = (100, 300, 600, 900, 1200, 1500, 1800)
PAPER_POSITIONS_CM = (0.0, 0.5, 1.0, 1.5, 2.0)
PAPER_POSITIONS_M = tuple(value / 100.0 for value in PAPER_POSITIONS_CM)
FIGURE_SCRIPT = "scripts/generate_q1_figures.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_freeze_payload() -> tuple[dict[str, Any], str]:
    actual_hash = sha256(FREEZE_REFERENCE)
    if actual_hash != EXPECTED_FREEZE_HASH:
        raise RuntimeError(
            "refusing to generate Q1 figures: freeze output hash mismatch "
            f"expected={EXPECTED_FREEZE_HASH} actual={actual_hash}"
        )
    with gzip.open(FREEZE_REFERENCE, "rb") as stream:
        payload = pickle.load(stream)
    if payload.get("schema_version") != "Q1_FREEZE_INTERNAL_OUTPUT_V1":
        raise RuntimeError(f"unsupported freeze payload schema: {payload.get('schema_version')!r}")
    return payload, actual_hash


def _time_index(times_s: np.ndarray, time_s: float) -> int:
    index = int(np.argmin(np.abs(times_s - time_s)))
    if abs(float(times_s[index]) - time_s) > 1.0e-9:
        raise ValueError(f"time {time_s} s is not present in the frozen output")
    return index


def _position_index(nodes_m: np.ndarray, position_m: float) -> int:
    index = int(np.argmin(np.abs(nodes_m - position_m)))
    if abs(float(nodes_m[index]) - position_m) > 1.0e-12:
        raise ValueError(f"position {position_m} m is not an explicit frozen output node")
    return index


def _write_csv(path: Path, headers: Iterable[str], rows: Iterable[Iterable[Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(tuple(headers))
        writer.writerows(rows)


def _round_half_up(value: float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def _save_figure(fig: Any, stem: str) -> tuple[Path, Path]:
    FINAL_FIG_ROOT.mkdir(parents=True, exist_ok=True)
    png_path = FINAL_FIG_ROOT / f"{stem}.png"
    svg_path = FINAL_FIG_ROOT / f"{stem}.svg"
    fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(svg_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return png_path, svg_path


def _base_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Arial Unicode MS", "DejaVu Sans"],
            "axes.unicode_minus": False,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 8.5,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def _plot_profile(
    figure_id: str,
    stem: str,
    title: str,
    ylabel: str,
    values: np.ndarray,
    times_s: np.ndarray,
    radius_cm: np.ndarray,
    value_key: str,
    source_hash: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    csv_path = DATA_ROOT / f"{stem}.csv"
    rows: list[list[Any]] = []
    raw_records: list[dict[str, Any]] = []
    colors = plt.get_cmap("viridis")(np.linspace(0.05, 0.95, len(PAPER_TIMES_S)))
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    for color, time_s in zip(colors, PAPER_TIMES_S):
        time_index = _time_index(times_s, time_s)
        line = values[time_index]
        ax.plot(
            radius_cm,
            line,
            color=color,
            linewidth=1.7,
            marker="o",
            markersize=2.6,
            markevery=max(1, len(radius_cm) // 16),
            label=f"{time_s} s",
        )
        for radius_value, value in zip(radius_cm, line):
            rows.append([time_s, f"{radius_value:.12g}", f"{float(value):.17g}"])
            raw_records.append(
                {
                    "figure_id": figure_id,
                    "time_s": int(time_s),
                    "distance_cm": float(radius_value),
                    "value": float(value),
                }
            )
    _write_csv(csv_path, ("time_s", "distance_cm", value_key), rows)
    ax.set_title(title)
    ax.set_xlabel("距药材中心的距离 / cm")
    ax.set_ylabel(ylabel)
    ax.set_xlim(0.0, 2.0)
    ax.grid(True, alpha=0.25, linewidth=0.6)
    ax.legend(loc="best", ncol=2, frameon=False)
    png_path, svg_path = _save_figure(fig, stem)
    return (
        {
            "figure_id": figure_id,
            "title": title,
            "source_run": "experiments/Q1_FREEZE_RUN/run_1/internal_output_reference.pkl.gz",
            "source_hash": source_hash,
            "variables": [value_key],
            "time_selection": list(PAPER_TIMES_S),
            "radius_selection": "all 339 frozen nodal positions, including official points",
            "data_file": str(csv_path.relative_to(ROOT)),
            "data_sha256": sha256(csv_path),
            "png_path": str(png_path.relative_to(ROOT)),
            "svg_path": str(svg_path.relative_to(ROOT)),
            "generation_script": FIGURE_SCRIPT,
        },
        raw_records,
    )


def _plot_heatmap(
    figure_id: str,
    stem: str,
    title: str,
    colorbar_label: str,
    values: np.ndarray,
    times_s: np.ndarray,
    radius_cm: np.ndarray,
    value_key: str,
    source_hash: str,
) -> dict[str, Any]:
    data_path = DATA_ROOT / f"{stem}.npz"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(data_path, times_s=times_s, radius_cm=radius_cm, values=values)
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    cmap = "inferno" if value_key == "temperature_c" else "YlGnBu"
    mesh = ax.pcolormesh(
        times_s,
        radius_cm,
        values.T,
        shading="nearest",
        cmap=cmap,
        rasterized=True,
    )
    colorbar = fig.colorbar(mesh, ax=ax, pad=0.02)
    colorbar.set_label(colorbar_label)
    ax.set_title(title)
    ax.set_xlabel("时间 / s")
    ax.set_ylabel("距药材中心的距离 / cm")
    ax.set_xlim(0.0, float(times_s[-1]))
    ax.set_ylim(0.0, 2.0)
    png_path, svg_path = _save_figure(fig, stem)
    return {
        "figure_id": figure_id,
        "title": title,
        "source_run": "experiments/Q1_FREEZE_RUN/run_1/internal_output_reference.pkl.gz",
        "source_hash": source_hash,
        "variables": [value_key],
        "time_selection": "all 7201 internal time layers, 0..1800 s at dt=0.25 s",
        "radius_selection": "all 339 frozen nodal positions",
        "data_file": str(data_path.relative_to(ROOT)),
        "data_sha256": sha256(data_path),
        "png_path": str(png_path.relative_to(ROOT)),
        "svg_path": str(svg_path.relative_to(ROOT)),
        "generation_script": FIGURE_SCRIPT,
    }


def _plot_history(
    figure_id: str,
    stem: str,
    title: str,
    ylabel: str,
    values: np.ndarray,
    times_s: np.ndarray,
    nodes_m: np.ndarray,
    value_key: str,
    source_hash: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    csv_path = DATA_ROOT / f"{stem}.csv"
    rows: list[list[Any]] = []
    raw_records: list[dict[str, Any]] = []
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    colors = plt.get_cmap("tab10")(np.linspace(0.0, 0.8, len(PAPER_POSITIONS_CM)))
    for color, position_cm, position_m in zip(colors, PAPER_POSITIONS_CM, PAPER_POSITIONS_M):
        position_index = _position_index(nodes_m, position_m)
        line = values[:, position_index]
        ax.plot(times_s, line, color=color, linewidth=1.6, label=f"r={position_cm:g} cm")
        for time_s, value in zip(times_s, line):
            rows.append([f"{float(time_s):.12g}", f"{position_cm:g}", f"{float(value):.17g}"])
            raw_records.append(
                {
                    "figure_id": figure_id,
                    "time_s": float(time_s),
                    "distance_cm": float(position_cm),
                    "value": float(value),
                }
            )
    _write_csv(csv_path, ("time_s", "distance_cm", value_key), rows)
    ax.set_title(title)
    ax.set_xlabel("时间 / s")
    ax.set_ylabel(ylabel)
    ax.set_xlim(0.0, 1800.0)
    ax.grid(True, alpha=0.25, linewidth=0.6)
    ax.legend(loc="best", ncol=2, frameon=False)
    png_path, svg_path = _save_figure(fig, stem)
    return (
        {
            "figure_id": figure_id,
            "title": title,
            "source_run": "experiments/Q1_FREEZE_RUN/run_1/internal_output_reference.pkl.gz",
            "source_hash": source_hash,
            "variables": [value_key],
            "time_selection": "all 7201 internal time layers, 0..1800 s at dt=0.25 s",
            "radius_selection": list(PAPER_POSITIONS_CM),
            "data_file": str(csv_path.relative_to(ROOT)),
            "data_sha256": sha256(csv_path),
            "png_path": str(png_path.relative_to(ROOT)),
            "svg_path": str(svg_path.relative_to(ROOT)),
            "generation_script": FIGURE_SCRIPT,
        },
        raw_records,
    )


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _plot_convergence(
    figure_id: str,
    stem: str,
    title: str,
    x_label: str,
    comparison_key: str,
    metric_key: str,
    source_paths: tuple[Path, Path],
) -> dict[str, Any]:
    spatial = _load_json(source_paths[0])
    temporal = _load_json(source_paths[1])
    metrics = spatial if metric_key == "spatial" else temporal
    source_path = source_paths[0] if metric_key == "spatial" else source_paths[1]
    observed = metrics[f"{metric_key}_observed_order_and_richardson"]
    comparisons = metrics[f"{metric_key}_comparisons"]
    if metric_key == "spatial":
        labels = ["base320→640", "base640→1280"]
        keys = ["Cluster-L1_vs_L2", "Cluster-L2_vs_L3"]
        x_values = [640, 1280]
    else:
        labels = ["dt .25→.125", "dt .125→.0625"]
        keys = ["dt0.5_vs_dt0.25", "dt0.25_vs_dt0.125"]
        x_values = [0.125, 0.0625]
    data_path = DATA_ROOT / f"{stem}.csv"
    rows: list[list[Any]] = []
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.6), sharey=False)
    field_labels = (("temperature_c", "温度 / °C"), ("moisture_kg_kg", "水分浓度 / (kg/kg)"))
    for axis, (field, field_label) in zip(axes, field_labels):
        y_values = []
        for label, key, x_value in zip(labels, keys, x_values):
            fine_error = observed[field]["full_grid" if metric_key == "spatial" else "full_grid"]
            # The two adjacent comparisons are stored in the raw comparison map;
            # the Richardson entry is stored for the corresponding fine case.
            comparison = comparisons[key]["fields"][field]["full_grid"]
            if metric_key == "spatial":
                observed_entry = observed[field]["full_grid"] if key.endswith("L2") else observed[field]["full_grid"]
            else:
                observed_entry = observed[field]["full_grid"]
            value = float(comparison["linf"])
            y_values.append(value)
            rows.append([metric_key, label, field, x_value, value, observed_entry.get("observed_order")])
        x_positions = list(range(len(x_values)))
        axis.plot(x_positions, y_values, marker="o", linewidth=1.8, color="#245a9b")
        axis.set_yscale("log")
        axis.set_title(field_label)
        axis.set_xlabel(x_label)
        axis.set_ylabel("相邻层 L∞ 差异")
        axis.grid(True, which="both", alpha=0.25, linewidth=0.6)
        axis.set_xticks(x_positions, labels, rotation=0)
        axis.set_xlim(-0.2, len(x_positions) - 0.8)
    fig.suptitle(title, y=1.02)
    fig.tight_layout()
    _write_csv(data_path, ("comparison_type", "refinement", "field", "x", "linf_difference", "observed_order"), rows)
    png_path, svg_path = _save_figure(fig, stem)
    return {
        "figure_id": figure_id,
        "title": title,
        "source_run": [str(path.relative_to(ROOT)) for path in source_paths],
        "source_hash": [sha256(path) for path in source_paths],
        "variables": ["temperature_c", "moisture_kg_kg"],
        "time_selection": "full-horizon validation evidence, 1..1800 s",
        "radius_selection": "full official 1800×21 grid",
        "data_file": str(data_path.relative_to(ROOT)),
        "data_sha256": sha256(data_path),
        "png_path": str(png_path.relative_to(ROOT)),
        "svg_path": str(svg_path.relative_to(ROOT)),
        "generation_script": FIGURE_SCRIPT,
    }


def _plot_surface_decay(source_path: Path) -> dict[str, Any]:
    metrics = _load_json(source_path)
    by_time = metrics["N640_vs_N1280"]["by_time"]
    data_path = DATA_ROOT / "fig_q1_v02_initial_layer_surface_decay.csv"
    rows = [[item["time_s"], item["r1.9cm_abs"], item["r2.0cm_abs"]] for item in by_time]
    _write_csv(data_path, ("time_s", "r1.9cm_abs", "r2.0cm_abs"), rows)
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    time_values = [item[0] for item in rows]
    ax.plot(time_values, [item[1] for item in rows], linewidth=1.7, label="r=1.9 cm")
    ax.plot(time_values, [item[2] for item in rows], linewidth=1.7, label="r=2.0 cm")
    ax.set_yscale("log")
    ax.set_title("早期表面水分数值误差衰减")
    ax.set_xlabel("时间 / s")
    ax.set_ylabel("N640→N1280 绝对差异 / (kg/kg)")
    ax.grid(True, which="both", alpha=0.25, linewidth=0.6)
    ax.legend(frameon=False)
    png_path, svg_path = _save_figure(fig, "FIG-Q1-V02_initial_layer_surface_decay")
    return {
        "figure_id": "FIG-Q1-V02",
        "title": "早期表面水分数值误差衰减",
        "source_run": str(source_path.relative_to(ROOT)),
        "source_hash": sha256(source_path),
        "variables": ["surface_moisture_numerical_error"],
        "time_selection": "1..100 s",
        "radius_selection": [1.9, 2.0],
        "data_file": str(data_path.relative_to(ROOT)),
        "data_sha256": sha256(data_path),
        "png_path": str(png_path.relative_to(ROOT)),
        "svg_path": str(svg_path.relative_to(ROOT)),
        "generation_script": FIGURE_SCRIPT,
    }


def _paper_spot_check(
    values: dict[str, np.ndarray],
    times_s: np.ndarray,
    nodes_m: np.ndarray,
) -> dict[str, Any]:
    workbook = openpyxl.load_workbook(FINAL_RESULT, read_only=True, data_only=False)
    try:
        checks: list[dict[str, Any]] = []
        for sheet_name, field_name in (("温度", "temperature_c"), ("水分浓度", "moisture_kg_kg")):
            sheet = workbook[sheet_name]
            field = values[field_name]
            for time_s in PAPER_TIMES_S:
                time_index = _time_index(times_s, time_s)
                for position_cm, position_m in zip(PAPER_POSITIONS_CM, PAPER_POSITIONS_M):
                    position_index = _position_index(nodes_m, position_m)
                    raw_value = float(field[time_index, position_index])
                    expected = _round_half_up(raw_value)
                    actual = Decimal(str(sheet.cell(row=time_s + 1, column=2 + int(round(position_cm * 10))).value))
                    checks.append({"sheet": sheet_name, "time_s": time_s, "distance_cm": position_cm, "pass": actual == expected})
        passed = sum(item["pass"] for item in checks)
        return {"count": len(checks), "pass_count": passed, "status": "PASS" if passed == len(checks) else "FAIL"}
    finally:
        workbook.close()


def _figure_data_spot_check(
    records: list[dict[str, Any]],
    values: dict[str, np.ndarray],
    times_s: np.ndarray,
    nodes_m: np.ndarray,
) -> dict[str, Any]:
    rng = random.Random(20260911)
    sample = rng.sample(records, 20)
    checks: list[dict[str, Any]] = []
    for item in sample:
        field_name = "temperature_c" if item["figure_id"] in {"FIG-Q1-01", "FIG-Q1-05"} else "moisture_kg_kg"
        time_index = _time_index(times_s, item["time_s"])
        position_index = _position_index(nodes_m, item["distance_cm"] / 100.0)
        expected = float(values[field_name][time_index, position_index])
        checks.append({"figure_id": item["figure_id"], "time_s": item["time_s"], "distance_cm": item["distance_cm"], "pass": abs(expected - item["value"]) <= 1.0e-12})
    passed = sum(item["pass"] for item in checks)
    return {"seed": 20260911, "count": len(checks), "pass_count": passed, "status": "PASS" if passed == len(checks) else "FAIL", "checks": checks}


def main() -> int:
    _base_style()
    payload, source_hash = load_freeze_payload()
    times_s = np.asarray(payload["times_s"], dtype=float)
    nodes_m = np.asarray(payload["grid"]["nodes_m"], dtype=float)
    radius_cm = nodes_m * 100.0
    temperature_c = np.asarray(payload["temperatures_k"], dtype=float) - 273.15
    moisture = np.asarray(payload["moistures_kg_kg"], dtype=float)
    if temperature_c.shape != (7201, 339) or moisture.shape != (7201, 339):
        raise RuntimeError(f"unexpected freeze field shape: temperature={temperature_c.shape} moisture={moisture.shape}")

    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    figures: list[dict[str, Any]] = []
    core_records: list[dict[str, Any]] = []
    figure, records = _plot_profile(
        "FIG-Q1-01",
        "FIG-Q1-01_temperature_radial_profiles",
        "不同时刻药材内部温度径向分布",
        "温度 / °C",
        temperature_c,
        times_s,
        radius_cm,
        "temperature_c",
        source_hash,
    )
    figures.append(figure)
    core_records.extend(records)
    figure, records = _plot_profile(
        "FIG-Q1-02",
        "FIG-Q1-02_moisture_radial_profiles",
        "不同时刻药材内部水分浓度径向分布",
        "水分浓度 / (kg/kg)",
        moisture,
        times_s,
        radius_cm,
        "moisture_kg_kg",
        source_hash,
    )
    figures.append(figure)
    core_records.extend(records)
    figures.append(
        _plot_heatmap(
            "FIG-Q1-03",
            "FIG-Q1-03_temperature_time_radius_heatmap",
            "药材内部温度时空分布",
            "温度 / °C",
            temperature_c,
            times_s,
            radius_cm,
            "temperature_c",
            source_hash,
        )
    )
    figures.append(
        _plot_heatmap(
            "FIG-Q1-04",
            "FIG-Q1-04_moisture_time_radius_heatmap",
            "药材内部水分浓度时空分布",
            "水分浓度 / (kg/kg)",
            moisture,
            times_s,
            radius_cm,
            "moisture_kg_kg",
            source_hash,
        )
    )
    figure, records = _plot_history(
        "FIG-Q1-05",
        "FIG-Q1-05_temperature_time_histories",
        "不同径向位置温度随时间的变化",
        "温度 / °C",
        temperature_c,
        times_s,
        nodes_m,
        "temperature_c",
        source_hash,
    )
    figures.append(figure)
    core_records.extend(records)
    figure, records = _plot_history(
        "FIG-Q1-06",
        "FIG-Q1-06_moisture_time_histories",
        "不同径向位置水分浓度随时间的变化",
        "水分浓度 / (kg/kg)",
        moisture,
        times_s,
        nodes_m,
        "moisture_kg_kg",
        source_hash,
    )
    figures.append(figure)
    core_records.extend(records)

    spatial_metrics = ROOT / "experiments" / "EXP-Q1-FULL-SPATIAL" / "metrics.json"
    temporal_metrics = ROOT / "experiments" / "EXP-Q1-FULL-TEMPORAL" / "metrics.json"
    surface_metrics = ROOT / "experiments" / "EXP-Q1-SURFACE-DECAY" / "metrics.json"
    figures.append(
        _plot_convergence(
            "FIG-Q1-V01a",
            "FIG-Q1-V01a_spatial_convergence",
            "Q1 空间收敛性检验",
            "细网格区间",
            "spatial",
            "spatial",
            (spatial_metrics, temporal_metrics),
        )
    )
    figures.append(
        _plot_convergence(
            "FIG-Q1-V01b",
            "FIG-Q1-V01b_temporal_convergence",
            "Q1 时间收敛性检验",
            "时间步长细化",
            "temporal",
            "temporal",
            (spatial_metrics, temporal_metrics),
        )
    )
    figures.append(_plot_surface_decay(surface_metrics))

    paper_check = _paper_spot_check({"temperature_c": temperature_c, "moisture_kg_kg": moisture}, times_s, nodes_m)
    figure_check = _figure_data_spot_check(core_records, {"temperature_c": temperature_c, "moisture_kg_kg": moisture}, times_s, nodes_m)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    for figure in figures:
        figure["commit"] = commit
        figure["generated_at"] = generated_at
    manifest = {
        "schema_version": "Q1_FIGURE_MANIFEST_V1",
        "status": "PASS" if paper_check["status"] == "PASS" and figure_check["status"] == "PASS" else "FAIL",
        "source_run": str(FREEZE_REFERENCE.relative_to(ROOT)),
        "source_hash": source_hash,
        "generation_script": FIGURE_SCRIPT,
        "commit": commit,
        "generated_at": generated_at,
        "figures": figures,
        "validation": {
            "paper_official_point_spot_check": paper_check,
            "random_figure_data_spot_check": figure_check,
        },
    }
    FIG_ROOT.mkdir(parents=True, exist_ok=True)
    (FIG_ROOT / "FIGURE_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (FIG_ROOT / "FIGURE_VALIDATION.json").write_text(json.dumps(manifest["validation"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "figure_count": len(figures), "paper_points": paper_check, "random_points": {key: value for key, value in figure_check.items() if key != "checks"}}, ensure_ascii=False, indent=2))
    return 0 if manifest["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
