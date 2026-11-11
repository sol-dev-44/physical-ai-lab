# exp000: IR bridge

Write-up: `content/experiments/exp000-ir-bridge.mdx`. Plan and run sheet: the
"Experiment 0" Claude Doc (Alan edits it). Bench history: the log entry
`content/log/2026-11-10-first-hardware-session.mdx`.

## Question

Can a $30 IR blaster, driven through the harness, hit at least 9/10 commands per
device, while a null test (nothing sent) scores near zero?

## Hardware, as of 2026-11-10

| Device | Remote | Status | Tools |
|---|---|---|---|
| BroadLink RM4 Mini (`rm4-mini-living`) | n/a | on Wi-Fi, unlocked, reachable | the blaster |
| Toy robot ("Wall-e"), remote 2 | IR, 2 buttons: forward; reverse = back and to the left | learned, drives smoothly | `robot.forward`, `robot.reverse` |
| Toy robot, remote 1 | RF (blinks until paired) | not usable with an RM4 Mini | none |
| Samsung TV | Bluetooth smart remote | TV obeys standard Samsung IR codes; not yet tested on this TV from the lab | `tv.power`, `tv.volume_up`, `tv.volume_down` |
| Minka Aire ceiling fan | RF | not usable with an RM4 Mini (RM4 Pro might, unproven) | `fan.*` registered but no codes |
| Fireplace | not checked | no code | `fireplace.power` (manual only) |
| Kasa plug | none found on the network | `lamp.*` falls back to a fake | `lamp.on`, `lamp.off` |

The final device list is not decided. **Publish nothing** until Alan confirms it.

## Setup

```bash
# from the repo root
uv sync --all-packages --extra hardware          # broadlink + python-kasa
cp services/lab-agent/.env.example services/lab-agent/.env
cd services/lab-agent

uv run lab discover                              # IP, model, and whether it is locked
# put the IP in .env as RM4_HOST (the lab machine's is 192.168.1.152)
uv run lab learn --host <RM4 IP> \
  --codes ../../experiments/exp000-ir-bridge/codes/rm4-mini-living.json \
  robot_forward robot_reverse
uv run lab tools
```

No hardware? Set `LAB_FAKE=1`, or leave `RM4_HOST` unset, and everything runs against
fakes (device ids start with `fake-`, so a fake run can never pass as real).

### RM4 Mini checklist

1. Pair it with the BroadLink app on **2.4 GHz** Wi-Fi (no 5 GHz, no guest network that
   isolates clients). Give it a DHCP reservation.
2. In the app: device, then the three dots, then Property or Settings: **Lock device off**.
   A locked RM4 is visible to `lab discover` (`locked: yes`) but refuses authentication.
   Adding it to Alexa or Google Home can turn the lock back on.
3. `lab discover` should list it. On macOS the global broadcast fails with
   `[Errno 65] No route to host`; discover retries on the subnet broadcast
   automatically (`--broadcast 192.168.1.255` to force one).

### Is a remote learnable?

The RM4 Mini hears **IR only**. RF (radio) and Bluetooth remotes cannot be learned.

- The phone-camera test is unreliable: iPhone rear cameras filter IR. Use the front
  camera in a dim room, or skip the test.
- Better tests: cover the remote's tip and press; if the device still responds, it is
  not IR. Remotes that pair, blink until paired, or work through walls are RF/Bluetooth.
  Smart TV remotes (Samsung, Roku, Fire TV, Google TV) are usually Bluetooth even when
  they have a dark window on the front.
- The real test is `lab learn`: it listens for 60 s, re-arming every 25 s (the RM4's LED
  is on while listening and goes off briefly between arms, and when it captures).
  Hold the remote 2 to 3 cm from the RM4 and press **only while the LED is on**.
- Test one remote at a time. Two remotes in range make captures you can't attribute.
- No learnable remote? The device may still obey IR: the BroadLink app's brand list
  ("Add remote", then the type and brand) proves it, but its codes live in BroadLink's
  cloud. For the lab, use a published code set. The Samsung codes here are the public
  Samsung32 protocol (`tv_power` E0E040BF, volume up E0E0E01F, down E0E0D02F, mute E0E0F00F).

