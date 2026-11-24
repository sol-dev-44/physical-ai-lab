"""The servo board bridge (centre back of the deck): a platform over the caster cup on four posts,
carrying the Waveshare Bus Servo Adapter (A) on 20 mm standoffs. Frame: the base plate's
(params.derive_deck); `servo_bridge_for_print` turns it over for the printer.

Print orientation: upside down, the platform's top face on the bed. The coupon's M2.5 bosses hang
under the platform (so its top stays flat) and print standing up, their nut pockets opening
upward; the posts rise from the platform with their hex nut wells opening onto the bed, and each
well's floor (the nut seat) bridges 5.9 mm. No supports.

Fit: drop an M3 nut down each post's hex well onto its seat and drive M3 x 12 up through the plate
into it. A hex nut into each boss's pocket from below, a 20 mm M-F standoff screwed in from above,
the board on top with M2.5 x 5.
"""

from __future__ import annotations

import cadquery as cq

from .deck_shapes import cylinder, hexagon, m3_holes, m25_boss, slab, union
from .params import DeckCoupon, DeckDerived


def servo_bridge(d: DeckDerived) -> cq.Workplane:
    b, co, cc = d.bridge, d.coupon, DeckCoupon()
    under, top = b.platform_z_mm
    part = union([slab(r, under, top) for r in (b.platform, *b.arms)])
    part = part.union(union([cylinder(x, y, b.post_mm, 0.0, top) for x, y in b.posts]))
    part = part.cut(slab(b.window, under - 1.0, top + 1.0))
    for x, y in b.bosses:
        part = m25_boss(
            part,
            x,
            y,
            cc.boss_mm,
            b.boss_bottom_mm,
            top - b.boss_bottom_mm,
            co.nut_pocket_af_mm,
            co.nut_pocket_depth_mm,
            co.stud_hole_mm,
        )
    for x, y in b.posts:
        part = part.cut(hexagon(x, y, b.well_af_mm, b.nut_seat_mm, top + 1.0))
    return m3_holes(part, b.posts, top)


def servo_bridge_for_print(d: DeckDerived) -> cq.Workplane:
    """Turned over about x so the platform's top face is on the bed (z = 0)."""
    top = d.bridge.platform_z_mm[1]
    return servo_bridge(d).rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, top))
