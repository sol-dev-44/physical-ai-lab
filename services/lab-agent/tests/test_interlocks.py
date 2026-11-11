from dataclasses import dataclass

import pytest
from lab_agent.interlocks import ArenaFence, FreshPose, Motion, Pose
from lab_agent.registry import Registry, Tool
from lab_agent.safety import Request, SafetyGate
from pydantic import BaseModel, ConfigDict


class Secs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    seconds: float


@dataclass
class Fixed:
    pose: Pose | None

    def latest(self) -> Pose | None:
        return self.pose


def gate(tmp_path, source, *, now=0.0) -> SafetyGate:
    reg = Registry()
    reg.add(Tool("robot.forward", "fwd", lambda _a: None, args_model=Secs))
    reg.add(Tool("robot.reverse", "rev", lambda _a: None, args_model=Secs))
    reg.add(Tool("tv.power", "tv", lambda _a: None))
    moving = frozenset({"robot.forward", "robot.reverse"})
    reg.add_interlock(FreshPose(source, moving, max_age_s=1.0, clock=lambda: now))
    reg.add_interlock(
        ArenaFence(
            source,
            width_cm=100,
            height_cm=80,
            motions={"robot.forward": Motion(20, 0), "robot.reverse": Motion(20, 180)},
            margin_cm=10,
        )
    )
    return SafetyGate(reg, stop_file=tmp_path / "STOP")


def fwd(seconds=1):
    return Request("robot.forward", {"seconds": seconds}, "cli")


def test_no_fix_no_motion(tmp_path):
    d = gate(tmp_path, Fixed(None)).check(fwd())
    assert (d.allow, d.rule) == (False, "interlock")
    assert d.reason.startswith("fresh_pose: robot not tracked")


def test_stale_fix_denied(tmp_path):
    d = gate(tmp_path, Fixed(Pose(50, 40, 0, t=0.0)), now=2.5).check(fwd())
    assert not d.allow and "2.5s old" in d.reason


def test_unguarded_tools_ignore_the_camera(tmp_path):
    assert gate(tmp_path, Fixed(None)).check(Request("tv.power", {}, "cli")).allow


def test_move_in_the_middle_is_allowed(tmp_path):
    assert gate(tmp_path, Fixed(Pose(50, 40, 0, t=0.0))).check(fwd()).allow


@pytest.mark.parametrize(
    ("pose", "tool", "seconds"),
    [
        (Pose(70, 40, 0, t=0.0), "robot.forward", 1),  # 70 + 20 = 90, slack 10 -> at the edge
        (Pose(30, 40, 0, t=0.0), "robot.reverse", 1),  # backing toward x = 0
        (Pose(50, 60, 90, t=0.0), "robot.forward", 1),  # heading +y toward y = 80
        (Pose(50, 40, 0, t=0.0), "robot.forward", 3),  # long move from the middle
    ],
)
def test_fence_denies_moves_that_end_near_an_edge(tmp_path, pose, tool, seconds):
    d = gate(tmp_path, Fixed(pose)).check(Request(tool, {"seconds": seconds}, "cli"))
    assert not d.allow and d.reason.startswith("arena_fence:")


def test_dry_runs_are_fenced_too(tmp_path):
    # Null tests must see the same gate as real runs; the gate doesn't know about dry_run.
    d = gate(tmp_path, Fixed(Pose(95, 40, 0, t=0.0))).check(
        Request("robot.forward", {"seconds": 1}, "cli", automated=True)
    )
    assert not d.allow
