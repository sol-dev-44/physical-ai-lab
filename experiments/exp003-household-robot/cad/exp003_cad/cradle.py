"""Servo cradle geometry: the wheel servo bolts in from its bottom face. Frame: see params.Cradle.

Prints with the back wall on the bed (c = -wall - pad down), cheeks and ears rising from it, so
there are no overhangs; the only horizontal holes are the two M3 holes through the ears.
"""

from __future__ import annotations

import cadquery as cq

from .params import CLEARANCE_MM, Case, Cradle, Horn, derive_cradle


def _box(a0: float, a1: float, b0: float, b1: float, c0: float, c1: float) -> cq.Solid:
    return cq.Solid.makeBox(a1 - a0, b1 - b0, c1 - c0, cq.Vector(a0, b0, c0))


def cradle(case: Case, horn: Horn, c: Cradle | None = None) -> cq.Workplane:
    c = c or Cradle()
    d = derive_cradle(case, horn, c)
    a0, a1, bo = d.a_min_mm, d.a_max_mm, d.b_outer_mm
    back = -(c.wall_mm + c.pad_mm)
    wall_top = -c.pad_mm

    body = _box(a0, a1, -bo, bo, back, wall_top)
    for sign in (-1, 1):  # cheeks
        b_lo, b_hi = sorted((sign * d.b_inner_mm, sign * bo))
        body = body.fuse(_box(a0, a1, b_lo, b_hi, back, c.cheek_height_mm))
    for e0, e1 in ((a0 - c.ear_length_mm, a0), (a1, a1 + c.ear_length_mm)):  # ears on the foot
        body = body.fuse(_box(e0, e1, -bo, -bo + c.ear_mm, back, c.cheek_height_mm))

    # Openings in the wall: round the idler disc, and the window for connectors and pad.
    cut = cq.Solid.makeCylinder(d.disc_opening_radius_mm, -back, cq.Vector(0, 0, back))
    w0, w1, half = d.window
    cut = cut.fuse(_box(w0, w1, -half, half, back, wall_top))
    cut = cut.fuse(_box(0.0, w0, -d.throat_half_width_mm, d.throat_half_width_mm, back, wall_top))
    body = body.cut(cut)

    for a, b in d.holes:  # pads, then screw holes through pad and wall
        body = body.fuse(
            cq.Solid.makeCylinder(c.pad_diameter_mm / 2, c.pad_mm, cq.Vector(a, b, wall_top))
        )
    for a, b in d.holes:
        hole = cq.Solid.makeCylinder(d.hole_diameter_mm / 2, -back, cq.Vector(a, b, back))
        body = body.cut(hole)

    ear_c = (back + c.cheek_height_mm) / 2
    for a in (a0 - c.ear_length_mm / 2, a1 + c.ear_length_mm / 2):
        r = CLEARANCE_MM[c.ear_screw] / 2
        hole = cq.Solid.makeCylinder(r, c.ear_mm, cq.Vector(a, -bo, ear_c), cq.Vector(0, 1, 0))
        body = body.cut(hole)
    return cq.Workplane("XY").add(body.clean())


def servo_in_cradle(step_path: str) -> cq.Workplane:
    """The vendored STS3215 model moved into the cradle's frame, for checking the fit.

    The model has its shaft at x = 12.5 with the far end towards -x, and its bottom step face at
    z = -15.9. Turning it half a turn about z and shifting it puts the shaft on the origin, the
    far end towards +a, and the step face on c = 0.
    """
    model = cq.importers.importStep(step_path).val()
    model = model.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180)
    return cq.Workplane("XY").add(model.translate(cq.Vector(12.5, 0, 15.9)))
