"""The base plate against the real cradle and caster cup solids. Skipped without CadQuery."""

import math
from pathlib import Path

import pytest

cq = pytest.importorskip("cadquery")

from exp003_cad.base_plate import base_plate  # noqa: E402
from exp003_cad.cradle import cradle  # noqa: E402
from exp003_cad.params import (  # noqa: E402
    PLATE_MM,
    BaseLayout,
    BasePlate,
    Caster,
    CasterCup,
    Cradle,
    cradle_to_plate,
    derive_base_plate,
    load,
    load_case,
)

SERVO = Path(__file__).resolve().parents[1] / "servo.toml"
CASE = load_case(SERVO)
HORN = load(SERVO).horn
D = derive_base_plate(CASE, HORN, Cradle(), Caster(), BaseLayout(), BasePlate(), CasterCup())


@pytest.fixture(scope="module")
def part():
    return base_plate(D)


@pytest.fixture(scope="module")
def cradle_part():
    return cradle(CASE, HORN)


def inside(shape, x, y, z):
    return shape.val().isInside(cq.Vector(x, y, z))


def to_cradle(side, x, y, z):
    """Plate point to the cradle's frame on that side (inverse of cradle_to_plate)."""
    cols, (tx, ty, tz) = cradle_to_plate(CASE, HORN, Cradle(), BaseLayout(), side)
    p = (x - tx, y - ty, z - tz)
    return tuple(sum(cols[i][j] * p[j] for j in range(3)) for i in range(3))


def test_plate_is_one_solid_4_mm_thick_with_fences(part):
    assert len(part.solids().vals()) == 1
    bb = part.val().BoundingBox()
    assert (bb.xlen, bb.ylen) == pytest.approx((300.0, 261.6))
    assert bb.zlen == pytest.approx(PLATE_MM + BasePlate().fence_height_mm)


def test_plate_holes_line_up_with_the_cradle_ear_holes(part, cradle_part):
    for x, y in D.cradle_holes:
        side = 1 if y > 0 else -1
        assert not inside(part, x, y, PLATE_MM / 2)  # hole through the plate
        z = PLATE_MM + 2.0  # inside the ear's 4 mm thickness
        assert not inside(cradle_part, *to_cradle(side, x, y, z))  # and through the ear
        assert inside(cradle_part, *to_cradle(side, x + 2.6, y, z))  # with the ear round it


def test_check_above_can_fail(cradle_part):
    """Self-test: a hole 3 mm off would land in solid ear."""
    x, y = D.cradle_holes[0]
    assert inside(cradle_part, *to_cradle(1, x + 3.0, y, PLATE_MM + 2.0))


def test_cradle_feet_sit_on_the_plate_not_in_a_hole(part):
    for x0, x1, y0, y1 in D.cradle_feet:
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
