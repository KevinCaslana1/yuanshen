"""Explicit Q2 physical and numerical configurations."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class Q2Parameters:
    radius_m: float = 0.02
    length_m: float = 0.25
    heat_transfer_w_m2_k: float = 25.0
    mass_transfer_m_s: float = 8.0e-7
    initial_temperature_c: float = 28.0
    initial_moisture_kg_kg: float = 2.55


@dataclass(frozen=True)
class Q2RunConfig:
    end_time_s: float = 60.0
    time_step_s: float = 0.25
    candidate: str = "A"
    n_intervals: int = 320
    cluster_power: float = 2.0
    scheme: str = "bdf2"
    interface_mean: str = "harmonic"
    interpolation: str = "linear"
    post_attachment_mode: str = "raise"
    output_interval_s: float = 1.0
    picard_tolerance: float = 1.0e-8
    picard_max_iterations: int = 50
    picard_relaxation: float = 1.0
    input_path: Path = Path("A题/附件/附件1.xlsx")
    parameters: Q2Parameters = field(default_factory=Q2Parameters)

    def __post_init__(self) -> None:
        if self.end_time_s <= 0 or self.time_step_s <= 0:
            raise ValueError("end_time_s and time_step_s must be positive")
        if abs(self.end_time_s / self.time_step_s - round(self.end_time_s / self.time_step_s)) > 1e-10:
            raise ValueError("end_time_s must be an integer number of time steps")
        if self.candidate not in {"A", "B"}:
            raise ValueError("candidate must be A or B")
        if self.scheme not in {"be", "bdf2"}:
            raise ValueError("scheme must be be or bdf2")
        if self.interface_mean not in {"arithmetic", "harmonic"}:
            raise ValueError("interface_mean must be arithmetic or harmonic")
        if self.interpolation not in {"linear", "pchip"}:
            raise ValueError("interpolation must be linear or pchip")
        if self.post_attachment_mode not in {"raise", "constant"}:
            raise ValueError("post_attachment_mode must be raise or constant")
        if self.output_interval_s <= 0 or abs(self.output_interval_s / self.time_step_s - round(self.output_interval_s / self.time_step_s)) > 1e-10:
            raise ValueError("output_interval_s must be an integer number of time steps")
        if self.n_intervals < 2 or self.cluster_power <= 1.0:
            raise ValueError("invalid spatial grid configuration")
        if self.picard_tolerance <= 0 or self.picard_max_iterations < 1 or not (0 < self.picard_relaxation <= 1):
            raise ValueError("invalid Picard configuration")

    def as_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["input_path"] = str(self.input_path)
        result["parameters"] = asdict(self.parameters)
        return result
