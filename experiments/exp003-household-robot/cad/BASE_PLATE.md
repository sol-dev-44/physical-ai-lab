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
| Servos | Far end pointing back; cradle backs 96 mm either side of the centre, leaving 20 mm for the plugs beside the battery |
| Battery | Across the robot, centred 40 mm behind the axle |
| Electronics deck | 80 to 185 mm behind the axle: Pi 5, servo driver, converters, INA226 |
| Caster | 165 mm behind the axle |
| Front strip | 60 to 110 mm ahead of the axle: bumper and forward sensors |
| v2 arm base | 110 mm behind the axle, on a top deck |

Balance, from the estimated masses in `BaseLayout` (battery at its low 1.07 kg):

| Case | Centre of mass | Meaning |
|---|---|---|
| v1 | 46 mm behind the axle; caster carries about 28% | Stable under braking; the wheels keep most of the weight for grip |
| v2, 1 kg arm at full forward reach | 18 mm behind the axle | Still does not tip forward. The README's tip test with a dummy weight decides |

## Height (decided 2026-11-21)

The caster measured 50 mm from the floor to the top of its plate. Two ways to hold the axle at 60 mm:

| Option | Plate | Caster | Verdict |
|---|---|---|---|
| Cradles on top of the plate | Top face 44.4 mm off the floor, underside 40.4 mm (4 mm plate) | Bolts into a raised pocket: its plate sits 9.6 mm above the underside, a boss 5.6 mm above the top | **Chosen:** lowest centre of mass (owner: "the stouter the better"), servos protected inside the plate's outline, 40 mm floor clearance |
| Cradles hung under the plate | Underside 75.6 mm off the floor | 25.6 mm spacer block | Higher centre of mass, servos exposed underneath |

Numbers come from `derive_heights` in `params.py` (tested). The caster wheel's top is 2.3 mm under
the plate. Still to settle when the plate is modelled:

- The pocket's footprint: it must take the caster's plate (46 x 38 mm) and whatever of the
  swivel and fork sweeps above the plate's underside. The wheel sweeps a 32 mm radius circle but
  stays below the plate; the fork's sweep radius is not published. With the caster at 165 mm
  behind the axle a boss much over 25 mm in radius runs off the 190 mm back edge, so move the
  caster forward a little if the pocket needs more room.
- Screws: M4 through the caster's holes (published holes are 4.2 to 5.3 mm) into heat-set
  inserts in the boss.

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
| ExpertPower 12V 10Ah LiFePO4 (taken to be the EP1210) | L x W x H | 152 x 66 x 94 mm; 99 mm over the terminals | High for EP1210; the ASIN's model is inferred | [EP1210 sheet](https://cdn.shopify.com/s/files/1/2364/9089/files/EP1210-4S.pdf) |
| | Weight | 1.22 kg on the sheet (inventory says 1.07) | High for EP1210 | same |
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
- **Battery:** which long edge the terminals are on; weigh it (1.07 or 1.22 kg).
- **DROK, UCTRONICS, INA226, servo driver:** outline and mounting holes or tabs.
- **Rocker switch, DC jack:** panel cutout (the switch model is not identified).
