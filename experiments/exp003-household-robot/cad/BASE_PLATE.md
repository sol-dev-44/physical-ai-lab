# Base plate: inputs

What the base plate has to carry, gathered 2026-11-19 under "Before designing a part" (cad/README).
Each number names its source. "On arrival" marks what no source gives: the part itself is the only
source, so check it when the 2026-11-21 to 23 order lands, and say why when asking.

## Plan layout (decided 2026-11-19: the widest stance)

The owner asked for the stoutest base, so the battery lies across between the servos.
`BaseLayout` and `derive_base` in `exp003_cad/params.py` hold the numbers and check them; tests
in `tests/test_exp003_base.py`.

| What | Value |
|---|---|
| Width over the tires | 330 mm (track 298 mm) |
| Base plate | 300 mm fore-aft x 262 mm across, one piece (H2D bed 325 x 320); stops 2 mm short of the wheels |
| Servos | Cradle backs 96 mm either side of the centre, leaving 20 mm for the plugs beside the battery. The two cradles are identical, so one servo's far end points back and the other's forward (corrected 2026-11-21: "both back" would need a mirrored cradle) |
| Battery | Across the robot, centred 40 mm behind the axle |
| Electronics deck | 80 to 185 mm behind the axle: Pi 5, servo driver, converters, INA226 |
| Caster | 158 mm behind the axle (from 165 on 2026-11-21, so the caster cup and its screws stay on the plate) |
| Front strip | 60 to 110 mm ahead of the axle: bumper and forward sensors |
| v2 arm base | 110 mm behind the axle, on a top deck |

Balance, from the masses in `BaseLayout` (battery 1.22 kg, the EP1210 sheet; the rest estimates):

| Case | Centre of mass | Meaning |
|---|---|---|
| v1 | 44.5 mm behind the axle; caster carries about 28% | Stable under braking; the wheels keep most of the weight for grip |
| v2, 1 kg arm at full forward reach | 18.1 mm behind the axle | Still does not tip forward. The README's tip test with a dummy weight decides |

## Height (decided 2026-11-21)

The caster measured 50 mm from the floor to the top of its plate. Two ways to hold the axle at 60 mm:

| Option | Plate | Caster | Verdict |
|---|---|---|---|
| Cradles on top of the plate | Top face 44.4 mm off the floor, underside 40.4 mm (4 mm plate) | Bolts into a raised pocket: its plate sits 9.6 mm above the underside, a boss 5.6 mm above the top | **Chosen:** lowest centre of mass (owner: "the stouter the better"), servos protected inside the plate's outline, 40 mm floor clearance |
| Cradles hung under the plate | Underside 75.6 mm off the floor | 25.6 mm spacer block | Higher centre of mass, servos exposed underneath |

Numbers come from `derive_heights` in `params.py` (tested). The caster wheel's top is 2.3 mm under
the plate. Still to settle when the plate is modelled:

- The pocket is a separate caster cup (`exp003_cad/caster_cup.py`) so the plate prints flat. The
  plate needs a hole the same shape as the cup's cavity: a box for the caster's plate plus a
  25.5 mm radius circle for the fork (the fork reaches 24 mm, measured 2026-11-21). The cup is
  27.5 mm in radius outside, so with the plate's back edge 190 mm behind the axle the caster
  must sit at least 163 mm behind it, not 165: move it to about 160 mm when the plate is modelled.
- Screws: M4 through the caster's holes (published holes are 4.2 to 5.3 mm) into heat-set
  inserts in the boss.

## The plate (modelled 2026-11-21)

`BasePlate` and `derive_base_plate` in `params.py`, the solid in `exp003_cad/base_plate.py`, tests
in `tests/test_exp003_base_plate*.py` (including the real cradle model placed on it: its ear holes
line up with the plate's, and the caster's fork swings clear through the plate).

| Feature | Where | Fastening |
|---|---|---|
| Plate | 300 x 261.6 x 4 mm PETG, 10 mm corners, printed underside down | |
| Servo cradles | Ear holes at (15.2, 107.25), (-40.2, 107.25), (-15.2, -107.25), (40.2, -107.25) | 4 x M3 x 12 button head down through ear and plate, nut under |
| Caster cup | Cutout the shape of the cup's cavity at 158 mm behind the axle; 4 holes at 45 degrees, 33 mm out | 4 x M3 x 16 up from under the plate through the cup's bosses, nut on the cup's roof |
| Battery | 3 mm corner fences round 154 x 68 mm (1 mm clearance), centred 40 mm behind the axle | Two hook-and-loop straps through four slots, front and back of the battery |
| Electronics deck | Grid of M3 holes on 20 mm centres, 95 to 175 mm behind the axle, clear of the caster | The deck (not designed yet) copies the grid |
| Bumper | Row of M3 holes 100 mm ahead of the axle, 30 mm apart | The bumper copies the row |
| Forward sensors | Row of M3 holes 75 mm ahead of the axle | Sensor brackets |
| Cliff sensors | Three 14 mm windows 88 mm ahead of the axle, at the centre and 105 mm out | Downward ToF sensors look through them |

