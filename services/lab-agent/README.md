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
| `devices/` | Thin adapters: BroadLink IR, Kasa plug, fakes |

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
```

## Tests

`uv run pytest` from the repo root. `tests/test_contract.py` checks this package
against the shared fixtures and the generated JSON Schema.
