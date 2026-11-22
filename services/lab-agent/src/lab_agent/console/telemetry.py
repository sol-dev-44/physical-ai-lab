"""Telemetry: what the robot's sensors say, for the console's state stream.

Live only: readings are not events (CONTROL_APP.md, "What gets logged"). Anything that
matters for safety reaches the gate through an interlock instead. Real sources arrive with
the sensors (step 3 of the order of work); FakeTelemetry lets the app be built on the Mac.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol


class Telemetry(Protocol):
    def read(self) -> dict[str, Any]:
        """Every State field except type, t, lease_alive, moving and stop_file."""
        ...


@dataclass
class FakeTelemetry:
    clock: Callable[[], float] = time.monotonic

    def read(self) -> dict[str, Any]:
        t = self.clock()
        wobble = math.sin(t / 30.0)
        return {
            "fake": True,
            "battery": {
                "volts": 13.1 + 0.05 * wobble,
                "amps": 0.4 + 0.05 * wobble,
                "soc_pct": 88.0,
                "runtime_min": 310.0,
            },
            "servos": [
                {"id": 1, "temp_c": 31.0 + wobble, "load_pct": 4.0, "volts": 12.1},
                {"id": 2, "temp_c": 30.5 + wobble, "load_pct": 3.5, "volts": 12.1},
            ],
            "tof": {"left_mm": 820, "center_mm": int(1200 + 100 * wobble), "right_mm": None},
            "cliff_mm": [42, 41, 43],
            "bumpers": [False, False],
            "wifi_dbm": -54.0,
            "pi_temp_c": 48.0 + wobble,
            "estop": False,
            "controller": {"connected": False, "battery_pct": None},
        }
