"""Wheel module v2: both servo boxes and the axle beam in one piece. Frame: see params.WheelModule.

Built in the base's frame (x forward, y left, z up from the plate's top face): the +y box, its
mirror, and the beam between them. Prints standing on the beam's front face (x = beam front
down), so every hole across the print direction is a teardrop pointing up the print (-x).
"""

from __future__ import annotations

import math

import cadquery as cq

from .params import (
    CLEARANCE_MM,
    PLATE_MM,
    BaseLayout,
    Case,
    Cradle,
    Horn,
    WheelModule,
    cradle_to_plate,
    derive_cradle,
    derive_wheel_module,
)

BIG = 400.0


def _box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Solid:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def _teardrop(r: float, length: float, at: cq.Vector, axis: str) -> cq.Solid:
    """A hole of radius r along y or z, with a 45-degree point towards -x (up the print)."""
    tip = r * math.sqrt(2)
    t = r / math.sqrt(2)
    if axis == "z":
        wp = cq.Workplane("XY", origin=(at.x, at.y, at.z))
        pts = [(-tip, 0.0), (-t, t), (-t, -t)]
    else:  # along y: sketch in XZ, whose normal is -y, so extrude negative
        wp = cq.Workplane("XZ", origin=(at.x, at.y, at.z))
        pts = [(-tip, 0.0), (-t, t), (-t, -t)]
    circle = wp.circle(r).extrude(length if axis == "z" else -length).val()
    point = wp.polyline(pts).close().extrude(length if axis == "z" else -length).val()
    return circle.fuse(point)


def _gusset(x0: float, x1: float, pts: list[tuple[float, float]]) -> cq.Solid:
    """A plate in the y-z plane, from x0 to x1, with outline pts as (y, z)."""
    wp = cq.Workplane("YZ", origin=(x0, 0, 0))
    return wp.polyline(pts).close().extrude(x1 - x0).val()


def _half(case: Case, horn: Horn, cradle: Cradle, layout: BaseLayout, m: WheelModule) -> cq.Solid:
    d = derive_wheel_module(case, horn, cradle, layout, m)
    fx0, fx1, fy0, fy1 = d.foot
    (rx0, rx1), (nx0, nx1) = d.end_walls_x
    by0, by1 = d.back_wall_y_mm
    top, out = d.top_z_mm, d.outer_y_mm

    body = _box(fx0, fx1, fy0, fy1, 0.0, m.foot_mm)
    body = body.fuse(_box(rx0, nx1, by0, out, 0.0, top))
    # The front end wall carries on inboard as a gusset (the beam is under it in the print). The
    # rear brace is a fin along x, so it prints without support; the cables pass inboard of it.
    full = [(fy0, 0.0), (by0, 0.0), (by0, top), (fy0, m.foot_mm)]
    body = body.fuse(_gusset(nx0, nx1, full))
    # Rear fin: a block from the foot to the top, against the back wall. Its front end tapers at
    # 45 degrees (in plan), so in the print each layer reaches one step further off the wall.
    fin_x0, fin_x1, fin_y = d.rear_fin
    fin = _box(fin_x0, fin_x1, fin_y, by0 + 0.01, 0.0, top)
    reach = by0 - fin_y
    taper = (
        cq.Workplane("XY", origin=(0, 0, -1))
        .polyline([(fin_x1, fin_y), (fin_x1 + 0.01, by0), (fin_x1 - reach, fin_y)])
        .close()
        .extrude(top + 2)
        .val()
    )
    body = body.fuse(fin.cut(taper))

    cx0, cx1, cz0, cz1, cy0 = d.cavity
    body = body.cut(_box(cx0, cx1, cy0, BIG, cz0, cz1))
    for x, z in d.m2_holes:  # pads the servo's step face sits on
        pad = cq.Solid.makeCylinder(
            cradle.pad_diameter_mm / 2, cradle.pad_mm, cq.Vector(x, cy0, z), cq.Vector(0, 1, 0)
        )
        body = body.fuse(pad)

    # Back wall: the idler disc, the connector window, and the throat joining them.
    dx, dz, dr = d.disc_opening
    cut = cq.Solid.makeCylinder(dr, d.step_y_mm - by0, cq.Vector(dx, by0, dz), cq.Vector(0, 1, 0))
    wx0, wx1, wz0, wz1 = d.window
    cut = cut.fuse(_box(wx0, wx1, by0, d.step_y_mm, wz0, wz1))
    tx0, tx1, tz0, tz1 = d.throat
    cut = cut.fuse(_box(tx0, tx1, by0, d.step_y_mm, tz0, tz1))
    # Driver grooves through the foot, so a screwdriver reaches the lower M2 screws.
    gw, gz = m.driver_groove_mm
    for gx in d.driver_grooves_x:
        cut = cut.fuse(_box(gx - gw / 2, gx + gw / 2, fy0 - 1, by0, gz, m.foot_mm + 1))
    body = body.cut(cut)

    r2 = CLEARANCE_MM["M2"] / 2
    cb0, cb1 = d.counterbore_y_mm
    for x, z in d.m2_holes:
        body = body.cut(_teardrop(r2, d.step_y_mm - cb0 + 0.01, cq.Vector(x, cb0, z), "y"))
        body = body.cut(
            _teardrop(m.counterbore_mm / 2, cb1 - cb0, cq.Vector(x, cb0 - 0.01, z), "y")
        )
    r3 = CLEARANCE_MM["M3"] / 2
    for x, y in m.foot_bolts:
        body = body.cut(_teardrop(r3, m.foot_mm + 0.02, cq.Vector(x, y, -0.01), "z"))
    return body


