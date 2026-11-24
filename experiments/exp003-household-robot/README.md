# exp003: household robot

**Goal:** a small Wi-Fi robot that lives with the family. It knows each family member and the pets,
talks with each of them in a way that suits them, remembers them and the house, keeps to the
household's rules about where it may go and when, and can be driven by remote.

- **v1:** the rolling robot. Drives on carpet and hard floor without hitting anything, converses,
  recognizes people and pets, remembers, follows household rules, goes where it is told by voice,
  and ends with a vision-language-action (VLA) policy trained on its own driving.
- **v2:** adds an arm (or two) to pick up light toys and put them away.

**Status (2026-11-23, evening):** the chassis is assembled, but the wheel mounts failed the
dry fit: under the robot's weight the servo cradles roll over and the wheels lean in. The cause
is two bolts on one line beside the edge the cradle tips about, and walls loaded across their
print layers. The fix is a wheel module v2: a boxed servo mount on a wide six-bolt foot, an axle
beam tying left and right together, and a base plate v2 with the new holes
([cad/WHEEL_MOUNT.md](cad/WHEEL_MOUNT.md)). All three electronics deck parts are printed and
dry-fitted ([cad/DECK.md](cad/DECK.md)). They bolt to plate v2, which keeps the same grid. The
robot console (phone control app, [CONTROL_APP.md](CONTROL_APP.md)) step 1 is built and runs on
simulated wheels.

**Next, in order:**

1. Keep the weight off the wheels until the new mounts are in, so the old cradles do not creep.
2. Wheel module v2 is modelled (2026-11-24): both servo boxes and the beam in one PETG piece,
   checked at 5 x the static load ([cad/WHEEL_MOUNT.md](cad/WHEEL_MOUNT.md), "Stage 1 as
   modelled"). Print the fit coupon (14 g), then the module (about 190 g, front face down, 6
   walls, 40% infill) and plate v2 (about 225 g).
3. Rebuild the chassis on plate v2 and pass the load check: under 0.5 degrees of lean with 1 kg
   extra, and no change after 10 drops and 24 h loaded.
4. Bolt the deck to plate v2 in the assembly order in [cad/DECK.md](cad/DECK.md).
5. Power harness: the wiring diagram first, then soldering once the kit lands (2026-11-25 to 27;
   see [docs/inventory.md](../../docs/inventory.md)).
6. Phase 0 bench test of the servos in wheel mode. It does not need the chassis, so it can run
   in between.
7. Before the v2 arm, or sooner if step 3 shows lean inside the servo: a 6806 bearing so the
   servo only drives and the box carries the weight (stage 2 in WHEEL_MOUNT.md). The bearings and
   the 3-spool PETG order are in "Orders to place".

Nothing here runs against hardware yet. Photos and personal data are the
owner's call ([ADR 0013](../../docs/adr/0013-owner-governs-personal-data.md)).

## Design: the body

- **Drive:** two STS3215 12V servos in wheel mode (the lab's spares), 120 mm wheels (PETG hub,
  TPU tire), one 1.5" swivel caster at the back. Works on carpet and hard floor. About 0.28 m/s at
  12V, measured on the bench before anything else.
- **Compute:** Raspberry Pi 5 on the robot for motors, sensors and the safety gate. The Mac does
  speech-to-text, recognition, vision and policy inference over Wi-Fi. Conversation goes through the
  Claude API.
- **Power:** 12.8V 10Ah LiFePO4 pack (about 128 Wh, ExpertPower EP1210, 1.22 kg) with a BMS. Main
  switch and 10A fuse, then an INA226 fuel gauge. Motor rail: e-stop, 12V buck-boost, 5A fuse.
  Compute rail: 5V 5A buck to the Pi. The e-stop cuts motor power only, so the Pi stays up and logs
  what happened. Estimated run time: about 6 h of active play, 8.5 h of chatting, 20 h listening.
  The 2A charger refills it in about 5.5 h; self-docking comes with mapping.
- **Sensing:** three forward ToF sensors in a soft TPU bumper, two bumper switches, two or three
  downward ToF cliff sensors (infrared reflectance sensors mistake dark carpet for a drop), a
  front camera (Logitech C920x), and later a 2D LiDAR.
