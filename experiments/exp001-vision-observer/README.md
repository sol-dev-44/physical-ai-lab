# exp001: vision observer

Write-up: `content/experiments/exp001-vision-observer.mdx`.

## Question

Can a webcam replace the human judge? Target: the camera agrees with a human on at least
95% of robot trials, and scores the null test (nothing sent) at 0.

This is step 1 of three. Step 2 measures the robot's motion model (how far forward goes
per second, how reverse arcs). Step 3 is the RL experiment: drive to a taped target with
only "straight forward" and "back-left arc", a planner against tabular Q-learning, with
the camera giving the reward.

## How it works

```
overhead camera -> LivePose (tracks, drops each frame) -> pose in arena cm
                                  |                          |
              gate interlocks: fresh_pose, arena_fence     judge(before, after)
                                  |                          |
lab Runner.request -> RM4 hold ---+         outcome.observed (method: camera)
```

- **Markers:** a neon green sticker on the robot's head (front) and a pink one on its
  back. Position is their midpoint, heading points tail to head. Colours are HSV ranges
  in `arena.json`.
- **Two tracking modes** (`tracking` in `arena.json`):
  - `markers`: two stickers in colours found nowhere else in view (front and back).
  - `background`: the robot is whatever differs from a stored picture of the empty arena,
    and one front colour *inside* the robot's outline gives the heading. Use it when the
    floor shares the sticker colours (the Botley mats are orange like the exp000 robot's
    triangles) or has glare. Needs steady light; retake the background when it changes.
    A blob too big to be the robot (a hand, a person) reads as "not tracked", so the gate
    stops motion.
- **Arena:** a taped rectangle. `arena.json` holds its size in cm and the four corner
  pixels, in order origin, +x, +x+y, +y going counterclockwise seen from above. That
  order makes left turns positive, whatever the camera's orientation.
- **Interlocks (in the gate, `lab_agent.interlocks`):** no fresh camera fix (older than
  1 s) denies every move; a move whose predicted end, plus slack, comes within 10 cm of
  an edge is denied. The motion numbers in `tools.py` are deliberately pessimistic until
  step 2 measures the real ones, so expect the fence to stop runs early.
- **Judge:** forward succeeds if the robot moved at least 5 cm ahead along its starting
  heading; reverse if it moved at least 5 cm and backwards. The log records `along_cm`,
  `lateral_cm`, `turn_deg` and `moved_cm` too.
- **Human labels:** with `--human`, you're asked "did it work?" **before** the camera's
  verdict is printed. Your answer is a `note` linked to the same command
  (`human_success`), so run summaries count only the camera's observation and
  `exp001 report` pairs the two.

## Privacy (ADR 0007)

The camera can see people. Frames are tracked and dropped in memory; only numbers are
logged. Two commands write a frame, both refuse without `--nobody-in-frame`, and both
write only to `media/exp001/` (gitignored, never synced): `snapshot` (calibration) and
`background` (the empty arena). Never commit, sync or post a frame. If a frame turns out
to show a person, delete it at once. (2026-11-10: a snapshot from the wrong camera caught
people; it was deleted, and snapshots now open the camera by name.)

## macOS camera notes

- The Claude app can't get camera permission; camera commands run in **Terminal**
  (it asks once; allow it). `scripts/camera_permission.py` waits for the answer.
- OpenCV's camera numbers don't follow macOS's order. Snapshots open the camera by name
  (ffmpeg); `exp001 cameras --match "HD Pro Webcam C920"` finds the OpenCV index by
  comparing pictures (on the lab Mac the C920 is OpenCV camera 0).
- Live view for people: `ffplay -f avfoundation -video_size 1920x1080 -i "HD Pro Webcam C920"`
  (add `-vf "crop=iw/1.5:ih/1.5"` for the 1.5x zoom). Nothing is recorded.

## Commands

Run from `services/lab-agent` (same `.env` and events dir as `lab`). Without
`arena.json`, real mode refuses; `--sim` (or `LAB_SIM=1`) runs everything in the
simulator, robot and camera both.

