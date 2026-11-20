# 3D printing in the lab

How an agent prints on the lab's printer, quickly and safely. Hard-won notes: add to them whenever
something new is learned.

## The printer

- **Bambu Lab H2D AMS Combo**, standard (not Pro), firmware 01.04.20.00. Two 0.4 mm nozzles,
  textured PEI plate.
- **Build area:** 325 x 320 x 325 mm on one nozzle; 300 x 320 x 320 mm where both nozzles reach.
  Larger parts split into pieces.
- **AMS 2 Pro** (firmware 02.04.19.87) feeds the **right** nozzle and has a drying mode. The
  **left** nozzle feeds from the external spool holder. TPU must go there, never through the AMS.
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
- **Progress:** the Device tab's "Printing Progress" shows layer, percent and finish time. Its
  camera image may be stale ("Non-live image, captured at ..."), so don't trust it for "plate is
  clear".

## Settings that work

- **Process:** "0.20mm Standard @BBL H2D". Functional PETG parts use 4 walls and 30% grid infill.
  Toys and light parts in PLA are fine with 3 walls and 15 to 20%.
- **Orientation:** put the flattest functional face on the plate and avoid supports. Lab parts so far
  (hubs, cradles) print support-free by design.
- **PETG** sticks well to textured PEI. Dry it if it strings.
- **TPU 95A:** external spool, the "Generic TPU" preset, slow.
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
