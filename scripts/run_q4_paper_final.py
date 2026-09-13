"""Run the authorized Q4 deadline spatial production configurations.

The numerical method is the already audited src/q4 BE/Picard solver.  Each
invocation starts from the documented initial state at t=0 and writes only to
its own experiment directory.  The n=640 mode is intentionally minimal; the
n=768 mode retains all raw data needed for the workbook, Table6 and figures so
that no second solver run is needed for delivery generation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q2.environment import EnvironmentProvider
from src.q4.model import Q4State, advance_q4, initial_state, map_to_physical_radii, material_profile_csv_row
from src.q4.radius import RadiusLaw


ATTACHMENT1 = ROOT / "A题" / "附件" / "附件1.xlsx"
ATTACHMENT2 = ROOT / "A题" / "附件" / "附件2.xlsx"
THRESHOLD = 0.15
DT = 2.0
HORIZON = 230400.0
FIXED_RADII_CANONICAL = [i / 10.0 for i in range(21)]
FIXED_RADII_WORKBOOK = [i / 10.0 for i in range(20)]
PAPER_HOURS = [6, 12, 18, 24, 30, 36, 42, 48]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def scalar_state(state: Q4State) -> dict[str, Any]:
    row = material_profile_csv_row(state)
    return {key: float(value) if isinstance(value, (int, float)) else value for key, value in row.items()}


def mapped_row(state: Q4State, radii: list[float]) -> list[object]:
    return [state.time_s, *map_to_physical_radii(state, radii), state.moisture[-1], state.radius_cm, state.cmax, state.mean_moisture]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--minimal", action="store_true")
    args = parser.parse_args()
    if args.n not in (640, 768):
        raise ValueError("deadline mode only permits n=640 or n=768")
    if args.n == 768 and args.minimal:
        raise ValueError("n=768 must retain full canonical raw data")
    out = args.output if args.output.is_absolute() else ROOT / args.output
    out.mkdir(parents=True, exist_ok=True)
    radius_law = RadiusLaw.from_attachment2(ATTACHMENT2)
    environment = EnvironmentProvider.from_attachment1(
        ATTACHMENT1,
        method="linear",
        post_attachment_mode="constant",
        post_temperature_c=49.99525,
        post_moisture_kg_kg=0.049988,
    )
    state = initial_state(args.n)
    started = time.perf_counter()
    max_mass = 0.0
    cumulative_mass = 0.0
    max_robin = 0.0
    max_picard = 0
    max_nonlinear = 0.0
    max_linear = 0.0
    steps = 0
    coarse_bracket: tuple[Q4State, Q4State] | None = None
    official_rows: list[list[object]] = []
    timeseries_rows: list[list[object]] = []
    paper_states: dict[float, Q4State] = {}
    previous = state

    while state.time_s < HORIZON - 1e-12:
        previous = state
        state = advance_q4(state, min(DT, HORIZON - state.time_s), radius_law=radius_law, environment=environment, n_intervals=args.n)
        steps += 1
        max_mass = max(max_mass, abs(state.mass_step_residual))
        cumulative_mass += abs(state.mass_step_residual)
        max_robin = max(max_robin, abs(state.robin_residual))
        max_picard = max(max_picard, state.picard_iterations)
        max_nonlinear = max(max_nonlinear, state.nonlinear_residual)
        max_linear = max(max_linear, state.linear_residual)
        if abs(state.time_s / 60.0 - round(state.time_s / 60.0)) < 1e-10:
            timeseries_rows.append(list(material_profile_csv_row(state).values()))
            if not args.minimal:
                official_rows.append(mapped_row(state, FIXED_RADII_CANONICAL))
                hour = state.time_s / 3600.0
                if hour in PAPER_HOURS:
                    paper_states[hour] = state
        if float(state.cmax) < THRESHOLD <= float(previous.cmax):
            coarse_bracket = (previous, state)
            break

    if coarse_bracket is None:
        raise RuntimeError(f"n={args.n}, dt=2 s did not cross the Q4 threshold")
    low, high = coarse_bracket
    root_dt = DT / 32.0
    root_prev = low
    refined: tuple[Q4State, Q4State] | None = None
    root_steps = 0
    while root_prev.time_s < high.time_s - 1e-12:
        root_next = advance_q4(root_prev, min(root_dt, high.time_s - root_prev.time_s), radius_law=radius_law, environment=environment, n_intervals=args.n)
        root_steps += 1
        max_mass = max(max_mass, abs(root_next.mass_step_residual))
        cumulative_mass += abs(root_next.mass_step_residual)
        max_robin = max(max_robin, abs(root_next.robin_residual))
        max_picard = max(max_picard, root_next.picard_iterations)
        max_nonlinear = max(max_nonlinear, root_next.nonlinear_residual)
        max_linear = max(max_linear, root_next.linear_residual)
        if float(root_next.cmax) < THRESHOLD <= float(root_prev.cmax):
            refined = (root_prev, root_next)
            break
        root_prev = root_next
    if refined is None:
        raise RuntimeError(f"n={args.n} local root refinement did not bracket threshold")
    root_low, root_high = refined
    fraction = (root_low.cmax - THRESHOLD) / (root_low.cmax - root_high.cmax)
    fraction = max(0.0, min(1.0, fraction))
    t4 = root_low.time_s + fraction * (root_high.time_s - root_low.time_s)
    endpoint = advance_q4(root_low, t4 - root_low.time_s, radius_law=radius_law, environment=environment, n_intervals=args.n)
    max_mass = max(max_mass, abs(endpoint.mass_step_residual))
    cumulative_mass += abs(endpoint.mass_step_residual)
    max_robin = max(max_robin, abs(endpoint.robin_residual))
    max_picard = max(max_picard, endpoint.picard_iterations)
    max_nonlinear = max(max_nonlinear, endpoint.nonlinear_residual)
    max_linear = max(max_linear, endpoint.linear_residual)
    if endpoint.cmax >= THRESHOLD:
        endpoint = root_high
        t4 = endpoint.time_s
    if endpoint.cmax >= THRESHOLD:
        raise RuntimeError(f"n={args.n} endpoint failed strict threshold")
    elapsed = time.perf_counter() - started

    event = {
        "threshold_kg_kg": THRESHOLD,
        "coarse_bracket_s": [low.time_s, high.time_s],
        "root_bracket_s": [root_low.time_s, root_high.time_s],
        "root_bracket_width_s": root_high.time_s - root_low.time_s,
        "t4_s": t4,
        "t4_h": t4 / 3600.0,
        "R_t4_cm": radius_law.radius_cm(t4),
        "R_t4_rate_cm_s": radius_law.radius_rate_cm_s(t4),
        "cmax_before": root_low.cmax,
        "cmax_after": root_high.cmax,
        "endpoint_cmax": endpoint.cmax,
        "critical_xi": endpoint.critical_xi,
        "critical_radius_cm": endpoint.critical_xi * endpoint.radius_cm,
        "controlling_point": "center / xi=0" if endpoint.critical_xi == 0.0 else "not center",
        "endpoint_R_cm": endpoint.radius_cm,
    }
    metrics = {
        "name": f"{'K' if args.n == 640 else 'L'}_n{args.n}_dt2",
        "n_intervals": args.n,
        "dt_s": DT,
        "horizon_s": HORIZON,
        "initial_state": "fresh t=0; no checkpoint or prior-grid state reuse",
        "runtime_s": elapsed,
        "full_steps_to_event": steps,
        "root_refinement_steps": root_steps,
        "event": event,
        "max_abs_step_mass_residual": max_mass,
        "cumulative_abs_step_mass_residual": cumulative_mass,
        "max_abs_robin_residual": max_robin,
        "max_picard_iterations": max_picard,
        "max_nonlinear_residual": max_nonlinear,
        "max_linear_residual": max_linear,
        "status": "COMPLETED",
    }
    inputs = {
        "attachment1": str(ATTACHMENT1.relative_to(ROOT)).replace("\\", "/"),
        "attachment2": str(ATTACHMENT2.relative_to(ROOT)).replace("\\", "/"),
        "attachment1_sha256": sha256(ATTACHMENT1),
        "attachment2_sha256": sha256(ATTACHMENT2),
        "environment": {"interpolation": "linear within Attachment 1", "post_attachment_mode": "constant", "post_temperature_c": 49.99525, "post_moisture_kg_kg": 0.049988},
        "radius": {"interpolation": "PchipInterpolator-compatible Fritsch-Carlson monotone cubic", "tail": f"hold R_last={radius_law.last_radius_cm} cm after t={radius_law.last_time_s} s"},
        "solver": {"model": "Appendix 4 Q4 moving-domain moisture-temperature coupling", "coordinate": "xi=r/R(t)", "interface": "harmonic", "time_scheme": "backward Euler", "nonlinear_solver": "Picard", "h_m_W_m2K": 25.0, "h_moisture_m_s": 8.0e-7},
    }
    write_json(out / "config.json", {"n_intervals": args.n, "dt_s": DT, "output_interval_s": 60.0, "threshold_kg_kg": THRESHOLD, "full_raw_mode": not args.minimal})
    write_json(out / "inputs.json", inputs)
    write_json(out / "event.json", event)
    write_json(out / "metrics.json", metrics)
    write_json(out / "lineage.json", {"status": "Q4_PAPER_FINAL_CANONICAL" if args.n == 768 else "Q4_SPATIAL_CONFIRMATION", "run": metrics["name"], "source": "src/q4/model.py; fresh initial_state(t=0)", "no_checkpoint": True, "no_prior_grid_state": True})

    if not args.minimal:
        workbook_header = ["time_s", *[f"r_{r:.1f}_cm" for r in FIXED_RADII_WORKBOOK], "surface", "radius_cm", "cmax_kg_kg", "volume_mean_kg_kg"]
        workbook_rows = []
        for row in official_rows:
            workbook_rows.append([row[0], *row[1:21], row[22], row[23], row[24], row[25]])
        workbook_rows.append(mapped_row(endpoint, FIXED_RADII_WORKBOOK))
        write_csv(out / "q4_result4_matrix_full_precision.csv", workbook_header, workbook_rows)
        canonical_header = ["time_s", *[f"r_{r:.1f}_cm" for r in FIXED_RADII_CANONICAL], "surface", "radius_cm", "cmax_kg_kg", "volume_mean_kg_kg"]
        write_csv(out / "official_samples_raw.csv", canonical_header, official_rows)
        write_csv(out / "official_samples_with_endpoint_raw.csv", canonical_header, official_rows + [mapped_row(endpoint, FIXED_RADII_CANONICAL)])
        profile_header = ["time_s", "radius_cm", "cmax_kg_kg", "center_kg_kg", "surface_kg_kg", "volume_mean_kg_kg", "picard_iterations", "nonlinear_residual", "linear_residual", "radius_rate_cm_s", "mass_step_residual", "robin_residual"]
        timeseries_rows.append(list(material_profile_csv_row(endpoint).values()))
        write_csv(out / "q4_timeseries.csv", profile_header, timeseries_rows)
        surface_header = profile_header
        write_csv(out / "surface_samples.csv", surface_header, timeseries_rows)
        paper_header = ["time_label", "time_h", "radius_cm", "r_0.0_cm", "r_0.5_cm", "r_1.0_cm", "r_1.5_cm", "r_2.0_cm", "surface"]
        paper_rows: list[list[object]] = []
        for hour in PAPER_HOURS:
            if hour * 3600.0 >= t4:
                continue
            sample = paper_states[float(hour)]
            mapped = map_to_physical_radii(sample, [0.0, 0.5, 1.0, 1.5, 2.0])
            paper_rows.append([f"{hour} h", hour, sample.radius_cm, *mapped, sample.moisture[-1]])
        mapped = map_to_physical_radii(endpoint, [0.0, 0.5, 1.0, 1.5, 2.0])
        paper_rows.append(["烘干结束时间", t4 / 3600.0, endpoint.radius_cm, *mapped, endpoint.moisture[-1]])
        write_csv(out / "paper_samples.csv", paper_header, paper_rows)
        snapshot_rows: list[list[object]] = []
        snapshot_states = [(hour, paper_states[float(hour)]) for hour in PAPER_HOURS if float(hour) in paper_states]
        snapshot_states.append(("event", endpoint))
        for label, sample in snapshot_states:
            for index, (xi, c, temp) in enumerate(zip(np.linspace(0.0, 1.0, args.n + 1), sample.moisture, sample.temperature_k)):
                snapshot_rows.append([label, sample.time_s, index, xi, xi * sample.radius_cm, c, temp])
        write_csv(out / "representative_snapshots.csv", ["label", "time_s", "node_index", "xi", "radius_cm", "moisture_kg_kg", "temperature_K"], snapshot_rows)
        np.savez_compressed(out / "event_states.npz", before_moisture=np.asarray(root_low.moisture), after_moisture=np.asarray(root_high.moisture), endpoint_moisture=np.asarray(endpoint.moisture), before_temperature=np.asarray(root_low.temperature_k), after_temperature=np.asarray(root_high.temperature_k), endpoint_temperature=np.asarray(endpoint.temperature_k))

    output_hashes = {}
    for path in sorted(out.iterdir()):
        if path.is_file() and path.name != "hashes.json":
            output_hashes[path.name] = {"sha256": sha256(path), "size_bytes": path.stat().st_size}
    write_json(out / "hashes.json", {"inputs": {"attachment1_sha256": inputs["attachment1_sha256"], "attachment2_sha256": inputs["attachment2_sha256"]}, "outputs": output_hashes})
    print(json.dumps({"run": metrics["name"], "status": metrics["status"], "runtime_s": elapsed, "t4_s": t4, "t4_h": t4 / 3600.0, "R_t4_cm": event["R_t4_cm"], "critical_point": event["controlling_point"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
