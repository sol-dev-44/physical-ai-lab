"""Measurements and derived numbers for the wheel hub, and the servo body for brackets.

Measurements come from a caliper and live in `servo.toml` (see MEASURING.md). Everything the
model needs is derived here and checked, so an impossible measurement fails loudly before any
geometry is built. Nothing here imports CadQuery, so these checks run in the lab's test suite.

Axis convention: z is the wheel axis, and z = 0 is the hub face that sits on the horn's top face.
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
# Air between the hub and the servo case. Generous because the loaded wheel tilts the hub a
# little, and because caliper and print errors each run to about 0.2 mm.
MIN_CASE_GAP_MM = 2.0
MAX_RELIEF_MM = 3.0  # most the hub's underside may step up, beyond the horn, to clear the case
MIN_POCKET_ROOF_MM = 0.8  # material between the centre pocket and the counterbore floors
SCREW_TIP_MARGIN_MM = 0.5  # a screw tip stops this far short of the servo case


@dataclass(frozen=True)
class Horn:
    """The round horn on the STS3215 output shaft, and the case round it, as measured."""

    od_mm: float
    thickness_mm: float
    bolt_count: int
    bolt_circle_mm: float
    bolt_size: str
    center_head_mm: float
    center_head_height_mm: float  # how far the centre screw head stands above the horn; 0 if flush
    shaft_height_mm: float  # horn top face down to the case right round the shaft
    # Horn top face down to the highest part of the case the hub sweeps over. On the STS3215 the
    # case is low round the shaft and a raised block (under the label) starts at the horn's edge.
    raised_case_mm: float


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
    pad_diameter_mm: float  # the part of the underside that sits on the horn's top face
    relief_mm: float  # how far the underside steps up beyond the pad; 0 when the case is low enough
    case_gap_mm: float  # air between the hub and the highest part of the case
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

    # The hub sits flat on the horn's top face (z = 0). It cannot wrap down round the horn: the
    # case's raised block starts right at the horn's edge, so everything outside the horn must
    # stay clear of it. Centring comes from the centre pocket and the screws.
    if h.shaft_height_mm < MIN_CASE_GAP_MM:
        raise ValueError(
            f"shaft_height {h.shaft_height_mm} mm leaves under {MIN_CASE_GAP_MM} mm between the "
            "hub and the servo case round the shaft; re-measure shaft_height"
        )
    if h.raised_case_mm > h.shaft_height_mm:
        raise ValueError(
            f"raised_case {h.raised_case_mm} mm is deeper than shaft_height "
            f"{h.shaft_height_mm} mm; raised_case is measured to the highest part of the case, "
            "so it can only be smaller"
        )
    relief = max(0.0, MIN_CASE_GAP_MM - h.raised_case_mm)
    if relief > MAX_RELIEF_MM:
        raise ValueError(
            f"raised_case {h.raised_case_mm} mm would need the hub to step up {relief:.1f} mm "
            "beyond the horn; re-measure raised_case, or the hub needs a spacer"
        )

    bolt_r = h.bolt_circle_mm / 2
    if bolt_r + hole / 2 >= h.od_mm / 2:
        raise ValueError("bolt holes fall outside the horn; re-measure bolt_circle and od")

    # The centre pocket locates the hub on the centre screw head, so it fits closely.
    pocket_d = h.center_head_mm + 2 * f.clearance_mm
    if pocket_d / 2 + 0.5 > bolt_r - hole / 2:
        raise ValueError("the centre screw pocket would cut into the bolt holes; re-measure")
    pocket_depth = h.center_head_height_mm + 0.5 if h.center_head_height_mm else 0.0

    cb_d = head_d + f.counterbore_extra_mm
    cb_depth = head_h + 0.3
    # A deep centre pocket must stop below the counterbore floors, or only a thin ring of
    # plastic separates them. A relief step must also leave material under the heads.
    above_pocket = pocket_depth + cb_depth + MIN_POCKET_ROOF_MM if pocket_depth else 0.0
    min_web = max(w.min_web_mm, relief + cb_depth + MIN_UNDER_HEAD_MM, above_pocket)

    # Pick the shortest screw on hand that grips the horn, thickening the web (the hub material
    # the screw passes before the horn) when a screw is long enough to reach the servo case.
    min_clamp = min_web - cb_depth
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
    web = clamp + cb_depth

    bolt_outer = bolt_r + cb_d / 2 + 3.0
    rim_inner = w.rim_od_mm / 2 - w.rim_wall_mm
    light_r = (bolt_outer + rim_inner) / 2
    chord = 2 * light_r * math.sin(math.pi / w.lightening_holes)
    light_d = min(rim_inner - bolt_outer - 8.0, chord - 8.0)

    return Derived(
        pad_diameter_mm=h.od_mm,
        relief_mm=relief,
        case_gap_mm=h.raised_case_mm + relief,
        center_pocket_diameter_mm=pocket_d,
        center_pocket_depth_mm=pocket_depth,
        hole_diameter_mm=hole,
        counterbore_diameter_mm=cb_d,
        counterbore_depth_mm=cb_depth,
        web_mm=web,
        coupon_od_mm=max(44.0, h.od_mm + 24.0),
        lightening_radius_mm=light_r,
        lightening_diameter_mm=light_d,
        screw_length_mm=length,
        screw=f"{h.bolt_size} x {length}",
    )


MAX_TIRE_STRETCH = 0.05  # most a TPU 95A tire should stretch to roll over a flange by hand
MIN_TIRE_OVER_FLANGE_MM = 3.0  # tread left above a flange, so the flange never touches the floor


@dataclass(frozen=True)
class Tire:
    """The TPU tire, printed flat. Design choices; refine after the first one is fitted."""

    od_mm: float = 120.0
    # How much smaller the bore is than the rim seat, on diameter: the stretch that grips the rim.
    # Printed bores come out a little small too, so start low.
    interference_mm: float = 1.0
    clearance_mm: float = 0.2  # per side, round the flanges, so the tire seats on the rim
    edge_chamfer_mm: float = 1.5  # 45-degree chamfer on both outer edges; prints without support
    # The printed rim's seat diameter, if measured with a caliper; the design value otherwise.
    rim_measured_od_mm: float | None = None


@dataclass(frozen=True)
class TireDerived:
    rim_seat_od_mm: float  # what the bore is sized against
    bore_mm: float  # inside diameter on the rim seat
    lip_bore_mm: float  # inside diameter of the lips that wrap over the flanges
    tread_mm: float  # rubber over the rim seat
    over_flange_mm: float  # rubber over the flanges
    grip_stretch: float  # how far the bore stretches on the seat, as a fraction
    mount_stretch: float  # how far the bore stretches to roll over a flange, as a fraction


def load_tire(path: Path) -> Tire:
    """The tire's design values, plus the printed rim's seat from `[tire]` in servo.toml if set."""
    raw = tomllib.loads(path.read_text()).get("tire", {})
    return Tire(rim_measured_od_mm=raw.get("rim_measured_od_mm"))


def derive_tire(p: HubParams, t: Tire) -> TireDerived:
    """Size the tire against the rim, or raise ValueError naming what does not work."""
    w = p.wheel
    seat = t.rim_measured_od_mm if t.rim_measured_od_mm is not None else w.rim_od_mm
    if abs(seat - w.rim_od_mm) > 1.0:
        raise ValueError(
            f"measured rim {seat} mm is over 1 mm from the design {w.rim_od_mm} mm; re-measure "
            "across the bare seat between the flanges"
        )
    if t.interference_mm < 0:
        raise ValueError("interference must be zero or more, or the tire spins on the rim")
    bore = seat - t.interference_mm
    flange_od = seat + 2 * w.flange_mm
    over_flange = (t.od_mm - flange_od) / 2 - t.clearance_mm
    if over_flange < MIN_TIRE_OVER_FLANGE_MM:
        raise ValueError(
            f"only {over_flange:.1f} mm of tire over the flanges; need "
            f"{MIN_TIRE_OVER_FLANGE_MM} mm, so raise the tire od or lower the flanges"
        )
    if t.edge_chamfer_mm >= over_flange:
        raise ValueError("the edge chamfer would cut through the lip over the flange")
    mount = flange_od / bore - 1
    if mount > MAX_TIRE_STRETCH:
        raise ValueError(
            f"the tire must stretch {mount:.1%} to pass a flange; TPU 95A manages about "
            f"{MAX_TIRE_STRETCH:.0%} by hand, so lower the flanges or the interference"
        )
    return TireDerived(
        rim_seat_od_mm=seat,
        bore_mm=bore,
        lip_bore_mm=flange_od + 2 * t.clearance_mm,
        tread_mm=(t.od_mm - bore) / 2,
        over_flange_mm=over_flange,
        grip_stretch=seat / bore - 1,
        mount_stretch=mount,
    )


@dataclass(frozen=True)
class Case:
    """The STS3215 body, for brackets and the base plate. Origin: the shaft axis.

    Case length and width and the top mounting-hole spacing are caliper readings (2026-11-19);
    the rest is read from the vendored STEP model (cad/vendor) and noted as such in servo.toml.
    """

    length_mm: float  # 1: along the case, shaft end to far end
    width_mm: float  # 2: across the case
    shaft_to_near_end_mm: float  # shaft centre to the near end of the case
    holes_along_mm: float  # top mounting holes, centre to centre along the case
    holes_across_mm: float  # and across it
    holes_near_offset_mm: (
        float  # shaft centre to the nearer pair of mounting holes (top and bottom)
    )
    bottom_holes_along_mm: float  # bottom mounting holes, centre to centre along the case
    bottom_holes_across_mm: float  # and across it
    height_shaft_end_mm: float  # case top round the shaft to case bottom round the shaft
    height_far_end_mm: float  # the far end is taller: raised strips on top, a step underneath
    bottom_disc_od_mm: float  # the idler disc on the bottom, on the shaft axis
    bottom_disc_proud_mm: float  # how far it stands below the case bottom round the shaft


def load_case(path: Path) -> Case:
    """Read `[case]` from servo.toml, or raise ValueError naming what does not add up."""
    c = Case(**tomllib.loads(path.read_text())["case"])
    if c.width_mm >= c.length_mm:
        raise ValueError(f"case width {c.width_mm} mm is not less than length {c.length_mm} mm")
    if not 0 < c.shaft_to_near_end_mm < c.length_mm / 2:
        raise ValueError("shaft_to_near_end must put the shaft in the near half of the case")
    if c.holes_across_mm >= c.width_mm:
        raise ValueError("mounting holes across must fall inside the case width")
    far_hole = c.holes_near_offset_mm + c.holes_along_mm
    if far_hole >= c.length_mm - c.shaft_to_near_end_mm:
        raise ValueError("the far pair of mounting holes falls past the end of the case")
    if c.bottom_holes_across_mm >= c.width_mm:
        raise ValueError("bottom mounting holes across must fall inside the case width")
    if c.holes_near_offset_mm + c.bottom_holes_along_mm >= c.length_mm - c.shaft_to_near_end_mm:
        raise ValueError("the far pair of bottom mounting holes falls past the end of the case")
    if c.height_far_end_mm < c.height_shaft_end_mm:
        raise ValueError("height_far_end is measured over the raised strips, so it is the larger")
    if c.bottom_disc_od_mm > c.width_mm:
        raise ValueError("the bottom disc cannot be wider than the case")
    return c


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
