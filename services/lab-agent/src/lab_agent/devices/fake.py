"""In-memory devices for tests, null tests and developing without hardware."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FakeBlaster:
    id: str = "fake-blaster"
    known: set[str] | None = None  # None = accept any code
    fail_next: int = 0
    sent: list[str] = field(default_factory=list)

    def send(self, code_name: str) -> None:
        if self.fail_next > 0:
            self.fail_next -= 1
            raise TimeoutError("fake device timeout")
        if self.known is not None and code_name not in self.known:
            raise KeyError(f"no code named {code_name!r}")
        self.sent.append(code_name)

    def hold(self, code_name: str, seconds: float) -> int:
        self.send(code_name)
        return max(1, round(seconds / 0.12))


@dataclass
class FakeSwitch:
    id: str = "fake-switch"
    state: bool = False
    history: list[bool] = field(default_factory=list)

    def set(self, on: bool) -> None:
        self.state = on
        self.history.append(on)
