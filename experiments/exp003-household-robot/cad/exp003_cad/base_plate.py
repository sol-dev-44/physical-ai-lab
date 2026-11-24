"""The base plate. Frame and features: see params.BasePlate and derive_base_plate.

Prints underside down: a flat 4 mm plate with low fences on top round the battery, so there are
no overhangs. Every hole is vertical.
"""

from __future__ import annotations

import cadquery as cq

from .params import CLEARANCE_MM, BasePlate, BasePlateDerived


def _box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Solid:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def _cavity(d: BasePlateDerived) -> cq.Workplane:
    """The hole the caster and its fork come up through: the caster cup's cavity, in place."""
    cx, cy = d.caster_xy
    ix, iy = d.cup.inner_mm
    t = d.thickness_mm
    rect = cq.Workplane("XY").center(cx, cy).rect(ix, iy).extrude(t + 2).translate((0, 0, -1))
    circle = (
        cq.Workplane("XY")
        .center(cx, cy)
        .circle(d.cup.sweep_radius_mm)
        .extrude(t + 2)
        .translate((0, 0, -1))
    )
    return rect.union(circle)


def base_plate(d: BasePlateDerived, p: BasePlate | None = None) -> cq.Workplane:
    p = p or BasePlate()
    t = d.thickness_mm
    length = d.x_front_mm - d.x_back_mm
    plate = (
        cq.Workplane("XY")
        .center((d.x_front_mm + d.x_back_mm) / 2, 0)
        .rect(length, 2 * d.half_width_mm)
        .extrude(t)
        .edges("|Z")
        .fillet(p.corner_radius_mm)
    )

    # Corner fences round the battery, on the top face.
    bx0, bx1, by0, by1 = d.battery_box
    f, leg, h = p.fence_mm, p.fence_leg_mm, p.fence_height_mm
    fences = []
    for x, sx in ((bx0, -1), (bx1, 1)):  # sx, sy point out of the battery box at this corner
        for y, sy in ((by0, -1), (by1, 1)):
            fx = sorted((x, x + sx * f))
            fy = sorted((y + sy * f, y - sy * leg))
            fences.append(_box(fx[0], fx[1], fy[0], fy[1], t, t + h))  # across the end face
            gx = sorted((x + sx * f, x - sx * leg))
            gy = sorted((y, y + sy * f))
            fences.append(_box(gx[0], gx[1], gy[0], gy[1], t, t + h))  # along the side face
    for fence in fences:
        plate = plate.union(cq.Workplane("XY").add(fence))

    r3 = CLEARANCE_MM["M3"] / 2
    m3 = [*d.wheel_holes, *d.cup_holes, *d.grid_holes, *d.front_holes]
    holes = cq.Workplane("XY").pushPoints(m3).circle(r3).extrude(t + 2).translate((0, 0, -1))
    cliffs = (
        cq.Workplane("XY")
        .pushPoints(list(d.cliff_windows))
        .circle(p.cliff_window_mm / 2)
        .extrude(t + 2)
        .translate((0, 0, -1))
    )
    plate = plate.cut(holes).cut(cliffs).cut(_cavity(d))
    for x0, x1, y0, y1 in d.strap_slots:
        plate = plate.cut(cq.Workplane("XY").add(_box(x0, x1, y0, y1, -1, t + 1)))
    return plate
