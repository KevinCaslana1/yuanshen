"""Official Appendix 3 variable properties for Q2.

Internal units are C [kg/kg], T_K [K], rho [kg/m^3], cp [J/(kg K)],
k [W/(m K)] and D [m^2/s].  No output rounding is performed here.
"""

from __future__ import annotations

from math import exp, isfinite
from typing import Iterable, List, Sequence


def _positive_finite(value: float, name: str) -> float:
    value = float(value)
    if not isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def _moisture(value: float) -> float:
    return _positive_finite(value, "C [kg/kg]")


def density(C: float) -> float:
    """Appendix 3: rho(C) = 650 + 128 C [kg/m^3]."""

    C = _moisture(C)
    return 650.0 + 128.0 * C


def cp(C: float) -> float:
    """Appendix 3: cp(C) = 1450 + 2736 C/(C+1) [J/(kg K)]."""

    C = _moisture(C)
    return 1450.0 + 2736.0 * C / (C + 1.0)


def conductivity(C: float) -> float:
    """Appendix 3: k(C) = 0.21 + 0.38 C/(C+1) [W/(m K)]."""

    C = _moisture(C)
    return 0.21 + 0.38 * C / (C + 1.0)


def diffusivity(C: float, T_K: float) -> float:
    """Appendix 3: D(C,T) [m^2/s], with T explicitly in Kelvin."""

    C = _moisture(C)
    T_K = _positive_finite(T_K, "T_K [K]")
    return 2.4e-3 * exp(-0.45 / C) * exp(-3850.0 / T_K)


def _map(values: Iterable[float], function) -> List[float]:
    return [function(value) for value in values]


def density_array(values: Sequence[float]) -> List[float]:
    return _map(values, density)


def cp_array(values: Sequence[float]) -> List[float]:
    return _map(values, cp)


def conductivity_array(values: Sequence[float]) -> List[float]:
    return _map(values, conductivity)


def diffusivity_array(C_values: Sequence[float], T_values: Sequence[float]) -> List[float]:
    if len(C_values) != len(T_values):
        raise ValueError("C and T arrays must have the same length")
    return [diffusivity(C, T) for C, T in zip(C_values, T_values)]
