"""The bench layout: which module sits in which grid cells. Plain Python (tested, drawn).

Grid cells are (col, row): col 0 at the left, row 0 at the front (nearest the chair).
Left to right follows the job: heat at the left by the iron station, solder and flux in the
middle, cleaning at the right with the alcohol farthest from the heat. Tall at the back.

Tool sizes come from makers' and retailers' listings (2026-11-24); "check" marks a size no
listing gives, to confirm on arrival before that module is modelled.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Placement:
    name: str
    col: int
    row: int
    nx: int
    ny: int
    steps: int  # height in 26 mm steps
    holds: str
    material: str = "PLA"
    sized_from: str = ""
    status: str = "planned"  # planned, printed


FIELD_COLS, FIELD_ROWS = 9, 3  # 468 x 156 mm: about the soldering mat's 450 mm width

LAYOUT: tuple[Placement, ...] = (
    Placement(
        "HEAT GUN",
        0,
        1,
        2,
        2,
        4,
        "QWORK 300 W mini heat gun, nozzle up, stored cold (it has its own stand for use)",
        material="PETG",
        sized_from="similar 300 W minis about 225 x 45 mm; check the body on arrival",
    ),
    Placement(
        "SOLDER",
        2,
        1,
        2,
        2,
        2,
        "1/4 lb spool on a spindle, wire out of a front slot; 2 wick bobbins behind it",
        sized_from="listing 2.4 x 2.4 x 1.5 in (61 mm round, 38 wide); too big for 2 x 1",
    ),
    Placement(
        "FLUX",
        4,
        2,
        1,
        1,
        4,
        "10 mL flux syringe standing up, a few acid brushes (6 in, so they stand 48 mm proud)",
        sized_from="brushes 6 in overall; syringe length not published, check",
    ),
    Placement("TIPS", 4, 1, 1, 1, 2, "spare tips", status="printed"),
    Placement(
        "BIG",
        5,
        1,
        2,
        2,
        5,
        "general bin, 99.5 mm square inside and 128 mm deep (owner: at least 4 x 4 in, and deep)",
        sized_from="owner, 2026-11-25",
    ),
    Placement(
        "ALCOHOL",
        7,
        1,
        2,
        2,
        5,
        "16 oz isopropyl bottle (64 mm square, 167 mm tall); false floor with a stash",
        sized_from="listing 6.38 x 6.38 x 16.69 cm",
    ),
    Placement(
        "RACK",
        0,
        0,
        3,
        1,
        2,
        "crimper (9 in), stripper (8 in), 2 micro cutters (5 in), standing jaws down",
        sized_from="Klein 3005CR 9 x 3 in; IRWIN 8 in; Hakko CHP-170 about 5 in; slots on arrival",
    ),
    Placement(
        "GLASSES",
        3,
        0,
        3,
        1,
        1,
        "safety glasses, folded, lying flat",
        sized_from="no folded size published; 151 mm cavity, check on arrival",
    ),
    Placement("SPARE", 6, 0, 1, 1, 2, "odds and ends", status="printed"),
    Placement(
        "PARTS",
        7,
        0,
        2,
        1,
        1,
        "heat-shrink offcuts, screws, header pins; first check that the grid holds over 104 mm",
        sized_from="generic",
    ),
)

NOT_IN_THE_FIELD = (
    "Hakko 599B tip cleaner: 70 mm round, 71 mm tall, with its own weighted base; it sits "
    "beside the iron, so it needs no module.",
    "WEP 948DQ-III station and the silicone mat (450 x 300 mm): the field sits behind the mat.",
)


def cells(p: Placement) -> list[tuple[int, int]]:
    return [(p.col + i, p.row + k) for i in range(p.nx) for k in range(p.ny)]
