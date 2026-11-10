//! `lab-events` for the browser. A thin wasm-bindgen layer: no contract logic
//! lives here, so the viewer validates and folds logs with exactly the code
//! `labctl` and the contract tests use.
//!
//! Results cross the boundary as JSON strings. One `JSON.parse` on the JS side
//! is cheaper and simpler than marshalling nested objects field by field.

use lab_events::{Event, LogIssue, parse_event, parse_log, summarize};
use serde::Serialize;
use wasm_bindgen::prelude::wasm_bindgen;

#[derive(Serialize)]
struct Issue<'a> {
    line: usize,
    message: &'a str,
}

fn issues_json(issues: &[LogIssue]) -> String {
    let out: Vec<Issue<'_>> = issues
        .iter()
        .map(|i| Issue {
            line: i.line,
            message: &i.message,
        })
        .collect();
    serde_json::to_string(&out).unwrap_or_else(|_| "[]".into())
}

/// A parsed log, held in WASM memory so the viewer can scrub without
/// re-parsing. Lines that are not valid events are reported in `issues` and
/// left out of `len`, `event` and `summary_at`.
#[wasm_bindgen]
pub struct Run {
    raw: Vec<String>,
    events: Vec<Event>,
    issues: Vec<LogIssue>,
}

#[wasm_bindgen]
impl Run {
    /// Parse and validate a JSONL log.
    #[wasm_bindgen(constructor)]
    #[must_use]
    pub fn new(text: &str) -> Run {
        let lines: Vec<&str> = text.lines().collect();
        let parsed = parse_log(lines.iter().copied());
        let (raw, events) = parsed
            .events
            .into_iter()
            .map(|(line, e)| (lines[line - 1].to_owned(), e))
            .unzip();
        Run {
            raw,
            events,
            issues: parsed.issues,
        }
    }

    /// Number of valid events.
    #[must_use]
    pub fn len(&self) -> usize {
        self.events.len()
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.events.is_empty()
    }

    /// `true` when the whole log passes every contract and log rule.
    #[must_use]
    pub fn valid(&self) -> bool {
        self.issues.is_empty()
    }

    /// Log issues as JSON: `[{ "line": 3, "message": "..." }]`.
    #[must_use]
    pub fn issues(&self) -> String {
        issues_json(&self.issues)
    }

    /// The i-th valid event, as its original JSON line.
    #[must_use]
    pub fn event(&self, i: usize) -> Option<String> {
        self.raw.get(i).cloned()
    }

    /// Summary of the first `n` valid events, as JSON. `n` past the end means all.
    #[must_use]
    pub fn summary_at(&self, n: usize) -> String {
        let n = n.min(self.events.len());
        serde_json::to_string(&summarize(&self.events[..n])).unwrap_or_else(|_| "null".into())
    }
}

/// Check one event against the contract. `None` if valid, else the reason.
#[wasm_bindgen]
#[must_use]
pub fn check_event(json: &str) -> Option<String> {
    match serde_json::from_str::<serde_json::Value>(json) {
        Err(_) => Some("not valid JSON".into()),
        Ok(v) => parse_event(&v).err().map(|e| e.to_string()),
    }
}

/// One-shot check for the benchmark: validate and fold a whole log.
/// Returns `{ "issues": [...], "summary": {...} }`.
#[wasm_bindgen]
#[must_use]
pub fn analyze(text: &str) -> String {
    let run = Run::new(text);
    format!(
        r#"{{"issues":{},"summary":{}}}"#,
        run.issues(),
        run.summary_at(usize::MAX)
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::Value;

    const FULL: &str = include_str!("../../../packages/schema/fixtures/logs/valid/full_run.jsonl");
    const FULL_SUMMARY: &str =
        include_str!("../../../packages/schema/fixtures/summaries/full_run.json");
    const SEQ_GAP: &str =
        include_str!("../../../packages/schema/fixtures/logs/invalid/seq_gap.jsonl");

    /// JSON equality with numbers compared as f64 (fixtures write `1`, Rust writes `1.0`).
    fn norm(v: Value) -> Value {
        match v {
            Value::Number(n) => serde_json::json!(n.as_f64()),
            Value::Array(a) => Value::Array(a.into_iter().map(norm).collect()),
            Value::Object(o) => Value::Object(o.into_iter().map(|(k, v)| (k, norm(v))).collect()),
            v => v,
        }
    }

    fn parse(s: &str) -> Value {
        norm(serde_json::from_str(s).unwrap())
    }

    #[test]
    fn full_summary_matches_shared_fixture() {
        let run = Run::new(FULL);
        assert!(run.valid(), "{}", run.issues());
        assert_eq!(parse(&run.summary_at(usize::MAX)), parse(FULL_SUMMARY));
    }

    #[test]
    fn prefix_summary_folds_only_first_n_events() {
        let run = Run::new(FULL);
        for n in 0..=run.len() {
            let want = serde_json::to_string(&summarize(&run.events[..n])).unwrap();
            assert_eq!(run.summary_at(n), want);
        }
    }

    #[test]
    fn event_returns_original_line() {
        let run = Run::new(FULL);
        assert_eq!(run.event(0).as_deref(), FULL.lines().next());
        assert_eq!(run.event(run.len()), None);
    }

    #[test]
    fn invalid_log_reports_issues_but_keeps_events() {
        let run = Run::new(SEQ_GAP);
        assert!(!run.valid());
        assert!(run.issues().contains("expected"));
        assert!(!run.is_empty());
    }

    #[test]
    fn check_event_reports_reason() {
        assert_eq!(check_event(FULL.lines().next().unwrap()), None);
        assert_eq!(check_event("{"), Some("not valid JSON".into()));
        assert_eq!(check_event("{}"), Some("type: required".into()));
    }

    #[test]
    fn empty_log() {
        let run = Run::new("");
        assert!(run.is_empty());
        assert!(run.issues().contains("log is empty"));
    }

    #[test]
    fn analyze_wraps_issues_and_summary() {
        let v = parse(&analyze(FULL));
        assert_eq!(v["issues"], serde_json::json!([]));
        assert_eq!(v["summary"], parse(FULL_SUMMARY));
    }
}
