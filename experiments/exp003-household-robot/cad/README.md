# exp003 printed parts

Parametric CadQuery models. Measurements go in `servo.toml` ([MEASURING.md](MEASURING.md)); design
choices (wheel size, print tolerances) are in `exp003_cad/params.py`. Output goes to `out/`,
which git ignores: rebuild instead of committing meshes.

CadQuery is large, so it stays out of the lab's uv workspace and runs on demand:

```bash
uv run --no-project --python 3.12 --with cadquery python experiments/exp003-household-robot/cad/build.py
```

```bash
uv run --no-project --python 3.12 --with cadquery --with pytest pytest -q experiments/exp003-household-robot
```

The plain `uv run pytest` runs the measurement checks and skips the geometry tests.

## Parts

| Part | File | What it is |
|---|---|---|
| Hub coupon | `out/hub_coupon.step` | The horn interface only. About 20 minutes. Print this first. |
| Wheel hub | `out/wheel_hub.step` | 108 mm rim, 32 mm wide, flanges for a 6 mm TPU tire (120 mm wheel). |

The servo body itself, for brackets and the base plate, is the `[case]` table in `servo.toml`
and the vendored STS3215 model in [vendor/](vendor/README.md).

### Rules for the parts still to come

- **Servo bracket and chassis:** stay at least 2 mm below the hub's servo-side face everywhere
  inside the wheel's radius (60 mm round the shaft), so nothing rubs the spinning wheel.
- **Anything under the servo:** the idler disc on the bottom stands about 4.1 mm proud, so leave
  a pocket for it (vendor README) or hold the servo by its top holes or sides.

While `servo.toml` says `measured = false`, files end in `_UNMEASURED`. Do not print those.

## Print settings (H2D, PETG)

- Open the `.step` file in Bambu Studio (true curves; the `.stl` is there for other slicers).
- Servo side down: the flat face with the small centre pocket goes on the plate. No supports, no
  brim. The full hub can only print this way (its rim is a cup opening upward), so print the
  coupon the same way for an honest test.
- 0.4 mm nozzle, 0.2 mm layers, 4 walls, 30% infill (the profile's grid pattern is fine).

## Coupon check

1. Set the coupon on the horn, flat side down. The centre pocket drops over the centre screw head
   with almost no side-to-side play, and the coupon sits flat on the horn without rocking.
2. Fit the screws the build printed (for example `4 x M3 x 8`). They go in from the counterbored
   side and should pull the coupon down flat without forcing. Their tips poke a little out of the
   bottom of the horn; that is intended.
3. Spin the servo by hand. The coupon must not touch the servo case anywhere, including the raised
   block beside the horn: there should be about 2 mm of air (`raised_case_mm`).

| Result | Change |
|---|---|
| Centre pocket will not go over the centre screw | Raise `Fit.clearance_mm` by 0.05 and rebuild |
| Slides side to side on the horn | Lower `Fit.clearance_mm` by 0.05 and rebuild |
| Screw holes do not line up | Re-measure D (bolt circle) |
| Rubs the case, or under 2 mm of air | Re-measure H and I (shaft height, raised case) |
| Screws bottom out or are too short | Re-measure B and H |

Record the result in `../README.md` before printing the full hub.
