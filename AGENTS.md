# Working in this repo

Read `docs/architecture.md` first. Rules that matter most:

- The event contract in `packages/schema/src/event.ts` is the source of truth. Changing it means:
  `pnpm schema:gen`, new fixtures (valid and invalid), and matching changes in
  `services/lab-agent/src/lab_agent/events.py` and `crates/lab-events/src/event.rs`.
  If the change affects counts, also `summary.ts`, `summary.py`, `summary.rs`, then `pnpm --filter @lab/schema gen:summaries`.
- Hardware is only ever reached through `Runner.request` in lab-agent. Never add a device call anywhere else, and never put safety logic in a device adapter.
- The website never talks to devices. Admin actions insert rows; the agent decides.
- Never commit `events/`, media, `.env*` (except `.env.example`), or anything identifying a child (ADR 0007).
- Keep strict settings on: no `ignoreBuildErrors`, no skipping lint, no `any` without a comment saying why.
- `apps/web` is Next.js 16 with Cache Components; read `apps/web/AGENTS.md` and the docs in `node_modules/next/dist/docs/` before changing data fetching.
- Before finishing: `pnpm check`, `uv run pytest`, `cargo test`.
