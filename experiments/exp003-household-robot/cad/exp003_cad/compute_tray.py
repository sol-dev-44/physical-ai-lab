"""The compute tray (left of the deck): the Pi 5 on four M2.5 bosses and the UCTRONICS 5 V buck in
an open-ended channel behind it. Frame: the base plate's (params.derive_deck).

Print orientation: as modelled, floor on the bed. The bosses and channel walls rise straight up;
the nut pockets open onto the bed (their roofs bridge 5.4 mm, as on the coupon) and the zip-tie
grooves in the underside bridge 4.5 mm. No supports.

Fit: four M3 x 12 up through the plate and the floor, nuts on top, before the Pi goes on. A
hex nut in each boss's pocket from below (the plate then holds it), an 11 mm M-F standoff
screwed in from above, the Pi on top with M2.5 x 5. Slide the UCTRONICS into the channel, input
end inboard, and hold it with two zip ties through the floor slots.
"""

from __future__ import annotations

import cadquery as cq

from .deck_shapes import box, cut_ties, m3_holes, m25_boss, slab, union
from .params import DeckCoupon, DeckDerived


def compute_tray(d: DeckDerived) -> cq.Workplane:
    c, co, cc = d.compute, d.coupon, DeckCoupon()
    t = d.floor_mm
    part = union([slab(r, 0.0, t) for r in c.floor])
    part = part.union(union([box(w) for w in c.walls]))
    for w in c.windows:
        part = part.cut(slab(w, -1.0, t + 1.0))
    for x, y in c.bosses:
        part = m25_boss(
            part,
            x,
            y,
            cc.boss_mm,
            0.0,
            co.boss_height_mm,
            co.nut_pocket_af_mm,
            co.nut_pocket_depth_mm,
            co.stud_hole_mm,
        )
    part = cut_ties(part, c.ties, t)
    return m3_holes(part, c.holes, t)
