"""Small solids the electronics deck's parts share. Everything is in the base plate's frame
(params.derive_deck): x fore-aft, y across, z up from the base plate's top face."""

from __future__ import annotations

import math

import cadquery as cq

from .params import CLEARANCE_MM, Box, Rect, TiePoint


def slab(r: Rect, z0: float, z1: float) -> cq.Workplane:
    x0, x1, y0, y1 = r
    return cq.Workplane("XY").add(
        cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))
    )


def box(b: Box) -> cq.Workplane:
    return slab(b.plan(), b.z0, b.z1)


def cylinder(x: float, y: float, dia: float, z0: float, z1: float) -> cq.Workplane:
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(dia / 2).extrude(z1 - z0)


def hexagon(x: float, y: float, af: float, z0: float, z1: float) -> cq.Workplane:
    """A hex prism, flats facing +-y (as the coupon's nut pocket)."""
    r = af / math.sqrt(3)
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).polygon(6, 2 * r).extrude(z1 - z0)


def union(parts: list[cq.Workplane]) -> cq.Workplane:
    out = parts[0]
    for p in parts[1:]:
        out = out.union(p)
    return out


def m3_holes(part: cq.Workplane, holes, z1: float) -> cq.Workplane:
    for x, y in holes:
        part = part.cut(cylinder(x, y, CLEARANCE_MM["M3"], -1.0, z1 + 1.0))
    return part


def cut_ties(part: cq.Workplane, ties: tuple[TiePoint, ...], floor_mm: float) -> cq.Workplane:
    """Each tie's two slots through the floor and the groove under it joining them."""
    for tie in ties:
        for s in tie.slots:
            part = part.cut(slab(s, -1.0, floor_mm + 1.0))
        part = part.cut(slab(tie.groove, -1.0, tie.groove_mm))
    return part


def m25_boss(
    part: cq.Workplane,
    x: float,
    y: float,
    dia: float,
    z0: float,
    height: float,
    pocket_af: float,
    pocket_mm: float,
    stud_mm: float,
) -> cq.Workplane:
    """The coupon's M2.5 boss: a hex nut pocket from its bottom (z0) and the stud's hole above."""
    part = part.union(cylinder(x, y, dia, z0, z0 + height))
    part = part.cut(hexagon(x, y, pocket_af, z0 - 1.0, z0 + pocket_mm))
    return part.cut(cylinder(x, y, stud_mm, z0 - 1.0, z0 + height + 1.0))
