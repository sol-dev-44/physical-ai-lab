# Tessera: modular bench storage

Printed storage for the lab's bench tools. Modules sit on a 52 mm grid and lock together with
bowtie keys, so the field grows in any direction and any module lifts straight out.
Design agreed with the owner 2026-11-23.

## The system

- **Grid:** 52 mm squares, so the smallest cup is about 2 in square (owner, 2026-11-23: the
  first 40 mm grid was too small). A module is an nx x ny rectangle of squares (L shapes later),
  26, 52, 78, 104 or 130 mm tall (about 1, 2, 3, 4 or 5 in). Each module is 0.25 mm inside its cells on every side, so neighbours
  never bind.
- **Joint:** every 52 mm along every outside wall, at the middle of each square's edge, a
  half-bowtie socket runs from top to bottom. A bowtie key drops into two facing sockets and
  locks the two modules together. Keys are the height of the shorter neighbour, so they sit
  flush with its top. Sockets with no key show on the outside as vertical grooves.
- **Lift-out:** every joint is vertical, so any module lifts straight up out of the field.
- **Colours (owner, 2026-11-23):** modules Sunflower Yellow PLA, keys Blue PLA. Test keys print
  in yellow so a test plate needs no colour swaps.
- **Material:** PLA, except anything that holds the heat gun or sits near the iron: PETG.

## How the bench is organised

- **Left to right follows the job:** heat end (heat gun, near the iron station), solder and
  flux in the middle, cleaning at the right. The alcohol sits at the far right, away from heat.
- **Tall at the back, low at the front,** so every tool is in sight from the chair.
- **Sharp tools stand on their edge, jaws down,** in a hand-tool rack: blades covered.
- **Engraving does the labelling:** each module's front face carries its name; each pocket's
  floor carries the outline of the tool that lives there, so an empty outline shows what's out.
- **Easter eggs:** each module's underside carries "TESSERA" and its serial number; the
  alcohol tower has a false floor with a hidden stash (see ALCOHOL below).

## Bench layout (2026-11-24)

Nine squares wide and three deep (468 x 156 mm, about the soldering mat's width), behind the
mat. `tessera_cad/layout.py` holds it (tested: no overlaps, tall at the back, heat at the
left, alcohol at the far right); `draw_layout.py` draws it to `out/layout.png`.

**What fits where.** The socket bosses stand 6.1 mm into every cavity, so a round thing fits:
up to 35 mm across in a 1 x 1 (and in a 3 x 1), 47.5 mm in a 2 x 1, 94 mm in a 2 x 2. A
module's size follows from its tool, not a fixed ladder of sizes.

| Module | Cells (col, row) | Size | Holds | Sized from | Est. |
|---|---|---|---|---|---|
| HEAT GUN | 0-1, 1-2 | 2 x 2, 104 mm, PETG | mini heat gun, nozzle up, stored cold (it has its own stand for use) | similar 300 W minis about 225 x 45 mm; check the body on arrival | 149 g PETG |
| SOLDER | 2-3, 1-2 | 2 x 2, 52 mm | 1/4 lb spool on a spindle, wire out a front slot; 2 wick bobbins | listing 2.4 x 2.4 x 1.5 in: 61 mm round, too big for a 2 x 1 | 85 g |
| FLUX | 4, 2 | 1 x 1, 104 mm | flux syringe standing up, a few brushes (6 in, 48 mm proud) | brushes 6 in; syringe length not published, check | 67 g |
| TIPS | 4, 1 | 1 x 1, 52 mm | printed 2026-11-23 | | |
| BIG | 5-6, 1-2 | 2 x 2, 130 mm | general bin, 99.5 mm square inside, 128 mm deep; modelled (No. 005) | owner, 2026-11-25: at least 4 x 4 in, and deep | 181 g |
| ALCOHOL | 7-8, 1-2 | 2 x 2, 130 mm | 16 oz bottle on a false floor over a 10 mm stash, 51 mm proud; modelled (No. 004) | 6.38 x 6.38 x 16.69 cm (diagonal 90 mm, fits the 94) | 181 g + 37 g floor |
| RACK | 0-2, 0 | 3 x 1, 52 mm | crimper, stripper, 2 cutters, jaws down | Klein 3005CR 9 x 3 in; IRWIN 8 in; Hakko CHP-170 about 5 in; slot widths on arrival | 79 g |
| GLASSES | 3-5, 0 | 3 x 1, 26 mm | safety glasses, folded flat | no folded size published; 151 mm cavity, check | 47 g |
| SPARE | 6, 0 | 1 x 1, 52 mm | printed 2026-11-23 | | |
| PARTS | 7-8, 0 | 2 x 1, 26 mm | heat-shrink offcuts, screws, pins | generic | 34 g |

Not in the field: the Hakko 599B tip cleaner (70 mm round, 71 mm tall, with its own weighted
base; Hakko datasheet) sits beside the iron, and the WEP 948DQ-III station sits left of the mat
(no size published; check on arrival).

Estimates scale the solid volume by the first piece's slicer weight (about 35.6 g per 1 x 1,
52 mm cup), before keys. Yellow PLA still to print: about 677 g (2026-11-25, with BIG and the
false floor), more than the 616 g left on A4. ALCOHOL, its floor and BIG (about 399 g) fit
now; the spool on order (due 2026-12-01) covers the rest. The heat gun holster's 149 g PETG waits for the PETG order: the
wheel module v2 takes most of spool 1.

