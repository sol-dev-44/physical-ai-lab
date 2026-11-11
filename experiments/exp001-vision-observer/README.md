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
logged. The one exception is `exp001 snapshot --nobody-in-frame`, for calibration: it
writes a single annotated frame to `media/exp001/` (gitignored, never synced) and refuses
to run without the flag. Never commit, sync or post a frame.

## Commands

Run from `services/lab-agent` (same `.env` and events dir as `lab`). Without
`arena.json`, real mode refuses; `--sim` (or `LAB_SIM=1`) runs everything in the
simulator, robot and camera both.

```bash
uv run exp001 --sim check                          # tracker on simulated frames
uv run exp001 --sim trials robot.forward -n 10     # a whole run, simulated
uv run exp001 cameras                              # which camera index is which
uv run exp001 snapshot --nobody-in-frame           # one frame to media/exp001/, for corners
uv run exp001 calibrate --corners X,Y X,Y X,Y X,Y --width 120 --height 90 --camera 1
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

Software ready and tested against the simulator (2026-11-10). Real camera not wired yet.
