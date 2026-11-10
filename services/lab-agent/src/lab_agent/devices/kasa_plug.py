"""TP-Link Kasa smart plug. Requires the optional extra: uv sync --extra kasa"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass
class KasaPlug:
    id: str
    host: str

    def set(self, on: bool) -> None:
        asyncio.run(self._set(on))

    async def _set(self, on: bool) -> None:
        from kasa import Discover  # optional dependency

        dev = await Discover.discover_single(self.host)
        try:
            await (dev.turn_on() if on else dev.turn_off())
        finally:
            await dev.disconnect()
