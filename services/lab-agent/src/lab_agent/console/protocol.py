"""WebSocket messages between the robot console and the app.

Mirrored in apps/robot-console/src/protocol.ts; both sides test against
packages/schema/fixtures/console. Change both together.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class _Msg(BaseModel):
    model_config = ConfigDict(extra="forbid")


# Browser to robot
class Hello(_Msg):
    type: Literal["hello"]
    token: Annotated[str, Field(min_length=1)]


class DriveMsg(_Msg):
    type: Literal["drive"]
    v: float
    w: float
    seq: Annotated[int, Field(ge=0)]


class Heartbeat(_Msg):
    type: Literal["heartbeat"]
    seq: Annotated[int, Field(ge=0)]


class StopMsg(_Msg):
    type: Literal["stop"]


ClientMessage = Annotated[Hello | DriveMsg | Heartbeat | StopMsg, Field(discriminator="type")]
client_message: TypeAdapter[ClientMessage] = TypeAdapter(ClientMessage)


# Robot to browser
class Battery(_Msg):
    volts: float
    amps: float
    soc_pct: float
    runtime_min: float


class Servo(_Msg):
    id: int
    temp_c: float
    load_pct: float
    volts: float


class Tof(_Msg):
    left_mm: int | None
    center_mm: int | None
    right_mm: int | None


class Controller(_Msg):
    connected: bool
    battery_pct: float | None = None


class Welcome(_Msg):
    type: Literal["welcome"]
    run_id: str
    max_v: float
    max_w: float
    lease_s: float


class State(_Msg):
    type: Literal["state"]
    t: float
    fake: bool
    battery: Battery
    servos: list[Servo]
    tof: Tof
    cliff_mm: list[int | None]
    bumpers: list[bool]
    wifi_dbm: float | None
    pi_temp_c: float | None
    lease_alive: bool
    moving: bool
    estop: bool
    stop_file: bool
    controller: Controller


class Refused(_Msg):
    type: Literal["refused"]
    rule: str
    reason: str = ""


ServerMessage = Annotated[Welcome | State | Refused, Field(discriminator="type")]
server_message: TypeAdapter[ServerMessage] = TypeAdapter(ServerMessage)