- **Audio:** reSpeaker XVF3800 mic array on top of the head, small speaker.
- **Connectivity:** the Pi 5's on-board dual-band Wi-Fi is the main link (to the Mac and for the
  control app; use 5 GHz, since Wi-Fi and Bluetooth share one radio). The Xbox controller pairs
  over the Pi's Bluetooth 5.0. Losing either link stops the wheels.
- **Control app:** the robot serves a web app on the home network: drive (joystick or Xbox
  controller), live sensors, a live camera view for debugging (never saved), the event log and the
  lab's inventory. Design: [CONTROL_APP.md](CONTROL_APP.md).
- **Privacy mode:** a mic mute and a printed camera shutter that the gate can see, and a light that
  shows when the robot is listening.

## Design: who it knows and how it behaves

Recognition and memory run on the lab machine and the robot, and their data is kept in a local
store by default. The Claude API gets the person's name and role and a few relevant memories.
What gets saved, shared or published is the owner's call (ADR 0013); nothing personal goes in
this repo or on the site unless the owner puts it there.

- **Recognition.** Face and voice together, on device, from live frames that are then dropped.
  Pets by species detection plus appearance. Anyone not recognized with confidence is a guest.
  Candidates to compare: Apple Vision or an ArcFace-family model for faces, an ECAPA speaker
  embedding for voices, a YOLO detector for people and pets.
- **Profiles.** Each person has a role (parent, child, guest) and style settings a parent can edit.
  Starting defaults:

| Who | Tone and content | Movement |
|---|---|---|
| Child | Playful, short sentences, patient; asks questions back; age-appropriate topics only; honest that it is a robot; sends worries and big questions to a parent | Slower near the child; never blocks a doorway |
| Parent | Concise and direct; status reports; can ask anything the robot can do | Normal |
| Pet | Calm voice or silent | Keeps about 1 m away, never chases, slows when a pet is near |
| Guest or unknown | Polite and generic; nothing personal about the household | Normal, cautious |

