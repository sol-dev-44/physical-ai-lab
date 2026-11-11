"""Tool set for Experiment 0.

Devices come from the environment. With no RM4_HOST (or LAB_FAKE=1) every
device is a fake, and its id starts with "fake-", so a fake run can never be
mistaken for a real one in the logs.
"""

from __future__ import annotations

import os
from pathlib import Path

from lab_agent.devices.base import Blaster, Switch
from lab_agent.devices.codes import CodeBook
from lab_agent.devices.fake import FakeBlaster, FakeSwitch
from lab_agent.registry import Registry, Tool
from pydantic import BaseModel, ConfigDict, Field

CODES = Path(__file__).resolve().parents[2] / "codes"


class Hold(BaseModel):
    """Hold a direction for a short time. Toy IR robots move only while the code repeats."""

    model_config = ConfigDict(extra="forbid")
    seconds: float = Field(gt=0, le=3)


def _blaster() -> Blaster:
    host = os.environ.get("RM4_HOST")
    if not host or os.environ.get("LAB_FAKE") == "1":
        return FakeBlaster(id="fake-rm4")
    from lab_agent.devices.broadlink_ir import BroadlinkBlaster

    return BroadlinkBlaster(
        id="rm4-mini-living", host=host, codes=CodeBook(CODES / "rm4-mini-living.json")
    )


def _plug(env: str, name: str) -> Switch | None:
    host = os.environ.get(env)
    if os.environ.get("LAB_FAKE") == "1" or not host:
        return FakeSwitch(id=f"fake-{name}")
    from lab_agent.devices.kasa_plug import KasaPlug

    return KasaPlug(id=name, host=host)


def build() -> Registry:
    ir = _blaster()
    lamp = _plug("KASA_LAMP_HOST", "kasa-lamp")
    reg = Registry()

    def press(code: str):
        def handler(_args: BaseModel) -> None:
            ir.send(code)

        return handler

    def hold(code: str):
        def handler(args: BaseModel) -> dict[str, int]:
            assert isinstance(args, Hold)
            return {"frames": ir.hold(code, args.seconds)}

        return handler

    # IR: everyday devices
    reg.add(
        Tool("fan.power", "Fan power toggle", press("fan_power"), device=ir.id, min_interval_s=1)
    )
    reg.add(
        Tool("fan.speed", "Fan speed step", press("fan_speed"), device=ir.id, min_interval_s=0.5)
    )
    reg.add(Tool("tv.power", "TV power toggle", press("tv_power"), device=ir.id, min_interval_s=2))
    reg.add(
        Tool(
            "tv.volume_up", "TV volume up", press("tv_volume_up"), device=ir.id, min_interval_s=0.3
        )
    )
    reg.add(
        Tool(
            "tv.volume_down",
            "TV volume down",
            press("tv_volume_down"),
            device=ir.id,
            min_interval_s=0.3,
        )
    )

    # IR: toy robot with a two-button IR remote (forward, reverse). Checked 2026-11-10.
    reg.add(
        Tool(
            "robot.forward",
            "Drive forward",
            hold("robot_forward"),
            args_model=Hold,
            device=ir.id,
            duration_arg="seconds",
            max_duration_s=3,
        )
    )
    reg.add(
        Tool(
            "robot.reverse",
            "Reverse (this robot backs up and turns left)",
            hold("robot_reverse"),
            args_model=Hold,
            device=ir.id,
            duration_arg="seconds",
            max_duration_s=3,
        )
    )

    # Fireplace: heat source. Confirmation every time, never automated, never remote.
    reg.add(
        Tool(
            "fireplace.power",
            "Fireplace power toggle (supervised only)",
            press("fireplace_power"),
            device=ir.id,
            requires_confirmation=True,
            manual_only=True,
            min_interval_s=5,
        )
    )

    # Wi-Fi plug
    if lamp is not None:
        reg.add(Tool("lamp.on", "Lamp on", lambda _a: lamp.set(True), device=lamp.id))
        reg.add(Tool("lamp.off", "Lamp off", lambda _a: lamp.set(False), device=lamp.id))
    return reg
