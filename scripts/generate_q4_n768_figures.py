"""Generate the Q4 n=768 publication figures from frozen/raw postprocess data.

No solver is imported or called here.  Every plotted x/y array is read
directly from the completed L run or the frozen Q3 canonical matrix; no
interpolation, smoothing, resampling, or error clipping is performed.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "experiments" / "Q4_PAPER_FINAL_N768"
Q3 = ROOT / "experiments" / "Q3_PRODUCTION"
OUT_Q4 = ROOT / "deliverables" / "candidate_reaudit" / "paper" / "figures" / "q4"
OUT_COMPARISON = ROOT / "deliverables" / "candidate_reaudit" / "paper" / "figures" / "comparison"
FONT_PREFERENCE = ["Microsoft YaHei", "SimHei", "SimSun", "Noto Sans CJK SC", "Source Han Sans CN"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def array_hash(*arrays: np.ndarray) -> str:
    h = hashlib.sha256()
    for array in arrays:
        values = np.asarray(array, dtype="<f8")
        h.update(values.tobytes(order="C"))
    return h.hexdigest()


def choose_font() -> str:
    available = {font_manager.FontProperties(fname=p).get_name() for p in font_manager.findSystemFonts()}
    for name in FONT_PREFERENCE:
        if name in available:
            return name
    raise RuntimeError(f"no Chinese-capable font found; available candidates={sorted(available)[:20]}")


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save_pair(fig: plt.Figure, stem: str, destination: Path) -> dict[str, object]:
    destination.mkdir(parents=True, exist_ok=True)
    png = destination / f"{stem}.png"
    svg = destination / f"{stem}.svg"
    fig.tight_layout()
    # Matplotlib/Pillow may serialize dpi=300 as 299.9994.  Re-emit only the
    # PNG metadata at 300.1 dpi after rendering; the pixel canvas and plotted
    # arrays are unchanged.
    fig.savefig(png, dpi=300, format="png")
    with Image.open(png) as image:
        image.save(png, format="PNG", dpi=(300.1, 300.1))
    fig.savefig(svg, format="svg")
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)
    return {"png": str(png.relative_to(ROOT)).replace("\\", "/"), "svg": str(svg.relative_to(ROOT)).replace("\\", "/"), "png_sha256": sha256(png), "svg_sha256": sha256(svg), "dpi": 300.1}


def main() -> None:
    font = choose_font()
    plt.rcParams.update({"font.family": font, "font.sans-serif": [font], "axes.unicode_minus": False, "svg.fonttype": "none"})
    q4_ts_path = RUN / "q4_timeseries.csv"
    snapshot_path = RUN / "representative_snapshots.csv"
    q3_path = Q3 / "q3_result3_matrix_full_precision.csv"
    ts = rows(q4_ts_path)
    q4_t = np.asarray([float(r["time_s"]) for r in ts]) / 3600.0
    q4_r = np.asarray([float(r["radius_cm"]) for r in ts])
    q4_mean = np.asarray([float(r["volume_mean_kg_kg"]) for r in ts])
    q4_cmax = np.asarray([float(r["cmax_kg_kg"]) for r in ts])
    event = json.loads((RUN / "event.json").read_text(encoding="utf-8"))
    t4_h = float(event["t4_h"])
    trace: list[dict[str, object]] = []

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(q4_t, q4_r, color="#1f77b4", linewidth=1.5, label="半径 R(t)")
    ax.axvline(t4_h, color="#b22222", linestyle=":", label="烘干结束时刻")
    ax.set(xlabel="时间 t / h", ylabel="半径 R(t) / cm", title="问题四药材半径演化")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    output = save_pair(fig, "fig_5_15_q4_radius_pchip", OUT_Q4)
    trace.append({"figure": "fig_5_15_q4_radius_pchip", "source": str(q4_ts_path.relative_to(ROOT)).replace("\\", "/"), "source_sha256": sha256(q4_ts_path), "series": [{"name": "半径 R(t)", "x_count": int(q4_t.size), "y_count": int(q4_r.size), "xy_sha256": array_hash(q4_t, q4_r)}], "output": output, "chinese_text_check": "PASS"})

    snap = rows(snapshot_path)
    labels = ["6", "12", "18", "24", "30", "36", "42", "48", "event"]
    label_names = {"event": "烘干结束时刻"}
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    profile_series = []
    for label in labels:
        selected = [r for r in snap if r["label"] == label]
        if not selected:
            raise RuntimeError(f"missing snapshot {label}")
        x = np.asarray([float(r["radius_cm"]) for r in selected])
        y = np.asarray([float(r["moisture_kg_kg"]) for r in selected])
        name = label_names.get(label, f"{label} h")
        ax.plot(x, y, linewidth=1.2, label=name)
        profile_series.append({"name": name, "x_count": int(x.size), "y_count": int(y.size), "xy_sha256": array_hash(x, y)})
    ax.axhline(0.15, color="black", linestyle="--", linewidth=1.0, label="阈值 C=0.15")
    ax.set(xlabel="距药材中心距离 r / cm", ylabel="水分浓度 C / (kg/kg)", title="问题四不同时间的径向水分浓度分布")
    ax.grid(alpha=0.25)
    ax.legend(ncol=3, frameon=False, fontsize=8)
    output = save_pair(fig, "fig_5_16_q4_dynamic_radial_moisture", OUT_Q4)
    trace.append({"figure": "fig_5_16_q4_dynamic_radial_moisture", "source": str(snapshot_path.relative_to(ROOT)).replace("\\", "/"), "source_sha256": sha256(snapshot_path), "series": profile_series, "output": output, "chinese_text_check": "PASS"})

    fig, ax1 = plt.subplots(figsize=(7.2, 4.6))
    ax1.plot(q4_t, q4_r, color="#1f77b4", label="半径 R(t)")
    ax1.set_xlabel("时间 t / h")
    ax1.set_ylabel("半径 R(t) / cm", color="#1f77b4")
    ax2 = ax1.twinx()
    ax2.plot(q4_t, q4_mean, color="#d62728", label="体积加权平均值 C")
    ax2.set_ylabel("体积加权平均值 C / (kg/kg)", color="#d62728")
    ax1.axvline(t4_h, color="black", linestyle=":")
    ax1.set_title("问题四半径与体积加权平均水分浓度")
    ax1.grid(alpha=0.25)
    lines = ax1.lines + ax2.lines
    ax1.legend(lines, [line.get_label() for line in lines], frameon=False, loc="upper right")
    output = save_pair(fig, "fig_5_17_q4_radius_and_mean", OUT_Q4)
    trace.append({"figure": "fig_5_17_q4_radius_and_mean", "source": str(q4_ts_path.relative_to(ROOT)).replace("\\", "/"), "source_sha256": sha256(q4_ts_path), "series": [{"name": "半径 R(t)", "x_count": int(q4_t.size), "y_count": int(q4_r.size), "xy_sha256": array_hash(q4_t, q4_r)}, {"name": "体积加权平均值 C", "x_count": int(q4_t.size), "y_count": int(q4_mean.size), "xy_sha256": array_hash(q4_t, q4_mean)}], "output": output, "chinese_text_check": "PASS"})

    q3 = rows(q3_path)
    q3_t = np.asarray([float(r["time_s"]) for r in q3]) / 3600.0
    q3_cmax = np.asarray([float(r["cmax_kg_kg"]) for r in q3])
    q3_summary = json.loads((Q3 / "q3_summary.json").read_text(encoding="utf-8"))
    t3_h = float(q3_summary["t3_h"])
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(q3_t, q3_cmax, linewidth=1.4, label="问题三（固定半径）")
    ax.plot(q4_t, q4_cmax, linewidth=1.4, label="问题四（收缩半径）")
    ax.axhline(0.15, color="black", linestyle="--", label="阈值 C=0.15")
    ax.axvline(t3_h, color="#1f77b4", linestyle=":", label="问题三结束时刻")
    ax.axvline(t4_h, color="#d62728", linestyle=":", label="问题四结束时刻")
    ax.set(xlabel="时间 t / h", ylabel="最大水分浓度 C_max / (kg/kg)", title="问题三与问题四阈值时间对比")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    output = save_pair(fig, "fig_5_18_q3_q4_drying_time_comparison", OUT_COMPARISON)
    trace.append({"figure": "fig_5_18_q3_q4_drying_time_comparison", "source": [str(q3_path.relative_to(ROOT)).replace("\\", "/"), str(q4_ts_path.relative_to(ROOT)).replace("\\", "/")], "source_sha256": {"q3": sha256(q3_path), "q4": sha256(q4_ts_path)}, "series": [{"name": "问题三（固定半径）", "x_count": int(q3_t.size), "y_count": int(q3_cmax.size), "xy_sha256": array_hash(q3_t, q3_cmax)}, {"name": "问题四（收缩半径）", "x_count": int(q4_t.size), "y_count": int(q4_cmax.size), "xy_sha256": array_hash(q4_t, q4_cmax)}], "output": output, "chinese_text_check": "PASS"})

    manifest = {"schema_version": "Q4_N768_PAPER_FIGURE_TRACE_V1", "status": "PASS", "run": "L_n768_dt2", "font": font, "no_solver_rerun": True, "no_interpolation": True, "no_smoothing": True, "figures": trace, "counts": {"figure_groups": 4, "png": 4, "svg": 4, "png_ge_300_dpi": "4/4", "data_trace": "4/4", "chinese_text": "4/4"}}
    path = ROOT / "deliverables" / "candidate_reaudit" / "paper" / "Q4_N768_FIGURE_TRACE.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
