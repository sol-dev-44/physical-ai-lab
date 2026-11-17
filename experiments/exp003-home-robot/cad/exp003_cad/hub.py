"""Wheel hub geometry. Dimensions come from params.derive; see params.py for the axis convention.

Both parts print servo side down on the bed with no supports: the horn recess and centre pocket
open onto the bed, the screw counterbores open upward, and the only overhangs are 45 degrees.
"""

from __future__ import annotations

import math

import cadquery as cq

from .params import HubParams, derive


def _ring(radius: float, count: int) -> list[tuple[float, float]]:
    """`count` points evenly round a circle, the first on the +x axis."""
    angles = (2 * math.pi * i / count for i in range(count))
    return [(radius * math.cos(a), radius * math.sin(a)) for a in angles]


def _horn_web(p: HubParams, od_mm: float) -> cq.Workplane:
    """A disc that bolts to the horn: recess, centre pocket, screw holes, counterbores."""
    d = derive(p)
    web = cq.Workplane("XY").circle(od_mm / 2).extrude(d.web_mm)
    web = web.cut(cq.Workplane("XY").circle(d.recess_diameter_mm / 2).extrude(d.recess_depth_mm))
    if d.center_pocket_depth_mm:
        pocket = cq.Workplane("XY").circle(d.center_pocket_diameter_mm / 2)
        web = web.cut(pocket.extrude(d.center_pocket_depth_mm))
    pts = _ring(p.horn.bolt_circle_mm / 2, p.horn.bolt_count)
    holes = cq.Workplane("XY").pushPoints(pts).circle(d.hole_diameter_mm / 2).extrude(d.web_mm)
    counterbores = (
        cq.Workplane("XY")
        .workplane(offset=d.web_mm - d.counterbore_depth_mm)
        .pushPoints(pts)
        .circle(d.counterbore_diameter_mm / 2)
        .extrude(d.counterbore_depth_mm)
    )
    return web.cut(holes).cut(counterbores)


def hub_coupon(p: HubParams) -> cq.Workplane:
    """The 20-minute test piece: just the horn interface, to check the fit before the full hub."""
    return _horn_web(p, derive(p).coupon_od_mm)


def _flange(r_rim: float, r_out: float, land: float, z_land: float, slope_up: bool) -> cq.Solid:
    """A tire flange: a full-height land plus a 45-degree slope back down to the rim."""
    rise = r_out - r_rim
    land_ring = cq.Solid.makeCylinder(r_out, land, cq.Vector(0, 0, z_land))
    if slope_up:  # slope above the land, narrowing upward
        cone = cq.Solid.makeCone(r_out, r_rim, rise, cq.Vector(0, 0, z_land + land))
    else:  # slope below the land, widening upward, so it prints as a 45-degree overhang
        cone = cq.Solid.makeCone(r_rim, r_out, rise, cq.Vector(0, 0, z_land - rise))
    return land_ring.fuse(cone)


def full_hub(p: HubParams) -> cq.Workplane:
    """The wheel: horn web on the servo side, an open rim, a tire flange at each edge."""
    d, w = derive(p), p.wheel
    r_rim = w.rim_od_mm / 2
    r_in = r_rim - w.rim_wall_mm
    r_out = r_rim + w.flange_mm

    rim = cq.Workplane("XY").circle(r_rim).circle(r_in).extrude(w.width_mm)
    inboard = _flange(r_rim, r_out, w.flange_land_mm, 0.0, slope_up=True)
    outboard = _flange(r_rim, r_out, w.flange_land_mm, w.width_mm - w.flange_land_mm, False)
    bore = cq.Solid.makeCylinder(r_in, w.width_mm)
    flanges = cq.Workplane("XY").add(inboard.fuse(outboard).cut(bore))

    web = _horn_web(p, 2 * r_in + 0.01)
    lightening = (
        cq.Workplane("XY")
        .pushPoints(_ring(d.lightening_radius_mm, w.lightening_holes))
        .circle(d.lightening_diameter_mm / 2)
        .extrude(d.web_mm)
    )
    web = web.cut(lightening)
    return rim.union(flanges).union(web).clean()
