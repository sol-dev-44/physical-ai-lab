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
5. **Never ask the owner to measure what the sources already give.** Extract it from the docs
   here, a vendor CAD model, a related part's CAD (the SO-101 holders gave the screw depth), a
   datasheet or a quick search first. Once a model has matched the caliper checks, trust it for
   that part. Ask for a measurement only for what no source can show (a printed part's real size,
   a thread's feel), say why the source cannot settle it, and check it can be taken with the tool
   on hand (caliper jaws reach about 40 mm; flanges and bosses block jaws), with a drawing of where
   the jaws or depth rod go.
6. **Ask whatever is still open in one go**, before modelling. Do not model around a guess. A
   test print checks a fit; it never stands in for a number nobody measured. If no source gives
   a dimension and the owner can measure it in a minute, ask. The miss behind this rule
   (2026-11-21): the caster cup was printed knowing the fork's sweep was unpublished, "so the
   print is the test", and the fork hit the walls. One caliper reading would have caught it.
7. **Record** what was measured (lab) and what was read from a model or datasheet (model) in
   `servo.toml` and the docs, so the next part starts from facts.

## Gotchas and hints (for agents)

- **CadQuery runs outside the workspace:** `uv run --no-project --python 3.12 --with cadquery
  python -I <script>`. Put numbers and checks in `exp003_cad/params.py` (no CadQuery import), so
  the lab's plain `uv run pytest` tests them; geometry modules import CadQuery and their tests skip
  without it.
- **Don't trust OpenCascade's boolean intersect on the vendored servo model.** It silently returns
  nothing for overlaps deeper than about 0.3 mm. Check clashes by sampling `isInside` at points
  (see `tests/test_exp003_cradle_geometry.py`). A clash test must also be shown to fail, on a
  deliberately lowered servo.
- **Sampling on a face that touches by design counts as a clash** (points on a boundary are
  "inside"). Sample heights that avoid those faces.
- **Look at a render before calling a part done.** The tests passed while a 0.15 mm sliver of wall
  sat between two openings; the rear-view render showed it. Quick renders: tessellate and plot with
  matplotlib (`uv run --no-project --with cadquery --with matplotlib`).
- **Probe the vendored model first:** list every cylinder and planar face (axis, diameter, extent)
  before designing against it. Its holes are drawn only 1.5 mm deep; real depths come from related
  parts (the SO-101 holders' STEP files gave the screw depth).
- **The website draws this build from `content/builds/household-robot.data.json`.** It is written
  by `export_site.py` from `params.py`, `servo.toml`, the exp003 README (progress log and phases)
  and `docs/inventory.md`. After changing any of those, run
  `uv run python experiments/exp003-household-robot/cad/export_site.py` and commit the JSON;
  `tests/test_exp003_site_data.py` fails until you do. Markdown tables there are parsed by header
  name, so rename a column only together with the exporter.

## Parts

| Part | File | What it is |
|---|---|---|
| Hub coupon | `out/hub_coupon.step` | The horn interface only. About 20 minutes. Print this first. |
| Wheel hub | `out/wheel_hub.step` | 108 mm rim, 32 mm wide, flanges for a 6 mm TPU tire (120 mm wheel). |
| Servo cradle | `out/servo_cradle.step` | Holds a wheel servo by its bottom holes. Cheeks hug the case; the lower cheek is the foot, with an M3 ear at each end. |
| Tire | `out/tire.step` | TPU 95A ring for the hub: 120 mm outside, 107 mm bore (grips the 108 mm seat), lips over both flanges. |
| Caster cup | `out/caster_cup.step` | Light open cup (55 x 55 x 12.6 mm) the rear caster bolts up into: the raised pocket that holds the plate level. A box for the caster's plate joined with a circle for the fork's sweep. A separate part so the base plate prints flat. |

The servo body itself, for brackets and the base plate, is the `[case]` table in `servo.toml`
and the vendored STS3215 model in [vendor/](vendor/README.md).

### Rules for the parts still to come

- **Servo mount: from below, decided 2026-11-19.** The top holes cannot be used: they sit on
  the case's side strips, 1.5 mm above the low case round the shaft, so the spinning hub is only
  about 2.5 mm above them (H = 4.0 minus 1.5). A plate there needs 2 mm of plastic plus an M2
  head, and must keep 2 mm from the hub. The bottom holes (24.5 x 20.5 mm) are free, and this
  is how the SO-101 holds its servos.
- **What the bottom mount must allow for** (numbers in `servo.toml` `[case]` and
  `vendor/README.md`):
  - It sits on bosses at the four holes, which are on the bottom step face.
  - The idler disc stands 2.6 mm past that face. Give it an opening with 2 mm all round, except
    by the near bosses: the near holes are 13.2 mm from the shaft axis and the disc's edge is at
    10, so those bosses stay slim. This is the tightest spot in the design.
  - The pad stands 1.8 mm past the step face. Either the bosses clear it by 0.5 mm, or the plate
    has a pocket over it.
  - The two bus connectors are on the bottom, 14 mm from the shaft. Leave a window for the
    plugs and room for the cables to bend.
  - The supplied M2 x 6 self-tapping screws go no deeper than 4.1 mm into the case, so keep at
    least 1.9 mm (2.0 to 2.5 mm is good) of plastic under each head.
- **Servo mount and chassis:** stay at least 2 mm below the hub's servo-side face everywhere
  inside the wheel's radius (60 mm round the shaft), so nothing rubs the spinning wheel.

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
- TPU 95A feeds the **right** hotend through the rear TPU inlet, never the AMS: see `docs/printing.md`
  (TPU) for the tube swap. Studio preset: Generic TPU. A sealed spool is dry enough; if it strings or pops, dry it.
- Flat, either face down, no supports, no brim. 3 walls, 25% gyroid infill (some give, still
  holds its shape), 4 top and bottom layers. Use the preset's slow speeds.
- Fitting: hub off the servo, servo-side face down. Push the tire over the top (outboard)
  flange at one point, then work round, rolling the lip over. It stretches about 3.7% to pass the
  flange. If it fights, a few minutes in hot tap water softens it.

Result 2026-11-21: both tires fit snugly first time at the design numbers (1.0 mm interference
on the measured 107.6 mm seat, 0.2 mm lip clearance). Keep them for the next tire.

| Result | Change |
|---|---|
| Tire turns on the rim under load | Raise `Tire.interference_mm` by 0.5 and reprint |
| Cannot get it over the flange | Lower `Tire.interference_mm` by 0.5 |
| Lip does not sit down over a flange | Raise `Tire.clearance_mm` by 0.1 |

## Caster cup (H2D, PETG)

Numbers are `CasterCup` and `derive_caster_cup` in `params.py`; heights come from `derive_heights`.

- Roof on the bed, open end up: no supports. Default 2 walls, 15% infill: about 25 minutes.
- For a fit test print `out/caster_cup_test.step` (`CASTER_CUP_TEST`: 1.2 mm walls, 2 mm roof,
  34 mm centre hole): same cavity, holes and depth at half the plastic (5.4 g, 22 min).
- Fit: put the caster's plate against the roof inside the cup, then 4 x M4 x 12 button head
  from below through the caster and the roof, a nut on each on top (Mywish kit).
- Check: (1) the caster's plate drops in without forcing; (2) spin the caster all the way round
  by hand: the fork must not touch the walls (the fork's sweep is not published, so this is the
  test, and v1 failed it); (3) the open end of the cup is the plate's underside, 40.4 mm off the floor: stand the
  cup on its caster and the open rim should be 40.4 mm up.

| Result | Change |
|---|---|
| Plate will not drop in | Raise `CasterCup.clearance_mm` by 0.2 |

Result 2026-11-21 (first cup): the plate drops in with a little play and the four holes line up,
but the fork hits the walls as it swivels. The fork reaches 24 mm from the swivel axis (owner's
reading: 47 mm from a point of one short end to the fork's far side, fork turned out past the
other end; minus half the 46 mm plate). v2 adds a circle of 25.5 mm radius to the cavity.
Result 2026-11-21 (v2, light version): the fork swivels clear all the way round. Settled.

| Fork rubs a wall as it swivels | Make the cavity round the sweep (a circle) and move the caster forward so the cup stays on the plate (`BASE_PLATE.md`, "Height") |
| Screws do not line up | Re-measure the hole centres into `Caster` |

## Servo cradle (H2D, PETG)

Numbers in `Cradle` (`exp003_cad/params.py`) and `[case]` (`servo.toml`); the build prints the
screw depth and the axle height. Tests load the vendored servo model into it and check for clashes
by sampling points, because OpenCascade's boolean intersect silently misses deep overlaps on that
model.

- Print with the back wall on the bed (the face with the screw-head side of the holes), no
  supports. 4 walls, 30% infill, like the hubs.
- Fitting: slide the servo between the cheeks, bottom first, so it sits on the four pads. Drive
  the four supplied M2 x 6 self-tapping screws from the back; they go 3.5 mm into the case (the
  SO-101 puts them in up to 4.1). Snug, not tight: they cut their own thread in plastic.
- Take the loose metal idler disc off the servo's bottom first (the one with a hole in the middle;
  the top horn has a screw there) and keep it with the spares. Nothing here bolts to it, and it
  would rattle or drop out through the round opening. Plug the bus cables in through the window.
- For the chassis: the wheel axle is 15.6 mm above the foot face, and the screw heads and the
  idler disc stand slightly proud of the back wall, so keep 2 mm clear behind it.

| Result | Change |
|---|---|
| Servo will not slide between the cheeks | Raise `Cradle.side_clearance_mm` by 0.1 |
| Servo rocks on the pads | Check nothing on its bottom touches the wall; widen `keepout_margin_mm` |
| A screw turns without tightening | Lower `Cradle.wall_mm` by 0.5 so it bites 0.5 mm deeper (the build refuses past 4.1) |

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
