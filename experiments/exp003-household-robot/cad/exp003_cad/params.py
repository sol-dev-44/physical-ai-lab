"""Measurements and derived numbers for the wheel hub, and the servo body for brackets.

Measurements come from a caliper and live in `servo.toml` (see MEASURING.md). Everything the
model needs is derived here and checked, so an impossible measurement fails loudly before any
geometry is built. Nothing here imports CadQuery, so these checks run in the lab's test suite.

Axis convention: z is the wheel axis, and z = 0 is the hub face that sits on the horn's top face.
"""

from __future__ import annotations

import itertools
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


def tire_profile(p: HubParams, t: Tire) -> list[tuple[float, float]]:
    """The tire's cross-section as (radius, z) points, round the ring once.

    Same axes as the hub: z is the wheel axis, z = 0 the servo-side face. Each flange slope is the
    line r + z = r_out + land (mirrored at the far edge); the tire's face follows it, moved out by
    the clearance.
    """
    d, w = derive_tire(p, t), p.wheel
    width, land, ch = w.width_mm, w.flange_land_mm, t.edge_chamfer_mm
    r_out = d.rim_seat_od_mm / 2 + w.flange_mm  # flange land radius
    r_tread, r_bore, r_lip = t.od_mm / 2, d.bore_mm / 2, d.lip_bore_mm / 2
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
    bottom_step_mm: float  # the bottom steps down this much, from bottom_step_from_mm along
    bottom_step_from_mm: float
    bottom_keepout_from_mm: float  # connector recess and pad on the bottom: keep clear
    bottom_keepout_to_mm: float
    bottom_keepout_half_width_mm: float
    bottom_keepout_proud_mm: float  # how far past the step face (the connector pins)
    mount_screw_length_mm: int  # the M2 self-tapping screws supplied with the servo
    max_screw_depth_mm: float  # deepest a mounting screw is known to go into the case


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
    if not c.bottom_step_from_mm < c.holes_near_offset_mm:
        raise ValueError("the bottom mounting holes must sit on the bottom step")
    if not c.bottom_keepout_from_mm < c.bottom_keepout_to_mm:
        raise ValueError("bottom_keepout_from must come before bottom_keepout_to")
    if not 0 < c.max_screw_depth_mm < c.mount_screw_length_mm:
        raise ValueError("max_screw_depth must be positive and shorter than the mounting screw")
    if c.bottom_disc_od_mm > c.width_mm:
        raise ValueError("the bottom disc cannot be wider than the case")
    return c


MIN_SELF_TAP_MM = 3.0  # least thread an M2 self-tapping screw should cut into the case
SCREW_HEAD_MM = 4.0  # the supplied M2 screws' head diameter, at most (typical pan head)
MIN_HUB_GAP_MM = 2.0  # anything static stays this far below the hub's servo-side face


@dataclass(frozen=True)
class Cradle:
    """The servo mount: a U that the servo's bottom bolts into. Design choices.

    Frame: the shaft axis is the origin; a runs along the case towards the far end, b across it,
    c along the shaft towards the horn, with c = 0 on the bottom step face the servo sits on.
    """

    wall_mm: float = 2.0  # back wall the screws pass through
    pad_mm: float = 0.5  # pads at the four holes, so the servo sits on them and not on the wall
    pad_diameter_mm: float = 4.3
    cheek_mm: float = 3.0  # side walls that hug the case's long sides
    cheek_height_mm: float = 20.0  # from the step face towards the horn
    side_clearance_mm: float = 0.2  # per side, so the servo slides in
    disc_clearance_mm: float = 1.0  # round the idler disc, radially
    keepout_margin_mm: float = 0.4  # round the connector recess and pad
    ear_length_mm: float = 10.0  # tabs on the foot cheek, one at each end
    ear_mm: float = 4.0
    ear_screw: str = "M3"


@dataclass(frozen=True)
class CradleDerived:
    a_min_mm: float  # near end of the case
    a_max_mm: float  # far end
    b_inner_mm: float  # cheek inner faces at +-this
    b_outer_mm: float  # cheek outer faces; the foot is the face at -this
    holes: tuple[tuple[float, float], ...]  # (a, b) of the four mounting holes
    hole_diameter_mm: float
    screw_depth_mm: float  # how far the supplied screws go into the case
    disc_opening_radius_mm: float
    near_pad_gap_mm: float  # between the disc opening and the near pads
    window: tuple[float, float, float]  # a from, a to, half width
    throat_half_width_mm: float  # joins the disc opening to the window, clear of the near pads
    hub_face_c_mm: float
    axle_above_foot_mm: float  # the chassis needs this: foot face to wheel axis


def derive_cradle(case: Case, horn: Horn, c: Cradle) -> CradleDerived:
    """Size the cradle against the servo, or raise ValueError naming what does not fit."""
    under_head = c.wall_mm + c.pad_mm
    depth = case.mount_screw_length_mm - under_head
    if depth > case.max_screw_depth_mm:
        raise ValueError(
            f"the M2 x {case.mount_screw_length_mm} screws would go {depth:.1f} mm into the case, "
            f"past the {case.max_screw_depth_mm} mm known to be safe; thicken the wall"
        )
    if depth < MIN_SELF_TAP_MM:
        raise ValueError(f"the screws would bite only {depth:.1f} mm into the case; thin the wall")

    along = (case.holes_near_offset_mm, case.holes_near_offset_mm + case.bottom_holes_along_mm)
    across = case.bottom_holes_across_mm / 2
    holes = tuple((a, b) for a in along for b in (-across, across))

    disc_r = case.bottom_disc_od_mm / 2 + c.disc_clearance_mm
    near = math.hypot(along[0], across)
    near_pad_gap = near - c.pad_diameter_mm / 2 - disc_r
    if near_pad_gap < 0:
        raise ValueError("the disc opening cuts into the near pads; slim the pads")
    if near - SCREW_HEAD_MM / 2 < disc_r:
        raise ValueError("the near screw heads would overhang the disc opening")

    m = c.keepout_margin_mm
    window = (case.bottom_keepout_from_mm - m, case.bottom_keepout_to_mm + m)
    half = case.bottom_keepout_half_width_mm + m
    pad_r = c.pad_diameter_mm / 2
    if window[0] < along[0] + pad_r or window[1] > along[1] - pad_r:
        raise ValueError("the connector window would cut into the mounting pads")

    # The disc opening and the window nearly meet; a strip between them would be too thin to
    # print, so a throat joins them, staying 1 mm clear of the near pads.
    throat = across - pad_r - 1.0
    if throat < 2.0:
        raise ValueError("no room for a throat between the disc opening and the window")

    b_inner = case.width_mm / 2 + c.side_clearance_mm
    if half >= b_inner:
        raise ValueError("the connector window is wider than the case")
    hub_face = case.bottom_step_mm + case.height_shaft_end_mm + horn.shaft_height_mm
    if c.cheek_height_mm > hub_face - MIN_HUB_GAP_MM:
        raise ValueError(f"cheeks reach within {MIN_HUB_GAP_MM} mm of the spinning hub")

    a_min = -case.shaft_to_near_end_mm
    return CradleDerived(
        a_min_mm=a_min,
        a_max_mm=a_min + case.length_mm,
        b_inner_mm=b_inner,
        b_outer_mm=b_inner + c.cheek_mm,
        holes=holes,
        hole_diameter_mm=CLEARANCE_MM["M2"],
        screw_depth_mm=depth,
        disc_opening_radius_mm=disc_r,
        near_pad_gap_mm=near_pad_gap,
        window=(window[0], window[1], half),
        throat_half_width_mm=throat,
        hub_face_c_mm=hub_face,
        axle_above_foot_mm=b_inner + c.cheek_mm,
    )


PRINT_BED_MM = (325.0, 320.0)  # H2D, one nozzle (Bambu tech specs)
MIN_COM_BEHIND_AXLE_MM = 20.0  # with one caster at the back, the robot tips forward without this
MIN_COM_BEHIND_WITH_ARM_MM = 10.0  # v2: the arm at full forward reach


@dataclass(frozen=True)
class Mass:
    name: str
    kg: float
    x_mm: float  # fore-aft position of its centre of mass; + is forward of the axle
    source: str


@dataclass(frozen=True)
class BaseLayout:
    """Plan view of the base, decided 2026-11-19: the widest stance, battery across between the
    servos. Axes: x fore-aft (+ forward) with the axle at x = 0, y across.

    Masses are estimates for the balance check; the README's tip test is what decides v2.
    """

    battery_mm: tuple[float, float, float] = (152.0, 66.0, 94.0)  # across, fore-aft, height
    battery_x_mm: float = -40.0  # behind the axle, so its weight keeps the nose up
    cable_room_mm: float = 20.0  # battery end to cradle back: the servo plugs come out there
    front_mm: float = 110.0  # plate edges, fore-aft
    back_mm: float = -190.0
    caster_x_mm: float = (
        -158.0
    )  # moved from -165 so the caster cup and its screws stay on the plate
    electronics_x_mm: tuple[float, float] = (-80.0, -185.0)  # deck zone behind the battery
    arm_base_x_mm: float = -110.0  # v2: SO-101 base on a top deck
    arm_reach_com_mm: float = 150.0  # the arm's centre of mass ahead of its base at full reach
    arm_kg: float = 1.0
    other: tuple[Mass, ...] = (
        Mass("plate", 0.25, -40.0, "estimate: about 300 x 260 x 4 mm PETG, part infill"),
        Mass("electronics", 0.25, -130.0, "estimate: Pi 5, driver, converters, wiring"),
        Mass("caster", 0.04, -158.0, "estimate"),
    )
    battery_kg: float = 1.22  # EP1210 sheet; the model is confirmed from its label (2026-11-21)
    servo_kg: float = 0.055  # each (STS3215 listings: about 55 g)
    wheel_module_kg: float = 0.19  # wheel module v2, from its model's volume (2026-11-24)
    wheel_module_x_mm: float = -8.0  # its centre of mass, boxes and beam (model, rounded)
    wheel_kg: float = 0.146  # each: printed hub 59 g (118.5 g for two) + TPU tire about 87 g


@dataclass(frozen=True)
class BaseDerived:
    cradle_back_y_mm: float
    wheel_inner_y_mm: float
    track_mm: float
    width_over_tires_mm: float
    plate_half_width_mm: float
    plate_length_mm: float
    masses: tuple[Mass, ...]
    com_x_mm: float
    com_x_with_arm_mm: float
    caster_share: float  # of the weight, without the arm


def _com(masses: tuple[Mass, ...]) -> float:
    total = sum(m.kg for m in masses)
    return sum(m.kg * m.x_mm for m in masses) / total