- **Memory.** After an interaction the robot writes short notes about that person: facts ("likes
  dinosaurs"), preferences, one-line summaries of what happened. No transcripts, no audio. Parents
  can review, edit and delete memories on the lab machine; anyone can say "forget that". A child's
  event memories expire after 90 days unless a parent pins them. The robot never repeats one
  person's memories to another, except to parents about a child.
- **Household rules.** Built on the map: named rooms, no-go zones (stairs, bathrooms), zones by time
  (bedrooms at night), quiet hours, and what each role may ask for (a child can call the robot over,
  but can't send it into a no-go zone or change a rule). Rules are enforced by the safety gate as
  interlocks, and changed only by a parent on the lab machine, never by voice alone.

## Design: ready for v2

v2 mounts an SO-101 follower arm on the top deck (the lab's second SO-ARM101 pair is the candidate;
its leader records teleop demos). v1 leaves room for it:

- The top deck carries the SO-101 base bolt pattern and a fused 12V tap for the arm.
- Weight and balance are budgeted for about 1 kg of arm reaching forward. Before v2 starts, a tip
  test with a dummy weight decides whether the two-wheel base needs a wider stance or outriggers.
- The arm only moves light toys (under about 150 g) into a bin, and an interlock stops it whenever a
  person or pet is within reach.
- exp002's lessons apply: trim idle frames, audit data and checkpoints before training.

## Rules this experiment adds

- **The safety gate runs on the robot.** A lab-agent on the Pi is the only path to the motors.
  Losing Wi-Fi means stop. (ADR to write before phase 1.)
- **Remote driving goes over a private VPN (Tailscale), not the website.** The web stays
  queue-only (ADR 0003). (ADR to write before phase 4.)
- **Photos, recordings and personal data are the owner's call** (ADR 0013). Wake word and
  speech-to-text run locally by default.

## Phases

### v1

| # | Phase | Done when |
|---|---|---|
| 0 | Bench: Xbox controller and the control app's Drive screen drive two servos in wheel mode with a dead-man (drive lease); voice loop on the Mac | Both work for 10 minutes; releasing the button, closing the tab or dropping Wi-Fi stops the wheels |
| 1 | Chassis printed and assembled, teleop over Wi-Fi | 10 minutes of driving; dead-man and e-stop both stop it |
| 2 | Safety interlocks: bumpers, forward ToF, cliff, speed cap about 0.3 m/s, battery | Stops before a box 20/20; stops at a test edge 10/10 |
| 3 | Voice on the robot: one guest-level personality, parent controls, privacy mode | 15-minute conversation; no audio leaves the house; mute stops listening 10/10 |
| 4 | Remote driving over Tailscale | Stops within 300 ms when the link drops |
| 5 | Mapping with LiDAR, named places, self-docking | Reaches a named place 9/10 from 3 starts; docks 9/10 |
| 6 | Household rules: zones, time zones, quiet hours, as gate interlocks | Refuses to enter a no-go zone 20/20; silent in quiet hours |
| 7 | Recognition of family and pets | Right person or pet in at least 95 of 100 encounters; mistakes one family member for another at most once; strangers treated as guests 20/20 |
| 8 | Per-person behaviour and memory | A parent can tell from transcripts whom the robot was talking to, 9/10; "forget that" works 10/10; never reveals one person's memories to another across 20 probing prompts |
| 9 | Voice-commanded navigation with role permissions | "Go to the couch" works 9/10; a child's request into a no-go zone is refused 10/10 |
| 10 | VLA trained on teleop demos with spoken instructions | Beats a scripted baseline on a fixed test |

### v2

| # | Phase | Done when |
|---|---|---|
| 11 | Arm on the deck, teleop with the leader arm, reach interlock | Tip test passes; arm stops within 0.5 s when a person comes within reach, 10/10 |
| 12 | Tidy-up demos ("put the blocks in the bin") and a trained policy | Policy picks and places a known toy 8/10 from fixed starts |
| 13 | Autonomous tidy-up: find toys on the map, drive, pick, place | Clears 5 scattered toys into the bin in one run, 4/5 runs |

## Printed parts

See [cad/README.md](cad/README.md). Measurements: [cad/MEASURING.md](cad/MEASURING.md) and
`cad/servo.toml`; the STS3215 model is in [cad/vendor/](cad/vendor/README.md).

| Part | Material | Status |
|---|---|---|
| Hub coupon v1 (recess round the horn) | PETG | Printed 2026-11-18; too close to the case, retired |
| Hub coupon v2 (flat seat) | PETG | Printed 2026-11-19; kept as the fit gauge and phase 0 spin indicator |
| Wheel hub x 2 | PETG | Printed 2026-11-19; fit and spin true |
| Tire x 2 | TPU 95A | Printed 2026-11-21 (8 h 8 min, 105 g), right hotend through the rear TPU inlet; fit snug, first try |
| Servo cradle x 2 | PETG | Both printed and fitted 2026-11-19 (34 min, 10.0 g each). Failed under load 2026-11-23: they roll over under the robot's weight; replaced by wheel module v2 ([cad/WHEEL_MOUNT.md](cad/WHEEL_MOUNT.md)) |
| Caster cup v1 (test piece) | PETG | Printed 2026-11-21 (24 min 47 s, 8.3 g), first print from the AMS on the left nozzle. Plate and holes fit; the fork hit the walls |
| Caster cup v2 (round cavity for the fork) | PETG | Light fit test printed 2026-11-21 (22 min 30 s, 5.4 g) and passed: the fork swivels clear all the way round. Full-strength cup with mounting bosses printed 2026-11-21 (33 min, 12 g) but 4 mm too tall |
| Caster cup (corrected, 8.6 mm) | PETG | Printed 2026-11-22 (27 min 24 s, 9.9 g, 4 walls, 30% infill) and fitted with M3 x 16 to the plate: the plate sits level |
| Base plate | PETG | Printed 2026-11-21 (4 h 56 min, 223 g, 4 walls, 30% infill; [cad/BASE_PLATE.md](cad/BASE_PLATE.md), "The plate"); cradles and caster cup fitted, level on the floor |
| Electronics deck fit coupon | PETG | Printed 2026-11-23 (27 min 46 s, 8.85 g): the rocker snaps in, the M2.5 boss holds, the UCTRONICS slides into a 27.6 mm channel ([cad/DECK.md](cad/DECK.md)) |
| Deck power tray (with switch panel) and servo bridge | PETG | Printed 2026-11-23 together (1 h 38 min, 34.78 g, 4 walls, 30% infill); dry-fitted, bolt to plate v2 |
| Compute tray | PETG | Printed 2026-11-23 (42 min 16 s, 17.44 g, 4 walls, 30% infill); dry-fitted, bolts to plate v2 |

## Progress log

- 2026-11-17: design chosen (two-wheel plus caster for carpet and hard floor, LiFePO4 battery).
  Parametric hub and coupon modelled in CadQuery; `servo.toml` holds placeholders until measured.
- 2026-11-17: scope widened to a household robot (recognition, per-person behaviour, memory,
  household rules) with a v2 arm for tidying toys. Privacy rules handed to the owner (ADR 0013,
  superseding 0007 and 0012); folder renamed from `exp003-home-robot`.
- 2026-11-17: horn measured on a spare STS3215 (19.9 mm aluminium horn, 4 M3 holes on 13.6 mm,
  centre screw 2 mm proud). Hub web thickened so the centre pocket stays below the screw
  counterbores. Coupon ready to print.
- 2026-11-18: the lab's screw kit is button head with M3 only from 8 mm, so the model now takes the
  screws on hand (`[screws]` in `servo.toml`) and thickens the web (7.95 mm) until an M3 x 8 stops
  0.5 mm short of the servo case. Fixed with 4 x M3 x 8 button head.
- 2026-11-18: H2D set up (firmware 01.04.20.00, AMS 2 Pro on the right nozzle). First print: the
  hub coupon in PETG Basic, servo side down, 0.2 mm layers, 4 walls, 30% infill, no supports,
  textured PEI plate (22 min, 8.3 g). Snug fit on the horn with 4 x M3 x 8 button head and the
  default 0.2 mm clearance; screws pull it flat and it spins free. But it cleared the servo by
  only about two sheets of paper (design: 2.5 mm): the case is low round the shaft, and a raised
  block under the label starts right at the horn's edge, 2.0 mm below the horn top (new
  measurement I, `raised_case_mm`). A 1.5 mm recess wrapping round the horn left 0.5 mm over it.
- 2026-11-18: hub redesigned to sit flat on the horn's top face, centred by the centre pocket
  (5.4 mm over the 5.0 mm screw head) and the screws. It now clears the case by 2.0 mm, the new
  minimum (it was 1.0); the model steps the underside up beyond the horn if a case needs more.
  Web 6.45 mm, still 4 x M3 x 8. Reprint the coupon to confirm before the full hub.
- 2026-11-19: coupon v2 (flat seat) printed in PETG (20 min, 7.2 g) and fits well on the horn.
  Kept as the fit gauge and phase 0 spin indicator. Next: two full wheel hubs.
- 2026-11-19: both full wheel hubs printed together in PETG, servo side down, no supports
  (2 h 44 min, 118.5 g). Clean prints; each seats on the horn like the coupon and spins true
  without touching the case. Next: the TPU tire, once the TPU arrives.
- 2026-11-19: STS3215 CAD model vendored from The Robot Studio's SO-ARM100 repo (Apache-2.0) in
  `cad/vendor/`. A caliper on a spare confirmed the case (45.4 x 24.8 mm) and the top mounting
  holes (20.7 x 20.4 mm centre to centre) exactly; the horn differs by 0.3 to 0.5 mm, so the hub
  keeps its measured numbers. The idler disc on the bottom stands about 4.1 mm proud of the case
  bottom round the shaft, so anything under the servo needs a pocket. Case numbers in
  `servo.toml` `[case]`, checked by the tests.
- 2026-11-19: TPU tire modelled (`cad/exp003_cad/tire.py`): a 120 mm ring with a 107 mm bore that
  grips the 108 mm rim seat (0.9% stretch) and a lip over each flange, 0.2 mm clear, so it cannot
  walk off sideways. Fitting it means stretching 3.7% over one flange. Tests check the only
  contact with the hub is the grip band on the seat. Prints flat in TPU 95A, no supports.
- 2026-11-19: printed rim measured across the top flange (110.6 mm, design 111.0), so the seat is
  about 107.6 mm. The tire's bore is now sized to it (106.6 mm, `[tire]` in `servo.toml`).
- 2026-11-19: full survey of the STS3215 model after a bracket was pitched for the top holes
  without checking the rest of the case. The bottom has its own four holes (24.5 x 20.5 mm,
  confirmed present), the two bus connectors, a step and a raised pad. All recorded in
  `cad/vendor/README.md` and `servo.toml`; a "Before designing a part" checklist now gates every
  printed part (cad/README, pointed to from AGENTS.md).
- 2026-11-19: servo cradle modelled (`cad/exp003_cad/cradle.py`), following the new checklist. It
  holds the servo by its bottom holes because the top holes sit only about 2.5 mm under the
  spinning hub. It is a U: the back wall has four 0.5 mm pads and one opening for the idler
  disc, connectors and pad; cheeks hug the case 0.2 mm clear; the lower cheek is the foot, with
  M3 ears. The supplied M2 x 6 screws go 3.5 mm into the case. Tests load the vendored servo
  model into the cradle and find no clashes; the clash check fails as it should on a servo
  lowered 0.6 mm. The wheel axle sits 15.6 mm above the foot, which the base plate will need.
- 2026-11-19: servo cradle sent to print in PETG (34 min, 10.0 g). Base plate inputs gathered with
  sources in `cad/BASE_PLATE.md`; the caster's mounting height is not published anywhere and is
  measured on arrival. Owner chose the widest stance: battery across between the servos, 330 mm
  over the tires, a 300 x 262 mm one-piece plate. Balance check: centre of mass 46 mm behind the
  axle, 18 mm with a 1 kg v2 arm at full forward reach.
- 2026-11-19: the first servo cradle is printed and fitted. The servo slides in well, sits flat
  on the pads and holds solid with the supplied M2 x 6 screws. The loose metal idler disc on the
  servo's bottom comes off first (only a two-sided bracket holds it) and goes with the spares.
  The second cradle printed and fitted perfectly too: both wheel servos are in their cradles.
- 2026-11-20: most of the 2026-11-17 order arrived (Pi 5, XT60s, fuses and limit switches due
  2026-11-21). The two TPU tires are printing on the right hotend: TPU 95A goes through the rear
  TPU inlet once the right hotend's tube is moved there from the AMS buffer (Bambu's H2 TPU guide).
  Generic TPU profile, 3 walls, 25% gyroid, 8 h 8 min, 105 g.
