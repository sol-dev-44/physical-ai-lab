"""Tessera's solids. Skipped unless CadQuery is installed."""

import math

import pytest

cq = pytest.importorskip("cadquery")

from tessera_cad.key import field_key, key  # noqa: E402
from tessera_cad.module import cup, front_label_box  # noqa: E402
from tessera_cad.params import (  # noqa: E402
    FIRST_PIECE_CUPS,
    PARTS_TRAY,
    Cup,
    Grid,
    Joint,
    boss_size,
)

G, J = Grid(), Joint()
M = G.unit_mm / 2  # middle of a 1 x 1 cell


@pytest.fixture(scope="module")
def tips():
    return cup(FIRST_PIECE_CUPS[0])


def inside(part, x, y, z):
    return part.val().isInside(cq.Vector(x, y, z))


def test_one_solid_of_the_right_size(tips):
    assert len(tips.solids().vals()) == 1
    bb = tips.val().BoundingBox()
    assert (bb.xlen, bb.ylen, bb.zlen) == pytest.approx((51.5, 51.5, 52.0))
    assert 15000 < tips.val().Volume() < 40000  # mm3: solid, about 20 to 50 g of PLA


def test_sockets_run_top_to_bottom_and_bosses_back_them(tips):
    y_in_socket = G.gap_mm + J.depth_mm / 2
    y_in_boss = G.gap_mm + J.depth_mm + J.boss_skin_mm / 2
    for z in (0.3, 26, 51.7):
        assert not inside(tips, M, y_in_socket, z)
        assert inside(tips, M, y_in_boss, z)
    # beside the socket the plain wall, then the cavity
    w, _ = boss_size(G, J)
    assert inside(tips, M + w / 2 + 2, G.gap_mm + 1, M)
    assert not inside(tips, M + w / 2 + 2, G.gap_mm + G.wall_mm + 1, M)


def test_open_top_and_solid_floor(tips):
    assert not inside(tips, 12, 12, M)
    assert inside(tips, 12, 12, 1.2)


def test_front_label_is_cut_left_of_the_groove(tips):
    cx, width = front_label_box(G, J, 1)
    assert width > 10
    region = cq.Workplane("XY").box(width + 3, 1.0, 20).translate((cx, G.gap_mm + 0.3, M))
    plain = cq.Workplane("XY").box(width + 3, 1.0, 20).translate((cx, G.gap_mm + 0.3, M))
    plain = plain.intersect(cup(Cup(label="", serial=1)))
    engraved = region.intersect(tips)
    assert plain.val().Volume() - engraved.val().Volume() > 1.0


def test_underside_engraving_is_shallow(tips):
    bottom = cq.Workplane("XY").box(30, 12, 0.6, centered=(True, True, False))
    bottom = bottom.translate((M, M, 0))
    cut = bottom.val().Volume() - bottom.intersect(tips).val().Volume()
    assert cut > 2.0  # mm3 of letters
    assert inside(tips, M, M, 0.9) or inside(tips, 12, 12, 0.9)


@pytest.mark.parametrize("clearance", [0.10, 0.15, 0.20])
def test_key_drops_between_two_cups_without_touching(clearance):
    left = cup(Cup(label="", serial=1))
    right = cup(Cup(label="", serial=2)).translate((G.unit_mm, 0, 0))
    k = key(G.unit_mm, clearance=clearance).translate((G.unit_mm, G.unit_mm / 2, 0))
    for c in (left, right):
        clash = k.intersect(c)
        vol = clash.val().Volume() if clash.solids().vals() else 0.0
        assert vol < 1e-6
    # and it cannot slide out sideways: its ends are wider than the socket mouths
    assert k.val().BoundingBox().ylen > J.neck_mm


def test_test_key_carries_its_mark():
    plain, marked = key(G.unit_mm, 0.15), key(G.unit_mm, 0.15, mark="15")
    assert plain.val().Volume() - marked.val().Volume() > 0.5


def _volume(part):
    return part.val().Volume() if part.solids().vals() else 0.0


@pytest.mark.parametrize("interference", [0.10, 0.20])
def test_ribbed_key_grips_only_on_its_ribs(interference):
    left = cup(Cup(label="", serial=1))
    k = key(G.unit_mm, clearance=0.10, rib_interference=interference)
    k = k.translate((G.unit_mm, G.unit_mm / 2, 0))
    plain = key(G.unit_mm, clearance=0.10).translate((G.unit_mm, G.unit_mm / 2, 0))
    assert len(k.solids().vals()) == 1
    overlap = k.intersect(left).val().Volume()
    # two ribs bite into each cup: a circular segment of the rib along its straight height
    rho, h = J.rib_radius_mm, interference
    segment = rho**2 * math.acos((rho - h) / rho) - (rho - h) * math.sqrt(2 * rho * h - h * h)
    assert overlap == pytest.approx(2 * segment * (G.unit_mm - J.rib_start_mm), rel=0.05)
    assert _volume(plain.intersect(left)) < 1e-6
    # the ribs start above the lead chamfer, so the key still starts in by hand
    low = cq.Workplane("XY").box(40, 40, 1.4, centered=(True, True, False))
    low = low.translate((G.unit_mm, G.unit_mm / 2, 0))
    assert _volume(k.intersect(left).intersect(low)) < 1e-6


def test_parts_tray_is_one_low_2x1():
    tray = cup(PARTS_TRAY)
    assert len(tray.solids().vals()) == 1
    bb = tray.val().BoundingBox()
    assert (bb.xlen, bb.ylen, bb.zlen) == pytest.approx((103.5, 51.5, 26.0))


def test_field_key_is_r1():
    r1 = key(26, clearance=0.10, rib_interference=0.10)
    assert field_key(26).val().Volume() == pytest.approx(r1.val().Volume())
    assert field_key(26).val().Volume() > key(26, clearance=0.10).val().Volume()
