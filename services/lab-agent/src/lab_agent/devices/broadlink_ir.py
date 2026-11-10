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

    def learn(self, code_name: str, wait_s: float = 15.0) -> bytes:
        """Point the remote at the RM4 and press the button once."""
        from broadlink.exceptions import ReadError, StorageError

        dev = self._device()
        dev.enter_learning()
        deadline = time.monotonic() + wait_s
        while time.monotonic() < deadline:
            time.sleep(0.5)
            try:
                packet = dev.check_data()
            except (ReadError, StorageError):
                continue
            self.codes.put(code_name, packet)
            return packet
        raise TimeoutError(f"no IR signal received in {wait_s}s for {code_name!r}")


def discover(timeout_s: float = 5.0) -> list[dict[str, str]]:
    import broadlink

    return [
        {"host": d.host[0], "type": d.type, "model": getattr(d, "model", ""), "mac": d.mac.hex(":")}
        for d in broadlink.discover(timeout=timeout_s)
    ]
