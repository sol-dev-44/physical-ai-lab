"""The bowtie key that locks two Tessera modules together."""

from __future__ import annotations

import cadquery as cq

from tessera_cad.params import ENGRAVING, GRID, JOINT, Engraving, Grid, Joint, bowtie, ribs


def key(
    height: float,
    clearance: float | None = None,
    mark: str = "",
    rib_interference: float | None = None,
    g: Grid = GRID,
    j: Joint = JOINT,
    e: Engraving = ENGRAVING,
) -> cq.Workplane:
    """A key centred on the origin, its length along x (across the joint), standing on z = 0.

    mark is engraved on the top face (the test keys carry their clearance in hundredths).
    rib_interference adds four crush ribs (see Joint): a ribbed key keeps the given clearance
    on its flats and grips on the ribs, so the joint has no play.
    """
    c = j.key_clearance_mm if clearance is None else clearance
    part = (
        cq.Workplane("XY")
        .polyline(bowtie(j, g, c))
        .close()
        .extrude(height)
        .faces("<Z")
        .edges()
        .chamfer(j.key_lead_mm)
    )
    if mark:
        part = (
            part.faces(">Z")
            .workplane(centerOption="CenterOfBoundBox")
            .text(mark, e.key_mm, -e.depth_mm, halign="center", valign="center", combine="cut")
        )
    if rib_interference is not None:
        z0, rho = j.rib_start_mm, j.rib_radius_mm
        for cx, cy in ribs(j, g, rib_interference):
            rod = cq.Workplane("XY").workplane(offset=z0).center(cx, cy).circle(rho)
            part = part.union(rod.extrude(height - z0))
            part = part.union(cq.Workplane("XY").sphere(rho).translate((cx, cy, z0)))
    return part
