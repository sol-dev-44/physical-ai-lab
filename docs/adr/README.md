# Architecture decision records

One page per decision that would be expensive to reverse. Format: context,
decision, consequences. Supersede instead of editing: add a new ADR and mark the
old one `Superseded by 00NN`.

| # | Decision | Status |
|---|---|---|
| [0001](0001-polyglot-monorepo.md) | One polyglot monorepo: pnpm/Turborepo, uv, Cargo | Accepted |
| [0002](0002-event-contract.md) | The event contract is the spine | Accepted |
| [0003](0003-web-never-touches-hardware.md) | The website never touches hardware | Accepted |
| [0004](0004-rust-policy.md) | Rust where it measurably earns its place | Accepted |
| [0005](0005-standalone-apps.md) | When an experiment gets its own app | Accepted |
| [0006](0006-content-and-data.md) | Write-ups in git, run data in Supabase | Accepted |
| [0007](0007-child-privacy.md) | No identifiable child data, ever | Accepted |
| [0008](0008-device-played-holds.md) | Timed actions are played by the device, from one frame | Accepted |
| [0009](0009-arm-bench-camera.md) | Arm bench camera frames may show adults, never children | Proposed |
