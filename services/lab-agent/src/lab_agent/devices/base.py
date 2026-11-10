from __future__ import annotations

from typing import Protocol


class Blaster(Protocol):
    """Anything that can send a named code (IR blaster, RF bridge, fake)."""

    id: str

    def send(self, code_name: str) -> None: ...


class Switch(Protocol):
    """Anything with on/off (smart plug, relay)."""

    id: str

    def set(self, on: bool) -> None: ...
