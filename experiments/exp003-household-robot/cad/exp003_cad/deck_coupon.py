"""The electronics deck's fit coupon. Frame and features: see params.DeckCoupon.

Prints flat as modelled: the panel on the bed, the boss and channel walls rising from it, the
nut pocket opening on the bed side (its roof bridges 5.4 mm, fine for PETG). No supports.
"""

from __future__ import annotations

import math

import cadquery as cq

from .params import DeckCoupon, derive_deck_coupon


def deck_coupon(c: DeckCoupon | None = None) -> cq.Workplane:
    c = c or DeckCoupon()
    d = derive_deck_coupon(c)
    w = c.width_mm
    part = cq.Workplane("XY").box(c.length_mm, w, c.panel_mm, centered=(False, False, False))
    part = part.edges("|Z").fillet(3.0)

    bx, by = d.boss_xy
    boss = cq.Workplane("XY").center(bx, by).circle(c.boss_mm / 2).extrude(d.boss_height_mm)
    x0, x1 = d.channel_x_mm
    wall_y = (w - d.channel_inner_mm) / 2 - c.channel_wall_mm
    walls = (
        cq.Workplane("XY")
        .pushPoints(
            [
                ((x0 + x1) / 2, wall_y + c.channel_wall_mm / 2),
                ((x0 + x1) / 2, w - wall_y - c.channel_wall_mm / 2),
            ]
        )
        .rect(x1 - x0, c.channel_wall_mm)
        .extrude(c.panel_mm + c.channel_height_mm)
    )
    part = part.union(boss).union(walls)

    for x, y, long, short in d.rockers:
        part = part.cut(cq.Workplane("XY").center(x, y).rect(long, short).extrude(c.panel_mm + 1))
    for x, y, dia in d.jacks:
        part = part.cut(cq.Workplane("XY").center(x, y).circle(dia / 2).extrude(c.panel_mm + 1))
    # Hex pocket from the bed side, flats facing +-y; the stud's clearance hole above it.
    r = d.nut_pocket_af_mm / math.sqrt(3)  # circumradius of the hexagon
    part = part.cut(
        cq.Workplane("XY").center(bx, by).polygon(6, 2 * r).extrude(d.nut_pocket_depth_mm)
    )
    part = part.cut(
        cq.Workplane("XY").center(bx, by).circle(d.stud_hole_mm / 2).extrude(d.boss_height_mm + 1)
    )
    return part
