"""Replay: re-issue a past run's requests as a new run, through the same gate.

The new run records forked_from=<source run_id>, actor=replay. Replays are
automated, so manual-only tools (the fireplace) are denied by the gate and the
denial is logged. Pass dry_run=True on the Runner for a null-test replay.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import datetime

from .events import Event
from .runner import CommandResult, Runner


def _t(ts: str) -> float:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()


def replay(
    source: list[Event],
    runner: Runner,
    *,
    experiment_id: str | None = None,
    pace: bool = True,
    max_gap_s: float = 10.0,
    sleep: Callable[[float], None] = time.sleep,
) -> list[CommandResult]:
    """With pace=True, keeps the original gaps between requests (each capped at
    max_gap_s), so rate limits and device timing behave as they did live."""
    started = next((e for e in source if e.type == "run.started"), None)
    if started is None:
        raise ValueError("source log has no run.started")
    runner.start(experiment_id or started.payload.experiment_id, forked_from=started.run_id)
    results: list[CommandResult] = []
    prev: float | None = None
    for e in source:
        if e.type != "command.requested":
            continue
        if pace and prev is not None:
            sleep(min(max(_t(e.ts) - prev, 0.0), max_gap_s))
        prev = _t(e.ts)
        results.append(runner.request(e.tool, e.args, actor="replay", automated=True))
    runner.end("completed")
    return results
