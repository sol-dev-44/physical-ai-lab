"""TPU tire geometry. Same axes as the hub: z is the wheel axis, z = 0 the servo-side face.

The tire is one ring that wraps the rim: its bore grips the bare seat between the flanges, and a
lip at each edge passes over a flange, so the flanges hold it from sliding off sideways. Prints
flat on either face with no supports: the only overhangs are the 45-degree faces that follow the
flange slopes, and the outer edge chamfers.
"""

from __future__ import annotations

import cadquery as cq

from .params import HubParams, Tire, tire_profile


def tire(p: HubParams, t: Tire | None = None) -> cq.Workplane:
    """The tire, in place on the hub (same axis, same z)."""
    pts = tire_profile(p, t or Tire())
    # On the XZ workplane local (x, y) is global (x, z), so revolving about local y turns the
    # cross-section round the wheel axis.
    return cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))
