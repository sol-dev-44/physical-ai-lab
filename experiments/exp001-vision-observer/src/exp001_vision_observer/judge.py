"""Did the command do what it says? Decided from the pose before and after, nothing else."""

from __future__ import annotations

import math
from dataclasses import dataclass

from lab_agent.interlocks import Pose

MIN_MOVE_CM = 5.0


@dataclass(frozen=True)
class Verdict:
    success: bool
    reason: str
    along_cm: float = 0.0  # + forward along the starting heading, - backward
    lateral_cm: float = 0.0  # + to the left of the starting heading
    turn_deg: float = 0.0  # + left (counterclockwise from above)
    moved_cm: float = 0.0

    def payload(self) -> dict[str, float | str | bool]:
        return {
            "reason": self.reason,
            "along_cm": round(self.along_cm, 1),
            "lateral_cm": round(self.lateral_cm, 1),
            "turn_deg": round(self.turn_deg, 1),
            "moved_cm": round(self.moved_cm, 1),
        }


def _wrap(deg: float) -> float:
    return (deg + 180) % 360 - 180


def heading_from_move(
    tool: str, before: Pose, after: Pose, *, turn_deg: float = 0.0
) -> float | None:
    """Which way the robot faces after a move, from where it went: forward travel points
    the way it faces, reverse travel the opposite way. A move that turns by `turn_deg`
    (+ left) travels along the middle of its arc, so the end heading is half the turn on
    from the travel direction. None if it moved too little to tell."""
    dx, dy = after.x_cm - before.x_cm, after.y_cm - before.y_cm
    if math.hypot(dx, dy) < MIN_MOVE_CM:
        return None
    travel = math.degrees(math.atan2(dy, dx))
    if tool == "robot.forward":
        return _wrap(travel + turn_deg / 2)
    if tool == "robot.reverse":
        return _wrap(travel + 180 + turn_deg / 2)
    return None


def judge(
    tool: str, before: Pose | None, after: Pose | None, min_cm: float = MIN_MOVE_CM
) -> Verdict:
    """forward: moved at least min_cm ahead. reverse: moved at least min_cm, backwards.
    Anything else, or a lost fix, is not a success; the reason says which."""
    if before is None or after is None:
        return Verdict(False, "robot not tracked before or after")
    dx, dy = after.x_cm - before.x_cm, after.y_cm - before.y_cm
    if math.isnan(before.heading_deg):
        # Heading unknown (first move with heading from motion): only "did it move".
        moved = math.hypot(dx, dy)
        ok = moved >= min_cm
        return Verdict(ok, f"moved {moved:.1f} cm, heading unknown", moved_cm=moved)
    a = math.radians(before.heading_deg)
    along = dx * math.cos(a) + dy * math.sin(a)
    lateral = -dx * math.sin(a) + dy * math.cos(a)
    turn = 0.0 if math.isnan(after.heading_deg) else _wrap(after.heading_deg - before.heading_deg)
    moved = math.hypot(dx, dy)
    v = dict(along_cm=along, lateral_cm=lateral, turn_deg=turn, moved_cm=moved)
    if tool == "robot.forward":
        ok = along >= min_cm
        return Verdict(ok, "moved forward" if ok else f"forward only {along:.1f} cm", **v)
    if tool == "robot.reverse":
        ok = moved >= min_cm and along < 0
        return Verdict(ok, "moved backward" if ok else f"backward only {-along:.1f} cm", **v)
    return Verdict(False, f"no visual check for {tool}", **v)
