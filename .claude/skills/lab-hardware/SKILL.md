---
name: lab-hardware
description: Drive the lab's real hardware (RM4 Mini IR blaster, toy robot, TV) through the lab-agent safely - check the RM4, learn IR codes, run a session or trials, start the agent for /admin, or send moves while the agent runs. Use when asked to move the robot, test a remote, learn a code, run exp000 trials, or make the /admin controls work.
---

# Driving the lab hardware

Read `experiments/exp000-ir-bridge/README.md` first: device table, RM4 checklist, which
remotes are IR, and bench notes. Rules that never bend:

- Hardware only through `Runner.request` (lab CLI or agent). No direct `broadlink` sends
  from scripts. (`lab discover` and `lab learn` are the setup exceptions.)
- **One lab process against the hardware at a time.** Each has its own gate and rate
  limits. If the agent is running, send moves through it (below), don't open a session.
- Fireplace: manual session, `!` confirmation, the person in the room. Never automated.
- Never print, echo or paste the Supabase secret key. Never publish or `lab sync` runs
  without Alan's say-so (device list not final).
- Robot moves: `{"seconds": s}` with 0 < s <= 3. Tell the person before you send.

All commands run from `services/lab-agent`.

## 1. Is the RM4 there?

```bash
uv run lab discover
```

Expect `RM4MINI`, its IP (`RM4_HOST` in `.env`), and `locked: no`. Locked: the person turns
off "Lock device" in the BroadLink app. Nothing found: 2.4 GHz Wi-Fi, same network.

## 2. Learn a code (person presses the remote)

`lab learn` needs Enter per code, so it's for the person's terminal. From Bash, run the
same thing with Enter supplied, in the background, and tell the person to press the button
while the RM4's LED is on (it re-arms every 25 s for 60 s):

```bash
printf '\n' | uv run lab learn --host "$RM4_HOST" --codes ../../experiments/exp000-ir-bridge/codes/rm4-mini-living.json robot_forward
```

Output gives frames captured and whether a usable frame was found. A timeout means the
remote is RF or Bluetooth, or was pressed while the LED was off. One remote at a time.
New tool? Add it in `experiments/exp000-ir-bridge/src/exp000_ir_bridge/tools.py`
(press for toggles, hold for motion).

## 3. Interactive session driven from Bash

The person watches; you type. Feed `lab session` from a FIFO so you can answer y/n after
asking what they saw:

```bash
F="${TMPDIR:-/tmp}/lab.fifo"; rm -f "$F"; mkfifo "$F"
(sleep 3600 > "$F" &)                       # keeps the pipe open
PYTHONUNBUFFERED=1 uv run lab session exp000-ir-bridge < "$F"    # run_in_background
echo 'robot.forward {"seconds": 1}' > "$F"  # then read the output for "sent."
echo 'y smooth push' > "$F"                 # the person's answer, their words as the note
echo end > "$F"; pkill -f "sleep 3600"
```

Always record an observation after each command, and `end` the run when done.

## 4. Website control (/admin Wall-e Robot panel)

```bash
uv run lab agent exp000-ir-bridge           # run_in_background; prints each command it handles
```

Needs `SUPABASE_URL` and the `sb_secret_` key in `.env` (the person pastes it; check with
the one-liner in `services/lab-agent/README.md`). It dies when the session ends.

While it runs, send moves by queuing rows, exactly like the website:

```bash
uv run python -I -c "
import httpx; from lab_agent.config import Settings
u,k=Settings.from_env().require_supabase()
h={'apikey':k,'Content-Type':'application/json','Prefer':'return=minimal'}
httpx.post(f'{u}/rest/v1/commands',headers=h,json={'tool':'robot.forward','args':{'seconds':1}}).raise_for_status()"
```

Space queued moves by at least their duration plus 2 s (poll interval); rows older than
60 s expire. Results show in the agent's output and in `/admin`.

## 5. Trials (the experiment itself)

`lab trials` asks y/n per trial, so drive it like the session (FIFO) or let the person
run it. Null tests add `--dry-run`. Log notes say what happened, in the person's words.

## If something's off

- Surges or stutter: the hold isn't using `Blaster.hold` (ADR 0008).
- One direction does nothing: check `ir.one_frame` on its capture; relearn with one short press.
- `No route to host` from a terminal tab while Bash reaches the RM4: drive from Bash.
- `/admin` "permission denied for table commands": the web is sending a column other
  than `tool, args, confirmed`.