**Print order:**
1. Now (no tool needed): PARTS tray, the first check that sockets line up over 104 mm, and
   blue R1 keys for the field (about 6.5 g each).
2. ALCOHOL (modelled 2026-11-25, with its false floor): the bottle's size is listed; any time.
   BIG, general bin, any time.
3. After the flux and cutters arrive (2026-11-25): FLUX.
4. After the rest arrives (2026-11-27): RACK (slot widths), SOLDER (spool), GLASSES; HEAT GUN
   once the PETG order is in.

## Joint numbers

Bowtie (plan view), centred on the line between two modules: neck 9.0 mm wide on that line,
13.0 mm wide at each end, ends 6.75 mm from the line (0.25 gap + 6.5 socket depth). Flank
angle about 16 degrees. Behind each socket the wall thickens into a boss 16.2 mm wide that
stands 6.1 mm into the cavity (wall 2.0 mm, 1.6 mm of plastic round the socket).

Key fit is set by `key_clearance_mm` per side. The first plate tested 0.10, 0.15 and 0.20
(engraved on each test key's top as 10, 15 and 20).

**Test plate 1 result (owner, 2026-11-24): all three keys had too much play.** The flanks
run only 16.5 degrees off the direction the modules pull apart, so each 0.1 mm of side
clearance lets a socket travel 0.35 mm; with both sockets and both key ends, the 0.10 key
still lets two cups move about 0.9 mm (`flank_play`). Shaving the clearance only shrinks
this: a plain key cannot slide in and also have no play.

**Test plate 2: crush ribs.** A ribbed key keeps 0.10 clearance on its flats, so it starts
in as easily as key 10, and carries one vertical rib (radius 1.0 mm) on each of its four
flanks, midway along the socket. Each rib's crest stands past the socket wall and crushes a
little on the way in. The ribs press the key toward the deep ends of both sockets, so the
key's ends seat against the socket ends and the joint has no play in any direction. Ribs
start 2.5 mm up, rounded, so the key's lead chamfer still finds the socket.

| Key | Clearance on the flats | Rib crest past the socket wall |
|---|---|---|
| 05 | 0.05 (plain, for comparison) | no ribs |
| R1 | 0.10 | 0.10 |
| R2 | 0.10 | 0.20 |

The owner tries each between the two cups: a key should go in by thumb pressure (a tap on a
table is fine for the last few mm) and leave the two cups moving as one. If R1 still moves,
R2 is the fit; if R2 will not go in, R1 is. The winner sets `rib_interference_mm`, and every
blue key after that is ribbed.

**Test plate 2 result (owner, 2026-11-24): R1 is the fit,** "perfect key size". Every key from
now on is ribbed at 0.10 past the socket wall on a 0.10 clearance (the `Joint` defaults).

**Lifting a module out with ribbed keys:** a ribbed key holds by friction, so it no longer
drops out. Push it up from underneath (lift the pair, thumb on the key's bottom) before lifting
a module out.

## First piece (2026-11-23)

Two 1 x 1 cups, 51.5 mm square and 52 mm tall, about 2 x 2 x 2 in ("TIPS" and "SPARE" on their fronts, "TESSERA 001" and "002"
underneath), plus three 52 mm test keys. One yellow plate. (A first plate on the 40 mm grid was
sliced but never sent: too small.)

## Plate 3 (2026-11-24)

- **PARTS tray,** 2 x 1, 26 mm tall (4.1 x 2.0 x 1.0 in), yellow, "TESSERA No. 003" underneath.
  The first check that sockets line up over 104 mm: set TIPS and SPARE side by side along its
  back edge and key all three together.
- **Blue field keys (R1),** 4 at 52 mm and 4 at 26 mm (`field_key`). A key is as tall as the
  shorter of the two modules it joins; every key has the same R1 cross-section.
- Two plates in one project, one colour each, so no filament swaps between layers.

## ALCOHOL and BIG (2026-11-25)

**ALCOHOL** (No. 004) is a 2 x 2 cup, 130 mm tall, for the 16 oz isopropyl bottle. A loose
false floor sits in its bottom: a 2.4 mm plate on a 2 mm skirt, 12.4 mm tall in all. The skirt
stands on the real floor and leaves a hidden stash 10 mm deep under the plate, about 95 mm
square (a USB stick, SD cards, folded notes). The ceiling of the stash reads "YOU FOUND IT".

- **Fit:** the plate is notched round all eight socket bosses and stands 0.2 mm in from every
  wall and boss (docs/printing.md, slip fit). It slides in and out but cannot rattle.
- **Lifting it:** take the bottle out. In the middle of the front edge there is a half-round
  notch, 20 mm wide. The front wall hides it from the chair. Put a fingertip down the notch,
  hook it under the plate's edge (it overhangs the notch by 4 mm) and lift. A ring of skirt
  behind that edge keeps the stash closed, so nothing shows or slips out through the notch.
  Or lift the module out (push its keys up first) and tip it over: the floor drops out.
- **The bottle:** it stands on the plate, 14.4 mm above the bench, so its top is 51 mm above
  the rim (39 mm without the false floor). That is fine: two thirds of the bottle is inside,
  its middle sits 32 mm below the rim, and it can lean at most 9 degrees before the rim stops
  it. The extra 12 mm makes it easier to grab. Turned 45 degrees, one corner sits over the notch
  (under 1% of its base); square on, all of it stands on the plate.
- **Printing:** the cup open side up; the floor plate side down, skirt up. Neither has an
  overhang past 45 degrees (tested). Files: `out/tessera_alcohol_2x2`,
  `out/tessera_alcohol_false_floor`.
- **Label:** the builder puts every label left of the first front groove, so "ALCOHOL" is
  shrunk to about 3.8 mm letters.

**BIG** (No. 005) is the same 2 x 2 x 130 mm cup with no false floor: a general bin, 103.5 mm
(4.1 in) square outside, 99.5 mm square and 128 mm deep inside. It takes the 2 x 2 once kept
free to grow (cells 5-6, 1-2). File: `out/tessera_big_2x2`.

## Files

- `tessera_cad/params.py`: numbers and derived geometry; no CadQuery (tested by `uv run pytest`).
- `tessera_cad/module.py`, `tessera_cad/key.py`: the solids; `tessera_cad/false_floor.py`:
  ALCOHOL's false floor.
- `tessera_cad/layout.py`: the bench layout (plain Python, tested); `draw_layout.py` draws it.
- `build.py`: writes STEP and STL to `out/` (gitignored).

Build: `uv run --no-project --python 3.12 --with cadquery python -I bench/tessera/build.py`
Geometry tests: `uv run --no-project --python 3.12 --with cadquery --with pytest python -I -m pytest bench/tessera/tests`