Straps (measured 2026-11-21): 21.5 mm wide, 27.5 mm at the buckle. The slots are 24.5 x 4 mm, so
thread each strap's free end down through one slot, under the plate, up through the other, over
the battery and back through its buckle; the buckle never goes through a slot. The strap runs about
400 mm round the battery and plate, so check the straps are at least that long before relying on
them.

## Fixed by our own parts

| What | Value | Source |
|---|---|---|
| Wheel | 120 mm outside, 32 mm wide; axle 60 mm above the floor | `params.py` (`Tire`, `Wheel`) |
| Servo cradle | Axle 15.6 mm above the foot face; 65.4 x 31.2 x 22.5 mm with ears | `params.py` (`Cradle`), build output |
| Wheel inner face | 34.3 mm from the servo's bottom step face (36.8 from the cradle's back) | `derive_cradle` (`hub_face_c_mm`) |
| Keep clear | 2 mm below the hub face inside the wheel's 60 mm radius; 2 mm behind the cradle's back wall (screw heads, idler disc) | cad/README |

## From published sources

| Part | Dimension | Value | Confidence | Source |
|---|---|---|---|---|
| ExpertPower 12V 10Ah LiFePO4, EP1210 (model on its label, 2026-11-21) | L x W x H | 152 x 66 x 94 mm; 99 mm over the terminals | High | [EP1210 sheet](https://cdn.shopify.com/s/files/1/2364/9089/files/EP1210-4S.pdf) |
| | Weight | 1.22 kg | High | same |
| | Terminals | F2 (6.35 mm spade) on the top face at one short end: + (red) at the label side, - (black) at the back | High (owner's photo, sheet) | same |
| | Current | 10 A continuous, 15 A for 5 s; charge 14.4 V CV, 5 A recommended | High | label and sheet |
| | Terminals | F2 tabs on top, along one long edge | Medium | same (drawing) |
| Raspberry Pi 5 | Board, holes | 85 x 56 mm; holes 58 x 49 mm, 3.5 mm from the edges, 2.7 mm | High | [Raspberry Pi mechanical drawing](https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008347-DS-1-raspberry-pi-5-mechanical-drawing.pdf) |
| | Active Cooler | 63.5 x 42.5 mm, 13.7 mm tall | High | [Raspberry Pi drawing, via ELV](https://media.elv.com/file/253864_bauzeichnung.pdf) |
| Servo driver board | Board, holes | 42 x 33 mm; 2.5 mm holes at 37 x 28 (if it is the Waveshare Bus Servo Adapter (A) design) | Medium | [Waveshare](https://www.waveshare.com/bus-servo-adapter-a.htm) |
| UCTRONICS 5V buck | Board | 63 x 27 x 10 mm, open board, no screw holes reported | Medium | [UCTRONICS](https://www.uctronics.com/amp/uctronics-dc-6v-9v-12v-24v-to-dc-5v-5a-buck-converter-module-9-36v-step-down-to-usb-5v-transformer-dual-output-voltage-regulator-board-2-pack.html) |
| DROK 12V buck-boost | Case | 39 x 57 x 22 mm (model 200494) | Low | retailer snippet |
| INA226 20A module | Board | about 26 x 22 mm (a similar module) | Low | [Tinytronics](https://www.tinytronics.nl/shop/en/sensors/current-voltage/ina226-i2c-dc-current-and-voltage-meter-20a-module) |
| E-stop | Panel hole | 22 mm | Medium | listing title |
| Casters (VXB, 1.5 in PU) | Wheel, rating | 1.5 in wheel; 100 lb per 4 | High | [bearingscanada](https://bearingscanada.com/products/1-5-casters-set-of-8-swivel-plate-un) |
| Bambu H2D | Build area | 325 x 320 mm on one nozzle | High | [Bambu tech specs](https://bambulab.com/en/h2d/tech-specs) |

## On arrival (no source gives these)

- **Caster:** measured 2026-11-21 (`Caster` in `params.py`): 50 mm floor to the top of its plate;
  plate 46 x 38.25 mm, its long ends concave to 40.5 mm across the middle; holes on 35.75 x 27.75 mm
  centres (the common 46 x 38 plate is 36 x 28, [Tente 1430 sheet](https://media.tente.com/en-us/pdf/17/1/1430POI038P60-46x38_EN.pdf));
  swivel offset 13 mm, so the wheel sweeps a 32 mm radius.
- **Battery:** settled 2026-11-21 from the label and a photo: an EP1210, terminals on top at one
  short end, so no wire passes through the plate and the plate only needs the 152 x 66 mm
  footprint and straps. Put the terminal end on the side the wiring runs to (the electronics deck
  is behind it either way).
- **DROK, UCTRONICS, INA226, servo driver:** outline and mounting holes or tabs.
- **Rocker switch, DC jack:** panel cutout (the switch model is not identified).