def derive_base(case: Case, horn: Horn, cradle: Cradle, b: BaseLayout) -> BaseDerived:
    """Lay out the base in plan, or raise ValueError naming what does not work."""
    d = derive_cradle(case, horn, cradle)
    back_wall = cradle.wall_mm + cradle.pad_mm  # cradle back face, behind the step face
    cradle_back = b.battery_mm[0] / 2 + b.cable_room_mm
    wheel_inner = cradle_back + back_wall + d.hub_face_c_mm
    wheel_width = Wheel().width_mm
    plate_half = wheel_inner - MIN_HUB_GAP_MM
    length = b.front_mm - b.back_mm
    if max(length, 2 * plate_half) > max(PRINT_BED_MM) or min(length, 2 * plate_half) > min(
        PRINT_BED_MM
    ):
        raise ValueError(f"a {length:.0f} x {2 * plate_half:.0f} mm plate does not fit the H2D bed")
    if not b.back_mm < b.caster_x_mm < b.battery_x_mm - b.battery_mm[1] / 2:
        raise ValueError("the caster must sit behind the battery and on the plate")

    masses = (
        Mass("battery", b.battery_kg, b.battery_x_mm, "EP1210 sheet (model on the label)"),
        # Wheel module v2: both servos' far ends point back.
        Mass("servo, +y", b.servo_kg, -(d.a_min_mm + d.a_max_mm) / 2, "STS3215 about 55 g"),
        Mass("servo, -y", b.servo_kg, -(d.a_min_mm + d.a_max_mm) / 2, "STS3215 about 55 g"),
        Mass("wheel module v2", b.wheel_module_kg, b.wheel_module_x_mm, "model volume, 6 walls"),
        Mass("wheels", 2 * b.wheel_kg, 0.0, "printed hubs weighed by the slicer; tire estimate"),
        *b.other,
    )
    com = _com(masses)
    arm = Mass("v2 arm at full reach", b.arm_kg, b.arm_base_x_mm + b.arm_reach_com_mm, "README")
    com_arm = _com((*masses, arm))
    if -com < MIN_COM_BEHIND_AXLE_MM:
        raise ValueError(f"centre of mass only {-com:.0f} mm behind the axle; move weight back")
    if -com_arm < MIN_COM_BEHIND_WITH_ARM_MM:
        raise ValueError(
            f"with the v2 arm reaching forward the centre of mass is {-com_arm:.0f} mm behind "
            "the axle; move the arm base back or the battery back"
        )
    return BaseDerived(
        cradle_back_y_mm=cradle_back,
        wheel_inner_y_mm=wheel_inner,
        track_mm=2 * (wheel_inner + wheel_width / 2),
        width_over_tires_mm=2 * (wheel_inner + wheel_width),
        plate_half_width_mm=plate_half,
        plate_length_mm=length,
        masses=masses,
        com_x_mm=com,
        com_x_with_arm_mm=com_arm,
        caster_share=-com / -b.caster_x_mm,
    )


@dataclass(frozen=True)
class Caster:
    """The rear swivel caster (1.5 in PU, 8-pack, inventory row 8), measured 2026-11-21.

    Its plate is the common 46 x 38 mm caster plate; the Tente 1430 sheet gives that plate holes on
    36 x 28 mm centres and a 5.3 mm hole (other makers about 4.2 mm), which the readings match. Size
    the plate's screws to M4: they pass either hole.
    """

    height_mm: float = 50.0  # floor to the top face of its mounting plate
    plate_long_mm: float = 46.0  # over the corners; both long ends are concave
    plate_waist_mm: float = 40.5  # the long length across the middle of the concave ends
    plate_short_mm: float = 38.25
    holes_long_mm: float = 35.75  # hole centres
    holes_short_mm: float = 27.75
    swivel_offset_mm: float = 13.0  # swivel axis to wheel axle, sideways
    wheel_mm: float = 38.1  # 1.5 in, from the listing
    # Upside down, fork turned out past one short end: from a point of the other short end to the
    # fork's farthest point (not the wheel). Measured after the first cup's walls hit the fork.
    fork_reach_mm: float = 47.0

    @property
    def fork_radius_mm(self) -> float:
        """Swivel axis (the plate's centre) to the fork's farthest point: what it sweeps."""
        return self.fork_reach_mm - self.plate_long_mm / 2

    @property
    def swing_radius_mm(self) -> float:
        """Swivel axis to the far side of the wheel: the circle it sweeps as it turns."""
        return self.swivel_offset_mm + self.wheel_mm / 2


PLATE_MM = 4.0  # base plate thickness (design choice, PETG)
MIN_CASTER_WHEEL_GAP_MM = 1.0  # plate underside above the caster wheel's top


@dataclass(frozen=True)
class Heights:
    """Heights above the floor with the cradles sitting on top of the base plate."""

    axle_mm: float
    plate_top_mm: float
    plate_underside_mm: float
    caster_mount_mm: float  # how far above the plate's underside the caster's plate must sit
    caster_boss_mm: float  # how far the caster's mounting face stands above the plate's top
    caster_wheel_gap_mm: float  # plate underside above the top of the caster wheel


def derive_heights(
    case: Case, horn: Horn, cradle: Cradle, caster: Caster, plate_mm: float = PLATE_MM
) -> Heights:
    """Where the base plate sits so the cradles hold the axle at the wheel radius and the plate is
    level on the caster. Decided 2026-11-21: cradles on top of the plate (the low, stout option);
    the caster then mounts in a raised pocket. Raises ValueError naming what does not work."""
    axle = Tire().od_mm / 2
    top = axle - derive_cradle(case, horn, cradle).axle_above_foot_mm
    under = top - plate_mm
    mount = caster.height_mm - under
    if mount < plate_mm:
        raise ValueError(
            f"the caster's plate would sit {mount:.1f} mm above the plate's underside, inside the "
            "plate; use a flat mount or a spacer instead of a raised pocket"
        )
    gap = under - caster.wheel_mm
    if gap < MIN_CASTER_WHEEL_GAP_MM:
        raise ValueError(
            f"the plate's underside is only {gap:.1f} mm above the caster wheel; it would rub"
        )
    return Heights(
        axle_mm=axle,
        plate_top_mm=top,
        plate_underside_mm=under,
        caster_mount_mm=mount,
        caster_boss_mm=caster.height_mm - top,
        caster_wheel_gap_mm=gap,
    )


@dataclass(frozen=True)
class CasterCup:
    """A light open cup the caster bolts up into: the raised pocket from `derive_heights`, made as
    its own part so the base plate can print flat. The cavity is the caster's plate (a box) plus
    the fork's sweep (a circle). v1 (2026-11-21) had the box only and the fork hit its walls.

    Frame: x along the caster plate's long side, y across, z down from the mounting face (the cup
    prints roof-down, so the model's z = 0 is the roof's outer face on the bed).
    """

    wall_mm: float = 2.0
    roof_mm: float = 3.0
    clearance_mm: float = 0.5  # per side round the caster's plate
    fork_clearance_mm: float = 1.5  # round the fork's sweep (swivel play, centre not exact)
    inner_corner_mm: float = 1.0
    hole_mm: float = 4.5  # M4 clearance, through the roof; nut on top
    center_hole_mm: float = 22.0  # clears the swivel rivet and saves plastic
    # Four bosses outside the walls, at 45 degrees, bolt the cup to the plate: M3 from under the
    # plate up through the boss, nut on the roof. Off on the fit-test version.
    mount_bosses: bool = True
    boss_at_mm: float = 33.0  # boss centres from the swivel axis
    boss_mm: float = 8.0  # boss diameter


# Fit tests only check the caster's plate, holes and fork sweep, so they skimp on plastic.
CASTER_CUP_TEST = CasterCup(wall_mm=1.2, roof_mm=2.0, center_hole_mm=34.0, mount_bosses=False)

M4_MIN_ENGAGE_MM = 2.0  # three threads at 0.7 mm pitch
M3_NUT_MM = 2.4
M3_MIN_ENGAGE_MM = 1.5  # three threads at 0.5 mm pitch


@dataclass(frozen=True)
class CasterCupDerived:
    inner_mm: tuple[float, float]  # the box that takes the caster's plate
    outer_mm: tuple[float, float]
    sweep_radius_mm: float  # the round part of the cavity, for the fork
    outer_radius_mm: float
    depth_mm: float  # roof's inner face to the open end, which sits on the plate's top face
    height_mm: float
    holes: tuple[tuple[float, float], ...]
    screw: str
    mount_holes: tuple[tuple[float, float], ...]  # M3 through the bosses, into the base plate
    mount_screw: str


def derive_caster_cup(caster: Caster, heights: Heights, c: CasterCup) -> CasterCupDerived:
    inner = (
        caster.plate_long_mm + 2 * c.clearance_mm,
        caster.plate_short_mm + 2 * c.clearance_mm,
    )
    outer = (inner[0] + 2 * c.wall_mm, inner[1] + 2 * c.wall_mm)
    sweep = caster.fork_radius_mm + c.fork_clearance_mm
    # The cup sits on the plate's TOP face, so its cavity is the raised pocket less the plate's
    # thickness; the plate's cutout supplies the rest. (v1 and v2 counted the plate twice and
    # left the caster 4 mm high: the robot tipped nose up, found by the owner 2026-11-21.)
    depth = heights.caster_mount_mm - PLATE_MM
    if depth <= 0:
        raise ValueError("the caster's plate sits below the base plate's top: no cup needed")
    hx, hy = caster.holes_long_mm / 2, caster.holes_short_mm / 2
    holes = tuple((sx * hx, sy * hy) for sx in (-1, 1) for sy in (-1, 1))
    if c.center_hole_mm / 2 + c.hole_mm / 2 + 2.0 > (hx**2 + hy**2) ** 0.5:
        raise ValueError("the centre hole runs into the caster's screw holes")
    # Screw: caster plate (about 3 mm) + roof + three threads into the nut, rounded up to a
    # length in the Mywish kit. The tip need not pass the nut: 2026-11-21 the owner found M4 x 12
    # stood well proud, and long tips would reach for the electronics deck above the cup.
    need = 3.0 + c.roof_mm + M4_MIN_ENGAGE_MM
    length = next(n for n in (8, 12, 16, 20) if n >= need)
    mount: tuple[tuple[float, float], ...] = ()
    mount_screw = ""
    if c.mount_bosses:
        k = c.boss_at_mm / math.sqrt(2)
        mount = tuple((sx * k, sy * k) for sx in (-1, 1) for sy in (-1, 1))
        r = CLEARANCE_MM["M3"] / 2
        if k - r - inner[1] / 2 < 1.5 or c.boss_at_mm - r - sweep < 1.5:
            raise ValueError("the cup's mounting holes come within 1.5 mm of its cavity")
        m_need = PLATE_MM + depth + c.roof_mm + M3_MIN_ENGAGE_MM
        m_len = next((n for n in (8, 12, 16, 20) if n >= m_need), None)
        if m_len is None:
            raise ValueError(f"the cup's mounting screws need {m_need:.1f} mm, longer than the kit")
        mount_screw = f"M3 x {m_len} button head and nut"
    return CasterCupDerived(
        inner_mm=inner,
        outer_mm=outer,
        sweep_radius_mm=sweep,
        outer_radius_mm=sweep + c.wall_mm,
        depth_mm=depth,
        height_mm=depth + c.roof_mm,
        holes=holes,
        screw=f"M4 x {length} button head and nut",
        mount_holes=mount,
        mount_screw=mount_screw,
    )


WHEEL_LOAD_FACTOR = 5.0  # owner, 2026-11-24: "hella sturdy"; the plan's rule was 3 x static
MAX_LEVER_RATIO = 2.0  # load lever to bolt lever about the pivot edge (cad/README.md, rule 9)
M3_PULL_THROUGH_N = 900.0  # a button head pulling through 5 mm of PETG, low estimate (shear of a
#  5.7 mm ring 5 mm deep at about 10 MPa, a third of the bulk figure, for layers and creep)
SAFE_PETG_MPA = 5.0  # bending stress allowed in a wall along its layers, after creep (about 1/6)
G = 9.81


