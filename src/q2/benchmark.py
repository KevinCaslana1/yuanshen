"""Independent manufactured-solution benchmarks for variable-coefficient FVM."""

from __future__ import annotations

import math
from typing import Dict, Iterable

from src.common.numerics import make_radial_grid

from .model import interface_values, solve_system, assemble_variable_radial_system


def _exact(r: float, time_s: float, radius: float, beta: float = 0.2, decay: float = 1.0) -> float:
    return math.exp(-decay * time_s) * (1.0 + beta * (r / radius) ** 2)


def _exact_derivative(r: float, time_s: float, radius: float, beta: float = 0.2, decay: float = 1.0) -> float:
    return math.exp(-decay * time_s) * 2.0 * beta * r / (radius * radius)


def _operator(r: float, time_s: float, radius: float, coefficient_kind: str, beta: float = 0.2, decay: float = 1.0) -> float:
    # a(r)=a0+a1*r/R; the radial divergence is evaluated analytically,
    # including the regular center limit.
    a1 = 0.4 if coefficient_kind == "heat" else 0.6
    factor = math.exp(-decay * time_s) * 2.0 * beta / (radius * radius)
    if r == 0.0:
        return factor * 2.0
    return factor * (2.0 + 3.0 * a1 * r / radius)


def _coefficient(r: float, radius: float, coefficient_kind: str) -> float:
    return 1.0 + (0.4 if coefficient_kind == "heat" else 0.6) * r / radius


def manufactured_run(n_intervals: int, dt_s: float, end_time_s: float, coefficient_kind: str, interface_mean: str = "harmonic") -> float:
    radius = 1.0
    grid = make_radial_grid(radius, n_intervals)
    nodes = grid.nodes_m
    coefficients = [_coefficient(r, radius, coefficient_kind) for r in nodes]
    faces = interface_values(coefficients, interface_mean)
    values = [_exact(r, 0.0, radius) for r in nodes]
    current = 0.0
    while current < end_time_s - 1e-14:
        current += dt_s
        source = []
        for r in nodes:
            exact_value = _exact(r, current, radius)
            source.append(-exact_value - _operator(r, current, radius, coefficient_kind))
        surface_coefficient = faces[-1]
        environment = _exact(radius, current, radius) + surface_coefficient * _exact_derivative(radius, current, radius) / 3.0
        system = assemble_variable_radial_system(values, grid, dt_s, [1.0] * len(nodes), faces, 3.0, environment, source_values=source)
        values = solve_system(system)
    exact = [_exact(r, end_time_s, radius) for r in nodes]
    return max(abs(a - b) for a, b in zip(values, exact))


def run_benchmark() -> Dict[str, object]:
    spatial = {}
    for kind in ("heat", "moisture"):
        errors = {}
        for n in (10, 20, 40, 80):
            dt = 0.02 / (n * n)
            errors[str(n)] = manufactured_run(n, dt, 0.02, kind)
        spatial[kind] = errors
    temporal = {}
    for kind in ("heat", "moisture"):
        errors = {}
        for dt in (0.02, 0.01, 0.005, 0.0025):
            errors[str(dt)] = manufactured_run(320, dt, 0.2, kind)
        temporal[kind] = errors
    interface_comparison = {}
    for method in ("arithmetic", "harmonic"):
        interface_comparison[method] = {
            kind: manufactured_run(80, 0.02 / (80 * 80), 0.02, kind, interface_mean=method)
            for kind in ("heat", "moisture")
        }
    def orders(values: Dict[str, float], numeric_keys: Iterable[float], *, refinement_ratio: str) -> Dict[str, float]:
        keys = list(numeric_keys)
        result = {}
        for a, b in zip(keys, keys[1:]):
            key_a = str(int(a)) if float(a).is_integer() else str(a)
            key_b = str(int(b)) if float(b).is_integer() else str(b)
            denominator = math.log(b / a) if refinement_ratio == "space" else math.log(a / b)
            result[f"{a:g}_to_{b:g}"] = math.log(values[key_a] / values[key_b]) / denominator
        return result
    return {
        "spatial_linf": spatial,
        "spatial_observed_order": {
            kind: orders(values, (10.0, 20.0, 40.0, 80.0), refinement_ratio="space") for kind, values in spatial.items()
        },
        "temporal_linf": temporal,
        "temporal_observed_order": {
            kind: orders(values, (0.02, 0.01, 0.005, 0.0025), refinement_ratio="time") for kind, values in temporal.items()
        },
        "interface_comparison_linf_n80": interface_comparison,
        "pass": all(min(order.values()) > 0.8 for order in ({kind: orders(values, (10.0, 20.0, 40.0, 80.0), refinement_ratio="space") for kind, values in spatial.items()}.values()))
        and all(min(order.values()) > 0.7 for order in ({kind: orders(values, (0.02, 0.01, 0.005, 0.0025), refinement_ratio="time") for kind, values in temporal.items()}.values())),
    }