def wheel_module(
    case: Case,
    horn: Horn,
    cradle: Cradle | None = None,
    layout: BaseLayout | None = None,
    m: WheelModule | None = None,
) -> cq.Workplane:
    cradle, layout, m = cradle or Cradle(), layout or BaseLayout(), m or WheelModule()
    d = derive_wheel_module(case, horn, cradle, layout, m)
    half = _half(case, horn, cradle, layout, m)
    other = half.mirror("XZ")
    bx0, bx1 = m.beam_x_mm
    beam = _box(bx0, bx1, -d.outer_y_mm, d.outer_y_mm, 0.0, d.top_z_mm)
    r3 = CLEARANCE_MM["M3"] / 2
    for x, y in d.beam_holes:
        beam = beam.cut(_teardrop(r3, m.beam_bolt_floor_mm + 0.02, cq.Vector(x, y, -0.01), "z"))
        beam = beam.cut(
            _teardrop(
                m.beam_counterbore_mm / 2,
                d.top_z_mm - m.beam_bolt_floor_mm + 0.01,
                cq.Vector(x, y, m.beam_bolt_floor_mm),
                "z",
            )
        )
    body = half.fuse(other).fuse(beam).clean()
    return cq.Workplane("XY").add(body)


def wheel_module_for_print(case: Case, horn: Horn) -> cq.Workplane:
    """Standing on the beam's front face: x up the print becomes z, the beam front on z = 0."""
    part = wheel_module(case, horn).val()
    part = part.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 90)  # +x -> -z: front face down
    bb = part.BoundingBox()
    return cq.Workplane("XY").add(part.translate(cq.Vector(0, 0, -bb.zmin)))


def servo_in_module(step_path: str, case: Case, horn: Horn, side: int = 1) -> cq.Workplane:
    """The vendored servo placed where the module holds it (+y side, or -y turned about its shaft).

    Uses the cradle's placement (the servo has not moved), shifted down to the plate's top face.
    """
    from .cradle import servo_in_cradle

    servo = servo_in_cradle(step_path).val()
    _, shift = cradle_to_plate(case, horn, Cradle(), BaseLayout(), 1)
    # (a, b, c) -> (-a, c, b): a quarter turn about x, then half a turn about z.
    o = cq.Vector(0, 0, 0)
    servo = servo.rotate(o, cq.Vector(1, 0, 0), 90).rotate(o, cq.Vector(0, 0, 1), 180)
    servo = servo.translate(cq.Vector(shift[0], shift[1], shift[2] - PLATE_MM))
    if side < 0:  # half a turn about z, then half a turn about its own shaft: far end back
        axis_z = derive_cradle(case, horn, Cradle()).axle_above_foot_mm
        servo = servo.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180)
        servo = servo.rotate(cq.Vector(0, 0, axis_z), cq.Vector(0, 1, axis_z), 180)
    return cq.Workplane("XY").add(servo)


COUPON_Y_MM = (81.0, 109.5)  # inboard foot edge to 11 mm into the box: back wall and 3 bolts


def wheel_module_coupon(case: Case, horn: Horn) -> cq.Workplane:
    """A 30-minute slice of the +y box, printed the same way as the module (front face down).

    It has the real back wall (counterbores, pads, disc opening, connector window), 11 mm of all
    four walls round the case, the front gusset and the rear fin, the driver grooves, and three
    foot bolt holes. Push a servo's step face in, drive the four M2 x 6, and bolt it to plate v1's
    spare (or anything 4 mm) with M3 x 12: that checks the case fit, the screw bite, and the
    teardrop holes.
    """
    d = derive_wheel_module(case, horn, Cradle(), BaseLayout())
    half = _half(case, horn, Cradle(), BaseLayout(), WheelModule())
    y0, y1 = COUPON_Y_MM
    keep = _box(d.foot[0] - 1, d.foot[1] + 1, y0 - 1, y1, -1, d.top_z_mm + 1)
    part = half.intersect(keep)
    part = part.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 90)  # front face down
    bb = part.BoundingBox()
    return cq.Workplane("XY").add(part.translate(cq.Vector(0, 0, -bb.zmin)))
