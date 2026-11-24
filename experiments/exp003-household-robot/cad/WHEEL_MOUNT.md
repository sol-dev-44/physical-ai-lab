# Wheel mount v2: what failed, why, and the plan

Written 2026-11-23, the evening the owner found the wheels "bending" while dry-fitting the
electronics deck. Numbers come from `params.py` (`derive_base`, `derive_cradle`) unless a source
is named. Nothing here is modelled yet; this is the input for the next CAD session, gathered
under "Before designing a part" ([README.md](README.md)).

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
3. **Base plate v2.**
   - Kept the same: outline, thickness, deck grid, caster holes, battery fences and strap slots,
     so every deck part and the caster cup move across unchanged.
   - New: holes for the box feet and the beam.
   - A reprint, not drilling: the owner preferred not to drill the plate for the DROK. About
     5 h and 225 g. The old plate becomes a spare and a drilling template.
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
- **To order now** so it never blocks: 4 x 6806-2RS (two plus spares). See
  [docs/inventory.md](../../../docs/inventory.md), "Orders to place".

### Meanwhile

- **Keep the weight off the wheels.** Battery off, or the plate resting on a box, so the old
  cradles do not creep further.
- **The deck:**
  - Put the standoffs into the trays now: step 1 of the assembly order in [DECK.md](DECK.md).
  - Bolt the trays to plate v2, not the old plate. The grid is unchanged.
- **Unchanged:** the power harness waits for the soldering kit (2026-11-25 to 27) and the wiring
  diagram. The phase 0 bench test (servos in wheel mode on the bench) does not need the chassis.

### PETG

The new parts use about 375 g (estimate):
- servo boxes: about 2 x 45 g
- beam: about 50 g
- coupon: about 10 g
- plate v2: about 225 g

Spool 1 has about 526 g, and spool 2 is sealed. That covers it, but it takes the buffer well
under the 2 kg rule, so the 3-spool PETG order is now urgent.
