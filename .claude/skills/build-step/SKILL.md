---
name: build-step
description: Guide the owner through a hands-on build (robot, printed parts, bench) one step at a time, each with a diagram. Use when the owner asks "what's next", "next step", "start at step N", or wants directions to assemble, drill, wire or fit something, and when they report a step done.
---

# One build step at a time

The owner builds at the bench and follows along. They asked (2026-11-25) for exactly one next
step at a time, always with a diagram unless it truly needs none, and to assume the previous step
went as planned.

## Where the steps live

Each build keeps an ordered checklist in its experiment folder, for example
`experiments/exp003-household-robot/BUILD_STEPS.md`. Steps are numbered from 0, `- [ ]` open,
`- [x]` done, with the date moved to the "Done" section.

- No steps file yet: write one first, from the build's own notes (README, CAD docs such as
  `cad/WHEEL_MOUNT.md`, `cad/DECK.md`). Put in every step you can already see, in order.
- The owner names a step ("start at task 0"): start there. Otherwise give the first open step.
- New steps turn up (a fix, a part that arrived): add them to the file in order.
- The owner reports a step done: tick it and move it to "Done" with the date, then give the
  next one.

## Giving a step

1. **Get the numbers from the source**, not memory: the CAD params (`cad/exp003_cad/params.py`
   and its `derive_*` functions; run them with `uv run python` from the `cad` folder), the
   build notes, `docs/inventory.md` for what tools and screws the owner has. Never ask the owner
   to measure what the CAD, a datasheet or a search gives.
2. **Draw it** with the visualize tool (`read_me` first, then `show_widget`, one SVG, 680 wide,
   dark-mode classes). Draw the real part to scale where it helps, in the view the owner will
   see from the bench: top view for placement, the face being worked on for screws. Show the
   reference edges and distances, the holes or fasteners, the direction of motion as an arrow.
   Grey for structure, one colour for the part being moved, one for fasteners. Labels outside
   the drawing or in a short legend below it.
3. **Write the directions** after the drawing, plain (see the `plain-measuring-instructions`
   memory): orientation first ("front = ..."), then one action per numbered line, exact contact
   points, the tool and bit or screw size from the inventory. Then a short "Check" list: how the
   owner knows the step worked.
4. **Only that step.** Don't list later steps; the file holds them. Mention at most one line
   on what the step leads to if it helps.
5. **Safety and material:** say where the part can be damaged (overtightening into plastic,
   drilling speed in PETG). Never plan a reprint where drilling or reuse works (the
   `conserve-print-material` memory).

## After

Save what the step taught (a measured fit, a surprise) in the build's notes in the same change
as the ticked step. Commit and push only when the owner asks.

## Lessons (2026-11-25 to 26)

- **Check the CAD before naming a feature.** "Nut in the well" was wrong for the deck trays
  (plain holes; only the bridge legs have wells). Read the part's code (`deck_shapes.py`,
  the part's own module) or run its `derive_*` before telling the owner what a hole holds.
- **Say what a part is before telling them what to do with it.** The owner asked "is that
  electric or plastic?" and "zip ties?": name the part, what it looks like and where it sits.
- **Mark up the owner's own photo when they send one.** "Show me on the real photo" beat any
  drawing: crop and annotate it with PIL in the scratchpad (circles, an arrow for the route, a
  two-line legend) and send it with SendUserFile.
- **Draw in the owner's orientation.** Their photos have the front to the right and the robot's
  left at the top; a diagram in that view needs no mental rotation.
- **Gotchas before the step, not after:** things that become hard once a part is fixed (zip
  ties under a tray, nuts under a board) go first in the step's list.
- **Record what actually happened**, including uncertainty: the load check passed by hand with
  no numbers; the crack's bead may be PLA.
