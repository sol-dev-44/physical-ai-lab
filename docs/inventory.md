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
| exp003 wheel hub, PETG | 2 | Reserved | exp003 drive wheels; tires to follow in TPU |
| exp003 hub coupon v2, PETG | 1 | Active | Fit gauge and phase 0 spin indicator |
| exp003 hub coupon v1, PETG | 1 | Spare | Retired (too close to the servo case) |

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
| Feetech STS3215 12V servos (loose spares) | 2 | Reserved | exp003 wheel motors, each with a PETG wheel hub fitted to its horn. Dimensions: `experiments/exp003-household-robot/cad/servo.toml` and the vendored model in `cad/vendor/` |

## Printing

| Item | Qty | Status | Where / notes |
|---|---|---|---|
| Bambu Lab H2D AMS Combo, Standard (not Pro) | 1 | Active | All printed parts. Delivered 2026-11-12; firmware 01.04.20.00 |
| Bambu AMS 2 Pro (in the combo) | 1 | Active | On the right nozzle; firmware 02.04.19.87; has a drying mode (use it for PETG). Slots on 2026-11-19: A1 PETG Orange, A2 PLA Jade White, A3 PLA Blue, A4 PLA Sunflower Yellow. The left nozzle feeds from the external spool holder (TPU) |
| Bambu PLA Basic, Jade White (10100), 1 kg | 1 | Spare | Studio preset: Bambu PLA Basic |
| Bambu PLA Basic, Blue (10601), 1 kg | 1 | Spare | Studio preset: Bambu PLA Basic |
| Bambu PLA Basic, Sunflower Yellow (10402), 1 kg | 1 | Spare | Studio preset: Bambu PLA Basic |
| Bambu PLA Basic, Pumpkin Orange (10301), 1 kg | 1 | Spare | Studio preset: Bambu PLA Basic |
| Bambu PLA Pure, Baby Blue (17600), 1 kg | 1 | Spare | Studio preset: Bambu PLA Pure |
| Bambu PETG Basic, Orange (30301), 1 kg | 2 | Reserved | exp003 wheel hubs, brackets. Studio preset: Bambu PETG Basic. About 134 g used from the first spool by 2026-11-19 (two coupons, two hubs) |
| SUNLU TPU 95A 1.75 mm, black, 1 kg | 1 | On order | exp003 tires and bumper. Studio preset: Generic TPU. Feed from the external spool holder, not the AMS |

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

Status for all: **On order**, reserved for exp003. "Check on arrival" is what to verify before use.

| # | Item | ASIN | Check on arrival |
|---|---|---|---|
| 1 | Raspberry Pi 5 8GB | B0CK2FCG1K | Genuine board |
| 2 | Official Pi 5 Active Cooler | B0CLXZBR5P | |
| 3 | CanaKit 45W USB-C PD supply (27W at 5V 5A for Pi 5) | B07H125ZRL | Bench power only; not the official PSU |
| 4 | SanDisk Extreme 64GB A2 microSD | B09X7C7LL1 | |
| 5 | M2.5 brass standoff kit, 160 pcs | B07KM5B3PT | |
| 6 | Serial bus servo driver board for Feetech ST/SC, USB | B0CTMM4LWK | Stand-in for the Waveshare Bus Servo Adapter (A). Test with LeRobot's motor setup on a spare STS3215 |
| 7 | 608-ZZ bearings 8x22x7 mm, 10-pack | B07XLV1W2M | Optional outboard wheel support |
| 8 | 1.5" PU swivel plate casters, set of 8 | B0DHHJRDDV | Measure overall height (expect about 50 mm); 1 used, 7 spare |
| 9 | SUNLU TPU 95A, 1 kg | B0BXNWK6NS | (also listed under Printing) |
| 10 | Brass heat-set inserts M2 to M5, 520 pcs | B0D5V3TZLB | |
| 11 | ExpertPower 12V 10Ah LiFePO4, built-in BMS | B07X3Y3LS5 | 152 x 66 x 94 mm, 1.07 kg. No charger included |
| 12 | 14.6V 2A LiFePO4 charger, 5.5x2.1 mm barrel, center positive | B09HKDPLQ9 | Confirm center positive with the multimeter |
| 13 | UCTRONICS 9-36V to 5V (5.2V) buck, up to 6A | B07XXWQ49N | Stand-in for Pololu D36V50F5. Check 5.1 to 5.25V out under load |
| 14 | DROK buck-boost, 9-36V in, 12V 5A out, potted | B0B6VK8BPN | Check 12.0V out before connecting servos |
| 15 | INA226 I2C current/voltage module, 0-36V 20A | B0DRNG1VKM | **Shunt must be R010 (or lower), not R100** |
| 16 | XT60 pairs with 14 AWG leads, 5 pairs | B085HF31K7 | |
| 17 | Nilight inline ATC fuse holders 14 AWG, 10-pack, + ATC fuse assortment 2-40A | B07426WCLM, B0DNCJRX18 | 10A main, 5A servo rail |
| 18 | DaierTek 12V 20A SPST rocker switch | B07S2QJKTX | Main power |
| 19 | 5.5x2.1 mm panel-mount DC jacks, 5A, 6 sets | B0D9B7WR23 | Charge port; matches item 12 |
| 20 | 22 mm red mushroom e-stop, latching, 2NC 10A, 2-pack | B07R8PTTDX | 1 used, 1 spare |
| 21 | 16 AWG silicone wire, 10 ft red + 10 ft black | B0D93K21TN | |
| 22 | 22 AWG silicone wire, 6 colors x 10 ft | B089CQHRDT | |
| 23 | Heat-shrink kit, 580 pcs | B01MFA3OFA | |
| 24 | Hook-and-loop battery straps, 6-pack | B08HHHFMCJ | |
| 25 | VL53L1X ToF modules (TOF400C), 3-pack | B0HC653J8F | **XSHUT pin broken out** (needed to give each its own address) |
| 26 | VL53L0X ToF modules (GY-VL53L0XV2), 3-pack | B0B6ZT7NRW | Cliff sensors |
| 27 | KW12-3 roller-lever limit switches, 10-pack | B07X142VGC | Bumpers; 2 used |
| 28 | Dupont jumper wires, 120 pcs | B01EV70C78 | |
| 29 | JST-XH pre-crimped connector kit | B08G18PWQ6 | |
| 30 | AYL mini speaker, 3.5 mm aux, about 64 mm, USB-charged | B007OYAVLI | |

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
