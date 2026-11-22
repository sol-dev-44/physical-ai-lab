# Lab inventory

What the lab owns, where each thing is, and what is coming. Check here before ordering anything.

**Keep it current.** Update this file in the same change whenever a part arrives, gets assigned to
an experiment, breaks, or is used up, and add a line to the change log at the bottom.
The repo is public: personal details go in only when the owner says so (ADR 0013).

## Status key

| Status | Meaning |
|---|---|
| **Active** | In use. "Where" says by what. |
| **Reserved** | Set aside for a planned use; don't borrow without updating this file. |
| **Spare** | On hand and free. |
| **On order** | Paid for, not here yet. |
| **Wishlist** | Saved, not bought. |
| **Unknown** | Owned, but where it is or whether it's in use needs checking (see "To confirm"). |

## Printed parts

| Item | Qty | Status | Where / notes |
|---|---|---|---|
| exp003 wheel hub, PETG | 2 | Reserved | exp003 drive wheels, tires fitted 2026-11-21 |
| exp003 tire, TPU 95A | 2 | Reserved | On the exp003 wheel hubs; printed and fitted 2026-11-21, snug first try |
| exp003 hub coupon v2, PETG | 1 | Active | Fit gauge and phase 0 spin indicator |
| exp003 servo cradle, PETG | 2 | Reserved | Fitted to both exp003 wheel servos 2026-11-19 |
| exp003 hub coupon v1, PETG | 1 | Spare | Retired (too close to the servo case) |
| exp003 caster cup v1, PETG | 1 | Spare | Fit test 2026-11-21: plate and holes fit; the fork hits the walls. Retired |
| exp003 caster cup (final), PETG | 1 | Reserved | Full strength, v2 cavity, with mounting bosses; printing 2026-11-21 (33 min) |
| exp003 base plate, PETG | 1 | Reserved | Printed 2026-11-21 (4 h 56 min, 223 g); fit check next |
| exp003 caster cup v2 light, PETG | 1 | Spare | Fit test passed 2026-11-21: plate, holes and the fork's full swivel all clear. The full-strength cup prints with the base plate |

## Robot arms (exp002)

| Item | Qty | Status | Where / notes |
|---|---|---|---|
| SO-ARM101 Pro kit, leader arm (black, 7.4V motors) | 1 | Active | exp002 bench, read-only teleop arm |
| SO-ARM101 Pro kit, follower arm (white, 12V STS3215) | 1 | Active | exp002 bench |
| SO-ARM101 Pro kit, second leader + follower | 1 pair | Unknown | Second kit from the 2026-11-07 order. Candidate for the exp003 v2 arm (follower on the robot, leader for teleop demos) |
| Bus servo driver boards (from the arm kits) | 4 | 2 Active, 2 Unknown | One per arm |
| Wrist cameras ("USB HD Camera", from the kits) | 2 | 1 Active, 1 Unknown | exp002 follower gripper |
| 5V 4A adapter (leader power) | 1+ | Active | exp002 |
| 12V 2A adapter (follower power, labelled theqingliupower) | 1+ | Active | exp002; also bench power for spare servos when the arms are off |
| Feetech STS3215 12V servos (loose spares) | 2 | Reserved | exp003 wheel motors, each with a PETG wheel hub on its horn and fitted in a PETG cradle; idler discs off, kept with the servo bags. Dimensions: `experiments/exp003-household-robot/cad/servo.toml` and the vendored model in `cad/vendor/` |

## Printing

| Item | Qty | Status | Where / notes |
|---|---|---|---|
| Bambu Lab H2D AMS Combo, Standard (not Pro) | 1 | Active | All printed parts. Delivered 2026-11-12; firmware 01.04.20.00 |
| Bambu AMS 2 Pro (in the combo) | 1 | Active | On the left nozzle since 2026-11-21 (right before that); firmware 02.04.19.87; has a drying mode (use it for PETG). Slots on 2026-11-19: A1 PETG Orange, A2 PLA Jade White, A3 PLA Blue, A4 PLA Sunflower Yellow. TPU bypasses it: the right nozzle is the TPU nozzle, fed through the rear TPU inlet (docs/printing.md) |
| Bambu PLA Basic, Jade White (10100), 1 kg | 1 | Spare | Studio preset: Bambu PLA Basic |
| Bambu PLA Basic, Blue (10601), 1 kg | 1 | Spare | Studio preset: Bambu PLA Basic |
| Bambu PLA Basic, Sunflower Yellow (10402), 1 kg | 1 | Spare | Studio preset: Bambu PLA Basic |
| Bambu PLA Basic, Pumpkin Orange (10301), 1 kg | 1 | Spare | Studio preset: Bambu PLA Basic |
| Bambu PLA Pure, Baby Blue (17600), 1 kg | 1 | Spare | Studio preset: Bambu PLA Pure |
| Bambu PETG Basic, Orange (30301), 1 kg | 2 | Reserved | exp003 wheel hubs, brackets. Studio preset: Bambu PETG Basic. About 134 g used from the first spool by 2026-11-19 (two coupons, two hubs) |
| SUNLU TPU 95A 1.75 mm, black, 1 kg | 1 | Reserved | Arrived 2026-11-20. exp003 tires and bumper. Studio preset: Generic TPU. Feed through the rear TPU inlet to the right hotend, not the AMS (docs/printing.md). Stored sealed in a bag with desiccant between prints (unloaded 2026-11-21, about 895 g) |

