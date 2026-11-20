"""Checks on the base plate's plan-view layout and balance. No CadQuery needed."""

from dataclasses import replace
from pathlib import Path

import pytest
from exp003_cad.params import BaseLayout, Cradle, derive_base, load, load_case

SERVO = Path(__file__).resolve().parents[1] / "servo.toml"
CASE = load_case(SERVO)
HORN = load(SERVO).horn


def base(**changes):
    return derive_base(CASE, HORN, Cradle(), replace(BaseLayout(), **changes))


def test_wide_stance_with_the_battery_across_between_the_servos():
    d = base()
    assert d.cradle_back_y_mm == pytest.approx(152 / 2 + 20)
    # Cradle back face, then 36.8 mm to the wheel's inner face.
    assert d.wheel_inner_y_mm == pytest.approx(96 + 2.5 + 34.3)
    assert d.track_mm == pytest.approx(297.6)
    assert d.width_over_tires_mm == pytest.approx(329.6)


def test_plate_stays_clear_of_the_wheels_and_fits_the_printer():
    d = base()
    assert d.wheel_inner_y_mm - d.plate_half_width_mm == pytest.approx(2.0)
    assert d.plate_length_mm <= 325 and 2 * d.plate_half_width_mm <= 320


def test_centre_of_mass_sits_behind_the_axle_even_with_the_arm_reaching_forward():
    d = base()
    assert d.com_x_mm < -20
    assert d.com_x_with_arm_mm < -10
    assert 0.15 < d.caster_share < 0.5  # the wheels keep most of the weight for traction


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"battery_x_mm": 15.0, "other": ()}, "behind the axle"),
        ({"arm_base_x_mm": 0.0}, "arm"),
        ({"front_mm": 160.0}, "does not fit"),
        ({"caster_x_mm": -60.0}, "caster"),
        ({"battery_x_mm": 0.0}, "arm"),  # battery on the axle: fine alone, not with the arm
    ],
)
def test_unworkable_layouts_are_rejected(changes, message):
    with pytest.raises(ValueError, match=message):
        base(**changes)
