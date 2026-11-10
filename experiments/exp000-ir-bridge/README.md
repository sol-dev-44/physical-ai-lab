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
  fan_power fan_speed tv_power fireplace_power robot_forward robot_left robot_right
uv run lab tools
```

No hardware? Set `LAB_FAKE=1` and everything runs against fake devices
(device ids start with `fake-`).

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
