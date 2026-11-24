"""The power tray's solid, switch panel included. Skipped unless CadQuery is installed."""

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
from exp003_cad.power_tray import power_tray  # noqa: E402

SERVO = Path(__file__).resolve().parents[1] / "servo.toml"
PLATE = derive_base_plate(
    load_case(SERVO), load(SERVO).horn, Cradle(), Caster(), BaseLayout(), BasePlate(), CasterCup()
)
D = derive_deck(PLATE)
P = D.power
PX = (P.panel.x0 + P.panel.x1) / 2


@pytest.fixture(scope="module")
def part():
    return power_tray(D)


def inside(part, x, y, z):
    return part.val().isInside(cq.Vector(x, y, z))


def test_one_light_solid(part):
    assert len(part.solids().vals()) == 1
    bb = part.val().BoundingBox()
    assert bb.zmin == pytest.approx(0.0) and bb.zmax == pytest.approx(P.panel.z1)
    assert bb.xmin == pytest.approx(-179.0)
    assert bb.xlen <= 300 and bb.ylen <= 320
    assert part.val().Volume() < 30000  # mm3: about 23 g


def test_grid_holes_go_through(part):
    for x, y in P.holes:
        assert not inside(part, x, y, 1.5)
        assert inside(part, x + 3.0, y, 1.5)


def test_drok_pads_have_slots_over_sliding_nut_channels(part):
    for p in P.pads:
        sx0, sx1, sy0, sy1 = p.slot
        y = (sy0 + sy1) / 2
        for x in (sx0 + 1.8, (sx0 + sx1) / 2, sx1 - 1.8):  # the whole 54 to 68 mm range
            assert not inside(part, x, y, p.top_mm - 1.0)  # slot through the roof
            assert not inside(part, x, y, p.channel_mm - 1.0)  # channel under it
        assert inside(part, (sx0 + sx1) / 2, y + 3.5, p.top_mm - 1.0)  # roof beside the slot
        assert inside(part, (sx0 + sx1) / 2, y + 3.4, 1.0)  # channel wall holds the nut's flats
        # The channel opens at the pad's outer end (away from the DROK), so a nut slides in.
        front = p.pad[0] > -118.0
        end = p.pad[1] - 0.3 if front else p.pad[0] + 0.3
        assert not inside(part, end, y, 1.0)


def test_ina226_pocket_is_open_with_walls(part):
    walls = P.pocket_walls
    plus, minus = walls[0], walls[1]
    x = (plus.x0 + plus.x1) / 2
    assert inside(part, x, (plus.y0 + plus.y1) / 2, plus.z1 - 0.5)
    assert inside(part, x, (minus.y0 + minus.y1) / 2, minus.z1 - 0.5)
    assert not inside(part, x, (plus.y0 + minus.y1) / 2, D.floor_mm + 1.0)


def test_zip_tie_slots_go_through(part):
    assert len(P.ties) == 6
    for tie in P.ties:
        for x0, x1, y0, y1 in tie.slots:
            assert not inside(part, (x0 + x1) / 2, (y0 + y1) / 2, D.floor_mm / 2)
        gx0, gx1, gy0, gy1 = tie.groove
        assert not inside(part, (gx0 + gx1) / 2, (gy0 + gy1) / 2, tie.groove_mm / 2)


def test_switch_panel_cutouts_go_through(part):
    y, z, across, tall = P.rocker_cutout
    assert not inside(part, PX, y, z)
    assert not inside(part, PX, y + across / 2 - 0.3, z + tall / 2 - 0.3)  # upright: tall in z
    assert inside(part, PX, y + across / 2 + 0.5, z)
    assert inside(part, PX, y, z + tall / 2 + 0.5)
    jy, jz, jd = P.jack_hole
    assert not inside(part, PX, jy, jz)
    assert not inside(part, PX, jy + jd / 2 - 0.3, jz)
    assert inside(part, PX, jy + jd / 2 + 0.5, jz)
    assert inside(part, PX, jy, jz - jd / 2 - 0.5)
    assert not inside(part, PX, jy, jz + jd / 2 + 1.5)  # the teardrop's point, for printing


def test_panel_stands_up_with_gussets(part):
    assert inside(part, PX, P.panel.y0 + 1.0, P.panel.z1 - 0.5)
    for g in P.gussets:
        y = (g.y0 + g.y1) / 2
        assert inside(part, P.panel.x1 + 1.0, y, P.panel.z1 - 3.0)  # tall at the panel
        assert inside(part, g.x1 - 1.5, y, D.floor_mm + 0.5)  # low at its far end
        assert not inside(part, g.x1 - 1.5, y, P.panel.z1 - 2.0)
