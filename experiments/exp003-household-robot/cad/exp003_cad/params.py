"""Measurements and derived numbers for the wheel hub.

Measurements come from a caliper and live in `servo.toml` (see MEASURING.md). Everything the
model needs is derived here and checked, so an impossible measurement fails loudly before any
geometry is built. Nothing here imports CadQuery, so these checks run in the lab's test suite.

Axis convention: z is the wheel axis, and z = 0 is the hub face that sits against the servo.
"""

from __future__ import annotations

import math
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# Clearance hole for each thread (mm).
CLEARANCE_MM: dict[str, float] = {"M2": 2.4, "M2.5": 2.9, "M3": 3.4}
# Head diameter and height (mm) by head style: socket cap (ISO 4762), button head (ISO 7380).
HEADS: dict[str, dict[str, tuple[float, float]]] = {
    "socket": {"M2": (3.8, 2.0), "M2.5": (4.5, 2.5), "M3": (5.5, 3.0)},
    "button": {"M2": (3.5, 1.3), "M2.5": (4.7, 1.5), "M3": (5.7, 1.65)},
}

MIN_UNDER_HEAD_MM = 2.0  # hub material left between a screw head and the horn
MAX_EXTRA_WEB_MM = 6.0  # most the web may grow to suit a long screw
MIN_CASE_GAP_MM = 1.0  # air between the hub and the servo case
MIN_POCKET_ROOF_MM = 0.8  # material between the centre pocket and the counterbore floors
SCREW_TIP_MARGIN_MM = 0.5  # a screw tip stops this far short of the servo case


@dataclass(frozen=True)
class Horn:
    """The round horn on the STS3215 output shaft, as measured."""

    od_mm: float
    thickness_mm: float
    bolt_count: int
    bolt_circle_mm: float
    bolt_size: str
    center_head_mm: float
    center_head_height_mm: float  # how far the centre screw head stands above the horn; 0 if flush
    shaft_height_mm: float  # horn top face down to the servo case top


@dataclass(frozen=True)
class Wheel:
    """Design choices, not measurements. A 108 mm rim plus a 6 mm TPU tire makes a 120 mm wheel."""

    rim_od_mm: float = 108.0
    width_mm: float = 32.0
    rim_wall_mm: float = 3.0
    flange_mm: float = 1.5  # how far each tire flange stands above the rim
    flange_land_mm: float = 1.2  # straight part of each flange before the 45-degree slope
    min_web_mm: float = 6.0
    lightening_holes: int = 5


@dataclass(frozen=True)
class Fit:
    """Print tolerances for the H2D in PETG. Adjust after the coupon if fits are off."""

    clearance_mm: float = 0.2  # per side, for parts that slip together
    counterbore_extra_mm: float = 0.6  # on diameter, so a hex key fits beside the head


@dataclass(frozen=True)
class Screws:
    """The screws on hand for fixing the hub to the horn: head style and the lengths available."""

    head: str = "socket"
    lengths_mm: tuple[int, ...] = (3, 4, 5, 6, 8, 10, 12, 16)


@dataclass(frozen=True)
class HubParams:
    horn: Horn
    measured: bool
    wheel: Wheel = field(default_factory=Wheel)
    fit: Fit = field(default_factory=Fit)
    screws: Screws = field(default_factory=Screws)


@dataclass(frozen=True)
class Derived:
    recess_diameter_mm: float
    recess_depth_mm: float
    center_pocket_diameter_mm: float
    center_pocket_depth_mm: float  # 0 when the centre screw is flush
    hole_diameter_mm: float
    counterbore_diameter_mm: float
    counterbore_depth_mm: float
    web_mm: float
    coupon_od_mm: float
    lightening_radius_mm: float
    lightening_diameter_mm: float
    screw_length_mm: int
    screw: str


