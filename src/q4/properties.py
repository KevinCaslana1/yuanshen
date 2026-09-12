"""Official Appendix 4 moisture-dependent properties for Q4."""

from __future__ import annotations

from math import exp, isfinite
from typing import Iterable, List, Sequence


def _positive(value: float, name: str) -> float:
    value = float(value)
    if not isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def density(C: float) -> float:
    C = _positive(C, "C [kg/kg]")
    return 760.0 + 90.0 * C


def cp(C: float) -> float:
    C = _positive(C, "C [kg/kg]")
    return 1850.0 + 2150.0 * C / (C + 1.0)


def conductivity(C: float) -> float:
    C = _positive(C, "C [kg/kg]")
    return 0.12 + 0.20 * C / (C + 1.0)


def diffusivity(C: float, T_K: float) -> float:
    C = _positive(C, "C [kg/kg]")
    T_K = _positive(T_K, "T_K [K]")
    return 4.2e-4 * exp(-0.30 / C) * exp(-3850.0 / T_K)


def _map(values: Iterable[float], fn) -> List[float]:
    return [fn(v) for v in values]


def density_array(values: Sequence[float]) -> List[float]:
    return _map(values, density)


def cp_array(values: Sequence[float]) -> List[float]:
    return _map(values, cp)


def conductivity_array(values: Sequence[float]) -> List[float]:
    return _map(values, conductivity)


def diffusivity_array(C_values: Sequence[float], T_values: Sequence[float]) -> List[float]:
    if len(C_values) != len(T_values):
        raise ValueError("C and T arrays must have equal length")
    return [diffusivity(c, t) for c, t in zip(C_values, T_values)]

