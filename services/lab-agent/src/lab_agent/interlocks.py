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
    """How far a tool moves the robot: base_cm + speed * seconds, in a direction relative
    to its heading (0 = straight ahead, 180 = straight back). `base_cm` is a fixed step
    per command: the exp000 toy moves about 16 cm for any press, even 0.3 s (measured
    2026-11-11). `slack` widens the predicted end point into a disc of radius
    slack * distance, to cover an unmeasured or noisy model."""

    speed_cm_s: float
    direction_deg: float
    slack: float = 0.5
    base_cm: float = 0.0

    def distance(self, seconds: float) -> float:
        return self.base_cm + self.speed_cm_s * seconds


@dataclass
class ArenaFence:
    """Deny a move whose predicted end (with slack) comes within `margin_cm` of an edge.

    Tools not in `motions` pass. The prediction is a straight line; for an arcing move,
    set `slack` to cover the arc.

    Recovery: when the robot is already near or past an edge, a move is allowed if even
    its worst-case end (with slack) is further from the edge than the robot is now, by at
    least `recovery_gain_cm`. So a robot that strayed can be brought back, but never
    pushed further out."""

    source: PoseSource
    width_cm: float
    height_cm: float
    motions: Mapping[str, Motion]
    duration_arg: str = "seconds"
    margin_cm: float = 10.0
    recovery: bool = True
    recovery_gain_cm: float = 2.0
    name: str = "arena_fence"

    def room(self, x: float, y: float) -> float:
        """Distance to the nearest edge; negative outside the arena."""
        return min(x, y, self.width_cm - x, self.height_cm - y)

    def predict(self, pose: Pose, tool: str, seconds: float) -> tuple[float, float, float]:
        """(x, y, slack radius) of the predicted end of `tool` held for `seconds`."""
        motion = self.motions[tool]
        dist = motion.distance(seconds)
        a = math.radians(pose.heading_deg + motion.direction_deg)
        return pose.x_cm + dist * math.cos(a), pose.y_cm + dist * math.sin(a), motion.slack * dist

    def check(self, tool: Tool, args: BaseModel) -> str | None:
        if tool.name not in self.motions:
            return None
        pose = self.source.latest()
        if pose is None:
            return "robot not tracked"
        seconds = float(getattr(args, self.duration_arg, 0) or 0)
        if math.isnan(pose.heading_deg):
            # Heading unknown (learned from motion, not yet): the move could go any way.
            motion = self.motions[tool.name]
            # Every direction is already assumed, so no heading slack; 15% for distance.
            reach = motion.distance(seconds) * 1.15
            if self.room(pose.x_cm, pose.y_cm) - reach >= self.margin_cm:
                return None
            return (
                f"heading unknown and a {reach:.0f} cm move from ({pose.x_cm:.0f},"
                f" {pose.y_cm:.0f}) could reach the edge: move the robot to the middle"
            )
        x, y, slack = self.predict(pose, tool.name, seconds)
        room = self.room(x, y) - slack
        if room >= self.margin_cm:
            return None
        if self.recovery and room >= self.room(pose.x_cm, pose.y_cm) + self.recovery_gain_cm:
            return None  # brings a stray robot back toward the middle
        return (
            f"predicted end ({x:.0f}, {y:.0f}) cm is within {self.margin_cm:.0f} cm of the"
            f" arena edge (arena {self.width_cm:.0f} x {self.height_cm:.0f} cm)"
        )