- 2026-11-21: both tires printed cleanly and fit the hubs snugly on the first try, with the bore
  sized to the caliper reading of the printed rim (107.6 mm seat, 1.0 mm interference). Both
  wheels are complete. No reprint needed. The printer is now laid out with the AMS on the left
  nozzle and the right nozzle kept for TPU (docs/printing.md), so the bumper prints with no tube swap.
- 2026-11-21: caster measured (50 mm to the top of its plate, holes on 36 x 28 mm centres). That
  settles the base plate's height: the cradles sit on top of the plate, whose top face is 44.4 mm
  off the floor, and the caster bolts into a raised pocket (`cad/BASE_PLATE.md`, "Height"). The
  bumper waits until the plate is modelled.
- 2026-11-21: the caster's raised pocket is a separate light cup (`cad/exp003_cad/caster_cup.py`), so the
  base plate can print flat. The cup is printing as the fit test: the caster's plate must drop
  in and the fork must swivel clear of its walls.
- 2026-11-21: first cup fitted. The caster's plate drops in (slight play) and the holes line
  up, but the fork hits the walls when it swivels. Its sweep was never measured; it reaches 24 mm
  from the swivel axis. Cup v2 adds a 25.5 mm radius circle to the cavity.
- 2026-11-21: cup v2 (light fit-test version) passed: the caster's plate drops in, the holes line
  up, and the fork swivels clear all the way round. The caster mount is settled; the base plate
  takes a matching hole.
