"""One browser's driving: turns joystick input into gated, logged drive commands.

- drive(v, w) renews the lease and sends base.drive only on a meaningful change, at most
  every min_interval_s, so the log stays readable (CONTROL_APP.md, "What gets logged").
- heartbeat() renews the lease without logging.
- tick() is the watchdog: called often, it sends one base.stop when the lease has lapsed.
- stop() cancels the lease and stops at once.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field

from ..events import Actor
from ..lease import DriveLease
from ..runner import CommandResult, Runner


@dataclass
class DriveSession:
    runner: Runner
    lease: DriveLease
    clock: Callable[[], float] = time.monotonic
    min_interval_s: float = 0.1
    min_dv: float = 0.02
    min_dw: float = 0.05
    moving: bool = field(default=False, init=False)
    _last: tuple[float, float] | None = field(default=None, init=False)
    _last_t: float = field(default=float("-inf"), init=False)
    _stopped_t: float = field(default=float("-inf"), init=False)

    def drive(self, v: float, w: float) -> CommandResult | None:
        self.lease.renew()
        now = self.clock()
        if self._last is not None:
            if now - self._last_t < self.min_interval_s:
                return None
            lv, lw = self._last
            if abs(v - lv) < self.min_dv and abs(w - lw) < self.min_dw:
                return None
        result = self.runner.request("base.drive", {"v": v, "w": w}, actor="human")
        if result.ok:
            self._last, self._last_t = (v, w), now
            self.moving = v != 0.0 or w != 0.0
        return result

    def heartbeat(self) -> None:
        self.lease.renew()

    def tick(self) -> CommandResult | None:
        if self.moving and not self.lease.alive():
            return self._halt("system")
        return None

    def stop(self, actor: Actor = "human") -> CommandResult | None:
        """Cancel the lease and stop. A stop while already stopped within the last
        min_interval_s is collapsed (returns None), so a flood of stops cannot flood the
        log or the servo bus; a stop is never refused by the gate."""
        self.lease.cancel()
        now = self.clock()
        if not self.moving and now - self._stopped_t < self.min_interval_s:
            return None
        return self._halt(actor)

    def _halt(self, actor: Actor) -> CommandResult:
        result = self.runner.request("base.stop", actor=actor)
        self.moving = False
        self._last = None
        self._stopped_t = self.clock()
        return result
