"""One browser's driving: turns joystick input into gated, logged drive commands.

- drive(v, w) renews the lease and sends base.drive only on a meaningful change, at most
  every min_interval_s, so the log stays readable (CONTROL_APP.md, "What gets logged").
- heartbeat() renews the lease without logging.
- tick() is the watchdog: called often, it sends one base.stop when the lease has lapsed.
- stop() cancels the lease and stops at once.

The wheels never stay running on a lost command: a change dropped by the time dedupe is kept
as a pending target and sent by tick(); a move to (0, 0) is never deduped; a drive that is
refused or fails while moving, a lapsed lease, or the STOP file all halt the wheels; and a
failed stop is retried by tick() at most once per min_interval_s.

Worst-case run-on after the browser goes silent is ttl_s plus the watchdog period (about
0.35 s) if the event loop is not blocked. The real wheel driver needs its own hardware
timeout as a backstop; this module cannot cover a hung process.
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
    _pending: tuple[float, float] | None = field(default=None, init=False)
    _stopped_t: float = field(default=float("-inf"), init=False)
    _halt_t: float = field(default=float("-inf"), init=False)

    def drive(self, v: float, w: float) -> CommandResult | None:
        self.lease.renew()
        now = self.clock()
        if v == 0.0 and w == 0.0:
            self._pending = None
            return self._halt("human") if self.moving else None
        if self._last is not None:
            if now - self._last_t < self.min_interval_s:
                self._pending = (v, w)  # tick() sends it once the interval has passed
                return None
            lv, lw = self._last
            if abs(v - lv) < self.min_dv and abs(w - lw) < self.min_dw:
                self._pending = None
                return None
        return self._send(v, w)

    def _send(self, v: float, w: float) -> CommandResult:
        self._pending = None
        result = self.runner.request("base.drive", {"v": v, "w": w}, actor="human")
        if result.ok:
            self._last, self._last_t = (v, w), self.clock()
            self.moving = True
        elif self.moving:
            return self._halt("system", result)
        return result

    def heartbeat(self) -> None:
        self.lease.renew()

    def tick(self) -> CommandResult | None:
        if not self.moving:
            return None
        now = self.clock()
        if not self.lease.alive() or self.runner.gate.stop_file.exists():
            if now - self._halt_t >= self.min_interval_s:
                return self._halt("system")
            return None
        if self._pending is not None and now - self._last_t >= self.min_interval_s:
            return self._send(*self._pending)
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

    def _halt(self, actor: Actor, instead: CommandResult | None = None) -> CommandResult:
        """Stop the wheels. A failed stop leaves moving True so tick() retries it. When
        halting because a drive was refused, return that drive's result."""
        result = self.runner.request("base.stop", actor=actor)
        self._halt_t = self.clock()
        self._pending = None
        self._last = None
        self.moving = not result.ok
        if result.ok:
            self._stopped_t = self._halt_t
        return instead or result
