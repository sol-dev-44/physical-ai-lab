"""Tessera numbers. Plain Python (no CadQuery) so the root test suite can check them.

Frame: x across the bench (+ right), y depth (+ back), z up. A module's cells run from
(0, 0) to (nx * unit, ny * unit); its body sits gap_mm inside that on every side.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

Point = tuple[float, float]


@dataclass(frozen=True)
class Grid:
    unit_mm: float = 52.0  # smallest cup about 2 in square (owner, 2026-11-23)
    height_step_mm: float = 26.0
    gap_mm: float = 0.25  # each module stands this far inside its cells
    wall_mm: float = 2.0
    floor_mm: float = 2.0
    corner_r_mm: float = 1.5
    foot_chamfer_mm: float = 0.4  # bottom outer edge: hides elephant's foot


@dataclass(frozen=True)
class Joint:
    neck_mm: float = 9.0  # bowtie width on the line between two modules
    end_mm: float = 13.0  # bowtie width at each end
    depth_mm: float = 6.5  # socket depth into a module, from its outer face
    boss_skin_mm: float = 1.6  # plastic round a socket, inside the module
    key_clearance_mm: float = 0.10  # per side on a field key's flats (key R1, 2026-11-24)
    key_lead_mm: float = 0.6  # chamfer on the key's bottom edges
    # Crush ribs (2026-11-24): the flanks sit only 16.5 degrees off the pull direction, so
    # every 0.1 mm of side clearance lets a socket travel 0.35 mm. All three plain test keys
    # (0.10 to 0.20) had play. A ribbed key keeps 0.10 clearance so it starts in easily, and
    # one vertical rib per flank stands rib_interference_mm past the socket wall and crushes.
    rib_radius_mm: float = 1.0
    rib_interference_mm: float = 0.10  # per flank, past the socket wall: key R1 (owner, 2026-11-24)
    rib_start_mm: float = 2.5  # ribs begin above the lead chamfer, rounded, so they ease in


@dataclass(frozen=True)
class Engraving:
    depth_mm: float = 0.6
    label_mm: float = 6.5  # letter height on a front face
    base_mm: float = 5.0  # letter height under a module
    key_mm: float = 4.0  # digits on a test key's top


@dataclass(frozen=True)
class Socket:
    """One socket: the point on the module's outer face, and the outward normal."""

    at: Point
    normal: Point


def half_width(j: Joint, g: Grid, u: float) -> float:
    """Half the bowtie's width at distance u from the joint line (0 <= u <= g.gap + j.depth)."""
    reach = g.gap_mm + j.depth_mm
    return (j.neck_mm + (j.end_mm - j.neck_mm) * abs(u) / reach) / 2


def bowtie(j: Joint, g: Grid, clearance: float = 0.0) -> list[Point]:
    """The key's outline centred on the origin, the joint line along y (u = x).

    clearance is the gap per side, square to every face: 0 gives the socket shape (both
    halves), a key uses j.key_clearance_mm.
    """
    reach = g.gap_mm + j.depth_mm
    slope = (j.end_mm - j.neck_mm) / 2 / reach
    neck = j.neck_mm / 2 - clearance * math.hypot(1.0, slope)
    r = reach - clearance
    end = neck + slope * r
    return [(-r, -end), (0.0, -neck), (r, -end), (r, end), (0.0, neck), (-r, end)]


def flank_play(j: Joint, g: Grid, clearance: float) -> float:
    """How far two keyed modules can move apart and together with a plain key, in mm."""
    slope = (j.end_mm - j.neck_mm) / 2 / (g.gap_mm + j.depth_mm)
    sin_flank = slope / math.hypot(1.0, slope)
    return 2 * clearance / sin_flank + 2 * clearance  # both sockets' flanks, then both ends


def ribs(j: Joint, g: Grid, interference: float | None = None) -> list[Point]:
    """Centres (plan view) of a key's four crush ribs, radius j.rib_radius_mm.

    One rib per flank, midway along the part of the flank inside the socket, its crest
    interference beyond the socket wall (clearance 0) along the flank's outward normal.
    """
    i = j.rib_interference_mm if interference is None else interference
    rho = j.rib_radius_mm
    reach = g.gap_mm + j.depth_mm
    slope = (j.end_mm - j.neck_mm) / 2 / reach
    norm = math.hypot(1.0, slope)
    u = (g.gap_mm + reach) / 2
    w = half_width(j, g, u)
    out: list[Point] = []
    for sx in (1.0, -1.0):
        for sy in (1.0, -1.0):
            nx, ny = -sx * slope / norm, sy / norm  # outward normal of that flank
            out.append((sx * u + nx * (i - rho), sy * w + ny * (i - rho)))
    return out


def module_height(g: Grid, steps: int) -> float:
    if not 1 <= steps <= 5:
        raise ValueError("modules are 1 to 5 height steps (26 to 130 mm)")
    return steps * g.height_step_mm


