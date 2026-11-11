"""Safety gate. Every command passes through check() before any device sees it.

Rules run in order; the first deny wins. Interlocks (world-state rules a tool set
attaches, see interlocks.py) run after the request rules and before the rate limit.
Each decision is logged as a safety.checked event, including the rule that decided
it, so the gate itself can be evaluated from the logs.

This lives with the hardware, never on the website. It is a candidate for a
Rust port once it guards the arms (see docs/adr/0004-rust-policy.md).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from .registry import Registry, Tool


@dataclass(frozen=True)
class Decision:
    allow: bool
    rule: str
    reason: str = ""
    args: BaseModel | None = None  # validated args, when allowed


@dataclass
class Request:
    tool_name: str
    raw_args: dict[str, Any]
    actor: str
    confirmed: bool = False
    automated: bool = False  # True for evals, replays, scripted loops
    remote: bool = False  # True for commands queued from the website


@dataclass
class SafetyGate:
    registry: Registry
    #: If this file exists, everything is denied. `touch STOP` is the software e-stop.
    stop_file: Path = Path("STOP")
    clock: Callable[[], float] = time.monotonic
    _last_sent: dict[str, float] = field(default_factory=dict)

    def check(self, req: Request) -> Decision:
        if self.stop_file.exists():
            return Decision(False, "stop_file", f"{self.stop_file} exists")
        tool = self.registry.get(req.tool_name)
        if tool is None:
            return Decision(False, "allowlist", f"unknown tool {req.tool_name}")
        try:
            args = tool.args_model.model_validate(req.raw_args)
        except ValidationError as e:
            return Decision(False, "args", e.errors(include_url=False)[0]["msg"])
        for rule in (_manual_only, _confirmation, _duration_cap):
            denied = rule(tool, req, args)
            if denied:
                return denied
        for interlock in self.registry.interlocks:
            reason = interlock.check(tool, args)
            if reason:
                return Decision(False, "interlock", f"{interlock.name}: {reason}")
        if tool.min_interval_s:
            last = self._last_sent.get(tool.name)
            if last is not None and self.clock() - last < tool.min_interval_s:
                return Decision(False, "rate_limit", f"wait {tool.min_interval_s}s between sends")
        return Decision(True, "allow", args=args)

    def record_sent(self, tool_name: str) -> None:
        self._last_sent[tool_name] = self.clock()


def _manual_only(tool: Tool, req: Request, _args: BaseModel) -> Decision | None:
    if tool.manual_only and (req.automated or req.remote):
        return Decision(False, "manual_only", f"{tool.name} is manual-only (local, supervised)")
    return None


def _confirmation(tool: Tool, req: Request, _args: BaseModel) -> Decision | None:
    if tool.requires_confirmation and not req.confirmed:
        return Decision(False, "requires_confirmation", f"{tool.name} needs explicit confirmation")
    return None


def _duration_cap(tool: Tool, _req: Request, args: BaseModel) -> Decision | None:
    if tool.duration_arg and tool.max_duration_s is not None:
        value = getattr(args, tool.duration_arg, None)
        if not isinstance(value, int | float) or value <= 0 or value > tool.max_duration_s:
            return Decision(
                False, "duration_cap", f"{tool.duration_arg} must be in (0, {tool.max_duration_s}]"
            )
    return None
