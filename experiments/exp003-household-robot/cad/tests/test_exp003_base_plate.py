"""The base plate's numbers. No CadQuery needed."""

import math
from dataclasses import replace
from pathlib import Path

import pytest
from exp003_cad.params import (
    BaseLayout,
    BasePlate,
    Caster,
    CasterCup,
    Cradle,
    derive_base_plate,
    load,
    load_case,
)

SERVO = Path(__file__).resolve().parents[1] / "servo.toml"
CASE = load_case(SERVO)
HORN = load(SERVO).horn


def plate(layout=None, p=None):
    return derive_base_plate(
        CASE, HORN, Cradle(), Caster(), layout or BaseLayout(), p or BasePlate(), CasterCup()
    )


def test_outline_is_the_planned_plate_and_fits_the_left_nozzle():
    d = plate()
    assert (d.x_back_mm, d.x_front_mm) == (-190.0, 110.0)
    assert d.half_width_mm == pytest.approx(130.8)
    # The AMS feeds the left nozzle, which reaches 325 x 320 mm.
    assert d.x_front_mm - d.x_back_mm <= 320 and 2 * d.half_width_mm <= 325


def test_wheel_module_holes_mirror_across_the_robot():
    d = plate()
    # Plate v2 (2026-11-24): 4 foot bolts per side plus 7 through the beam; the cradle holes
    # are gone.
    assert len(d.wheel_holes) == 15
    for x, y in d.wheel_holes:
        assert any(math.isclose(x, a) and math.isclose(-y, b) for a, b in d.wheel_holes)
    # Bolts on two lines across each wheel's load, the outer one near the plate edge.
    ys = sorted({abs(y) for _, y in d.wheel_holes})
    assert ys[-1] == pytest.approx(124.0) and 85.0 in ys


def test_caster_cup_and_its_screws_stay_on_the_plate():
    d = plate()
    assert d.caster_xy == (-158.0, 0.0)
    for x, _ in d.cup_holes:
        assert x - 1.7 >= d.x_back_mm + 5.0 - 1e-6


def test_battery_fits_between_the_cradles_with_its_straps():
    d = plate()
    bx0, bx1, by0, by1 = d.battery_box
    assert (bx1 - bx0, by1 - by0) == pytest.approx((66 + 2, 152 + 2))
    assert len(d.strap_slots) == 4
    for x0, x1, _, _ in d.strap_slots:
        assert x1 < bx0 - 2 or x0 > bx1 + 2  # outside the fences


def test_strap_slots_take_the_measured_strap_not_the_buckle():
    d = plate()
    assert d.measured
    assert d.strap_slots[0][3] - d.strap_slots[0][2] == pytest.approx(21.5 + 3.0)
    assert not plate(p=replace(BasePlate(), strap_width_mm=None)).measured


def test_screws_all_come_from_the_kit_with_nuts():
    d = plate()
    assert "8 x M3 x 12" in d.screws["wheel module"]
    assert "7 x M3 x 16" in d.screws["wheel module"]
    assert "M3 x 16" in d.screws["cup"]
    assert "M4 x 8" in d.screws["caster"]


def test_a_caster_too_far_back_is_refused():
    with pytest.raises(ValueError):
        plate(layout=replace(BaseLayout(), caster_x_mm=-170.0))
