# 0004: Rust where it measurably earns its place

**Context.** Rust is a goal of the lab, but not by rewriting working code for its own sake.

**Decision.** New work starts in the language its ecosystem lives in (Python for
robotics and ML, TypeScript for the site). A component moves to Rust when at least one holds:

1. Measured performance limit (log validation and replay on large runs, browser replay via WASM)
2. Reliability or latency that matters physically (the safety gate and agent once they guard the arms)
3. Deployment as a single static binary on edge hardware (Jetson, Pi)
4. A profiled hot spot inside Python (via PyO3)

Every port ships with a before/after benchmark written up as a lab log entry, and
must pass the same shared fixtures as the version it replaces.

**Roadmap.** `lab-events` + `labctl` (done, v0) -> WASM replay viewer (done
2026-11-10; measured 2.6x slower to load and 1.8x slower to scrub than TypeScript, so
TypeScript stays the viewer default; see the log entry "Rust in the browser") -> a typed,
borrowing parser in `lab-events` (the measured bottleneck) -> Rust safety gate as a
library the Python agent calls -> single-binary edge agent.

**Consequences.** Rust lands where it is visible and defensible, and each port
becomes portfolio content with numbers.