All Bambu spools are 1 kg with RFID tags, so the AMS reads type and colour itself. Amounts left are
not tracked yet; the AMS shows an estimate per spool.

## Cameras, audio, control

| Item | Qty | Status | Where / notes |
|---|---|---|---|
| Logitech C920x webcam | 2 | 1 Active, 1 Reserved | Active: overhead camera (exp001 arena, then exp002 bench). Reserved: exp003 front camera |
| Seeed reSpeaker XVF3800 USB mic array | 1 | Reserved | exp003 head |
| DJI Mic Mini | 1 | Spare | Build-log narration |
| Xbox controller | 1 | Reserved | exp003 teleop |
| Neewer LED panels (2) + 22" overhead arm | 1 set | Unknown | Probably the bench lighting and camera mount |
| Sabrent 10-port USB hub | 1 | Spare | Keep the arms off hubs (exp002) |

## Home devices (exp000, exp001)

| Item | Qty | Status | Where / notes |
|---|---|---|---|
| BroadLink RM4 Mini IR blaster | 1 | Active | exp000/exp001; IR only, 2.4 GHz Wi-Fi |
| Toy robot "Wall-e" with IR remote (remote 2) | 1 | Active | exp000/exp001 test robot. Remote 1 is RF and unusable |

## Tools and bench

| Item | Qty | Status | Notes |
|---|---|---|---|
| Pinecil soldering iron | 1 | Active | Also for heat-set inserts |
| AstroAI multimeter | 1 | Active | |
| Digital caliper | 1 | Active | |
| STREBITO screwdriver set | 1 | Active | |
| 6" C-clamps | 4 | Active | Bench |
| Felt desk mat | 1 | Active | Bench |
| Mywish 1290-piece M2 to M5 button-head hex socket screw kit (B0CQWYFTXC) | 1 | Spare | Each size in 8, 12, 16 and 20 mm, with nuts, flat washers and hex keys. No M3 shorter than 8 mm |

## exp003 household robot parts (ordered 2026-11-17, due 2026-11-21 to 23)

All reserved for exp003. Most arrived 2026-11-20; the Pi 5, XT60 leads, fuse assortment and limit switches are due 2026-11-21. "Check on arrival" is what to verify before use; a part counts as on hand only once it passes.

