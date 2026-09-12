"""Dependency-free monotone PchipInterpolator-compatible radius function."""

from __future__ import annotations

from bisect import bisect_right
from typing import Sequence


class PchipInterpolator:
    """Fritsch-Carlson monotone cubic Hermite interpolator.

    The public call and derivative interface mirrors the SciPy class used by
    the workflow contract, while keeping this repository self-contained.
    """

    def __init__(self, x: Sequence[float], y: Sequence[float]):
        if len(x) != len(y) or len(x) < 2:
            raise ValueError("PCHIP x/y arrays must have equal length >= 2")
        self.x = tuple(float(v) for v in x)
        self.y = tuple(float(v) for v in y)
        if any(b <= a for a, b in zip(self.x, self.x[1:])):
            raise ValueError("PCHIP x values must be strictly increasing")
        h = [b - a for a, b in zip(self.x, self.x[1:])]
        d = [(b - a) / step for a, b, step in zip(self.y, self.y[1:], h)]

        def endpoint(h0, h1, d0, d1):
            value = ((2.0 * h0 + h1) * d0 - h0 * d1) / (h0 + h1)
            if value * d0 <= 0.0:
                return 0.0
            if d0 * d1 < 0.0 and abs(value) > 3.0 * abs(d0):
                return 3.0 * d0
            return value

        m = [0.0] * len(self.x)
        m[0] = endpoint(h[0], h[1] if len(h) > 1 else h[0], d[0], d[1] if len(d) > 1 else d[0])
        m[-1] = endpoint(h[-1], h[-2] if len(h) > 1 else h[-1], d[-1], d[-2] if len(d) > 1 else d[-1])
        for i in range(1, len(m) - 1):
            if d[i - 1] * d[i] <= 0.0:
                m[i] = 0.0
            else:
                w1 = 2.0 * h[i] + h[i - 1]
                w2 = h[i] + 2.0 * h[i - 1]
                m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
        self.m = tuple(m)

    def _interval(self, value: float) -> int:
        if value <= self.x[0]:
            return 0
        if value >= self.x[-1]:
            return len(self.x) - 2
        return bisect_right(self.x, value) - 1

    def __call__(self, value: float) -> float:
        value = float(value)
        if value <= self.x[0]:
            return self.y[0]
        if value >= self.x[-1]:
            return self.y[-1]
        i = self._interval(value)
        h = self.x[i + 1] - self.x[i]
        u = (value - self.x[i]) / h
        h00 = (1 + 2 * u) * (1 - u) ** 2
        h10 = u * (1 - u) ** 2
        h01 = u * u * (3 - 2 * u)
        h11 = u * u * (u - 1)
        return h00 * self.y[i] + h10 * h * self.m[i] + h01 * self.y[i + 1] + h11 * h * self.m[i + 1]

    def derivative(self, value: float) -> float:
        value = float(value)
        i = self._interval(value)
        h = self.x[i + 1] - self.x[i]
        u = max(0.0, min(1.0, (value - self.x[i]) / h))
        # derivative with respect to u divided by h
        dh00 = 6 * u * (u - 1) / h
        dh10 = (1 - 4 * u + 3 * u * u)
        dh01 = 6 * u * (1 - u) / h
        dh11 = (3 * u * u - 2 * u) 
        return dh00 * self.y[i] + dh10 * self.m[i] + dh01 * self.y[i + 1] + dh11 * self.m[i + 1]

