"""A Tessera module: an open box on the grid, with a bowtie socket in every cell edge."""

from __future__ import annotations

import cadquery as cq

from tessera_cad.params import (
    ENGRAVING,
    GRID,
    JOINT,
    Cup,
    Engraving,
    Grid,
    Joint,
    Socket,
    body,
    boss_size,
    bowtie,
    cavity,
    half_width,
    module_height,
    sockets,
)


def _prism(points: list[tuple[float, float]], z0: float, z1: float) -> cq.Workplane:
    return cq.Workplane("XY").workplane(offset=z0).polyline(points).close().extrude(z1 - z0)


def _place(s: Socket, u: float, v: float, gap: float) -> tuple[float, float]:
    """Point u along the socket's outward normal (from the joint line) and v along the wall."""
    nx, ny = s.normal
    tx, ty = -ny, nx
    jx, jy = s.at[0] + nx * gap, s.at[1] + ny * gap  # the joint line, gap outside the face
    return (jx + nx * u + tx * v, jy + ny * u + ty * v)


def _boss(s: Socket, g: Grid, j: Joint, h: float) -> cq.Workplane:
    w, d = boss_size(g, j)
    nx, ny = s.normal
    tx, ty = -ny, nx
    ax, ay = s.at
    pts = [
        (ax + tx * w / 2, ay + ty * w / 2),
        (ax - tx * w / 2, ay - ty * w / 2),
        (ax - tx * w / 2 - nx * d, ay - ty * w / 2 - ny * d),
        (ax + tx * w / 2 - nx * d, ay + ty * w / 2 - ny * d),
    ]
    return _prism(pts, 0, h)


def _socket_cut(s: Socket, g: Grid, j: Joint, h: float) -> cq.Workplane:
    pts = [_place(s, u, v, g.gap_mm) for u, v in bowtie(j, g)]
    return _prism(pts, -1, h + 1)


def _fit_text(text: str, size: float, max_width: float) -> float:
    """Letter height so the text is at most max_width wide (never above size)."""
    probe = cq.Workplane("XY").text(text, size, 1.0, halign="center", valign="center")
    width = probe.val().BoundingBox().xlen
    return size if width <= max_width else size * max_width / width


def front_label_box(g: Grid, j: Joint, nx: int) -> tuple[float, float]:
    """(x centre, usable width) for the label on the front face, left of the first groove."""
    x0 = body(g, nx, 1)[0]
    groove = g.unit_mm / 2 - half_width(j, g, g.gap_mm)
    margin = 1.5
    return ((x0 + groove) / 2, groove - x0 - 2 * margin)


def cup(c: Cup, g: Grid = GRID, j: Joint = JOINT, e: Engraving = ENGRAVING) -> cq.Workplane:
    x0, x1, y0, y1 = body(g, c.nx, c.ny)
    h = module_height(g, c.steps)

    part = (
        cq.Workplane("XY")
        .box(x1 - x0, y1 - y0, h, centered=False)
        .translate((x0, y0, 0))
        .edges("|Z")
        .fillet(g.corner_r_mm)
        .faces("<Z")
        .edges()
        .chamfer(g.foot_chamfer_mm)
    )
    cx0, cx1, cy0, cy1 = cavity(g, c.nx, c.ny)
    pocket = (
        cq.Workplane("XY")
        .box(cx1 - cx0, cy1 - cy0, h, centered=False)
        .translate((cx0, cy0, g.floor_mm))
        .edges("|Z")
        .fillet(max(g.corner_r_mm - g.wall_mm / 2, 0.5))
    )
    part = part.cut(pocket)
    socks = sockets(g, c.nx, c.ny)
    for s in socks:
        part = part.union(_boss(s, g, j, h))
    for s in socks:
        part = part.cut(_socket_cut(s, g, j, h))

    if c.label:
        cx, width = front_label_box(g, j, c.nx)
        size = _fit_text(c.label, e.label_mm, width)
        front = cq.Plane(origin=(cx, y0, h / 2), xDir=(1, 0, 0), normal=(0, -1, 0))
        part = part.cut(
            cq.Workplane(front).text(c.label, size, -e.depth_mm, halign="center", valign="center")
        )

    # Underneath (reads right way round when the module is turned over): the easter egg.
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    under = cq.Plane(origin=(mx, my, 0), xDir=(1, 0, 0), normal=(0, 0, -1))
    for line, dy in (("TESSERA", e.base_mm * 0.75), (f"No. {c.serial:03d}", -e.base_mm * 0.75)):
        part = part.cut(
            cq.Workplane(under)
            .center(0, dy)
            .text(line, e.base_mm, -e.depth_mm, halign="center", valign="center")
        )
    return part