@dataclass(frozen=True)
class WheelModule:
    """Wheel module v2: both servo boxes and the axle beam in one PETG piece (2026-11-24).

    Replaces the two cradles, which rolled over under the robot's weight (WHEEL_MOUNT.md). Each
    servo sits in a closed box: walls on its two long sides and both ends, and a back wall it
    screws into. A solid beam ahead of the boxes ties the two together, so the two wheels'
    rolling moments meet in the part, not in the plate. Both servos point their far ends back
    (the -y servo is turned half a turn about its shaft, which its symmetric holes allow).

    Frame: the base's (x forward, y left, axle at x = 0), z up from the base plate's top face.
    Prints standing on the beam's front face, so the rolling moment lies in the layers.
    """

    back_wall_mm: float = 5.0  # the servo screws into this; counterbored for the M2 x 6
    top_wall_mm: float = 5.0  # over the case's upper long side
    end_wall_mm: float = 5.0  # at both ends of the case, carried inboard as gussets
    foot_mm: float = 5.0  # slab on the plate, outside the case's footprint
    # Under the case the wall stays the cradle's 3 mm (Cradle.cheek_mm), so the axle keeps its
    # height and the caster cup still levels the robot.
    side_clearance_mm: float = 0.2  # per side round the case, as the cradle
    fence_gap_mm: float = 2.0  # foot's inboard edge to the battery fence
    foot_back_mm: float = -52.0  # foot's rear edge (x); the deck starts at x = -80.8
    beam_x_mm: tuple[float, float] = (15.4, 31.0)  # solid beam, ahead of the front end walls
    gusset_notch_mm: tuple[float, float] = (6.0, 12.0)  # cable notch: from the foot edge, height
    driver_groove_mm: tuple[float, float] = (6.0, 2.0)  # width, floor height: screwdriver path
    counterbore_mm: float = 4.4  # for the M2 screw heads (SCREW_HEAD_MM plus 0.4)
    screw_bite_mm: float = 3.5  # how far the M2 x 6 goes into the case
    foot_bolts: tuple[tuple[float, float], ...] = (  # +y side; the -y side mirrors in y
        (5.0, 85.0),
        (-46.0, 85.0),
        (-46.0, 105.0),
        (-46.0, 124.0),
    )
    beam_bolts_y_mm: tuple[float, ...] = (124.0, 85.0, 42.0, 0.0)  # and their mirrors
    beam_counterbore_mm: float = 6.4  # button head 5.7 plus room
    beam_bolt_floor_mm: float = 10.0  # beam left under each beam bolt's head


@dataclass(frozen=True)
class WheelModuleDerived:
    axis_z_mm: float  # wheel axis above the plate's top
    step_y_mm: float  # the servo's step face (bottom), +y side
    cavity: tuple[float, float, float, float, float]  # x0, x1, z0, z1, y0 (+y side)
    back_wall_y_mm: tuple[float, float]
    outer_y_mm: float  # boxes and beam end here, 2 mm short of the hub
    top_z_mm: float
    end_walls_x: tuple[tuple[float, float], tuple[float, float]]  # far (rear), near (front)
    foot: tuple[float, float, float, float]  # x0, x1, y0, y1, +y side
    m2_holes: tuple[tuple[float, float], ...]  # (x, z) on the back wall
    counterbore_y_mm: tuple[float, float]  # from the back face to the counterbore floor
    disc_opening: tuple[float, float, float]  # x, z, radius
    window: tuple[float, float, float, float]  # x0, x1, z0, z1
    throat: tuple[float, float, float, float]
    driver_grooves_x: tuple[float, ...]
    plate_holes: tuple[tuple[float, float], ...]  # every M3 to the plate, both sides
    beam_holes: tuple[tuple[float, float], ...]  # the subset through the beam (counterbored)
    footprint: tuple[Rect, ...]  # boxes and beam in plan, for the plate's checks
    screws: dict[str, str]
    lever_ratio: float
    wheel_load_n: float  # per wheel, static, with the v2 arm at full reach
    design_load_n: float  # times WHEEL_LOAD_FACTOR
    bolt_tension_n: float  # outboard bolts at the design load
    wall_stress_mpa: float  # bending at the back-wall section at the design load


def derive_wheel_module(
    case: Case, horn: Horn, cradle: Cradle, layout: BaseLayout, m: WheelModule | None = None
) -> WheelModuleDerived:
    """Size the wheel module and check it, or raise ValueError naming what does not work."""
    m = m or WheelModule()
    cd = derive_cradle(case, horn, cradle)
    base = derive_base(case, horn, cradle, layout)
    axis = cd.axle_above_foot_mm
    step = base.cradle_back_y_mm + cradle.wall_mm + cradle.pad_mm
    pad = cradle.pad_mm
    sc = m.side_clearance_mm
    x0, x1 = -cd.a_max_mm - sc, -cd.a_min_mm + sc  # far end back
    half = case.width_mm / 2 + sc
    z0, z1 = axis - half, axis + half
    if abs(z0 - cradle.cheek_mm) > 1e-9:
        raise ValueError("the wall under the case must stay the cradle's, or the axle moves")
    back = (step - pad - m.back_wall_mm, step - pad)
    outer = step + cd.hub_face_c_mm - MIN_HUB_GAP_MM
    top = z1 + m.top_wall_mm
    ends = ((x0 - m.end_wall_mm, x0), (x1, x1 + m.end_wall_mm))
    if abs(ends[1][1] - m.beam_x_mm[0]) > 1e-9:
        raise ValueError("the beam must start at the front end walls' faces")
    fence = layout.battery_mm[0] / 2 + 1.0 + 2.0  # BasePlate clearance and fence
    foot = (m.foot_back_mm, ends[1][1], fence + m.fence_gap_mm, outer)

    under_head = case.mount_screw_length_mm - m.screw_bite_mm
    if not MIN_SELF_TAP_MM <= m.screw_bite_mm <= case.max_screw_depth_mm:
        raise ValueError("the M2 screws' bite is outside what the case holes take")
    cb = (back[0], step - under_head)
    if cb[1] <= cb[0]:
        raise ValueError("no counterbore needed: the wall is thin enough as is")
    holes = tuple((-a, axis + b) for a, b in cd.holes)

    w0, w1, wh = cd.window
    window = (-w1, -w0, axis - wh, axis + wh)
    throat = (-w0, 0.0, axis - cd.throat_half_width_mm, axis + cd.throat_half_width_mm)
    grooves = tuple(sorted({-a for a, _ in cd.holes}))
    # The lower screws sit just above the foot: a groove lets a driver reach them.
    for x, z in holes:
        if z < m.foot_mm + 2.0 and x not in grooves:
            raise ValueError("a lower M2 screw has no driver groove")
    low = min(z for _, z in holes)
    if low - 2.0 < m.driver_groove_mm[1]:
        raise ValueError("the driver groove is not deep enough for a 4 mm driver")

    # Bolts: on the plate, clear of the walls, window and grooves, two lines across the load.
    r_head = HEADS["button"]["M3"][0] / 2
    for x, y in m.foot_bolts:
        if not (foot[0] + r_head <= x <= foot[1] and foot[2] + r_head <= y <= foot[3] - r_head):
            raise ValueError(f"foot bolt ({x}, {y}) is off the foot")
        in_x = x0 - m.end_wall_mm - r_head < x < x1 + m.end_wall_mm + r_head
        if in_x and y > back[0] - r_head:
            raise ValueError(f"foot bolt ({x}, {y}) is under the servo box")
        for gx in grooves:
            if abs(x - gx) < m.driver_groove_mm[0] / 2 + r_head and y < back[0]:
                raise ValueError(f"foot bolt ({x}, {y}) is in a driver groove")
        for ex0, ex1 in ends:
            if ex0 - r_head < x < ex1 + r_head and y < back[0]:
                raise ValueError(f"foot bolt ({x}, {y}) is under a gusset")
    beam_x = sum(m.beam_x_mm) / 2
    if m.beam_x_mm[1] - m.beam_x_mm[0] < m.beam_counterbore_mm + 4.0:
        raise ValueError("the beam is too thin for its bolt counterbores")
    beam_holes = tuple((beam_x, s * y) for y in m.beam_bolts_y_mm for s in (1, -1) if s > 0 or y)
    plate_holes = (
        *((x, s * y) for x, y in m.foot_bolts for s in (1, -1)),
        *beam_holes,
    )
    ys_out = [y for _, y in m.foot_bolts]
    if max(ys_out) - min(ys_out) < 20.0:
        raise ValueError("the foot bolts must stand on two lines across the load")

    # The load path (WHEEL_MOUNT.md): per wheel, the robot's weight with the arm reaching forward.
    total = sum(mm.kg for mm in base.masses) + layout.arm_kg
    com = base.com_x_with_arm_mm
    wheel_n = total * G * (1 - (-com) / (-layout.caster_x_mm)) / 2
    design = WHEEL_LOAD_FACTOR * wheel_n
    tire_y = base.wheel_inner_y_mm + Wheel().width_mm / 2
    pivot = foot[2]
    lever = tire_y - pivot
    out_y = max(ys_out)
    ratio = lever / (out_y - pivot)
    if ratio > MAX_LEVER_RATIO:
        raise ValueError(f"load lever {ratio:.2f} x the bolt lever; move bolts outboard")
    outboard = sum(1 for _, y in m.foot_bolts if y == out_y) + sum(
        1 for y in m.beam_bolts_y_mm if y == out_y
    )
    tension = design * lever / ((out_y - pivot) * outboard)
    if tension > M3_PULL_THROUGH_N / 3:
        raise ValueError(f"outboard bolts carry {tension:.0f} N each; add bolts")
    # Bending at the back-wall section (y = back face): an I of the top wall, the wall under the
    # case plus foot, and the two end walls, about the section's centroid.
    length_x = ends[1][1] - ends[0][0]
    parts = (
        (length_x * m.top_wall_mm, (z1 + top) / 2, m.top_wall_mm),
        (length_x * m.foot_mm, m.foot_mm / 2, m.foot_mm),
    )
    walls = 2 * m.end_wall_mm
    area = sum(a for a, _, _ in parts) + walls * top
    zc = (sum(a * z for a, z, _ in parts) + walls * top * top / 2) / area
    inertia = sum(a * (z - zc) ** 2 + a * t**2 / 12 for a, z, t in parts)
    inertia += walls * top**3 / 12 + walls * top * (top / 2 - zc) ** 2
    moment = design * (tire_y - back[0])
    stress = moment * max(zc, top - zc) / inertia
    if stress > SAFE_PETG_MPA:
        raise ValueError(f"the box walls see {stress:.1f} MPa at the back wall; thicken them")

    foot_screw = kit_screw(m.foot_mm + PLATE_MM, "wheel module foot")
    beam_screw = kit_screw(m.beam_bolt_floor_mm + PLATE_MM, "wheel module beam")
    footprint = (
        (foot[0], foot[1], foot[2], outer),
        (foot[0], foot[1], -outer, -foot[2]),
        (m.beam_x_mm[0], m.beam_x_mm[1], -outer, outer),
    )
    n_foot = 2 * len(m.foot_bolts)
    return WheelModuleDerived(
        axis_z_mm=axis,
        step_y_mm=step,
        cavity=(x0, x1, z0, z1, step - pad),
        back_wall_y_mm=back,
        outer_y_mm=outer,
        top_z_mm=top,
        end_walls_x=ends,
        foot=foot,
        m2_holes=holes,
        counterbore_y_mm=cb,
        disc_opening=(0.0, axis, cd.disc_opening_radius_mm),
        window=window,
        throat=throat,
        driver_grooves_x=grooves,
        plate_holes=tuple(plate_holes),
        beam_holes=beam_holes,
        footprint=footprint,
        screws={
            "foot": f"{n_foot} x M3 x {foot_screw} button head and nut (foot 5 mm + plate 4 mm)",
            "beam": f"{len(beam_holes)} x M3 x {beam_screw} button head and nut, heads down "
            "the beam's counterbores",
            "servos": "8 x the M2 x 6 self-tapping screws supplied with the servos",
        },
        lever_ratio=ratio,
        wheel_load_n=wheel_n,
        design_load_n=design,
        bolt_tension_n=tension,
        wall_stress_mpa=stress,
    )


