"""The deck fit coupon's solid. Skipped unless CadQuery is installed."""

import pytest

cq = pytest.importorskip("cadquery")

from exp003_cad.deck_coupon import deck_coupon  # noqa: E402
from exp003_cad.params import DeckCoupon, derive_deck_coupon  # noqa: E402

D = derive_deck_coupon(DeckCoupon())


@pytest.fixture(scope="module")
def part():
    return deck_coupon()


def inside(part, x, y, z):
    return part.val().isInside(cq.Vector(x, y, z))


def test_one_small_solid(part):
    assert len(part.solids().vals()) == 1
    bb = part.val().BoundingBox()
    assert (bb.xlen, bb.ylen) == pytest.approx((96.0, 45.0))
    assert bb.zlen == pytest.approx(10.0)  # channel walls: 2 mm panel + 8 mm
    assert part.val().Volume() < 12000  # mm3: about 15 g of PETG at most


def test_rocker_and_jack_holes_go_through(part):
    for x, y, _, _ in D.rockers:
        assert not inside(part, x, y, 1.0)
    for x, y, dia in D.jacks:
        assert not inside(part, x, y, 1.0)
        assert inside(part, x + dia / 2 + 1.0, y, 1.0)


def test_boss_has_a_nut_pocket_below_and_a_stud_hole_above(part):
    bx, by = D.boss_xy
    assert not inside(part, bx + 2.0, by, 1.5)  # inside the hex pocket, off the hole
    assert inside(part, bx + 2.0, by, D.nut_pocket_depth_mm + 1.0)  # roof over the pocket
    assert not inside(part, bx, by, D.boss_height_mm - 0.5)  # stud hole
    assert inside(part, bx + 3.9, by, D.boss_height_mm - 0.5)  # boss wall


def test_channel_is_open_between_its_walls(part):
    x = sum(D.channel_x_mm) / 2
    assert not inside(part, x, 22.5, 5.0)
    assert inside(part, x, 22.5 - D.channel_inner_mm / 2 - 0.8, 5.0)
