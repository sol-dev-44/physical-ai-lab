"""The compute tray's solid. Skipped unless CadQuery is installed."""

from pathlib import Path

import pytest

cq = pytest.importorskip("cadquery")

from exp003_cad.compute_tray import compute_tray  # noqa: E402
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

SERVO = Path(__file__).resolve().parents[1] / "servo.toml"
PLATE = derive_base_plate(
    load_case(SERVO), load(SERVO).horn, Cradle(), Caster(), BaseLayout(), BasePlate(), CasterCup()
)
D = derive_deck(PLATE)
C = D.compute


@pytest.fixture(scope="module")
def part():
    return compute_tray(D)


def inside(part, x, y, z):
    return part.val().isInside(cq.Vector(x, y, z))


def test_one_light_solid_on_the_plate_top(part):
    assert len(part.solids().vals()) == 1
    bb = part.val().BoundingBox()
    assert bb.zmin == pytest.approx(0.0)
    assert bb.zmax == pytest.approx(D.floor_mm + 8.0)  # the channel walls
    assert bb.xlen <= 300 and bb.ylen <= 320
    assert part.val().Volume() < 20000  # mm3: about 15 g at 4 walls, 30% infill


def test_grid_holes_go_through_the_floor(part):
    for x, y in C.holes:
        assert not inside(part, x, y, 1.5)
        assert inside(part, x + 3.0, y, 1.5)


def test_bosses_have_nut_pockets_from_below_and_stud_holes(part):
    pocket = D.coupon.nut_pocket_depth_mm
    for x, y in C.bosses:
        assert not inside(part, x + 2.0, y, pocket - 0.5)  # hex pocket, off the stud hole
        assert inside(part, x + 2.0, y, pocket + 1.0)  # roof over the nut
        assert not inside(part, x, y, D.coupon.boss_height_mm - 0.5)  # stud hole
        assert inside(part, x + 3.9, y, D.coupon.boss_height_mm - 0.5)  # boss wall


def test_channel_is_open_between_its_walls(part):
    back, front = C.walls
    y = (back.y0 + back.y1) / 2
    assert inside(part, (back.x0 + back.x1) / 2, y, D.floor_mm + 4.0)
    assert inside(part, (front.x0 + front.x1) / 2, y, D.floor_mm + 4.0)
    assert not inside(part, (back.x1 + front.x0) / 2, y, D.floor_mm + 4.0)
    assert front.x0 - back.x1 == pytest.approx(27.6)


def test_zip_tie_slots_go_through_and_join_under_the_floor(part):
    for tie in C.ties:
        for x0, x1, y0, y1 in tie.slots:
            assert not inside(part, (x0 + x1) / 2, (y0 + y1) / 2, D.floor_mm / 2)
        gx0, gx1, gy0, gy1 = tie.groove
        mid = ((gx0 + gx1) / 2, (gy0 + gy1) / 2)
        assert not inside(part, *mid, tie.groove_mm / 2)  # the groove under the board
        assert inside(part, *mid, tie.groove_mm + 0.7)  # the floor above it


def test_bridge_posts_stay_uncovered(part):
    for x, y in D.bridge.posts:
        assert not inside(part, x, y, 1.5)
        assert not inside(part, x, y + 5.5, 1.5)
