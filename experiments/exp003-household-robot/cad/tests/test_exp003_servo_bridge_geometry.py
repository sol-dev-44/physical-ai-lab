"""The servo board bridge's solid. Skipped unless CadQuery is installed."""

import math
from pathlib import Path

import pytest

cq = pytest.importorskip("cadquery")

from exp003_cad.params import (  # noqa: E402
    BaseLayout,
    BasePlate,
    Caster,
    CasterCup,
    Cradle,
    derive_base_plate,
    derive_deck,
    load,
    load_case,
)
from exp003_cad.servo_bridge import servo_bridge, servo_bridge_for_print  # noqa: E402

SERVO = Path(__file__).resolve().parents[1] / "servo.toml"
PLATE = derive_base_plate(
    load_case(SERVO), load(SERVO).horn, Cradle(), Caster(), BaseLayout(), BasePlate(), CasterCup()
)
D = derive_deck(PLATE)
B = D.bridge
UNDER, TOP = B.platform_z_mm


@pytest.fixture(scope="module")
def part():
    return servo_bridge(D)


def inside(part, x, y, z):
    return part.val().isInside(cq.Vector(x, y, z))


def test_one_light_solid(part):
    assert len(part.solids().vals()) == 1
    bb = part.val().BoundingBox()
    assert (bb.zmin, bb.zmax) == pytest.approx((0.0, TOP))
    assert part.val().Volume() < 12000  # mm3: about 9 g


def test_nothing_below_the_bosses_over_the_cup(part):
    cx, cy = PLATE.caster_xy
    for r in (5.0, 15.0, 25.0, 33.0, 36.5):
        for i in range(24):
            a = math.radians(15 * i)
            for z in (2.0, 8.0, 12.4):
                assert not inside(part, cx + r * math.cos(a), cy + r * math.sin(a), z), (r, i, z)


def test_bosses_hang_under_the_platform_with_nut_pockets(part):
    pocket = D.coupon.nut_pocket_depth_mm
    for x, y in B.bosses:
        assert not inside(part, x + 2.0, y, B.boss_bottom_mm + pocket - 0.5)  # hex pocket
        assert inside(part, x + 2.0, y, B.boss_bottom_mm + pocket + 0.5)  # roof over it
        assert not inside(part, x, y, TOP - 0.5)  # stud hole through the platform
        assert inside(part, x + 3.9, y, B.boss_bottom_mm + 1.0)  # boss wall
        assert not inside(part, x + 3.9, y, B.boss_bottom_mm - 0.5)  # nothing below it


def test_posts_have_a_hole_through_and_a_nut_well_from_the_top(part):
    for x, y in B.posts:
        assert not inside(part, x, y, 1.0)  # M3 hole at the foot
        assert inside(part, x + 2.6, y, B.nut_seat_mm - 1.0)  # solid under the nut seat
        assert not inside(part, x + 2.6, y, B.nut_seat_mm + 1.0)  # hex well above it
        assert not inside(part, x + 2.6, y, TOP - 0.5)  # open at the top
        assert inside(part, x + B.post_mm / 2 - 0.4, y, 10.0)  # post wall


def test_platform_window_is_open(part):
    x0, x1, y0, y1 = B.window
    assert not inside(part, (x0 + x1) / 2, (y0 + y1) / 2, TOP - 1.0)
    assert inside(part, x0 - 1.5, (y0 + y1) / 2, TOP - 1.0)


def test_prints_upside_down_on_its_flat_top():
    p = servo_bridge_for_print(D)
    bb = p.val().BoundingBox()
    assert bb.zmin == pytest.approx(0.0) and bb.zmax == pytest.approx(TOP)
    # The platform's top face is on the bed: solid just above z = 0 by a boss, posts end at TOP.
    x, y = B.bosses[0]
    assert p.val().isInside(cq.Vector(x + 3.9, -y, 0.5))
    px, py = B.posts[0]
    assert p.val().isInside(cq.Vector(px + 3.0, -py, TOP - 0.5))  # the post's foot, up top