@dataclass(frozen=True)
class BasePlate:
    """The base plate: one flat 4 mm PETG piece, printed underside down. Design choices.

    Frame: x fore-aft (+ forward, axle at 0), y across, z up from the plate's underside. Every
    screw is M3 with a nut, so the plate needs no inserts. Parts that are not designed yet (the
    electronics deck, the bumper, sensor brackets) bolt to hole patterns here and copy them.
    """

    corner_radius_mm: float = 10.0
    edge_margin_mm: float = 5.0  # hole edge to plate edge, at least
    battery_clearance_mm: float = 1.0  # per side round the battery's footprint
    fence_mm: float = 2.0  # corner stops round the battery
    fence_height_mm: float = 3.0
    fence_leg_mm: float = 12.0
    # Hook-and-loop straps go up one slot, over the battery and down the other. Measured
    # 2026-11-21 (inventory row 24): the strap is 21.5 mm wide, its buckle 27.5 mm. Thread the free
    # end through the slots, so only the strap passes and the buckle stays on top. None means not
    # measured, and the build then marks the plate unmeasured.
    strap_width_mm: float | None = 21.5
    strap_slot_mm: float = 4.0  # slot width, for the strap's thickness
    strap_y_mm: float = 40.0  # two straps, at +- this
    grid_pitch_mm: float = 20.0  # electronics deck holes
    grid_x_mm: tuple[float, ...] = (-95.0, -115.0, -135.0, -155.0, -175.0)
    grid_y_max_mm: float = 100.0
    grid_caster_keepout_mm: float = 42.0  # no grid holes this close to the caster's axis
    bumper_x_mm: float = 100.0  # front row: the bumper
    sensor_x_mm: float = 75.0  # second row: forward sensor brackets
    row_pitch_mm: float = 30.0
    row_y_max_mm: float = 120.0
    cliff_window_mm: float = 14.0  # downward ToF sensors look through these
    cliff_x_mm: float = 88.0
    cliff_y_mm: tuple[float, ...] = (-105.0, 0.0, 105.0)


STRAP_PLACEHOLDER_MM = 25.0  # used for drawing only, while BasePlate.strap_width_mm is None


@dataclass(frozen=True)
class BasePlateDerived:
    x_back_mm: float
    x_front_mm: float
    half_width_mm: float
    thickness_mm: float
    measured: bool  # False while the strap width is a placeholder
    wheel_holes: tuple[tuple[float, float], ...]  # wheel module v2: foot and beam bolts
    wheel_footprint: tuple[tuple[float, float, float, float], ...]  # x0, x1, y0, y1 on the top
    caster_xy: tuple[float, float]
    cup: CasterCupDerived
    cup_holes: tuple[tuple[float, float], ...]
    battery_box: tuple[float, float, float, float]  # x0, x1, y0, y1 inside the fences
    strap_slots: tuple[tuple[float, float, float, float], ...]  # x0, x1, y0, y1
    grid_holes: tuple[tuple[float, float], ...]
    front_holes: tuple[tuple[float, float], ...]
    cliff_windows: tuple[tuple[float, float], ...]
    screws: dict[str, str]


