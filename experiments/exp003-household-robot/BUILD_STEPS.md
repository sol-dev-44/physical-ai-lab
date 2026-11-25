# exp003 build steps

The owner's physical build, one step at a time. The `build-step` skill
(`.claude/skills/build-step/SKILL.md`) reads this file, gives the next open step with a
diagram, and ticks steps off when the owner reports them done. Numbers come from the CAD
(`cad/exp003_cad/params.py`) and the notes linked on each step; never ask the owner to measure
them.

Frame: x forward, y left, z up from the plate's top face. Front = the plate end with the two
rows of bumper holes; the caster is at the back.

## Wheel module v2 onto plate v1 ([cad/WHEEL_MOUNT.md](cad/WHEEL_MOUNT.md))

- [ ] **2. Bolt the module to the plate.** Feet first (8 x M3 x 12), then the beam (7 x M3 x 16,
  heads down the counterbores); nuts under the plate.
- [ ] **4. Load check** (README "Next" 3): under 0.5 degrees of lean with 1 kg extra, no change
  after 10 drops and 24 h loaded.

## Done

- [x] **0. Drill plate v1 for the module (15 holes).** Done 2026-11-25 (owner). Feet at
  x 5 and -46 (y 85, 105, 124), beam at x 23.2 (y 0, 42, 85, 124), each side; 1/8 inch bit
  with the module as the template.
- [x] **1. Fit the servos into the module.** Done 2026-11-25 (owner). Both bodies point to the
  rear (the right servo flipped compared with its old cradle), horns out, 4 x M2 x 6 each from
  inboard. Cables not plugged in yet: the bus connectors face the back wall's window and can be
  plugged later from inboard with the battery out.
- [x] **3. Hubs and wheels on.** Done 2026-11-25: the wheels stayed on the horns through step 1
  (work at the bench edge, the wheel hangs 44 mm below the foot).
