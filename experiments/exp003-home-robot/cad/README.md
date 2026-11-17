# exp003 printed parts

Parametric CadQuery models. Measurements go in `servo.toml` ([MEASURING.md](MEASURING.md)); design
choices (wheel size, print tolerances) are in `exp003_cad/params.py`. Output goes to `out/`,
which git ignores: rebuild instead of committing meshes.

CadQuery is large, so it stays out of the lab's uv workspace and runs on demand:

```bash
uv run --no-project --python 3.12 --with cadquery python experiments/exp003-home-robot/cad/build.py
```

```bash
uv run --no-project --python 3.12 --with cadquery --with pytest pytest -q experiments/exp003-home-robot
```

The plain `uv run pytest` runs the measurement checks and skips the geometry tests.

## Parts

| Part | File | What it is |
|---|---|---|
| Hub coupon | `out/hub_coupon.step` | The horn interface only. About 20 minutes. Print this first. |
| Wheel hub | `out/wheel_hub.step` | 108 mm rim, 32 mm wide, flanges for a 6 mm TPU tire (120 mm wheel). |

While `servo.toml` says `measured = false`, files end in `_UNMEASURED`. Do not print those.

## Print settings (H2D, PETG)

- Open the `.step` file in Bambu Studio (true curves; the `.stl` is there for other slicers).
- Servo side down: the face with the shallow round recess goes on the plate. No supports, no brim.
- 0.4 mm nozzle, 0.2 mm layers, 4 walls, 30% gyroid infill.

## Coupon check

1. Set the coupon on the horn, recess down. It should drop over the horn with no rocking and
   almost no side-to-side play.
2. Fit the screws the build printed (for example `4 x M2 x 5`). They go in from the counterbored
   side and should pull the coupon down flat without forcing.
3. Spin the servo by hand. The coupon must not touch the servo case.

| Result | Change |
|---|---|
| Will not go over the horn | Raise `Fit.clearance_mm` by 0.05 and rebuild |
| Wobbles side to side | Lower `Fit.clearance_mm` by 0.05 and rebuild |
| Screw holes do not line up | Re-measure D (bolt circle) |
| Rubs the case | Re-measure H (shaft height) |
| Screws bottom out or are too short | Re-measure B and H |

Record the result in `../README.md` before printing the full hub.