```bash
uv run exp001 --sim check                          # tracker on simulated frames
uv run exp001 --sim trials robot.forward -n 10     # a whole run, simulated
uv run exp001 cameras                              # which camera index is which
uv run exp001 snapshot --nobody-in-frame           # one frame to media/exp001/, for corners
uv run exp001 background --nobody-in-frame --camera-name "HD Pro Webcam C920" --zoom 1.5
uv run exp001 calibrate --corners X,Y X,Y X,Y X,Y --width 61 --height 41 --camera 0 \
  --camera-name "HD Pro Webcam C920" --zoom 1.5 --tracking background --front orange
uv run exp001 check                                # real camera: is the robot tracked?
uv run exp001 trials robot.forward -n 10 --human   # camera + you
uv run exp001 trials robot.forward -n 10 --dry-run # null test
uv run exp001 report ../../events/exp001-vision-observer/*.jsonl
```

One lab process at a time: stop the agent before running trials here.

## Wiring the real camera (next)

1. Camera: an iPhone via Continuity Camera or a USB webcam, pointing straight down,
   seeing the whole taped arena. macOS will ask for camera permission once.
2. Stickers on the robot: neon green on the head, pink on the back, about 2 to 3 cm.
3. `exp001 cameras`, then `snapshot --nobody-in-frame`, read the four corner pixels
   off it, `calibrate`, then `check` until the robot is found in at least 90% of frames.
4. Tune the HSV ranges in `arena.json` if the floor or lighting confuses a colour.
5. Then 10 trials per move with `--human`, and a null test.

## Status (2026-11-11, afternoon)

**Working.** Camera-judged, steered, fenced data collection on a taped floor arena: 30
moves, 29 of 29 tracked moves judged correctly, robot kept in the middle with no fence
denials and no recovery. Results below ("Session 2").

**Setup.** C920 overhead at full frame (zoom 1.0) over a duct-tape rectangle on the wood
floor, 94.5 x 69.5 cm inside the tape. `tracking: background`, `heading_from: none`:
the camera gives position only and each move sets the heading (forward travel points the
way Wall-e faces, reverse travel the opposite way, corrected by `move_turn_deg`). Stickers
are no longer needed for tracking.

**Resume in this order.**
1. If the camera, tape or light moved: Wall-e out, nobody in the whole frame,
   `exp001 background --nobody-in-frame`, refit corners, `calibrate` (see Gotchas).
2. `lab discover` (wakes and checks the RM4). Wall-e on, in the middle of the tape (the
   first move is only allowed if it's safe in any direction).
3. `exp001 collect -n 30`. Then the human-agreement trials and the null test (next).

**Next.** Human agreement (`trials --human`, both moves) and the null test, with the
heading-from-motion judge; `motion --save` should learn `base_cm` and turn per move
directly; the SimRobot should get the measured fixed step and right turn.

## Data so far (2026-11-10)

Run logs are in `events/exp001-vision-observer/` (local; `-sim` runs are simulated).

| What | Result | Trust |
|---|---|---|
| Still robot, 20 frames | +-0.1 cm, +-1 deg | good |
| `check`, 5 s | robot found in 100% of 42 frames (about 8 fps) | good |
| Heading calibration, forward 0.5 s | moved 6.4 cm toward 3 deg; markers said -25 deg, offset +28.4 | good |
| Forward 0.5 s (collect) | 3.6 to 4.7 cm | low: tracking flipped between two places |
| Reverse 0.3 s (collect) | 2.4 to 4.7 cm, turning left 2 to 8 deg | low |
| Forward 0.3 s | 0.5 to 1.1 cm | short pulses barely move him |
| Forward 0.75 s, last move | 0 cm | tracking lost by then (mats moved) |
| Gate | 21 moves denied by `arena_fence`, 6 by `fresh_pose` after tracking was lost | working as designed |

The collect numbers are provisional: between moves the pose alternated between about
(30, 22) and (50, 12) cm, because the mats had shifted and the camera re-balanced, so the
background tracker saw two regions. Re-collect before fitting.

## Session 2 (2026-11-11): taped floor arena

**Setup.** Mats gone; a duct-tape rectangle on the wood floor, 94.5 x 69.5 cm inside the
tape, the C920 at full frame (zoom 1.0, about 12 px/cm). Corners fitted to the tape's
inner edges (under 1 px residual). `heading_from: back_to_body` (see below), heading
offset re-measured at +146.9 deg (1.0 s forward moved 15.1 cm).

**Still robot:** found in 100% of frames, position +-0.1 cm, heading +-3 deg.

**First collect (7 of 30 moves, then stuck):** the before-poses jumped between moves
(x 78, 45, 69, 56 cm) more than the moves themselves, three reverses read exactly 0.0 cm,
and afterwards Wall-e wasn't visible in the arena. Suspected: the RM4 Mini's position,
so some sends didn't reach Wall-e depending on which way he faced (his IR receiver is
directional). The RM4 was moved to a better spot before the next try. Treat this run's
numbers as unreliable. Log: `exp001-20261111-141410-collect.jsonl`.

