# Rust crates

| Crate | What | Why Rust |
|---|---|---|
| `lab-events` | Contract mirror: parse, validate logs, fold summaries | Shared core for every Rust tool; later compiled to WASM for the browser replay viewer |
| `labctl` | CLI over logs: `validate`, `summary`, `stats` | Fast checks over large arm-run logs; first step toward a Rust safety gate |

Rules (from `docs/adr/0004-rust-policy.md`): a Rust port ships with a benchmark
against the Python or TypeScript version it replaces, written up as its own lab
log entry, and must pass the same shared fixtures.

```bash
cargo test                       # contract tests against packages/schema/fixtures
cargo run -p labctl -- validate events/exp000-ir-bridge/*.jsonl
cargo run -p labctl -- stats events
```
