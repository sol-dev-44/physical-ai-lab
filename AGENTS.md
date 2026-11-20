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
- Photos, recordings and personal information are the owner's call (ADR 0013): when the owner
  asks for something done with them, do it. Don't add personal information to the public repo
  or site on your own initiative. exp001 still drops frames and asks for `--nobody-in-frame`
  before writing one, until the owner says otherwise.
- On the lab machine always sync with `uv sync --all-packages --extra hardware`. A plain
  `uv sync` removes broadlink/python-kasa, and every real send then fails with
  `ModuleNotFoundError` (happened 2026-11-10).
- Run one lab process against hardware at a time (session, trials, replay or agent):
  each has its own gate and rate limits.
- Camera work (exp001): read its README's "Gotchas and hints" first. Camera commands run in macOS Terminal, never in this app.
- Hardware facts (which remotes are IR, RM4 setup, bench notes): `experiments/exp000-ir-bridge/README.md`.
- Printed parts: before proposing, modelling or printing a part, work through "Before designing a part"
  in `experiments/exp003-household-robot/cad/README.md` (every face of every component, every mounting
  option, every fastener, and whether each requested measurement can actually be taken).
- What the lab owns, where it is, and what's on order: `docs/inventory.md`. Check it before ordering,
  and update it in the same change when a part arrives, gets assigned, breaks or is used up.
- Never commit `events/` or `.env*` (except `.env.example`). Commit media or personal information
  only when the owner asks (ADR 0013). Published arm clips live in `apps/web/public/clips/` (ADR 0011).
- Keep strict settings on: no `ignoreBuildErrors`, no skipping lint, no `any` without a comment saying why.
- `apps/web` is Next.js 16 with Cache Components; read `apps/web/AGENTS.md` and the docs in `node_modules/next/dist/docs/` before changing data fetching.
- Before finishing: `pnpm check`, `uv run pytest`, `cargo test` (and `supabase/tests/run.sh` when touching SQL or anything that writes to Supabase).

## Shipping and environment

- Vercel deploys every merge to `main` straight to production. Merging is deploying, so
  get the owner's go before merging a PR. Each PR gets a preview deployment, but previews
  sit behind Vercel sign-in (a plain `curl` gets a 302 to `vercel.com/sso-api`).
- In a fresh git worktree, run `pnpm install` and `uv sync --all-packages --locked` first;
  without the sync, pytest fails at collection. Never run either in someone else's checkout.
- If `cargo` is not on PATH in an agent shell, prepend `$(ls -d ~/.rustup/toolchains/stable-*)/bin`.
- `supabase/tests/run.sh` needs a local Postgres (`psql`). Without one, rely on CI's
  `database` job and say so.
- Web app specifics: `apps/web/AGENTS.md`, below the generated Next.js block.
