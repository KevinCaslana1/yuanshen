"""Question 1 implementation candidates and numerical validation tools."""

from .config import DEFAULT_PARAMETERS, Q1Parameters, Q1RunConfig
from .inputs import BoundaryProvider
from .solver import Q1Result, run_m1

__all__ = [
    "BoundaryProvider",
    "DEFAULT_PARAMETERS",
    "Q1Parameters",
    "Q1Result",
    "Q1RunConfig",
    "run_m1",
]
