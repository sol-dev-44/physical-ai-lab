"""The caster cup's solid. Skipped unless CadQuery is installed."""

from pathlib import Path

import pytest

cq = pytest.importorskip("cadquery")

from exp003_cad.caster_cup import caster_cup  # noqa: E402
from exp003_cad.params import Caster, Cradle, derive_heights, load, load_case  # noqa: E402

SERVO = Path(__file__).resolve().parents[1] / "servo.toml"
HEIGHTS = derive_heights(load_case(SERVO), load(SERVO).horn, Cradle(), Caster())


@pytest.fixture(scope="module")
def part():
    return caster_cup(Caster(), HEIGHTS)


def inside(part, x, y, z):
    return part.val().isInside(cq.Vector(x, y, z))


def test_one_light_solid_of_the_right_size(part):
    assert len(part.solids().vals()) == 1
    bb = part.val().BoundingBox()
    assert (bb.xlen, bb.ylen, bb.zlen) == pytest.approx((55.0, 55.0, 12.6))
    assert part.val().Volume() < 11000  # mm3: about 14 g of PETG at most


def test_roof_has_the_four_screw_holes_and_the_centre_hole(part):
    for x in (-17.875, 17.875):
        for y in (-13.875, 13.875):
            assert not inside(part, x, y, 1.5)
            assert inside(part, x + 3.5, y, 1.5)  # roof round the hole
    assert not inside(part, 0, 0, 1.5)


def test_cavity_is_open_and_the_walls_are_solid(part):
    assert not inside(part, 23.0, 19.0, 8.0)  # inside the plate's corner clearance
    assert inside(part, 26.5, 0, 8.0)  # round wall, past the sweep
    assert inside(part, 24.5, 20.6, 8.0)  # box wall round the plate's corner


def test_fork_sweeps_clear_all_the_way_round(part):
    import math

    r = Caster().fork_radius_mm + 0.5
    for i in range(36):
        a = math.radians(i * 10)
        for z in (4.0, 8.0, 12.0):
            assert not inside(part, r * math.cos(a), r * math.sin(a), z), (i * 10, z)


def test_light_version_is_much_lighter(part):
    from exp003_cad.params import CASTER_CUP_TEST

    light = caster_cup(Caster(), HEIGHTS, CASTER_CUP_TEST)
    assert light.val().Volume() < 0.6 * part.val().Volume()
    r = Caster().fork_radius_mm + 0.5
    assert not light.val().isInside(cq.Vector(0, r, 8.0))
