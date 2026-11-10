# 0002: The event contract is the spine

**Context.** Experiments will be written in different languages and stacks. The
site, evals, replay and the database must not care which.

**Decision.** Everything that happens in the lab is an event in an append-only
JSONL log, one file per run. The contract lives in `packages/schema`:

- zod (`src/event.ts`) is the authoring source; `schema/event.v0.schema.json` is generated from it and checked for drift in CI.
- Python (`lab_agent.events`) and Rust (`lab-events`) mirror it by hand.
- Shared fixtures (`fixtures/`) define truth: every implementation must accept `valid/`, reject `invalid/`, and produce `summaries/` exactly.

Envelope is strict (unknown keys rejected); payloads are typed per event type but
loose (extra keys allowed). Optional fields may be omitted but never null.
Breaking changes create v1 alongside v0; v0 logs stay valid forever.

**Consequences.** Any new stack can join by writing valid events. Hand-written
mirrors cost a little duplication, paid back by fixtures that catch drift. Code
generation for Python and Rust can replace the mirrors later without changing
the contract.
