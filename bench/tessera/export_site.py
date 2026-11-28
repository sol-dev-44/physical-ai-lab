"""Export Tessera's numbers for the website's blueprint drawings.

    uv run python bench/tessera/export_site.py

Writes content/bench/tessera.data.json from tessera_cad (params.py, layout.py), so the drawings
cannot drift from the models: tests/test_tessera_site_data.py fails when the file is stale.
No CadQuery needed.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from tessera_cad.layout import FIELD_COLS, FIELD_ROWS, LAYOUT  # noqa: E402
from tessera_cad.params import GRID, JOINT, body, boss_size, bowtie, ribs, sockets  # noqa: E402

REPO = HERE.parents[1]
OUT = REPO / "content" / "bench" / "tessera.data.json"
MAT_MM = (450.0, 300.0)  # PAFOWO silicone mat in front of the field (docs/inventory.md)


def _r(v: float) -> float:
    return round(v, 3)


def _pts(pts: list[tuple[float, float]]) -> list[list[float]]:
    return [[_r(x), _r(y)] for x, y in pts]


def build() -> dict[str, Any]:
    g, j = GRID, JOINT
    reach = g.gap_mm + j.depth_mm
    slope = (j.end_mm - j.neck_mm) / 2 / reach
    boss_w, boss_d = boss_size(g, j)
    x0, x1, y0, y1 = body(g, 1, 1)
    return {
        "source": "bench/tessera/tessera_cad (params.py, layout.py)",
        "grid": {
            "unit_mm": g.unit_mm,
            "gap_mm": g.gap_mm,
            "wall_mm": g.wall_mm,
            "height_step_mm": g.height_step_mm,
            "corner_r_mm": g.corner_r_mm,
            "cup_mm": _r(x1 - x0),
        },
        "joint": {
            "neck_mm": j.neck_mm,
            "end_mm": j.end_mm,
            "depth_mm": j.depth_mm,
            "reach_mm": _r(reach),
            "flank_deg": _r(math.degrees(math.atan(slope))),
            "boss_width_mm": _r(boss_w),
            "boss_depth_mm": _r(boss_d),
            "key_clearance_mm": j.key_clearance_mm,
            "rib_radius_mm": j.rib_radius_mm,
            "rib_interference_mm": j.rib_interference_mm,
            "socket": _pts(bowtie(j, g)),
            "key": _pts(bowtie(j, g, j.key_clearance_mm)),
            "ribs": _pts(ribs(j, g)),
            "cup_sockets": _pts([s.at for s in sockets(g, 1, 1)]),
        },
        "layout": {
            "cols": FIELD_COLS,
            "rows": FIELD_ROWS,
            "mat_mm": list(MAT_MM),
            "modules": [
                {
                    "name": p.name,
                    "col": p.col,
                    "row": p.row,
                    "nx": p.nx,
                    "ny": p.ny,
                    "height_mm": _r(p.steps * g.height_step_mm),
                    "material": p.material,
                    "status": p.status,
                }
                for p in LAYOUT
            ],
        },
    }


def render(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2) + "\n"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(build()))
    print(f"wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
