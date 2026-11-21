"""Build exp003's printable parts from servo.toml into cad/out/ (gitignored).

    uv run --no-project --python 3.12 --with cadquery \
        python experiments/exp003-household-robot/cad/build.py

Writes STEP (open this in Bambu Studio: true curves) and STL for each part. While servo.toml
still says measured = false, every file name ends in _UNMEASURED: do not print those.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from exp003_cad.caster_cup import caster_cup  # noqa: E402
from exp003_cad.cradle import cradle  # noqa: E402
from exp003_cad.hub import full_hub, hub_coupon  # noqa: E402
from exp003_cad.params import (  # noqa: E402
    CASTER_CUP_TEST,
    Caster,
    CasterCup,
    Cradle,
    derive,
    derive_caster_cup,
    derive_cradle,
    derive_heights,
    derive_tire,
    load,
    load_case,
    load_tire,
)
from exp003_cad.tire import tire  # noqa: E402

PARTS = {
    "hub_coupon": hub_coupon,
    "wheel_hub": full_hub,
    "tire": lambda p: tire(p, load_tire(HERE / "servo.toml")),
    "servo_cradle": lambda p: cradle(load_case(HERE / "servo.toml"), p.horn),
    "caster_cup": lambda p: caster_cup(Caster(), _heights(p)),
    "caster_cup_test": lambda p: caster_cup(Caster(), _heights(p), CASTER_CUP_TEST),
}


def _heights(p):
    return derive_heights(load_case(HERE / "servo.toml"), p.horn, Cradle(), Caster())


def main() -> None:
    p = load(HERE / "servo.toml")
    d = derive(p)
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    suffix = "" if p.measured else "_UNMEASURED"

    for name, make in PARTS.items():
        part = make(p)
        for ext in ("step", "stl"):
            path = out / f"{name}{suffix}.{ext}"
            if ext == "stl":
                cq.exporters.export(part, str(path), tolerance=0.02, angularTolerance=0.1)
            else:
                cq.exporters.export(part, str(path))
        print(f"{name}: {path.with_suffix('.step').name} and .stl, {part.val().Volume():.0f} mm3")

    step = f", underside stepped up {d.relief_mm:.1f} mm beyond the horn" if d.relief_mm else ""
    print(f"\nweb {d.web_mm:.2f} mm, sits flat on the horn{step}")
    print(f"clears the servo case by {d.case_gap_mm:.1f} mm")
    print(f"screws: {p.horn.bolt_count} x {d.screw} {p.screws.head}-head")
    tire_design = load_tire(HERE / "servo.toml")
    t = derive_tire(p, tire_design)
    print(
        f"tire: {tire_design.od_mm:.0f} mm wheel, bore {t.bore_mm:.1f} mm on the "
        f"{t.rim_seat_od_mm:.1f} mm seat ({t.grip_stretch:.1%} grip), "
        f"stretches {t.mount_stretch:.1%} to pass a flange"
    )
    cr = derive_cradle(load_case(HERE / "servo.toml"), p.horn, Cradle())
    print(
        f"servo cradle: supplied M2 x 6 screws go {cr.screw_depth_mm:.1f} mm into the case; "
        f"wheel axle {cr.axle_above_foot_mm:.1f} mm above the foot"
    )
    h = _heights(p)
    cup = derive_caster_cup(Caster(), h, CasterCup())
    print(
        f"caster cup: {max(cup.outer_mm[0], 2 * cup.outer_radius_mm):.1f} x "
        f"{max(cup.outer_mm[1], 2 * cup.outer_radius_mm):.1f} x {cup.height_mm:.1f} mm, "
        f"fork circle r {cup.sweep_radius_mm:.1f}, "
        f"{cup.depth_mm:.1f} mm deep; plate top {h.plate_top_mm:.1f} mm off the floor; "
        f"4 x {cup.screw}"
    )
    if not p.measured:
        print("\nservo.toml is still placeholders (measured = false). Do not print these files.")


if __name__ == "__main__":
    main()
