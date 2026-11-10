from pathlib import Path

import pytest
from lab_agent.devices.fake import FakeBlaster
from lab_agent.log import EventLog
from lab_agent.registry import Registry, Tool
from lab_agent.runner import Runner

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