**Recovery (added 2026-11-11).** If Wall-e is near or past the tape, `collect` switches
to recovery: it tries the move predicted to end furthest from the edges, and the fence
(`ArenaFence.recovery`) allows a move there only if even its worst case ends further in
than he is now. After 4 recovery moves in a row without getting back inside the margin it
stops as "stuck". The tracker now also looks 15 cm beyond the tape
(`background.look_beyond_cm`), so a stray robot is still seen. Every recovery move is a
normal gated, logged request; its `outcome.observed` note starts with `recovery:`.
**To do:** fine-tune recovery from results (how often it's needed, how many moves it
takes, whether reverse's left arc should be planned for rather than covered by slack).
Count them with `grep '"note": "recovery' events/exp001-vision-observer/*.jsonl`.

**Third collect (22 moves, `exp001-20261111-143906-collect.jsonl`): the distance model.**
Distance travelled doesn't depend on heading, so it's trustworthy even while the heading
isn't (below):

| Move | Fit | Mean error | Moves |
|---|---|---|---|
| forward | 16.9 cm + 12.1 cm/s x seconds | 1.4 cm | 10 |
| reverse | 15.8 cm + 14.8 cm/s x seconds | 1.5 cm | 11 |

Every press moves Wall-e about 16 cm, even 0.3 s; holding adds about 13 cm per second. So
duration is a weak control: the action space is close to "one step forward" and "one
step back-left". The fence assumed distance = speed x seconds and under-predicted short
moves about 4x, which is how he reached the edge. `Motion.base_cm` fixes that;
`arena.json` now has the fitted numbers (slack 0.4 / 0.6).

**Heading is the weak link.** Still, back sticker to body centre is steady (+-3 deg), but
after moves the judged direction was often sideways or backwards (forward judged
"backward" 8 times), so camera verdicts from this run aren't trustworthy. Next: a bright
front sticker that contrasts with dark wood (pink or blue, about 5 cm) and
`heading_from: front`, then re-run `heading`.

**Fourth collect (`-150440`), blue front + orange back on the base: 8 of 8 right, then lost.**
Steering kept him central, but from the camera's angle his head hides the front sticker
for some headings. Fifth (`-151433`), blue on the tracks: heading readings jumped up to
110 deg while moving; steering drove him to the edge in 3 moves. Stickers on this toy
don't give a usable heading in motion.

**Sixth collect (`exp001-20261111-151917-collect.jsonl`): heading from motion, 30 moves.**

| Result | Value |
|---|---|
| Moves sent / tracked / judged right | 30 / 29 / 29 (the last: lost or asleep) |
| Where he stayed | x 37 to 64 cm, y 25 to 55 cm; 0 fence denials, 0 recovery |
| Forward per press | 20.3 cm mean (0.3 s: 15 to 22 cm), +-1.6 cm; drifts 5.2 cm right |
| Reverse per press | about 18 cm (0.3 s: 15 to 21 cm), +-1.6 cm; drifts 3.7 cm left of the line |
| Turn per press | forward -14.8 deg (sd 5.3), reverse -11.1 deg (sd 9.3): both turn right |

Both buttons turn him clockwise seen from above; "back and to the left" is the tail
swinging left. Duration barely matters (0.3 s and 0.5 s forward differ by about 1 cm),
so the useful action set is {forward step, reverse step}. `arena.json` has these as
fence motions (`base_cm`, direction, slack 0.35) and `move_turn_deg`.

Caveat: with heading from motion, the judge checks each move against the heading the
previous move implied. It catches a move in the wrong direction, but it isn't
independent of the robot's own motion; the human-agreement trials are the real test.

## Gotchas and hints

**macOS and the camera**
- The Claude app can't get camera permission. Run camera commands in **Terminal** (it asks
  once). From a Claude session: `osascript -e 'tell application "Terminal" to do script
  "cd ~/physical-ai-lab/services/lab-agent && uv run exp001 ... > LOG 2>&1; echo EXIT $? >> LOG"'`,
  then poll LOG. Write straight to a file: piping through `grep | tee` killed a run.
  Terminal truncates very long `do script` commands: put long paths in a small shell
  script and run that.
