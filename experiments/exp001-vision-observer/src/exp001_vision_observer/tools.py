"""Tool set for Experiment 1: the exp000 robot, with the camera wired into the gate.

Real mode needs RM4_HOST and a calibrated arena.json; it drives the real RM4 with the
exp000 codebook and reads the real camera. Otherwise (or with LAB_SIM=1 / LAB_FAKE=1)
everything is simulated: a simulated robot and a simulated overhead camera, never a
mix of real and simulated.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from lab_agent.devices.base import Blaster
from lab_agent.devices.codes import CodeBook
from lab_agent.interlocks import ArenaFence, FreshPose, Motion
from lab_agent.registry import Registry, Tool
from pydantic import BaseModel, ConfigDict, Field

from .camera import SIM_ARENA, Camera, OpenCVCamera, SimBlaster, SimCamera, SimRobot
from .config import Arena
from .live import LivePose
from .tracker import Tracker, make_tracker

CODES = Path(__file__).resolve().parents[3] / "exp000-ir-bridge" / "codes" / "rm4-mini-living.json"
MOVES = frozenset({"robot.forward", "robot.reverse"})

# Conservative until step 2 (motion model) measures them. The fence uses speed x seconds
# plus slack; reverse arcs, so it gets more slack.
MOTIONS = {
    "robot.forward": Motion(speed_cm_s=25, direction_deg=0, slack=0.5),
    "robot.reverse": Motion(speed_cm_s=20, direction_deg=180, slack=1.0),
}


class Hold(BaseModel):
    model_config = ConfigDict(extra="forbid")
    seconds: float = Field(gt=0, le=3)


@dataclass
class Rig:
    registry: Registry
    live: LivePose
    arena: Arena
    simulated: bool
    fence: ArenaFence
    robot: SimRobot | None = None
    camera: SimCamera | None = None


def simulated() -> bool:
    return (
        os.environ.get("LAB_SIM") == "1"
        or os.environ.get("LAB_FAKE") == "1"
        or not (os.environ.get("RM4_HOST"))
    )


def make_rig(*, sim: bool | None = None, realtime: bool = False) -> Rig:
    sim = simulated() if sim is None else sim
    robot: SimRobot | None = None
    sim_cam: SimCamera | None = None
    blaster: Blaster
    camera: Camera
    if sim:
        arena = SIM_ARENA
        robot = SimRobot()
        blaster = SimBlaster(robot, realtime=realtime)
        camera = sim_cam = SimCamera(robot, arena)
    else:
        from lab_agent.devices.broadlink_ir import BroadlinkBlaster

        arena = Arena.load()
        blaster = BroadlinkBlaster(
            id="rm4-mini-living", host=os.environ["RM4_HOST"], codes=CodeBook(CODES)
        )
        camera = OpenCVCamera(arena.camera_index, zoom=arena.zoom)

    live = LivePose(camera, Tracker(arena) if sim else make_tracker(arena))
    live.motion_heading = (
        not sim and arena.tracking == "background" and (arena.background.heading_from == "none")
    )
    reg = Registry()

    def hold(code: str):
        def handler(args: BaseModel) -> dict[str, int]:
            assert isinstance(args, Hold)
            return {"frames": blaster.hold(code, args.seconds)}

        return handler

    for name, code, desc in (
        ("robot.forward", "robot_forward", "Drive forward"),
        ("robot.reverse", "robot_reverse", "Reverse (backs up and turns left)"),
    ):
        reg.add(
            Tool(
                name,
                desc,
                hold(code),
                args_model=Hold,
                device=blaster.id,
                duration_arg="seconds",
                max_duration_s=3,
            )
        )
    reg.add_interlock(FreshPose(live, MOVES, max_age_s=1.0))
    motions = (
        {
            k: Motion(m.speed_cm_s, m.direction_deg, m.slack, m.base_cm)
            for k, m in arena.motions.items()
        }
        if arena.motions
        else MOTIONS
    )
    fence = ArenaFence(live, arena.width_cm, arena.height_cm, motions, margin_cm=arena.margin_cm)
    reg.add_interlock(fence)
    return Rig(reg, live, arena, sim, fence, robot, sim_cam)


def build() -> Registry:
    """For LAB_TOOLS (agent, generic CLI): starts background tracking so interlocks work."""
    rig = make_rig()
    rig.live.start()
    return rig.registry
