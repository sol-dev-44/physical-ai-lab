# exp003 build steps

The owner's physical build, one step at a time. The `build-step` skill
(`.claude/skills/build-step/SKILL.md`) reads this file, gives the next open step with a
diagram, and ticks steps off when the owner reports them done. Numbers come from the CAD
(`cad/exp003_cad/params.py`) and the notes linked on each step; never ask the owner to measure
them.

Frame: x forward, y left, z up from the plate's top face. Front = the plate end with the two
rows of bumper holes; the caster is at the back.

## Wheel module v2 onto plate v1 ([cad/WHEEL_MOUNT.md](cad/WHEEL_MOUNT.md))

All done 2026-11-26 (steps 0 to 4 in Done).

## Deck onto the plate ([cad/DECK.md](cad/DECK.md), "Dry fit and assembly order")

- [ ] **8b. Zip ties on the UCTRONICS and INA226** (2 each) once there are ties: thread through the
  floor tunnels, or undo that tray's 4 screws to thread them.
- [ ] **9. Rocker and charge jack** into the switch panel, once their leads are on (waits for the
  bench soldering).
- [ ] **11. Fuse holders** on their tie points while wiring.

## Wiring (next, from README "Next" 5 and 6)

- [ ] **13. Bench soldering** of the harness joins, away from the PETG (it softens at about
  80 C), heat-shrunk; then step 9 (rocker and charge jack) and step 11 (fuse holders). Method:
  [HARNESS.md](HARNESS.md), "Bench method".
  - [x] 13a. Rocker leads. Done 2026-11-27 (owner): tab A (marker dot) = 150 mm red "IN" + the
    3 A holder; tab B = 250 mm red + the 5 A holder. Beep test passed (on beeps, off silent).
  - [ ] 13b. Charge jack + onto the 3 A holder's free lead (twist, tin, join, heat-shrink).
    Check the jack's leads first (HARNESS.md, "To confirm").
  - [ ] 13c. 5 A holder's free lead to DROK IN+. Find which DROK pair is IN first (label or
    lead colours).
  - [ ] 13d. Main 10 A holder: one lead to a crimped 6.3 mm female spade (battery +, Klein
    crimper), the other into INA226 VIN.
  - [ ] 13e. Ground star (battery -, DROK IN-, UCTRONICS IN-, INA226 GND, charge jack -),
    soldered and heat-shrunk; battery - spade crimped.
  - [ ] 13f. Continuity checks of the whole harness, battery still off.
- [ ] **14. Check the DROK's output reads 12.0 V** on the meter before any servo is plugged in
  (inventory "Check on arrival").
- [ ] **15. Servo cables** from the two wheel servos into the servo board's D V G sockets, in
  through the boxes' back-wall windows, battery out. The two servos need different bus IDs
  before they share the bus (phase 0 bench test).

## Done

- [x] **12. Power harness wiring diagram** ([HARNESS.md](HARNESS.md)). Drafted 2026-11-27; the
  owner checked it against the parts and built the rocker to it the same day (3 A charge fuse
  kept). The DROK's IN/OUT pair and the charge jack's leads are checked at their joins (13b, 13c).
- [x] **10. Pi 5 and servo board on their standoffs.** Done 2026-11-26 (owner, photos). Pi:
  GPIO pins along the front edge, USB/Ethernet toward the centre, USB-C and HDMI on the back
  edge, Active Cooler fitted (push pins in the diagonal holes, fan at the USB corner, lead in the
  FAN socket by the USB ports, not the 3-pin UART socket between the HDMI ports), 4 x M2.5 x 5.
  Servo board: turned half a turn from the first try so its USB-C, DC terminal and barrel jack
  face the Pi and the D V G sockets face the power side; its own corner screws into the 20 mm
  standoffs. Jumper caps looked to be on B (USB to servo) in the photo; confirm before wiring.
- [x] **8. INA226 and UCTRONICS placed.** Done 2026-11-26 (owner, photo): UCTRONICS in the compute
  tray's back channel, USB-A outboard; INA226 in its pocket, screw terminals forward. No zip ties
  yet (none on hand), see 8b.
- [x] **7. DROK onto the power tray.** Done 2026-11-26 (owner). M3 nuts pushed into the pad
  channels from their open ends (front pad from the front, back pad from the back), 2 x M3 x 8
  through the ears, leads inboard and left full length for the bench solder joins.
- [x] **6. The three deck parts to the plate.** Done 2026-11-26 (owner). Compute tray, power
  tray and servo bridge, 4 x M3 x 12 each up from under the plate. The trays' M3 holes are plain
  (nut held on the floor while the screw turns); only the bridge's legs have hex wells.
- [x] **5. Standoffs into the trays.** Done 2026-11-26 (owner). 4 x 11 mm M-F on the compute
  tray, 4 x 20 mm M-F on the servo bridge, M2.5 nuts in the pockets. The kit's sizes are body
  length; each has a 6 mm stud on top of that. The servo board's own short corner feet come off
  (keep its screws for step 10): the CAD's collision check needs at least 18 mm under the board,
  or its USB-C and 12 V plugs hit the Pi's USB corner.
- [x] **4. Load check.** Passed 2026-11-26 on the owner's hands-on check (loaded and handled);
  no caliper readings were taken, so the lean is not measured. If the wheels later look
  splayed or the +y box crack reopens, do the caliper check (book beside each tire, T and B
  readings, pass under 0.9 mm change).
- [x] **4a. Patch the crack in the +y box top.** Done 2026-11-26 (owner). Found 2026-11-25,
  through the 5 mm top wall along a layer joint. Stitched across with binder-ring wire sunk flush
  with the Pinecil at 260 C (the office staples were copper-thick and would not sink at 350 C),
  then a bead melted along the crack over the stitches (the plan was orange PETG from a retired
  cradle; the bead shows blue in the 2026-11-26 photos, and the only blue filament on hand is
  PLA, which bonds poorly to PETG: confirm the material, and watch the crack). The load check (step 4) decides
  whether it holds.
- [x] **2. Bolt the module to the plate.** Done 2026-11-25 (owner). 8 x M3 x 12 in the feet,
  7 x M3 x 16 down the beam counterbores, nuts under the plate.
- [x] **0. Drill plate v1 for the module (15 holes).** Done 2026-11-25 (owner). Feet at
  x 5 and -46 (y 85, 105, 124), beam at x 23.2 (y 0, 42, 85, 124), each side; 1/8 inch bit
  with the module as the template.
- [x] **1. Fit the servos into the module.** Done 2026-11-25 (owner). Both bodies point to the
  rear (the right servo flipped compared with its old cradle), horns out, 4 x M2 x 6 each from
  inboard. Cables not plugged in yet: the bus connectors face the back wall's window and can be
  plugged later from inboard with the battery out.
- [x] **3. Hubs and wheels on.** Done 2026-11-25: the wheels stayed on the horns through step 1
  (work at the bench edge, the wheel hangs 44 mm below the foot).