def derive_base_plate(
    case: Case,
    horn: Horn,
    cradle: Cradle,
    caster: Caster,
    layout: BaseLayout,
    p: BasePlate,
    cup: CasterCup,
    wheel: WheelModule | None = None,
) -> BasePlateDerived:
    """Every hole and feature on the base plate, or ValueError naming what collides."""
    base = derive_base(case, horn, cradle, layout)
    heights = derive_heights(case, horn, cradle, caster)
    t = PLATE_MM
    x0, x1, half = layout.back_mm, layout.front_mm, base.plate_half_width_mm

    # Wheel module v2 (2026-11-24): its foot and beam bolts. The cradles' holes are gone; plate
    # v1, drilled for them, is the spare.
    wm = derive_wheel_module(case, horn, cradle, layout, wheel)
    wheel_holes = wm.plate_holes
    feet = wm.footprint

    cupd = derive_caster_cup(caster, heights, cup)
    cx = layout.caster_x_mm
    cup_holes = tuple((cx + hx, hy) for hx, hy in cupd.mount_holes)

    bw = layout.battery_mm[0] / 2 + p.battery_clearance_mm
    bd = layout.battery_mm[1] / 2 + p.battery_clearance_mm
    bx = layout.battery_x_mm
    battery_box = (bx - bd, bx + bd, -bw, bw)
    strap = p.strap_width_mm or STRAP_PLACEHOLDER_MM
    slot_len = strap + 3.0
    off = p.fence_mm + 0.5 + p.strap_slot_mm / 2
    slots = tuple(
        (sx - p.strap_slot_mm / 2, sx + p.strap_slot_mm / 2, sy - slot_len / 2, sy + slot_len / 2)
        for sx in (bx - bd - off, bx + bd + off)
        for sy in (-p.strap_y_mm, p.strap_y_mm)
    )

    n = int(p.grid_y_max_mm // p.grid_pitch_mm)
    ys = [k * p.grid_pitch_mm for k in range(-n, n + 1)]
    grid = tuple(
        (x, y) for x in p.grid_x_mm for y in ys if math.hypot(x - cx, y) > p.grid_caster_keepout_mm
    )
    m = int(p.row_y_max_mm // p.row_pitch_mm)
    row_y = [k * p.row_pitch_mm for k in range(-m, m + 1)]
    front = tuple((x, y) for x in (p.bumper_x_mm, p.sensor_x_mm) for y in row_y)
    cliffs = tuple((p.cliff_x_mm, y) for y in p.cliff_y_mm)

    # Checks: every hole on the plate with margin, and no two features touching.
    r3 = CLEARANCE_MM["M3"] / 2
    circles = [(x, y, r3) for x, y in (*wheel_holes, *cup_holes, *grid, *front)]
    circles += [(x, y, p.cliff_window_mm / 2) for x, y in cliffs]
    for x, y, r in circles:
        tol = 1e-6
        if not (x0 + p.edge_margin_mm + r - tol <= x <= x1 - p.edge_margin_mm - r + tol):
            raise ValueError(f"hole at ({x:.1f}, {y:.1f}) is too close to the front or back edge")
        if abs(y) > half - p.edge_margin_mm - r + tol:
            raise ValueError(f"hole at ({x:.1f}, {y:.1f}) is too close to a side edge")
    for i, (xa, ya, ra) in enumerate(circles):
        for xb, yb, rb in circles[i + 1 :]:
            if math.hypot(xa - xb, ya - yb) < ra + rb + 2.0:
                raise ValueError(f"holes at ({xa:.1f}, {ya:.1f}) and ({xb:.1f}, {yb:.1f}) touch")

    def in_rect(x: float, y: float, r: float, rect: tuple[float, float, float, float]) -> bool:
        rx0, rx1, ry0, ry1 = rect
        return rx0 - r - 2.0 < x < rx1 + r + 2.0 and ry0 - r - 2.0 < y < ry1 + r + 2.0

    keep = [*slots, battery_box]
    for x, y, r in circles:
        if (x, y) in wheel_holes:
            continue
        for rect in (*keep, *feet):
            if in_rect(x, y, r, rect):
                raise ValueError(f"hole at ({x:.1f}, {y:.1f}) runs into a slot, foot or battery")
    cut_r = max(cupd.sweep_radius_mm, math.hypot(*[v / 2 for v in cupd.inner_mm]))
    for x, y, r in circles:
        if (x, y) in cup_holes:
            continue
        if math.hypot(x - cx, y) < cut_r + r + 2.0:
            raise ValueError(f"hole at ({x:.1f}, {y:.1f}) runs into the caster cutout")
    if cx - cupd.outer_radius_mm < x0 + 1.0:
        raise ValueError("the caster cup hangs off the back edge; move the caster forward")
    for fx0, fx1, fy0, fy1 in feet:
        bx0, bx1, by0, by1 = battery_box
        if fx0 < bx1 and bx0 < fx1 and fy0 < by1 + p.fence_mm and by0 - p.fence_mm < fy1:
            raise ValueError("the wheel module overlaps the battery's fences")

    screws = {
        "wheel module": f"{wm.screws['foot']}; {wm.screws['beam']}",
        "caster": f"4 x {cupd.screw} (caster to cup)",
        "cup": f"4 x {cupd.mount_screw} (cup to plate, from under the plate)",
    }
    return BasePlateDerived(
        x_back_mm=x0,
        x_front_mm=x1,
        half_width_mm=half,
        thickness_mm=t,
        measured=p.strap_width_mm is not None,
        wheel_holes=wheel_holes,
        wheel_footprint=feet,
        caster_xy=(cx, 0.0),
        cup=cupd,
        cup_holes=cup_holes,
        battery_box=battery_box,
        strap_slots=slots,
        grid_holes=grid,
        front_holes=front,
        cliff_windows=cliffs,
        screws=screws,
    )


def cradle_to_plate(case: Case, horn: Horn, cradle: Cradle, layout: BaseLayout, side: int):
    """The map from the cradle's frame (a, b, c) to the plate's (x, y, z), for side +1 or -1.

    Returns (rotation as three column vectors, translation). The foot face (b = -b_outer) lands
    on the plate's top face; the back face (c = -wall - pad) at y = +-cradle_back.
    """
    base = derive_base(case, horn, cradle, layout)
    cd = derive_cradle(case, horn, cradle)
    back = -(cradle.wall_mm + cradle.pad_mm)
    s = 1 if side > 0 else -1
    # a -> -s x, b -> z, c -> s y: a proper rotation for both sides (side -1 is side +1 turned
    # half a turn about z).
    cols = ((-s, 0, 0), (0, 0, 1), (0, s, 0))
    shift = (0.0, s * (base.cradle_back_y_mm - back), PLATE_MM + cd.b_outer_mm)
    return cols, shift


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


# Electronics deck (DECK.md). M2.5 hardware comes from the HanTof standoff kit (inventory row 5):
# brass standoffs with a 5 or 6 mm male stud, M2.5 x 5 screws and M2.5 hex nuts.
M25_NUT_AF_MM = 5.0  # across flats (ISO 4032)
M25_NUT_MM = 2.0
M25_STUD_MM = 6.0  # the 11 and 20 mm standoffs' male stud
ROCKER_CUTOUT_MM = (19.2, 13.2)  # DaierTek KCD1-101 (Daier sheet), long x short
JACK_THREAD_MM = 11.4  # charge jack's threaded tube, owner's caliper on the kit socket (DECK.md)
UCTRONICS_MM = (63.5, 27.3, 10.0)  # 5 V buck, long x wide x tall (owner's caliper 2026-11-23)


@dataclass(frozen=True)
class DeckCoupon:
    """One flat print that checks the deck's new fits before the real parts: two rocker cutouts,
    three jack holes, an M2.5 boss with a nut pocket underneath, and a short channel at the
    UCTRONICS's width. Frame: x along the coupon, y across, z up from the bed (plate underside).
    """

    length_mm: float = 96.0
    width_mm: float = 45.0
    panel_mm: float = 2.0  # the rocker's clips and the jack's nut both take a thin panel
    rocker_play_mm: tuple[float, float] = (0.2, 0.5)  # added to each side length: snug, loose
    jack_holes_mm: tuple[float, float, float] = (8.2, 8.4, 8.6)
    nut_clearance_mm: float = 0.2  # per side round the hex nut (PETG slip fit, printing.md)
    boss_mm: float = 9.0  # boss diameter
    # Per side round the UCTRONICS's width: 27.6 mm inside, which the coupon proved (a tiny bit
    # of play on the measured 27.3 mm board).
    channel_play_mm: float = 0.15
    channel_wall_mm: float = 1.6
    channel_height_mm: float = 8.0  # above the panel
    channel_length_mm: float = 20.0


@dataclass(frozen=True)
class DeckCouponDerived:
    rockers: tuple[tuple[float, float, float, float], ...]  # x, y centre; long, short side
    jacks: tuple[tuple[float, float, float], ...]  # x, y, diameter
    boss_xy: tuple[float, float]
    boss_height_mm: float
    nut_pocket_af_mm: float
    nut_pocket_depth_mm: float  # from the bed up
    stud_hole_mm: float
    channel_inner_mm: float
    channel_x_mm: tuple[float, float]


def derive_deck_coupon(c: DeckCoupon) -> DeckCouponDerived:
    """Places every feature and checks the M2.5 stack: a standoff's stud must reach through the
    boss into the nut, but its tip must stop short of the bed (in the deck, the base plate)."""
    w = c.width_mm
    rockers = tuple(
        (15.0, y, ROCKER_CUTOUT_MM[0] + p, ROCKER_CUTOUT_MM[1] + p)
        for y, p in zip((w * 0.25, w * 0.75), c.rocker_play_mm, strict=True)
    )
    jacks = tuple((38.0, w * f, d) for f, d in zip((0.2, 0.5, 0.8), c.jack_holes_mm, strict=True))
    # The nut is pulled up against the pocket's roof, so the stud engages it from the roof down.
    # Pocket depth = nut + room for the stud's tip; boss height = roof + pocket depth, where the
    # roof (stud length less the nut) keeps the tip clear of the bed.
    tip_room = 1.0
    depth = M25_NUT_MM + tip_room
    roof = M25_STUD_MM - M25_NUT_MM
    height = depth + roof
    if roof < 2.0:
        raise ValueError("the boss's roof over the nut is under 2 mm: too weak")
    inner = UCTRONICS_MM[1] + 2 * c.channel_play_mm
    x0 = c.length_mm - c.channel_length_mm - 4.0
    if x0 < 56.0 + c.boss_mm / 2 + 2.0:
        raise ValueError("the channel runs into the boss")
    if inner + 2 * c.channel_wall_mm > w:
        raise ValueError("the channel is wider than the coupon")
    return DeckCouponDerived(
        rockers=rockers,
        jacks=jacks,
        boss_xy=(56.0, w / 2),
        boss_height_mm=height,
        nut_pocket_af_mm=M25_NUT_AF_MM + 2 * c.nut_clearance_mm,
        nut_pocket_depth_mm=depth,
        stud_hole_mm=CLEARANCE_MM["M2.5"],
        channel_inner_mm=inner,
        channel_x_mm=(x0, x0 + c.channel_length_mm),
    )


# The electronics deck itself (DECK.md, "Parts to model"): a compute tray (left), a bridge over the
# caster cup for the servo board (centre back) and a power tray with the switch panel (right).
# Frame: the base plate's, x fore-aft (+ forward, axle at 0), y across (+ is the robot's left),
# z up from the base plate's TOP face. Every part bolts to the plate's M3 grid with M3 screws up
# from under the plate and nuts on top. `derive_deck` places every part, component, plug and
# screw as boxes and raises on any clash.
KIT_M3_MM = (8, 12, 16, 20)  # Mywish kit lengths
M3_NUT_AF_MM = 5.5  # across flats (ISO 4032)
M4_NUT_MM = 3.2
NUT_ROOM_MM = 4.0  # radius kept free round a nut on top of a part: the nut (3.2) and fingers
CUP_MIN_AIR_MM = 0.5  # least air any deck part keeps over the cup's nuts and tips
STRAP_KEEP_MM = 3.5  # deck parts stay this far behind the rear strap slots (x <= -84)
BATTERY_KEEP_MM = 4.0  # and this far behind the battery's back fences (x <= -80)
PI_BOARD_MM = 1.6
PI_UNDERSIDE_MM = 2.0  # through-hole pins and parts under a board
CHARGE_JACK_HOLE_MM = JACK_THREAD_MM + 1.0  # 12.4: prints about 12.1 (DECK.md)
PLATE_EDGE_KEEP_MM = 1.0  # the rocker's paddle stays this far inside the plate's back edge


def kit_screw(stack_mm: float, what: str) -> int:
    """Shortest kit M3 that passes `stack_mm` of plate and plastic and still has three threads
    (1.5 mm) in the nut, the rule the caster cup uses. Raises ValueError naming the joint."""
    need = stack_mm + M3_MIN_ENGAGE_MM
    for n in KIT_M3_MM:
        if n >= need - 1e-9:
            return n
    raise ValueError(f"{what}: needs an M3 of {need:.1f} mm, longer than the kit's 20 mm")


Rect = tuple[float, float, float, float]  # x0, x1, y0, y1 in plan


@dataclass(frozen=True)
class Box:
    """An axis-aligned box in the plate frame. `kind` is "part" (printed plastic), "component"
    (a board or body), "reach" (room a plug, lead or terminal needs) or "hardware" (a nut on top
    and the screw's tip). `owner` is the printed part or the component it belongs to."""

    name: str
    owner: str
    kind: str
    x0: float
    x1: float
    y0: float
    y1: float
    z0: float
    z1: float

    def plan(self) -> Rect:
        return (self.x0, self.x1, self.y0, self.y1)

    def overlaps(self, o: Box) -> bool:
        """True if the boxes share volume; boxes that only touch do not."""
        tol = 1e-6
        return (
            self.x0 < o.x1 - tol
            and o.x0 < self.x1 - tol
            and self.y0 < o.y1 - tol
            and o.y0 < self.y1 - tol
            and self.z0 < o.z1 - tol
            and o.z0 < self.z1 - tol
        )


def _box(name: str, owner: str, kind: str, r: Rect, z0: float, z1: float) -> Box:
    return Box(name, owner, kind, min(r[0], r[1]), max(r[0], r[1]), r[2], r[3], z0, z1)


def _around(x: float, y: float, r: float) -> Rect:
    return (x - r, x + r, y - r, y + r)


@dataclass(frozen=True)
class TiePoint:
    """A zip tie's anchor: two slots through a floor and a groove under the floor joining them,
    so the tie runs under the floor (which sits on the base plate) and round the component."""

    slots: tuple[Rect, Rect]
    groove: Rect
    groove_mm: float  # depth, from the floor's underside


TIE_SLOT_MM = (2.0, 4.5)  # across the tie (its thickness) x along it (its width: ties up to 3.6)
TIE_GROOVE_MM = 1.5


def _tie(a: float, b: float, at: float, along_x: bool) -> TiePoint:
    """Slots centred at a and b (on the tie's path), at `at` on the other axis. along_x: the tie's
    path runs in x (its slots are thin in x)."""
    t, w = TIE_SLOT_MM
    lo, hi = sorted((a, b))
    if along_x:
        s1 = (lo - t / 2, lo + t / 2, at - w / 2, at + w / 2)
        s2 = (hi - t / 2, hi + t / 2, at - w / 2, at + w / 2)
        groove = (lo - t / 2, hi + t / 2, at - w / 2, at + w / 2)
    else:
        s1 = (at - w / 2, at + w / 2, lo - t / 2, lo + t / 2)
        s2 = (at - w / 2, at + w / 2, hi - t / 2, hi + t / 2)
        groove = (at - w / 2, at + w / 2, lo - t / 2, hi + t / 2)
    return TiePoint(slots=(s1, s2), groove=groove, groove_mm=TIE_GROOVE_MM)


@dataclass(frozen=True)
class Deck:
    """Design choices and component facts for the deck (sources in DECK.md)."""

    floor_mm: float = 3.0  # the trays' floors
    edge_margin_mm: float = 1.0  # printed parts stay this far inside the plate's outline
    cup_clearance_mm: float = 1.0  # air over the caster cup's nuts and screw tips
    hole_margin_mm: float = 1.0  # a grid nut's room stays this far inside its part's floor
    holes_per_part: int = 4

    # Compute tray: the Pi 5 (RP-008347) and the UCTRONICS behind it.
    pi_board: Rect = (-144.0, -88.0, 39.0, 124.0)
    pi_holes_x: tuple[float, float] = (-140.5, -91.5)
    pi_holes_y: tuple[float, float] = (62.5, 120.5)
    pi_standoff_mm: float = 11.0
    pi_tall_mm: float = 16.0  # USB stack above the board's top
    pi_port_overhang_mm: float = 3.0  # USB/Ethernet past the inboard end
    pi_usb_reach: Rect = (-128.0, -92.0, 5.0, 36.0)  # spec: the plugs' lane, kept clear in plan
    pi_power_y_mm: float = 113.0  # USB-C on the back edge
    pi_power_reach_mm: float = 18.0  # a USB-C plug's body behind the back edge
    pi_window: Rect = (-129.0, -101.0, 69.0, 112.0)
    uct_x_mm: float = -165.5  # channel centre: x about -152 to -179 (spec)
    uct_y0_mm: float = 52.5  # input end (inboard); output end at y0 + 63.5
    uct_in_reach_mm: float = 7.0  # screw-terminal leads before they bend
    uct_out_reach_mm: float = 14.0  # the right-angle cable's USB-A head
    uct_wall_inset_mm: float = 4.0  # channel walls stop short of the board's ends (open ends)
    uct_tie_inset_mm: float = 8.0  # zip ties this far in from the board's ends
    uct_window_mm: float = 4.0  # the cradle's floor window stops this far from walls and ties
    cradle_floor_y0_mm: float = 46.0

    # Servo board bridge: Waveshare Bus Servo Adapter (A), 42 x 33 mm, holes 37 x 28.
    servo_xy: tuple[float, float] = (-158.0, 0.0)
    servo_mm: tuple[float, float] = (42.0, 33.0)  # fore-aft x across
    servo_holes_mm: tuple[float, float] = (37.0, 28.0)
    servo_standoff_mm: float = 20.0  # lifts its plugs above the Pi's USB stack (see derive_deck)
    servo_tall_mm: float = 10.0
    servo_overhang_mm: float = 2.0  # USB-C and the jack past the +y edge
    servo_plus_y_reach_mm: float = 28.0  # USB-C or barrel plug, toward the Pi
    servo_minus_y_reach_mm: float = 15.0  # bus servo plugs
    platform_mm: float = 3.0
    # Posts on grid holes clear of the cup. (-135, +40) would stand under the Pi's USB end
    # (2 mm below the board), so the fourth post is (-115, 0) instead.
    posts: tuple[tuple[float, float], ...] = (
        (-175.0, 40.0),
        (-175.0, -40.0),
        (-135.0, -40.0),
        (-115.0, 0.0),
    )
    post_mm: float = 9.5
    post_nut_seat_mm: float = 5.0  # the M3 nut sits on this, at the bottom of a hex well
    platform_window_mm: tuple[float, float] = (24.0, 18.0)

    # Power tray: DROK, INA226, two fuse holders, and the switch panel.
    drok_xy: tuple[float, float] = (-118.0, -100.0)
    drok_mm: tuple[float, float, float] = (57.0, 39.0, 22.0)
    drok_spacing_mm: tuple[float, float] = (54.0, 68.0)  # ear holes, scaled about 61
    drok_ear_mm: tuple[float, float, float] = (1.5, 3.0, 3.5)  # ear thickness: min, design, max
    drok_ear_reach_mm: float = 35.0  # ear tips from the centre (scaled)
    drok_lead_reach_mm: float = 6.0  # potted leads leave the inboard face
    pad_mm: tuple[float, float] = (14.0, 9.0)  # width (y), height
    pad_inner_mm: float = 22.0  # pads run from here out to the channel's open end
    pad_roof_mm: float = 3.0
    ina_xy: tuple[float, float] = (-161.0, -61.0)
    ina_mm: tuple[float, float, float] = (26.0, 22.0, 14.0)  # GODIYMODULES, long x across
    ina_pocket_mm: tuple[float, float] = (27.0, 23.0)
    ina_wall_mm: tuple[float, float] = (5.0, 1.5)  # long walls, end stops (catch the PCB)
    ina_reach_mm: float = 10.0  # terminals (+x end) and I2C header (-x end)
    ina_tie_x_mm: tuple[float, float] = (-154.0, -164.0)
    fuse_axes_y_mm: tuple[float, float] = (-44.0, -61.0)  # main 10 A, servo rail 5 A
    fuse_x_mm: tuple[float, float] = (-124.0, -84.0)
    fuse_mm: float = 15.0  # round body (DECK.md); its length is assumed 40 (Low)
    fuse_tie_x_mm: tuple[float, float] = (-92.0, -116.0)
    # Its back face: far enough in that the rocker's paddle (rocker_front_mm) stays 1 mm inside
    # the plate's back edge, so the plate takes the knocks.
    panel_x_mm: float = -179.0
    panel_mm: float = 2.0  # the coupon's
    panel_y_mm: tuple[float, float] = (-124.5, -74.5)
    panel_top_mm: float = 28.0
    gusset_mm: tuple[float, float] = (2.0, 10.0)  # thickness, reach behind the panel
    rocker_y_mm: float = -115.0  # outboard of the DROK's back pad and ear (y -93 to -107)
    jack_y_mm: float = -84.5  # inboard of them
    switch_z_mm: float = 14.5  # centres of the rocker and the jack
    rocker_bezel_mm: tuple[float, float] = (15.0, 21.0)  # across, tall
    rocker_body_mm: tuple[float, float, float] = (13.4, 18.7, 21.4)  # with clips, tall, deep
    rocker_crimp_mm: float = 6.0  # 4.8 mm spade crimps on its tabs
    rocker_front_mm: float = 10.0  # bezel and paddle in front of the panel: assumed at most
    jack_body_mm: tuple[float, float] = (16.0, 25.0)  # collar diameter, depth with leads (Low)
    jack_front_mm: float = 3.0  # its nut, in front
    power_floor: tuple[Rect, ...] = (
        (-128.5, -84.0, -110.0, -35.0),  # fuses and the DROK's front half
        (-179.0, -128.5, -110.0, -46.0),  # the DROK's back half, the INA226, the panel
        (-169.5, -141.0, -110.0, -44.9),  # under the INA226's tie slots, between the posts
        (-84.0, -80.8, -110.0, -74.0),  # the DROK's front pad
        (-179.0, -140.0, -125.0, -110.0),  # the panel's far end
    )


@dataclass(frozen=True)
class ComputeTrayDerived:
    floor: tuple[Rect, ...]
    windows: tuple[Rect, ...]
    bosses: tuple[tuple[float, float], ...]
    walls: tuple[Box, ...]
    ties: tuple[TiePoint, ...]
    holes: tuple[tuple[float, float], ...]
    screw_mm: int


@dataclass(frozen=True)
class BridgeDerived:
    platform: Rect
    window: Rect
    arms: tuple[Rect, ...]
    platform_z_mm: tuple[float, float]
    bosses: tuple[tuple[float, float], ...]
    boss_bottom_mm: float
    posts: tuple[tuple[float, float], ...]
    post_mm: float
    nut_seat_mm: float
    well_af_mm: float
    screw_mm: int


@dataclass(frozen=True)
class Pad:
    pad: Rect
    slot: Rect  # the ear screw's slot through the roof
    channel: Rect  # hex channel in the underside, open at the pad's outer end
    channel_mm: float  # depth from the tray's underside
    top_mm: float


@dataclass(frozen=True)
class PowerTrayDerived:
    floor: tuple[Rect, ...]
    pads: tuple[Pad, Pad]
    channel_af_mm: float
    pocket_walls: tuple[Box, ...]
    ties: tuple[TiePoint, ...]
    panel: Box
    gussets: tuple[Box, ...]
    rocker_cutout: tuple[float, float, float, float]  # y, z centre; across, tall
    jack_hole: tuple[float, float, float]  # y, z centre; diameter
    holes: tuple[tuple[float, float], ...]
    screw_mm: int
    ear_screw_mm: int


@dataclass(frozen=True)
class DeckDerived:
    compute: ComputeTrayDerived
    bridge: BridgeDerived
    power: PowerTrayDerived
    coupon: DeckCouponDerived
    floor_mm: float
    boxes: tuple[Box, ...]
    cup_reach_mm: float
    rocker_inside_mm: float  # the rocker's paddle tip to the plate's back edge
    fasteners: dict[str, int]


def _in_plate(x: float, y: float, plate: BasePlateDerived, radius: float, margin: float) -> bool:
    x0, x1, h = plate.x_back_mm, plate.x_front_mm, plate.half_width_mm
    tol = 1e-6
    if not (x0 + margin - tol <= x <= x1 - margin + tol and abs(y) <= h - margin + tol):
        return False
    cx = min(max(x, x0 + radius), x1 - radius)
    cy = min(max(y, -h + radius), h - radius)
    return math.hypot(x - cx, y - cy) <= radius - margin + tol


def _dist_to_rect(x: float, y: float, r: Rect) -> float:
    dx = max(r[0] - x, 0.0, x - r[1])
    dy = max(r[2] - y, 0.0, y - r[3])
    return math.hypot(dx, dy)


def _hull_area(pts: tuple[tuple[float, float], ...]) -> float:
    ps = sorted(pts)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list[tuple[float, float]] = []
    upper: list[tuple[float, float]] = []
    for p in ps:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(ps):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]
    n = len(hull)
    return (
        abs(
            sum(
                hull[i][0] * hull[(i + 1) % n][1] - hull[(i + 1) % n][0] * hull[i][1]
                for i in range(n)
            )
        )
        / 2
    )


def _pick_holes(
    part: str,
    grid: tuple[tuple[float, float], ...],
    taken: set[tuple[float, float]],
    floor: tuple[Rect, ...],
    keep_free: tuple[Rect, ...],
    floor_mm: float,
    tip_mm: float,
    obstacles: list[Box],
    d: Deck,
) -> tuple[tuple[tuple[float, float], ...], list[Box]]:
    """The grid holes a part bolts down with: holes well inside its floor, clear of its cuts, whose
    nut and screw tip hit nothing; of those, the `holes_per_part` spread widest."""
    cands: list[tuple[float, float]] = []
    for x, y in grid:
        if (x, y) in taken:
            continue
        room = NUT_ROOM_MM + d.hole_margin_mm
        if not any(
            r[0] + room <= x <= r[1] - room and r[2] + room <= y <= r[3] - room for r in floor
        ):
            continue
        if any(_dist_to_rect(x, y, r) < NUT_ROOM_MM + d.hole_margin_mm for r in keep_free):
            continue
        hw = _box(
            f"{part} nut at ({x:.0f}, {y:.0f})",
            part,
            "hardware",
            _around(x, y, NUT_ROOM_MM),
            floor_mm,
            tip_mm,
        )
        if any(hw.overlaps(o) for o in obstacles):
            continue
        cands.append((x, y))
    if len(cands) < d.holes_per_part:
        raise ValueError(
            f"the {part} finds only {len(cands)} free grid holes, needs {d.holes_per_part}"
        )
    best = max(
        itertools.combinations(sorted(cands), d.holes_per_part),
        key=lambda c: (round(_hull_area(c), 6), c),
    )
    hw = [
        _box(
            f"{part} nut at ({x:.0f}, {y:.0f})",
            part,
            "hardware",
            _around(x, y, NUT_ROOM_MM),
            floor_mm,
            tip_mm,
        )
        for x, y in best
    ]
    return best, hw


def derive_deck(
    plate: BasePlateDerived,
    d: Deck | None = None,
    base: BasePlate | None = None,
    cup: CasterCup | None = None,
) -> DeckDerived:
    """Places the four deck parts on the base plate (`derive_base_plate`, as build.py makes it)
    and raises ValueError naming whatever collides: two footprints, a plug's reach, a shared grid
    hole, the strap slots, the caster cup, the battery or the plate's edges."""
    d = d or Deck()
    base = base or BasePlate()
    cup = cup or CasterCup()
    co = derive_deck_coupon(DeckCoupon())
    cc = DeckCoupon()
    t = d.floor_mm
    boxes: list[Box] = []

    # --- The caster cup: its radius with the bosses, and its height with nuts and tips. ---
    cx, cy = plate.caster_xy
    cup_r = cup.boss_at_mm + cup.boss_mm / 2
    h = plate.cup.height_mm
    cup_screw = kit_screw(PLATE_MM + h, "cup to plate")  # as derive_caster_cup picks it
    caster_plate = 3.0  # the caster's plate under the roof (derive_caster_cup)
    m4 = next(n for n in KIT_M3_MM if n >= caster_plate + cup.roof_mm + M4_MIN_ENGAGE_MM)
    cup_reach = max(
        h + M3_NUT_MM,  # the cup's own nuts on its bosses
        cup_screw - PLATE_MM,  # their tips
        h + M4_NUT_MM,  # the caster's nuts on the roof
        h + m4 - caster_plate - cup.roof_mm,  # their tips
    )

    # --- Compute tray ---
    ct = "compute tray"
    px0, px1, py0, py1 = d.pi_board
    pi_bottom = co.boss_height_mm + d.pi_standoff_mm
    bosses = tuple((x, y) for x in d.pi_holes_x for y in d.pi_holes_y)
    for x, y in bosses:
        if _dist_to_rect(x, y, (px0 + 3.5, px1 - 3.5, py0 + 3.5, py1 - 3.5)) > 1e-6:
            raise ValueError(f"Pi hole ({x}, {y}) is not 3.5 mm inside the board (RP-008347)")
    boxes += [
        _box(f"Pi boss ({x}, {y})", ct, "part", _around(x, y, cc.boss_mm / 2), 0, co.boss_height_mm)
        for x, y in bosses
    ]
    boxes.append(
        _box(
            "Pi 5",
            "Pi 5",
            "component",
            (px0, px1, py0 - d.pi_port_overhang_mm, py1),
            pi_bottom - PI_UNDERSIDE_MM,
            pi_bottom + PI_BOARD_MM + d.pi_tall_mm,
        )
    )
    # The plugs' lane, from under the board (cables sag) to above the USB stack. Below it the lane
    # passes over the caster cup's keep-out, which is fine: the cup is 12 mm tall.
    boxes.append(
        _box(
            "Pi USB plugs",
            "Pi 5",
            "reach",
            d.pi_usb_reach,
            pi_bottom - 4.0,
            pi_bottom + PI_BOARD_MM + d.pi_tall_mm + 4.0,
        )
    )
    boxes.append(
        _box(
            "Pi USB-C power plug",
            "Pi 5",
            "reach",
            (px0 - d.pi_power_reach_mm, px0, d.pi_power_y_mm - 8, d.pi_power_y_mm + 8),
            pi_bottom,
            pi_bottom + PI_BOARD_MM + 8.0,
        )
    )
    ul, uw, uh = UCTRONICS_MM
    inner = co.channel_inner_mm
    if inner < uw:
        raise ValueError("the UCTRONICS channel is narrower than the board")
    ux0, ux1 = d.uct_x_mm - uw / 2, d.uct_x_mm + uw / 2
    uy0, uy1 = d.uct_y0_mm, d.uct_y0_mm + ul
    boxes.append(_box("UCTRONICS", "UCTRONICS", "component", (ux0, ux1, uy0, uy1), t, t + uh))
    boxes.append(
        _box(
            "UCTRONICS input leads",
            "UCTRONICS",
            "reach",
            (ux0, ux1, uy0 - d.uct_in_reach_mm, uy0),
            t,
            t + uh,
        )
    )
    boxes.append(
        _box(
            "UCTRONICS USB-A plug",
            "UCTRONICS",
            "reach",
            (ux0, ux1, uy1, uy1 + d.uct_out_reach_mm),
            t,
            t + uh,
        )
    )
    wi = (d.uct_x_mm - inner / 2, d.uct_x_mm + inner / 2)
    ww = cc.channel_wall_mm
    wy = (uy0 + d.uct_wall_inset_mm, uy1 - d.uct_wall_inset_mm)
    walls = (
        _box(
            "UCTRONICS wall (back)",
            ct,
            "part",
            (wi[0] - ww, wi[0], *wy),
            t,
            t + cc.channel_height_mm,
        ),
        _box(
            "UCTRONICS wall (front)",
            ct,
            "part",
            (wi[1], wi[1] + ww, *wy),
            t,
            t + cc.channel_height_mm,
        ),
    )
    boxes += walls
    st = TIE_SLOT_MM[0]
    a, b = wi[0] - ww - st / 2, wi[1] + ww + st / 2
    uties = tuple(
        _tie(a, b, y, along_x=True) for y in (uy0 + d.uct_tie_inset_mm, uy1 - d.uct_tie_inset_mm)
    )
    floor_c = (
        (
            px0 - 2.0,
            px1 + 2.0,
            min(d.pi_holes_y) - cc.boss_mm / 2 - 1.5,
            max(d.pi_holes_y) + cc.boss_mm / 2 + 2.0,
        ),
        (
            a - st / 2 - 1.5,
            px0 - 2.0,
            d.cradle_floor_y0_mm,
            max(d.pi_holes_y) + cc.boss_mm / 2 + 2.0,
        ),
    )
    boxes += [_box(f"compute tray floor {i}", ct, "part", r, 0, t) for i, r in enumerate(floor_c)]
    g0, g1 = uties[0].groove, uties[1].groove
    uct_window = (
        wi[0] + d.uct_window_mm,
        wi[1] - d.uct_window_mm,
        g0[3] + d.uct_window_mm,
        g1[2] - d.uct_window_mm,
    )
    if uct_window[3] - uct_window[2] < 10.0:
        raise ValueError("the UCTRONICS ties are too close together for a floor window")
    for w in (d.pi_window, uct_window):
        if not any(r[0] < w[0] and w[1] < r[1] and r[2] < w[2] and w[3] < r[3] for r in floor_c):
            raise ValueError(f"window {w} is not inside the compute tray's floor")
    for x, y in bosses:
        if any(_dist_to_rect(x, y, w) < cc.boss_mm / 2 + 1.0 for w in (d.pi_window,)):
            raise ValueError(f"the Pi window cuts the boss at ({x}, {y})")

    # --- Servo board bridge ---
    br = "servo bridge"
    sx, sy = d.servo_xy
    sl, sw = d.servo_mm
    hx, hy = d.servo_holes_mm[0] / 2, d.servo_holes_mm[1] / 2
    sbosses = tuple((sx + i * hx, sy + j * hy) for i in (-1, 1) for j in (-1, 1))
    boss_bottom = cup_reach + d.cup_clearance_mm
    top = boss_bottom + co.boss_height_mm
    if top < 15.0:
        raise ValueError("the bridge's platform must stand at least 15 mm (DECK.md)")
    under = top - d.platform_mm
    if under - boss_bottom < co.nut_pocket_depth_mm - 1e-6:
        raise ValueError("the platform is thicker than the boss's roof: the nut pocket closes")
    br_r = cc.boss_mm / 2 + 1.0
    platform = (sx - hx - br_r, sx + hx + br_r, sy - hy - br_r + 0.5, sy + hy + br_r - 0.5)
    wx, wy_ = d.platform_window_mm
    window = (sx - wx / 2, sx + wx / 2, sy - wy_ / 2, sy + wy_ / 2)
    for x, y in sbosses:
        if _dist_to_rect(x, y, window) < cc.boss_mm / 2 + 1.0:
            raise ValueError("the platform's window cuts a boss")
    boxes.append(_box("bridge platform", br, "part", platform, under, top))
    boxes += [
        _box(
            f"bridge boss ({x:.1f}, {y:.1f})",
            br,
            "part",
            _around(x, y, cc.boss_mm / 2),
            boss_bottom,
            top,
        )
        for x, y in sbosses
    ]
    pr = d.post_mm / 2
    well_af = M3_NUT_AF_MM + 2 * cc.nut_clearance_mm
    if pr - well_af / math.sqrt(3) < 1.2:
        raise ValueError("the posts' walls round the nut wells are under 1.2 mm")
    grid = set(plate.grid_holes)
    arms: list[Rect] = []
    for x, y in d.posts:
        if (x, y) not in grid:
            raise ValueError(f"bridge post ({x}, {y}) is not on a grid hole")
        if math.hypot(x - cx, y - cy) - pr < cup_r - 1e-6:
            raise ValueError(f"bridge post ({x}, {y}) stands on the caster cup")
        boxes.append(_box(f"bridge post ({x:.0f}, {y:.0f})", br, "part", _around(x, y, pr), 0, top))
        if platform[0] <= x <= platform[1]:
            q = min(max(y, platform[2]), platform[3])
            arms.append((x - pr, x + pr, min(y, q), max(y, q)))
        elif platform[2] <= y <= platform[3]:
            q = min(max(x, platform[0]), platform[1])
            arms.append((min(x, q), max(x, q), y - pr, y + pr))
        else:
            raise ValueError(f"bridge post ({x}, {y}) is off the platform's axes: no straight arm")
    boxes += [_box(f"bridge arm {i}", br, "part", r, under, top) for i, r in enumerate(arms)]
    post_screw = kit_screw(PLATE_MM + d.post_nut_seat_mm, "bridge posts")
    if post_screw - PLATE_MM > top:
        raise ValueError("the bridge posts' screws stand out of the wells")
    s_bottom = top + d.servo_standoff_mm
    s_rect = (sx - sl / 2, sx + sl / 2, sy - sw / 2, sy + sw / 2 + d.servo_overhang_mm)
    s_z = (s_bottom - PI_UNDERSIDE_MM, s_bottom + PI_BOARD_MM + d.servo_tall_mm)
    boxes.append(_box("servo board", "servo board", "component", s_rect, *s_z))
    boxes.append(
        _box(
            "servo board USB-C and 12 V",
            "servo board",
            "reach",
            (s_rect[0], s_rect[1], s_rect[3], s_rect[3] + d.servo_plus_y_reach_mm),
            s_z[0],
            s_z[1] + 2.0,
        )
    )
    boxes.append(
        _box(
            "servo bus plugs",
            "servo board",
            "reach",
            (s_rect[0], s_rect[1], s_rect[2] - d.servo_minus_y_reach_mm, s_rect[2]),
            s_z[0],
            s_z[1],
        )
    )

    # --- Power tray and switch panel ---
    pw = "power tray"
    dx_, dy_ = d.drok_xy
    dl, dw, dh = d.drok_mm
    pad_w, pad_top = d.pad_mm
    s_lo, s_hi = d.drok_spacing_mm[0] / 2, d.drok_spacing_mm[1] / 2
    e_min, e_design, e_max = d.drok_ear_mm
    ear_screw = kit_screw(e_design + d.pad_roof_mm, "DROK ears")
    if ear_screw - e_max - d.pad_roof_mm < M3_MIN_ENGAGE_MM - 1e-6:
        raise ValueError("the DROK's ear screw is short for its thickest ear")
    channel = pad_top - d.pad_roof_mm
    if pad_top + e_min - ear_screw < 0.5:
        raise ValueError("the DROK's ear screw reaches the base plate under its thinnest ear")
    if channel < M3_NUT_MM + 0.5:
        raise ValueError("the DROK pads' nut channels are shallower than a nut")
    pads: list[Pad] = []
    nut_r = well_af / math.sqrt(3)
    r3 = CLEARANCE_MM["M3"] / 2
    for s in (1, -1):
        outer = s_hi + r3 + 1.5
        pad = (dx_ + s * d.pad_inner_mm, dx_ + s * outer, dy_ - pad_w / 2, dy_ + pad_w / 2)
        slot = (dx_ + s * (s_lo - r3), dx_ + s * (s_hi + r3), dy_ - r3, dy_ + r3)
        ch = (
            dx_ + s * (s_lo - nut_r),
            dx_ + s * (outer + 1.0),
            dy_ - well_af / 2,
            dy_ + well_af / 2,
        )
        if s * (dx_ + s * (s_lo - nut_r)) <= s * (dx_ + s * d.pad_inner_mm):
            raise ValueError("the DROK pad's nut channel runs past the pad's inner end")
        pad, slot, ch = ((min(r[0], r[1]), max(r[0], r[1]), r[2], r[3]) for r in (pad, slot, ch))
        pads.append(Pad(pad=pad, slot=slot, channel=ch, channel_mm=channel, top_mm=pad_top))
        boxes.append(
            _box(f"DROK pad ({'front' if s > 0 else 'back'})", pw, "part", pad, 0, pad_top)
        )
    boxes.append(
        _box(
            "DROK",
            "DROK",
            "component",
            (dx_ - dl / 2, dx_ + dl / 2, dy_ - dw / 2, dy_ + dw / 2),
            pad_top,
            pad_top + dh,
        )
    )
    boxes += [
        _box(
            f"DROK ear ({'front' if s > 0 else 'back'})",
            "DROK",
            "component",
            (
                min(dx_ + s * dl / 2, dx_ + s * d.drok_ear_reach_mm),
                max(dx_ + s * dl / 2, dx_ + s * d.drok_ear_reach_mm),
                dy_ - pad_w / 2,
                dy_ + pad_w / 2,
            ),
            pad_top,
            pad_top + e_max,
        )
        for s in (1, -1)
    ]
    boxes.append(
        _box(
            "DROK leads",
            "DROK",
            "reach",
            (dx_ - dl / 2, dx_ + dl / 2, dy_ + dw / 2, dy_ + dw / 2 + d.drok_lead_reach_mm),
            pad_top,
            pad_top + dh,
        )
    )

    ix, iy = d.ina_xy
    il, iw, ih = d.ina_mm
    ipl, ipw = d.ina_pocket_mm
    if ipl < il or ipw < iw:
        raise ValueError("the INA226 pocket is smaller than the board")
    lw, ew = d.ina_wall_mm
    pin = (ix - ipl / 2, ix + ipl / 2, iy - ipw / 2, iy + ipw / 2)
    pocket = (
        _box("INA226 wall (+y)", pw, "part", (pin[0], pin[1], pin[3], pin[3] + ww), t, t + lw),
        _box("INA226 wall (-y)", pw, "part", (pin[0], pin[1], pin[2] - ww, pin[2]), t, t + lw),
        _box("INA226 stop (+x)", pw, "part", (pin[1], pin[1] + ww, pin[2], pin[3]), t, t + ew),
        _box("INA226 stop (-x)", pw, "part", (pin[0] - ww, pin[0], pin[2], pin[3]), t, t + ew),
    )
    boxes += pocket
    ina = (ix - il / 2, ix + il / 2, iy - iw / 2, iy + iw / 2)
    boxes.append(_box("INA226", "INA226", "component", ina, t, t + ih))
    zr = (t + ew + 0.1, t + ih)  # wires and plugs pass over the end stops
    boxes.append(
        _box(
            "INA226 terminals",
            "INA226",
            "reach",
            (ina[1], ina[1] + d.ina_reach_mm, ina[2], ina[3]),
            *zr,
        )
    )
    boxes.append(
        _box(
            "INA226 I2C header",
            "INA226",
            "reach",
            (ina[0] - d.ina_reach_mm, ina[0], ina[2], ina[3]),
            *zr,
        )
    )
    ina_ties = tuple(
        _tie(pin[2] - ww - st / 2, pin[3] + ww + st / 2, x, along_x=False) for x in d.ina_tie_x_mm
    )
    fuses = tuple(
        _box(
            f"fuse holder ({'main' if i == 0 else 'servo'})",
            f"fuse {i + 1}",
            "component",
            (d.fuse_x_mm[0], d.fuse_x_mm[1], y - d.fuse_mm / 2, y + d.fuse_mm / 2),
            t,
            t + d.fuse_mm,
        )
        for i, y in enumerate(d.fuse_axes_y_mm)
    )
    boxes += fuses
    fuse_ties = tuple(
        _tie(y - 4.5, y + 4.5, x, along_x=False) for y in d.fuse_axes_y_mm for x in d.fuse_tie_x_mm
    )

    p_in = d.panel_x_mm + d.panel_mm
    panel = _box("switch panel", pw, "part", (d.panel_x_mm, p_in, *d.panel_y_mm), 0, d.panel_top_mm)
    gt, gr = d.gusset_mm
    gussets = (
        _box(
            "panel gusset (+y)",
            pw,
            "part",
            (p_in, p_in + gr, d.panel_y_mm[1] - gt, d.panel_y_mm[1]),
            t,
            d.panel_top_mm,
        ),
        _box(
            "panel gusset (-y)",
            pw,
            "part",
            (p_in, p_in + gr, d.panel_y_mm[0], d.panel_y_mm[0] + gt),
            t,
            d.panel_top_mm,
        ),
    )
    boxes += [panel, *gussets]
    zc = d.switch_z_mm
    ra, rt, rd = d.rocker_body_mm
    ba, bt = d.rocker_bezel_mm
    boxes.append(
        _box(
            "rocker",
            "rocker",
            "component",
            (p_in, p_in + rd + d.rocker_crimp_mm, d.rocker_y_mm - ra / 2, d.rocker_y_mm + ra / 2),
            zc - rt / 2,
            zc + rt / 2,
        )
    )
    boxes.append(
        _box(
            "rocker bezel",
            "rocker",
            "component",
            (d.panel_x_mm - 2.0, d.panel_x_mm, d.rocker_y_mm - ba / 2, d.rocker_y_mm + ba / 2),
            zc - bt / 2,
            zc + bt / 2,
        )
    )
    jd, jl = d.jack_body_mm
    boxes.append(
        _box(
            "charge jack",
            "charge jack",
            "component",
            (p_in, p_in + jl, d.jack_y_mm - jd / 2, d.jack_y_mm + jd / 2),
            zc - jd / 2,
            zc + jd / 2,
        )
    )
    boxes.append(
        _box(
            "charge jack nut",
            "charge jack",
            "component",
            (
                d.panel_x_mm - d.jack_front_mm,
                d.panel_x_mm,
                d.jack_y_mm - jd / 2 - 1,
                d.jack_y_mm + jd / 2 + 1,
            ),
            zc - jd / 2 - 1,
            zc + jd / 2 + 1,
        )
    )
    rc = co.rockers[0]  # the snug cutout the coupon proved
    rocker_cut = (d.rocker_y_mm, zc, rc[3], rc[2])  # long side vertical
    if zc - bt / 2 < t + 0.5 or zc + bt / 2 > d.panel_top_mm - 1.5:
        raise ValueError("the rocker's bezel does not fit on the panel")
    if zc - CHARGE_JACK_HOLE_MM / 2 < t + 2.0:
        raise ValueError("the charge jack's hole runs into the floor")
    if abs(d.rocker_y_mm - d.jack_y_mm) < ba / 2 + jd / 2 + 1.0:
        raise ValueError("the rocker and the charge jack are too close on the panel")
    for yy, half in ((d.rocker_y_mm, ba / 2), (d.jack_y_mm, jd / 2)):
        if yy - half < d.panel_y_mm[0] + gt or yy + half > d.panel_y_mm[1] - gt:
            raise ValueError("the rocker or the jack runs off the panel or into a gusset")
    boxes += [
        _box(f"power tray floor {i}", pw, "part", r, 0, t) for i, r in enumerate(d.power_floor)
    ]

    # --- Grid holes: each part takes its own, the bridge's posts first. ---
    taken = set(d.posts)
    floor_screw = kit_screw(PLATE_MM + t, "tray floors")
    tip = max(floor_screw - PLATE_MM, t + M3_NUT_MM)
    others = [
        b for b in boxes if not (b.kind == "part" and b.name.startswith("compute tray floor"))
    ]
    ckeep = (d.pi_window, uct_window, *(tie.groove for tie in uties))
    c_holes, c_hw = _pick_holes(ct, plate.grid_holes, taken, floor_c, ckeep, t, tip, others, d)
    taken |= set(c_holes)
    others = [b for b in boxes if not (b.kind == "part" and b.name.startswith("power tray floor"))]
    pkeep = (
        *(p.channel for p in pads),
        *(tie.groove for tie in (*ina_ties, *fuse_ties)),
    )
    p_holes, p_hw = _pick_holes(
        pw, plate.grid_holes, taken, d.power_floor, pkeep, t, tip, others + c_hw, d
    )
    boxes += c_hw + p_hw
    used = [*d.posts, *c_holes, *p_holes]
    if len(used) != len(set(used)):
        raise ValueError("two deck parts claim one grid hole")

    _check_deck(boxes, plate, base, d, (cx, cy), cup_r, cup_reach)
    for tie in (*uties, *ina_ties, *fuse_ties):
        for s_ in tie.slots:
            floors = floor_c if tie in uties else d.power_floor
            if not any(
                r[0] + 1.0 <= s_[0]
                and s_[1] <= r[1] - 1.0
                and r[2] + 1.0 <= s_[2]
                and s_[3] <= r[3] - 1.0
                for r in floors
            ):
                raise ValueError(f"a zip-tie slot at {s_} runs off its part's floor")
            owner = ct if tie in uties else pw
            for b in boxes:  # the tie must rise straight out of its slot
                if b.owner == owner and b.kind == "part" and b.z0 > 0.0:
                    sb = _box("tie slot", owner, "cut", s_, b.z0, b.z0 + 1.0)
                    if sb.overlaps(b):
                        raise ValueError(f"a zip-tie slot at {s_} is under the {b.name}")

    rocker_inside = d.panel_x_mm - d.rocker_front_mm - plate.x_back_mm
    if rocker_inside < PLATE_EDGE_KEEP_MM - 1e-6:
        raise ValueError(
            f"the rocker's paddle stands {d.rocker_front_mm:.0f} mm proud of the panel: only "
            f"{rocker_inside:.1f} mm inside the plate's back edge (keep {PLATE_EDGE_KEEP_MM:.0f})"
        )
    n_ties = len(uties) + len(ina_ties) + len(fuse_ties)
    fasteners = {
        f"M3 x {floor_screw} (trays to plate)": len(c_holes) + len(p_holes),
        f"M3 x {post_screw} (bridge posts to plate)": len(d.posts),
        f"M3 x {ear_screw} (DROK ears)": 2,
        "M3 nuts": len(c_holes) + len(p_holes) + len(d.posts) + 2,
        f"M2.5 x {d.pi_standoff_mm:.0f} mm standoffs (Pi)": 4,
        f"M2.5 x {d.servo_standoff_mm:.0f} mm standoffs (servo board)": 4,
        "M2.5 nuts": 8,
        "M2.5 x 5 screws": 8,
        "zip ties": n_ties,
    }
    return DeckDerived(
        compute=ComputeTrayDerived(
            floor=floor_c,
            windows=(d.pi_window, uct_window),
            bosses=bosses,
            walls=walls,
            ties=uties,
            holes=c_holes,
            screw_mm=floor_screw,
        ),
        bridge=BridgeDerived(
            platform=platform,
            window=window,
            arms=tuple(arms),
            platform_z_mm=(under, top),
            bosses=sbosses,
            boss_bottom_mm=boss_bottom,
            posts=d.posts,
            post_mm=d.post_mm,
            nut_seat_mm=d.post_nut_seat_mm,
            well_af_mm=well_af,
            screw_mm=post_screw,
        ),
        power=PowerTrayDerived(
            floor=d.power_floor,
            pads=(pads[0], pads[1]),
            channel_af_mm=well_af,
            pocket_walls=pocket,
            ties=(*ina_ties, *fuse_ties),
            panel=panel,
            gussets=gussets,
            rocker_cutout=rocker_cut,
            jack_hole=(d.jack_y_mm, zc, CHARGE_JACK_HOLE_MM),
            holes=p_holes,
            screw_mm=floor_screw,
            ear_screw_mm=ear_screw,
        ),
        coupon=co,
        floor_mm=t,
        boxes=tuple(boxes),
        cup_reach_mm=cup_reach,
        rocker_inside_mm=rocker_inside,
        fasteners=fasteners,
    )


def _check_deck(
    boxes: list[Box],
    plate: BasePlateDerived,
    base: BasePlate,
    d: Deck,
    cup_xy: tuple[float, float],
    cup_r: float,
    cup_reach: float,
) -> None:
    """Every box against the plate's outline, the battery, the strap slots, the caster cup and
    every other box. Raises ValueError naming the first clash."""
    rear = [s for s in plate.strap_slots if s[0] < plate.battery_box[0]]
    strap_x = min(s[0] for s in rear) - STRAP_KEEP_MM
    front = plate.battery_box[0] - base.fence_mm - BATTERY_KEEP_MM
    for b in boxes:
        margin = d.edge_margin_mm if b.kind == "part" else 0.0
        for x in (b.x0, b.x1):
            for y in (b.y0, b.y1):
                if not _in_plate(x, y, plate, base.corner_radius_mm, margin):
                    raise ValueError(f"{b.name} runs off the base plate at ({x:.1f}, {y:.1f})")
        if b.x1 > front + 1e-6:
            raise ValueError(f"{b.name} reaches x {b.x1:.1f}, past the deck's front ({front:.1f})")
        for s in rear:
            if b.x1 > strap_x + 1e-6 and b.y0 < s[3] and s[2] < b.y1:
                raise ValueError(f"{b.name} is in a battery strap's way (keep x <= {strap_x:.1f})")
        over_cup = _dist_to_rect(*cup_xy, b.plan()) < cup_r - 1e-6
        if over_cup and b.z0 < cup_reach + CUP_MIN_AIR_MM - 1e-6:
            raise ValueError(
                f"{b.name} hits the caster cup (radius {cup_r:.0f}, {cup_reach:.0f} mm tall)"
            )
    for i, a in enumerate(boxes):
        for b in boxes[i + 1 :]:
            if a.kind == "reach" and b.kind == "reach":
                continue  # cables may share room
            if a.owner == b.owner and (a.kind == b.kind == "part" or "reach" in (a.kind, b.kind)):
                continue
            if a.owner == b.owner and a.kind == b.kind == "component":
                continue
            if a.overlaps(b):
                raise ValueError(f"{a.name} collides with {b.name}")
