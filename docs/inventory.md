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
| exp003 servo cradle, PETG | 2 | Spare | Retired 2026-11-25: the servos moved into wheel module v2. They rolled over under the robot's weight (2026-11-23; `experiments/exp003-household-robot/cad/WHEEL_MOUNT.md`) |
| exp003 wheel module v2, PETG | 1 | Reserved | Printed 2026-11-24 (3 h 52 min, 164.26 g). Both servos fitted (bodies to the rear) and wheels on 2026-11-25, bolted to the drilled base plate the same day (8 x M3 x 12, 7 x M3 x 16); cables not plugged in yet. A crack through the +y box top (a layer joint) was patched 2026-11-26 (binder-ring wire stitches and a melted bead) and the load check passed on the owner's hands-on test (no caliper numbers) |
| exp003 hub coupon v1, PETG | 1 | Spare | Retired (too close to the servo case) |
| exp003 caster cup v1, PETG | 1 | Spare | Fit test 2026-11-21: plate and holes fit; the fork hits the walls. Retired |
| exp003 caster cup (final), PETG | 1 | Spare | 4 mm too tall (the robot tips nose up); replaced by the corrected cup. Full strength, v2 cavity, with mounting bosses; printing 2026-11-21 (33 min) |
| exp003 caster cup (corrected), PETG | 1 | Reserved | On the exp003 chassis. 8.6 mm tall, rim 44.4 mm off the floor; printed 2026-11-22 (27 min) and fitted the same day with 4 x M4 x 8 (caster) and 4 x M3 x 16 (to the plate). The plate sits level |
| exp003 electronics deck fit coupon, PETG | 1 | Reserved | Printed 2026-11-23 (28 min): rocker cutouts, charge-jack holes, an M2.5 standoff boss with nut pocket, a UCTRONICS channel. Fit results go in cad/DECK.md |
| exp003 deck power tray and servo bridge, PETG | 2 | Reserved | Printed together 2026-11-23; bolted to the plate 2026-11-26 with the DROK, INA226 and servo board on them. Power tray: DROK on slotted pads, INA226 pocket, fuse tie points, rocker and charge socket in the panel. Servo bridge: over the caster cup on four posts; Waveshare Bus Servo Adapter (A) on 20 mm standoffs (cad/DECK.md) |
| exp003 compute tray, PETG | 1 | Reserved | Printed 2026-11-23; bolted to the plate 2026-11-26 with the Pi 5 (Active Cooler fitted) and the UCTRONICS on it; bolts to the base plate: Pi 5 on four 11 mm M2.5 standoffs, UCTRONICS in a zip-tied cradle behind it; bolts to the plate at (-95/-135, 80/100) |
| exp003 base plate, PETG | 1 | Reserved | exp003 chassis. Drilled 2026-11-25 for the wheel module v2 (15 x M3, 1/8 inch bit, the module as template) instead of reprinting. Printed 2026-11-21 (4 h 56 min, 223 g); cradles and caster cup fitted, level on the floor 2026-11-22 |
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
| Bambu PLA Basic, Sunflower Yellow (10402), 1 kg: 3 refills, 1 with spool | 4 | On order | Bambu US store, ordered 2026-11-25, about a week. Tessera bench storage |
| Bambu PLA Basic, Jade White (10100), 1 kg: 2 refills, 1 with spool | 3 | On order | Same order |
| Bambu PLA Basic, Blue (10601), 1 kg refill | 2 | On order | Same order |
| Bambu PETG Basic, Orange (30301), 1 kg refill | 3 | On order | Same order. On top of the 3 spools from Amazon due 2026-11-27 |
| Bambu PETG Matte, Avocado Green (35501), 1 kg with spool | 1 | On order | Same order; free gift at 10 rolls or more. No use planned yet |
| SUNLU TPU 95A 1.75 mm, black, 1 kg | 1 | Reserved | Arrived 2026-11-20. exp003 tires and bumper. Studio preset: Generic TPU. Feed through the rear TPU inlet to the right hotend, not the AMS (docs/printing.md). Stored sealed in a bag with desiccant between prints (unloaded 2026-11-21, about 895 g) |

