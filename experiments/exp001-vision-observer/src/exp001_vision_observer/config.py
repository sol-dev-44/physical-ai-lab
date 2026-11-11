"""Arena and marker configuration, stored as arena.json next to this package.

Corners are pixel coordinates of the taped arena corners, in this order, seen from above:
(0, 0), (width, 0), (width, height), (0, height). Going around counterclockwise from
above makes the arena frame right-handed, so a left turn is a positive heading change.
Holding the camera mirrored doesn't matter: the corner order defines the frame.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ARENA_JSON = Path(__file__).resolve().parents[2] / "arena.json"
#: The empty-arena reference frame. Local only (media/ is gitignored), captured only with
#: --nobody-in-frame (ADR 0007).
BACKGROUND = Path(__file__).resolve().parents[4] / "media" / "exp001" / "background.png"


class HsvRange(BaseModel):
    """OpenCV HSV: hue 0-179, saturation and value 0-255. lo_h > hi_h wraps (reds)."""

    model_config = ConfigDict(extra="forbid")
    lo: tuple[int, int, int]
    hi: tuple[int, int, int]


#: Named colours for --front / --back. Orange: the checkered triangles on the exp000 robot.
PRESETS: dict[str, HsvRange] = {
    "green": HsvRange(lo=(45, 120, 120), hi=(80, 255, 255)),
    "pink": HsvRange(lo=(150, 100, 120), hi=(175, 255, 255)),
    "orange": HsvRange(lo=(4, 130, 140), hi=(20, 255, 255)),
    "blue": HsvRange(lo=(100, 150, 80), hi=(125, 255, 255)),
    # dark green sticker: low brightness, so a wide value range; tune from a snapshot
    "darkgreen": HsvRange(lo=(40, 60, 30), hi=(90, 255, 200)),
}


class Markers(BaseModel):
    model_config = ConfigDict(extra="forbid")
    head: HsvRange = HsvRange(lo=(45, 120, 120), hi=(80, 255, 255))  # neon green, front
    tail: HsvRange = HsvRange(lo=(150, 100, 120), hi=(175, 255, 255))  # pink, back
    min_area_px: int = 30


class Background(BaseModel):
    """Settings for tracking="background": the robot is whatever differs from the empty
    arena, and the `markers.head` colour inside it marks the front. Works on busy or
    same-coloured floors and ignores static glare; needs steady lighting."""

    model_config = ConfigDict(extra="forbid")
    #: A pixel changed if its colour (Lab a or b) moved more than this...
    chroma_threshold: int = 30
    #: ...or its lightness moved more than this. Higher than chroma so shadows, which
    #: mostly darken, don't count as robot (measured on the Botley mats, 2026-11-10).
    light_threshold: int = 80
    min_robot_px: int = 2000  # smaller blobs are noise
    max_robot_px: int = 200_000  # bigger means a person, a hand, or a lighting change
    min_front_px: int = 40  # front-marker pixels needed to trust the heading


class Arena(BaseModel):
    model_config = ConfigDict(extra="forbid")
    width_cm: float = Field(gt=0)
    height_cm: float = Field(gt=0)
    corners_px: list[tuple[float, float]] = Field(min_length=4, max_length=4)
    markers: Markers = Markers()
    #: Camera index for OpenCV (0 is usually the built-in camera; Continuity Camera is often 1).
    camera_index: int = 0
    #: macOS camera name; snapshots open the camera by this name, and `exp001 cameras
    #: --match` finds the OpenCV index showing the same picture.
    camera_name: str | None = None
    #: Digital zoom: crop the centre 1/zoom of the frame (1.5 = what the 1.5x preview shows).
    #: Corner pixels are in the cropped frame, so change zoom only before calibrating.
    zoom: float = Field(default=1.0, ge=1.0, le=4.0)
    margin_cm: float = 10.0
    #: "markers": two colour stickers (front + back). "background": empty-arena difference
    #: plus one front colour (`markers.head`), for floors that share the stickers' colours.
    tracking: Literal["markers", "background"] = "markers"
    #: Added to the marker heading so it matches the direction the robot actually drives.
    #: Measured by `exp001 heading` (one forward move); stickers needn't be on the centre line.
    heading_offset_deg: float = 0.0
    background: Background = Background()

    @classmethod
    def load(cls, path: Path = ARENA_JSON) -> Arena:
        return cls.model_validate(json.loads(path.read_text()))

    def save(self, path: Path = ARENA_JSON) -> None:
        path.write_text(json.dumps(self.model_dump(mode="json"), indent=2) + "\n")
