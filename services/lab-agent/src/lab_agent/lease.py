"""A drive lease: motion is allowed only inside a short, renewable window.

The robot console renews it on every heartbeat while the drive button is held. When the
heartbeats stop (button released, tab closed, Wi-Fi gone) it lapses, the drive_lease
interlock refuses further drive commands, and the console's watchdog stops the wheels.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class DriveLease:
    ttl_s: float = 0.3
    clock: Callable[[], float] = time.monotonic
    _until: float = field(default=float("-inf"), init=False)

    def renew(self) -> None:
        self._until = self.clock() + self.ttl_s

    def cancel(self) -> None:
        self._until = float("-inf")

    def alive(self) -> bool:
        return self.clock() < self._until
