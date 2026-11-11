"""BroadLink RM4 Mini (IR). Requires the optional extra: uv sync --extra broadlink

Setup notes:
- Pair the RM4 with the BroadLink app on 2.4 GHz Wi-Fi, then turn OFF "Lock device"
  in the app's device settings, or authentication from Python fails.
- Give it a DHCP reservation so its IP never changes.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from . import ir
from .codes import CodeBook


@dataclass
class BroadlinkBlaster:
    id: str
    host: str
    codes: CodeBook
    timeout_s: float = 5.0
    _dev: Any = field(default=None, repr=False)

    def _device(self) -> Any:
        if self._dev is None:
            import broadlink  # optional dependency

            dev = broadlink.hello(self.host, timeout=self.timeout_s)
            dev.auth()
            self._dev = dev
        return self._dev

    def send(self, code_name: str) -> None:
        self._device().send_data(self.codes.get(code_name))

    def hold(self, code_name: str, seconds: float) -> int:
        """One network call: the RM4 repeats a single frame itself, so Wi-Fi latency
        cannot chop the motion up, and a long learned code cannot outlast `seconds`."""
        frame = ir.one_frame(self.codes.get(code_name))
        period = ir.duration_s(frame)
        frames = max(1, min(ir.MAX_REPEAT + 1, round(seconds / period)))
        self._device().send_data(ir.encode(frame, repeat=frames - 1))
        time.sleep(frames * period)  # return when the motion ends
        return frames

    def learn(self, code_name: str, wait_s: float = 60.0, arm_s: float = 25.0) -> bytes:
        """Point the remote at the RM4 and press the button once.

        The RM4 leaves learning mode after about 30 s (its LED goes off), so re-arm every
        `arm_s` until `wait_s`. A capture holds every frame sent while the button was
        down; `ir.one_frame` picks the usable one at send time."""
        from broadlink.exceptions import ReadError, StorageError

        dev = self._device()
        deadline = time.monotonic() + wait_s
        while time.monotonic() < deadline:
            dev.enter_learning()
            armed = time.monotonic()
            while time.monotonic() - armed < arm_s and time.monotonic() < deadline:
                time.sleep(0.5)
                try:
                    packet = dev.check_data()
                except (ReadError, StorageError):  # StorageError = nothing captured yet
                    continue
                self.codes.put(code_name, packet)
                return packet
        raise TimeoutError(
            f"no IR received in {wait_s:.0f}s for {code_name!r}: the remote is probably RF or"
            " Bluetooth (the RM4 Mini hears IR only), or was pressed while the LED was off"
        )


def _local_broadcast() -> str:
    """Broadcast address of the LAN this machine routes through, assuming a /24."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("192.0.2.1", 9))  # TEST-NET address: picks the route, sends nothing
        ip = s.getsockname()[0]
    return ip.rsplit(".", 1)[0] + ".255"


def discover(timeout_s: float = 5.0, broadcast: str | None = None) -> list[dict[str, str]]:
    """Find BroadLink devices. macOS often refuses 255.255.255.255 ("No route to host"),
    so on that error retry with the local subnet's broadcast address."""
    import broadlink

    try:
        found = broadlink.discover(
            timeout=timeout_s, discover_ip_address=broadcast or "255.255.255.255"
        )
    except OSError:
        if broadcast:
            raise
        found = broadlink.discover(timeout=timeout_s, discover_ip_address=_local_broadcast())
    return [
        {
            "host": d.host[0],
            "type": d.type,
            "model": getattr(d, "model", ""),
            "mac": d.mac.hex(":"),
            "locked": "yes (turn off Lock device in the BroadLink app)" if d.is_locked else "no",
        }
        for d in found
    ]
