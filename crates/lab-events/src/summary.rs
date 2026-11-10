use std::collections::BTreeMap;

use serde::Serialize;

use crate::event::{Event, Kind};

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize)]
pub struct ToolCounts {
    pub requested: u64,
    pub sent: u64,
    pub succeeded: u64,
    pub observed: u64,
}

/// Must match `summarizeRun` (TypeScript) and `summarize_run` (Python) exactly;
/// all three are tested against `fixtures/summaries/*.json`.
#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct RunSummary {
    pub run_id: String,
    pub experiment_id: Option<String>,
    pub status: String,
    pub null_test: bool,
    pub started_at: Option<String>,
    pub ended_at: Option<String>,
    pub requested: u64,
    pub denied: u64,
    pub sent: u64,
    pub failed: u64,
    pub observed: u64,
    pub succeeded: u64,
    pub success_rate: Option<f64>,
    pub tools: BTreeMap<String, ToolCounts>,
}

pub fn summarize(events: &[Event]) -> RunSummary {
    let mut s = RunSummary {
        run_id: events.first().map(|e| e.run_id.clone()).unwrap_or_default(),
        experiment_id: None,
        status: "open".into(),
        null_test: false,
        started_at: None,
        ended_at: None,
        requested: 0,
        denied: 0,
        sent: 0,
        failed: 0,
        observed: 0,
        succeeded: 0,
        success_rate: None,
        tools: BTreeMap::new(),
    };

    for e in events {
        let tool = e.tool.clone();
        match e.kind {
            Kind::RunStarted => {
                s.experiment_id = e.payload_str("experiment_id").map(str::to_owned);
                s.null_test = e.payload_bool("null_test").unwrap_or(false);
                s.started_at = Some(e.ts.clone());
            }
            Kind::RunEnded => {
                s.status = e.payload_str("status").unwrap_or("open").to_owned();
                s.ended_at = Some(e.ts.clone());
            }
            Kind::CommandRequested => {
                s.requested += 1;
                if let Some(t) = tool {
                    s.tools.entry(t).or_default().requested += 1;
                }
            }
            Kind::SafetyChecked => {
                if e.payload_str("decision") == Some("deny") {
                    s.denied += 1;
                }
            }
            Kind::CommandSent => {
                s.sent += 1;
                if let Some(t) = tool {
                    s.tools.entry(t).or_default().sent += 1;
                }
            }
            Kind::CommandFailed => s.failed += 1,
            Kind::OutcomeObserved => {
                let ok = e.payload_bool("success").unwrap_or(false);
                s.observed += 1;
                s.succeeded += u64::from(ok);
                if let Some(t) = tool {
                    let c = s.tools.entry(t).or_default();
                    c.observed += 1;
                    c.succeeded += u64::from(ok);
                }
            }
            Kind::Note => {}
        }
    }
    #[allow(clippy::cast_precision_loss)]
    {
        s.success_rate = (s.observed > 0).then(|| s.succeeded as f64 / s.observed as f64);
    }
    s
}