### How a learned code is used

`lab learn` prints how many frames it captured and whether a usable frame was found.
A capture contains every frame the remote sent while the button was down:

- Press tools (`tv.power`, `fan.power`) send the capture as is.
- Hold tools (`robot.*`) send **one frame**, and the RM4 repeats it on its own
  (the packet's repeat byte) for the requested seconds. `ir.one_frame` picks the frame:
  the **first frame that repeats**. It skips a glitched first frame (captured as the
  button went down) and never picks the "still held" frame this robot's remote sends
  for every button after the first few command frames. A capture where no frame
  repeats is refused; learn it again with one short press.

## Driving it

```bash
uv run lab session exp000-ir-bridge          # interactive; prompt is "<run_id>>"
```

```
robot.forward {"seconds": 1}       # 0 < seconds <= 3, enforced by the gate
y smooth push                      # record what you saw: y or n, plus a note
robot.reverse {"seconds": 1}
tv.volume_up
end                                # or: abort
```

**One lab process at a time.** Rate limits and the safety gate live in each process, so
two sessions (or a session plus the agent) don't see each other's commands. Close one
before starting another.

### From the website

`/admin` has a **Wall-e Robot** panel (Forward, Reverse, 0.5 to 3 s) and a generic
command form. Both only queue a row; nothing moves unless the agent is running here:

```bash
uv run lab agent exp000-ir-bridge            # needs SUPABASE_URL + the sb_secret_ key in .env
```

Website commands are `remote`: the fireplace is always denied, commands older than
60 s expire, and every step lands in the agent's own run log (`<run_id>-agent`).

## Protocol

| Step | Command |
|---|---|
| 1. Warm-up session | `uv run lab session exp000-ir-bridge` |
| 2. 10 trials per tool | `uv run lab trials exp000-ir-bridge robot.forward -n 10 --args '{"seconds": 1}'` |
| 3. Null test | same, with `--dry-run` (nothing is sent; answer honestly) |
| 4. Replay a run | `uv run lab replay ../../events/exp000-ir-bridge/<run>.jsonl` |
| 5. Check | `uv run lab validate ../../events/exp000-ir-bridge/*.jsonl` |
| 6. Publish | `uv run lab sync`, then publish in `/admin`, **only after Alan confirms the devices** |

Repeat step 2 for `robot.reverse` and each TV tool. Fireplace: manual session only, with
`!` to confirm, and you in the room. The gate denies it in trials, replays and remote
commands.

## Bench notes (2026-11-10, first hardware session)

- **Surges came from Wi-Fi, not the robot.** The first `robot.forward` re-sent the code
  from the Mac every 0.11 s, but each round trip to the RM4 took 0.2 to 0.4 s, so 1 s
  became 2 sends. Each learned code held about 3 frames, so the robot moved in "two
  rounds of three surges", and reverse gave two "baby" reverses. Playing one frame on
  the RM4 with the repeat byte (1 s = 8 frames of 127 ms) gives one smooth push.
- **A learned code can outlast the duration cap.** The first forward capture was 5.9 s
  of frames (button held while learning). The 3 s cap bounds the `seconds` argument;
  without trimming, one packet would have played for 5.9 s.
- **Command frame, then a shared hold frame.** Forward sends its own frame about 4 times,
  reverse about 2, then both send the same frame while held. A "most common frame" rule
  turned forward into the hold frame; reverse's first frame was glitched and did nothing.
  "First frame that repeats" works for both (verified: smooth forward and reverse).
- **TV remote:** learning timed out three times (Bluetooth). The BroadLink app's Samsung
  brand codes worked at once.
- **Fan and robot remote 1:** RF, nothing captured.
- The run logs from this session are in `events/exp000-ir-bridge/` (local only). They
  mix tuning commands with real ones, so they are not experiment runs.

## Results

Computed on the site from the published runs listed in the write-up's front matter.