| # | Item | ASIN | Check on arrival | Arrived |
|---|---|---|---|---|
| 1 | Raspberry Pi 5 8GB | B0CK2FCG1K | Genuine board | Due 2026-11-21 |
| 2 | Official Pi 5 Active Cooler | B0CLXZBR5P | | 2026-11-20 |
| 3 | CanaKit 45W USB-C PD supply (27W at 5V 5A for Pi 5) | B07H125ZRL | Bench power only; not the official PSU | 2026-11-20 |
| 4 | SanDisk Extreme 64GB A2 microSD | B09X7C7LL1 | | 2026-11-20 |
| 5 | M2.5 brass standoff kit, 160 pcs | B07KM5B3PT | | 2026-11-20 |
| 6 | Serial bus servo driver board for Feetech ST/SC, USB | B0CTMM4LWK | Stand-in for the Waveshare Bus Servo Adapter (A). Test with LeRobot's motor setup on a spare STS3215 | 2026-11-20 |
| 7 | 608-ZZ bearings 8x22x7 mm, 10-pack | B07XLV1W2M | Optional outboard wheel support | 2026-11-20 |
| 8 | 1.5" PU swivel plate casters, set of 8 | B0DHHJRDDV | Checked 2026-11-21: 50 mm to the top of the plate; plate 46 x 38.25 mm, holes on 35.75 x 27.75 mm centres, swivel offset 13 mm (`Caster` in exp003 `params.py`); 1 used, 7 spare | 2026-11-20 |
| 9 | SUNLU TPU 95A, 1 kg | B0BXNWK6NS | (also listed under Printing) | 2026-11-20 |
| 10 | Brass heat-set inserts M2 to M5, 520 pcs | B0D5V3TZLB | | 2026-11-20 |
| 11 | ExpertPower 12V 10Ah LiFePO4, built-in BMS | B07X3Y3LS5 | Checked 2026-11-21: model EP1210 on the label (152 x 66 x 94 mm, 1.22 kg on its sheet; not weighed). F2 6.35 mm spade terminals on top at one short end, + at the label side. 10 A continuous, 15 A for 5 s. No charger included. Needs 6.3 mm female spade terminals (not on hand) | 2026-11-20 |
| 12 | 14.6V 2A LiFePO4 charger, 5.5x2.1 mm barrel, center positive | B09HKDPLQ9 | Confirm center positive with the multimeter | 2026-11-20 |
| 13 | UCTRONICS 9-36V to 5V (5.2V) buck, up to 6A | B07XXWQ49N | Stand-in for Pololu D36V50F5. Check 5.1 to 5.25V out under load | 2026-11-20 |
| 14 | DROK buck-boost, 9-36V in, 12V 5A out, potted | B0B6VK8BPN | Check 12.0V out before connecting servos | 2026-11-20 |
| 15 | INA226 I2C current/voltage module, 0-36V 20A | B0DRNG1VKM | **Shunt must be R010 (or lower), not R100** | 2026-11-20 |
| 16 | XT60 pairs with 14 AWG leads, 5 pairs | B085HF31K7 | | Due 2026-11-21 |
| 17 | Nilight inline ATC fuse holders 14 AWG, 10-pack, + ATC fuse assortment 2-40A | B07426WCLM, B0DNCJRX18 | 10A main, 5A servo rail | Holders 2026-11-20; fuse assortment due 2026-11-21 |
| 18 | DaierTek 12V 20A SPST rocker switch | B07S2QJKTX | Main power | 2026-11-20, as a 10-pack of mini rockers: check the rating printed on the switch carries 10 A at 12 V before using one as the main switch |
| 19 | 5.5x2.1 mm panel-mount DC jacks, 5A, 6 sets | B0D9B7WR23 | Charge port; matches item 12 | 2026-11-20 |
| 20 | 22 mm red mushroom e-stop, latching, 2NC 10A, 2-pack | B07R8PTTDX | 1 used, 1 spare | 2026-11-20 |
| 21 | 16 AWG silicone wire, 10 ft red + 10 ft black | B0D93K21TN | | 2026-11-20 |
| 22 | 22 AWG silicone wire, 6 colors x 10 ft | B089CQHRDT | | 2026-11-20 |
| 23 | Heat-shrink kit, 580 pcs | B01MFA3OFA | | 2026-11-20 |
| 24 | Hook-and-loop battery straps, 6-pack | B08HHHFMCJ | Checked 2026-11-21: 21.5 mm wide, 27.5 mm at the buckle | 2026-11-20 |
| 25 | VL53L1X ToF modules (TOF400C), 3-pack | B0HC653J8F | **XSHUT pin broken out** (needed to give each its own address) | 2026-11-20 |
| 26 | VL53L0X ToF modules (GY-VL53L0XV2), 3-pack | B0B6ZT7NRW | Cliff sensors | 2026-11-20 |
| 27 | KW12-3 roller-lever limit switches, 10-pack | B07X142VGC | Bumpers; 2 used | Due 2026-11-21 |
| 28 | Dupont jumper wires, 120 pcs | B01EV70C78 | | 2026-11-20 |
| 29 | JST-XH pre-crimped connector kit | B08G18PWQ6 | | 2026-11-20 |
| 30 | AYL mini speaker, 3.5 mm aux, about 64 mm, USB-charged | B007OYAVLI | | 2026-11-20 |
| 31 | AIRIC blue female spade terminals, 16 to 14 AWG, 100-pack | | For the battery's F2 (6.35 mm) tabs: check they are 6.3 mm (0.250") on arrival | Due by 2026-11-25 |

## Consumables: stock, usage and reorders

The owner asked (2026-11-19) for usage to be tracked and orders flagged ahead of need. Rules:

- **Log every use in the same change that uses it:** each print (slicer weight) and each
  assembly (screws, inserts, wire). The usage log is below.
