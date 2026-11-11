"""Arena and marker configuration, stored as arena.json next to this package.

Corners are pixel coordinates of the taped arena corners, in this order, seen from above:
(0, 0), (width, 0), (width, height), (0, height). Going around counterclockwise from
above makes the arena frame right-handed, so a left turn is a positive heading change.
Holding the camera mirrored doesn't matter: the corner order defines the frame.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

ARENA_JSON = Path(__file__).resolve().parents[2] / "arena.json"


class HsvRange(BaseModel):
    """OpenCV HSV: hue 0-179, saturation and value 0-255. lo_h > hi_h wraps (reds)."""

    model_config = ConfigDict(extra="forbid")
    lo: tuple[int, int, int]
    hi: tuple[int, int, int]


class Markers(BaseModel):
    model_config = ConfigDict(extra="forbid")
    head: HsvRange = HsvRange(lo=(45, 120, 120), hi=(80, 255, 255))  # neon green, front
    tail: HsvRange = HsvRange(lo=(150, 100, 120), hi=(175, 255, 255))  # pink, back
    min_area_px: int = 30


class Arena(BaseModel):
    model_config = ConfigDict(extra="forbid")
    width_cm: float = Field(gt=0)
    height_cm: float = Field(gt=0)
    corners_px: list[tuple[float, float]] = Field(min_length=4, max_length=4)
    markers: Markers = Markers()
    #: Camera index for OpenCV (0 is usually the built-in camera; Continuity Camera is often 1).
    camera_index: int = 0
    margin_cm: float = 10.0

    @classmethod
    def load(cls, path: Path = ARENA_JSON) -> Arena:
        return cls.model_validate(json.loads(path.read_text()))

    def save(self, path: Path = ARENA_JSON) -> None:
        path.write_text(json.dumps(self.model_dump(mode="json"), indent=2) + "\n")
