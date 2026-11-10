"""Publish local logs to Supabase. Idempotent: run it as often as you like.

- Every log is validated first; an invalid log is reported and skipped, never uploaded.
- runs rows are upserted (the `published` flag is never touched; you set that in /admin).
- events are inserted with ON CONFLICT DO NOTHING, which the append-only trigger allows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

from .events import Event
from .log import read_log
from .summary import summarize_run
from .supabase import Supabase


@dataclass
class SyncReport:
    synced: list[str] = field(default_factory=list)
    skipped: dict[str, str] = field(default_factory=dict)


def run_row(events: list[Event]) -> dict[str, Any]:
    s = summarize_run(events)
    start = events[0]
    return {
        "run_id": start.run_id,
        "experiment_id": s["experiment_id"],
        "status": s["status"],
        "null_test": s["null_test"],
        "forked_from": getattr(start.payload, "forked_from", None),
        "git_sha": getattr(start.payload, "git_sha", None),
        "started_at": s["started_at"],
        "ended_at": s["ended_at"],
        "event_count": len(events),
    }


def event_row(e: Event) -> dict[str, Any]:
    return {
        "event_id": e.event_id,
        "run_id": e.run_id,
        "seq": e.seq,
        "ts": e.ts,
        "type": e.type,
        "actor": e.actor,
        "tool": getattr(e, "tool", None),
        "device": e.device,
        "parent_id": e.parent_id,
        "raw": e.model_dump(mode="json", exclude_none=True),
    }


def sync(
    events_dir: Path, db: Supabase, *, site_url: str | None = None, secret: str | None = None
) -> SyncReport:
    report = SyncReport()
    logs: list[list[Event]] = []
    for path in sorted(events_dir.rglob("*.jsonl")):
        try:
            logs.append(read_log(path))
        except ValueError as e:
            report.skipped[str(path)] = str(e)
    # Sources before forks, so forked_from foreign keys resolve.
    logs.sort(key=lambda evs: evs[0].ts)
    for events in logs:
        db.upsert("runs", [run_row(events)], on_conflict="run_id")
        for i in range(0, len(events), 500):
            db.upsert(
                "events",
                [event_row(e) for e in events[i : i + 500]],
                on_conflict="event_id",
                ignore=True,
            )
        report.synced.append(events[0].run_id)

    if report.synced and site_url and secret:
        try:
            httpx.post(
                f"{site_url.rstrip('/')}/api/revalidate",
                json={"run_ids": report.synced[:100]},
                headers={"Authorization": f"Bearer {secret}"},
                timeout=10,
            ).raise_for_status()
        except httpx.HTTPError as e:
            report.skipped["revalidate"] = str(e)
    return report
