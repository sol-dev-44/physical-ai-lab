# 0001: One polyglot monorepo

**Context.** The lab spans a website (TypeScript), robotics and ML (Python,
LeRobot), and performance-critical tooling (Rust). Splitting repos early means
the contract between them drifts silently.

**Decision.** One repo. Each ecosystem uses its native workspace tool from the root:

- pnpm + Turborepo for `apps/*` and `packages/*`
- uv workspace for Python (`services/*`, Python experiments), members listed explicitly
- Cargo workspace for `crates/*`

CI runs every ecosystem plus a cross-language check on every push.

**Consequences.** One clone, one CI, atomic changes across languages (change the
contract and every implementation in one commit). Cost: three toolchains to keep
installed. A standalone app may still live in its own repo if it needs to (0005).