def body(g: Grid, nx: int, ny: int) -> tuple[float, float, float, float]:
    """The module's outer box in plan: (x0, x1, y0, y1)."""
    if nx < 1 or ny < 1:
        raise ValueError("a module covers at least one cell")
    u, s = g.unit_mm, g.gap_mm
    return (s, nx * u - s, s, ny * u - s)


def sockets(g: Grid, nx: int, ny: int) -> list[Socket]:
    """One socket at the middle of every cell edge on the module's outside."""
    x0, x1, y0, y1 = body(g, nx, ny)
    u = g.unit_mm
    out: list[Socket] = []
    for i in range(nx):
        cx = (i + 0.5) * u
        out.append(Socket((cx, y0), (0.0, -1.0)))
        out.append(Socket((cx, y1), (0.0, 1.0)))
    for k in range(ny):
        cy = (k + 0.5) * u
        out.append(Socket((x0, cy), (-1.0, 0.0)))
        out.append(Socket((x1, cy), (1.0, 0.0)))
    return out


def boss_size(g: Grid, j: Joint) -> tuple[float, float]:
    """(width along the wall, depth in from the outer face) of the wall boss behind a socket."""
    width = 2 * half_width(j, g, g.gap_mm + j.depth_mm) + 2 * j.boss_skin_mm
    return (width, j.depth_mm + j.boss_skin_mm)


def boss_intrusion(g: Grid, j: Joint) -> float:
    """How far a boss stands into the cavity past the plain wall."""
    return boss_size(g, j)[1] - g.wall_mm


def cavity(g: Grid, nx: int, ny: int) -> tuple[float, float, float, float]:
    x0, x1, y0, y1 = body(g, nx, ny)
    w = g.wall_mm
    return (x0 + w, x1 - w, y0 + w, y1 - w)


@dataclass(frozen=True)
class Cup:
    """A plain open module: the first piece is two 1 x 1 cups."""

    nx: int = 1
    ny: int = 1
    steps: int = 2
    label: str = ""
    serial: int = 1


GRID, JOINT, ENGRAVING = Grid(), Joint(), Engraving()  # the defaults the solids use

FIRST_PIECE_CUPS = (Cup(label="TIPS", serial=1), Cup(label="SPARE", serial=2))
TEST_KEY_CLEARANCES = (0.10, 0.15, 0.20)  # test plate 1 (2026-11-23): all three had play
TEST_PLATE_2_PLAIN = 0.05  # plain key, clearance 0.05: the tightest plain fit worth trying
TEST_PLATE_2_RIBS = (0.10, 0.20)  # ribbed keys R1 and R2: rib interference per flank

PARTS_TRAY = Cup(nx=2, ny=1, steps=1, label="PARTS", serial=3)  # plate 3 (2026-11-24)
PLATE_3_KEYS = {52: 4, 26: 4}  # blue field keys by height (mm): count

ALCOHOL = Cup(nx=2, ny=2, steps=5, label="ALCOHOL", serial=4)  # 16 oz bottle, false floor
BIG = Cup(nx=2, ny=2, steps=5, label="BIG", serial=5)  # general bin (owner, 2026-11-25)

# Amazon Basics 99% isopropyl alcohol, 16 oz: listing 6.38 x 6.38 x 16.69 cm (w, d, h, mm)
ALCOHOL_BOTTLE_MM = (63.8, 63.8, 166.9)


@dataclass(frozen=True)
class FalseFloor:
    """ALCOHOL's false floor: a loose plate on a skirt that stands on the real floor.

    In use the skirt points down and the plate sits on top, so the stash is the space inside
    the skirt, stash_mm tall. It prints plate down, skirt up: no overhangs.
    """

    stash_mm: float = 10.0  # clear height of the hidden stash (USB stick, SD cards, cash)
    plate_mm: float = 2.4  # stiff enough under a full bottle (about 0.15 mm sag)
    skirt_mm: float = 2.0  # skirt wall thickness
    clearance_mm: float = 0.2  # per side in the cavity: docs/printing.md, slip fit
    # Lift notch: a half round in the front edge, between the two front bosses, where the front
    # wall hides it from the chair. Round it the plate overhangs lip_mm (a fingertip hooks
    # under), then a skirt ring closes the stash, so nothing shows or slips out of the notch.
    notch_r_mm: float = 10.0
    lip_mm: float = 4.0
    secret: str = "YOU FOUND IT"  # engraved on the stash's ceiling


FALSE_FLOOR = FalseFloor()


def false_floor_height(f: FalseFloor) -> float:
    return f.stash_mm + f.plate_mm


def notch_ring_r(f: FalseFloor) -> float:
    """Outer radius of the skirt ring round the lift notch (centred on the cavity's front wall)."""
    return f.notch_r_mm + f.lip_mm + f.skirt_mm


def false_floor_top(g: Grid, f: FalseFloor) -> float:
    """Height of the false floor's top face above the bench (what the bottle stands on)."""
    return g.floor_mm + false_floor_height(f)


def proud(g: Grid, c: Cup, standing_on: float, thing_mm: float) -> float:
    """How far a thing thing_mm tall, standing at height standing_on, rises above the cup."""
    return standing_on + thing_mm - module_height(g, c.steps)
