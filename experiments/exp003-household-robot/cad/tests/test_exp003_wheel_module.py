"""Wheel module v2's numbers and load checks. No CadQuery needed."""

from dataclasses import replace
from pathlib import Path

import pytest
from exp003_cad.params import (
    MAX_LEVER_RATIO,
    BaseLayout,
    Caster,
    Cradle,
    WheelModule,
    derive_cradle,
    derive_heights,
    derive_wheel_module,
    load,
    load_case,
)

SERVO = Path(__file__).resolve().parents[1] / "servo.toml"
CASE = load_case(SERVO)
HORN = load(SERVO).horn


def module(**change):
    return derive_wheel_module(CASE, HORN, Cradle(), BaseLayout(), replace(WheelModule(), **change))


def test_the_axle_stays_where_the_cradles_had_it():
    d = module()
    assert d.axis_z_mm == pytest.approx(derive_cradle(CASE, HORN, Cradle()).axle_above_foot_mm)
    assert derive_heights(CASE, HORN, Cradle(), Caster()).axle_mm == pytest.approx(60.0)
    assert d.cavity[2] == pytest.approx(Cradle().cheek_mm)  # wall under the case unchanged


def test_case_is_boxed_on_four_sides_and_the_back():
    d = module()
    x0, x1, z0, z1, y0 = d.cavity
    assert x1 - x0 == pytest.approx(CASE.length_mm + 0.4)
    assert z1 - z0 == pytest.approx(CASE.width_mm + 0.4)
    assert d.top_z_mm - z1 == pytest.approx(5.0)
    (r0, r1), (n0, n1) = d.end_walls_x
    assert (r1 - r0, n1 - n0) == pytest.approx((5.0, 5.0))
    assert d.back_wall_y_mm[1] - d.back_wall_y_mm[0] == pytest.approx(5.0)
    assert d.outer_y_mm == pytest.approx(130.8)  # 2 mm short of the hub, as the plate edge


def test_servo_screws_bite_as_before_through_the_thicker_wall():
    d = module()
    under_head = d.step_y_mm - d.counterbore_y_mm[1]
    assert CASE.mount_screw_length_mm - under_head == pytest.approx(3.5)
    assert len(d.m2_holes) == 4


def test_hella_sturdy_load_checks():
    d = module()
    assert 10 < d.wheel_load_n < 20  # static, arm reaching forward
    assert d.design_load_n == pytest.approx(5 * d.wheel_load_n)
    assert d.lever_ratio < MAX_LEVER_RATIO  # the cradles were 4.7
    assert d.bolt_tension_n < 100
    assert d.wall_stress_mpa < 1.0


def test_bolts_on_one_line_are_refused():
    with pytest.raises(ValueError, match="two lines"):
        module(foot_bolts=((5.0, 85.0), (-46.0, 85.0)))


def test_bolts_too_far_inboard_fail_the_lever_rule():
    with pytest.raises(ValueError, match="lever"):
        module(
            foot_bolts=((5.0, 85.0), (-46.0, 85.0), (-46.0, 110.0)), beam_bolts_y_mm=(110.0, 0.0)
        )


def test_screws_come_from_the_kit():
    d = module()
    assert "8 x M3 x 12" in d.screws["foot"]
    assert "7 x M3 x 16" in d.screws["beam"]
