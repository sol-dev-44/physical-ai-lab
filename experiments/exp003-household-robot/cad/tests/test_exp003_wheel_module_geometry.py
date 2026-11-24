"""Wheel module v2 as a solid, with the vendor servo model in place. Skipped without CadQuery."""

from pathlib import Path

import pytest

cq = pytest.importorskip("cadquery")

from exp003_cad.params import (  # noqa: E402
    BaseLayout,
    Cradle,
    WheelModule,
    derive_wheel_module,
    load,
    load_case,
)
from exp003_cad.wheel_module import (  # noqa: E402
    servo_in_module,
    wheel_module,
    wheel_module_for_print,
)

HERE = Path(__file__).resolve().parents[1]
CASE = load_case(HERE / "servo.toml")
HORN = load(HERE / "servo.toml").horn
D = derive_wheel_module(CASE, HORN, Cradle(), BaseLayout())
M = WheelModule()
STEP = HERE / "vendor" / "STS3215_03a.step"


@pytest.fixture(scope="module")
def part():
    return wheel_module(CASE, HORN)


def inside(shape, x, y, z):
    return shape.val().isInside(cq.Vector(x, y, z))


def test_one_solid_across_the_robot(part):
    assert len(part.solids().vals()) == 1
    bb = part.val().BoundingBox()
    assert (bb.ymin, bb.ymax) == pytest.approx((-130.8, 130.8))
    assert (bb.zmin, bb.zmax) == pytest.approx((0.0, D.top_z_mm))
    assert (bb.xmin, bb.xmax) == pytest.approx((M.foot_back_mm, M.beam_x_mm[1]))


@pytest.mark.parametrize("side", [1, -1])
def test_servo_drops_in_without_touching(part, side):
    servo = servo_in_module(str(STEP), CASE, HORN, side)
    sb = servo.val().BoundingBox()
    assert (sb.xmin, sb.xmax) == pytest.approx((-35.2, 10.2), abs=0.05)  # far end back
    clash = part.intersect(servo)
    assert not clash.solids().vals() or clash.val().Volume() < 1e-3


@pytest.mark.parametrize("side", [1, -1])
def test_case_is_held_on_every_side(part, side):
    x0, x1, z0, z1, _ = D.cavity
    y = side * 110.0  # half way along the case
    zm = (z0 + z1) / 2
    assert inside(part, x0 - 2.5, y, zm) and inside(part, x1 + 2.5, y, zm)  # end walls
    assert inside(part, -12.0, y, z1 + 2.5) and inside(part, -12.0, y, z0 - 1.5)  # top, under
    assert not inside(part, -12.0, y, zm)  # and the case's room


def test_m2_counterbores_leave_the_wall_under_the_heads(part):
    cb0, cb1 = D.counterbore_y_mm
    for x, z in D.m2_holes:
        assert not inside(part, x + 1.9, (cb0 + cb1) / 2, z)  # in the counterbore
        assert inside(part, x + 1.9, (cb1 + D.back_wall_y_mm[1]) / 2, z)  # wall under the head
        assert not inside(part, x, (cb1 + D.back_wall_y_mm[1]) / 2, z)  # the screw's hole


def test_driver_reaches_the_lower_screws(part):
    for x in D.driver_grooves_x:
        assert not inside(part, x, 87.0, M.driver_groove_mm[1] + 1.0)


def test_cable_notch_in_the_rear_gusset(part):
    (r0, r1), _ = D.end_walls_x
    y = D.foot[2] + 3.0
    assert not inside(part, (r0 + r1) / 2, y, M.foot_mm + 3.0)
    assert inside(part, (r0 + r1) / 2, D.back_wall_y_mm[0] - 1.0, 20.0)  # gusset above it


def test_prints_on_the_beam_front_within_the_bed():
    bb = wheel_module_for_print(CASE, HORN).val().BoundingBox()
    assert bb.zmin == pytest.approx(0.0)
    assert bb.zlen == pytest.approx(M.beam_x_mm[1] - M.foot_back_mm)
    assert bb.ylen <= 320 and bb.xlen <= 325
