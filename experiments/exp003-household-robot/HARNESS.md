# exp003 power harness (v1, BUILD_STEPS 12)

Drafted 2026-11-27 from the parts in `docs/inventory.md` (exp003 rows 11 to 22) and the deck
layout in `cad/DECK.md`. The owner checks it against the parts before any soldering (step 13).
v1 has no e-stop (moved to v2, DECK.md): the rocker is the only hardware cut, so v1 runs only
under the owner's supervision.

## Topology

```
Battery + --[10 A fuse]-- INA226 VIN -> VOUT --+-- Rocker --+--[5 A fuse]-- DROK IN  (12.0 V out) -- servo board 12 V terminal -- 2 servos
                                               |            |
              Charge jack + --[3 A fuse]-------+            +-------------- UCTRONICS IN (5.2 V USB-A out) -- right-angle adapter -- Pi 5 USB-C
Battery - ---- ground star: DROK IN-, UCTRONICS IN-, INA226 GND, charge jack -
DROK OUT- ---- servo board -
INA226 I2C ---- Pi 5: VCC pin 1 (3.3 V), SDA pin 3, SCL pin 5, GND pin 6
Pi 5 USB-A ---- servo board USB-C (data; jumper caps on B)
```

## Why it is wired this way

- **Main fuse first, within a short lead of the battery +.** Everything after it is protected,
  including the charge lead. The fuse tie points sit forward, next to the + terminal (DECK.md).
- **INA226 before the rocker and the charge join.** All current, in and out, passes its shunt,
  so the fuel gauge counts charging as negative current and discharging as positive (the INA226
  is bidirectional). It reads up to about 8 A with an R010 shunt; peaks above that only clip
  the reading, and the 10 A fuse still protects.
- **Charge jack joins at the rocker's input,** so the battery charges with the rocker off.
  With the rocker on, the charger (14.6 V) also feeds the DROK and UCTRONICS; both take 9 to
  36 V, and the servos only ever see the DROK's regulated 12.0 V.
- **3 A fuse on the charge lead (added 2026-11-27, built 2026-11-27).** The jack's own leads are
  thinner than the 16 AWG main run, so the 10 A fuse alone would not protect them from a short
  in the jack. The charger gives 2 A.
- **5 A fuse on the servo rail,** before the DROK (its output is rated 5 A).
- **No separate fuse on the compute rail.** The UCTRONICS draws about 2.5 A at 12 V when the Pi
  takes 5 A; its 16 AWG feed is covered by the 10 A main fuse.
- **Ground: one soldered star joint,** heat-shrunk, near the INA226. Load current never runs
  through the INA226 board's GND terminal; that terminal is only its voltage reference.

## Parts per join

| Join | Wire | Ends |
|---|---|---|
| Battery + to main fuse holder | The holder's own 14 AWG lead | 6.3 mm female spade (row 31), crimped |
| Main fuse to INA226 VIN | Holder lead | Into the screw terminal |
| INA226 VOUT to rocker tab 1 | 16 AWG red | Screw terminal; soldered to the 4.8 mm tab |
| Charge jack + to 3 A fuse to rocker tab 1 | Jack lead, holder leads | Soldered, heat-shrunk |
| Rocker tab 2 to the split | 16 AWG red | Soldered to the tab |
| Split to 5 A fuse to DROK IN+ | 16 AWG red, holder leads | Soldered, heat-shrunk |
| Split to UCTRONICS IN+ | 16 AWG red | Screw terminal |
| DROK OUT to servo board | DROK leads | 2-pin screw terminal |
| UCTRONICS USB-A to Pi USB-C | Right-angle adapter (row 32) + the owner's right-angle USB-A to C cable | Plugged |
| INA226 I2C to Pi GPIO | 4 Dupont jumpers (row 28) | Pins 1, 3, 5, 6 |
| Battery - to ground star | 16 AWG black | 6.3 mm female spade, crimped |

ATC fuse colours: 3 A violet, 5 A tan, 10 A red. Three inline holders used of ten.

## Rocker tabs (built 2026-11-27)

| Tab | Wires soldered on | Goes to |
|---|---|---|
| A (marker dot) | 150 mm red 16 AWG, taped "IN"; one lead of the 3 A holder (violet fuse) | INA226 VOUT; charge jack + |
| B | 250 mm red 16 AWG; one lead of the 5 A holder (tan fuse) | UCTRONICS IN+; DROK IN+ |

The rocker has no polarity and the I/O marks do not change the wiring. Either tab can be A.

## Bench method (learned 2026-11-27)

The owner is new to soldering; give one sub-step at a time with temperatures and checks.

1. **Prep with the iron cold.** Strip 6 mm with the IRWIN stripper (16 AWG notch for the red
   wire, 14 AWG for the fuse holder leads; strip only the end being joined), twist each wire's
   strands, then cut 20 mm of 10 mm heat-shrink (the size printed on the kit's tray) and slide
   it over both wires of the pair together, 50 mm back. It cannot go on after the joint.
2. **Twist the pair** side by side, both bare ends pointing the same way.
3. **Heat** the WEP station's iron to 370 C (700 F), SAC305 solder. Fume fan about 15 cm away,
   glasses on. Tin the tip (wipe in the brass cleaner, melt solder onto the tip until silver).
4. **Tin** the bundle (iron under, solder on top, until the strands turn silver) and the tab
   (iron on one face, solder on the other, under 3 s so the rocker body does not soften).
5. **Join.** A 16 + 14 AWG bundle does not fit through the 4.8 mm tab's hole: lay it flat along
   the tab's face, press the iron on it for about 3 s until the solder flows, lift off and hold
   the wire still for 10 s.
6. **Shrink.** Iron off, joints cool, tug test. Take the rocker out of the PETG coupon (the heat
   gun warps it), slide each tube down to the rocker body, heat with the QWORK gun 3 to 5 cm away,
   moving, 10 to 20 s, until it hugs the joint.
7. **Beep test** with the AstroAI on the "·))) Ω" position (press Select if the screen shows only
   Ω): across the two far ends, on beeps and off is silent. Beeping both ways means a solder
   bridge between the tabs; silent both ways means an open joint or a missing fuse.

## Gotchas

- **Each fuse holder comes as one closed loop of red wire** (owner's photo, 2026-11-27). Cut the
  loop opposite the holder to get its two leads.
- **The rocker 10-pack comes with pre-wired leads** on 4.8 mm push-on spades. Their wire is
  thinner than the 16 AWG main run, so they are not used on the power path; the leads are
  soldered to the tabs instead.

- **The rocker's tabs are 4.8 mm,** and the spade terminals on hand are 6.3 mm (for the
  battery). Solder the rocker's two leads off the robot, heat-shrink them, then snap the rocker
  into the panel from outside. No iron near the PETG panel (it softens at about 80 C).
- **Battery last.** Build and check the whole harness with the battery's spades off; connect
  them only after the continuity checks in step 13.
- **The Pi limits USB to 600 mA without USB PD.** The UCTRONICS has no PD, so set
  `PSU_MAX_CURRENT=5000` in the Pi's bootloader EEPROM before relying on it (DECK.md).
- **Charger polarity:** confirm centre positive with the meter before the first charge
  (inventory row 12).
- **DROK reads 12.0 V before any servo is plugged in** (step 14).

## To confirm on the parts (step 12)

- The fuse assortment has a 10 A, a 5 A and a 3 A ATC fuse.
- The DROK's leads: which pair is IN and which is OUT (label or lead colours).
- The charge jack's leads: two wires, red and black, about 150 mm.
