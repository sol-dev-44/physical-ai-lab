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

## Before designing a part (measure twice, cut once)

Do all of this before proposing a design, modelling it or asking for a print. It exists because
of two misses on 2026-11-19: a bracket was pitched for the servo's top holes before anyone noticed
the bottom holes and connectors, and the rim seat was asked for although caliper jaws cannot
reach it.

1. **Gather every source** for each component the part touches: datasheet, the vendor CAD model,
   how other builds mount it (the SO-101 guide for STS3215s), and what `servo.toml` already holds.
2. **Survey every face**, not just the one you plan to use: holes (top, bottom, ends, sides),
   threads, bosses, discs, steps, connectors and cable exits, screw heads, moving parts and what
   they sweep. With a CAD model, probe all its cylinders and faces and write the result down (as
   in `vendor/README.md`).
3. **List every way to mount it**, with what each needs and what it blocks, and pick one with
   reasons. Say the choice and the alternatives when proposing the part.
4. **For each fastener:** thread size, hole depth, screws on hand (`[screws]`), and room for the
   driver to reach the head.
5. **For each measurement you ask for:** check it can be taken with the tool on hand (caliper jaws
   reach about 40 mm; flanges and bosses block jaws) and say exactly where the jaws or depth rod go.
   Prefer a drawing.
6. **Ask every open question in one go**, before modelling. Do not model around a guess.
7. **Record** what was measured (lab) and what was read from a model or datasheet (model) in
   `servo.toml` and the docs, so the next part starts from facts.

## Parts

| Part | File | What it is |
|---|---|---|
| Hub coupon | `out/hub_coupon.step` | The horn interface only. About 20 minutes. Print this first. |
| Wheel hub | `out/wheel_hub.step` | 108 mm rim, 32 mm wide, flanges for a 6 mm TPU tire (120 mm wheel). |
| Tire | `out/tire.step` | TPU 95A ring for the hub: 120 mm outside, 107 mm bore (grips the 108 mm seat), lips over both flanges. |

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

## Tire (H2D, TPU 95A)

Design numbers are `Tire` in `exp003_cad/params.py`; the build prints the bore and stretch.

- **Before printing, measure the printed rim.** Caliper jaws cannot reach across a 108 mm seat,
  and the flanges stand in the way from above. So lay the hub flat, open side up, rest the beam
  across the top with the jaws hanging down, and close them gently on the top flange's narrow flat
  land. Take three readings 60 degrees apart; the seat is the middle one minus 3.0. Put it in
  `[tire]` in `servo.toml` (2026-11-19: flange 110.6, seat 107.6) and rebuild. The build refuses
  a seat over 1 mm off the design.
- Left nozzle, filament from the external spool holder, never through the AMS. Studio preset:
  Generic TPU. A sealed spool is dry enough; if it strings or pops, dry it.
- Flat, either face down, no supports, no brim. 3 walls, 25% gyroid infill (some give, still
  holds its shape), 4 top and bottom layers. Use the preset's slow speeds.
- Fitting: hub off the servo, servo-side face down. Push the tire over the top (outboard)
  flange at one point, then work round, rolling the lip over. It stretches about 3.7% to pass the
  flange. If it fights, a few minutes in hot tap water softens it.

| Result | Change |
|---|---|
| Tire turns on the rim under load | Raise `Tire.interference_mm` by 0.5 and reprint |
| Cannot get it over the flange | Lower `Tire.interference_mm` by 0.5 |
| Lip does not sit down over a flange | Raise `Tire.clearance_mm` by 0.1 |

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
