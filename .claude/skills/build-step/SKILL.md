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
