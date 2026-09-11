"""Q1 constants and run configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Q1Parameters:
    density_kg_m3: float = 820.0
    heat_capacity_j_kg_k: float = 2600.0
    conductivity_w_m_k: float = 0.36
    heat_transfer_w_m2_k: float = 25.0
    mass_transfer_m_s: float = 8.0e-7
    radius_m: float = 0.02
    length_m: float = 0.25

    def diffusivity_m2_s(self, moisture_kg_kg: float) -> float:
        if moisture_kg_kg <= 0.0:
            raise ValueError("Q1 diffusivity is undefined for non-positive moisture")
        return 7.0e-9 * pow(2.718281828459045, -0.89 / moisture_kg_kg)


@dataclass(frozen=True)
class Q1RunConfig:
    end_time_s: float = 1800.0
    time_step_s: float = 1.0
    n_intervals: int = 80
    interpolation: str = "linear"
    surface_boundary: str = "robin"
    picard_tolerance: float = 1.0e-8
    picard_max_iterations: int = 50
    initial_temperature_c: float = 28.0
    initial_moisture_kg_kg: float = 2.55
    input_path: Path = Path("A题/附件/附件1.xlsx")

    def __post_init__(self) -> None:
        if self.end_time_s <= 0.0 or self.time_step_s <= 0.0:
            raise ValueError("Q1 end time and time step must be positive")
        if self.n_intervals < 2:
            raise ValueError("Q1 n_intervals must be at least 2")
        if self.interpolation not in {"linear", "zero_order"}:
            raise ValueError("Q1 interpolation must be linear or zero_order")
        if self.surface_boundary not in {"robin", "dirichlet"}:
            raise ValueError("Q1 surface_boundary must be robin or dirichlet")
        if self.picard_tolerance <= 0.0 or self.picard_max_iterations < 1:
            raise ValueError("invalid Picard configuration")
        quotient = self.end_time_s / self.time_step_s
        if abs(quotient - round(quotient)) > 1.0e-10:
            raise ValueError("end_time_s must be an integer number of time steps")


DEFAULT_PARAMETERS = Q1Parameters()
