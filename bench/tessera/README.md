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
  alcohol tower will have a false floor with a hidden stash.

First layout (agreed on the 40 mm grid; re-plan in 52 mm squares when the tools arrive):
front: rack (crimper, stripper, 2 cutters) / tip-cleaner seat / small cups / glasses;
back: solder / flux and brushes (tall) / heat gun (tall, PETG) / small cups / room to grow /
alcohol (tall). Tool modules wait for the tools (due 2026-11-25 to 11-28);
measure on arrival: flux syringe, solder spool, wick bobbin, heat gun body.

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

**Lifting a module out with ribbed keys:** a ribbed key holds by friction, so it no longer
drops out. Push it up from underneath (lift the pair, thumb on the key's bottom) before lifting
a module out.

## First piece (2026-11-23)

Two 1 x 1 cups, 51.5 mm square and 52 mm tall, about 2 x 2 x 2 in ("TIPS" and "SPARE" on their fronts, "TESSERA 001" and "002"
underneath), plus three 52 mm test keys. One yellow plate. (A first plate on the 40 mm grid was
sliced but never sent: too small.)

## Files

- `tessera_cad/params.py`: numbers and derived geometry; no CadQuery (tested by `uv run pytest`).
- `tessera_cad/module.py`, `tessera_cad/key.py`: the solids.
- `build.py`: writes STEP and STL to `out/` (gitignored).

Build: `uv run --no-project --python 3.12 --with cadquery python -I bench/tessera/build.py`
Geometry tests: `uv run --no-project --python 3.12 --with cadquery --with pytest python -I -m pytest bench/tessera/tests`
