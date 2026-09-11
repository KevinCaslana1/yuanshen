"""Question 2 implementation: coupled variable-property radial model."""

from .config import Q2Parameters, Q2RunConfig
from .environment import EnvironmentProvider
from .baseline import Q2BaselineResult, run_q2_b0
from .lineage import canonical_csv_path, canonical_path, load_canonical_manifest
from .properties import cp, diffusivity, conductivity, density
from .solver import Q2NonConvergenceError, Q2RunResult, run_q2

__all__ = [
    "EnvironmentProvider",
    "Q2BaselineResult",
    "Q2NonConvergenceError",
    "Q2Parameters",
    "Q2RunConfig",
    "Q2RunResult",
    "cp",
    "diffusivity",
    "conductivity",
    "canonical_csv_path",
    "canonical_path",
    "density",
    "load_canonical_manifest",
    "run_q2",
    "run_q2_b0",
]
