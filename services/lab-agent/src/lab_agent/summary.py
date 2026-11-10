"""Fold a run into the numbers the site shows. Must match packages/schema
summarizeRun exactly; tests compare both to fixtures/summaries/*.json."""

from __future__ import annotations

from typing import Any

from .events import Event


def summarize_run(events: list[Event]) -> dict[str, Any]:
    s: dict[str, Any] = {
        "run_id": events[0].run_id if events else "",
        "experiment_id": None,
        "status": "open",
        "null_test": False,
        "started_at": None,
        "ended_at": None,
        "requested": 0,
        "denied": 0,
        "sent": 0,
        "failed": 0,
        "observed": 0,
        "succeeded": 0,
        "success_rate": None,
        "tools": {},
    }

    def tool(name: str) -> dict[str, int]:
        return s["tools"].setdefault(
            name, {"requested": 0, "sent": 0, "succeeded": 0, "observed": 0}
        )

    for e in events:
        match e.type:
            case "run.started":
                s["experiment_id"] = e.payload.experiment_id
                s["null_test"] = bool(e.payload.null_test)
                s["started_at"] = e.ts
            case "run.ended":
                s["status"] = e.payload.status
                s["ended_at"] = e.ts
            case "command.requested":
                s["requested"] += 1
                tool(e.tool)["requested"] += 1
            case "safety.checked":
                if e.payload.decision == "deny":
                    s["denied"] += 1
            case "command.sent":
                s["sent"] += 1
                tool(e.tool)["sent"] += 1
            case "command.failed":
                s["failed"] += 1
            case "outcome.observed":
                s["observed"] += 1
                if e.payload.success:
                    s["succeeded"] += 1
                if e.tool:
                    tool(e.tool)["observed"] += 1
                    if e.payload.success:
                        tool(e.tool)["succeeded"] += 1
    s["success_rate"] = s["succeeded"] / s["observed"] if s["observed"] else None
    return s
