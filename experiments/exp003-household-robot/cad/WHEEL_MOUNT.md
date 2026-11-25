# Wheel mount v2: what failed, why, and the plan

Written 2026-11-23, the evening the owner found the wheels "bending" while dry-fitting the
electronics deck. Numbers come from `params.py` (`derive_base`, `derive_cradle`) unless a source
is named. Stage 1 is modelled (2026-11-24): see "Stage 1 as modelled" below, which supersedes the
plan's details where they differ.

## What happened

Photo (owner, 2026-11-23): the +y cradle (the Pi's side) has rolled about the inboard edge of
its foot. The servo's outer end has lifted, and the wheel's top leans in toward the plate. The hub
and the tire are intact. The hinge is the cradle and its two bolts, not the wheel.

## Why

| Quantity | Value | Source |
|---|---|---|
| Robot mass | about 2.3 kg (battery 1.22, wheels 0.29, plate 0.25, electronics 0.25, servos and cradles 0.14, caster 0.04, deck parts about 0.07) | `BaseLayout`, slicer |
| Centre of mass | 45 mm behind the axle; the caster carries 28% | `derive_base` |
| Load on each wheel | about 8 N now; about 14 N with the v2 arm at full reach (centre of mass 18 mm behind the axle) | same |
| Tire centre line | y = 148.8 mm (wheel inner face 132.8 plus half the 32 mm width) | `derive_base`, `Wheel` |
| Cradle foot | y = 96 (back wall) to 118.5, 3 mm thick | `derive_cradle` |
| Foot bolts | 2 x M3, both on one line at y = 107.25, 55.4 mm apart along x | `derive_base_plate` |
| Cradle walls | back wall 2 mm, cheeks 3 mm and 20 mm tall; printed back wall down | `Cradle`, cradle.py |

- **The lever.** The tire pushes up 52.8 mm outboard of the foot's inboard edge, and the bolts
  hold 11.25 mm from that edge. Every newton at the tire puts 4.7 N on the bolts: about 38 N
  static per side, 66 N with the v2 arm, and two to three times that over a bump or a drop.
- **The layers.** The cradle prints with its back wall on the bed, so the cheeks and the foot
  rise in layers stacked along the shaft. The rolling moment bends the cheek roots and the
  foot-to-wall joint across those layers, which is the weakest direction of a print (the
  [Qidi](https://au.qidi3d.com/blogs/print-lab/petg-strength-wall-mounted-brackets) and
  [Evetech](https://evezone.evetech.co.za/build-lab/how-to-print-brackets-and-mounts-that-actually-hold-weight)
  bracket guides: route the load so it does not rely on layer adhesion).
- **Creep.** PETG under a constant load creeps at room temperature (Qidi, same page), and the
  robot stood with the battery on.
- **The plate.** Between the bolt line and the pivot edge, the 4 mm plate bends locally.
- **Not the cause:** the hub. Its 6 mm web carries the tire's 13 mm offset easily, and 4 x M3
  clamp it to the horn.
- **Unknown: the servo's own shaft support.** No radial load rating is published.
  [ServoDatabase](https://servodatabase.com/servo/feetech/sts3215) lists a single bearing and
  [DFRobot](https://www.dfrobot.com/product-2961.html) a ball bearing. The usual advice for a
  geared motor driving a wheel is to carry the weight on a separate bearing so the motor only
  gives torque ([Pololu forum](https://forum.pololu.com/t/radial-load-and-number-of-bearings-of-50-1-metal-gearmotor-3/8629)).
  LeKiwi runs a 1.7 kg base on three STS3215s with wheels on the horns, about 5.7 N per wheel
  ([Seeed kit](https://www.robotshop.com/products/seeedstudio-lekiwi-kit-12v-mobile-base-w-3d-printed-parts-battery)).
  Ours is 8 N now and 14 N with the arm, and LeKiwi sandwiches each motor mount between a bottom
  and a top plate ([LeKiwi](https://github.com/sigrobotics-uiuc/lekiwi)), so its mounts do not
  hinge.

## Rules this adds

These are in the "Before designing a part" checklist ([README.md](README.md)) from now on.

1. **Find the pivot.** For every bolted joint under load, name the edge it would tip about and
   compare the load's distance from that edge with the bolts' distance. Keep the ratio under
   about 2 to 1, and put bolts on two lines across the load, not one.
2. **Load the layers along their length.** Orient the print so the main bending happens in the
   layer plane, not across it.
3. **Close the frame.** When two sides carry matching loads (left and right wheels), tie them
   together so the moments meet in one stiff member, not in a thin plate.
4. **Design for about 3 x static and for creep.** Bumps and drops are part of daily use, and
   PETG under constant load creeps.

## Plan

### Stage 1: wheel module v2 (print only, nothing to buy)

1. **Servo box (replaces the cradle), one per side.**
   - Walls 4 mm round the case on four sides: top, bottom and both ends. The servo can no longer
     rotate inside it.
   - Back wall 5 mm, with counterbores so the supplied M2 x 6 screws still go 3.5 mm into the
     case, the same as now.
   - Cheeks reach to 2 mm under the hub (c = 32.3) instead of 20 mm, holding the case near its
     output end.
   - **Foot:** 5 mm thick. Across the robot it runs from y = 81 (outside the battery fence) to
     y = 128.8 (2 mm inside the plate edge); fore and aft from about x = -60 to the box's front
     wall (about x = +14), where the axle beam takes over.
   - **Bolts:** 6 x M3 on two lines, y about 85 and 124. The lever drops from 4.7 to 1 to about
     1.6 to 1.
   - **Gussets:** two per box, fore and aft of the case, from the foot's outboard edge up to the
     top wall.
   - **Mirror images.** Turn the -y servo half a turn about its own shaft, which its symmetric
     holes and window allow. Both far ends then point back, and both connector windows face back,
     away from the axle beam.
   - **Printing:** on its end (fore-aft axis vertical), so the rolling moment's plane lies in the
     layers. 6 walls, 40% infill, teardrop horizontal holes.
2. **Axle beam.** One box-section beam across the robot, just ahead of the boxes' front walls
   (about x = 15 to 31):
   - Clear of the strap slots (x = -3.5 to 0.5), the battery and the front sensor rows (x = 75
     and up).
   - About 30 mm deep and 16 mm wide with 3 mm walls.
   - Bolted to both boxes and to the plate with 4 x M3.
   - The two wheels' rolling moments meet in it instead of in the plate: the same idea as
     LeKiwi's top plate.
   - Prints lying on its side, so its bending plane is in the layers.
3. **Plate v1, drilled (owner, 2026-11-25: no reprint).**
   - A plate v2 would have kept the same outline, thickness, grid, caster holes, fences and slots,
     and only moved the holes: 225 g of PETG for 15 holes. Instead, drill plate v1 with the
     module as the template (see "Drilling plate v1" below).
   - The base plate model (`base_plate.py`) now shows the drilled plate. The old cradle holes
     stay in the real plate, covered by the feet.
4. **Fit coupon first, about 30 min.** A slice of the box foot with two bolt holes and one M2
   counterbore, and a 40 mm stub of the beam with its joint. It checks the counterbore depth for
   the M2 x 6, the teardrop holes and the beam-to-box bolts.
5. **Done when:**
   - With the battery, the deck and 1 kg on the battery top (standing in for the arm), each wheel
     leans less than 0.5 degrees. Measure with a phone level held flat against the tire's side:
     first on the bare plate, then loaded.
   - Ten drops from 2 cm onto a hard floor and 24 h standing loaded leave no change you can
     measure.
   - Each wheel still spins true by hand.

### Stage 1 as modelled (2026-11-24)

`exp003_cad/wheel_module.py`, numbers and checks in `params.WheelModule` and
`derive_wheel_module`, tests in `tests/test_exp003_wheel_module*.py`. The owner asked for it
"hella sturdy", so every check uses **5 x** the static load, not the plan's 3 x.

**What changed from the plan, and why:**
- **One piece.** The two servo boxes and the beam are one part, a U across the front of the
  battery. The beam no longer bolts to the boxes, so there is no joint to work loose, and the
  wheels' rolling moments meet in one solid. It prints standing on the beam's front face: 262 x
  33 mm on the bed, 83 mm tall, with every rolling-moment bending plane in the layers.
- **The wall under the case stays 3 mm**, not 4. A thicker wall there lifts the axle by 1 mm and
  tilts the robot back about 0.4 degrees, because the caster cup levels it. The 5 mm foot runs
  everywhere outside the case's footprint instead.
- **Beam solid**, 15.6 mm (x) by 33.2 mm (z), not a hollow box: infill does the job, and the
  bolts go through it in counterbores.
- **A fin, not a rear gusset.** Printing on the beam's face, a plate across x hangs over air
  unless the beam is under it; Bambu Studio flagged the rear gusset as a floating cantilever. The
  rear brace is a fin running along x instead, tapered at 45 degrees where it starts, so every
  layer stands on the one below. The front gusset sits on the beam and stays.

**The part (+y side; the -y side mirrors it):**

| Feature | Size |
|---|---|
| Servo box | Case 45.4 x 24.8 mm, 0.2 mm clearance; walls 5 mm on top and both ends, 3 mm under, back wall 5 mm |
| Back wall | 4 counterbores, 4.4 mm across and 3 mm deep, so the M2 x 6 bites 3.5 mm as before; pads, idler disc opening, connector window as the cradle |
| Braces | The front end wall carried inboard to the foot's edge (y 81) as a gusset; at the rear, a fin from the foot to the top along the back wall (x -44 to -35.8, 5 mm off the wall), its front end tapered at 45 degrees. The servo cables pass inboard of the fin, over the foot |
| Foot | 5 mm thick, x -52 to 15.4, y 81 to 130.8; grooves 6 mm wide down to 2 mm so a screwdriver reaches the lower M2 screws |
| Beam | x 15.4 to 31, across the robot, full box height |
| Bolts to the plate | 8 x M3 x 12 through the feet (y 85, 105, 124), 7 x M3 x 16 through the beam (y 0, +-42, +-85, +-124), heads in counterbores, nuts under the plate |
| Servo position | Unchanged: step face at y 98.5, axle 15.6 mm above the plate; the -y servo turned half a turn about its shaft so both far ends point back |

**Load checks** (the design load is 5 x the static load with the v2 arm reaching forward):

| Check | Value | Limit |
|---|---|---|
| Static load per wheel | 15 N | |
| Design load per wheel | 73 N | |
| Load lever to bolt lever, about the foot's inboard edge | 1.58 to 1 | under 2 (the cradles: 4.7) |
| Tension in each outboard bolt | 57 N | a third of about 900 N pull-through |
| Bending stress at the back wall section | 0.47 MPa | 5 MPa (PETG along its layers, allowing for creep) |

The vendor servo model sits in both boxes with no overlap (`test_exp003_wheel_module_geometry`).

**Printing:** PETG, 6 walls, 40% infill, front face of the beam down, no supports (the holes
across the print are teardrops). About 164 g and 3 h 52 min in Bambu Studio (the 190 g was an estimate); the build's estimate at 4 walls and 30% is 152 g.
The coupon (`wheel_module_coupon`, 18 g, 1 h 24 min) is a 28 mm slice at the back wall: push a servo in,
drive the four M2 screws, and bolt it down with M3 x 12 to check the case fit, the screw bite and
the holes before the 190 g print.

**Coupon result (owner, 2026-11-24):** printed in orange PETG (17.96 g) and the servo fits. Next is
the full module.

**Drilling plate v1** (no filament; about 15 minutes). Module frame: x forward, y left.
- Hole positions, from the plate's centre line (y) and its front edge: feet at x = 5 and -46
  (y = 85 each side, and y = 105 and 124 at x = -46); beam at x = 23.2, y = 0, 42, 85 and 124
  each side. They come from the module itself, so nothing needs marking.
- Place: the module's outer faces sit flush with the plate's side edges (both 130.8 mm from the
  centre line), and the beam's front face is 79 mm behind the plate's front edge (the end with
  the two rows of bumper holes). Check: the beam's rear face is 14.9 mm in front of the front
  strap slots.
- Bit: 1/8 inch (3.18 mm). It passes through the module's 3.4 mm holes, and M3 (3.0 mm) goes
  through it. The beam holes are 33 mm deep, so about 40 mm of bit must stand out of the chuck.
- Slow speed, light pressure, back out to clear chips: fast drilling melts PETG.
- Every hole is a teardrop with its point to the rear, so start each with the bit against the
  front of the round part.
- The nearest old cradle hole is 6.2 mm from the new one at (-46, 105): 2.8 mm of plate between.

**Assembly:**
1. Battery out. Push each servo into its box from outboard, cables first through the window.
2. Drive the four M2 x 6 from inboard (the lower two along the driver grooves).
3. Route the cables back over the foot, inboard of the rear fin.
4. Bolt the module to the drilled plate: feet first (8 x M3 x 12), then the beam (7 x M3 x 16,
   heads down the counterbores), nuts under the plate.
5. Fit the hubs and wheels as before.

### Stage 2: a bearing that carries the wheel

Do this before the v2 arm, or sooner if Stage 1's check shows tilt inside the servo itself (the
wheel leaning while the box stays put).

- **Concept:**
  - A 6806-2RS bearing (30 x 42 x 7 mm) in a ring on each servo box's outer face, centred on
    the shaft.
  - The hub gains a 30 mm sleeve round the horn that turns in the bearing.
  - A printed spacer moves the hub out about 8 mm (M3 x 16 from the kit instead of x 8).
  - The box then carries the weight, and the servo only drives.
- **Checks before modelling:**
  - The ring's lower half hangs past the plate edge; its bottom is about 37 mm off the floor.
  - The spacer must leave the horn screws reachable.
  - The width over the tires grows by about 16 mm (330 to about 346 mm).
- **Order now** (owner, 2026-11-24: don't hold up the build), though the one-piece module may
  make stage 2 unnecessary until the arm: 4 x 6806-2RS. The 10 x 608-ZZ on hand (8 mm bore) cannot go round
  the 20 mm horn, so they do not fit this concept; they could carry an outboard stub axle on a
  bracket round the tire instead (free, but wider and bulkier). See
  [docs/inventory.md](../../../docs/inventory.md), "Orders to place".

### Meanwhile

- **Keep the weight off the wheels.** Battery off, or the plate resting on a box, so the old
  cradles do not creep further.
- **The deck:**
  - Put the standoffs into the trays now: step 1 of the assembly order in [DECK.md](DECK.md).
  - Bolt the trays to the plate once the module is on. The grid is unchanged.
- **Unchanged:** the power harness waits for the soldering kit (2026-11-25 to 27) and the wiring
  diagram. The phase 0 bench test (servos in wheel mode on the bench) does not need the chassis.

### PETG

The new parts used about 182 g (slicer, 2026-11-24): the wheel module 164.26 g and the coupon
17.96 g. No plate v2: plate v1 is drilled instead (owner, 2026-11-25).

Spool 1 has about 344 g left and spool 2 is sealed; 3 more spools are due 2026-11-27.
