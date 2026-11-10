# Contract fixtures

Shared by every language that reads or writes lab events. Each implementation
(TypeScript `@lab/schema`, Python `lab_agent`, Rust `labctl`) must:

- accept every file in `valid/` and reject every file in `invalid/` (single events)
- accept every log in `logs/valid/` and reject every log in `logs/invalid/`

When you add a rule, add a fixture that breaks it. When a bug slips through,
add the fixture first, then fix every implementation.