All Bambu spools are 1 kg with RFID tags, so the AMS reads type and colour itself. Refills come without a spool: wind each onto an empty Bambu spool (the order brings 2, and every finished spool frees one) before it goes in the AMS. Amounts left are
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
| WEP 948DQ-III soldering station with fume extractor (2-in-1) | 1 | On order | Ordered 2026-11-23. Due 2026-11-25. For the exp003 power harness; run the fume extractor while soldering |
| Hakko CHP-170 micro soft wire cutters | 1 | On order | Ordered 2026-11-23. 2-pack. Due 2026-11-25 |
| MG Chemicals 8341 no-clean flux paste, 10 mL | 1 | On order | Ordered 2026-11-23. Due 2026-11-25 |
| MG Chemicals 4900 SAC305 lead-free solder, 0.032 in, 1/4 lb | 1 | Active | Ordered 2026-11-23, arrived 2026-11-25 (due 2026-11-27). Lead-free: runs hotter than leaded (about 350 C tip) |
| Klein Tools 3005CR ratcheting crimper, 10 to 22 AWG | 1 | On order | Ordered 2026-11-23. Due 2026-11-27. For insulated terminals, e.g. the spade terminals (exp003 row 31); not for bare ferrules |
| IRWIN Vise-Grip wire stripper, 10 to 24 AWG | 1 | On order | Ordered 2026-11-23. Due 2026-11-27 |
| QWORK 300 W mini heat gun | 1 | On order | Ordered 2026-11-23. Due 2026-11-27. For the heat-shrink kit (exp003 row 23) |
| Copper solder wick braid, 2.5 mm | 1 | On order | Ordered 2026-11-23. 2-pack. Due 2026-11-27 |
| Hakko 599B-02 tip cleaning wire and holder | 1 | On order | Ordered 2026-11-23. Due 2026-11-27 |
| Acid/flux brushes, 3/8 in | 1 | On order | Ordered 2026-11-23. 36 count. Due 2026-11-27 |
| PAFOWO silicone soldering mat, 17.7 x 11.8 in | 1 | On order | Ordered 2026-11-23. Due 2026-11-27 |
| NoCry clear anti-fog safety glasses | 1 | On order | Ordered 2026-11-23. Due 2026-11-27. Wear them when soldering and clipping leads |
| Amazon Basics 99% isopropyl alcohol, 16 oz | 1 | On order | Ordered 2026-11-23. Due 2026-11-28. Cleans flux off boards |

## exp003 household robot parts (ordered 2026-11-17, due 2026-11-21 to 23)

All reserved for exp003. Most arrived 2026-11-20; the Pi 5, XT60 leads and fuse assortment 2026-11-21. The limit switches were due 2026-11-21 and are not in yet. "Check on arrival" is what to verify before use; a part counts as on hand only once it passes.

