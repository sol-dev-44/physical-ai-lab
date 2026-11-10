# Rust crates

| Crate | What | Why Rust |
|---|---|---|
| `lab-events` | Contract mirror: parse, validate logs, fold summaries | Shared core for every Rust tool; later compiled to WASM for the browser replay viewer |
| `labctl` | CLI over logs: `validate`, `summary`, `stats` | Fast checks over large arm-run logs; first step toward a Rust safety gate |
| `lab-events-wasm` | `lab-events` for the browser replay viewer (`/harness/replay`), via `packages/lab-events-wasm` | Measured 2-3x *slower* than the TypeScript engine in V8, so it is opt-in. See `content/log/2026-11-10-wasm-replay-viewer.mdx` |

Rules (from `docs/adr/0004-rust-policy.md`): a Rust port ships with a benchmark
against the Python or TypeScript version it replaces, written up as its own lab
log entry, and must pass the same shared fixtures.

```bash
cargo test                       # contract tests against packages/schema/fixtures
cargo run -p labctl -- validate events/exp000-ir-bridge/*.jsonl
cargo run -p labctl -- stats events

# after changing lab-events or lab-events-wasm (needs the wasm32 target and
# wasm-bindgen-cli at the Cargo.lock version; CI fails until you do):
pnpm --filter @lab/events-wasm wasm
pnpm --filter @lab/events-wasm bench   # TS vs WASM
```
