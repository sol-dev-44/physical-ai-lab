# Architecture

```mermaid
flowchart TB
  subgraph home["Lab machine (home LAN)"]
    cli["lab CLI: session / trials / replay"]
    agent["lab agent (queue worker)"]
    runner["Runner: one execution path"]
    gate["Safety gate"]
    dev["Device adapters: BroadLink IR, Kasa, later LeRobot arms"]
    log[("events/*.jsonl, append-only, source of truth")]
    labctl["labctl (Rust): validate, stats"]
    cli --> runner
    agent --> runner
    runner --> gate --> dev
    runner --> log
    log --> labctl
  end

  subgraph cloud["Supabase"]
    runs[("runs / events (published copy)")]
    queue[("commands queue + tools")]
  end

  subgraph web["apps/web (Vercel)"]
    pub["Public site: MDX write-ups + results from events"]
    admin["/admin: publish runs, queue commands"]
  end

  content[("content/*.mdx (git)")] --> pub
  log -- "lab sync (service role)" --> runs
  runs -- "anon, RLS: published only" --> pub
  admin -- "insert (admin RLS)" --> queue
  queue -- "claim_next_command (outbound poll)" --> agent
  agent -. "register tools" .-> queue
```

## Repo map

| Path | What |
|---|---|
| `packages/schema` | Event contract (zod source, generated JSON Schema, shared fixtures, TS fold) |
| `apps/web` | Next.js 16 site: public pages + gated `/admin` |
| `services/lab-agent` | Python: registry, safety gate, runner, devices, sync, queue worker |
| `crates/lab-events`, `crates/labctl` | Rust: contract mirror + log tooling |
| `experiments/<id>` | Per-experiment code, tool sets, protocol; any language |
| `content/` | MDX write-ups: `experiments`, `log`, `builds` |
| `supabase/` | Migrations and RLS tests |
| `docs/adr` | Decisions and their reasons |

## Invariants (each is enforced somewhere, not just written down)

| Invariant | Enforced by |
|---|---|
| Every implementation agrees on the event format | Shared fixtures in TS, Python and Rust tests; JSON Schema drift check |
| Python and Rust compute identical summaries on real runs | `scripts/crosscheck.sh` in CI |
| Logs are append-only and gap-free | `validate_log` in all three languages; DB triggers and unique `(run_id, seq)` |
| Nothing invalid is ever written | `EventLog.append` validates before writing |
| Hardware is reachable only through the gate | Runner is the only caller of handlers; web has no device path |
| Stale or remote commands can't fire dangerous tools | `claim_next_command` expiry; `manual_only` rule for `remote` |
| A timed action can't outlast its `seconds` | Gate caps `seconds`; `Blaster.hold` plays one frame with a repeat count (ADR 0008) |
| The web can only queue `(tool, args, confirmed)` as itself | Column grants + `commands_queue` policy (`requested_by = auth.uid()`), pinned in `rls_test.sql` |
| Only published runs are public | RLS policies, tested in `supabase/tests/rls_test.sql` |
| Write-ups have valid front matter | zod at build + `apps/web/test/content.test.ts` |
| Site builds with no secrets | CI builds without Supabase env |

## Known gaps

Not enforced yet; work around them, and fix them before the arms arrive.

- **One lab process per device.** The gate's rate limits live in each process, so a
  session and the agent (or two sessions) don't see each other's commands. Run one.
- **The agent runs only while someone keeps it running.** No launchd service yet.
- **`commands.run_id` stays empty** until runs are synced; the agent names its local run
  in `result` instead.
- **Run logs mix tuning and trials.** A bench session is a run like any other; mark it
  with notes and don't publish it as an experiment run.

## Adding things

- **New event type**: edit `packages/schema/src/event.ts`, `pnpm schema:gen`, add valid + invalid fixtures, mirror in Python and Rust, update the folds if it counts toward a summary. CI fails until all three agree.
- **New device**: adapter in `services/lab-agent/src/lab_agent/devices/`, no safety logic in it. Timed actions are played by the device (ADR 0008), not by a send loop.
- **New tool set**: a `build() -> Registry` function in the experiment's package; point `LAB_TOOLS` at it.
- **New experiment**: `experiments/expNNN-name/` (code) + `content/experiments/expNNN-name.mdx` (write-up). If Python, add it to `[tool.uv.workspace].members`.
- **New write-up collection**: schema in `apps/web/lib/content/collections.ts`, routes via `collectionIndex` / `collectionDetail`.
