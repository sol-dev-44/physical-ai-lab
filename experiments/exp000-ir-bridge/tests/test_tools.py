import pytest
from exp000_ir_bridge.tools import build
from lab_agent.safety import Request, SafetyGate


@pytest.fixture(autouse=True)
def fake(monkeypatch, tmp_path):
    monkeypatch.setenv("LAB_FAKE", "1")
    monkeypatch.chdir(tmp_path)


def test_builds_with_fakes():
    reg = build()
    assert {t.device for t in reg} == {"fake-rm4", "fake-kasa-lamp"}


def test_fireplace_is_locked_down():
    gate = SafetyGate(build())
    assert gate.check(Request("fireplace.power", {}, "human")).rule == "requires_confirmation"
    assert (
        gate.check(Request("fireplace.power", {}, "agent", confirmed=True, remote=True)).rule
        == "manual_only"
    )
    assert (
        gate.check(Request("fireplace.power", {}, "cli", confirmed=True, automated=True)).rule
        == "manual_only"
    )
    assert gate.check(Request("fireplace.power", {}, "human", confirmed=True)).allow


def test_robot_duration_capped():
    gate = SafetyGate(build())
    assert not gate.check(Request("robot.forward", {"seconds": 10}, "human")).allow
    assert gate.check(Request("robot.forward", {"seconds": 0.5}, "human")).allow
