use std::sync::LazyLock;

use regex::Regex;
use serde_json::{Map, Value};

static ULID: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^[0-9A-HJKMNP-TV-Z]{26}$").unwrap());
static RUN_ID: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[a-z0-9][a-z0-9-]{2,79}$").unwrap());
static EXPERIMENT_ID: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^exp[0-9]{3}(-[a-z0-9]+)*$").unwrap());
static TOOL: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$").unwrap());
static TS: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,6})?Z$").unwrap()
});

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Kind {
    RunStarted,
    RunEnded,
    CommandRequested,
    SafetyChecked,
    CommandSent,
    CommandFailed,
    OutcomeObserved,
    Note,
}

impl Kind {
    fn parse(s: &str) -> Option<Self> {
        Some(match s {
            "run.started" => Self::RunStarted,
            "run.ended" => Self::RunEnded,
            "command.requested" => Self::CommandRequested,
            "safety.checked" => Self::SafetyChecked,
            "command.sent" => Self::CommandSent,
            "command.failed" => Self::CommandFailed,
            "outcome.observed" => Self::OutcomeObserved,
            "note" => Self::Note,
            _ => return None,
        })
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Self::RunStarted => "run.started",
            Self::RunEnded => "run.ended",
            Self::CommandRequested => "command.requested",
            Self::SafetyChecked => "safety.checked",
            Self::CommandSent => "command.sent",
            Self::CommandFailed => "command.failed",
            Self::OutcomeObserved => "outcome.observed",
            Self::Note => "note",
        }
    }

    /// Whether `tool` + `args` are required (a tool call), optional-tool, or absent.
    fn tool_fields(self) -> ToolFields {
        match self {
            Self::CommandRequested
            | Self::SafetyChecked
            | Self::CommandSent
            | Self::CommandFailed => ToolFields::Required,
            Self::OutcomeObserved => ToolFields::ToolOptional,
            _ => ToolFields::None,
        }
    }
}

enum ToolFields {
    Required,
    ToolOptional,
    None,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Actor {
    Human,
    Cli,
    Agent,
    Llm,
    Replay,
    System,
}

impl Actor {
    fn parse(s: &str) -> Option<Self> {
        Some(match s {
            "human" => Self::Human,
            "cli" => Self::Cli,
            "agent" => Self::Agent,
            "llm" => Self::Llm,
            "replay" => Self::Replay,
            "system" => Self::System,
            _ => return None,
        })
    }
}

/// A validated event. `payload` keeps every key, including extras.
#[derive(Debug, Clone, PartialEq)]
pub struct Event {
    pub event_id: String,
    pub run_id: String,
    pub seq: u64,
    pub ts: String,
    pub actor: Actor,
    pub kind: Kind,
    pub parent_id: Option<String>,
    pub device: Option<String>,
    pub tool: Option<String>,
    pub args: Option<Map<String, Value>>,
    pub payload: Map<String, Value>,
}

impl Event {
    pub fn payload_str(&self, key: &str) -> Option<&str> {
        self.payload.get(key).and_then(Value::as_str)
    }

    pub fn payload_bool(&self, key: &str) -> Option<bool> {
        self.payload.get(key).and_then(Value::as_bool)
    }
}

#[derive(Debug, thiserror::Error, PartialEq)]
pub enum EventError {
    #[error("not an object")]
    NotObject,
    #[error("{0}: required")]
    Missing(&'static str),
    #[error("{0}: invalid")]
    Invalid(String),
    #[error("{0}: unknown key")]
    Unknown(String),
}

fn invalid(k: impl Into<String>) -> EventError {
    EventError::Invalid(k.into())
}

/// Optional field: absent is fine, null is not.
fn opt<'a>(m: &'a Map<String, Value>, k: &str) -> Result<Option<&'a Value>, EventError> {
    match m.get(k) {
        None => Ok(None),
        Some(Value::Null) => Err(invalid(k)),
        Some(v) => Ok(Some(v)),
    }
}

fn req<'a>(m: &'a Map<String, Value>, k: &'static str) -> Result<&'a Value, EventError> {
    match m.get(k) {
        None => Err(EventError::Missing(k)),
        Some(v) => Ok(v),
    }
}

fn str_matching(v: &Value, re: &Regex, k: &str) -> Result<String, EventError> {
    match v.as_str() {
        Some(s) if re.is_match(s) => Ok(s.to_owned()),
        _ => Err(invalid(k)),
    }
}

fn opt_str_matching(
    m: &Map<String, Value>,
    k: &str,
    re: &Regex,
) -> Result<Option<String>, EventError> {
    opt(m, k)?.map(|v| str_matching(v, re, k)).transpose()
}

fn opt_string(
    m: &Map<String, Value>,
    k: &str,
    min_len: usize,
) -> Result<Option<String>, EventError> {
    match opt(m, k)? {
        None => Ok(None),
        Some(Value::String(s)) if s.chars().count() >= min_len => Ok(Some(s.clone())),
        Some(_) => Err(invalid(k)),
    }
}

