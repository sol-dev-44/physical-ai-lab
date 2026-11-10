"""Runner: the one execution path. request -> safety.checked -> sent | failed.

Every caller (CLI session, admin queue, LLM, replay, evals) uses this, so the
log has the same shape regardless of who asked.
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .events import Actor, Event
from .log import EventLog
from .registry import Registry
from .safety import Request, SafetyGate


@dataclass
class CommandResult:
    requested: Event
    checked: Event
    outcome: Event | None  # command.sent or command.failed; None when denied

    @property
    def allowed(self) -> bool:
        return self.outcome is not None

    @property
    def ok(self) -> bool:
        return self.outcome is not None and self.outcome.type == "command.sent"

    @property
    def last(self) -> Event:
        return self.outcome or self.checked


def git_sha() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=2
        )
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


class Runner:
    def __init__(
        self,
        registry: Registry,
        log: EventLog,
        gate: SafetyGate | None = None,
        *,
        dry_run: bool = False,
    ) -> None:
        self.registry = registry
        self.log = log
        self.gate = gate or SafetyGate(registry)
        #: Null test: run every rule and log every step, but never call the handler.
        self.dry_run = dry_run

    def start(self, experiment_id: str, *, forked_from: str | None = None, **extra: Any) -> Event:
        payload: dict[str, Any] = {"experiment_id": experiment_id, **extra}
        if sha := git_sha():
            payload["git_sha"] = sha
        if forked_from:
            payload["forked_from"] = forked_from
        if self.dry_run:
            payload["null_test"] = True
        return self.log.append("run.started", "system", payload)

    def end(self, status: str = "completed") -> Event:
        return self.log.append("run.ended", "system", {"status": status})

    def request(
        self,
        tool_name: str,
        args: dict[str, Any] | None = None,
        *,
        actor: Actor = "cli",
        confirmed: bool = False,
        automated: bool = False,
        remote: bool = False,
    ) -> CommandResult:
        args = args or {}
        tool = self.registry.get(tool_name)
        device = tool.device if tool else None
        common = {"tool": tool_name, "args": args, "device": device}

        requested = self.log.append("command.requested", actor, {}, **common)
        d = self.gate.check(
            Request(tool_name, args, actor, confirmed=confirmed, automated=automated, remote=remote)
        )
        checked = self.log.append(
            "safety.checked",
            "system",
            {
                "decision": "allow" if d.allow else "deny",
                "rule": d.rule,
                **({"reason": d.reason} if d.reason else {}),
            },
            parent_id=requested.event_id,
            **common,
        )
        if not d.allow or tool is None or d.args is None:
            return CommandResult(requested, checked, None)

        t0 = time.perf_counter()
        try:
            extra = {} if self.dry_run else (tool.handler(d.args) or {})
        except Exception as e:  # noqa: BLE001 - any device error is logged, never raised
            failed = self.log.append(
                "command.failed",
                "system",
                {"error": f"{type(e).__name__}: {e}"},
                parent_id=checked.event_id,
                **common,
            )
            return CommandResult(requested, checked, failed)
        self.gate.record_sent(tool_name)
        sent = self.log.append(
            "command.sent",
            "system",
            {
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2),
                **({"dry_run": True} if self.dry_run else {}),
                **extra,
            },
            parent_id=checked.event_id,
            **common,
        )
        return CommandResult(requested, checked, sent)

    def observe(
        self,
        result: CommandResult | Event,
        success: bool,
        *,
        method: str = "human",
        note: str | None = None,
        actor: Actor = "human",
    ) -> Event:
        parent = result.last if isinstance(result, CommandResult) else result
        tool = getattr(parent, "tool", None)
        payload: dict[str, Any] = {"success": success, "method": method}
        if note:
            payload["note"] = note
        return self.log.append(
            "outcome.observed", actor, payload, parent_id=parent.event_id, tool=tool
        )

    def note(self, text: str, actor: Actor = "human") -> Event:
        return self.log.append("note", actor, {"text": text})


def run_path(root: Path, experiment_id: str, run_id: str) -> Path:
    return root / experiment_id / f"{run_id}.jsonl"