def derive(p: HubParams) -> Derived:
    """Turn measurements into model dimensions, or raise ValueError naming what is impossible."""
    h, w, f, s = p.horn, p.wheel, p.fit, p.screws
    if h.bolt_size not in CLEARANCE_MM:
        raise ValueError(f"bolt_size {h.bolt_size!r} must be one of {', '.join(CLEARANCE_MM)}")
    if s.head not in HEADS:
        raise ValueError(f"screw head {s.head!r} must be one of {', '.join(HEADS)}")
    if h.bolt_count < 2:
        raise ValueError(f"bolt_count is {h.bolt_count}; the hub needs at least 2 screws")
    if h.thickness_mm < 1.0:
        raise ValueError(f"horn thickness {h.thickness_mm} mm is too thin to locate the hub")
    hole = CLEARANCE_MM[h.bolt_size]
    head_d, head_h = HEADS[s.head][h.bolt_size]

    recess_depth = min(1.5, h.thickness_mm - 0.5)
    recess_d = h.od_mm + 2 * f.clearance_mm
    if h.shaft_height_mm - recess_depth < MIN_CASE_GAP_MM:
        raise ValueError(
            f"shaft_height {h.shaft_height_mm} mm leaves under {MIN_CASE_GAP_MM} mm between the "
            "hub and the servo case; re-measure shaft_height"
        )

    bolt_r = h.bolt_circle_mm / 2
    if bolt_r + hole / 2 >= h.od_mm / 2:
        raise ValueError("bolt holes fall outside the horn; re-measure bolt_circle and od")

    pocket_d = h.center_head_mm + 2 * 0.5
    if pocket_d / 2 + 0.5 > bolt_r - hole / 2:
        raise ValueError("the centre screw pocket would cut into the bolt holes; re-measure")
    pocket_depth = recess_depth + h.center_head_height_mm + 0.5 if h.center_head_height_mm else 0.0

    cb_d = head_d + f.counterbore_extra_mm
    cb_depth = head_h + 0.3
    # A deep centre pocket must stop below the counterbore floors, or only a thin ring of
    # plastic separates them.
    above_pocket = pocket_depth + cb_depth + MIN_POCKET_ROOF_MM if pocket_depth else 0.0
    min_web = max(w.min_web_mm, recess_depth + cb_depth + MIN_UNDER_HEAD_MM, above_pocket)

    # Pick the shortest screw on hand that grips the horn, thickening the web (the hub material
    # the screw passes before the horn) when a screw is long enough to reach the servo case.
    min_clamp = min_web - cb_depth - recess_depth
    engage = min(h.thickness_mm, 2.0)
    room_below = h.shaft_height_mm - SCREW_TIP_MARGIN_MM  # horn top face to where a tip stops
    choice = None
    for n in sorted(s.lengths_mm):
        clamp = max(min_clamp, n - room_below)
        if n - clamp >= engage and clamp - min_clamp <= MAX_EXTRA_WEB_MM:
            choice = (n, clamp)
            break
    if choice is None:
        raise ValueError(
            f"none of the {s.head}-head {h.bolt_size} screws on hand ({s.lengths_mm} mm) fit: "
            f"each needs {engage:.1f} mm of thread in the horn without reaching the case"
        )
    length, clamp = choice
    web = clamp + cb_depth + recess_depth

    bolt_outer = bolt_r + cb_d / 2 + 3.0
    rim_inner = w.rim_od_mm / 2 - w.rim_wall_mm
    light_r = (bolt_outer + rim_inner) / 2
    chord = 2 * light_r * math.sin(math.pi / w.lightening_holes)
    light_d = min(rim_inner - bolt_outer - 8.0, chord - 8.0)

    return Derived(
        recess_diameter_mm=recess_d,
        recess_depth_mm=recess_depth,
        center_pocket_diameter_mm=pocket_d,
        center_pocket_depth_mm=pocket_depth,
        hole_diameter_mm=hole,
        counterbore_diameter_mm=cb_d,
        counterbore_depth_mm=cb_depth,
        web_mm=web,
        coupon_od_mm=max(44.0, recess_d + 16.0),
        lightening_radius_mm=light_r,
        lightening_diameter_mm=light_d,
        screw_length_mm=length,
        screw=f"{h.bolt_size} x {length}",
    )


def load(path: Path) -> HubParams:
    data = tomllib.loads(path.read_text())
    screws = Screws()
    if "screws" in data:
        raw = data["screws"]
        screws = Screws(
            head=raw.get("head", screws.head),
            lengths_mm=tuple(raw.get("lengths_mm", screws.lengths_mm)),
        )
    return HubParams(horn=Horn(**data["horn"]), measured=bool(data["measured"]), screws=screws)
