# 3D printing in the lab

How an agent prints on the lab's printer, quickly and safely. Hard-won notes: add to them whenever
something new is learned.

## The printer

- **Bambu Lab H2D AMS Combo**, standard (not Pro), firmware 01.04.20.00. Two 0.4 mm nozzles,
  textured PEI plate.
- **Build area:** 325 x 320 x 325 mm on one nozzle; 300 x 320 x 320 mm where both nozzles reach.
  Larger parts split into pieces.
- **Nozzle layout (since 2026-11-21):** the **AMS 2 Pro** (firmware 02.04.19.87, has a drying mode)
  feeds the **left** nozzle: its tube and 6-pin cable go to the left side of the filament buffer
  (the lower buffer connector is the left extruder). The **right** nozzle is the TPU nozzle: its
  tube stays in the rear "TPU filament inlet", so soft TPU loads with no tube swap. Soft TPU (95A
  and below) never goes through the AMS, and the printer refuses Generic TPU on the left extruder.
  Before 2026-11-21 the AMS fed the right nozzle; moving it means re-running the AMS
  initialization on the touchscreen (Detect, or assign it to the left by hand), or the printer
  and Bambu Studio still treat it as the right nozzle's AMS. Check it before slicing: Prepare
  tab, **Sync info**; the Printer panel shows the AMS under the nozzle it feeds (the Device tab
  draws it on that side too). Restarting Bambu Studio does not change it; the printer holds it.
  The first try at re-binding on 2026-11-21 still read right; the owner fixed it on the
  touchscreen on the second try.
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
- **Another job already on the plate** (for example the owner's toy): leave it, click the toolbar's
  Add Plate (second icon), then `open -a BambuStudio file.stl` lands on the new plate.
- **Background clicks on the 3D canvas go to the last hovered toolbar icon** (2026-11-22): after
  clicking Add Plate, two more canvas clicks each added a plate. Remove strays with Edit > Undo
  (app menu), one at a time, and screenshot between. Buttons in the top bar (Slice plate) are fine.
- **Open several parts one file per `open` call** (2026-11-23): `open -a BambuStudio a.stl b.stl`
  pops "Object with multiple parts was detected", a dialog in another process that only the owner
  can answer (No keeps separate objects).
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
- **Move tool fields and process settings take typing only with full-screen control**
  (2026-11-21): in the background the X/Y fields and the Strength tab's fields ignore typed text.
  With full-screen control: triple-click the field, cmd+A, type, Return.
- **Never scroll the settings panel while a number field has focus:** the scroll changes the
  field's value. Scrolling up after setting infill to 30% turned it into 0 and an "Invalid numeric"
  error; the first slice of the base plate came out at 163 g instead of 223 g. Click empty canvas
  to leave a field before scrolling, and re-check the values before slicing.
- **The left nozzle (the AMS's) cannot reach the grey "Right nozzle only area".** A 300 mm part
  fits with its centre at X 160; at the default X 175 it ran into that strip and Studio flagged
  "laid over the boundary of plate".
- **Heating from the Device tab:** the nozzle target fields take a typed value plus Return, and work
  from the background. The printer drops a manually set nozzle target back to about 38 C after a
  few idle minutes, so heat it only when the owner is at the printer, ready to load (about a
  minute to 250 C). In the background the field needs app_type with mode replace (it
  selects its text on focus), then Return; on 2026-11-21 the target showed 250 but the reading
  had not moved before the owner's Unload took over, so confirm the temperature climbs, and
  prefer the printer's own Unload and Load, which heat for you. The extruder arrows next to it are drawn, not real buttons: background clicks
  on them gave no confirmation and did not seem to run the motor (2026-11-20), so load filament
  from the printer's touchscreen instead.
- **Two colours on one nozzle is two jobs** (2026-11-24): parts of different colours that share
  layer heights make the AMS swap twice per layer (about 260 swaps for a 26 mm plate: hours and
  more purge than the parts). Put each colour on its own plate and send them one after the
  other, or put the second colour on the right nozzle's external spool.
- **Background filament keys can land late** (2026-11-24): a number key sent to the canvas in
  the background did nothing at first, then applied to every selected object on the next
  action. Object-list row clicks fail in the background too. To colour objects on separate
  plates: load one colour's parts, Select all, press its number, then Add Plate and load the
  next; a newly loaded object is already selected. Edit > Delete all and `a` (arrange) act on
  every plate; arranging merged two plates into one.
- **Progress:** the Device tab's "Printing Progress" shows layer, percent and finish time. Its
  camera image may be stale ("Non-live image, captured at ..."), so don't trust it for "plate is
  clear".

## Settings that work

- **Process:** "0.20mm Standard @BBL H2D". Functional PETG parts use 4 walls and 30% grid infill.
  Toys and light parts in PLA are fine with 3 walls and 15 to 20%.
- **Orientation:** put the flattest functional face on the plate and avoid supports. Lab parts so far
  (hubs, cradles) print support-free by design.
- **Strength comes before a flat face** for anything that carries a load: a print is weakest across
  its layers, so orient it so the main bending runs along them. The exp003 wheel cradles printed
  back wall down, took the wheel's moment across their layers and rolled over under the robot's
  weight (2026-11-23; `experiments/exp003-household-robot/cad/WHEEL_MOUNT.md`). PETG also creeps
  under constant load, so loaded parts get more walls (6) and infill (40%).
- **Turning a part on its end turns its cross plates into shelves** (2026-11-24): the wheel
  module prints standing on its beam, and its rear gusset (a plate across the print direction)
  hung over air; Bambu Studio warned "floating cantilever". Every plate across the print axis
  must sit on something below it, or become a fin along the axis with a 45-degree start. Read
  the slicer's warnings before sending.
- **PETG** sticks well to textured PEI. Dry it if it strings.
- **TPU 95A** ([Bambu's H2 TPU guide](https://wiki.bambulab.com/en/h2/h2d-tpu-printing-guide); it
  blocks automated fetches, so read it in the built-in browser):
  - It feeds the **right** hotend, not the left. The marked "TPU filament inlet" on the back is a
    bare pass-through: filament pushed in just drops inside until a tube is fitted.
  - Set up once (done 2026-11-21, see "Nozzle layout"; kept here for a rebuild): inside, at the
    filament buffer, unplug the right hotend's PTFE tube (this takes the AMS off
    that hotend) and plug it into the TPU inlet. Push the toolhead to its rear limit (behind the
    screen) so the tube length is right.
  - Unplug the tube at the toolhead, push the TPU through until it comes out, and heat the right
    hotend to 250 C. Push the filament into the extruder and tap the extruder's down arrow slowly.
    Once it extrudes steadily, plug the tube back into the toolhead.
  - Dry the TPU first. The guide lists glue stick or liquid glue on textured PEI for 95A. A 0.4 mm
    standard nozzle is fine for 95A; 85A needs 0.6 mm or more and direct feed.
  - Loading with the toolhead end left plugged in also works (owner, 2026-11-20): move only the
    buffer end of the tube to the TPU inlet and push the TPU up the tube to the extruder.
  - In Bambu Studio, use the "Generic TPU" preset on the right nozzle.
  - **Unload with the printer's Unload** (touchscreen, or the Device tab's Unload button): it heats
    the nozzle, cuts the filament in the toolhead, then asks you to pull it back. Pull the TPU out
    from the rear inlet (the cut end is clean, so it slides out) and seal it in a bag with
    desiccant straight away: TPU soaks up moisture. Never pull TPU out cold without the cut; the
    end in the hotend is swollen and the gears hold it.
  - Proven 2026-11-21: two 120 mm tires (Generic TPU, 3 walls, 25% gyroid, 4 top and bottom
    layers, no brim) printed in 8 h 8 min from a freshly opened spool.
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
