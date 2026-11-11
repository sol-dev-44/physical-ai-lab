# Working in this repo

Read `docs/architecture.md` first. Rules that matter most:

- The event contract in `packages/schema/src/event.ts` is the source of truth. Changing it means:
  `pnpm schema:gen`, new fixtures (valid and invalid), and matching changes in
  `services/lab-agent/src/lab_agent/events.py` and `crates/lab-events/src/event.rs`.
  If the change affects counts, also `summary.ts`, `summary.py`, `summary.rs`, then `pnpm --filter @lab/schema gen:summaries`.
  Any change under `crates/lab-events` also needs `pnpm --filter @lab/events-wasm wasm` (the committed browser build).
- Hardware is only ever reached through `Runner.request` in lab-agent. Never add a device call anywhere else, and never put safety logic in a device adapter.
- The website never talks to devices. Admin actions insert rows; the agent decides.
  The web inserts only `(tool, args, confirmed)` into `commands`; the database fills `requested_by`.
- Timed device actions (holds) are played by the device from one frame with a repeat count,
  never by a send loop (ADR 0008). Learned IR codes go through `ir.one_frame`.
- Safety rules that depend on sensors are interlocks (`lab_agent/interlocks.py`), attached to the registry and run by the gate. Never in a camera or device module.
- Camera frames are never written, committed, synced or posted. exp001 keeps numbers only; the one exception is `exp001 snapshot --nobody-in-frame` into gitignored `media/` (ADR 0007).
- Run one lab process against hardware at a time (session, trials, replay or agent):
  each has its own gate and rate limits.
- Hardware facts (which remotes are IR, RM4 setup, bench notes): `experiments/exp000-ir-bridge/README.md`.
- Never commit `events/`, media, `.env*` (except `.env.example`), or anything identifying a child (ADR 0007).
- Keep strict settings on: no `ignoreBuildErrors`, no skipping lint, no `any` without a comment saying why.
- `apps/web` is Next.js 16 with Cache Components; read `apps/web/AGENTS.md` and the docs in `node_modules/next/dist/docs/` before changing data fetching.
- Before finishing: `pnpm check`, `uv run pytest`, `cargo test` (and `supabase/tests/run.sh` when touching SQL or anything that writes to Supabase).
