# Electronics deck: inputs

Gathered 2026-11-23 under "Before designing a part" (cad/README), before any modelling. Each
number names its source. Confidence: High = maker drawing or datasheet, Medium = retailer spec or
maker photo, Low = scaled from a photo or a similar part.

## Space

From `derive_base_plate` (params.py), axle at x = 0, + forward, y across (+ is the robot's left):

| What | Where |
|---|---|
| Deck zone | x -80 to -190 (battery fence to the plate's back edge), y +-128 (plate half width 130.8) |
| Battery | Box x -74 to -6, y +-77; 94 mm tall, 99 over the terminals (top 143 mm off the floor) |
| Rear strap slots | x -80.5 to -76.5, y +-27.8 to +-52.2: keep clear, the straps rise there |
| Caster cup | Centre (-158, 0), 27.5 mm radius, 8.6 mm tall on the plate top; M3 nuts on its roof at (-181.3 / -134.7, +-23.3) |
| Deck grid | M3 holes on 20 mm centres at x -95, -115, -135, -155, -175; y -100 to 100; none within 42 mm of the caster axis |
| Wheels | x -60 to +60, so the deck zone is clear of them |

## Parts (research 2026-11-23)

| Part | Key numbers | Mounting | Confidence | Source |
|---|---|---|---|---|
| Raspberry Pi 5 | 85 x 56 mm; holes 58 x 49, 3.5 mm in, 2.7 mm (M2.5). USB-C power and 2 micro-HDMI on one long edge; USB/Ethernet stack on a short edge, about 3 mm overhang; GPIO along the other long edge; PCIe FPC on the other short edge; microSD underneath at the PCIe end | M2.5 standoffs | High | [RP-008347 drawing](https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008347-DS-1-raspberry-pi-5-mechanical-drawing.pdf) |
| Pi 5 Active Cooler | 63.5 x 42.5 x 13.7 mm, 30 mm blower; the heatsink must touch nothing | On the Pi | High | [cooler brief](https://pip-assets.raspberrypi.com/categories/993-raspberry-pi-active-cooler/documents/RP-008188-DS-2-raspberry-pi-active-cooler-product-brief.pdf) |
| Pi 5 power | Wants 5 V 5 A over USB PD. Without PD it limits USB to 600 mA. Fix for a non-PD supply: `PSU_MAX_CURRENT=5000` in the bootloader EEPROM (also turns on `usb_max_current_enable`) | | High | [USB PD white paper](https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-009856-WP-1-USB%20Power%20delivery%20on%20Raspberry%20Pi%205.pdf) |
| Servo board: Waveshare Bus Servo Adapter (A) v1.1 | 42 x 33 mm (one shop says 34); 2.5 mm holes at 37 x 28. Two servo sockets on one long edge; USB-C and a 5.5 x 2.1 jack overhang the other long edge, a 2-pin screw terminal between them; 9 to 12.6 V. **Jumper on B** for USB from the Pi | M2.5 | High (drawing); Medium that the ASIN is this board | [Waveshare drawing](https://www.waveshare.com/img/devkit/accBoard/Bus-Servo-Adapter-A/Bus-Servo-Adapter-A-details-size.jpg?v=26061501), [wiki](https://www.waveshare.com/wiki/Bus_Servo_Adapter_(A)) |
| UCTRONICS 5.2 V buck (U6223, 2-pack) | 63 x 27 x 10 mm. In: 5.5 x 2.1 jack + screw terminal on one short end. Out: USB-A + screw terminal on the other. No USB-C, no PD. No mounting holes | Cradle and tie | High (size), Medium (ends) | [UCTRONICS](https://www.uctronics.com/uctronics-dc-6v-9v-12v-24v-to-dc-5v-5a-buck-converter-module-9-36v-step-down-to-usb-5v-transformer-dual-output-voltage-regulator-board-2-pack.html) |
| DROK 9-36 V to 12 V 5 A (200494) | 57 x 39 x 22 mm without ears; an ear on each 39 mm end, 4.1 mm holes, about 61 mm apart (scaled). All 4 leads leave one 57 mm face, about 17 AWG; potted, IP67 | M4 or M3 through the ears; slots cover the scaled spacing | High (case), Low (spacing) | [DROK](https://www.droking.com/all-items/Power-supply-conversion/dc-boost-buck/dc-boost-buck-converter-9v-36v-to-12v-5a-60w-stabilizer-waterproof-car-auto-step-up-down-led-display-regulator) |
| INA226 "20 A" module | About 27 x 20 mm (or 26 x 22). Screw terminals VIN, GND, GND, VOUT on one short edge; I2C header on the other. Shunt R010 in most photos: then it reads up to about 8 A, enough for the 10 A main fuse's normal load | Pocket and tie (holes only scaled) | Medium / Low | [AliExpress](https://www.aliexpress.us/item/3256805187560537.html), [Tinytronics](https://www.tinytronics.nl/shop/en/sensors/current-voltage/ina226-i2c-dc-current-and-voltage-meter-20a-module) |
| Nilight inline ATC fuse holder | No mounting tab; 14 AWG leads out both ends | Tie-down points | Medium | [Nilight](https://www.nilight.com/products/nilight-10-pack-ni-fh01-inline-holder-14awg-wiring-harness-atc-ato-30amp-blade-automotive-fuse-holder-10-2-years-warranty) |
| Rocker switch (Daier KCD1-101 type) | Cutout 19.2 x 13.2 mm; bezel 21 x 15; 21.4 mm deep behind the panel; 20 A at 12 V DC; two 4.8 mm tabs | Snap-in panel | High for KCD1-101, Medium that it is ours | [Daier](https://daierswitches.com/products/20a-12v-spst-on-off-2-pin-rocker-switch) |
| 22 mm e-stop (LA38-02ZS type) | 22 mm hole; head about 40 mm; about 78 mm overall; 32 x 30 mm behind the panel | Panel nut | Low-Medium | [AliExpress](https://www.aliexpress.us/item/3256806731686244.html) |
| 5.5 x 2.1 panel jack | Common 5 A metal type: 11 mm hole, panel up to 6 mm; another style is M8 in a 7.6 mm hole. Ours not identified | Panel nut | Low | [Tinytronics DC-099](https://www.tinytronics.nl/en/cables-and-connectors/connectors/dc-jack/dc-jack-metal-5.5mm-female-dc-099) |
| XT60 | 15.5 x 8.1 x 20.5 mm per half | Inline | High | [Amass sheet](https://mrsdprojects.ri.cmu.edu/2025teamb/wp-content/uploads/sites/84/2025/05/xt60.pdf) |
| Heat-set inserts (Kadrick 520 kit) | M3 in 3 to 8 mm lengths; **no M2.5** | M3 only | Medium | [listing](https://ibspot.com/products/kadrick-520pcs-m2-m3-m4-m5-threaded-inserts-assortment-kit-for-3d-printing-components-metric-brass-knurled-nuts-insert-by-heat-into-plastic-parts) |

## Design consequences

- The Pi and the servo board take M2.5: hex nut pockets under the deck, since there are no M2.5
  inserts.
- The DROK gets slotted ear holes (the spacing is only scaled); the UCTRONICS a cradle with open
  ends (no holes); the INA226 and fuse holders tie-down points.
- The Pi is powered from the UCTRONICS (no PD): set `PSU_MAX_CURRENT=5000` when the Pi is set up.

## Owner's answers and what they settle (2026-11-23)

- **E-stop:** anywhere, but under a cover that must be flipped back to reach it. Design: a lid
  hinged at its back edge, no latch, one finger lifts it; the rocker and charge jack sit under the
  same lid, which covers the second answer too. Trade-off told to the owner: a lid slows a slap
  by about a second; the console stop and releasing the stick stay the quick stops.
- **Switch and charge jack:** tucked away from wear: under the e-stop's lid.
- **Battery terminals:** decided from first principles: terminals to the robot's right (-y), the
  power side, so the main fuse sits within a short lead of the + terminal and high current stays
  away from the Pi. Turn the battery if they face left.
- **Mywish kit:** no M2.5. Not needed: the standoff kit brings M2.5 screws and nuts (below).
- **INA226 shunt:** no R0xx marking visible. The deck does not depend on it; calibrate in software
  (known current, read the shunt-voltage register, mV / A gives the shunt).
- **Servo board:** the box says "Bus Servo Adapter (A)", Wonrabai's resale of the Waveshare board;
  Wonrabai lists 42 x 33 mm, matching Waveshare's drawing (2.5 mm holes at 37 x 28).

## Research 2026-11-23 (second pass)

| Part | Finding | Confidence |
|---|---|---|
| Standoff kit B07KM5B3PT: HanTof 160 pcs | 20 each M2.5 M-F 5+5, M-F 11+6, M-F 20+6, plain 11 (likely F-F); 40 M2.5 nuts; 40 M2.5 x 5 screws; brass, stainless screws | Medium (listing snippets) |
| E-stop B07R8PTTDX: mxuteuk HB2-ES544, 2NC 10 A | Head 40 mm, 22 mm hole. Size split above and below the panel not published | Medium / unknown |
| Charge jack B0D9B7WR23: Tugermoola OLA012 | 5 A, IP68, 150 mm leads; panel hole about 12 mm (Low). Thread not published | Low |
| INA226 B0DRNG1VKM: GODIYMODULES | PCB 26 x 22 x 14 mm; holes not published | Medium |

## E-stop moved to v2 (owner, 2026-11-23)

v1 runs only under the owner's supervision; the son may play with v2, so the e-stop and its
flip-back cover belong to v2. Without the e-stop the main rocker switch is v1's only hardware cut
(beside the console stop and the stick release), so it stays reachable: tucked inside the plate's
footprint, not under a lid.

## Layout decision (2026-11-23, revised)

Without the control box over the caster cup, one level fits again:

- **Left:** the Pi 5 on standoffs, long side across the robot, USB end inboard so its plugs use
  the centre lane.
- **Centre back:** a low bridge over the caster cup carrying the servo board; servo sockets and
  USB-C face sideways.
- **Right (power side, battery terminals this side):** the DROK bolted by its ears to the grid,
  the UCTRONICS in a cradle, the INA226 in a holder, fuse holders on tie-downs.
- **Main switch and charge jack:** a small upright panel at the right rear, its face set back
  from the plate's back edge so the plate takes the knocks.
- **v2:** the bridge over the cup can later carry the e-stop box with its cover.

## Still open (2026-11-23, third round)

Charge jack thread diameter; whether the DROK's ear holes land on two grid holes 60 mm apart; the
rating printed on the rocker switch (needs 10 A at 12 V).

**DROK fit check (owner, 2026-11-23):** its ear holes do not land on the grid. It gets a small
printed mount with slots under its ears, bolted to the grid. Don't drill the base plate.

**Charge jack (owner, caliper, 2026-11-23):** the kit socket's threaded tube measures about
11.4 mm (an M12-class thread; an earlier 7.75 mm reading was the charger's plug and is withdrawn).
Panel hole 12.4 mm as modelled (prints about 12.1). The owner accepts it without a test print.

**Coupon results (2026-11-23):** the rocker snaps in and holds ("snap perfect"): use the snug
cutout, 19.4 x 13.4 mm as modelled. The M2.5 boss works: nut in the pocket, standoff screwed in, it holds.
The owner has a right-angle USB-A to USB-C cable for the Pi's power.
The UCTRONICS slides between the channel walls (27.6 mm) with a tiny bit of play: keep that
width; zip ties through the cradle hold it. The board measures 63.5 x 27.3 mm (owner's caliper).

**Rocker (owner's box, 2026-11-23):** DaierTek KCD1-101, the mini rocker; Daier rates it 20 A at
12 V DC, above the 10 A main fuse. Cutout 19.2 x 13.2 mm (Daier sheet).

## Fit coupon (before the deck parts)

One small flat print checks every new interface: two rocker cutouts (small, large), three jack
holes (8.2, 8.4, 8.6 mm), one M2.5 boss with a nut pocket under it for a brass standoff's stud,
and a short channel at the UCTRONICS's 27 mm width.

## Parts to model (spec, revised 2026-11-23 after the coupon)

Plate frame as above; z up from the base plate's top face. Every part bolts to the plate's M3 grid
with M3 screws up from under the plate and nuts on top (Mywish kit: 8, 12, 16, 20 mm; choose the
shortest giving three threads past the nut), like the cradles. A layout function (`derive_deck`)
places everything and raises if any two footprints overlap, two parts claim one grid hole, a
plug's reach hits something, or a part meets the strap slots (keep x <= -84 where |y| is 27.8 to
52.2), the caster cup (radius 37 with its bosses, 12 mm tall with nuts and screw tips) or the
plate's edges (half width 130.8, back edge x -190, 10 mm corner radius); tests pin it.

Proven by the coupon: M2.5 boss with a hex nut pocket from below (as `derive_deck_coupon`), rocker
cutout 19.4 x 13.4 mm in a 2 mm panel, UCTRONICS channel 27.6 mm inside.

1. **Compute tray (left).** Pi 5 long side across the robot: board x -88 to -144, y 39 to 124;
   GPIO edge forward (x -88), USB/Ethernet end inboard (its plugs reach into the centre lane,
   y 5 to 36, x -92 to -128: keep clear), PCIe/microSD end outboard. Holes at x -91.5 / -140.5,
   y 62.5 / 120.5 (RP-008347). Four coupon bosses, 11 mm brass standoffs. Its USB-C power port is
   on the back edge (x -144) about 11 mm from the outboard end (y about 113). The UCTRONICS sits
   behind the Pi in a cradle, long side across: x about -152 to -179, y about 52 to 115, USB-A
   output at the outboard end (a right-angle cable, on hand, loops to the Pi's USB-C), input
   end inboard. 3 mm tray, four grid holes it alone uses.
2. **Servo board bridge (centre back, over the caster cup).** Waveshare Bus Servo Adapter (A),
   42 x 33 mm, 2.5 mm holes at 37 x 28: long side fore-aft, x -137 to -179, y -16.5 to 16.5.
   Its USB-C and 12 V screw terminal face +y (toward the Pi), servo sockets face -y. Platform top
   at least 15 mm above the plate (the cup reaches 12), coupon bosses on top, legs with feet on
   grid holes clear of the cup's 42 mm keep-out, for example (-135, +-40) and (-175, +-40); then
   the compute tray must not use or cover those. Prints upside down (platform on the bed) or with
   legs that need no supports.
3. **Power tray (right).** DROK (57 x 39 x 22 mm body, ears on the 39 mm ends with 4.1 mm holes
   about 61 apart, potted, all four leads out one 57 mm face) long side fore-aft at y -100: two
   slotted pads under its ears, slots fore-aft covering 54 to 68 mm hole spacing, each with a hex
   channel underneath so the M3 nut slides with the slot. INA226 (GODIYMODULES, 26 x 22 x 14 mm, no
   published holes) in a 27 x 23 pocket with zip-tie slots. Tie-down loops for two inline fuse
   holders (about 15 mm round bodies, 14 AWG leads) along the inboard edge.
4. **Switch panel (back right).** An upright 2 mm panel, face at x -186 (4 mm inside the plate's
   back edge so the plate takes knocks), facing back. Rocker cutout 19.4 x 13.4 mm, long side
   vertical (rocker: 21 x 15 bezel in front, 21.4 mm deep behind). Charge socket hole 12.4 mm
   (thread measured 11.4; its collar and leads stay behind). Keep both clear of the DROK's back
   ear and leads. Part of the power tray if it prints without supports, else its own part with
   feet on the grid.

**Rocker body (owner, caliper, 2026-11-23):** 18.7 x 11.7 mm without the clips. That fits Daier's
19.2 x 13.2 cutout: the clips sit on the long faces, so the short side needs the extra room for
them to flex in and spring out. The coupon's 13.4 and 13.7 mm short sides test how firmly they hold.

## As modelled (2026-11-23)

Three parts (the switch panel is part of the power tray): compute tray about 14 g, servo bridge
about 8 g (prints upside down), power tray about 19 g. Changes from the spec, each pinned by a
test in `tests/test_exp003_deck.py`:

- Switch panel face at x -179, not -186: a rocker paddle up to 10 mm proud stays 1 mm inside the
  plate's back edge. Rocker at y -115, charge socket at y -84.5, either side of the DROK's back ear.
- Bridge posts at (-175, +-40), (-135, -40), (-115, 0): a post at (-135, +40) would stand under
  the Pi's USB end. The servo board rides on 20 mm standoffs so its plugs clear the Pi's USB stack.
- INA226 behind the fuses; the fuse tie points sit forward, near the battery's + terminal.
- Power tray bolts at (-95, -80), (-115, -100), (-135, -80), (-135, -100).

Fasteners: 12 x M3 x 12, 2 x M3 x 8 (DROK ears), 14 M3 nuts; 4 x 11 mm and 4 x 20 mm M2.5 M-F
standoffs, 8 M2.5 nuts, 8 x M2.5 x 5; 8 zip ties.

## Dry fit and assembly order (owner, 2026-11-23)

All three deck parts are printed and were laid on the plate (photos, 2026-11-23). An overlay of
the CAD on the owner's top-view photo (registered to 40 plate holes, mean error 0.3 mm) matched
the layout. Orientation as laid out:

- Right as placed: the Pi (USB and Ethernet to the centre, GPIO forward, USB-C and HDMI back),
  the DROK (leads to the centre, ears fore and aft on the pads) and the servo bridge.
- **Servo board: turn half a turn.** Its barrel jack, screw terminal and USB-C face the Pi (+y);
  the servo sockets face the power side. The jumper caps go on **B (USB to servo)**; the two loose
  yellow caps in the bag are spares.
- **INA226: turn half a turn.** Screw terminal forward (toward the fuses), I2C header back.
- UCTRONICS: long side across in its channel, USB-A output at the outboard end beside the Pi's
  USB-C.

Every deck screw goes up from under the plate into a nut in the part, so a part must be bolted
down before anything covers its nuts (the Pi covers the compute tray's, the DROK the power
tray's). Order:

1. Standoffs into the trays before they go on the plate (the M2.5 nut pockets are underneath):
   M2.5 nut plus 11 mm standoff at each compute tray boss, nut plus 20 mm standoff at each
   bridge boss.
2. The three parts to the plate, 4 x M3 x 12 each (power tray, compute tray, bridge): nut in the
   well, screw up from below, snug only. **Wait for base plate v2** ([WHEEL_MOUNT.md](WHEEL_MOUNT.md));
   the grid does not change.
3. DROK: M3 nut slid into each pad's channel, ears on the pads, M3 x 8 through each ear.
4. INA226 in its pocket, UCTRONICS in its channel, two zip ties each.
5. Rocker snapped into the panel and the charge jack through its hole, once their leads are on
   (the rocker is hard to remove once snapped in).
6. Pi (cooler fitted first) and servo board on their standoffs, M2.5 x 5.
7. Fuse holders on their tie points while wiring.

Solder or crimp on the bench, away from the PETG (it softens at about 80 C), before fitting: the
INA226 header (if its pins are only pushed through), the rocker's leads (4.8 mm spades or
soldered) and the power harness joins (DROK, fuse holders, XT60s, charge jack), heat-shrunk as
one harness. Nothing else on the deck needs solder.
