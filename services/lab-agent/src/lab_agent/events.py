"""Python mirror of the lab event contract (packages/schema, version 0).

zod in packages/schema is the authoring source. This module must accept and
reject exactly what it does; tests/test_contract.py enforces that against the
shared fixtures and the generated JSON Schema.
"""

from __future__ import annotations

import os
import time
from datetime import UTC, datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, TypeAdapter

SCHEMA_VERSION = 0

ULID_RE = r"^[0-9A-HJKMNP-TV-Z]{26}$"
RUN_ID_RE = r"^[a-z0-9][a-z0-9-]{2,79}$"
EXPERIMENT_ID_RE = r"^exp\d{3}(-[a-z0-9]+)*$"
TOOL_RE = r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$"
TS_RE = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?Z$"

Ulid = Annotated[str, Field(pattern=ULID_RE)]
RunId = Annotated[str, Field(pattern=RUN_ID_RE)]
ExperimentId = Annotated[str, Field(pattern=EXPERIMENT_ID_RE)]
ToolName = Annotated[str, Field(pattern=TOOL_RE)]
Timestamp = Annotated[str, Field(pattern=TS_RE)]
Actor = Literal["human", "cli", "agent", "llm", "replay", "system"]
Args = dict[str, Any]

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_ulid(now_ms: int | None = None) -> str:
    """26-char ULID: 48-bit ms timestamp + 80 random bits, Crockford base32."""
    ms = int(time.time() * 1000) if now_ms is None else now_ms
    value = (ms << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD[(value >> (5 * i)) & 31] for i in reversed(range(26)))


def now_ts() -> str:
    """RFC 3339 UTC with milliseconds, e.g. 2026-11-09T20:00:01.180Z"""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


# Optional fields may be omitted but not sent as null (zod's .optional() rejects
# null). Annotating the plain type with a None default does exactly that:
# pydantic does not validate defaults, so "missing" -> None, explicit null -> error.
OMIT: Any = None


# ---------------------------------------------------------------- payloads (loose)
class _Payload(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)


class RunStartedPayload(_Payload):
    experiment_id: ExperimentId
    git_sha: str = OMIT
    forked_from: RunId = OMIT
    null_test: StrictBool = OMIT


class RunEndedPayload(_Payload):
    status: Literal["completed", "aborted", "failed"]


class EmptyPayload(_Payload):
    pass


class SafetyPayload(_Payload):
    decision: Literal["allow", "deny"]
    rule: str = OMIT
    reason: str = OMIT


class SentPayload(_Payload):
    latency_ms: Annotated[float, Field(ge=0)] = OMIT


class FailedPayload(_Payload):
    error: Annotated[str, Field(min_length=1)]


class OutcomePayload(_Payload):
    success: StrictBool
    method: Literal["human", "camera", "sensor", "device"]
    note: str = OMIT


class NotePayload(_Payload):
    text: Annotated[str, Field(min_length=1)]


# ---------------------------------------------------------------- envelope (strict)
class _Envelope(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    v: Literal[0]
    event_id: Ulid
    run_id: RunId
    seq: Annotated[StrictInt, Field(ge=0)]
    ts: Timestamp
    actor: Actor
    parent_id: Ulid = OMIT
    device: Annotated[str, Field(min_length=1)] = OMIT


class _ToolCall(_Envelope):
    tool: ToolName
    args: Args


class RunStarted(_Envelope):
    type: Literal["run.started"]
    payload: RunStartedPayload


class RunEnded(_Envelope):
    type: Literal["run.ended"]
    payload: RunEndedPayload


class CommandRequested(_ToolCall):
    type: Literal["command.requested"]
    payload: EmptyPayload


class SafetyChecked(_ToolCall):
    type: Literal["safety.checked"]
    payload: SafetyPayload


class CommandSent(_ToolCall):
    type: Literal["command.sent"]
    payload: SentPayload


class CommandFailed(_ToolCall):
    type: Literal["command.failed"]
    payload: FailedPayload


class OutcomeObserved(_Envelope):
    type: Literal["outcome.observed"]
    tool: ToolName = OMIT
    payload: OutcomePayload


class Note(_Envelope):
    type: Literal["note"]
    payload: NotePayload


Event = Annotated[
    RunStarted
    | RunEnded
    | CommandRequested
    | SafetyChecked
    | CommandSent
    | CommandFailed
    | OutcomeObserved
    | Note,
    Field(discriminator="type"),
]

EventAdapter: TypeAdapter[Event] = TypeAdapter(Event)


def parse_event(data: dict[str, Any] | str | bytes) -> Event:
    """Validate one event (dict or JSON text). Raises pydantic.ValidationError."""
    if isinstance(data, str | bytes):
        return EventAdapter.validate_json(data)
    return EventAdapter.validate_python(data)


def to_json(event: Event) -> str:
    """Serialize for the log: no None fields, compact, stable key order."""
    return event.model_dump_json(exclude_none=True)
