from pathlib import Path
from types import SimpleNamespace

import pytest
from lab_agent.devices.fake import FakeBlaster, FakeWheels
from lab_agent.interlocks import LeaseRequired
from lab_agent.lease import DriveLease
from lab_agent.log import EventLog
from lab_agent.registry import HALT, Registry, Tool
from lab_agent.runner import Runner
from pydantic import BaseModel, ConfigDict, Field

FIXTURES = Path(__file__).resolve().parents[3] / "packages" / "schema" / "fixtures"


@pytest.fixture
def blaster() -> FakeBlaster:
    return FakeBlaster()


@pytest.fixture
def registry(blaster: FakeBlaster) -> Registry:
    reg = Registry()
    reg.add(Tool("fan.power", "fan", lambda _a: blaster.send("fan_power"), device=blaster.id))
    reg.add(
        Tool(
            "heater.power",
            "heater",
            lambda _a: blaster.send("heater"),
            device=blaster.id,
            requires_confirmation=True,
            manual_only=True,
        )
    )
    return reg


@pytest.fixture
def runner(tmp_path: Path, registry: Registry, monkeypatch: pytest.MonkeyPatch) -> Runner:
    monkeypatch.chdir(tmp_path)  # isolate the STOP file
    log = EventLog(tmp_path / "events" / "exp000-test" / "exp000-t-r1.jsonl", "exp000-t-r1")
    return Runner(registry, log)


class DriveArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    v: float = Field(ge=-0.3, le=0.3)
    w: float = Field(ge=-1.5, le=1.5)


class ManualClock:
    def __init__(self, t: float = 10.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t


@pytest.fixture
def drive_rig(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Build a runner with base.drive and base.stop on fake wheels behind a drive lease.
    Call it with a clock; the default is a ManualClock the test moves by hand."""
    monkeypatch.chdir(tmp_path)  # isolate the STOP file

    def make(clock=None):
        clock = clock or ManualClock()
        lease = DriveLease(ttl_s=0.3, clock=clock)
        wheels = FakeWheels()
        reg = Registry()

        def drive(a: DriveArgs) -> None:
            wheels.set_speeds(a.v - a.w * 0.15, a.v + a.w * 0.15)

        def stop(_a: BaseModel) -> None:
            wheels.set_speeds(0.0, 0.0)

        reg.add(Tool("base.drive", "drive", drive, args_model=DriveArgs, device=wheels.id))
        halt = frozenset({HALT})
        reg.add(Tool("base.stop", "stop", stop, device=wheels.id, tags=halt))
        reg.add_interlock(LeaseRequired(lease, frozenset({"base.drive"})))
        log = EventLog(tmp_path / "events" / "console.jsonl", "exp003-t-console")
        runner = Runner(reg, log)
        runner.start("exp003-household-robot")
        return SimpleNamespace(runner=runner, lease=lease, wheels=wheels, clock=clock)

    return make
