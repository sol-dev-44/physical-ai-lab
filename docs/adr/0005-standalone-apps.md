# 0005: When an experiment gets its own app

**Context.** The main site must not limit what experiments can do.

**Decision.** An experiment gets a standalone app (in `apps/<name>`, or its own repo) when it needs:

- a different runtime (GPU, WebGPU-heavy, native, long-running processes), or
- dependencies that would bloat or destabilize the main site, or
- its own deploy cadence or scaling.

A standalone app must write events in the contract format, deploy on a subdomain,
and be listed on the main site through its experiment write-up (`app_url`). Shared
UI moves to `packages/ui` only once two apps need it.

**Consequences.** The main site stays a stable, fast publisher; experiments stay free.
