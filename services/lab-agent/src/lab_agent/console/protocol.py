"""WebSocket messages between the robot console and the app.

Mirrored in apps/robot-console/src/protocol.ts; both sides test against
packages/schema/fixtures/console. Change both together.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

Finite = Annotated[float, Field(allow_inf_nan=False)]
Seq = Annotated[int, Field(ge=0, le=2**53 - 1)]  # exactly representable in JS numbers


class _Msg(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


# Browser to robot
class Hello(_Msg):
    type: Literal["hello"]
    token: Annotated[str, Field(min_length=1, max_length=256)]


class DriveMsg(_Msg):
    type: Literal["drive"]
    v: Finite
    w: Finite
    seq: Seq


class Heartbeat(_Msg):
    type: Literal["heartbeat"]
    seq: Seq


class StopMsg(_Msg):
    type: Literal["stop"]


ClientMessage = Annotated[Hello | DriveMsg | Heartbeat | StopMsg, Field(discriminator="type")]
client_message: TypeAdapter[ClientMessage] = TypeAdapter(ClientMessage)


# Robot to browser
class Battery(_Msg):
    volts: Finite
    amps: Finite
    soc_pct: Finite
    runtime_min: Finite


class Servo(_Msg):
    id: int
    temp_c: Finite
    load_pct: Finite
    volts: Finite


class Tof(_Msg):
    left_mm: int | None
    center_mm: int | None
    right_mm: int | None


class Controller(_Msg):
    connected: bool
    battery_pct: Finite | None = None


class Welcome(_Msg):
    type: Literal["welcome"]
    run_id: str
    max_v: Finite
    max_w: Finite
    lease_s: Finite


class State(_Msg):
    type: Literal["state"]
    t: Finite
    fake: bool
    battery: Battery
    servos: list[Servo]
    tof: Tof
    cliff_mm: list[int | None]
    bumpers: list[bool]
    wifi_dbm: Finite | None
    pi_temp_c: Finite | None
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
