"""The cradle against the vendored servo model. Skipped unless CadQuery is installed."""

from pathlib import Path

import pytest

cq = pytest.importorskip("cadquery")

from exp003_cad.cradle import cradle, servo_in_cradle  # noqa: E402
from exp003_cad.params import Cradle, derive_cradle, load, load_case  # noqa: E402

CAD = Path(__file__).resolve().parents[1]
CASE = load_case(CAD / "servo.toml")
HORN = load(CAD / "servo.toml").horn
D = derive_cradle(CASE, HORN, Cradle())


@pytest.fixture(scope="module")
def part():
    return cradle(CASE, HORN)


@pytest.fixture(scope="module")
def servo():
    return servo_in_cradle(str(CAD / "vendor" / "STS3215_03a.step"))


def solid(shape, a, b, c):
    return shape.val().isInside(cq.Vector(a, b, c))


def test_servo_model_lands_where_the_frame_says(servo):
    bb = servo.val().BoundingBox()
    assert (bb.xmin, bb.xmax) == (pytest.approx(-10.2), pytest.approx(35.2))
    assert (bb.ymin, bb.ymax) == (pytest.approx(-12.4), pytest.approx(12.4))
    # Lowest point: the connector pins, 3.5 mm past the step face.
    assert bb.zmin == pytest.approx(-3.5)
    assert solid(servo, 20.0, 0.0, 0.5)  # case body just above the step face
    for a, b in D.holes:
        assert not solid(servo, a, b, 0.5)  # its bottom holes line up with ours


def clashes(servo_shape, dz=0.0, step=0.5):
    """Points where the servo (lowered dz mm into the cradle) would hit the back wall or pads.

    The cheeks sit outside the servo's width (checked below), so only the wall and pads can
    clash. OpenCascade's boolean intersect is not used: on this vendored model it silently
    returns nothing for overlaps deeper than about 0.3 mm. Sampling heights avoid the faces that
    touch by design (the pad tops at c = 0).
    """
    c = Cradle()
    w0, w1, half = D.window
    r2 = D.disc_opening_radius_mm**2
    pad_r2 = (c.pad_diameter_mm / 2) ** 2
    found = []
    for k in range(int((D.a_max_mm - D.a_min_mm) / step) + 1):
        a = D.a_min_mm + k * step
        for j in range(int(2 * D.b_inner_mm / step) + 1):
            b = -D.b_inner_mm + j * step
            opening = a * a + b * b < r2 or (w0 < a < w1 and abs(b) < half)
            on_pad = any((a - ha) ** 2 + (b - hb) ** 2 < pad_r2 for ha, hb in D.holes)
            for z in (-0.1, -0.4, -1.0, -2.0, -2.4):
                hit = on_pad if z > -c.pad_mm else not opening
                if hit and servo_shape.isInside(cq.Vector(a, b, z + dz)):
                    found.append((a, b, z))
    return found


def test_cradle_and_servo_do_not_collide(servo):
    model = servo.val()
    assert clashes(model) == []
    # Cheeks: the servo is narrower than the gap between them.
    bb = model.BoundingBox()
    assert max(-bb.ymin, bb.ymax) <= D.b_inner_mm - Cradle().side_clearance_mm + 1e-6


def test_the_clash_check_can_fail(servo):
    # Lower the servo 0.6 mm into the cradle: the check must see it hit the pads and wall.
    assert len(clashes(servo.val(), dz=0.6, step=1.0)) > 10


def test_servo_sits_on_the_pads(part):
    for a, b in D.holes:
        ring = a + 1.8  # on the pad, beside the screw hole
        assert solid(part, ring, b, -0.25)
        assert not solid(part, a, b, -1.0)  # screw hole through


def test_openings_for_the_disc_and_the_connectors(part):
    assert not solid(part, 0.0, 0.0, -1.5)
    assert not solid(part, 14.0, 9.0, -1.5)  # connector recess
    assert not solid(part, 25.0, 0.0, -1.5)  # pad
    # No thin strip of wall where the disc opening meets the window.
    for a in (10.6, 11.0, 11.1):
        assert not solid(part, a, 0.0, -1.5)
    # The throat stays clear of the near pads: wall remains between them.
    assert solid(part, 8.3, 10.25 - 2.15 - 0.5, -1.5)
    assert solid(part, 20.0, 11.5, -1.5)  # wall left beside the window


def test_cheeks_and_foot(part):
    bb = part.val().BoundingBox()
    assert bb.ymin == pytest.approx(-D.b_outer_mm)
    assert bb.zmax == pytest.approx(Cradle().cheek_height_mm)
    assert solid(part, 0.0, D.b_inner_mm + 1.0, 10.0)
    assert not solid(part, 0.0, D.b_inner_mm - 0.1, 10.0)
    # Ears with an M3 hole each.
    ear_c = (-2.5 + Cradle().cheek_height_mm) / 2
    for a in (D.a_min_mm - 5.0, D.a_max_mm + 5.0):
        assert not solid(part, a, -D.b_outer_mm + 1.0, ear_c)
        assert solid(part, a, -D.b_outer_mm + 1.0, ear_c + 3.0)
