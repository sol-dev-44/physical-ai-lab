"""Build Tessera's printable parts into bench/tessera/out/ (gitignored).

    uv run --no-project --python 3.12 --with cadquery python -I bench/tessera/build.py

Writes STEP (open in Bambu Studio: true curves) and STL for each part.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from tessera_cad.false_floor import false_floor_print  # noqa: E402
from tessera_cad.key import field_key, key  # noqa: E402
from tessera_cad.module import cup  # noqa: E402
from tessera_cad.params import (  # noqa: E402
    ALCOHOL,
    BIG,
    FIRST_PIECE_CUPS,
    PARTS_TRAY,
    PLATE_3_KEYS,
    TEST_KEY_CLEARANCES,
    TEST_PLATE_2_PLAIN,
    TEST_PLATE_2_RIBS,
    Grid,
    module_height,
)

OUT = HERE / "out"


def _write(name: str, part: cq.Workplane) -> None:
    cq.exporters.export(part, str(OUT / f"{name}.step"))
    cq.exporters.export(part, str(OUT / f"{name}.stl"), tolerance=0.01, angularTolerance=0.1)
    print(f"wrote out/{name}.step and .stl")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for c in FIRST_PIECE_CUPS:
        _write(f"tessera_cup_1x1_{c.label.lower()}", cup(c))
    h = module_height(Grid(), FIRST_PIECE_CUPS[0].steps)
    for c in TEST_KEY_CLEARANCES:
        mark = f"{round(c * 100):d}"
        _write(f"tessera_test_key_{mark}", key(h, clearance=c, mark=mark))
    # test plate 2 (2026-11-24): one tighter plain key and two ribbed keys
    mark = f"{round(TEST_PLATE_2_PLAIN * 100):02d}"
    _write(f"tessera_test_key_{mark}", key(h, clearance=TEST_PLATE_2_PLAIN, mark=mark))
    for n, i in enumerate(TEST_PLATE_2_RIBS, start=1):
        _write(f"tessera_test_key_r{n}", key(h, clearance=0.10, mark=f"R{n}", rib_interference=i))
    # plate 3 (2026-11-24): the PARTS tray (yellow) and blue field keys, one file per height
    _write("tessera_parts_2x1", cup(PARTS_TRAY))
    for height in PLATE_3_KEYS:
        _write(f"tessera_key_{height}", field_key(height))
    # 2026-11-25: ALCOHOL (No. 004) and its false floor, printed plate down; BIG (No. 005).
    # Cups print open side up, as built.
    _write("tessera_alcohol_2x2", cup(ALCOHOL))
    _write("tessera_alcohol_false_floor", false_floor_print(ALCOHOL))
    _write("tessera_big_2x2", cup(BIG))


if __name__ == "__main__":
    main()
