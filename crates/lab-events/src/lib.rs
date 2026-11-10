//! Rust mirror of the lab event contract (`packages/schema`, version 0).
//!
//! zod in `packages/schema` is the authoring source. This crate must accept and
//! reject exactly what it does; `tests/contract.rs` checks every shared fixture.
//!
//! Parsing goes through `serde_json::Value` with explicit checks instead of
//! derived `Deserialize`, because the contract needs two things serde does not
//! give for free here: unknown top-level keys are rejected, and optional fields
//! may be omitted but never `null`.

mod event;
mod log;
mod summary;

pub use event::{Actor, Event, EventError, Kind, parse_event};
pub use log::{LogIssue, validate_log};
pub use summary::{RunSummary, ToolCounts, summarize};
