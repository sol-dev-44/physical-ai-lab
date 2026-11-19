"""Geometry checks on the tire against the real hub. Skipped unless CadQuery is installed."""

import math

import pytest

cq = pytest.importorskip("cadquery")

from exp003_cad.hub import full_hub  # noqa: E402
from exp003_cad.params import Horn, HubParams, Tire, derive_tire  # noqa: E402
from exp003_cad.tire import tire  # noqa: E402

P = HubParams(horn=Horn(19.9, 2.08, 4, 13.6, "M3", 5.0, 2.0, 4.0, 2.0), measured=True)
T = Tire()
D = derive_tire(P, T)
W = P.wheel


@pytest.fixture(scope="module")
def ring():
    return tire(P, T)


@pytest.fixture(scope="module")
def overlap(ring):
    return ring.intersect(full_hub(P))


def inside(part, r, z, angle=0.3):
    return part.val().isInside(cq.Vector(r * math.cos(angle), r * math.sin(angle), z))


def test_tire_makes_a_120_mm_wheel_as_wide_as_the_hub(ring):
    bb = ring.val().BoundingBox()
    assert bb.xlen == pytest.approx(T.od_mm, abs=0.01)
    assert bb.ylen == pytest.approx(T.od_mm, abs=0.01)
    assert (bb.zmin, bb.zmax) == (pytest.approx(0.0, abs=0.01), pytest.approx(W.width_mm, abs=0.01))


def test_bore_lips_and_tread(ring):
    mid = W.width_mm / 2
    assert inside(ring, D.bore_mm / 2 + 0.2, mid)
    assert not inside(ring, D.bore_mm / 2 - 0.2, mid)
    # Lips over the flanges at both edges, clear of the flange lands.
    for z in (0.5, W.width_mm - 0.5):
        assert inside(ring, D.lip_bore_mm / 2 + 0.2, z)
        assert not inside(ring, D.lip_bore_mm / 2 - 0.3, z)
    assert inside(ring, T.od_mm / 2 - 0.2, mid)


def test_tire_touches_the_hub_only_where_it_grips_the_seat(overlap):
    # The only overlap is the stretch: bore (53.5 mm radius) against the rim seat (54.0), between
    # the flange slopes. Nothing presses on the flanges, so the tire seats fully.
    bb = overlap.val().BoundingBox()
    assert max(abs(bb.xmax), abs(bb.xmin)) <= W.rim_od_mm / 2 + 0.01
    assert bb.zmin >= W.flange_land_mm + W.flange_mm - 0.01
    assert bb.zmax <= W.width_mm - W.flange_land_mm - W.flange_mm + 0.01
    seat_length = W.width_mm - 2 * (W.flange_land_mm + W.flange_mm)
    band = math.pi * ((W.rim_od_mm / 2) ** 2 - (D.bore_mm / 2) ** 2) * seat_length
    assert overlap.val().Volume() == pytest.approx(band, rel=0.05)
