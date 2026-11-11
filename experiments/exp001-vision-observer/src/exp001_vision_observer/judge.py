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


def judge(
    tool: str, before: Pose | None, after: Pose | None, min_cm: float = MIN_MOVE_CM
) -> Verdict:
    """forward: moved at least min_cm ahead. reverse: moved at least min_cm, backwards.
    Anything else, or a lost fix, is not a success; the reason says which."""
    if before is None or after is None:
        return Verdict(False, "robot not tracked before or after")
    a = math.radians(before.heading_deg)
    dx, dy = after.x_cm - before.x_cm, after.y_cm - before.y_cm
    along = dx * math.cos(a) + dy * math.sin(a)
    lateral = -dx * math.sin(a) + dy * math.cos(a)
    turn = _wrap(after.heading_deg - before.heading_deg)
    moved = math.hypot(dx, dy)
    v = dict(along_cm=along, lateral_cm=lateral, turn_deg=turn, moved_cm=moved)
    if tool == "robot.forward":
        ok = along >= min_cm
        return Verdict(ok, "moved forward" if ok else f"forward only {along:.1f} cm", **v)
    if tool == "robot.reverse":
        ok = moved >= min_cm and along < 0
        return Verdict(ok, "moved backward" if ok else f"backward only {-along:.1f} cm", **v)
    return Verdict(False, f"no visual check for {tool}", **v)
