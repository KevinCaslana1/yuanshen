"""Q3 helpers built on the frozen Q2 official lattice.

Q3 deliberately reads Q2 production samples without importing or rewriting
the Q2 solver.  The one-second endpoint refinement is a local BE/Picard
continuation from the last full-precision Q2 sample because Q2 did not retain
a restart checkpoint at the Q3 event.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from src.common.numerics import make_radial_grid
from src.q2.environment import EnvironmentProvider
from src.q2.model import assemble_variable_radial_system, interface_values, solve_system
from src.q2.properties import cp_array, conductivity_array, density_array, diffusivity_array


THRESHOLD_KG_KG = 0.15
Q2_OFFICIAL_RADII_CM: Tuple[float, ...] = tuple(i / 10.0 for i in range(21))


@dataclass(frozen=True)
class OfficialSnapshot:
    time_s: float
    radius_cm: Tuple[float, ...]
    temperature_k: Tuple[float, ...]
    moisture: Tuple[float, ...]

    @property
    def cmax(self) -> float:
        return max(self.moisture)

    @property
    def critical_radius_cm(self) -> float:
        index = max(range(len(self.moisture)), key=self.moisture.__getitem__)
        return self.radius_cm[index]


def stream_q2_snapshots(path: str | Path, wanted_times: Iterable[float]) -> Dict[float, OfficialSnapshot]:
    """Read selected rows from Q2 raw official samples in one streaming pass."""

    wanted = {round(float(t), 9) for t in wanted_times}
    values: Dict[float, Dict[str, List[float]]] = {}
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            t = float(row["time_s"])
            key = round(t, 9)
            if key not in wanted:
                continue
            bucket = values.setdefault(key, {"r": [], "T": [], "C": []})
            bucket["r"].append(float(row["radius_cm"]))
            bucket["T"].append(float(row["temperature_K"]))
            bucket["C"].append(float(row["moisture_kg_kg"]))
    result: Dict[float, OfficialSnapshot] = {}
    for key, bucket in values.items():
        order = sorted(range(len(bucket["r"])), key=lambda i: bucket["r"][i])
        radii = tuple(bucket["r"][i] for i in order)
        if tuple(round(v, 10) for v in radii) != Q2_OFFICIAL_RADII_CM:
            raise ValueError(f"Q2 official sample radius lattice mismatch at t={key:g} s")
        result[key] = OfficialSnapshot(
            time_s=key,
            radius_cm=radii,
            temperature_k=tuple(bucket["T"][i] for i in order),
            moisture=tuple(bucket["C"][i] for i in order),
        )
    missing = sorted(wanted - set(result))
    if missing:
        raise ValueError(f"missing Q2 official sample times: {missing[:5]}")
    return result


def volume_weighted_mean(moisture: Sequence[float], radius_cm: Sequence[float]) -> float:
    """Cylindrical volume-weighted mean on a radial node lattice."""

    if len(moisture) != len(radius_cm) or len(moisture) < 2:
        raise ValueError("moisture/radius arrays must have matching length >= 2")
    r2 = [float(r) ** 2 for r in radius_cm]
    total = r2[-1]
    weights = [0.0] * len(moisture)
    weights[0] = 0.5 * (r2[1] - r2[0])
    for i in range(1, len(moisture) - 1):
        weights[i] = 0.5 * (r2[i + 1] - r2[i - 1])
    weights[-1] = 0.5 * (r2[-1] - r2[-2])
    return sum(w * float(c) for w, c in zip(weights, moisture)) / total


def _scaled_residual(new: Sequence[float], old: Sequence[float]) -> float:
    return max((abs(a - b) / max(1.0, abs(a), abs(b)) for a, b in zip(new, old)), default=0.0)


def refine_endpoint(
    start: OfficialSnapshot,
    end_time_s: float,
    *,
    threshold: float = THRESHOLD_KG_KG,
    substeps_per_second: int = 1024,
    input_path: str | Path = "A题/附件/附件1.xlsx",
) -> Tuple[float, OfficialSnapshot, Dict[str, object]]:
    """Perform a local subsecond BE/Picard event refinement.

    The refinement is not an interpolation of two Excel rows: every local
    substep assembles and solves the variable-property radial BE systems.
    The state returned at the refined root is obtained with one additional
    partial BE step.
    """

    if end_time_s <= start.time_s or substeps_per_second < 2:
        raise ValueError("invalid local endpoint interval")
    env = EnvironmentProvider.from_attachment1(
        input_path, method="linear", post_attachment_mode="constant", post_temperature_c=50.0, post_moisture_kg_kg=0.05
    )
    grid = make_radial_grid(0.02, len(start.moisture) - 1)
    T = list(start.temperature_k)
    C = list(start.moisture)
    current = float(start.time_s)
    target = float(end_time_s)
    min_c = start.cmax
    previous_cmax = start.cmax
    bracket: Tuple[float, float] | None = None
    bracket_states: Tuple[List[float], List[float], float, float] | None = None
    step_s = 1.0 / float(substeps_per_second)
    steps = 0

    def advance(old_T: Sequence[float], old_C: Sequence[float], t0: float, dt_s: float) -> Tuple[List[float], List[float], int]:
        env_temp_c, env_moisture = env.at(t0 + dt_s)
        T_guess = list(old_T)
        C_guess = list(old_C)
        for iteration in range(1, 31):
            rho = density_array(C_guess)
            cap = [a * b for a, b in zip(rho, cp_array(C_guess))]
            k_faces = interface_values(conductivity_array(C_guess), "harmonic")
            heat_system = assemble_variable_radial_system(old_T, grid, dt_s, cap, k_faces, 25.0, env_temp_c + 273.15, scheme="be")
            T_new = solve_system(heat_system)
            d_faces = interface_values(diffusivity_array(C_guess, T_new), "harmonic")
            moisture_system = assemble_variable_radial_system(old_C, grid, dt_s, [1.0] * len(old_C), d_faces, 8.0e-7, env_moisture, scheme="be")
            C_new = solve_system(moisture_system)
            if min(C_new) <= 0.0 or not all(math.isfinite(v) for v in C_new):
                raise ValueError(f"local Q3 refinement became nonphysical at t={t0 + dt_s:g} s")
            if max(_scaled_residual(T_new, T_guess), _scaled_residual(C_new, C_guess)) <= 1.0e-10:
                return list(T_new), list(C_new), iteration
            T_guess, C_guess = list(T_new), list(C_new)
        raise ValueError(f"local Q3 Picard did not converge at t={t0 + dt_s:g} s")

    while current < target - 1.0e-12:
        dt = min(step_s, target - current)
        old_T, old_C, old_time, old_max = list(T), list(C), current, previous_cmax
        T, C, iterations = advance(T, C, current, dt)
        current += dt
        steps += 1
        new_max = max(C)
        min_c = min(min_c, new_max)
        if bracket is None and old_max >= threshold and new_max < threshold:
            bracket = (old_time, current)
            bracket_states = (old_T, old_C, T, C)
            break
        previous_cmax = new_max
    if bracket is None or bracket_states is None:
        raise ValueError("local Q3 refinement did not bracket the threshold")

    t0, t1 = bracket
    old_T, old_C, high_T, high_C = bracket_states
    g0 = max(old_C) - threshold
    g1 = max(high_C) - threshold
    fraction = 0.5 if g1 == g0 else max(0.0, min(1.0, g0 / (g0 - g1)))
    root_time = t0 + fraction * (t1 - t0)
    root_T, root_C, root_iterations = advance(old_T, old_C, t0, root_time - t0)
    # The strict event definition is the first refined substep with Cmax <
    # threshold.  Keep the continuous root estimate for audit, but use the
    # verified strict-below state as the candidate endpoint row.
    endpoint = OfficialSnapshot(t1, Q2_OFFICIAL_RADII_CM, tuple(high_T), tuple(high_C))
    details = {
        "method": "local BE/Picard continuation on reconstructed official 0.1 cm lattice",
        "source_time_s": start.time_s,
        "bracket_s": [t0, t1],
        "substeps_per_second": substeps_per_second,
        "substeps_used_before_bracket": steps,
        "root_fraction_in_local_bracket": fraction,
        "root_estimate_s": root_time,
        "first_strictly_below_time_s": t1,
        "picard_iterations_at_endpoint": root_iterations,
        "cmax_at_bracket_before": max(old_C),
        "cmax_at_bracket_after": max(high_C),
        "threshold_kg_kg": threshold,
    }
    return t1, endpoint, details
