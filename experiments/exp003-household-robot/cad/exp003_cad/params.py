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
    caster_x_mm: float = -165.0
    electronics_x_mm: tuple[float, float] = (-80.0, -185.0)  # deck zone behind the battery
    arm_base_x_mm: float = -110.0  # v2: SO-101 base on a top deck
    arm_reach_com_mm: float = 150.0  # the arm's centre of mass ahead of its base at full reach
    arm_kg: float = 1.0
    other: tuple[Mass, ...] = (
        Mass("plate", 0.25, -40.0, "estimate: about 300 x 260 x 4 mm PETG, part infill"),
        Mass("electronics", 0.25, -130.0, "estimate: Pi 5, driver, converters, wiring"),
        Mass("caster", 0.04, -165.0, "estimate"),
    )
    battery_kg: float = 1.07  # inventory figure; the EP1210 sheet says 1.22, so this is the low end
    servo_kg: float = 0.07  # each, with its cradle (estimate)
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
        Mass("battery", b.battery_kg, b.battery_x_mm, "inventory; EP1210 sheet says 1.22"),
        Mass("servos and cradles", 2 * b.servo_kg, -(d.a_min_mm + d.a_max_mm) / 2, "estimate"),
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


# Fit tests only check the caster's plate, holes and fork sweep, so they skimp on plastic.
CASTER_CUP_TEST = CasterCup(wall_mm=1.2, roof_mm=2.0, center_hole_mm=34.0)

M4_NUT_MM = 3.2  # ISO 4032 thickness


@dataclass(frozen=True)
class CasterCupDerived:
    inner_mm: tuple[float, float]  # the box that takes the caster's plate
    outer_mm: tuple[float, float]
    sweep_radius_mm: float  # the round part of the cavity, for the fork
    outer_radius_mm: float
    depth_mm: float  # roof's inner face to the open end: the plate's underside
    height_mm: float
    holes: tuple[tuple[float, float], ...]
    screw: str


def derive_caster_cup(caster: Caster, heights: Heights, c: CasterCup) -> CasterCupDerived:
    inner = (
        caster.plate_long_mm + 2 * c.clearance_mm,
        caster.plate_short_mm + 2 * c.clearance_mm,
    )
    outer = (inner[0] + 2 * c.wall_mm, inner[1] + 2 * c.wall_mm)
    sweep = caster.fork_radius_mm + c.fork_clearance_mm
    hx, hy = caster.holes_long_mm / 2, caster.holes_short_mm / 2
    holes = tuple((sx * hx, sy * hy) for sx in (-1, 1) for sy in (-1, 1))
    if c.center_hole_mm / 2 + c.hole_mm / 2 + 2.0 > (hx**2 + hy**2) ** 0.5:
        raise ValueError("the centre hole runs into the caster's screw holes")
    # Screw: caster plate (about 3 mm) + roof + nut, rounded up to a length in the Mywish kit.
    need = 3.0 + c.roof_mm + M4_NUT_MM
    length = next(n for n in (8, 12, 16, 20) if n >= need)
    return CasterCupDerived(
        inner_mm=inner,
        outer_mm=outer,
        sweep_radius_mm=sweep,
        outer_radius_mm=sweep + c.wall_mm,
        depth_mm=heights.caster_mount_mm,
        height_mm=heights.caster_mount_mm + c.roof_mm,
        holes=holes,
        screw=f"M4 x {length} button head and nut",
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
