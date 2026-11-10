//! The Rust mirror must agree with the zod source on every shared fixture.

use std::fs;
use std::path::{Path, PathBuf};

use lab_events::{parse_event, summarize, validate_log};
use serde_json::Value;

fn fixtures() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../packages/schema/fixtures")
}

fn files(sub: &str) -> Vec<PathBuf> {
    let mut v: Vec<_> = fs::read_dir(fixtures().join(sub))
        .unwrap()
        .map(|e| e.unwrap().path())
        .filter(|p| !p.file_name().unwrap().to_string_lossy().starts_with('.'))
        .collect();
    v.sort();
    assert!(!v.is_empty(), "no fixtures in {sub}");
    v
}

fn json(p: &Path) -> Value {
    serde_json::from_str(&fs::read_to_string(p).unwrap()).unwrap()
}

#[test]
fn accepts_valid_events() {
    for p in files("valid") {
        if let Err(e) = parse_event(&json(&p)) {
            panic!("{}: {e}", p.display());
        }
    }
}

#[test]
fn rejects_invalid_events() {
    for p in files("invalid") {
        assert!(
            parse_event(&json(&p)).is_err(),
            "{} should be rejected",
            p.display()
        );
    }
}

#[test]
fn accepts_valid_logs() {
    for p in files("logs/valid") {
        let text = fs::read_to_string(&p).unwrap();
        assert_eq!(validate_log(text.lines()), vec![], "{}", p.display());
    }
}

#[test]
fn rejects_invalid_logs() {
    for p in files("logs/invalid") {
        let text = fs::read_to_string(&p).unwrap();
        assert!(
            !validate_log(text.lines()).is_empty(),
            "{} should be rejected",
            p.display()
        );
    }
}

/// JSON numbers compare by value: TypeScript writes 1, serde writes 1.0.
fn normalize(v: Value) -> Value {
    match v {
        Value::Number(n) => serde_json::json!(n.as_f64().unwrap()),
        Value::Array(a) => Value::Array(a.into_iter().map(normalize).collect()),
        Value::Object(o) => Value::Object(o.into_iter().map(|(k, v)| (k, normalize(v))).collect()),
        other => other,
    }
}

#[test]
fn summaries_match_typescript() {
    for p in files("summaries") {
        let name = p.file_stem().unwrap().to_string_lossy();
        let log = fs::read_to_string(fixtures().join(format!("logs/valid/{name}.jsonl"))).unwrap();
        let events: Vec<_> = log
            .lines()
            .filter(|l| !l.trim().is_empty())
            .map(|l| parse_event(&serde_json::from_str(l).unwrap()).unwrap())
            .collect();
        let got = normalize(serde_json::to_value(summarize(&events)).unwrap());
        assert_eq!(got, normalize(json(&p)), "{}", p.display());
    }
}
