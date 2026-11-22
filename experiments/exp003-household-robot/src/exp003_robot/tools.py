"""Tool set for Experiment 3: the household robot's wheels.

With LAB_FAKE=1, or no EXP003_SERVO_PORT, the wheels are fake and their id starts with
"fake-", so a fake run can never be mistaken for a real one in the logs. Real STS3215
wheels arrive in step 2 of the console's order of work (CONTROL_APP.md).
"""

from __future__ import annotations

import os

from lab_agent.devices.base import Wheels
from lab_agent.devices.fake import FakeWheels
from lab_agent.interlocks import LeaseRequired
from lab_agent.lease import DriveLease
from lab_agent.registry import HALT, Registry, Tool
from pydantic import BaseModel, ConfigDict, Field

TRACK_M = 0.2976  # wheel centre to wheel centre (cad/exp003_cad/params.py, derive_base)
MAX_V_M_S = 0.3  # CONTROL_APP.md, Safety
MAX_W_RAD_S = 1.5
LEASE_S = 0.3


class Drive(BaseModel):
    """Drive for one lease: forward speed and turn rate."""

    model_config = ConfigDict(extra="forbid")
    v: float = Field(ge=-MAX_V_M_S, le=MAX_V_M_S, description="forward speed, m/s")
    w: float = Field(ge=-MAX_W_RAD_S, le=MAX_W_RAD_S, description="turn rate, rad/s, + is left")


def wheel_speeds(v: float, w: float, track_m: float = TRACK_M) -> tuple[float, float]:
    """(left, right) ground speeds for a differential drive."""
    half = w * track_m / 2
    return v - half, v + half


def _wheels() -> Wheels:
    if os.environ.get("LAB_FAKE") == "1" or not os.environ.get("EXP003_SERVO_PORT"):
        return FakeWheels(id="fake-wheels")
    raise SystemExit("real wheels are not wired yet: unset EXP003_SERVO_PORT or set LAB_FAKE=1")


def build(lease: DriveLease | None = None, wheels: Wheels | None = None) -> Registry:
    """Register the wheel tools.

    A lease created inside build() is never renewed, so base.drive is always refused with it.
    Callers that drive (the console) must pass their own lease.
    """
    lease = lease if lease is not None else DriveLease(ttl_s=LEASE_S)
    wheels = wheels if wheels is not None else _wheels()
    reg = Registry()

    def drive(args: BaseModel) -> None:
        assert isinstance(args, Drive)
        wheels.set_speeds(*wheel_speeds(args.v, args.w))

    def stop(_args: BaseModel) -> None:
        wheels.set_speeds(0.0, 0.0)

    reg.add(
        Tool(
            "base.drive",
            "Drive for one lease: forward speed v (m/s) and turn rate w (rad/s)",
            drive,
            args_model=Drive,
            device=wheels.id,
        )
    )
    reg.add(Tool("base.stop", "Stop both wheels", stop, device=wheels.id, tags=frozenset({HALT})))
    reg.add_interlock(LeaseRequired(lease, frozenset({"base.drive"})))
    return reg
