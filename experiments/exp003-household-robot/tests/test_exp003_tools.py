from pathlib import Path

import pytest
from exp003_robot.tools import MAX_V_M_S, TRACK_M, build, wheel_speeds
from lab_agent.devices.fake import FakeWheels
from lab_agent.lease import DriveLease
from lab_agent.log import EventLog, read_log
from lab_agent.runner import Runner


class Clock:
    t = 50.0

    def __call__(self) -> float:
        return self.t


@pytest.fixture
def rig(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)  # isolate the STOP file
    clock = Clock()
    lease = DriveLease(ttl_s=0.3, clock=clock)
    wheels = FakeWheels()
    log = EventLog(tmp_path / "events" / "exp003" / "r1.jsonl", "exp003-t-r1")
    runner = Runner(build(lease=lease, wheels=wheels), log)
    runner.start("exp003-household-robot")
    return runner, lease, wheels, clock


def test_turning_left_slows_the_left_wheel():
    left, right = wheel_speeds(0.2, 1.0)
    assert left == pytest.approx(0.2 - TRACK_M / 2)
    assert right == pytest.approx(0.2 + TRACK_M / 2)


def test_drive_needs_a_live_lease(rig):
    runner, lease, wheels, _ = rig
    denied = runner.request("base.drive", {"v": 0.1, "w": 0.0}, actor="human")
    assert not denied.allowed and "drive_lease" in denied.checked.payload.reason
    lease.renew()
    ok = runner.request("base.drive", {"v": 0.1, "w": 0.0}, actor="human")
    assert ok.ok and wheels.speeds == (pytest.approx(0.1), pytest.approx(0.1))


def test_speed_over_the_cap_is_refused(rig):
    runner, lease, wheels, _ = rig
    lease.renew()
    r = runner.request("base.drive", {"v": MAX_V_M_S + 0.1, "w": 0.0}, actor="human")
    assert not r.allowed and r.checked.payload.rule == "args"
    assert wheels.history == []


def test_stop_always_works_even_with_a_stop_file(rig, tmp_path):
    runner, lease, wheels, _ = rig
    lease.renew()
    runner.request("base.drive", {"v": 0.1, "w": 0.0}, actor="human")
    (tmp_path / "STOP").touch()
    r = runner.request("base.stop", actor="system")
    assert r.ok and r.checked.payload.rule == "halt"
    assert wheels.speeds == (0.0, 0.0)


def test_every_step_is_logged_and_the_log_is_valid(rig):
    runner, lease, _, _ = rig
    lease.renew()
    runner.request("base.drive", {"v": 0.1, "w": 0.5}, actor="human")
    runner.request("base.stop", actor="human")
    runner.end()
    events = read_log(runner.log.path)
    assert [e.type for e in events].count("command.sent") == 2
