"""Read-only Attachment 1 environment providers for Q2."""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Sequence, Tuple

from openpyxl import load_workbook

from src.common.paths import resolve_project_path


@dataclass(frozen=True)
class EnvironmentProvider:
    """Attachment 1 interpolation with explicit post-data behavior.

    ``linear`` is the reproducible default. ``pchip`` is intentionally
    optional: it is available only when SciPy is installed and is never
    silently substituted for linear interpolation.
    """

    times_s: Tuple[float, ...]
    temperatures_c: Tuple[float, ...]
    moistures_kg_kg: Tuple[float, ...]
    method: str = "linear"
    post_attachment_mode: str = "raise"
    post_temperature_c: float = 50.0
    post_moisture_kg_kg: float = 0.05
    source_path: str = ""
    source_sha256: str = ""

    @classmethod
    def from_attachment1(
        cls,
        path: str | Path,
        *,
        method: str = "linear",
        post_attachment_mode: str = "raise",
        post_temperature_c: float = 50.0,
        post_moisture_kg_kg: float = 0.05,
    ) -> "EnvironmentProvider":
        resolved = resolve_project_path(path)
        raw = resolved.read_bytes()
        workbook = load_workbook(resolved, read_only=True, data_only=True)
        worksheet = workbook.active
        rows = list(worksheet.iter_rows(min_row=2, values_only=True))
        workbook.close()
        if not rows:
            raise ValueError("attachment 1 contains no data rows")
        times, temperatures, moistures = [], [], []
        for row in rows:
            if len(row) < 3 or any(value is None for value in row[:3]):
                raise ValueError("attachment 1 contains an incomplete row")
            times.append(float(row[0]))
            temperatures.append(float(row[1]))
            moistures.append(float(row[2]))
        if any(right <= left for left, right in zip(times, times[1:])):
            raise ValueError("attachment 1 times must be strictly increasing")
        return cls(
            tuple(times), tuple(temperatures), tuple(moistures), method,
            post_attachment_mode, float(post_temperature_c),
            float(post_moisture_kg_kg), str(resolved), sha256(raw).hexdigest(),
        )

    def __post_init__(self) -> None:
        if self.method not in {"linear", "pchip"}:
            raise ValueError("method must be linear or pchip")
        if self.post_attachment_mode not in {"raise", "constant"}:
            raise ValueError("post_attachment_mode must be raise or constant")
        if len(self.times_s) < 2 or len(self.times_s) != len(self.temperatures_c) or len(self.times_s) != len(self.moistures_kg_kg):
            raise ValueError("environment arrays have inconsistent lengths")
        if any(right <= left for left, right in zip(self.times_s, self.times_s[1:])):
            raise ValueError("environment times must be strictly increasing")
        if self.method == "pchip":
            try:
                import scipy.interpolate  # noqa: F401
            except ImportError as exc:
                raise RuntimeError("PCHIP requested but SciPy is not installed") from exc

    @property
    def raw_count(self) -> int:
        return len(self.times_s)

    @property
    def last_time_s(self) -> float:
        return self.times_s[-1]

    def _linear(self, values: Sequence[float], time_s: float) -> float:
        right = bisect_right(self.times_s, time_s)
        if right == 0:
            return float(values[0])
        if right == len(self.times_s):
            return float(values[-1])
        left = right - 1
        if self.times_s[left] == time_s:
            return float(values[left])
        fraction = (time_s - self.times_s[left]) / (self.times_s[right] - self.times_s[left])
        return float(values[left] + fraction * (values[right] - values[left]))

    def _pchip(self, values: Sequence[float], time_s: float) -> float:
        from scipy.interpolate import PchipInterpolator

        return float(PchipInterpolator(self.times_s, values, extrapolate=False)(time_s))

    def at(self, time_s: float) -> Tuple[float, float]:
        time_s = float(time_s)
        if time_s < self.times_s[0]:
            raise ValueError(f"boundary time {time_s} s precedes Attachment 1")
        if time_s > self.times_s[-1]:
            if self.post_attachment_mode == "raise":
                raise ValueError(f"boundary time {time_s} s requires an unapproved post-attachment rule")
            return self.post_temperature_c, self.post_moisture_kg_kg
        if self.method == "linear":
            return self._linear(self.temperatures_c, time_s), self._linear(self.moistures_kg_kg, time_s)
        return self._pchip(self.temperatures_c, time_s), self._pchip(self.moistures_kg_kg, time_s)