- OpenCV camera numbers don't follow macOS's list. The C920 is OpenCV **0** here even
  though ffmpeg lists it as 1. Open by name (`grab_by_name`), or `cameras --match NAME`.
- A snapshot from the wrong index caught people; it was deleted. Only snapshot by name,
  only with nobody in view, and delete anything that shows a person.
- Live view for a person: `ffplay -f avfoundation -video_size 1920x1080 -i "HD Pro Webcam
  C920" -vf "crop=iw/1.5:ih/1.5"`. ffplay can only zoom by cropping; so does the tracker.
- Terminal needs Local Network permission to reach the RM4 (macOS may ask once).

**Python environment**
- Always `uv sync --all-packages --extra hardware` on the lab machine. A plain sync
  removed broadlink and the first real move failed (`command.failed`, robot didn't move).

**Tracking**
- A bumped camera shows up as the whole tape outline "changing". Retake the background
  and refit the corners. The tracker now ignores shiny tape (`ignore_tape`) and takes the
  biggest robot-sized region (`max_robot_px` 60000 at zoom 1.0), not the biggest region.
- Corner fitting: glare inside the tape fools a plain colour threshold. Walk inward from
  the middle of the tape strip to the first run of floor pixels, then fit lines robustly.
- The empty-floor picture must have nobody in the whole frame, not just the arena: the
  camera sees about 45 cm past the tape on the left. A foot at the edge meant a retake.
- Colour stickers fail when the floor shares their colour (orange triangles on orange
  mats). Use `background` tracking, or colours found nowhere else (green, pink).
- Shadows: count colour change (Lab a/b > 30) separately from lightness (> 80).
- Auto exposure / white balance: a dark robot entering view shifts the whole picture.
  The tracker removes the median global shift (simulator-tested; confirm live).
- The background is stale the moment anything in the arena moves: mats, toys, a hand.
  Symptom: one huge blob (whole mat area) and `tracker: None`. Fix: retake `background`.
- A marker near the robot's middle gives a noisy heading. Back marker inside the body
  helps; `exp001 heading` measures the offset so stickers needn't be on the centre line.
- Use `scripts/blobs.py` (all changed regions), `jitter.py` (still-robot steadiness) and
  `diagnose.py` before guessing. None of them saves a frame.

**Timing (found 2026-11-11, second collect)**
- `hold()` returns when the RM4 has finished playing the move (send overhead is about
  50 ms; the rest of `latency_ms` is the move). But the old judge read "after" from the
  next 5 frames, and `settle` returned the previous pose whenever a frame wasn't tracked,
  so coasting, buffered webcam frames and lost frames all leaked in: exact 0.0 cm moves
  and "before" poses that jumped. Now: wait `COAST_S` (0.4 s), then 3 fresh fixes in a
  row within 0.7 cm, else None. Log `exp001-20261111-142730-collect.jsonl` predates it.

**Markers on Wall-e (superseded by heading from motion)**
- His head swivels while he drives and overhangs the front of his base, and from the
  camera's angle his head and body hide stickers for some headings. Head, base and track
  stickers all failed once he moved. Use `heading_from: none` (position only, heading
  from each move); stickers are optional.

**Robot and fence**
- Place the RM4 where it sees Wall-e from every heading in the arena (high, pointing
  down at the arena, or beside the camera). His IR receiver is directional, and a missed
  send reads as a 0.0 cm move.
- Every press moves him about 20 cm, even 0.3 s (the 2026-11-10 "0.3 s barely moves
  him" was tracking error). He switches himself off when idle: if moves stop
  registering, `collect` stops with "asleep" (exit 3) or "lost" (exit 5); switch him on.
- In a 61 x 41 cm arena the default fence (25 cm/s, big slack, 10 cm margin) allowed
  almost nothing. Measure, then `motion --save`; a bigger arena (1 m x 80 cm) helps RL.
- Only one lab process at a time: stop the agent (and its /admin buttons) for camera runs.