fn opt_bool(m: &Map<String, Value>, k: &str) -> Result<(), EventError> {
    match opt(m, k)? {
        None | Some(Value::Bool(_)) => Ok(()),
        Some(_) => Err(invalid(k)),
    }
}

fn one_of(m: &Map<String, Value>, k: &'static str, allowed: &[&str]) -> Result<(), EventError> {
    match req(m, k)?.as_str() {
        Some(s) if allowed.contains(&s) => Ok(()),
        _ => Err(invalid(k)),
    }
}

/// Per-type payload checks. Payloads are loose: extra keys are allowed.
fn check_payload(kind: Kind, p: &Map<String, Value>) -> Result<(), EventError> {
    match kind {
        Kind::RunStarted => {
            str_matching(
                req(p, "experiment_id")?,
                &EXPERIMENT_ID,
                "payload.experiment_id",
            )?;
            opt_string(p, "git_sha", 0)?;
            opt_str_matching(p, "forked_from", &RUN_ID)?;
            opt_bool(p, "null_test")?;
        }
        Kind::RunEnded => one_of(p, "status", &["completed", "aborted", "failed"])?,
        Kind::CommandRequested => {}
        Kind::SafetyChecked => {
            one_of(p, "decision", &["allow", "deny"])?;
            opt_string(p, "rule", 0)?;
            opt_string(p, "reason", 0)?;
        }
        Kind::CommandSent => match opt(p, "latency_ms")? {
            None => {}
            Some(v) if v.as_f64().is_some_and(|x| x >= 0.0) => {}
            Some(_) => return Err(invalid("payload.latency_ms")),
        },
        Kind::CommandFailed => {
            if opt_string(p, "error", 1)?.is_none() {
                return Err(EventError::Missing("payload.error"));
            }
        }
        Kind::OutcomeObserved => {
            if !req(p, "success")?.is_boolean() {
                return Err(invalid("payload.success"));
            }
            one_of(p, "method", &["human", "camera", "sensor", "device"])?;
            opt_string(p, "note", 0)?;
        }
        Kind::Note => {
            if opt_string(p, "text", 1)?.is_none() {
                return Err(EventError::Missing("payload.text"));
            }
        }
    }
    Ok(())
}

const ENVELOPE: &[&str] = &[
    "v",
    "event_id",
    "run_id",
    "seq",
    "ts",
    "actor",
    "type",
    "parent_id",
    "device",
    "payload",
];

pub fn parse_event(value: &Value) -> Result<Event, EventError> {
    let m = value.as_object().ok_or(EventError::NotObject)?;

    let kind_str = req(m, "type")?.as_str().ok_or_else(|| invalid("type"))?;
    let kind = Kind::parse(kind_str).ok_or_else(|| invalid("type"))?;
    let tool_fields = kind.tool_fields();

    for key in m.keys() {
        let allowed = ENVELOPE.contains(&key.as_str())
            || match tool_fields {
                ToolFields::Required => key == "tool" || key == "args",
                ToolFields::ToolOptional => key == "tool",
                ToolFields::None => false,
            };
        if !allowed {
            return Err(EventError::Unknown(key.clone()));
        }
    }

    if req(m, "v")?.as_u64() != Some(0) {
        return Err(invalid("v"));
    }
    let event_id = str_matching(req(m, "event_id")?, &ULID, "event_id")?;
    let run_id = str_matching(req(m, "run_id")?, &RUN_ID, "run_id")?;
    let seq = req(m, "seq")?.as_u64().ok_or_else(|| invalid("seq"))?;
    let ts = str_matching(req(m, "ts")?, &TS, "ts")?;
    let actor = req(m, "actor")?
        .as_str()
        .and_then(Actor::parse)
        .ok_or_else(|| invalid("actor"))?;
    let parent_id = opt_str_matching(m, "parent_id", &ULID)?;
    let device = opt_string(m, "device", 1)?;

    let (tool, args) = match tool_fields {
        ToolFields::Required => {
            let tool = str_matching(req(m, "tool")?, &TOOL, "tool")?;
            let args = req(m, "args")?
                .as_object()
                .cloned()
                .ok_or_else(|| invalid("args"))?;
            (Some(tool), Some(args))
        }
        ToolFields::ToolOptional => (opt_str_matching(m, "tool", &TOOL)?, None),
        ToolFields::None => (None, None),
    };

    let payload = req(m, "payload")?
        .as_object()
        .cloned()
        .ok_or_else(|| invalid("payload"))?;
    check_payload(kind, &payload)?;

    Ok(Event {
        event_id,
        run_id,
        seq,
        ts,
        actor,
        kind,
        parent_id,
        device,
        tool,
        args,
        payload,
    })
}