- **Forecast from the plan:** "Planned" lists what the next exp003 parts will use, from the
  models and slicer where they exist, estimates otherwise (marked "est.").
- **Flag an order** when stock minus planned use falls below the reorder point, allowing for the
  lead time. The owner prints every day (2026-11-21), so keep a bigger buffer: at least 2 kg of
  PETG on hand after planned use, and a spare spool of each PLA colour that toys are using. Claude proposes the order with links; the owner places it (Amazon blocks AI agents,
  and checkout is the owner's).

### Stock

| Item | Start | Used | Left | Planned next | Reorder point | Lead time |
|---|---|---|---|---|---|---|
| PETG Basic Orange, spool 1 (AMS A1) | 1000 g | 403 g | about 597 g | about 750 g est. (base plate 223 g sliced, cup, deck, shells, mounts) | Keep at least 2 kg after planned use (daily printing); order 3 spools at a time. 3 to order now (see Orders to place) | Bambu store about 1 week |
| PETG Basic Orange, spool 2 (sealed) | 1000 g | 0 | 1000 g | | | |
| PLA Basic Jade White (AMS A2) | 1000 g | 35 g (toy truck coupon) | about 965 g | about 480 g (toy truck: chassis, axles, bins 414 g slicer; cab window band about 65 g est.) | One spool per colour is enough for now | Bambu store about 1 week |
| PLA Basic Blue (AMS A3) | 1000 g | about 160 g (toy truck tyres) | about 840 g | about 360 g (toy truck: body and tailgate 360 g slicer) | | |
| PLA Basic Sunflower Yellow (AMS A4) | 1000 g | about 13 g (toy truck hub caps) | about 987 g | about 200 g est. (toy truck: cab, arm) | | |
| PLA Basic Pumpkin Orange, PLA Pure Baby Blue (spares) | 1000 g each | 0 | 1000 g each | Not planned yet | | |
| SUNLU TPU 95A, black | 1000 g (arrived 2026-11-20) | 105 g (two tires) | about 895 g | about 100 g est. (bumper) | Order when under 300 g | Amazon 1 to 2 days |
| M3 x 8 button head (Mywish kit) | Not counted: per-size counts are not published; similar kits hold 20 per length | 8 (wheel hubs) | about 12 if 20 | Cradle-to-plate screws (length set by the plate design) | Count the compartment when the plate design picks lengths | Amazon 1 to 2 days |
| M2 self-tapping screws (servo bags) | One bag per servo | 8 (two cradles) | Rest of the bags | None planned | Keep the bags with the servos | |
| Brass heat-set inserts M2 to M5 | On order, 520 | | | Base plate and shells est. 20 to 40 | Plenty | |
| M2.5 brass standoffs | On order, 160 | | | Pi 5 and boards est. 12 to 16 | Plenty | |

### Usage log

| Date | What | Used |
|---|---|---|
| 2026-11-18 | Hub coupon v1 | PETG 8.3 g |
| 2026-11-19 | Hub coupon v2 | PETG 7.2 g |
| 2026-11-19 | Two wheel hubs | PETG 118.5 g |
| 2026-11-19 | Hubs fitted to horns | 8 x M3 x 8 button head |
| 2026-11-19 | Servo cradle 1, fitted | PETG 10.0 g; 4 x M2 x 6 self-tapping (servo bag) |
| 2026-11-19 | Servo cradle 2, fitted | PETG 10.0 g; 4 x M2 x 6 self-tapping (servo bag) |
| 2026-11-20 | Two TPU tires (printed 2026-11-21, 8 h 8 min, fitted) | TPU 105.0 g (slicer), right hotend via the TPU inlet |
| 2026-11-21 | Caster cup v1, test piece (24 min 47 s, left nozzle) | PETG 8.32 g (slicer); 4 x M4 x 12 button head and 4 M4 nuts to fit |
| 2026-11-21 | Caster cup v2 light, test piece (22 min 30 s, left nozzle) | PETG 5.43 g (slicer); reuses the 4 M4 screws and nuts |
| 2026-11-21 | Base plate (printed, 4 h 56 min, left nozzle, 4 walls, 30% infill) | PETG 223.19 g (slicer) |
| 2026-11-21 | Caster cup (final), full strength (33 min 13 s, left nozzle, 4 walls, 30% infill) | PETG 11.98 g (slicer); to fit: 4 x M4 x 12 and nuts (caster), 4 x M3 x 20 and nuts (cup to plate) |
| 2026-11-19 | Toy truck joint coupon (home project, files in ~/toys/garbage-truck) | PLA Jade White 35.3 g (slicer) |
| 2026-11-20 | Toy truck wheels, 6 (blue tyres, yellow caps) | PLA 172.75 g total (slicer): about 160 g Blue, about 13 g Sunflower Yellow (split estimated) |

### Orders to place

- **Bambu PETG Basic, 3 x 1 kg at least** (owner, 2026-11-21: "3 spools minimum", printing every
  day on the robot or toys). After the base plate (223 g) spool 1 is down to about 609 g; with the
  sealed spool that is about 1.6 kg, against about 530 g still planned (caster cup, electronics
  deck, shells, bumper mounts) plus daily printing. Bambu store, about 1 week. Spools with the RFID
  tag (or refills plus the reusable spool) so the AMS reads them. Orange matches the robot so far;
  a second colour for the shells is the owner's call.

The battery's spade terminals were ordered 2026-11-21 (row 31).

PETG covers the planned parts with about 1100 g to spare. The TPU on hand covers the bumper.

## Wishlist (Amazon list "Robot - later")

| Item | ASIN | Price seen | For |
|---|---|---|---|
| SLAMTEC RPLIDAR C1M1 2D LiDAR, 5V UART | B0FRM8KHZF | $69 | exp003 phase 5 (mapping) |
| Magnetic pogo pin connectors, 3-pin 2A, 2 pairs | B0CSX6232W | $9.99 | exp003 self-docking |

## Learning Together materials

Toys for sessions alongside the robot work. Not lab hardware; listed so nothing is bought twice.

| Item | Qty | Status |
|---|---|---|
| Code & Go Robot Mouse | 1 | Active |
| Botley 2.0 coding robot | 1 | Active |
| Gears Deluxe Set | 1 | Active |
| Design & Drill | 1 | Active |
| PicassoTiles 100 | 1 | Active |
| LEGO DUPLO Deluxe Brick Box | 1 | Active |

## Orders

| Date | Vendor | Total | What |
|---|---|---|---|
| 2026-11-07 | Seeed | $701.53 | 2x SO-ARM101 Pro assembled kits |
| 2026-11-07 | Bambu Lab | $1,819.78 | H2D AMS Combo, 5 PLA, 2 PETG |
| 2026-11-07 | Amazon | $433.29 | Learning Together toys, Pinecil, multimeter, Neewer lights and arm, Xbox controller |
| 2026-11-07 | Amazon | $408.07 | 2x C920x, DJI Mic Mini, PicassoTiles, DUPLO, caliper, screwdrivers |
| 2026-11-07 | Amazon | $165.91 | Sabrent hub, 2x STS3215 spares, C-clamps, screw assortment, desk mat |
| 2026-11-07 | Amazon | $75.68 | reSpeaker XVF3800 |
| 2026-11-17 | Amazon | $639.60 before tax | exp003 robot parts, items 1 to 30 above |

The BroadLink RM4 Mini and the Wall-e toy predate these orders.

## To confirm

- Second SO-ARM101 pair: boxed or in use? Its two driver boards and wrist camera follow the answer.
- Neewer lights and overhead arm: what they hold now.
- Filament left on each spool, once a scale is handy.

## Change log

- 2026-11-17: file created from the 2026-11-07 and 2026-11-17 orders and the experiment READMEs.
- 2026-11-17: exp003 renamed household robot; privacy rules moved to owner judgement (ADR 0013); second SO-ARM101 pair noted as the v2 arm candidate.
- 2026-11-18: screw kit identified from the order (button heads, 8 to 20 mm); exp003 hub sized for M3 x 8.
- 2026-11-18: filament audited against the Bambu order email (all 7 spools match); colour codes, spool weights and Studio presets added; H2D confirmed Standard.
- 2026-11-19: AMS 2 Pro and its slots, printer firmware, PETG used, and the printed exp003 parts added; STS3215 spares point to their dimensions.
- 2026-11-19: consumables tracking added (stock, usage log, forecast, reorder points); servo cradles added to printed parts.
- 2026-11-19: second servo cradle printed and fitted; both wheel servos now in cradles.
- 2026-11-19: PLA rows split per spool; toy truck joint coupon logged (35 g white) and the truck's planned PLA use forecast.
- 2026-11-20: toy truck wheel plate logged (172.75 g: blue tyres, yellow caps).
- 2026-11-20: most of the 2026-11-17 exp003 order arrived (Arrived column); Pi 5, XT60, fuse assortment and limit switches due 2026-11-21. TPU on hand.
