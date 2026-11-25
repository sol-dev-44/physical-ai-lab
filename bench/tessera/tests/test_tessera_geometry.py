"""Tessera's solids. Skipped unless CadQuery is installed."""

import math

import pytest

cq = pytest.importorskip("cadquery")

from tessera_cad.false_floor import false_floor, false_floor_print  # noqa: E402
from tessera_cad.key import field_key, key  # noqa: E402
from tessera_cad.module import cup, front_label_box  # noqa: E402
from tessera_cad.params import (  # noqa: E402
    ALCOHOL,
    ALCOHOL_BOTTLE_MM,
    BIG,
    FALSE_FLOOR,
    FIRST_PIECE_CUPS,
    PARTS_TRAY,
    Cup,
    Engraving,
    FalseFloor,
    Grid,
    Joint,
    body,
    boss_size,
    cavity,
    false_floor_height,
    false_floor_top,
    module_height,
)

G, J, E, F = Grid(), Joint(), Engraving(), FALSE_FLOOR
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


@pytest.fixture(scope="module")
def alcohol():
    return cup(ALCOHOL)


@pytest.fixture(scope="module")
def insert():
    return false_floor(ALCOHOL)


def _cavity_centre(c):
    x0, x1, y0, y1 = cavity(G, c.nx, c.ny)
    return (x0 + x1) / 2, (y0 + y1) / 2


@pytest.mark.parametrize("c", [ALCOHOL, BIG], ids=["ALCOHOL", "BIG"])
def test_tall_2x2_cups_are_one_solid_over_4_in_square(c):
    part = cup(c)
    assert len(part.solids().vals()) == 1
    bb = part.val().BoundingBox()
    assert (bb.xlen, bb.ylen, bb.zlen) == pytest.approx((103.5, 103.5, 130.0))
    assert bb.xlen > 4 * 25.4  # owner, 2026-11-25: at least 4 x 4 in, and deep
    assert not inside(part, *_cavity_centre(c), 129.0)  # open all the way down
    assert inside(part, *_cavity_centre(c), 1.2)


@pytest.mark.parametrize("turn", [0, 15, 30, 45])
def test_bottle_stands_on_the_false_floor_clear_of_the_bosses(alcohol, insert, turn):
    w, d, h = ALCOHOL_BOTTLE_MM
    cx, cy = _cavity_centre(ALCOHOL)
    top = false_floor_top(G, F)

    def block(z0, tall):
        b = cq.Workplane("XY").box(w, d, tall, centered=(True, True, False))
        return b.rotate((0, 0, 0), (0, 0, 1), turn).translate((cx, cy, z0))

    bottle = block(top + 0.01, h)
    assert _volume(bottle.intersect(alcohol)) < 1e-6
    assert _volume(bottle.intersect(insert)) < 1e-6
    # its base stands on plate: all of it square on, over 99% turned 45 (a corner over the notch)
    foot = block(top - 0.5, 0.5)
    held = _volume(foot.intersect(insert)) / foot.val().Volume()
    assert held == pytest.approx(1.0) if turn < 45 else held > 0.99


def test_false_floor_fits_the_cavity_at_its_clearance_and_no_looser(alcohol, insert):
    assert len(insert.solids().vals()) == 1
    assert insert.val().BoundingBox().zmin == pytest.approx(G.floor_mm)  # skirt on the floor
    assert _volume(insert.intersect(alcohol)) < 1e-6
    c = F.clearance_mm
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        near = insert.translate((dx * (c - 0.02), dy * (c - 0.02), 0))
        assert _volume(near.intersect(alcohol)) < 1e-6
        far = insert.translate((dx * (c + 0.05), dy * (c + 0.05), 0))
        assert _volume(far.intersect(alcohol)) > 0.1  # a wall or boss stops it: no rattle
    bb = insert.val().BoundingBox()
    x0, x1, y0, y1 = cavity(G, ALCOHOL.nx, ALCOHOL.ny)
    assert (bb.xlen, bb.ylen) == pytest.approx((x1 - x0 - 2 * c, y1 - y0 - 2 * c))


def test_stash_is_its_depth_under_a_closed_plate(insert):
    cx, cy = _cavity_centre(ALCOHOL)
    x0, _, y0, _ = cavity(G, ALCOHOL.nx, ALCOHOL.ny)
    floor, ceiling = G.floor_mm, G.floor_mm + F.stash_mm
    assert F.stash_mm >= 10.0  # a USB stick, SD cards, folded notes
    for z in (floor + 0.05, floor + F.stash_mm / 2, ceiling - 0.05):
        assert not inside(insert, cx, cy + 25, z)  # the stash, away from the engraving
        assert inside(insert, x0 + F.clearance_mm + F.skirt_mm / 2, cy, z)  # the skirt
    assert inside(insert, cx, cy + 25, ceiling + E.depth_mm + 0.3)  # the plate above
    assert insert.val().BoundingBox().zmax == pytest.approx(floor + false_floor_height(F))
    # the lift notch is open top to bottom, the lip beside it has room under it to hook
    assert not inside(insert, cx, y0 + F.notch_r_mm - 1, ceiling + 1)
    hook = y0 + F.notch_r_mm + F.lip_mm / 2
    assert inside(insert, cx, hook, ceiling + 1) and not inside(insert, cx, hook, ceiling - 1)
    # and a skirt ring closes the stash behind the lip
    assert inside(insert, cx, y0 + F.notch_r_mm + F.lip_mm + F.skirt_mm / 2, floor + 1)


def test_stash_ceiling_carries_the_secret(insert):
    plain = false_floor(ALCOHOL, FalseFloor(secret=""))
    assert plain.val().Volume() - insert.val().Volume() > 5.0  # mm3 of letters


def _overhangs(part):
    """Centroids of triangles facing down more than 45 degrees (the slicer would support them)."""
    verts, tris = part.val().tessellate(0.05, 0.2)
    out = []
    for a, b, c in tris:
        p, q, r = verts[a], verts[b], verts[c]
        n = (q - p).cross(r - p)
        if n.Length > 1e-9 and n.z / n.Length < -math.cos(math.radians(45)) - 0.01:
            out.append((p + q + r) * (1 / 3))
    return out


def test_false_floor_prints_flat_with_nothing_overhanging():
    part = false_floor_print(ALCOHOL)
    bb = part.val().BoundingBox()
    assert bb.zmin == pytest.approx(0.0) and bb.zlen == pytest.approx(false_floor_height(F))
    down = _overhangs(part)
    assert down and all(abs(p.z) < 1e-6 for p in down)  # only the face on the bed


@pytest.mark.parametrize("c", [ALCOHOL, BIG], ids=["ALCOHOL", "BIG"])
def test_tall_cups_print_open_side_up_without_supports(c):
    part = cup(c)
    _, _, y0, _ = body(G, c.nx, c.ny)
    for p in _overhangs(part):
        on_bed = p.z < E.depth_mm + 1e-6  # the bed, and the underside letters' tiny bridges
        label = p.y < y0 + E.depth_mm + 1e-6 and 0 < p.z < module_height(G, c.steps)
        assert on_bed or label, f"overhang at {p}"
