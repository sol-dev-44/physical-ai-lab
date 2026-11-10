"""Append-only JSONL event log, one file per run.

Layout on the lab machine (never committed, see .gitignore):
    events/<experiment_id>/<run_id>.jsonl
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .events import (
    SCHEMA_VERSION,
    Actor,
    Event,
    RunEnded,
    new_ulid,
    now_ts,
    parse_event,
    to_json,
)


@dataclass(frozen=True)
class LogIssue:
    line: int
    message: str


def validate_log(lines: Iterable[str]) -> list[LogIssue]:
    """Same rules as packages/schema/src/log.ts and labctl. See fixtures/logs."""
    issues: list[LogIssue] = []
    seen: set[str] = set()
    run_id: str | None = None
    ended = False
    expected_seq = 0

    for i, raw in enumerate(lines, start=1):
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            issues.append(LogIssue(i, "not valid JSON"))
            continue
        try:
            e = parse_event(data)
        except ValidationError as err:
            issues.append(
                LogIssue(
                    i,
                    "; ".join(f"{'.'.join(map(str, x['loc']))}: {x['msg']}" for x in err.errors()),
                )
            )
            continue
        if expected_seq == 0 and e.type != "run.started":
            issues.append(LogIssue(i, "first event must be run.started"))
        if ended:
            issues.append(LogIssue(i, "event after run.ended"))
        run_id = run_id or e.run_id
        if e.run_id != run_id:
            issues.append(LogIssue(i, f"run_id {e.run_id} != {run_id}"))
        if e.seq != expected_seq:
            issues.append(LogIssue(i, f"seq {e.seq}, expected {expected_seq}"))
        if e.event_id in seen:
            issues.append(LogIssue(i, f"duplicate event_id {e.event_id}"))
        if e.parent_id and e.parent_id not in seen:
            issues.append(LogIssue(i, f"parent_id {e.parent_id} not found earlier in log"))
        seen.add(e.event_id)
        expected_seq = e.seq + 1
        ended = ended or isinstance(e, RunEnded)

    if not seen:
        issues.append(LogIssue(0, "log is empty"))
    return issues


def read_log(path: Path) -> list[Event]:
    """Read and validate a whole log. Raises ValueError listing every issue."""
    lines = path.read_text().splitlines()
    issues = validate_log(lines)
    if issues:
        raise ValueError(f"{path}: " + "; ".join(f"line {x.line}: {x.message}" for x in issues))
    return [parse_event(line) for line in lines if line.strip()]


class EventLog:
    """Writer for one run. Assigns event_id, seq and ts; validates before writing;
    flushes and fsyncs every line so a crash loses at most the event in flight."""

    def __init__(self, path: Path, run_id: str) -> None:
        self.path = path
        self.run_id = run_id
        self.seq = 0
        self.closed = False
        if path.exists() and path.stat().st_size > 0:
            existing = read_log(path)  # resume: refuses to append to a corrupt log
            self.seq = existing[-1].seq + 1
            self.closed = isinstance(existing[-1], RunEnded)
        path.parent.mkdir(parents=True, exist_ok=True)

    def append(
        self, type: str, actor: Actor, payload: dict[str, Any] | None = None, **fields: Any
    ) -> Event:
        if self.closed:
            raise RuntimeError(f"run {self.run_id} has ended; start a new run")
        data = {
            "v": SCHEMA_VERSION,
            "event_id": new_ulid(),
            "run_id": self.run_id,
            "seq": self.seq,
            "ts": now_ts(),
            "actor": actor,
            "type": type,
            "payload": payload or {},
            **{k: v for k, v in fields.items() if v is not None},
        }
        event = parse_event(data)  # never write an invalid line
        with self.path.open("a", encoding="utf-8") as f:
            f.write(to_json(event) + "\n")
            f.flush()
            os.fsync(f.fileno())
        self.seq += 1
        self.closed = isinstance(event, RunEnded)
        return event
