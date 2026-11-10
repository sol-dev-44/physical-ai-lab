"""Learned IR/RF codes, stored as JSON: {"fan_power": "<base64>", ...}.
One file per physical blaster, e.g. experiments/exp000-ir-bridge/codes/rm4-mini-living.json"""

from __future__ import annotations

import base64
import json
from pathlib import Path


class CodeBook:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._codes: dict[str, str] = json.loads(path.read_text()) if path.exists() else {}

    def get(self, name: str) -> bytes:
        if name not in self._codes:
            raise KeyError(f"no code named {name!r} in {self.path}; learn it first")
        return base64.b64decode(self._codes[name])

    def put(self, name: str, packet: bytes) -> None:
        self._codes[name] = base64.b64encode(packet).decode()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._codes, indent=2, sort_keys=True) + "\n")

    def names(self) -> list[str]:
        return sorted(self._codes)
