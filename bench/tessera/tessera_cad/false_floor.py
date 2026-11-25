"""ALCOHOL's false floor: a loose plate on a skirt, with a hidden stash underneath.

The plate follows the cavity, notched round every socket boss, clearance_mm in from every
wall. A skirt round its edge stands it stash_mm above the real floor. A half-round notch in
the middle of the front edge takes a fingertip, which hooks under the lip round the notch to
lift the plate out. A skirt ring behind the lip keeps the stash closed.
"""

from __future__ import annotations

import cadquery as cq

from tessera_cad.params import (
    ENGRAVING,
    FALSE_FLOOR,
    GRID,
    JOINT,
    Cup,
    Engraving,
    FalseFloor,
    Grid,
    Joint,
    Socket,
    boss_size,
    cavity,
    false_floor_height,
    notch_ring_r,
    sockets,
)


def _boss_keepout(s: Socket, g: Grid, j: Joint, inset: float, z0: float, z1: float) -> cq.Workplane:
    """A socket's boss grown by inset on its three cavity faces, running out past the wall."""
    w, d = boss_size(g, j)
    nx, ny = s.normal
    tx, ty = -ny, nx
    ax, ay = s.at[0] + nx, s.at[1] + ny  # 1 mm outside the outer face, so the cut is clean
    half, deep = w / 2 + inset, d + inset + 1
    pts = [
        (ax + tx * half, ay + ty * half),
        (ax - tx * half, ay - ty * half),
        (ax - tx * half - nx * deep, ay - ty * half - ny * deep),
        (ax + tx * half - nx * deep, ay + ty * half - ny * deep),
    ]
    return cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)


def _outline(c: Cup, g: Grid, j: Joint, inset: float, z0: float, z1: float) -> cq.Workplane:
    """The cavity in plan, inset on every face (walls and bosses), as a prism z0 to z1."""
    cx0, cx1, cy0, cy1 = cavity(g, c.nx, c.ny)
    part = (
        cq.Workplane("XY")
        .box(cx1 - cx0 - 2 * inset, cy1 - cy0 - 2 * inset, z1 - z0, centered=False)
        .translate((cx0 + inset, cy0 + inset, z0))
        .edges("|Z")
        .fillet(1.0)  # the pocket's corners are 0.5: any radius over 0.5 - inset keeps the gap
    )
    for s in sockets(g, c.nx, c.ny):
        part = part.cut(_boss_keepout(s, g, j, inset, z0 - 1, z1 + 1))
    return part


def false_floor(
    c: Cup,
    f: FalseFloor = FALSE_FLOOR,
    g: Grid = GRID,
    j: Joint = JOINT,
    e: Engraving = ENGRAVING,
) -> cq.Workplane:
    """The insert where it sits in the cup: skirt on the real floor, plate on top."""
    z0 = g.floor_mm
    ceiling = z0 + f.stash_mm
    z1 = z0 + false_floor_height(f)
    cx0, cx1, cy0, cy1 = cavity(g, c.nx, c.ny)

    def round_notch(r: float, top: float) -> cq.Workplane:
        base = cq.Workplane("XY").workplane(offset=z0 - 1).center((cx0 + cx1) / 2, cy0)
        return base.circle(r).extrude(top - z0 + 1)

    stash = _outline(c, g, j, f.clearance_mm + f.skirt_mm, z0 - 1, ceiling)
    stash = stash.cut(round_notch(notch_ring_r(f), ceiling))  # the ring round the notch
    part = _outline(c, g, j, f.clearance_mm, z0, z1).cut(stash)
    part = part.cut(round_notch(f.notch_r_mm + f.lip_mm, ceiling))  # room to hook the lip
    part = part.cut(round_notch(f.notch_r_mm, z1 + 1))

    if not f.secret:
        return part
    # On the stash's ceiling, read with the plate turned over: the easter egg.
    under = cq.Plane(
        origin=((cx0 + cx1) / 2, (cy0 + cy1) / 2, ceiling), xDir=(1, 0, 0), normal=(0, 0, -1)
    )
    return part.cut(
        cq.Workplane(under).text(
            f.secret, e.label_mm, -e.depth_mm, halign="center", valign="center"
        )
    )


def false_floor_print(c: Cup, f: FalseFloor = FALSE_FLOOR, g: Grid = GRID) -> cq.Workplane:
    """The insert turned over to print: plate on the bed, skirt up, so nothing overhangs."""
    _, _, cy0, cy1 = cavity(g, c.nx, c.ny)
    cy = (cy0 + cy1) / 2  # turn it over about its own middle, so it stays over the cells
    part = false_floor(c, f, g).rotate((0, cy, 0), (1, cy, 0), 180)
    return part.translate((0, 0, -part.val().BoundingBox().zmin))
