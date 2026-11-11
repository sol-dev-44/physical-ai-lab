"""Interlocks: safety rules that depend on the state of the world, not just the request.

A tool set attaches them to its Registry; the SafetyGate runs every one after its own
rules and denies with rule "interlock" and a reason naming the interlock. They live here,
with the gate, never in a device adapter: sensors only report state.

Arena coordinates are centimetres in a right-handed frame seen from above: x along the
first edge, y along the second, heading in degrees counterclockwise from +x. So a left
turn is a positive heading change.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel

from .registry import Tool


@dataclass(frozen=True)
class Pose:
    x_cm: float
    y_cm: float
    heading_deg: float
    t: float  # time.monotonic() of the frame it came from


class PoseSource(Protocol):
    """Anything that knows where the robot is (a camera tracker, a simulator)."""

    def latest(self) -> Pose | None: ...


class Interlock(Protocol):
    name: str

    def check(self, tool: Tool, args: BaseModel) -> str | None:
        """A reason to deny, or None to allow."""
        ...


@dataclass
class FreshPose:
    """Deny guarded tools unless the robot was seen recently. No fix, no motion."""

    source: PoseSource
    guarded: frozenset[str]
    max_age_s: float = 1.0
    clock: Callable[[], float] = time.monotonic
    name: str = "fresh_pose"

    def check(self, tool: Tool, _args: BaseModel) -> str | None:
        if tool.name not in self.guarded:
            return None
        pose = self.source.latest()
        if pose is None:
            return "robot not tracked"
        age = self.clock() - pose.t
        if age > self.max_age_s:
            return f"last robot fix is {age:.1f}s old (max {self.max_age_s}s)"
        return None


@dataclass(frozen=True)
class Motion:
    """How far a tool moves the robot: speed, and direction relative to its heading
    (0 = straight ahead, 180 = straight back). `slack` widens the predicted end point
    into a disc of radius slack * distance, to cover an unmeasured or noisy model."""

    speed_cm_s: float
    direction_deg: float
    slack: float = 0.5


@dataclass
class ArenaFence:
    """Deny a move whose predicted end (with slack) comes within `margin_cm` of an edge.

    Tools not in `motions` pass. The prediction is a straight line; for an arcing move,
    set `slack` to cover the arc."""

    source: PoseSource
    width_cm: float
    height_cm: float
    motions: Mapping[str, Motion]
    duration_arg: str = "seconds"
    margin_cm: float = 10.0
    name: str = "arena_fence"

    def check(self, tool: Tool, args: BaseModel) -> str | None:
        motion = self.motions.get(tool.name)
        if motion is None:
            return None
        pose = self.source.latest()
        if pose is None:
            return "robot not tracked"
        seconds = float(getattr(args, self.duration_arg, 0) or 0)
        dist = motion.speed_cm_s * seconds
        a = math.radians(pose.heading_deg + motion.direction_deg)
        x, y = pose.x_cm + dist * math.cos(a), pose.y_cm + dist * math.sin(a)
        room = min(x, y, self.width_cm - x, self.height_cm - y) - motion.slack * dist
        if room < self.margin_cm:
            return (
                f"predicted end ({x:.0f}, {y:.0f}) cm is within {self.margin_cm:.0f} cm of the"
                f" arena edge (arena {self.width_cm:.0f} x {self.height_cm:.0f} cm)"
            )
        return None
