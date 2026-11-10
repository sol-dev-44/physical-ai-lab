use std::collections::HashSet;

use crate::event::{Kind, parse_event};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LogIssue {
    /// 1-based line number; 0 for whole-log issues.
    pub line: usize,
    pub message: String,
}

/// Same rules as `packages/schema/src/log.ts` and `lab_agent.log`.
pub fn validate_log<'a>(lines: impl IntoIterator<Item = &'a str>) -> Vec<LogIssue> {
    let mut issues = Vec::new();
    let mut seen: HashSet<String> = HashSet::new();
    let mut run_id: Option<String> = None;
    let mut ended = false;
    let mut expected_seq: u64 = 0;
    let mut push = |line: usize, message: String| issues.push(LogIssue { line, message });

    for (i, raw) in lines.into_iter().enumerate() {
        let line = i + 1;
        if raw.trim().is_empty() {
            continue;
        }
        let value: serde_json::Value = match serde_json::from_str(raw) {
            Ok(v) => v,
            Err(_) => {
                push(line, "not valid JSON".into());
                continue;
            }
        };
        let e = match parse_event(&value) {
            Ok(e) => e,
            Err(err) => {
                push(line, err.to_string());
                continue;
            }
        };
        if expected_seq == 0 && e.kind != Kind::RunStarted {
            push(line, "first event must be run.started".into());
        }
        if ended {
            push(line, "event after run.ended".into());
        }
        let rid = run_id.get_or_insert_with(|| e.run_id.clone());
        if &e.run_id != rid {
            push(line, format!("run_id {} != {rid}", e.run_id));
        }
        if e.seq != expected_seq {
            push(line, format!("seq {}, expected {expected_seq}", e.seq));
        }
        if seen.contains(&e.event_id) {
            push(line, format!("duplicate event_id {}", e.event_id));
        }
        if let Some(p) = &e.parent_id
            && !seen.contains(p)
        {
            push(line, format!("parent_id {p} not found earlier in log"));
        }
        seen.insert(e.event_id.clone());
        expected_seq = e.seq + 1;
        ended |= e.kind == Kind::RunEnded;
    }
    if seen.is_empty() {
        push(0, "log is empty".into());
    }
    issues
}