| # | Item | ASIN | Check on arrival | Arrived |
|---|---|---|---|---|
| 1 | Raspberry Pi 5 8GB | B0CK2FCG1K | Genuine board | 2026-11-21 |
| 2 | Official Pi 5 Active Cooler | B0CLXZBR5P | Fitted to the Pi 5 2026-11-26 (lead in the FAN socket) | 2026-11-20 |
| 3 | CanaKit 45W USB-C PD supply (27W at 5V 5A for Pi 5) | B07H125ZRL | Bench power only; not the official PSU | 2026-11-20 |
| 4 | SanDisk Extreme 64GB A2 microSD | B09X7C7LL1 | | 2026-11-20 |
| 5 | M2.5 brass standoff kit, 160 pcs | B07KM5B3PT | | 2026-11-20 |
| 6 | Serial bus servo driver board for Feetech ST/SC, USB | B0CTMM4LWK | The board that arrived is marked Waveshare Bus Servo Adapter (A) V1.1 (photo, 2026-11-26), so it is the planned board, not a stand-in. On the deck's servo bridge 2026-11-26, jumpers on B (USB to servo; confirm). Test with LeRobot's motor setup on a spare STS3215 | 2026-11-20 |
| 7 | 608-ZZ bearings 8x22x7 mm, 10-pack | B07XLV1W2M | Optional outboard wheel support | 2026-11-20 |
| 8 | 1.5" PU swivel plate casters, set of 8 | B0DHHJRDDV | Checked 2026-11-21: 50 mm to the top of the plate; plate 46 x 38.25 mm, holes on 35.75 x 27.75 mm centres, swivel offset 13 mm (`Caster` in exp003 `params.py`); 1 used, 7 spare | 2026-11-20 |
| 9 | SUNLU TPU 95A, 1 kg | B0BXNWK6NS | (also listed under Printing) | 2026-11-20 |
| 10 | Brass heat-set inserts M2 to M5, 520 pcs | B0D5V3TZLB | | 2026-11-20 |
| 11 | ExpertPower 12V 10Ah LiFePO4, built-in BMS | B07X3Y3LS5 | Checked 2026-11-21: model EP1210 on the label (152 x 66 x 94 mm, 1.22 kg on its sheet; not weighed). F2 6.35 mm spade terminals on top at one short end, + at the label side. 10 A continuous, 15 A for 5 s. No charger included. Needs 6.3 mm female spade terminals (not on hand) | 2026-11-20 |
| 12 | 14.6V 2A LiFePO4 charger, 5.5x2.1 mm barrel, center positive | B09HKDPLQ9 | Confirm center positive with the multimeter | 2026-11-20 |
| 13 | UCTRONICS 9-36V to 5V (5.2V) buck, up to 6A | B07XXWQ49N | Stand-in for Pololu D36V50F5. Check 5.1 to 5.25V out under load | 2026-11-20 |
| 14 | DROK buck-boost, 9-36V in, 12V 5A out, potted | B0B6VK8BPN | Check 12.0V out before connecting servos | 2026-11-20 |
| 15 | INA226 I2C current/voltage module, 0-36V 20A | B0DRNG1VKM | **Shunt must be R010 (or lower), not R100** | 2026-11-20 |
| 16 | XT60 pairs with 14 AWG leads, 5 pairs | B085HF31K7 | | 2026-11-21 |
| 17 | Nilight inline ATC fuse holders 14 AWG, 10-pack, + ATC fuse assortment 2-40A | B07426WCLM, B0DNCJRX18 | 10A main, 5A servo rail | Holders 2026-11-20; fuse assortment 2026-11-21 |
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
| 32 | Antrader USB 3.0 right-angle up and down extension, 4-pack (ordered 2026-11-23) | B07F7Y21GW | Turns the UCTRONICS's USB-A output 90 degrees so the Pi's power cable stays inside the plate (cad/DECK.md); check it says up and down, not left and right | Due 2026-11-27 (Friday) |

## Consumables: stock, usage and reorders

The owner asked (2026-11-19) for usage to be tracked and orders flagged ahead of need. Rules:

- **Log every use in the same change that uses it:** each print (slicer weight) and each
  assembly (screws, inserts, wire). The usage log is below.
- **Forecast from the plan:** "Planned" lists what the next exp003 parts will use, from the
  models and slicer where they exist, estimates otherwise (marked "est.").
