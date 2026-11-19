"""Geometry checks on the built hub. Skipped unless CadQuery is installed (see cad/README.md)."""

import math
from dataclasses import replace

import pytest

cq = pytest.importorskip("cadquery")

from exp003_cad.hub import full_hub, hub_coupon  # noqa: E402
from exp003_cad.params import Horn, HubParams, derive  # noqa: E402

P = HubParams(
    horn=Horn(
        od_mm=20.0,
        thickness_mm=2.5,
        bolt_count=4,
        bolt_circle_mm=14.0,
        bolt_size="M2",
        center_head_mm=5.0,
        center_head_height_mm=1.0,
        shaft_height_mm=4.0,
        raised_case_mm=4.0,
    ),
    measured=True,
)
D = derive(P)
P_STEP = HubParams(horn=replace(P.horn, raised_case_mm=1.0), measured=True)


def solid_at(part, x, y, z) -> bool:
    return part.val().isInside(cq.Vector(x, y, z))


def size(part):
    bb = part.val().BoundingBox()
    return bb.xlen, bb.ylen, bb.zlen


@pytest.fixture(scope="module")
def coupon():
    return hub_coupon(P)


@pytest.fixture(scope="module")
def hub():
    return full_hub(P)


def test_coupon_is_a_small_disc(coupon):
    x, y, z = size(coupon)
    assert x == pytest.approx(D.coupon_od_mm, abs=0.01)
    assert y == pytest.approx(D.coupon_od_mm, abs=0.01)
    assert z == pytest.approx(D.web_mm, abs=0.01)


@pytest.mark.parametrize("make", [hub_coupon, full_hub])
def test_bolt_holes_go_through_and_material_sits_between_them(make):
    part = make(P)
    r = P.horn.bolt_circle_mm / 2
    for i in range(P.horn.bolt_count):
        a = 2 * math.pi * i / P.horn.bolt_count
        for z in (0.2, D.web_mm / 2, D.web_mm - 0.2):
            assert not solid_at(part, r * math.cos(a), r * math.sin(a), z)
        between = a + math.pi / P.horn.bolt_count
        assert solid_at(part, r * math.cos(between), r * math.sin(between), D.web_mm / 2)


def test_servo_side_is_flat_with_an_open_centre_pocket(coupon):
    # Solid right down to the bed, inside and outside the horn's footprint (between two holes).
    a = math.pi / P.horn.bolt_count
    for r in (P.horn.od_mm / 2 - 1.0, P.horn.od_mm / 2 + 3.0):
        assert solid_at(coupon, r * math.cos(a), r * math.sin(a), 0.2)
    assert not solid_at(coupon, 0, 0, D.center_pocket_depth_mm - 0.2)
    assert solid_at(coupon, 0, 0, D.center_pocket_depth_mm + 0.3)


@pytest.mark.parametrize("make", [hub_coupon, full_hub])
def test_underside_steps_up_beyond_the_horn_over_a_raised_case(make):
    d = derive(P_STEP)
    assert d.relief_mm == pytest.approx(1.0)
    part = make(P_STEP)
    a = math.pi / P.horn.bolt_count
    inside, outside = P.horn.od_mm / 2 - 1.0, P.horn.od_mm / 2 + 3.0
    assert solid_at(part, inside * math.cos(a), inside * math.sin(a), 0.5)
    assert not solid_at(part, outside * math.cos(a), outside * math.sin(a), 0.5)
    assert solid_at(part, outside * math.cos(a), outside * math.sin(a), d.relief_mm + 0.5)


def test_counterbores_are_on_the_outboard_face(coupon):
    r = P.horn.bolt_circle_mm / 2 + D.counterbore_diameter_mm / 2 - 0.3
    assert not solid_at(coupon, r, 0, D.web_mm - 0.2)
    assert solid_at(coupon, r, 0, 0.5)


def test_full_hub_is_an_open_cup_with_flanges(hub):
    w = P.wheel
    x, _, z = size(hub)
    assert x == pytest.approx(w.rim_od_mm + 2 * w.flange_mm, abs=0.01)
    assert z == pytest.approx(w.width_mm, abs=0.01)
    rim_mid = w.rim_od_mm / 2 - w.rim_wall_mm / 2
    assert solid_at(hub, rim_mid, 0, w.width_mm / 2)
    assert not solid_at(hub, w.rim_od_mm / 2 - w.rim_wall_mm - 1, 0, w.width_mm / 2)
    # Tire seat between the flanges is the bare rim.
    assert not solid_at(hub, w.rim_od_mm / 2 + 0.5, 0, w.width_mm / 2)
    # Both flanges stand proud of the rim.
    assert solid_at(hub, w.rim_od_mm / 2 + w.flange_mm - 0.3, 0, 0.5)
    assert solid_at(hub, w.rim_od_mm / 2 + w.flange_mm - 0.3, 0, w.width_mm - 0.5)


def test_full_hub_web_has_lightening_holes(hub):
    assert not solid_at(hub, D.lightening_radius_mm, 0, D.web_mm / 2)
    assert D.lightening_diameter_mm > 10
