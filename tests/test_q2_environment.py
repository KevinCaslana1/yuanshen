from pathlib import Path

import pytest

from src.q2.environment import EnvironmentProvider


ROOT = Path(__file__).resolve().parents[1]


def test_attachment1_points_are_reproduced_exactly() -> None:
    provider = EnvironmentProvider.from_attachment1(ROOT / "A题/附件/附件1.xlsx")
    assert provider.raw_count == 241
    for time_s, temperature, moisture in zip(provider.times_s[::37], provider.temperatures_c[::37], provider.moistures_kg_kg[::37]):
        assert provider.at(time_s) == (temperature, moisture)


def test_linear_midpoint_and_post_attachment_are_explicit() -> None:
    provider = EnvironmentProvider.from_attachment1(ROOT / "A题/附件/附件1.xlsx")
    t0, t1 = provider.times_s[3:5]
    temp0, temp1 = provider.temperatures_c[3:5]
    moist0, moist1 = provider.moistures_kg_kg[3:5]
    assert provider.at((t0 + t1) / 2) == pytest.approx(((temp0 + temp1) / 2, (moist0 + moist1) / 2))
    with pytest.raises(ValueError):
        provider.at(provider.last_time_s + 1.0)
    constant = EnvironmentProvider.from_attachment1(ROOT / "A题/附件/附件1.xlsx", post_attachment_mode="constant")
    assert constant.at(constant.last_time_s + 1.0) == (50.0, 0.05)


def test_pchip_is_dependency_free_and_reproduces_raw_knots() -> None:
    provider = EnvironmentProvider.from_attachment1(ROOT / "A题/附件/附件1.xlsx", method="pchip")
    for time_s, temperature, moisture in zip(provider.times_s, provider.temperatures_c, provider.moistures_kg_kg):
        assert provider.at(time_s) == (temperature, moisture)
    for left, right in zip(provider.times_s[:-1], provider.times_s[1:]):
        midpoint = (left + right) / 2.0
        temperature, moisture = provider.at(midpoint)
        left_index = provider.times_s.index(left)
        assert min(provider.temperatures_c[left_index:left_index + 2]) <= temperature <= max(provider.temperatures_c[left_index:left_index + 2])
        assert min(provider.moistures_kg_kg[left_index:left_index + 2]) <= moisture <= max(provider.moistures_kg_kg[left_index:left_index + 2])