- 2026-11-21: battery confirmed as an EP1210 from its label. Its F2 spade terminals sit on top
  at one short end, so the base plate needs only the footprint and straps. 6.3 mm female spade
  terminals are not on hand: ordered the same day (AIRIC 100-pack, due by 2026-11-25).
- 2026-11-21: base plate modelled. It holds the cradles, the caster cup (now bolted to the plate
  through four bosses), the battery with fences and strap slots, and hole patterns for the
  electronics deck, bumper, forward sensors and cliff sensors. Every screw is M3 or M4 with a nut.
  Checking it against the real cradle model caught a layout error: two identical cradles cannot
  both point their servos' far ends back, so one points forward. The caster moved to 158 mm behind
  the axle to keep the cup on the plate.
- 2026-11-21: battery straps measured (21.5 mm wide, 27.5 mm at the buckle); the strap slots are
  sized to the strap, threaded free end first. The plate is ready to print.
- 2026-11-21: base plate printed (4 h 56 min, 223 g PETG). Next: fit the cradles, the battery and
  the caster cup (still to print at full strength).
- 2026-11-21: robot console step 1 built on fake wheels (CONTROL_APP.md, ADR 0014): the robot's
  agent serves a phone app on the home network; hold-to-drive with a 300 ms lease, a watchdog stop,
  one driver at a time, pairing by link, fake sensor readings marked "no sensor". Each task had a
  spec and a code review; the reviews found and fixed a dozen ways the wheels could have been left
  turning (refused, dropped or failed commands, reconnects, a second phone) before any real wheel.
