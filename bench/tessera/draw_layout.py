"""Draw the bench layout (plan view) to bench/tessera/out/layout.png (gitignored).

uv run --no-project --python 3.12 --with matplotlib python -I bench/tessera/draw_layout.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from tessera_cad.layout import FIELD_COLS, FIELD_ROWS, GROW, LAYOUT  # noqa: E402
from tessera_cad.params import GRID  # noqa: E402

U = GRID.unit_mm
FILL = {"printed": "#f2c230", "planned": "#fbe7a6"}
PETG = "#f4a36a"
MAT_W, MAT_D = 450.0, 300.0


def main() -> None:
    fig, ax = plt.subplots(figsize=(11, 7.2))
    width = FIELD_COLS * U
    # the soldering mat in front of the field, the station to its left
    mat_x = (width - MAT_W) / 2
    ax.add_patch(Rectangle((mat_x, -MAT_D - 15), MAT_W, MAT_D, fc="#d9e3ea", ec="#7d8f9c"))
    ax.text(
        width / 2,
        -MAT_D / 2 - 15,
        "silicone mat 450 x 300\n(work area)",
        ha="center",
        va="center",
        color="#4d5d69",
        fontsize=10,
    )
    ax.add_patch(Rectangle((-150, -MAT_D - 15), 135, 200, fc="#e6e6e6", ec="#888", ls="--"))
    ax.text(
        -82,
        -MAT_D + 85,
        "iron station\n+ fume fan\n(size on\narrival)",
        ha="center",
        va="center",
        fontsize=8,
        color="#555",
    )
    ax.add_patch(plt.Circle((-82, -55), 35, fc="#e6e6e6", ec="#888", ls="--"))
    ax.text(-82, -55, "599B\ntip\ncleaner", ha="center", va="center", fontsize=7, color="#555")
    for c, r in GROW:
        ax.add_patch(
            Rectangle(
                (c * U + 0.25, r * U + 0.25),
                U - 0.5,
                U - 0.5,
                fc="white",
                ec="#bbb",
                ls=":",
                hatch="..",
                lw=0.8,
            )
        )
    ax.text(6 * U, 2 * U, "room\nto grow", ha="center", va="center", color="#999", fontsize=9)
    for p in LAYOUT:
        fc = PETG if p.material == "PETG" else FILL[p.status]
        ax.add_patch(
            FancyBboxPatch(
                (p.col * U + 1.5, p.row * U + 1.5),
                p.nx * U - 3,
                p.ny * U - 3,
                boxstyle="round,pad=0,rounding_size=3",
                fc=fc,
                ec="#6b5400",
                lw=2.0 if p.status == "printed" else 1.0,
            )
        )
        cx, cy = (p.col + p.nx / 2) * U, (p.row + p.ny / 2) * U
        small = p.nx == 1
        size = f"{p.nx}x{p.ny}" + ("\n" if small else ", ") + f"{p.steps * 26} mm"
        if p.material == "PETG":
            size += "\nPETG"
        ax.text(
            cx,
            cy + (9 if small else 6),
            p.name,
            ha="center",
            va="center",
            fontsize=8.5 if small else 9.5,
            weight="bold",
        )
        ax.text(cx, cy - (8 if small else 8), size, ha="center", va="center", fontsize=7.5)
    for i in range(FIELD_COLS + 1):
        ax.plot([i * U, i * U], [0, FIELD_ROWS * U], color="#00000010", lw=0.5)
    ax.annotate(
        "",
        xy=(width + 30, 0),
        xytext=(width + 30, FIELD_ROWS * U),
        arrowprops={"arrowstyle": "<->", "color": "#666"},
    )
    ax.text(width + 38, FIELD_ROWS * U / 2, f"{FIELD_ROWS * U:.0f}", va="center", fontsize=8)
    ax.annotate(
        "",
        xy=(0, FIELD_ROWS * U + 22),
        xytext=(width, FIELD_ROWS * U + 22),
        arrowprops={"arrowstyle": "<->", "color": "#666"},
    )
    ax.text(
        width / 2, FIELD_ROWS * U + 30, f"{width:.0f} mm (9 squares of 52)", ha="center", fontsize=8
    )
    ax.text(width / 2, -MAT_D - 40, "you sit here (front)", ha="center", fontsize=9, style="italic")
    ax.text(
        -150,
        FIELD_ROWS * U + 60,
        "Tessera bench layout, plan view (2026-11-24)",
        fontsize=12,
        weight="bold",
    )
    ax.text(
        -150,
        FIELD_ROWS * U + 42,
        "heat at the left, solder and flux in the middle, alcohol far right; tall at the back",
        fontsize=9,
        color="#555",
    )
    for i, (fc, lw, label) in enumerate(
        [
            (FILL["printed"], 2.0, "printed"),
            (FILL["planned"], 1.0, "planned, PLA"),
            (PETG, 1.0, "planned, PETG (near heat)"),
        ]
    ):
        x = width + 60
        y = -40 - i * 26
        ax.add_patch(Rectangle((x, y), 18, 18, fc=fc, ec="#6b5400", lw=lw))
        ax.text(x + 26, y + 9, label, va="center", fontsize=8)
    ax.set_xlim(-170, width + 230)
    ax.set_ylim(-MAT_D - 55, FIELD_ROWS * U + 75)
    ax.set_aspect("equal")
    ax.axis("off")
    out = HERE / "out" / "layout.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"wrote {out.relative_to(HERE)}")


if __name__ == "__main__":
    main()
