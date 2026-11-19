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

from exp003_cad.hub import full_hub, hub_coupon  # noqa: E402
from exp003_cad.params import Tire, derive, derive_tire, load  # noqa: E402
from exp003_cad.tire import tire  # noqa: E402

PARTS = {"hub_coupon": hub_coupon, "wheel_hub": full_hub, "tire": tire}


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
    t = derive_tire(p, Tire())
    print(
        f"tire: {Tire().od_mm:.0f} mm wheel, bore {t.bore_mm:.1f} mm on the "
        f"{t.rim_seat_od_mm:.1f} mm seat ({t.grip_stretch:.1%} grip), "
        f"stretches {t.mount_stretch:.1%} to pass a flange"
    )
    if not p.measured:
        print("\nservo.toml is still placeholders (measured = false). Do not print these files.")


if __name__ == "__main__":
    main()
