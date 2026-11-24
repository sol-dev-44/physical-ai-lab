"""Export the household robot build's numbers for the website's Builds page.

    uv run python experiments/exp003-household-robot/cad/export_site.py

Writes content/builds/household-robot.data.json. Everything comes from the CAD parameters,
servo.toml, the exp003 README (progress log, phases) and docs/inventory.md, so the site cannot
drift from the design: tests/test_exp003_site_data.py fails when the file is stale. No CadQuery
needed; section drawings are computed from the same numbers the models use.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from exp003_cad.params import (  # noqa: E402
    BaseLayout,
    Cradle,
    HubParams,
    derive,
    derive_base,
    derive_cradle,
    derive_tire,
    load,
    load_case,
    load_tire,
    tire_profile,
)

REPO = HERE.parents[2]
EXP = HERE.parent
OUT = REPO / "content" / "builds" / "household-robot.data.json"

# BOM groups for the 2026-11-17 order, by item number in docs/inventory.md.
BOM_GROUPS: dict[int, str] = {
    **dict.fromkeys(range(1, 6), "Compute"),
    **dict.fromkeys((6, 7, 8), "Drive"),
    **dict.fromkeys((9, 10), "Printing"),
    **dict.fromkeys(range(11, 25), "Power"),
    **dict.fromkeys(range(25, 30), "Sensing and wiring"),
    30: "Audio",
    31: "Power",
    32: "Power",
}  # A new row in docs/inventory.md's exp003 order table needs its number here.


def _group(n: int) -> str:
    if n not in BOM_GROUPS:
        raise SystemExit(f"order row {n} has no group: add it to BOM_GROUPS in export_site.py")
    return BOM_GROUPS[n]


def _plain(text: str) -> str:
    """Markdown cell to plain text: drop bold, code ticks and link targets."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.replace("**", "").replace("`", "").strip()


def _tables_after(md: str, heading: str) -> list[list[dict[str, str]]]:
    """Every markdown table between `heading` and the next heading of the same or higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    start = md.index(heading + "\n")
    rest = md[start + len(heading) + 1 :]
    stop = re.search(rf"^#{{1,{level}}} ", rest, re.M)
    section = rest[: stop.start()] if stop else rest
    tables, block = [], []
    for line in [*section.splitlines(), ""]:
        if line.startswith("|"):
            block.append(line)
        elif block:
            header = [_plain(c) for c in block[0].strip("|").split("|")]
            rows = [[_plain(c) for c in r.strip("|").split("|")] for r in block[2:]]
            tables.append([dict(zip(header, r, strict=True)) for r in rows])
            block = []
    return tables


def _bullets_after(md: str, heading: str) -> list[str]:
    """Top-level bullets (with their wrapped lines) under a heading."""
    section = md[md.index(heading + "\n") + len(heading) + 1 :]
    stop = re.search(r"^## ", section, re.M)
    section = section[: stop.start()] if stop else section
    items: list[str] = []
    for line in section.splitlines():
        if line.startswith("- "):
            items.append(line[2:].strip())
        elif line.startswith("  ") and items:
            items[-1] += " " + line.strip()
    return [_plain(i) for i in items]


def _r(x: float, nd: int = 2) -> float:
    return round(x, nd)


def hub_section(p: HubParams) -> list[list[list[float]]]:
    """Half section of the wheel hub through a bolt hole (angle 0), as (r, z) polygons.

    At angle 0 the cut passes through a bolt hole and a lightening hole, so the drawing shows the
    screw path and how much web is left. Hub faces: z = 0 on the horn, rim up to z = width.
    """
    d, w = derive(p), p.wheel
    r_rim = w.rim_od_mm / 2
    r_in = r_rim - w.rim_wall_mm
    r_out = r_rim + w.flange_mm
    web, cb_floor = d.web_mm, d.web_mm - d.counterbore_depth_mm
    bolt_r = p.horn.bolt_circle_mm / 2
    hole, cb = d.hole_diameter_mm / 2, d.counterbore_diameter_mm / 2
    light = d.lightening_diameter_mm / 2
    pocket = d.center_pocket_diameter_mm / 2

    def web_floor(r: float) -> float | None:
        """Bottom of the web at radius r, or None where the cut is open."""
        if (
            bolt_r - hole <= r < bolt_r + hole
            or d.lightening_radius_mm - light <= r < d.lightening_radius_mm + light
        ):
            return None
        return d.center_pocket_depth_mm if r < pocket else 0.0

    def web_top(r: float) -> float:
        return cb_floor if bolt_r - cb <= r < bolt_r + cb else web

    edges = sorted(
        {0.0, pocket, bolt_r - cb, bolt_r - hole, bolt_r + hole, bolt_r + cb}
        | {d.lightening_radius_mm - light, d.lightening_radius_mm + light, r_in}
    )
    polys: list[list[list[float]]] = []
    for a, b in zip(edges, edges[1:], strict=False):
        mid = (a + b) / 2
        floor = web_floor(mid)
        if floor is None or b > r_in:
            continue
        top = web_top(mid)
        polys.append([[_r(a), _r(floor)], [_r(b), _r(floor)], [_r(b), _r(top)], [_r(a), _r(top)]])
    land, rise, width = w.flange_land_mm, w.flange_mm, w.width_mm
    rim = [
        [r_in, 0.0],
        [r_out, 0.0],
        [r_out, land],
        [r_rim, land + rise],
        [r_rim, width - land - rise],
        [r_out, width - land],
        [r_out, width],
        [r_in, width],
    ]
    polys.append([[_r(r), _r(z)] for r, z in rim])
    return polys


def build() -> dict[str, Any]:
    servo_toml = HERE / "servo.toml"
    p, case, tire_design = load(servo_toml), load_case(servo_toml), load_tire(servo_toml)
    hub, cradle_design = derive(p), Cradle()
    t = derive_tire(p, tire_design)
    c = derive_cradle(case, p.horn, cradle_design)
    layout = BaseLayout()
    base = derive_base(case, p.horn, cradle_design, layout)

    readme = (EXP / "README.md").read_text()
    inventory = (REPO / "docs" / "inventory.md").read_text()

    timeline = []
    for item in _bullets_after(readme, "## Progress log"):
        date, _, text = item.partition(": ")
        timeline.append({"date": date, "text": text})

    phases = []
    for track, table in zip(("v1", "v2"), _tables_after(readme, "## Phases"), strict=True):
        for row in table:
            phases.append(
                {
                    "track": track,
                    "n": int(row["#"]),
                    "phase": row["Phase"],
                    "done_when": row["Done when"],
                }
            )

    bom_table = _tables_after(
        inventory, "## exp003 household robot parts (ordered 2026-11-17, due 2026-11-21 to 23)"
    )[0]
    bom = [
        {
            "n": int(r["#"]),
            "item": r["Item"],
            "asin": r["ASIN"],
            "check": r["Check on arrival"],
            "group": _group(int(r["#"])),
        }
        for r in bom_table
    ]
    printed = [
        {"item": r["Item"], "qty": r["Qty"], "status": r["Status"], "notes": r["Where / notes"]}
        for r in _tables_after(inventory, "## Printed parts")[0]
    ]
    stock_table, usage_table = _tables_after(
        inventory, "## Consumables: stock, usage and reorders"
    )[:2]
    consumables = {
        "stock": [
            {
                "item": r["Item"],
                "start": r["Start"],
                "used": r["Used"],
                "left": r["Left"],
                "planned": r["Planned next"],
                "reorder": r["Reorder point"],
                "lead_time": r["Lead time"],
            }
            for r in stock_table
        ],
        "usage": [{"date": r["Date"], "what": r["What"], "used": r["Used"]} for r in usage_table],
    }
    grams = [float(g) for r in usage_table for g in re.findall(r"PETG ([\d.]+) g", r["Used"])]

    horn = asdict(p.horn)
    return {
        "slug": "household-robot",
        "source": "experiments/exp003-household-robot/cad/export_site.py",
        "wheel": {
            "od_mm": tire_design.od_mm,
            "width_mm": p.wheel.width_mm,
            "rim_od_mm": p.wheel.rim_od_mm,
            "rim_wall_mm": p.wheel.rim_wall_mm,
            "flange_mm": p.wheel.flange_mm,
            "flange_land_mm": p.wheel.flange_land_mm,
            "web_mm": _r(hub.web_mm),
            "screw": f"{p.horn.bolt_count} x {hub.screw} {p.screws.head} head",
            "counterbore_diameter_mm": _r(hub.counterbore_diameter_mm),
            "counterbore_depth_mm": _r(hub.counterbore_depth_mm),
            "hole_diameter_mm": hub.hole_diameter_mm,
            "center_pocket_diameter_mm": _r(hub.center_pocket_diameter_mm),
            "center_pocket_depth_mm": _r(hub.center_pocket_depth_mm),
            "case_gap_mm": _r(hub.case_gap_mm),
            "lightening_holes": p.wheel.lightening_holes,
            "lightening_radius_mm": _r(hub.lightening_radius_mm),
            "lightening_diameter_mm": _r(hub.lightening_diameter_mm),
            "hub_section": hub_section(p),
        },
        "tire": {
            "od_mm": tire_design.od_mm,
            "rim_seat_od_mm": t.rim_seat_od_mm,
            "rim_measured": tire_design.rim_measured_od_mm is not None,
            "bore_mm": _r(t.bore_mm),
            "lip_bore_mm": _r(t.lip_bore_mm),
            "tread_mm": _r(t.tread_mm),
            "over_flange_mm": _r(t.over_flange_mm),
            "grip_stretch": _r(t.grip_stretch, 4),
            "mount_stretch": _r(t.mount_stretch, 4),
            "profile": [[_r(r), _r(z)] for r, z in tire_profile(p, tire_design)],
        },
        "cradle": {
            "a_min_mm": _r(c.a_min_mm),
            "a_max_mm": _r(c.a_max_mm),
            "b_inner_mm": _r(c.b_inner_mm),
            "b_outer_mm": _r(c.b_outer_mm),
            "wall_mm": cradle_design.wall_mm,
            "pad_mm": cradle_design.pad_mm,
            "pad_diameter_mm": cradle_design.pad_diameter_mm,
            "cheek_mm": cradle_design.cheek_mm,
            "cheek_height_mm": cradle_design.cheek_height_mm,
            "ear_length_mm": cradle_design.ear_length_mm,
            "ear_mm": cradle_design.ear_mm,
            "holes": [[_r(a), _r(b)] for a, b in c.holes],
            "hole_diameter_mm": c.hole_diameter_mm,
            "disc_opening_radius_mm": _r(c.disc_opening_radius_mm),
            "window": [_r(v) for v in c.window],
            "throat_half_width_mm": _r(c.throat_half_width_mm),
            "screw_depth_mm": _r(c.screw_depth_mm),
            "axle_above_foot_mm": _r(c.axle_above_foot_mm),
        },
        "servo": {
            "model": "Feetech STS3215 12V",
            "horn": horn,
            "case": asdict(case),
            "measured_note": (
                "Case length, width and mounting holes confirmed by caliper; "
                "the rest from the vendored CAD model."
            ),
        },
        "base": {
            **{
                k: (_r(v) if isinstance(v, float) else v)
                for k, v in asdict(base).items()
                if k != "masses"
            },
            "masses": [
                {"name": m.name, "kg": m.kg, "x_mm": _r(m.x_mm), "source": m.source}
                for m in base.masses
            ],
            "battery_mm": list(layout.battery_mm),
            "battery_x_mm": layout.battery_x_mm,
            "front_mm": layout.front_mm,
            "back_mm": layout.back_mm,
            "caster_x_mm": layout.caster_x_mm,
            "electronics_x_mm": list(layout.electronics_x_mm),
            "arm_base_x_mm": layout.arm_base_x_mm,
            "arm_kg": layout.arm_kg,
            "arm_reach_com_mm": layout.arm_reach_com_mm,
        },
        "printed": printed,
        "petg_used_g": _r(sum(grams), 1),
        "consumables": consumables,
        "bom": bom,
        "phases": phases,
        "timeline": timeline,
        "design": {"tire": asdict(tire_design), "cradle": asdict(cradle_design)},
    }


def render(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=1) + "\n"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(build()))
    print(f"wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
