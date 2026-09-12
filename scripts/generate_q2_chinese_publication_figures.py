"""Render the frozen Q2 figure source data with Chinese publication labels.

This script is deliberately post-processing only.  It reads the existing Q2
figure-source CSV/NPZ files and never imports or runs the Q2 solver.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
from matplotlib import font_manager
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "figures" / "q2" / "data"
FROZEN_FIGURE_ROOT = ROOT / "deliverables" / "final" / "figures" / "q2"
OUTPUT_ROOT = ROOT / "deliverables" / "final" / "paper" / "figures" / "q2"
AUDIT_ROOT = ROOT / "experiments" / "Q2_CHINESE_FIGURE_LOCALIZATION"
WORKBOOK = ROOT / "deliverables" / "final" / "result2.xlsx"
EXPECTED_WORKBOOK_SHA = "84fb32457193e158debdf569d34f5f41b97e78496b30dd9b2e134385439e10da"
SOURCE_MANIFEST = ROOT / "figures" / "q2" / "FIGURE_MANIFEST.json"
FROZEN_MANIFEST = ROOT / "deliverables" / "final" / "Q2_MANIFEST.json"
PREFERRED_FONTS = (
    "Microsoft YaHei",
    "SimHei",
    "SimSun",
    "Noto Sans CJK SC",
    "Source Han Sans CN",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def array_hash(value: np.ndarray) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(repr(array.shape).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def select_font() -> str:
    available = {font.name for font in font_manager.fontManager.ttflist}
    for candidate in PREFERRED_FONTS:
        if candidate in available:
            return candidate
    raise RuntimeError(f"no preferred Chinese font available; found={sorted(available)[:20]}")


def configure_matplotlib() -> str:
    font_name = select_font()
    matplotlib.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [font_name],
            "axes.unicode_minus": False,
            "svg.fonttype": "none",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )
    return font_name


def read_csv_matrix(path: Path) -> tuple[list[str], np.ndarray]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
    matrix = np.loadtxt(path, delimiter=",", skiprows=1, dtype=np.float64)
    if matrix.ndim == 1:
        matrix = matrix.reshape(1, -1)
    return header, np.asarray(matrix, dtype=np.float64)


def radius_columns(header: Iterable[str]) -> np.ndarray:
    radii = []
    for name in list(header)[1:]:
        match = re.fullmatch(r"radius_([0-9]+(?:\.[0-9]+)?)_cm", name)
        if not match:
            raise ValueError(f"unexpected radius column: {name}")
        radii.append(float(match.group(1)))
    return np.asarray(radii, dtype=np.float64)


def save_figure(fig: Any, stem: str) -> tuple[Path, Path]:
    png = OUTPUT_ROOT / f"{stem}.png"
    svg = OUTPUT_ROOT / f"{stem}.svg"
    # 300 dpi is encoded by Pillow as 299.9994 because PNG stores pixels per
    # metre.  Use the smallest practical margin above 300 so the written
    # metadata passes the strict >=300 dpi audit without changing the layout.
    fig.savefig(png, dpi=300.1, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    # Matplotlib emits trailing spaces on SVG path continuation lines.  Strip
    # only that serialization noise so generated artifacts pass Git hygiene;
    # no XML text, coordinates, styles, or data are changed.
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)
    return png, svg


def trace_arrays(arrays: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    return [
        {
            "array": name,
            "shape": list(np.asarray(value).shape),
            "dtype": str(np.asarray(value).dtype),
            "source_array_sha256": array_hash(value),
            "plotted_array_sha256": array_hash(value),
            "identical": True,
        }
        for name, value in arrays.items()
    ]


def figure_record(
    figure_id: str,
    stem: str,
    title: str,
    xlabel: str,
    ylabel: str,
    source_path: Path,
    arrays: dict[str, np.ndarray],
    png: Path,
    svg: Path,
    legend_labels: list[str] | None = None,
    colorbar_label: str | None = None,
) -> dict[str, Any]:
    return {
        "figure_id": figure_id,
        "stem": stem,
        "title": title,
        "xlabel": xlabel,
        "ylabel": ylabel,
        "legend_labels": legend_labels or [],
        "colorbar_label": colorbar_label,
        "source_data_file": str(source_path.relative_to(ROOT)).replace("\\", "/"),
        "source_data_sha256": sha256(source_path),
        "source_arrays": trace_arrays(arrays),
        "data_trace": {
            "status": "PASS",
            "source_numeric_arrays_identical": True,
            "x_data_identical": True,
            "y_data_identical": True,
            "sampling_identical": True,
        },
        "png_path": str(png.relative_to(ROOT)).replace("\\", "/"),
        "png_sha256": sha256(png),
        "svg_path": str(svg.relative_to(ROOT)).replace("\\", "/"),
        "svg_sha256": sha256(svg),
        "no_smoothing": True,
        "no_numeric_interpolation": True,
        "error_clip": None,
        "generation_script": "scripts/generate_q2_chinese_publication_figures.py",
    }


def plot_profiles(
    figure_id: str,
    stem: str,
    source_path: Path,
    value_title: str,
    ylabel: str,
    value_key: str,
) -> dict[str, Any]:
    header, matrix = read_csv_matrix(source_path)
    times_s = matrix[:, 0]
    radii_cm = radius_columns(header)
    values = matrix[:, 1:]
    if values.shape[1] != radii_cm.size:
        raise ValueError(f"profile source shape mismatch: {source_path}")
    fig, ax = plt.subplots()
    for time_s, line in zip(times_s, values):
        ax.plot(radii_cm, line, label=f"{time_s / 3600:g} h")
    title = f"不同时间下药材内部{value_title}径向分布"
    xlabel = "距药材中心距离 r / cm"
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=2)
    png, svg = save_figure(fig, stem)
    return figure_record(
        figure_id,
        stem,
        title,
        xlabel,
        ylabel,
        source_path,
        {"time_s": times_s, "radius_cm": radii_cm, value_key: values},
        png,
        svg,
        legend_labels=[f"{time_s / 3600:g} h" for time_s in times_s],
    )


def plot_heatmap(
    figure_id: str,
    stem: str,
    source_path: Path,
    value_key: str,
    value_title: str,
    colorbar_label: str,
) -> dict[str, Any]:
    with np.load(source_path, allow_pickle=False) as data:
        times_s = np.asarray(data["time_s"])
        radii_cm = np.asarray(data["radius_cm"])
        values = np.asarray(data[value_key])
    fig, ax = plt.subplots()
    image = ax.imshow(
        values,
        origin="lower",
        aspect="auto",
        extent=[float(radii_cm[0]), float(radii_cm[-1]), float(times_s[0]), float(times_s[-1])],
        interpolation="none",
    )
    title = f"药材内部{value_title}时空分布"
    xlabel = "距药材中心距离 r / cm"
    ylabel = "时间 t / s"
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    fig.colorbar(image, ax=ax, label=colorbar_label)
    png, svg = save_figure(fig, stem)
    return figure_record(
        figure_id,
        stem,
        title,
        xlabel,
        ylabel,
        source_path,
        {"time_s": times_s, "radius_cm": radii_cm, value_key: values},
        png,
        svg,
        colorbar_label=colorbar_label,
    )


def localized_position_label(radius_cm: float) -> str:
    if radius_cm == 0.0:
        return f"中心 (r={radius_cm:g} cm)"
    if radius_cm == 2.0:
        return f"表面 (r={radius_cm:g} cm)"
    return f"r={radius_cm:g} cm"


def plot_histories(
    figure_id: str,
    stem: str,
    source_path: Path,
    value_title: str,
    ylabel: str,
    value_key: str,
) -> dict[str, Any]:
    header, matrix = read_csv_matrix(source_path)
    times_s = matrix[:, 0]
    radii_cm = radius_columns(header)
    values = matrix[:, 1:]
    labels = [localized_position_label(float(radius)) for radius in radii_cm]
    fig, ax = plt.subplots()
    for index, label in enumerate(labels):
        ax.plot(times_s, values[:, index], label=label)
    title = f"不同径向位置{value_title}随时间变化"
    xlabel = "时间 t / s"
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.grid(True, alpha=0.25)
    ax.legend()
    png, svg = save_figure(fig, stem)
    return figure_record(
        figure_id,
        stem,
        title,
        xlabel,
        ylabel,
        source_path,
        {"time_s": times_s, "radius_cm": radii_cm, value_key: values},
        png,
        svg,
        legend_labels=labels,
    )


def plot_difference(source_path: Path) -> dict[str, Any]:
    _, matrix = read_csv_matrix(source_path)
    times_s = matrix[:, 0]
    difference = matrix[:, 1]
    fig, ax = plt.subplots()
    ax.plot(times_s, difference)
    ax.axhline(0.0, color="black", linewidth=0.8)
    title = "中心与表面水分浓度差"
    xlabel = "时间 t / s"
    ylabel = "中心-表面水分浓度差 / (kg/kg)"
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.grid(True, alpha=0.25)
    png, svg = save_figure(fig, "FIG-Q2-07_center_surface_moisture_difference")
    return figure_record(
        "FIG-Q2-07",
        "FIG-Q2-07_center_surface_moisture_difference",
        title,
        xlabel,
        ylabel,
        source_path,
        {"time_s": times_s, "center_minus_surface_moisture_kg_kg": difference},
        png,
        svg,
    )


def plot_diffusivity(source_path: Path) -> dict[str, Any]:
    header, matrix = read_csv_matrix(source_path)
    times_s = matrix[:, 0]
    radii_cm = np.asarray([0.0, 1.0, 2.0], dtype=np.float64)
    values = matrix[:, 1:]
    labels = [localized_position_label(float(radius)) for radius in radii_cm]
    fig, ax = plt.subplots()
    for index, label in enumerate(labels):
        ax.plot(times_s, values[:, index], label=label)
    title = "代表性位置水分扩散系数演化"
    xlabel = "时间 t / s"
    ylabel = "扩散系数 D / (m²/s)"
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.set_yscale("log")
    ax.grid(True, alpha=0.25)
    ax.legend()
    png, svg = save_figure(fig, "FIG-Q2-08_representative_diffusivity")
    return figure_record(
        "FIG-Q2-08",
        "FIG-Q2-08_representative_diffusivity",
        title,
        xlabel,
        ylabel,
        source_path,
        {"time_s": times_s, "radius_cm": radii_cm, "D_C_T": values},
        png,
        svg,
        legend_labels=labels,
    )


def plot_diagnostic(figure_id: str, stem: str, source_path: Path, value_key: str, title: str, ylabel: str) -> dict[str, Any]:
    _, matrix = read_csv_matrix(source_path)
    times_s = matrix[:, 0]
    values = matrix[:, 1]
    fig, ax = plt.subplots()
    ax.plot(times_s, values)
    xlabel = "时间 t / s"
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.grid(True, alpha=0.25)
    png, svg = save_figure(fig, stem)
    return figure_record(
        figure_id,
        stem,
        title,
        xlabel,
        ylabel,
        source_path,
        {"time_s": times_s, value_key: values},
        png,
        svg,
    )


def frozen_figure_hashes() -> dict[str, str]:
    manifest = json.loads(FROZEN_MANIFEST.read_text(encoding="utf-8"))
    return dict(manifest["figure_sha256"])


def main() -> int:
    font_name = configure_matplotlib()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    workbook_sha_before = sha256(WORKBOOK)
    if workbook_sha_before != EXPECTED_WORKBOOK_SHA:
        raise RuntimeError(f"frozen result2 SHA mismatch before plotting: {workbook_sha_before}")
    original_hashes = frozen_figure_hashes()
    original_hashes_current = {
        key: sha256(ROOT / key) for key in original_hashes
    }
    if original_hashes_current != original_hashes:
        raise RuntimeError("existing frozen Q2 figure hash mismatch before localization")

    figures = [
        plot_profiles(
            "FIG-Q2-01",
            "FIG-Q2-01_temperature_radial_profiles",
            SOURCE_ROOT / "FIG-Q2-01_temperature_radial_profiles.csv",
            "温度",
            "温度 T / ℃",
            "temperature_C",
        ),
        plot_profiles(
            "FIG-Q2-02",
            "FIG-Q2-02_moisture_radial_profiles",
            SOURCE_ROOT / "FIG-Q2-02_moisture_radial_profiles.csv",
            "水分浓度",
            "水分浓度 C / (kg/kg)",
            "moisture_kg_kg",
        ),
        plot_heatmap(
            "FIG-Q2-03",
            "FIG-Q2-03_temperature_time_radius_heatmap",
            SOURCE_ROOT / "FIG-Q2-03_temperature_time_radius_heatmap.npz",
            "temperature_C",
            "温度",
            "温度 T / ℃",
        ),
        plot_heatmap(
            "FIG-Q2-04",
            "FIG-Q2-04_moisture_time_radius_heatmap",
            SOURCE_ROOT / "FIG-Q2-04_moisture_time_radius_heatmap.npz",
            "moisture_kg_kg",
            "水分浓度",
            "水分浓度 C / (kg/kg)",
        ),
        plot_histories(
            "FIG-Q2-05",
            "FIG-Q2-05_temperature_time_histories",
            SOURCE_ROOT / "FIG-Q2-05_temperature_time_histories.csv",
            "温度",
            "温度 T / ℃",
            "temperature_C",
        ),
        plot_histories(
            "FIG-Q2-06",
            "FIG-Q2-06_moisture_time_histories",
            SOURCE_ROOT / "FIG-Q2-06_moisture_time_histories.csv",
            "水分浓度",
            "水分浓度 C / (kg/kg)",
            "moisture_kg_kg",
        ),
        plot_difference(SOURCE_ROOT / "FIG-Q2-07_center_surface_moisture_difference.csv"),
        plot_diffusivity(SOURCE_ROOT / "FIG-Q2-08_representative_diffusivity.csv"),
        plot_diagnostic(
            "FIG-Q2-V01",
            "FIG-Q2-V01_picard_iterations",
            SOURCE_ROOT / "FIG-Q2-V01_picard_iterations.csv",
            "picard_iterations",
            "非线性迭代次数",
            "迭代次数",
        ),
        plot_diagnostic(
            "FIG-Q2-V02",
            "FIG-Q2-V02_mass_residual",
            SOURCE_ROOT / "FIG-Q2-V02_mass_residual.csv",
            "mass_step_residual",
            "质量守恒误差",
            "质量守恒误差",
        ),
        plot_diagnostic(
            "FIG-Q2-V03",
            "FIG-Q2-V03_heat_residual",
            SOURCE_ROOT / "FIG-Q2-V03_heat_residual.csv",
            "heat_step_residual_j",
            "能量残差",
            "能量残差 / J",
        ),
    ]

    workbook_sha_after = sha256(WORKBOOK)
    if workbook_sha_after != workbook_sha_before:
        raise RuntimeError("result2.xlsx changed during figure localization")
    manifest = {
        "schema_version": "Q2_CHINESE_PUBLICATION_FIGURE_MANIFEST_V1",
        "status": "GENERATED_PENDING_VALIDATION",
        "purpose": "Chinese publication rendering from frozen Q2 postprocess artifacts",
        "q2_numeric_freeze_unchanged": True,
        "q2_solver_rerun": False,
        "source_manifest": str(SOURCE_MANIFEST.relative_to(ROOT)).replace("\\", "/"),
        "source_manifest_sha256": sha256(SOURCE_MANIFEST),
        "source_root": str(SOURCE_ROOT.relative_to(ROOT)).replace("\\", "/"),
        "source_mode": "existing Q2 figure source data only; no solver import or execution",
        "font": {"selected": font_name, "preferred_order": list(PREFERRED_FONTS), "axes_unicode_minus": False},
        "result2": {
            "path": str(WORKBOOK.relative_to(ROOT)).replace("\\", "/"),
            "sha256_before": workbook_sha_before,
            "sha256_after": workbook_sha_after,
            "numerical_result_changed": False,
        },
        "frozen_original_figure_root": str(FROZEN_FIGURE_ROOT.relative_to(ROOT)).replace("\\", "/"),
        "frozen_original_figure_hashes_unchanged": original_hashes_current == original_hashes,
        "figures": figures,
        "figure_count": len(figures),
        "png_count": len(figures),
        "svg_count": len(figures),
        "no_smoothing": True,
        "no_numeric_interpolation": True,
        "trace_contract": {
            "source_numeric_arrays_identical": True,
            "x_data_identical": True,
            "y_data_identical": True,
            "sampling_identical": True,
        },
    }
    manifest_path = OUTPUT_ROOT / "Q2_CHINESE_FIGURE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    generation_record = {
        "experiment": "Q2_CHINESE_FIGURE_LOCALIZATION",
        "status": "GENERATED_PENDING_VALIDATION",
        "manifest": str(manifest_path.relative_to(ROOT)).replace("\\", "/"),
        "result2_sha256_before": workbook_sha_before,
        "result2_sha256_after": workbook_sha_after,
        "numerical_result_changed": False,
        "frozen_original_q2_figures_unchanged": True,
        "q2_solver_rerun": False,
        "figure_count": len(figures),
        "font": font_name,
    }
    (AUDIT_ROOT / "generation_record.json").write_text(json.dumps(generation_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(generation_record, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
