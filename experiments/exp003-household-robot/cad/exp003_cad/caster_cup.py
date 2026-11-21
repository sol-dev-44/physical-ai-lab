"""The caster cup: a light open cup the rear caster bolts up into. Frame: see params.CasterCup.

The cavity is a box for the caster's plate joined with a circle for the fork's sweep. Prints
roof-down with the open end up: no overhangs, no supports. The caster's plate sits against the
roof's inner face; M4 screws come up through the caster and the roof, nuts on top.
"""

from __future__ import annotations

import cadquery as cq

from .params import Caster, CasterCup, Heights, derive_caster_cup


def caster_cup(caster: Caster, heights: Heights, c: CasterCup | None = None) -> cq.Workplane:
    c = c or CasterCup()
    d = derive_caster_cup(caster, heights, c)
    (ix, iy), (ox, oy) = d.inner_mm, d.outer_mm
    outer = (
        cq.Workplane("XY")
        .rect(ox, oy)
        .extrude(d.height_mm)
        .edges("|Z")
        .fillet(c.inner_corner_mm + c.wall_mm)
        .union(cq.Workplane("XY").circle(d.outer_radius_mm).extrude(d.height_mm))
    )
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=c.roof_mm)
        .rect(ix, iy)
        .extrude(d.depth_mm + 1)
        .edges("|Z")
        .fillet(c.inner_corner_mm)
        .union(
            cq.Workplane("XY")
            .workplane(offset=c.roof_mm)
            .circle(d.sweep_radius_mm)
            .extrude(d.depth_mm + 1)
        )
    )
    holes = (
        cq.Workplane("XY")
        .pushPoints(list(d.holes))
        .circle(c.hole_mm / 2)
        .extrude(c.roof_mm + 1)
        .union(cq.Workplane("XY").circle(c.center_hole_mm / 2).extrude(c.roof_mm + 1))
    )
    return outer.cut(cavity).cut(holes)
