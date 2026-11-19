"""TPU tire geometry. Same axes as the hub: z is the wheel axis, z = 0 the servo-side face.

The tire is one ring that wraps the rim: its bore grips the bare seat between the flanges, and a
lip at each edge passes over a flange, so the flanges hold it from sliding off sideways. Prints
flat on either face with no supports: the only overhangs are the 45-degree faces that follow the
flange slopes, and the outer edge chamfers.
"""

from __future__ import annotations

import math

import cadquery as cq

from .params import HubParams, Tire, derive_tire


def profile(p: HubParams, t: Tire) -> list[tuple[float, float]]:
    """The tire's cross-section as (radius, z) points, round the ring once."""
    d, w = derive_tire(p, t), p.wheel
    width, land, ch = w.width_mm, w.flange_land_mm, t.edge_chamfer_mm
    r_out = d.rim_seat_od_mm / 2 + w.flange_mm  # flange land radius
    r_tread, r_bore, r_lip = t.od_mm / 2, d.bore_mm / 2, d.lip_bore_mm / 2
    # Each flange slope is the line r + z = r_out + land (mirrored at the far edge). The tire's
    # face follows it, moved out by the clearance.
    slope = r_out + land + t.clearance_mm * math.sqrt(2)
    z_lip, z_bore = slope - r_lip, slope - r_bore
    return [
        (r_lip, 0.0),
        (r_tread - ch, 0.0),
        (r_tread, ch),
        (r_tread, width - ch),
        (r_tread - ch, width),
        (r_lip, width),
        (r_lip, width - z_lip),
        (r_bore, width - z_bore),
        (r_bore, z_bore),
        (r_lip, z_lip),
    ]


def tire(p: HubParams, t: Tire | None = None) -> cq.Workplane:
    """The tire, in place on the hub (same axis, same z)."""
    pts = profile(p, t or Tire())
    # On the XZ workplane local (x, y) is global (x, z), so revolving about local y turns the
    # cross-section round the wheel axis.
    return cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))