- **Flag an order** when stock minus planned use falls below the reorder point, allowing for the
  lead time. The owner prints all day, every day (2026-11-25): plan on about 500 g a day
  (3.5 kg a week; the H2D runs about 30 to 45 g an hour). Keep two weeks on hand, about 7 kg
  across PETG and PLA, and order in batches of about 4 kg whenever usable stock drops under one
  week (3.5 kg), since the Bambu store takes about a week. Within that: at least 2 kg of PETG,
  and a sealed spare of every PLA colour in active use (Tessera yellow, white, blue keys). Claude proposes the order with links; the owner places it (Amazon blocks AI agents,
  and checkout is the owner's).

### Stock

| Item | Start | Used | Left | Planned next | Reorder point | Lead time |
|---|---|---|---|---|---|---|
| PETG Basic Orange, spool 1 (AMS A1) | 1000 g | about 656 g (wheel module coupon 17.96 g, wheel module 164.26 g) | about 344 g | about 400 g est. (shells, bumper mounts) | Keep at least 2 kg after planned use (daily printing); order 3 spools at a time. 3 ordered 2026-11-24 (Amazon, due 2026-11-27) and 3 refills 2026-11-25 (Bambu store) | Bambu store about 1 week |
| PETG Basic Orange, spool 2 (sealed) | 1000 g | 0 | 1000 g | | | |
| PLA Basic Jade White (AMS A2) | 1000 g | about 545 g (toy truck: coupon 35 g; chassis, axles, bins 415 g; cab band 43 g; bin slide test 12 g; new bin and wheels about 40 g) | about 455 g | Toy truck: more bins (about 40 g each with wheels) only if the new bin passes play | One spool per colour is enough for now | Bambu store about 1 week |
| PLA Basic Blue (AMS A3) | 1000 g | about 559 g (toy truck: tyres 160 g; body and tailgate 360 g; Tessera keys 38.71 g) | about 441 g | Tessera keys (R1), about 4 to 7 g each | | |
| PLA Basic Sunflower Yellow (AMS A4) | 1000 g | about 566 g (toy truck: hub caps 13 g; cab, arm, paddle 227 g; Tessera first piece 90.66 g; Tessera test keys 2, 19.51 g; PARTS tray 33.31 g; ALCOHOL tower 181.62 g) | about 434 g | Tessera bench layout: about 460 g est. for the 5 modules left (bench/tessera/README.md); 1 spool due 2026-12-01 (Amazon) and 4 on order (Bambu store) | | |
| PLA Basic Pumpkin Orange, PLA Pure Baby Blue (spares) | 1000 g each | 0 | 1000 g each | Not planned yet | | |
| SUNLU TPU 95A, black | 1000 g (arrived 2026-11-20) | 105 g (two tires) | about 895 g | about 100 g est. (bumper) | Order when under 300 g | Amazon 1 to 2 days |
| M3 x 8 button head (Mywish kit) | Not counted: per-size counts are not published; similar kits hold 20 per length | 10 (wheel hubs 8, DROK ears 2) | about 10 if 20 | None planned | Count the compartment when a design picks this length | Amazon 1 to 2 days |
| M3 x 12, M3 x 16, M4 x 8 button head, M3 and M4 nuts (Mywish kit) | Not counted (similar kits hold 20 per length) | M3 x 12: 4 (cradles, retired; not known if back in the kit), 8 (wheel module feet), 12 (deck parts); M3 x 16: 4 (caster cup), 7 (module beam); M3 nuts: 8 (cradles, cup), 15 (module), 14 (deck parts, DROK); 4 x M4 x 8 (caster), 4 M4 nuts; toy truck: 8 x M4 x 16, 4 x M4 x 20, 8 M4 nuts, 6 M4 washers (cab still needs 4 x M4 x 20, arm 2 x M4 x 16 and 2 nuts) | **Running low (owner, 2026-11-26)**: M3 x 12 and M3 x 16 nearly used up | Shells, bumper mounts, arm v2 | Restock now (Orders to place) | Amazon 1 to 2 days |
| M2 self-tapping screws (servo bags) | One bag per servo | 8 (two cradles) | Rest of the bags | None planned | Keep the bags with the servos | |
| Brass heat-set inserts M2 to M5 | 520 (arrived 2026-11-20) | 0 | 520 | Shells est. 20 to 40 (the plate and cup use nuts) | Plenty | |
| M2.5 brass standoffs | 160 (arrived 2026-11-20) | 8 (4 x 11 mm Pi, 4 x 20 mm servo board), 8 M2.5 nuts, 4 x M2.5 x 5 | 152 | Sensors and the camera, est. 8 | Plenty | |
| Zip ties, small (about 2.5 mm wide, 100 mm) | 0 (none on hand, 2026-11-26) | 0 | 0 | 8 on the deck (2 UCTRONICS, 2 INA226, 4 fuse holders) plus the harness | Order now (Orders to place) | Amazon 1 to 2 days |

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
| 2026-11-21 | Caster cup (final), full strength (33 min 13 s, left nozzle, 4 walls, 30% infill) | PETG 11.98 g (slicer); to fit: 4 x M4 x 8 and nuts (caster; M4 x 12 stood too proud), 4 x M3 x 20 and nuts (cup to plate) |
| 2026-11-21 | Chassis assembled: cradles to plate, caster to cup, cup to plate | 4 x M3 x 12 and 4 M3 nuts (cradles); 4 x M4 x 8 and 4 M4 nuts (caster); 4 x M3 x 20 and 4 M3 nuts (cup; M3 x 16 with the corrected cup) |
| 2026-11-22 | Caster cup (corrected), 8.6 mm (27 min 24 s, left nozzle, 4 walls, 30% infill) | PETG 9.89 g (slicer) |
| 2026-11-22 | Caster cup swapped: caster into the corrected cup, cup to plate | 4 x M3 x 16 and 4 M3 nuts (cup to plate); the caster's 4 x M4 x 8 and nuts moved over. The old cup's 4 x M3 x 20 and nuts back to the kit |
| 2026-11-23 | Electronics deck fit coupon (27 min 46 s, left nozzle, 4 walls, 30% infill) | PETG 8.85 g (slicer) |
| 2026-11-23 | Electronics deck power tray and servo bridge, one plate (1 h 38 min, left nozzle, 4 walls, 30% infill) | PETG 34.78 g (slicer) |
| 2026-11-23 | Electronics deck: compute tray (42 min 16 s, left nozzle, 4 walls, 30% infill) | PETG 17.44 g (slicer) |
| 2026-11-19 | Toy truck joint coupon (home project, files in ~/toys/garbage-truck) | PLA Jade White 35.3 g (slicer) |
| 2026-11-20 | Toy truck wheels, 6 (blue tyres, yellow caps) | PLA 172.75 g total (slicer): about 160 g Blue, about 13 g Sunflower Yellow (split estimated) |
| 2026-11-21 | Toy truck chassis, 3 axles, 2 bins | PLA Jade White 414.74 g (slicer) |
| 2026-11-22 | Toy truck body and tailgate (7 h 46 min, left nozzle, 4 walls, 15% infill, 5 mm brim) | PLA Blue 359.90 g (slicer) |
| 2026-11-22 | Toy truck assembled so far: 6 wheels, body to chassis, hopper hinge | 6 x M4 x 16, 6 M4 nuts, 6 M4 washers (wheels); 4 x M4 x 20 (body hold-down); 2 x M4 x 16 and 2 M4 nuts (hinge) |
| 2026-11-22 | Toy truck cab, bin arm, push-out paddle (4 h 41 min, left nozzle, 2 colour changes, 4 walls, 15% infill, 5 mm brim) | PLA 270.52 g (slicer): Sunflower Yellow 227.32 g, Jade White 43.20 g |
| 2026-11-22 | Toy truck cab, arm and paddle fitted (truck complete) | 4 x M4 x 20 (cab); 2 x M4 x 16 and 2 M4 nuts (arm pivot) |
| 2026-11-22 | Toy truck bin slide test, 3 pieces (30 min, left nozzle) | PLA Jade White 12.17 g (slicer) |
| 2026-11-23 | Tessera bench storage, first piece: cups TIPS and SPARE (No. 001, 002) and test keys 10, 15, 20, 52 mm grid (3 h 30 min, left nozzle, 4 walls, 30% infill) | PLA Sunflower Yellow 90.66 g (slicer) |
| 2026-11-23 | Toy truck new bin (tongue +0.15) and 2 spinning bin wheels (about 59 min, left nozzle) | PLA Jade White about 40 g (model estimate: bin 37.5 g, wheels 1.2 g each; the slicer figure was not read); to fit: 2 x M4 x 16 and 2 M4 washers |
| 2026-11-24 | Tessera test plate 2: keys 05 (plain), R1 and R2 (crush ribs), 52 mm (48 min, left nozzle, 4 walls, 30% infill) | PLA Sunflower Yellow 19.51 g (slicer) |
| 2026-11-24 | Tessera plate 3, two jobs: 8 blue R1 keys, 4 x 52 mm and 4 x 26 mm (1 h 33 min), and the PARTS tray, 2 x 1, 26 mm, No. 003 (1 h 13 min); left nozzle, 4 walls, 30% infill | PLA Blue 38.71 g, PLA Sunflower Yellow 33.31 g (slicer) |
| 2026-11-24 | exp003 wheel module v2 fit coupon (1 h 24 min, left nozzle, 4 walls, 30% infill, front face down) | PETG Orange 17.96 g (slicer) |
| 2026-11-24 | exp003 wheel module v2 (3 h 52 min, left nozzle, 6 walls, 40% infill, front face down; coupon passed) | PETG Orange 164.26 g (slicer) |
| 2026-11-25 | Tessera ALCOHOL tower, 2 x 2, 130 mm, No. 004 (6 h 23 min, left nozzle, 4 walls, 30% infill) | PLA Sunflower Yellow 181.62 g (slicer) |
| 2026-11-25 | exp003 wheel module v2 bolted to plate v1 | 8 x M3 x 12 (feet), 7 x M3 x 16 (beam), 15 M3 nuts |
| 2026-11-26 | exp003 +y wheel box crack patched | Steel wire from a binder ring (5 stitches), a scrap bead melted along the crack, superglue on its edges (owner's choice of scrap; it shows blue in the photos) |
| 2026-11-26 | exp003 electronics deck assembled on the plate | 12 x M3 x 12 and 12 M3 nuts (three deck parts); 2 x M3 x 8 and 2 M3 nuts (DROK ears); 4 x 11 mm and 4 x 20 mm M2.5 M-F standoffs, 8 M2.5 nuts; 4 x M2.5 x 5 (Pi); the servo board's own 4 corner screws |

### Orders to place

**Ordered 2026-11-25 (Bambu US store, the owner placed it; about a week):** 13 rolls at the 10-roll mix-and-match tier (35% off, free shipping): PLA Basic Sunflower Yellow (10402) 3 refills and 1 with spool, Jade White (10100) 2 refills and 1 with spool, Blue (10601) 2 refills; PETG Basic Orange (30301) 3 refills; plus the free PETG Matte Avocado Green (35501) with spool. The proposal priced it at about $119 (about $9.15 a kg); the final total was not recorded. Why Bambu, from a 15-vendor price check on 2026-11-25: the only exact Sunflower Yellow 10402 match, AMS RFID, and big single-colour boxes from Elegoo or Anycubic saved only $0.70 to $1.10 a kg. Cheaper but unproven, for utility colours only: Geeetech 20 rolls of PLA in black or white, $7.23 a kg; Jayo PETG 11 kg mixed colours on Amazon, $7.27 a kg.

**Ordered 2026-11-24 (Amazon, $107.08 before tax):** 3 x Bambu PETG Basic Orange (30301), due 2026-11-27; 4 x 6806-2RS (one pack), due 2026-11-28; 1 x Bambu PLA Sunflower Yellow (10402) from a reseller, due 2026-12-01: its title says Matte, so check the spool label reads PLA Basic 10402 and return it if not. The three entries below stay for their reasons until they arrive.

- **Bambu PETG Basic, 3 x 1 kg at least** (owner, 2026-11-21: "3 spools minimum", printing every
  day on the robot or toys). After the base plate and the caster cups spool 1 is down to about 526 g (after the deck coupon and all three deck parts); with the
  sealed spool that is about 1.5 kg, against about 500 g still planned (electronics
  deck, shells, bumper mounts) plus daily printing. Bambu store, about 1 week. Spools with the RFID
  tag (or refills plus the reusable spool) so the AMS reads them. Orange matches the robot so far;
  a second colour for the shells is the owner's call.

- **PETG is now urgent:** wheel module v2 (about 435 g est. as modelled, `experiments/exp003-household-robot/cad/WHEEL_MOUNT.md`) leaves about 1.1 kg of the two spools, and about 700 g after the shells and bumper mounts too, well under the 2 kg rule. Order the 3 spools above first.
- **6806-2RS deep-groove ball bearings, 30 x 42 x 7 mm, 4 pcs** (two for the wheels plus spares;
  2026-11-23). Stage 2 of the wheel mount: each wheel turns on its own bearing so the STS3215 only
  drives. Any rubber-sealed (2RS) 6806 / 61806 from a bearing brand or a 4- or 10-pack on Amazon;
  check the size on arrival. Needed before the v2 arm, or sooner if the stage 1 load check shows
  lean inside the servo. **Order now (owner, 2026-11-24: don't hold up the build):** a few dollars,
  1 to 2 days, so a failed stage 1 check never waits on parts. The 10 x 608-ZZ on hand
  (8 x 22 x 7 mm, row 7) cannot replace them (an 8 mm bore cannot go round the 20 mm horn).

- **Bambu PLA Basic Sunflower Yellow, 1 x 1 kg** (2026-11-24): the Tessera bench layout
  (`bench/tessera/README.md`) takes about 493 g of the 649 g left on A4, so add one spool to the
  PETG order (same store). The Tessera heat gun holster (about 149 g) also waits for that PETG.

- **Screws and ties restock (owner, 2026-11-26: "need to order some new hex screws, etc soon")**,
  before the shells and bumper mounts. M3 button-head hex socket screws: at least 50 each of M3 x 12
  and M3 x 16, and 25 of M3 x 8 (stainless, 2 mm key, to match the Mywish kit); 100 M3 hex nuts;
  100 small zip ties (about 2.5 mm wide, 100 mm long; the deck's slots are 4.5 x 2 mm) for the 8
  deck tie points and the harness. Count the M3 x 20 and M4 compartments at the same time. Vendor
  and price check (spend-research skill) before the owner orders.

The battery's spade terminals were ordered 2026-11-21 (row 31).
The soldering and wiring tools proposed 2026-11-22 were ordered 2026-11-23 (Tools and bench, On order).

PETG covers the planned parts with about 700 g to spare, below the 2 kg rule (order above). The TPU on hand covers the bumper.

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
| 2026-11-23 | Amazon | $275.26 | Soldering station, solder, flux, crimper, stripper, cutters, heat gun and bench supplies (Tools and bench, On order) |
| 2026-11-23 | Amazon | $10.38 | Item 32: right-angle USB-A up/down extensions (Pi power) |
| 2026-11-24 | Amazon | $107.08 before tax | 3 x PETG Orange, 6806-2RS 4-pack, 1 x PLA Sunflower Yellow |
| 2026-11-25 | Bambu Lab | about $119 (proposal; final not recorded) | 12 filament rolls plus a free PETG Matte (Printing, On order) |

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
- 2026-11-21: toy truck white plate logged (414.74 g Jade White). AMS now feeds the left nozzle.
- 2026-11-22: toy truck blue plate logged (359.90 g Blue); about 480 g left on the A3 spool, a spare Blue spool on hand.
- 2026-11-22: toy truck yellow+white plate logged (227.32 g Yellow, 43.20 g White) and its M4 hardware so far; the last truck plate.
- 2026-11-20: most of the 2026-11-17 exp003 order arrived (Arrived column); Pi 5, XT60, fuse assortment and limit switches due 2026-11-21. TPU on hand.
- 2026-11-22: corrected caster cup fitted; the chassis sits level.
- 2026-11-22: Pi 5, XT60 leads and the fuse assortment marked arrived (2026-11-21); limit switches still out.
- 2026-11-22: soldering and wiring tools proposed for the power harness (Orders to place).
- 2026-11-22: toy truck finished (cab and arm hardware logged); bin slide test logged (12.17 g White).
- 2026-11-23: toy truck new bin with spinning wheels logged (about 40 g White, estimate).
- 2026-11-23: Tessera bench storage first piece sent (90.66 g Yellow, `bench/tessera/`); about 669 g Yellow left.
- 2026-11-23: the exp003 servo cradles roll over under load; wheel module v2 planned (about 375 g PETG est.); 6806-2RS bearings added to Orders to place and the PETG order marked urgent. Compute tray printed; all three deck parts dry-fitted.
- 2026-11-24: Tessera test plate 2 logged (19.51 g Yellow): all three plate 1 keys had play, so the new keys carry crush ribs; about 649 g Yellow left.
- 2026-11-24: key R1 chosen; Tessera bench layout drawn (about 493 g Yellow, 149 g PETG est.); one Yellow spool added to Orders to place.
- 2026-11-24: Tessera plate 3 logged (38.71 g Blue keys, 33.31 g Yellow PARTS tray); about 441 g Blue and 616 g Yellow left.
- 2026-11-24: exp003 wheel module v2 modelled as one piece (about 190 g, coupon 18 g, plate v2 225 g: about 435 g PETG est.).
- 2026-11-24: ordered on Amazon: 3 x PETG Orange (due 11-27), 6806-2RS 4-pack (11-28), 1 x PLA Sunflower Yellow (12-01); $107.08 before tax.
- 2026-11-24: wheel module v2 fit coupon logged (17.96 g PETG); about 508 g left on spool 1.
- 2026-11-24: coupon passed (servo fits); wheel module v2 sliced at 164.26 g PETG (6 walls, 40%); about 344 g left on spool 1.
- 2026-11-25: plate v2 (225 g PETG) dropped: plate v1 gets drilled instead.
- 2026-11-25: reorder rule raised for all-day printing (500 g a day, two weeks on hand); 4 PLA spools proposed.
- 2026-11-25: Tessera ALCOHOL tower sent (181.62 g yellow, about 434 g left). Next job: BIG bin and the ALCOHOL false floor in Jade White (215.48 g, 7 h 2 min, sliced).
- 2026-11-25: plate v1 drilled for the wheel module; both servos fitted in the module, wheels on; cradles retired.
- 2026-11-25: Bambu store filament order placed: 4 Yellow, 3 White, 2 Blue PLA, 3 Orange PETG, plus a free PETG Matte Avocado Green (Printing, On order).
- 2026-11-25: exp003 wheel module v2 bolted to the base plate (8 x M3 x 12, 7 x M3 x 16 from the kit).
- 2026-11-26: exp003 crack patched and load check passed (owner); electronics deck assembled on the plate (three parts, DROK, INA226, UCTRONICS, Pi 5 with cooler, servo board); fasteners logged; M3 screws running low and no zip ties on hand, so a restock went into Orders to place. The servo board on hand is the Waveshare Bus Servo Adapter (A) itself.
