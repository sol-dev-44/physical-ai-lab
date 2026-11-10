//! labctl: fast tooling over lab event logs.
//!
//!   labctl validate <log>...      check logs against the contract (exit 1 on any issue)
//!   labctl summary <log>          fold one log into its summary (JSON)
//!   labctl stats <dir>            validate every log under a directory and report throughput

use std::fs;
use std::path::{Path, PathBuf};
use std::process::ExitCode;
use std::time::Instant;

use anyhow::{Context, Result, bail};
use clap::{Parser, Subcommand};
use lab_events::{parse_event, summarize, validate_log};

#[derive(Parser)]
#[command(version, about = "Fast tooling over lab event logs")]
struct Cli {
    #[command(subcommand)]
    cmd: Cmd,
}

#[derive(Subcommand)]
enum Cmd {
    /// Check logs against the event contract
    Validate { logs: Vec<PathBuf> },
    /// Fold a log into its summary
    Summary { log: PathBuf },
    /// Validate every .jsonl under a directory and report throughput
    Stats { dir: PathBuf },
}

fn main() -> ExitCode {
    match run(Cli::parse()) {
        Ok(true) => ExitCode::SUCCESS,
        Ok(false) => ExitCode::FAILURE,
        Err(e) => {
            eprintln!("error: {e:#}");
            ExitCode::from(2)
        }
    }
}

fn run(cli: Cli) -> Result<bool> {
    match cli.cmd {
        Cmd::Validate { logs } => {
            if logs.is_empty() {
                bail!("pass at least one log file");
            }
            let mut ok = true;
            for path in logs {
                let text = read(&path)?;
                let issues = validate_log(text.lines());
                println!(
                    "{} {}",
                    if issues.is_empty() { "ok " } else { "BAD" },
                    path.display()
                );
                for i in &issues {
                    println!("    line {}: {}", i.line, i.message);
                }
                ok &= issues.is_empty();
            }
            Ok(ok)
        }
        Cmd::Summary { log } => {
            let text = read(&log)?;
            let issues = validate_log(text.lines());
            if !issues.is_empty() {
                bail!(
                    "{} is not a valid log ({} issues); run labctl validate",
                    log.display(),
                    issues.len()
                );
            }
            let events = text
                .lines()
                .filter(|l| !l.trim().is_empty())
                .map(|l| parse_event(&serde_json::from_str(l)?).map_err(anyhow::Error::from))
                .collect::<Result<Vec<_>>>()?;
            println!("{}", serde_json::to_string_pretty(&summarize(&events))?);
            Ok(true)
        }
        Cmd::Stats { dir } => {
            let mut files = Vec::new();
            walk(&dir, &mut files)?;
            let start = Instant::now();
            let (mut events, mut bad, mut bytes) = (0usize, 0usize, 0usize);
            for f in &files {
                let text = read(f)?;
                bytes += text.len();
                events += text.lines().filter(|l| !l.trim().is_empty()).count();
                if !validate_log(text.lines()).is_empty() {
                    bad += 1;
                    println!("BAD {}", f.display());
                }
            }
            let secs = start.elapsed().as_secs_f64();
            #[allow(clippy::cast_precision_loss)]
            let rate = if secs > 0.0 {
                events as f64 / secs
            } else {
                0.0
            };
            println!(
                "{} logs, {} invalid, {events} events, {bytes} bytes in {:.1} ms ({rate:.0} events/s)",
                files.len(),
                bad,
                secs * 1000.0
            );
            Ok(bad == 0)
        }
    }
}

fn read(path: &Path) -> Result<String> {
    fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))
}

fn walk(dir: &Path, out: &mut Vec<PathBuf>) -> Result<()> {
    for entry in fs::read_dir(dir).with_context(|| format!("reading {}", dir.display()))? {
        let path = entry?.path();
        if path.is_dir() {
            walk(&path, out)?;
        } else if path.extension().is_some_and(|e| e == "jsonl") {
            out.push(path);
        }
    }
    out.sort();
    Ok(())
}
