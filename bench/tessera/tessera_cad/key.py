"""The bowtie key that locks two Tessera modules together."""

from __future__ import annotations

import cadquery as cq

from tessera_cad.params import ENGRAVING, GRID, JOINT, Engraving, Grid, Joint, bowtie


def key(
    height: float,
    clearance: float | None = None,
    mark: str = "",
    g: Grid = GRID,
    j: Joint = JOINT,
    e: Engraving = ENGRAVING,
) -> cq.Workplane:
    """A key centred on the origin, its length along x (across the joint), standing on z = 0.

    mark is engraved on the top face (the test keys carry their clearance in hundredths).
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
    return part