- 2026-11-21: chassis assembled. Both cradles bolted to the plate (4 x M3 x 12 and nuts; the
  two servos point opposite ways, as identical cradles must), the caster bolted into the full
  cup (M4 x 12 stood well proud of the nuts, so M4 x 8) and the cup bolted to the plate. On the
  floor the robot leaned back toward the caster: the cup's cavity had been sized as if the cup
  started at the plate's underside, but it sits on the top face, so the plate's 4 mm was counted
  twice and the caster sat 4 mm high. The model is fixed (cup 8.6 mm tall, M3 x 16 to the plate)
  with a test that the plate, cup and caster heights add up; the corrected cup prints tomorrow.
  The printer is busy with a toy garbage truck.
- 2026-11-22: corrected caster cup printed (27 min 24 s, 9.89 g PETG) and fitted: the caster
  into the cup with its 4 x M4 x 8, the cup to the plate with 4 x M3 x 16 and nuts. The robot
  now sits perfectly level on the floor. The chassis is done.
- 2026-11-22: the Pi 5, XT60 leads and fuse assortment (arrived 2026-11-21) are logged; the
  limit switches are still to come. The build page and site log are brought up to date.
- 2026-11-23: electronics deck designed ([cad/DECK.md](cad/DECK.md)) and printed. A fit coupon
  settled the rocker cutout, the M2.5 standoff boss and the UCTRONICS channel first. Three parts:
  the compute tray (Pi 5 on 11 mm standoffs, the UCTRONICS behind it), a bridge over the caster
  cup for the servo board, and the power tray (DROK on slotted pads, INA226, fuse ties, switch
  and charge-socket panel). The power tray and bridge are printed; the compute tray followed the same evening. The e-stop moved to v2: v1 runs only under the owner's supervision,
  and the main rocker is its one hardware cut. Soldering and wiring tools ordered; next is a dry
  fit of all three parts, then the power harness.
- 2026-11-23: in the evening all three deck parts were dry-fitted on the plate. A CAD overlay on the
  owner's top-view photo matched the layout; the servo board and the INA226 each turn half a
  turn, and the assembly order is written up in [cad/DECK.md](cad/DECK.md). Then the wheels were
  found "bending". The +y cradle had rolled about the inboard edge of its foot, the servo's outer
  end lifted and the wheel leaned in.
  - Cause: each cradle's two bolts sit on one line 11 mm from that edge while the tire pushes
    53 mm out (a 4.7 to 1 lever), and the cheeks take the bending across their print layers.
  - Plan: wheel module v2, with a boxed servo mount on a wide six-bolt foot (printed on its end),
    an axle beam tying the two sides together, and a base plate v2. Later, a 6806 bearing so the
    servo only drives.
  - A ninth checklist rule: trace the load path ([cad/WHEEL_MOUNT.md](cad/WHEEL_MOUNT.md)).
  - The deck waits for plate v2.
- 2026-11-24: wheel module v2 modelled: both servo boxes and the axle beam in one PETG piece, both servos' far ends back, 15 x M3 to a new plate v2. The owner asked for it "hella sturdy", so every check runs at 5 x the static load with the v2 arm reaching forward (73 N a wheel): lever 1.6 to 1 (the cradles were 4.7), 57 N on each outboard bolt, 0.5 MPa in the walls. The wall under the case stays 3 mm so the axle keeps its height. A 14 g coupon checks the servo fit first.
