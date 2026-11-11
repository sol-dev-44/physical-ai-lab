# lab-agent

The only process allowed to touch lab hardware. Python first because LeRobot and
the device libraries are Python; parts move to Rust when measurements say so
(see `docs/adr/0004-rust-policy.md`).

```
caller (CLI session | trials | replay | website queue | LLM later)
   └─> Runner.request(tool, args)
         ├─ command.requested
         ├─ SafetyGate.check  ──> safety.checked (allow | deny + rule)
         ├─ tool handler -> device adapter
         └─ command.sent | command.failed
       Runner.observe(...)   ──> outcome.observed
```

| Module | Job |
|---|---|
| `events.py` | Pydantic mirror of the event contract (`packages/schema`) |
| `log.py` | Append-only JSONL writer (fsync per line) and log validator |
| `registry.py` | Typed tools: name, args model, handler, safety metadata |
| `safety.py` | The gate: STOP file, allowlist, args, manual-only, confirmation, duration cap, rate limit |
| `runner.py` | The single execution path; logs every step with causal `parent_id` links |
| `replay.py` | Re-issue a run as a new forked run, paced like the original |
| `summary.py` | Fold a run into numbers; must match the TypeScript fold exactly |
| `sync.py` | Publish validated logs to Supabase (idempotent) |
| `agent.py` | Register tools, claim queued commands from the website, run them |
| `devices/` | Thin adapters: BroadLink IR, Kasa plug, fakes. No safety logic |
| `devices/ir.py` | Pure BroadLink IR packet helpers: decode, encode with a repeat count, pick one usable frame |

## Software e-stop

`touch STOP` in the agent's working directory and every command is denied
(logged as `rule: stop_file`). Remove the file to resume. This is not a substitute
for the hardware e-stop on the arms.

## Commands

```bash
uv run lab --help
uv run lab session exp000-ir-bridge          # interactive
uv run lab trials exp000-ir-bridge fan.power -n 10 [--dry-run]
uv run lab replay <log> [--dry-run]
uv run lab validate <log>...
uv run lab summary <log>
uv run lab sync                              # needs SUPABASE_* in .env
uv run lab agent exp000-ir-bridge            # serve the /admin command queue
uv run lab discover [--broadcast 192.168.1.255]
uv run lab learn --host <ip> --codes <codebook.json> name... [--wait 60]
```

## Devices: what to know

- **Holds are played by the device, not timed by the Mac.** A `Blaster.hold(code, seconds)`
  sends one frame once with a repeat count, so Wi-Fi latency (0.2 to 0.4 s per round
  trip to an RM4 Mini) can't chop a motion into bursts, and a long learned capture can't
  outlast `seconds`. See `docs/adr/0008-device-played-holds.md`.
- **Which frame:** `ir.one_frame` takes the first frame that repeats in a capture (skips
  a glitched first frame and a shared "still held" frame). No repeating frame: refused.
- **BroadLink:** "Lock device" must be off in the BroadLink app. macOS refuses the
  255.255.255.255 broadcast (`Errno 65`), so `discover` retries on the subnet broadcast.
  The RM4 Mini learns IR only; RF and Bluetooth remotes time out.
- **One process per device.** The gate and rate limits live in each process. Two lab
  processes (session + agent, or two sessions) don't see each other. Run one at a time.

## The agent (website commands)

`lab agent <experiment>` registers the tool set in Supabase, then polls
`claim_next_command` every 2 s and runs each command through the same Runner, marked
`remote`. It needs `SUPABASE_URL` and the **secret key** (`sb_secret_...`, Supabase:
Project Settings, API Keys) in `.env` on this machine only. Check the key without
printing it:

```bash
uv run python -c "from lab_agent.config import Settings as S; u,k=S.from_env().require_supabase(); print(u, k.startswith('sb_secret_'))"
```

The agent writes `status` and `result` (with the local run id) back to the command row.
It does not set `commands.run_id`: that column references `runs`, which only has a run
after `lab sync`. A failed status update is logged, never fatal. Remote control works
only while the agent runs; nothing restarts it yet.

## Tests

`uv run pytest` from the repo root. `tests/test_contract.py` checks this package
against the shared fixtures and the generated JSON Schema.
