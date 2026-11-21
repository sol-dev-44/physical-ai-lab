# 3D printing in the lab

How an agent prints on the lab's printer, quickly and safely. Hard-won notes: add to them whenever
something new is learned.

## The printer

- **Bambu Lab H2D AMS Combo**, standard (not Pro), firmware 01.04.20.00. Two 0.4 mm nozzles,
  textured PEI plate.
- **Build area:** 325 x 320 x 325 mm on one nozzle; 300 x 320 x 320 mm where both nozzles reach.
  Larger parts split into pieces.
- **AMS 2 Pro** (firmware 02.04.19.87) feeds the **right** nozzle and has a drying mode. The
  **left** nozzle feeds from the external spool holder. Soft TPU (95A and below) never goes through
  the AMS; it feeds the **right** hotend through the TPU inlet (see "TPU" below).
- **What is loaded where:** see `docs/inventory.md` ("Printing" and the AMS row), which is kept
  current. On 2026-11-19: A1 PETG Orange, A2 PLA Jade White, A3 PLA Blue, A4 PLA Sunflower Yellow.

## Driving Bambu Studio (agent)

- The app is BambuStudio, bundle `com.bambulab.bambu-studio`. Use the computer-use background
  tools (`app_screenshot`, `app_click`, `app_menu`) after `request_access`; the owner prefers
  background control.
- **Open a model from the shell:** `open -b com.bambulab.bambu-studio /path/part.step`. Prefer STEP
  (true curves) over STL.
- **Two dialogs only the owner can click,** because they belong to another process: OK in "Step file
  import parameters", and **Send** in "Send print job". Ask for each in one line; don't try to work
  around it.
- **Clear the plate:** Edit > Delete all. Edit > Cut is refused (clipboard); to delete one object,
  click it on the canvas and press `forward_delete`.
- **Copies:** Edit > Clone selected (its dialog's OK can be clicked by element index). The `a` key
  on the canvas arranges; the toolbar arrange button may not respond to a background click.
- **Watch out:** opening a file adds to the current plate. Hidden leftovers get cloned too, so clear
  first.
- **Slice:** the green "Slice plate" button at the top right (about 993, 50 in a 1200 x 800
  window). The Slicing Result panel shows time, metres and grams.
- **Send:** "Print plate" (about 1139, 50) opens "Send print job". Wait until it shows the printer
  connected and the AMS slot mapped (it can take a few seconds), then ask the owner to click Send.
- **TPU job setup that worked (2026-11-20):**
  - Device tab: the small box beside the right panel's AMS icon (element "AMS 255") shows the right
    extruder's own external spool. Its edit dialog (Materials Setting) is another process: the
    owner picks the filament there, or on the touchscreen (right extruder, external spool, Edit,
    TPU). The printer refuses TPU on the left extruder's external spool.
  - Prepare tab: the right external spool's synced entry is "Generic TPU for AMS" (for hard TPU).
    For 95A choose Generic > TPU. The submenu opens only on a slow hover: move across "Generic"
    in steps, wait about 2 s, then click "TPU". Filament dropdowns need full-screen control.
  - Select an object and press a number key to assign it that filament. Edit > Clone selected
    does NOT copy the assignment, so check every copy's colour after cloning.
  - Exact placement: select, press `m`, then click each X/Y field, select its text and type
    a value plus Return. Avoid Tab (it set off a slice) and avoid cmd+A while the canvas has focus
    (it selects every object, and the next digit you type reassigns their filament).
  - Keep TPU parts out of the grey "left nozzle only" strip, or the slicer moves them to the left
    nozzle. Both nozzles reach X 25 to 325.
  - Clicks near the top toolbar can be refused in full-screen mode; cmd+R slices instead.
  - The send window maps filament to spools; it is another process, so the owner maps the TPU to
    the right external spool and clicks Send.
- **Heating from the Device tab:** the nozzle target fields take a typed value plus Return, and work
  from the background. The printer drops a manually set nozzle target back to about 38 C after a
  few idle minutes, so heat it only when the owner is at the printer, ready to load (about a
  minute to 250 C). The extruder arrows next to it are drawn, not real buttons: background clicks
  on them gave no confirmation and did not seem to run the motor (2026-11-20), so load filament
  from the printer's touchscreen instead.
- **Progress:** the Device tab's "Printing Progress" shows layer, percent and finish time. Its
  camera image may be stale ("Non-live image, captured at ..."), so don't trust it for "plate is
  clear".

## Settings that work

- **Process:** "0.20mm Standard @BBL H2D". Functional PETG parts use 4 walls and 30% grid infill.
  Toys and light parts in PLA are fine with 3 walls and 15 to 20%.
- **Orientation:** put the flattest functional face on the plate and avoid supports. Lab parts so far
  (hubs, cradles) print support-free by design.
- **PETG** sticks well to textured PEI. Dry it if it strings.
- **TPU 95A** ([Bambu's H2 TPU guide](https://wiki.bambulab.com/en/h2/h2d-tpu-printing-guide); it
  blocks automated fetches, so read it in the built-in browser):
  - It feeds the **right** hotend, not the left. The marked "TPU filament inlet" on the back is a
    bare pass-through: filament pushed in just drops inside until a tube is fitted.
  - Inside, at the filament buffer, unplug the right hotend's PTFE tube (this takes the AMS off
    that hotend) and plug it into the TPU inlet. Push the toolhead to its rear limit (behind the
    screen) so the tube length is right.
  - Unplug the tube at the toolhead, push the TPU through until it comes out, and heat the right
    hotend to 250 C. Push the filament into the extruder and tap the extruder's down arrow slowly.
    Once it extrudes steadily, plug the tube back into the toolhead.
  - Dry the TPU first. The guide lists glue stick or liquid glue on textured PEI for 95A. A 0.4 mm
    standard nozzle is fine for 95A; 85A needs 0.6 mm or more and direct feed.
  - In Bambu Studio, use the "Generic TPU" preset on the right nozzle. Afterwards, put the buffer
    tube back so the AMS feeds the right hotend again.
- **Fit tolerances on this printer** (PETG, measured): 0.2 mm per side for parts that slip together;
  printed outer diameters come out about 0.4 mm under on 108 mm (measured rim). Print a 20-minute
  test coupon of any interface before the full part.

## Rules

- **The printer is a heat source:** start a print only with the owner present and their go. The
  owner clicks Send, and confirms the plate is clear. One job at a time.
- **Log every print** in `docs/inventory.md` (Consumables: usage log and stock) in the same change:
  the slicer's grams, per spool.
- **Before designing a printed part,** follow "Before designing a part" in
  `experiments/exp003-household-robot/cad/README.md`.
- **Never ask the owner to measure** what a datasheet, CAD model or search can give. When a printed
  part must be measured, check the caliper can reach (jaws are about 40 mm) and show where the jaws
  go.
