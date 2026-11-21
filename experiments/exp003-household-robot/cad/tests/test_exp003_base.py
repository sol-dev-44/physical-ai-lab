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


def heights(**changes):
    from exp003_cad.params import Caster, derive_heights

    return derive_heights(CASE, HORN, Cradle(), replace(Caster(), **changes))


def test_cradles_on_top_put_the_plate_low_and_the_caster_in_a_raised_pocket():
    h = heights()
    assert h.axle_mm == pytest.approx(60.0)
    assert h.plate_top_mm == pytest.approx(60.0 - 15.6)
    assert h.plate_underside_mm == pytest.approx(40.4)
    # The 50 mm caster mounts 9.6 mm above the underside: a boss 5.6 mm above the plate's top.
    assert h.caster_mount_mm == pytest.approx(9.6)
    assert h.caster_boss_mm == pytest.approx(5.6)
    assert h.caster_wheel_gap_mm == pytest.approx(40.4 - 38.1)


def test_caster_swing_circle():
    from exp003_cad.params import Caster

    assert Caster().swing_radius_mm == pytest.approx(13 + 19.05)


def test_a_short_caster_is_refused_for_a_raised_pocket():
    with pytest.raises(ValueError, match="inside the plate"):
        heights(height_mm=42.0)


def test_a_tall_caster_wheel_that_would_rub_the_plate_is_refused():
    with pytest.raises(ValueError, match="rub"):
        heights(wheel_mm=40.0)
