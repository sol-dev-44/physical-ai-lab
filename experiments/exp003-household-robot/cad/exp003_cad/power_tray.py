"""The power tray (right of the deck) with the switch panel built in: two slotted pads for the
DROK 12 V converter's ears, a pocket for the INA226, tie-down points for the two inline fuse
holders, and an upright panel at the back for the main rocker switch and the charge jack.
Frame: the base plate's (params.derive_deck).

Print orientation: as modelled, floor on the bed. The panel, its gussets, the pads and the pocket
walls rise straight up. Bridges only: the DROK pads' nut channels (5.9 mm) and the zip-tie
grooves (4.5 mm) in the underside, and the rocker cutout's top (13.4 mm); the charge jack's hole is
a teardrop, its point up, so its top is a 45 degree overhang. No supports.

Fit: four M3 x 12 up through the plate and the floor, nuts on top. Slide an M3 nut into each pad's
channel from its open end, set the DROK on the pads (leads inboard) and fix each ear with M3 x 8
from above through the slot. The INA226 drops into its pocket, terminals toward the DROK, and
takes two zip ties; each fuse holder takes two. The rocker snaps into its cutout from outside
(the panel's face toward the back of the robot), long side vertical; the charge jack goes in from
inside, collar and leads behind the panel, its nut on the outside.
"""

from __future__ import annotations

import math

import cadquery as cq

from .deck_shapes import box, cut_ties, m3_holes, slab, union
from .params import DeckDerived


def _gusset(g, panel_x1: float, floor_mm: float) -> cq.Workplane:
    """A triangle behind the panel: full height at the panel, down to the floor at its reach."""
    reach = g.x1 - g.x0
    return (
        cq.Workplane("XZ", origin=(0, g.y1, 0))  # XZ's normal is -y: extrudes from y1 to y0
        .polyline([(panel_x1, floor_mm), (panel_x1, g.z1), (panel_x1 + reach, floor_mm)])
        .close()
        .extrude(g.y1 - g.y0)
    )


def _teardrop(x0: float, x1: float, y: float, z: float, dia: float) -> cq.Workplane:
    r = dia / 2
    k = r / math.sqrt(2)
    tip = (
        cq.Workplane("YZ", origin=(x0, 0, 0))
        .polyline([(y - k, z + k), (y, z + r * math.sqrt(2)), (y + k, z + k), (y, z)])
        .close()
        .extrude(x1 - x0)
    )
    disc = cq.Workplane("YZ", origin=(x0, 0, 0)).center(y, z).circle(r).extrude(x1 - x0)
    return disc.union(tip)


def power_tray(d: DeckDerived) -> cq.Workplane:
    pt, t = d.power, d.floor_mm
    part = union([slab(r, 0.0, t) for r in pt.floor])
    part = part.union(union([slab(p.pad, 0.0, p.top_mm) for p in pt.pads]))
    part = part.union(union([box(w) for w in pt.pocket_walls]))
    part = part.union(box(pt.panel))
    for g in pt.gussets:
        part = part.union(_gusset(g, pt.panel.x1, t))
    for p in pt.pads:
        part = part.cut(slab(p.channel, -1.0, p.channel_mm))
        sx0, sx1, sy0, sy1 = p.slot
        slot = (
            cq.Workplane("XY")
            .workplane(offset=p.channel_mm - 0.5)
            .center((sx0 + sx1) / 2, (sy0 + sy1) / 2)
            .slot2D(sx1 - sx0, sy1 - sy0)
            .extrude(p.top_mm - p.channel_mm + 1.5)
        )
        part = part.cut(slot)
    y, z, across, tall = pt.rocker_cutout
    px0, px1 = pt.panel.x0, pt.panel.x1
    part = part.cut(
        slab((px0 - 1.0, px1 + 1.0, y - across / 2, y + across / 2), z - tall / 2, z + tall / 2)
    )
    jy, jz, jd = pt.jack_hole
    part = part.cut(_teardrop(px0 - 1.0, px1 + 1.0, jy, jz, jd))
    part = cut_ties(part, pt.ties, t)
    return m3_holes(part, pt.holes, t)
