from math import isfinite

import pytest

from src.q2.properties import cp, diffusivity, conductivity, density


def test_appendix3_known_points() -> None:
    C = 2.55
    assert density(C) == pytest.approx(976.4)
    assert cp(C) == pytest.approx(3415.295774647887)
    assert conductivity(C) == pytest.approx(0.48295774647887324)
    assert diffusivity(C, 301.15) == pytest.approx(5.641680373025664e-9, rel=1e-13)
    assert diffusivity(C, 323.15) == pytest.approx(1.3470968217415811e-8, rel=1e-13)
    assert density(1.0) == pytest.approx(778.0)
    assert cp(1.0) == pytest.approx(2818.0)
    assert conductivity(1.0) == pytest.approx(0.4)
    assert diffusivity(1.0, 323.15) == pytest.approx(1.024723031208691e-8, rel=1e-13)
    assert density(0.15) == pytest.approx(669.2)
    assert cp(0.15) == pytest.approx(1806.8695652173913)
    assert conductivity(0.15) == pytest.approx(0.25956521739130434)
    assert diffusivity(0.15, 323.15) == pytest.approx(8.001208146652626e-10, rel=1e-13)


def test_properties_are_finite_positive_and_monotone_on_domain() -> None:
    concentrations = [0.15, 0.5, 1.0, 2.55, 4.0]
    for C in concentrations:
        values = [density(C), cp(C), conductivity(C), diffusivity(C, 323.15)]
        assert all(isfinite(value) and value > 0 for value in values)
    assert density(2.0) > density(1.0)
    assert cp(2.0) > cp(1.0)
    assert conductivity(2.0) > conductivity(1.0)
    assert diffusivity(2.0, 323.15) > diffusivity(1.0, 323.15)
    assert diffusivity(1.0, 323.15) > diffusivity(1.0, 301.15)


def test_temperature_argument_is_kelvin_not_celsius() -> None:
    assert diffusivity(2.55, 323.15) / diffusivity(2.55, 301.15) == pytest.approx(2.387758137065687, rel=1e-12)
    assert diffusivity(2.55, 50.0) < 1e-30


@pytest.mark.parametrize("function,args", [(density, (0.0,)), (cp, (0.0,)), (conductivity, (0.0,)), (diffusivity, (0.0, 323.15)), (diffusivity, (1.0, 0.0))])
def test_invalid_property_domain_fails_closed(function, args) -> None:
    with pytest.raises(ValueError):
        function(*args)
