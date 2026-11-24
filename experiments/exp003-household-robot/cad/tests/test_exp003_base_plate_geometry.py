"""The base plate against the wheel module and caster cup solids. Skipped without CadQuery."""

import math
from pathlib import Path

import pytest

cq = pytest.importorskip("cadquery")

from exp003_cad.base_plate import base_plate  # noqa: E402
from exp003_cad.params import (  # noqa: E402
    PLATE_MM,
    BaseLayout,
    BasePlate,
    Caster,
    CasterCup,
    Cradle,
    derive_base_plate,
    load,
    load_case,
)
from exp003_cad.wheel_module import wheel_module  # noqa: E402

SERVO = Path(__file__).resolve().parents[1] / "servo.toml"
CASE = load_case(SERVO)
HORN = load(SERVO).horn
D = derive_base_plate(CASE, HORN, Cradle(), Caster(), BaseLayout(), BasePlate(), CasterCup())


@pytest.fixture(scope="module")
def part():
    return base_plate(D)


@pytest.fixture(scope="module")
def wheel_part():
    """The wheel module standing on the plate's top face."""
    return wheel_module(CASE, HORN).translate((0, 0, PLATE_MM))


def inside(shape, x, y, z):
    return shape.val().isInside(cq.Vector(x, y, z))


def test_plate_is_one_solid_4_mm_thick_with_fences(part):
    assert len(part.solids().vals()) == 1
    bb = part.val().BoundingBox()
    assert (bb.xlen, bb.ylen) == pytest.approx((300.0, 261.6))
    assert bb.zlen == pytest.approx(PLATE_MM + BasePlate().fence_height_mm)


def test_plate_holes_line_up_with_the_wheel_module_holes(part, wheel_part):
    for x, y in D.wheel_holes:
        assert not inside(part, x, y, PLATE_MM / 2)  # hole through the plate
        z = PLATE_MM + 2.0  # inside the module's foot or beam
        assert not inside(wheel_part, x, y, z)  # and through the module
        assert inside(wheel_part, x + 2.6, y, z)  # with plastic round it


def test_check_above_can_fail(wheel_part):
    """Self-test: a hole 3 mm off would land in solid foot."""
    x, y = D.wheel_holes[0]
    assert inside(wheel_part, x + 3.0, y, PLATE_MM + 2.0)


def test_wheel_module_sits_on_the_plate_not_in_a_hole(part):
    for x0, x1, y0, y1 in D.wheel_footprint:
        for x in (x0 + 1, (x0 + x1) / 2, x1 - 1):
            for y in (y0 + 1, y1 - 1):
                assert inside(part, x, y, PLATE_MM - 0.5)


def test_fork_swings_clear_through_the_plate(part):
    cx, _ = D.caster_xy
    r = Caster().fork_radius_mm + 0.5
    for i in range(36):
        a = math.radians(i * 10)
        assert not inside(part, cx + r * math.cos(a), r * math.sin(a), PLATE_MM / 2)


def test_cup_mount_holes_go_through_the_plate(part):
    for x, y in D.cup_holes:
        assert not inside(part, x, y, PLATE_MM / 2)
        assert inside(part, x + 3.5, y, PLATE_MM / 2) or inside(part, x - 3.5, y, PLATE_MM / 2)
