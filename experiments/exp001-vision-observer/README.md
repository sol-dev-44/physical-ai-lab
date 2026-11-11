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

## Status

2026-11-10: software tested against the simulator. Logitech C920 connected, overhead at
1.5x zoom over six 8-inch Botley mats (about 61 x 41 cm); the robot is about 22 x 20 cm,
so the fence allows only short moves. Markers: a dark green circle at the front and the
orange checkered triangles at the back (orange matches the mats, hence `background`
tracking). Calibrated: corners from the empty-mat frame, shadow-tolerant thresholds
(chroma 30, lightness 80; Wall-e's shadow had doubled the blob), heading offset +28.4 deg
from one forward move (stickers sit diagonally). First measurement: forward 0.5 s moved
6.4 cm (about 13 cm/s). `check`: robot found in 100% of frames at about 8 fps.
