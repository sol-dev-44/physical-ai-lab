"""Typed tool registry.

A tool is the only unit the harness can execute: a dotted name, a pydantic
model for its args, a handler, and safety metadata. Callers (CLI, admin queue,
LLM, replay) all go through the same Runner, so every path is gated and logged.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ConfigDict


class NoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")


Handler = Callable[[BaseModel], dict[str, Any] | None]


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    handler: Handler
    args_model: type[BaseModel] = NoArgs
    device: str | None = None
    requires_confirmation: bool = False
    #: Minimum seconds between two sends of this tool (debounce, protects devices).
    min_interval_s: float = 0.0
    #: Arg name holding a duration in seconds, and its hard cap.
    duration_arg: str | None = None
    max_duration_s: float | None = None
    #: Excluded from automated loops (evals, replay); manual, supervised use only.
    manual_only: bool = False
    tags: frozenset[str] = field(default_factory=frozenset)

    def args_schema(self) -> dict[str, Any]:
        return self.args_model.model_json_schema()


class Registry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        #: World-state safety rules the gate runs after its own (see interlocks.py).
        #: Typed loosely to avoid an import cycle; each must satisfy interlocks.Interlock.
        self.interlocks: list[Any] = []

    def add_interlock(self, interlock: Any) -> None:
        self.interlocks.append(interlock)

    def add(self, tool: Tool) -> Tool:
        import re

        from .events import TOOL_RE

        if not re.match(TOOL_RE, tool.name):
            raise ValueError(f"bad tool name {tool.name!r}; use dotted lowercase like fan.power")
        if tool.name in self._tools:
            raise ValueError(f"tool {tool.name} already registered")
        if tool.duration_arg and tool.max_duration_s is None:
            raise ValueError(f"{tool.name}: duration_arg needs max_duration_s")
        self._tools[tool.name] = tool
        return tool

    def tool(self, name: str, description: str, **opts: Any) -> Callable[[Handler], Handler]:
        """Decorator form: @registry.tool("fan.power", "Toggle fan power")"""

        def wrap(fn: Handler) -> Handler:
            self.add(Tool(name=name, description=description, handler=fn, **opts))
            return fn

        return wrap

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def __iter__(self):
        return iter(sorted(self._tools.values(), key=lambda t: t.name))

    def __len__(self) -> int:
        return len(self._tools)
