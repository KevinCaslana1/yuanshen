"""Generate reproducible Q3/Q4 candidate evidence and paper assets.

This script never writes Q2 final assets.  Q3 reads the frozen Q2 raw official
lattice and performs only a local endpoint continuation.  Q4 is an independent
prescribed-shrinkage production candidate using Appendix 4 properties.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q2.environment import EnvironmentProvider
from src.q3.model import OfficialSnapshot, refine_endpoint, stream_q2_snapshots, volume_weighted_mean
from src.q4.model import Q4State, advance_q4, initial_state, map_to_physical_radii, material_profile_csv_row
from src.q4.radius import RadiusLaw


Q2_RAW = ROOT / "experiments" / "Q2_FREEZE_RUN_V3" / "run_1" / "official_samples_raw.csv"
Q2_FINAL = ROOT / "deliverables" / "final" / "result2.xlsx"
ATTACHMENT1 = ROOT / "A题" / "附件" / "附件1.xlsx"
ATTACHMENT2 = ROOT / "A题" / "附件" / "附件2.xlsx"
Q3_DIR = ROOT / "experiments" / "Q3_PRODUCTION"
Q4_DIR = ROOT / "experiments" / "Q4_PRODUCTION"
PAPER_DIR = ROOT / "deliverables" / "candidate" / "paper"
FIG_DIR = PAPER_DIR / "figures"
TABLE_DIR = PAPER_DIR / "tables"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path: Path, header: Sequence[object], rows: Iterable[Sequence[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def q4(value: float | None) -> str:
    return "" if value is None else f"{float(value):.4f}"


def configure_plot() -> None:
    fonts = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
    matplotlib.rcParams.update({"font.size": 10, "axes.unicode_minus": False, "figure.dpi": 120})
    for preferred in ("Microsoft YaHei", "SimHei", "Noto Sans CJK SC"):
        if preferred in fonts:
            matplotlib.rcParams["font.family"] = preferred
            break


def save_figure(fig: plt.Figure, stem: str) -> Dict[str, object]:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    png = FIG_DIR / f"{stem}.png"
    svg = FIG_DIR / f"{stem}.svg"
    fig.savefig(png, dpi=360, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    plt.close(fig)
    return {"png": str(png.relative_to(ROOT)), "svg": str(svg.relative_to(ROOT)), "png_sha256": sha256(png), "svg_sha256": sha256(svg), "png_dpi": 360}


def q3_pipeline() -> Dict[str, object]:
    Q3_DIR.mkdir(parents=True, exist_ok=True)
    threshold = 0.15
    regular_end = 206880
    regular_times = list(range(60, regular_end + 1, 60))
    wanted = regular_times + [206935, 206936]
    snaps = stream_q2_snapshots(Q2_RAW, wanted)
    before = snaps[206935.0]
    after = snaps[206936.0]
    t3, endpoint, refine_meta = refine_endpoint(before, 206936.0, threshold=threshold, substeps_per_second=1024, input_path=ATTACHMENT1)
    if not (before.cmax >= threshold and after.cmax < threshold and endpoint.cmax < threshold):
        raise RuntimeError("Q3 threshold bracket/refinement assertion failed")

    sample_rows = []
    for t in regular_times:
        snap = snaps[float(t)]
        sample_rows.append([snap.time_s, *snap.moisture, snap.cmax, snap.critical_radius_cm, volume_weighted_mean(snap.moisture, snap.radius_cm)])
    sample_rows.append([endpoint.time_s, *endpoint.moisture, endpoint.cmax, endpoint.critical_radius_cm, volume_weighted_mean(endpoint.moisture, endpoint.radius_cm)])
    header = ["time_s", *[f"r_{r:.1f}_cm" for r in before.radius_cm], "cmax_kg_kg", "critical_radius_cm", "volume_mean_kg_kg"]
    write_csv(Q3_DIR / "q3_result3_matrix_full_precision.csv", header, sample_rows)

    table_hours = [6, 12, 18, 24, 30, 36, 42, 48, 54]
    table_rows: List[List[object]] = []
    table_header = ["time_label", "time_h", *[f"r_{r:.1f}_cm" for r in (0.0, 0.5, 1.0, 1.5, 2.0)]]
    for hours in table_hours:
        snap = snaps[float(hours * 3600)]
        index = [round(v, 10) for v in snap.radius_cm].index(round(0.0, 10))
        positions = [snap.moisture[round(r * 10)] for r in (0.0, 0.5, 1.0, 1.5, 2.0)]
        table_rows.append([f"{hours} h", float(hours), *[q4(v) for v in positions]])
    endpoint_positions = [endpoint.moisture[round(r * 10)] for r in (0.0, 0.5, 1.0, 1.5, 2.0)]
    table_rows.append(["实际 t3", t3 / 3600.0, *[q4(v) for v in endpoint_positions]])
    write_csv(Q3_DIR / "table5.csv", table_header, table_rows)
    write_csv(TABLE_DIR / "table5_q3.csv", table_header, table_rows)
    write_csv(PAPER_DIR / "table5_q3.csv", table_header, table_rows)

    summary = {
        "question": "Q3",
        "status": "CANDIDATE",
        "threshold_kg_kg": threshold,
        "source_q2_raw": str(Q2_RAW.relative_to(ROOT)),
        "source_q2_raw_sha256": sha256(Q2_RAW),
        "frozen_q2_final_sha256": sha256(Q2_FINAL),
        "official_lattice_radius_cm": list(before.radius_cm),
        "coarse_bracket_s": [206935.0, 206936.0],
        "cmax_before": before.cmax,
        "cmax_after": after.cmax,
        "critical_radius_before_cm": before.critical_radius_cm,
        "critical_radius_after_cm": after.critical_radius_cm,
        "t3_s": t3,
        "t3_h": t3 / 3600.0,
        "endpoint_cmax": endpoint.cmax,
        "endpoint_critical_radius_cm": endpoint.critical_radius_cm,
        "endpoint_refinement": refine_meta,
        "prior_not_satisfied": before.cmax >= threshold,
        "endpoint_satisfied": endpoint.cmax < threshold,
        "overlap_source": "Q2_FREEZE_RUN_V3/run_1/official_samples_raw.csv; values copied by streaming selection and rounded only in candidate workbook",
    }
    write_json(Q3_DIR / "q3_summary.json", summary)

    # Plot assets are made only from the generated Q3 matrix; no smoothing or
    # interpolation is applied to the plotted time series.
    configure_plot()
    plot_times = regular_times + [t3]
    plot_snaps = [snaps[float(t)] for t in regular_times] + [endpoint]
    selected = [(6, snaps[21600.0]), (12, snaps[43200.0]), (18, snaps[64800.0]), (24, snaps[86400.0]), (48, snaps[172800.0]), ("t3", endpoint)]
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for label, snap in selected:
        ax.plot(snap.radius_cm, snap.moisture, linewidth=1.5, label=f"{label} h" if label != "t3" else "实际 t3")
    ax.axhline(threshold, color="black", linestyle="--", linewidth=1.0, label="阈值 0.15")
    ax.set(xlabel="到中心距离 r (cm)", ylabel="水分含量 C (kg/kg)", title="Q3 径向水分剖面")
    ax.legend(ncol=2, frameon=False)
    ax.grid(alpha=0.25)
    fig5_12 = save_figure(fig, "fig_5_12_q3_radial_moisture_profiles")

    means = [volume_weighted_mean(s.moisture, s.radius_cm) for s in plot_snaps]
    centers = [s.moisture[0] for s in plot_snaps]
    surfaces = [s.moisture[-1] for s in plot_snaps]
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(plot_times, centers, label="中心", linewidth=1.5)
    ax.plot(plot_times, surfaces, label="表面", linewidth=1.5)
    ax.plot(plot_times, means, label="体积加权平均", linewidth=1.5)
    ax.axhline(threshold, color="black", linestyle="--", linewidth=1.0, label="阈值 0.15")
    ax.axvline(t3, color="#b22222", linestyle=":", linewidth=1.2, label="t3")
    ax.set(xlabel="时间 t (s)", ylabel="水分含量 C (kg/kg)", title="Q3 中心、表面与体积加权平均水分")
    ax.legend(frameon=False, ncol=2)
    ax.grid(alpha=0.25)
    fig5_13 = save_figure(fig, "fig_5_13_q3_moisture_histories")

    sensitivity = []
    cmax_series = [s.cmax for s in plot_snaps]
    for level in (0.14, 0.15, 0.16):
        crossing = None
        for t, c in zip(plot_times, cmax_series):
            if c < level:
                crossing = float(t)
                break
        sensitivity.append([level, crossing])
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    plotted = [row for row in sensitivity if row[1] is not None]
    ax.plot([row[0] for row in plotted], [row[1] / 3600.0 for row in plotted], marker="o", linewidth=1.5)
    ax.set(xlabel="判定阈值 (kg/kg)", ylabel="首次低于阈值时间 (h)", title="Q3 阈值判定敏感性（离散输出）")
    ax.grid(alpha=0.25)
    fig5_14 = save_figure(fig, "fig_5_14_q3_threshold_sensitivity")
    summary["figures"] = {"fig_5_12": fig5_12, "fig_5_13": fig5_13, "fig_5_14": fig5_14}
    summary["threshold_sensitivity_discrete"] = sensitivity
    write_json(Q3_DIR / "q3_summary.json", summary)
    return summary


class _ConstantRadiusLaw:
    def radius_cm(self, time_s: float) -> float:
        return 2.0

    def radius_rate_cm_s(self, time_s: float) -> float:
        return 0.0


def q4_pipeline() -> Dict[str, object]:
    Q4_DIR.mkdir(parents=True, exist_ok=True)
    radius_law = RadiusLaw.from_attachment2(ATTACHMENT2)
    environment = EnvironmentProvider.from_attachment1(
        ATTACHMENT1, method="linear", post_attachment_mode="constant", post_temperature_c=49.99525, post_moisture_kg_kg=0.049988
    )
    n_intervals = 96
    production_dt = 4.0
    threshold = 0.15
    state = initial_state(n_intervals)
    series: Dict[float, Q4State] = {}
    prev = state
    bracket = None
    upper = None
    while state.time_s < radius_law.last_time_s - 1e-12:
        prev = state
        state = advance_q4(state, min(production_dt, radius_law.last_time_s - state.time_s), radius_law=radius_law, environment=environment, n_intervals=n_intervals)
        if abs(state.time_s / 60.0 - round(state.time_s / 60.0)) < 1e-10:
            series[round(state.time_s, 9)] = state
        if prev.cmax >= threshold and state.cmax < threshold:
            bracket = (prev, state)
            upper = state
            break
    if bracket is None:
        raise RuntimeError("Q4 did not reach the drying threshold within Attachment 2 horizon")

    # Refine the bracket by actual BE/Picard substeps, then apply one partial
    # solve at the estimated crossing.  This is separate from output sampling.
    low, high = bracket
    refine_steps = 64
    local_prev = low
    local_bracket = None
    for _ in range(refine_steps):
        local_next = advance_q4(local_prev, (high.time_s - low.time_s) / refine_steps, radius_law=radius_law, environment=environment, n_intervals=n_intervals)
        if local_prev.cmax >= threshold and local_next.cmax < threshold:
            local_bracket = (local_prev, local_next)
            break
        local_prev = local_next
    if local_bracket is None:
        raise RuntimeError("Q4 local threshold refinement did not bracket")
    local_low, local_high = local_bracket
    fraction = (local_low.cmax - threshold) / (local_low.cmax - local_high.cmax)
    fraction = max(0.0, min(1.0, fraction))
    t4 = local_low.time_s + fraction * (local_high.time_s - local_low.time_s)
    endpoint = advance_q4(local_low, t4 - local_low.time_s, radius_law=radius_law, environment=environment, n_intervals=n_intervals)
    if endpoint.cmax >= threshold:
        endpoint = local_high
        t4 = endpoint.time_s
    if not endpoint.cmax < threshold:
        raise RuntimeError("Q4 endpoint does not satisfy threshold")

    # Keep regular output samples only at 60 s, then append the actual endpoint.
    series = {t: s for t, s in series.items() if t < endpoint.time_s - 1.0e-9}
    rows = []
    fixed_radii = [i / 10.0 for i in range(20)]
    for t in sorted(series):
        s = series[t]
        mapped = map_to_physical_radii(s, fixed_radii)
        rows.append([s.time_s, *mapped, s.moisture[-1], s.radius_cm, s.cmax, s.mean_moisture])
    if not rows or abs(rows[-1][0] - endpoint.time_s) > 1e-9:
        mapped = map_to_physical_radii(endpoint, fixed_radii)
        rows.append([endpoint.time_s, *mapped, endpoint.moisture[-1], endpoint.radius_cm, endpoint.cmax, endpoint.mean_moisture])
    result_header = ["time_s", *[f"r_{r:.1f}_cm" for r in fixed_radii], "surface", "radius_cm", "cmax_kg_kg", "volume_mean_kg_kg"]
    write_csv(Q4_DIR / "q4_result4_matrix_full_precision.csv", result_header, rows)

    profile_header = ["time_s", "radius_cm", "cmax_kg_kg", "center_kg_kg", "surface_kg_kg", "volume_mean_kg_kg", "picard_iterations", "nonlinear_residual", "linear_residual", "radius_rate_cm_s", "mass_step_residual", "robin_residual"]
    profile_rows = [list(material_profile_csv_row(series[t]).values()) for t in sorted(series)] + [list(material_profile_csv_row(endpoint).values())]
    write_csv(Q4_DIR / "q4_timeseries.csv", profile_header, profile_rows)

    paper_hours = [6, 12, 18, 24, 30, 36, 42, 48, 54, 60]
    paper_header = ["time_label", "time_h", "radius_cm", "r_0.0_cm", "r_0.5_cm", "r_1.0_cm", "r_1.5_cm", "r_2.0_cm", "surface"]
    paper_rows: List[List[object]] = []
    for hours in paper_hours:
        t = hours * 3600.0
        if t >= endpoint.time_s:
            break
        s = series[round(t, 9)]
        mapped = map_to_physical_radii(s, [0.0, 0.5, 1.0, 1.5, 2.0])
        paper_rows.append([f"{hours} h", float(hours), q4(s.radius_cm), *[q4(v) for v in mapped], q4(s.moisture[-1])])
    mapped = map_to_physical_radii(endpoint, [0.0, 0.5, 1.0, 1.5, 2.0])
    paper_rows.append(["实际 t4", t4 / 3600.0, q4(endpoint.radius_cm), *[q4(v) for v in mapped], q4(endpoint.moisture[-1])])
    write_csv(Q4_DIR / "table6.csv", paper_header, paper_rows)
    write_csv(TABLE_DIR / "table6_q4.csv", paper_header, paper_rows)
    write_csv(PAPER_DIR / "table6_q4.csv", paper_header, paper_rows)

    # Constant-R regression and short time/grid sanity checks are compact and
    # independent of the production endpoint.
    const_law = _ConstantRadiusLaw()
    const = initial_state(24)
    const_max_source = 0.0
    for _ in range(60):
        const = advance_q4(const, 1.0, radius_law=const_law, environment=environment, n_intervals=24)
        const_max_source = max(const_max_source, abs(const.radius_rate_cm_s))
    sanity = {}
    for n, dt in ((32, 8.0), (48, 4.0)):
        s = initial_state(n)
        while s.time_s < 7200.0 - 1e-12:
            s = advance_q4(s, dt, radius_law=radius_law, environment=environment, n_intervals=n)
        sanity[f"n{n}_dt{dt:g}"] = {"center": s.moisture[0], "surface": s.moisture[-1], "mean": s.mean_moisture, "radius_cm": s.radius_cm}
    coarse = sanity["n32_dt8"]
    fine = sanity["n48_dt4"]
    sanity["differences_fine_minus_coarse"] = {k: fine[k] - coarse[k] for k in ("center", "surface", "mean")}

    q3_summary = json.loads((Q3_DIR / "q3_summary.json").read_text(encoding="utf-8"))
    metrics = {
        "question": "Q4",
        "status": "CANDIDATE",
        "threshold_kg_kg": threshold,
        "appendix4": {"rho": "760+90*C", "cp": "1850+2150*C/(C+1)", "k": "0.12+0.20*C/(C+1)", "D": "4.2e-4*exp(-0.30/C)*exp(-3850/T_K)"},
        "radius_source": str(ATTACHMENT2.relative_to(ROOT)),
        "radius_source_sha256": radius_law.source_sha256,
        "radius_interpolation": "PchipInterpolator-compatible Fritsch-Carlson monotone cubic",
        "radius_nodes_exact_to_machine": True,
        "post_attachment_radius_rule": f"hold R_last={radius_law.last_radius_cm} cm after t={radius_law.last_time_s} s",
        "material_coordinate": "xi=r/R(t), uniform xi lattice",
        "production": {"n_intervals": n_intervals, "dt_s": production_dt, "output_interval_s": 60.0, "interface_mean": "harmonic", "scheme": "backward Euler + coupled Picard"},
        "coarse_bracket_s": [low.time_s, high.time_s],
        "cmax_before": low.cmax,
        "cmax_after": high.cmax,
        "t4_s": t4,
        "t4_h": t4 / 3600.0,
        "radius_at_t4_cm": endpoint.radius_cm,
        "endpoint_cmax": endpoint.cmax,
        "critical_xi_at_t4": endpoint.critical_xi,
        "critical_radius_at_t4_cm": endpoint.critical_xi * endpoint.radius_cm,
        "prior_not_satisfied": low.cmax >= threshold,
        "endpoint_satisfied": endpoint.cmax < threshold,
        "delta_t4_minus_t3_s": t4 - q3_summary["t3_s"],
        "relative_delta_t4_minus_t3": (t4 - q3_summary["t3_s"]) / q3_summary["t3_s"],
        "constant_radius_regression": {"max_radius_deviation_cm": 0.0, "max_radius_rate_cm_s": const_max_source, "finite": all(math.isfinite(v) for v in const.moisture)},
        "time_grid_sanity": sanity,
        "mass_conservation": {"max_abs_normalized_step_residual": max(abs(s.mass_step_residual) for s in series.values()), "definition": "moving-volume balance with Robin loss and prescribed boundary motion"},
        "robin_audit": {"max_abs_flux_residual": max(abs(s.robin_residual) for s in series.values()), "condition": "-D(C_s)*dC/dr = hm*(C_s-C_inf)"},
        "environment": {"interpolation": "linear within Attachment 1", "post_attachment_mode": "constant", "post_temperature_c": 49.99525, "post_moisture_kg_kg": 0.049988},
    }
    write_json(Q4_DIR / "q4_summary.json", metrics)

    configure_plot()
    interp = radius_law._pchip
    dense_t = np.linspace(0.0, radius_law.last_time_s, 1000)
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(dense_t / 3600.0, [interp(t) for t in dense_t], label="PCHIP R(t)", linewidth=1.6)
    ax.plot(np.asarray(radius_law.times_s) / 3600.0, radius_law.radii_cm, "o", markersize=2.5, label="附件2节点")
    ax.axvline(t4 / 3600.0, color="#b22222", linestyle=":", label="t4")
    ax.set(xlabel="时间 t (h)", ylabel="半径 R(t) (cm)", title="Q4 药材半径及 PCHIP 插值")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)
    f15 = save_figure(fig, "fig_5_15_q4_radius_pchip")

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    profile_times = [6, 12, 18, 24, 48, "t4"]
    for label in profile_times:
        s = endpoint if label == "t4" else series[float(label * 3600)]
        x = np.linspace(0.0, s.radius_cm, len(s.moisture))
        ax.plot(x, s.moisture, label=f"{label} h" if label != "t4" else "实际 t4")
    ax.axhline(threshold, color="black", linestyle="--", linewidth=1.0, label="阈值 0.15")
    ax.set(xlabel="物理距离 r (cm)", ylabel="水分含量 C (kg/kg)", title="Q4 动态径向水分剖面")
    ax.legend(ncol=2, frameon=False)
    ax.grid(alpha=0.25)
    f16 = save_figure(fig, "fig_5_16_q4_dynamic_radial_moisture")

    ts = sorted(series) + [endpoint.time_s]
    rs = [series[t].radius_cm for t in sorted(series)] + [endpoint.radius_cm]
    ms = [series[t].mean_moisture for t in sorted(series)] + [endpoint.mean_moisture]
    fig, ax1 = plt.subplots(figsize=(7.2, 4.6))
    ax1.plot(np.asarray(ts) / 3600.0, rs, color="#1f77b4", label="R(t)")
    ax1.set_xlabel("时间 t (h)")
    ax1.set_ylabel("半径 R (cm)", color="#1f77b4")
    ax2 = ax1.twinx()
    ax2.plot(np.asarray(ts) / 3600.0, ms, color="#d62728", label="体积加权平均 C")
    ax2.set_ylabel("体积加权平均 C (kg/kg)", color="#d62728")
    ax1.axvline(t4 / 3600.0, color="black", linestyle=":")
    ax1.set_title("Q4 半径与体积加权平均水分")
    ax1.grid(alpha=0.25)
    f17 = save_figure(fig, "fig_5_17_q4_radius_and_mean")

    q3_matrix = list(csv.DictReader((Q3_DIR / "q3_result3_matrix_full_precision.csv").open(encoding="utf-8")))
    q3_t = np.asarray([float(row["time_s"]) for row in q3_matrix]) / 3600.0
    q3_c = np.asarray([float(row["cmax_kg_kg"]) for row in q3_matrix])
    q4_t = np.asarray(ts) / 3600.0
    q4_c = np.asarray([series[t].cmax for t in sorted(series)] + [endpoint.cmax])
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(q3_t, q3_c, label="Q3 固定半径", linewidth=1.5)
    ax.plot(q4_t, q4_c, label="Q4 收缩半径", linewidth=1.5)
    ax.axhline(threshold, color="black", linestyle="--", label="阈值 0.15")
    ax.axvline(q3_summary["t3_h"], color="#1f77b4", linestyle=":", label="t3")
    ax.axvline(t4 / 3600.0, color="#d62728", linestyle=":", label="t4")
    ax.set(xlabel="时间 t (h)", ylabel="最大水分含量 Cmax (kg/kg)", title="Q3 与 Q4 烘干阈值时间对比")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)
    f18 = save_figure(fig, "fig_5_18_q3_q4_drying_time_comparison")
    metrics["figures"] = {"fig_5_15": f15, "fig_5_16": f16, "fig_5_17": f17, "fig_5_18": f18}
    write_json(Q4_DIR / "q4_summary.json", metrics)
    return metrics


def main() -> None:
    for directory in (PAPER_DIR, TABLE_DIR, FIG_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    q3 = q3_pipeline()
    q4 = q4_pipeline()
    comparison = {
        "status": "CANDIDATE",
        "q3_t3_s": q3["t3_s"], "q3_t3_h": q3["t3_h"], "q4_t4_s": q4["t4_s"], "q4_t4_h": q4["t4_h"],
        "delta_s_q4_minus_q3": q4["delta_t4_minus_t3_s"], "relative_delta": q4["relative_delta_t4_minus_t3"],
        "interpretation": "Q3 fixed-radius and Q4 prescribed-shrinkage candidates are reported separately; no superiority claim is frozen.",
    }
    write_json(PAPER_DIR / "q3_q4_comparison.json", comparison)
    write_json(PAPER_DIR / "q3_summary.json", q3)
    write_json(PAPER_DIR / "q4_summary.json", q4)
    (PAPER_DIR / "q3_results.md").write_text("# Q3 候选结果\n\n- 阈值：0.15 kg/kg。\n- 端点由冻结 Q2 官方格点读取并用局部 BE/Picard 子步细化。\n- 详见 `q3_summary.json` 与 `tables/table5_q3.csv`。\n", encoding="utf-8")
    (PAPER_DIR / "q4_results.md").write_text("# Q4 候选结果\n\n- 使用附录4物性、附件2 PCHIP 半径与材料坐标 ξ=r/R(t)。\n- 当前半径之外的固定物理位置留空，表面单独输出。\n- 详见 `q4_summary.json` 与 `tables/table6_q4.csv`。\n", encoding="utf-8")
    write_json(ROOT / "deliverables" / "candidate" / "Q3_Q4_CANDIDATE_MANIFEST.json", {"q3": q3, "q4": q4, "comparison": comparison, "status": "WAITING_FOR_HUMAN_Q3_Q4_FREEZE_APPROVAL"})


if __name__ == "__main__":
    main()
