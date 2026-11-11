# exp000: IR bridge

Write-up: `content/experiments/exp000-ir-bridge.mdx`. Plan and run sheet: the
"Experiment 0" doc.

## Question

Can a $30 IR blaster, driven through the harness, hit at least 9/10 commands per
device, while a null test (nothing sent) scores near zero?

## Setup

```bash
# from the repo root
uv sync --all-packages --extra hardware
cp services/lab-agent/.env.example services/lab-agent/.env   # set RM4_HOST etc.
cd services/lab-agent

uv run lab discover                                   # find the RM4's IP
uv run lab learn --host $RM4_HOST \
  --codes ../../experiments/exp000-ir-bridge/codes/rm4-mini-living.json \
  fan_power fan_speed tv_power fireplace_power robot_forward robot_reverse
uv run lab tools
```

No hardware? Set `LAB_FAKE=1` and everything runs against fake devices
(device ids start with `fake-`).

## Bench notes (2026-11-10, first hardware session)

Which remotes the RM4 Mini can learn (it hears IR only, not RF or Bluetooth):

| Device | Remote | Result |
|---|---|---|
| Toy robot, remote 2 | IR, two buttons (forward; reverse = back and to the left) | learned, works |
| Toy robot, remote 1 | RF (pairs, blinks until paired) | not learnable |
| Samsung TV | Bluetooth smart remote | not learnable; TV obeys standard Samsung IR codes (`tv_*`) |
| Minka Aire ceiling fan | RF | not learnable; needs an RM4 Pro, maybe not even then |

What we learned about driving the robot:

- **Surges came from Wi-Fi, not the robot.** The first `robot.forward` re-sent the code
  from the Mac every 0.11 s, but each round trip to the RM4 took 0.2 to 0.4 s, so 1 s
  became 2 sends. Each learned code held about 3 frames, so the robot moved in "two
  rounds of three surges". Now the hold tools send one frame once and let the RM4 repeat
  it (`repeat` byte), so 1 s is 8 frames back to back: one smooth push.
- **A learned code can outlast the duration cap.** The first forward capture was 5.9 s
  of frames (button held while learning). The 3 s cap bounds how long we send, not what
  one packet plays, so `hold` now always trims to a single frame.
- **The remote sends a command frame, then a shared "still held" frame.** Forward sends
  its own frame about 4 times, reverse about 2, then both send the same frame while the
  button stays down. Picking the most common frame would make forward and reverse the
  same command, and the first frame can be glitched (reverse's was). `ir.one_frame` takes
  the first frame that repeats.
- macOS refuses broadcast to 255.255.255.255 ("No route to host"); `lab discover` now
  retries on the subnet broadcast. The RM4 must have "Lock device" off in the BroadLink app.

## Protocol

| Step | Command |
|---|---|
| 1. Warm-up session | `uv run lab session exp000-ir-bridge` |
| 2. 10 trials per device | `uv run lab trials exp000-ir-bridge fan.power -n 10` |
| 3. Null test | same, with `--dry-run` |
| 4. Replay run 2 | `uv run lab replay ../../events/exp000-ir-bridge/<run>.jsonl` |
| 5. Check + publish | `uv run lab validate ...`, `uv run lab sync`, then publish in /admin |

Fireplace: manual session only, with `!` to confirm, and you in the room. The gate
denies it in trials, replays and remote commands.

## Results

Computed on the site from the published runs listed in the write-up's front matter.
