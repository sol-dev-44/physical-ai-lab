# Lab

A physical AI lab, documented from day one. One event format, many stacks:
experiments write append-only event logs, and everything else (replay, evals,
the site) reads only those logs.

Start with [docs/architecture.md](docs/architecture.md) and the
[decision records](docs/adr/README.md).

## Layout

```
apps/web/            Next.js 16: public site + gated /admin
packages/schema/     the event contract (TypeScript source of truth, fixtures)
services/lab-agent/  Python: tool registry, safety gate, devices, sync, queue worker
crates/              Rust: lab-events (contract mirror), labctl (log tooling)
experiments/         one folder per experiment, any language
content/             MDX write-ups: experiments, log, builds
supabase/            migrations + RLS tests
docs/                architecture + ADRs
scripts/             cross-language checks
```

## Setup

Needs Node 22+, pnpm 10, uv, Rust stable.

```bash
pnpm install
uv sync --all-packages            # add --extra hardware in experiments when using real devices
cargo build

pnpm dev                          # site at http://localhost:3000 (works without Supabase)
cp apps/web/.env.example apps/web/.env.local
cp services/lab-agent/.env.example services/lab-agent/.env
```

Supabase setup: [supabase/README.md](supabase/README.md).

## Checks

```bash
pnpm check                        # TS: lint, typecheck, tests (incl. contract), build
uv run ruff check . && uv run pytest
cargo clippy --all-targets -- -D warnings && cargo test
supabase/tests/run.sh             # needs a local Postgres
scripts/crosscheck.sh             # Python writes runs, Rust validates, summaries must match
```

CI runs all of these on every push.

## First experiment

[experiments/exp000-ir-bridge](experiments/exp000-ir-bridge/README.md)
